#!/usr/bin/env python3
"""Validate and inspect persistent in-progress state for a blog proposal."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED = (
    "schema_version", "proposal_id", "status", "current_stage",
    "current_position", "confirmed_timeline", "taka_statements",
    "completed_interviews", "unresolved_items", "grounding",
    "state_changes", "operation_history", "save_boundary",
)
STATUSES = {"active", "paused", "completed"}


def validate(state: dict) -> None:
    missing = [key for key in REQUIRED if key not in state]
    if missing:
        raise ValueError("missing state fields: " + ", ".join(missing))
    if state["schema_version"] != 1:
        raise ValueError("unsupported schema_version")
    if not isinstance(state["proposal_id"], str) or not state["proposal_id"]:
        raise ValueError("proposal_id must be a non-empty string")
    if state["status"] not in STATUSES:
        raise ValueError("invalid status")
    if not isinstance(state["current_stage"], str) or not state["current_stage"]:
        raise ValueError("current_stage must be a non-empty string")
    for key in ("confirmed_timeline","taka_statements","completed_interviews",
                "unresolved_items","grounding","state_changes","operation_history"):
        if not isinstance(state[key], list):
            raise ValueError(f"{key} must be a list")
    if not state["grounding"]:
        raise ValueError("grounding must not be empty")
    if not isinstance(state["save_boundary"], dict):
        raise ValueError("save_boundary must be an object")
    if not isinstance(state["save_boundary"].get("direct_chat_path"), str) or not state["save_boundary"]["direct_chat_path"]:
        raise ValueError("save_boundary.direct_chat_path must be a non-empty string")


def load(path: Path) -> dict:
    state = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(state, dict):
        raise ValueError("work state must be a JSON object")
    validate(state)
    return state


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", type=Path, required=True)
    args = parser.parse_args()
    try:
        state = load(args.state)
        print(json.dumps({
            "ok": True,
            "proposal_id": state["proposal_id"],
            "current_stage": state["current_stage"],
            "status": state["status"],
            "completed_interviews": len(state["completed_interviews"]),
            "unresolved_items": len(state["unresolved_items"]),
        }, ensure_ascii=False, indent=2))
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"STOP: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
