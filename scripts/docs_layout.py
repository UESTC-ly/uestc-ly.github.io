"""Build the document navigation from the same registry as the note index."""
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote
import hashlib
import html
import json
import os
import re

ROOT = Path(__file__).resolve().parents[1]

def esc(value):
    return html.escape(str(value), quote=True)

def href(path, target):
    return quote(os.path.relpath(target, path.parent).replace(os.sep, '/'), safe='/')

@lru_cache(maxsize=1)
def catalog():
    topics = json.loads((ROOT / 'config/topics.json').read_text())
    manifest = ROOT / 'notes/manifest.json'
    posts = json.loads(manifest.read_text()) if manifest.exists() else []
    return topics, posts

def group_id(group):
    return 'group-' + hashlib.sha256(group.encode()).hexdigest()[:12]

def group_label(group):
    parts = group.replace(' / ', '/').split('/')
    return ' / '.join(re.sub(r'^\d+[-_]', '', p) for p in parts[-2:])

def sidebar(path, icon):
    topics, posts = catalog()
    current_url = '/' + path.relative_to(ROOT).as_posix()
    current = next((p for p in posts if p['url'] == current_url), None)
    topic_id = current['topic'] if current else (path.parent.name if path.parent.name in {t['id'] for t in topics} else None)
    title = next((t['name'] for t in topics if t['id'] == topic_id), '全部专题')
    switches = ''.join(
        f'<a href="{href(path, ROOT / "notes" / t["id"] / "index.html")}"'
        + (' aria-current="true"' if t['id'] == topic_id else '')
        + f'>{icon(t.get("icon", "book-open"))}<span>{esc(t["name"])}</span></a>' for t in topics)
    top = f'''<div class="sidebar-heading"><a href="{href(path, ROOT / 'notes/index.html')}">{icon('book-open')} 专题目录</a><button class="sidebar-close" type="button" aria-label="关闭专题目录" hidden>{icon('x')}</button></div>
<details class="topic-switcher"><summary>{esc(title)}<span aria-hidden="true">⌄</span></summary><nav aria-label="切换专题">{switches}</nav></details>'''
    if topic_id:
        entries = [p for p in posts if p['topic'] == topic_id]
        groups = defaultdict(list)
        for p in entries:
            groups[p['group']].append(p)
        content = f'<a class="sidebar-overview" href="{href(path, ROOT / "notes" / topic_id / "index.html")}">专题概览<span>{len(entries)} 篇</span></a>'
        for i, (group, members) in enumerate(groups.items(), 1):
            opened = current and current['group'] == group or not current and i == 1
            content += f'<details class="sidebar-group"{ " open" if opened else ""}><summary><span class="chapter-number">{i:02d}</span><span>{esc(group_label(group))}</span></summary><div class="sidebar-entries">'
            for p in members:
                selected = p['url'] == current_url
                content += f'<a href="{href(path, ROOT / p["url"].lstrip("/"))}"' + (' aria-current="page"' if selected else '') + f'>{esc(p["title"])}</a>'
            content += '</div></details>'
    else:
        content = f'<a class="sidebar-overview" href="{href(path, ROOT / "index.html")}">博客介绍</a>'
        for i, t in enumerate(topics, 1):
            members = [p for p in posts if p['topic'] == t['id']]
            groups = list(dict.fromkeys(p['group'] for p in members))
            target = ROOT / 'notes' / t['id'] / 'index.html'
            content += f'<details class="sidebar-group sidebar-topic"><summary><span class="chapter-number">{i:02d}</span><span>{esc(t["name"])}</span><span class="sidebar-count">{len(members)}</span></summary><div class="sidebar-entries"><a class="sidebar-topic-link" href="{href(path, target)}">{esc(t["name"])} · 专题概览</a>'
            for group in groups:
                content += f'<a href="{href(path, target)}#{group_id(group)}">{esc(group_label(group))}</a>'
            content += '</div></details>'
    return f'<aside class="docs-sidebar" id="docs-sidebar" aria-label="专题目录">{top}<nav class="sidebar-tree" aria-label="笔记章节">{content}</nav></aside>'

def outline(main, icon):
    headings = main.select('h2[id], h3[id]')
    links = ''.join(f'<li class="outline-level-{h.name[1]}"><a href="#{quote(h["id"], safe="")}">{esc(h.get_text(" ", strip=True))}</a></li>' for h in headings)
    empty = '博客介绍' if main.select_one('.home-intro') else '暂无小节目录'
    contents = f'<ul>{links}</ul>' if links else f'<p class="outline-empty">{empty}</p>'
    nav = f'<nav class="outline-nav" aria-label="本页目录"><p class="outline-title">本页目录</p>{contents}</nav>'
    tools = f'''<div class="reader-tools"><button type="button" class="theme-toggle" aria-label="切换到深色模式" hidden>{icon('moon')}{icon('sun')}<span>深色模式</span></button><a href="#main" class="back-to-top">{icon('arrow-up-right')}<span>返回顶部</span></a></div>'''
    mobile = f'<details class="mobile-outline"><summary>本页目录</summary><nav aria-label="本页目录（移动端）">{contents}</nav></details>' if links else ''
    return f'<aside class="docs-outline" aria-label="阅读辅助">{nav}{tools}</aside>', mobile

def pagination(path, icon):
    _, posts = catalog()
    current_url = '/' + path.relative_to(ROOT).as_posix()
    current = next((p for p in posts if p['url'] == current_url), None)
    if not current:
        return ''
    entries = [p for p in posts if p['topic'] == current['topic']]
    index = entries.index(current)
    links = []
    for offset, label in [(-1, '上一篇'), (1, '下一篇')]:
        if 0 <= index + offset < len(entries):
            p = entries[index + offset]
            links.append(f'<a class="page-{"previous" if offset < 0 else "next"}" href="{href(path, ROOT / p["url"].lstrip("/"))}"><span>{label} {icon("arrow-right")}</span><strong>{esc(p["title"])}</strong></a>')
    return '<nav class="article-pagination" aria-label="相邻笔记">' + ''.join(links) + '</nav>'
