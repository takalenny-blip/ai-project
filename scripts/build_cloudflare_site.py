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
body {{ margin: 0; background: #f3f0eb; color: #333; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans JP", sans-serif; line-height: 1.9; }}
.site-header {{ background: #fff; border-bottom: 1px solid #ddd; }}
.header-inner {{ max-width: 1040px; margin: 0 auto; padding: 30px 22px 24px; }}
.blog-name {{ margin: 0; font-size: 1.35rem; color: #333; letter-spacing: .04em; font-weight: 600; }}
.banner {{ background: #4a4a4a; color: #fff; }}
.banner-inner {{ max-width: 1040px; margin: 0 auto; padding: 12px 22px; font-size: .9rem; }}
.layout {{ display: grid; grid-template-columns: minmax(0, 1fr) 250px; gap: 28px; align-items: start; }}
.profile {{ display: block; margin: 0; padding: 18px 16px; background: #faf8f5; border: 1px solid #e5e0da; border-radius: 8px; position: sticky; top: 20px; }}
.profile-icon {{ width: 54px; height: 54px; margin-bottom: 12px; border-radius: 50%; display: grid; place-items: center; background: #ddd; font-weight: 700; }}
.profile p {{ margin: 0; }}
main {{ max-width: 1040px; margin: 0 auto; padding: 34px 22px 72px; }}
article {{ background: #fff; padding: 42px 52px; border-radius: 10px; box-shadow: 0 2px 14px rgba(0,0,0,.07); }}
h1 {{ font-size: clamp(1.8rem, 4vw, 2.5rem); line-height: 1.4; margin: 0 0 1.2em; }}
h2 {{ margin-top: 3em; padding-bottom: .35em; border-bottom: 2px solid #ddd; line-height: 1.45; }}
h3 {{ margin-top: 2.2em; line-height: 1.5; }}
p {{ margin: 1em 0; }}
blockquote {{ background: #fafafa; }}
nav {{ margin: 2em 0; padding: 1.2em 1.4em; background: #f7f7f7; border: 1px solid #e5e5e5; border-radius: 8px; }}
nav ul {{ margin: 0; padding-left: 1.4em; }}
nav li {{ margin: .35em 0; }}
a {{ color: #1769aa; }}
figure {{ margin: 2em auto !important; }}
figure img {{ border-radius: 6px; display: block; height: auto; max-width: 100%; }}
figcaption {{ margin-top: .55em; color: #666; font-size: .9em; }}
.flow-box {{ background: #fafafa; }}
code {{ background: #f1f1f1; padding: .1em .3em; border-radius: 3px; }}
.post-meta {{ margin: -1em 0 2em; color: #777; font-size: .9rem; }}
.site-footer {{ border-top: 1px solid #ddd; background: #fff; color: #777; text-align: center; padding: 28px 18px; font-size: .85rem; }}
@media (max-width: 760px) {{ main {{ padding: 12px 8px 40px; }} .layout {{ grid-template-columns: 1fr; gap: 16px; }} article {{ padding: 24px 18px; border-radius: 6px; }} .header-inner {{ padding: 22px 16px; }} .profile {{ position: static; }} }}
</style>
</head>
<body>
<header class="site-header">
  <div class="header-inner">
    <p class="blog-name">たか’sブログ</p>
  </div>
</header>
<div class="banner"><div class="banner-inner">AIとのやりとりと、そこから生まれた経験を残していく</div></div>
<main>
  <div class="layout">
    <article>
      <h1>{TITLE}</h1>
      <p class="post-meta">固定ページ：{PERMALINK}</p>
      {html}
    </article>
    <aside class="profile" aria-label="プロフィール">
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

home = f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>たか’sブログ</title>
<meta name="description" content="AIとのやりとりと、そこから生まれた経験を残していくブログです。">
<link rel="canonical" href="https://takalenny-blip.github.io/ai-project/">
<style>
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: #f3f0eb; color: #333; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans JP", sans-serif; line-height: 1.8; }}
.site-header {{ background: #fff; border-bottom: 1px solid #ddd; }}
.header-inner {{ max-width: 1040px; margin: 0 auto; padding: 30px 22px 24px; }}
.blog-name {{ margin: 0; font-size: 1.35rem; font-weight: 600; letter-spacing: .04em; }}
.banner {{ background: #4a4a4a; color: #fff; }}
.banner-inner {{ max-width: 1040px; margin: 0 auto; padding: 12px 22px; font-size: .9rem; }}
.layout {{ display: grid; grid-template-columns: minmax(0, 1fr) 250px; gap: 28px; align-items: start; max-width: 1040px; margin: 0 auto; padding: 34px 22px 72px; }}
.content {{ background: #fff; padding: 36px 40px; border-radius: 10px; box-shadow: 0 2px 14px rgba(0,0,0,.07); }}
.content h1 {{ margin: 0 0 1.4em; font-size: 2rem; }}
.card {{ display: block; margin: 0 0 18px; padding: 22px 24px; border: 1px solid #e3ded8; border-radius: 10px; background: #faf8f5; color: inherit; text-decoration: none; }}
.card:hover {{ border-color: #bbb; }}
.part {{ margin: 0 0 .35em; font-size: .82rem; color: #777; }}
.card h2 {{ margin: 0 0 .5em; font-size: 1.25rem; line-height: 1.5; }}
.card p {{ margin: 0; color: #666; font-size: .92rem; }}
.profile {{ padding: 18px 16px; background: #faf8f5; border: 1px solid #e5e0da; border-radius: 8px; position: sticky; top: 20px; }}
.profile-icon {{ width: 54px; height: 54px; margin-bottom: 12px; border-radius: 50%; display: grid; place-items: center; background: #ddd; font-weight: 700; }}
.profile p {{ margin: 0; }}
.site-footer {{ border-top: 1px solid #ddd; background: #fff; color: #777; text-align: center; padding: 28px 18px; font-size: .85rem; }}
@media (max-width: 760px) {{ .layout {{ grid-template-columns: 1fr; padding: 12px 8px 40px; }} .content {{ padding: 24px 18px; }} .header-inner {{ padding: 22px 16px; }} .profile {{ position: static; }} }}
</style>
</head>
<body>
<header class="site-header"><div class="header-inner"><p class="blog-name">たか’sブログ</p></div></header>
<div class="banner"><div class="banner-inner">AIとのやりとりと、そこから生まれた経験を残していく</div></div>
<div class="layout">
<section class="content">
<h1>記事一覧</h1>
<a class="card" href="ai-blog-start.html"><p class="part">第1部｜経験ログ</p><h2>AIとのやりとりを残してみる――それは「便利そうだな」から始まった</h2><p>AIと一緒にブログを作ろうと思うまでの始まり。</p></a>
<a class="card" href="vaio-p-again-and-beyond.html"><p class="part">第2部｜VAIO P</p><h2>もう一度動かしてみた――その先で考えたこと</h2><p>AIと一緒に進める中で、VAIO Pをもう一度動かしていった記録。</p></a>
<a class="card" href="github-ai-conversation.html"><p class="part">第3部｜GitHub</p><h2>AIとのやりとりを「残るもの」にしていった――GitHubで作った仕組み</h2><p>AIとのやりとりを保存し、現在を間違えない仕組みにしていった経験。</p></a>
</section>
<aside class="profile" aria-label="プロフィール"><div class="profile-icon" aria-hidden="true">た</div><p><strong>たか</strong></p><p>AIとのやりとりと、その過程を記録しています。</p></aside>
</div>
<footer class="site-footer">たか’sブログ</footer>
</body>
</html>
"""
(DIST / "index.html").write_text(home, encoding="utf-8")
(DIST / PERMALINK).write_text(page, encoding="utf-8")

def article_variant(base_page, title, permalink, body_html):
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
