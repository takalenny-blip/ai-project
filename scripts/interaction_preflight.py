"""Mandatory acceptance-layer entrypoint for interaction preflight."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
try:
    from scripts import interaction_guard as guard
    from scripts import blog_work_state
except ModuleNotFoundError:
    import interaction_guard as guard
    import blog_work_state

def run_preflight(*, state_path: Path, text: str, evidence_path: Path, history_path: Path, loop_threshold: int = 2, work_state_path: Path | None = None, instruction: str | None = None, active_track: str | None = None, selected_track: str | None = None) -> None:
    state = guard.load_json(state_path)
    if instruction is not None or active_track is not None or selected_track is not None:
        if instruction is None or active_track is None or selected_track is None:
            raise ValueError("instruction, active_track, and selected_track must be supplied together")
        guard.validate_instruction_routing(instruction, active_track, selected_track)
    if work_state_path:
        blog_work_state.load(work_state_path)
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    history = json.loads(history_path.read_text(encoding="utf-8"))
    if not isinstance(evidence, list):
        raise ValueError("evidence must be a JSON list")
    if not isinstance(history, list):
        raise ValueError("history must be a JSON list")
    guard.validate_blocked_output(state, text)
    guard.validate_evidence_claim(text, evidence)
    guard.validate_loop(history, loop_threshold)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--text", required=True)
    parser.add_argument("--evidence-json", type=Path, required=True)
    parser.add_argument("--history", type=Path, required=True)
    parser.add_argument("--loop-threshold", type=int, default=2)
    parser.add_argument("--work-state", type=Path)
    parser.add_argument("--instruction")
    parser.add_argument("--active-track")
    parser.add_argument("--selected-track")
    args = parser.parse_args()
    try:
        run_preflight(state_path=args.state,text=args.text,evidence_path=args.evidence_json,history_path=args.history,loop_threshold=args.loop_threshold,work_state_path=args.work_state,instruction=args.instruction,active_track=args.active_track,selected_track=args.selected_track)
        print("OK: mandatory interaction preflight passed")
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"STOP: {exc}")
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
