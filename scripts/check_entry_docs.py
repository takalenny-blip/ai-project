#!/usr/bin/env python3
"""Check the repository entry documents for the current source-of-truth contract."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
RULE = ROOT / "rules" / "構造変更時・独立監査ガード.md"


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise SystemExit(f"FAIL: {label}: missing required text: {needle}")


def main() -> int:
    readme = README.read_text(encoding="utf-8")
    rule = RULE.read_text(encoding="utf-8")

    require(readme, "最初に [`docs/現在状態.json`](./docs/現在状態.json) を読んでください。これが現在状態の唯一の正本です。", "README source of truth")
    require(readme, "BUD.md", "README generated view reference")
    require(readme, "機械生成されるビュー", "README generated-view contract")
    require(readme, "これらを現在状態の正本として直接編集してはいけません", "README no-direct-edit contract")
    require(readme, "構造変更時だけ深い独立監査を起動し", "README conditional audit trigger")
    require(readme, "起動時・再開時の現在化ゲート", "README startup currentization gate")
    require(readme, "docs/現在状態.json", "README canonical startup state")
    require(readme, "BUD.mdや引き継ぎを先に読んで現在状態を決めてはならない", "README no BUD-first startup")
    require(readme, "前回の作業完了後に新しいPR・merge・commitが存在する場合", "README post-work freshness check")

    require(rule, "構造変更時だけ", "audit trigger")
    require(rule, "scripts/check_repo_integrity.py", "mechanical integrity guard")
    require(rule, "scripts/save_and_currentize.py", "atomic save guard")
    require(rule, "次に参加するAI", "next-agent safety check")
    require(rule, "通常工程へ戻る", "return-to-normal-operation rule")
    require(rule, "GitHub上の `docs/現在状態.json` を最初に直接読み", "rule canonical startup state")
    require(rule, "前回作業以後にPR/merge/commitが存在する場合", "rule post-work freshness check")
    require(rule, "GitHub正本より優先しない", "rule stale-history precedence")

    print("OK: AI entry documentation contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
