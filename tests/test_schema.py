"""Question normalization and the program's discrete output contract."""

from copy import deepcopy

import pytest
from pydantic import ValidationError

from jev_heuristic_adapter import Choice, Noul, Score
from jev_heuristic_adapter._schema import (
    OutputValidationError,
    OutputValidator,
    build_output_schema,
    normalize_questions,
)


@pytest.mark.parametrize(
    ("question", "valid", "invalid"),
    [
        ({"type": "noul"}, [True, False], [0, 1, "true", None]),
        (
            {"type": "choice", "criteria": {"accept": None, "reject": "Reject"}},
            ["accept", "reject"],
            ["ACCEPT", "unknown", 0, True, None],
        ),
        (
            {"type": "score", "criteria": ["low", "medium", "high"]},
            [0, 1, 2],
            [-1, 3, 0.5, "1", True, None],
        ),
    ],
    ids=["noul", "choice", "score"],
)
def test_discrete_answers_preserve_values_and_reject_invalid_answers(
    question, valid, invalid
):
    validator = OutputValidator(question)
    for answer in valid:
        output = {"answer": answer}
        assert validator.validate(output) is output
    for answer in invalid:
        with pytest.raises(OutputValidationError):
            validator.validate({"answer": answer})


@pytest.mark.parametrize(
    "question",
    [
        None,
        [],
        {},
        {"type": "unknown"},
        {"type": "choice"},
        {"type": "choice", "criteria": ["a", "b"]},
        {"type": "choice", "criteria": {"a": None}},
        {"type": "choice", "criteria": {0: None, 1: None}},
        {"type": "score"},
        {"type": "score", "criteria": {"a": None, "b": None}},
        {"type": "score", "criteria": []},
        {"type": "score", "criteria": ["only"]},
    ],
)
def test_invalid_question_definitions_cannot_build_a_schema(question):
    with pytest.raises(ValueError):
        build_output_schema(question)


@pytest.mark.parametrize(
    "output", [None, True, [], "answer", {}, {"answer": True, "extra": 1}]
)
def test_output_must_be_an_object_with_exactly_one_answer(output):
    with pytest.raises(OutputValidationError):
        OutputValidator({"type": "noul"}).validate(output)


@pytest.mark.parametrize("answer", [float("nan"), float("inf"), {1, 2}, "\ud800"])
def test_output_must_be_finite_serializable_utf8_json(answer):
    with pytest.raises(OutputValidationError, match="Output is not valid JSON"):
        OutputValidator({"type": "noul"}).validate({"answer": answer})


def test_schema_errors_identify_the_answer_path():
    validator = OutputValidator({"type": "choice", "criteria": {"a": None, "b": None}})
    with pytest.raises(OutputValidationError, match=r"\$\.answer"):
        validator.validate({"answer": "missing"})


def test_sdk_questions_and_dictionaries_normalize_identically():
    sdk = {
        "yes": Noul(
            instructions={"text": "合格?", "context": None}, criteria={"true": None}
        ),
        "pick": Choice(criteria={"accept": None, "reject": {"reason": "invalid"}}),
        "rate": Score(criteria=("low", {"description": "high"})),
    }
    raw = {name: dict(item) for name, item in sdk.items()}
    before = deepcopy(raw)
    normalized = normalize_questions(raw)
    assert normalized == normalize_questions(sdk)
    assert raw == before
    assert normalized["yes"]["instructions"]["context"] is None
    assert normalized["yes"]["criteria"]["true"] is None
    assert normalized["rate"]["criteria"] == ["low", {"description": "high"}]
    normalized["yes"]["instructions"]["text"] = "changed"
    assert raw == before


@pytest.mark.parametrize(
    ("questions", "error"),
    [
        (None, ValueError),
        ([], ValueError),
        ({}, ValueError),
        ({1: Noul()}, ValueError),
        ({"q": object()}, TypeError),
        ({"q": {}}, ValueError),
        ({"q": {"type": []}}, ValueError),
        ({"q": {"type": "other"}}, ValueError),
        ({"q": {"type": "noul", "unexpected": True}}, ValidationError),
        ({"q": {"type": "choice", "criteria": {"only": None}}}, ValueError),
        ({"q": {"type": "score", "criteria": ["only"]}}, ValueError),
        ({"q": {"type": "choice", "criteria": {1: "a", 2: "b"}}}, ValidationError),
    ],
)
def test_normalization_rejects_bad_names_types_and_rubrics(questions, error):
    with pytest.raises(error):
        normalize_questions(questions)
