"""Provider-neutral experiment logic. No benchmark test data enters generation."""

import hashlib
import random
from collections import Counter, defaultdict
from dataclasses import asdict

from jev_heuristic_adapter._compiler import build_messages, validate_program
from jev_heuristic_adapter._program import (
    CompiledQuestion,
    build_artifact_id,
    build_question_id,
    canonical_json,
    load_predictor,
)
from jev_heuristic_adapter.providers import ProviderResult

from .prompts import REVISION_INSTRUCTIONS


def text_key(text):
    return " ".join(text.casefold().split())


def sha256(value):
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def make_program(question, messages, result):
    source = validate_program(result)
    question_json = canonical_json(question)
    question_id = build_question_id(question_json)
    request_json = canonical_json(messages)
    generation_json = canonical_json(asdict(result))
    artifact_id = build_artifact_id(question_id, source, request_json, generation_json)
    return CompiledQuestion(
        question_id, artifact_id, question_json, source, request_json, generation_json
    )


def assess(question, messages, result, examples):
    """Count invalid programs/predictions as wrong; do not silently drop them."""
    try:
        predict = load_predictor(make_program(question, messages, result))
        load_error = None
    except Exception as exc:
        predict, load_error = None, f"{type(exc).__name__}: {exc}"
    rows = []
    for item in examples:
        answer, error = None, load_error
        if predict is not None:
            try:
                answer = predict(item["state"])["answer"]
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
        rows.append({**item, "prediction": answer, "error": error})
    correct = sum(r["answer"] == r["prediction"] for r in rows)
    return {"correct": correct, "n": len(rows), "rows": rows}


def feedback(evaluation, limit=40, seed=0):
    """Cover different failed labels instead of returning only the first errors."""
    errors = defaultdict(list)
    for row in evaluation["rows"]:
        if row["answer"] != row["prediction"]:
            errors[row["answer"]].append(row)
    labels = sorted(errors)
    random.Random(seed).shuffle(labels)
    chosen = []
    while labels and len(chosen) < limit:
        for label in labels:
            if errors[label] and len(chosen) < limit:
                chosen.append(errors[label].pop(0))
        labels = [label for label in labels if errors[label]]
    return {
        "correct": evaluation["correct"],
        "total": evaluation["n"],
        "predicted_label_counts": dict(
            Counter(str(r["prediction"]) for r in evaluation["rows"])
        ),
        "confusions": [
            {"expected": pair[0], "predicted": pair[1], "count": count}
            for pair, count in Counter(
                (r["answer"], r["prediction"])
                for r in evaluation["rows"]
                if r["answer"] != r["prediction"]
            ).most_common()
        ],
        "failed_examples": chosen,
    }


def split_synthetic(examples, labels, per_label, seed=20260926):
    """Validate the teacher output, then freeze disjoint feedback/selection sets."""
    groups, seen = defaultdict(list), set()
    if per_label < 3:
        raise ValueError("Need at least three examples per label")
    for item in examples:
        if (
            not isinstance(item, dict)
            or set(item) != {"state", "answer"}
            or not isinstance(item["state"], str)
            or not item["state"].strip()
            or not isinstance(item["answer"], str)
            or item["answer"] not in labels
        ):
            raise ValueError("Invalid synthetic example")
        key = text_key(item["state"])
        if key in seen:
            raise ValueError("Duplicate synthetic text")
        seen.add(key)
        groups[item["answer"]].append(item)
    if set(groups) != set(labels) or any(
        len(group) != per_label for group in groups.values()
    ):
        raise ValueError("Synthetic label counts differ from the frozen protocol")
    train, dev = [], []
    rng = random.Random(seed)
    for label in sorted(labels):
        items = list(groups[label])
        rng.shuffle(items)
        n_dev = max(1, per_label // 3)
        dev.extend(items[:n_dev])
        train.extend(items[n_dev:])
    return {"feedback": train, "selection": dev}


def compile_trial(request, question, prompt, *, rounds=0, checks=None, initial=None):
    """Choose on synthetic selection data only; test inputs are not an argument.

    request(messages, round_index) returns a ProviderResult and records each call.
    The feedback arm can reuse the exact prompt-only initial candidate.
    """
    if rounds < 0 or rounds > 2:
        raise ValueError("The experiment permits zero, one or two feedback rounds")
    if rounds and (not checks or not checks["feedback"] or not checks["selection"]):
        raise ValueError("Feedback requires nonempty feedback and selection sets")
    messages = build_messages(question)
    messages[0]["content"] = prompt
    result = initial or request(messages, 0)
    candidates = []
    for index in range(rounds + 1):
        candidate = {
            "round": index,
            "messages": list(messages),
            "result": asdict(result),
        }
        if checks:
            candidate["feedback"] = assess(
                question, messages, result, checks["feedback"]
            )
            candidate["selection"] = assess(
                question, messages, result, checks["selection"]
            )
        candidates.append(candidate)
        if index == rounds:
            break
        observed = feedback(candidate["feedback"], seed=index)
        messages = [
            *messages,
            {"role": "assistant", "content": result.text},
            {
                "role": "user",
                "content": REVISION_INSTRUCTIONS + "\n" + canonical_json(observed),
            },
        ]
        result = request(messages, index + 1)
    # Fixed tie rule: prefer the earliest candidate. No early-stop/test selection.
    selected = (
        max(range(len(candidates)), key=lambda i: candidates[i]["selection"]["correct"])
        if checks
        else 0
    )
    return {"selected": selected, "candidates": candidates}


def selected_program(question, trial):
    item = trial["candidates"][trial["selected"]]
    return make_program(question, item["messages"], ProviderResult(**item["result"]))
