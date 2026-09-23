#!/usr/bin/env python3
"""Build a deterministic Blogger API draft payload from an article candidate."""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

from scripts import interaction_preflight

REQUIRED_FIELDS = ("title", "intro", "body", "insights", "uncertain_or_notes")


def _paragraphs(value: str) -> str:
    parts = [part.strip() for part in value.split("\n") if part.strip()]
    return "".join(f"<p>{html.escape(part)}</p>" for part in parts)


def build_blogger_payload(candidate: dict) -> dict:
    missing = [field for field in REQUIRED_FIELDS if not isinstance(candidate.get(field), str)]
    if missing:
        raise ValueError("missing candidate fields: " + ", ".join(missing))
    content = (
        f"<p>{html.escape(candidate['intro'])}</p>"
        f"<h2>本文</h2>{_paragraphs(candidate['body'])}"
        f"<h2>得られた知見</h2>{_paragraphs(candidate['insights'])}"
        f"<h2>未確定・注意</h2>{_paragraphs(candidate['uncertain_or_notes'])}"
    )
    return {"title": candidate["title"], "content": content}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--output", default="-")
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--text", required=True)
    parser.add_argument("--evidence-json", type=Path, required=True)
    parser.add_argument("--history", type=Path, required=True)
    parser.add_argument("--loop-threshold", type=int, default=2)
    parser.add_argument("--work-state", type=Path)
    args = parser.parse_args()
    try:
        interaction_preflight.run_preflight(
            state_path=args.state,
            text=args.text,
            evidence_path=args.evidence_json,
            history_path=args.history,
            loop_threshold=args.loop_threshold,
            work_state_path=args.work_state,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise SystemExit(f"STOP: interaction preflight failed: {exc}")
    candidate = json.loads(Path(args.candidate).read_text(encoding="utf-8"))
    payload = json.dumps(build_blogger_payload(candidate), ensure_ascii=False, indent=2) + "\n"
    if args.output == "-":
        print(payload, end="")
    else:
        Path(args.output).write_text(payload, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
