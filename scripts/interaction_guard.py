#!/usr/bin/env python3
"""Mechanical preflight for progress claims and conversational loop risk."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
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


def state_fingerprint(state: dict, board_path: Path) -> str:
    """Fingerprint the actual Dropbox board, never retired GitHub queue fields."""
    if state.get("work_queue_source") != "dropbox_board":
        raise ValueError("work_queue_source must be dropbox_board")
    if state.get("work_items") != []:
        raise ValueError("legacy GitHub work_items must be empty")
    if "next_step" in state:
        raise ValueError("legacy next_step field is retired")
    if not board_path.is_file():
        raise ValueError("Dropbox work board is missing or unavailable: " + str(board_path))
    try:
        with zipfile.ZipFile(board_path) as workbook:
            if workbook.testzip() is not None:
                raise ValueError("Dropbox work board contains a corrupt XLSX member")
            required = {"[Content_Types].xml", "xl/workbook.xml"}
            missing = required.difference(workbook.namelist())
            if missing:
                raise ValueError("Dropbox work board is not a valid XLSX workbook")
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        raise ValueError("Dropbox work board is unreadable: " + str(exc)) from exc
    payload = {
        "work_queue_source": "dropbox_board",
        "execution_environment": state.get("execution_environment", {}),
        "dropbox_board_sha256": hashlib.sha256(board_path.read_bytes()).hexdigest(),
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def has_progress_claim(text: str) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in CLAIM_PATTERNS)


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
    # Progress is represented by the structured fingerprint. Do not trust a
    # caller-supplied progress boolean that can contradict unchanged state.
    if fingerprints[0] and len(set(fingerprints)) == 1:
        raise ValueError(
            f"forced stop: identical structured work state repeated {threshold} times"
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
