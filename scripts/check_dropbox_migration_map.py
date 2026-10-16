#!/usr/bin/env python3
"""Validate the Dropbox migration dependency map and safety-critical guards."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "docs" / "計画" / "Dropbox作業管理依存関係対応表_20261016.md"
DESIGN_PATH = ROOT / "docs" / "計画" / "Dropbox作業管理移行設計.md"
NO_REWORK_GUARD_PATH = ROOT / "docs" / "計画" / "Dropbox作業管理002再作業禁止ガード.md"

REQUIRED_PATHS = (
    "README.md",
    "docs/AI_READ_MAP.md",
    "rules/README.md",
    "rules/運用ルール.md",
    "scripts/work_queue.py",
    "scripts/generate_current_views.py",
    "scripts/current_state_guard.py",
    "scripts/resume_check.py",
    "scripts/check_entry_docs.py",
    "scripts/check_canonical_state_change.py",
    ".github/workflows/current-state-guard.yml",
    ".github/workflows/current-state-views.yml",
    "scripts/check_direct_chat_immutability.py",
    "tests/test_check_direct_chat_immutability.py",
    "BUD.md",
    "docs/引き継ぎ/現在の引き継ぎ.md",
    "docs/現在状態.json",
)

REQUIRED_SAFETY_STATEMENTS = (
    "既存の直チャット原本は変更・削除・改名・上書き・置換しない",
    "既存ボード",
    "上書き",
    "切替完了とは宣言しない",
    "PR #1102",
    "PR #1116",
    "PR #1118",
    "コールドスタート",
)

REQUIRED_NO_REWORK_STATEMENTS = (
    "項目002",
    "再開・再検証・再実行しない",
    "002は完了・再作業禁止",
    "項目003以降",
)


def validate_map(text: str) -> list[str]:
    errors: list[str] = []
    for path in REQUIRED_PATHS:
        if f"`{path}`" not in text:
            errors.append(f"dependency map missing required path: {path}")
    for statement in REQUIRED_SAFETY_STATEMENTS:
        if statement not in text:
            errors.append(f"dependency map missing safety/evidence statement: {statement}")
    if "優先度1〜5" not in text or "既定値3" not in text:
        errors.append("dependency map must reflect the board's priority range 1-5 and default 3")
    return errors


def validate_no_002_rework(text: str) -> list[str]:
    errors: list[str] = []
    for statement in REQUIRED_NO_REWORK_STATEMENTS:
        if statement not in text:
            errors.append(f"002 no-rework guard missing required rule: {statement}")
    return errors


def validate_design_status(text: str) -> list[str]:
    """Keep the design aligned with the completed board check and merged dependency-map PR."""
    errors: list[str] = []
    required = (
        "PR #1119は2026-10-16にマージ済み",
        "項目002は完了扱い",
        "再実施しない",
        "`/ChatGPT/Dropbox作業管理統合ボード.xlsx`",
    )
    for statement in required:
        if statement not in text:
            errors.append(f"migration design missing current-state/no-rework statement: {statement}")
    return errors


def main() -> int:
    try:
        text = MAP_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"FAIL: cannot read dependency map: {exc}", file=sys.stderr)
        return 1
    errors = validate_map(text)
    try:
        design_text = DESIGN_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"cannot read Dropbox migration design: {exc}")
    else:
        errors.extend(validate_design_status(design_text))
    try:
        guard_text = NO_REWORK_GUARD_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"cannot read 002 no-rework guard: {exc}")
    else:
        errors.extend(validate_no_002_rework(guard_text))
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("OK: dependency map and 002 no-rework guard cover required safety boundaries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
