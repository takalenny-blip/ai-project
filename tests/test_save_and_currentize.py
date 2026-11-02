from pathlib import Path

def test_save_updates_operating_rules_not_retired_state_views():
    source = Path("scripts/save_and_currentize.py").read_text(encoding="utf-8")
    assert "rules/運用ルール.md" in source
    assert "docs/現在状態.json" not in source
    assert "BUD.md" not in source
    assert "現在の引き継ぎ.md" not in source
    assert "--state-patch-file" not in source

def test_retired_embedded_patch_is_stripped_without_parsing_its_body():
    from scripts.save_and_currentize import strip_retired_embedded_state_patch
    content = (
        "historical record\n"
        "<!-- BUD_STATE_PATCH_BEGIN\n"
        "this is deliberately not JSON and must never be parsed\n"
        "BUD_STATE_PATCH_END -->\n"
        "historical tail\n"
    )
    cleaned, found = strip_retired_embedded_state_patch(content)
    assert found is True
    assert "BUD_STATE_PATCH_BEGIN" not in cleaned
    assert "not JSON" not in cleaned
    assert "historical record" in cleaned
    assert "historical tail" in cleaned

def test_content_without_retired_embedded_patch_is_unchanged():
    from scripts.save_and_currentize import strip_retired_embedded_state_patch
    content = "ordinary direct-chat record\n"
    cleaned, found = strip_retired_embedded_state_patch(content)
    assert cleaned == content
    assert found is False

def test_update_latest_save_record_changes_only_the_three_pointer_fields():
    from scripts.save_and_currentize import update_latest_save_record
    rules = (
        "#### 直チャット保存記録（現行）\n"
        "- 最新保存：`old`\n"
        "- 原本：`old.md`\n"
        "- 内容SHA：`oldsha`\n"
        "- 既存の連番方式ファイルは履歴として保持する。\n"
    )
    updated = update_latest_save_record(rules, "2026-11-02T12-00-00.123456+0900", "直チャット/new.md", "abc123")
    assert "- 最新保存：`2026-11-02T12-00-00.123456+0900`" in updated
    assert "- 原本：`直チャット/new.md`" in updated
    assert "- 内容SHA：`abc123`" in updated
    assert "既存の連番方式ファイルは履歴として保持する。" in updated
