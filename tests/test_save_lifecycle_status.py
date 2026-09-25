#!/usr/bin/env python3
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import save_lifecycle_status as mod


class SaveLifecycleStatusTests(unittest.TestCase):
    def test_queue_closed_is_not_failure_when_downstream_save_merged(self):
        result = mod.resolve({"queue_pr":{"number":553,"state":"closed","merged":False},"final_save_pr":{"number":554,"state":"closed","merged":True},"canonical_readback":{"verified":True}})
        self.assertEqual(result.status, "completed")

    def test_queue_closed_without_downstream_save_is_incomplete(self):
        result = mod.resolve({"queue_pr":{"number":553,"state":"closed","merged":False}})
        self.assertEqual(result.status, "failed_or_incomplete")

    def test_merged_save_without_readback_is_not_complete(self):
        result = mod.resolve({"queue_pr":{"number":553,"state":"closed","merged":False},"final_save_pr":{"number":554,"state":"closed","merged":True},"canonical_readback":{"verified":False}})
        self.assertEqual(result.status, "merged_readback_pending")

    def test_closed_queue_without_intake_evidence_is_pending_not_failure(self):
        result = mod.resolve({"queue_pr":{"number":553,"state":"closed","merged":False}})
        self.assertEqual(result.status, "submitted_pending")

    def test_intake_failure_is_terminal_failure(self):
        result = mod.resolve({"queue_pr":{"number":553,"state":"closed","merged":False},"intake":{"status":"failure"}})
        self.assertEqual(result.status, "failed_or_incomplete")

    def test_intake_success_allows_downstream_final_save_state(self):
        result = mod.resolve({
            "queue_pr":{"number":553,"state":"closed","merged":False},
            "intake":{"status":"success"},
            "final_save_pr":{"number":554,"state":"open","merged":False},
        })
        self.assertEqual(result.status, "final_save_pending")


if __name__ == "__main__":
    unittest.main()
