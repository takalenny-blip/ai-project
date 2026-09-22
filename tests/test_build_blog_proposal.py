import json,unittest
from scripts.build_blog_proposal import build_proposal
class T(unittest.TestCase):
 def setUp(self): self.c={"title":"タイトル","intro":"導入","body":"本文","insights":"知見","uncertain_or_notes":"注意","grounding":[{"source_path":"EXP.md","evidence":"根拠"}]}
 def test_draft(self):
  p=build_proposal(self.c); self.assertEqual(p["status"],"draft"); self.assertTrue(p["review"]["required"]); self.assertEqual(p["review"]["decision"],"pending"); self.assertFalse(p["publication"]["published"])
 def test_missing(self):
  c=dict(self.c); del c["body"]
  with self.assertRaises(ValueError): build_proposal(c)
 def test_real(self):
  c=json.loads(open("tests/fixtures/experience_article_candidate_EXP-0000000050.json",encoding="utf-8").read()); p=build_proposal(c)
  self.assertEqual(p["proposal"]["title"],c["title"]); self.assertEqual(len(p["grounding"]),4)
if __name__=="__main__": unittest.main()
