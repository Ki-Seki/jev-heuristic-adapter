"""Offline protocol tests: requests, retries, costs, scoring, and publication."""

import json
import sys
import tarfile
from concurrent.futures import ThreadPoolExecutor
from contextlib import nullcontext
from threading import Event
from types import SimpleNamespace

import pytest

from evals import api, data, results
from evals.__main__ import main
from evals.run import compile_job, decision_one, evaluate_program

QUESTION = {
    "type": "choice",
    "instructions": "Choose yes or no.",
    "criteria": {"yes": "Yes", "no": "No"},
}
SOURCE = 'def predict(state): return {"answer": "yes"}'
MODEL = "gpt-6.2-astra"


def response(source=SOURCE, status="completed"):
    return {
        "status": status,
        "model": MODEL,
        "output": [{"content": [{"type": "output_text", "text": source}]}],
        "usage": {
            "input_tokens": 100,
            "output_tokens": 200,
            "input_tokens_details": {"cached_tokens": 20, "cache_write_tokens": 10},
            "output_tokens_details": {"reasoning_tokens": 50},
        },
    }


@pytest.fixture
def sdk_factory():
    def make(responses):
        queue = iter(responses)
        calls = []

        def next_response(payload):
            calls.append(payload)
            value = next(queue)
            if isinstance(value, Exception):
                raise value
            return value

        def create(**payload):
            raw = next_response(payload)
            value = SimpleNamespace(model_dump=lambda **kwargs: raw)
            return nullcontext(
                iter(
                    [
                        SimpleNamespace(
                            type="response.output_text.delta",
                            delta=api.output_text(raw),
                        ),
                        SimpleNamespace(
                            type=f"response.{raw['status']}", response=value
                        ),
                    ]
                )
            )

        def post(path, cast_to, body):
            assert path == "/decisions" and cast_to is dict
            return next_response(body)

        return SimpleNamespace(
            responses=SimpleNamespace(create=create),
            post=post,
            calls=calls,
            close=lambda: None,
        )

    return make


@pytest.fixture(autouse=True)
def no_backoff(monkeypatch):
    monkeypatch.setattr("evals.run.time.sleep", lambda _: None)


@pytest.fixture
def task():
    return {
        "question": QUESTION,
        "examples": [{"id": "train:1", "state": "training", "answer": "no"}],
        "test": [{"id": "test:1", "state": "held out", "answer": "no"}],
    }


def test_plan_has_no_api_calls_or_downloads(capsys):
    main(["plan"])
    plan = json.loads(capsys.readouterr().out)
    assert len(plan["models"]) == 7
    assert plan["compile_jobs"] == 63 and plan["decisions_requests"] == 2700
    assert plan["reasoning_effort"] == "high"
    assert plan["token_caps"] == [48000, 96000, 128000]


def test_call_records_and_replays_without_resending(tmp_path, sdk_factory):
    sdk = sdk_factory([response()])
    caller = api.API(sdk, tmp_path, 10)
    payload = api.generation_payload(
        MODEL, [{"role": "user", "content": "Write a program"}], 48000
    )
    folder = tmp_path / "calls" / "job" / "1"
    raw, receipt = caller.call("compile", MODEL, payload, folder)
    assert sdk.calls[0]["reasoning"] == {"effort": "high"}
    assert sdk.calls[0]["stream"] is True and sdk.calls[0]["store"] is False
    assert sdk.calls[0]["service_tier"] == "default"
    assert raw == response()
    assert caller.used == pytest.approx(receipt["cost_upper_usd"])
    resumed = api.API(sdk, tmp_path, 10)
    assert resumed.call("compile", MODEL, payload, folder) == (raw, receipt)
    assert len(sdk.calls) == 1
    with pytest.raises(ValueError, match="different API request"):
        resumed.call("compile", MODEL, {**payload, "max_output_tokens": 96000}, folder)


def test_cost_includes_cache_writes_and_free_decision_outputs():
    assert api.cost(response(), MODEL, "compile", 100) == pytest.approx(
        (0.008668, 0.008668)
    )
    raw = response()
    del raw["usage"]["input_tokens_details"]["cache_write_tokens"]
    low, high = api.cost(raw, MODEL, "compile", 100)
    assert high > low
    raw["usage"]["input_tokens_details"]["cache_write_tokens"] = None
    assert api.cost(raw, MODEL, "compile", 100) == (low, high)
    assert api.cost(response(), "gpt-6-luna", "decisions", 100)[0] == pytest.approx(
        0.00000845
    )
    assert api.cost({}, MODEL, "compile", 100) == (None, 100)
    raw["usage"]["output_tokens"] = None
    assert api.cost(raw, MODEL, "compile", 100) == (None, 100)


