from scripts.save_direct_chat import strip_retired_embedded_state_patch


def test_retired_embedded_state_patch_is_removed_without_parsing():
    content = "start\n<!-- BUD_STATE_PATCH_BEGIN\nnot JSON\nBUD_STATE_PATCH_END -->\nend\n"
    cleaned, found = strip_retired_embedded_state_patch(content)
    assert found is True
    assert "BUD_STATE_PATCH_BEGIN" not in cleaned
    assert "not JSON" not in cleaned
    assert "start" in cleaned and "end" in cleaned


def test_content_without_retired_patch_is_unchanged():
    content = "ordinary direct-chat record\n"
    cleaned, found = strip_retired_embedded_state_patch(content)
    assert cleaned == content
    assert found is False
