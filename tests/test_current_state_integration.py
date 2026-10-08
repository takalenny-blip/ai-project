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

    def test_current_state_work_queue_is_valid_and_selects_gsc_sitemap_troubleshooting(self):
        validate_work_items(self.state["work_items"])
        actionable = select_actionable(self.state["work_items"], self.state["updated"])
        self.assertTrue(actionable)
        self.assertEqual(self.state["next_step"]["id"], actionable[0]["id"])
        self.assertEqual(actionable[0]["id"], "GSC-確認")
        self.assertTrue(any(item["id"] == "WP無料ホスティング検証" for item in actionable))
        gsc = next(item for item in self.state["work_items"] if item["id"] == "GSC-確認")
        gsc_steps = {step["id"]: step for step in gsc["progress"]["steps"]}
        self.assertEqual(gsc["progress"]["current_step"], "github-pages-sitemap-retrieval")
        self.assertEqual(gsc_steps["github-pages-robots-txt"]["status"], "done")
        self.assertEqual(gsc_steps["github-pages-sitemap-retrieval"]["status"], "in_progress")

    def test_current_state_preserves_structured_progress(self):
        wp = next(item for item in self.state["work_items"] if item["id"] == "WP無料ホスティング検証")
        steps = {step["id"]: step for step in wp["progress"]["steps"]}
        for step_id in ("free-account", "subdomain", "admin-login", "wordpress-install",
                        "script-installer-recheck", "https", "sitemap",
                        "blog2-publication", "blog3-publication"):
            self.assertEqual(steps[step_id]["status"], "done")
        current_step = wp["progress"]["current_step"]
        self.assertIn(current_step, steps)
        self.assertNotEqual(steps[current_step]["status"], "done")
        if wp["execution_state"] == "waiting_external":
            self.assertEqual(steps[current_step]["status"], "waiting_external")
        else:
            self.assertNotEqual(steps[current_step]["status"], "waiting_external")
        self.assertEqual(steps["wp-icon-asset"]["status"], "done")
        self.assertEqual(current_step, "wp-icon")
        self.assertEqual(steps["wp-icon"]["status"], "in_progress")

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


if __name__ == "__main__":
    unittest.main()
