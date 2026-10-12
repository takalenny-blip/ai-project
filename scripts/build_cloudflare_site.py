#!/usr/bin/env python3
"""Build the BLOG-0003 production page for GitHub Pages."""

from pathlib import Path
import html as html_module
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/企画/BLOG-0003/BLOG-0003_Blogger掲載用.html"
IMAGE_DIR = ROOT / "docs/企画/BLOG-0003/images"
DIST = ROOT / "dist"

TITLE = "GitHub編：AIとのやりとりを、どうやって「残るもの」にしていったか"
PERMALINK = "github-ai-conversation.html"
BLOG1_SOURCE = ROOT / "docs/企画/BLOG-0001_Blogger掲載用.html"
BLOG2_SOURCE = ROOT / "docs/企画/BLOG-0002/BLOG-0002_Blogger掲載用.html"
BLOG2_IMAGE_DIR = ROOT / "docs/企画/BLOG-0002/画像"
BLOG1_TITLE = "AIとのやりとりを残してみる――それは「便利そうだな」から始まった"
BLOG2_TITLE = "もう一度動かしてみた――その先で考えたこと"
BLOG1_PERMALINK = "ai-blog-start.html"
BLOG2_PERMALINK = "vaio-p-again-and-beyond.html"
BLOG1_DESCRIPTION = "AIとのやりとりからブログ制作の仕組みを考え始めた記録。Claudeのブラウザ操作をきっかけに、GeminiやPythonでの自動化、経験を記事として残す発想につながっていく。"
BLOG2_DESCRIPTION = "VAIO Pをもう一度動かすためにDebianを導入し、環境を整えた記録。DIGA／DiMORAの番組予約情報を扱う自動化テストを通して、試行錯誤と次の発想を振り返る。"
BLOG3_DESCRIPTION = "AIとのやりとりをGitHubに残し、現在状態や作業の進み具合を管理する仕組みを作った経験。会話を保存するだけでなく、あとから再開できる形に整えていく過程を紹介する。"
SITE_IMAGE_URL = "https://takalenny-blip.github.io/ai-project/images/taka-blog-banner.jpg"
ARTICLES = [
    {"title": BLOG1_TITLE, "permalink": BLOG1_PERMALINK, "part": "第1部｜経験ログ", "description": BLOG1_DESCRIPTION},
    {"title": BLOG2_TITLE, "permalink": BLOG2_PERMALINK, "part": "第2部｜VAIO P", "description": BLOG2_DESCRIPTION},
    {"title": TITLE, "permalink": PERMALINK, "part": "第3部｜GitHub", "description": BLOG3_DESCRIPTION},
]


def render_sidebar():
    recent_links = "\n".join(
        f'<li><a href="{item["permalink"]}">{html_module.escape(item["title"])}</a></li>'
        for item in reversed(ARTICLES)
    )
    return f"""<aside class="profile" aria-label="ブログ案内">
  <p class="profile-label">PROFILE</p>
  <div class="profile-icon" aria-hidden="true">た</div>
  <p><strong>たか</strong></p>
  <p>AIとのやりとりと、その過程を記録しています。</p>
  <nav class="sidebar-section" aria-label="記事を探す">
    <h2>記事を探す</h2>
    <ul><li><a href="sitemap.html">すべての記事</a></li></ul>
    <h2>最近の記事</h2>
    <ul>{recent_links}</ul>
  </nav>
</aside>"""


def render_footer():
    return """<footer class="site-footer">
  <nav aria-label="フッターナビゲーション">
    <a href="./">トップページ</a> ·
    <a href="sitemap.html">記事一覧</a> ·
    <a href="about.html">ブログについて</a> ·
    <a href="privacy.html">プライバシーポリシー</a>
  </nav>
  <p>たか’sブログ</p>
</footer>"""


def render_article_navigation(permalink):
    index = next(i for i, item in enumerate(ARTICLES) if item["permalink"] == permalink)
    previous_item = ARTICLES[index - 1] if index > 0 else None
    next_item = ARTICLES[index + 1] if index + 1 < len(ARTICLES) else None
    previous_link = (
        f'<a rel="prev" href="{previous_item["permalink"]}">← 前の記事：{html_module.escape(previous_item["title"])}</a>'
        if previous_item else '<span class="nav-unavailable">前の記事はありません</span>'
    )
    next_link = (
        f'<a rel="next" href="{next_item["permalink"]}">次の記事：{html_module.escape(next_item["title"])} →</a>'
        if next_item else '<span class="nav-unavailable">次の記事はありません</span>'
    )
    related_links = "\n".join(
        f'<li><a href="{item["permalink"]}">{html_module.escape(item["title"])}</a></li>'
        for item in ARTICLES if item["permalink"] != permalink
    )
    return f"""<nav class="article-navigation" aria-label="記事ナビゲーション">
  <p class="nav-label">記事ナビゲーション</p>
  <div class="article-neighbors">{previous_link}{next_link}</div>
  <h2>あわせて読みたい</h2>
  <ul>{related_links}</ul>
</nav>"""




