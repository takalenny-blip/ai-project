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

    def test_fix_branch_is_not_blocked(self):
        ok, _ = validate("fix/current-state-guard", ["docs/現在状態.json"])
        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
