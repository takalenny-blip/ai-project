# BUD — バドのための最上位ダッシュボード

更新日：2026-10-11

## 正本

- 正本リポジトリ：takalenny-blip/ai-project
- 現在状態正本：docs/現在状態.json
- 現在ビュー：BUD.md / docs/引き継ぎ/現在の引き継ぎ.md

## 実行環境

- 現在：**work_pc**
- 退役：vaio_p
- work_pc clone：**unverified**

## 現在地点

**WordPress公開済みのBLOG-0002・BLOG-0003を本番公開先として継続運用する。Bloggerは下書き・表示確認の作業場所、GitHub Pagesだけを予備公開サイトとする。サイトアイコン画像はPR #962で保存済みだが、WordPressへの適用・実表示確認は未確認。Cocoonスキン「モノクロ」と引用記号・吹き出し・コマンド／スクリプト表示の見直しは、たかの確認により完了。GSCでは3サイトを別々に登録済み。2026-10-10、GitHub Pagesのsitemap.xmlは作業PCのブラウザーでHTTP 200 OK、Content-Type: application/xml、XML内4 URLすべて表示可能と確認。一方、GSCは最終読み込み2026/10/09、検出ページ0・動画0、追加エラー詳細なしで「サイトマップを読み込めませんでした」が継続。sitemap.xml自体のライブテストはクロール許可・取得・インデックス許可がすべて成功だが、GSCのサイトマップ処理正常化は未確認。URL検査ではVAIO P記事は登録済み、GitHub編記事はクロール済み・インデックス未登録、トップページは未認識。トップページのライブテストは2026/10/10 17:53:48に取得成功、クロール・インデックス許可あり、正規URLは自身。インデックス登録リクエストはキュー追加済みだが、登録結果は未確認。GitHub Pagesの残るURLとWordPressのインデックス状況も未確認。Bloggerは3記事の登録成功を2026-10-08に確認済み。2026-10-09にBlogger検索対象外化の設定を行ったとの報告があるが、設定保存・記事応答・Google検索結果からの除外は未確認。**

## 作業キュー

- actionable：3件
- 一覧：
- [GSC-確認] priority=20：GSCのサイトマップ取得失敗を切り分け、3サイト別インデックス状況を確認する
  - 未完了工程：github-pages-sitemap-retrieval [in_progress] GSC sitemap.xml取得失敗の原因切り分け
  - 未完了工程：site-index-status-check [in_progress] GitHub Pages・WordPressのインデックス登録状況を個別確認
- [BLOGGER-SEARCH-EXCLUSION] priority=22：BloggerをGoogle検索対象外にし、公開済み3記事の反映を確認する
  - 未完了工程：recheck-saved-settings [pending] 設定を開き直し、3項目の保存状態を確認
  - 未完了工程：verify-article-noindex [pending] 公開済み3記事がnoindexを返すことを確認
  - 未完了工程：verify-google-removal [pending] Google再クロール後、公開済み3記事が検索結果から外れたことを確認
- [WP無料ホスティング検証] priority=23：WordPress公開環境の整備
  - 未完了工程：wp-icon [in_progress] WordPressへサイトアイコン画像を適用して実表示を確認する
  - 未完了工程：operation-check [pending] WordPressの表示・更新・運用確認
  - 未完了工程：wordpress-production-judgment [pending] WordPress本番化を判断し現在状態へ反映

## 次の一手（互換ビュー）

- [GSC-確認] GitHub PagesのGSC sitemap.xml取得失敗の原因切り分けを継続する。確認済みのブラウザーHTTP応答とライブテスト取得成功をGSCサイトマップ処理成功と混同しない。GitHub PagesのURL検査結果を記録し、トップページはインデックス登録リクエスト済みのため結果を待つ。未確認のai-blog-start.htmlとWordPressのインデックス状況を個別確認する。Bloggerの登録済み3記事は再確認しない。GSCプロパティ登録は再実行しない。
## 現在の作業レーン

**experience-log → Blogger下書き確認 → WordPress本番公開**

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

- 最新保存：**2026-10-10T20-06-22.368533+0900**
- 最新パス：直チャット/2026-10-10_直チャット即時保存_2026-10-10T20-06-22.368533+0900.md
- 旧連番保存：true
- 新タイムスタンプ方式：true

## 移行

- 状態：complete
- 通常工程：DiMORA本来工程へは復帰せず、経験ログを中心としたAI編集・Blogger自動化へ戻る
- 暫定同期：BUD/引き継ぎの手動同期は終了し、現在状態JSONを正本として生成結果を一致検証する