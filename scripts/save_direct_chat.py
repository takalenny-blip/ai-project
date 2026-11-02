#!/usr/bin/env python3
"""Save exactly one new direct-chat original; do not write state snapshots or views."""
from __future__ import annotations
import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
DIRECT_CHAT_DIR = ROOT / "直チャット"
PATCH_BEGIN = "<!-- BUD_STATE_PATCH_BEGIN"
PATCH_END = "BUD_STATE_PATCH_END -->"

def strip_retired_embedded_state_patch(content: str) -> tuple[str, bool]:
    pattern = re.compile(re.escape(PATCH_BEGIN) + r"\s*\n.*?\n" + re.escape(PATCH_END), re.DOTALL)
    cleaned, count = pattern.subn("", content, count=1)
    if not count:
        return content, False
    return cleaned.strip() + "\n", True

def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True, encoding="utf-8").strip()

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--content-file", type=Path, required=True)
    parser.add_argument("--message")
    args = parser.parse_args()
    if not args.content_file.is_file():
        raise SystemExit(f"content file is missing: {args.content_file}")
    content = args.content_file.read_text(encoding="utf-8")
    content, removed_patch = strip_retired_embedded_state_patch(content)
    if not content.strip():
        raise SystemExit("refusing to save an empty direct-chat record")
    now = datetime.now(ZoneInfo("Asia/Tokyo"))
    timestamp = now.strftime("%Y-%m-%dT%H-%M-%S.%f%z")
    filename = f"{now:%Y-%m-%d}_直チャット即時保存_{timestamp}.md"
    path = DIRECT_CHAT_DIR / filename
    if path.exists():
        raise SystemExit(f"refusing to overwrite existing record: {path}")
    DIRECT_CHAT_DIR.mkdir(parents=True, exist_ok=True)
    if not content.startswith("# 直チャット"):
        content = f"# 直チャット{timestamp}\n\n" + content.lstrip()
    path.write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", str(path.relative_to(ROOT))], cwd=ROOT, check=True)
    staged_raw = subprocess.check_output(["git", "diff", "--cached", "--name-only", "-z"], cwd=ROOT)
    staged = {item for item in staged_raw.decode("utf-8").split("\0") if item}
    expected = {str(path.relative_to(ROOT))}
    if staged != expected:
        raise SystemExit(f"refusing to commit unexpected staged paths: {sorted(staged)}")
    subprocess.run([sys.executable, "scripts/check_repo_integrity.py"], cwd=ROOT, check=True)
    message = args.message or f"直チャット{timestamp}保存"
    subprocess.run(["git", "commit", "-m", message], cwd=ROOT, check=True)
    subprocess.run([sys.executable, "scripts/check_atomic_save_commit.py", "--commit", "HEAD"], cwd=ROOT, check=True)
    print(git("rev-parse", "HEAD"))
    if removed_patch:
        print("NOTICE: retired embedded state patch block was not applied and was excluded from the saved record.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
