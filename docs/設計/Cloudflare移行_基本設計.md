# Cloudflare Pages移行 基本設計

## 1. 目的

Bloggerを公開先としてきた経験ログ運用を見直し、GitHubを唯一の正本・制作・レビュー場所として維持しながら、公開だけをCloudflare Pagesへ分離する。

今回の設計では、**「GitHubで完成したこと」と「Webへ公開されたこと」を別の状態として扱う**。

## 2. 基本方針

- **GitHub**：記事HTML、画像、構成、レビュー、保存、制作履歴の唯一の正本。
- **GitHub main**：確認・レビュー・マージ済みの完成状態を保持する。
- **Cloudflare Pages Preview**：PR等の確認用。自動デプロイを基本とする。
- **Cloudflare Pages Production**：自動公開しない。
- **Production公開**：たかが明示的に公開するときだけ実行する。
- **公開対象**：GitHub mainの確認済み内容を対象とする。
- **公開後**：実ページ表示確認を行い、その後GSC確認へ進む。

## 3. 状態の分離

次の状態を混同しない。

1. GitHubで制作中
2. PRでレビュー中
3. mainへマージ済み
4. Cloudflare Previewで確認可能
5. Production公開を実施
6. 公開ページの実表示確認済み
7. GSC確認済み

特に、**mainへのマージをProduction公開とはみなさない**。

## 4. 公開フロー

`記事制作 → PR → レビュー・確認 → mainへmerge → Preview確認 → たかが公開指示 → Production deploy → 実表示確認 → GSC`

Productionへの自動デプロイを停止し、公開操作を明示的な工程として残す。

## 5. GitHub中心の公開操作

公開操作自体も可能な限りGitHub側から追跡できる形にする。

第一候補は、GitHub Actionsの手動実行等を使い、確認済みのmainをCloudflare PagesへProduction deployする方式とする。

この段階では実装方式を確定したとは扱わず、Cloudflare接続・認証・対象ディレクトリ・Wrangler等の具体方式を検証してから確定する。

## 6. 移行検証の順序

設計は一括、実装は小さな検証単位とする。

1. Cloudflare Pagesで静的HTMLを配信できることを確認
2. GitHubリポジトリとの接続を確認
3. Preview自動デプロイを確認
4. Production自動公開を停止できることを確認
5. 明示操作によるProduction deployを確認
6. 画像・相対/絶対パス・HTML表示を確認
7. 独自ドメイン・HTTPSを確認
8. スマホ表示等の実表示を確認
9. 公開後のGSC運用を確認
10. 問題なければBloggerからCloudflare Pagesへの正式移行方針を確定

## 7. 完了条件

Cloudflare移行を正式採用する条件は、少なくとも以下をすべて確認すること。

- GitHubを唯一の正本として維持できる。
- Previewを確認用として自動利用できる。
- mainへのmergeだけではProduction公開されない。
- たかの明示操作でProduction公開できる。
- 公開対象が確認済みのGitHub状態と一致する。
- HTML・画像・リンク等が実ページで正常に表示される。
- 独自ドメイン・HTTPS等の公開条件を満たす。
- 公開後確認とGSC確認を現在の工程管理へ組み込める。

## 8. 現段階の扱い

本設計は2026-10-06時点の基本設計として採用する。

Cloudflare接続、公開操作、ドメイン、広告・アフィリエイト等の具体的な可否や実装は、個別に検証した事実と提案を分離して扱う。

BloggerからCloudflare Pagesへの正式切替は、検証完了後に別途確定する。
