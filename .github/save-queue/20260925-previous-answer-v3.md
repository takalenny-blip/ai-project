# 直前の回答

## 保存対象種別

会話記録

## 概要

直前の回答全文を会話記録として保存キューへ委譲する。

## 直前の回答

進めた。かなり大きい原因候補が確定した。

### 1. 以前から同じ問題が実際に発生していた

過去の **#325** に、まったく同じ構造の修正が入っている。

> 共通auto-approve-and-mergeが `chat-save-request/*` まで対象にしていたため、intake前にqueue PRをmergeし得た。

その修正では明示的に、

```
!startsWith(github.event.pull_request.head.ref, 'chat-save-request/')
```

を入れて、保存キューを自動マージ対象から除外していた。

### 2. さらに #337 → #339 でintake方式自体を変更している

#337では `pull_request_target` をやめて `workflow_run` に変更。

しかし #337の方式は「intakeが発火しない」という問題が出て、**#339で再び `pull_request_target` に戻されている**。

つまり現在の設計は、

**過去に一度潰した「共通自動処理がsave-requestを触る問題」を再発させないことが極めて重要な構造**

になっている。

### 3. #639 / #641の異常は「intake失敗」ではない

#641は現在openだが、head SHAに対するworkflow runは **0件**。

一方、現在の `save-request-intake.yml` は `pull_request_target` の `opened / synchronize / reopened` をトリガーにしている。GitHub公式仕様上、このイベントはPR活動で起動できる。

したがって、

**#641がopenになったのにintake runが存在しない**

こと自体が調査対象。

そして#637/#639についてはさらに、

- PR close
- branch delete
- intake runなし

がセットで発生している。

現在のintake workflowのcleanupは**intake成功後**にしかbranchを削除しないので、これだけでは説明できない。

---

### ここで一旦止める

ここで新しい保存PRをさらに積むのはやらない。

今やるべき根本調査は、

1. **#637/#639をcloseした主体**
2. **branchをdeleteした主体**
3. **現在のauto-approve系workflowが#325の除外条件を保持しているか**
4. **#641がなぜ `pull_request_target` を発火させていないか**
5. **#325で一度修正した制御が、どの変更で現在の状態になったか**
6. そのうえで、**save-request PRを「intake以外の経路がclose/delete/mergeできない」状態に機械的に固定する**

ここまで潰してから#641を処理する。

GitHub公式仕様でも `pull_request_target` はbase側のtrusted workflowを実行するイベントなので、今回の「runそのものが存在しない」問題と、PRをclose/deleteした主体は切り分けて追う必要がある。

**現時点の判定：未完了。#641は保存未完了。根本原因調査を継続する。**
