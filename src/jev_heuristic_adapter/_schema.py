"""Normalize question definitions and derive their program-output schemas."""

from collections.abc import Mapping
from typing import Any

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
