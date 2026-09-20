#!/usr/bin/env python3
"""Generate a freshness manifest from the canonical current-state JSON."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "docs" / "現在状態.json"

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = STATE.read_bytes()
    state = json.loads(raw.decode("utf-8"))
    manifest = {
        "manifest_version": 1,
        "source": "docs/現在状態.json",
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "source_updated": state["updated"],
        "execution_environment": state["execution_environment"],
        "current_position": state["current_position"],
        "next_step": state["next_step"],
        "required_first_check": "scripts/resume_check.py",
        "stop_if": [
            "canonical state unreadable",
            "required current-state fields missing",
            "active/retired environment conflict",
            "next_step.environment differs from active environment",
            "generated views are not regenerated from the canonical state",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: wrote {args.output}")
    print(f"source_sha256: {manifest['source_sha256']}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
