#!/usr/bin/env python3
import os
import tempfile
import unittest
import zipfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import resume_check

class ResumeCheckSingleSourceTests(unittest.TestCase):
    def make_board(self, path):
        with zipfile.ZipFile(path, "w") as workbook:
            workbook.writestr("[Content_Types].xml", "<Types></Types>")
            workbook.writestr("xl/workbook.xml", "<workbook></workbook>")

    def run_check(self, board=None, pending=False):
        old_board = os.environ.get("DROPBOX_WORK_QUEUE_PATH")
        old_remote = os.environ.get("DROPBOX_REQUIRE_REMOTE")
        old_token = os.environ.get("DROPBOX_ACCESS_TOKEN")
        old_rules = resume_check.RULES
        try:
            with tempfile.TemporaryDirectory() as td:
                if board:
                    path = Path(td) / "board.xlsx"
                    self.make_board(path)
                    os.environ["DROPBOX_WORK_QUEUE_PATH"] = str(path)
                else:
                    os.environ["DROPBOX_WORK_QUEUE_PATH"] = str(Path(td) / "missing.xlsx")
                os.environ.pop("DROPBOX_REQUIRE_REMOTE", None)
                os.environ.pop("DROPBOX_ACCESS_TOKEN", None)
                if pending:
                    original = resume_check.RULES.read_text(encoding="utf-8")
                    changed = original.replace("状態：clear（未処理の外部提案なし）", "状態：pending")
                    rules_path = Path(td) / "rules.md"
                    rules_path.write_text(changed, encoding="utf-8")
                    resume_check.RULES = rules_path
                return resume_check.main()
        finally:
            resume_check.RULES = old_rules
            for key, old in (("DROPBOX_WORK_QUEUE_PATH", old_board), ("DROPBOX_REQUIRE_REMOTE", old_remote), ("DROPBOX_ACCESS_TOKEN", old_token)):
                if old is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = old

    def test_valid_rules_and_board_pass(self):
        self.assertEqual(self.run_check(board=True), 0)

    def test_missing_board_stops_without_fallback(self):
        self.assertEqual(self.run_check(board=False), 1)

    def test_pending_external_response_stops(self):
        self.assertEqual(self.run_check(board=True, pending=True), 3)

if __name__ == "__main__":
    unittest.main()
