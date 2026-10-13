# BUD — バドのための最上位ダッシュボード

更新日：2026-10-13

## 正本

- 正本リポジトリ：takalenny-blip/ai-project
- 現在状態正本：docs/現在状態.json
- 現在ビュー：BUD.md / docs/引き継ぎ/現在の引き継ぎ.md

## 実行環境

- 現在：**work_pc**
- 退役：vaio_p
- work_pc clone：**unverified**

## 現在地点

**GitHub Pagesを本番公開先として運用する。BLOG-0001〜0003はGitHub Pages公開レーンの対象。2026-10-12、たかが作業PCのブラウザーでGitHub Pagesのrobots.txt、sitemap.xml、トップページの正常表示を確認済み。Google Search Console側のサイトマップ処理結果は未確認・外部待ち。公開物の表示確認は完了しており、再確認しない。Bloggerは下書き・表示確認の作業場所。WordPressは本番公開先として扱わない。**

## 作業キュー

- actionable：3件
- 一覧：
- [AI-MANUAL-PRODUCTION] priority=15：AI作業のセッティングマニュアル本文作成・実地検証
  - 未完了工程：body-drafting [in_progress] セッティングマニュアル本文を作成する
  - 未完了工程：practical-validation [pending] 手順を実環境で通して効果・限界を検証する
  - 未完了工程：publication-preparation [pending] GitHub Pages向け無料記事・サンプルと公開準備を整える
  - 未完了工程：note-demand-validation [pending] noteを候補に需要・購入意向を検証する
- [PAT-EXPIRY] priority=16：保存・承認フローのPAT期限切れ対策
  - 未完了工程：inventory [in_progress] PAT依存箇所・必要権限・API操作を棚卸しする
  - 未完了工程：github-app-design [pending] GitHub App移行方式と秘密鍵管理を設計する
  - 未完了工程：migration-pr [pending] 移行PRを作成する
  - 未完了工程：end-to-end-verification [pending] 保存PRからマージ後CI・正本読み戻しまで検証する
  - 未完了工程：temporary-expiry-notice [pending] 移行完了までのPAT期限前通知を検討する
- [GITHUB-PAGES-PRODUCTION] priority=23：GitHub Pagesを本番公開先として継続運用
  - 未完了工程：ongoing-publication [in_progress] GitHub Pagesを本番公開先として継続運用

## 次の一手（互換ビュー）

- [AI-MANUAL-PRODUCTION] 決定済みの対象読者・無料前提を再検討せず、Noteマニュアル群の統合管理設計に従って、先行するAI作業のセッティングマニュアルの最小提供範囲を定め、本文作成・実地検証を進める。GitHub Pagesで無料公開し、公開後にNote等で需要を検証する。販売、価格、正式仕様、開始時期は未決定のまま管理する。
## 現在の作業レーン

**experience-log → Blogger下書き確認 → GitHub Pages本番公開**

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

- 最新保存：**2026-10-13T16-17-35.747476+0900**
- 最新パス：直チャット/2026-10-13_直チャット即時保存_2026-10-13T16-17-35.747476+0900.md
- 旧連番保存：true
- 新タイムスタンプ方式：true

## 移行

- 状態：complete
- 通常工程：DiMORA本来工程へは復帰せず、経験ログを中心としたAI編集を継続する。Bloggerは下書き・表示確認、GitHub Pagesは本番公開先とする。WordPressは本番公開先として扱わない。
- 暫定同期：BUD/引き継ぎの手動同期は終了し、現在状態JSONを正本として生成結果を一致検証する