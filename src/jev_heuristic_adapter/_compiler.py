"""Build compilation requests from task definitions and examples."""

import ast
import json
from collections.abc import Mapping, Sequence
from typing import Any

from ._prompt import SYSTEM_PROMPT
from ._schema import build_output_schema
from .providers import Provider, ProviderResult


def build_messages(
    questions: Mapping[str, Any],
    examples: Sequence[Mapping[str, Any]] = (),
) -> list[dict[str, str]]:
    """Accept JSON-ready questions and zero or more {state, answers} examples."""
    payload = {
        "task_definition": {
            "questions": dict(questions),
            "output_schema": build_output_schema(questions),
        },
        "examples": list(examples),
    }
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": json.dumps(payload, ensure_ascii=False, allow_nan=False),
        },
    ]


def request_program(
    provider: Provider,
    *,
    questions: Mapping[str, Any],
    examples: Sequence[Mapping[str, Any]] = (),
) -> ProviderResult:
    """Request source code through a caller-owned provider; validation follows."""
    return provider.request(build_messages(questions, examples))


class ProgramValidationError(ValueError):
    """Keep the provider result so failed generations remain inspectable."""

    def __init__(self, reason: str, result: ProviderResult):
        super().__init__(reason)
        self.result = result


def validate_program(result: ProviderResult) -> str:
    """Check syntax and the entry point without execution; not a safety check."""
    if not result.complete:
        raise ProgramValidationError("Generation did not complete", result)
    if not result.text.strip():
        raise ProgramValidationError("Generation returned empty source", result)
    try:
        tree = ast.parse(result.text, feature_version=(3, 10))
        compile(tree, "<heuristic>", "exec")  # Compile to bytecode, never execute.
    except SyntaxError as exc:
        raise ProgramValidationError(
            f"Invalid Python at line {exc.lineno}: {exc.msg}", result
        ) from exc
    entries = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "predict"
    ]
    if len(entries) != 1 or not isinstance(entries[0], ast.FunctionDef):
        raise ProgramValidationError(
            "Define exactly one top-level def predict(state)", result
        )
    entry = entries[0]
    args = entry.args
    if (
        [arg.arg for arg in args.args] != ["state"]
        or args.posonlyargs
        or args.kwonlyargs
        or args.vararg
        or args.kwarg
        or args.defaults
        or entry.decorator_list
    ):
        raise ProgramValidationError(
            "predict must take only state, with no defaults or decorators", result
        )
    return result.text
