#!/usr/bin/env python3
"""Mechanical repository checks for the ai-project surgery lane."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "docs/現在状態.json"

TIMESTAMP_CHAT = re.compile(r"^\d{4}-\d{2}-\d{2}_直チャット即時保存_(\d{3})\.md$")
HISTORIC_TIMESTAMP_CHAT = re.compile(r"^\d{4}-\d{2}-\d{2}_直チャット即時保存_\d{4}\.md$")
SECRET_PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9]{30,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{30,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]


def git_files() -> list[str]:
    out = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return [p for p in out.decode("utf-8").split("\0") if p]


def check_state(files: list[str]) -> None:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    path = state["direct_chat"]["latest_path"]
    latest = state["direct_chat"]["latest_saved"]
    if path not in files:
        raise SystemExit(f"FAIL: latest direct-chat path missing: {path}")
    match = re.search(r"_(\d{3})\.md$", path)
    if not match or match.group(1) != latest:
        raise SystemExit("FAIL: current state latest_saved/latest_path mismatch")


def check_chat_names(files: list[str]) -> None:
    names = [Path(p).name for p in files if p.startswith("直チャット/")]
    marked = [n for n in names if "_直チャット即時保存_" in n]
    bad = [
        n
        for n in marked
        if not TIMESTAMP_CHAT.fullmatch(n) and not HISTORIC_TIMESTAMP_CHAT.fullmatch(n)
    ]
    if bad:
        raise SystemExit("FAIL: malformed timestamped direct-chat names: " + ", ".join(sorted(bad)))

    # New saves use three-digit serials. Historical four-digit files are preserved
    # as legacy timestamped records and are intentionally excluded from this
    # duplicate check so their older numbering cannot collide with the new lane.
    serials = [int(match.group(1)) for n in marked if (match := TIMESTAMP_CHAT.fullmatch(n))]
    if len(serials) != len(set(serials)):
        raise SystemExit("FAIL: duplicate timestamped direct-chat serial")


def check_secrets(files: list[str]) -> None:
    text_exts = {".md", ".json", ".py", ".yml", ".yaml", ".txt", ".sh"}
    for rel in files:
        path = ROOT / rel
        if path.suffix.lower() not in text_exts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                raise SystemExit(f"FAIL: secret-like value detected in {rel}")


if __name__ == "__main__":
    files = git_files()
    check_state(files)
    check_chat_names(files)
    check_secrets(files)
    print("OK: repository integrity checks")
