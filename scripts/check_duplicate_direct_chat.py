#!/usr/bin/env python3
"""Detect an already-saved direct-chat body without changing the source."""

from __future__ import annotations

import re
import sys
from pathlib import Path

PATCH_BEGIN = "<!-- BUD_STATE_PATCH_BEGIN"
PATCH_END = "BUD_STATE_PATCH_END -->"


def strip_retired_patch(content: str) -> str:
    pattern = re.compile(
        re.escape(PATCH_BEGIN) + r"\s*\n.*?\n" + re.escape(PATCH_END),
        re.DOTALL,
    )
    content = pattern.sub("", content, count=1)
    if not content.endswith("\n"):
        content += "\n"
    return content


def find_duplicate(source_text: str, directory: Path) -> Path | None:
    """Return the exact canonical path if the source body is already saved."""
    cleaned_source = strip_retired_patch(source_text)
    source_has_own_title = cleaned_source.startswith("# 直チャット")
    expected = cleaned_source if source_has_own_title else cleaned_source.lstrip()

    if not directory.exists():
        return None

    for candidate in sorted(directory.glob("*.md")):
        try:
            saved = strip_retired_patch(candidate.read_text(encoding="utf-8"))
        except (OSError, UnicodeError):
            continue

        if not source_has_own_title and saved.startswith("# 直チャット") and "\n\n" in saved:
            # save_and_currentize.py prepends this title only when the incoming
            # source does not already start with "# 直チャット".
            saved_body = saved.split("\n\n", 1)[1]
        else:
            saved_body = saved

        if saved_body == expected:
            return candidate
    return None


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: check_duplicate_direct_chat.py SOURCE_FILE DIRECT_CHAT_DIR", file=sys.stderr)
        return 2
    source_path = Path(sys.argv[1])
    directory = Path(sys.argv[2])
    duplicate = find_duplicate(source_path.read_text(encoding="utf-8"), directory)
    if duplicate:
        print(duplicate.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
