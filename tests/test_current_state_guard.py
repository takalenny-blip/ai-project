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
            "next_step": {
                "environment": "work_pc",
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
        }

    def test_active_work_pc_passes(self):
        guard.validate_state(self.base_state())
        guard.validate_next_step_no_retired(self.base_state())

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
