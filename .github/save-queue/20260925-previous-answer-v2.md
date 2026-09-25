# 直前の回答

## 保存対象種別

会話記録

## 概要

直前の回答全文を会話記録として保存キューへ委譲する。

## 直前の回答

進めた。ここで重要な新事実が出た。

### #639
- **#639も作成から約20秒で closed / merged=false**
- `save-request-intake.yml` にはPRをcloseする処理がない
- #639のhead SHAには `current-state-guard` 成功しかなく、**Save request intakeは起動していない**
- つまり、#637と#639は同じ異常経路で閉じられている可能性が高い。

そして、これはもう「intake失敗」では説明できない。

### ここまでの確定状態

| PR | 状態 | intake確認 |
|---|---|---|
| #634 | merged | **intakeを通らず直接merge** |
| #635 | closed / unmerged | intake確認なし |
| #637 | closed / unmerged | intake起動なし |
| #639 | closed / unmerged | intake起動なし |

さらに、#639を作った直後にこちらで実行したworkflow確認でも、runはまだ存在しなかった。

**したがって、今は再投入を絶対にしない。**

GitHub側ではrequired checks / review / rulesetによってmerge条件を強制できるので、直接merge問題はActions内のconcurrencyだけでは封じられない。GitHub公式ドキュメントでも、protected branchではrequired status checksやreviewなどの条件をmerge前に強制できるとされている。

次は、**「誰が・何の経路でchat-save-request PRを自動的にclosedにしているのか」そのものを特定する段階**に入る。
ここを潰さずに#633を通したり新しい保存PRを積んだりすると、また同じ穴に入る。
