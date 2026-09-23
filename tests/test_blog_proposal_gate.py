import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from scripts.blog_proposal_gate import check
from scripts.blog_proposal_gate import main as gate_main
from scripts.interaction_preflight import run_preflight

class T(unittest.TestCase):
    def test_pending_blocks_payload(self):
        r=check({"review":{"decision":"pending"}})
        self.assertFalse(r["payload_ready"])
        self.assertIsNotNone(r["blocked_reason"])

    def test_preflight_rejects_blocked_state(self):
        with TemporaryDirectory() as d:
            root=Path(d)
            state=root/"state.json"
            evidence=root/"evidence.json"
            history=root/"history.json"
            state.write_text('{"next_step":{"readiness":"blocked"},"external_response_gate":{"status":"clear"}}', encoding="utf-8")
            evidence.write_text("[]", encoding="utf-8")
            history.write_text("[]", encoding="utf-8")
            with self.assertRaises(ValueError):
                run_preflight(state_path=state,text="完了しました",evidence_path=evidence,history_path=history)

    def test_preflight_accepts_non_claim_text(self):
        with TemporaryDirectory() as d:
            root=Path(d)
            state=root/"state.json"
            evidence=root/"evidence.json"
            history=root/"history.json"
            state.write_text('{"next_step":{"readiness":"ready"},"external_response_gate":{"status":"clear","clear_reason":"test"}}', encoding="utf-8")
            evidence.write_text("[]", encoding="utf-8")
            history.write_text("[]", encoding="utf-8")
            run_preflight(state_path=state,text="提案本文を確認する",evidence_path=evidence,history_path=history)

    def test_approved_allows_payload(self):
        r=check({"review":{"decision":"approved"}})
        self.assertTrue(r["payload_ready"])
        self.assertIsNone(r["blocked_reason"])

if __name__ == "__main__":
    unittest.main()
