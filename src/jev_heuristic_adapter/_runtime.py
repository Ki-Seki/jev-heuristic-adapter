"""Load trusted heuristic code and validate its output against the question schema."""

import json
from collections.abc import Callable, Mapping
from copy import deepcopy
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry

from ._program import CompiledQuestion
from ._schema import build_output_schema


class OutputValidationError(ValueError):
    """The program returned a value that violates its output contract."""


class OutputValidator:
    """Validate the {"answer": value} output of one fixed question."""

    def __init__(self, question: Mapping[str, Any]):
        schema = build_output_schema(question)
        Draft202012Validator.check_schema(schema)
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


def load_predictor(program: CompiledQuestion) -> Callable[[Any], dict[str, Any]]:
    """Load trusted source once in this process; no sandbox or forced timeout."""
    validator = OutputValidator(json.loads(program.question_json))
    namespace: dict[str, Any] = {"__name__": "heuristic"}
    exec(
        compile(program.source, f"<heuristic:{program.artifact_id[:12]}>", "exec"),
        namespace,
    )
    generated_predict = namespace.get("predict")
    if not callable(generated_predict):
        raise ValueError("Program must define a callable predict")

    def predict(state: Any) -> dict[str, Any]:
        return validator.validate(generated_predict(deepcopy(state)))

    return predict
