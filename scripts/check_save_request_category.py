#!/usr/bin/env python3
"""Validate a save-request envelope and extract only its original body.

New requests use the structured template. Previously submitted raw-chat queue
payloads remain accepted as a compatibility path; they are never wrapped in the
saved record.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ALLOWED_KINDS = {"会話記録", "保存機構メタ報告"}
REQUEST_TITLE = "# 直チャット保存要求"


def section(content: str, heading: str) -> str | None:
    heading_pattern = re.compile(rf"^##[ \t]+{re.escape(heading)}[ \t]*$")
    boundary_pattern = re.compile(r"^#{1,2}[ \t]+")
    lines = content.splitlines()
    start = None
    for index, line in enumerate(lines):
        if heading_pattern.fullmatch(line):
            start = index + 1
            break
    if start is None:
        return None
    end = len(lines)
    for index in range(start, len(lines)):
        if boundary_pattern.match(lines[index]):
            end = index
            break
    return "\n".join(lines[start:end]).strip()


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


def extract_body(content: str) -> tuple[str | None, str]:
    """Extract the exact body after the single ## 本文 delimiter.

    Only the one blank line that separates the heading from the body is removed.
    The body itself, including its headings, spacing and final newline, is kept.
    """
    lines = content.splitlines(keepends=True)
    matches = [
        index for index, line in enumerate(lines)
        if re.fullmatch(r"##[ \t]+本文[ \t]*(?:\r?\n)?", line)
    ]
    if len(matches) != 1:
        return None, "request must contain exactly one ## 本文 section"

    body_start = sum(len(line) for line in lines[: matches[0] + 1])
    if content.startswith("\r\n", body_start):
        body_start += 2
    elif content.startswith("\n", body_start):
        body_start += 1

    body = content[body_start:]
    if not body.strip():
        return None, "## 本文 must contain the original content"
    return body, "ok"


def prepare_request(content: str) -> tuple[bool, str, str | None]:
    """Return only the conversation body; support legacy raw queue files."""
    if content.startswith(REQUEST_TITLE + "\n") or content.startswith(REQUEST_TITLE + "\r\n"):
        ok, message = validate(content)
        if not ok:
            return False, message, None
        body, message = extract_body(content)
        if body is None:
            return False, message, None
        return True, "structured request: " + message, body

    if not content.strip():
        return False, "raw conversation payload is empty", None

    # Legacy raw queue payloads are classified as conversation records by the
    # trusted intake script. This validation envelope is never written to disk.
    envelope = "## 保存対象種別\n会話記録\n\n" + content
    ok, message = validate(envelope)
    if not ok:
        return False, message, None
    return True, "legacy raw conversation payload: " + message, content


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument(
        "--prepare-chat-to",
        type=Path,
        help="write only the original conversation body to this path",
    )
    args = parser.parse_args()

    with args.path.open("r", encoding="utf-8", newline="") as source:
        content = source.read()

    if args.prepare_chat_to:
        ok, message, body = prepare_request(content)
        if ok and body is not None:
            with args.prepare_chat_to.open("w", encoding="utf-8", newline="") as output:
                output.write(body)
    else:
        ok, message = validate(content)
    print(message)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
