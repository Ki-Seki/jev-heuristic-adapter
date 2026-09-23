"""A single-question compilation artifact with immutable JSON snapshots."""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class CompiledQuestion:
    question_id: str
    artifact_id: str
    question_json: str
    source: str
    request_json: str
    generation_json: str
    validation: Literal["syntax_checked"] = "syntax_checked"
