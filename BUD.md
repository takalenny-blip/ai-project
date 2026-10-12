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

**GitHub Pagesを本番公開先として継続運用する。BLOG-0001〜0003は公開済み。2026-10-11、サイトアイコン、BLOG-0001本文・画像、引用・吹き出し・コマンド表示、モバイル表示は問題なしとたかが確認。2026-10-12、たかが作業PCのブラウザーでGitHub Pagesのrobots.txt、sitemap.xml、トップページの正常表示を確認済み。Google Search Console側のサイトマップ処理結果は未確認・外部待ち。公開物の表示確認は完了しており、再確認しない。Bloggerは下書き・表示確認の作業場所。WordPressは本番公開先として扱わない。**

## 作業キュー

- actionable：1件
- 一覧：
- [WP無料ホスティング検証] priority=23：GitHub Pagesを本番公開先として継続運用

  - 未完了工程：ongoing-publication [in_progress] GitHub Pagesを本番公開先として継続運用

## 次の一手（互換ビュー）

- [GITHUB-PAGES-PRODUCTION] GitHub Pagesを本番公開先として継続運用する。robots.txt・sitemap.xml・トップページは表示確認済み。確認済み工程を繰り返さず、Google側のGSC処理結果の変化または新たな不具合・変更要求があった場合のみ対応する。
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

- 最新保存：**2026-10-12T12-42-14.628707+0900**
- 最新パス：直チャット/2026-10-12_直チャット即時保存_2026-10-12T12-42-14.628707+0900.md
- 旧連番保存：true
- 新タイムスタンプ方式：true

## 移行

- 状態：complete
- 通常工程：DiMORA本来工程へは復帰せず、経験ログを中心としたAI編集を継続する。Bloggerは下書き・表示確認、GitHub Pagesを本番公開先とする。WordPressは本番公開先として扱わない。
- 暫定同期：BUD/引き継ぎの手動同期は終了し、現在状態JSONを正本として生成結果を一致検証する