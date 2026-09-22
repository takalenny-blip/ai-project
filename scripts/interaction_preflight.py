#!/usr/bin/env python3
"""Mandatory acceptance-layer entrypoint for interaction preflight.

This wrapper deliberately requires a candidate text, evidence manifest, and
persistent interaction history. The repository cannot infer conversational
history, so callers must provide all three inputs explicitly.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import interaction_guard as guard
import blog_work_state


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--text", required=True)
    parser.add_argument("--evidence-json", type=Path, required=True)
    parser.add_argument("--history", type=Path, required=True)
    parser.add_argument("--loop-threshold", type=int, default=2)
    parser.add_argument("--work-state", type=Path)
    args = parser.parse_args()

    try:
        state = guard.load_json(args.state)
        if args.work_state:
            blog_work_state.load(args.work_state)
        evidence = json.loads(args.evidence_json.read_text(encoding="utf-8"))
        history = json.loads(args.history.read_text(encoding="utf-8"))
        if not isinstance(evidence, list):
            raise ValueError("evidence must be a JSON list")
        if not isinstance(history, list):
            raise ValueError("history must be a JSON list")
        guard.validate_blocked_output(state, args.text)
        guard.validate_evidence_claim(args.text, evidence)
        guard.validate_loop(history, args.loop_threshold)
        print("OK: mandatory interaction preflight passed")
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"STOP: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
