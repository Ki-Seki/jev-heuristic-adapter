"""Run the frozen synthesis, compilation and held-out evaluation stages."""

import argparse
import getpass
import json
import math
import os
import platform
import re
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, replace
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

from jev_heuristic_adapter import HeuristicAdapterClient
from jev_heuristic_adapter._cache import ProgramStore
from jev_heuristic_adapter._prompt import SYSTEM_PROMPT
from jev_heuristic_adapter.providers import ProviderResult

from .experiment import compile_trial, sha256, split_synthetic, text_key
from .prompts import IMPROVED_PROMPT, SYNTHESIS_PROMPT

HERE = Path(__file__).resolve().parent
MODELS = ("gpt-6-luna", "gpt-6-sol")
ARMS = ("baseline", "prompt", "feedback")
REPEATS = 1


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    if re.search(r"sk-(?:proj-|or-v1-)?[A-Za-z0-9_-]{20,}", encoded):
        raise ValueError("Refusing to serialize a credential")
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(encoded)
    temporary.replace(path)


def request_cost(result, model):
    """Standard short-context API fees; retain an upper bound for missing writes."""
    usage = result.raw.get("usage") or {}
    details = usage.get("input_tokens_details") or {}
    if result.input_tokens is None or result.output_tokens is None:
        return {"usd": None, "upper_usd": None}
    if result.input_tokens > 272000:
        raise ValueError("The frozen pricing table covers short context only")
    tier = result.raw.get("service_tier", "default") or "default"
    if tier not in {"default", "standard"}:
        raise ValueError(f"Unexpected service tier: {tier}")
    rates = read(HERE / "pricing.json")["models"][model]
    cached = details.get("cached_tokens", 0) or 0
    written = details.get("cache_write_tokens", 0) or 0
    ordinary = result.input_tokens - cached - written
    if ordinary < 0:
        raise ValueError("Invalid token accounting")
    fee = (
        ordinary * rates["input"]
        + cached * rates["cached_input"]
        + written * rates["cache_write"]
        + result.output_tokens * rates["output"]
    ) / 1_000_000
    extra = (
        ordinary * (rates["cache_write"] - rates["input"]) / 1_000_000
        if "cache_write_tokens" not in details
        else 0
    )
    return {
        "usd": fee,
        "upper_usd": fee + extra,
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
        "cached_tokens": cached,
        "cache_write_tokens": written if "cache_write_tokens" in details else None,
    }


class Calls:
    def __init__(self, key):
        from openai import OpenAI

        from jev_heuristic_adapter.providers.openai import OpenAIProvider

        self.providers = {
            model: OpenAIProvider(
                OpenAI(
                    api_key=key,
                    base_url="https://api.openai.com/v1",
                    max_retries=0,
                    timeout=600,
                ),
                model,
                reasoning_effort="high",
                max_output_tokens=24000,
            )
            for model in MODELS
        }

    def request(self, model, messages, directory):
        saved = directory / "response.json"
        if saved.exists():
            record = read(saved)
            if (
                read(directory / "messages.json") != messages
                or record["model"] != model
            ):
                raise ValueError("Saved call does not match this request")
            return ProviderResult(**record["result"])
        started = directory / "started.json"
        if started.exists():
            raise RuntimeError(
                f"Unfinished call; refusing automatic resubmission: {directory}"
            )
        write(directory / "messages.json", messages)
        write(started, {"model": model, "at": time.time()})
        begin = time.perf_counter()
        try:
            result = self.providers[model].request(messages)
        except Exception as exc:
            # SDK errors may echo authentication input; retain only the error type.
            write(directory / "failure.json", {"error_type": type(exc).__name__})
            raise RuntimeError(
                f"Provider failure ({type(exc).__name__}); see {directory}"
            ) from None
        result = replace(
            result,
            raw={
                key: result.raw.get(key)
                for key in ("id", "model", "status", "usage", "service_tier")
            },
        )
        write(
            saved,
            {
                "model": model,
                "seconds": time.perf_counter() - begin,
                "finished_at": time.time(),
                "result": asdict(result),
                "cost": request_cost(result, model),
            },
        )
        if result.raw["model"] != model:
            raise ValueError("Returned model differs from the requested model")
        return result


def parallel(jobs, workers):
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(fn, *args): label for label, fn, args in jobs}
        for future in as_completed(futures):
            future.result()
            print(f"Completed {futures[future]}", flush=True)


