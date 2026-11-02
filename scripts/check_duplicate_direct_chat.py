#!/usr/bin/env python3
"""Detect exact duplicate direct-chat originals without normalizing their content."""
from __future__ import annotations
import re
import sys
from pathlib import Path

LEGACY_GENERATED_TITLE = re.compile(
    r"^# 直チャット\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}(?:\.\d{6})?\+0900\n\n"
)

def read_exact(path: Path) -> str:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return stream.read()

def remove_legacy_generated_title(saved: str, source: str) -> str:
    """Remove only the exact legacy title inserted by the former save script."""
    if source.startswith("# 直チャット"):
        return saved
    return LEGACY_GENERATED_TITLE.sub("", saved, count=1)

def find_duplicate(source_text: str, directory: Path) -> Path | None:
    """Return a saved path only when the original body matches exactly."""
    if not directory.exists():
        return None
    for candidate in sorted(directory.glob("*.md")):
        try:
            saved = read_exact(candidate)
        except (OSError, UnicodeError):
            continue
        comparable = remove_legacy_generated_title(saved, source_text)
        if comparable == source_text:
            return candidate
    return None

def main() -> int:
    if len(sys.argv) != 3:
        print("usage: check_duplicate_direct_chat.py SOURCE_FILE DIRECT_CHAT_DIR", file=sys.stderr)
        return 2
    source_path = Path(sys.argv[1])
    directory = Path(sys.argv[2])
    duplicate = find_duplicate(read_exact(source_path), directory)
    if duplicate:
        print(duplicate.as_posix())
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
