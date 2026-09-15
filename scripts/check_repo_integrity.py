#!/usr/bin/env python3
"""Mechanical repository checks for the ai-project surgery lane."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "docs/現在状態.json"

# New records may use a real wall-clock timestamp between the date and marker.
# The old date+serial form remains valid for records already created.
TIMESTAMP_CHAT = re.compile(
    r"^\d{4}-\d{2}-\d{2}(?:_\d{2}-\d{2}-\d{2})?_直チャット即時保存_(\d{3})\.md$"
)
HISTORIC_TIMESTAMP_CHAT = re.compile(
    r"^\d{4}-\d{2}-\d{2}_直チャット即時保存_\d{4}\.md$"
)
SECRET_PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9]{30,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{30,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]


def git_files() -> list[str]:
    out = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return [p for p in out.decode("utf-8").split("\0") if p]


def check_verification_state(state: dict) -> None:
    required = state.get("verification_required", [])
    if not all(isinstance(item, dict) and "item" in item and "status" in item for item in required):
        raise SystemExit("FAIL: verification_required must use {item,status} objects")

    statuses = {item["status"] for item in required}
    invalid = statuses - {"done", "pending", "not_started", "conditional"}
    if invalid:
        raise SystemExit("FAIL: invalid verification status: " + ", ".join(sorted(invalid)))

    # `conditional` is a valid non-terminal state. It must never satisfy the
    # migration-complete condition merely by being accepted here.
    if state["migration"]["status"] == "generated_views_migration_verified":
        incomplete = [item["item"] for item in required if item["status"] != "done"]
        if incomplete:
            raise SystemExit(
                "FAIL: migration.status claims verified with incomplete verification items: "
                + "; ".join(incomplete)
            )


def check_state(files: list[str]) -> None:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    check_verification_state(state)

    path = state["direct_chat"]["latest_path"]
    latest = state["direct_chat"]["latest_saved"]
    if path not in files:
        raise SystemExit(f"FAIL: latest direct-chat path missing: {path}")
    match = re.search(r"_(\d{3})\.md$", path)
    if not match or match.group(1) != latest:
        raise SystemExit("FAIL: current state latest_saved/latest_path mismatch")

    # The state must identify the newest three-digit direct-chat record, not
    # merely a path that is internally consistent. Historical four-digit files
    # are preserved and excluded from this comparison.
    names = [Path(p).name for p in files if p.startswith("直チャット/")]
    records: list[tuple[str, int, str]] = []
    for name in names:
        m = TIMESTAMP_CHAT.fullmatch(name)
        if m:
            records.append((name[:10], int(m.group(1)), name))
    if not records:
        raise SystemExit("FAIL: no three-digit direct-chat records found")

    newest_date = max(date for date, _, _ in records)
    newest_serial = max(serial for date, serial, _ in records if date == newest_date)
    path_name = Path(path).name
    path_date = path_name[:10]
    if path_date != newest_date or int(latest) != newest_serial:
        raise SystemExit(
            "FAIL: current state does not point to newest direct-chat record: "
            f"state={path_name}, newest={newest_date}_..._{newest_serial:03d}.md"
        )


def check_chat_names(files: list[str]) -> None:
    names = [Path(p).name for p in files if p.startswith("直チャット/")]
    marked = [n for n in names if "_直チャット即時保存_" in n]

    bad = [
        n for n in marked
        if not TIMESTAMP_CHAT.fullmatch(n)
        and not HISTORIC_TIMESTAMP_CHAT.fullmatch(n)
    ]
    if bad:
        raise SystemExit(
            "FAIL: malformed timestamped direct-chat names: "
            + ", ".join(sorted(bad))
        )

    # A serial may recur on a different date. Within one date, however, a
    # three-digit serial must identify one new record. Historical four-digit
    # records are preserved and excluded.
    identities = []
    for n in marked:
        match = TIMESTAMP_CHAT.fullmatch(n)
        if match:
            identities.append((n[:10], match.group(1)))
    if len(identities) != len(set(identities)):
        raise SystemExit("FAIL: duplicate timestamped direct-chat serial for date")


def scan_secret_text(text: str) -> str | None:
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            return pattern.pattern
    return None


def check_secrets(files: list[str]) -> None:
    text_exts = {".md", ".json", ".py", ".yml", ".yaml", ".txt", ".sh"}
    for rel in files:
        path = ROOT / rel
        if path.suffix.lower() not in text_exts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if scan_secret_text(text):
            raise SystemExit(f"FAIL: secret-like value detected in {rel}")


def self_test() -> None:
    # Green test: a real timestamp filename is accepted.
    check_chat_names([
        "直チャット/2026-09-15_12-34-56_直チャット即時保存_043.md"
    ])

    # Red-test semantics: the secret scanner must reject a synthetic secret-like value.
    synthetic = "github_pat_" + "A" * 40
    if scan_secret_text(synthetic) is None:
        raise SystemExit("FAIL: secret self-test did not detect synthetic secret-like value")

    print("OK: integrity self-test (timestamp green + secret red detection)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return 0

    files = git_files()
    check_state(files)
    check_chat_names(files)
    check_secrets(files)
    print("OK: repository integrity checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
