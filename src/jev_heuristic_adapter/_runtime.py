"""Validate program output; isolated code execution is added separately."""

import json
from collections.abc import Mapping
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry

from ._schema import build_output_schema


class OutputValidationError(ValueError):
    """The program returned a value that violates its output contract."""


class OutputValidator:
    """Reuse a Draft 2020-12 validator for one fixed task."""

    def __init__(self, questions: Mapping[str, Any]):
        schema = build_output_schema(questions)
        Draft202012Validator.check_schema(schema)
        self._validator = Draft202012Validator(schema, registry=Registry())

    def validate(self, output: Any) -> dict[str, Any]:
        """Check a decoded JSON result without changing or coercing its values."""
        if not isinstance(output, dict):
            raise OutputValidationError("predict must return a JSON object")
        try:
            json.dumps(output, allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise OutputValidationError(f"Output is not valid JSON: {exc}") from exc
        error = next(self._validator.iter_errors(output), None)
        if error is not None:
            raise OutputValidationError(
                f"{error.json_path}: {error.message}"
            ) from error
        return output
