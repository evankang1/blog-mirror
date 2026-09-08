
from pathlib import Path
import re
from datetime import datetime, timezone

BASE_URL = "https://evankang1.github.io/blog-mirror/"
today = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

posts = sorted(Path("posts").glob("*.html"), reverse=True)
ids = [re.search(r"(\d+)", p.stem).group(1) for p in posts if re.search(r"(\d+)", p.stem)]

with open("sitemap.xml", "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    f.write(f'  <url><loc>{BASE_URL}</loc><lastmod>{today}</lastmod></url>\n')
    for pid in ids:
        f.write(f'  <url><loc>{BASE_URL}posts/{pid}.html</loc><lastmod>{today}</lastmod></url>\n')
    f.write('</urlset>\n')

Path(".nojekyll").touch()
