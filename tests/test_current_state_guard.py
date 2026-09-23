#!/usr/bin/env python3
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import current_state_guard as guard


ROOT = Path(__file__).resolve().parents[1]


def git_blob_sha(path):
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()


class CurrentStateGuardTests(unittest.TestCase):
    def base_state(self):
        resume_check = ROOT / "scripts" / "resume_check.py"
        return {
            "execution_environment": {"active": "work_pc", "retired": ["vaio_p"]},
            "current_position": {"summary": "current"},
            "verification_records": {"resume_check": {"status": "verified", "evidence": {"method": "test fixture", "checked_at": "2026-09-20"}}},
            "next_step": {
                "environment": "work_pc",
                "scope": "new_scope",
                "target": "work_pcで再開確認を実施する",
                "evidence": "resume_check.py",
                "readiness": "ready",
                "prerequisites": [{"name": "scripts/resume_check.py", "kind": "repo_file", "verify_scope": "ci", "status": "verified", "evidence": {"method": "test fixture", "checked_at": "2026-09-20", "blob_sha": git_blob_sha(resume_check)}}],
            },
            "work_pc": {"clone_status": "unverified"},
            "resume_manifest": {
                "source": "docs/現在状態.json",
                "generator": "scripts/resume_manifest.py",
            },
            "external_response_gate": {
                "status": "clear",
                "clear_reason": "no pending external proposal",
                "reaction_contract": {
                    "required_fields": ["proposal", "judgment", "reason", "next_action", "consistency"],
                    "judgment_values": ["adopt", "adopt_modified", "hold", "reject", "info_only"],
                    "rule": "all five required",
                    "clear_condition": "all five valid",
                },
            },
        }


    def test_open_threads_and_active_track_pass(self):
        state = self.base_state()
        state["active_track"] = "main"
        state["open_threads"] = [{
            "id": "thread-1", "title": "副線", "kind": "proposal", "opened_at": "2026-09-23",
            "status": "進行中", "next_action": "確認する",
            "state_changes": [{"changed_by": "taka", "changed_at": "2026-09-23", "reason": "test"}],
        }]
        guard.validate_open_threads(state)

    def test_active_track_must_reference_thread(self):
        state = self.base_state()
        state["active_track"] = "missing-thread"
        state["open_threads"] = []
        with self.assertRaises(ValueError):
            guard.validate_open_threads(state)

    def test_thread_state_change_is_required(self):
        state = self.base_state()
        state["active_track"] = "main"
        state["open_threads"] = [{
            "id": "thread-1", "title": "副線", "kind": "proposal", "opened_at": "2026-09-23",
            "status": "保留", "next_action": "確認する", "state_changes": [],
        }]
        with self.assertRaises(ValueError):
            guard.validate_open_threads(state)

    def test_legacy_verification_model_is_temporarily_accepted(self):
        state = self.base_state()
        state.pop("verification_records")
        state["next_step"].pop("scope")
        guard.validate_state(state)

    def test_active_work_pc_passes(self):
        guard.validate_state(self.base_state())
        guard.validate_next_step_no_retired(self.base_state())


    def test_next_step_repeating_verified_scope_fails(self):
        state = self.base_state()
        state["next_step"]["scope"] = "resume_check"
        with self.assertRaises(ValueError):
            guard.validate_state(state)

    def test_missing_next_step_scope_fails(self):
        state = self.base_state()
        state["next_step"].pop("scope")
        with self.assertRaises(ValueError):
            guard.validate_state(state)

    def test_verified_record_without_evidence_fails(self):
        state = self.base_state()
        state["verification_records"]["resume_check"]["evidence"] = None
        with self.assertRaises(ValueError):
            guard.validate_state(state)

    def test_retired_environment_mismatch_fails(self):
        state = self.base_state()
        state["next_step"]["environment"] = "vaio_p"
        with self.assertRaises(ValueError):
            guard.validate_state(state)

    def test_retired_alias_in_next_step_fails(self):
        state = self.base_state()
        state["next_step"]["target"] = "VAIO Pで取得テスト"
        with self.assertRaises(ValueError):
            guard.validate_next_step_no_retired(state)

    def test_abstract_next_step_fails(self):
        state = self.base_state()
        state["next_step"]["target"] = "通常のDiMORA本来工程へ復帰"
        with self.assertRaises(ValueError):
            guard.validate_state(state)

    def test_stale_pr3_next_step_fails(self):
        state = self.base_state()
        state["next_step"]["target"] = "PR3完了後のcanonical現在状態を確認し、次の実装単位を決める"
        with self.assertRaises(ValueError):
            guard.validate_state(state)

    def test_ready_with_unverified_prerequisite_fails(self):
        state = self.base_state()
        state["next_step"]["prerequisites"][0]["status"] = "unverified"
        with self.assertRaises(ValueError):
            guard.validate_state(state)

    def test_blocked_with_unverified_prerequisite_passes(self):
        state = self.base_state()
        state["next_step"]["readiness"] = "blocked"
        state["next_step"]["blocked_reason"] = "artifact missing"
        state["next_step"]["unblock_action"] = "run preflight"
        state["next_step"]["prerequisites"][0]["status"] = "unverified"
        guard.validate_state(state)

    def test_verified_without_evidence_fails(self):
        state = self.base_state()
        state["next_step"]["prerequisites"][0]["evidence"] = None
        with self.assertRaises(ValueError):
            guard.validate_state(state)

    def test_cloned_without_evidence_fails(self):
        state = self.base_state()
        state["work_pc"] = {"clone_status": "cloned"}
        with self.assertRaises(ValueError):
            guard.validate_state(state)

    def test_stale_manifest_source_fails(self):
        state = self.base_state()
        state["resume_manifest"]["source"] = "README.md"
        with self.assertRaises(ValueError):
            guard.validate_hash_contract(state)

    def test_verified_repo_file_without_hash_fails(self):
        state = self.base_state()
        state["next_step"]["prerequisites"][0]["evidence"].pop("method", None)
        with self.assertRaises(ValueError):
            guard.validate_state(state)

    def test_verified_repo_file_wrong_hash_fails(self):
        state = self.base_state()
        state["next_step"]["prerequisites"][0]["evidence"]["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            guard.validate_state(state)

    def test_pending_external_response_gate_requires_fields(self):
        state = self.base_state()
        state["external_response_gate"] = {"status": "pending"}
        with self.assertRaises(ValueError):
            guard.validate_state(state)

    def test_pending_external_response_gate_passes_shape_validation(self):
        state = self.base_state()
        state["external_response_gate"] = {
            "status": "pending",
            "purpose": "react to external proposal",
            "trigger": "proposal received",
            "required_action": "state judgment and next action",
            "completion": "reaction presented",
            "reaction_contract": {
                "required_fields": ["proposal", "judgment", "reason", "next_action", "consistency"],
                "judgment_values": ["adopt", "adopt_modified", "hold", "reject", "info_only"],
                "rule": "all five required",
                "clear_condition": "all five valid",
            },
        }
        guard.validate_state(state)

    def test_clear_without_reaction_or_reason_fails(self):
        state = self.base_state()
        state["external_response_gate"] = {
            "status": "clear",
            "reaction_contract": {
                "required_fields": ["proposal", "judgment", "reason", "next_action", "consistency"],
                "judgment_values": ["adopt", "adopt_modified", "hold", "reject", "info_only"],
                "rule": "all five required",
                "clear_condition": "all five valid",
            },
        }
        with self.assertRaises(ValueError):
            guard.validate_state(state)

    def test_readiness_status_conflict_fails(self):
        state = self.base_state()
        state["next_step"]["status"] = "ready"
        state["next_step"]["readiness"] = "blocked"
        state["next_step"]["blocked_reason"] = "blocked"
        state["next_step"]["unblock_action"] = "preflight"
        with self.assertRaises(ValueError):
            guard.validate_state(state)


if __name__ == "__main__":
    unittest.main()
