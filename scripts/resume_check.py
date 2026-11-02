#!/usr/bin/env python3
"""Fail-closed resume preflight for the single Dropbox work queue."""
from __future__ import annotations
import os
import zipfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from dropbox_board import validate_remote_board_from_env

ROOT = Path(__file__).resolve().parents[1]
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

def main() -> int:
    try:
        if not RULES.is_file() or not RULES.read_text(encoding="utf-8").strip():
            raise ValueError("rules/運用ルール.md is missing or unreadable")
        if os.environ.get("DROPBOX_ACCESS_TOKEN"):
            remote_path = validate_remote_board_from_env()
            print(f"dropbox_remote_board: read and validated {remote_path}")
        elif os.environ.get("DROPBOX_REQUIRE_REMOTE") == "1":
            raise ValueError("DROPBOX_ACCESS_TOKEN is required for remote Dropbox board validation")
        else:
            path = dropbox_board_path()
            validate_dropbox_board(path)
            print(f"dropbox_local_board: validated {path}; cloud freshness not verified")
        print("daily_work_queue_source: Dropbox /ChatGPT/Dropbox作業管理統合ボード.xlsx")
        print("No fallback to GitHub files or conversation history is permitted.")
        print("OK: resume preflight passed")
        return 0
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"STOP: {exc}")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
