#!/usr/bin/env python3
"""Resolve the state of the canonical direct-chat save lifecycle."""
from __future__ import annotations
import argparse, json
from dataclasses import dataclass

@dataclass(frozen=True)
class SaveLifecycle:
    status: str
    reason: str
    queue_pr: str | None
    final_pr: str | None

def resolve(data: dict) -> SaveLifecycle:
    queue = data.get("queue_pr") or {}
    final = data.get("final_save_pr") or {}
    readback = data.get("canonical_readback") or {}
    q = str(queue["number"]) if queue.get("number") is not None else None
    f = str(final["number"]) if final.get("number") is not None else None
    if not q: return SaveLifecycle("not_submitted", "queue PR is not present", None, f)
    if queue.get("state") == "open": return SaveLifecycle("submitted_pending", "queue PR is still open", q, f)
    if queue.get("state") == "closed" and not f: return SaveLifecycle("failed_or_incomplete", "queue PR closed but no canonical save PR is recorded", q, None)
    if final.get("state") == "open": return SaveLifecycle("final_save_pending", "canonical save PR is open", q, f)
    if final.get("state") == "closed" and not final.get("merged"): return SaveLifecycle("failed_or_incomplete", "canonical save PR closed without merge", q, f)
    if final.get("merged") is not True: return SaveLifecycle("final_save_pending", "canonical save PR merge is not yet confirmed", q, f)
    if readback.get("verified") is not True: return SaveLifecycle("merged_readback_pending", "canonical save PR merged but canonical readback is not verified", q, f)
    return SaveLifecycle("completed", "canonical save PR merged and canonical readback verified", q, f)

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("path", nargs="?"); args = parser.parse_args()
    import sys
    raw = open(args.path, encoding="utf-8").read() if args.path else sys.stdin.read()
    result = resolve(json.loads(raw)); print(json.dumps(result.__dict__, ensure_ascii=False, indent=2)); return 0

if __name__ == "__main__": raise SystemExit(main())