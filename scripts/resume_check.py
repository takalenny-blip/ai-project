#!/usr/bin/env python3
"""Preflight the single-source operating rules and Dropbox work board."""
from __future__ import annotations

import os
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from dropbox_board import validate_remote_board_from_env
from current_state_guard import validate_rules

RULES = ROOT / "rules" / "運用ルール.md"

def dropbox_board_path() -> Path:
    configured = os.environ.get("DROPBOX_WORK_QUEUE_PATH")
    return Path(configured) if configured else ROOT / "Dropbox作業管理統合ボード.xlsx"

def validate_dropbox_board(path: Path) -> None:
    if not path.is_file():
        raise ValueError(f"Dropbox work board is missing or unavailable: {path}")
    try:
        with zipfile.ZipFile(path) as workbook:
            bad_member = workbook.testzip()
            if bad_member is not None:
                raise ValueError(f"corrupt XLSX member: {bad_member}")
            required = {"[Content_Types].xml", "xl/workbook.xml"}
            missing = required.difference(workbook.namelist())
            if missing:
                raise ValueError("not a valid XLSX workbook; missing: " + ", ".join(sorted(missing)))
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        raise ValueError(f"Dropbox work board is unreadable: {exc}") from exc

def fail(message: str) -> int:
    print(f"STOP: {message}")
    return 1

def main() -> int:
    try:
        text = RULES.read_text(encoding="utf-8")
        validate_rules(text)
    except Exception as exc:
        return fail(f"operating rules unavailable or invalid: {exc}")

    section = re.search(
        r"#### 外部提案対応状態（現行）\s*\n(.*?)(?=\n#### |\n### |\Z)",
        text,
        re.DOTALL,
    )
    if not section:
        return fail("external proposal response status section is missing")
    status = re.search(r"状態：\s*(clear|pending)", section.group(1))
    if not status:
        return fail("external proposal response status must be clear or pending")
    if status.group(1) == "pending":
        print("STOP: external proposal response is pending; react before any other work")
        return 3

    try:
        if os.environ.get("DROPBOX_ACCESS_TOKEN"):
            remote_path = validate_remote_board_from_env()
            print(f"dropbox_remote_board: read and validated {remote_path}")
        elif os.environ.get("DROPBOX_REQUIRE_REMOTE") == "1":
            raise ValueError("DROPBOX_ACCESS_TOKEN is required for remote Dropbox board validation")
        else:
            validate_dropbox_board(dropbox_board_path())
            print("dropbox_local_board: validated local sync copy only; cloud freshness not verified")
    except ValueError as exc:
        return fail(str(exc))

    print("current_state_source: rules/運用ルール.md")
    print("daily_work_queue_source: Dropbox /ChatGPT/Dropbox作業管理統合ボード.xlsx")
    print("active_environment: work_pc")
    print("retired_environment: vaio_p")
    print("OK: resume preflight passed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
