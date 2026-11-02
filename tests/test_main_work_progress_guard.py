#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from unittest.mock import patch, Mock
from main_work_progress_guard import changed_paths, validate


class MainWorkProgressGuardTests(unittest.TestCase):
    def test_work_branch_requires_substantive_change(self):
        ok, _ = validate("work/docs-only", ["docs/notes.md"])
        self.assertFalse(ok)

    def test_work_branch_accepts_script_change(self):
        ok, _ = validate("work/real-change", ["scripts/example.py"])
        self.assertTrue(ok)

    def test_work_branch_accepts_tests(self):
        ok, _ = validate("work/real-change", ["tests/test_example.py"])
        self.assertTrue(ok)

    def test_work_branch_accepts_project_document(self):
        ok, _ = validate("work/27-star-wars-readme", ["projects/27_スター・ウォーズ続編再構築/README.md"])
        self.assertTrue(ok)

    def test_work_branch_accepts_japanese_rules_path(self):
        ok, _ = validate("work/rules", ["rules/運用ルール.md"])
        self.assertTrue(ok)

    @patch("main_work_progress_guard.subprocess.run")
    def test_changed_paths_preserves_japanese_filenames(self, run):
        run.return_value = Mock(stdout="rules/運用ルール.md\0docs/notes.md\0")
        paths = changed_paths("origin/main", "HEAD")
        self.assertEqual(paths, ["rules/運用ルール.md", "docs/notes.md"])
        self.assertIn("-z", run.call_args.args[0])

    def test_fix_branch_requires_substantive_change(self):
        ok, _ = validate("fix/docs-only", ["docs/notes.md"])
        self.assertFalse(ok)

    def test_fix_branch_accepts_substantive_change(self):
        ok, _ = validate("fix/entry-docs", ["scripts/check_entry_docs.py"])
        self.assertTrue(ok)

    def test_save_request_branch_is_not_blocked(self):
        ok, _ = validate("chat-save-request/20261008-1234", [".github/save-queue/request.md"])
        self.assertTrue(ok)

    def test_save_direct_chat_branch_is_not_blocked(self):
        ok, _ = validate("save/direct-chat-1234", ["直チャット/2026-10-08_直チャット即時保存_2026-10-08T08-34-00.000000+0900.md"])
        self.assertTrue(ok)

    def test_legacy_save_currentize_branch_is_not_special_cased(self):
        ok, _ = validate("save/currentize-old", ["docs/notes.md"])
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
