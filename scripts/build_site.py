#!/usr/bin/env python3
"""Build module pages and refresh shared chrome without reimporting note content."""
import re
from bs4 import BeautifulSoup
from site_layout import ROOT, config, render_page, module_url, relative, icon
import json
from docs_layout import group_id

def refresh_note_chrome(main, path):
    topics = {t['id']: t for t in json.loads((ROOT / 'config/topics.json').read_text())}
    if path == ROOT / 'notes/index.html':
        main.select_one('.notes-hero h1').string = '专题笔记'
        main.select_one('.notes-description').string = '按专题整理算法、计算机基础与 AI 技术笔记，收录概念、方法和开发实践。'
    for group in main.select('.note-group[data-group]'):
        heading = group.select_one('h2')
        label = ''.join(str(text) for text in heading.find_all(string=True, recursive=False)).strip()
        group['id'] = group_id(label)
    for card in main.select('.topic-card'):
        card.find(['h2', 'h3']).name = 'h2'
        topic_id = card['href'].split('/')[0]
        if topic_id in topics:
            card.select_one('.topic-symbol').clear()
            card.select_one('.topic-symbol').append(BeautifulSoup(icon(topics[topic_id].get('icon', 'book-open')), 'html.parser'))
            bottom = card.select_one('.topic-card-bottom > span:last-child')
            bottom.clear()
            bottom.append('进入专题 ')
            bottom.append(BeautifulSoup(icon('arrow-up-right'), 'html.parser'))
    symbol = main.select_one('.topic-hero-symbol')
    if symbol and path.parent.name in topics:
        symbol.clear()
        symbol['aria-hidden'] = 'true'
        symbol.append(BeautifulSoup(icon(topics[path.parent.name].get('icon', 'book-open')), 'html.parser'))
    search = main.select_one('#note-search')
    if search and 'search-field' not in search.parent.get('class', []):
        field = BeautifulSoup('', 'html.parser').new_tag('div')
        field['class'] = 'search-field'
        search.wrap(field)
        field.insert(0, BeautifulSoup(icon('search'), 'html.parser'))

def build():
    site = config()
    for module in site['modules']:
        if not module.get('template'):
            continue
        path = ROOT / module['path'] / 'index.html'
        body = (ROOT / 'templates/pages' / module['template']).read_text()
        body = re.sub(r'\{\{url:([\w-]+)\}\}', lambda m: module_url(path, m[1]), body)
        body = re.sub(r'\{\{asset:([^}]+)\}\}', lambda m: relative(path, ROOT / m[1]), body)
        body = re.sub(r'\{\{icon:([\w-]+)\}\}', lambda m: icon(m[1]), body)
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
        refresh_note_chrome(main, path)
        extra = ''.join(str(tag) for tag in soup.head.select('script[src], link[rel="stylesheet"]')
                        if any(item in tag.get('src', tag.get('href', '')) for item in ('katex/', 'render-diagrams.js', 'article.js', 'search.js')))
        path.write_text(render_page(soup.title.get_text(), description, path, main.decode_contents(), extra=extra))
    print(f'Built {sum(bool(m.get("template")) for m in site["modules"])} module pages; refreshed {len(pages)} note pages.')

if __name__ == '__main__':
    build()
