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
            "updated": "2026-10-06",
            "canonical_repository": "takalenny-blip/ai-project",
            "primary_lane": "test lane",
            "execution_environment": {"active": "work_pc", "retired": ["vaio_p"]},
            "current_position": {"summary": "current"},
            "direct_chat": {"latest_saved": "2026-10-05T20-53-20.081260+0900", "latest_path": "直チャット/test.md", "legacy_serial_files_preserved": True, "new_timestamp_naming_allowed": True},
            "surgery": {"inventory": "test", "design": "test", "adoption": "test", "bulk_refactor": "test", "verification": "test"},
            "current_state_model": {"target": "test", "generation_flow": "test", "status": "test"},
            "migration": {"status": "test", "normal_work_policy": "test", "temporary_manual_sync": "test"},
            "verification_records": {"resume_check": {"status": "verified", "evidence": {"method": "test fixture", "checked_at": "2026-09-20"}}},
            "work_queue_source": "dropbox_board",
            "work_items": [],
            "next_step": {
                "id": "LEGACY-QUEUE-RETIRED",
                "title": "legacy queue retired",
                "environment": "work_pc",
                "target": "日常作業の選定・優先順位・再開判断はDropbox固定ボードのみから行う。",
                "evidence": "Dropbox is the sole daily queue.",
                "readiness": "ready",
                "unblock_action": "none",
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


    def test_legacy_verification_model_is_temporarily_accepted(self):
        state = self.base_state()
        state.pop("verification_records")
        state["next_step"].pop("scope")
        guard.validate_state(state)

    def test_active_work_pc_passes(self):
        guard.validate_state(self.base_state())
        guard.validate_state(self.base_state())


    @unittest.skip("legacy GitHub work_items/next_step queue semantics retired")


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

    def test_retired_name_in_historical_target_is_allowed(self):
        state = self.base_state()
        state["next_step"]["target"] = "VAIO Pのサーバー化の経験を記事として整理する"
        guard.validate_state(state)

    @unittest.skip("legacy GitHub work-item view retired; historical items are not rendered in Dropbox mode")
    @unittest.skip("legacy GitHub work_items/next_step queue semantics retired")

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


    @unittest.skip("legacy GitHub work_items/next_step queue semantics retired")




    def test_wordpress_primary_lane_rejects_stale_blogger_automation_policy(self):
        state = self.base_state()
        state["primary_lane"] = "experience-log → Blogger下書き確認 → WordPress本番公開"
        state["surgery"] = {"next_design_item": "experience-log → Blogger自動化へ戻る"}
        state["migration"] = {
            "normal_work_policy": "経験ログを中心としたAI編集・Blogger自動化へ戻る"
        }
        with self.assertRaisesRegex(ValueError, "publishing-lane prose still points back to Blogger automation"):
            guard.validate_publishing_lane_consistency(state)

    def test_wordpress_primary_lane_accepts_current_publishing_policy(self):
        state = self.base_state()
        state["primary_lane"] = "experience-log → Blogger下書き確認 → WordPress本番公開"
        state["surgery"] = {
            "next_design_item": "GSC-確認完了後にBLOG-0004の企画・一次資料確認・制作へ進む"
        }
        state["migration"] = {
            "normal_work_policy": (
                "経験ログを中心としたAI編集を継続する。Bloggerは下書き・表示確認、"
                "WordPressは本番公開先、GitHub Pagesは予備公開サイトとする。"
            )
        }
        guard.validate_publishing_lane_consistency(state)



    def test_legacy_queue_data_must_be_empty(self):
        state = self.base_state()
        state["work_items"] = [{"id": "OLD"}]
        with self.assertRaisesRegex(ValueError, "legacy GitHub work_items must be empty"):
            guard.validate_state(state)

    def test_legacy_queue_source_is_rejected(self):
        state = self.base_state()
        state["work_queue_source"] = "github_json"
        with self.assertRaisesRegex(ValueError, "Dropbox is the only daily queue"):
            guard.validate_state(state)

    def test_dropbox_board_mode_does_not_treat_legacy_work_items_as_queue(self):
        state = self.base_state()
        state["work_queue_source"] = "dropbox_board"
        state["work_items"] = []
        guard.validate_state(state)
        bud_text, handover_text = guard.render(state)
        for rendered in (bud_text, handover_text):
            self.assertIn("Dropboxの固定ファイル /ChatGPT/Dropbox作業管理統合ボード.xlsx", rendered)
            self.assertIn("古いGitHub項目へフォールバックしない", rendered)
            self.assertNotIn("actionable：", rendered)

    def test_dropbox_board_mode_generated_views_guard_accepts_queue_contract(self):
        state = self.base_state()
        state["work_queue_source"] = "dropbox_board"
        guard.validate_generated_views(state)


if __name__ == "__main__":
    unittest.main()
