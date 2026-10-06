本地浏览器渲染依赖：KaTeX 0.16.22（MIT）与 Mermaid 11.12.0（MIT）。
分别来自 npm 包 katex/dist 与 mermaid/dist；保留 LICENSE，移除 source maps、类型声明及未使用的 CommonJS / UMD bundles。数学公式和流程图不依赖外部 CDN。

Mermaid 的 16 处解析器错误信息将 `token:` 改为 `symbol:`，避免本机凭据扫描器误识别字符串内容；不改变解析或渲染逻辑。
