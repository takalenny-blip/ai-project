#!/usr/bin/env python3
"""Backup and restore Blogger HTML generations.

The current HTML remains the canonical working file. Immutable snapshots live
under the version directory and use the blog number in every filename.

Examples:
  python scripts/blog_html_version.py backup
  python scripts/blog_html_version.py list
  python scripts/blog_html_version.py restore 2
"""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

BLOG_ID = "BLOG-0001"
CURRENT_HTML = Path("docs/企画/BLOG-0001_Blogger掲載用.html")
VERSION_DIR = Path("docs/企画/BLOG-0001_versions")
VERSION_RE = re.compile(r"^BLOG-0001_ver(\d{5})\.html$")


def version_path(version: int) -> Path:
    if version < 1:
        raise ValueError("version must be >= 1")
    return VERSION_DIR / f"{BLOG_ID}_ver{version:05d}.html"


def available_versions() -> list[int]:
    if not VERSION_DIR.exists():
        return []
    versions = []
    for path in VERSION_DIR.iterdir():
        match = VERSION_RE.fullmatch(path.name)
        if match and path.is_file():
            versions.append(int(match.group(1)))
    return sorted(versions)


def next_version() -> int:
    versions = available_versions()
    return (max(versions) + 1) if versions else 1


def backup() -> Path:
    if not CURRENT_HTML.is_file():
        raise FileNotFoundError(f"current HTML not found: {CURRENT_HTML}")
    VERSION_DIR.mkdir(parents=True, exist_ok=True)
    destination = version_path(next_version())
    # Copy bytes exactly: no newline/encoding normalization.
    shutil.copyfile(CURRENT_HTML, destination)
    return destination


def restore(version: int) -> Path:
    source = version_path(version)
    if not source.is_file():
        raise FileNotFoundError(f"version not found: {source}")
    if not CURRENT_HTML.is_file():
        raise FileNotFoundError(f"current HTML not found: {CURRENT_HTML}")
    # Copy bytes exactly from the immutable snapshot to the working HTML.
    shutil.copyfile(source, CURRENT_HTML)
    return source


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage BLOG-0001 HTML generations.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("backup", help="copy current HTML to the next version")
    sub.add_parser("list", help="list available versions")
    restore_parser = sub.add_parser("restore", help="restore a version to current HTML")
    restore_parser.add_argument("version", type=int)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "backup":
        print(backup())
    elif args.command == "list":
        for version in available_versions():
            print(version_path(version))
    elif args.command == "restore":
        print(f"restored {restore(args.version)} -> {CURRENT_HTML}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
