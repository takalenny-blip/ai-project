import unittest

from scripts.check_direct_chat_immutability import parse_name_status_z, violations


class DirectChatImmutabilityTests(unittest.TestCase):
    def test_new_direct_chat_is_allowed(self):
        self.assertEqual(violations([("A", ("直チャット/2026-10-16_chat.md",))]), [])

    def test_modification_is_rejected(self):
        self.assertEqual(
            violations([("M", ("直チャット/2026-10-16_chat.md",))]),
            ["M: 直チャット/2026-10-16_chat.md"],
        )

    def test_deletion_is_rejected(self):
        self.assertEqual(
            violations([("D", ("直チャット/old.md",))]),
            ["D: 直チャット/old.md"],
        )

    def test_rename_from_protected_folder_is_rejected(self):
        self.assertEqual(
            violations([("R100", ("直チャット/old.md", "archive/old.md"))]),
            ["R100: 直チャット/old.md"],
        )

    def test_rename_into_protected_folder_is_rejected(self):
        self.assertEqual(
            violations([("R100", ("archive/old.md", "直チャット/new.md"))]),
            ["R100: 直チャット/new.md"],
        )

    def test_unrelated_changes_are_ignored(self):
        self.assertEqual(violations([("M", ("README.md",)), ("A", ("docs/new.md",))]), [])

    def test_name_status_z_parses_rename_records(self):
        self.assertEqual(
            parse_name_status_z(b"R100\0\xe7\x9b\xb4\xe3\x83\x81\xe3\x83\xa3\xe3\x83\x83\xe3\x83\x88/old.md\0archive/old.md\0"),
            [("R100", ("直チャット/old.md", "archive/old.md"))],
        )


if __name__ == "__main__":
    unittest.main()
