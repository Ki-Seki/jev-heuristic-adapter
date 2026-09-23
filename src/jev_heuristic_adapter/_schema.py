"""Derive the discrete program-output contract from JSON-ready questions."""

from collections.abc import Mapping
from typing import Any


def build_output_schema(questions: Mapping[str, Any]) -> dict[str, Any]:
    if not questions:
        raise ValueError("At least one question is required")
    properties = {}
    for name, question in questions.items():
        if not isinstance(name, str) or not isinstance(question, Mapping):
            raise ValueError("Questions must map string names to question definitions")
        kind, criteria = question.get("type"), question.get("criteria")
        if kind == "noul":
            answer = {"type": "boolean"}
        elif kind == "choice":
            if not isinstance(criteria, Mapping) or len(criteria) < 2:
                raise ValueError(f"{name}: choice requires at least two criteria")
            if not all(isinstance(label, str) for label in criteria):
                raise ValueError(f"{name}: choice labels must be strings")
            answer = {"type": "string", "enum": list(criteria)}
        elif kind == "score":
            if not isinstance(criteria, list) or len(criteria) < 2:
                raise ValueError(
                    f"{name}: score requires a list of at least two criteria"
                )
            answer = {"type": "integer", "minimum": 0, "maximum": len(criteria) - 1}
        else:
            raise ValueError(f"{name}: unsupported question type {kind!r}")
        properties[name] = answer
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }
