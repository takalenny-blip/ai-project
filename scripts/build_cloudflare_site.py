#!/usr/bin/env python3
"""Build a minimal Cloudflare Pages site from the canonical BLOG-0003 HTML."""

from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/企画/BLOG-0003/BLOG-0003_Blogger掲載用.html"
IMAGE_DIR = ROOT / "docs/企画/BLOG-0003/images"
DIST = ROOT / "dist"

if not SOURCE.is_file():
    raise SystemExit(f"missing source: {SOURCE}")

if DIST.exists():
    shutil.rmtree(DIST)
(DIST / "images").mkdir(parents=True)

html = SOURCE.read_text(encoding="utf-8")

raw_base = "https://raw.githubusercontent.com/takalenny-blip/ai-project/main/docs/%E4%BC%81%E7%94%BB/BLOG-0003/images/"
html = html.replace(raw_base, "/images/")

for image in sorted(IMAGE_DIR.iterdir()):
    if image.is_file():
        shutil.copy2(image, DIST / "images" / image.name)

page = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GitHub編：AIとのやりとりを、どうやって「残るもの」にしていったか</title>
<style>
* { box-sizing: border-box; }
body { margin: 0; background: #f6f4f0; color: #333; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans JP", sans-serif; line-height: 1.9; }
main { max-width: 900px; margin: 0 auto; padding: 36px 22px 72px; }
article { background: #fff; padding: 42px 52px; border-radius: 10px; box-shadow: 0 2px 14px rgba(0,0,0,.07); }
h1 { font-size: clamp(1.8rem, 4vw, 2.5rem); line-height: 1.4; margin: 0 0 2em; }
h2 { margin-top: 3em; padding-bottom: .35em; border-bottom: 2px solid #ddd; line-height: 1.45; }
h3 { margin-top: 2.2em; line-height: 1.5; }
p { margin: 1em 0; }
blockquote { background: #fafafa; }
nav { margin: 2em 0; padding: 1.2em 1.4em; background: #f7f7f7; border: 1px solid #e5e5e5; border-radius: 8px; }
nav ul { margin: 0; padding-left: 1.4em; }
nav li { margin: .35em 0; }
a { color: #1769aa; }
figure { margin: 2em auto !important; }
figure img { border-radius: 6px; }
figcaption { margin-top: .55em; color: #666; font-size: .9em; }
.flow-box { background: #fafafa; }
code { background: #f1f1f1; padding: .1em .3em; border-radius: 3px; }
@media (max-width: 650px) { main { padding: 12px 8px 40px; } article { padding: 24px 18px; border-radius: 6px; } }
</style>
</head>
<body><main><article>
<h1>GitHub編：AIとのやりとりを、どうやって「残るもの」にしていったか</h1>
""" + html + """
</article></main></body>
</html>
"""
(DIST / "index.html").write_text(page, encoding="utf-8")

# The minimal verification site must not retain the old raw-GitHub image host.
if re.search(r"https://raw\.githubusercontent\.com/.*/BLOG-0003/images/", html):
    raise SystemExit("unrewritten raw GitHub image URL remains")

missing = [
    name for name in re.findall(r'src="/images/([^"]+)"', html)
    if not (DIST / "images" / name).is_file()
]
if missing:
    raise SystemExit("missing local images: " + ", ".join(sorted(set(missing))))

print(f"built {DIST / 'index.html'}")
print(f"images: {len(list((DIST / 'images').iterdir()))}")
