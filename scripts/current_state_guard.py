#!/usr/bin/env python3
"""Guard the canonical resume state and current-state views."""
from __future__ import annotations

import argparse
import json
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / "scripts"))
from work_queue import validate_work_items, derived_next_step, select_actionable
from generate_current_views import render
STATE_PATH = ROOT / "docs" / "現在状態.json"

REQUIRED = ("execution_environment", "current_position", "work_items", "next_step")
ABSTRACT_NEXT_STEP = (
    "本来工程へ復帰",
    "通常のDiMORA本来工程へ復帰",
    "PR3完了後のcanonical現在状態を確認し、次の実装単位を決める",
)
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

def _repo_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = ("blob " + str(len(data)) + "\0").encode()
    return hashlib.sha1(header + data).hexdigest()

def _validate_verified_evidence(prerequisite: dict) -> None:
    evidence = prerequisite.get("evidence")
    if not isinstance(evidence, dict) or not evidence.get("method") or not evidence.get("checked_at"):
        fail("verified prerequisite requires method and checked_at evidence")
    if prerequisite["kind"] == "repo_file":
        path = ROOT / prerequisite["name"]
        if not path.is_file():
            fail("verified repo_file does not exist: " + prerequisite["name"])
        expected = evidence.get("sha256") or evidence.get("blob_sha")
        if not expected:
            fail("verified repo_file requires sha256 or blob_sha evidence: " + prerequisite["name"])
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if evidence.get("sha256") else _repo_blob_sha(path)
        if actual != expected:
            fail("verified repo_file evidence mismatch: " + prerequisite["name"])

def validate_prerequisites(next_step: dict) -> None:
    prerequisites = next_step.get("prerequisites")
    if not isinstance(prerequisites, list):
        fail("next_step.prerequisites must be an explicit list")
    readiness = next_step.get("readiness")
    if readiness not in {"ready", "blocked"}:
        fail("next_step.readiness must be ready or blocked")
    if readiness == "blocked" and (not next_step.get("blocked_reason") or not next_step.get("unblock_action")):
        fail("blocked next_step requires blocked_reason and unblock_action")
    for index, prerequisite in enumerate(prerequisites):
        if not isinstance(prerequisite, dict):
            fail(f"next_step.prerequisites[{index}] must be an object")
        for field in ("name", "kind", "verify_scope", "status"):
            if not prerequisite.get(field):
                fail(f"next_step.prerequisites[{index}].{field} is missing")
        if prerequisite["status"] not in {"verified", "unverified", "missing", "invalid"}:
            fail(f"invalid prerequisite status: {prerequisite['status']}")
        if prerequisite["status"] == "verified":
            _validate_verified_evidence(prerequisite)
    if readiness == "ready" and any(p["status"] != "verified" for p in prerequisites):
        fail("next_step.readiness=ready requires every prerequisite to be verified")

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


def validate_work_queue(state: dict) -> None:
    items = state.get("work_items")
    if not isinstance(items, list) or not items:
        fail("work_items must be a non-empty list")
    try:
        validate_work_items(items)
    except ValueError as exc:
        fail(str(exc))
    derived = derived_next_step(items, state.get("updated"))
    cached = state.get("next_step")
    if derived is None:
        if cached not in (None, {}):
            fail("next_step must be empty when no actionable work exists")
        return
    if not isinstance(cached, dict):
        fail("next_step must be an object derived from work_items")
    if cached.get("id") != derived.get("id"):
        fail("next_step does not match the highest-priority actionable work item")
    for key in ("target", "evidence", "environment", "scope", "readiness", "unblock_action"):
        if cached.get(key) != derived.get(key):
            fail("next_step is not an exact derived view of work_items: " + key)
    if derived.get("readiness") == "blocked" and cached.get("blocked_reason") != derived.get("blocked_reason"):
        fail("next_step blocked_reason is not derived from work_items")

def validate_state(state: dict) -> None:
    missing = [key for key in REQUIRED if key not in state]
    if missing:
        fail("missing required fields: " + ", ".join(missing))
    env = state["execution_environment"]
    active = env.get("active")
    retired = env.get("retired", [])
    nxt = state["next_step"]
    legacy_verification_model = "verification_records" not in state
    if not legacy_verification_model:
        validate_completed_verifications(state)
        validate_work_queue(state)
        if not nxt.get("scope"):
            fail("next_step.scope is missing")
        completed = state["verification_records"].get(nxt["scope"])
        if isinstance(completed, dict) and completed.get("status") == "verified":
            fail("next_step repeats an already verified scope: " + nxt["scope"])
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
    if nxt.get("environment") != active:
        fail("next_step.environment does not match active environment")
    for field in ("target", "evidence"):
        if not nxt.get(field):
            fail(f"next_step.{field} is missing")
    if nxt.get("status") not in {None, nxt.get("readiness")}:
        fail("next_step.status must be absent or equal to readiness")
    if not current.get("summary"):
        fail("current_position.summary is missing")
    if any(phrase in nxt["target"] for phrase in ABSTRACT_NEXT_STEP):
        fail("next_step.target is too abstract or stale; require current concrete work")
    validate_prerequisites(nxt)
    validate_external_response_gate(state)
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
    actionable_items = select_actionable(state["work_items"], state.get("updated"))
    actionable = actionable_items[0] if actionable_items else None
    bud_text, handover_text = render(state)
    for name, text in (("BUD.md", bud_text), ("docs/引き継ぎ/現在の引き継ぎ.md", handover_text)):
        required = [
            f"現在：**{env['active']}**",
            f"退役：{', '.join(env.get('retired', [])) or '(なし)'}",
            f"**{current['summary']}**",
            f"actionable：{len(actionable_items)}件",
        ]
        for fragment in required:
            if fragment not in text:
                fail(f"generated view is stale or incomplete: {name} missing {fragment}")
        if actionable:
            marker = f"- [{actionable['id']}] priority={actionable['priority']}：{actionable['title']}"
            if marker not in text:
                fail(f"generated view is missing actionable work item: {name}: {actionable['id']}")

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
