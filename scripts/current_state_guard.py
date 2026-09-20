#!/usr/bin/env python3
"""Guard the canonical resume state and current-state views."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "docs" / "現在状態.json"
BUD_PATH = ROOT / "BUD.md"
HANDOVER_PATH = ROOT / "docs" / "引き継ぎ" / "現在の引き継ぎ.md"

REQUIRED = ("execution_environment", "current_position", "next_step")
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


def validate_state(state: dict) -> None:
    missing = [key for key in REQUIRED if key not in state]
    if missing:
        fail("missing required fields: " + ", ".join(missing))

    env = state["execution_environment"]
    active = env.get("active")
    retired = env.get("retired", [])
    nxt = state["next_step"]
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
    if not current.get("summary"):
        fail("current_position.summary is missing")

    target = nxt["target"]
    if any(phrase in target for phrase in ABSTRACT_NEXT_STEP):
        fail("next_step.target is too abstract or stale; require current concrete work")

    work_pc = state.get("work_pc", {})
    if work_pc.get("clone_status") == "cloned" and not work_pc.get("clone_evidence"):
        fail("work_pc clone_status=cloned requires clone_evidence")


def retired_tokens(state: dict) -> tuple[str, ...]:
    tokens = []
    for item in state["execution_environment"].get("retired", []):
        tokens.append(item)
        tokens.extend(RETIRED_ALIASES.get(item, ()))
    return tuple(dict.fromkeys(tokens))


def validate_next_step_no_retired(state: dict) -> None:
    text = json.dumps(state["next_step"], ensure_ascii=False)
    for token in retired_tokens(state):
        if token in text:
            fail(f"retired environment appears in next_step: {token}")


def validate_generated_views(state: dict) -> None:
    env = state["execution_environment"]
    nxt = state["next_step"]
    current = state["current_position"]
    expected = [
        f"現在：**{env['active']}**",
        f"退役：{', '.join(env.get('retired', [])) or '(なし)'}",
        f"環境：**{nxt['environment']}**",
        f"目的：**{nxt['target']}**",
        f"根拠：{nxt['evidence']}",
        f"**{current['summary']}**",
    ]
    for path in (BUD_PATH, HANDOVER_PATH):
        text = path.read_text(encoding="utf-8")
        for fragment in expected:
            if fragment not in text:
                fail(f"generated view is stale or incomplete: {path} missing {fragment}")
        for token in retired_tokens(state):
            if token in text and token not in "
".join([
                f"退役：{', '.join(env.get('retired', []))}",
            ]):
                fail(f"retired environment leaked into generated view outside retired list: {path}: {token}")


def validate_projects(state: dict) -> None:
    retired = retired_tokens(state)
    if not retired:
        return
    for path in sorted((ROOT / "projects").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if not any(token in text for token in retired):
            continue
        header = "
".join(text.splitlines()[:20]).lower()
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
    validate_next_step_no_retired(state)
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
