保存対象種別 = 会話記録

# 直前の回答

進めた。Crow提案の実作業に入った。

### 実施済み

**① 確認手順の正式化**
- `rules/運用ルール.md` に、キューPRのopen/closedだけで成否判定しない証拠ゲートを追加。
- `save-request-intake` のcheck-run結果を必須確認にした。
- intake成功未確認なら「失敗」とせず、結果待ち／未確認扱い。
- 同一対象の再投入禁止も明記。

GitHubのcheck-runはPR状態とは別にstatus/conclusionを持つため、この分離はGitHubの仕様にも沿っている。

**② `save_lifecycle_status.py` の実運用接続**
- `intake` 証拠を入力に追加。
- `closed + intake未確認` → `submitted_pending`
- `intake failure` → `failed_or_incomplete`
- `intake success + canonical save PR open` → `final_save_pending`
- 回帰テストを追加。
- `save-request-intake.yml` の実処理からresolverを呼ぶところまで接続した。

現在、変更PR **#648** を作成済み。

### ③ 4記録の照合

#637/#639/#641/#643から生成された4件を実体で確認した。

**結論：重複はあるが、単純な同一内容の重複ではない。**

09:41 → 09:44 → 09:48 → 09:51 と、それぞれ直前の回答・その時点の調査結果が更新されている。したがって、現時点では**削除・統合しない**。一次記録として残す判断にした。

### いまの未完了

- **#648：CI・承認・merge・canonical readbackはまだ未確認。**
- **#647：今回の「直前の回答」保存要求は、現時点では完了確認できていない。** 追加投入はせず、この状態を別トラックで追う。
- キューPRを直接mergeできないようにする構造的防止は、今回の①②とは別の残課題として残っている。

ここでは「PRを作った＝完了」とは扱わず、#648の実CI→承認→merge→readbackまで確認してから次へ進める。