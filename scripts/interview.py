"""Topic-specific reading routes, chapter catalog and lazy question search index."""
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit
import html
import json
import re
import posixpath
import markdown
from bs4 import BeautifulSoup

from docs_layout import group_id
from site_layout import icon

ROOT = Path(__file__).resolve().parents[1]
PREFIX = '知识库/八股题库搜集/'


def render_markdown(raw):
    """Isolate collected excerpts so malformed upstream HTML cannot swallow later questions."""
    # GitHub accepts labels such as "jsx harmony"; Python Markdown expects
    # one language token, otherwise JSX could escape from its code fence.
    raw = re.sub(r'^([ \t]*```)([^\s`]+)[ \t]+[^\n]*$', r'\1\2', raw, flags=re.M)
    parser = markdown.Markdown(extensions=['extra', 'toc', 'sane_lists', 'pymdownx.arithmatex'], extension_configs={'pymdownx.arithmatex': {'generic': True, 'smart_dollar': True}, 'toc': {'permalink': False}})
    used = set()
    output = []
    for section in re.split(r'(?m)(?=^<a id="[km][0-9a-f]+"></a>[ \t]*$)', raw):
        piece = BeautifulSoup(parser.convert(section), 'html.parser')
        parser.reset()
        for tag in piece.select('[id]'):
            original = candidate = tag['id']
            suffix = 1
            while candidate in used:
                candidate = f'{original}_{suffix}'
                suffix += 1
            tag['id'] = candidate
            used.add(candidate)
        output.append(str(piece))
    return '\n'.join(output)


def esc(value):
    return html.escape(str(value), quote=True)


def prepare_entry(key, post):
    relative = Path(key.removeprefix(PREFIX))
    post['group'] = relative.parts[0] if len(relative.parts) > 1 else '阅读指南'
    if relative.as_posix() == 'README.md':
        post['title'] = '计算机八股大全 · 阅读指南'


def entry_order(entry):
    source = Path(entry['source'])
    foundation = source.stem == re.sub(r'^\d+-', '', source.parent.name)
    return (not foundation, source.name)


def upstream_reference(element, value, image=False):
    """Recover excerpt-relative assets from the section's pinned source citation."""
    heading = element.find_previous('h2')
    if not heading or '{' in value or '}' in value:
        return None
    for node in heading.next_elements:
        if node is not heading and getattr(node, 'name', None) == 'h2':
            break
        if getattr(node, 'name', None) != 'a' or '来源许可' not in node.parent.get_text():
            continue
        source = urlsplit(node.get('href', ''))
        match = re.fullmatch(r'/([^/]+)/([^/]+)/blob/([^/]+)/(.+)', unquote(source.path))
        if source.netloc != 'github.com' or not match:
            continue
        owner, repo, revision, original = match.groups()
        target = urlsplit(unquote(value).replace('\\', '/'))
        resolved = posixpath.normpath(target.path.lstrip('/') if target.path.startswith('/') else posixpath.join(posixpath.dirname(original), target.path))
        # Datawhale serves /images from VitePress's public directory.
        if image and owner.lower() == 'datawhalechina' and repo == 'daily-interview' and target.path.lstrip('/').startswith('images/'):
            resolved = 'docs/public/' + target.path.lstrip('/')
        if resolved.startswith('../'):
            return None
        if image:
            return f'https://raw.githubusercontent.com/{owner}/{repo}/{revision}/' + quote(resolved, safe='/')
        return f'https://github.com/{owner}/{repo}/blob/{revision}/' + quote(resolved, safe='/') + (('#' + quote(target.fragment)) if target.fragment else '')
    return None


