#!/usr/bin/env python3
"""Require canonical state/view files to move together when canonical state changes."""

from __future__ import annotations

import argparse
from pathlib import Path


CANONICAL_STATE = "docs/現在状態.json"
GENERATED_VIEWS = {
    "BUD.md",
    "docs/引き継ぎ/現在の引き継ぎ.md",
}


def validate_changed_paths(paths: list[str]) -> tuple[bool, str]:
    changed = set(paths)
    if CANONICAL_STATE not in changed:
        return True, "canonical state unchanged"
    missing = sorted(GENERATED_VIEWS - changed)
    if missing:
        return False, (
            "docs/現在状態.json changed without generated views: "
            + ", ".join(missing)
        )
    return True, "canonical state and generated views changed together"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paths-file", type=Path, required=True)
    args = parser.parse_args()
    paths = [line.strip() for line in args.paths_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    ok, message = validate_changed_paths(paths)
    print(("OK: " if ok else "FAIL: ") + message)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
