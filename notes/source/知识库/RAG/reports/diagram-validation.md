# 图表验证报告

状态：`D01-static-checked-unrendered-review-pending`。

已创建 `assets/diagrams/rag-end-to-end.mmd`。静态与人工阅读检查确认：

- 使用 `flowchart LR` 和约定安全子集；
- 注释中有 D01、标题、教学问题、阅读顺序和验证状态；
- 节点覆盖 Corpus、Chunk、Embedding、相似度、Top-K、Context、Prompt、回答与引用；
- 空语料、空查询、零向量和 Top-K 越界路径可见；
- 与 02-01 和 minimal-rag 的术语方向一致。

当前环境没有 `mmdc`，因此没有真实 Mermaid 解析、渲染或视觉审查证据。D01 只能保持
`static-checked`，D02-D20 仍为 planned。
