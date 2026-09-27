# 直チャット保存要求

## 保存対象種別
会話記録

## 本文

PR #736で意図せず消失した作業キューを復旧する。WORK-0001は完了のまま維持し、作業途中のBLOG-0002と、消失したWORK-0002〜0004を現在状態へ戻す。

復旧根拠：
- BLOG-0002：PR #723が未マージの途中稿で、DIGA／DiMORA部分の肉付けを前提とした作業途中。
- WORK-0002〜0004：PR #736以前のcanonical stateに存在していたキュー項目で、PR #736の差分で消失した。
- WORK-0001：doneを維持する。

<!-- BUD_STATE_PATCH_BEGIN
{
  "work_items": [
    {
      "id": "WORK-0001",
      "title": "GitHub公開リポジトリのpull_request_target既定ポリシー変更への対応を確定・実装・本番検証する",
      "priority": 10,
      "status": "done",
      "depends_on": [],
      "not_before": "2026-09-27",
      "scope": "save_pipeline",
      "target": "2026-11-02までにsave-request-intake.ymlとauto-approve-save-pr.ymlの継続運用方式を確定・実装・本番検証する",
      "evidence": "2026-09-27確認。Actions Policy「save-workflows-pull_request_target」がActiveで、対象2 workflowにpull_request_targetを明示許可。save-request-intake実運用Run #635等、auto-approve-save-pr実運用Run #828等が正常終了。Policy変更・workflow変更は不要と判断。",
      "readiness": "ready",
      "unblock_action": "none",
      "environment": "work_pc",
      "created_at": "2026-09-27",
      "updated_at": "2026-09-27",
      "prerequisites": []
    },
    {
      "id": "BLOG-0002",
      "title": "BLOG-0002「VAIO Pをサーバーにしてみたい」を作業稿から完成へ進める",
      "priority": 10,
      "status": "queued",
      "depends_on": [],
      "not_before": null,
      "scope": "experience_log_to_blogger",
      "target": "DIGA／DiMORA部分を含む未完部分を肉付けし、本文を完成・確認して公開可能な状態にする",
      "evidence": "PR #723で現時点の本文229行を保存済み。PR本文に「次回のDIGA／DiMORA部分の肉付けを前提とした途中稿」と明記。",
      "readiness": "ready",
      "unblock_action": "none",
      "environment": "work_pc",
      "created_at": "2026-09-27",
      "updated_at": "2026-09-27",
      "prerequisites": []
    },
    {
      "id": "WORK-0002",
      "title": "save-request-intake.ymlのPR作成失敗を本番経路で確認する",
      "priority": 20,
      "status": "queued",
      "depends_on": [],
      "not_before": null,
      "scope": "save_pipeline",
      "target": "save-request-intake.ymlのPR作成失敗がジョブ失敗として可視化されることを本番経路で確認する",
      "evidence": "既存のpending_monitoring項目。",
      "readiness": "ready",
      "unblock_action": "none",
      "environment": "work_pc",
      "created_at": "2026-09-27",
      "updated_at": "2026-09-27",
      "prerequisites": []
    },
    {
      "id": "WORK-0003",
      "title": "save-request-intake.ymlのpushトリガー非発火問題を本番経路で確認する",
      "priority": 20,
      "status": "queued",
      "depends_on": [],
      "not_before": null,
      "scope": "save_pipeline",
      "target": "pull_request_target＋キューPR方式への変更後、save-request-intake.ymlの本番経路を確認する",
      "evidence": "既存のpending_monitoring項目。",
      "readiness": "ready",
      "unblock_action": "none",
      "environment": "work_pc",
      "created_at": "2026-09-27",
      "updated_at": "2026-09-27",
      "prerequisites": []
    },
    {
      "id": "WORK-0004",
      "title": "BLOG-0001のGSC Redirect errorを経過観察後に再確認する",
      "priority": 30,
      "status": "queued",
      "depends_on": [],
      "not_before": "2026-10-01",
      "scope": "experience_log_to_blogger",
      "target": "2026-10-01以降にGSC WizardでBLOG-0001 URLのURL検査とインデックス状況を再確認する",
      "evidence": "BLOG-0001のmeta description設定・確認まで完了。現在残っている確認事項はGSC「Redirect error」の経過観察。",
      "readiness": "ready",
      "unblock_action": "none",
      "environment": "work_pc",
      "created_at": "2026-09-27",
      "updated_at": "2026-09-27",
      "prerequisites": []
    }
  ]
}
BUD_STATE_PATCH_END -->