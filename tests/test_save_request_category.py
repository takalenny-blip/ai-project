import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_save_request_category import validate


class SaveRequestCategoryTests(unittest.TestCase):
    def test_template_default_is_valid(self):
        content = (ROOT / "scripts" / "save_request_template.md").read_text(encoding="utf-8")
        ok, message = validate(content)
        self.assertTrue(ok, message)

    def test_missing_category_is_rejected(self):
        ok, message = validate("# 直チャット保存要求\n\n## 本文\nテスト")
        self.assertFalse(ok)
        self.assertIn("保存対象種別 is required", message)

    def test_meta_report_requires_decision(self):
        content = "# 直チャット保存要求\n\n## 保存対象種別\n保存機構メタ報告\n\n## 本文\nテスト"
        ok, message = validate(content)
        self.assertFalse(ok)
        self.assertIn("新しい決定事項", message)


if __name__ == "__main__":
    unittest.main()
