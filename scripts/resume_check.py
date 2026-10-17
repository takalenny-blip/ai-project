#!/usr/bin/env python3
"""Validate the canonical state before resuming work."""
from __future__ import annotations
import json
import os
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / "scripts"))
from dropbox_board import validate_remote_board_from_env
STATE = ROOT / "docs" / "現在状態.json"
REQUIRED_BASE = ("execution_environment", "current_position")

def dropbox_board_path():
    configured = os.environ.get("DROPBOX_WORK_QUEUE_PATH")
    return Path(configured) if configured else ROOT / "Dropbox作業管理統合ボード.xlsx"

def validate_dropbox_board(path):
    """Fail closed unless the configured local Dropbox-sync file is a readable XLSX."""
    if not path.is_file():
        raise ValueError(f"Dropbox work board is missing or unavailable: {path}")
    try:
        with zipfile.ZipFile(path) as workbook:
            bad_member = workbook.testzip()
            if bad_member is not None:
                raise ValueError(f"corrupt XLSX member: {bad_member}")
            required_members = {"[Content_Types].xml", "xl/workbook.xml"}
            missing = required_members.difference(workbook.namelist())
            if missing:
                raise ValueError("not a valid XLSX workbook; missing: " + ", ".join(sorted(missing)))
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        raise ValueError(f"Dropbox work board is unreadable: {exc}") from exc

def fail(message):
    print(f"STOP: {message}")
    return 1

def main():
    try:
        with STATE.open(encoding="utf-8") as f:
            state = json.load(f)
    except Exception as exc:
        return fail(f"canonical state unreadable: {exc}")

    queue_source = state.get("work_queue_source")
    if queue_source != "dropbox_board":
        return fail("work_queue_source must be dropbox_board; GitHub queue fallback is disabled")
    if "work_items" in state:
        return fail("legacy GitHub work_items field is retired and must not be reintroduced")
    if "next_step" in state:
        return fail("legacy next_step field is retired and must not be reintroduced")
    required = REQUIRED_BASE
    missing = [k for k in required if k not in state]
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

    if queue_source == "dropbox_board":
        try:
            if os.environ.get("DROPBOX_ACCESS_TOKEN"):
                remote_path = validate_remote_board_from_env()
                print(f"dropbox_remote_board: read and validated {remote_path}")
            elif os.environ.get("DROPBOX_REQUIRE_REMOTE") == "1":
                raise ValueError("DROPBOX_ACCESS_TOKEN is required for remote Dropbox board validation")
            else:
                validate_dropbox_board(dropbox_board_path())
                print("dropbox_local_board: validated local sync copy only; cloud freshness not verified")
        except ValueError as exc:
            return fail(str(exc))

    print("daily_work_queue_source: Dropbox /ChatGPT/Dropbox作業管理統合ボード.xlsx")
    print("No fallback to legacy GitHub work_items or next_step is permitted.")
    env = state["execution_environment"]
    active = env.get("active")
    retired = env.get("retired", [])
    current = state["current_position"]

    if not active:
        return fail("active execution environment is not defined")
    if not isinstance(retired, list):
        return fail("retired execution environments must be a list")
    if active in retired:
        return fail(f"active environment is also retired: {active}")
    if not current.get("summary"):
        return fail("current_position.summary is missing")

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
    print("daily_next_action: read from Dropbox board; not derived from GitHub JSON")
    print(f"manifest_generator: {manifest['generator']}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
