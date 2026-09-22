#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_experience_article_ai_prompt import build_prompt

class ExperienceArticleAiPromptTests(unittest.TestCase):
    def test_prompt_keeps_source_material_and_forbids_invention(self):
        material = {
            "schema_version": 1,
            "exp_id": "EXP-0000000050",
            "source": {"exp_path": "経験ログ/EXP-0000000050.md", "rec_paths": []},
            "exp": {"title": "記事候補", "sections": {"タイトル": "記事候補"}},
            "recs": [],
            "article_material": {"facts": "本文の事実", "result": "結果A", "insights": "知見A"},
        }
        prompt = build_prompt(material)
        self.assertIn("本文の事実", prompt)
        self.assertIn("結果A", prompt)
        self.assertIn("知見A", prompt)
        self.assertIn("推測せず「記録上不明」", prompt)
        self.assertIn("本人の発言を作らない", prompt)
        self.assertIn("Bloggerへの投稿、公開、認証、外部通信は行わない", prompt)

    def test_rejects_unknown_schema(self):
        with self.assertRaises(ValueError):
            build_prompt({"schema_version": 99})

if __name__ == "__main__":
    unittest.main()
