"""Load trusted heuristic code as reusable predictors."""

import json
from collections.abc import Callable
from copy import deepcopy
from typing import Any

from ._program import CompiledQuestion
from ._schema import OutputValidator


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
