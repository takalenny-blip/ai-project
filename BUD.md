# BUD — バドのための最上位ダッシュボード

更新日：2026-09-30

## 正本

- 正本リポジトリ：takalenny-blip/ai-project
- 現在状態正本：docs/現在状態.json
- 現在ビュー：BUD.md / docs/引き継ぎ/現在の引き継ぎ.md

## 実行環境

- 現在：**work_pc**
- 退役：vaio_p
- work_pc clone：**unverified**

## 現在地点

**BLOG-0001は公開済み。GSC「Redirect error」は経過観察中。BLOG-0002「VAIO Pをサーバーにしてみたい」はブロック3まで完成し、PR #756をマージして一区切り。次はBLOG-0003としてGitHub編へ進む。**

## 作業キュー

- actionable：3件
- 一覧：
- [BLOG-0003] priority=10：BLOG-0003「GitHub編」を作成する
- [WORK-0002] priority=20：save-request-intake.ymlのPR作成失敗を本番経路で確認する
- [WORK-0003] priority=20：save-request-intake.ymlのpushトリガー非発火問題を本番経路で確認する

## 次の一手（互換ビュー）

- [BLOG-0003] BLOG-0002の続きとして、AIとのやりとりをどう残し、GitHubを使ってどう管理するようになったかを、一次記録を中心に記事化する
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

- 最新保存：**2026-09-30T21-44-01.422513+0900**
- 最新パス：直チャット/2026-09-30_直チャット即時保存_2026-09-30T21-44-01.422513+0900.md
- 旧連番保存：true
- 新タイムスタンプ方式：true

## 移行

- 状態：complete
- 通常工程：DiMORA本来工程へは復帰せず、経験ログを中心としたAI編集・Blogger自動化へ戻る
- 暫定同期：BUD/引き継ぎの手動同期は終了し、現在状態JSONを正本として生成結果を一致検証する