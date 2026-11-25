"""Prepare the same pinned 300-example cohorts used in earlier evaluations."""

import hashlib
import json
import platform
import random
import subprocess
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASKS = json.loads(Path(__file__).with_name("tasks.json").read_text())
MODELS = (
    "gpt-6-astra",
    "gpt-6-sol",
    "gpt-6-luna",
    "gpt-6.1-sol",
    "gpt-6.1-terra",
    "gpt-6.2-astra",
    "gpt-6.2-sol",
)
SHOTS = (0, 1, 2)
CAPS = (48_000, 96_000, 128_000)


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def digest(value):
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, ensure_ascii=False, separators=(",", ":")
        ).encode()
    ).hexdigest()


def text_key(text):
    return " ".join(text.casefold().split())


def select_indices(texts, n=300):
    previous = list(range(len(texts)))
    random.Random(0).shuffle(previous)
    seen = {text_key(texts[i]) for i in previous[:500]}
    candidates = list(range(len(texts)))
    random.Random(20260926).shuffle(candidates)
    selected = []
    for i in candidates:
        key = text_key(texts[i])
        if key not in seen:
            selected.append(i)
            seen.add(key)
        if len(selected) == n:
            return selected
    raise ValueError(
        "Not enough distinct examples outside the earlier 500-example cohort"
    )


def source_hashes():
    paths = list((ROOT / "src").rglob("*.py")) + list((ROOT / "evals").glob("*.py"))
    paths += [ROOT / "evals/tasks.json", ROOT / "uv.lock"]
    return {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(paths)
    }


def prepare(output):
    from datasets import load_dataset

    output.mkdir(parents=True, exist_ok=False)
    for name, spec in TASKS.items():

        def load(split):
            return load_dataset(
                spec["hf_repo"], revision=spec["hf_revision"], split=split, token=False
            )

        test, train = load(spec["split"]), load("train")
        labels = spec["label_order"]
        for source in (test, train):
            names = [
                x.lower().replace("?", "").replace("/", "_")
                for x in source.features["label"].names
            ]
            if names != labels:
                raise ValueError(f"Label mapping changed: {name}")
        if len(test) != spec["source_rows"]:
            raise ValueError(f"Dataset size changed: {name}")

        def row(source, split, i):
            return {
                "id": f"{name}:{split}:{i}",
                "state": source[i][spec["text_field"]],
                "answer": labels[source[i]["label"]],
            }

        rows = [
            row(test, spec["split"], i)
            for i in select_indices(test[spec["text_field"]])
        ]
        examples = [row(train, "train", i) for i in spec["example_indices"]]
        if digest(rows) != spec["test_sha256"]:
            raise ValueError(f"Test cohort changed: {name}")
        if {text_key(x["state"]) for x in examples} & {
            text_key(t) for t in test[spec["text_field"]]
        }:
            raise ValueError(f"Training/test overlap: {name}")
        write(
            output / "data" / f"{name}.json",
            {"question": spec["question"], "examples": examples, "test": rows},
        )
    files = {
        str(p.relative_to(output)): digest(read(p))
        for p in sorted((output / "data").glob("*.json"))
    }
    write(
        output / "manifest.json",
        {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "git_commit": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip(),
            "source_hashes": source_hashes(),
            "data_hashes": files,
            "tasks": TASKS,
            "models": MODELS,
            "shots": SHOTS,
            "reasoning_effort": "high",
            "token_caps": CAPS,
            "max_attempts": 3,
            "test_n": 300,
            "python": platform.python_version(),
            "packages": {
                p: version(p)
                for p in (
                    "jev-heuristic-adapter",
                    "openai",
                    "datasets",
                    "huggingface-hub",
                )
            },
        },
    )


def verify(output):
    manifest = read(output / "manifest.json")
    if manifest["source_hashes"] != source_hashes():
        raise ValueError(
            "Source or lockfile changed since prepare; create a new run directory"
        )
    for name, expected in manifest["data_hashes"].items():
        if digest(read(output / name)) != expected:
            raise ValueError(f"Prepared data changed: {name}")
    return manifest
