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


if __name__ == "__main__":
    unittest.main()
