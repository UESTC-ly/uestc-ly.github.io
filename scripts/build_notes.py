#!/usr/bin/env python3
"""Import two local Markdown collections into the static personal site."""
from pathlib import Path
from collections import Counter, defaultdict
from urllib.parse import quote, unquote, urlsplit
import argparse, hashlib, html, json, re, shutil, os
import markdown, bleach
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
TOPICS = {
 'leetcode': ('力扣刷题','ALGORITHMS / 01','[ ]','记录解题思路、算法模板与复盘，让每一道题留下可以复用的方法。', ['数据结构','算法','解题复盘']),
 'computer-science': ('计算机基础','COMPUTER SCIENCE / 02','01','梳理系统如何运转，从底层原理到日常开发，建立知识之间的连接。',['操作系统','网络与数据库','后端工程']),
 'llm': ('大模型','LARGE LANGUAGE MODELS / 03','∑','理解模型背后的原理，整理训练、微调、推理与评测。',['模型原理','训练与微调','推理与评测']),
 'ai-agent': ('AI Agent 开发','AI AGENT DEVELOPMENT / 04','↳','围绕工具调用、工作流与检索增强，记录把模型能力变成可用工具的实践。',['工具调用','工作流','RAG']),
 'deep-learning': ('深度学习','DEEP LEARNING / 05','∇','整理机器学习、神经网络与视觉实践，从基础原理到动手实验。',['神经网络','模型训练','计算机视觉'])
}
def classify(key):
 if key.startswith('力扣刷题笔记/'): return 'leetcode'
 p=key.split('/')[1:]; full='/'.join(p)
 if p[0]=='RAG': return 'ai-agent'
 if p[0]=='LLM': return 'ai-agent' if p[1] in ('agent','MCP') else 'llm'
 if p[0]=='AI与算法知识库':
  if p[1]=='01-LLM基础与微调': return 'llm'
  if p[1]=='02-Agent-RAG-MCP': return 'ai-agent'
  if p[1]=='03-提示词工程与应用': return 'llm'
  if p[1]=='05-机器学习与算法': return 'computer-science' if '数据结构与算法' in p else ('llm' if '大模型算法岗' in full else 'deep-learning')
  if p[1]=='04-工程化与部署':
   return 'computer-science' if any(x in full for x in ('Docker','Git_')) else ('llm' if any(x in full for x in ('KV_Cache','finetuning','Rerank')) else 'ai-agent')
 if p[0]=='06-Python-AI应用开发':
  if p[1]=='01-机器学习与深度学习基础': return 'llm' if any(x in p[-1] for x in ('09-','10-','11-')) else 'deep-learning'
  return 'ai-agent'
 if p[0]=='02-语言' and p[1] in ('python-FastAPI','python_ai_agent'): return 'ai-agent'
 if p[0]=='04-计算机基础' and p[1] in ('数字图像处理','openCV'): return 'deep-learning'
 if p[0]=='补充' and p[1]=='MLOps与LLMOps': return 'ai-agent'
 return 'computer-science'

def normalize_mermaid(text):
 # Quote rectangle labels, including nested array brackets and math parentheses.
 if not re.match(r'^\s*(?:flowchart|graph)\s',text): return text
 result=[]; last=0; i=0
 while i<len(text):
  m=re.match(r'\b[A-Za-z_][A-Za-z0-9_]*\[',text[i:])
  if not m: i+=1; continue
  start=i+len(m.group(0))-1; depth=1; end=start+1
  while end<len(text) and depth:
   depth += (text[end]=='[')-(text[end]==']'); end+=1
  if depth: i=start+1;continue
  label=text[start+1:end-1]
  if label and label[0] not in '"([{':
   result.append(text[last:start]+'["'+label.replace('"','#quot;')+'"]');last=end
  i=end
 result.append(text[last:]);return ''.join(result)

