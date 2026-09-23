"""Validate blog proposals and run mandatory interaction preflight before Blogger publication decisions."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from scripts import interaction_preflight

def check(proposal: dict) -> dict:
    review = proposal.get("review", {})
    decision = review.get("decision")
    return {
        "payload_ready": decision == "approved",
        "blocked_reason": None if decision == "approved" else "blog proposal review is not approved",
        "review_decision": decision,
    }

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--proposal",required=True)
    p.add_argument("--state",required=True)
    p.add_argument("--text",required=True)
    p.add_argument("--evidence-json",required=True)
    p.add_argument("--history",required=True)
    p.add_argument("--loop-threshold",type=int,default=2)
    p.add_argument("--work-state")
    a=p.parse_args()

    try:
        result = interaction_preflight.run_preflight(
            state_path=Path(a.state),
            text=a.text,
            evidence_path=Path(a.evidence_json),
            history_path=Path(a.history),
            loop_threshold=a.loop_threshold,
            work_state_path=Path(a.work_state) if a.work_state else None,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise SystemExit(f"STOP: interaction preflight failed: {exc}")

    print(json.dumps(check(json.loads(Path(a.proposal).read_text(encoding="utf-8"))),ensure_ascii=False,indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
