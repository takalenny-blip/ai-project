#!/usr/bin/env python3
"""Enforce the atomic save bundle for current-state/direct-chat changes."""

from __future__ import annotations

import subprocess
import sys

BUNDLE = {
    "docs/現在状態.json",
    "BUD.md",
    "docs/引き継ぎ/現在の引き継ぎ.md",
}
DIRECT_CHAT_PREFIX = "直チャット/"


def git(*args: str) -> list[str]:
    return subprocess.check_output(["git", *args], text=True, encoding="utf-8").splitlines()


def main() -> int:
    parents = git("rev-list", "--parents", "-n", "1", "HEAD")
    fields = parents[0].split()
    if len(fields) != 2:
        print("OK: initial commit has no parent; atomic-save guard skipped")
        return 0

    changed = set(git("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD^", "HEAD"))
    bundle_touched = changed & BUNDLE
    direct_chat = sorted(p for p in changed if p.startswith(DIRECT_CHAT_PREFIX))

    if not bundle_touched and not direct_chat:
        print("OK: commit does not touch the atomic-save bundle")
        return 0

    expected = BUNDLE | {direct_chat[0]} if len(direct_chat) == 1 else BUNDLE
    missing = sorted(BUNDLE - changed)
    if len(direct_chat) != 1 or missing:
        print("ERROR: current-state/direct-chat changes must be one atomic save commit.")
        print("Use scripts/save_and_currentize.py; do not split the save across commits.")
        print(f"Changed direct-chat files: {len(direct_chat)}")
        if missing:
            print("Missing required files:")
            for path in missing:
                print(f"  - {path}")
        return 1

    print("OK: atomic save bundle contains exactly one direct-chat file and all current-state views")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
