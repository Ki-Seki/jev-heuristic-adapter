"""Generate once per task family, then score without feedback to the compiler."""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict

from jev_heuristic_adapter._compiler import compile_question
from jev_heuristic_adapter._program import CompiledQuestion, load_predictor
from jev_heuristic_adapter.providers import ProviderResult

from .api import (
    API,
    BudgetExceeded,
    CallError,
    decision_payload,
    generation_payload,
    output_text,
)
from .data import CAPS, MODELS, SHOTS, TASKS, read, verify, write
from .results import report, score, write_rows


class CompileProvider:
    def __init__(self, api, model, cap, folder):
        self.api, self.model, self.cap, self.folder = api, model, cap, folder
        self.raw = {}

    def request(self, messages):
        self.raw, _ = self.api.call(
            "compile",
            self.model,
            generation_payload(self.model, messages, self.cap),
            self.folder,
        )
        usage = self.raw.get("usage") or {}
        return ProviderResult(
            output_text(self.raw),
            self.raw.get("status") == "completed",
            usage.get("input_tokens"),
            usage.get("output_tokens"),
            self.raw,
        )


def compile_job(api, model, name, shots, data):
    job = f"compile--{model}--{name}--{shots}shot"
    status_path = api.output / "programs" / f"{job}.status.json"
    if status_path.exists():
        return read(status_path)
    examples = [
        {"state": x["state"], "answer": x["answer"]} for x in data["examples"][:shots]
    ]
    cap_index, error = 0, None
    for attempt in range(1, 4):
        folder = api.output / "calls" / job / str(attempt)
        provider = CompileProvider(api, model, CAPS[cap_index], folder)
        try:
            program = compile_question(
                provider, question=data["question"], examples=examples
            )
            # Syntax/import/entry-point checks only; no labeled-example gate.
            load_predictor(program)
        except BudgetExceeded:
            raise
        except CallError as exc:
            if not exc.retryable:
                raise
            error = str(exc)
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
        else:
            write(api.output / "programs" / f"{job}.json", asdict(program))
            (api.output / "programs" / f"{job}.py").write_text(
                program.source, encoding="utf-8"
            )
            error = None
            break
        write(folder / "validation.json", {"error": error})
        if (provider.raw.get("incomplete_details") or {}).get(
            "reason"
        ) == "max_output_tokens":
            cap_index = min(cap_index + 1, len(CAPS) - 1)
        if attempt < 3:
            time.sleep(2 ** (attempt - 1))
    result = {
        "job": job,
        "method": "compile",
        "model": model,
        "dataset": name,
        "shots": shots,
        "attempts": attempt,
        "error": error,
    }
    write(status_path, result)
    print(
        f"{job}: {'ready' if error is None else 'failed'} ({attempt} attempts)",
        flush=True,
    )
    return result


def evaluate_program(output, compiled, data):
    job = compiled["job"]
    if (output / "results" / f"{job}.json").exists():
        return
    predict = None
    if compiled["error"] is None:
        program = CompiledQuestion(**read(output / "programs" / f"{job}.json"))
        program.validate_integrity(program.artifact_id)
        predict = load_predictor(program)
    rows = []
    started = time.perf_counter()
    for sample in data["test"]:
        before = time.perf_counter()
        answer, error = None, compiled["error"]
        if predict is not None:
            try:
                answer = predict(sample["state"])["answer"]
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
        rows.append(
            {
                "id": sample["id"],
                "gold": sample["answer"],
                "prediction": answer,
                "error": error,
                "latency_ms": (time.perf_counter() - before) * 1000
                if predict
                else None,
            }
        )
    save_result(output, compiled, data, rows, time.perf_counter() - started)


def decision_one(api, job, question, examples, sample):
    payload = decision_payload(question, examples, sample["state"])
    elapsed, unknown_time, answer, error = 0.0, False, None, None
    for attempt in range(1, 4):
        folder = (
            api.output / "calls" / job / sample["id"].replace(":", "-") / str(attempt)
        )
        try:
            raw, receipt = api.call("decisions", "gpt-6-luna", payload, folder)
        except CallError as exc:
            if not exc.retryable:
                raise
            receipt, error = exc.receipt, str(exc)
        else:
            matches = [a for a in raw.get("answers", []) if a.get("name") == "label"]
            answer = matches[0].get("choice") if len(matches) == 1 else None
            error = (
                None if answer in question["criteria"] else "Invalid decision answer"
            )
            if error:
                answer = None
        elapsed += receipt["seconds"] or 0
        unknown_time |= receipt["seconds"] is None
        if error is None:
            break
        if attempt < 3:
            time.sleep(2 ** (attempt - 1))
    return {
        "id": sample["id"],
        "gold": sample["answer"],
        "prediction": answer,
        "error": error,
        "latency_ms": None if unknown_time else elapsed * 1000,
    }


def save_result(output, identity, data, rows, seconds):
    write_rows(output / "predictions" / f"{identity['job']}.jsonl", rows)
    result = {
        **identity,
        **score(rows, data["question"]["criteria"]),
        "inference_seconds": seconds,
    }
    if identity.get("error"):
        result.update(accuracy=None, macro_f1=None)
    write(output / "results" / f"{identity['job']}.json", result)


def parallel(function, arguments, workers):
    """Keep input order, but surface errors promptly and cancel queued calls."""
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(function, *args): i for i, args in enumerate(arguments)}
        values = [None] * len(futures)
        try:
            for future in as_completed(futures):
                values[futures[future]] = future.result()
        finally:
            for future in futures:
                future.cancel()
        return values


def run(output, budget, workers):
    from openai import OpenAI

    verify(output)
    data = {name: read(output / "data" / f"{name}.json") for name in TASKS}
    # Disable SDK retries so the three-attempt limit counts physical requests.
    client = OpenAI(base_url="https://api.openai.com/v1", max_retries=0, timeout=1800)
    api = API(client, output, budget)
    started, complete = time.perf_counter(), False
    try:
        compiled = parallel(
            compile_job,
            (
                (api, model, name, shots, data[name])
                for model in MODELS
                for name in TASKS
                for shots in SHOTS
            ),
            workers,
        )
        # Freeze every program before scoring any test labels.
        for result in compiled:
            evaluate_program(output, result, data[result["dataset"]])
        for name in TASKS:
            for shots in SHOTS:
                job = f"decisions--gpt-6-luna--{name}--{shots}shot"
                if (output / "results" / f"{job}.json").exists():
                    continue
                samples = [
                    {"state": x["state"], "answer": x["answer"]}
                    for x in data[name]["examples"][:shots]
                ]
                before = time.perf_counter()
                rows = parallel(
                    decision_one,
                    (
                        (api, job, data[name]["question"], samples, row)
                        for row in data[name]["test"]
                    ),
                    workers,
                )
                identity = {
                    "job": job,
                    "method": "decisions",
                    "model": "gpt-6-luna",
                    "dataset": name,
                    "shots": shots,
                    "error": None,
                }
                save_result(
                    output, identity, data[name], rows, time.perf_counter() - before
                )
        complete = True
    finally:
        client.close()
        write(
            output / "run.json",
            {
                "complete": complete,
                "workers": workers,
                "budget_usd": budget,
                "invocation_seconds": time.perf_counter() - started,
            },
        )
        report(output)
