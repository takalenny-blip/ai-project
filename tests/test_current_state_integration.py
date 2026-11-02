#!/usr/bin/env python3
import os
import tempfile
import unittest
import zipfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import current_state_guard
import resume_check

class SingleSourceRulesIntegrationTests(unittest.TestCase):
    def make_board(self, path):
        with zipfile.ZipFile(path, "w") as workbook:
            workbook.writestr("[Content_Types].xml", "<Types></Types>")
            workbook.writestr("xl/workbook.xml", "<workbook></workbook>")

    def test_rules_are_the_only_current_state_source(self):
        text = (ROOT / "rules" / "運用ルール.md").read_text(encoding="utf-8")
        current_state_guard.validate_rules(text)
        self.assertIn("現在状態・共通運用ルールの唯一の正本", text)
        self.assertIn("Dropboxの固定ファイル", text)

    def test_resume_check_passes_with_readable_board(self):
        old_board = os.environ.get("DROPBOX_WORK_QUEUE_PATH")
        old_remote = os.environ.get("DROPBOX_REQUIRE_REMOTE")
        old_token = os.environ.get("DROPBOX_ACCESS_TOKEN")
        try:
            with tempfile.TemporaryDirectory() as td:
                board = Path(td) / "board.xlsx"
                self.make_board(board)
                os.environ["DROPBOX_WORK_QUEUE_PATH"] = str(board)
                os.environ.pop("DROPBOX_REQUIRE_REMOTE", None)
                os.environ.pop("DROPBOX_ACCESS_TOKEN", None)
                self.assertEqual(resume_check.main(), 0)
        finally:
            for key, old in (("DROPBOX_WORK_QUEUE_PATH", old_board), ("DROPBOX_REQUIRE_REMOTE", old_remote), ("DROPBOX_ACCESS_TOKEN", old_token)):
                if old is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = old

if __name__ == "__main__":
    unittest.main()
