#!/usr/bin/env python3
"""Apply an audited canonical-state patch and prepare one atomic state bundle."""
from __future__ import annotations
import argparse, json, re, subprocess, sys
from datetime import date
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from save_and_currentize import merge_patch, validate_queue_retirement, render_views, STATE_PATH, BUD_PATH, HANDOVER_PATH


def validate_technical_patch(patch: object, request: dict) -> dict:
    if not isinstance(patch, dict):
        raise SystemExit("patch must be an object")
    if not patch:
        raise SystemExit("provide a non-empty technical-state patch")
    if "work_items" in patch or "work_item_updates" in request:
        raise SystemExit("GitHub work_items updates are retired; update the Dropbox board for daily queue changes")
    return patch


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--request-file", type=Path, required=True)
    args = ap.parse_args()
    req = json.loads(args.request_file.read_text(encoding="utf-8"))
    uid = req.get("update_id", "")
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9][a-z0-9-]{2,70}", uid):
        raise SystemExit("invalid update_id")
    patch = validate_technical_patch(req.get("patch", {}), req)
    for key in ("purpose", "source"):
        if not isinstance(req.get(key), str) or not req[key].strip():
            raise SystemExit(f"{key} must be a non-empty string")
    audit_path = ROOT / "docs" / "state-updates" / f"{uid}.json"
    if audit_path.exists():
        raise SystemExit(f"refusing to overwrite {audit_path.relative_to(ROOT)}")
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    merge_patch(state, patch)
    state["updated"] = date.today().isoformat()
    sync_next_step(state)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema_version": 1, "date": uid[:10], "kind": "canonical_state_update",
             "purpose": req["purpose"], "source": req["source"],
             "confirmed": req.get("confirmed", []), "not_verified": req.get("not_verified", []),
             "references": req.get("references", []), "patch": patch,
             "patch": patch}
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
