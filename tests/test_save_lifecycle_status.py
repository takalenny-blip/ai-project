#!/usr/bin/env python3
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import save_lifecycle_status as mod


class SaveLifecycleStatusTests(unittest.TestCase):
    def test_queue_closed_is_not_failure_when_downstream_save_merged(self):
        result = mod.resolve({"queue_pr":{"number":553,"state":"closed","merged":False},"intake":{"status":"success"},"final_save_pr":{"number":554,"state":"closed","merged":True},"canonical_readback":{"verified":True}})
        self.assertEqual(result.status, "completed")

    def test_queue_closed_without_downstream_save_is_incomplete_after_verified_intake(self):
        result = mod.resolve({"queue_pr":{"number":553,"state":"closed","merged":False},"intake":{"status":"success"}})
        self.assertEqual(result.status, "failed_or_incomplete")

    def test_merged_save_without_readback_is_not_complete(self):
        result = mod.resolve({"queue_pr":{"number":553,"state":"closed","merged":False},"intake":{"status":"success"},"final_save_pr":{"number":554,"state":"closed","merged":True},"canonical_readback":{"verified":False}})
        self.assertEqual(result.status, "merged_readback_pending")

    def test_closed_queue_without_intake_evidence_is_pending_not_failure(self):
        result = mod.resolve({"queue_pr":{"number":553,"state":"closed","merged":False}})
        self.assertEqual(result.status, "submitted_pending")

    def test_intake_failure_is_terminal_failure_when_no_final_save_exists(self):
        result = mod.resolve({"queue_pr":{"number":553,"state":"closed","merged":False},"intake":{"status":"failure"}})
        self.assertEqual(result.status, "failed_or_incomplete")

    def test_intake_success_allows_downstream_final_save_state(self):
        result = mod.resolve({
            "queue_pr":{"number":553,"state":"closed","merged":False},
            "intake":{"status":"success"},
            "final_save_pr":{"number":554,"state":"open","merged":False},
        })
        self.assertEqual(result.status, "final_save_pending")

    def test_open_queue_does_not_hide_existing_final_save_pr(self):
        result = mod.resolve({
            "queue_pr":{"number":963,"state":"open","merged":False},
            "intake":{"status":"success"},
            "final_save_pr":{"number":964,"state":"open","merged":False},
            "canonical_readback":{"verified":False},
        })
        self.assertEqual(result.status, "final_save_pending")
        self.assertEqual(result.final_pr, "964")

    def test_open_queue_does_not_hide_verified_merged_final_save(self):
        result = mod.resolve({
            "queue_pr":{"number":963,"state":"open","merged":False},
            "intake":{"status":"success"},
            "final_save_pr":{"number":964,"state":"closed","merged":True},
            "canonical_readback":{"verified":True},
        })
        self.assertEqual(result.status, "completed")

    def test_intake_failure_does_not_hide_verified_merged_final_save(self):
        result = mod.resolve({
            "queue_pr":{"number":963,"state":"open","merged":False},
            "intake":{"status":"failure"},
            "final_save_pr":{"number":964,"state":"closed","merged":True},
            "canonical_readback":{"verified":True},
        })
        self.assertEqual(result.status, "completed")


if __name__ == "__main__":
    unittest.main()
