# 李杨的个人主页

在线主页：https://uestc-ly.github.io/

极简首页通过统一菜单连接独立模块：项目、专题笔记、关于。桌面显示横向菜单，手机显示可展开菜单。笔记和项目的详细内容位于各自页面。

## 结构与职责

```text
config/
  site.json                站点信息、模块注册与菜单顺序
  topics.json              笔记专题信息、标签与可选导入规则
templates/pages/           首页、项目、关于的正文模板
scripts/
  site_layout.py           共用页面框架、导航、页脚与 URL
  build_site.py            生成模块页面，刷新笔记公共框架
  build_notes.py           导入 Markdown、生成专题与文章
  check_site.py            检查导航、页面和站内链接
assets/
  css/site.css             全站导航、页脚和模块布局
  css/home.css             首页专用样式
  css/portfolio.css        项目与关于的展示组件
  js/navigation.js         手机菜单交互与键盘行为
notes/                     生成的专题、文章、原文与渲染依赖
styles.css                 颜色、排版和基本组件
```

页面框架、内容模板和模块配置相互独立。模块 URL 为实际目录页面，无需客户端路由；刷新文章链接可以直接访问。导航在构建时写入 HTML，关闭 JavaScript 仍能使用；JavaScript 仅增强手机菜单、搜索和图表。

## 构建与验证

```sh
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
.venv/bin/python scripts/build_site.py
.venv/bin/python scripts/check_site.py
python3 -m http.server 8765
```

GitHub Pages 从 `main` 分支根目录发布生成后的静态 HTML，不要求部署服务器安装 Python。修改配置或模板后，运行构建及验证，并同时提交生成页面。

## 新增模块

1. 在 `templates/pages/` 添加正文模板，如 `reading.html`。
2. 在 `config/site.json` 的 `modules` 中添加注册信息：

```json
{
  "id": "reading",
  "label": "阅读",
  "path": "reading/",
  "title": "阅读 · 李杨",
  "description": "阅读记录与书单。",
  "template": "reading.html",
  "main_class": "module-page wrap",
  "styles": []
}
```

3. 运行 `build_site.py`。新模块页面和所有页面的导航自动生成，手机菜单同时更新。

正文模板中可用 `{{url:notes}}` 引用注册模块，用 `{{asset:assets/example.png}}` 引用资源。构建器根据页面所在目录生成相对 URL，新增模块无需复制导航或页脚。`template: null` 表示由专用生成器管理的模块，例如笔记。

## 专题笔记

当前共 676 篇：力扣刷题 89、计算机基础 271、大模型 33、AI Agent 开发 245、深度学习 38。包含标题与分类搜索、章节目录、Markdown 下载及 3 个算法交互演示。

重新导入笔记：

```sh
.venv/bin/python scripts/build_notes.py /path/to/knowledgeBase
.venv/bin/python scripts/build_site.py
.venv/bin/python scripts/check_site.py
```

输入目录包含 `力扣刷题笔记/` 和 `知识库/`。导入器只读取原笔记，不修改首页模板；文章 URL 使用原路径的稳定哈希。专题标题、文案与标签在 `config/topics.json` 管理。新增专题可提供 `source_prefixes` 数组指定来源前缀，规则优先于默认分类，例如 `"source_prefixes": ["知识库/新领域/"]`。

`notes/source/` 保留原文及配套文件，排除 Git 数据、会话、缓存与临时文件。`notes/manifest.json` 保存来源映射，`notes/import-report.json` 保存导入报告。公式与流程图使用本地 KaTeX 和 Mermaid 依赖，许可证位于 `notes/vendor/`。原有出处、图片链接与声明保留。字体加载失败时回退系统字体，无追踪脚本或后台服务。
