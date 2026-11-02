#!/usr/bin/env python3
"""Require direct-chat originals and their current pointer to be saved atomically."""
from __future__ import annotations
import argparse, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES = "rules/運用ルール.md"
DIRECT_CHAT_PREFIX = "直チャット/"

def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True, encoding="utf-8").strip()

def validate_changed_paths(paths: list[str]) -> tuple[bool, str]:
    changed = set(paths)
    direct_chat = sorted(path for path in changed if path.startswith(DIRECT_CHAT_PREFIX))
    if not direct_chat:
        return True, "commit does not change direct-chat originals"
    if len(direct_chat) != 1:
        return False, "a direct-chat save commit must add exactly one direct-chat original"
    if changed != {direct_chat[0], RULES}:
        return False, "a direct-chat save commit must change exactly one direct-chat original and rules/運用ルール.md; changed paths: " + ", ".join(sorted(changed))
    return True, "atomic direct-chat + operating-rules save bundle"

def validate_commit(root: Path, commit: str) -> tuple[bool, str]:
    parents = git("rev-list", "--parents", "-n", "1", commit).split()
    if len(parents) == 1:
        return True, "initial commit; atomic-save guard skipped"
    if len(parents) != 2:
        return False, "atomic-save validation requires a single-parent commit"
    parent = parents[1]
    raw = git("-c", "core.quotepath=false", "diff-tree", "--no-commit-id", "--name-only", "-r", parent, commit)
    return validate_changed_paths([line for line in raw.splitlines() if line])

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", default="HEAD")
    args = parser.parse_args()
    try:
        ok, message = validate_commit(ROOT, args.commit)
    except subprocess.CalledProcessError as exc:
        print(f"ERROR: unable to inspect commit: {exc}")
        return 1
    print(("OK: " if ok else "ERROR: ") + message)
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
