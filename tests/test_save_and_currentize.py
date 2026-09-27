from pathlib import Path


def test_save_currentize_does_not_overwrite_canonical_next_design_item():
    source = Path("scripts/save_and_currentize.py").read_text(encoding="utf-8")
    assert 'state["surgery"]["next_design_item"]' not in source
    assert "通常のDiMORA本来工程へ復帰する" not in source


def test_save_currentize_allows_explicit_state_patch_only():
    source = Path("scripts/save_and_currentize.py").read_text(encoding="utf-8")
    assert "--state-patch-file" in source
    assert "merge_patch(state, patch)" in source
    assert "embedded_patch" not in source
    assert "extract_embedded_state_patch" not in source
    assert "BUD_STATE_PATCH_BEGIN" not in source
