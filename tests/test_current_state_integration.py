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

    def test_current_state_work_queue_is_valid_and_selects_wp(self):
        validate_work_items(self.state["work_items"])
        actionable = select_actionable(self.state["work_items"], self.state["updated"])
        self.assertEqual([item["id"] for item in actionable], ["WP無料ホスティング検証"])
        self.assertEqual(self.state["next_step"]["id"], "WP無料ホスティング検証")

    def test_wp_progress_keeps_completed_steps_and_resume_point(self):
        wp = next(item for item in self.state["work_items"] if item["id"] == "WP無料ホスティング検証")
        steps = {step["id"]: step for step in wp["progress"]["steps"]}
        for step_id in ("free-account", "subdomain", "admin-login", "wordpress-install",
                        "script-installer-recheck", "https", "sitemap"):
            self.assertEqual(steps[step_id]["status"], "done")
        self.assertEqual(steps["google-tests"]["status"], "waiting_external")
        self.assertEqual(wp["progress"]["current_step"], "ads-tests")
        self.assertEqual(steps["ads-tests"]["status"], "in_progress")

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
