# BUD — バドのための最上位ダッシュボード

更新日：2026-09-15

## 正本

- 正本リポジトリ：`takalenny-blip/ai-project`
- 現在状態正本：`docs/現在状態.json`
- 現在ビュー：BUD.md / docs/引き継ぎ/現在の引き継ぎ.md

## 現在の作業レーン

**ai-project運用基盤の大手術（一括改修）**

「一括改修」は設計を一括で行う意味であり、実装は小さな検証単位で進める。

順序：**現状棚卸し → 大手術の設計 → 採用する改善を確定 → 小さな検証単位で順次実装 → 検証**。

- 棚卸し：complete
- 設計：revised_complete
- 採用：complete
- 実装：current_views_migrated_ci_guard_added
- 検証：three_ci_error_notifications_pending_root_cause

## 現在状態モデル

- docs/現在状態.jsonを唯一の現在状態正本とし、BUD.mdとdocs/引き継ぎ/現在の引き継ぎ.mdを生成ビューにする
- 自動生成：第1実装済み。scripts/generate_current_views.pyが候補ビューを決定的に生成し、GitHub Actionsで決定性を検証する。run #5/#6で決定性検証はsuccess。既存BUD/引き継ぎを生成結果へ移行し、CIで完全一致を機械検証する段階へ進んだ。今回3件のエラーメールを受領したため、失敗runのjob/logを直接確認して原因を確定するまで移行完了とは扱わない。現時点で正本JSONとBUD/引き継ぎの保存番号不一致を確認済み。

## 直チャット

- 最新保存：**034**
- 最新パス：`直チャット/2026-09-15_直チャット即時保存_034.md`
- 旧連番保存：True
- 新タイムスタンプ方式：True

## 移行

- 状態：generated_views_active_ci_verification_pending
- 通常工程：自動生成への移行が完了するまでDiMORA本来工程は再開せず、大手術を優先する
- 暫定同期：BUD/引き継ぎの手動同期は終了し、現在状態JSONを正本として生成結果を一致検証する

## 次の一手

**正本JSONとBUD/引き継ぎの保存番号不一致を最小修正し、完全一致CIで再検証する。成功後に移行完了側へ状態を更新する。**
