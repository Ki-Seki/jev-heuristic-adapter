"""OpenRouter routing and billing checks, using an in-memory HTTP transport."""

import json
import sys
from types import SimpleNamespace

import pytest

from evals.api import API, BudgetExceeded, cost, decision_answer, jev_payload
from evals.data import DIRECT_MODELS, read
from evals.run import decision_one

MODELS = DIRECT_MODELS["jev"]
QUESTION = {
    "type": "choice",
    "instructions": "Choose one.",
    "criteria": {"yes": "Yes", "no": "No"},
}
EXAMPLES = [
    {"state": "training A", "answer": "yes"},
    {"state": "training B", "answer": "no"},
]


@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize("shots", [0, 1, 2])
def test_native_payload_preserves_question_and_exact_training_examples(model, shots):
    payload = jev_payload(model, QUESTION, EXAMPLES[:shots], "test input")
    assert set(payload) == {"model", "state", "questions"}
    assert payload["model"] == model and payload["state"] == "test input"
    question = payload["questions"]["label"]
    assert question["criteria"] == QUESTION["criteria"]
    if shots:
        assert (
            json.loads(question["instructions"].split("Examples:\n")[1])
            == EXAMPLES[:shots]
        )
    else:
        assert question == QUESTION
    assert QUESTION["instructions"] == "Choose one."


@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize("billed", [0, 0.0000123])
def test_reported_cost_takes_precedence_even_without_token_usage(model, billed):
    assert cost({"usage": {"cost": billed}}, model, "jev", 1) == (billed, billed)


@pytest.mark.parametrize("model", MODELS)
def test_cost_fallback_and_missing_usage(model):
    assert cost(
        {"usage": {"input_tokens": 1000, "output_tokens": 9000}}, model, "jev", 1
    ) == pytest.approx((0.000042, 0.000042))
    assert cost({}, model, "jev", 1) == (None, 1)
    for invalid in (-1, "unknown", float("nan")):
        assert cost({"usage": {"cost": invalid}}, model, "jev", 1) == (None, 1)


@pytest.mark.parametrize(
    "answers",
    [None, [], {"label": {"type": "refusal", "choice": "yes"}}, {"label": "yes"}],
)
def test_missing_or_unexpected_answers_are_not_accepted(answers):
    assert decision_answer({"answers": answers}, "jev") is None


@pytest.fixture
def clients():
    openai = pytest.importorskip("openai")
    httpx = pytest.importorskip("httpx2")
    created = []

    def create(handler):
        def forbidden(request):
            pytest.fail("Jev must not use the OpenAI endpoint or credential")

        first = openai.OpenAI(
            api_key="openai-only",
            max_retries=0,
            base_url="https://api.openai.com/v1",
            http_client=httpx.Client(
                transport=httpx.MockTransport(forbidden), trust_env=False
            ),
        )
        second = openai.OpenAI(
            api_key="router-only",
            max_retries=0,
            base_url="https://openrouter.ai/api",
            http_client=httpx.Client(
                transport=httpx.MockTransport(handler), trust_env=False
            ),
        )
        created.extend([first, second])
        return first, second, httpx

    yield create
    for client in created:
        client.close()


@pytest.mark.parametrize("model", MODELS)
def test_real_sdk_uses_native_route_separate_key_and_replays_records(
    tmp_path, clients, model
):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "model": model,
                "answers": {
                    "label": {
                        "type": "choice",
                        "choice": "yes",
                        "probabilities": {"yes": 0.9, "no": 0.1},
                    }
                },
                "usage": {"input_tokens": 10, "cost": 0.000123},
            },
        )

    first, second, httpx = clients(handler)
    caller = API(first, tmp_path, 1, openrouter=second)
    sample = {"id": "test:1", "state": "held out", "answer": "no"}
    row = decision_one(caller, "job", QUESTION, EXAMPLES, sample, "jev", model)
    assert row["prediction"] == "yes" and row["error"] is None
    assert caller.used == pytest.approx(0.000123)
    assert len(requests) == 1
    assert str(requests[0].url) == "https://openrouter.ai/api/alpha/decisions"
    assert requests[0].headers["authorization"] == "Bearer router-only"
    payload = json.loads(requests[0].content)
    assert payload == jev_payload(model, QUESTION, EXAMPLES, "held out")
    assert "gold" not in payload
    assert decision_one(caller, "job", QUESTION, EXAMPLES, sample, "jev", model) == row
    assert len(requests) == 1
    request = (tmp_path / "calls/job/test-1/1/request.json").read_text(encoding="utf-8")
    assert "router-only" not in request and "openai-only" not in request
    receipt = read(tmp_path / "calls/job/test-1/1/receipt.json")
    assert receipt["cost_usd"] == receipt["cost_upper_usd"] == 0.000123
    # Both services draw from the same ledger, including already recorded Jev calls.
    caller.budget = caller.used
    with pytest.raises(BudgetExceeded):
        caller.call(
            "compile",
            "gpt-6-luna",
            {"max_output_tokens": 1},
            tmp_path / "calls/other/1",
        )


def test_rate_limit_and_invalid_choice_share_three_attempts(
    tmp_path, clients, monkeypatch
):
    requests = []
    monkeypatch.setattr("evals.run.time.sleep", lambda _: None)

    def handler(request):
        requests.append(json.loads(request.content))
        if len(requests) == 1:
            return httpx.Response(
                429, json={"error": {"message": "limited", "type": "rate_limit_error"}}
            )
        label = "invalid" if len(requests) == 2 else "yes"
        return httpx.Response(
            200,
            json={
                "answers": {"label": {"type": "choice", "choice": label}},
                "usage": {"cost": 0.00001},
            },
        )

    first, second, httpx = clients(handler)
    caller = API(first, tmp_path, 1, openrouter=second)
    sample = {"id": "test:1", "state": "held out", "answer": "no"}
    row = decision_one(caller, "job", QUESTION, [], sample, "jev", MODELS[0])
    assert row["prediction"] == "yes" and len(requests) == 3
    assert requests[0] == requests[1] == requests[2]
    receipts = list((tmp_path / "calls").rglob("receipt.json"))
    assert len(receipts) == 3
    assert sum(read(p)["cost_usd"] or 0 for p in receipts) == pytest.approx(0.00002)


def test_missing_router_key_stops_before_any_client_or_model_call(
    tmp_path, monkeypatch
):
    import evals.run as runner

    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setattr(runner, "verify", lambda _: {})
    monkeypatch.setitem(
        sys.modules,
        "openai",
        SimpleNamespace(
            OpenAI=lambda **kwargs: pytest.fail("No client should be created")
        ),
    )
    with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
        runner.run(tmp_path, 1, 1)
