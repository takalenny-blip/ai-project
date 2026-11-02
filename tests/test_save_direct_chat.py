import tempfile
import unittest
from pathlib import Path

from scripts.save_direct_chat import write_original

class SaveDirectChatTests(unittest.TestCase):
    def test_writes_original_text_exactly_including_legacy_state_block_and_crlf(self):
        content = "  original leading whitespace\r\n<!-- BUD_STATE_PATCH_BEGIN\r\nlegacy embedded data\r\nBUD_STATE_PATCH_END -->\r\ntrailing text  \r\n"
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "direct-chat.md"
            write_original(target, content)
            with target.open("r", encoding="utf-8", newline="") as stream:
                self.assertEqual(stream.read(), content)

    def test_refuses_to_overwrite_existing_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "direct-chat.md"
            target.write_text("existing original", encoding="utf-8")
            with self.assertRaisesRegex(FileExistsError, "refusing to overwrite"):
                write_original(target, "replacement")
            self.assertEqual(target.read_text(encoding="utf-8"), "existing original")

if __name__ == "__main__":
    unittest.main()