def test_budget_stops_before_request_and_unknown_failures_reserve_cost(
    tmp_path, sdk_factory
):
    sdk = sdk_factory([RuntimeError("secret must never appear in artifacts")])
    payload = api.generation_payload(MODEL, [], 48000)
    folder = tmp_path / "calls" / "job" / "1"
    with pytest.raises(api.BudgetExceeded):
        api.API(sdk, tmp_path, 0.01).call("compile", MODEL, payload, folder)
    assert not sdk.calls and not folder.exists()
    caller = api.API(sdk, tmp_path, 10)
    with pytest.raises(api.CallError, match="RuntimeError"):
        caller.call("compile", MODEL, payload, folder)
    receipt = data.read(folder / "receipt.json")
    assert receipt["cost_usd"] is None and receipt["cost_upper_usd"] > 1.9
    assert "secret" not in (folder / "receipt.json").read_text()
    resumed = api.API(sdk, tmp_path, 10)
    assert resumed.used == caller.used
    with pytest.raises(api.CallError):
        resumed.call("compile", MODEL, payload, folder)
    assert len(sdk.calls) == 1


@pytest.mark.parametrize("saved_response", [False, True])
def test_interrupted_attempt_is_recovered_without_duplicate_call(
    tmp_path, sdk_factory, saved_response
):
    folder = tmp_path / "calls" / "job" / "1"
    payload = api.generation_payload(MODEL, [], 48000)
    data.write(
        folder / "request.json",
        {"method": "compile", "model": MODEL, "payload": payload, "reserve_usd": 2},
    )
    if saved_response:
        data.write(folder / "response.json", response())
    sdk = sdk_factory([])
    caller = api.API(sdk, tmp_path, 10)
    if saved_response:
        assert caller.call("compile", MODEL, payload, folder)[0] == response()
        assert caller.used < 2
    else:
        with pytest.raises(api.CallError, match="InterruptedCall"):
            caller.call("compile", MODEL, payload, folder)
        assert caller.used == 2
    assert sdk.calls == []


def test_three_truncations_use_48_96_128k(tmp_path, sdk_factory, task):
    truncated = {
        **response(status="incomplete"),
        "incomplete_details": {"reason": "max_output_tokens"},
    }
    sdk = sdk_factory([truncated, truncated, response()])
    caller = api.API(sdk, tmp_path, 50)
    compiled = compile_job(caller, MODEL, "toy", 1, task)
    assert compiled["attempts"] == 3 and compiled["error"] is None
    assert [x["max_output_tokens"] for x in sdk.calls] == [48000, 96000, 128000]
    for call in sdk.calls:
        message = json.loads(call["input"][1]["content"])
        assert message["task_definition"]["question"] == QUESTION
        assert message["examples"] == [{"state": "training", "answer": "no"}]
        assert "held out" not in json.dumps(call)
    assert compile_job(caller, MODEL, "toy", 1, task) == compiled
    assert len(sdk.calls) == 3


def test_syntax_and_load_failures_retry_without_raising_token_cap(
    tmp_path, sdk_factory, task
):
    sdk = sdk_factory(
        [
            response("invalid python !"),
            response('raise RuntimeError("load failed")\n' + SOURCE),
            response(),
        ]
    )
    compiled = compile_job(api.API(sdk, tmp_path, 10), MODEL, "toy", 0, task)
    assert compiled["error"] is None and compiled["attempts"] == 3
    assert {x["max_output_tokens"] for x in sdk.calls} == {48000}


@pytest.mark.parametrize(
    "source", [SOURCE, 'def predict(state): return {"answer": "invalid"}']
)
def test_wrong_answers_and_prediction_errors_never_trigger_generation(
    tmp_path, sdk_factory, task, source
):
    sdk = sdk_factory([response(source)])
    compiled = compile_job(api.API(sdk, tmp_path, 10), MODEL, "toy", 1, task)
    evaluate_program(tmp_path, compiled, task)
    result = data.read(tmp_path / "results" / f"{compiled['job']}.json")
    assert result["accuracy"] == 0 and len(sdk.calls) == 1
    assert result["errors"] == (0 if source == SOURCE else 1)
    evaluate_program(tmp_path, compiled, task)
    assert len(sdk.calls) == 1


