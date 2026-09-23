"""Wrap validated discrete predictions as official SDK response objects."""

from collections.abc import Mapping
from typing import Any

from typesafe_sdk import ChoiceAnswer, NoulAnswer, ScoreAnswer, SystemOneResponse, Usage


def build_response(
    questions: Mapping[str, Any], values: Mapping[str, Any]
) -> SystemOneResponse:
    """Probabilities encode deterministic choices, not calibrated confidence."""
    answers = {}
    for name, question in questions.items():
        value = values[name]
        kind = question["type"]
        if kind == "noul":
            answers[name] = NoulAnswer(noul=float(value))
        elif kind == "choice":
            probabilities = {
                label: float(label == value) for label in question["criteria"]
            }
            answers[name] = ChoiceAnswer(
                choice=value,
                probabilities=probabilities,
                confidence=1.0,
            )
        elif kind == "score":
            legend = dict(enumerate(question["criteria"]))
            probabilities = {level: float(level == value) for level in legend}
            answers[name] = ScoreAnswer(
                score=float(value),
                legend=legend,
                probabilities=probabilities,
                confidence=1.0,
            )
        else:
            raise ValueError(f"Unsupported question type {kind!r}")
    return SystemOneResponse(
        model="heuristic",
        answers=answers,
        usage=Usage(input_tokens=0, output_tokens=0),
    )
