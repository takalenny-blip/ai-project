#!/usr/bin/env python3
"""Save one direct-chat record and currentize all dependent state/views in one commit."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from typing import Any

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


def merge_patch(target: dict[str, Any], patch: dict[str, Any]) -> None:
    """Recursively merge a JSON object patch into the current state."""
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            merge_patch(target[key], value)
        else:
            target[key] = value


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
    ap.add_argument("--message", default=None)
    ap.add_argument(
        "--state-patch-file",
        type=Path,
        default=None,
        help="optional JSON object recursively merged into docs/現在状態.json before views are generated",
    )
    args = ap.parse_args()

    if run("git", "diff", "--cached", "--name-only"):
        raise SystemExit("refusing to run with pre-staged changes")

    content = (args.content_file.read_text(encoding="utf-8") if args.content_file else sys.stdin.read())
    if not content.endswith("\n"):
        content += "\n"

    now = datetime.now(ZoneInfo("Asia/Tokyo"))
    save_date = now.strftime("%Y-%m-%d")
    timestamp = f"{save_date}T{now:%H-%M-%S.%f%z}"
    filename = f"{save_date}_直チャット即時保存_{timestamp}.md"
    path = DIRECT_CHAT_DIR / filename
    if path.exists():
        raise SystemExit(f"refusing to overwrite existing record: {path}")

    title = f"# 直チャット{timestamp}\n"
    if not content.startswith("# 直チャット"):
        content = title + "\n" + content.lstrip()
    path.write_text(content, encoding="utf-8")

    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    state["updated"] = save_date
    state["direct_chat"]["latest_saved"] = timestamp
    state["direct_chat"]["latest_path"] = f"直チャット/{filename}"
    state["direct_chat"]["latest_content_sha"] = git_blob_sha(content.encode("utf-8"))
    state["direct_chat"]["legacy_serial_files_preserved"] = True
    state["direct_chat"]["new_timestamp_naming_allowed"] = True

    # Keep canonical save metadata aligned with the sole live entrypoint.
    state["save_pipeline"]["normal_entrypoints"] = ["save-request-intake.yml (pull_request_target; queue PR required)"]
    state["pending_monitoring"] = [
        item for item in state.get("pending_monitoring", [])
        if item != "最終修正PR merge後のCI成功確認"
    ]
    state["surgery"]["next_design_item"] = "通常のDiMORA本来工程へ復帰する"

    if args.state_patch_file:
        patch = json.loads(args.state_patch_file.read_text(encoding="utf-8"))
        if not isinstance(patch, dict):
            raise SystemExit("state patch must be a JSON object")
        merge_patch(state, patch)

    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    render_views()

    subprocess.run(["git", "add", str(path), str(STATE_PATH), str(BUD_PATH), str(HANDOVER_PATH)], cwd=ROOT, check=True)
    expected = {
        str(path.relative_to(ROOT)),
        str(STATE_PATH.relative_to(ROOT)),
        str(BUD_PATH.relative_to(ROOT)),
        str(HANDOVER_PATH.relative_to(ROOT)),
    }
    staged_raw = subprocess.check_output(["git", "diff", "--cached", "--name-only", "-z"], cwd=ROOT)
    staged = set(p for p in staged_raw.decode("utf-8").split("\0") if p)
    if staged != expected:
        raise SystemExit(f"unexpected staged paths: {sorted(staged)}")

    subprocess.run([sys.executable, "scripts/check_repo_integrity.py"], cwd=ROOT, check=True)
    subprocess.run([sys.executable, "scripts/generate_current_views.py", "--out-dir", ".generated-save-check", "--check-deterministic"], cwd=ROOT, check=True)
    subprocess.run(["cmp", "--silent", ".generated-save-check/BUD.md", "BUD.md"], cwd=ROOT, check=True)
    subprocess.run(["cmp", "--silent", ".generated-save-check/現在の引き継ぎ.md", str(HANDOVER_PATH)], cwd=ROOT, check=True)
    subprocess.run(["rm", "-rf", ".generated-save-check"], cwd=ROOT, check=True)

    message = args.message or f"直チャット{timestamp}保存＋現在状態と生成ビューを一括同期"
    subprocess.run(["git", "commit", "-m", message], cwd=ROOT, check=True)
    print(run("git", "rev-parse", "HEAD"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
