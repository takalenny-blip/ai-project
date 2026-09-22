#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_experience_article_candidate import validate_candidate

class ExperienceArticleCandidateGroundingTests(unittest.TestCase):
    def setUp(self):
        self.material = {
            "schema_version": 1,
            "source": {"exp_path": "経験ログ/EXP-0000000050.md"},
            "exp": {"sections": {"内容": "本人の評価と判断を残す"}},
            "recs": [{"source_path": "EXP-0000000050_REC-0000000020.md",
                      "sections": {"得られた知見": "trigger → required action → completion → verification"}}],
        }

    def candidate(self, evidence="本人の評価と判断を残す"):
        return {
            "title": "経験DBに評価・判断も残す",
            "intro": "記録を記事候補へ編集する。",
            "body": "本人の評価と判断を残す。",
            "insights": "運用ルールを検証可能にする。",
            "uncertain_or_notes": "記録上不明",
            "grounding": [{"source_path": "経験ログ/EXP-0000000050.md", "evidence": evidence}],
        }

    def test_accepts_exact_source_evidence(self):
        self.assertEqual(validate_candidate(self.material, self.candidate()), [])

    def test_rejects_unknown_source(self):
        candidate = self.candidate()
        candidate["grounding"][0]["source_path"] = "unknown.md"
        self.assertTrue(any("unknown source_path" in error for error in validate_candidate(self.material, candidate)))

    def test_rejects_non_source_evidence(self):
        candidate = self.candidate("記録にない主張")
        self.assertTrue(any("exact substring" in error for error in validate_candidate(self.material, candidate)))

    def test_rejects_missing_grounding(self):
        candidate = self.candidate()
        candidate["grounding"] = []
        self.assertTrue(any("non-empty list" in error for error in validate_candidate(self.material, candidate)))

if __name__ == "__main__":
    unittest.main()
