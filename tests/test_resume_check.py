#!/usr/bin/env python3
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import resume_check


class ResumeCheckExternalArtifactTests(unittest.TestCase):
    def write_state(self, root, prerequisite, readiness="ready"):
        state = {
            "execution_environment": {"active": "work_pc", "retired": ["vaio_p"]},
            "current_position": {"summary": "current"},
            "next_step": {
                "environment": "work_pc",
                "target": "target",
                "evidence": "evidence",
                "readiness": readiness,
                "prerequisites": [prerequisite],
            },
            "resume_manifest": {"source": "docs/現在状態.json", "generator": "scripts/resume_manifest.py"},
        }
        if readiness == "blocked":
            state["next_step"]["blocked_reason"] = "blocked"
            state["next_step"]["unblock_action"] = "preflight"
        (root / "docs").mkdir()
        (root / "docs" / "現在状態.json").write_text(json.dumps(state), encoding="utf-8")

    def run_check(self, root, artifact):
        old_state = resume_check.STATE
        old_root = resume_check.ROOT
        old_path = os.environ.get("DIMORA_ARTIFACT_PATH")
        resume_check.STATE = root / "docs" / "現在状態.json"
        resume_check.ROOT = root
        os.environ["DIMORA_ARTIFACT_PATH"] = str(artifact)
        try:
            return resume_check.main()
        finally:
            resume_check.STATE = old_state
            resume_check.ROOT = old_root
            if old_path is None:
                os.environ.pop("DIMORA_ARTIFACT_PATH", None)
            else:
                os.environ["DIMORA_ARTIFACT_PATH"] = old_path

    def test_ready_valid_json_and_count(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            artifact = root / "dimora.json"
            artifact.write_text(json.dumps([{"eventId": 1}, {"eventId": 2}]), encoding="utf-8")
            digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
            p = {"name": "dimora-favorite-programs.json", "kind": "external_artifact",
                 "verify_scope": "runtime", "status": "verified",
                 "evidence": {"method": "runtime preflight", "checked_at": "2026-09-20",
                              "sha256": digest, "record_count": 2}}
            self.write_state(root, p)
            self.assertEqual(self.run_check(root, artifact), 0)

    def test_invalid_json_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            artifact = root / "dimora.json"
            artifact.write_text("{invalid", encoding="utf-8")
            digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
            p = {"name": "dimora-favorite-programs.json", "kind": "external_artifact",
                 "verify_scope": "runtime", "status": "verified",
                 "evidence": {"method": "runtime preflight", "checked_at": "2026-09-20",
                              "sha256": digest, "record_count": 1}}
            self.write_state(root, p)
            self.assertEqual(self.run_check(root, artifact), 1)

    def test_record_count_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            artifact = root / "dimora.json"
            artifact.write_text(json.dumps([{"eventId": 1}]), encoding="utf-8")
            digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
            p = {"name": "dimora-favorite-programs.json", "kind": "external_artifact",
                 "verify_scope": "runtime", "status": "verified",
                 "evidence": {"method": "runtime preflight", "checked_at": "2026-09-20",
                              "sha256": digest, "record_count": 2}}
            self.write_state(root, p)
            self.assertEqual(self.run_check(root, artifact), 1)

    def test_pending_external_response_gate_stops_with_exit_3(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            artifact = root / "dimora.json"
            p = {"name": "dimora-favorite-programs.json", "kind": "external_artifact",
                 "verify_scope": "runtime", "status": "unverified"}
            self.write_state(root, p, readiness="blocked")
            state_path = root / "docs" / "現在状態.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["external_response_gate"] = {
                "status": "pending", "purpose": "react", "trigger": "proposal received",
                "required_action": "respond", "completion": "reaction presented",
            }
            state_path.write_text(json.dumps(state), encoding="utf-8")
            self.assertEqual(self.run_check(root, artifact), 3)

    def test_missing_artifact_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            artifact = root / "missing.json"
            p = {"name": "dimora-favorite-programs.json", "kind": "external_artifact",
                 "verify_scope": "runtime", "status": "verified",
                 "evidence": {"method": "runtime preflight", "checked_at": "2026-09-20",
                              "sha256": "0" * 64, "record_count": 0}}
            self.write_state(root, p)
            self.assertEqual(self.run_check(root, artifact), 1)

    def test_pending_gate_reaction_missing_field_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            artifact = root / "dimora.json"
            p = {"name": "dimora-favorite-programs.json", "kind": "external_artifact", "verify_scope": "runtime", "status": "unverified"}
            self.write_state(root, p, readiness="blocked")
            state_path = root / "docs" / "現在状態.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["external_response_gate"] = {
                "status": "pending", "purpose": "react", "trigger": "proposal received",
                "required_action": "respond", "completion": "reaction presented",
                "reaction_contract": {"required_fields": ["proposal","judgment","reason","next_action","consistency"],"judgment_values": ["adopt","adopt_modified","hold","reject","info_only"],"rule": "all five required","clear_condition": "all five valid"},
                "last_reaction": {"proposal": "x", "judgment": "adopt", "reason": "r", "next_action": "n"}
            }
            state_path.write_text(json.dumps(state), encoding="utf-8")
            self.assertEqual(self.run_check(root, artifact), 1)

    def test_reaction_contract_accepts_complete_consistent_reaction(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            artifact = root / "dimora.json"
            artifact.write_text(json.dumps([{"eventId": 1}]), encoding="utf-8")
            digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
            p = {"name": "dimora-favorite-programs.json", "kind": "external_artifact", "verify_scope": "runtime", "status": "verified",
                 "evidence": {"method": "runtime preflight", "checked_at": "2026-09-20", "sha256": digest, "record_count": 1}}
            self.write_state(root, p)
            state_path = root / "docs" / "現在状態.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["external_response_gate"] = {
                "status": "clear", "purpose": "react", "trigger": "proposal received",
                "required_action": "respond", "completion": "reaction presented",
                "reaction_contract": {"required_fields": ["proposal","judgment","reason","next_action","consistency"],"judgment_values": ["adopt","adopt_modified","hold","reject","info_only"],"rule": "all five required","clear_condition": "all five valid"},
                "last_reaction": {"proposal": "x", "judgment": "adopt_modified", "reason": "r", "next_action": "n", "consistency": True}
            }
            state_path.write_text(json.dumps(state), encoding="utf-8")
            self.assertEqual(self.run_check(root, artifact), 0)


if __name__ == "__main__":
    unittest.main()
