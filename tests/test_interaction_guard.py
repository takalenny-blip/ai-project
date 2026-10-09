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
            "updated": "2026-10-08",
            "work_items": [{
                "id": "WORK-TEST", "title": "test", "priority": 10, "status": "queued",
                "depends_on": [], "not_before": None, "scope": "experience_log_to_blogger",
                "target": "経験ログを中心としたAI編集・Blogger自動化へ戻る", "evidence": "test",
                "readiness": readiness, "unblock_action": "preflight", "environment": "work_pc",
                "execution_state": "actionable", "created_at": "2026-10-08", "updated_at": "2026-10-08",
                "blocked_reason": "external wait" if readiness == "blocked" else None,
                "progress": {"current_step": "step-1", "steps": [{"id": "step-1", "title": "test", "status": "pending"}], "updated_at": "2026-10-08"},
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

    def test_state_change_resets_loop(self):
        state1 = self.state()
        state2 = self.state()
        state2["work_items"][0]["target"] = "別の具体的作業"
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
