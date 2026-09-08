import urllib.request
import xml.etree.ElementTree as ET
import os, json, re, html
from datetime import datetime, timezone
from pathlib import Path
import hashlib

BLOG_ID = "kevin-story2009"
RSS_URL = f"https://rss.blog.naver.com/{BLOG_ID}.xml"
BASE_DIR = Path(__file__).resolve().parent.parent
POSTS_DIR = BASE_DIR / "posts"
POSTS_INDEX_FILE = BASE_DIR / "posts_index.json"
INDEX_FILE = BASE_DIR / "index.html"
SITEMAP_FILE = BASE_DIR / "sitemap.xml"
ROBOTS_FILE = BASE_DIR / "robots.txt"
GITHUB_PAGES_BASE = "https://evankang1.github.io/blog-mirror/"

def clean_html(raw_desc):
    # Naver RSS description contains HTML, keep it but strip excessive scripts
    # Remove CDATA wrapper if present
    return raw_desc

def load_index():
    if POSTS_INDEX_FILE.exists():
        try:
            return json.loads(POSTS_INDEX_FILE.read_text(encoding="utf-8"))
        except:
            return {}
    return {}

def save_index(data):
    POSTS_INDEX_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def make_post_html(item):
    title_esc = html.escape(item["title"])
    desc = clean_html(item["description"])
    pub = html.escape(item["pubDate"])
    orig_link = html.escape(item["link"])
    # Simple SEO friendly template
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title_esc} - orion 블로그</title>
<meta name="description" content="{html.escape(re.sub('<[^<]+?>','', item['description'])[:150])}">
<link rel="canonical" href="{orig_link}">
<meta property="og:title" content="{title_esc}">
<meta property="og:description" content="{html.escape(re.sub('<[^<]+?>','', item['description'])[:150])}">
<meta property="og:url" content="{orig_link}">
<meta name="robots" content="index, follow">
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,'Noto Sans KR',sans-serif;max-width:760px;margin:0 auto;padding:24px;line-height:1.7;color:#222}}
a{{color:#03c75a;text-decoration:none}} a:hover{{text-decoration:underline}}
header{{border-bottom:2px solid #03c75a;padding-bottom:16px;margin-bottom:24px}}
h1{{font-size:1.8rem;margin:0 0 8px}}
.meta{{color:#666;font-size:.9rem}}
.content img{{max-width:100%;height:auto}}
.back{{display:inline-block;margin-bottom:16px}}
</style>
</head>
<body>
<header>
<a class="back" href="../index.html">← 목록으로</a>
<h1>{title_esc}</h1>
<div class="meta">{pub} | 원본: <a href="{orig_link}" target="_blank" rel="noopener">{orig_link}</a></div>
</header>
<article class="content">
{desc}
</article>
<footer style="margin-top:40px;padding-top:16px;border-top:1px solid #eee;color:#888;font-size:.85rem">
이 페이지는 <a href="{orig_link}">네이버 블로그 원본</a>의 검색엔진 노출을 위한 미러입니다. 모든 저작권은 원 작성자에게 있습니다.
</footer>
</body>
</html>
"""
    return html_content

def make_index_html(items):
    # sort by pubDate desc
    sorted_items = sorted(items, key=lambda x: x.get("pubDate",""), reverse=True)
    list_html = ""
    for it in sorted_items:
        title = html.escape(it["title"])
        link = f"posts/{it['log_no']}.html"
        pub = html.escape(it["pubDate"])
        orig = html.escape(it["link"])
        list_html += f'<li><a href="{link}"><strong>{title}</strong></a><br><span style="color:#666;font-size:.85em">{pub} | <a href="{orig}" target="_blank">원본 보기</a></span></li>\n'
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    index_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>orion (kevin-story2009) 블로그 미러</title>
<meta name="description" content="네이버 블로그 kevin-story2009 (orion) 의 구글 검색 노출용 미러 사이트입니다. 골프, 반려동물, 러닝, AI 이야기">
<meta name="robots" content="index, follow">
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,'Noto Sans KR',sans-serif;max-width:760px;margin:0 auto;padding:24px;line-height:1.7}}
header{{border-bottom:3px solid #03c75a;padding-bottom:16px;margin-bottom:24px}}
h1{{margin:0}}
ul{{list-style:none;padding:0}} li{{padding:12px 0;border-bottom:1px solid #eee}}
a{{color:#03c75a;text-decoration:none}} a:hover{{text-decoration:underline}}
</style>
</head>
<body>
<header>
<h1>orion 블로그 (kevin-story2009) 미러</h1>
<p>네이버 블로그 <a href="https://blog.naver.com/kevin-story2009/" target="_blank">kevin-story2009</a> 의 글을 구글 검색엔진에 노출시키기 위한 미러 사이트입니다. 매일 오전 9시 자동 업데이트됩니다.</p>
<p style="color:#666;font-size:.9em">마지막 업데이트: {now} | 총 {len(sorted_items)}개 글</p>
</header>
<ul>
{list_html}
</ul>
<footer style="margin-top:40px;color:#888;font-size:.85em">© 2026 orion / kevin-story2009. Powered by GitHub Pages.</footer>
</body>
</html>
"""
    return index_html

def make_sitemap(items, base_url):
    # base_url should be like https://username.github.io/repo/
    if not base_url.endswith("/"):
        base_url += "/"
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
    urlset = ET.Element("{http://www.sitemaps.org/schemas/sitemap/0.9}urlset")

    def add_url(loc, lastmod, changefreq, priority):
        url = ET.SubElement(urlset, "{http://www.sitemaps.org/schemas/sitemap/0.9}url")
        ET.SubElement(url, "{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text = loc
        ET.SubElement(url, "{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod").text = lastmod
        ET.SubElement(url, "{http://www.sitemaps.org/schemas/sitemap/0.9}changefreq").text = changefreq
        ET.SubElement(url, "{http://www.sitemaps.org/schemas/sitemap/0.9}priority").text = priority

    add_url(base_url, now_iso, "daily", "1.0")
    for it in items:
        loc = f"{base_url}posts/{it['log_no']}.html"
        # try parse pubDate to iso
        lastmod = now_iso
        try:
            # Naver pubDate format: Wed, 14 Dec 2023 17:06:00 +0900
            dt = datetime.strptime(it["pubDate"], "%a, %d %b %Y %H:%M:%S %z")
            lastmod = dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        except:
            pass
        add_url(loc, lastmod, "weekly", "0.8")

    return ET.tostring(urlset, encoding="unicode", xml_declaration=True)

def main():
    POSTS_DIR.mkdir(exist_ok=True)
    xml_bytes = fetch_rss()
    items = parse_rss(xml_bytes)
    print(f"Found {len(items)} items")
    if not items:
        print("No items, check RSS 공개 설정")
        return
    
    index_data = load_index()
    # save posts
    for it in items:
        path = POSTS_DIR / f"{it['log_no']}.html"
        html_str = make_post_html(it)
        path.write_text(html_str, encoding="utf-8")
        index_data[it["log_no"]] = {"title": it["title"], "link": it["link"], "pubDate": it["pubDate"]}
    
    # Determine base URL for sitemap: try env var, fallback to GITHUB_PAGES_BASE
    base_url = os.environ.get("PAGES_BASE_URL") or GITHUB_PAGES_BASE
    # Write files
    INDEX_FILE.write_text(make_index_html(items), encoding="utf-8")
    SITEMAP_FILE.write_text(make_sitemap(items, base_url), encoding="utf-8")
    ROBOTS_FILE.write_text(f"User-agent: *\nAllow: /\nSitemap: {base_url.rstrip('/')}/sitemap.xml\n", encoding="utf-8")
    save_index(index_data)
    print("Done")

if __name__ == "__main__":
    main()