def esc(s): return html.escape(str(s),quote=True)
def local_url(current,target): return quote(os.path.relpath(target,current.parent).replace(os.sep,'/'),safe='/')
def shell(title,desc,path,body,extra=''):
 home=local_url(path,ROOT/'index.html'); notes=local_url(path,ROOT/'notes/index.html'); css=local_url(path,ROOT/'styles.css'); ncss=local_url(path,ROOT/'notes/notes.css')
 url='https://uestc-ly.github.io/'+quote(str(path.relative_to(ROOT)).replace('index.html',''),safe='/')
 return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#f6f5f0"><title>{esc(title)} · 李杨的学习笔记</title><meta name="description" content="{esc(desc)}"><meta property="og:title" content="{esc(title)} · 李杨的学习笔记"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}"><link rel="canonical" href="{url}"><link rel="stylesheet" href="{css}"><link rel="stylesheet" href="{ncss}">{extra}</head><body><a class="skip-link" href="#main">跳到主要内容</a><header class="header wrap"><a class="brand" href="{home}" aria-label="李杨，返回首页"><span class="brand-mark">ly<span>.</span></span><span class="brand-name">李杨</span></a><nav aria-label="主导航"><a href="{home}#projects">项目</a><a href="{notes}">笔记</a><a href="{home}#about">关于</a><a class="nav-github" href="https://github.com/UESTC-ly" target="_blank" rel="noopener noreferrer">GitHub ↗</a></nav></header><main id="main" class="notes-page wrap" tabindex="-1">{body}</main><footer class="footer wrap"><span>© 2026 李杨</span><span>学习 · 记录 · 实践</span><a href="{home}">返回首页 ↗</a></footer></body></html>'''
def topicnav(path,current):
 return '<nav class="topic-nav" aria-label="笔记专题">'+''.join(f'<a href="{local_url(path,ROOT/"notes"/key/"index.html")}"'+(' aria-current="page"' if key==current else '')+f'>{value[0]}</a>' for key,value in TOPICS.items())+'</nav>'
def cards(path,counts):
 return '<div class="topic-grid">'+''.join(f'<a class="topic-card" href="{local_url(path,ROOT/"notes"/key/"index.html")}"><div class="topic-card-top"><span class="topic-symbol" aria-hidden="true">{v[2]}</span><span class="topic-code">{v[1]}</span></div><h3>{v[0]}</h3><p>{v[3]}</p><div class="topic-tags">'+''.join(f'<span>{s}</span>' for s in v[4])+f'</div><div class="topic-card-bottom"><span>{counts[key]} 篇笔记</span><span>进入专题 ↗</span></div></a>' for key,v in TOPICS.items())+'</div>'

