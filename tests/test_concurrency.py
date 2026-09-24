"""Deterministic concurrency tests using gates, never timing-based sleeps."""

from concurrent.futures import Future, ThreadPoolExecutor
from threading import Barrier, Event

import pytest

from jev_heuristic_adapter import _compiler as compiler
from jev_heuristic_adapter._cache import ProgramStore
from jev_heuristic_adapter._compiler import compile_or_load

SOURCE = 'def predict(state): return {"answer": True}'


class CompilationInterrupted(BaseException):
    pass


@pytest.mark.parametrize(
    "failure",
    [None, RuntimeError("provider failed"), CompilationInterrupted("interrupted")],
    ids=["result", "exception", "base-exception"],
)
def test_concurrent_callers_share_results_or_failures_and_release_the_flight(
    provider_factory, question, store, monkeypatch, failure
):
    entered, release, follower_waiting = Event(), Event(), Event()

    class ObservedFuture(Future):
        def result(self, *args, **kwargs):
            follower_waiting.set()
            return super().result(*args, **kwargs)

    def slow_generation(messages):
        entered.set()
        assert release.wait(10), "test did not release the provider"
        if failure is not None:
            raise failure
        return SOURCE

    monkeypatch.setattr(compiler, "Future", ObservedFuture)
    provider = provider_factory(slow_generation)
    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(
            compile_or_load, provider, question=question, store=store
        )
        try:
            assert entered.wait(5)
            second = executor.submit(
                compile_or_load, provider, question=question, store=store
            )
            assert follower_waiting.wait(5), (
                "second caller did not join the in-flight work"
            )
        finally:
            release.set()
        if failure is None:
            assert first.result(timeout=5) is second.result(timeout=5)
        else:
            for future in (first, second):
                with pytest.raises(type(failure)) as caught:
                    future.result(timeout=5)
                assert caught.value is failure
    assert provider.calls == 1
    provider.source = SOURCE
    compile_or_load(provider, question=question, store=store)
    assert provider.calls == (1 if failure is None else 2)


@pytest.mark.parametrize("separation", ["question", "directory"])
def test_independent_compilations_can_enter_the_provider_concurrently(
    provider_factory, question, store, tmp_path, separation
):
    both_entered = Barrier(2)

    def generation(messages):
        both_entered.wait(timeout=5)
        return SOURCE

    provider = provider_factory(generation)
    other_question = (
        {**question, "instructions": "Another question"}
        if separation == "question"
        else question
    )
    other_store = (
        ProgramStore(tmp_path / "other") if separation == "directory" else store
    )
    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(
            compile_or_load, provider, question=question, store=store
        )
        second = executor.submit(
            compile_or_load, provider, question=other_question, store=other_store
        )
        assert first.result(timeout=10).source == SOURCE
        assert second.result(timeout=10).source == SOURCE
    assert provider.calls == 2


def test_cached_read_is_not_blocked_by_a_forced_recompile(provider, question, store):
    original = compile_or_load(provider, question=question, store=store)
    entered, release = Event(), Event()

    def generation(messages):
        entered.set()
        assert release.wait(10)
        return 'def predict(state): return {"answer": False}'

    provider.source = generation
    with ThreadPoolExecutor(max_workers=2) as executor:
        forced = executor.submit(
            compile_or_load, provider, question=question, store=store, force=True
        )
        try:
            assert entered.wait(5)
            cached = executor.submit(
                compile_or_load, provider, question=question, store=store
            )
            assert cached.result(timeout=5) == original
        finally:
            release.set()
        assert forced.result(timeout=5).artifact_id != original.artifact_id
    assert provider.calls == 2


def test_mutating_caller_inputs_during_compilation_does_not_change_the_snapshot(
    provider, question, store, monkeypatch
):
    import json

    entered, release = Event(), Event()
    examples = [{"state": {"items": [1]}, "answer": True}]
    identity = provider.cache_identity()

    def delayed_identity():
        entered.set()
        assert release.wait(10)
        return identity

    monkeypatch.setattr(provider, "cache_identity", delayed_identity)
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            compile_or_load, provider, question=question, examples=examples, store=store
        )
        try:
            assert entered.wait(5)
            question["instructions"] = "mutated"
            examples[0]["state"]["items"].append(2)
        finally:
            release.set()
        program = future.result(timeout=5)
    assert json.loads(program.question_json)["instructions"] == "Return true."
    request = json.loads(program.request_json)
    assert json.loads(request[1]["content"])["examples"][0]["state"] == {"items": [1]}
