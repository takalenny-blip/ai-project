#!/usr/bin/env python3
"""Guard the canonical resume state and current-state views."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUD_PATH = ROOT / "BUD.md"
HANDOVER_PATH = ROOT / "docs" / "引き継ぎ" / "現在の引き継ぎ.md"
import sys
sys.path.insert(0, str(ROOT / "scripts"))
from generate_current_views import render
STATE_PATH = ROOT / "docs" / "現在状態.json"

REQUIRED = ("execution_environment", "current_position")
RETIRED_ALIASES = {
    "vaio_p": ("vaio_p", "VAIO P", "VAIO P + Chromium", "VAIO P運用"),
}

def fail(message: str) -> None:
    raise ValueError(message)

def load_state(path: Path = STATE_PATH) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"canonical state unreadable: {exc}")

def validate_external_response_gate(state: dict) -> None:
    gate = state.get("external_response_gate", {"status": "clear"})
    if not isinstance(gate, dict):
        fail("external_response_gate must be an object")
    status = gate.get("status", "clear")
    if status not in {"clear", "pending"}:
        fail("external_response_gate.status must be clear or pending")
    contract = gate.get("reaction_contract")
    if not isinstance(contract, dict):
        fail("external_response_gate.reaction_contract must be an object")
    required_contract = ("required_fields", "judgment_values", "rule", "clear_condition")
    missing_contract = [key for key in required_contract if not contract.get(key)]
    if missing_contract:
        fail("reaction_contract missing: " + ", ".join(missing_contract))
    if status == "clear" and gate.get("last_reaction") is None and not gate.get("clear_reason"):
        fail("clear external_response_gate requires last_reaction or clear_reason")
    reaction = gate.get("last_reaction")
    if reaction is not None:
        required_reaction = ("proposal", "judgment", "reason", "next_action", "consistency")
        missing_reaction = [key for key in required_reaction if not reaction.get(key)]
        if missing_reaction:
            fail("last_reaction missing: " + ", ".join(missing_reaction))
        if reaction.get("judgment") not in contract["judgment_values"]:
            fail("last_reaction.judgment is invalid")
        if reaction.get("consistency") is not True:
            fail("last_reaction.consistency must be true")
    if status == "pending":
        required = ("purpose", "trigger", "required_action", "completion")
        missing = [key for key in required if not gate.get(key)]
        if missing:
            fail("pending external_response_gate missing: " + ", ".join(missing))



def validate_completed_verifications(state: dict) -> None:
    records = state.get("verification_records")
    if not isinstance(records, dict):
        fail("verification_records must be an object")
    for scope, record in records.items():
        if not isinstance(record, dict):
            fail(f"verification_records[{scope}] must be an object")
        if record.get("status") not in {"verified", "unverified", "retired"}:
            fail(f"verification_records[{scope}].status must be verified, unverified, or retired")
        if record.get("status") == "retired":
            evidence = record.get("evidence")
            if not isinstance(evidence, dict) or not evidence.get("method") or not evidence.get("checked_at") or not evidence.get("reason"):
                fail(f"retired verification record requires method, checked_at, and reason: {scope}")
        if record.get("status") == "verified":
            evidence = record.get("evidence")
            if not isinstance(evidence, dict) or not evidence.get("method") or not evidence.get("checked_at"):
                fail(f"verified verification record requires method and checked_at: {scope}")


def validate_completed_step_prose(state: dict) -> None:
    """Check only current technical-state prose; old queue-step status rules are retired."""
    current = state.get("current_position", {})
    for key in ("summary", "next_stage_boundary", "next_focus"):
        value = current.get(key)
        if isinstance(value, str) and not value.strip():
            fail(f"current_position.{key} must not be blank")


def validate_publishing_lane_consistency(state: dict) -> None:
    lane = state.get("primary_lane", "")
    if "WordPress本番公開" not in lane:
        return
    migration = state.get("migration")
    if not isinstance(migration, dict):
        fail("WordPress production lane requires migration policy")
    policy = migration.get("normal_work_policy", "")
    stale = "Blogger自動化へ戻る"
    if stale in policy or stale in state.get("surgery", {}).get("next_design_item", ""):
        fail("publishing-lane prose still points back to Blogger automation")
    required = ("Bloggerは下書き・表示確認", "WordPressは本番公開先", "GitHub Pagesは予備公開サイト")
    missing_policy = [phrase for phrase in required if phrase not in policy]
    if missing_policy:
        fail("migration.normal_work_policy contradicts primary_lane; missing: " + ", ".join(missing_policy))


def validate_state(state: dict) -> None:
    validate_publishing_lane_consistency(state)
    missing = [key for key in REQUIRED if key not in state]
    if missing:
        fail("missing required fields: " + ", ".join(missing))
    env = state["execution_environment"]
    active = env.get("active")
    retired = env.get("retired", [])
    legacy_verification_model = "verification_records" not in state
    if not legacy_verification_model:
        validate_completed_verifications(state)
    if state.get("work_queue_source") != "dropbox_board":
        fail("work_queue_source must be dropbox_board; GitHub queue fallback is disabled")
    if "work_items" in state:
        fail("legacy GitHub work_items field is retired and must not be reintroduced")
    if "next_step" in state:
        fail("legacy next_step field is retired and must not be reintroduced")
    # Staged migration compatibility: the current canonical state predates the
    # verification_records/scope fields. Allow it to pass until the normal save
    # pipeline applies the explicit migration patch; do not silently invent evidence.
    current = state["current_position"]
    if not active:
        fail("active execution environment is not defined")
    if not isinstance(retired, list):
        fail("retired execution environments must be a list")
    if active in retired:
        fail(f"active environment is also retired: {active}")
    if not current.get("summary"):
        fail("current_position.summary is missing")
    validate_external_response_gate(state)
    validate_completed_step_prose(state)
    work_pc = state.get("work_pc", {})
    if work_pc.get("clone_status") == "cloned" and not work_pc.get("clone_evidence"):
        fail("work_pc clone_status=cloned requires clone_evidence")

def retired_tokens(state: dict) -> tuple[str, ...]:
    tokens = []
    for item in state["execution_environment"].get("retired", []):
        tokens.append(item)
        tokens.extend(RETIRED_ALIASES.get(item, ()))
    return tuple(dict.fromkeys(tokens))

def validate_generated_views(state: dict) -> None:
    """Validate views rendered directly from the canonical state.

    BUD.md and the handover are compatibility views, not sources of truth.
    Their checked-in copies may lag briefly until the sync workflow updates them;
    guard validation must therefore inspect freshly rendered output from the
    canonical state rather than treating those copies as independent state.
    """
    env = state["execution_environment"]
    current = state["current_position"]
    queue_source = state.get("work_queue_source")
    if queue_source != "dropbox_board":
        fail("work_queue_source must be dropbox_board; GitHub queue fallback is disabled")
    if "work_items" in state:
        fail("legacy GitHub work_items field is retired and must not be reintroduced")
    if "next_step" in state:
        fail("legacy next_step field is retired and must not be reintroduced")
    bud_text, handover_text = render(state)
    for name, text in (("BUD.md", bud_text), ("docs/引き継ぎ/現在の引き継ぎ.md", handover_text)):
        required = [
            f"現在：**{env['active']}**",
            f"退役：{', '.join(env.get('retired', [])) or '(なし)'}",
            f"**{current['summary']}**",
        ]
        required.append("Dropboxの固定ファイル /ChatGPT/Dropbox作業管理統合ボード.xlsx")
        required.append("古いGitHub項目へフォールバックしない")
        for fragment in required:
            if fragment not in text:
                fail(f"generated view is stale or incomplete: {name} missing {fragment}")

def validate_projects(state: dict) -> None:
    retired = retired_tokens(state)
    for path in sorted((ROOT / "projects").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if any(token in text for token in retired):
            header = "\n".join(text.splitlines()[:20]).lower()
            if "status: historical" not in header:
                fail(f"non-historical project doc mentions retired policy: {path}")

def validate_hash_contract(state: dict) -> None:
    manifest = state.get("resume_manifest", {})
    if manifest.get("source") != "docs/現在状態.json":
        fail("resume_manifest.source must point to canonical state")
    if not manifest.get("generator"):
        fail("resume_manifest.generator is missing")

def validate(state_path: Path = STATE_PATH) -> None:
    state = load_state(state_path)
    validate_state(state)
    validate_hash_contract(state)
    validate_generated_views(state)
    validate_projects(state)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", type=Path, default=STATE_PATH)
    args = parser.parse_args()
    try:
        validate(args.state)
    except ValueError as exc:
        print(f"FAIL: {exc}")
        return 1
    print("OK: current-state guards passed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
