"""Shared static page shell and module registry. No client-side routing required."""
from pathlib import Path
from urllib.parse import quote
import html
import json
import os

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

def relative(path, target):
    return quote(os.path.relpath(target, path.parent).replace(os.sep, '/'), safe='/')

def module_url(path, module_id):
    module = next(m for m in config()['modules'] if m['id'] == module_id)
    return relative(path, ROOT / module['path'] / 'index.html')

def header(path, active):
    site = config()
    links = []
    for module in site['modules']:
        current = ' aria-current="page"' if module['id'] == active else ''
        href = relative(path, ROOT / module['path'] / 'index.html')
        links.append(f'<a href="{href}"{current}>{esc(module["label"])}</a>')
    links.append(f'<a class="nav-github" href="{esc(site["github"])}" target="_blank" rel="noopener noreferrer">GitHub <span aria-hidden="true">↗</span></a>')
    return f'''<div class="site-header-bar"><header class="header wrap site-header">
  <a class="brand" href="{module_url(path, 'home')}" aria-label="{esc(site['name'])}，返回首页"><span class="brand-mark">ly<span>.</span></span><span class="brand-name">{esc(site['name'])}</span></a>
  <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-navigation" hidden><span>菜单</span><span class="menu-icon" aria-hidden="true"></span></button>
  <nav id="site-navigation" aria-label="主导航">{''.join(links)}</nav>
</header></div>'''

def footer(path):
    site = config()
    return f'<footer class="footer wrap site-footer"><span>© 2026 {esc(site["name"])}</span><span>{esc(site["footer"])}</span><a href="{esc(site["github"])}" target="_blank" rel="noopener noreferrer">GitHub ↗</a></footer>'

def render_page(title, description, path, body, active='notes', extra='', main_class=None):
    site = config()
    module = next(m for m in site['modules'] if m['id'] == active)
    styles = ['styles.css', *module.get('styles', []), 'assets/css/site.css']
    styles = ''.join(f'<link rel="stylesheet" href="{relative(path, ROOT / s)}">' for s in styles)
    canonical = site['url'].rstrip('/') + '/' + quote(path.relative_to(ROOT).as_posix().removesuffix('index.html'), safe='/')
    main_class = main_class or module['main_class']
    return f'''<!doctype html>
<html lang="zh-CN"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#f6f5f0">
<title>{esc(title)}</title><meta name="description" content="{esc(description)}">
<meta property="og:type" content="website"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{canonical}"><link rel="canonical" href="{canonical}">
<link rel="icon" type="image/svg+xml" href="{relative(path, ROOT / 'assets/favicon.svg')}">
{styles}<script defer src="{relative(path, ROOT / 'assets/js/navigation.js')}"></script>{extra}
</head><body class="module-{esc(active)}">
<a class="skip-link" href="#main">跳到主要内容</a>
{header(path, active)}
<main id="main" class="{esc(main_class)}" tabindex="-1">{body}</main>
{footer(path)}
</body></html>
'''
