"""Shared static page shell and module registry. No client-side routing required."""
from pathlib import Path
from urllib.parse import quote
import html
import hashlib
import json
import os
import re
from functools import lru_cache
from bs4 import BeautifulSoup
from docs_layout import sidebar, outline, pagination

ROOT = Path(__file__).resolve().parents[1]

def config():
    data = json.loads((ROOT / 'config/site.json').read_text())
    modules = data['modules']
    if len({m['id'] for m in modules}) != len(modules):
        raise ValueError('Module IDs must be unique')
    if len({m['path'] for m in modules}) != len(modules):
        raise ValueError('Module paths must be unique')
    for module in modules:
        path = module['path']
        if path.startswith('/') or '..' in Path(path).parts or (path and not path.endswith('/')):
            raise ValueError(f'Invalid module path: {path}')
        template = module.get('template')
        if template and (Path(template).is_absolute() or '..' in Path(template).parts):
            raise ValueError(f'Invalid template path: {template}')
    return data

def esc(value):
    return html.escape(str(value), quote=True)

@lru_cache(maxsize=None)
def icon(name):
    """Inline a vetted local Lucide SVG; decorative icons never need JavaScript."""
    if not re.fullmatch(r'[a-z0-9-]+', name):
        raise ValueError(f'Invalid icon name: {name}')
    svg = (ROOT / 'assets/icons/lucide' / f'{name}.svg').read_text()
    svg = re.sub(r'class="[^"]*"', 'class="icon"', svg)
    svg = re.sub(r'\s+', ' ', svg).strip()
    return svg.replace('<svg', '<svg aria-hidden="true" focusable="false"', 1)

def relative(path, target):
    return quote(os.path.relpath(target, path.parent).replace(os.sep, '/'), safe='/')

def module_url(path, module_id):
    module = next(m for m in config()['modules'] if m['id'] == module_id)
    return relative(path, ROOT / module['path'] / 'index.html')

def header(path, active):
    site = config()
    brand = site.get('brand', site['name'])
    links = []
    for module in site['modules']:
        current = ' aria-current="page"' if module['id'] == active else ''
        href = relative(path, ROOT / module['path'] / 'index.html')
        links.append(f'<a href="{href}"{current}>{esc(module["label"])}</a>')
    links.append(f'<a class="nav-github" href="{esc(site["github"])}" target="_blank" rel="noopener noreferrer">GitHub {icon("arrow-up-right")}</a>')
    return f'''<div class="site-header-bar"><header class="header site-header">
  <a class="brand" href="{module_url(path, 'home')}" aria-label="ly. {esc(brand)}，返回首页"><span class="brand-mark">ly<span>.</span></span><span class="brand-name">{esc(brand)}</span></a>
  <a class="site-search-trigger" href="{module_url(path, 'notes')}" data-index="{relative(path, ROOT / 'notes/manifest.json')}" aria-label="搜索笔记，全部专题">{icon('search')}<span>搜索笔记</span><kbd aria-hidden="true">/</kbd></a>
  <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-navigation" hidden><span>菜单</span><span class="menu-open">{icon('menu')}</span><span class="menu-close">{icon('x')}</span></button>
  <nav id="site-navigation" aria-label="主导航">{''.join(links)}</nav>
</header></div>'''

def search_dialog():
    return f'''<dialog id="search-dialog" class="search-dialog" aria-labelledby="global-search-label"><div class="search-dialog-head"><label id="global-search-label" for="global-search-input">搜索全部笔记</label><form method="dialog"><button aria-label="关闭搜索">{icon('x')}</button></form></div><div class="global-search-field">{icon('search')}<input id="global-search-input" type="search" placeholder="输入标题、分类或关键词…" autocomplete="off"></div><p id="global-search-status" role="status">搜索算法、计算机基础与 AI 技术笔记。</p><div id="global-search-results"></div></dialog>'''

def footer(path):
    site = config()
    return f'<footer class="footer wrap site-footer"><span>© 2026 {esc(site["name"])}</span><span>{esc(site["footer"])}</span><a href="{esc(site["github"])}" target="_blank" rel="noopener noreferrer">GitHub {icon("arrow-up-right")}</a></footer>'

def render_page(title, description, path, body, active='notes', extra='', main_class=None):
    site = config()
    module = next(m for m in site['modules'] if m['id'] == active)
    styles = ['styles.css', 'assets/css/site.css', *module.get('styles', [])]
    styles = ''.join(f'<link rel="stylesheet" href="{relative(path, ROOT / s)}">' for s in styles)
    canonical = site['url'].rstrip('/') + '/' + quote(path.relative_to(ROOT).as_posix().removesuffix('index.html'), safe='/')
    main_class = main_class or module['main_class']
    main = BeautifulSoup(body, 'html.parser')
    for toc in main.select('.article-toc, .mobile-outline, .article-pagination'):
        toc.decompose()
    for h in main.select('h2, h3'):
        if not h.get('id'):
            # Navigation chrome only: article anchors remain unchanged.
            h['id'] = 'section-' + hashlib.sha256(h.get_text().encode()).hexdigest()[:12]
    page_outline, mobile_outline = outline(main, icon)
    crumb = main.select_one('.breadcrumb')
    if crumb:
        crumb.extract()
    for bar in main.select('.reader-bar, .article-end'):
        bar.decompose()
    reader_bar = f'<div class="reader-bar"><button class="sidebar-toggle" type="button" aria-expanded="true" aria-controls="docs-sidebar" hidden>{icon("menu")}<span>专题目录</span></button>{str(crumb) if crumb else ""}<button type="button" class="theme-toggle" aria-label="切换到深色模式" hidden>{icon("moon")}{icon("sun")}<span>深色模式</span></button></div>'
    intro = main.select_one('.article-header, .notes-hero, .module-intro')
    if intro and mobile_outline:
        intro.insert_after(BeautifulSoup(mobile_outline, 'html.parser'))
        mobile_outline = ''
    body = main.decode_contents()
    neighbor_links = pagination(path, icon)
    return f'''<!doctype html>
<html lang="zh-CN"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#fdfdfc">
<title>{esc(title)}</title><meta name="description" content="{esc(description)}">
<meta property="og:type" content="website"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{canonical}"><link rel="canonical" href="{canonical}">
<link rel="icon" type="image/svg+xml" href="{relative(path, ROOT / 'assets/favicon.svg')}">
<link rel="preload" href="{relative(path, ROOT / 'assets/fonts/inter/inter-latin-wght-normal.woff2')}" as="font" type="font/woff2" crossorigin>
{styles}<script>try{{const theme=localStorage.getItem('notes-theme')||'light';document.documentElement.dataset.theme=theme;document.documentElement.classList.toggle('dark',theme==='dark')}}catch(e){{}}</script><script defer src="{relative(path, ROOT / 'assets/js/navigation.js')}"></script><script defer src="{relative(path, ROOT / 'assets/js/reader.js')}"></script>{extra}
</head><body class="module-{esc(active)}">
<a class="skip-link" href="#main">跳到主要内容</a>
{header(path, active)}
<div class="docs-shell">{sidebar(path, icon)}<div class="docs-main"><main id="main" class="{esc(main_class)}" tabindex="-1">{reader_bar}{mobile_outline}{body}{neighbor_links}</main>{footer(path)}</div>{page_outline}</div>
<button class="sidebar-backdrop" aria-label="关闭专题目录" type="button" hidden></button>
{search_dialog()}
</body></html>
'''
