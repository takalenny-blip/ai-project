# 経験ログ → Blogger下書きpayload 第4実装

## 目的

根拠照合済みの記事候補を、Blogger APIの下書き作成に渡せる決定的なpayloadへ変換する。

## 境界

- 入力：第3実装で根拠照合済みの記事候補JSON
- 出力：Blogger下書き作成APIで扱える最小payload（title / content）
- HTML：記事候補の導入・本文・知見・未確定事項をHTMLへ変換し、本文中の文字はHTMLエスケープする
- しないこと：Blogger API呼び出し、認証、公開、外部通信

## 完了条件

1. 必須記事項目がない入力を拒否する。
2. titleをそのままpayloadのtitleへ渡す。
3. intro/body/insights/uncertain_or_notesを決定的なHTML contentへ変換する。
4. HTMLとして解釈される文字をエスケープする。
5. 同じ入力から同じpayloadになることをテストする。
6. この段階ではBloggerへの実送信・認証情報を導入しない。

## 次段

このpayloadをBlogger APIへ下書きとして送る実通信工程を、認証・公開を分離した小さな検証単位として追加する。
