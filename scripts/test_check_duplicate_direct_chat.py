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

    def test_detects_source_with_generated_title(self):
        source = "# 会話記録\n\n本文です。\n"
        saved = self.archive / "saved.md"
        saved.write_text("# 直チャット2026-10-22T10-00-00.000000+0900\n\n" + source, encoding="utf-8")
        self.assertEqual(find_duplicate(source, self.archive), saved)

    def test_detects_source_that_has_its_own_title(self):
        source = "# 直チャット手動タイトル\n\n本文です。\n"
        saved = self.archive / "saved.md"
        saved.write_text(source, encoding="utf-8")
        self.assertEqual(find_duplicate(source, self.archive), saved)

    def test_does_not_match_different_content(self):
        source = "# 会話記録\n\n別の本文。\n"
        (self.archive / "saved.md").write_text("# 直チャット2026-10-22T10-00-00.000000+0900\n\n本文です。\n", encoding="utf-8")
        self.assertIsNone(find_duplicate(source, self.archive))

    def test_ignores_retired_embedded_state_patch_when_comparing(self):
        source = "# 会話記録\n\n本文です。\n<!-- BUD_STATE_PATCH_BEGIN\n{\"work_items\": []}\nBUD_STATE_PATCH_END -->\n"
        saved = self.archive / "saved.md"
        saved.write_text("# 直チャット2026-10-22T10-00-00.000000+0900\n\n# 会話記録\n\n本文です。\n", encoding="utf-8")
        self.assertEqual(find_duplicate(source, self.archive), saved)


if __name__ == "__main__":
    unittest.main()
