#!/usr/bin/env python3
import json
import os
import tempfile
import unittest
import zipfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import resume_check


class ResumeCheckDropboxOnlyTests(unittest.TestCase):
    def write_state(self, root):
        state = {
            "execution_environment": {"active": "work_pc", "retired": ["vaio_p"]},
            "current_position": {"summary": "technical state preserved"},
            "work_queue_source": "dropbox_board",
            "work_items": [],
            "interaction_control": {
                "status": "implemented_preflight",
                "guard_script": "scripts/interaction_guard.py",
                "loop_detection": {"threshold": 2, "action": "強制停止して人間判断へ戻す"},
                "blocked_output": {"exit_code": 2},
            },
            "resume_manifest": {
                "source": "docs/現在状態.json",
                "generator": "scripts/resume_manifest.py",
            },
            "external_response_gate": {
                "status": "clear",
                "clear_reason": "no pending external proposal",
                "reaction_contract": {
                    "required_fields": ["proposal", "judgment", "reason", "next_action", "consistency"],
                    "judgment_values": ["adopt", "adopt_modified", "hold", "reject", "info_only"],
                    "rule": "all five required",
                    "clear_condition": "all five valid",
                },
            },
            "work_pc": {"clone_status": "unverified"},
        }
        (root / "docs").mkdir(exist_ok=True)
        path = root / "docs" / "現在状態.json"
        path.write_text(json.dumps(state), encoding="utf-8")
        return path

    def write_xlsx(self, path):
        with zipfile.ZipFile(path, "w") as workbook:
            workbook.writestr("[Content_Types].xml", "<Types></Types>")
            workbook.writestr("xl/workbook.xml", "<workbook></workbook>")

    def run_check(self, root, state_path):
        old_state, old_root = resume_check.STATE, resume_check.ROOT
        old_board = os.environ.get("DROPBOX_WORK_QUEUE_PATH")
        old_remote = os.environ.get("DROPBOX_REQUIRE_REMOTE")
        old_token = os.environ.get("DROPBOX_ACCESS_TOKEN")
        resume_check.STATE, resume_check.ROOT = state_path, root
        os.environ["DROPBOX_WORK_QUEUE_PATH"] = str(root / "Dropbox作業管理統合ボード.xlsx")
        os.environ.pop("DROPBOX_REQUIRE_REMOTE", None)
        os.environ.pop("DROPBOX_ACCESS_TOKEN", None)
        try:
            return resume_check.main()
        finally:
            resume_check.STATE, resume_check.ROOT = old_state, old_root
            if old_board is None:
                os.environ.pop("DROPBOX_WORK_QUEUE_PATH", None)
            else:
                os.environ["DROPBOX_WORK_QUEUE_PATH"] = old_board
            if old_remote is None:
                os.environ.pop("DROPBOX_REQUIRE_REMOTE", None)
            else:
                os.environ["DROPBOX_REQUIRE_REMOTE"] = old_remote
            if old_token is None:
                os.environ.pop("DROPBOX_ACCESS_TOKEN", None)
            else:
                os.environ["DROPBOX_ACCESS_TOKEN"] = old_token

    def test_valid_state_and_readable_board_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            state = self.write_state(root)
            self.write_xlsx(root / "Dropbox作業管理統合ボード.xlsx")
            self.assertEqual(self.run_check(root, state), 0)

    def test_github_queue_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            state_path = self.write_state(root)
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["work_queue_source"] = "github_json"
            state_path.write_text(json.dumps(state), encoding="utf-8")
            self.write_xlsx(root / "Dropbox作業管理統合ボード.xlsx")
            self.assertEqual(self.run_check(root, state_path), 1)

    def test_nonempty_legacy_queue_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            state_path = self.write_state(root)
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["work_items"] = [{"id": "obsolete"}]
            state_path.write_text(json.dumps(state), encoding="utf-8")
            self.write_xlsx(root / "Dropbox作業管理統合ボード.xlsx")
            self.assertEqual(self.run_check(root, state_path), 1)

    def test_missing_board_stops_without_fallback(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            state_path = self.write_state(root)
            self.assertEqual(self.run_check(root, state_path), 1)

    def test_unreadable_board_stops_without_fallback(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            state_path = self.write_state(root)
            (root / "Dropbox作業管理統合ボード.xlsx").write_text("not xlsx", encoding="utf-8")
            self.assertEqual(self.run_check(root, state_path), 1)

    def test_pending_external_response_stops(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            state_path = self.write_state(root)
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["external_response_gate"].update({
                "status": "pending",
                "purpose": "react",
                "trigger": "proposal received",
                "required_action": "respond",
                "completion": "reaction presented",
            })
            state_path.write_text(json.dumps(state), encoding="utf-8")
            self.write_xlsx(root / "Dropbox作業管理統合ボード.xlsx")
            self.assertEqual(self.run_check(root, state_path), 3)

    def test_environment_conflict_stops(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            state_path = self.write_state(root)
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["execution_environment"]["retired"].append("work_pc")
            state_path.write_text(json.dumps(state), encoding="utf-8")
            self.write_xlsx(root / "Dropbox作業管理統合ボード.xlsx")
            self.assertEqual(self.run_check(root, state_path), 1)

    def test_stale_manifest_source_stops(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            state_path = self.write_state(root)
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["resume_manifest"]["source"] = "README.md"
            state_path.write_text(json.dumps(state), encoding="utf-8")
            self.write_xlsx(root / "Dropbox作業管理統合ボード.xlsx")
            self.assertEqual(self.run_check(root, state_path), 1)


if __name__ == "__main__":
    unittest.main()
