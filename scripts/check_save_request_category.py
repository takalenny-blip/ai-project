#!/usr/bin/env python3
"""Validate the declared kind of a direct-chat save request."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ALLOWED_KINDS = {"会話記録", "保存機構メタ報告"}


def section(content: str, heading: str) -> str | None:
    pattern = re.compile(
        rf"(?ms)^##[ \t]+{re.escape(heading)}[ \t]*\n(.*?)(?=^#{1,2}[ \t]+|\Z)"
    )
    match = pattern.search(content)
    return match.group(1).strip() if match else None


def validate(content: str) -> tuple[bool, str]:
    kind = section(content, "保存対象種別")
    if not kind:
        return False, "保存対象種別 is required"
    if kind not in ALLOWED_KINDS:
        return False, f"unknown 保存対象種別: {kind}"
    if kind == "保存機構メタ報告":
        decision = section(content, "新しい決定事項")
        if not decision:
            return False, "保存機構メタ報告 requires 新しい決定事項"
    return True, "ok"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    ok, message = validate(args.path.read_text(encoding="utf-8"))
    print(message)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
