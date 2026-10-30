#!/usr/bin/env python3
"""Check the repository entry documents for the current source-of-truth contract."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
AUDIT_RULE = ROOT / "rules" / "構造変更時・独立監査ガード.md"
OPERATING_RULE = ROOT / "rules" / "運用ルール.md"
CHAT_RULE = ROOT / "rules" / "直チャット保存.md"
BLOG_RULE = ROOT / "rules" / "ブログ制作.md"
RULES_README = ROOT / "rules" / "README.md"
READ_MAP = ROOT / "docs" / "AI_READ_MAP.md"


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise SystemExit(f"FAIL: {label}: missing required text: {needle}")


def main() -> int:
    readme = README.read_text(encoding="utf-8")
    audit_rule = AUDIT_RULE.read_text(encoding="utf-8")
    operating_rule = OPERATING_RULE.read_text(encoding="utf-8")
    chat_rule = CHAT_RULE.read_text(encoding="utf-8")
    blog_rule = BLOG_RULE.read_text(encoding="utf-8")
    rules_readme = RULES_README.read_text(encoding="utf-8")
    read_map = READ_MAP.read_text(encoding="utf-8")

    require(readme, "日常作業キューの唯一の正本はDropboxの固定ファイル", "README Dropbox queue source")
    require(readme, "BUD.md", "README generated view reference")
    require(readme, "機械生成されるビュー", "README generated-view contract")
    require(readme, "これらを現在状態の正本として直接編集してはいけません", "README no-direct-edit contract")
    require(readme, "構造変更時だけ深い独立監査を起動し", "README conditional audit trigger")
    require(readme, "起動時・再開時の現在化ゲート", "README startup currentization gate")
    require(readme, "docs/現在状態.json", "README canonical startup state")
    require(readme, "日常作業キューと優先度・状態・次のアクションはDropboxの固定ファイル", "README Dropbox startup queue")
    require(readme, "Dropboxボードを読み取れない場合は作業キュー利用不可として停止", "README no stale queue fallback")

    require(audit_rule, "構造変更時だけ", "audit trigger")
    require(audit_rule, "scripts/check_repo_integrity.py", "mechanical integrity guard")
    require(audit_rule, "scripts/save_and_currentize.py", "atomic save guard")
    require(audit_rule, "次に参加するAI", "next-agent safety check")
    require(audit_rule, "通常工程へ戻る", "return-to-normal-operation rule")
    require(operating_rule, "GitHub上の `docs/現在状態.json` を最初に直接読み", "rule canonical startup state")
    require(operating_rule, "操作別ルールの読み込みゲート", "operation-specific routing gate")
    require(operating_rule, "rules/直チャット保存.md", "chat rule route")
    require(operating_rule, "rules/ブログ制作.md", "blog rule route")
    require(operating_rule, "宣言だけでは読み込み済みと認めない", "read-before-declare gate")
    require(chat_rule, "### 4-1. 保存目的", "chat rule content moved")
    require(blog_rule, "7-5-4-1. ブログ制作における勝手な判断", "blog top rule moved")
    require(blog_rule, "## 8. Blogger掲載用HTML整形規約", "blog HTML rules moved")
    require(rules_readme, "rules/直チャット保存.md", "rules README chat route")
    require(rules_readme, "rules/ブログ制作.md", "rules README blog route")
    if "### 4-1. 保存目的" in operating_rule or "## 7. ブログ記事作成時のインタビュー方針" in operating_rule or "## 8. Blogger掲載用HTML整形規約" in operating_rule:
        raise SystemExit("FAIL: operation-specific rule body remains duplicated in common operating rule")

    require(read_map, "Dropbox `/ChatGPT/Dropbox作業管理統合ボード.xlsx` — 日常作業キュー・優先度・状態・次のアクションの唯一の正本", "AI read map Dropbox queue source")
    require(read_map, "`BUD.md` / `docs/引き継ぎ/現在の引き継ぎ.md` — 正本から生成された互換ビュー", "AI read map generated views")
    require(read_map, "Dropboxボードを読み取れない場合は停止し、旧GitHubキューや古い生成ビューへフォールバックしない", "AI read map no stale fallback")
    if "BUD.md（現在状態） + rules/運用ルール.md（行動規則） > その他の資料" in read_map:
        raise SystemExit("FAIL: AI_READ_MAP still contains the obsolete BUD-first source-of-truth contract")

    print("OK: AI entry documentation contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
