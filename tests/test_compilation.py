from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from jev_heuristic_adapter import HeuristicAdapterClient
from jev_heuristic_adapter._cache import ProgramStore
from jev_heuristic_adapter._schema import build_output_schema
from jev_heuristic_adapter.providers import ProviderResult


class FakeProvider:
    def __init__(self):
        self.source = 'def predict(state): return {"answer": True}'
        self.calls = 0

    def cache_identity(self):
        return {"provider": "compilation-test"}

    def request(self, messages):
        self.calls += 1
        return ProviderResult(self.source, True, 1, 1, {"attempt": self.calls})


class CompilationTests(TestCase):
    def test_incorrect_program_replaces_and_reuses_the_cached_version(self):
        provider = FakeProvider()
        questions = {"q": {"type": "noul", "instructions": "Return true."}}
        examples = [{"state": "fixture", "answers": {"q": True}}]
        with TemporaryDirectory() as directory:
            client = HeuristicAdapterClient(provider, ProgramStore(directory))
            original = client.compile(questions, examples)
            provider.source = 'def predict(state): return {"answer": False}'
            replacement = client.compile(questions, examples, force=True)
            self.assertNotEqual(replacement, original)
            self.assertEqual(client.system_one("fixture", questions).nouls["q"].noul, 0)
            fresh = HeuristicAdapterClient(provider, ProgramStore(directory))
            self.assertEqual(fresh.compile(questions, examples), replacement)
            self.assertEqual(fresh.system_one("fixture", questions).nouls["q"].noul, 0)
            self.assertEqual(provider.calls, 2)

    def test_compile_does_not_execute_examples(self):
        provider = FakeProvider()
        provider.source = 'def predict(state): raise RuntimeError("predict executed")'
        questions = {"q": {"type": "noul", "instructions": "Return true."}}
        examples = [{"state": "fixture", "answers": {"q": True}}]
        with TemporaryDirectory() as directory:
            client = HeuristicAdapterClient(provider, ProgramStore(directory))
            original = client.compile(questions, examples)
            fresh = HeuristicAdapterClient(provider, ProgramStore(directory))
            self.assertEqual(fresh.compile(questions, examples), original)
            self.assertEqual(provider.calls, 1)
            with self.assertRaisesRegex(RuntimeError, "predict executed"):
                fresh.system_one("fixture", questions)

    def test_output_schema_change_recompiles_without_a_manual_version(self):
        provider = FakeProvider()
        questions = {"q": {"type": "noul", "instructions": "Return true."}}
        schema = build_output_schema(questions["q"])
        schema["description"] = "Updated output contract."
        with TemporaryDirectory() as directory:
            client = HeuristicAdapterClient(provider, ProgramStore(directory))
            original = client.compile(questions)
            with patch(
                "jev_heuristic_adapter._compiler.build_output_schema",
                return_value=schema,
            ):
                updated = client.compile(questions)
                self.assertNotEqual(updated, original)
                self.assertEqual(client.compile(questions), updated)
            self.assertEqual(client.compile(questions), original)
            self.assertEqual(provider.calls, 2)
