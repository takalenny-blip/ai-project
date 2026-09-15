#!/usr/bin/env python3
"""Save one direct-chat record and currentize all dependent views in one commit."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "docs" / "現在状態.json"
DIRECT_CHAT_DIR = ROOT / "直チャット"
BUD_PATH = ROOT / "BUD.md"
HANDOVER_PATH = ROOT / "docs" / "引き継ぎ" / "現在の引き継ぎ.md"


def run(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def next_serial(date: str) -> str:
    values = []
    prefix = f"{date}_直チャット即時保存_"
    for p in DIRECT_CHAT_DIR.glob(f"{prefix}*.md"):
        tail = p.stem[len(prefix):]
        if tail.isdigit() and len(tail) == 3:
            values.append(int(tail))
    next_value = max(values, default=0) + 1
    if next_value > 999:
        raise SystemExit(f"no three-digit serials remaining for date {date}")
    return f"{next_value:03d}"


def render_views() -> None:
    subprocess.run(
        [sys.executable, "scripts/generate_current_views.py", "--out-dir", ".generated-save-views"],
        cwd=ROOT,
        check=True,
    )
    src = ROOT / ".generated-save-views"
    BUD_PATH.write_text((src / "BUD.md").read_text(encoding="utf-8"), encoding="utf-8")
    HANDOVER_PATH.write_text((src / "現在の引き継ぎ.md").read_text(encoding="utf-8"), encoding="utf-8")
    subprocess.run(["rm", "-rf", str(src)], cwd=ROOT, check=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--content-file", type=Path, help="direct-chat markdown; stdin when omitted")
    ap.add_argument("--date", default=datetime.now().astimezone().strftime("%Y-%m-%d"))
    ap.add_argument("--serial", default=None)
    ap.add_argument("--message", default=None)
    args = ap.parse_args()

    # Do not mix unrelated pre-staged work into the atomic save commit.
    if run("git", "diff", "--cached", "--name-only"):
        raise SystemExit("refusing to run with pre-staged changes")

    content = (args.content_file.read_text(encoding="utf-8") if args.content_file else sys.stdin.read())
    if not content.endswith("\n"):
        content += "\n"

    serial = args.serial or next_serial(args.date)
    if not (serial.isdigit() and len(serial) == 3):
        raise SystemExit("serial must be exactly three digits")
    filename = f"{args.date}_直チャット即時保存_{serial}.md"
    path = DIRECT_CHAT_DIR / filename
    if path.exists():
        raise SystemExit(f"refusing to overwrite existing record: {path}")

    title = f"# 直チャット{serial}\n"
    if not content.startswith("# 直チャット"):
        content = title + "\n" + content.lstrip()
    path.write_text(content, encoding="utf-8")

    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    state["updated"] = args.date
    state["direct_chat"]["latest_saved"] = serial
    state["direct_chat"]["latest_path"] = f"直チャット/{filename}"
    state["direct_chat"]["latest_content_sha"] = git_blob_sha(content.encode("utf-8"))
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    render_views()

    # Stage before integrity checks because the integrity checker intentionally
    # reasons about tracked files via `git ls-files`.
    subprocess.run(["git", "add", str(path), str(STATE_PATH), str(BUD_PATH), str(HANDOVER_PATH)], cwd=ROOT, check=True)
    expected = {
        str(path.relative_to(ROOT)),
        str(STATE_PATH.relative_to(ROOT)),
        str(BUD_PATH.relative_to(ROOT)),
        str(HANDOVER_PATH.relative_to(ROOT)),
    }
    staged = set(run("git", "diff", "--cached", "--name-only").splitlines())
    if staged != expected:
        raise SystemExit(f"unexpected staged paths: {sorted(staged)}")

    subprocess.run([sys.executable, "scripts/check_repo_integrity.py"], cwd=ROOT, check=True)
    subprocess.run([sys.executable, "scripts/generate_current_views.py", "--out-dir", ".generated-save-check", "--check-deterministic"], cwd=ROOT, check=True)
    subprocess.run(["cmp", "--silent", ".generated-save-check/BUD.md", "BUD.md"], cwd=ROOT, check=True)
    subprocess.run(["cmp", "--silent", ".generated-save-check/現在の引き継ぎ.md", str(HANDOVER_PATH)], cwd=ROOT, check=True)
    subprocess.run(["rm", "-rf", ".generated-save-check"], cwd=ROOT, check=True)

    message = args.message or f"直チャット{serial}保存＋現在状態と生成ビューを一括同期"
    subprocess.run(["git", "commit", "-m", message], cwd=ROOT, check=True)
    print(run("git", "rev-parse", "HEAD"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
