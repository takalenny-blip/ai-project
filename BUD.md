# BUD — バドのための最上位ダッシュボード

更新日：2026-09-27

## 正本

- 正本リポジトリ：takalenny-blip/ai-project
- 現在状態正本：docs/現在状態.json
- 現在ビュー：BUD.md / docs/引き継ぎ/現在の引き継ぎ.md

## 実行環境

- 現在：**work_pc**
- 退役：vaio_p
- work_pc clone：**unverified**

## 現在地点

**BLOG-0001は公開済み。改善候補の整理、次に実施する1件の確定、Blogger側の検索向け説明（meta description）候補文の作成・確認・設定・確認まで完了。現在はGSC「Redirect error」の経過観察中。**

## 作業キュー

- actionable：0件
- 一覧：
- actionableな作業なし

## 次の一手（互換ビュー）

- actionableな作業なし
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
- 自動生成：第2実装済み。work_itemsを唯一の作業キュー正本とし、next_stepはwork_itemsから導出する互換ビュー。生成ビューでactionable一覧を表示し、依存関係・期限・優先順位を機械検証する。

## 直チャット

- 最新保存：**2026-09-27T16-42-03.215008+0900**
- 最新パス：直チャット/2026-09-27_直チャット即時保存_2026-09-27T16-42-03.215008+0900.md
- 旧連番保存：true
- 新タイムスタンプ方式：true

## 移行

- 状態：complete
- 通常工程：DiMORA本来工程へは復帰せず、経験ログを中心としたAI編集・Blogger自動化へ戻る
- 暫定同期：BUD/引き継ぎの手動同期は終了し、現在状態JSONを正本として生成結果を一致検証する