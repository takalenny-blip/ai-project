#!/usr/bin/env python3
"""Explicit per-turn loop gate for callers that can supply canonical state.

This does not hook into ChatGPT's runtime. A caller must invoke it once per turn
and keep one history file per conversation/session.
"""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

try:
    from scripts import interaction_guard as guard
except ModuleNotFoundError:
    import interaction_guard as guard


def load_history(path: Path) -> list[dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or any(
        not isinstance(item, dict) or not isinstance(item.get("state_fingerprint"), str)
        for item in data
    ):
        raise ValueError("history must be a JSON list of state_fingerprint records")
    return data


def atomic_write_json(path: Path, data: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def record_turn(state_path: Path, history_path: Path, threshold: int = 2) -> str:
    state = guard.load_json(state_path)
    history = load_history(history_path)
    fingerprint = guard.state_fingerprint(state)
    candidate = history + [{"state_fingerprint": fingerprint}]
    guard.validate_loop(candidate, threshold)
    atomic_write_json(history_path, candidate)
    return fingerprint


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Record one turn's structured state; stop if it repeats without state change."
    )
    parser.add_argument("--state", type=Path, required=True, help="Path to docs/現在状態.json")
    parser.add_argument("--history", type=Path, required=True, help="Private JSON ledger for this conversation")
    parser.add_argument("--loop-threshold", type=int, default=2)
    args = parser.parse_args()
    try:
        fingerprint = record_turn(args.state, args.history, args.loop_threshold)
        print("OK: turn state recorded; fingerprint=" + fingerprint)
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print("STOP: " + str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
