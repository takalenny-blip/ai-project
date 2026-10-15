#!/usr/bin/env python3
import json
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from work_queue import select_actionable, validate_work_items
import resume_check


class CanonicalCurrentStateIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.state_path = ROOT / "docs" / "現在状態.json"
        self.state = json.loads(self.state_path.read_text(encoding="utf-8"))

    def test_current_state_work_queue_marks_url_checks_done_and_waits_for_google(self):
        validate_work_items(self.state["work_items"])
        actionable = select_actionable(self.state["work_items"], self.state["updated"])
        self.assertTrue(actionable)
        self.assertEqual(self.state["next_step"]["id"], actionable[0]["id"])
        self.assertIn("GITHUB-PAGES-PRODUCTION", [item["id"] for item in actionable])
        self.assertNotIn("GITHUB-PAGES-SEO", [item["id"] for item in self.state["work_items"]])
        self.assertIn("robots.txt", self.state["current_position"]["summary"])
        self.assertIn("sitemap.xml", self.state["current_position"]["summary"])
        self.assertIn("トップページ", self.state["current_position"]["summary"])
        gsc = next(item for item in self.state["work_items"] if item["id"] == "GSC-確認")
        gsc_steps = {step["id"]: step for step in gsc["progress"]["steps"]}
        self.assertEqual(gsc["execution_state"], "waiting_external")
        self.assertTrue(gsc.get("wait_reason"))
        self.assertEqual(gsc["progress"]["current_step"], "github-pages-sitemap-retrieval")
        self.assertEqual(gsc_steps["github-pages-robots-txt"]["status"], "done")
        self.assertEqual(gsc_steps["site-index-status-check"]["status"], "done")
        self.assertEqual(gsc_steps["github-pages-sitemap-retrieval"]["status"], "waiting_external")
        self.assertIn("再実施しない", gsc_steps["site-index-status-check"]["evidence"])

    def test_current_state_preserves_structured_progress(self):
        work_item = next(item for item in self.state["work_items"] if item["id"] == "GITHUB-PAGES-PRODUCTION")
        steps = {step["id"]: step for step in work_item["progress"]["steps"]}
        for step_id in ("free-account", "subdomain", "admin-login", "wordpress-install",
                        "script-installer-recheck", "https", "sitemap",
                        "blog2-publication", "blog3-publication"):
            self.assertEqual(steps[step_id]["status"], "done")
        current_step = work_item["progress"]["current_step"]
        self.assertIn(current_step, steps)
        self.assertNotEqual(steps[current_step]["status"], "done")
        if work_item["execution_state"] == "waiting_external":
            self.assertEqual(steps[current_step]["status"], "waiting_external")
        else:
            self.assertNotEqual(steps[current_step]["status"], "waiting_external")
        self.assertEqual(steps["wp-icon-asset"]["status"], "done")
        self.assertEqual(current_step, "ongoing-publication")
        self.assertEqual(steps["wp-icon"]["status"], "done")

    def test_removed_dependencies_are_not_referenced(self):
        ids = {item["id"] for item in self.state["work_items"]}
        for item in self.state["work_items"]:
            self.assertTrue(set(item.get("depends_on", [])) <= ids, item["id"])
            for prerequisite in item.get("prerequisites", []):
                ref = prerequisite.get("id")
                if ref:
                    self.assertIn(ref, ids, item["id"])

    def test_resume_check_accepts_canonical_state(self):
        old_state = resume_check.STATE
        resume_check.STATE = self.state_path
        try:
            self.assertEqual(resume_check.main(), 0)
        finally:
            resume_check.STATE = old_state

    def test_ai_manual_validation_record_cannot_regress_to_unperformed(self):
        work_item = next(item for item in self.state["work_items"] if item["id"] == "AI-MANUAL-PRODUCTION")
        steps = {step["id"]: step for step in work_item["progress"]["steps"]}
        validation = steps["practical-validation"]
        follow_up = steps["validation-findings-follow-up"]
        self.assertEqual(validation["status"], "done")
        self.assertIn("部分合格", validation["evidence"])
        self.assertIn("チェックボックス", validation["evidence"])
        self.assertIn("WritingBlock", validation["evidence"])
        self.assertIn("外部送信", validation["evidence"])
        self.assertEqual(follow_up["status"], "in_progress")
        self.assertEqual(work_item["progress"]["current_step"], "validation-findings-follow-up")
        self.assertIn("未実施として再提示しない", work_item["target"])

    def test_ai_manual_state_has_no_stale_validation_or_ci_status(self):
        state_text = self.state_path.read_text(encoding="utf-8")
        self.assertNotIn("正本・生成ビュー同期後の最新headのCIは再実行中。", state_text)
        self.assertNotIn("実地インストールと保存テストは次工程であり未実施。", state_text)
        self.assertNotIn("実サービス画面での登録／ログイン／初回会話と作業PCでの実地検証は未完了。", state_text)
        self.assertNotIn("実サービス画面での操作確認と作業PCでの実地検証は別工程として未完了。", state_text)
        work_item = next(item for item in self.state["work_items"] if item["id"] == "AI-MANUAL-PRODUCTION")
        steps = {step["id"]: step for step in work_item["progress"]["steps"]}
        self.assertEqual(steps["practical-validation"]["status"], "done")
        self.assertIn("部分合格", steps["practical-validation"]["evidence"])
        self.assertEqual(steps["validation-findings-follow-up"]["status"], "in_progress")

if __name__ == "__main__":
    unittest.main()