def test_failed_compilation_stops_at_three_and_counts_every_fee(
    tmp_path, sdk_factory, task
):
    sdk = sdk_factory([response("bad !")] * 3)
    compiled = compile_job(api.API(sdk, tmp_path, 10), MODEL, "toy", 0, task)
    evaluate_program(tmp_path, compiled, task)
    result = data.read(tmp_path / "results" / f"{compiled['job']}.json")
    assert result["accuracy"] is None and result["errors"] == 1
    totals = results.attempt_totals(tmp_path / "calls")
    assert totals["api_attempts"] == 3
    assert totals["cost_known_usd"] == pytest.approx(3 * 0.008668)
    assert totals["reasoning_tokens"] == 150


def test_decisions_retries_invalid_answer_with_no_gold_label_feedback(
    tmp_path, sdk_factory, task
):
    sdk = sdk_factory(
        [
            {"answers": []},
            {
                "answers": [{"name": "label", "choice": "yes"}],
                "usage": {"input_tokens": 50},
            },
        ]
    )
    caller = api.API(sdk, tmp_path, 10)
    row = decision_one(caller, "decision-job", QUESTION, [], task["test"][0])
    assert row["prediction"] == "yes" and row["gold"] == "no"
    assert len(sdk.calls) == 2 and sdk.calls[0] == sdk.calls[1]
    assert sdk.calls[0]["input"] == [{"role": "user", "content": "held out"}]
    assert "reasoning" not in sdk.calls[0] and "max_output_tokens" not in sdk.calls[0]


def test_nonretryable_auth_error_aborts_immediately(tmp_path, sdk_factory, task):
    error = RuntimeError("unauthorized")
    error.status_code = 401
    sdk = sdk_factory([error])
    caller = api.API(sdk, tmp_path, 10)
    with pytest.raises(api.CallError):
        compile_job(caller, MODEL, "toy", 0, task)
    assert len(sdk.calls) == 1


def test_metrics_keep_errors_in_denominator_and_all_declared_labels():
    rows = [
        {"gold": "a", "prediction": "a", "error": None, "latency_ms": 1},
        {"gold": "b", "prediction": None, "error": "failed", "latency_ms": 3},
    ]
    metrics = results.score(rows, ["a", "b", "absent"])
    assert metrics == {
        "n": 2,
        "accuracy": 0.5,
        "macro_f1": 1 / 3,
        "errors": 1,
        "p50_ms": 2,
        "p95_ms": 3,
    }


def test_prepare_pins_sources_and_rejects_data_changes(tmp_path, monkeypatch):
    class Dataset:
        features = {"label": SimpleNamespace(names=["yes", "no"])}

        def __init__(self, prefix):
            self.rows = [{"text": f"{prefix} {i}", "label": i % 2} for i in range(900)]

        def __len__(self):
            return len(self.rows)

        def __getitem__(self, key):
            return (
                [r[key] for r in self.rows] if isinstance(key, str) else self.rows[key]
            )

    train, test = Dataset("train"), Dataset("test")
    rows = [
        {
            "id": f"toy:test:{i}",
            "state": test[i]["text"],
            "answer": ("yes", "no")[i % 2],
        }
        for i in data.select_indices(test["text"])
    ]
    calls = []

    def loader(repo, **kwargs):
        calls.append((repo, kwargs))
        return train if kwargs["split"] == "train" else test

    monkeypatch.setitem(sys.modules, "datasets", SimpleNamespace(load_dataset=loader))
    monkeypatch.setattr(data, "version", lambda _: "test")
    monkeypatch.setattr(
        data,
        "TASKS",
        {
            "toy": {
                "hf_repo": "org/toy",
                "hf_revision": "frozen",
                "split": "test",
                "text_field": "text",
                "source_rows": 900,
                "label_order": ["yes", "no"],
                "question": QUESTION,
                "example_indices": [0, 1],
                "test_sha256": data.digest(rows),
            }
        },
    )
    output = tmp_path / "fresh"
    data.prepare(output)
    assert len(data.read(output / "data/toy.json")["test"]) == 300
    assert all(
        kwargs["revision"] == "frozen" and kwargs["token"] is False
        for _, kwargs in calls
    )
    assert data.verify(output)["reasoning_effort"] == "high"
    with pytest.raises(FileExistsError):
        data.prepare(output)
    data.write(output / "data/toy.json", {})
    with pytest.raises(ValueError, match="Prepared data changed"):
        data.verify(output)
    monkeypatch.setattr(data, "source_hashes", lambda: {})
    with pytest.raises(ValueError, match="Source or lockfile"):
        data.verify(output)


def test_selection_is_deterministic_deduplicated_and_requires_enough_rows():
    texts = [f"sentence {i}" for i in range(1000)]
    texts += [" SENTENCE 1 "] * 100
    selected = data.select_indices(texts)
    assert selected == data.select_indices(texts) and len(selected) == 300
    assert len({data.text_key(texts[i]) for i in selected}) == 300
    with pytest.raises(ValueError, match="Not enough"):
        data.select_indices(texts[:10])


