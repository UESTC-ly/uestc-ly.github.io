#!/usr/bin/env python3
"""Validate all built pages, shared navigation, and local references."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
from bs4 import BeautifulSoup
from site_layout import ROOT, config

site = config()
modules = [ROOT / m['path'] / 'index.html' for m in site['modules']]
notes = [*(ROOT / 'notes').glob('*/index.html'), *(ROOT / 'notes').glob('*/n-*.html')]
pages = list(dict.fromkeys([*modules, *notes]))
soups = {p.resolve(): BeautifulSoup(p.read_text(), 'html.parser') for p in pages}
ids = {p: {t.get('id') for t in soup.select('[id]')} for p, soup in soups.items()}
references = 0
for path, soup in soups.items():
    assert len(soup.select('.site-header nav a')) == len(site['modules']) + 1, path
    assert len(soup.select('.site-header nav a[aria-current="page"]')) == 1, path
    assert len(soup.select('#docs-sidebar, .docs-outline, .site-search-trigger, .reader-bar')) == 4, path
    assert len(soup.select('#search-dialog, #global-search-input')) == 2, path
    if path.name.startswith('n-'):
        assert len(soup.select('.docs-sidebar a[aria-current="page"]')) == 1, path
        assert len(soup.select('.note-content')) == 1, path
    for tag, attribute in [('a', 'href'), ('img', 'src'), ('link', 'href'), ('script', 'src')]:
        for element in soup.select(f'{tag}[{attribute}]'):
            value = element[attribute]
            parsed = urlsplit(value)
            if parsed.scheme or value.startswith('//'):
                continue
            references += 1
            target = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            if target.is_dir():
                target /= 'index.html'
            assert target.exists(), f'{path.relative_to(ROOT)} -> {value}'
            if parsed.fragment and target in ids:
                assert unquote(parsed.fragment) in ids[target], f'{path.relative_to(ROOT)} -> {value}'
assert not soups[(ROOT / 'index.html').resolve()].select('.project-card, .topic-card, .system-card, #about')
assert len(list((ROOT / 'notes').glob('*/n-*.html'))) == len(__import__('json').loads((ROOT / 'notes/manifest.json').read_text()))
print(f'PASS {len(pages)} pages, {references} local references, shared navigation, and minimal homepage.')
