import tempfile
import unittest
from pathlib import Path

from scripts.check_duplicate_direct_chat import find_duplicate


class DuplicateDirectChatTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.archive = self.root / "直チャット"
        self.archive.mkdir()

    def test_detects_legacy_generated_title_without_changing_body(self):
        source = "# 会話記録\n\n本文です。\n"
        saved = self.archive / "saved.md"
        saved.write_text("# 直チャット2026-10-22T10-00-00.000000+0900\n\n" + source, encoding="utf-8")
        self.assertEqual(find_duplicate(source, self.archive), saved)

    def test_detects_exact_original_with_own_title(self):
        source = "# 直チャット手動タイトル\n\n本文です。\n"
        saved = self.archive / "saved.md"
        saved.write_text(source, encoding="utf-8")
        self.assertEqual(find_duplicate(source, self.archive), saved)

    def test_does_not_match_different_content(self):
        source = "# 会話記録\n\n別の本文。\n"
        (self.archive / "saved.md").write_text("# 会話記録\n\n本文です。\n", encoding="utf-8")
        self.assertIsNone(find_duplicate(source, self.archive))

    def test_different_legacy_state_patch_is_not_treated_as_duplicate(self):
        source = "# 会話記録\n\n本文です。\n<!-- BUD_STATE_PATCH_BEGIN\n{\"work_items\": [1]}\nBUD_STATE_PATCH_END -->\n"
        saved = self.archive / "saved.md"
        saved.write_text("# 会話記録\n\n本文です。\n<!-- BUD_STATE_PATCH_BEGIN\n{\"work_items\": [2]}\nBUD_STATE_PATCH_END -->\n", encoding="utf-8")
        self.assertIsNone(find_duplicate(source, self.archive))

    def test_exact_legacy_state_patch_is_duplicate(self):
        source = "# 会話記録\n\n本文です。\n<!-- BUD_STATE_PATCH_BEGIN\n{\"work_items\": [1]}\nBUD_STATE_PATCH_END -->\n"
        saved = self.archive / "saved.md"
        saved.write_text(source, encoding="utf-8")
        self.assertEqual(find_duplicate(source, self.archive), saved)

    def test_preserves_whitespace_and_crlf_for_exact_comparison(self):
        source = "  original\r\n本文  \r\n"
        saved = self.archive / "saved.md"
        with saved.open("w", encoding="utf-8", newline="") as stream:
            stream.write(source)
        self.assertEqual(find_duplicate(source, self.archive), saved)
        self.assertIsNone(find_duplicate(source.strip(), self.archive))


if __name__ == "__main__":
    unittest.main()
