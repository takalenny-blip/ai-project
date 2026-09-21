#!/usr/bin/env python3
import json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_experience_article_material import build_material

class ExperienceArticleMaterialTests(unittest.TestCase):
    def test_collects_exp_and_both_supported_rec_filename_forms(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "EXP-0000000050.md").write_text("# EXP-0000000050\n\n## タイトル\n記事候補\n\n## 内容\n本文の事実\n\n## 得られた知見\n知見A\n", encoding="utf-8")
            (root / "EXP-0000000050_REC-0000000010.md").write_text("# REC-0000000010\n\n## 内容\nREC-A\n\n## 結果\n結果A\n", encoding="utf-8")
            (root / "REC_EXP-0000000050_REC-0000000020.md").write_text("# REC-0000000020\n\n## 内容\nREC-B\n\n## 気づき\n気づきB\n", encoding="utf-8")
            result = build_material(root, "EXP-0000000050")
            self.assertEqual(result["exp_id"], "EXP-0000000050")
            self.assertEqual(result["exp"]["title"], "記事候補")
            self.assertEqual(len(result["recs"]), 2)
            self.assertEqual(result["source"]["rec_paths"], ["EXP-0000000050_REC-0000000010.md", "REC_EXP-0000000050_REC-0000000020.md"])
            self.assertEqual(result["article_material"]["facts"], "本文の事実")
            self.assertEqual(result["article_material"]["insights"], "知見A")

    def test_output_is_json_serializable_and_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "EXP-0000000010.md").write_text("# EXP-0000000010\n\n## タイトル\nT\n\n## 内容\nC\n", encoding="utf-8")
            first = build_material(root, "EXP-0000000010")
            second = build_material(root, "EXP-0000000010")
            self.assertEqual(json.dumps(first, ensure_ascii=False, sort_keys=True), json.dumps(second, ensure_ascii=False, sort_keys=True))

if __name__ == "__main__":
    unittest.main()
