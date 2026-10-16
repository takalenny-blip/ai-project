#!/usr/bin/env python3
"""Reject modifications, deletions, and renames of historical direct-chat originals.

New files under 直チャット/ are allowed. Existing files must remain byte-for-byte
unchanged and at the same path; corrections belong in separate supplemental files.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import PurePosixPath


def parse_name_status_z(raw: bytes) -> list[tuple[str, tuple[str, ...]]]:
    """Parse git diff --name-status -z output, including rename records."""
    tokens = raw.decode("utf-8", errors="surrogateescape").split("\0")
    if tokens and tokens[-1] == "":
        tokens.pop()
    records: list[tuple[str, tuple[str, ...]]] = []
    i = 0
    while i < len(tokens):
        status = tokens[i]
        i += 1
        if status.startswith(("R", "C")):
            if i + 1 >= len(tokens):
                raise ValueError("truncated rename/copy record from git diff")
            records.append((status, (tokens[i], tokens[i + 1])))
            i += 2
        else:
            if i >= len(tokens):
                raise ValueError("truncated file record from git diff")
            records.append((status, (tokens[i],)))
            i += 1
    return records


def is_direct_chat_path(path: str) -> bool:
    return PurePosixPath(path).parts[:1] == ("直チャット",)


def violations(records: list[tuple[str, tuple[str, ...]]]) -> list[str]:
    failures: list[str] = []
    for status, paths in records:
        affected = [path for path in paths if is_direct_chat_path(path)]
        if not affected:
            continue
        # Only a genuinely new file is permitted. M/D/T and any rename/copy
        # involving the protected directory must fail.
        if status != "A":
            failures.append(f"{status}: " + " -> ".join(affected))
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True, help="base commit SHA")
    parser.add_argument("--head", required=True, help="head commit SHA")
    args = parser.parse_args()
    if not args.base or not args.head or set(args.base) == {"0"}:
        print("FAIL: missing usable base/head SHA; cannot verify direct-chat originals", file=sys.stderr)
        return 2
    try:
        raw = subprocess.check_output(
            ["git", "diff", "--name-status", "-z", "--find-renames", args.base, args.head, "--", "直チャット/"],
            stderr=subprocess.PIPE,
        )
        failures = violations(parse_name_status_z(raw))
    except (subprocess.CalledProcessError, ValueError) as exc:
        print(f"FAIL: could not verify direct-chat immutability: {exc}", file=sys.stderr)
        return 2
    if failures:
        print("FAIL: existing direct-chat originals must not be modified, deleted, renamed, or replaced:")
        for failure in failures:
            print(f"  {failure}")
        print("Add corrections or interpretations in separate supplemental files; do not edit the original.")
        return 1
    print("OK: direct-chat originals are unchanged; new original files may be added.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
