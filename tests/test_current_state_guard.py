#!/usr/bin/env python3
import json
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import current_state_guard as guard


class CurrentStateGuardTests(unittest.TestCase):
    def base_state(self):
        return {
            "execution_environment": {"active": "work_pc", "retired": ["vaio_p"]},
            "current_position": {"summary": "current"},
            "next_step": {
                "environment": "work_pc",
                "target": "work_pcで再開確認を実施する",
                "evidence": "resume_check.py",
                "status": "proposed",
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

    def test_stale_pr3_next_step_fails(self):\n        state = self.base_state()\n        state["next_step"]["target"] = "PR3完了後のcanonical現在状態を確認し、次の実装単位を決める"\n        with self.assertRaises(ValueError):\n            guard.validate_state(state)\n\n    def test_cloned_without_evidence_fails(self):
        state = self.base_state()
        state["work_pc"] = {"clone_status": "cloned"}
        with self.assertRaises(ValueError):
            guard.validate_state(state)

    def test_stale_manifest_source_fails(self):
        state = self.base_state()
        state["resume_manifest"]["source"] = "README.md"
        with self.assertRaises(ValueError):
            guard.validate_hash_contract(state)


if __name__ == "__main__":
    unittest.main()
