#!/usr/bin/env python3
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = sorted((ROOT / ".github" / "workflows").glob("*.yml")) + sorted((ROOT / ".github" / "workflows").glob("*.yaml"))


class WorkflowSyntaxTests(unittest.TestCase):
    def test_workflow_yaml_and_run_blocks_are_parseable(self):
        ruby = shutil.which("ruby")
        self.assertIsNotNone(ruby, "ruby is required on the GitHub Actions runner")
        yaml_script = r"""
require "yaml"
path = ARGV.fetch(0)
data = YAML.load_file(path)
raise "empty workflow" if data.nil?
"""
        for path in WORKFLOWS:
            with self.subTest(path=path.name):
                parsed = subprocess.run([ruby, "-e", yaml_script, str(path)], text=True, capture_output=True)
                self.assertEqual(parsed.returncode, 0, parsed.stderr or parsed.stdout)

                lines = path.read_text(encoding="utf-8").splitlines()
                i = 0
                while i < len(lines):
                    match = re.match(r"^( +)run:\s*\|\s*$", lines[i])
                    if not match:
                        i += 1
                        continue
                    run_indent = len(match.group(1))
                    i += 1
                    block = []
                    while i < len(lines):
                        line = lines[i]
                        if line.strip() and len(line) - len(line.lstrip(" ")) <= run_indent:
                            break
                        block.append(line)
                        i += 1
                    while block and not block[-1].strip():
                        block.pop()
                    if not block:
                        continue

                    content_indent = min(
                        len(line) - len(line.lstrip(" "))
                        for line in block
                        if line.strip()
                    )
                    shell = "\n".join(line[content_indent:] for line in block) + "\n"
                    # GitHub expressions are not Bash syntax; replace them before bash -n.
                    shell = re.sub(r"\$\{\{.*?\}\}", "GITHUB_EXPRESSION", shell, flags=re.S)
                    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".sh") as fh:
                        fh.write(shell)
                        fh.flush()
                        checked = subprocess.run(["bash", "-n", fh.name], text=True, capture_output=True)
                    self.assertEqual(checked.returncode, 0, checked.stderr or checked.stdout)


if __name__ == "__main__":
    unittest.main()