def test_upload_only_approved_artifacts_and_never_creates_repo(tmp_path, monkeypatch):
    output = tmp_path / "run-name"
    data.write(output / "run.json", {"complete": False})
    data.write(output / "calls/job/1/request.json", {"reserve_usd": 1})
    (output / ".env").write_text("a private value")
    (output / "calls/job/1/unrelated.txt").write_text("unrelated")
    results.report(output)
    uploads = []
    monkeypatch.setitem(
        sys.modules,
        "huggingface_hub",
        SimpleNamespace(
            HfApi=lambda: SimpleNamespace(
                upload_folder=lambda **kwargs: uploads.append(kwargs),
                file_exists=lambda *args, **kwargs: True,
            )
        ),
    )
    results.upload(output, "owner/chosen-name")
    assert uploads[0]["repo_id"] == "owner/chosen-name"
    assert (
        uploads[0]["repo_type"] == "dataset"
        and uploads[0]["path_in_repo"] == "run-name"
    )
    assert ".env" not in uploads[0]["allow_patterns"]
    with tarfile.open(output / "calls.tar.gz") as archive:
        assert archive.getnames() == ["calls/job/1/request.json"]
    assert "Run complete: False" in (output / "README.md").read_text()
    with pytest.raises(ValueError, match="No evaluation"):
        results.upload(tmp_path / "empty", "owner/unused")


def test_complete_offline_run_and_resume(tmp_path, monkeypatch, sdk_factory, task):
    import evals.run as runner

    sdk = sdk_factory(
        [
            response(),
            {
                "answers": [{"name": "label", "choice": "no"}],
                "usage": {"input_tokens": 50},
            },
        ]
    )
    configs = []

    def client(**kwargs):
        configs.append(kwargs)
        return sdk

    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=client))
    monkeypatch.setattr(runner, "verify", lambda _: {})
    monkeypatch.setattr(runner, "MODELS", [MODEL])
    monkeypatch.setattr(runner, "TASKS", {"toy": {}})
    monkeypatch.setattr(runner, "SHOTS", [0])
    data.write(tmp_path / "data/toy.json", task)
    runner.run(tmp_path, 10, 1)
    assert data.read(tmp_path / "run.json")["complete"] is True
    summary = [
        json.loads(line)
        for line in (tmp_path / "summary.jsonl").read_text().splitlines()
    ]
    assert [row["accuracy"] for row in summary] == [0, 1]
    assert configs[0]["max_retries"] == 0 and configs[0]["timeout"] == 1800
    runner.run(tmp_path, 10, 1)
    assert len(sdk.calls) == 2


def test_budget_stop_writes_partial_report(tmp_path, monkeypatch, sdk_factory, task):
    import evals.run as runner

    sdk = sdk_factory([])
    monkeypatch.setitem(
        sys.modules, "openai", SimpleNamespace(OpenAI=lambda **kwargs: sdk)
    )
    monkeypatch.setattr(runner, "verify", lambda _: {})
    monkeypatch.setattr(runner, "MODELS", [MODEL])
    monkeypatch.setattr(runner, "TASKS", {"toy": {}})
    monkeypatch.setattr(runner, "SHOTS", [0])
    data.write(tmp_path / "data/toy.json", task)
    with pytest.raises(api.BudgetExceeded):
        runner.run(tmp_path, 0.001, 1)
    assert not sdk.calls
    assert data.read(tmp_path / "run.json")["complete"] is False
    assert (tmp_path / "summary.jsonl").exists()


@pytest.mark.parametrize("status, retryable", [(429, True), (500, True), (401, False)])
def test_decision_api_errors_obey_three_total_attempts(
    tmp_path, sdk_factory, task, status, retryable
):
    error = RuntimeError("API error")
    error.status_code = status
    sdk = sdk_factory([error] * 3)
    caller = api.API(sdk, tmp_path, 10)
    if retryable:
        row = decision_one(caller, "job", QUESTION, [], task["test"][0])
        assert row["prediction"] is None and row["error"]
        assert len(sdk.calls) == 3
    else:
        with pytest.raises(api.CallError):
            decision_one(caller, "job", QUESTION, [], task["test"][0])
        assert len(sdk.calls) == 1


