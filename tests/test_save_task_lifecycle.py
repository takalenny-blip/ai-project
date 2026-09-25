import unittest
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import save_task_lifecycle as mod

class SaveTaskLifecycleTests(unittest.TestCase):
    def test_delegated_incomplete_child_is_not_parent_failure(self):
        self.assertEqual(mod.resolve(True, [{"status": "in_progress"}]).parent_status, "in_progress")
    def test_blocked_child_is_pending_not_failure(self):
        self.assertEqual(mod.resolve(True, [{"status": "blocked"}]).parent_status, "in_progress")
    def test_dispatch_without_child_outcome_is_not_failure(self):
        self.assertEqual(mod.resolve(True, []).parent_status, "dispatched")
    def test_explicit_child_failure_fails_parent(self):
        self.assertEqual(mod.resolve(True, [{"status": "failed"}]).parent_status, "failed")
    def test_all_children_completed_completes_parent(self):
        self.assertEqual(mod.resolve(True, [{"status": "completed"}, {"status": "completed"}]).parent_status, "completed")

if __name__ == "__main__":
    unittest.main()
