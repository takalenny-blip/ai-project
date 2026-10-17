from pathlib import Path


def test_save_currentize_does_not_overwrite_canonical_next_design_item():
    source = Path("scripts/save_and_currentize.py").read_text(encoding="utf-8")
    assert 'state["surgery"]["next_design_item"]' not in source
    assert "通常のDiMORA本来工程へ復帰する" not in source


def test_save_currentize_allows_explicit_state_patch():
    source = Path("scripts/save_and_currentize.py").read_text(encoding="utf-8")
    assert "--state-patch-file" in source
    assert "embedded_patch" in source


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
