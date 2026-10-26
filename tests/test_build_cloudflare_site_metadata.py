import json
import re
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET
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
        expected_descriptions = {
            "ai-blog-start.html": "AIとのやりとりからブログ制作の仕組みを考え始めた記録。Claudeのブラウザ操作をきっかけに、GeminiやPythonでの自動化、経験を記事として残す発想につながっていく。",
            "vaio-p-again-and-beyond.html": "VAIO Pをもう一度動かすためにDebianを導入し、環境を整えた記録。DIGA／DiMORAの番組予約情報を扱う自動化テストを通して、試行錯誤と次の発想を振り返る。",
            "github-ai-conversation.html": "AIとのやりとりをGitHubに残し、現在状態や作業の進み具合を管理する仕組みを作った経験。会話を保存するだけでなく、あとから再開できる形に整えていく過程を紹介する。",
            "ai-trial-and-record.html": "AIと一緒に試し、結果や失敗を確かめ、経験を記録して次の作業につなげる。ブログ制作や古いPCの再活用、GitHubでの作業管理を通して学んだ、AIとの付き合い方を紹介する。",
        }
        self.assertIn(
            f'<meta name="description" content="{expected_descriptions[permalink]}">',
            html,
        )
        self.assertIn(
            f'<meta property="og:description" content="{expected_descriptions[permalink]}">',
            html,
        )
        self.assertNotEqual(expected_descriptions[permalink], expected_title)
        self.assertIn(f'<link rel="canonical" href="{expected_url}">', html)
        self.assertIn(f'<meta property="og:title" content="{expected_title}">', html)
        self.assertIn(f'<meta property="og:url" content="{expected_url}">', html)
        self.assertIn(
            '<meta property="og:image" content="https://takalenny-blip.github.io/ai-project/images/taka-blog-banner.jpg">',
            html,
        )
        self.assertIn('<meta name="twitter:card" content="summary_large_image">', html)

    def test_series_title_and_article_parts_are_rendered_consistently(self):
        expected_parts = {
            "ai-blog-start.html": "第1部｜経験ログ",
            "vaio-p-again-and-beyond.html": "第2部｜VAIO P",
            "github-ai-conversation.html": "第3部｜GitHub",
            "ai-trial-and-record.html": "総括・実践ガイドのご案内",
        }
        for permalink, part in expected_parts.items():
            with self.subTest(permalink=permalink):
                html = (DIST / permalink).read_text(encoding="utf-8")
                self.assertIn("AIと一緒に。無料で試して、残して、育てる", html)
                self.assertIn(f'<p class="eyebrow">{part}</p>', html)
        home = (DIST / "index.html").read_text(encoding="utf-8")
        self.assertIn("AIと一緒に。無料で試して、残して、育てる", home)
        self.assertNotIn("{SERIES_TITLE}", home)

    def test_blog_0004_four_panel_manga_is_rendered(self):
        html = (DIST / "ai-trial-and-record.html").read_text(encoding="utf-8")
        self.assertIn('<figure class="blog4-manga">', html)
        self.assertIn(
            'src="https://raw.githubusercontent.com/takalenny-blip/ai-project/main/docs/%E4%BC%81%E7%94%BB/BLOG-0004/images/blog-0004-four-panel.png"',
            html,
        )
        self.assertIn('alt="AIと試し、結果を確かめ、経験を記録して次につなげる流れを描いた4コマ漫画"', html)
        self.assertIn("試して、確かめて、記録する。AIとの実践で大切にしていること。", html)

    def test_blog_0001_metadata_matches_its_own_url_and_title(self):
        self.assert_article_metadata(
            "ai-blog-start.html",
            "第1部｜AIとのやりとりを残してみる――それは「便利そうだな」から始まった",
        )

    def test_blog_0002_metadata_matches_its_own_url_and_title(self):
        self.assert_article_metadata(
            "vaio-p-again-and-beyond.html",
            "第2部｜もう一度動かしてみた――その先で考えたこと",
        )

    def test_blog_0003_metadata_matches_its_own_url_and_title(self):
        self.assert_article_metadata(
            "github-ai-conversation.html",
            "第3部｜GitHub編：AIとのやりとりを、どうやって「残るもの」にしていったか",
        )

    def test_blog_0004_metadata_matches_its_own_url_and_title(self):
        self.assert_article_metadata(
            "ai-trial-and-record.html",
            "総括・実践ガイドのご案内｜AIを使うなら、会話だけで終わらせない。試行錯誤から学んだこと",
        )

    def test_canonical_pages_have_consistent_social_metadata_and_valid_json_ld(self):
        expected_types = {
            "index.html": ("website", "WebSite"),
            "ai-blog-start.html": ("article", "BlogPosting"),
            "vaio-p-again-and-beyond.html": ("article", "BlogPosting"),
            "github-ai-conversation.html": ("article", "BlogPosting"),
            "ai-trial-and-record.html": ("article", "BlogPosting"),
            "about.html": ("website", "AboutPage"),
            "privacy.html": ("website", "PrivacyPolicy"),
            "sitemap.html": ("website", "WebPage"),
        }
        for permalink, (og_type, schema_type) in expected_types.items():
            with self.subTest(permalink=permalink):
                html = (DIST / permalink).read_text(encoding="utf-8")
                self.assertIn(f'<meta property="og:type" content="{og_type}">', html)
                self.assertIn('<meta property="og:title" content="', html)
                self.assertIn('<meta property="og:description" content="', html)
                self.assertIn('<meta property="og:url" content="', html)
                self.assertIn(
                    '<meta property="og:image" content="https://takalenny-blip.github.io/ai-project/images/taka-blog-banner.jpg">',
                    html,
                )
                self.assertIn('<meta property="og:image:alt" content="たか’sブログのサイトバナー">', html)
                self.assertIn('<meta name="twitter:card" content="summary_large_image">', html)
                matches = re.findall(
                    r'<script type="application/ld\+json">(.*?)</script>',
                    html,
                    re.DOTALL,
                )
                self.assertEqual(len(matches), 1)
                schema = json.loads(matches[0])
                self.assertEqual(schema["@context"], "https://schema.org")
                self.assertEqual(schema["@type"], schema_type)
                self.assertEqual(schema["inLanguage"], "ja-JP")
                self.assertIn("url", schema)
                self.assertNotIn(r"\n", matches[0])

    def test_homepage_has_website_social_metadata(self):
        html = (DIST / "index.html").read_text(encoding="utf-8")
        self.assertIn('<meta property="og:type" content="website">', html)
        self.assertIn('<meta property="og:title" content="たか’sブログ">', html)
        self.assertIn(
            '<meta property="og:url" content="https://takalenny-blip.github.io/ai-project/">',
            html,
        )
        self.assertIn(
            '<meta property="og:image" content="https://takalenny-blip.github.io/ai-project/images/taka-blog-banner.jpg">',
            html,
        )
        self.assertIn('<meta name="twitter:card" content="summary_large_image">', html)

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


    def test_robots_txt_has_real_line_breaks_and_xml_sitemap_reference(self):
        robots = (DIST / "robots.txt").read_text(encoding="utf-8")
        self.assertEqual(
            robots,
            "User-agent: *\nAllow: /\n\nSitemap: https://takalenny-blip.github.io/ai-project/sitemap.xml\n",
        )


    def test_xml_sitemap_contains_all_canonical_content_pages_and_excludes_temporary_pages(self):
        sitemap = ET.fromstring((DIST / "sitemap.xml").read_text(encoding="utf-8"))
        namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = {
            node.text
            for node in sitemap.findall("sm:url/sm:loc", namespace)
        }
        expected = {
            f"{BASE_URL}/",
            f"{BASE_URL}/ai-blog-start.html",
            f"{BASE_URL}/vaio-p-again-and-beyond.html",
            f"{BASE_URL}/github-ai-conversation.html",
            f"{BASE_URL}/ai-trial-and-record.html",
            f"{BASE_URL}/about.html",
            f"{BASE_URL}/privacy.html",
        }
        self.assertEqual(urls, expected)
        self.assertNotIn(f"{BASE_URL}/sitemap.html", urls)
        self.assertNotIn(f"{BASE_URL}/quote-samples.html", urls)

    def test_temporary_quote_samples_page_is_noindex(self):
        html = (DIST / "quote-samples.html").read_text(encoding="utf-8")
        self.assertIn('<meta name="robots" content="noindex,follow">', html)
        xml_sitemap = (DIST / "sitemap.xml").read_text(encoding="utf-8")
        html_sitemap = (DIST / "sitemap.html").read_text(encoding="utf-8")
        self.assertNotIn("quote-samples.html", xml_sitemap)
        self.assertNotIn("quote-samples.html", html_sitemap)

    def test_generated_pages_have_alt_text_for_images_and_valid_local_image_paths(self):
        for page_path in sorted(DIST.glob("*.html")):
            with self.subTest(page=page_path.name):
                html = page_path.read_text(encoding="utf-8")
                for tag in re.findall(r"<img\b[^>]*>", html, re.IGNORECASE):
                    self.assertRegex(tag, r"""\balt=["\'][^"\']*["\']""")
                for image_name in re.findall(r'src="images/([^"]+)"', html):
                    self.assertTrue(
                        (DIST / "images" / image_name).is_file(),
                        f"{page_path.name} references missing image {image_name}",
                    )


    def test_navigation_links_use_accessible_unified_colors_and_keyboard_focus(self):
        for permalink in (
            "index.html",
            "ai-blog-start.html",
            "vaio-p-again-and-beyond.html",
            "github-ai-conversation.html",
            "ai-trial-and-record.html",
            "about.html",
            "privacy.html",
            "sitemap.html",
        ):
            html = (DIST / permalink).read_text(encoding="utf-8")
            self.assertIn('<style id="accessible-link-colors">', html)
            self.assertIn("color: #9fd7ff;", html)
            self.assertIn("color: #ffffff;", html)
            self.assertIn("outline: 3px solid #ffd166;", html)
            self.assertNotIn('id="accessible-link-colors"\\n</head>', html)

    def test_sidebar_and_footer_navigation_are_generated(self):
        for permalink in (
            "index.html",
            "ai-blog-start.html",
            "vaio-p-again-and-beyond.html",
            "github-ai-conversation.html",
            "ai-trial-and-record.html",
        ):
            html = (DIST / permalink).read_text(encoding="utf-8")
            self.assertIn('<nav class="sidebar-section" aria-label="記事を探す">', html)
            self.assertIn("最近の記事", html)
            self.assertIn('href="about.html">ブログについて</a>', html)
            self.assertIn('href="privacy.html">プライバシーポリシー</a>', html)
            self.assertIn('aria-label="フッターナビゲーション"', html)

    def test_article_navigation_has_story_neighbors_and_related_links(self):
        expected = {
            "ai-blog-start.html": (None, "vaio-p-again-and-beyond.html"),
            "vaio-p-again-and-beyond.html": ("ai-blog-start.html", "github-ai-conversation.html"),
            "github-ai-conversation.html": ("vaio-p-again-and-beyond.html", "ai-trial-and-record.html"),
            "ai-trial-and-record.html": ("github-ai-conversation.html", None),
        }
        for permalink, (previous, following) in expected.items():
            html = (DIST / permalink).read_text(encoding="utf-8")
            self.assertIn('aria-label="記事ナビゲーション"', html)
            self.assertIn("あわせて読みたい", html)
            if previous:
                self.assertIn(f'<a rel="prev" href="{previous}">', html)
            else:
                self.assertIn("前の記事はありません", html)
            if following:
                self.assertIn(f'<a rel="next" href="{following}">', html)
            else:
                self.assertIn("次の記事はありません", html)

    def test_about_and_privacy_pages_are_generated_and_listed(self):
        about = (DIST / "about.html").read_text(encoding="utf-8")
        privacy = (DIST / "privacy.html").read_text(encoding="utf-8")
        sitemap = (DIST / "sitemap.html").read_text(encoding="utf-8")
        self.assertIn('<link rel="canonical" href="https://takalenny-blip.github.io/ai-project/about.html">', about)
        self.assertIn('<link rel="canonical" href="https://takalenny-blip.github.io/ai-project/privacy.html">', privacy)
        self.assertIn("AIとのやりとりをきっかけに生まれた試行錯誤", about)
        self.assertIn("ホスティングサービス", privacy)
        self.assertIn('href="about.html">ブログについて｜たか’sブログ</a>', sitemap)
        self.assertIn('href="privacy.html">プライバシーポリシー｜たか’sブログ</a>', sitemap)
        self.assertIn('href="privacy.html">プライバシーポリシー</a>', about)
        self.assertIn('href="about.html">ブログについて</a>', privacy)

    def test_home_and_article_pages_link_to_html_sitemap(self):
        for permalink in (
            "index.html",
            "ai-blog-start.html",
            "vaio-p-again-and-beyond.html",
            "github-ai-conversation.html",
            "ai-trial-and-record.html",
        ):
            html = (DIST / permalink).read_text(encoding="utf-8")
            self.assertIn('href="sitemap.html">記事一覧</a>', html)
            self.assertIn('href="sitemap.html">すべての記事</a>', html)


if __name__ == "__main__":
    unittest.main()
