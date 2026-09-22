#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_blogger_draft_payload import build_blogger_payload


class BloggerDraftPayloadTests(unittest.TestCase):
    def candidate(self):
        return {
            "title": "記事タイトル",
            "intro": "導入 <確認>",
            "body": "本文です。",
            "insights": "知見です。",
            "uncertain_or_notes": "記録上不明",
        }

    def test_builds_title_and_html_content(self):
        payload = build_blogger_payload(self.candidate())
        self.assertEqual(payload["title"], "記事タイトル")
        self.assertIn("<p>導入 &lt;確認&gt;</p>", payload["content"])
        self.assertIn("<h2>本文</h2><p>本文です。</p>", payload["content"])
        self.assertIn("<h2>得られた知見</h2><p>知見です。</p>", payload["content"])
        self.assertIn("<h2>未確定・注意</h2><p>記録上不明</p>", payload["content"])

    def test_rejects_missing_field(self):
        candidate = self.candidate()
        del candidate["insights"]
        with self.assertRaises(ValueError):
            build_blogger_payload(candidate)


if __name__ == "__main__":
    unittest.main()
