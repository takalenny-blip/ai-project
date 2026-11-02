import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.save_direct_chat import write_original

REPO_ROOT = Path(__file__).resolve().parents[1]


class SaveDirectChatTests(unittest.TestCase):
    def test_writes_original_text_exactly_including_legacy_state_block_and_crlf(self):
        content = (
            "  original leading whitespace\r\n"
            "<!-- BUD_STATE_PATCH_BEGIN\r\n"
            "legacy embedded data\r\n"
            "BUD_STATE_PATCH_END -->\r\n"
            "original trailing text  \r\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "direct-chat.md"
            write_original(target, content)
            with target.open("r", encoding="utf-8", newline="") as stream:
                self.assertEqual(stream.read(), content)

    def test_refuses_to_overwrite_existing_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "direct-chat.md"
            target.write_text("existing original", encoding="utf-8")
            with self.assertRaisesRegex(FileExistsError, "refusing to overwrite"):
                write_original(target, "replacement")
            self.assertEqual(target.read_text(encoding="utf-8"), "existing original")

    def test_cli_commits_one_exact_original_without_state_sidecars(self):
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            repo = temp_root / "repo"
            source = temp_root / "source.md"
            (repo / "scripts").mkdir(parents=True)
            for name in ("save_direct_chat.py", "check_repo_integrity.py", "check_atomic_save_commit.py"):
                shutil.copy2(REPO_ROOT / "scripts" / name, repo / "scripts" / name)

            content = (
                "  original start\r\n"
                "<!-- BUD_STATE_PATCH_BEGIN\r\n"
                '{"work_items": [1]}\r\n'
                "BUD_STATE_PATCH_END -->\r\n"
                "original end  \r\n"
            )
            with source.open("w", encoding="utf-8", newline="") as stream:
                stream.write(content)

            subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Save Test"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.email", "save-test@example.invalid"], cwd=repo, check=True)
            subprocess.run(["git", "add", "scripts"], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-m", "test base"], cwd=repo, check=True, capture_output=True)
            base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()

            result = subprocess.run(
                [sys.executable, "scripts/save_direct_chat.py", "--content-file", str(source)],
                cwd=repo,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(result.stdout.strip())

            changed = subprocess.check_output(
                ["git", "-c", "core.quotepath=false", "diff-tree", "--no-commit-id", "--name-status", "-r", "HEAD"],
                cwd=repo,
                text=True,
            ).splitlines()
            self.assertEqual(len(changed), 1, changed)
            status, relative = changed[0].split("\t", 1)
            self.assertEqual(status, "A")
            self.assertTrue(relative.startswith("直チャット/"))
            saved = repo / relative
            with saved.open("r", encoding="utf-8", newline="") as stream:
                self.assertEqual(stream.read(), content)

            for retired in (
                "docs/現在状態.json",
                "BUD.md",
                "docs/引き継ぎ/現在の引き継ぎ.md",
            ):
                self.assertFalse((repo / retired).exists(), retired)

            status = subprocess.check_output(["git", "status", "--porcelain"], cwd=repo, text=True)
            self.assertEqual(status, "")
            head_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
            self.assertNotEqual(base, head_sha)


if __name__ == "__main__":
    unittest.main()
