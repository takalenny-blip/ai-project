#!/usr/bin/env python3
"""Normalize an exported DiMORA favorite-programs JSON file.

Input is the array written by the authenticated DiMORA page:
window.GL_FAVPGM_DATA.record
It also accepts an object containing a "record" array.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


FIELDS = (
    "eventId",
    "mindsProgramId",
    "title",
    "startDate",
    "endDate",
    "bcsNm",
    "chNo",
    "mode",
    "requestId",
    "recTimerState",
    "length",
    "status",
    "genre",
)


def load_records(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("record")
    if not isinstance(data, list):
        raise ValueError("input must be a JSON array or an object containing record[]")
    if not all(isinstance(record, dict) for record in data):
        raise ValueError("every record must be a JSON object")
    return data


def normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    return {field: record.get(field) for field in FIELDS}


def normalize(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [normalize_record(record) for record in records]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()

    result = normalize(load_records(args.input))
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
