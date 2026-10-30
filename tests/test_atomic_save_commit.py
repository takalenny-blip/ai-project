import json
import unittest

from scripts.check_atomic_save_commit import safe_historical_backfill


class HistoricalDirectChatBackfillTests(unittest.TestCase):
    def setUp(self):
        self.previous_state = json.dumps({
            "direct_chat": {
                "latest_saved": "2026-10-30T18-56-21.005353+0900",
                "latest_path": "直チャット/2026-10-30_直チャット即時保存_2026-10-30T18-56-21.005353+0900.md",
            }
        }, ensure_ascii=False)
        self.path = "直チャット/2026-10-30_直チャット即時保存_2026-10-30T18-54-24.839137+0900.md"

    def test_accepts_new_older_record_without_state_change(self):
        ok, reason = safe_historical_backfill(
            self.path, "A", self.previous_state, self.previous_state, True
        )
        self.assertTrue(ok, reason)
        self.assertIn("pointer remains unchanged", reason)

    def test_rejects_modification_of_existing_record(self):
        ok, _ = safe_historical_backfill(
            self.path, "M", self.previous_state, self.previous_state, True
        )
        self.assertFalse(ok)

    def test_rejects_record_newer_than_current_pointer(self):
        newer = self.path.replace("18-54-24.839137", "18-57-24.839137")
        ok, _ = safe_historical_backfill(
            newer, "A", self.previous_state, self.previous_state, True
        )
        self.assertFalse(ok)

    def test_rejects_any_state_change(self):
        changed = self.previous_state.replace("18-56-21.005353", "18-57-21.005353")
        ok, _ = safe_historical_backfill(
            self.path, "A", self.previous_state, changed, True
        )
        self.assertFalse(ok)

    def test_rejects_missing_current_latest_record(self):
        ok, _ = safe_historical_backfill(
            self.path, "A", self.previous_state, self.previous_state, False
        )
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
