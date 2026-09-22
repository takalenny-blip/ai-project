# 直チャット保存要求：Blogger設定接続提案

## User
わかった。公式APIをChatGPTの設定から追加できるか試すしかないと思うが？その提案がなぜ出ない？頼りない。やりとり書き込んで

## Bud
たか、その指摘はその通り。**「Blogger APIが存在する」まで確認したなら、次に「ChatGPTの設定→Apps/PluginsでBlogger、またはカスタムMCP/アプリとして接続できるかを確認する」という提案を出すべきだった。** そこを出さなかったのは、バドの切り分け不足。

いま公式情報を確認した。ChatGPTでは **Settings → Apps / Plugins** から利用可能なアプリを接続でき、表示されるアプリはプラン・地域・アカウント等で変わる。citeturn0search6turn0search9

ただし重要な点がある。現在のOpenAI公式仕様では、**カスタムMCPで書き込み・変更まで使えるFull MCPはBusiness / Enterprise / Edu向け**で、ProはカスタムMCPをDeveloper modeで接続できてもread/fetch権限までと案内されている。さらに、OpenAI提供アプリは現時点ではwrite actionをサポートしないと明記されている。citeturn0search0

だから、まず試すべきことはこれ。

1. ChatGPTの **設定 → Apps（または Plugins）** を開く。
2. 「Blogger」またはGoogle系のBlogger連携が表示されるか確認。
3. 表示されれば接続して、**投稿作成／公開の権限まで要求されるか**を見る。
4. 表示されなければ、次に「カスタムアプリ / MCPを追加できる設定が、このアカウントで使えるか」を確認する。
5. そこでwrite権限が使えないなら、**ChatGPTから直接Blogger APIを呼ぶ方式は現環境では不可**と切り分ける。
6. その場合は、別経路（GitHub Actions等）からBlogger APIを呼ぶ構成を検討する。

つまり、**「APIはある」→「ChatGPT側に接続口を追加できるか」→「write権限があるか」**の3段階で確認するのが正しい。前回は2段目を提案しなかった。そこは俺のミス。

【作業】
- 公式仕様を再確認。
- ChatGPT側のApps/Plugins接続可能性と、MCPのwrite権限制約を確認。
- BLOG-0001本文・Blogger HTMLは変更していない。
- 次に確認する対象は「ChatGPT設定からBlogger接続を追加できるか」。

【保存】
- 今回の「やりとり書き込んで」を保存対象として正規保存キューへ投入する。
- 直前の保存要求はPR #452が後続の自動同期PR #453で処理済みなので、今回の保存は別件として扱う。
- 今回は新しい保存キューを作成し、通常の自動保存フローに渡す。
