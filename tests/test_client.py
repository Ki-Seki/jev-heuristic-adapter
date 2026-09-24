"""User-facing compilation, question reuse, and official SDK answers."""

import json
import subprocess
import sys

import pytest
from typesafe_sdk import ChoiceAnswer, NoulAnswer, ScoreAnswer, SystemOneResponse

from jev_heuristic_adapter import Choice, HeuristicAdapterClient, Noul, Score
from jev_heuristic_adapter._client import _build_response
from jev_heuristic_adapter._schema import OutputValidationError, build_output_schema


def test_multiple_question_types_return_official_answers_and_roundtrip_json(
    provider_factory, store
):
    fields = {"noul": "enabled", "choice": "label", "score": "level"}

    def source_for_question(messages):
        kind = json.loads(messages[1]["content"])["task_definition"]["question"]["type"]
        return f'def predict(state): return {{"answer": state[{fields[kind]!r}]}}'

    provider = provider_factory(source_for_question)
    client = HeuristicAdapterClient(provider, store)
    questions = {
        "enabled": Noul(),
        "label": Choice(criteria={"accept": None, "reject": "No"}),
        "level": Score(criteria=["low", {"description": "high"}]),
    }
    programs = client.compile(questions)
    assert set(programs) == set(questions)
    for enabled, label, level in [(True, "accept", 1), (False, "reject", 0)]:
        response = client.system_one(
            {"enabled": enabled, "label": label, "level": level}, questions
        )
        assert isinstance(response, SystemOneResponse)
        assert isinstance(response.nouls["enabled"], NoulAnswer)
        assert response.nouls["enabled"].noul == float(enabled)
        assert isinstance(response.choices["label"], ChoiceAnswer)
        assert response.choices["label"].choice == label
        assert response.choices["label"].probabilities == {
            option: float(option == label) for option in ("accept", "reject")
        }
        assert response.choices["label"].confidence == 1.0
        assert isinstance(response.scores["level"], ScoreAnswer)
        assert response.scores["level"].score == float(level)
        assert response.scores["level"].probabilities == {
            index: float(index == level) for index in (0, 1)
        }
        assert response.scores["level"].legend == {
            0: "low",
            1: {"description": "high"},
        }
        assert response.scores["level"].confidence == 1.0
        assert response.model == "heuristic"
        assert response.usage.input_tokens == response.usage.output_tokens == 0
        assert (
            SystemOneResponse.model_validate_json(response.model_dump_json())
            == response
        )
    assert provider.calls == 3


def test_aliases_share_one_program_and_collect_only_their_named_examples(
    provider, store
):
    question = Noul(instructions="Same question.")
    questions = {"first": question, "second": question}
    examples = [
        {"state": {"age": 20}, "answers": {"first": True}},
        {"state": {"age": 17}, "answers": {"second": False, "unrelated": True}},
    ]
    client = HeuristicAdapterClient(provider, store)
    programs = client.compile(questions, examples)
    assert programs["first"] is programs["second"]
    assert provider.calls == 1
    assert json.loads(provider.requests[0][1]["content"])["examples"] == [
        {"state": {"age": 20}, "answer": True},
        {"state": {"age": 17}, "answer": False},
    ]
    assert client.system_one({}, {"renamed": question}).nouls["renamed"].noul == 1.0
    assert provider.calls == 1


def test_new_client_can_reuse_sdk_or_dictionary_question_without_a_provider_call(
    provider, store
):
    first = HeuristicAdapterClient(provider, store).compile({"q": Noul()})
    provider.error = AssertionError("cache hit must not invoke the provider")
    fresh = HeuristicAdapterClient(provider, store)
    assert fresh.compile({"q": {"type": "noul"}}) == first
    assert fresh.system_one({}, {"q": Noul()}).nouls["q"].noul == 1.0
    assert provider.calls == 1


def test_default_store_and_missing_question_preflight(provider, store, monkeypatch):
    monkeypatch.setattr("jev_heuristic_adapter._client.ProgramStore", lambda: store)
    provider.source = 'def predict(state): raise AssertionError("must not execute")'
    client = HeuristicAdapterClient(provider)
    client.compile({"known": Noul()})
    with pytest.raises(LookupError, match="Compile all"):
        client.system_one({}, {"known": Noul(), "missing": Noul(instructions="new")})


