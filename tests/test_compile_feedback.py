"""Protect experiment isolation, candidate selection and cost accounting offline."""

from copy import deepcopy
from dataclasses import replace

import pytest

from benchmarks.compile_feedback.experiment import (
    assess,
    compile_trial,
    feedback,
    split_synthetic,
    text_key,
)
from benchmarks.compile_feedback.prepare import normalized_label_names, select_indices
from benchmarks.compile_feedback.report import break_even, paired_delta
from benchmarks.compile_feedback.run import (
    Calls,
    compile_one,
    evaluate_one,
    request_cost,
    score_rows,
    write,
)
from jev_heuristic_adapter._compiler import build_messages
from jev_heuristic_adapter.providers import ProviderResult

QUESTION = {"type": "choice", "criteria": {"yes": "Yes", "no": "No"}}


def result(answer="yes"):
    return ProviderResult(
        f"def predict(state): return {{'answer': {answer!r}}}",
        True,
        100,
        20,
        {
            "usage": {
                "input_tokens_details": {"cached_tokens": 20, "cache_write_tokens": 30}
            }
        },
    )


def test_feedback_uses_execution_and_never_receives_selection_text():
    replies = iter((result("no"), result("yes"), result("no")))
    sent = []

    def request(messages, index):
        sent.append(deepcopy(messages))
        return next(replies)

    trial = compile_trial(
        request,
        QUESTION,
        "Write Python",
        rounds=2,
        checks={
            "feedback": [{"state": "feedback input", "answer": "yes"}],
            "selection": [{"state": "secret selection input", "answer": "yes"}],
        },
    )
    assert len(sent) == 3
    assert trial["selected"] == 1  # The final revision regresses.
    assert "feedback input" in str(sent[1])
    assert "secret selection input" not in str(sent)
    assert trial["candidates"][0]["feedback"]["correct"] == 0


def test_feedback_reuses_exact_initial_candidate_and_ties_prefer_earliest():
    calls = []
    initial = result()

    def request(messages, index):
        calls.append(index)
        return result()

    examples = [{"state": "a", "answer": "yes"}]
    trial = compile_trial(
        request,
        QUESTION,
        "prompt",
        rounds=2,
        initial=initial,
        checks={"feedback": examples, "selection": [{"state": "b", "answer": "yes"}]},
    )
    assert calls == [1, 2]
    assert trial["selected"] == 0
    assert trial["candidates"][0]["result"]["text"] == initial.text


@pytest.mark.parametrize("rounds", [-1, 3])
def test_round_budget_is_enforced(rounds):
    with pytest.raises(ValueError, match="zero, one or two"):
        compile_trial(None, QUESTION, "prompt", rounds=rounds)


def test_feedback_cannot_run_without_separate_checks():
    with pytest.raises(ValueError, match="nonempty"):
        compile_trial(None, QUESTION, "prompt", rounds=1)


@pytest.mark.parametrize(
    "source",
    [
        "broken syntax",
        "def predict(state): return {'answer': 'unknown'}",
        "def predict(state): raise ValueError('failed')",
    ],
)
def test_invalid_source_or_predictions_count_as_errors(source):
    scored = assess(
        QUESTION,
        build_messages(QUESTION),
        replace(result(), text=source),
        [{"state": "hello", "answer": "yes"}],
    )
    assert scored["correct"] == 0
    assert scored["n"] == 1
    assert scored["rows"][0]["error"] is not None


def test_feedback_balances_error_examples_across_labels():
    rows = [
        {"state": str(i), "answer": "yes", "prediction": "no", "error": None}
        for i in range(10)
    ] + [{"state": "last", "answer": "no", "prediction": "yes", "error": None}]
    observed = feedback({"correct": 0, "n": 11, "rows": rows}, limit=2)
    assert {row["answer"] for row in observed["failed_examples"]} == {"yes", "no"}
    assert sum(item["count"] for item in observed["confusions"]) == 11


def synthetic_rows():
    return [
        {"state": f"{label} {i}", "answer": label}
        for label in ("yes", "no")
        for i in range(6)
    ]


def test_synthetic_splits_are_disjoint_balanced_and_reproducible():
    rows = synthetic_rows()
    split = split_synthetic(rows, QUESTION["criteria"], 6)
    assert len(split["feedback"]) == 8
    assert len(split["selection"]) == 4
    assert {text_key(x["state"]) for x in split["feedback"]}.isdisjoint(
        text_key(x["state"]) for x in split["selection"]
    )
    assert split == split_synthetic(rows, QUESTION["criteria"], 6)