def synthesize(calls, output, specs, workers):
    jobs = []
    for name, spec in specs.items():
        labels = sorted(spec["question"]["criteria"])
        count = max(6, math.ceil(120 / len(labels)))
        for chunk, offset in enumerate(range(0, len(labels), 11)):
            messages = [
                {"role": "system", "content": SYNTHESIS_PROMPT},
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "question": spec["question"],
                            "target_labels": labels[offset : offset + 11],
                            "count_per_label": count,
                        }
                    ),
                },
            ]
            jobs.append(
                (
                    f"synthetic {name}/{chunk}",
                    calls.request,
                    ("gpt-6-sol", messages, output / "synthesis" / name / str(chunk)),
                )
            )
    parallel(jobs, workers)
    for name, spec in specs.items():
        examples = []
        for path in sorted((output / "synthesis" / name).glob("*/response.json")):
            response = read(path)["result"]
            if not response["complete"]:
                raise ValueError("Synthetic generation was incomplete")
            examples.extend(json.loads(response["text"]))
        labels = spec["question"]["criteria"]
        checks = split_synthetic(examples, labels, max(6, math.ceil(120 / len(labels))))
        write(output / "synthesis" / name / "checks.json", checks)
    write(
        output / "synthetic-freeze.json",
        {
            name: sha256(read(output / "synthesis" / name / "checks.json"))
            for name in specs
        },
    )


def compile_one(calls, output, name, spec, model, repeat, method="feedback"):
    directory = output / "trials" / f"{model}--{name}--{repeat}"
    checks = None
    if method == "feedback":
        checks = read(output / "synthesis" / name / "checks.json")
        if sha256(checks) != read(output / "synthetic-freeze.json")[name]:
            raise ValueError("Synthetic checks changed after freezing")
    question = spec["question"]
    for arm in ARMS if method == "feedback" else ARMS[:2]:
        target = directory / arm / "trial.json"
        if target.exists():
            continue
        start = time.perf_counter()

        def request(messages, index):
            return calls.request(model, messages, directory / arm / f"call-{index}")

        kwargs = {}
        if arm == "feedback":
            initial = read(directory / "prompt" / "trial.json")["candidates"][0][
                "result"
            ]
            kwargs = {
                "rounds": 2,
                "checks": checks,
                "initial": ProviderResult(**initial),
            }
        trial = compile_trial(
            request,
            question,
            SYSTEM_PROMPT if arm == "baseline" else IMPROVED_PROMPT,
            **kwargs,
        )
        trial.update(model=model, dataset=name, repeat=repeat, arm=arm)
        trial["phase_seconds"] = time.perf_counter() - start
        write(target, trial)
        print(
            f"Frozen {model}/{name}/{repeat}/{arm}: candidate {trial['selected']}",
            flush=True,
        )


def compile_all(calls, output, specs, workers, method="feedback"):
    jobs = [
        (
            f"compile {model}/{name}/{repeat}",
            compile_one,
            (calls, output, name, spec, model, repeat, method),
        )
        for repeat in range(REPEATS)
        for name, spec in specs.items()
        for model in MODELS
    ]
    parallel(jobs, workers)
    trials = sorted((output / "trials").glob("*/*/trial.json"))
    arm_count = 3 if method == "feedback" else 2
    if len(trials) != len(MODELS) * len(specs) * REPEATS * arm_count:
        raise ValueError("Compilation is incomplete")
    write(
        output / "program-freeze.json",
        {str(p.relative_to(output)): sha256(read(p)) for p in trials},
    )


class ReplayProvider:
    """Install one frozen result through the real adapter without a model call."""

    def __init__(self, result):
        self.result = result
        self.calls = 0

    def cache_identity(self):
        return {
            "provider": "frozen-experiment",
            "source_sha256": sha256(self.result.text),
        }

    def request(self, messages):
        self.calls += 1
        if self.calls != 1:
            raise AssertionError("Only one local replay is permitted")
        return self.result


def percentile(values, fraction):
    values = sorted(values)
    position = (len(values) - 1) * fraction
    low, high = math.floor(position), math.ceil(position)
    return values[low] + (values[high] - values[low]) * (position - low)


def score_rows(rows, labels):
    f1s = []
    for label in labels:
        tp = sum(r["gold"] == label and r["prediction"] == label for r in rows)
        actual = sum(r["gold"] == label for r in rows)
        predicted = sum(r["prediction"] == label for r in rows)
        f1s.append(2 * tp / (actual + predicted) if actual + predicted else 0)
    return {
        "n": len(rows),
        "accuracy": sum(r["gold"] == r["prediction"] for r in rows) / len(rows),
        "macro_f1": sum(f1s) / len(f1s),
        "errors": sum(r["error"] is not None for r in rows),
        "p50_ms": percentile([r["latency_ms"] for r in rows], 0.5),
        "p95_ms": percentile([r["latency_ms"] for r in rows], 0.95),
    }


