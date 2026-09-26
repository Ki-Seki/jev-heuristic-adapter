"""Export a compact auditable result bundle and a single comparison table."""

import argparse
import html
import json
import random
from decimal import ROUND_FLOOR, Decimal
from pathlib import Path

from .experiment import sha256
from .run import HERE, percentile, read, score_rows, write


def break_even(cost, per_thousand):
    ratio = Decimal(str(cost)) * 1000 / Decimal(str(per_thousand))
    return int(ratio.to_integral_value(rounding=ROUND_FLOOR)) + 1


def paired_delta(first, second):
    assert [row["id"] for row in first] == [row["id"] for row in second]
    delta = [
        int(b["prediction"] == b["gold"]) - int(a["prediction"] == a["gold"])
        for a, b in zip(first, second)
    ]
    rng = random.Random(20260926)
    samples = [sum(rng.choices(delta, k=len(delta))) / len(delta) for _ in range(2000)]
    return {
        "pp": 100 * sum(delta) / len(delta),
        "conditional_95ci_pp": [100 * percentile(samples, x) for x in (0.025, 0.975)],
        "only_new_correct": sum(x == 1 for x in delta),
        "only_baseline_correct": sum(x == -1 for x in delta),
    }


def cost_of_calls(paths):
    costs = [read(p)["cost"] for p in paths]
    if any(c["usd"] is None for c in costs):
        raise ValueError("Cannot report total fees with missing usage")
    return {
        key: sum(c.get(key, 0) for c in costs)
        for key in ("usd", "upper_usd", "input_tokens", "output_tokens")
    }


def collect(output, data):
    specs = read(HERE / "specs.json")
    references = read(HERE / "jev-reference.json")
    freeze = read(output / "program-freeze.json")
    rows, programs, predictions = [], [], []
    for relative, expected in sorted(freeze.items()):
        path = output / relative
        trial = read(path)
        if sha256(trial) != expected:
            raise ValueError("Frozen candidate selection was modified")
        evaluated = read(path.with_name("evaluation.json"))
        spec = specs[trial["dataset"]]
        assert evaluated["metrics"] == score_rows(
            evaluated["predictions"], spec["question"]["criteria"]
        )
        directory = path.parent
        charged = list(directory.glob("call-*/response.json"))
        seconds = trial["phase_seconds"]
        if trial["arm"] == "feedback":
            charged.extend((directory.parent / "prompt").glob("call-*/response.json"))
            teacher = list(
                (output / "synthesis" / trial["dataset"]).glob("*/response.json")
            )
            charged.extend(teacher)
            seconds += read(directory.parent / "prompt" / "trial.json")["phase_seconds"]
            seconds += max(read(p)["finished_at"] for p in teacher) - min(
                read(p.with_name("started.json"))["at"] for p in teacher
            )
        condition = (
            f"{trial['model']}--{trial['dataset']}--{trial['repeat']}--{trial['arm']}"
        )
        baseline = read(directory.parent / "baseline" / "evaluation.json")
        candidate = trial["candidates"][trial["selected"]]
        costs = cost_of_calls(charged)
        rows.append(
            {
                "condition": condition,
                "model": trial["model"],
                "dataset": trial["dataset"],
                "arm": trial["arm"],
                **evaluated["metrics"],
                "delta": paired_delta(
                    baseline["predictions"], evaluated["predictions"]
                ),
                "compile_cost": costs,
                "cold_compile_seconds": seconds,
                "charged_requests": len(charged),
                "selected_round": trial["selected"],
                "synthetic_selection": {
                    k: candidate["selection"][k] for k in ("correct", "n")
                }
                if "selection" in candidate
                else None,
                "break_even_n": break_even(
                    costs["usd"], references[trial["dataset"]]["cost_per_1k_usd"]
                ),
            }
        )
        for item in trial["candidates"]:
            programs.append(
                {
                    "condition": condition,
                    "round": item["round"],
                    "selected": item["round"] == trial["selected"],
                    "source": item["result"]["text"],
                    "source_sha256": sha256(item["result"]["text"]),
                    "complete": item["result"]["complete"],
                    "feedback_score": {k: item["feedback"][k] for k in ("correct", "n")}
                    if "feedback" in item
                    else None,
                    "selection_score": {
                        k: item["selection"][k] for k in ("correct", "n")
                    }
                    if "selection" in item
                    else None,
                }
            )
        predictions.extend(
            {"condition": condition, **r} for r in evaluated["predictions"]
        )
    physical_calls = list(output.glob("**/response.json"))
    return {
        "rows": rows,
        "observations": read(output / "observations.json")
        if (output / "observations.json").exists()
        else [],
        "programs": programs,
        "predictions": predictions,
        "physical_requests": len(physical_calls),
        "actual_experiment_fee": cost_of_calls(physical_calls),
        "references": references,
        "data_manifest": read(data / "manifest.json"),
        "protocol": read(output / "protocol.json"),
        "environment": read(output / "environment.json"),
        "synthetic": {
            name: read(output / "synthesis" / name / "checks.json")
            for name in specs
            if (output / "synthesis" / name / "checks.json").exists()
        },
    }


