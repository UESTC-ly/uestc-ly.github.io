# UI 资源

字体来自 Fontsource；图标来自 Lucide；颜色来自 Radix Colors。只保存本网站使用的资源，访客加载时无需连接外部字体、图标 API 或 CDN。

`resources.json` 记录上游 npm 包的固定版本、原始下载地址、SHA-1 及选用文件。字体与图标按原始内容保存；构建器为内联 SVG 加入装饰性语义属性并整理空白，显示尺寸和描边由 CSS 控制。许可证随资源保留。

全站视觉约定见 `design-system/MASTER.md`。模板使用 `{{icon:名称}}`；专题图标配置在 `config/topics.json`。中文优先使用系统字体，Inter 与 JetBrains Mono 仅提供拉丁文字。
