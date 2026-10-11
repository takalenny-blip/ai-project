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
            "work_items": [{
                "id": "WORK-TEST",
                "title": "test work",
                "priority": 10,
                "status": "queued",
                "depends_on": [],
                "not_before": None,
                "scope": "new_scope",
                "target": "work_pcで再開確認を実施する",
                "evidence": "resume_check.py",
                "readiness": "ready",
                "unblock_action": "none",
                "environment": "work_pc",
                "execution_state": "actionable",
                "progress": {
                    "current_step": "step-1",
                    "steps": [{"id": "step-1", "title": "test step", "status": "pending"}],
                    "updated_at": "2026-09-27",
                },
                "created_at": "2026-09-27",
                "updated_at": "2026-09-27",
            }],
            "next_step": {
                "id": "WORK-TEST",
                "title": "test work",
                "priority": 10,
                "depends_on": [],
                "not_before": None,
                "environment": "work_pc",
                "scope": "new_scope",
                "target": "work_pcで再開確認を実施する",
                "evidence": "resume_check.py",
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

    def test_retired_name_in_historical_target_is_allowed(self):
        state = self.base_state()
        state["work_items"][0]["target"] = "VAIO Pのサーバー化の経験を記事として整理する"
        state["next_step"]["target"] = state["work_items"][0]["target"]
        guard.validate_state(state)

    def test_retired_name_in_generated_historical_work_item_is_allowed(self):
        state = self.base_state()
        state["work_items"][0]["title"] = "VAIO Pのサーバー化の経験を記事として整理する"
        state["work_items"][0]["target"] = "VAIO Pの経験を記事として整理する"
        state["next_step"]["title"] = state["work_items"][0]["title"]
        state["next_step"]["target"] = state["work_items"][0]["target"]

        bud_text, handover_text = guard.render(state)
        for text in (bud_text, handover_text):
            self.assertIn("VAIO Pのサーバー化の経験を記事として整理する", text)


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
        state["work_items"][0]["readiness"] = "blocked"
        state["work_items"][0]["blocked_reason"] = "artifact missing"
        state["next_step"]["blocked_reason"] = "artifact missing"
        state["next_step"]["unblock_action"] = "run preflight"
        state["work_items"][0]["unblock_action"] = "run preflight"
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
        state["work_items"][0]["unblock_action"] = "preflight"
        with self.assertRaises(ValueError):
            guard.validate_state(state)


    def test_stale_unfinished_prose_conflicts_with_done_step(self):
        state = self.base_state()
        state["work_items"] = [{
            "id": "WP無料ホスティング検証",
            "progress": {"steps": [{"id": "wp-icon", "status": "done"}]},
        }]
        state["prose_status_consistency_rules"] = [{
            "work_item_id": "WP無料ホスティング検証",
            "step_id": "wp-icon",
            "keywords": ["サイトアイコン", "実表示確認"],
            "stale_markers": ["未完了", "未確認", "未実施", "残る作業"],
        }]
        state["current_position"]["next_stage_boundary"] = (
            "サイトアイコン画像の適用・実表示確認が未完了。"
        )
        with self.assertRaisesRegex(ValueError, "stale prose contradicts completed work step"):
            guard.validate_completed_step_prose(state)

    def test_unrelated_unconfirmed_status_does_not_conflict_with_done_step(self):
        state = self.base_state()
        state["work_items"] = [{
            "id": "WP無料ホスティング検証",
            "progress": {"steps": [{"id": "wp-icon", "status": "done"}]},
        }]
        state["prose_status_consistency_rules"] = [{
            "work_item_id": "WP無料ホスティング検証",
            "step_id": "wp-icon",
            "keywords": ["サイトアイコン", "実表示確認"],
            "stale_markers": ["未完了", "未確認", "未実施", "残る作業"],
        }]
        state["current_position"]["next_focus"] = (
            "サイトアイコンの実表示確認は完了済み。WordPressのGSC状況は未確認。"
        )
        guard.validate_completed_step_prose(state)


    def test_waiting_external_step_rejects_stale_investigation_title(self):
        state = self.base_state()
        stale_title = "GSCのサイトマップ取得失敗を切り分け、3サイト別インデックス状況を確認する"
        state["next_step"]["title"] = stale_title
        state["work_items"] = [{
            "id": "GSC-確認",
            "title": stale_title,
            "progress": {"steps": [{
                "id": "github-pages-sitemap-retrieval",
                "title": "GSC sitemap.xml取得失敗の原因切り分け",
                "status": "waiting_external",
            }]},
        }]
        state["prose_status_consistency_rules"] = [{
            "work_item_id": "GSC-確認",
            "step_id": "github-pages-sitemap-retrieval",
            "expected_step_status": "waiting_external",
            "keywords": ["サイトマップ取得失敗"],
            "stale_markers": ["切り分け"],
        }]
        with self.assertRaisesRegex(ValueError, "stale prose contradicts waiting_external work step"):
            guard.validate_completed_step_prose(state)

    def test_waiting_external_step_accepts_waiting_title(self):
        state = self.base_state()
        waiting_title = "GSCサイトマップ処理待ちを維持し、GitHub Pages・WordPressのインデックス状況を確認する"
        state["next_step"]["title"] = waiting_title
        state["work_items"] = [{
            "id": "GSC-確認",
            "title": waiting_title,
            "progress": {"steps": [{
                "id": "github-pages-sitemap-retrieval",
                "title": "Google側のGSC sitemap.xml処理待ち",
                "status": "waiting_external",
            }]},
        }]
        state["prose_status_consistency_rules"] = [{
            "work_item_id": "GSC-確認",
            "step_id": "github-pages-sitemap-retrieval",
            "expected_step_status": "waiting_external",
            "keywords": ["サイトマップ取得失敗"],
            "stale_markers": ["切り分け"],
        }]
        guard.validate_completed_step_prose(state)


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



if __name__ == "__main__":
    unittest.main()
