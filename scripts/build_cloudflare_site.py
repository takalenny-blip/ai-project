#!/usr/bin/env python3
"""Build the BLOG-0003 production page for GitHub Pages."""

from pathlib import Path
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
<meta name="description" content="{TITLE}">
<meta name="google-site-verification" content="Iaufdzv8o8vilCmpJ1WqXyjSyYZtNh13gEXbhYTgV0Y">
<link rel="canonical" href="https://takalenny-blip.github.io/ai-project/{PERMALINK}">
<meta property="og:type" content="article">
<meta property="og:title" content="{TITLE}">
<meta property="og:url" content="https://takalenny-blip.github.io/ai-project/{PERMALINK}">
<style>
* {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}
:root {{ --ink:#eee7db; --muted:#aaa093; --paper:#242424; --cream:#2d2b28; --line:#3d3933; --accent:#b3945a; }}
body {{ margin:0; background:var(--paper); color:var(--ink); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans JP",sans-serif; line-height:1.95; }}
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
blockquote {{ margin:2em 0; padding:1.1em 1.4em; background:#302e2a; border-left:3px solid var(--accent); }}
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
    <aside class="profile" aria-label="プロフィール">
      <p class="profile-label">PROFILE</p>
      <div class="profile-icon" aria-hidden="true">た</div>
      <p>たか</p>
      <p>AIとのやりとりと、その過程を記録しています。</p>
    </aside>
  </div>
</main>
<footer class="site-footer">たか’sブログ</footer>
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
<meta name="google-site-verification" content="Iaufdzv8o8vilCmpJ1WqXyjSyYZtNh13gEXbhYTgV0Y">
<link rel="canonical" href="https://takalenny-blip.github.io/ai-project/">
<style>
* { box-sizing:border-box; }
:root { --ink:#eee7db; --muted:#aaa093; --paper:#242424; --cream:#2d2b28; --line:#3d3933; --accent:#b3945a; }
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
<aside class="profile" aria-label="プロフィール"><p class="profile-label">PROFILE</p><div class="profile-icon" aria-hidden="true">た</div><p><strong>たか</strong></p><p>AIとのやりとりと、その過程を記録しています。</p></aside>
</div>
<footer class="site-footer">たか’sブログ</footer>
</body>
</html>
"""
sitemap = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://takalenny-blip.github.io/ai-project/</loc></url>
  <url><loc>https://takalenny-blip.github.io/ai-project/ai-blog-start.html</loc></url>
  <url><loc>https://takalenny-blip.github.io/ai-project/vaio-p-again-and-beyond.html</loc></url>
  <url><loc>https://takalenny-blip.github.io/ai-project/github-ai-conversation.html</loc></url>
</urlset>
"""
(DIST / "sitemap.xml").write_text(sitemap, encoding="utf-8")

(DIST / "index.html").write_text(home, encoding="utf-8")
(DIST / PERMALINK).write_text(page, encoding="utf-8")

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
    start = base_page.index("      <h1>")
    end = base_page.index("    </article>", start)
    replacement = f"""      <h1>{title}</h1>
      <p class="post-meta">固定ページ：{permalink}</p>
      {body_html}
"""
    return base_page[:start] + replacement + base_page[end:]

page1 = article_variant(page, BLOG1_TITLE, BLOG1_PERMALINK, blog1_html)
page2 = article_variant(page, BLOG2_TITLE, BLOG2_PERMALINK, blog2_html)
(DIST / BLOG1_PERMALINK).write_text(page1, encoding="utf-8")
(DIST / BLOG2_PERMALINK).write_text(page2, encoding="utf-8")

if re.search(r"https://raw\.githubusercontent\.com/.*/BLOG-0003/images/", html):
    raise SystemExit("unrewritten raw GitHub image URL remains")

missing = [
    name for name in re.findall(r'src="images/([^"]+)"', html)
    if not (DIST / "images" / name).is_file()
]
if missing:
    raise SystemExit("missing local images: " + ", ".join(sorted(set(missing))))

print(f"built {DIST / 'index.html'}")
print(f"built {DIST / PERMALINK}")
print(f"built {DIST / BLOG1_PERMALINK}")
print(f"built {DIST / BLOG2_PERMALINK}")
print(f"images: {len(list((DIST / 'images').iterdir()))}")
