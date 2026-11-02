import tempfile
import unittest
from pathlib import Path

from scripts.save_direct_chat import write_original


class SaveDirectChatTests(unittest.TestCase):
    def test_writes_original_text_exactly_including_legacy_state_block(self):
        content = (
            "  original leading whitespace\n"
            "<!-- BUD_STATE_PATCH_BEGIN\n"
            "legacy embedded data that must not be applied\n"
            "BUD_STATE_PATCH_END -->\n"
            "original trailing text  \n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "direct-chat.md"
            write_original(target, content)
            self.assertEqual(target.read_text(encoding="utf-8"), content)

    def test_refuses_to_overwrite_existing_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "direct-chat.md"
            target.write_text("existing original", encoding="utf-8")
            with self.assertRaisesRegex(FileExistsError, "refusing to overwrite"):
                write_original(target, "replacement")
            self.assertEqual(target.read_text(encoding="utf-8"), "existing original")


if __name__ == "__main__":
    unittest.main()