@pytest.mark.parametrize("bad", ["duplicate", "missing", "wrong_label", "empty"])
def test_bad_synthetic_data_is_rejected(bad):
    rows = synthetic_rows()
    if bad == "duplicate":
        rows[1]["state"] = rows[0]["state"].upper() + "  "
    elif bad == "missing":
        rows.pop()
    elif bad == "wrong_label":
        rows[0]["answer"] = "unknown"
    else:
        rows[0]["state"] = " "
    with pytest.raises(ValueError):
        split_synthetic(rows, QUESTION["criteria"], 6)


def test_holdout_excludes_previous_ids_and_duplicate_texts():
    texts = [f"Sentence {i}" for i in range(1000)]
    texts[999] = texts[0].upper() + "  "
    selected, old = select_indices(texts)
    assert len(selected) == 300
    assert set(selected).isdisjoint(old)
    assert {text_key(texts[i]) for i in selected}.isdisjoint(
        text_key(texts[i]) for i in old
    )
    assert len({text_key(texts[i]) for i in selected}) == 300
    assert (selected, old) == select_indices(texts)


def test_hf_label_names_keep_upstream_normalization_and_order():
    assert normalized_label_names(
        ["Refund_not_showing_up", "reverted_card_payment?", "Sci/Tech"]
    ) == ["refund_not_showing_up", "reverted_card_payment", "sci_tech"]


def test_cost_accounts_for_cached_reads_writes_and_output():
    cost = request_cost(result(), "gpt-6-sol")
    assert cost["usd"] == pytest.approx((50 * 2 + 20 * 0.2 + 30 * 2.5 + 20 * 10) / 1e6)
    assert cost["upper_usd"] == cost["usd"]
    unknown_writes = replace(
        result(), raw={"usage": {"input_tokens_details": {"cached_tokens": 20}}}
    )
    estimate = request_cost(unknown_writes, "gpt-6-sol")
    assert estimate["upper_usd"] > estimate["usd"]


def test_interrupted_provider_call_is_not_resubmitted(tmp_path):
    calls = Calls.__new__(Calls)
    calls.providers = {}  # Any provider access would fail this test.
    write(tmp_path / "started.json", {"model": "gpt-6-sol"})
    with pytest.raises(RuntimeError, match="refusing automatic resubmission"):
        calls.request("gpt-6-sol", [], tmp_path)


def test_real_adapter_evaluates_without_remote_provider_calls():
    trial = compile_trial(lambda messages, index: result(), QUESTION, "prompt")
    evaluation = evaluate_one(
        trial,
        {"question": QUESTION},
        [
            {"id": "one", "state": "hi", "answer": "yes"},
            {"id": "two", "state": "bye", "answer": "no"},
        ],
    )
    assert evaluation["metrics"]["accuracy"] == 0.5
    assert evaluation["metrics"]["macro_f1"] == pytest.approx(1 / 3)
    assert evaluation["metrics"]["errors"] == 0


def test_metric_denominator_includes_failures_and_absent_labels():
    rows = [
        {"gold": "yes", "prediction": "yes", "error": None, "latency_ms": 1},
        {"gold": "no", "prediction": None, "error": "failed", "latency_ms": 3},
    ]
    measured = score_rows(rows, ["yes", "no", "absent"])
    assert measured["accuracy"] == 0.5
    assert measured["macro_f1"] == pytest.approx(1 / 3)
    assert measured["errors"] == 1
    assert measured["p50_ms"] == 2


def test_break_even_requires_strictly_lower_api_fees():
    assert break_even(0.01, 0.01) == 1001
    assert break_even(0.01001, 0.01) == 1002


def test_paired_delta_matches_inputs_and_rejects_unpaired_results():
    baseline = [{"id": "a", "gold": "yes", "prediction": "no"}]
    improved = [{"id": "a", "gold": "yes", "prediction": "yes"}]
    observed = paired_delta(baseline, improved)
    assert observed["pp"] == 100
    assert observed["conditional_95ci_pp"] == [100, 100]
    with pytest.raises(AssertionError):
        paired_delta(baseline, [{**improved[0], "id": "different"}])


def test_prompt_only_experiment_never_loads_synthetic_data_or_refines(tmp_path):
    class FakeCalls:
        def __init__(self):
            self.count = 0

        def request(self, model, messages, directory):
            self.count += 1
            assert model == "gpt-6-luna"
            return result()

    calls = FakeCalls()
    compile_one(
        calls, tmp_path, "task", {"question": QUESTION}, "gpt-6-luna", 0, "prompt"
    )
    assert calls.count == 2  # One baseline and one alternative prompt.
    assert len(list(tmp_path.glob("trials/*/*/trial.json"))) == 2
    assert not (tmp_path / "synthesis").exists()
    assert not list(tmp_path.glob("trials/*/feedback"))
