#!/usr/bin/env python3
"""Validate the canonical state before resuming work."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "docs" / "現在状態.json"
REQUIRED = ("execution_environment", "current_position", "next_step")

def fail(message):
    print(f"STOP: {message}")
    return 1

def main():
    try:
        with STATE.open(encoding="utf-8") as f:
            state = json.load(f)
    except Exception as exc:
        return fail(f"canonical state unreadable: {exc}")

    missing = [k for k in REQUIRED if k not in state]
    if missing:
        return fail("missing required fields: " + ", ".join(missing))

    env = state["execution_environment"]
    active = env.get("active")
    retired = env.get("retired", [])
    current = state["current_position"]
    nxt = state["next_step"]

    if not active:
        return fail("active execution environment is not defined")
    if not isinstance(retired, list):
        return fail("retired execution environments must be a list")
    if active in retired:
        return fail(f"active environment is also retired: {active}")
    if nxt.get("environment") != active:
        return fail("next_step.environment does not match active environment")
    if not nxt.get("target") or not nxt.get("evidence"):
        return fail("next_step requires target and evidence")
    if not current.get("summary"):
        return fail("current_position.summary is missing")

    manifest = state.get("resume_manifest", {})
    if manifest.get("source") != "docs/現在状態.json":
        return fail("resume_manifest.source must point to canonical state")
    if not manifest.get("generator"):
        return fail("resume_manifest.generator is missing")

    if state.get("work_pc", {}).get("clone_status") == "cloned" and not state["work_pc"].get("clone_evidence"):
        return fail("work_pc clone_status=cloned requires clone_evidence")

    print("OK: resume state verified")
    print(f"active_environment: {active}")
    print(f"retired_environments: {', '.join(retired) if retired else '(none)'}")
    print(f"current_position: {current['summary']}")
    print(f"next_step: {nxt['target']}")
    print(f"next_step_environment: {nxt['environment']}")
    print(f"manifest_generator: {manifest['generator']}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
