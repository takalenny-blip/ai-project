# 直チャット保存要求

## 保存対象

### ユーザー
直前まで回答書き込んで。進めて。

### バド
了解。進める。

まず現状確認まで完了した。現在の正本HEADは `94307bec...`。本線は **experience-log → Blogger自動化** で、DiMORAには戻らない。

確認したところ、経験ログ→記事素材の第1実装は既に存在する。

- `scripts/build_experience_article_material.py`
- `tests/test_build_experience_article_material.py`
- `.github/workflows/experience-article-material.yml`
- `docs/経験ログ→記事素材_第1実装.md`

そして第1実装の次段は明記されている。

> このJSONを材料として、AIが記事候補を編集・構成する工程を別の小さな検証単位として追加する。

なので、**次は「AI記事候補生成」の最小検証単位**へ進む。  
Blogger API・認証・自動投稿はまだ触らない。

完了条件は、

1. 既存EXP/RECから記事素材を取得
2. その素材だけを根拠に記事候補を構成
3. 事実とAIによる構成・表現を混同しない
4. 本人発言を勝手に補完しない
5. Blogger投稿なしで、記事候補まで検証できる

ここを1単位として実装・検証する。
