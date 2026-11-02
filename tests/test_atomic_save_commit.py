import unittest
from scripts.check_atomic_save_commit import validate_changed_paths


class DirectChatAtomicCommitTests(unittest.TestCase):
    def setUp(self):
        self.path = "直チャット/2026-11-02_直チャット即時保存_2026-11-02T13-14-15.123456+0900.md"

    def test_accepts_one_new_direct_chat_file_only(self):
        ok, reason = validate_changed_paths([("A", self.path)])
        self.assertTrue(ok, reason)

    def test_rejects_sidecar_files(self):
        ok, _ = validate_changed_paths([("A", self.path), ("M", "README.md")])
        self.assertFalse(ok)

    def test_rejects_modifying_existing_direct_chat(self):
        ok, _ = validate_changed_paths([("M", self.path)])
        self.assertFalse(ok)

    def test_rejects_deleting_existing_direct_chat(self):
        ok, _ = validate_changed_paths([("D", self.path)])
        self.assertFalse(ok)

    def test_non_save_commit_passes(self):
        ok, _ = validate_changed_paths([("M", "rules/運用ルール.md")])
        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
