# BUD — バドのための最上位ダッシュボード

更新日：2026-10-06

## 正本

- 正本リポジトリ：takalenny-blip/ai-project
- 現在状態正本：docs/現在状態.json
- 現在ビュー：BUD.md / docs/引き継ぎ/現在の引き継ぎ.md

## 実行環境

- 現在：**work_pc**
- 退役：vaio_p
- work_pc clone：**unverified**

## 現在地点

**BLOG-0003はHTML・Crowレビュー・画像修正・Blogger下書き投入・実表示確認・公開まで完了。公開後の実ページ取得確認は未確認。**

## 作業キュー

- actionable：4件
- 一覧：
- [BLOG-0003公開後確認] priority=10：GitHub Pages公開後確認を行う
- [WORK-0002] priority=20：save-request-intake.ymlのPR作成失敗を本番経路で確認する
- [WORK-0003] priority=20：save-request-intake.ymlのpushトリガー非発火問題を本番経路で確認する
- [WORK-0004] priority=30：BLOG-0001のGSC Redirect errorを経過観察後に再確認する

## 次の一手（互換ビュー）

- [BLOG-0003公開後確認] 公開済みBLOG-0003の実ページ取得・表示状態を確認し、確認できない場合は未確認として記録する。その後GSC確認へ進む。
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

- 最新保存：**2026-10-05T20-53-20.081260+0900**
- 最新パス：直チャット/2026-10-05_直チャット即時保存_2026-10-05T20-53-20.081260+0900.md
- 旧連番保存：true
- 新タイムスタンプ方式：true

## 移行

- 状態：complete
- 通常工程：DiMORA本来工程へは復帰せず、経験ログを中心としたAI編集・Blogger自動化へ戻る
- 暫定同期：BUD/引き継ぎの手動同期は終了し、現在状態JSONを正本として生成結果を一致検証する