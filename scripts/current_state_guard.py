#!/usr/bin/env python3
"""Validate the single-source operating rules and current repository constraints."""
from __future__ import annotations

import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = ROOT / "rules" / "運用ルール.md"
RETIRED_ALIASES = ("vaio_p", "VAIO P", "VAIO P + Chromium", "VAIO P運用")

REQUIRED_RULES = (
    "現在状態・共通運用ルールの唯一の正本",
    "日常作業キューの唯一の正本",
    "/ChatGPT/Dropbox作業管理統合ボード.xlsx",
    "現行の実行環境",
    "work_pc",
    "vaio_p",
    "経験ログ → Blogger下書き・表示確認 → GitHub Pages本番公開",
    "WordPressは本番公開先として扱わない",
    "直チャット保存記録",
    "外部提案対応状態",
    "0-4. 画像機能の事前許可",
    "0-3. 作業開始ゲート",
    "4-14. 再開時の最初の確認",
    "4-17. 対話行動preflight gate",
)

def fail(message: str) -> None:
    raise ValueError(message)

def load_rules(path: Path = RULES_PATH) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        fail(f"operating rules unreadable: {exc}")

def validate_rules(text: str) -> None:
    missing = [item for item in REQUIRED_RULES if item not in text]
    if missing:
        fail("operating rules missing required current-state content: " + ", ".join(missing))

    # Old artifacts may be named only as explicitly retired migration targets.
    forbidden_active_patterns = (
        r"docs/現在状態\.json[^\n]{0,100}(?:を最初に直接読み|から技術状態|を唯一の現在状態正本)",
        r"BUD\.md[^\n]{0,100}生成される(?:互換ビュー|現在状態ビュー)",
        r"docs/引き継ぎ/現在の引き継ぎ\.md[^\n]{0,100}生成",
        r"WordPress本番公開",
        r"vaio_p[^\n]{0,80}(?:active|現行環境|次工程)",
    )
    for pattern in forbidden_active_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            fail("operating rules contain a retired active instruction: " + pattern)

    status_section = re.search(
        r"#### 外部提案対応状態（現行）\s*\n(.*?)(?=\n#### |\n### |\Z)",
        text,
        re.DOTALL,
    )
    if not status_section:
        fail("external proposal response status section is missing")
    status = re.search(r"状態：\s*(clear|pending)", status_section.group(1))
    if not status:
        fail("external proposal response status must be clear or pending")
    if status.group(1) == "pending":
        required = ("提案：", "判断：", "理由：", "次の行動：", "整合性：")
        missing_pending = [item for item in required if item not in status_section.group(1)]
        if missing_pending:
            fail("pending external proposal status missing: " + ", ".join(missing_pending))

    save_section = re.search(
        r"#### 直チャット保存記録（現行）\s*\n(.*?)(?=\n#### |\n### |\Z)",
        text,
        re.DOTALL,
    )
    if not save_section:
        fail("direct-chat save record section is missing")
    for key in ("最新保存：", "原本：", "内容SHA："):
        if key not in save_section.group(1):
            fail("direct-chat save record missing " + key)

def retired_tokens() -> tuple[str, ...]:
    return RETIRED_ALIASES

def validate_projects() -> None:
    projects = ROOT / "projects"
    if not projects.exists():
        return
    for path in sorted(projects.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if any(token in text for token in retired_tokens()):
            header = "\n".join(text.splitlines()[:20]).lower()
            if "status: historical" not in header:
                fail(f"non-historical project doc mentions retired environment: {path}")

def validate(path: Path = RULES_PATH) -> None:
    text = load_rules(path)
    validate_rules(text)
    validate_projects()

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rules", type=Path, default=RULES_PATH)
    args = parser.parse_args()
    try:
        validate(args.rules)
    except ValueError as exc:
        print(f"FAIL: {exc}")
        return 1
    print("OK: single-source operating-rules guard passed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
