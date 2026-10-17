import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from save_and_currentize import merge_patch, validate_queue_retirement
from apply_canonical_state_update import validate_technical_patch


class CanonicalStateUpdateTests(unittest.TestCase):
    def test_merge_patch_recurses_and_replaces_lists(self):
        target = {"a": {"b": 1, "keep": 2}, "items": [1, 2]}
        merge_patch(target, {"a": {"b": 3}, "items": [4]})
        self.assertEqual(target, {"a": {"b": 3, "keep": 2}, "items": [4]})

    def test_technical_patch_rejects_retired_queue_data(self):
        with self.assertRaisesRegex(SystemExit, "work_items updates are retired"):
            validate_technical_patch({"work_items": [{"id": "old"}]}, {})
        with self.assertRaisesRegex(SystemExit, "work_items updates are retired"):
            validate_technical_patch({"current_position": {"summary": "x"}}, {"work_item_updates": [{"id": "old"}]})

    def test_technical_patch_requires_nonempty_object(self):
        with self.assertRaisesRegex(SystemExit, "non-empty technical-state patch"):
            validate_technical_patch({}, {})
        with self.assertRaisesRegex(SystemExit, "patch must be an object"):
            validate_technical_patch([], {})

    def test_save_pipeline_preserves_retirement_marker_without_deriving_queue(self):
        state = {
            "work_queue_source": "dropbox_board",
            "work_items": [],
        }
        sync_next_step(state)

    def test_save_pipeline_rejects_reintroduced_legacy_queue(self):
        state = {
            "work_queue_source": "dropbox_board",
            "work_items": [{"id": "old"}],
        }
        with self.assertRaisesRegex(SystemExit, "work_items must be empty"):
            sync_next_step(state)


if __name__ == "__main__":
    unittest.main()
