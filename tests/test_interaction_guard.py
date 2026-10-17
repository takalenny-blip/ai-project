import hashlib
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import interaction_guard as guard


class InteractionGuardTests(unittest.TestCase):
    def test_progress_claim_requires_explicit_evidence(self):
        with self.assertRaisesRegex(ValueError, "requires explicit evidence"):
            guard.validate_evidence_claim("検証しました。", [])

    def test_progress_claim_accepts_matching_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "evidence.txt"
            path.write_text("verified evidence", encoding="utf-8")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            guard.validate_evidence_claim("検証しました。", [{"kind": "file", "path": str(path), "sha256": digest}])

    def test_evidence_sha_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "evidence.txt"
            path.write_text("evidence", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                guard.validate_evidence_claim("完了しました。", [{"kind": "file", "path": str(path), "sha256": "0" * 64}])

    def test_loop_stops_on_repeated_external_state_fingerprint(self):
        history = [{"state_fingerprint": "dropbox-sha-1"}, {"state_fingerprint": "dropbox-sha-1"}]
        with self.assertRaisesRegex(ValueError, "forced stop"):
            guard.validate_loop(history, 2)

    def test_loop_allows_changed_external_state_fingerprint(self):
        history = [{"state_fingerprint": "dropbox-sha-1"}, {"state_fingerprint": "dropbox-sha-2"}]
        guard.validate_loop(history, 2)

    def test_loop_ignores_caller_progress_boolean(self):
        history = [{"state_fingerprint": "same", "progress": False}, {"state_fingerprint": "same", "progress": True}]
        with self.assertRaisesRegex(ValueError, "forced stop"):
            guard.validate_loop(history, 2)

    def test_loop_threshold_must_be_at_least_two(self):
        with self.assertRaisesRegex(ValueError, "threshold must be >= 2"):
            guard.validate_loop([], 1)


if __name__ == "__main__":
    unittest.main()
