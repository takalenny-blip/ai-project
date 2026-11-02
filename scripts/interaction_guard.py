#!/usr/bin/env python3
"""Mechanical preflight for progress claims and conversational loop risk."""
from __future__ import annotations
import argparse, hashlib, json, os, re, zipfile
from pathlib import Path
try:
    from scripts.current_state_guard import validate_rules
except ModuleNotFoundError:
    from current_state_guard import validate_rules

BLOCKED_PROGRESS_PATTERNS = (
    r"完了(?:しました|済み|した)", r"進(?:みました|んだ|めました|めた)",
    r"検証(?:しました|済み|した)", r"確認(?:しました|済み|した)",
    r"実施(?:しました|済み|した)", r"成功(?:しました|済み|した)",
    r"反映(?:しました|済み|した)", r"解消(?:しました|済み|した)",
    r"マージ(?:しました|済み|した)", r"verified", r"completed", r"merged",
)
CLAIM_PATTERNS = BLOCKED_PROGRESS_PATTERNS + (r"問題(?:ありません|なし)", r"対応(?:済み|しました|した)")

def load_rules(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    validate_rules(text)
    return text

def validate_board(path: Path) -> None:
    if not path.is_file():
        raise ValueError("Dropbox work board is missing or unavailable: " + str(path))
    try:
        with zipfile.ZipFile(path) as workbook:
            if workbook.testzip() is not None:
                raise ValueError("Dropbox work board contains a corrupt XLSX member")
            missing = {"[Content_Types].xml", "xl/workbook.xml"}.difference(workbook.namelist())
            if missing:
                raise ValueError("Dropbox work board is not a valid XLSX workbook")
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        raise ValueError("Dropbox work board is unreadable: " + str(exc)) from exc

def state_fingerprint(rules_path: Path, board_path: Path) -> str:
    """Fingerprint the sole rules source and the separate Dropbox work queue."""
    rules = load_rules(rules_path)
    validate_board(board_path)
    payload = {
        "rules_sha256": hashlib.sha256(rules.encode("utf-8")).hexdigest(),
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
    if fingerprints[0] and len(set(fingerprints)) == 1:
        raise ValueError(f"forced stop: identical structured work state repeated {threshold} times")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rules", type=Path, default=Path(__file__).resolve().parents[1] / "rules" / "運用ルール.md")
    parser.add_argument("--text", default="")
    parser.add_argument("--evidence-json", type=Path)
    parser.add_argument("--history", type=Path)
    parser.add_argument("--loop-threshold", type=int, default=2)
    args = parser.parse_args()
    try:
        load_rules(args.rules)
        evidence = json.loads(args.evidence_json.read_text(encoding="utf-8")) if args.evidence_json else None
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
