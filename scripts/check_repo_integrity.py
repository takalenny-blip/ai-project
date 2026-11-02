#!/usr/bin/env python3
"""Repository integrity checks for direct-chat originals and secret-like values."""
from __future__ import annotations
import argparse
import re
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_TIMESTAMP_OFFSET = "+0900"
TIMESTAMP_CHAT = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})_直チャット即時保存_(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}(?:\.\d{6})?[+-]\d{4})\.md$"
)
TIMESTAMP_CHAT_PART = re.compile(
    r"^\d{4}-\d{2}-\d{2}_直チャット即時保存_\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}(?:\.\d{6})?[+-]\d{4}\.part-\d{2}\.md$"
)
SERIAL_CHAT = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})(?:_\d{2}-\d{2}-\d{2})?_直チャット即時保存_(?P<serial>\d{3})\.md$"
)
HISTORIC_TIMESTAMP_CHAT = re.compile(r"^\d{4}-\d{2}-\d{2}_直チャット即時保存_\d{4}\.md$")
SECRET_PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9]{30,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{30,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]

def git_files() -> list[str]:
    out = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return [p for p in out.decode("utf-8").split("\0") if p]

def check_chat_names(files: list[str]) -> None:
    names = [Path(p).name for p in files if p.startswith("直チャット/")]
    marked = [n for n in names if "_直チャット即時保存_" in n]
    bad = [n for n in marked if not TIMESTAMP_CHAT.fullmatch(n) and not TIMESTAMP_CHAT_PART.fullmatch(n) and not SERIAL_CHAT.fullmatch(n) and not HISTORIC_TIMESTAMP_CHAT.fullmatch(n)]
    if bad:
        raise SystemExit("FAIL: malformed timestamped direct-chat names: " + ", ".join(sorted(bad)))
    identities = []
    for name in marked:
        match = SERIAL_CHAT.fullmatch(name)
        if match:
            identities.append((match.group("date"), match.group("serial")))
    if len(identities) != len(set(identities)):
        raise SystemExit("FAIL: duplicate timestamped direct-chat serial for date")
    for name in marked:
        match = TIMESTAMP_CHAT.fullmatch(name)
        if match and match.group("timestamp").endswith(CANONICAL_TIMESTAMP_OFFSET):
            datetime.strptime(match.group("timestamp"), "%Y-%m-%dT%H-%M-%S.%f%z" if "." in match.group("timestamp") else "%Y-%m-%dT%H-%M-%S%z")

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
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if scan_secret_text(content):
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
    print("OK: integrity self-test (timestamp + secret detection)")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    files = git_files()
    check_chat_names(files)
    check_secrets(files)
    print("OK: repository integrity checks")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
