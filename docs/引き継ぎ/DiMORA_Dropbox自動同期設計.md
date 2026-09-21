# DiMORA → Dropbox 自動同期設計

## 目的

work_pc（Windows）の実機エクスポート原本
`C:\\Users\\kiyam\\Downloads\\dimora-favorite-programs.json`
を、毎回の手作業なしでDropboxへ同期し、Bud側から取得できる経路を作る。

## 役割分離

- PR #234: DiMORA実データ正規化検証は完了済み。再実行しない。
- この設計: work_pc原本JSONへの直接アクセス経路を検証するためのもの。
- GitHub mainには原本JSONを置かない。
- Dropbox同期はWindows側で行い、Bud側の取得はDropbox接続後に検証する。

## Windows側

リポジトリの `scripts/sync_dimora_to_dropbox.ps1` を使用する。

既定値:
- 入力: `%USERPROFILE%\\Downloads\\dimora-favorite-programs.json`
- 出力: `%USERPROFILE%\\Dropbox\\dimora\\dimora-favorite-programs.json`

Dropbox Desktopが同期しているフォルダを使う。DiMORAのJSONをDropboxへ手動アップロードするのではなく、PowerShellスクリプトをWindowsタスクスケジューラで定期実行する想定。

## 初回セットアップ

1. work_pcにDropbox Desktopを導入し、同期先を確認する。
2. `scripts/sync_dimora_to_dropbox.ps1` の `$DropboxTarget` を実際のDropbox同期フォルダに合わせる。
3. 手動で一度実行し、JSONがDropbox側フォルダに現れることを確認する。
4. タスクスケジューラでログオン時または定期実行にする。
5. Bud側でDropbox接続を有効化し、同期されたJSONを検索・取得できるか検証する。

## 完了条件

次の4点を確認できたら `dimora_source_artifact_access` を verified に更新する。

- work_pc上の原本が存在する
- PowerShell経由でDropbox同期フォルダへ自動コピーできる
- Dropbox上の同一JSONをBud側から取得できる
- 取得物がDiMORA原本JSONであることを確認できる

正規化処理は完了済みのため、この検証では実行しない。

## 現在の未確認事項

- work_pcにDropbox Desktopが導入済みか
- Dropbox同期フォルダの実パス
- Bud側Dropbox接続の認証・取得可否
