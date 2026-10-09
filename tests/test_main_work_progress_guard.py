#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from main_work_progress_guard import validate


class MainWorkProgressGuardTests(unittest.TestCase):
    def test_work_branch_requires_substantive_change(self):
        ok, _ = validate("work/state-only", [
            "docs/現在状態.json",
            "BUD.md",
            "docs/引き継ぎ/現在の引き継ぎ.md",
        ])
        self.assertFalse(ok)

    def test_work_branch_accepts_script_change(self):
        ok, _ = validate("work/real-change", [
            "docs/現在状態.json",
            "scripts/dimora_adapter.py",
        ])
        self.assertTrue(ok)

    def test_work_branch_accepts_tests(self):
        ok, _ = validate("work/real-change", ["tests/test_dimora_adapter.py"])
        self.assertTrue(ok)

    def test_work_branch_accepts_japanese_rules_path(self):
        ok, _ = validate("work/blog-publication-roles-20261009", ["rules/運用ルール.md"])
        self.assertTrue(ok)

    def test_quoted_escaped_path_would_not_be_treated_as_real_path(self):
        # changed_paths() must use git diff -z so paths are not returned as
        # Git's quoted/escaped display representation.
        ok, _ = validate("work/blog-publication-roles-20261009", ['"rules/\\351\\201\\213\\347\\224\\250\\343\\203\\253\\343\\203\\274\\343\\203\\253.md"'])
        self.assertFalse(ok)

    def test_fix_branch_requires_substantive_change(self):
        ok, _ = validate("fix/current-state-guard", ["docs/現在状態.json"])
        self.assertFalse(ok)

    def test_fix_branch_accepts_substantive_change(self):
        ok, _ = validate("fix/current-state-guard", ["scripts/main_work_progress_guard.py"])
        self.assertTrue(ok)

    def test_save_request_branch_is_not_blocked(self):
        ok, _ = validate("chat-save-request/20261008-1234", [".github/save-queue/request.md"])
        self.assertTrue(ok)

    def test_save_direct_chat_branch_is_not_blocked(self):
        ok, _ = validate("save/direct-chat-1234", ["20261008_0834.md"])
        self.assertTrue(ok)

    def test_save_currentize_branch_is_not_blocked(self):
        ok, _ = validate("save/currentize-closeout-reconciliation", ["docs/現在状態.json"])
        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