def build(base):
 sources={}
 for folder in ('力扣刷题笔记','知识库'):
  for f in sorted((base/folder).rglob('*')):
   rel=f.relative_to(base/folder)
   if f.is_file() and not any(p.startswith('.') or p in ('__pycache__','node_modules') for p in rel.parts) and f.suffix in ('.md','.html','.png','.jpg','.jpeg','.svg','.webp','.gif','.py','.txt','.sh','.mmd'):
    sources[f.relative_to(base).as_posix()]=f
 posts={}; basenames=defaultdict(list); stems=defaultdict(list)
 for key,f in sources.items():
  basenames[f.name].append(key); stems[f.stem].append(key)
  if f.suffix!='.md': continue
  raw=f.read_text(); topic=classify(key); titlematch=re.search(r'^#\s+(.+)',raw,re.M)
  title=titlematch.group(1).strip() if titlematch else (f.parent.name+' · 学习索引' if f.stem in ('README','00-MOC') else f.stem)
  path=ROOT/'notes'/topic/('n-'+hashlib.sha256(key.encode()).hexdigest()[:12]+'.html')
  parts=key.split('/'); group='/'.join(parts[1:-1]) or '综合与索引'
  if key.startswith('知识库/'): group=' / '.join(parts[1:-1]) or '知识库'
  posts[key]={'title':title,'topic':topic,'path':path,'group':group,'raw':raw}
 sourcepath={k:ROOT/'notes/source'/k for k in sources}
 unresolved=[]
 def resolve(value,key):
  value=unquote(value).replace('\\|','|'); value=value.split('|')[0]
  target,sep,anchor=value.partition('#')
  if not target: return key,anchor
  f=sources[key]; candidates=[(f.parent/target).resolve(),(base/key.split('/')[0]/target).resolve(),(base/target).resolve()]
  if not Path(target).suffix: candidates += [Path(str(c)+'.md') for c in list(candidates)]
  keys={str(f.resolve()):k for k,f in sources.items()}
  for c in candidates:
   if str(c) in keys: return keys[str(c)],anchor
  matches=basenames.get(Path(target).name,[]) or stems.get(Path(target).stem,[])
  same=[k for k in matches if k.split('/')[0]==key.split('/')[0]]
  if same: matches=same
  if len(matches)==1: return matches[0],anchor
  suffix=[k for k in matches if k.endswith(target) or k.endswith(target+'.md')]
  if len(suffix)==1: return suffix[0],anchor
  # Old folder names in Obsidian links may omit a renamed parent folder.
  tails=[k for k in sources if k.endswith('/'+target.lstrip('/')) or k.endswith('/'+target.lstrip('/')+'.md')]
  if len(tails)==1: return tails[0],anchor
  for n in range(min(len(Path(target).parts),4),1,-1):
   tail='/'.join(Path(target).parts[-n:])
   tails=[k for k in sources if k.endswith('/'+tail) or k.endswith('/'+tail+'.md')]
   if len(tails)==1: return tails[0],anchor
  normalize=lambda text: re.sub(r'[\W_]+','',text).casefold()
  norm=normalize(Path(target).stem)
  matches=[k for k in sources if normalize(Path(k).stem)==norm and k.split('/')[0]==key.split('/')[0]]
  if len(matches)==1: return matches[0],anchor
  aliases={
   '操作系统面试50问':'04-计算机基础/操作系统/操作系统面试50问-整合版.md',
   '操作系统面试50问-深度追问':'04-计算机基础/操作系统/操作系统面试50问-整合版.md',
   '计算机网络/计算机网络知识清单.md':'04-计算机基础/计算机网络/00-MOC.md',
   '数据库/数据库知识清单.md':'04-计算机基础/数据库/数据库原理/README.md',
   '操作系统/操作系统知识清单.md':'04-计算机基础/操作系统/00-MOC.md',
   '05-传输层核心：TCP、UDP、拥塞控制、流量控制':'04-计算机基础/计算机网络/05-传输层：UDP、TCP、可靠传输与拥塞控制.md',
   '03-图算法与搜索方案':'补充/算法设计与复杂度/03-图算法与搜索策略.md',
   '03-编码规范与测试方案':'补充/软件工程/03-编码规范与测试策略.md',
   'RAG':'RAG/README.md','Transformer':'LLM/Transformer/Transformer架构详解.md',
   'agent':'LLM/agent/00-Agent学习路线与知识地图.md',
   './06-FunctionCalling与ToolCalling.md':'06-Python-AI应用开发/02-大模型API与Prompt/06-Function-Calling-Tool-Calling.md',
  }
  alias='知识库/'+aliases.get(target,'')
  if alias in sources: return alias,anchor
  return None,anchor
 def href(value,key):
  dest,anchor=resolve(value,key)
  if not dest: unresolved.append({'source':key,'target':value}); return None
  target=posts[dest]['path'] if dest in posts else sourcepath[dest]
  return local_url(posts[key]['path'],target)+(('#'+quote(anchor,safe='')) if anchor else '')
 soups={}
 for key,p in posts.items():
  raw=p['raw']
  if re.match(r'^---\n[^\n]+:',raw): raw=re.sub(r'^---\n.*?\n---\n','',raw,count=1,flags=re.S)
  def wiki(m):
   value=m.group(1).replace('\\|','|'); target,_,label=value.partition('|'); label=label or target.split('#')[0].split('/')[-1] or target
   url=href(target,key)
   return f'<a href="{esc(url)}">{esc(label)}</a>' if url else m.group(0)
  # Convert wiki links only outside fenced code; instructions in notes remain content.
  chunks=re.split(r'(^[ \t]*```[^\n]*\n.*?^[ \t]*```[ \t]*$|`[^`\n]+`)',raw,flags=re.M|re.S)
  raw=''.join(c if i%2 else re.sub(r'\[\[([^\]\n]+)\]\]',wiki,c) for i,c in enumerate(chunks))
  output=markdown.markdown(raw,extensions=['extra','toc','sane_lists','pymdownx.arithmatex'],extension_configs={'pymdownx.arithmatex':{'generic':True,'smart_dollar':True},'toc':{'permalink':False}})
  allowed=set(bleach.sanitizer.ALLOWED_TAGS)|{'p','div','span','h1','h2','h3','h4','h5','h6','pre','code','table','thead','tbody','tr','th','td','img','hr','br','details','summary','del','sup','sub','kbd','dl','dt','dd','input','blockquote'}
  output=bleach.clean(output,tags=allowed,attributes={'*':['id','class','title'],'a':['href','name'],'img':['src','alt','width','height'],'th':['align'],'td':['align'],'input':['type','checked','disabled']},strip=True)
  soup=BeautifulSoup(output,'html.parser')
  first=soup.find('h1')
  if first and first.get_text().strip()==p['title']: first.decompose()
  for h in soup.find_all(re.compile('^h[1-6]$')):
   label=h.get_text().strip(); original=h.get('id')
   if original and original!=label:
    alias=soup.new_tag('span',id=label);alias['class']='heading-anchor'; h.insert_before(alias)
  for a in soup.select('a[href]'):
   value=a['href']; parsed=urlsplit(value)
   if parsed.scheme in ('http','https','mailto','tel'): continue
   if parsed.scheme or value.startswith('/notes/'): continue
   # Wiki links above already point to generated HTML.
   if re.match(r'(?:\.\./)*(?:[^/]+/)*n-[a-f0-9]{12}\.html',value): continue
   if 'source/' in value: continue
   url=href(value,key)
   if url: a['href']=url
   else: a.unwrap()
  for image in soup.select('img[src]'):
   value=image['src']
   if not urlsplit(value).scheme:
    dest,_=resolve(value,key)
    if dest: image['src']=local_url(p['path'],sourcepath[dest])
    else: unresolved.append({'source':key,'target':value}); image.replace_with(image.get('alt','图片'))
   image['loading']='lazy';image['referrerpolicy']='no-referrer'
  for code in soup.select('pre > code.language-mermaid'):
   pre=code.parent;pre['class']='mermaid';pre.string=normalize_mermaid(code.get_text())
  for table in soup.find_all('table'):
   wrap=soup.new_tag('div');wrap['class']='table-scroll';table.wrap(wrap)
  soups[key]=soup
 # Repair fragments against actual generated headings, including Obsidian text headings.
 for key,soup in soups.items():
  for a in soup.select('a[href]'):
   value=unquote(a['href']); target,sep,anchor=value.partition('#')
   if not sep or urlsplit(value).scheme: continue
   path=(posts[key]['path'].parent/target).resolve() if target else posts[key]['path'].resolve()
   dest=next((k for k,v in posts.items() if v['path'].resolve()==path),None)
   if not dest: continue
   ds=soups[dest]; ids={tag.get('id') for tag in ds.select('[id]')}
   if anchor not in ids:
    normalize=lambda s: re.sub(r'[\W_]+','',s).casefold()
    match=next((h for h in ds.find_all(re.compile('^h[1-6]$')) if normalize(h.get_text())==normalize(anchor)),None)
    if match: a['href']=quote(target,safe='/')+'#'+quote(match['id'],safe='')
    else:
     # Preserve the original reference as a valid alias at the destination.
     span=ds.new_tag('span',id=anchor);span['class']='heading-anchor';ds.insert(0,span)
 counts=Counter(p['topic'] for p in posts.values())
 for k,f in sources.items():
  sourcepath[k].parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,sourcepath[k])
 for key,p in posts.items():
  soup=soups[key]; description=next((e.get_text(' ',strip=True) for e in soup.find_all('p') if len(e.get_text())>20),p['title'])[:160]
  p['description']=description
  toc=''.join(f'<li><a href="#{quote(h["id"],safe="")}">{esc(h.get_text())}</a></li>' for h in soup.select('h2[id], h3[id]'))
  toc=f'<details class="article-toc"><summary>本篇目录</summary><ul>{toc}</ul></details>' if toc else ''
  body=f'<nav class="breadcrumb" aria-label="当前位置"><a href="../../index.html">首页</a><span>/</span><a href="../index.html">专题笔记</a><span>/</span><a href="index.html">{TOPICS[p["topic"]][0]}</a></nav><header class="article-header"><p class="eyebrow">{esc(p["group"])}</p><h1>{esc(p["title"])}</h1><div class="article-actions"><a href="index.html">← 返回专题</a><a href="{local_url(p["path"],sourcepath[key])}" download>下载 Markdown ↓</a></div></header>{toc}<article class="note-content">{soup}</article><div class="article-end"><a class="button" href="index.html">返回{TOPICS[p["topic"]][0]} ↗</a></div>'
  extra='<script defer src="../vendor/katex/katex.min.js"></script><script defer src="../vendor/katex/contrib/auto-render.min.js"></script><link rel="stylesheet" href="../vendor/katex/katex.min.css">' if soup.select('.arithmatex') else ''
  if soup.select('pre.mermaid'): extra+='<script type="module" src="../render-diagrams.js"></script>'
  extra+='<script defer src="../article.js"></script>'
  p['path'].parent.mkdir(parents=True,exist_ok=True);p['path'].write_text(shell(p['title'],description,p['path'],body,extra))
 manifest=[]
 for topic,v in TOPICS.items():
  path=ROOT/'notes'/topic/'index.html'; groups=defaultdict(list)
  for key,p in posts.items():
   if p['topic']==topic: groups[p['group']].append((key,p))
  content=''
  for i,(group,entries) in enumerate(sorted(groups.items())):
   content+=f'<section class="note-group" data-group><h2>{esc(group)}<span class="group-count">{len(entries)} 篇</span></h2><div class="note-list">'
   for key,p in entries:
    content+=f'<article class="note-entry" data-search="{esc(p["title"]+" "+group)}"><h3><a href="{p["path"].name}">{esc(p["title"])}</a></h3><p>{esc(p["description"])}</p></article>'
    manifest.append({'source':key,'title':p['title'],'topic':topic,'group':group,'url':'/'+p['path'].relative_to(ROOT).as_posix()})
   content+='</div></section>'
  if topic=='leetcode':
   demos=[k for k in sources if k.startswith('力扣刷题笔记/') and k.endswith('.html')]
   content+='<section class="note-group"><h2>交互演示<span class="group-count">3 个</span></h2><div class="note-list">'+''.join(f'<article class="note-entry"><h3><a href="{local_url(path,sourcepath[k])}">{esc(Path(k).stem)}</a></h3><p>在交互页面中观察算法执行过程。</p></article>' for k in demos)+'</div></section>'
  body=f'<nav class="breadcrumb"><a href="../../index.html">首页</a><span>/</span><a href="../index.html">专题笔记</a><span>/</span><span>{v[0]}</span></nav><section class="notes-hero"><p class="eyebrow">{v[1]}</p><h1>{v[0]}<span class="topic-hero-symbol">{v[2]}</span></h1><p class="notes-description">{v[3]}</p><p class="notes-overview">{counts[topic]} 篇笔记 · {len(groups)} 个分类</p></section>'+topicnav(path,topic)+f'<section class="topic-posts"><div class="search-row"><label for="note-search">搜索本专题</label><input id="note-search" type="search" placeholder="搜索标题或分类…" autocomplete="off"><span id="search-count" role="status">{counts[topic]} 篇笔记</span></div><p id="no-results" hidden>没有找到匹配的笔记，试试其他关键词。</p>{content}</section>'
  path.write_text(shell(v[0],v[3],path,body,'<script defer src="../search.js"></script>'))
 path=ROOT/'notes/index.html'
 body='<nav class="breadcrumb"><a href="../index.html">首页</a><span>/</span><span>专题笔记</span></nav><section class="notes-hero"><p class="eyebrow">LEARNING NOTES</p><h1>学习，留下一点痕迹。</h1><p class="notes-description">从一道题、一个概念到一次开发实践。把零散的收获整理成笔记，也给未来的自己留一份索引。</p>'+f'<p class="notes-overview">5 个专题 / {len(posts)} 篇笔记</p></section>'+cards(path,counts)
 path.write_text(shell('专题笔记','力扣刷题、计算机基础、大模型、AI Agent 开发与深度学习。',path,body))
 homepage=ROOT/'index.html'; home=BeautifulSoup(homepage.read_text(),'html.parser')
 for old in home.select('#notes'): old.decompose()
 link=home.new_tag('link',rel='stylesheet',href='notes/notes.css');home.head.append(link)
 for old in home.select('link[href="notes/notes.css"]')[:-1]:old.decompose()
 if not home.select('.header nav a[href="#notes"]'):
  a=home.new_tag('a',href='#notes');a.string='笔记';home.select_one('.header nav a[href="#about"]').insert_before(a)
 section=BeautifulSoup('<section id="notes" class="notes-home wrap"><div class="section-heading"><div><p class="eyebrow">LEARNING NOTES / 02</p><h2>把学过的，写成自己的。</h2></div><a class="text-link" href="notes/index.html">全部专题 ↗</a></div>'+cards(homepage,counts)+'</section>','html.parser')
 home.select_one('#about').insert_before(section); homepage.write_text(str(home))
 (ROOT/'notes/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 (ROOT/'notes/import-report.json').write_text(json.dumps({'counts':dict(counts),'total':len(posts),'support_files':len(sources)-len(posts),'unavailable_source_references':list({(x['source'],x['target']):x for x in unresolved}.values())},ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'counts':dict(counts),'total':len(posts),'support_files':len(sources)-len(posts),'unresolved':len(unresolved)},ensure_ascii=False))
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('base',type=Path);args=parser.parse_args();build(args.base.resolve())
