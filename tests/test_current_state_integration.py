#!/usr/bin/env python3
import json
import os
import tempfile
import unittest
import zipfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import current_state_guard
import generate_current_views
import resume_check


class CanonicalCurrentStateIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.state_path = ROOT / "docs" / "現在状態.json"
        self.state = json.loads(self.state_path.read_text(encoding="utf-8"))

    def test_dropbox_is_the_only_daily_queue_and_legacy_data_is_empty(self):
        self.assertEqual(self.state["work_queue_source"], "dropbox_board")
        self.assertNotIn("work_items", self.state)
        self.assertNotIn("next_step", self.state)
        self.assertIn("Issue #1059", " ".join(self.state["known_constraints"]))
        current_state_guard.validate_state(self.state)

    def test_technical_evidence_survives_queue_removal(self):
        summary = self.state["current_position"]["summary"]
        self.assertIn("部分合格", summary)
        self.assertIn("チェックボックス", summary)
        self.assertIn("WritingBlock", summary)
        self.assertIn("sitemap.xml", summary)
        closeout = self.state["verification_records"]["closeout_sync_gap_2026_10_08"]
        self.assertEqual(closeout["status"], "verified")
        self.assertIn("一本化", closeout["corrective_action"])

    def test_generated_views_have_no_github_queue(self):
        bud, handover = generate_current_views.render(self.state)
        for view in (bud, handover):
            self.assertIn("/ChatGPT/Dropbox作業管理統合ボード.xlsx", view)
            self.assertIn("古いGitHub項目へフォールバックしない", view)
            self.assertNotIn("actionable：", view)
            self.assertNotIn("validation-findings-follow-up [in_progress]", view)

    def test_resume_check_accepts_canonical_state_with_readable_board(self):
        old_state = resume_check.STATE
        old_board = os.environ.get("DROPBOX_WORK_QUEUE_PATH")
        resume_check.STATE = self.state_path
        try:
            with tempfile.TemporaryDirectory() as td:
                board = Path(td) / "Dropbox作業管理統合ボード.xlsx"
                with zipfile.ZipFile(board, "w") as workbook:
                    workbook.writestr("[Content_Types].xml", "<Types></Types>")
                    workbook.writestr("xl/workbook.xml", "<workbook></workbook>")
                os.environ["DROPBOX_WORK_QUEUE_PATH"] = str(board)
                self.assertEqual(resume_check.main(), 0)
        finally:
            resume_check.STATE = old_state
            if old_board is None:
                os.environ.pop("DROPBOX_WORK_QUEUE_PATH", None)
            else:
                os.environ["DROPBOX_WORK_QUEUE_PATH"] = old_board


if __name__ == "__main__":
    unittest.main()
