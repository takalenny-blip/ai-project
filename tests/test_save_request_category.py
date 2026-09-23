from scripts.check_save_request_category import validate


def test_missing_kind_is_rejected():
    ok, _ = validate("# 直チャット\n\n本文")
    assert not ok


def test_conversation_record_passes():
    ok, _ = validate("## 保存対象種別\n会話記録\n\n## 本文\n保存対象")
    assert ok


def test_meta_report_with_decision_passes():
    ok, _ = validate(
        "## 保存対象種別\n保存機構メタ報告\n\n"
        "## 新しい決定事項\nworkflowの入口境界を追加する"
    )
    assert ok


def test_meta_report_without_decision_is_rejected():
    ok, _ = validate("## 保存対象種別\n保存機構メタ報告")
    assert not ok


def test_meta_report_without_decision_section_is_rejected():
    ok, _ = validate("## 保存対象種別\n保存機構メタ報告\n\n## 本文\n監査結果")
    assert not ok


def test_unknown_kind_is_rejected():
    ok, _ = validate("## 保存対象種別\nその他")
    assert not ok


def test_real_previous_queue_shape_without_kind_is_rejected():
    content = (
        "【Crow追加監査】#543の保存処理結果を確認した。"
        "保存PRの状態を報告する。"
    )
    ok, _ = validate(content)
    assert not ok
