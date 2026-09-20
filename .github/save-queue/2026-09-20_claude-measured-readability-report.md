# 2026-09-20 Claude実測結果・協議報告

## たかからの指示
Claudeからの追加報告を受け、やり取りを書き込む。Claudeと協議して方向性を定めてから進める。現時点では実装しない。

## Claudeの実測報告

Claudeは「何を読めないか」を推測ではなく実測で切り分けた。読み取りだけを行い、リポジトリへの変更・pushはしていない。

### 読取経路ごとの差
- web_fetchで検索結果に出たURLは読めるが、BUD.mdについて9/15版が返り、実体9/20と一致しなかった。
- web_fetchで自分で組み立てたURLは拒否。
- github.com/.../raw/... はrobots.txtで拒否。
- web_searchはPR・Issueのタイトルや断片までで、JSON本文は出ない。
- Issueページのweb_fetchは本文のみでコメントが見えない。
- bash経由のraw.githubusercontent.comは docs/現在状態.json の全文をHTTP 200で取得できた。
- bashのgit clone --depth 1でリポジトリ全体を取得でき、HEADは63f225b。
- bashからapi.github.comでIssueコメントを取得できた。

### 重要な訂正
Claudeは、BUDそのものが古いという前回報告を訂正した。リポジトリ上のBUDは9/20付であり、古かったのはClaude側の取得結果だった。

### 確認済み構造
- docs/現在状態.jsonには実行環境・作業PC・clone・具体的な次の一手の項目がない。
- migration.normal_work_policy は「DiMORA本来工程へ復帰」という参照ラベルだけで、「本来工程」の定義が正本内にない。
- 旧VAIO P方針の具体的実体は projects/DIGA自動化.md にあり、VAIO P + Chromiumでの実証方針が記載されている。
- READMEにもVAIO Pを実運用基盤とする記述が残っている。
- rules/再開・検索ガード.mdにもVAIO P前提の記述がある。
- VAIOに触れるファイルは直チャット・経験ログを除いて14件ある。

### 未確認
- VAIO P断念と作業PC cloneの一次記録はまだ特定できていない。
- 9/15〜9/18の直チャットにclone/断念等の語があるが、内容は未読。
- 昨日の再開時にVAIO P + Chromiumを提示したセッションが、どの経路・版を読んだかは未確認。
- 保存待ちPR #116、#119に関連記録がある可能性はあるが、Claudeはまだ確認していない。

## Claudeの協議案

### B. 正本を読めなければ停止
Claudeは賛成。停止条件候補：
- JSONを取得できない。
- JSONとBUD・引き継ぎ等の更新日が一致しない。
- ハッシュ不一致。
- 環境項目欠落。
停止時は「現在状態未確認」とし、古い資料から次工程を推定しない。

### C. AI再開用manifest
- 正本JSONから生成する読み取り専用の最小情報。
- source_sha256、updated、有効環境、廃止環境、現在地点、具体的次工程、必須読取リスト、停止条件を含める。
- generate_current_views.pyから生成し、手編集禁止。
- save_and_currentize.pyの単一コミットに含める。
- scripts/resume_check.pyでJSONとビューのハッシュを検証し、OKなら再開情報、NGならSTOP。
- 正本はあくまでdocs/現在状態.jsonで、manifestを第二の正本にはしない。

### D. 生成範囲
- BUD、引き継ぎ、manifest、READMEの「現在の主要テーマ」「現在の中心」のマーカー部分を正本から生成する案。
- projects配下と旧docs資料は自動生成対象にせず、歴史資料としてstatus等を付ける案。
- rules/再開・検索ガード.mdのVAIO P前提を環境非依存に改訂する案。

### E. CI
Claude提案：
1. manifest/ビューと正本生成結果の完全一致
2. source_sha256一致
3. retired IDが次工程・現在節・README生成節に出たら失敗
4. 履歴扱いでない旧方針ファイルにstatusがなければ失敗
5. 「本来工程へ復帰」のような抽象的next_stepを失敗させ、環境・対象・根拠を必須化
6. clone_status=clonedなのに根拠なしなら失敗
7. mainからrawまたはclone経由でresume_check.pyが成功することを検証

### F. 回帰テスト
既存案に加え：
- ハッシュ不一致ならresume_check.pyがSTOPかつ非0。
- BUDがJSONより古ければSTOP。
- JSON取得不能でREADMEだけ読める場合はSTOPし、次工程を出さない。
- 固定ケース：retired=vaio_p、active=work_pc、clone_status=unverified。次工程は作業PCのclone確認を含み、VAIO Pを含まない。

### G. 実装順序案
1. JSONスキーマ拡張
2. resume_check.py・manifest・ハッシュ
3. CI・回帰テスト
4. README生成節化
5. 旧資料へのstatus付与
6. 再開・検索ガード.md改訂

## 現時点の合意前状態
Claudeの上記は「協議案」であり、採用決定・実装済みではない。
特に、manifestを導入するか、README/BUD等をどこまで生成ビュー化するか、旧資料をどう扱うかは、たかとClaudeの協議後に方向性を確定する。
作業PC cloneの事実も一次記録確認までは未確認として扱う。
VAIO Pを現行実行環境として復活させない。

## 次の協議ポイント
Claudeは最後に、作業PCでcloneした時期を特定できれば該当する直チャットを追加調査できるとしている。ただし、日付が分からない状態でも、まず「AIが正本を読めない／古い版を読んでしまう場合の停止・鮮度検証」を設計上の論点として協議できる。

この記録は保存キューへの投入用であり、保存完了とは扱わない。
