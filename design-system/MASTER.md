# 李杨个人主页 · 设计规范

## 目标与边界

按用户提供的文档网站参考图组织页面：固定顶栏、左侧章节树、中央正文、右侧页内目录。站点以「技术博客」命名，内容包含技术文章、项目实践与专题整理。首页用一句话说明内容范围，提供专题阅读入口。首页不使用个人介绍、slogan 或个人关注领域。项目、专题笔记和关于分别在独立模块展示。全站使用实际目录 URL；新增模块通过 `config/site.json` 注册。文章正文和稳定链接不因布局调整改变。

## 设计依据

使用 [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) 检索设计建议。风格检索匹配 Minimalism & Swiss Style；针对可读性的字体检索匹配 Minimal Swiss（Inter）。采用简洁网格、充足留白、清晰层级、克制的状态变化。

本次 `navigation hierarchy` 检索匹配 Breadcrumbs、Heading Hierarchy 和 Sticky Navigation。保留位置导航、连续标题层级与顶栏下的锚点滚动间距。页面以内容为主，无滚动驱动动画。

## 字体

- 拉丁文字：Fontsource Inter Variable，100–900 字重。
- 代码与短英文元信息：Fontsource JetBrains Mono Variable，100–800 字重。
- 中文：优先 PingFang SC / Microsoft YaHei 等系统字体。只加载两份拉丁 WOFF2，共约 87 KiB；字体失败时系统回退。
- 正文 16px，摘要 14px，辅助文案 12px。长篇阅读区最大宽度 800px、行高 2；代码块保持内部滚动。
- `font-display: swap`；仅预加载 Inter，不访问外部字体服务。

## 颜色与组件

使用 [Radix Colors](https://www.radix-ui.com/colors) 的 Sand 和 Blue。浅色与深色色阶保存在 `assets/vendor/radix-colors/`，`styles.css` 将它们映射成语义变量。既有 Teal 资源保留，阅读界面使用 Blue：

| 语义变量 | 基础色阶 | 用途 |
| --- | --- | --- |
| `--bg` | 白色 / 深色 sand-1 | 全站背景 |
| `--ink` | sand-12 | 标题、正文 |
| `--muted` | sand-11 | 摘要与辅助文字 |
| `--line` | sand-6 | 内容分隔 |
| `--line-strong` | sand-8 | 输入框与菜单按钮边界 |
| `--green` | blue-11 | 内容链接（保留原变量接口） |
| `--accent` | blue-11 | 强调、焦点、图标 |
| `--mint` | blue-3 | 当前菜单、图标底色 |
| `--selected-ink` | blue-12 | 选中项与浅蓝底色保持文字对比 |
| `--button-bg` | 浅色 blue-11 / 深色 blue-5 | 实心按钮，与白色文字保持对比 |

间距按 8/16/24/32/48/64px 组织。顶栏 64px；左栏 280px、右栏 224px，中央容器最大 920px（含两侧各 48px 留白）。小于 1200px 将页内目录移入正文；不超过 960px 用专题抽屉；手机正文边距 24px（窄屏 20px）。组件圆角 6px，卡片 12px。正文保持自然滚动，左栏和右栏分别滚动。

## 图标与扩展

[Lucide](https://lucide.dev/) 统一使用线框 SVG，24×24 viewBox、1.75px 显示描边。图标按需下载到 `assets/icons/lucide/`，构建时内联，无图标运行库或 API 请求。

- 模板用 `{{icon:book-open}}` 等占位符引用。
- 专题在 `config/topics.json` 的 `icon` 字段指定；省略时默认 `book-open`。
- 新增图标需保存官方 SVG 与许可证，并更新 `assets/resources.json`。
- 图标为文字的补充，使用 `aria-hidden="true"`、`focusable="false"`；按钮与链接保留明确文字。

## 交互与验收

手机菜单和专题抽屉提供展开状态、Escape 关闭及焦点返回；抽屉打开时隔离背景并约束焦点。无 JavaScript 时完整导航和章节链接仍可访问。手机操作至少 44px 高，搜索输入使用 16px 字号。搜索对话框按需加载笔记索引，搜索结果使用安全文本节点。保留跳转正文入口和键盘焦点指示；减少动态效果时关闭过渡与平滑滚动。深色模式保留流程图的浅色画布，以保持原图文字可读。

每次视觉改动检查 320/375/768/1024/1440px，确保正文和页面无横向溢出。表格、公式与代码在内容区内部滚动。验证菜单、搜索、公式与 Mermaid，运行 `scripts/check_site.py`；文章内容改动需与视觉改动区分。

## 来源与许可

资源版本、下载地址和上游包校验记录在 `assets/resources.json`。字体 OFL、Lucide ISC、Radix MIT 许可分别与资源存放。更换资源时保留相应声明。