def test_actual_sdk_serializes_both_endpoints_with_mock_transport(tmp_path):
    openai = pytest.importorskip("openai")
    httpx = pytest.importorskip("httpx2")
    requests = []

    def handler(request):
        requests.append((request.url.path, json.loads(request.content)))
        if request.url.path == "/v1/responses":
            body = {
                **response(),
                "id": "resp_fixture",
                "object": "response",
                "created_at": 0,
            }
            event = json.dumps({"type": "response.completed", "response": body})
            return httpx.Response(
                200,
                content=f"event: response.completed\ndata: {event}\n\n".encode(),
                headers={"content-type": "text/event-stream"},
            )
        return httpx.Response(
            200,
            json={
                "answers": [{"name": "label", "choice": "yes"}],
                "usage": {"input_tokens": 10},
            },
        )

    sdk = openai.OpenAI(
        api_key="offline-test",
        max_retries=0,
        base_url="https://api.example.invalid/v1",
        http_client=httpx.Client(
            transport=httpx.MockTransport(handler), trust_env=False
        ),
    )
    try:
        caller = api.API(sdk, tmp_path, 10)
        caller.call(
            "compile",
            MODEL,
            api.generation_payload(MODEL, [], 48000),
            tmp_path / "calls/c/1",
        )
        examples = [{"state": "training", "answer": "yes"}]
        caller.call(
            "decisions",
            "gpt-6-luna",
            api.decision_payload(QUESTION, examples, "input"),
            tmp_path / "calls/d/1",
        )
    finally:
        sdk.close()
    assert [path for path, _ in requests] == ["/v1/responses", "/v1/decisions"]
    assert requests[0][1]["reasoning"] == {"effort": "high"}
    assert requests[1][1]["input"][0]["role"] == "developer"


def test_stream_failure_keeps_partial_source(tmp_path):
    folder = tmp_path / "calls/c/1"

    def events():
        yield SimpleNamespace(type="response.output_text.delta", delta="def predict(")

    sdk = SimpleNamespace(
        responses=SimpleNamespace(create=lambda **kwargs: nullcontext(events()))
    )
    caller = api.API(sdk, tmp_path, 10)
    with pytest.raises(api.CallError, match="RuntimeError"):
        caller.call("compile", MODEL, api.generation_payload(MODEL, [], 48000), folder)
    assert (folder / "partial.py").read_text() == "def predict("
    assert data.read(folder / "receipt.json")["cost_usd"] is None


def test_cli_routes_without_implicitly_running_eval(tmp_path, monkeypatch):
    import evals.__main__ as cli
    import evals.run as runner

    actions = []
    monkeypatch.setattr(
        cli, "prepare", lambda output: actions.append(("prepare", output))
    )
    monkeypatch.setattr(runner, "run", lambda *args: actions.append(("run", args)))
    monkeypatch.setattr(
        results, "upload", lambda *args: actions.append(("upload", args))
    )
    output = str(tmp_path / "new")
    main(["prepare", "--output", output])
    assert [a[0] for a in actions] == ["prepare"]
    main(["run", "--output", output, "--budget-usd", "10"])
    main(["upload", "--output", output, "--repo-id", "owner/name"])
    assert [a[0] for a in actions] == ["prepare", "run", "upload"]
    for value in ("0", "-1", "nan", "inf"):
        with pytest.raises(SystemExit):
            main(["run", "--output", output, "--budget-usd", value])


def test_upload_adds_dataset_card_only_when_missing(tmp_path, monkeypatch):
    (tmp_path / "summary.jsonl").write_text("")
    uploads = []
    remote = SimpleNamespace(
        upload_folder=lambda **kwargs: "commit-url",
        file_exists=lambda *args, **kwargs: False,
        upload_file=lambda **kwargs: uploads.append(kwargs),
    )
    monkeypatch.setitem(
        sys.modules, "huggingface_hub", SimpleNamespace(HfApi=lambda: remote)
    )
    assert results.upload(tmp_path, "owner/chosen") == "commit-url"
    assert uploads[0]["path_in_repo"] == "README.md"
    assert b"*/summary.jsonl" in uploads[0]["path_or_fileobj"]


def test_in_flight_calls_reserve_budget_atomically(tmp_path, sdk_factory):
    entered, release = Event(), Event()
    sdk = sdk_factory([response()])
    generate = sdk.responses.create

    def blocked(**kwargs):
        entered.set()
        assert release.wait(5)
        return generate(**kwargs)

    sdk.responses.create = blocked
    caller = api.API(sdk, tmp_path, 3)
    payload = api.generation_payload(MODEL, [], 48000)
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(
            caller.call, "compile", MODEL, payload, tmp_path / "calls/a/1"
        )
        assert entered.wait(5)
        try:
            with pytest.raises(api.BudgetExceeded):
                caller.call("compile", MODEL, payload, tmp_path / "calls/b/1")
        finally:
            release.set()
        future.result()
    assert len(sdk.calls) == 1
