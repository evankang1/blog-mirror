
import re
from pathlib import Path
from datetime import datetime, timezone

BASE_URL = "https://evankang1.github.io/blog-mirror/"
today = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

posts_dir = Path("posts")
posts = []
if posts_dir.exists():
    for f in sorted(posts_dir.glob("*.html"), reverse=True):
        m = re.search(r"(\d+)", f.stem)
        if m:
            posts.append(m.group(1))

# sitemap.xml은 순수 XML만 - script 절대 안 넣음
with open("sitemap.xml", "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    f.write(f'  <url><loc>{BASE_URL}</loc><lastmod>{today}</lastmod></url>\n')
    for pid in posts:
        f.write(f'  <url><loc>{BASE_URL}posts/{pid}.html</loc><lastmod>{today}</lastmod></url>\n')
    f.write('</urlset>\n')

# .nojekyll 빈 파일 만들기
Path(".nojekyll").touch()
