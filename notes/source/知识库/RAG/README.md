# 从一个离线最小 RAG 开始

这是面向零基础读者的 RAG 教程仓库。仓库先用一个小而完整的离线试点展示主链路，
再用 00 至 08 的教学正文逐步展开准备度、基础知识、RAG 原理、数据摄取、文本切分、
嵌入向量、索引、检索与重排。离线试点不需要 API Key、网络或付费服务。

> 当前范围：00 至 08 已有教学草稿并处于 `reviewing`，不代表完成独立审查；09 之后的
> 生成、项目、评估、高级方法、安全、生产与综合实践仍按计划继续编写。本仓库不声称覆盖
> 所有 RAG 技术。

## 先选一条入口

| 你的目标 | 建议入口 |
|---|---|
| 完全从零开始 | [从 00 前言与准备度开始](docs/00-preface/README.md) |
| 先补 AI、API、Python 等最低基础 | [进入 01 基础知识](docs/01-foundations/README.md) |
| 先弄懂 RAG 为什么存在 | [阅读“什么是 RAG”](docs/02-rag-principles/01-what-is-rag.md) |
| 先看整条链路 | [查看 D01：RAG 端到端流程](assets/diagrams/rag-end-to-end.mmd) |
| 直接运行离线示例 | [进入 minimal-rag 项目](examples/minimal-rag/README.md) |
| 按教材顺序学习 | [进入教程文档索引](docs/README.md) |
| 检查边界与命令行路径 | [单元测试](tests/unit/test_minimal_rag.py)与[冒烟测试](tests/smoke/test_minimal_rag_cli.py) |

如果你第一次接触 RAG，推荐按“章节 → 示例 → 测试”的顺序前进。先形成直觉，
再观察语料、文本块、检索结果、上下文、回答和引用位置，最后用测试确认边界行为。

## 运行前准备

- Python 3.11 或更高版本。
- 不需要第三方模型、向量数据库、API Key 或网络连接。
- 教学运行依赖只使用 Python 标准库；测试使用仓库已经采用的 `pytest`。

在 macOS 或 Linux 的终端检查版本：

```bash
python3 --version
```

在 Windows PowerShell 检查版本：

```powershell
py -3.11 --version
```

具体启动命令、输入和预期输出由
[minimal-rag 项目 README](examples/minimal-rag/README.md)统一说明，避免根入口与可执行
项目维护两套可能漂移的命令。

## 这次试跑要观察什么

完成试跑后，你应该能在示例输出或代码中指出以下位置：

1. **语料（corpus）**：程序允许检索的本地知识集合。
2. **文本块（Chunk）**：从语料中切分出的检索单位。
3. **确定性嵌入与相似度**：把文本映射为可比较数值，并给候选排序。
4. **Top-K 检索**：只选择得分靠前的有限候选。
5. **上下文（context）**：交给回答步骤的检索结果，而且始终被当作不可信数据。
6. **提示词（Prompt）**：把回答规则、问题和上下文分区组合起来。
7. **回答与引用位置**：给出答案，同时标明它使用了哪些文本块。

这条链路能够让回答利用可更新、可检查的外部知识，但不能保证检索结果一定相关，
也不能消除幻觉。证据不足时，示例应该明确返回无答案，而不是编造确定结论。

## 学习路线

当前可达的最短路线是：

1. 按需要完成[00 前言与准备度](docs/00-preface/README.md)。
2. 补齐[01 基础知识](docs/01-foundations/README.md)。
3. 阅读[02 RAG 原理](docs/02-rag-principles/README.md)，理解两阶段、适用边界和失败模式。
4. 按[minimal-rag 运行说明](examples/minimal-rag/README.md)完成一次离线试跑。
5. 继续学习[03 数据摄取](docs/03-data-ingestion/README.md)、[04 文本切分](docs/04-chunking/README.md)和[05 嵌入向量](docs/05-embeddings/README.md)。
6. 学习[06 索引与向量数据库](docs/06-indexes-vector-databases/README.md)、[07 检索](docs/07-retrieval/README.md)和[08 重排](docs/08-reranking/README.md)。
7. 返回单元与冒烟测试，观察空语料、空查询、Top-K 越界、零向量或无答案路径。

03 至 08 当前以教材正文为主，章节中标记为 planned 的代码、图表、基准与厂商行为尚未
因此变成已验证交付。09 之后的生成、项目、评估、框架、高级方法、安全与生产章节仍在
后续批次中。离线试点负责提供第一条可运行、可解释、可核对的学习闭环。

## 验证状态怎么读

仓库不会把“写完”冒充“验证通过”：

- `static-checked`：完成静态规则和人工阅读检查，但不代表程序已经运行或图已经渲染。
- `unit-passed`：对应单元测试已真实运行并通过。
- `integration-passed`：对应集成或冒烟路径已真实运行并通过。
- `external-verified`：依赖外部服务的路径已真实验证；本离线试点不需要此状态。

D01 当前只声明 `static-checked`。环境中没有 Mermaid CLI（`mmdc`），所以它明确标注
“未渲染”，不会声称完成渲染或视觉审查。代码与测试状态以项目 README 和团队最终
集成证据为准。

## 已知边界

- 确定性嵌入和回答器用于教学，不等同于生产模型的语义能力。
- 少量内存语料不能代表大规模索引、权限隔离、延迟、成本与可用性问题。
- 有引用位置不等于引用内容必然支持结论；仍需要检查证据与答案是否一致。
- RAG 是一组可组合方法，本试点只展示最小主链路，不声称存在唯一最佳方案。
