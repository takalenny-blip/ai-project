#!/usr/bin/env python3
"""Apply an audited canonical-state patch and prepare one atomic state bundle."""
from __future__ import annotations
import argparse, json, re, subprocess, sys
from datetime import date
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from save_and_currentize import merge_patch, sync_next_step, render_views, STATE_PATH, BUD_PATH, HANDOVER_PATH

def apply_work_item_updates(state: dict, updates: object) -> None:
    """Apply ID-keyed patches to existing work items without replacing the queue."""
    if updates is None:
        return
    if not isinstance(updates, list) or not updates:
        raise SystemExit("work_item_updates must be a non-empty array when provided")
    work_items = state.get("work_items")
    if not isinstance(work_items, list):
        raise SystemExit("state work_items must be an array")
    seen_update_ids = set()
    for update in updates:
        if not isinstance(update, dict) or set(update) != {"id", "patch"}:
            raise SystemExit("each work_item_update must contain exactly id and patch")
        item_id = update["id"]
        item_patch = update["patch"]
        if not isinstance(item_id, str) or not item_id.strip():
            raise SystemExit("work_item_update id must be a non-empty string")
        if item_id in seen_update_ids:
            raise SystemExit(f"duplicate work_item_update id: {item_id}")
        seen_update_ids.add(item_id)
        if not isinstance(item_patch, dict) or not item_patch:
            raise SystemExit(f"work_item_update patch for {item_id} must be a non-empty object")
        if "id" in item_patch:
            raise SystemExit(f"work_item_update may not change id: {item_id}")
        matches = [item for item in work_items if isinstance(item, dict) and item.get("id") == item_id]
        if len(matches) != 1:
            reason = "not found" if not matches else "is not unique"
            raise SystemExit(f"work_item id {item_id!r} {reason}")
        merge_patch(matches[0], item_patch)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--request-file", type=Path, required=True)
    args = ap.parse_args()
    req = json.loads(args.request_file.read_text(encoding="utf-8"))
    uid = req.get("update_id", "")
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9][a-z0-9-]{2,70}", uid):
        raise SystemExit("invalid update_id")
    patch = req.get("patch", {})
    work_item_updates = req.get("work_item_updates")
    if not isinstance(patch, dict):
        raise SystemExit("patch must be an object")
    if not patch and (not isinstance(work_item_updates, list) or not work_item_updates):
        raise SystemExit("provide a non-empty patch or work_item_updates array")
    if "work_items" in patch and work_item_updates is not None:
        raise SystemExit("use either patch.work_items or work_item_updates, not both")
    for key in ("purpose", "source"):
        if not isinstance(req.get(key), str) or not req[key].strip():
            raise SystemExit(f"{key} must be a non-empty string")
    audit_path = ROOT / "docs" / "state-updates" / f"{uid}.json"
    if audit_path.exists():
        raise SystemExit(f"refusing to overwrite {audit_path.relative_to(ROOT)}")
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    merge_patch(state, patch)
    apply_work_item_updates(state, work_item_updates)
    state["updated"] = date.today().isoformat()
    sync_next_step(state)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema_version": 1, "date": uid[:10], "kind": "canonical_state_update",
             "purpose": req["purpose"], "source": req["source"],
             "confirmed": req.get("confirmed", []), "not_verified": req.get("not_verified", []),
             "references": req.get("references", []), "patch": patch,
             "work_item_updates": work_item_updates or []}
    for key in ("confirmed", "not_verified", "references"):
        if not isinstance(audit[key], list):
            raise SystemExit(f"{key} must be an array")
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    render_views()
    for command in ([sys.executable, "scripts/check_repo_integrity.py"],
                    [sys.executable, "scripts/current_state_guard.py"],
                    [sys.executable, "scripts/resume_check.py"]):
        subprocess.run(command, cwd=ROOT, check=True)
    subprocess.run(["git", "add", str(STATE_PATH), str(BUD_PATH), str(HANDOVER_PATH), str(audit_path)], cwd=ROOT, check=True)
    expected = {str(STATE_PATH.relative_to(ROOT)), str(BUD_PATH.relative_to(ROOT)),
                str(HANDOVER_PATH.relative_to(ROOT)), str(audit_path.relative_to(ROOT))}
    changed = set(subprocess.check_output(["git", "-c", "core.quotePath=false", "diff", "--cached", "--name-only"], cwd=ROOT, text=True).splitlines())
    if changed != expected:
        raise SystemExit(f"unexpected staged paths: {sorted(changed)}")
    print("OK: canonical state, audit record, and generated views staged atomically")
if __name__ == "__main__":
    main()
