"""Prepare a version PR, then publish it after review and merge."""

import argparse
import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
REPO = "Ki-Seki/jev-heuristic-adapter"


def run(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def prepare(bump):
    require(bump in {"patch", "minor", "major"}, "Choose patch, minor, or major.")
    require(
        not run("git", "status", "--porcelain", "--untracked-files=no"),
        "Commit or stash tracked changes before preparing a release.",
    )
    run("git", "fetch", "origin", "main", "--tags")
    run("git", "switch", "main")
    run("git", "merge", "--ff-only", "origin/main")
    require(
        run("git", "rev-parse", "HEAD") == run("git", "rev-parse", "origin/main"),
        "Local main must match origin/main.",
    )
    preview = run(
        "uv",
        "version",
        "--bump",
        bump,
        "--dry-run",
        "--output-format",
        "json",
        "--frozen",
    )
    version = json.loads(preview)["version"]
    branch = f"release/v{version}"
    run("git", "switch", "-c", branch)
    run("uv", "version", version, "--no-sync")
    run("git", "add", "pyproject.toml", "uv.lock")
    run("git", "commit", "-m", f"Release v{version}")
    run("git", "push", "--set-upstream", "origin", branch)
    print(
        run(
            "gh",
            "pr",
            "create",
            "--repo",
            REPO,
            "--base",
            "main",
            "--head",
            branch,
            "--title",
            f"Release v{version}",
            "--body",
            f"Prepare v{version}; update the package version and uv lockfile. After merging, run `uv run scripts/release.py publish <PR_NUMBER>` to create the GitHub Release and trigger PyPI publishing.",
        )
    )


def publish(number):
    require(number.isdecimal() and int(number) > 0, "Provide a release PR number.")
    pr = json.loads(
        run(
            "gh",
            "pr",
            "view",
            number,
            "--repo",
            REPO,
            "--json",
            "state,baseRefName,headRefName,mergeCommit",
        )
    )
    require(
        pr["state"] == "MERGED" and pr["baseRefName"] == "main",
        "The release PR must be merged into main first.",
    )
    sha = pr["mergeCommit"]["oid"]
    run("git", "fetch", "origin", "main", "--tags")
    run("git", "merge-base", "--is-ancestor", sha, "origin/main")
    with TemporaryDirectory() as directory:
        Path(directory, "pyproject.toml").write_text(
            run("git", "show", f"{sha}:pyproject.toml"), encoding="utf-8"
        )
        version = run("uv", "version", "--short", "--directory", directory)
    tag = f"v{version}"
    require(
        pr["headRefName"] == f"release/{tag}",
        "PR branch must match its merged package version.",
    )
    require(
        not run("git", "tag", "--list", tag),
        f"Tag {tag} already exists; inspect its release or workflow run.",
    )
    run("gh", "pr", "checks", number, "--repo", REPO)
    print(
        run(
            "gh",
            "release",
            "create",
            tag,
            "--repo",
            REPO,
            "--target",
            sha,
            "--generate-notes",
            "--fail-on-no-commits",
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "publish"))
    parser.add_argument(
        "value",
        nargs="?",
        default="patch",
        help="prepare: patch/minor/major; publish: merged PR number",
    )
    args = parser.parse_args()
    try:
        (prepare if args.action == "prepare" else publish)(args.value)
    except subprocess.CalledProcessError as exc:
        parser.exit(1, f"Command failed: {' '.join(exc.cmd)}\n")
