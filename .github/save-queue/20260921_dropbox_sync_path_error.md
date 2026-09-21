# 直前回答＋ユーザー追記

## 直前の回答

Dropbox接続できた。**Dropbox認証は通ってる。**

ただ、今のDropbox内検索では：

- `dimora-favorite-programs.json` → **0件**
- `dimora` → **0件**

だった。

つまり、**接続経路そのものは成功**。次の問題は「work_pcの原本JSONがDropboxへまだ同期されていない」か「同期先が別フォルダ」のどちらか。

しかも、PR #234の正規化検証は完了済みなので、**ここでは再正規化しない**。  
まずWindows側で、作った同期スクリプトを1回実行すればいい。

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\sync_dimora_to_dropbox.ps1
```

ただしこれは**GitHubリポジトリを置いているwork_pc上で実行**する。

実行結果が `SYNCED ...` になったら、俺がすぐDropboxを再検索して原本を確認する。

## ユーザー追記

「直前の回答書き込んで。-File パラメーターの引数 '.\scripts\sync_dimora_to_dropbox.ps1' は存在しません。既存の '.ps1' ファイルのパスを -File パラメーターの引数として指定してください。やり取り書き込んで。」
