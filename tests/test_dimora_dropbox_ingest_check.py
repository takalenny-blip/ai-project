#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


class DimoraDropboxIngestCheckTests(unittest.TestCase):
    def test_reports_record_count_and_ready(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "dimora.json"
            p.write_text(json.dumps([{
                "title": "test", "startDate": "20260924", "endDate": "20260925",
                "bcsNm": "BS", "chNo": "141", "mode": "15倍録"
            }], ensure_ascii=False), encoding="utf-8")
            r = subprocess.run(
                [sys.executable, "scripts/dimora_dropbox_ingest_check.py", str(p)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(r.returncode, 0)
            out = json.loads(r.stdout)
            self.assertEqual(out["record_count"], 1)
            self.assertTrue(out["ready_for_normal_processing"])
            self.assertEqual(len(out["sha256"]), 64)

    def test_missing_required_field_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "dimora.json"
            p.write_text(json.dumps([{"title": "test"}]), encoding="utf-8")
            r = subprocess.run(
                [sys.executable, "scripts/dimora_dropbox_ingest_check.py", str(p)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(r.returncode, 2)
            out = json.loads(r.stdout)
            self.assertFalse(out["ready_for_normal_processing"])
            self.assertIn("startDate", out["required_fields_missing"])


if __name__ == "__main__":
    unittest.main()