def table(rows, references):
    columns = [
        "任务",
        "方案",
        "准确率",
        "较原 prompt",
        "Macro-F1",
        "运行错误",
        "编译 API 费",
        "编译秒数",
        "推理 p50 / p95 ms",
        "比 Jev 费用低的 N",
        "选中轮次",
    ]
    values = []
    for dataset in ("sst2", "agnews", "banking77"):
        ref = references[dataset]
        values.append(
            [
                dataset,
                "Jev 1.13 · 历史参考 / N=500",
                f"{ref['accuracy']:.1%}",
                "—",
                f"{ref['macro_f1']:.1%}",
                "0",
                "—",
                "—",
                f"{ref['latency_p50_ms']:.0f} / {ref['latency_p95_ms']:.0f}",
                "—",
                "—",
            ]
        )
        for row in sorted(
            (r for r in rows if r["dataset"] == dataset),
            key=lambda r: (
                r["model"],
                ("baseline", "prompt", "feedback").index(r["arm"]),
            ),
        ):
            name = {
                "baseline": "原 prompt",
                "prompt": "改进 prompt",
                "feedback": "prompt + 执行反馈",
            }[row["arm"]]
            values.append(
                [
                    dataset,
                    f"{row['model']} · {name}",
                    f"{row['accuracy']:.1%}",
                    f"{row['delta']['pp']:+.1f} pp",
                    f"{row['macro_f1']:.1%}",
                    str(row["errors"]),
                    f"${row['compile_cost']['usd']:.5f}",
                    f"{row['cold_compile_seconds']:.1f}",
                    f"{row['p50_ms']:.3f} / {row['p95_ms']:.3f}",
                    str(row["break_even_n"]),
                    str(row["selected_round"]),
                ]
            )
    return columns, values


def export(bundle, destination, arm=None):
    destination.mkdir(parents=True, exist_ok=True)
    keep = (
        {"baseline", "prompt"}
        if arm == "prompt"
        else {"baseline", "prompt", "feedback"}
    )
    rows = [r for r in bundle["rows"] if r["arm"] in keep]
    conditions = {r["condition"] for r in rows}
    summary = {
        k: v
        for k, v in bundle.items()
        if k not in {"programs", "predictions", "synthetic"}
    }
    summary["rows"] = rows
    write(destination / "summary.json", summary)
    if arm != "prompt":
        write(destination / "synthetic.json", bundle["synthetic"])
    for kind in ("programs", "predictions"):
        selected = [row for row in bundle[kind] if row["condition"] in conditions]
        (destination / f"{kind}.jsonl").write_text(
            "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in selected)
        )
    columns, values = table(rows, bundle["references"])
    notes = (
        "每个模型/任务/方案各运行一轮实验，high；3 个任务各 300 条新样本，排除上一轮 500 条及重复文本。"
        "反馈方案从同一个改进 prompt 程序出发，最多修订两轮，只按合成 selection 集选程序。"
        "编译费用和时延包含该方案独立冷启动所需的合成数据、初始程序和全部修订；合成数据在本次实验中共享，表中每次冷启动均全额计入。"
        "推理为本地 adapter 串行实测；零模型 API 费，CPU 成本未定价。Jev 为上游不同样本/环境的历史参考。"
        "费用回本不代表准确率相同。每种方案只运行一次，无法估计生成过程的波动；JSON 中的区间仅对冻结程序按测试输入进行 paired bootstrap。"
    )
    notes += " " + " ".join(bundle.get("observations", []))
    md = "# Compile experiment\n\n" + notes + "\n\n"
    md += (
        "| "
        + " | ".join(columns)
        + " |\n| "
        + " | ".join(["---"] * len(columns))
        + " |\n"
    )
    md += "\n".join("| " + " | ".join(row) + " |" for row in values) + "\n"
    md += f"\n共享实验总计 {bundle['physical_requests']} 次 API 请求，API 用量费用估算 ${bundle['actual_experiment_fee']['usd']:.5f}。这不是把上表重复计入的冷启动费用相加。\n"
    md += f"\n[Jev 历史结果]({bundle['references']['sst2']['source']}) · [API 价格](https://developers.openai.com/api/docs/pricing)\n"
    (destination / "RESULTS.md").write_text(md)
    markup = "<!doctype html><html lang='zh-CN'><meta charset='utf-8'><title>Compile benchmark</title><style>body{font:14px system-ui;margin:28px;color:#18232e}p{max-width:1400px;line-height:1.65}table{border-collapse:collapse;white-space:nowrap}th,td{padding:10px 13px;border:1px solid #dce2e8;text-align:right}th{background:#eef2f6;position:sticky;top:0}td:nth-child(-n+2){text-align:left}tr:nth-child(even){background:#f8fafb}</style><h2>Compile benchmark</h2>"
    markup += (
        "<p>"
        + html.escape(notes)
        + "</p><table><thead><tr>"
        + "".join(f"<th>{html.escape(x)}</th>" for x in columns)
        + "</tr></thead><tbody>"
    )
    markup += (
        "".join(
            "<tr>" + "".join(f"<td>{html.escape(x)}</td>" for x in row) + "</tr>"
            for row in values
        )
        + "</tbody></table></html>"
    )
    (destination / "COMPARISON.html").write_text(markup)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--arm", choices=("prompt", "feedback"))
    args = parser.parse_args()
    bundle = collect(args.run, args.data)
    export(bundle, args.output, args.arm)
    for row in bundle["rows"]:
        print(
            row["condition"], f"{row['accuracy']:.1%}", f"{row['delta']['pp']:+.1f} pp"
        )


if __name__ == "__main__":
    main()
