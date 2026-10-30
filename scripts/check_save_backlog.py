#!/usr/bin/env python3
"""Block a new canonical save intake while another canonical save PR is open."""

from __future__ import annotations

import json
import sys
from typing import Any

SAVE_BRANCH_PREFIXES = ("save/direct-chat-", "save/currentize-")


def blocking_prs(prs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        pr for pr in prs
        if str(pr.get("state", "OPEN")).upper() == "OPEN"
        and str(pr.get("headRefName", "")).startswith(SAVE_BRANCH_PREFIXES)
    ]


def main() -> int:
    prs = json.load(sys.stdin)
    blocking = blocking_prs(prs)
    if blocking:
        details = ", ".join(
            f"#{pr.get('number')} ({pr.get('headRefName')})" for pr in blocking
        )
        print(f"Open canonical save PRs block new intake: {details}", file=sys.stderr)
        print(
            "Keep the queue request pending. Retry it with workflow_dispatch "
            "queue_pr_number after existing canonical save PRs are merged or resolved.",
            file=sys.stderr,
        )
        return 1
    print("No open canonical save PR; intake may proceed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