for required_source in (SOURCE, BLOG1_SOURCE, BLOG2_SOURCE):
    if not required_source.is_file():
        raise SystemExit(f"missing source: {required_source}")

if DIST.exists():
    shutil.rmtree(DIST)
(DIST / "images").mkdir(parents=True)
BANNER = ROOT / "docs/site/images/taka-blog-banner.jpg"
if not BANNER.is_file():
    raise SystemExit(f"missing banner: {BANNER}")
(DIST / "images" / "blog-0002").mkdir(parents=True)

html = SOURCE.read_text(encoding="utf-8")
blog1_html = BLOG1_SOURCE.read_text(encoding="utf-8")
blog2_html = BLOG2_SOURCE.read_text(encoding="utf-8")

raw_base = "https://raw.githubusercontent.com/takalenny-blip/ai-project/main/docs/%E4%BC%81%E7%94%BB/BLOG-0003/images/"
html = html.replace(raw_base, "images/")
blog2_raw_base = "https://raw.githubusercontent.com/takalenny-blip/ai-project/main/docs/%E4%BC%81%E7%94%BB/BLOG-0002/%E7%94%BB%E5%83%8F/"
blog2_html = blog2_html.replace(blog2_raw_base, "images/blog-0002/")

for image in sorted(IMAGE_DIR.iterdir()):
    if image.is_file():
        shutil.copy2(image, DIST / "images" / image.name)
shutil.copy2(BANNER, DIST / "images" / "taka-blog-banner.jpg")
for image in sorted(BLOG2_IMAGE_DIR.iterdir()):
    if image.is_file():
        shutil.copy2(image, DIST / "images" / "blog-0002" / image.name)

