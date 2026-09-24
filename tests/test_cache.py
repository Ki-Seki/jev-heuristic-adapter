"""Disk cache behavior, corruption detection, and atomic publication."""

import json

import pytest

from jev_heuristic_adapter._cache import ProgramStore

KEY = "a" * 64


def test_default_directory_is_lazy_and_missing_index_is_a_cache_miss(
    tmp_path, monkeypatch
):
    directory = tmp_path / "app-data"
    monkeypatch.setattr(
        "jev_heuristic_adapter._cache.user_data_path", lambda *args, **kwargs: directory
    )
    store = ProgramStore()
    assert store.directory == directory.resolve()
    assert store.lookup(KEY) is None
    assert not directory.exists()


def test_custom_directory_is_resolved(tmp_path):
    store = ProgramStore(tmp_path / "nested" / ".." / "programs")
    assert store.directory == (tmp_path / "programs").resolve()


@pytest.mark.parametrize("identifier", ["", "../escape", "a" * 63, "g" * 64, "A" * 64])
def test_invalid_artifact_and_index_identifiers_are_rejected(store, identifier):
    with pytest.raises(ValueError, match="Invalid artifact ID"):
        store.load(identifier)
    with pytest.raises(ValueError, match="Invalid artifact ID"):
        store.lookup(identifier)


def test_roundtrip_does_not_execute_saved_source(store, make_program):
    source = 'raise AssertionError("source was executed")\ndef predict(state): return {"answer": True}'
    program = make_program(source, {"type": "noul", "instructions": "判断是否合格"})
    path = store.save(program)
    assert path == store.directory / f"{program.artifact_id}.json"
    assert "判断是否合格" in path.read_text(encoding="utf-8")
    assert store.load(program.artifact_id) == program
    store.bind(KEY, program)
    assert ProgramStore(store.directory).lookup(KEY) == program


@pytest.mark.parametrize(
    ("contents", "error"),
    [
        ("{broken", json.JSONDecodeError),
        ("{}", KeyError),
        (json.dumps({"artifact_id": "b" * 64}), FileNotFoundError),
    ],
)
def test_corrupt_or_dangling_indexes_are_not_treated_as_cache_misses(
    store, contents, error
):
    path = store.directory / "index" / f"{KEY}.json"
    path.parent.mkdir(parents=True)
    path.write_text(contents, encoding="utf-8")
    with pytest.raises(error):
        store.lookup(KEY)


def test_malformed_artifact_json_is_reported(store, make_program):
    program = make_program()
    path = store.save(program)
    path.write_text("{broken", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        store.load(program.artifact_id)


def test_valid_artifact_under_another_filename_is_rejected(store, make_program):
    first = make_program()
    second = make_program('def predict(state): return {"answer": False}')
    first_path = store.save(first)
    second_path = store.save(second)
    first_path.write_bytes(second_path.read_bytes())
    with pytest.raises(ValueError, match="inconsistent"):
        store.load(first.artifact_id)


def test_interrupted_write_preserves_old_file_and_removes_temporary_file(
    store, make_program, monkeypatch
):
    program = make_program()
    path = store.save(program)
    original = path.read_bytes()

    def interrupted_dump(data, stream, **kwargs):
        stream.write("partial write")
        raise OSError("disk failure")

    monkeypatch.setattr("jev_heuristic_adapter._cache.json.dump", interrupted_dump)
    with pytest.raises(OSError, match="disk failure"):
        store.save(program)
    assert path.read_bytes() == original
    assert list(store.directory.glob("*.tmp")) == []
    assert store.load(program.artifact_id) == program


def test_failed_artifact_save_does_not_replace_the_index(
    store, make_program, monkeypatch
):
    first = make_program()
    second = make_program('def predict(state): return {"answer": False}')
    store.bind(KEY, first)

    def fail_save(program):
        raise OSError("cannot save artifact")

    monkeypatch.setattr(store, "save", fail_save)
    with pytest.raises(OSError, match="cannot save artifact"):
        store.bind(KEY, second)
    assert store.lookup(KEY) == first
