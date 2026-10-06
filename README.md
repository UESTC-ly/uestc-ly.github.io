# 李杨的个人主页

在线主页：https://uestc-ly.github.io/

采用文档式布局：固定顶栏与全站搜索、左侧专题目录、中央阅读区、右侧文章目录。首页仅介绍博客内容；项目、专题笔记、关于仍是独立模块。手机通过抽屉展开专题目录，文章目录显示在正文上方。

## 结构与职责

```text
config/
  site.json                站点信息、模块注册与菜单顺序
  topics.json              笔记专题信息、标签与可选导入规则
templates/pages/           首页、项目、关于的正文模板
scripts/
  site_layout.py           共用页面框架、导航、页脚与 URL
  docs_layout.py           根据笔记索引生成专题树、文章目录、上一篇与下一篇
  build_site.py            生成模块页面，刷新笔记公共框架
  build_notes.py           导入 Markdown、生成专题与文章
  check_site.py            检查导航、页面和站内链接
assets/
  fonts/                  Fontsource 本地 WOFF2 字体与许可证
  icons/lucide/            按需选取的 SVG 与许可证
  vendor/radix-colors/      Sand/Blue 浅色与深色色阶、许可证
  resources.json           上游版本、地址与校验记录
  css/site.css             全站导航、页脚和模块布局
  css/home.css             首页专用样式
  css/portfolio.css        项目与关于的展示组件
  js/navigation.js         手机菜单交互与键盘行为
  js/reader.js             全站搜索、目录抽屉、目录高亮、主题和阅读偏好
notes/                     生成的专题、文章、原文与渲染依赖
styles.css                 颜色、排版和基本组件
```

页面框架、内容模板和模块配置相互独立。模块 URL 为实际目录页面，无需客户端路由；刷新文章链接可以直接访问。导航与专题树在构建时写入 HTML，关闭 JavaScript 仍能浏览。目录与全站搜索共同读取 `notes/manifest.json`，新增笔记后无需手动添加导航。

全站搜索按需加载索引，支持标题与分类关键词、`/` 或 `Ctrl/Cmd+K` 快捷键、Escape 关闭。深色模式和桌面侧栏收起状态保存在本地浏览器；手机抽屉提供焦点约束、背景隔离和 Escape 关闭。原始 Markdown 下载、公式与流程图继续可用。

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

正文模板中可用 `{{url:notes}}` 引用注册模块，用 `{{asset:assets/example.png}}` 引用资源，用 `{{icon:book-open}}` 内联本地 Lucide 图标。构建器根据页面所在目录生成相对 URL，新增模块无需复制导航或页脚。`template: null` 表示由专用生成器管理的模块，例如笔记。

## 专题笔记

当前共 676 篇：力扣刷题 89、计算机基础 271、大模型 33、AI Agent 开发 245、深度学习 38。包含标题与分类搜索、章节目录、Markdown 下载及 3 个算法交互演示。

重新导入笔记：

```sh
.venv/bin/python scripts/build_notes.py /path/to/knowledgeBase
.venv/bin/python scripts/build_site.py
.venv/bin/python scripts/check_site.py
```

输入目录包含 `力扣刷题笔记/` 和 `知识库/`。导入器只读取原笔记，不修改首页模板；文章 URL 使用原路径的稳定哈希。专题标题、文案、标签与 `icon` 图标在 `config/topics.json` 管理。新增专题可提供 `source_prefixes` 数组指定来源前缀，规则优先于默认分类，例如 `"source_prefixes": ["知识库/新领域/"]`。

`notes/source/` 保留原文及配套文件，排除 Git 数据、会话、缓存与临时文件。`notes/manifest.json` 保存来源映射，`notes/import-report.json` 保存导入报告。公式与流程图使用本地 KaTeX 和 Mermaid 依赖，许可证位于 `notes/vendor/`。原有出处、图片链接与声明保留。字体加载失败时回退系统字体，无追踪脚本或后台服务。

## 视觉设计与资源

使用 UI UX Pro Max 的导航层级与阅读排版建议，搭配 Fontsource Inter / JetBrains Mono、Lucide SVG 与 Radix Sand / Blue 色阶。字体、图标和色阶随站点部署；中文优先系统字体。公共样式与模块样式分离，新模块复用文档框架、设计变量和图标接口。

完整规范见 [设计规范](design-system/MASTER.md)，资源版本和许可证见 [资源说明](assets/README.md)。
