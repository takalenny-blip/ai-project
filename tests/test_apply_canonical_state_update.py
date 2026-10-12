import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from save_and_currentize import merge_patch

class CanonicalStateUpdateTests(unittest.TestCase):
    def test_merge_patch_recurses_and_replaces_lists(self):
        target = {"a": {"b": 1, "keep": 2}, "items": [1, 2]}
        merge_patch(target, {"a": {"b": 3}, "items": [4]})
        self.assertEqual(target, {"a": {"b": 3, "keep": 2}, "items": [4]})

if __name__ == "__main__":
    unittest.main()
