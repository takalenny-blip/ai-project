# DiMORA Chromium取得テスト

## 目的

DiMORAの実データ正規化はPR #234で完了済み。このテストは別工程として、VAIO P + Chromiumの認証済みDiMORAページから機械可読データへ到達できるかを小さく実証する。

## 実行

VAIO PでChromiumを終了した状態から、認証済みプロファイルを指定して実行する。

```bash
scripts/probe_dimora_chromium.sh 'https://dimora.jp/（認証済みDiMORAページ）' /tmp/dimora-page.html
```

成功条件は、取得DOMに `GL_FAVPGM_DATA` が存在すること。

## 重要な境界

- Cookie、パスワード、セッション情報はGitHubへ保存しない。
- HTML取得物はリポジトリへ保存しない。
- これは取得経路の疎通確認であり、既存の実データ正規化検証を再実行するものではない。
- `GL_FAVPGM_DATA` が取得できた後に、record[]の抽出方法を実ページで確定する。
