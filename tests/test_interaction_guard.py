import hashlib
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import interaction_guard as guard

class InteractionGuardTests(unittest.TestCase):
    def state(self, readiness="ready"):
        return {
            "current_position": {"summary": "current"},
            "next_step": {"readiness": readiness},
            "work_items": [{
                "id": "BLOG-0001",
                "status": "in_progress",
                "readiness": readiness,
                "execution_state": "actionable",
                "progress": {
                    "current_step": "draft",
                    "steps": [
                        {"id": "draft", "status": "in_progress", "title": "本文を編集する"},
                        {"id": "publish", "status": "pending", "title": "公開確認"},
                    ],
                },
            }],
        }

    def test_blocked_rejects_completion_claim(self):
        with self.assertRaises(ValueError):
            guard.validate_blocked_output(self.state("blocked"), "検証しました。")

    def test_blocked_allows_preflight_statement(self):
        guard.validate_blocked_output(self.state("blocked"), "証拠ファイルの存在とSHA-256を確認するpreflightを実施する。")

    def test_ready_claim_requires_evidence(self):
        with self.assertRaises(ValueError):
            guard.validate_evidence_claim("完了しました。", [])

    def test_evidence_hash_is_required_and_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evidence.json"
            path.write_text('{"records": 1}', encoding="utf-8")
            sha = hashlib.sha256(path.read_bytes()).hexdigest()
            guard.validate_evidence_claim(
                "検証しました。",
                [{"kind": "external_artifact", "path": str(path), "sha256": sha}],
            )

    def test_wrong_evidence_hash_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evidence.json"
            path.write_text('{"records": 1}', encoding="utf-8")
            with self.assertRaises(ValueError):
                guard.validate_evidence_claim(
                    "検証しました。",
                    [{"kind": "external_artifact", "path": str(path), "sha256": "0" * 64}],
                )

    def test_loop_stops_after_two_identical_no_progress_states(self):
        state = self.state()
        fp = guard.state_fingerprint(state)
        history = [
            {"state_fingerprint": fp, "progress": False},
            {"state_fingerprint": fp, "progress": False},
        ]
        with self.assertRaises(ValueError):
            guard.validate_loop(history, 2)

    def test_prose_changes_do_not_change_fingerprint(self):
        state1 = self.state()
        state2 = self.state()
        state2["current_position"]["summary"] = "同じ作業について説明を言い換えた"
        state2["next_step"]["target"] = "同じ作業の説明を言い換えた"
        self.assertEqual(guard.state_fingerprint(state1), guard.state_fingerprint(state2))

    def test_work_step_transition_changes_fingerprint(self):
        state1 = self.state()
        state2 = self.state()
        state2["work_items"][0]["progress"]["steps"][0]["status"] = "done"
        state2["work_items"][0]["progress"]["current_step"] = "publish"
        self.assertNotEqual(guard.state_fingerprint(state1), guard.state_fingerprint(state2))

    def test_state_change_resets_loop(self):
        state1 = self.state()
        state2 = self.state()
        state2["work_items"][0]["progress"]["steps"][0]["status"] = "done"
        state2["work_items"][0]["progress"]["current_step"] = "publish"
        history = [
            {"state_fingerprint": guard.state_fingerprint(state1), "progress": False},
            {"state_fingerprint": guard.state_fingerprint(state2), "progress": False},
        ]
        guard.validate_loop(history, 2)

    def test_progress_breaks_loop(self):
        state = self.state()
        fp = guard.state_fingerprint(state)
        history = [
            {"state_fingerprint": fp, "progress": False},
            {"state_fingerprint": fp, "progress": True},
        ]
        guard.validate_loop(history, 2)

if __name__ == "__main__":
    unittest.main()
