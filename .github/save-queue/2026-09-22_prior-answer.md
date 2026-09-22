【直前回答】進めた。原因は確定した。

- #342 が起動しなかった直接原因
  - main の .github/workflows/save-request-intake.yml が YAML として壊れていた。
  - Cleanup request branch の後ろに不要な裸テキストが入り、さらに同じ cleanup step が重複していた。
  - そのため Save request intake 自体がロードされず、run が生成されなかった。
- この壊れた状態は #341 のマージコミット 8fde3be... に入った差分で確認できた。
- #342 はその壊れた状態を実際に踏んだため、今回の失敗結果は再現性のある証拠になった。

対応として、余計な変更はせず、壊れた10行だけを除去する修正PR #343 を作成した。

現在：
- #342：検証ケースとして保持
- #343：修正PR、未マージ
- save-request-intake の実処理：まだ未確認
- save_and_currentize.py：まだ未実行
- 4ファイルatomic save：未確認
- canonical readback：未確認
- 古いsave PR 28件：クローズ済み
- 古いブランチ削除：GitHub接続側に削除操作がなく、未完了

つまり、今回は「失敗したからまた次の修正を作る」ではなく、#342の実行結果 → 根因特定 → 最小修正PR #343まで進めたところ。