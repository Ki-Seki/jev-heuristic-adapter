"""Release preparation and publication boundaries, without remote writes."""

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "release", Path(__file__).resolve().parents[1] / "scripts/release.py"
)
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


@pytest.fixture
def cli(monkeypatch):
    state = {
        "state": "MERGED",
        "baseRefName": "main",
        "headRefName": "release/v0.1.1",
        "mergeCommit": {"oid": "a" * 40},
        "version": "0.1.1",
        "dirty": "",
        "head": "main-commit",
        "tag": "",
        "check_exit": 0,
        "ancestor_exit": 0,
    }
    calls = []

    def run(*args):
        calls.append(args)
        if args[:3] == ("gh", "pr", "view") or "--dry-run" in args:
            return json.dumps(state)
        if args[:2] == ("git", "status"):
            return state["dirty"]
        if args[:2] == ("git", "rev-parse"):
            return state["head"] if args[-1] == "HEAD" else "main-commit"
        if args[:3] == ("git", "tag", "--list"):
            return state["tag"]
        if args[:2] == ("git", "show"):
            return f'[project]\nname = "example"\nversion = "{state["version"]}"\n'
        if args[:3] == ("uv", "version", "--short"):
            assert Path(args[-1], "pyproject.toml").read_text().startswith("[project]")
            return state["version"]
        for prefix, key in (
            (("gh", "pr", "checks"), "check_exit"),
            (("git", "merge-base", "--is-ancestor"), "ancestor_exit"),
        ):
            if args[:3] == prefix and state[key]:
                raise subprocess.CalledProcessError(state[key], args)
        return "https://github.com/Ki-Seki/jev-heuristic-adapter/pull/9"

    monkeypatch.setattr(release, "run", run)
    return state, calls


def test_prepare_opens_a_version_pr_without_publishing(cli):
    _, calls = cli
    release.prepare("patch")
    assert ("git", "switch", "-c", "release/v0.1.1") in calls
    assert ("uv", "version", "0.1.1", "--no-sync") in calls
    assert ("git", "add", "pyproject.toml", "uv.lock") in calls
    assert any(c[:3] == ("gh", "pr", "create") for c in calls)
    assert not any(c[:2] == ("gh", "release") for c in calls)


@pytest.mark.parametrize(
    "change", [{"dirty": " M pyproject.toml"}, {"head": "local-only"}]
)
def test_prepare_rejects_uncommitted_or_unpushed_work(cli, change):
    state, calls = cli
    state.update(change)
    with pytest.raises(SystemExit):
        release.prepare("patch")
    assert not any(c[:2] == ("git", "commit") for c in calls)


def test_publish_tags_the_merged_commit_not_current_main(cli):
    _, calls = cli
    release.publish("9")
    publish = next(c for c in calls if c[:3] == ("gh", "release", "create"))
    assert publish[3] == "v0.1.1"
    assert publish[publish.index("--target") + 1] == "a" * 40
    assert "--generate-notes" in publish
    assert ("git", "show", f"{'a' * 40}:pyproject.toml") in calls
    assert not any(c[:2] == ("git", "switch") for c in calls)


@pytest.mark.parametrize(
    "change",
    [
        {"state": "OPEN"},
        {"baseRefName": "develop"},
        {"headRefName": "feature/unrelated"},
        {"version": "0.2.0"},
        {"tag": "v0.1.1"},
        {"check_exit": 1},
        {"check_exit": 8},
        {"ancestor_exit": 1},
    ],
)
def test_publish_refuses_an_unreviewed_or_inconsistent_release(cli, change):
    state, calls = cli
    state.update(change)
    with pytest.raises((SystemExit, subprocess.CalledProcessError)):
        release.publish("9")
    assert not any(c[:3] == ("gh", "release", "create") for c in calls)


@pytest.mark.parametrize(
    "action,value", [("prepare", "rc"), ("publish", "patch"), ("publish", "0")]
)
def test_bad_arguments_have_no_side_effects(cli, action, value):
    _, calls = cli
    with pytest.raises(SystemExit):
        getattr(release, action)(value)
    assert calls == []
