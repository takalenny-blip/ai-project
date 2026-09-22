# BUD — バドのための最上位ダッシュボード

更新日：2026-09-23

## 正本

- 正本リポジトリ：takalenny-blip/ai-project
- 現在状態正本：docs/現在状態.json
- 現在ビュー：BUD.md / docs/引き継ぎ/現在の引き継ぎ.md

## 実行環境

- 現在：**work_pc**
- 退役：vaio_p
- work_pc clone：**unverified**

## 現在地点

**DIGA / DiMORA自動化は、現行のバド単独運用では実機側の取得・操作まで完遂できないため断念。既存の正規化検証、work_pc原本→Dropbox→Bud取得の実証、変更検知等の成果は履歴・経験資産として保持し、本線は最終ゴールである経験ログを中心としたAI編集・Blogger自動化へ戻す。**

## 次の一手

- 環境：**work_pc**
- 目的：**BLOG-0001の公開準備を進めつつ、経験ログを中心としたAI編集・Blogger自動化へ戻る**
- 根拠：DIGA / DiMORA自動化 本線断念の決定記録
- 状態：ready
## 現在の作業レーン

**experience-log → Blogger自動化**

「一括改修」は設計を一括で行う意味であり、実装は小さな検証単位で進める。

順序：**現状棚卸し → 大手術の設計 → 採用する改善を確定 → 小さな検証単位で順次実装 → 検証**。

- 棚卸し：complete
- 設計：revised_complete
- 採用：complete
- 実装：current_views_migrated_ci_guard_added
- 検証：done

## 現在状態モデル

- docs/現在状態.jsonを唯一の現在状態正本とし、BUD.mdとdocs/引き継ぎ/現在の引き継ぎ.mdを生成ビューにする
- 自動生成：第1実装済み。scripts/generate_current_views.pyが候補ビューを決定的に生成し、GitHub Actionsで決定性と完全一致を検証する。

## 直チャット

- 最新保存：**2026-09-23T07-59-05.003501+0900**
- 最新パス：直チャット/2026-09-23_直チャット即時保存_2026-09-23T07-59-05.003501+0900.md
- 旧連番保存：true
- 新タイムスタンプ方式：true

## 移行

- 状態：complete
- 通常工程：DiMORA本来工程へは復帰せず、経験ログを中心としたAI編集・Blogger自動化へ戻る
- 暫定同期：BUD/引き継ぎの手動同期は終了し、現在状態JSONを正本として生成結果を一致検証する