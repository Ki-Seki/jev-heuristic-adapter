"""Persist compilation artifacts without executing their source."""

import json
import os
import re
import tempfile
from dataclasses import asdict
from pathlib import Path

from platformdirs import user_data_path

from ._program import CompiledQuestion


class ProgramStore:
    def __init__(self, directory: str | Path | None = None):
        """Use the user's application data directory unless explicitly overridden."""
        selected = (
            directory
            if directory is not None
            else user_data_path("jev-heuristic-adapter", appauthor=False)
        )
        self.directory = Path(selected).expanduser().resolve()

    def _path(self, artifact_id: str) -> Path:
        if not re.fullmatch(r"[0-9a-f]{64}", artifact_id):
            raise ValueError("Invalid artifact ID")
        return self.directory / f"{artifact_id}.json"

    def save(self, program: CompiledQuestion) -> Path:
        path = self._path(program.artifact_id)
        self._write(path, asdict(program))
        return path

    def _write(self, path: Path, data: dict[str, str]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(data, stream, ensure_ascii=False, allow_nan=False)
            Path(name).replace(path)
        finally:
            Path(name).unlink(missing_ok=True)

    def load(self, artifact_id: str) -> CompiledQuestion:
        data = json.loads(self._path(artifact_id).read_text(encoding="utf-8"))
        saved = CompiledQuestion(**data)
        saved.validate_integrity(artifact_id)
        return saved

    def lookup(self, key: str) -> CompiledQuestion | None:
        """Only an absent index entry is a cache miss; corrupt records raise."""
        path = self.directory / "index" / self._path(key).name
        try:
            artifact_id = json.loads(path.read_text(encoding="utf-8"))["artifact_id"]
        except FileNotFoundError:
            return None
        return self.load(artifact_id)

    def bind(self, key: str, program: CompiledQuestion) -> None:
        """Write the artifact before atomically publishing its recipe index."""
        path = self.directory / "index" / self._path(key).name
        self.save(program)
        self._write(path, {"artifact_id": program.artifact_id})
