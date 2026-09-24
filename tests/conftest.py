"""Offline test providers and fresh per-test program stores."""

from copy import deepcopy
from threading import Lock

import pytest

from jev_heuristic_adapter._cache import ProgramStore
from jev_heuristic_adapter._compiler import compile_question
from jev_heuristic_adapter.providers import ProviderResult

TRUE_SOURCE = 'def predict(state): return {"answer": True}'


class RecordingProvider:
    def __init__(self, source=TRUE_SOURCE):
        self.source = source
        self.identity = {"provider": "test", "model": "model-a"}
        self.error = None
        self.calls = 0
        self.requests = []
        self.results = []
        self._lock = Lock()

    def cache_identity(self):
        return deepcopy(self.identity)

    def request(self, messages):
        with self._lock:
            self.calls += 1
            attempt = self.calls
            self.requests.append(deepcopy(messages))
            source, error = self.source, self.error
        if error is not None:
            raise error
        text = source(messages) if callable(source) else source
        result = ProviderResult(text, True, 11, 17, {"attempt": attempt})
        with self._lock:
            self.results.append(result)
        return result


@pytest.fixture
def provider_factory():
    return RecordingProvider


@pytest.fixture
def provider(provider_factory):
    return provider_factory()


@pytest.fixture
def question():
    return {"type": "noul", "instructions": "Return true."}


@pytest.fixture
def store(tmp_path):
    return ProgramStore(tmp_path / "programs")


@pytest.fixture
def make_program(provider_factory):
    def make(source=TRUE_SOURCE, question=None):
        return compile_question(
            provider_factory(source),
            question={"type": "noul"} if question is None else question,
        )

    return make