def build_interview(posts, soups, shell, topicnav):
    topic = 'interview'
    path = ROOT / 'notes' / topic / 'index.html'
    path.parent.mkdir(parents=True, exist_ok=True)
    members = [(key, post) for key, post in posts.items() if post['topic'] == topic]
    groups = defaultdict(list)
    guide = None
    for key, post in members:
        if post['group'] == '阅读指南':
            guide = post
        else:
            groups[post['group']].append((key, post))
    groups = dict(sorted(groups.items()))
    for entries in groups.values():
        entries.sort(key=lambda pair: entry_order({'source': pair[0]}))

    chapters, questions = [], []
    question_counts = {}
    for group, entries in groups.items():
        for key, post in entries:
            chapter_index = len(chapters)
            chapters.append([post['path'].name, post['title'], group])
            headings = soups[key].select('h2[id]')
            question_counts[key] = len(headings)
            for heading in headings:
                fragments = []
                length = 0
                for sibling in heading.next_siblings:
                    if getattr(sibling, 'name', None) in ('h1', 'h2'):
                        break
                    text = sibling.get_text(' ', strip=True) if hasattr(sibling, 'get_text') else str(sibling).strip()
                    if text:
                        fragments.append(text)
                        length += len(text)
                    if length >= 160:
                        break
                excerpt = re.sub(r'\s+', ' ', ' '.join(fragments))[:160]
                questions.append([chapter_index, heading['id'], heading.get_text(' ', strip=True), excerpt])
    (path.parent / 'questions.json').write_text(json.dumps({'chapters': chapters, 'questions': questions}, ensure_ascii=False, separators=(',', ':')) + '\n')

    def foundation(number):
        group = next(g for g in groups if g.startswith(f'{number:02d}-'))
        return groups[group][0][1]

    routes = [
        ('01', '公共基础', '先建立通用知识框架。', [21, 2, 1]),
        ('02', '后端开发', '选择目标语言，再读存储与系统设计。', [3, 4, 5, 6, 7]),
        ('03', 'AI 与大模型', '从模型基础走向训练、推理与应用。', [8, 9, 10]),
        ('04', '岗位补充', '按岗位补充专项，再准备项目表达。', [15, 14, 18, 22]),
    ]
    route_html = ''
    for number, title, description, numbers in routes:
        links = ''.join(f'<a href="{foundation(n)["path"].name}">{esc(foundation(n)["title"])}{icon("arrow-right")}</a>' for n in numbers)
        route_html += f'<div class="interview-route"><span class="route-number">{number}</span><h3>{title}</h3><p>{description}</p><div>{links}</div></div>'

    categories, sections, options = '', '', ''
    for group, entries in groups.items():
        number, label = group.split('-', 1)
        target = group_id(group)
        options += f'<option value="{esc(group)}">{esc(label)}</option>'
        categories += f'<a class="interview-category" href="#{target}"><span class="category-number">{number}</span><span><strong>{esc(label)}</strong><small>{len(entries)} 篇笔记</small></span>{icon("arrow-right")}</a>'
        rows = ''
        for key, post in entries:
            basic = entry_order({'source': key})[0] is False
            badge = '<span class="foundation-badge">基础先读</span>' if basic else ''
            rows += f'<article class="interview-chapter"><h3><a href="{post["path"].name}"><span>{esc(post["title"])}</span>{badge}</a></h3><span class="chapter-questions">{question_counts[key]} 条</span></article>'
        sections += f'<section class="note-group interview-group" id="{target}" data-group><h2>{esc(group)}<span class="group-count">{len(entries)} 篇</span></h2><div>{rows}</div></section>'

    guide_link = f'<a href="{guide["path"].name}">阅读指南{icon("arrow-up-right")}</a>' if guide else ''
    body = f'''<nav class="breadcrumb" aria-label="当前位置"><a href="../../index.html">首页</a><span>/</span><a href="../index.html">专题笔记</a><span>/</span><span>计算机八股大全</span></nav>
<section class="notes-hero interview-hero"><p class="eyebrow">INTERVIEW HANDBOOK / 06</p><h1>计算机八股大全</h1><p class="notes-description">从计算机基础到工程实践与 AI，按知识主题整理面试笔记。先读各方向的基础笔记，再查阅专题问答，把零散问题串成知识体系。</p><div class="interview-stats"><span><strong>{len(groups)}</strong> 个方向</span><span><strong>{len(members)}</strong> 篇笔记</span><span><strong>{len(questions):,}</strong> 个知识条目</span></div><div class="interview-quicklinks">{guide_link}<a href="#category-directory">浏览分类{icon("arrow-right")}</a></div></section>
<section class="interview-search" id="question-search" data-question-index="questions.json" aria-labelledby="question-search-title"><h2 id="question-search-title">查一道题</h2><p class="interview-hint" id="question-search-hint">搜索题目、分类与回答摘要，点击结果直接跳到知识点。支持多个关键词。</p><div class="question-search-controls"><div class="question-input"><label for="question-query">关键词</label><div class="search-field">{icon("search")}<input id="question-query" type="search" placeholder="例如：TCP 握手、虚拟内存、LoRA…" aria-describedby="question-search-hint" autocomplete="off"></div></div><div class="question-category"><label for="question-category">知识方向</label><select id="question-category"><option value="">全部方向</option>{options}</select></div><button id="question-clear" type="button" hidden>清空</button></div><p id="question-status" role="status" aria-live="polite">输入关键词开始检索，也可以直接浏览下方分类。</p><div id="question-results"></div><button id="question-more" type="button" hidden>再显示 20 条</button><noscript><p>题目搜索需要启用 JavaScript；下方分类、文章与本页目录可直接阅读。</p></noscript></section>
<section class="interview-routes" aria-labelledby="reading-routes"><h2 id="reading-routes">按方向开始阅读</h2><div class="interview-route-grid">{route_html}</div></section>
<section class="interview-directory" aria-labelledby="category-directory"><h2 id="category-directory">24 个知识方向</h2><p class="interview-hint">选择分类跳转到章节列表；标有“基础先读”的笔记适合作为起点。</p><nav class="interview-category-grid" aria-label="知识方向索引">{categories}</nav></section>
<section class="interview-chapters" aria-label="全部笔记章节">{sections}</section>
<section class="interview-sources" id="{group_id('阅读指南')}"><h2 id="sources-and-reading">阅读与来源</h2><p>笔记保留原有参考资料、来源链接和许可说明，便于回到原文继续阅读。各来源的许可说明随相应内容保留；页面为整理发布版。代码、公式与图表可在文章内阅读，每篇文章均可下载原始 Markdown。</p>{guide_link}</section>'''
    extra = '<link rel="stylesheet" href="interview.css"><script defer src="interview-search.js"></script>'
    path.write_text(shell('计算机八股大全', '24 个方向的计算机面试笔记，含基础阅读路线、分类索引与题目搜索。', path, body, extra))
    print(f'Interview index: {len(groups)} categories, {len(members)} notes, {len(questions)} knowledge entries.')
