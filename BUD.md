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

**WordPress公開済みのBLOG-0001・BLOG-0002・BLOG-0003を本番公開先として継続運用する。Bloggerは下書き・表示確認の作業場所、GitHub Pagesだけを予備公開サイトとする。サイトアイコン画像はPR #962で保存済みだが、WordPressへの適用・実表示確認は未確認。Cocoonスキン「モノクロ」と引用記号・吹き出し・コマンド／スクリプト表示の見直しは、たかの確認により完了。GitHub Pagesのトップページは現在404ではない（2026-10-11、たか確認）。sitemap.xmlのブラウザーHTTP 200・application/xml・XML内4 URLの表示とURLライブテスト成功を確認済み。GSCのサイトマップ取得エラーの原因切り分けは実施済みで、現時点はGoogle側の処理待ち。GSCでの正常化は未確認。URL検査ではVAIO P記事は登録済み、GitHub編記事はクロール済み・インデックス未登録、トップページは未認識だが登録リクエストはキュー追加済み。GitHub Pagesの未確認URLとWordPressのインデックス状況は未確認。Bloggerは下書き・表示確認用としてnoindex化して閉じる方針。2026-10-09に設定変更したとのユーザー報告あり。設定保存・記事応答・Google検索結果からの除外は未検証だが、2026-10-11のユーザー判断により追加確認の作業キューから除外。**

## 作業キュー

- actionable：2件
- 一覧：
- [GSC-確認] priority=20：GSCのサイトマップ取得失敗を切り分け、3サイト別インデックス状況を確認する
  - 未完了工程：github-pages-sitemap-retrieval [waiting_external] GSC sitemap.xml取得失敗の原因切り分け
  - 未完了工程：site-index-status-check [in_progress] GitHub Pages・WordPressのインデックス登録状況を個別確認
- [WP無料ホスティング検証] priority=23：WordPress公開環境の整備
  - 未完了工程：wp-icon [in_progress] WordPressへサイトアイコン画像を適用して実表示を確認する
  - 未完了工程：operation-check [pending] WordPressの表示・更新・運用確認
  - 未完了工程：wordpress-production-judgment [pending] WordPress本番化を判断し現在状態へ反映

## 次の一手（互換ビュー）

- [GSC-確認] Google側のGSC sitemap.xml処理待ちを維持しつつ、未確認のGitHub Pages URLとWordPressのインデックス状況を個別確認する。サイトマップの原因切り分けとGSCサイトマップ詳細の再確認は、Google側の処理結果が変化するまで繰り返さない。GSCプロパティ登録は再実行しない。
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

- 最新保存：**2026-10-11T08-04-06.801000+0900**
- 最新パス：直チャット/2026-10-11_直チャット即時保存_2026-10-11T08-04-06.801000+0900.md
- 旧連番保存：true
- 新タイムスタンプ方式：true

## 移行

- 状態：complete
- 通常工程：DiMORA本来工程へは復帰せず、経験ログを中心としたAI編集・Blogger自動化へ戻る
- 暫定同期：BUD/引き継ぎの手動同期は終了し、現在状態JSONを正本として生成結果を一致検証する