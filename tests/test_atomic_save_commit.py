import unittest
from scripts.check_atomic_save_commit import validate_changed_paths

class AtomicDirectChatSaveTests(unittest.TestCase):
    def test_accepts_one_new_direct_chat_and_rules(self):
        ok, reason = validate_changed_paths([
            "直チャット/2026-11-02_直チャット即時保存_2026-11-02T12-00-00.123456+0900.md",
            "rules/運用ルール.md",
        ])
        self.assertTrue(ok, reason)
        self.assertIn("atomic direct-chat", reason)

    def test_rejects_direct_chat_without_rules_pointer(self):
        ok, _ = validate_changed_paths(["直チャット/new.md"])
        self.assertFalse(ok)

    def test_rejects_multiple_direct_chat_files(self):
        ok, _ = validate_changed_paths(["直チャット/a.md", "直チャット/b.md", "rules/運用ルール.md"])
        self.assertFalse(ok)

    def test_allows_non_save_commits(self):
        ok, _ = validate_changed_paths(["scripts/example.py"])
        self.assertTrue(ok)

    def test_rejects_extra_legacy_files_in_save_commit(self):
        ok, _ = validate_changed_paths(["直チャット/new.md", "rules/運用ルール.md", "docs/現在状態.json"])
        self.assertFalse(ok)

if __name__ == "__main__":
    unittest.main()
