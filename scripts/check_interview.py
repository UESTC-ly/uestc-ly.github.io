#!/usr/bin/env python3
"""Check publication completeness, preserved sources and every question deep link."""
from pathlib import Path
import argparse
import json
import re
from bs4 import BeautifulSoup
from interview import render_markdown

ROOT = Path(__file__).resolve().parents[1]
PREFIX = '知识库/八股题库搜集/'


def check(original=None):
    regression = '<a id="k001"></a>\n\n## One\n\n```jsx harmony\n<h2>{title}</h2>\n```\n\n<p align="center">\n<img src="example.png">\n\n<a id="k002"></a>\n\n## Two\n\nAnswer\n'
    sample = BeautifulSoup(render_markdown(regression), 'html.parser')
    assert [h.get_text() for h in sample.select('h2')] == ['One', 'Two']
    assert '<h2>{title}</h2>' in sample.select_one('pre code').get_text()
    manifest = json.loads((ROOT / 'notes/manifest.json').read_text())
    posts = [post for post in manifest if post['topic'] == 'interview']
    sources = ROOT / 'notes/source'
    published_sources = {post['source'].removeprefix(PREFIX) for post in posts}
    stored_sources = {p.relative_to(sources / PREFIX).as_posix() for p in (sources / PREFIX).rglob('*.md')}
    assert published_sources == stored_sources, 'Every original Markdown file needs an article'
    if original:
        originals = {p.relative_to(original).as_posix(): p for p in original.rglob('*.md')}
        assert published_sources == set(originals), 'Incomplete import'
        for relative, path in originals.items():
            assert path.read_bytes() == (sources / PREFIX / relative).read_bytes(), relative

    index = json.loads((ROOT / 'notes/interview/questions.json').read_text())
    hub = BeautifulSoup((ROOT / 'notes/interview/index.html').read_text(), 'html.parser')
    assert len(hub.select('.interview-category')) == 24
    assert len(hub.select('.interview-chapter')) == len(posts) - 1
    assert len(hub.select('.foundation-badge')) == 24
    assert len(index['chapters']) == len(posts) - 1
    assert hub.select_one('link[href="interview.css"]')
    assert hub.select_one('script[src="interview-search.js"]')
    pages = {}
    for post in posts:
        path = ROOT / post['url'].lstrip('/')
        soup = BeautifulSoup(path.read_text(), 'html.parser')
        assert len(soup.select('main h1')) == 1, post['source']
        assert not soup.select('.note-content script, .note-content iframe')
        assert soup.select_one('a[download]'), post['source']
        content = soup.select_one('.note-content')
        for anchor in re.findall(r'^<a id="([km][0-9a-f]+)"></a>', (sources / post['source']).read_text(), re.M):
            marker = content.find('a', id=anchor)
            assert marker is not None, ('Missing source knowledge point', post['source'], anchor)
            for node in marker.next_elements:
                if getattr(node, 'name', None) == 'h2':
                    break
                assert not (getattr(node, 'name', None) == 'a' and re.fullmatch(r'[km][0-9a-f]+', node.get('id', ''))), ('Unrendered knowledge point', post['source'], anchor)
            else:
                raise AssertionError(('No heading for knowledge point', post['source'], anchor))
        pages[path.name] = {h['id']: h.get_text(' ', strip=True) for h in soup.select('.note-content h2[id]')}
    seen = set()
    for chapter, anchor, title, excerpt in index['questions']:
        filename = index['chapters'][chapter][0]
        assert pages[filename].get(anchor) == title, (filename, anchor, title)
        assert (filename, anchor) not in seen, 'Question links must be unique'
        seen.add((filename, anchor))
    assert len(seen) == sum(len(pages[c[0]]) for c in index['chapters'])
    print(f'PASS {len(posts)} complete articles, 24 foundation notes, {len(seen)} verified question links; original Markdown preserved.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--original', type=Path)
    check(parser.parse_args().original)
