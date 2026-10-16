import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from generate_current_views import render
from work_queue import select_actionable


class ActionableProgressHandoffTests(unittest.TestCase):
    def test_actionable_work_view_exposes_only_unfinished_substeps(self):
        state = json.loads((ROOT / "docs" / "現在状態.json").read_text(encoding="utf-8"))
        state["work_queue_source"] = "github_json"
        bud, handover = render(state)
        actionable = select_actionable(state["work_items"], state.get("updated"))

        self.assertTrue(actionable, "fixture must include actionable work")
        for view in (bud, handover):
            for item in actionable:
                for step in item["progress"]["steps"]:
                    rendered_step = f"{step['id']} [{step['status']}] {step['title']}"
                    if step["status"] == "done":
                        self.assertNotIn(
                            rendered_step,
                            view,
                            f"completed step must not be listed as unfinished: {rendered_step}",
                        )
                    else:
                        self.assertIn(
                            rendered_step,
                            view,
                            f"unfinished actionable step must remain visible: {rendered_step}",
                        )


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
