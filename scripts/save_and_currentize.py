#!/usr/bin/env python3
"""Save one direct-chat record and update its latest pointer in the operating rules."""
from __future__ import annotations
import argparse, hashlib, re, subprocess, sys
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = ROOT / "rules" / "運用ルール.md"
DIRECT_CHAT_DIR = ROOT / "直チャット"

def run(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()

def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()

STATE_PATCH_BEGIN = "<!-- BUD_STATE_PATCH_BEGIN"
STATE_PATCH_END = "BUD_STATE_PATCH_END -->"

def strip_retired_embedded_state_patch(content: str) -> tuple[str, bool]:
    """Remove legacy embedded JSON patches without parsing or applying them."""
    pattern = re.compile(re.escape(STATE_PATCH_BEGIN) + r"\\s*\\n.*?\\n" + re.escape(STATE_PATCH_END), re.DOTALL)
    cleaned, count = pattern.subn("", content, count=1)
    if count == 0:
        return content, False
    return cleaned.strip() + "\\n", True

def update_latest_save_record(rules: str, timestamp: str, relative_path: str, blob_sha: str) -> str:
    pattern = re.compile(r"(#### 直チャット保存記録（現行）\\s*\\n)(.*?)(?=\\n#### |\\n### |\\Z)", re.DOTALL)
    match = pattern.search(rules)
    if not match:
        raise SystemExit("rules/運用ルール.md has no current direct-chat save record section")
    section = match.group(2)
    values = {"最新保存": timestamp, "原本": relative_path, "内容SHA": blob_sha}
    for label, value in values.items():
        line = re.compile(rf"^- {re.escape(label)}：.*$", re.MULTILINE)
        section, count = line.subn(f"- {label}：`{value}`", section)
        if count != 1:
            raise SystemExit(f"direct-chat save record must contain exactly one {label} field")
    return rules[:match.start(2)] + section + rules[match.end(2):]

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--content-file", type=Path, help="direct-chat markdown; stdin when omitted")
    ap.add_argument("--message", default=None)
    args = ap.parse_args()
    if run("git", "diff", "--cached", "--name-only"):
        raise SystemExit("refusing to run with pre-staged changes")
    content = args.content_file.read_text(encoding="utf-8") if args.content_file else sys.stdin.read()
    content, had_retired_patch = strip_retired_embedded_state_patch(content)
    if not content.endswith("\\n"):
        content += "\\n"
    now = datetime.now(ZoneInfo("Asia/Tokyo"))
    save_date = now.strftime("%Y-%m-%d")
    timestamp = f"{save_date}T{now:%H-%M-%S.%f%z}"
    filename = f"{save_date}_直チャット即時保存_{timestamp}.md"
    path = DIRECT_CHAT_DIR / filename
    relative_path = path.relative_to(ROOT).as_posix()
    if path.exists():
        raise SystemExit(f"refusing to overwrite existing record: {path}")
    if not content.startswith("# 直チャット"):
        content = f"# 直チャット{timestamp}\\n\\n" + content.lstrip()
    rules = RULES_PATH.read_text(encoding="utf-8")
    blob_sha = git_blob_sha(content.encode("utf-8"))
    updated_rules = update_latest_save_record(rules, timestamp, relative_path, blob_sha)
    path.write_text(content, encoding="utf-8")
    RULES_PATH.write_text(updated_rules, encoding="utf-8")
    if had_retired_patch:
        print("warning: embedded legacy state patch was stripped and not applied", file=sys.stderr)
    subprocess.run(["git", "add", str(path), str(RULES_PATH)], cwd=ROOT, check=True)
    expected = {relative_path, "rules/運用ルール.md"}
    staged_raw = subprocess.check_output(["git", "diff", "--cached", "--name-only", "-z"], cwd=ROOT)
    staged = {p for p in staged_raw.decode("utf-8").split("\\0") if p}
    if staged != expected:
        raise SystemExit(f"unexpected staged paths: {sorted(staged)}")
    subprocess.run([sys.executable, "scripts/check_repo_integrity.py"], cwd=ROOT, check=True)
    subprocess.run([sys.executable, "scripts/current_state_guard.py"], cwd=ROOT, check=True)
    message = args.message or f"直チャット{timestamp}保存＋運用ルール最新記録更新"
    subprocess.run(["git", "commit", "-m", message], cwd=ROOT, check=True)
    print(run("git", "rev-parse", "HEAD"))
    print(f"saved_path: {relative_path}")
    print(f"content_sha: {blob_sha}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
