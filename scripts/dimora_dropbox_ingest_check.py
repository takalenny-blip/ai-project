#!/usr/bin/env python3
"""Check a locally synced DiMORA export before normal processing.

This is an intake check only: it does not normalize or mutate the source.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REQUIRED_FIELDS = ("title", "startDate", "endDate", "bcsNm", "chNo", "mode")


def load_records(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("record")
    if not isinstance(data, list) or not all(isinstance(x, dict) for x in data):
        raise ValueError("input must be a JSON array or an object containing record[]")
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()

    raw = args.input.read_bytes()
    records = load_records(args.input)
    missing = sorted({field for record in records for field in REQUIRED_FIELDS if field not in record})
    result = {
        "path": str(args.input),
        "size_bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "record_count": len(records),
        "required_fields_missing": missing,
        "ready_for_normal_processing": not missing,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not missing else 2


if __name__ == "__main__":
    raise SystemExit(main())
