import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from scripts import sync


class NaverArticleExtractorTests(unittest.TestCase):
    def test_extracts_entire_nested_smarteditor_container(self):
        source = """
        <div class='outside'>ignore</div>
        <div class='se-main-container other'>
          <div class='se-component'><p>본문 &amp; 내용</p><div>중첩 내용</div></div>
          <img src='https://example.com/image.png'>
        </div>
        <div>ignore tail</div>
        """
        extractor = sync.NaverArticleExtractor()
        extractor.feed(source)

        result = "".join(extractor.parts)
        self.assertTrue(extractor.done)
        self.assertIn("본문 &amp; 내용", result)
        self.assertIn("중첩 내용", result)
        self.assertIn("<img src='https://example.com/image.png'>", result)
        self.assertNotIn("ignore tail", result)

    @patch("scripts.sync.urllib.request.urlopen")
    def test_fetches_article_container_from_naver(self, urlopen):
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return b"<div class='se-main-container'><p>Full article body with enough text to validate extraction</p></div>"

        urlopen.return_value = Response()
        result = sync.fetch_naver_article({"log_no": "123456789012"})

        self.assertIn("Full article body", result)
        request = urlopen.call_args.args[0]
        query = parse_qs(urlparse(request.full_url).query)
        self.assertEqual(query["blogId"], [sync.BLOG_ID])
        self.assertEqual(query["logNo"], ["123456789012"])

    def test_returns_none_when_naver_does_not_serve_article_markup(self):
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return b"<html><body>Unavailable</body></html>"

        with patch("scripts.sync.urllib.request.urlopen", return_value=Response()):
            self.assertIsNone(sync.fetch_naver_article({"log_no": "123456789012"}))


class SitemapTests(unittest.TestCase):
    def test_sitemap_contains_index_and_post_urls(self):
        items = [{
            "title": "제목",
            "link": "https://blog.naver.com/kevin-story2009/123456789012",
            "pubDate": "Wed, 11 Nov 2026 11:34:27 +0900",
            "log_no": "123456789012",
        }]

        document = sync.ET.fromstring(sync.make_sitemap(items, "https://example.github.io/blog-mirror/"))
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locations = [node.text for node in document.findall("s:url/s:loc", ns)]
        self.assertEqual(locations, [
            "https://example.github.io/blog-mirror/",
            "https://example.github.io/blog-mirror/posts/123456789012.html",
        ])


if __name__ == "__main__":
    unittest.main()