def test_failed_batch_does_not_partially_replace_existing_bindings(provider, store):
    client = HeuristicAdapterClient(provider, store)
    original = {"q": Noul(instructions="old")}
    client.compile(original)

    def fail_second_question(messages):
        question = json.loads(messages[1]["content"])["task_definition"]["question"]
        if question["instructions"] == "new":
            raise RuntimeError("second question failed")
        return 'def predict(state): return {"answer": False}'

    provider.source = fail_second_question
    with pytest.raises(RuntimeError, match="second question failed"):
        client.compile({**original, "new": Noul(instructions="new")}, force=True)
    assert client.system_one({}, original).nouls["q"].noul == 1.0
    with pytest.raises(LookupError):
        client.system_one({}, {"new": Noul(instructions="new")})


def test_wrong_example_answers_do_not_filter_or_prevent_replacement(provider, store):
    client = HeuristicAdapterClient(provider, store)
    questions = {"q": Noul(instructions="Return true.")}
    examples = [{"state": "fixture", "answers": {"q": True}}]
    original = client.compile(questions, examples)
    provider.source = 'def predict(state): return {"answer": False}'
    replacement = client.compile(questions, examples, force=True)
    assert replacement != original
    assert client.system_one("fixture", questions).nouls["q"].noul == 0.0
    fresh = HeuristicAdapterClient(provider, store)
    assert fresh.compile(questions, examples) == replacement
    assert fresh.system_one("fixture", questions).nouls["q"].noul == 0.0
    assert provider.calls == 2


def test_compilation_never_executes_the_supplied_examples(provider, store):
    provider.source = 'def predict(state): raise RuntimeError("predict executed")'
    questions = {"q": Noul()}
    examples = [{"state": "fixture", "answers": {"q": True}}]
    original = HeuristicAdapterClient(provider, store).compile(questions, examples)
    fresh = HeuristicAdapterClient(provider, store)
    assert fresh.compile(questions, examples) == original
    assert provider.calls == 1
    with pytest.raises(RuntimeError, match="predict executed"):
        fresh.system_one("fixture", questions)


def test_changed_output_schema_regenerates_then_reuses_the_new_cache(
    provider, store, monkeypatch
):
    questions = {"q": Noul()}
    client = HeuristicAdapterClient(provider, store)
    original = client.compile(questions)
    schema = {
        **build_output_schema({"type": "noul"}),
        "description": "Updated contract",
    }
    with monkeypatch.context() as patcher:
        patcher.setattr(
            "jev_heuristic_adapter._compiler.build_output_schema",
            lambda question: schema,
        )
        updated = client.compile(questions)
        assert updated != original
        assert client.compile(questions) == updated
    assert client.compile(questions) == original
    assert provider.calls == 2


@pytest.mark.parametrize(
    "field",
    [
        "question_id",
        "artifact_id",
        "question_json",
        "source",
        "request_json",
        "generation_json",
        "validation",
    ],
)
def test_corrupt_cache_is_rejected_without_automatic_regeneration(
    provider, store, field
):
    client = HeuristicAdapterClient(provider, store)
    questions = {"q": Noul()}
    program = client.compile(questions)["q"]
    path = store.save(program)
    data = json.loads(path.read_text(encoding="utf-8"))
    path.write_text(json.dumps({**data, field: "modified"}), encoding="utf-8")
    with pytest.raises(ValueError, match="inconsistent"):
        client.compile(questions)
    assert provider.calls == 1


def test_invalid_program_output_is_reported_before_sdk_conversion(provider, store):
    provider.source = 'def predict(state): return {"answer": "true"}'
    client = HeuristicAdapterClient(provider, store)
    client.compile({"q": Noul()})
    with pytest.raises(OutputValidationError):
        client.system_one({}, {"q": Noul()})


def test_response_conversion_rejects_unknown_question_kinds():
    with pytest.raises(ValueError, match="Unsupported question type"):
        _build_response({"q": {"type": "future"}}, {"q": True})


def test_core_import_does_not_require_the_optional_openai_sdk(tmp_path):
    script = """
import importlib.abc
import sys

class RejectOpenAI(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "openai" or fullname.startswith("openai."):
            raise ModuleNotFoundError("optional SDK is unavailable")
        return None

sys.meta_path.insert(0, RejectOpenAI())
from jev_heuristic_adapter import HeuristicAdapterClient, Noul, Choice, Score
assert Noul().type == "noul"
assert Choice(criteria={"a": None, "b": None}).type == "choice"
assert Score(criteria=["low", "high"]).type == "score"
assert "openai" not in sys.modules
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0, result.stderr
