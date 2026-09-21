#!/usr/bin/env python3
"""Mechanical preflight for progress claims and conversational loop risk."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

BLOCKED_PROGRESS_PATTERNS = (
    r"完了(?:しました|済み|した)",
    r"進(?:みました|んだ|めました|めた)",
    r"検証(?:しました|済み|した)",
    r"確認(?:しました|済み|した)",
    r"実施(?:しました|済み|した)",
    r"成功(?:しました|済み|した)",
    r"反映(?:しました|済み|した)",
    r"解消(?:しました|済み|した)",
    r"マージ(?:しました|済み|した)",
    r"verified",
    r"completed",
    r"merged",
)

CLAIM_PATTERNS = BLOCKED_PROGRESS_PATTERNS + (
    r"問題(?:ありません|なし)",
    r"対応(?:済み|しました|した)",
)

def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def state_fingerprint(state: dict) -> str:
    payload = {
        "next_step": state.get("next_step", {}),
        "current_position": state.get("current_position", {}),
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def has_progress_claim(text: str) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in CLAIM_PATTERNS)

def validate_blocked_output(state: dict, text: str) -> None:
    readiness = (state.get("next_step") or {}).get("readiness")
    if readiness == "blocked" and has_progress_claim(text):
        raise ValueError(
            "blocked next_step rejects progress/completion claims; "
            "only evidence acquisition, preflight, or unblock work may be reported"
        )

def validate_evidence_claim(text: str, evidence: list[dict] | None) -> None:
    if not has_progress_claim(text):
        return
    evidence = evidence or []
    if not evidence:
        raise ValueError("progress/completion claim requires explicit evidence records")
    for item in evidence:
        if not item.get("kind") or not item.get("path") or not item.get("sha256"):
            raise ValueError("evidence record requires kind, path, and sha256")
        path = Path(item["path"])
        if not path.is_file():
            raise ValueError("evidence file does not exist: " + str(path))
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != item["sha256"]:
            raise ValueError("evidence SHA-256 mismatch: " + str(path))

def validate_loop(history: list[dict], threshold: int = 2) -> None:
    if threshold < 2:
        raise ValueError("loop threshold must be >= 2")
    if len(history) < threshold:
        return
    tail = history[-threshold:]
    fingerprints = [item.get("state_fingerprint") for item in tail]
    no_progress = all(item.get("progress") is False for item in tail)
    if fingerprints[0] and len(set(fingerprints)) == 1 and no_progress:
        raise ValueError(
            f"forced stop: identical state repeated {threshold} times without progress"
        )

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--text", default="")
    parser.add_argument("--evidence-json", type=Path)
    parser.add_argument("--history", type=Path)
    parser.add_argument("--loop-threshold", type=int, default=2)
    args = parser.parse_args()
    try:
        state = load_json(args.state)
        validate_blocked_output(state, args.text)
        evidence = None
        if args.evidence_json:
            evidence = json.loads(args.evidence_json.read_text(encoding="utf-8"))
        validate_evidence_claim(args.text, evidence)
        if args.history:
            history = json.loads(args.history.read_text(encoding="utf-8"))
            if not isinstance(history, list):
                raise ValueError("history must be a JSON list")
            validate_loop(history, args.loop_threshold)
        print("OK: interaction preflight passed")
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"STOP: {exc}")
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
