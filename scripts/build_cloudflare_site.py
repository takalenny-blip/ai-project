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

if not SOURCE.is_file():
    raise SystemExit(f"missing source: {SOURCE}")

if DIST.exists():
    shutil.rmtree(DIST)
(DIST / "images").mkdir(parents=True)

html = SOURCE.read_text(encoding="utf-8")

raw_base = "https://raw.githubusercontent.com/takalenny-blip/ai-project/main/docs/%E4%BC%81%E7%94%BB/BLOG-0003/images/"
html = html.replace(raw_base, "images/")

for image in sorted(IMAGE_DIR.iterdir()):
    if image.is_file():
        shutil.copy2(image, DIST / "images" / image.name)

page = f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<meta name="description" content="{TITLE}">
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

(DIST / "index.html").write_text(page, encoding="utf-8")
(DIST / PERMALINK).write_text(page, encoding="utf-8")

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
print(f"images: {len(list((DIST / 'images').iterdir()))}")
