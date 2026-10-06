#!/usr/bin/env python3
"""Build module pages and refresh shared chrome without reimporting note content."""
import re
from bs4 import BeautifulSoup
from site_layout import ROOT, config, render_page, module_url, relative

def build():
    site = config()
    for module in site['modules']:
        if not module.get('template'):
            continue
        path = ROOT / module['path'] / 'index.html'
        body = (ROOT / 'templates/pages' / module['template']).read_text()
        body = re.sub(r'\{\{url:([\w-]+)\}\}', lambda m: module_url(path, m[1]), body)
        body = re.sub(r'\{\{asset:([^}]+)\}\}', lambda m: relative(path, ROOT / m[1]), body)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_page(module['title'], module['description'], path, body, active=module['id']))
    # Preserve all article content, anchors and page-specific rendering assets.
    pages = [ROOT / 'notes/index.html', *(ROOT / 'notes').glob('*/index.html'), *(ROOT / 'notes').glob('*/n-*.html')]
    for path in pages:
        if not path.exists():
            continue
        soup = BeautifulSoup(path.read_text(), 'html.parser')
        description = soup.select_one('meta[name="description"]')['content']
        main = soup.select_one('main')
        extra = ''.join(str(tag) for tag in soup.head.select('script[src], link[rel="stylesheet"]')
                        if any(item in tag.get('src', tag.get('href', '')) for item in ('katex/', 'render-diagrams.js', 'article.js', 'search.js')))
        path.write_text(render_page(soup.title.get_text(), description, path, main.decode_contents(), extra=extra))
    print(f'Built {sum(bool(m.get("template")) for m in site["modules"])} module pages; refreshed {len(pages)} note pages.')

if __name__ == '__main__':
    build()
