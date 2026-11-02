#!/usr/bin/env python3
"""Check repository entry documents against the single operating-rule source."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "README": ROOT / "README.md",
    "operating_rule": ROOT / "rules" / "運用ルール.md",
    "chat_rule": ROOT / "rules" / "直チャット保存.md",
    "blog_rule": ROOT / "rules" / "ブログ制作.md",
    "rules_readme": ROOT / "rules" / "README.md",
    "read_map": ROOT / "docs" / "AI_READ_MAP.md",
}
RETIRED = ("docs/現在状態.json", "BUD.md", "docs/引き継ぎ/現在の引き継ぎ.md")

def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise SystemExit(f"FAIL: {label}: missing required text: {needle}")

def main() -> int:
    content = {}
    for name, path in FILES.items():
        if not path.is_file():
            raise SystemExit(f"FAIL: required entry document missing: {path.relative_to(ROOT)}")
        content[name] = path.read_text(encoding="utf-8")
    require(content["README"], "rules/運用ルール.md", "README common rule entry")
    require(content["README"], "Dropboxの固定ファイル", "README Dropbox queue")
    require(content["README"], "送信前ゲート", "README send gate")
    require(content["operating_rule"], "日常作業キューの唯一の正本", "operating rule queue source")
    require(content["operating_rule"], "rules/直チャット保存.md", "chat operation rule route")
    require(content["operating_rule"], "rules/ブログ制作.md", "blog operation rule route")
    require(content["chat_rule"], "scripts/save_direct_chat.py", "single-file save processor")
    require(content["blog_rule"], "Blogger掲載用HTML整形規約", "blog operation rule remains available")
    require(content["rules_readme"], "rules/運用ルール.md", "rules readme common rule source")
    require(content["read_map"], "Dropbox", "read map Dropbox queue")
    for name, text in content.items():
        for retired in RETIRED:
            if retired in text:
                raise SystemExit(f"FAIL: {name} still references retired current-state file: {retired}")
    for name in ("README", "operating_rule", "chat_rule", "rules_readme", "read_map"):
        if "save_and_currentize.py" in content[name] or "current_state_guard.py" in content[name] or "generate_current_views.py" in content[name]:
            raise SystemExit(f"FAIL: {name} still references retired current-state machinery")
    print("OK: repository entry documents use the single operating-rule source")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
