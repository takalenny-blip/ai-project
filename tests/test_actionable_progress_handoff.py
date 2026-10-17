import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from generate_current_views import render


class ActionableProgressHandoffTests(unittest.TestCase):
    def test_legacy_github_queue_source_is_rejected(self):
        state = json.loads((ROOT / "docs" / "現在状態.json").read_text(encoding="utf-8"))
        state["work_queue_source"] = "github_json"
        with self.assertRaises(ValueError):
            render(state)

    def test_retired_work_items_field_is_rejected_even_when_empty(self):
        state = json.loads((ROOT / "docs" / "現在状態.json").read_text(encoding="utf-8"))
        state["work_items"] = []
        with self.assertRaisesRegex(ValueError, "legacy work_items field is retired"):
            render(state)

    def test_retired_next_step_field_is_rejected(self):
        state = json.loads((ROOT / "docs" / "現在状態.json").read_text(encoding="utf-8"))
        state["next_step"] = {"target": "old queue"}
        with self.assertRaisesRegex(ValueError, "legacy next_step field is retired"):
            render(state)

    def test_dropbox_queue_view_never_renders_legacy_items(self):
        state = json.loads((ROOT / "docs" / "現在状態.json").read_text(encoding="utf-8"))
        state["work_queue_source"] = "dropbox_board"
        bud, handover = render(state)
        for view in (bud, handover):
            self.assertIn("Dropboxの固定ファイル /ChatGPT/Dropbox作業管理統合ボード.xlsx", view)
            self.assertIn("古いGitHub項目へフォールバックしない", view)
            self.assertNotIn("actionable：", view)
            self.assertNotIn("validation-findings-follow-up [in_progress]", view)

if __name__ == "__main__":
    unittest.main()
