#!/usr/bin/env python3
import json
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from dimora_json_normalizer import load_records, normalize


class DimoraJsonNormalizerTests(unittest.TestCase):
    def sample(self):
        return {
            "eventId": "3068",
            "mindsProgramId": "997701",
            "title": "アニメ　株式会社マジルミエ 第2期　第11話　諦めのある仕事など無価値です",
            "startDate": "202609240100",
            "endDate": "202609240130",
            "bcsNm": "BS日テレ",
            "chNo": "141",
            "mode": "15倍録",
            "requestId": "26848326400",
            "recTimerState": "1",
            "length": "30",
            "status": "10",
            "genre": "アニメ/特撮",
            "extra": "ignored",
        }

    def test_normalizes_exported_array(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "dimora.json"
            path.write_text(json.dumps([self.sample()], ensure_ascii=False), encoding="utf-8")
            records = load_records(path)
            result = normalize(records)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], self.sample()["title"])
        self.assertEqual(result[0]["requestId"], "26848326400")
        self.assertNotIn("extra", result[0])

    def test_accepts_record_wrapper(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "dimora.json"
            path.write_text(json.dumps({"record": [self.sample()]}, ensure_ascii=False), encoding="utf-8")
            self.assertEqual(load_records(path)[0]["eventId"], "3068")

    def test_rejects_invalid_input(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "dimora.json"
            path.write_text(json.dumps({"records": []}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_records(path)


if __name__ == "__main__":
    unittest.main()
