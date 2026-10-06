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

(DIST / "index.html").write_text(html, encoding="utf-8")

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
