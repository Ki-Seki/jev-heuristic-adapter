"""Validate program output; isolated code execution is added separately."""

import json
import math
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry

from ._schema import build_output_schema


@dataclass(frozen=True)
class RuntimeLimits:
    """Execution budgets; time budgets are enforced by the future worker runner."""

    wall_seconds: float = 5.0
    cpu_seconds: int = 2
    max_output_bytes: int = 64 * 1024

    def __post_init__(self) -> None:
        if (
            type(self.wall_seconds) not in (int, float)
            or not math.isfinite(self.wall_seconds)
            or self.wall_seconds <= 0
        ):
            raise ValueError("wall_seconds must be a finite positive number")
        for name, value in (
            ("cpu_seconds", self.cpu_seconds),
            ("max_output_bytes", self.max_output_bytes),
        ):
            if type(value) is not int or value <= 0:
                raise ValueError(f"{name} must be a positive integer")


class OutputValidationError(ValueError):
    """The program returned a value that violates its output contract."""


class OutputValidator:
    """Validate the {"answer": value} output of one fixed question."""

    def __init__(
        self, question: Mapping[str, Any], limits: RuntimeLimits | None = None
    ):
        self.limits = RuntimeLimits() if limits is None else limits
        schema = build_output_schema(question)
        Draft202012Validator.check_schema(schema)
        self._validator = Draft202012Validator(schema, registry=Registry())

    def validate(self, output: Any) -> dict[str, Any]:
        """Check a decoded JSON result without changing or coercing its values."""
        if not isinstance(output, dict):
            raise OutputValidationError("predict must return a JSON object")
        try:
            encoded = json.dumps(output, ensure_ascii=False, allow_nan=False).encode(
                "utf-8"
            )
        except (TypeError, ValueError) as exc:
            raise OutputValidationError(f"Output is not valid JSON: {exc}") from exc
        if len(encoded) > self.limits.max_output_bytes:
            raise OutputValidationError("Output exceeds max_output_bytes")
        error = next(self._validator.iter_errors(output), None)
        if error is not None:
            raise OutputValidationError(
                f"{error.json_path}: {error.message}"
            ) from error
        return output
