# 术语表

本表是术语规范，不替代正文首现解释。`planned` 表示主解释章节尚未完成。

| 中文术语 | English / 缩写 | 简明定义 | 主解释路径 | 状态 | 避免混淆 |
|---|---|---|---|---|---|
| 检索增强生成 | Retrieval-Augmented Generation, RAG | 先从外部知识源检索相关内容，再把选定上下文交给生成模型回答的方法族 | docs/02-rag-principles/01-what-is-rag.md | planned | 能降低但不能消除幻觉 |
| 大语言模型 | Large Language Model, LLM | 使用大量文本训练、按上下文预测并生成序列的模型 | docs/01-foundations/01-ai-ml-dl-llm-transformer.md | planned | 不等同于知识库 |
| Token | Token | 模型处理文本时使用的离散单位 | docs/01-foundations/02-tokens-context-and-prompts.md | planned | 不必等于一个字或词 |
| 上下文窗口 | Context window | 一次请求中模型可处理的 Token 范围 | docs/01-foundations/02-tokens-context-and-prompts.md | planned | 长窗口不保证使用所有信息 |
| 提示词 | Prompt | 提供给模型的指令、问题和上下文组合 | docs/01-foundations/02-tokens-context-and-prompts.md | planned | 检索文本不能冒充系统指令 |
| 文档 | Document | 摄取管线中的原始或规范化内容及其元数据对象 | docs/03-data-ingestion/01-document-model-loaders-and-parsers.md | planned | 不等同于 Chunk |
| 文本块 | Chunk | 从文档切分出的可索引内容单元 | docs/04-chunking/01-fixed-sentence-and-paragraph-chunking.md | planned | 大小不是越小越好 |
| 元数据 | Metadata | 描述来源、页码、时间、权限、租户等属性的数据 | docs/03-data-ingestion/06-metadata-permissions-and-provenance.md | planned | 权限元数据必须参与授权 |
| 嵌入向量 | Embedding | 把输入映射到数值向量空间的表示 | docs/05-embeddings/01-embedding-and-vector-space-intuition.md | planned | 不同模型的向量不能直接混用 |
| 稀疏检索 | Sparse retrieval | 以词项或稀疏特征匹配为主的检索 | docs/07-retrieval/01-keyword-tfidf-bm25-and-sparse.md | planned | 中文分词会影响结果 |
| 稠密检索 | Dense retrieval | 使用稠密向量相似度寻找候选内容 | docs/07-retrieval/02-dense-and-hybrid-retrieval.md | planned | 不保证胜过关键词检索 |
| 混合检索 | Hybrid retrieval | 组合稀疏和稠密等多路候选的检索方式 | docs/07-retrieval/02-dense-and-hybrid-retrieval.md | planned | 需要明确融合与评估方式 |
| 索引 | Index | 为提高查找效率而构建的数据结构 | docs/06-indexes-vector-databases/01-flat-and-ann-indexes.md | planned | 向量数据库不是索引算法的同义词 |
| 近似最近邻 | Approximate Nearest Neighbor, ANN | 以部分准确率换取速度和规模的近邻搜索方法族 | docs/06-indexes-vector-databases/01-flat-and-ann-indexes.md | planned | 需要与 Flat 基线比较 |
| 重排 | Reranking | 对初始候选集合进行更精细相关性排序 | docs/08-reranking/01-why-and-when-to-rerank.md | planned | 不能补回未召回的内容 |
| 有依据生成 | Grounded generation | 要求答案受给定可核对证据约束的生成方式 | docs/09-context-generation/04-citations-grounding-and-source-trust.md | planned | 有引用不等于引用支持结论 |
| 拒答 | Refusal / abstention | 在证据不足或风险过高时不直接给出确定答案 | docs/09-context-generation/05-no-answer-refusal-and-structured-output.md | planned | 需要可评估阈值和错误成本 |
| 幻觉 | Hallucination | 模型生成缺少依据、与事实或给定证据不一致的内容 | docs/02-rag-principles/05-failure-modes-and-boundaries.md | planned | RAG 不能彻底消除 |
| 召回率 | Recall | 在相关项中成功找回的比例 | docs/12-evaluation/02-retrieval-metrics.md | planned | Recall@K 依赖 K 和相关性标签 |
| 精确率 | Precision | 在返回项中相关项所占比例 | docs/12-evaluation/02-retrieval-metrics.md | planned | 与生成正确性不同 |
| 租户 | Tenant | 在共享系统中需要数据和策略隔离的组织边界 | docs/14-security-governance/04-authorization-tenancy-and-permission-inheritance.md | planned | 过滤不能替代完整授权 |
| 个人可识别信息 | Personally Identifiable Information, PII | 可单独或组合识别个人的信息 | docs/14-security-governance/05-pii-moderation-residency-and-compliance.md | planned | 范围受司法辖区影响 |
