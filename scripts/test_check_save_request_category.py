import unittest
from pathlib import Path

from scripts.check_save_request_category import prepare_request, validate


TEMPLATE = Path(__file__).with_name("save_request_template.md")


def request(kind="会話記録", body="# 20261030\n\n本文\n", decision=None):
    parts = ["# 直チャット保存要求", "", "## 保存対象種別", kind, ""]
    if decision is not None:
        parts.extend(["## 新しい決定事項", decision, ""])
    parts.extend(["## 本文", "", body])
    return "\n".join(parts)


class SaveRequestCategoryTests(unittest.TestCase):
    def test_template_category_is_valid_and_comment_is_outside_section(self):
        content = TEMPLATE.read_text(encoding="utf-8")
        ok, message = validate(content)
        self.assertTrue(ok, message)

    def test_structured_request_extracts_only_exact_body(self):
        body = "# 20261030-2\n\n**You**\n\n本文\n\n## 内部見出し\n内容\n"
        ok, message, extracted = prepare_request(request(body=body))
        self.assertTrue(ok, message)
        self.assertEqual(extracted, body)
        self.assertNotIn("保存対象種別", extracted)
        self.assertNotIn("直チャット保存要求", extracted)

    def test_legacy_raw_payload_is_preserved_unchanged(self):
        raw = "# 20261030-3\n\n会話本文\n\n"
        ok, message, extracted = prepare_request(raw)
        self.assertTrue(ok, message)
        self.assertEqual(extracted, raw)

    def test_rejects_unknown_category(self):
        ok, message, extracted = prepare_request(request(kind="その他"))
        self.assertFalse(ok)
        self.assertIn("unknown", message)
        self.assertIsNone(extracted)

    def test_rejects_missing_body_section(self):
        raw = "# 直チャット保存要求\n\n## 保存対象種別\n会話記録\n"
        ok, message, extracted = prepare_request(raw)
        self.assertFalse(ok)
        self.assertIn("本文", message)
        self.assertIsNone(extracted)

    def test_rejects_empty_body(self):
        ok, message, extracted = prepare_request(request(body=""))
        self.assertFalse(ok)
        self.assertIn("本文", message)
        self.assertIsNone(extracted)

    def test_rejects_duplicate_body_sections(self):
        raw = request(body="# 本文\n") + "\n## 本文\n\n二つ目\n"
        ok, message, extracted = prepare_request(raw)
        self.assertFalse(ok)
        self.assertIn("exactly one", message)
        self.assertIsNone(extracted)

    def test_meta_report_requires_new_decision(self):
        ok, message, extracted = prepare_request(request(kind="保存機構メタ報告"))
        self.assertFalse(ok)
        self.assertIn("新しい決定事項", message)
        self.assertIsNone(extracted)

    def test_meta_report_with_decision_and_body_is_valid(self):
        body = "# 保存機構の判断記録\n\n本文\n"
        ok, message, extracted = prepare_request(
            request(kind="保存機構メタ報告", decision="新しい停止条件を追加する", body=body)
        )
        self.assertTrue(ok, message)
        self.assertEqual(extracted, body)

    def test_template_is_recognized_and_extracts_only_original_body(self):
        content = TEMPLATE.read_text(encoding="utf-8")
        body = "# 20261030-3\\n\\n会話本文\\n\\n"
        request_content = content.replace("## 本文\\n\\n", "## 本文\\n\\n" + body, 1)
        ok, message, extracted = prepare_request(request_content)
        self.assertTrue(ok, message)
        self.assertEqual(extracted, body)
        self.assertNotIn("保存対象種別", extracted)
        self.assertNotIn("直チャット保存要求", extracted)


if __name__ == "__main__":
    unittest.main()
