#!/usr/bin/env python3
"""Check repository entry documents for the single-source operating-rules contract."""
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
    readme=README.read_text(encoding="utf-8")
    audit_rule=AUDIT_RULE.read_text(encoding="utf-8")
    operating_rule=OPERATING_RULE.read_text(encoding="utf-8")
    chat_rule=CHAT_RULE.read_text(encoding="utf-8")
    blog_rule=BLOG_RULE.read_text(encoding="utf-8")
    rules_readme=RULES_README.read_text(encoding="utf-8")
    read_map=READ_MAP.read_text(encoding="utf-8")

    require(readme,"現在状態・共通運用ルールの唯一の正本","README single current-state source")
    require(readme,"rules/運用ルール.md","README rules source")
    require(readme,"日常作業キュー","README Dropbox queue role")
    require(readme,"Dropboxボードを読み取れない場合は停止","README stop without queue")
    require(readme,"画像","README image prohibition")
    require(operating_rule,"現在状態・共通運用ルールの唯一の正本","rule single source")
    require(operating_rule,"操作別ルールの読み込みゲート","operation-specific routing gate")
    require(operating_rule,"rules/直チャット保存.md","chat rule route")
    require(operating_rule,"rules/ブログ制作.md","blog rule route")
    require(operating_rule,"宣言だけでは読み込み済みと認めない","read-before-declare gate")
    require(audit_rule,"構造変更時だけ","audit trigger")
    require(audit_rule,"scripts/check_repo_integrity.py","mechanical integrity guard")
    require(audit_rule,"scripts/save_and_currentize.py","atomic save guard")
    require(audit_rule,"次に参加するAI","next-agent safety check")
    require(chat_rule,"### 4-1. 保存目的","chat rule content")
    require(blog_rule,"7-5-4-1. ブログ制作における勝手な判断","blog top rule")
    require(blog_rule,"## 8. Blogger掲載用HTML整形規約","blog HTML rules")
    require(rules_readme,"rules/直チャット保存.md","rules README chat route")
    require(rules_readme,"rules/ブログ制作.md","rules README blog route")
    require(read_map,"rules/運用ルール.md","read map operating rules source")
    require(read_map,"Dropbox `/ChatGPT/Dropbox作業管理統合ボード.xlsx`","read map Dropbox queue")
    for legacy in ("docs/現在状態.json","BUD.md","docs/引き継ぎ/現在の引き継ぎ.md"):
        if legacy in readme or legacy in read_map:
            raise SystemExit(f"FAIL: entry documents still direct readers to retired source: {legacy}")
    print("OK: AI entry documentation contract")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
