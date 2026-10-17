# BLOG-0001 HTML世代管理

- 現在の作業HTML: `docs/企画/BLOG-0001_Blogger掲載用.html`
- 世代保存先: `docs/企画/BLOG-0001_versions/`
- 命名: `BLOG-0001_ver00001.html`, `BLOG-0001_ver00002.html`, …
- バックアップは現在HTMLを次の世代へ**バイト単位でコピー**する。
- 復元は指定世代を現在HTMLへ**バイト単位でコピー**する。
- 世代ファイルは既存世代を上書きせず、常に最大番号の次を作る。

CLI:
```text
python scripts/blog_html_version.py backup
python scripts/blog_html_version.py list
python scripts/blog_html_version.py restore 2
```

GitHub上では、この世代ファイル自体とGit履歴の両方を残す。
