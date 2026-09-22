#!/usr/bin/env python3
"""Reject work/* PRs that only move canonical state/docs without doing main work."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess


ADMIN_ONLY = {
    "BUD.md",
    "docs/現在状態.json",
    "docs/引き継ぎ/現在の引き継ぎ.md",
}
SUBSTANTIVE_PREFIXES = (
    "scripts/",
    "tests/",
    "src/",
    "app/",
    "tools/",
    "docs/企画/",
    "schemas/",
)
SUBSTANTIVE_WORKFLOW_PREFIX = ".github/workflows/"


def changed_paths(base: str, head: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...{head}"],
        check=True,
        text=True,
        capture_output=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def validate(branch: str, paths: list[str]) -> tuple[bool, str]:
    if not branch.startswith("work/"):
        return True, "not a work/* branch; progress gate not required"
    substantive = [
        path for path in paths
        if path not in ADMIN_ONLY
        and path.startswith(SUBSTANTIVE_PREFIXES)
        or path.startswith(SUBSTANTIVE_WORKFLOW_PREFIX)
    ]
    if substantive:
        return True, "substantive main-work change detected: " + ", ".join(sorted(substantive))
    return False, (
        "work/* PR contains no substantive main-work change. "
        "State/view-only updates belong to the save track; "
        "a work/* PR must include implementation, tests, or workflow changes. "
        f"changed paths: {', '.join(sorted(paths)) or '(none)'}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    args = parser.parse_args()

    paths = changed_paths(args.base, args.head)
    ok, message = validate(args.branch, paths)
    print(("OK: " if ok else "FAIL: ") + message)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
