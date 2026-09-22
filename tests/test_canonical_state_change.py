#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_canonical_state_change as guard


class CanonicalStateChangeTests(unittest.TestCase):
    def test_state_only_change_fails(self):
        ok, _ = guard.validate_changed_paths(["docs/現在状態.json"])
        self.assertFalse(ok)

    def test_state_with_one_view_fails(self):
        ok, _ = guard.validate_changed_paths(["docs/現在状態.json", "BUD.md"])
        self.assertFalse(ok)

    def test_state_with_both_views_passes(self):
        ok, _ = guard.validate_changed_paths([
            "docs/現在状態.json",
            "BUD.md",
            "docs/引き継ぎ/現在の引き継ぎ.md",
        ])
        self.assertTrue(ok)

    def test_unrelated_change_passes(self):
        ok, _ = guard.validate_changed_paths(["docs/企画/BLOG-0001_Blogger掲載用.html"])
        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
