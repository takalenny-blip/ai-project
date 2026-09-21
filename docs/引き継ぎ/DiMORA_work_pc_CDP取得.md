# work_pc DiMORA CDP取得

認証済みDiMORAページをwork_pc上のChrome/Edgeから取得し、ページ内の \`GL_FAVPGM_DATA.record[]\` をDropboxへ保存する本線用プローブ。

実行:
\`powershell
.\\scripts\\dimora_workpc_cdp_capture.ps1 -Url "<認証済みDiMORAのお気に入りURL>"
\`

初回は専用プロファイルを起動する。ログイン画面が出た場合はそのブラウザでDiMORAへログインし、同じコマンドを再実行する。認証情報・Cookieはリポジトリへ保存しない。

既定出力: %USERPROFILE%\Dropbox\dimora\dimora-favorite-programs.json

これは正規化・変更検知より前段の本線取得を実証するためのもの。既存の正規化検証は再実行しない。
