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


def test_real_previous_queue_shapes_without_kind_are_rejected():
    contents = [
        """# 直前回答の保存依頼

## 対象
PR #533 の承認・マージ結果に関する直前の回答。

## 記録
- PR #533：taka2-dev APPROVED
- squash merge：完了
- main readback：確認済み
""",
        """# 直前回答の保存依頼

## 対象
#530 の停止原因を確認した直前回答。

## 記録
- #530 の当時のCI失敗は、PR #533 で修正した import 問題。
- 次に必要なのは #530 の再チェック／再評価。
""",
        """# 直前回答の保存依頼

## 対象
保存処理がループしている可能性についての直前回答。

## 記録
- 保存処理の経路がループ気味になっていると判断。
- #534、#536 と保存PRを増やしてしまった。
""",
    ]
    assert all(not validate(content)[0] for content in contents)
