#!/usr/bin/env python3
"""Require every direct-chat save commit to add exactly one new original file."""
from __future__ import annotations
import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECT_CHAT_PREFIX = "直チャット/"
RECORD_RE = re.compile(
    r"\d{4}-\d{2}-\d{2}_直チャット即時保存_"
    r"\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}(?:\.\d{6})?\+0900\.md$"
)

def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=root)

def parse_name_status_z(raw: bytes) -> list[tuple[str, str]]:
    tokens = raw.decode("utf-8", errors="surrogateescape").split("\0")
    if tokens and tokens[-1] == "":
        tokens.pop()
    out = []
    i = 0
    while i < len(tokens):
        status = tokens[i]
        i += 1
        if status.startswith(("R", "C")):
            if i + 1 >= len(tokens):
                raise ValueError("truncated rename/copy diff record")
            old, new = tokens[i], tokens[i + 1]
            i += 2
            out.extend([(status, old), (status, new)])
        else:
            if i >= len(tokens):
                raise ValueError("truncated name-status diff record")
            out.append((status, tokens[i]))
            i += 1
    return out

def validate_changed_paths(entries: list[tuple[str, str]]) -> tuple[bool, str]:
    chat = [(status, path) for status, path in entries if path.startswith(DIRECT_CHAT_PREFIX)]
    if not chat:
        return True, "commit does not change direct-chat originals"
    if len(chat) != 1 or len(entries) != 1:
        return False, "direct-chat save commit must contain exactly one changed path and no sidecar files"
    status, path = chat[0]
    if status != "A":
        return False, "direct-chat originals may only be newly added; modification, deletion, and rename are prohibited"
    if not RECORD_RE.fullmatch(Path(path).name):
        return False, "new direct-chat file must use the canonical Japan-time timestamp filename"
    return True, "single new direct-chat original; no current-state snapshots or sidecar views"

def validate_commit(root: Path, commit: str) -> tuple[bool, str]:
    parents = git(root, "rev-list", "--parents", "-n", "1", commit).decode().split()
    if len(parents) != 2:
        return False, "direct-chat save validation requires a single-parent commit"
    parent = parents[1]
    raw = git(root, "-c", "core.quotepath=false", "diff-tree", "--no-commit-id", "--name-status", "-r", "-z", parent, commit)
    return validate_changed_paths(parse_name_status_z(raw))

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", default="HEAD")
    args = parser.parse_args()
    try:
        ok, message = validate_commit(ROOT, args.commit)
    except (subprocess.CalledProcessError, ValueError) as exc:
        print(f"ERROR: unable to inspect commit: {exc}")
        return 1
    print(("OK: " if ok else "ERROR: ") + message)
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
