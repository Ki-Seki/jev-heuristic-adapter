"""Build compilation requests from task definitions and examples."""

import ast
import hashlib
import json
from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import asdict
from typing import Any

from ._cache import ProgramStore
from ._program import CompiledQuestion
from ._prompt import SYSTEM_PROMPT
from ._runtime import OutputValidator
from ._schema import build_output_schema
from .providers import Provider, ProviderResult


def build_messages(
    question: Mapping[str, Any],
    examples: Sequence[Mapping[str, Any]] = (),
) -> list[dict[str, str]]:
    """Accept one JSON-ready question and zero or more {state, answer} examples."""
    validator = OutputValidator(question)
    for example in examples:
        if not isinstance(example, Mapping) or set(example) != {"state", "answer"}:
            raise ValueError("Each example must contain exactly state and answer")
        validator.validate({"answer": example["answer"]})
    payload = {
        "task_definition": {
            "question": dict(question),
            "output_schema": build_output_schema(question),
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
    question: Mapping[str, Any],
    examples: Sequence[Mapping[str, Any]] = (),
) -> ProviderResult:
    """Request one program returning {"answer": value}; source validation follows."""
    return provider.request(build_messages(question, examples))


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


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)


def compile_question(
    provider: Provider,
    *,
    question: Mapping[str, Any],
    examples: Sequence[Mapping[str, Any]] = (),
) -> CompiledQuestion:
    """Generate and syntax-check one artifact; execution checks are still pending."""
    question_json = _canonical_json(dict(question))
    messages = build_messages(json.loads(question_json), examples)
    request_json = _canonical_json(messages)
    result = provider.request(json.loads(request_json))
    source = validate_program(result)
    generation_json = _canonical_json(asdict(result))
    question_id = hashlib.sha256(
        ("predict-answer-v1\n" + question_json).encode()
    ).hexdigest()
    artifact_id = hashlib.sha256(
        _canonical_json([question_id, source, request_json, generation_json]).encode()
    ).hexdigest()
    return CompiledQuestion(
        question_id, artifact_id, question_json, source, request_json, generation_json
    )


def compile_key(
    provider: Provider,
    *,
    question: Mapping[str, Any],
    examples: Sequence[Mapping[str, Any]] = (),
) -> str:
    """Identify a compilation recipe without invoking the provider."""
    build_messages(question, examples)  # Validate inputs before cache lookup.
    identity = {
        "contract": "predict-answer-v1",
        "provider": provider.cache_identity(),
        "question": dict(question),
        "examples": list(examples),
        "prompt": SYSTEM_PROMPT,
    }
    return hashlib.sha256(_canonical_json(identity).encode()).hexdigest()


def compile_or_load(
    provider: Provider,
    *,
    question: Mapping[str, Any],
    examples: Sequence[Mapping[str, Any]] = (),
    store: ProgramStore | None = None,
    force: bool = False,
) -> CompiledQuestion:
    """Reuse a recipe's artifact or generate one; execution checks remain pending."""
    question, examples = deepcopy(dict(question)), deepcopy(list(examples))
    store = ProgramStore() if store is None else store
    key = compile_key(provider, question=question, examples=examples)
    if not force:
        cached = store.lookup(key)
        if cached is not None:
            return cached
    program = compile_question(provider, question=question, examples=examples)
    store.bind(key, program)
    return program
