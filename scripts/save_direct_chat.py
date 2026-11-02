#!/usr/bin/env python3
"""Save exactly one new direct-chat original; do not write state snapshots or views."""
from __future__ import annotations
import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
DIRECT_CHAT_DIR = ROOT / "直チャット"

def write_original(path: Path, content: str) -> None:
    """Write supplied conversation text without cleanup or sidecars."""
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8", newline="") as stream:
            stream.write(content)
    except FileExistsError as exc:
        raise FileExistsError(f"refusing to overwrite existing record: {path}") from exc

def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True, encoding="utf-8").strip()

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--content-file", type=Path, required=True)
    parser.add_argument("--message")
    args = parser.parse_args()
    if not args.content_file.is_file():
        raise SystemExit(f"content file is missing: {args.content_file}")
    with args.content_file.open("r", encoding="utf-8", newline="") as stream:
        content = stream.read()
    if not content.strip():
        raise SystemExit("refusing to save an empty direct-chat record")
    now = datetime.now(ZoneInfo("Asia/Tokyo"))
    timestamp = now.strftime("%Y-%m-%dT%H-%M-%S.%f%z")
    filename = f"{now:%Y-%m-%d}_直チャット即時保存_{timestamp}.md"
    path = DIRECT_CHAT_DIR / filename
    try:
        write_original(path, content)
    except FileExistsError as exc:
        raise SystemExit(str(exc)) from exc
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
    return 0

if __name__ == "__main__":
    raise SystemExit(main())