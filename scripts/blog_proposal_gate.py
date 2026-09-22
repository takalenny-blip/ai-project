#!/usr/bin/env python3
"""Validate whether a blog proposal is eligible for Blogger payload generation."""
from __future__ import annotations
import argparse, json
from pathlib import Path

def check(proposal: dict) -> dict:
    review = proposal.get("review", {})
    decision = review.get("decision")
    return {
        "payload_ready": decision == "approved",
        "blocked_reason": None if decision == "approved" else "blog proposal review is not approved",
        "review_decision": decision,
    }

def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--proposal",required=True)
    a=p.parse_args()
    print(json.dumps(check(json.loads(Path(a.proposal).read_text(encoding="utf-8"))),ensure_ascii=False,indent=2))

if __name__ == "__main__":
    main()
