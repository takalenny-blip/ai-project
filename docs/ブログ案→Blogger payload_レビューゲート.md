# ブログ案 → Blogger payload ゲート

ブログ案を作成しただけではBlogger payloadを投稿可能状態にしない。

## 契約

- ブログ案の採否判断が `pending` の間は payload_ready=false。
- `approved` の場合だけ payload_ready=true。
- このゲート自体はBlogger APIを呼ばない。
- 公開・認証・外部通信は行わない。

## 現在

EXP-0000000050のブログ案は現在 `pending` のため、Blogger payload作成工程はレビュー完了まで停止する。
