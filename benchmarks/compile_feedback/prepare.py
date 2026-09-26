"""Freeze new held-out inputs, excluding the previously inspected seed-0 cohort."""

import argparse
import hashlib
import json
import random
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from .experiment import sha256, text_key


def normalized_label_names(names):
    return [name.lower().replace("?", "").replace("/", "_") for name in names]


def select_indices(texts, n=300, seed=20260926):
    previous = list(range(len(texts)))
    random.Random(0).shuffle(previous)
    excluded = {text_key(texts[i]) for i in previous[:500]}
    candidates = list(range(len(texts)))
    random.Random(seed).shuffle(candidates)
    selected, seen = [], set(excluded)
    for i in candidates:
        key = text_key(texts[i])
        if key not in seen:
            selected.append(i)
            seen.add(key)
        if len(selected) == n:
            break
    if len(selected) != n:
        raise ValueError("Not enough uninspected, distinct inputs")
    return selected, previous[:500]


def main():
    from datasets import load_dataset

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    if (args.output / "manifest.json").exists():
        raise ValueError("The evaluation cohort is already frozen")
    specs = json.loads(Path(__file__).with_name("specs.json").read_text())
    manifest = {"created_at": datetime.now(timezone.utc).isoformat(), "datasets": {}}
    for name, spec in specs.items():
        source = load_dataset(
            spec["hf_repo"],
            revision=spec["hf_revision"],
            split=spec["split"],
            token=False,
        )
        texts = source[spec["text_field"]]
        indices, old = select_indices(texts)
        labels = spec["label_order"]
        assert len(source) == spec["source_rows"]
        assert normalized_label_names(source.features["label"].names) == labels
        old_rows = [
            {
                "dataset": name,
                "id": f"{name}:{spec['split']}:{i}",
                "position": position,
                "source_index": i,
                "text": texts[i],
                "label": labels[int(source[i]["label"])],
            }
            for position, i in enumerate(old)
        ]
        previous_bytes = "".join(
            json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
            for row in old_rows
        ).encode()
        assert (
            hashlib.sha256(previous_bytes).hexdigest() == spec["previous_sample_sha256"]
        )
        rows = [
            {
                "id": f"{name}:{spec['split']}:{i}",
                "state": texts[i],
                "answer": labels[int(source[i]["label"])],
            }
            for i in indices
        ]
        (args.output / f"{name}.json").write_text(json.dumps(rows, ensure_ascii=False))
        manifest["datasets"][name] = {
            **spec,
            "source_indices": indices,
            "previous_source_indices": old,
            "sha256": sha256(rows),
            "label_counts": dict(Counter(row["answer"] for row in rows)),
            "n": len(rows),
        }
        print(f"Frozen {name}: {len(rows)} disjoint inputs", flush=True)
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
