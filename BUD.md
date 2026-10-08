# BUD — バドのための最上位ダッシュボード

更新日：2026-10-08

## 正本

- 正本リポジトリ：takalenny-blip/ai-project
- 現在状態正本：docs/現在状態.json
- 現在ビュー：BUD.md / docs/引き継ぎ/現在の引き継ぎ.md

## 実行環境

- 現在：**work_pc**
- 退役：vaio_p
- work_pc clone：**unverified**

## 現在地点

**BLOG-0003は公開確認まで完了。GSCは所有権確認・Google登録リクエスト完了、現在Google側の処理待ち。WP無料ホスティング検証はWordPress導入・Script Installer再確認・HTTPS・サイトマップ確認まで完了し、Google登録は処理中、広告条件確認から再開する。**

## 作業キュー

- actionable：1件
- 一覧：
- [WP無料ホスティング検証] priority=23：完全無料のWordPress公開環境を検証する

## 次の一手（互換ビュー）

- [WP無料ホスティング検証] 完全無料・広告掲載可能・WordPress対応のホスティング環境を1つ選定し、検証用サイトを構築して、HTTPS・WordPress動作・サイトマップ・Google登録可否・広告掲載条件を実測する。本番移行やBLOG-0004の制作先変更は検証結果を確認してから判断する。
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

- 最新保存：**2026-10-06T21-08-38.893676+0900**
- 最新パス：直チャット/2026-10-06_直チャット即時保存_2026-10-06T21-08-38.893676+0900.md
- 旧連番保存：true
- 新タイムスタンプ方式：true

## 移行

- 状態：complete
- 通常工程：DiMORA本来工程へは復帰せず、経験ログを中心としたAI編集・Blogger自動化へ戻る
- 暫定同期：BUD/引き継ぎの手動同期は終了し、現在状態JSONを正本として生成結果を一致検証する