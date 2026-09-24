"""Compilation requests, source contracts, identities, and cache reuse."""

import json
from copy import deepcopy

import pytest

from jev_heuristic_adapter import _compiler as compiler
from jev_heuristic_adapter._compiler import (
    ProgramValidationError,
    build_messages,
    compile_key,
    compile_or_load,
    compile_question,
    validate_program,
)
from jev_heuristic_adapter._prompt import SYSTEM_PROMPT
from jev_heuristic_adapter._schema import OutputValidationError, build_output_schema
from jev_heuristic_adapter.providers import ProviderResult

SOURCE = 'def predict(state): return {"answer": True}'


@pytest.mark.parametrize("count", [0, 1, 3, 7])
def test_messages_include_full_task_schema_and_all_examples(question, count):
    question["instructions"] = {"rule": "判断年龄", "threshold": 18}
    examples = [{"state": {"age": index}, "answer": False} for index in range(count)]
    messages = build_messages(question, examples)
    assert messages[0] == {"role": "system", "content": SYSTEM_PROMPT}
    assert messages[1]["role"] == "user"
    payload = json.loads(messages[1]["content"])
    assert payload["task_definition"] == {
        "question": question,
        "output_schema": build_output_schema(question),
    }
    assert payload["examples"] == examples


@pytest.mark.parametrize(
    "examples",
    [[None], [{}], [{"state": {}}], [{"state": {}, "answer": True, "extra": 1}]],
)
def test_bad_example_structure_is_rejected_before_generation(
    provider, question, store, examples
):
    with pytest.raises(ValueError, match="exactly state and answer"):
        compile_or_load(provider, question=question, examples=examples, store=store)
    assert provider.calls == 0


def test_example_answer_format_is_validated_without_checking_correctness(question):
    with pytest.raises(OutputValidationError):
        build_messages(question, [{"state": {}, "answer": "true"}])
    assert build_messages(question, [{"state": {}, "answer": False}])


@pytest.mark.parametrize(
    ("source", "complete", "message"),
    [
        (SOURCE, False, "did not complete"),
        (" \n", True, "empty source"),
        ("def predict(:", True, "Invalid Python"),
        ("return True", True, "Invalid Python"),
        ("answer = True", True, "exactly one top-level"),
        ("predict = lambda state: {}", True, "exactly one top-level"),
        ("async def predict(state): return {}", True, "exactly one top-level"),
        (
            "def predict(state): return {}\ndef predict(state): return {}",
            True,
            "exactly one top-level",
        ),
        ("def predict(value): return {}", True, "take only state"),
        ("def predict(state, other): return {}", True, "take only state"),
        ("def predict(state, /): return {}", True, "take only state"),
        ("def predict(context, /, state): return {}", True, "take only state"),
        ("def predict(*, state): return {}", True, "take only state"),
        ("def predict(state, *args): return {}", True, "take only state"),
        ("def predict(state, **kwargs): return {}", True, "take only state"),
        ("def predict(state, *, extra=None): return {}", True, "take only state"),
        ("def predict(state=None): return {}", True, "take only state"),
        ("@decorator\ndef predict(state): return {}", True, "take only state"),
    ],
)
def test_invalid_generations_preserve_the_original_provider_result(
    source, complete, message
):
    result = ProviderResult(source, complete, 11, 17, {"request": "original"})
    with pytest.raises(ProgramValidationError, match=message) as caught:
        validate_program(result)
    assert caught.value.result is result


def test_source_validation_does_not_execute_or_rewrite_the_program():
    source = """raise RuntimeError("must not run")
def helper(value): return value
def predict(state) -> dict: return {"answer": helper(True)}
"""
    result = ProviderResult(source, True, None, None, {})
    assert validate_program(result) == source


def test_compilation_keeps_detached_question_request_and_generation_snapshots(
    provider, question
):
    question["instructions"] = {"nested": ["original"]}
    examples = [{"state": {"values": [1]}, "answer": True}]
    before_question, before_examples = deepcopy(question), deepcopy(examples)

    def mutate_request(messages):
        messages[0]["content"] = "provider changed the message"
        return SOURCE

    provider.source = mutate_request
    program = compile_question(provider, question=question, examples=examples)
    provider.results[0].raw["attempt"] = 999
    question["instructions"]["nested"].append("changed")
    examples[0]["state"]["values"].append(2)
    assert json.loads(program.question_json) == before_question
    request = json.loads(program.request_json)
    assert request[0]["content"] == SYSTEM_PROMPT
    assert json.loads(request[1]["content"])["examples"] == before_examples
    assert json.loads(program.generation_json)["raw"] == {"attempt": 1}
    program.validate_integrity(program.artifact_id)


def test_request_identity_is_stable_under_dictionary_key_reordering(provider):
    first = {
        "type": "choice",
        "criteria": {"z": "last", "a": "first"},
        "instructions": "Choose.",
    }
    reordered = {
        "instructions": "Choose.",
        "criteria": {"a": "first", "z": "last"},
        "type": "choice",
    }
    examples = [{"state": {"z": 1, "a": 2}, "answer": "a"}]
    reordered_examples = [{"answer": "a", "state": {"a": 2, "z": 1}}]
    assert compile_key(provider, question=first, examples=examples) == compile_key(
        provider, question=reordered, examples=reordered_examples
    )
    assert provider.calls == 0


@pytest.mark.parametrize(
    "change", ["question", "examples", "provider", "prompt", "schema"]
)
def test_generation_inputs_all_participate_in_the_cache_identity(
    provider, question, monkeypatch, change
):
    examples = [{"state": {}, "answer": True}]
    before = compile_key(provider, question=question, examples=examples)
    if change == "question":
        question["instructions"] = "A different task."
    elif change == "examples":
        examples[0]["state"] = {"new": True}
    elif change == "provider":
        provider.identity["model"] = "model-b"
    elif change == "prompt":
        monkeypatch.setattr(
            compiler, "SYSTEM_PROMPT", SYSTEM_PROMPT + "\nNew instruction."
        )
    else:
        schema = {**build_output_schema(question), "description": "New contract."}
        monkeypatch.setattr(compiler, "build_output_schema", lambda question: schema)
    assert compile_key(provider, question=question, examples=examples) != before
    assert provider.calls == 0


def test_default_store_is_used_and_force_replaces_the_saved_artifact(
    provider, question, store, monkeypatch
):
    monkeypatch.setattr(compiler, "ProgramStore", lambda: store)
    first = compile_or_load(provider, question=question)
    assert compile_or_load(provider, question=question) == first
    assert provider.calls == 1
    provider.source = 'def predict(state): return {"answer": False}'
    replacement = compile_or_load(provider, question=question, force=True)
    assert replacement.artifact_id != first.artifact_id
    assert store.lookup(compile_key(provider, question=question)) == replacement
    assert provider.calls == 2


def test_failed_forced_generation_keeps_previous_cache_and_can_be_retried(
    provider, question, store
):
    first = compile_or_load(provider, question=question, store=store)
    provider.source = "broken Python !"
    with pytest.raises(ProgramValidationError):
        compile_or_load(provider, question=question, store=store, force=True)
    assert compile_or_load(provider, question=question, store=store) == first
    assert provider.calls == 2
    provider.source = SOURCE
    retried = compile_or_load(provider, question=question, store=store, force=True)
    assert retried.artifact_id != first.artifact_id
    assert provider.calls == 3


def test_provider_failures_propagate_and_do_not_poison_later_attempts(
    provider, question, store
):
    error = RuntimeError("provider unavailable")
    provider.error = error
    with pytest.raises(RuntimeError) as caught:
        compile_or_load(provider, question=question, store=store)
    assert caught.value is error
    assert store.lookup(compile_key(provider, question=question)) is None
    provider.error = None
    assert compile_or_load(provider, question=question, store=store).source == SOURCE
    assert provider.calls == 2
