#!/usr/bin/env python3
import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,"scripts")
from dimora_change_payload import main
class PayloadTests(unittest.TestCase):
    def test_builds_stable_payload(self):
        with tempfile.TemporaryDirectory() as d:
            src=Path(d)/"changes.json"; out=Path(d)/"payload.json"
            src.write_text(json.dumps({"previous_count":1,"current_count":2,"added_count":1,"changed_count":0,"removed_count":0,"added":[{"title":"追加"}],"changed":[],"removed":[]},ensure_ascii=False),encoding="utf-8")
            old=sys.argv; sys.argv=["x",str(src),"--output",str(out)]
            try: self.assertEqual(main(),0)
            finally: sys.argv=old
            payload=json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema"],"dimora-change-v1")
            self.assertEqual(payload["counts"]["added"],1)
            self.assertEqual(payload["added"][0]["title"],"追加")
if __name__=="__main__": unittest.main()
