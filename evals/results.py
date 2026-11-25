"""Metrics and readable reports committed alongside the evaluation code."""

import json
import math
import statistics

from .data import plan, read


def write_rows(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def score(rows, labels):
    correct = sum(row["gold"] == row["prediction"] for row in rows)
    f1 = []
    for label in labels:
        tp = sum(row["gold"] == label == row["prediction"] for row in rows)
        count = sum(
            (row["gold"] == label) + (row["prediction"] == label) for row in rows
        )
        f1.append(2 * tp / count if count else 0.0)
    latencies = sorted(
        row["latency_ms"] for row in rows if row["latency_ms"] is not None
    )
    return {
        "n": len(rows),
        "accuracy": correct / len(rows),
        "macro_f1": statistics.mean(f1),
        "errors": sum(row["error"] is not None for row in rows),
        "p50_ms": statistics.median(latencies) if latencies else None,
        "p95_ms": latencies[math.ceil(len(latencies) * 0.95) - 1]
        if latencies
        else None,
    }


def attempt_totals(folder):
    total = {
        "api_attempts": 0,
        "cost_known_usd": 0.0,
        "cost_upper_usd": 0.0,
        "unknown_cost_attempts": 0,
        "api_seconds": 0.0,
        "input_tokens": 0,
        "output_tokens": 0,
        "reasoning_tokens": 0,
    }
    for request in folder.glob("**/request.json"):
        receipt_path = request.with_name("receipt.json")
        receipt = (
            read(receipt_path)
            if receipt_path.exists()
            else {
                "cost_usd": None,
                "cost_upper_usd": read(request)["reserve_usd"],
                "seconds": None,
            }
        )
        total["api_attempts"] += 1
        total["cost_known_usd"] += receipt["cost_usd"] or 0
        total["cost_upper_usd"] += receipt["cost_upper_usd"]
        total["unknown_cost_attempts"] += receipt["cost_usd"] is None
        total["api_seconds"] += receipt["seconds"] or 0
        response = request.with_name("response.json")
        usage = (read(response).get("usage") or {}) if response.exists() else {}
        for key in ("input_tokens", "output_tokens"):
            total[key] += usage.get(key, 0) or 0
        total["reasoning_tokens"] += (usage.get("output_tokens_details") or {}).get(
            "reasoning_tokens", 0
        ) or 0
    return total


def summary_table(rows):
    def fmt(value, spec):
        return "—" if value is None else format(value, spec)

    lines = [
        "| Method | Model | Dataset | Shot | Accuracy | Macro F1 | Errors | p50 ms | p95 ms | Cost range, USD |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        cells = [
            row["method"],
            row["model"],
            row["dataset"],
            str(row["shots"]),
            fmt(row["accuracy"], ".2%"),
            fmt(row["macro_f1"], ".2%"),
            str(row["errors"]),
            fmt(row["p50_ms"], ".3f"),
            fmt(row["p95_ms"], ".3f"),
            f"{row['cost_known_usd']:.4f}–{row['cost_upper_usd']:.4f}",
        ]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def report(output):
    rows = [
        {**read(p), **attempt_totals(output / "calls" / p.stem)}
        for p in sorted((output / "results").glob("*.json"))
    ]
    write_rows(output / "summary.jsonl", rows)
    totals = attempt_totals(output / "calls")
    text = f"""# Heuristic adapter evaluation

Run complete: {read(output / "run.json")["complete"]}. Completed groups: {len(rows)}/{plan()["result_groups"]}.

{summary_table(rows)}

Costs include every attempt, including failures: known ${totals["cost_known_usd"]:.4f};
conservative upper estimate ${totals["cost_upper_usd"]:.4f};
{totals["unknown_cost_attempts"]} attempts with unknown billed usage.

Seven GPT models compile with explicit high reasoning effort, 0/1/2 training examples,
and 48k initial output limits. Only truncation raises the next limit to 96k, then 128k.
At most three attempts; the first syntactically valid, loadable program is retained.
No correctness gate and no test-label feedback. Predictions that error count as incorrect;
uncompilable groups have null accuracy. Macro F1 averages over all declared labels.
OpenAI Decisions and OpenRouter Jev 1.13/1.14 classify the same test inputs directly,
using the same 0/1/2-shot training examples. Jev uses native `state`/`questions` requests;
its reported `usage.cost` takes precedence over token-price estimates.

Program latency includes input copying and output validation, without network calls.
Direct API latency includes failed request time but excludes retry backoff.
Cached replay durations come from recorded requests, not current wall time.
`api_seconds` is summed request time; it is not concurrent wall time.

`manifest.json` pins code, dependencies, datasets, training examples and test cohorts.
`programs/` contains generated source; `predictions/` contains per-example outputs.
`calls/` contains request payloads, responses, partial source and attempt receipts.
`data/` contains the frozen inputs, and `summary.jsonl` contains the full metrics.
Commit this run directory to GitHub with the evaluation code.
All generations are fresh for this run; resuming the same directory reuses only its records.

Tasks follow [dhruvmehra/jevbench](https://github.com/dhruvmehra/jevbench/tree/c983cc4a7dd9fc142ca3b6c7a813cae0e963c902):
[SST-2](https://huggingface.co/datasets/stanfordnlp/sst2),
[AG News](https://huggingface.co/datasets/fancyzhx/ag_news),
[Banking77](https://huggingface.co/datasets/legacy-datasets/banking77).
The fixed 300-example cohorts differ from upstream's historical 500-example Jev results;
no historical score is presented as a fresh measurement.
"""
    (output / "README.md").write_text(text, encoding="utf-8")
