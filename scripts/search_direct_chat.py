#!/usr/bin/env python3
"""Search direct-chat records from the local clone, with API fallback."""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

REPO = "takalenny-blip/ai-project"
DIRECT_CHAT_PATH = "直チャット"
API_ROOT = "https://api.github.com"
ROOT = Path(__file__).resolve().parents[1]


def local_files() -> list[Path]:
    base = ROOT / DIRECT_CHAT_PATH
    if not base.is_dir():
        return []
    return sorted(p for p in base.rglob("*.md") if p.is_file())


def api_get(url: str):
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "ai-project-direct-chat-search",
        },
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.load(response)


def search_local(files: list[Path], query: str, case_sensitive: bool, context: int) -> int:
    needle = query if case_sensitive else query.casefold()
    hits = 0
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        for i, line in enumerate(lines):
            haystack = line if case_sensitive else line.casefold()
            if needle in haystack:
                hits += 1
                start = max(0, i - context)
                end = min(len(lines), i + context + 1)
                print(f"{path.relative_to(ROOT)}:{i + 1}")
                for n in range(start, end):
                    print(f"  {n + 1}: {lines[n]}")
                print()
    return hits


def search_api(query: str, case_sensitive: bool, context: int) -> tuple[int, int]:
    encoded_path = urllib.parse.quote(DIRECT_CHAT_PATH, safe="")
    url = f"{API_ROOT}/repos/{REPO}/contents/{encoded_path}?ref=main"
    entries = api_get(url)
    files = [e for e in entries if e.get("type") == "file"]

    needle = query if case_sensitive else query.casefold()
    hits = 0
    for entry in files:
        data = api_get(entry["url"])
        content = data.get("content", "")
        if data.get("encoding") == "base64":
            text = base64.b64decode(content).decode("utf-8", errors="replace")
        else:
            text = content
        lines = text.splitlines()
        for i, line in enumerate(lines):
            haystack = line if case_sensitive else line.casefold()
            if needle in haystack:
                hits += 1
                start = max(0, i - context)
                end = min(len(lines), i + context + 1)
                print(f"{entry['path']}:{i + 1}")
                for n in range(start, end):
                    print(f"  {n + 1}: {lines[n]}")
                print()
    return len(files), hits


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--case-sensitive", action="store_true")
    parser.add_argument("--context", type=int, default=1)
    parser.add_argument("--api-fallback", action="store_true")
    args = parser.parse_args()

    files = local_files()
    if files:
        hits = search_local(files, args.query, args.case_sensitive, args.context)
        print(f"source=local_clone files_scanned={len(files)} hits={hits}", file=sys.stderr)
        return 0

    if not args.api_fallback:
        print("No local direct-chat clone found; rerun with --api-fallback to use GitHub API.", file=sys.stderr)
        return 2

    scanned, hits = search_api(args.query, args.case_sensitive, args.context)
    print(f"source=github_api files_scanned={scanned} hits={hits}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
