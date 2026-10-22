進めた。現状をGSC側で再確認した。

- `sitemap.xml` は **正常送信済み**
- 最終取得：2026-09-25 00:02 UTC
- エラー：**0**
- サイトマップ登録URL：1
- インデックス済み：**0**
- 対象記事のURL Inspection：**URL is unknown to Google**
- 最終クロール：なし
- 参照URL：なし

つまり、**サイトマップ自体はGoogleに読まれているが、対象記事はまだGoogle側で発見されていない**状態。Google公式でも、この状態ではURL検査からインデックス登録リクエストを行うのが通常の次手とされている。([support.google.com](https://support.google.com/webmasters/answer/9012289?hl=en&utm_source=chatgpt.com))

ただし、今のGSC Wizard接続には**「Request indexing」を直接実行するAPIが見当たらない**。なので、ここで勝手に別の操作へ逸れず、現時点では「サイトマップ送信済み・Google未認識」という事実まで確認した。

**次に必要なのは、Search Console画面から対象URLの「インデックス登録をリクエスト」を実行すること。**  
これはGoogle公式の手順でも、単一URLのクロール要求に使う操作。([support.google.com](https://support.google.com/webmasters/answer/10351509?hl=en&utm_source=chatgpt.com))