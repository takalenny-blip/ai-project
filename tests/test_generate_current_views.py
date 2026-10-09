import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from generate_current_views import check_committed_views


class CheckCommittedViewsTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        (self.root / "docs" / "引き継ぎ").mkdir(parents=True)
        (self.root / "BUD.md").write_text("BUD rendered", encoding="utf-8")
        (self.root / "docs" / "引き継ぎ" / "現在の引き継ぎ.md").write_text(
            "handover rendered", encoding="utf-8"
        )

    def tearDown(self):
        self.tempdir.cleanup()

    def test_matching_committed_views_pass(self):
        ok, message = check_committed_views("BUD rendered", "handover rendered", self.root)
        self.assertTrue(ok, message)

    def test_stale_committed_view_fails(self):
        ok, message = check_committed_views("BUD rendered", "outdated handover", self.root)
        self.assertFalse(ok)
        self.assertIn("differs", message)

    def test_missing_committed_view_fails(self):
        (self.root / "BUD.md").unlink()
        ok, message = check_committed_views("BUD rendered", "handover rendered", self.root)
        self.assertFalse(ok)
        self.assertIn("missing", message)


if __name__ == "__main__":
    unittest.main()
