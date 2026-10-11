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
GENERATED_VIEWS = {"BUD.md", "docs/引き継ぎ/現在の引き継ぎ.md"}
DIRECT_CHAT_PREFIX = "直チャット/"
STATE_UPDATE_PREFIX = "docs/state-updates/"


def git(*args: str) -> list[str]:
    return subprocess.check_output(["git", *args], text=True, encoding="utf-8").splitlines()


def main() -> int:
    parents = git("rev-list", "--parents", "-n", "1", "HEAD")
    fields = parents[0].split()
    if len(fields) != 2:
        print("OK: initial commit has no parent; atomic-save guard skipped")
        return 0

    changed = set(git("-c", "core.quotepath=false", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD^", "HEAD"))
    bundle_touched = changed & BUNDLE
    direct_chat = sorted(p for p in changed if p.startswith(DIRECT_CHAT_PREFIX))
    state_updates = sorted(p for p in changed if p.startswith(STATE_UPDATE_PREFIX))

    if not bundle_touched and not direct_chat and not state_updates:
        print("OK: commit does not touch the canonical-state bundle")
        return 0

    # Canonical direct-chat save: state and both generated views are updated
    # atomically with exactly one source conversation record.
    if len(direct_chat) == 1 and BUNDLE <= changed and not state_updates:
        print("OK: atomic direct-chat save bundle")
        return 0

    # Canonical state-only update: a machine-readable audit record accompanies
    # the state and both generated views in the same commit.
    if not direct_chat and len(state_updates) == 1 and BUNDLE <= changed:
        print("OK: atomic canonical-state update bundle")
        return 0

    # Generated-view synchronization PRs intentionally change only the two
    # derived files; the canonical state is unchanged in this commit.
    if not direct_chat and not state_updates and changed == GENERATED_VIEWS:
        print("OK: generated-view synchronization bundle")
        return 0

    print("ERROR: invalid canonical-state save/update bundle.")
    print("Allowed commit shapes:")
    print("  - docs/現在状態.json + BUD.md + docs/引き継ぎ/現在の引き継ぎ.md + exactly one 直チャット/*.md")
    print("  - docs/現在状態.json + BUD.md + docs/引き継ぎ/現在の引き継ぎ.md + exactly one docs/state-updates/*.json")
    print("  - generated-view sync: BUD.md + docs/引き継ぎ/現在の引き継ぎ.md only")
    print(f"Changed paths: {sorted(changed)}")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
