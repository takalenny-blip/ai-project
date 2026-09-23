#!/usr/bin/env python3
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_blogger_draft_payload import build_blogger_payload

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_blogger_draft_payload.py"


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

    def test_cli_requires_and_runs_interaction_preflight(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            candidate = tmp / "candidate.json"
            candidate.write_text(json.dumps(self.candidate(), ensure_ascii=False), encoding="utf-8")
            evidence_file = tmp / "evidence.txt"
            evidence_file.write_text("evidence", encoding="utf-8")
            evidence = tmp / "evidence.json"
            evidence.write_text(json.dumps([{
                "kind": "test",
                "path": str(evidence_file),
                "sha256": hashlib.sha256(evidence_file.read_bytes()).hexdigest(),
            }]), encoding="utf-8")
            state = tmp / "state.json"
            state.write_text(json.dumps({"next_step": {"readiness": "ready"}, "current_position": {}}), encoding="utf-8")
            history = tmp / "history.json"
            history.write_text(json.dumps([{"state_fingerprint": "a", "progress": False}]), encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPT), "--candidate", str(candidate), "--state", str(state), "--text", "確認しました。", "--evidence-json", str(evidence), "--history", str(history)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('"title": "記事タイトル"', result.stdout)

    def test_cli_stops_when_interaction_preflight_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            candidate = tmp / "candidate.json"
            candidate.write_text(json.dumps(self.candidate(), ensure_ascii=False), encoding="utf-8")
            evidence = tmp / "evidence.json"
            evidence.write_text("[]", encoding="utf-8")
            state = tmp / "state.json"
            state.write_text(json.dumps({"next_step": {"readiness": "blocked"}, "current_position": {}}), encoding="utf-8")
            history = tmp / "history.json"
            history.write_text(json.dumps([{"state_fingerprint": "a", "progress": False}]), encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPT), "--candidate", str(candidate), "--state", str(state), "--text", "証拠を確認しました。", "--evidence-json", str(evidence), "--history", str(history)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("interaction preflight failed", result.stderr)
    def test_rejects_missing_field(self):
        candidate = self.candidate()
        del candidate["insights"]
        with self.assertRaises(ValueError):
            build_blogger_payload(candidate)


if __name__ == "__main__":
    unittest.main()
