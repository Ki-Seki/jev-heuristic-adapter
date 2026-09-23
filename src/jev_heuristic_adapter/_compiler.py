"""Build compilation requests from task definitions and examples."""

import json
from collections.abc import Mapping, Sequence
from typing import Any

from ._prompt import SYSTEM_PROMPT


def build_messages(
    questions: Mapping[str, Any],
    output_schema: Mapping[str, Any],
    examples: Sequence[Mapping[str, Any]] = (),
) -> list[dict[str, str]]:
    """Accept JSON-ready questions and zero or more {state, answers} examples."""
    if not questions:
        raise ValueError("At least one question is required")
    payload = {
        "task_definition": {
            "questions": dict(questions),
            "output_schema": dict(output_schema),
        },
        "examples": list(examples),
    }
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False, allow_nan=False)},
    ]
