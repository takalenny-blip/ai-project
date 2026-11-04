from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROGRESS_GATE = ROOT / ".github" / "workflows" / "main-pr-progress-gate.yml"
AUTO_MERGE = ROOT / ".github" / "workflows" / "auto-approve-save-pr.yml"


class SavePrProgressGateWorkflowTests(unittest.TestCase):
    def test_target_event_has_a_distinct_required_check_name(self):
        workflow = PROGRESS_GATE.read_text(encoding="utf-8")
        self.assertIn("name: ${{ github.event_name == 'pull_request_target' && 'progress-gate-target' || 'progress-gate' }}", workflow)

    def test_progress_gate_handles_canonical_save_pr_target_events(self):
        workflow = PROGRESS_GATE.read_text(encoding="utf-8")
        self.assertIn("  pull_request_target:", workflow)
        self.assertIn("github.event_name == 'pull_request_target'", workflow)
        self.assertIn("github.event.pull_request.head.repo.full_name == github.repository", workflow)
        self.assertIn("startsWith(github.event.pull_request.head.ref, 'save/direct-chat-')", workflow)

    def test_target_event_checks_current_trusted_base_without_executing_pr_head(self):
        workflow = PROGRESS_GATE.read_text(encoding="utf-8")
        self.assertIn("ref: ${{ github.event.pull_request.base.ref }}", workflow)
        self.assertIn('echo "TRUSTED_BASE_SHA=$(git rev-parse HEAD)" >> "$GITHUB_ENV"', workflow)
        self.assertIn('git fetch --no-tags origin "$HEAD_SHA"', workflow)
        self.assertIn('git -c core.quotepath=false diff --name-only -z "$BASE_SHA...$HEAD_SHA"', workflow)
        self.assertIn("直チャット/*.md", workflow)
        self.assertNotIn("ref: ${{ github.event.pull_request.head.sha }}", workflow)

    def test_progress_gate_runs_its_own_regression_test(self):
        workflow = PROGRESS_GATE.read_text(encoding="utf-8")
        self.assertIn("test_save_pr_progress_gate_workflow.py", workflow)

    def test_auto_merge_uses_latest_exact_head_target_check_only(self):
        workflow = AUTO_MERGE.read_text(encoding="utf-8")
        self.assertIn('commits/${HEAD_SHA}/check-runs?per_page=100', workflow)
        self.assertIn('select(.name == "progress-gate-target")', workflow)
        self.assertIn('sort_by(.started_at // .created_at) | last', workflow)
        self.assertIn('elif .conclusion == "success" then "pass"', workflow)
        self.assertNotIn('gh pr checks "$PR_URL"', workflow)
        self.assertNotIn('select(.name != "approve-and-merge")', workflow)
        self.assertNotIn('select(.name == "guard")', workflow)
        self.assertNotIn("guard_ready=", workflow)
        self.assertIn('if [ "$progress_ready" = "missing" ] && [ "$attempt" -ge 24 ]; then', workflow)
        self.assertIn("No progress-gate-target check run was found for this exact HEAD", workflow)


if __name__ == "__main__":
    unittest.main()
