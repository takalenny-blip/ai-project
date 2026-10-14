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
    def test_keyed_update_changes_only_matching_item_and_preserves_order(self):
        from apply_canonical_state_update import apply_work_item_updates
        state = {"work_items": [{"id": "one", "status": "pending", "progress": {"steps": ["a", "b"]}}, {"id": "two", "status": "in_progress", "note": "keep"}, {"id": "three", "status": "queued"}]}
        untouched = [dict(state["work_items"][1]), dict(state["work_items"][2])]
        apply_work_item_updates(state, [{"id": "one", "patch": {"status": "done", "progress": {"current": "next"}}}])
        self.assertEqual([item["id"] for item in state["work_items"]], ["one", "two", "three"])
        self.assertEqual(state["work_items"][0], {"id": "one", "status": "done", "progress": {"steps": ["a", "b"], "current": "next"}})
        self.assertEqual(state["work_items"][1:], untouched)

    def test_keyed_update_rejects_missing_and_duplicate_target_ids(self):
        from apply_canonical_state_update import apply_work_item_updates
        with self.assertRaisesRegex(SystemExit, "not found"):
            apply_work_item_updates({"work_items": [{"id": "one"}]}, [{"id": "missing", "patch": {"status": "done"}}])
        with self.assertRaisesRegex(SystemExit, "is not unique"):
            apply_work_item_updates({"work_items": [{"id": "one"}, {"id": "one"}]}, [{"id": "one", "patch": {"status": "done"}}])

    def test_keyed_update_rejects_duplicate_requests_and_id_mutation(self):
        from apply_canonical_state_update import apply_work_item_updates
        state = {"work_items": [{"id": "one", "status": "pending"}]}
        with self.assertRaisesRegex(SystemExit, "duplicate work_item_update id"):
            apply_work_item_updates(state, [{"id": "one", "patch": {"status": "done"}}, {"id": "one", "patch": {"status": "pending"}}])
        with self.assertRaisesRegex(SystemExit, "may not change id"):
            apply_work_item_updates(state, [{"id": "one", "patch": {"id": "two"}}])

    def test_keyed_update_rejects_invalid_request_shape_and_empty_patch(self):
        from apply_canonical_state_update import apply_work_item_updates
        state = {"work_items": [{"id": "one"}]}
        with self.assertRaisesRegex(SystemExit, "exactly id and patch"):
            apply_work_item_updates(state, [{"id": "one", "patch": {"status": "done"}, "extra": True}])
        with self.assertRaisesRegex(SystemExit, "non-empty object"):
            apply_work_item_updates(state, [{"id": "one", "patch": {}}])

if __name__ == "__main__":
    unittest.main()
