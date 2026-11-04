from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROGRESS_GATE = ROOT / ".github" / "workflows" / "main-pr-progress-gate.yml"
AUTO_MERGE = ROOT / ".github" / "workflows" / "auto-approve-save-pr.yml"


class SavePrProgressGateWorkflowTests(unittest.TestCase):
    def test_progress_gate_handles_canonical_save_pr_target_events(self):
        workflow = PROGRESS_GATE.read_text(encoding="utf-8")
        self.assertIn("  pull_request_target:", workflow)
        self.assertIn("github.event_name == 'pull_request_target'", workflow)
        self.assertIn("github.event.pull_request.head.repo.full_name == github.repository", workflow)
        self.assertIn("startsWith(github.event.pull_request.head.ref, 'save/direct-chat-')", workflow)

    def test_target_event_checks_trusted_base_without_executing_pr_head(self):
        workflow = PROGRESS_GATE.read_text(encoding="utf-8")
        self.assertIn("ref: ${{ github.event.pull_request.base.sha }}", workflow)
        self.assertIn('git fetch --no-tags origin "$HEAD_SHA"', workflow)
        self.assertIn('git -c core.quotepath=false diff --name-only -z "$BASE_SHA...$HEAD_SHA"', workflow)
        self.assertIn("直チャット/*.md", workflow)
        self.assertNotIn("ref: ${{ github.event.pull_request.head.sha }}", workflow)

    def test_progress_gate_runs_its_own_regression_test(self):
        workflow = PROGRESS_GATE.read_text(encoding="utf-8")
        self.assertIn("test_save_pr_progress_gate_workflow.py", workflow)

    def test_auto_merge_waits_only_for_the_real_progress_gate(self):
        workflow = AUTO_MERGE.read_text(encoding="utf-8")
        self.assertIn('select(.name == "progress-gate")', workflow)
        self.assertNotIn('select(.name == "guard")', workflow)
        self.assertNotIn("guard_ready=", workflow)
        self.assertIn('if [ "$progress_ready" = "missing" ] && [ "$attempt" -ge 24 ]; then', workflow)
        self.assertIn("progress-gate check was not created", workflow)


if __name__ == "__main__":
    unittest.main()
