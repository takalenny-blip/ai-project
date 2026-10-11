import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = ROOT / "scripts" / "build_cloudflare_site.py"
DIST = ROOT / "dist"
BASE_URL = "https://takalenny-blip.github.io/ai-project"


class ArticleSeoMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(BUILD_SCRIPT)], cwd=ROOT, check=True)

    def assert_article_metadata(self, permalink, expected_title):
        html = (DIST / permalink).read_text(encoding="utf-8")
        expected_url = f"{BASE_URL}/{permalink}"
        self.assertIn(f"<title>{expected_title}</title>", html)
        self.assertIn(f'<meta name="description" content="{expected_title}">', html)
        self.assertIn(f'<link rel="canonical" href="{expected_url}">', html)
        self.assertIn(f'<meta property="og:title" content="{expected_title}">', html)
        self.assertIn(f'<meta property="og:url" content="{expected_url}">', html)

    def test_blog_0001_metadata_matches_its_own_url_and_title(self):
        self.assert_article_metadata(
            "ai-blog-start.html",
            "AIとのやりとりを残してみる――それは「便利そうだな」から始まった",
        )

    def test_blog_0002_metadata_matches_its_own_url_and_title(self):
        self.assert_article_metadata(
            "vaio-p-again-and-beyond.html",
            "もう一度動かしてみた――その先で考えたこと",
        )

    def test_blog_0003_metadata_matches_its_own_url_and_title(self):
        self.assert_article_metadata(
            "github-ai-conversation.html",
            "GitHub編：AIとのやりとりを、どうやって「残るもの」にしていったか",
        )

    def test_html_sitemap_lists_every_canonical_public_html_page(self):
        sitemap = (DIST / "sitemap.html").read_text(encoding="utf-8")
        self.assertIn("<title>サイトマップ｜たか’sブログ</title>", sitemap)
        self.assertIn('rel="canonical" href="https://takalenny-blip.github.io/ai-project/sitemap.html"', sitemap)
        public_page_count = 0
        for page_path in sorted(DIST.glob("*.html")):
            if page_path.name == "sitemap.html":
                continue
            page_html = page_path.read_text(encoding="utf-8")
            canonical = re.search(r'<link rel="canonical" href="([^"]+)"', page_html)
            title = re.search(r"<title>(.*?)</title>", page_html, re.DOTALL)
            if not canonical or not title:
                self.assertNotIn(page_path.name, sitemap)
                continue
            if not canonical.group(1).startswith(BASE_URL):
                self.assertNotIn(page_path.name, sitemap)
                continue
            public_page_count += 1
            expected_href = "./" if page_path.name == "index.html" else page_path.name
            self.assertIn(f'href="{expected_href}">{title.group(1)}</a>', sitemap)
        self.assertGreaterEqual(public_page_count, 4)
        self.assertIn('href="./">たか’sブログ</a>', sitemap)

    def test_home_and_article_pages_link_to_html_sitemap(self):
        for permalink in (
            "index.html",
            "ai-blog-start.html",
            "vaio-p-again-and-beyond.html",
            "github-ai-conversation.html",
        ):
            html = (DIST / permalink).read_text(encoding="utf-8")
            self.assertIn('href="sitemap.html">サイトマップ</a>', html)


if __name__ == "__main__":
    unittest.main()
