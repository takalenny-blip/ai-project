import os
import tempfile
import unittest
import zipfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import resume_check


class ResumeCheckDropboxOnlyTests(unittest.TestCase):
    def write_board(self, path):
        with zipfile.ZipFile(path, "w") as workbook:
            workbook.writestr("[Content_Types].xml", "<Types></Types>")
            workbook.writestr("xl/workbook.xml", "<workbook></workbook>")

    def run_check(self, root, board_exists=True, invalid=False):
        old_root, old_rules = resume_check.ROOT, resume_check.RULES
        old_board = os.environ.get("DROPBOX_WORK_QUEUE_PATH")
        old_remote = os.environ.get("DROPBOX_REQUIRE_REMOTE")
        old_token = os.environ.get("DROPBOX_ACCESS_TOKEN")
        resume_check.ROOT = root
        resume_check.RULES = root / "rules" / "運用ルール.md"
        (root / "rules").mkdir(exist_ok=True)
        resume_check.RULES.write_text("# 運用ルール\n", encoding="utf-8")
        board = root / "Dropbox作業管理統合ボード.xlsx"
        if board_exists:
            if invalid:
                board.write_text("not xlsx", encoding="utf-8")
            else:
                self.write_board(board)
        os.environ["DROPBOX_WORK_QUEUE_PATH"] = str(board)
        os.environ.pop("DROPBOX_REQUIRE_REMOTE", None)
        os.environ.pop("DROPBOX_ACCESS_TOKEN", None)
        try:
            return resume_check.main()
        finally:
            resume_check.ROOT, resume_check.RULES = old_root, old_rules
            for key, old in (("DROPBOX_WORK_QUEUE_PATH", old_board), ("DROPBOX_REQUIRE_REMOTE", old_remote), ("DROPBOX_ACCESS_TOKEN", old_token)):
                if old is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = old

    def test_valid_rules_and_readable_board_pass(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(self.run_check(Path(td)), 0)

    def test_missing_board_stops_without_fallback(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(self.run_check(Path(td), board_exists=False), 1)

    def test_unreadable_board_stops_without_fallback(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(self.run_check(Path(td), invalid=True), 1)

    def test_missing_rules_stop(self):
        old_root, old_rules = resume_check.ROOT, resume_check.RULES
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            resume_check.ROOT, resume_check.RULES = root, root / "rules" / "運用ルール.md"
            try:
                self.assertEqual(resume_check.main(), 1)
            finally:
                resume_check.ROOT, resume_check.RULES = old_root, old_rules


if __name__ == "__main__":
    unittest.main()
