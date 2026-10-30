#!/usr/bin/env python3
"""Enforce atomic canonical-state saves, including safe historical backfills."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = {
    "docs/現在状態.json",
    "BUD.md",
    "docs/引き継ぎ/現在の引き継ぎ.md",
}
GENERATED_VIEWS = {"BUD.md", "docs/引き継ぎ/現在の引き継ぎ.md"}
DIRECT_CHAT_PREFIX = "直チャット/"
STATE_UPDATE_PREFIX = "docs/state-updates/"
RECORD_RE = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2})_直チャット即時保存_"
    r"(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}\.\d{6}\+0900)\.md$"
)


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True, encoding="utf-8").strip()


def safe_historical_backfill(
    path: str,
    status: str,
    previous_state_text: str,
    current_state_text: str,
    latest_record_exists_in_parent: bool,
) -> tuple[bool, str]:
    """Allow one new, older archive record without changing the current pointer."""
    if not path.startswith(DIRECT_CHAT_PREFIX):
        return False, "backfill path is outside 直チャット/"
    if status != "A":
        return False, "historical backfill must add a new file, never modify one"
    match = RECORD_RE.fullmatch(Path(path).name)
    if not match:
        return False, "historical backfill filename has no canonical timestamp"
    if previous_state_text != current_state_text:
        return False, "historical backfill must not change canonical state or generated views"
    try:
        previous_state = json.loads(previous_state_text)
        latest = previous_state["direct_chat"]["latest_saved"]
        latest_path = previous_state["direct_chat"]["latest_path"]
        candidate_time = datetime.strptime(match.group("timestamp"), "%Y-%m-%dT%H-%M-%S.%f%z")
        latest_time = datetime.strptime(latest, "%Y-%m-%dT%H-%M-%S.%f%z")
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return False, "parent canonical state has no valid latest direct-chat pointer"
    if path == latest_path:
        return False, "backfill cannot replace the current latest record"
    if candidate_time >= latest_time:
        return False, "record is not older than the current latest direct-chat record"
    if not latest_record_exists_in_parent:
        return False, "parent latest direct-chat target is missing"
    return True, "safe historical direct-chat backfill; latest pointer remains unchanged"


def validate_commit(root: Path, commit: str) -> tuple[bool, str]:
    parents = git(root, "rev-list", "--parents", "-n", "1", commit).split()
    if len(parents) == 1:
        return True, "initial commit; atomic-save guard skipped"
    if len(parents) != 2:
        return False, "atomic-save validation requires a single-parent commit"
    parent = parents[1]
    raw = git(root, "-c", "core.quotepath=false", "diff-tree", "--no-commit-id", "--name-status", "-r", parent, commit)
    entries = [line.split("\\t", 1) for line in raw.splitlines() if line]
    statuses = {parts[1]: parts[0] for parts in entries if len(parts) == 2}
    changed = set(statuses)
    bundle_touched = changed & BUNDLE
    direct_chat = sorted(p for p in changed if p.startswith(DIRECT_CHAT_PREFIX))
    state_updates = sorted(p for p in changed if p.startswith(STATE_UPDATE_PREFIX))

    if not bundle_touched and not direct_chat and not state_updates:
        return True, "commit does not touch the canonical-state bundle"

    if len(direct_chat) == 1 and changed == {direct_chat[0]}:
        try:
            previous_state = git(root, "show", f"{parent}:docs/現在状態.json")
            current_state = git(root, "show", f"{commit}:docs/現在状態.json")
            pointer = json.loads(previous_state)["direct_chat"]["latest_path"]
            subprocess.run(
                ["git", "cat-file", "-e", f"{parent}:{pointer}"],
                cwd=root, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            latest_exists = True
        except (subprocess.CalledProcessError, KeyError, TypeError, json.JSONDecodeError):
            latest_exists = False
            previous_state = locals().get("previous_state", "")
            current_state = locals().get("current_state", "")
        ok, reason = safe_historical_backfill(
            direct_chat[0], statuses.get(direct_chat[0], ""),
            previous_state, current_state, latest_exists,
        )
        return ok, reason

    if len(direct_chat) == 1 and BUNDLE <= changed and not state_updates:
        return True, "atomic direct-chat save bundle"
    if not direct_chat and len(state_updates) == 1 and BUNDLE <= changed:
        return True, "atomic canonical-state update bundle"
    if not direct_chat and not state_updates and changed == GENERATED_VIEWS:
        return True, "generated-view synchronization bundle"
    return False, (
        "invalid canonical-state save/update bundle; allowed: one direct-chat plus full bundle, "
        "one state-update audit plus full bundle, generated views only, or a verified older "
        f"single-file historical backfill. Changed paths: {sorted(changed)}"
    )


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
