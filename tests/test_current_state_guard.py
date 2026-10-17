#!/usr/bin/env python3
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import current_state_guard as guard


class CurrentStateGuardTests(unittest.TestCase):
    def setUp(self):
        self.state = json.loads((ROOT / "docs" / "現在状態.json").read_text(encoding="utf-8"))

    def test_canonical_technical_state_passes(self):
        guard.validate_state(copy.deepcopy(self.state))

    def test_legacy_github_queue_source_is_rejected(self):
        state = copy.deepcopy(self.state)
        state["work_queue_source"] = "github_json"
        with self.assertRaisesRegex(ValueError, "work_queue_source must be dropbox_board"):
            guard.validate_state(state)

    def test_nonempty_legacy_work_items_are_rejected(self):
        state = copy.deepcopy(self.state)
        state["work_items"] = [{"id": "obsolete"}]
        with self.assertRaisesRegex(ValueError, "legacy GitHub work_items field is retired"):
            guard.validate_state(state)

    def test_retired_next_step_field_is_rejected(self):
        state = copy.deepcopy(self.state)
        state["next_step"] = {"target": "old queue"}
        with self.assertRaisesRegex(ValueError, "legacy next_step field is retired"):
            guard.validate_state(state)

    def test_empty_legacy_work_items_field_is_also_rejected(self):
        state = copy.deepcopy(self.state)
        state["work_items"] = []
        with self.assertRaisesRegex(ValueError, "legacy GitHub work_items field is retired"):
            guard.validate_state(state)

    def test_active_environment_cannot_also_be_retired(self):
        state = copy.deepcopy(self.state)
        state["execution_environment"]["retired"].append(state["execution_environment"]["active"])
        with self.assertRaisesRegex(ValueError, "active environment is also retired"):
            guard.validate_state(state)

    def test_verified_record_requires_evidence(self):
        state = copy.deepcopy(self.state)
        record = next(v for v in state["verification_records"].values() if v.get("status") == "verified")
        record["evidence"] = None
        with self.assertRaisesRegex(ValueError, "verified verification record requires method and checked_at"):
            guard.validate_state(state)

    def test_pending_external_response_gate_requires_fields(self):
        state = copy.deepcopy(self.state)
        state["external_response_gate"]["status"] = "pending"
        state["external_response_gate"].pop("purpose", None)
        with self.assertRaisesRegex(ValueError, "pending external_response_gate missing"):
            guard.validate_state(state)

    def test_pending_external_response_gate_with_contract_passes(self):
        state = copy.deepcopy(self.state)
        gate = state["external_response_gate"]
        gate.update({
            "status": "pending",
            "purpose": "react to proposal",
            "trigger": "proposal received",
            "required_action": "respond",
            "completion": "reaction presented",
        })
        guard.validate_state(state)

    def test_cloned_environment_requires_evidence(self):
        state = copy.deepcopy(self.state)
        state["work_pc"] = {"clone_status": "cloned"}
        state["work_pc"].pop("clone_evidence", None)
        with self.assertRaisesRegex(ValueError, "clone_status=cloned requires clone_evidence"):
            guard.validate_state(state)

    def test_generated_views_follow_dropbox_only_contract(self):
        guard.validate_generated_views(copy.deepcopy(self.state))

    def test_wordpress_lane_rejects_stale_blogger_automation_policy(self):
        state = copy.deepcopy(self.state)
        state["primary_lane"] = "experience-log → Blogger下書き確認 → WordPress本番公開"
        state["surgery"]["next_design_item"] = "experience-log → Blogger自動化へ戻る"
        state["migration"]["normal_work_policy"] = "経験ログを中心としたAI編集・Blogger自動化へ戻る"
        with self.assertRaisesRegex(ValueError, "publishing-lane prose still points back to Blogger automation"):
            guard.validate_publishing_lane_consistency(state)


if __name__ == "__main__":
    unittest.main()
