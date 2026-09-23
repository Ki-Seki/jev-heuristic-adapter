"""Compiled question artifacts and trusted in-process predictor loading."""

import hashlib
import json
from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Literal

from ._schema import OutputValidator


def canonical_json(value: Any) -> str:
    """Serialize JSON consistently for snapshots and cache identities."""
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)


def build_question_id(question_json: str) -> str:
    """Identify a canonical question snapshot by its content."""
    return hashlib.sha256(question_json.encode()).hexdigest()


def build_artifact_id(
    question_id: str, source: str, request_json: str, generation_json: str
) -> str:
    """Identify source and generation snapshots by their content."""
    content = [question_id, source, request_json, generation_json]
    return hashlib.sha256(canonical_json(content).encode()).hexdigest()


@dataclass(frozen=True)
class CompiledQuestion:
    question_id: str
    artifact_id: str
    question_json: str
    source: str
    request_json: str
    generation_json: str
    validation: Literal["syntax_checked"] = "syntax_checked"

    def validate_integrity(self, expected_artifact_id: str) -> None:
        """Check stored IDs and the syntax marker without executing source."""
        question_id = build_question_id(self.question_json)
        artifact_id = build_artifact_id(
            question_id, self.source, self.request_json, self.generation_json
        )
        if (
            self.question_id != question_id
            or self.artifact_id != expected_artifact_id
            or self.artifact_id != artifact_id
            or self.validation != "syntax_checked"
        ):
            raise ValueError("Artifact content or validation marker is inconsistent")


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
