"""Derive the discrete program-output contract from one JSON-ready question."""

from collections.abc import Mapping
from typing import Any


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
