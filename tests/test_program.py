"""Artifact identity, integrity, and reusable in-process execution."""

from dataclasses import FrozenInstanceError, replace

import pytest

from jev_heuristic_adapter._program import (
    build_question_id,
    canonical_json,
    load_predictor,
)
from jev_heuristic_adapter._schema import OutputValidationError


def test_canonical_question_identity_ignores_dictionary_insertion_order():
    first = {"type": "noul", "instructions": {"z": "中文", "a": None}}
    reordered = {"instructions": {"a": None, "z": "中文"}, "type": "noul"}
    assert canonical_json(first) == canonical_json(reordered)
    assert "中文" in canonical_json(first)
    assert build_question_id(canonical_json(first)) == build_question_id(
        canonical_json(reordered)
    )
    changed = {**first, "instructions": "Different rule"}
    assert build_question_id(canonical_json(first)) != build_question_id(
        canonical_json(changed)
    )


@pytest.mark.parametrize("value", [float("nan"), float("inf"), {"x": object()}])
def test_canonical_snapshots_reject_non_json_values(value):
    with pytest.raises((TypeError, ValueError)):
        canonical_json(value)


def test_artifact_is_immutable_and_matches_its_identity(make_program):
    program = make_program()
    assert program.validate_integrity(program.artifact_id) is None
    with pytest.raises(FrozenInstanceError):
        program.source = "replacement"
    with pytest.raises(ValueError, match="inconsistent"):
        program.validate_integrity("0" * 64)


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
def test_integrity_rejects_modified_content_or_markers(make_program, field):
    program = make_program()
    modified = replace(program, **{field: "modified"})
    with pytest.raises(ValueError, match="inconsistent"):
        modified.validate_integrity(program.artifact_id)


def test_loader_reuses_function_globals_and_copies_nested_state(make_program):
    source = """calls = 0
def predict(state):
    global calls
    calls += 1
    state["items"].append(calls)
    return {"answer": calls}
"""
    program = make_program(
        source, {"type": "score", "criteria": ["none", "once", "twice"]}
    )
    predict = load_predictor(program)
    state = {"items": []}
    assert predict(state) == {"answer": 1}
    assert predict(state) == {"answer": 2}
    assert state == {"items": []}


def test_loader_detects_an_entry_point_overwritten_by_generated_code(make_program):
    program = make_program(
        'def predict(state): return {"answer": True}\npredict = None'
    )
    with pytest.raises(ValueError, match="callable predict"):
        load_predictor(program)


def test_loader_propagates_generated_exceptions(make_program):
    predict = load_predictor(
        make_program('def predict(state): raise RuntimeError("generated failure")')
    )
    with pytest.raises(RuntimeError, match="generated failure"):
        predict({})


def test_loader_checks_each_prediction_against_the_question(make_program):
    predict = load_predictor(
        make_program('def predict(state): return {"answer": state["answer"]}')
    )
    assert predict({"answer": True}) == {"answer": True}
    with pytest.raises(OutputValidationError):
        predict({"answer": "true"})
