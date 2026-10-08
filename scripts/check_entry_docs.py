#!/usr/bin/env python3
"""Check the repository entry documents for the current source-of-truth contract."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
AUDIT_RULE = ROOT / "rules" / "構造変更時・独立監査ガード.md"
OPERATING_RULE = ROOT / "rules" / "運用ルール.md"
READ_MAP = ROOT / "docs" / "AI_READ_MAP.md"


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise SystemExit(f"FAIL: {label}: missing required text: {needle}")


def main() -> int:
    readme = README.read_text(encoding="utf-8")
    audit_rule = AUDIT_RULE.read_text(encoding="utf-8")
    operating_rule = OPERATING_RULE.read_text(encoding="utf-8")
    read_map = READ_MAP.read_text(encoding="utf-8")

    require(readme, "最初に [`docs/現在状態.json`](./docs/現在状態.json) を読んでください。これが現在状態の唯一の正本です。", "README source of truth")
    require(readme, "BUD.md", "README generated view reference")
    require(readme, "機械生成されるビュー", "README generated-view contract")
    require(readme, "これらを現在状態の正本として直接編集してはいけません", "README no-direct-edit contract")
    require(readme, "構造変更時だけ深い独立監査を起動し", "README conditional audit trigger")
    require(readme, "起動時・再開時の現在化ゲート", "README startup currentization gate")
    require(readme, "docs/現在状態.json", "README canonical startup state")
    require(readme, "BUD.mdや引き継ぎを先に読んで現在状態を決めてはならない", "README no BUD-first startup")
    require(readme, "前回の作業完了後に新しいPR・merge・commitが存在する場合", "README post-work freshness check")

    require(audit_rule, "構造変更時だけ", "audit trigger")
    require(audit_rule, "scripts/check_repo_integrity.py", "mechanical integrity guard")
    require(audit_rule, "scripts/save_and_currentize.py", "atomic save guard")
    require(audit_rule, "次に参加するAI", "next-agent safety check")
    require(audit_rule, "通常工程へ戻る", "return-to-normal-operation rule")
    require(operating_rule, "GitHub上の `docs/現在状態.json` を最初に直接読み", "rule canonical startup state")
    require(operating_rule, "前回作業以後にPR/merge/commitが存在する場合", "rule post-work freshness check")
    require(operating_rule, "GitHub正本より優先しない", "rule stale-history precedence")

    require(read_map, "`docs/現在状態.json` — 現在状態・現在の作業キュー・現在の次の一手の唯一の正本", "AI read map canonical state")
    require(read_map, "`BUD.md` / `docs/引き継ぎ/現在の引き継ぎ.md` — 正本から生成された互換ビュー", "AI read map generated views")
    require(read_map, "正本との不一致時は使用せず、正本を優先する", "AI read map stale-view precedence")
    if "BUD.md（現在状態） + rules/運用ルール.md（行動規則） > その他の資料" in read_map:
        raise SystemExit("FAIL: AI_READ_MAP still contains the obsolete BUD-first source-of-truth contract")

    print("OK: AI entry documentation contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
