"""Normalize question definitions, derive schemas, and validate program outputs."""

import json
from collections.abc import Mapping
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry
from typesafe_sdk import Choice, Noul, Score

_QUESTION_TYPES = {"noul": Noul, "choice": Choice, "score": Score}


def build_output_schema(question: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(question, Mapping) or not question:
        raise ValueError("A question definition is required")
    kind, criteria = question.get("type"), question.get("criteria")
    if kind == "noul":
        answer = {"type": "boolean"}
    elif kind == "choice":
        if not isinstance(criteria, Mapping) or len(criteria) < 2:
            raise ValueError("Choice requires at least two criteria")
        if not all(isinstance(label, str) for label in criteria):
            raise ValueError("Choice labels must be strings")
        answer = {"type": "string", "enum": list(criteria)}
    elif kind == "score":
        if not isinstance(criteria, list) or len(criteria) < 2:
            raise ValueError("Score requires a list of at least two criteria")
        answer = {"type": "integer", "minimum": 0, "maximum": len(criteria) - 1}
    else:
        raise ValueError(f"Unsupported question type {kind!r}")
    return {
        "type": "object",
        "properties": {"answer": answer},
        "required": ["answer"],
        "additionalProperties": False,
    }


def normalize_questions(questions: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    if not isinstance(questions, Mapping) or not questions:
        raise ValueError("At least one named question is required")
    normalized = {}
    for name, question in questions.items():
        if not isinstance(name, str):
            raise ValueError("Question names must be strings")
        if not isinstance(question, (Noul, Choice, Score, Mapping)):
            raise TypeError(f"{name}: expected a question dictionary or SDK object")
        data = dict(question)
        kind = data.get("type")
        if not isinstance(kind, str) or kind not in _QUESTION_TYPES:
            raise ValueError(f"{name}: unsupported question type {kind!r}")
        model = _QUESTION_TYPES[kind].model_validate(data, strict=True)
        value = model.model_dump(mode="json")
        build_output_schema(value)
        normalized[name] = value
    return normalized


class OutputValidationError(ValueError):
    """The program returned a value that violates its output contract."""


class OutputValidator:
    """Validate the {"answer": value} output of one fixed question."""

    def __init__(self, question: Mapping[str, Any]):
        schema = build_output_schema(question)
        self._validator = Draft202012Validator(schema, registry=Registry())

    def validate(self, output: Any) -> dict[str, Any]:
        """Check a decoded JSON result without changing or coercing its values."""
        if not isinstance(output, dict):
            raise OutputValidationError("predict must return a JSON object")
        try:
            json.dumps(output, ensure_ascii=False, allow_nan=False).encode("utf-8")
        except (TypeError, ValueError) as exc:
            raise OutputValidationError(f"Output is not valid JSON: {exc}") from exc
        error = next(self._validator.iter_errors(output), None)
        if error is not None:
            raise OutputValidationError(
                f"{error.json_path}: {error.message}"
            ) from error
        return output
