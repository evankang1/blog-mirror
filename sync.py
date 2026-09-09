from pathlib import Path
import re
from datetime import datetime, timezone

BASE_URL = "https://evankang1.github.io/blog-mirror/"
today = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sanitize_xml_or_html(text: str) -> str:
    text = re.sub(r'(?m)^<<<<<<<.*\n?', '', text)
    text = re.sub(r'(?m)^=======\n?', '', text)
    text = re.sub(r'(?m)^>>>>>>>.*\n?', '', text)
    text = re.sub(r'(?is)<\s*script\b[^>]*>.*?</\s*script\s*>', '', text)
    text = re.sub(r'(?is)<\s*script\b[^>]*?/?>', '', text)
    text = re.sub(r'(?is)</\s*script\s*>', '', text)
    return text


posts = sorted(Path("posts").glob("*.html"), reverse=True)
ids = []
for p in posts:
    m = re.search(r"(\d+)", p.stem)
    if m:
        ids.append(m.group(1))

sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
sitemap_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
sitemap_content += f'  <url><loc>{BASE_URL}</loc><lastmod>{today}</lastmod></url>\n'
for pid in ids:
    sitemap_content += f'  <url><loc>{BASE_URL}posts/{pid}.html</loc><lastmod>{today}</lastmod></url>\n'
sitemap_content += '</urlset>\n'

sitemap_content = sanitize_xml_or_html(sitemap_content)
Path("sitemap.xml").write_text(sitemap_content, encoding="utf-8")
Path(".nojekyll").touch()
print(f"Generated {len(ids)} urls, .nojekyll created")
