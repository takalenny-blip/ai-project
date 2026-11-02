#!/usr/bin/env python3
"""Mechanical repository checks for the ai-project surgery lane."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = ROOT / "rules/運用ルール.md"
CANONICAL_TIMESTAMP_OFFSET = "+0900"

TIMESTAMP_CHAT = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})_直チャット即時保存_(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}(?:\.\d{6})?[+-]\d{4})\.md$"
)
TIMESTAMP_CHAT_PART = re.compile(
    r"^\d{4}-\d{2}-\d{2}_直チャット即時保存_\d{4}-\d{2}-\d{2}T"
    r"\d{2}-\d{2}-\d{2}(?:\.\d{6})?[+-]\d{4}\.part-\d{2}\.md$"
)
SERIAL_CHAT = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})(?:_\d{2}-\d{2}-\d{2})?_直チャット即時保存_(?P<serial>\d{3})\.md$"
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


def timestamp_key(timestamp: str) -> datetime:
    return datetime.strptime(timestamp, "%Y-%m-%dT%H-%M-%S.%f%z" if "." in timestamp else "%Y-%m-%dT%H-%M-%S%z")


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("utf-8") + data).hexdigest()


def check_state(files: list[str]) -> None:
    text = (ROOT / RULES_PATH).read_text(encoding="utf-8")
    match = re.search(
        r"#### 直チャット保存記録（現行）\s*\n(.*?)(?=\n#### |\n### |\Z)",
        text,
        re.DOTALL,
    )
    if not match:
        raise SystemExit("FAIL: current direct-chat save record is missing from rules/運用ルール.md")
    section = match.group(1)
    fields = {}
    for label, key in (("最新保存", "timestamp"), ("原本", "path"), ("内容SHA", "sha")):
        found = re.findall(rf"^- {label}：(.+)$", section, re.MULTILINE)
        found = [value.strip().strip("`") for value in found]
        if len(found) != 1:
            raise SystemExit(f"FAIL: direct-chat save record must contain exactly one {label} field")
        fields[key] = found[0]
    path, latest = fields["path"], fields["timestamp"]
    if path not in files:
        raise SystemExit(f"FAIL: latest direct-chat path missing: {path}")
    timestamp_match = TIMESTAMP_CHAT.fullmatch(Path(path).name)
    if not timestamp_match or timestamp_match.group("timestamp") != latest:
        raise SystemExit("FAIL: rules latest_saved/latest_path timestamp mismatch")
    actual_sha = git_blob_sha((ROOT / path).read_bytes())
    if actual_sha != fields["sha"]:
        raise SystemExit("FAIL: rules latest direct-chat content SHA mismatch")
    timestamps = []
    for rel in files:
        if rel.startswith("直チャット/"):
            candidate = TIMESTAMP_CHAT.fullmatch(Path(rel).name)
            if candidate and candidate.group("timestamp").endswith(CANONICAL_TIMESTAMP_OFFSET):
                timestamps.append(candidate.group("timestamp"))
    if timestamps:
        newest = max(timestamps, key=timestamp_key)
        if latest.endswith(CANONICAL_TIMESTAMP_OFFSET) and latest != newest:
            raise SystemExit(
                "FAIL: rules does not point to newest canonical timestamped direct-chat record: "
                f"rules={latest}, newest={newest}"
            )


def check_chat_names(files: list[str]) -> None:
    names = [Path(p).name for p in files if p.startswith("直チャット/")]
    marked = [n for n in names if "_直チャット即時保存_" in n]
    bad = [
        n for n in marked
        if not TIMESTAMP_CHAT.fullmatch(n)
        and not TIMESTAMP_CHAT_PART.fullmatch(n)
        and not SERIAL_CHAT.fullmatch(n)
        and not HISTORIC_TIMESTAMP_CHAT.fullmatch(n)
    ]
    if bad:
        raise SystemExit("FAIL: malformed timestamped direct-chat names: " + ", ".join(sorted(bad)))

    identities = []
    for n in marked:
        match = SERIAL_CHAT.fullmatch(n)
        if match:
            identities.append((match.group("date"), match.group("serial")))
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
    check_chat_names([
        "直チャット/2026-09-15_直チャット即時保存_2026-09-15T12-34-56+0900.md",
        "直チャット/2026-09-15_直チャット即時保存_2026-09-15T12-34-56.123456+0900.md",
        "直チャット/2026-09-15_直チャット即時保存_2026-09-15T12-34-56.123456+0900.part-01.md",
        "直チャット/2026-09-15_12-34-56_直チャット即時保存_043.md",
    ])

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
