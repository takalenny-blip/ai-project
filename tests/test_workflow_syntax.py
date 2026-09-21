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
        script = r"""
require "yaml"
path = ARGV.fetch(0)
data = YAML.load_file(path)
raise "empty workflow" if data.nil?
"""
        for path in WORKFLOWS:
            with self.subTest(path=path.name):
                parsed = subprocess.run([ruby, "-e", script, str(path)], text=True, capture_output=True)
                self.assertEqual(parsed.returncode, 0, parsed.stderr or parsed.stdout)
                text = path.read_text(encoding="utf-8")
                masked = re.sub(r"${{.*?}}", "GITHUB_EXPRESSION", text, flags=re.S)
                blocks = re.findall(r"(?ms)^s+run:s*|
((?:^[ ]{10,}.*
?)+)", masked)
                for block in blocks:
                    lines = block.splitlines()
                    while lines and not lines[0].strip():
                        lines.pop(0)
                    if not lines:
                        continue
                    indent = min(len(line) - len(line.lstrip(" ")) for line in lines if line.strip())
                    shell = "
".join(line[indent:] for line in lines) + "
"
                    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".sh") as fh:
                        fh.write(shell)
                        fh.flush()
                        checked = subprocess.run(["bash", "-n", fh.name], text=True, capture_output=True)
                    self.assertEqual(checked.returncode, 0, checked.stderr or checked.stdout)


if __name__ == "__main__":
    unittest.main()
