import json, hashlib, tempfile, unittest, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"interaction_preflight.py"

class InteractionPreflightTests(unittest.TestCase):
    def test_requires_history_and_evidence_arguments(self):
        result=subprocess.run([sys.executable,str(SCRIPT),"--rules",str(ROOT/"rules"/"運用ルール.md"),"--text",""],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)

    def test_accepts_complete_preflight_inputs(self):
        with tempfile.TemporaryDirectory() as td:
            tmp=Path(td); evidence_file=tmp/"evidence.txt"; evidence_file.write_text("evidence",encoding="utf-8")
            evidence=tmp/"evidence.json"
            evidence.write_text(json.dumps([{"kind":"test","path":str(evidence_file),"sha256":hashlib.sha256(evidence_file.read_bytes()).hexdigest()}]),encoding="utf-8")
            history=tmp/"history.json"; history.write_text(json.dumps([{"state_fingerprint":"a","progress":False}]),encoding="utf-8")
            result=subprocess.run([sys.executable,str(SCRIPT),"--rules",str(ROOT/"rules"/"運用ルール.md"),"--text","証拠を確認する。","--evidence-json",str(evidence),"--history",str(history)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)

if __name__=="__main__":
    unittest.main()
