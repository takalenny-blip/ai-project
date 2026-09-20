# 直チャット保存要求

## User
前回回答書き込んで。dimora-favorite-programs.json はgithubのどの辺にありそう？探したけど見当たらない。

## Bud
GitHub正本を検索した結果、リポジトリ内に `dimora-favorite-programs.json` は見つからなかった。ファイル名、DimORA favorite-programs関連語、`DIMORA_ARTIFACT_PATH` の3系統で検索しても該当なし。

現在の正本状態では、このJSONはGitHub管理ファイルではなく「work_pc runtime artifact」として外部artifact prerequisiteに定義されている。したがって探す場所はGitHubの特定ディレクトリではなく、実機エクスポートを行ったwork_pc側。GitHubには正規化スクリプトやテスト、現在状態の「取得済みかどうか」の記録があり、実データJSONそのものは置かれていない。

実データ検証は、JSON本体を取得してから存在・可読性・JSON形式・件数をpreflightし、正規化へ入力して検証する。GitHub内に無いことを確認したので、同じ検索を繰り返さない。
