#!/usr/bin/env python3
"""Validate the canonical state before resuming work."""
from __future__ import annotations
import json
import hashlib
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / "scripts"))
from work_queue import validate_work_items, select_actionable
STATE = ROOT / "docs" / "現在状態.json"
REQUIRED = ("execution_environment", "current_position", "work_items")

def repo_blob_sha(path):
    data = path.read_bytes()
    header = ("blob " + str(len(data)) + "\0").encode()
    return hashlib.sha1(header + data).hexdigest()

def external_artifact_path(prerequisite):
    configured = os.environ.get("DIMORA_ARTIFACT_PATH")
    return Path(configured) if configured else ROOT / prerequisite["name"]

def external_record_count(data):
    if isinstance(data, list):
        records = data
    elif isinstance(data, dict) and isinstance(data.get("record"), list):
        records = data["record"]
    else:
        raise ValueError("external_artifact JSON must be an array or object with record array")
    if not all(isinstance(item, dict) for item in records):
        raise ValueError("external_artifact records must be objects")
    return len(records)

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

    external_gate = state.get("external_response_gate", {"status": "clear"})
    if not isinstance(external_gate, dict):
        return fail("external_response_gate must be an object")
    gate_status = external_gate.get("status", "clear")
    if gate_status not in {"clear", "pending"}:
        return fail("external_response_gate.status must be clear or pending")
    contract = external_gate.get("reaction_contract")
    if not isinstance(contract, dict):
        return fail("external_response_gate.reaction_contract must be an object")
    required_contract = ("required_fields", "judgment_values", "rule", "clear_condition")
    missing_contract = [k for k in required_contract if not contract.get(k)]
    if missing_contract:
        return fail("reaction_contract missing: " + ", ".join(missing_contract))
    if gate_status == "clear" and external_gate.get("last_reaction") is None and not external_gate.get("clear_reason"):
        return fail("clear external_response_gate requires last_reaction or clear_reason")
    reaction = external_gate.get("last_reaction")
    if reaction is not None:
        required_reaction = ("proposal", "judgment", "reason", "next_action", "consistency")
        missing_reaction = [k for k in required_reaction if not reaction.get(k)]
        if missing_reaction:
            return fail("last_reaction missing: " + ", ".join(missing_reaction))
        if reaction.get("judgment") not in contract["judgment_values"]:
            return fail("last_reaction.judgment is invalid")
        if reaction.get("consistency") is not True:
            return fail("last_reaction.consistency must be true")
    if gate_status == "pending":
        required_gate_fields = ("purpose", "trigger", "required_action", "completion")
        missing_gate_fields = [k for k in required_gate_fields if not external_gate.get(k)]
        if missing_gate_fields:
            return fail("pending external_response_gate missing: " + ", ".join(missing_gate_fields))
        print("STOP: external proposal response is pending; react before any other work")
        return 3

    try:
        validate_work_items(state["work_items"])
    except ValueError as exc:
        return fail("work queue invalid: " + str(exc))
    actionable = select_actionable(state["work_items"], state.get("updated"))
    if actionable:
        print("actionable_work_items: " + ", ".join(f"{item['id']} (priority={item['priority']})" for item in actionable))
        for item in actionable:
            progress = item["progress"]
            current = next(step for step in progress["steps"] if step["id"] == progress["current_step"])
            print(f"progress[{item['id']}]: current_step={progress['current_step']} status={current['status']}")
    else:
        print("actionable_work_items: (none)")
    waiting_external = [
        item for item in state["work_items"]
        if item["status"] not in {"done", "held"} and item["execution_state"] == "waiting_external"
    ]
    if waiting_external:
        print("waiting_external_work_items: " + ", ".join(
            f"{item['id']} ({item.get('wait_reason', 'reason unspecified')})"
            for item in waiting_external
        ))
        for item in waiting_external:
            progress = item["progress"]
            current = next(step for step in progress["steps"] if step["id"] == progress["current_step"])
            print(f"progress[{item['id']}]: current_step={progress['current_step']} status={current['status']}")
    else:
        print("waiting_external_work_items: (none)")
    actionable = select_actionable(state["work_items"], state.get("updated"))
    blocked_items = sorted((x for x in state["work_items"] if x["status"] not in {"done", "held"} and x["readiness"] == "blocked"), key=lambda x: (x["priority"], x["created_at"], x["id"]))
    selected = actionable[0] if actionable else (blocked_items[0] if blocked_items else None)
    if selected is None:
        if waiting_external:
            print("BLOCKED: all remaining work is waiting for external results")
            return 2
        return fail("no actionable or explicitly blocked work item is recorded")
    env = state["execution_environment"]
    active = env.get("active")
    retired = env.get("retired", [])
    current = state["current_position"]
    nxt = selected

    if not active:
        return fail("active execution environment is not defined")
    if not isinstance(retired, list):
        return fail("retired execution environments must be a list")
    if active in retired:
        return fail(f"active environment is also retired: {active}")
    if nxt.get("environment") != active:
        return fail("selected work item environment does not match active environment")
    if not nxt.get("target") or not nxt.get("evidence"):
        return fail("selected work item requires target and evidence")
    if not isinstance(nxt.get("preflight_prerequisites", []), list):
        return fail("work item preflight_prerequisites must be a list")
    if nxt.get("readiness") not in {"ready", "blocked"}:
        return fail("selected work item readiness must be ready or blocked")
    interaction = state.get("interaction_control")
    if not isinstance(interaction, dict):
        return fail("interaction_control must be defined")
    if interaction.get("status") != "implemented_preflight":
        return fail("interaction_control.status must be implemented_preflight")
    guard_script = interaction.get("guard_script")
    if guard_script != "scripts/interaction_guard.py":
        return fail("interaction_control.guard_script is invalid")
    loop = interaction.get("loop_detection") or {}
    if loop.get("threshold") != 2 or loop.get("action") != "強制停止して人間判断へ戻す":
        return fail("interaction_control.loop_detection contract is invalid")
    blocked = interaction.get("blocked_output") or {}
    if blocked.get("exit_code") != 2:
        return fail("interaction_control.blocked_output.exit_code must be 2")
    for p in nxt.get("preflight_prerequisites", []):
        if p.get("status") == "verified" and p.get("kind") == "external_artifact":
            path = external_artifact_path(p)
            ev = p.get("evidence") or {}
            expected = ev.get("sha256")
            expected_count = ev.get("record_count")
            if not path.is_file() or not expected or expected_count is None:
                return fail("verified external_artifact requires runtime file, sha256, and record_count: " + p.get("name", "?"))
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual != expected:
                return fail("verified external_artifact SHA-256 mismatch: " + p.get("name", "?"))
            try:
                with path.open(encoding="utf-8") as f:
                    data = json.load(f)
                actual_count = external_record_count(data)
            except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
                return fail("verified external_artifact JSON invalid: " + str(exc))
            if actual_count != expected_count:
                return fail("verified external_artifact record_count mismatch: " + p.get("name", "?"))
        if p.get("status") == "verified" and p.get("kind") == "repo_file":
            path = ROOT / p["name"]
            ev = p.get("evidence") or {}
            expected = ev.get("sha256") or ev.get("blob_sha")
            if not path.is_file() or not expected:
                return fail("verified repo_file cannot be proven: " + p.get("name", "?"))
            actual = hashlib.sha256(path.read_bytes()).hexdigest() if ev.get("sha256") else repo_blob_sha(path)
            if actual != expected:
                return fail("verified repo_file evidence mismatch: " + p.get("name", "?"))
    bad = [p.get("name", "?") for p in nxt.get("preflight_prerequisites", []) if p.get("status") != "verified"]
    if nxt["readiness"] == "ready" and bad:
        return fail("selected work item is ready but preflight prerequisites are not verified: " + ", ".join(bad))
    if nxt["readiness"] == "blocked":
        if not nxt.get("blocked_reason") or not nxt.get("unblock_action"):
            return fail("blocked work item requires blocked_reason and unblock_action")
        print("BLOCKED: work item is blocked: " + nxt["blocked_reason"])
        print("UNBLOCK: " + nxt["unblock_action"])
        return 2
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
    print(f"selected_work_item: {nxt['id']} — {nxt['target']}")
    print(f"selected_work_environment: {nxt['environment']}")
    print(f"manifest_generator: {manifest['generator']}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
