# 李杨的个人主页

在线主页：https://uestc-ly.github.io/

静态作品集和专题笔记站点，GitHub Pages 从 `main` 分支根目录自动发布。

## 专题笔记

`notes/index.html` 为专题总览，按原目录分类并支持专题内标题搜索：

| 专题 | 篇数 | 内容 |
|---|---:|---|
| 力扣刷题 | 89 | 算法题解、模板、150 题索引和交互演示 |
| 计算机基础 | 271 | 语言、系统、网络、数据库、后端及工程化 |
| 大模型 | 33 | 模型原理、微调、推理和提示词 |
| AI Agent 开发 | 245 | RAG、MCP、Agent、工作流及 Python 应用开发 |
| 深度学习 | 38 | 机器学习、神经网络、PyTorch、图像处理及 OpenCV |

总计 676 篇。每篇提供网页正文、章节目录、返回专题及 Markdown 下载。Obsidian 双链及旧文件名引用转换为站内链接，原图片和 3 个算法交互 HTML 一并保留。公式与 Mermaid 使用本地依赖渲染，无需外部 CDN；原文语法异常的图保留文本。

`notes/source/` 保留笔记 Markdown 与配套文件，排除 `.git`、`.omx`、`.coscribe`、缓存、临时文件及会话记录。`notes/manifest.json` 记录原文件与网页对应关系；`notes/import-report.json` 记录分类数量及原目录中不存在的引用。文章正文来自用户提供的资料，原有出处、链接和声明保留。

## 重新导入

```sh
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
.venv/bin/python scripts/build_notes.py /path/to/knowledgeBase
```

输入目录应包含 `力扣刷题笔记/` 和 `知识库/`。生成脚本只读取输入目录，更新站点内的文章、目录、计数与首页入口。文章 URL 使用原路径的稳定哈希，重跑保持不变。新增笔记会自动归类；分类逻辑位于 `scripts/build_notes.py`。

## 页面文件

- `index.html`：个人主页和专题入口。
- `styles.css`：个人主页公共样式。
- `notes/notes.css`：专题与文章的桌面、手机样式。
- `notes/search.js`：标题与分类筛选。
- `notes/article.js`、`notes/render-diagrams.js`：公式与流程图渲染。
- `notes/vendor/`：KaTeX 0.16.22 与 Mermaid 11.12.0，附许可证。

本地预览：`python3 -m http.server 8765`，访问 `http://localhost:8765/`。字体使用 Google Fonts，网络不可用时回退系统字体。无追踪脚本及后台服务。