def evaluate_one(trial, spec, inputs):
    candidate = trial["candidates"][trial["selected"]]
    provider = ReplayProvider(ProviderResult(**candidate["result"]))
    question = {"label": spec["question"]}
    rows = []
    with tempfile.TemporaryDirectory() as directory:
        client = HeuristicAdapterClient(provider, ProgramStore(Path(directory)))
        try:
            client.compile(question)
            compile_error = None
        except Exception as exc:
            compile_error = f"{type(exc).__name__}: {exc}"
        if compile_error is None:
            try:
                client.system_one(inputs[0]["state"], question)
            except Exception:
                pass  # Warmup errors are counted again in the scored pass.
        for item in inputs:
            start = time.perf_counter_ns()
            answer, error = None, compile_error
            if compile_error is None:
                try:
                    answer = (
                        client.system_one(item["state"], question)
                        .choices["label"]
                        .choice
                    )
                except Exception as exc:
                    error = f"{type(exc).__name__}: {exc}"
            rows.append(
                {
                    "id": item["id"],
                    "gold": item["answer"],
                    "prediction": answer,
                    "error": error,
                    "latency_ms": (time.perf_counter_ns() - start) / 1_000_000,
                }
            )
        assert provider.calls == 1, "Evaluation unexpectedly requested another program"
    return {
        "metrics": score_rows(rows, spec["question"]["criteria"]),
        "predictions": rows,
    }


def evaluate_all(output, data, specs):
    frozen = read(output / "program-freeze.json")
    method = read(output / "protocol.json").get("method", "feedback")
    arms = ARMS if method == "feedback" else ARMS[:2]
    expected = len(MODELS) * len(specs) * REPEATS * len(arms)
    if len(frozen) != expected:
        raise ValueError("Freeze every condition before reading evaluation inputs")
    for relative, expected_hash in frozen.items():
        if sha256(read(output / relative)) != expected_hash:
            raise ValueError("A frozen trial was modified")
    manifest = read(data / "manifest.json")
    # Only this stage reads real evaluation texts, after all selections are frozen.
    for name, spec in specs.items():
        inputs = read(data / f"{name}.json")
        if sha256(inputs) != manifest["datasets"][name]["sha256"]:
            raise ValueError("Evaluation inputs changed")
        checks_path = output / "synthesis" / name / "checks.json"
        checks = read(checks_path) if method == "feedback" else {}
        synthetic = {text_key(x["state"]) for group in checks.values() for x in group}
        overlaps = [
            item["id"] for item in inputs if text_key(item["state"]) in synthetic
        ]
        write(output / "overlaps" / f"{name}.json", overlaps)
        if overlaps:
            raise ValueError(
                "Synthetic/test overlap; preserve evidence and do not resample"
            )
        for model in MODELS:
            for repeat in range(REPEATS):
                for arm in arms:
                    directory = output / "trials" / f"{model}--{name}--{repeat}" / arm
                    target = directory / "evaluation.json"
                    if target.exists():
                        continue
                    trial = read(directory / "trial.json")
                    result = evaluate_one(trial, spec, inputs)
                    write(target, result)
                    print(
                        f"Evaluated {model}/{name}/{repeat}/{arm}: {result['metrics']['accuracy']:.1%}",
                        flush=True,
                    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("synthesize", "compile", "evaluate"))
    parser.add_argument("--method", choices=("prompt", "feedback"), default="feedback")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    if args.stage == "synthesize" and args.method != "feedback":
        parser.error("The prompt-only experiment does not require synthetic examples")
    specs = read(HERE / "specs.json")
    args.output.mkdir(parents=True, exist_ok=True)
    protocol = {
        "method": args.method,
        "models": MODELS,
        "repeats": REPEATS,
        "rounds": 2,
        "reasoning_effort": "high",
        "max_output_tokens": 24000,
        "synthetic_teacher": "gpt-6-sol",
        "synthetic_per_label": "max(6, ceil(120 / labels))",
        "workers": args.workers,
        "specs_sha256": sha256(specs),
        "data_manifest_sha256": sha256(read(args.data / "manifest.json")),
        "prompt_sha256": {
            "baseline": sha256(SYSTEM_PROMPT),
            "improved": sha256(IMPROVED_PROMPT),
        },
        "source_sha256": {
            p.name: sha256(p.read_text()) for p in sorted(HERE.glob("*.py"))
        },
    }
    path = args.output / "protocol.json"
    if path.exists():
        previous = read(path)
        if previous != json.loads(json.dumps(protocol)):
            raise ValueError(
                "Experiment configuration/code changed; use a new output directory"
            )
    else:
        write(path, protocol)
        write(
            args.output / "environment.json",
            {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "python": platform.python_version(),
                "platform": platform.platform(),
                "packages": {
                    p: version(p)
                    for p in ("openai", "typesafe-sdk", "jev-heuristic-adapter")
                },
            },
        )
    if args.stage == "evaluate":
        evaluate_all(args.output, args.data, specs)
    else:
        key = os.environ.get("OPENAI_API_KEY") or getpass.getpass("OpenAI API key: ")
        calls = Calls(key)
        if args.stage == "synthesize":
            synthesize(calls, args.output, specs, args.workers)
        else:
            compile_all(calls, args.output, specs, args.workers, args.method)


if __name__ == "__main__":
    main()
