#!/usr/bin/env python3
"""Search primary direct-chat records through the GitHub Contents API.

Usage:
  python3 scripts/search_direct_chat.py chromium
  python3 scripts/search_direct_chat.py --case-sensitive launch-light.sh

The repository remains the source of truth. No index is created and no
credentials/cookies/session data are stored. If GITHUB_TOKEN is set it is
used only for API requests; otherwise the script uses public API access.
"""

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

REPO = "takalenny-blip/ai-project"
DIRECT_CHAT_PATH = "直チャット"
API_ROOT = "https://api.github.com"


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--case-sensitive", action="store_true")
    parser.add_argument("--context", type=int, default=1)
    args = parser.parse_args()

    encoded_path = urllib.parse.quote(DIRECT_CHAT_PATH, safe="")
    url = f"{API_ROOT}/repos/{REPO}/contents/{encoded_path}?ref=main"
    entries = api_get(url)
    files = [e for e in entries if e.get("type") == "file"]

    needle = args.query if args.case_sensitive else args.query.casefold()
    hits = 0

    for entry in files:
        data = api_get(entry["url"])
        content = data.get("content", "")
        if data.get("encoding") == "base64":
            import base64
            text = base64.b64decode(content).decode("utf-8", errors="replace")
        else:
            text = content
        lines = text.splitlines()
        for i, line in enumerate(lines):
            haystack = line if args.case_sensitive else line.casefold()
            if needle in haystack:
                hits += 1
                start = max(0, i - args.context)
                end = min(len(lines), i + args.context + 1)
                print(f"{entry['path']}:{i + 1}")
                for n in range(start, end):
                    print(f"  {n + 1}: {lines[n]}")
                print()

    print(f"files_scanned={len(files)} hits={hits}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
