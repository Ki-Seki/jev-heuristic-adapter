"""Minimal synchronous adapter using trusted in-process heuristic programs."""

from collections.abc import Mapping
from typing import Any

from typesafe_sdk import ChoiceAnswer, NoulAnswer, ScoreAnswer, SystemOneResponse, Usage

from ._cache import ProgramStore
from ._compiler import _canonical_json, compile_or_load
from ._program import load_predictor
from ._schema import normalize_questions
from .providers import Provider


class HeuristicAdapterClient:
    def __init__(self, provider: Provider, store: ProgramStore | None = None):
        self.provider = provider
        self.store = ProgramStore() if store is None else store
        self._bindings = {}

    def compile(self, questions: Mapping[str, Any], examples=(), *, force=False):
        questions = normalize_questions(questions)
        keys = {name: _canonical_json(dict(q)) for name, q in questions.items()}
        definitions = {keys[name]: q for name, q in questions.items()}
        prepared = {}
        for key, question in definitions.items():
            samples = [
                {"state": item["state"], "answer": item["answers"][name]}
                for item in examples
                for name in keys
                if keys[name] == key and name in item["answers"]
            ]
            program = compile_or_load(
                self.provider,
                question=question,
                examples=samples,
                store=self.store,
                force=force,
            )
            predict = load_predictor(program)
            prepared[key] = (program, predict)
        self._bindings.update(prepared)
        return {name: prepared[key][0] for name, key in keys.items()}

    def system_one(self, state: Any, questions: Mapping[str, Any]) -> SystemOneResponse:
        questions = normalize_questions(questions)
        keys = {name: _canonical_json(dict(q)) for name, q in questions.items()}
        if any(key not in self._bindings for key in keys.values()):
            raise LookupError("Compile all requested questions before system_one")
        predictors = {name: self._bindings[key][1] for name, key in keys.items()}
        answers = {
            name: predict(state)["answer"] for name, predict in predictors.items()
        }
        return _build_response(questions, answers)


def _build_response(
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
