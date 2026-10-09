import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from generate_current_views import render


class ActionableProgressHandoffTests(unittest.TestCase):
    def test_actionable_work_view_exposes_unfinished_substeps(self):
        state = json.loads((ROOT / "docs" / "現在状態.json").read_text(encoding="utf-8"))
        bud, handover = render(state)
        for view in (bud, handover):
            self.assertIn("wp-design-template [pending] WordPressのデザインテンプレートを整える", view)
            self.assertIn("wp-icon [in_progress] WordPressへサイトアイコン画像を適用して実表示を確認する", view)
            self.assertIn("blog1-image [pending] BLOG-0001の画像問題を解消", view)
            self.assertNotIn("次の一手（互換ビュー）", view)

    def test_canonical_state_does_not_duplicate_selected_work_item(self):
        state = json.loads((ROOT / "docs" / "現在状態.json").read_text(encoding="utf-8"))
        self.assertNotIn("next_step", state)
        self.assertTrue(state["work_items"])
        self.assertTrue(all(item["progress"].get("current_step") for item in state["work_items"]))


if __name__ == "__main__":
    unittest.main()