page = f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<meta name="description" content="{BLOG3_DESCRIPTION}">
<meta name="google-site-verification" content="Iaufdzv8o8vilCmpJ1WqXyjSyYZtNh13gEXbhYTgV0Y">
<link rel="canonical" href="https://takalenny-blip.github.io/ai-project/{PERMALINK}">
<meta property="og:type" content="article">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{BLOG3_DESCRIPTION}">
<meta property="og:url" content="https://takalenny-blip.github.io/ai-project/{PERMALINK}">
<meta property="og:image" content="{SITE_IMAGE_URL}">
<meta property="og:image:alt" content="たか’sブログのサイトバナー">
<meta name="twitter:card" content="summary_large_image">
<style>
* {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}
:root {{ --ink:#eee7db; --muted:#aaa093; --paper:#363636; --cream:#2d2b28; --line:#3d3933; --accent:#b3945a; }}
body {{ margin:0; background:var(--paper); color:var(--ink); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans JP","Hiragino Kaku Gothic ProN","Yu Gothic",sans-serif; line-height:1.95; }}
.site-header {{ background:var(--paper); }}
.header-inner {{ max-width:1120px; margin:0 auto; padding:30px 28px 26px; }}
.site-signboard {{ display:block; border:0; text-decoration:none; }}
.site-signboard img {{ display:block; width:100%; height:auto; max-height:300px; object-fit:cover; border:1px solid var(--line); }}
.blog-name {{ margin:0; font-family:Georgia,"Times New Roman","Noto Serif JP",serif; font-size:1.55rem; letter-spacing:.08em; font-weight:500; }}
.header-kicker {{ margin:.55rem 0 0; color:var(--muted); font-size:.72rem; letter-spacing:.18em; text-transform:uppercase; }}
.banner {{ border-top:1px solid var(--line); border-bottom:1px solid var(--line); background:var(--cream); }}
.banner-inner {{ max-width:1120px; margin:0 auto; padding:13px 28px; color:var(--muted); font-size:.78rem; letter-spacing:.08em; }}
main {{ max-width:1120px; margin:0 auto; padding:58px 28px 90px; }}
.layout {{ display:grid; grid-template-columns:minmax(0,1fr) 250px; gap:54px; align-items:start; }}
article {{ min-width:0; }}
.article-intro {{ border-bottom:1px solid var(--line); padding:0 0 34px; margin-bottom:38px; }}
.eyebrow {{ margin:0 0 13px; color:var(--accent); font-size:.74rem; font-weight:600; letter-spacing:.18em; }}
article h1 {{ font-family:Georgia,"Times New Roman","Noto Serif JP",serif; font-weight:500; font-size:clamp(2rem,4.4vw,3.35rem); line-height:1.35; letter-spacing:.01em; margin:0; }}
.post-meta {{ margin:17px 0 0; color:var(--muted); font-size:.78rem; letter-spacing:.04em; }}
article h2 {{ margin-top:3.4em; padding-bottom:.45em; border-bottom:1px solid var(--line); font-family:Georgia,"Times New Roman","Noto Serif JP",serif; font-weight:500; line-height:1.5; }}
article h3 {{ margin-top:2.4em; line-height:1.55; }}
article p {{ margin:1.15em 0; }}
.dialogue {{ margin:1.2em 0; padding:.85em 1.1em; border-radius:1.1em; max-width:88%; }}
.dialogue.human {{ margin-right:auto; background:#f3ead8; color:#3f392f; }}
.dialogue.ai {{ margin-left:auto; background:#dfeaf4; color:#2f3b46; }}
pre {{ margin:1.2em 0; padding:1em 1.15em; overflow-x:auto; background:#242424; border:1px solid var(--line); border-radius:.45em; color:#eee7db; line-height:1.6; }}
pre code {{ display:block; background:transparent; padding:0; color:inherit; white-space:pre; font-family:"SFMono-Regular",Consolas,"Liberation Mono","Courier New",monospace; }}
.flow-diagram {{ display:flex; flex-direction:column; align-items:center; gap:.5em; margin:1.5em 0; }}
.flow-box {{ width:90%; max-width:42em; box-sizing:border-box; padding:.7em 1em; text-align:center; border:1px solid #999; border-radius:.7em; background:#2b2926; }}
.flow-arrow {{ line-height:1.2; text-align:center; color:var(--muted); }}
.flow-comparison {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:1.2em; margin:1.5em 0; }}
.flow-comparison-column {{ box-sizing:border-box; padding:1em; border:1px solid var(--line); border-radius:.7em; background:#2b2926; }}
.flow-comparison-column h4 {{ margin:.1em 0 1em; text-align:center; }}
.flow-comparison-column .flow-box {{ width:100%; max-width:none; background:#302e2a; }}
@media (max-width:700px) {{ .flow-comparison {{ grid-template-columns:1fr; }} }}
blockquote p {{ transform:skewX(-8deg); transform-origin:left center; }}
blockquote {{ margin:2em 0; padding:1.1em 1.4em; background:#302e2a; border-left:3px solid var(--accent); font-style:italic; }}
nav {{ margin:2.4em 0; padding:1.25em 1.4em; background:#2b2926; border:1px solid var(--line); }}
nav ul {{ margin:0; padding-left:1.4em; }}
nav li {{ margin:.35em 0; }}
a {{ color:#c4a46a; }}
figure {{ margin:2.8em auto !important; }}
figure img {{ display:block; height:auto; max-width:100%; }}
figcaption {{ margin-top:.65em; color:var(--muted); font-size:.82em; }}
.flow-box {{ background:#2b2926; }}
code {{ background:#35322e; padding:.1em .3em; border-radius:2px; }}
.profile {{ position:sticky; top:28px; padding:25px 0 0 26px; border-left:1px solid var(--line); color:var(--muted); }}
.sidebar-section {{ margin-top:30px; padding-top:22px; border-top:1px solid var(--line); }}
.sidebar-section h2 {{ margin:0 0 10px; color:var(--accent); font-size:.76rem; font-family:inherit; font-weight:600; letter-spacing:.08em; }}
.sidebar-section ul {{ margin:0 0 22px; padding-left:1.1em; }}
.sidebar-section li {{ margin:.55em 0; font-size:.84rem; }}
.article-navigation {{ margin:3em 0 0; padding:1.3em; border:1px solid var(--line); background:#2b2926; }}
.article-navigation .nav-label {{ margin:0 0 1em; color:var(--accent); font-size:.72rem; letter-spacing:.12em; font-weight:600; }}
.article-navigation .article-neighbors {{ display:flex; flex-wrap:wrap; justify-content:space-between; gap:1em; }}
.article-navigation .nav-unavailable {{ color:var(--muted); font-size:.86em; }}
.article-navigation h2 {{ margin:1.7em 0 .6em; padding:0; border:0; font-family:inherit; font-size:.9rem; font-weight:600; }}
.article-navigation ul {{ margin:0; padding-left:1.2em; }}
.article-navigation li {{ margin:.4em 0; }}
.profile-label {{ margin:0 0 18px; color:var(--accent); font-size:.68rem; letter-spacing:.2em; font-weight:600; }}
.profile-icon {{ width:58px; height:58px; margin-bottom:14px; border:1px solid #806b4a; border-radius:50%; display:grid; place-items:center; background:transparent; color:var(--ink); font-family:Georgia,serif; font-size:1.25rem; }}
.profile-name {{ color:var(--ink); font-family:Georgia,"Noto Serif JP",serif; font-size:1.05rem; }}
.site-footer {{ border-top:1px solid var(--line); background:var(--paper); color:var(--muted); text-align:center; padding:34px 18px; font-size:.76rem; letter-spacing:.1em; }}
@media (max-width:760px) {{
  .header-inner {{ padding:22px 18px 18px; }}
  .site-signboard img {{ max-height:180px; }}
  .banner-inner {{ padding:11px 18px; }}
  main {{ padding:38px 18px 60px; }}
  .layout {{ grid-template-columns:1fr; gap:42px; }}
  article h1 {{ font-size:2rem; }}
  .profile {{ position:static; padding:24px 0 0; border-left:0; border-top:1px solid var(--line); }}
}}
</style>
</head>
<body>
<header class="site-header">
  <div class="header-inner">
    <a class="site-signboard" href="./" aria-label="たか’sブログ ホーム">
      <img src="images/taka-blog-banner.jpg" alt="たか’sブログ">
    </a>
  </div>
</header>
<div class="banner"><div class="banner-inner">AIとのやりとりと、そこから生まれた経験を残していく</div></div>
<main>
  <div class="layout">
    <article>
      <div class="article-intro">
        <p class="eyebrow">THIRD PART / GITHUB</p>
        <h1>{TITLE}</h1>
        <p class="post-meta">固定ページ：{PERMALINK}</p>
      </div>
      {html}
    </article>
    {render_sidebar()}
  </div>
</main>
{render_footer()}
</body>
</html>
"""

home = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>たか’sブログ</title>
<meta name="description" content="AIとのやりとりと、そこから生まれた経験を残していくブログです。">
<meta property="og:type" content="website">
<meta property="og:title" content="たか’sブログ">
<meta property="og:description" content="AIとのやりとりと、そこから生まれた経験を残していくブログです。">
<meta property="og:url" content="https://takalenny-blip.github.io/ai-project/">
<meta property="og:image" content="https://takalenny-blip.github.io/ai-project/images/taka-blog-banner.jpg">
<meta property="og:image:alt" content="たか’sブログのサイトバナー">
<meta name="twitter:card" content="summary_large_image">
<meta name="google-site-verification" content="Iaufdzv8o8vilCmpJ1WqXyjSyYZtNh13gEXbhYTgV0Y">
<link rel="canonical" href="https://takalenny-blip.github.io/ai-project/">
<style>
* { box-sizing:border-box; }
:root { --ink:#eee7db; --muted:#aaa093; --paper:#363636; --cream:#2d2b28; --line:#3d3933; --accent:#b3945a; }
body { margin:0; background:var(--paper); color:var(--ink); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans JP",sans-serif; line-height:1.8; }
.site-header { background:var(--paper); }
.header-inner { max-width:1120px; margin:0 auto; padding:30px 28px 26px; }
.site-signboard { display:block; border:0; text-decoration:none; }
.site-signboard img { display:block; width:100%; height:auto; max-height:300px; object-fit:cover; border:1px solid var(--line); }
.blog-name { margin:0; font-family:Georgia,"Times New Roman","Noto Serif JP",serif; font-size:clamp(2rem,4vw,3rem); font-weight:500; letter-spacing:.08em; }
.header-kicker { margin:.7rem 0 0; color:var(--muted); font-size:.72rem; letter-spacing:.2em; }
.banner { border-top:1px solid var(--line); border-bottom:1px solid var(--line); background:var(--cream); }
.banner-inner { max-width:1120px; margin:0 auto; padding:13px 28px; color:var(--muted); font-size:.78rem; letter-spacing:.08em; }
.layout { display:grid; grid-template-columns:minmax(0,1fr) 250px; gap:54px; align-items:start; max-width:1120px; margin:0 auto; padding:62px 28px 90px; }
.content h1 { margin:0 0 36px; font-family:Georgia,"Times New Roman","Noto Serif JP",serif; font-size:1rem; font-weight:500; letter-spacing:.18em; color:var(--accent); }
.feature { position:relative; display:block; padding:42px 0 40px; border-top:1px solid var(--line); border-bottom:1px solid var(--line); color:inherit; text-decoration:none; }
.feature .part, .card .part { margin:0 0 14px; color:var(--accent); font-size:.72rem; letter-spacing:.16em; font-weight:600; }
.feature h2 { max-width:760px; margin:0; font-family:Georgia,"Times New Roman","Noto Serif JP",serif; font-weight:500; font-size:clamp(1.9rem,4vw,3rem); line-height:1.45; }
.feature p { max-width:650px; margin:18px 0 0; color:var(--muted); font-size:.92rem; }
.feature-arrow { position:absolute; right:4px; bottom:38px; color:var(--accent); font-size:1.4rem; }
.others { display:grid; grid-template-columns:1fr 1fr; gap:34px; margin-top:34px; }
.card { display:block; min-height:210px; padding:28px 0 10px; border-top:1px solid var(--line); color:inherit; text-decoration:none; }
.card h2 { margin:0 0 14px; font-family:Georgia,"Times New Roman","Noto Serif JP",serif; font-weight:500; font-size:1.35rem; line-height:1.55; }
.card p { margin:0; color:var(--muted); font-size:.88rem; }
.card:hover h2, .feature:hover h2 { color:#c4a46a; }
.profile { position:sticky; top:28px; padding:25px 0 0 26px; border-left:1px solid var(--line); color:var(--muted); }
.profile-label { margin:0 0 18px; color:var(--accent); font-size:.68rem; letter-spacing:.2em; font-weight:600; }
.profile-icon { width:58px; height:58px; margin-bottom:14px; border:1px solid #c9bda9; border-radius:50%; display:grid; place-items:center; background:transparent; color:var(--ink); font-family:Georgia,serif; font-size:1.25rem; }
.profile p { margin:0 0 .35em; }
.sidebar-section { margin-top:30px; padding-top:22px; border-top:1px solid var(--line); }
.sidebar-section h2 { margin:0 0 10px; color:var(--accent); font-size:.76rem; font-family:inherit; font-weight:600; letter-spacing:.08em; }
.sidebar-section ul { margin:0 0 22px; padding-left:1.1em; }
.sidebar-section li { margin:.55em 0; font-size:.84rem; }
.site-footer { border-top:1px solid var(--line); background:var(--paper); color:var(--muted); text-align:center; padding:34px 18px; font-size:.76rem; letter-spacing:.1em; }
@media (max-width:760px) {
  .header-inner { padding:22px 18px 18px; }
  .site-signboard img { max-height:180px; }
  .banner-inner { padding:11px 18px; }
  .layout { grid-template-columns:1fr; gap:42px; padding:42px 18px 60px; }
  .feature { padding:30px 0 34px; }
  .feature h2 { font-size:1.8rem; }
  .feature-arrow { display:none; }
  .others { grid-template-columns:1fr; gap:0; }
  .profile { position:static; padding:24px 0 0; border-left:0; border-top:1px solid var(--line); }
}
</style>
</head>
<body>
<header class="site-header"><div class="header-inner"><a class="site-signboard" href="./" aria-label="たか’sブログ ホーム"><img src="images/taka-blog-banner.jpg" alt="たか’sブログ"></a></div></header>
<div class="banner"><div class="banner-inner">AIとのやりとりと、そこから生まれた経験を残していく</div></div>
<div class="layout">
<section class="content">
<h1>THREE PARTS / ONE STORY</h1>
<a class="feature" href="ai-blog-start.html">
  <p class="part">第1部｜経験ログ</p>
  <h2>AIとのやりとりを残してみる――それは「便利そうだな」から始まった</h2>
  <p>AIと一緒にブログを作ろうと思うまで。その最初の気持ちから始まった記録。</p>
  <span class="feature-arrow" aria-hidden="true">→</span>
</a>
<div class="others">
  <a class="card" href="vaio-p-again-and-beyond.html"><p class="part">第2部｜VAIO P</p><h2>もう一度動かしてみた――その先で考えたこと</h2><p>VAIO Pをもう一度動かしていった記録。</p></a>
  <a class="card" href="github-ai-conversation.html"><p class="part">第3部｜GitHub</p><h2>AIとのやりとりを「残るもの」にしていった――GitHubで作った仕組み</h2><p>保存し、現在を間違えない仕組みにしていった経験。</p></a>
</div>
</section>
{render_sidebar()}
</div>
{render_footer()}
</body>
</html>
"""
home = home.replace('{render_sidebar()}', render_sidebar()).replace('{render_footer()}', render_footer())

quote_samples = """<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>引用表示サンプル</title><meta name="robots" content="noindex,follow">
<style>
*{box-sizing:border-box} body{margin:0;background:#363636;color:#eee7db;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans JP",sans-serif;line-height:1.9}
main{max-width:900px;margin:auto;padding:50px 28px 80px} h1{font-family:Georgia,"Noto Serif JP",serif;font-weight:500} h2{font-size:1rem;color:#b3945a;margin-top:42px}
.sample{margin:18px 0 44px} .label{color:#aaa093;font-size:.72rem;letter-spacing:.12em;margin-bottom:8px}
blockquote{margin:0;font-size:1rem;color:#eee7db}
.v1{padding:18px 22px;background:#302e2a;border-left:3px solid #b3945a}
.v2{padding:18px 0;border-top:1px solid #5a554d;border-bottom:1px solid #5a554d}
.v3{padding:18px 22px;background:#403e3a}
.v4{padding:20px 24px;border:1px solid #5a554d;border-radius:4px;background:#2d2b28}
.v5{padding:10px 0 10px 22px;color:#d8d1c5;font-style:italic}
.note{color:#aaa093;font-size:.8rem;margin-top:8px}
a{color:#c4a46a}
</style></head><body><main>
<h1>引用表示サンプル</h1>
<p>現在のブログ背景色 <strong>#363636</strong> に合わせた5パターン。これは比較用の一時ページ。</p>
<h2>01｜現在の左縦線</h2><div class="sample"><div class="label">BLOCKQUOTE</div><blockquote class="v1">AIとのやりとりは、その場で消えてしまうものではなく、あとから読み返せる経験として残していく。</blockquote></div>
<h2>02｜上下線</h2><div class="sample"><div class="label">BLOCKQUOTE</div><blockquote class="v2">AIとのやりとりは、その場で消えてしまうものではなく、あとから読み返せる経験として残していく。</blockquote></div>
<h2>03｜背景だけ</h2><div class="sample"><div class="label">BLOCKQUOTE</div><blockquote class="v3">AIとのやりとりは、その場で消えてしまうものではなく、あとから読み返せる経験として残していく。</blockquote></div>
<h2>04｜カード型</h2><div class="sample"><div class="label">BLOCKQUOTE</div><blockquote class="v4">AIとのやりとりは、その場で消えてしまうものではなく、あとから読み返せる経験として残していく。</blockquote></div>
<h2>05｜線なし・インデント</h2><div class="sample"><div class="label">BLOCKQUOTE</div><blockquote class="v5">AIとのやりとりは、その場で消えてしまうものではなく、あとから読み返せる経験として残していく。</blockquote></div>
<p class="note">※ 本番の引用表示はまだ変更していません。</p>
</main></body></html>
"""
(DIST / "quote-samples.html").write_text(quote_samples, encoding="utf-8")

robots_txt = "User-agent: *\nAllow: /\n\nSitemap: https://takalenny-blip.github.io/ai-project/sitemap.xml\n"
(DIST / "robots.txt").write_text(robots_txt, encoding="utf-8")


(DIST / "index.html").write_text(home, encoding="utf-8")
# The canonical article is written after article_variant adds the shared article navigation.

def article_variant(base_page, title, permalink, body_html):
    labels = {
        BLOG1_PERMALINK: "FIRST PART / EXPERIENCE",
        BLOG2_PERMALINK: "SECOND PART / VAIO P",
        PERMALINK: "THIRD PART / GITHUB",
    }
    base_page = base_page.replace(
        '<p class="eyebrow">THIRD PART / GITHUB</p>',
        f'<p class="eyebrow">{labels.get(permalink, "ARTICLE / RECORD")}</p>',
    )
    canonical_url = f"https://takalenny-blip.github.io/ai-project/{permalink}"
    base_page = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", base_page, count=1)
    descriptions = {
        BLOG1_PERMALINK: BLOG1_DESCRIPTION,
        BLOG2_PERMALINK: BLOG2_DESCRIPTION,
        PERMALINK: BLOG3_DESCRIPTION,
    }
    description = descriptions.get(permalink, title)
    base_page = re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{description}">',
        base_page,
        count=1,
    )
    base_page = re.sub(
        r'<meta property="og:description" content="[^"]*">',
        f'<meta property="og:description" content="{description}">',
        base_page,
        count=1,
    )
    base_page = re.sub(
        r'<link rel="canonical" href="[^"]*">',
        f'<link rel="canonical" href="{canonical_url}">',
        base_page,
        count=1,
    )
    base_page = re.sub(
        r'<meta property="og:title" content="[^"]*">',
        f'<meta property="og:title" content="{title}">',
        base_page,
        count=1,
    )
    base_page = re.sub(
        r'<meta property="og:url" content="[^"]*">',
        f'<meta property="og:url" content="{canonical_url}">',
        base_page,
        count=1,
    )
    start = base_page.index("      <h1>")
    end = base_page.index("    </article>", start)
    replacement = f"""      <h1>{title}</h1>
      <p class="post-meta">固定ページ：{permalink}</p>
      {body_html}
      {render_article_navigation(permalink)}
"""
    return base_page[:start] + replacement + base_page[end:]

page1 = article_variant(page, BLOG1_TITLE, BLOG1_PERMALINK, blog1_html)
page2 = article_variant(page, BLOG2_TITLE, BLOG2_PERMALINK, blog2_html)
page3 = article_variant(page, TITLE, PERMALINK, html)
(DIST / BLOG1_PERMALINK).write_text(page1, encoding="utf-8")
(DIST / BLOG2_PERMALINK).write_text(page2, encoding="utf-8")
(DIST / PERMALINK).write_text(page3, encoding="utf-8")

if re.search(r"https://raw\.githubusercontent\.com/.*/BLOG-0003/images/", html):
    raise SystemExit("unrewritten raw GitHub image URL remains")

missing = [
    name for name in re.findall(r'src="images/([^"]+)"', html)
    if not (DIST / "images" / name).is_file()
]
if missing:
    raise SystemExit("missing local images: " + ", ".join(sorted(set(missing))))


def build_xml_sitemap():
    """Build the XML sitemap from generated canonical public pages."""
    base_url = "https://takalenny-blip.github.io/ai-project"
    urls = []
    for page_path in sorted(DIST.glob("*.html")):
        # The HTML sitemap is navigation, not a content URL to submit in the XML sitemap.
        if page_path.name == "sitemap.html":
            continue
        page_html = page_path.read_text(encoding="utf-8")
        canonical_match = re.search(
            r'<link rel="canonical" href="([^"]+)"',
            page_html,
        )
        if not canonical_match:
            continue
        canonical_url = html_module.unescape(canonical_match.group(1)).strip()
        if canonical_url.rstrip("/") != base_url and not canonical_url.startswith(base_url + "/"):
            continue
        urls.append(canonical_url)

    homepage = base_url + "/"
    if homepage not in urls:
        raise SystemExit("XML sitemap generation failed: canonical homepage is missing")
    if len(urls) != len(set(urls)):
        raise SystemExit("XML sitemap generation failed: duplicate canonical URLs")

    urls.sort(key=lambda url: (url != homepage, url))
    entries = "\n".join(
        f"  <url><loc>{html_module.escape(url, quote=False)}</loc></url>"
        for url in urls
    )
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}\n"
        "</urlset>\n"
    )
    (DIST / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    print(f"built {DIST / 'sitemap.xml'} with {len(urls)} canonical pages")


def build_html_sitemap():
    base_url = "https://takalenny-blip.github.io/ai-project"
    public_pages = []
    for page_path in sorted(DIST.glob("*.html")):
        if page_path.name == "sitemap.html":
            continue
        page_html = page_path.read_text(encoding="utf-8")
        canonical_match = re.search(
            r'<link rel="canonical" href="([^"]+)"',
            page_html,
        )
        title_match = re.search(r"<title>(.*?)</title>", page_html, re.DOTALL)
        if not canonical_match or not title_match:
            continue
        canonical_url = html_module.unescape(canonical_match.group(1))
        if canonical_url.rstrip("/") != base_url and not canonical_url.startswith(base_url + "/"):
            continue
        href = "./" if page_path.name == "index.html" else page_path.name
        title = html_module.unescape(title_match.group(1).strip())
        public_pages.append((href, title))

    if not any(href == "./" for href, _ in public_pages):
        raise SystemExit("HTML sitemap generation failed: public homepage is missing")
    if not public_pages:
        raise SystemExit("HTML sitemap generation failed: no public pages found")

    links = "\n".join(
        f'<li><a href="{html_module.escape(href, quote=True)}">{html_module.escape(title)}</a></li>'
        for href, title in public_pages
    )
    html_sitemap = f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>サイトマップ｜たか’sブログ</title>
<meta name="description" content="たか’sブログの記事一覧。">
<link rel="canonical" href="{base_url}/sitemap.html">
<style>
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: #363636; color: #eee7db; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans JP", sans-serif; line-height: 1.9; }}
main {{ max-width: 850px; margin: 0 auto; padding: 48px 24px 72px; }}
h1 {{ font-family: Georgia, "Noto Serif JP", serif; font-weight: 500; }}
p {{ color: #aaa093; }}
ul {{ list-style: none; padding: 0; }}
li {{ padding: 18px 0; border-bottom: 1px solid #3d3933; }}
a {{ color: #c4a46a; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
.home {{ display: inline-block; margin-top: 30px; }}
.site-footer {{ border-top:1px solid #3d3933; color:#aaa093; text-align:center; padding:30px 18px; font-size:.76rem; letter-spacing:.04em; }}
.site-footer p {{ margin:.8em 0 0; }}
</style>
</head>
<body>
<main>
<h1>サイトマップ</h1>
<p>たか’sブログの記事一覧</p>
<ul>
{links}
</ul>
<a class="home" href="./">← トップページへ戻る</a>
</main>
{render_footer()}
</body>
</html>
"""
    (DIST / "sitemap.html").write_text(html_sitemap, encoding="utf-8")
    print(f"built {DIST / 'sitemap.html'} with {len(public_pages)} public pages")


def build_static_page(title, permalink, description, body):
    canonical_url = f"https://takalenny-blip.github.io/ai-project/{permalink}"
    page_html = f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}｜たか’sブログ</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical_url}">
<style>
* {{ box-sizing:border-box; }}
:root {{ --ink:#eee7db; --muted:#aaa093; --paper:#363636; --cream:#2d2b28; --line:#3d3933; --accent:#b3945a; }}
body {{ margin:0; background:var(--paper); color:var(--ink); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans JP",sans-serif; line-height:1.9; }}
.site-header {{ max-width:1120px; margin:0 auto; padding:30px 28px 26px; }}
.site-header img {{ display:block; width:100%; max-height:240px; object-fit:cover; height:auto; border:1px solid var(--line); }}
.banner {{ border-block:1px solid var(--line); background:var(--cream); color:var(--muted); padding:13px max(18px, calc((100% - 1064px)/2)); font-size:.78rem; letter-spacing:.08em; }}
main {{ max-width:850px; margin:0 auto; padding:48px 24px 72px; }}
h1 {{ font-family:Georgia,"Noto Serif JP",serif; font-weight:500; line-height:1.45; }}
a {{ color:#c4a46a; }}
.site-footer {{ border-top:1px solid var(--line); color:var(--muted); text-align:center; padding:30px 18px; font-size:.76rem; letter-spacing:.04em; }}
.site-footer p {{ margin:.8em 0 0; }}
@media(max-width:700px) {{ .site-header {{ padding:22px 18px 18px; }} .site-header img {{ max-height:180px; }} main {{ padding:36px 18px 54px; }} }}
</style>
</head>
<body>
<header class="site-header"><a href="./" aria-label="たか’sブログ ホーム"><img src="images/taka-blog-banner.jpg" alt="たか’sブログ"></a></header>
<div class="banner">AIとのやりとりと、そこから生まれた経験を残していく</div>
<main>
<h1>{title}</h1>
{body}
</main>
{render_footer()}
</body>
</html>
"""
    (DIST / permalink).write_text(page_html, encoding="utf-8")


build_static_page(
    "ブログについて",
    "about.html",
    "たか’sブログの目的と、記事に残していることを紹介します。",
    "<p>このブログでは、AIとのやりとりをきっかけに生まれた試行錯誤や、そこから得た経験を記録しています。</p><p>完成した結果だけでなく、うまくいかなかったことや、考えが変わっていく過程も残していきます。</p>",
)
build_static_page(
    "プライバシーポリシー",
    "privacy.html",
    "たか’sブログにおける個人情報と外部サービスの取扱いについて。",
    "<p>このサイトには、現時点で問い合わせフォームやコメント投稿機能を設けていません。</p><p>サイトの閲覧に伴い、ホスティングサービスなどの提供元が技術的なアクセス情報を処理する場合があります。サービス側での情報の取扱いについては、それぞれの提供元が公開する方針をご確認ください。</p><p>記事から外部サイトへ移動した場合、そのサイトでの情報の取扱いは移動先の方針に従います。</p><p>個人情報を収集する機能や外部サービスを追加した場合は、このページの記載を見直します。</p>",
)
build_html_sitemap()
build_xml_sitemap()


def apply_accessible_link_colors():
    """Use one high-contrast link palette across generated public pages."""
    css = """<style id="accessible-link-colors">
nav a:link, nav a:visited,
.site-footer a:link, .site-footer a:visited,
.sidebar-section a:link, .sidebar-section a:visited,
.article-navigation a:link, .article-navigation a:visited,
.content a:link, .content a:visited,
main > a:link, main > a:visited {
  color: #9fd7ff;
  text-decoration-thickness: 0.08em;
  text-underline-offset: 0.18em;
}
nav a:hover, .site-footer a:hover, .sidebar-section a:hover,
.article-navigation a:hover, .content a:hover, main > a:hover {
  color: #ffffff;
  text-decoration: underline;
  text-decoration-thickness: 0.12em;
}
a:focus-visible {
  outline: 3px solid #ffd166;
  outline-offset: 3px;
  border-radius: 2px;
}
</style>"""
    for page_path in DIST.glob("*.html"):
        page_html = page_path.read_text(encoding="utf-8")
        if "</head>" not in page_html:
            raise SystemExit(f"cannot add accessible link colors: missing </head> in {page_path.name}")
        if 'id="accessible-link-colors"' not in page_html:
            page_html = page_html.replace("</head>", css + "\\n</head>", 1)
            page_path.write_text(page_html, encoding="utf-8")


apply_accessible_link_colors()

print(f"built {DIST / 'index.html'}")
print(f"built {DIST / PERMALINK}")
print(f"built {DIST / BLOG1_PERMALINK}")
print(f"built {DIST / BLOG2_PERMALINK}")
print(f"images: {len(list((DIST / 'images').iterdir()))}")
