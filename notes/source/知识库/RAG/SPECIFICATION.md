# RAG 零基础系统教程生成任务

## 1. 项目目标

创建一套面向零基础学习者的、系统化的 RAG 教程。

教程必须从基础概念逐步推进到完整工程实践，覆盖 RAG 的核心原理、关键技术、代码实现、评估方法、高级架构、安全治理和生产部署。

最终交付物应当是一个结构完整的 Markdown 教程仓库，而不是一篇单独的长文章。

读者完成教程后，应能够：

1. 理解 RAG 的基本原理和完整工作流程。
2. 理解文档处理、切分、Embedding、索引、检索、重排和生成。
3. 独立实现一个基础 RAG 系统。
4. 使用主流框架开发较完整的 RAG 应用。
5. 建立测试集并评估 RAG 系统。
6. 诊断召回率低、答案错误、引用不一致、幻觉、延迟和成本等问题。
7. 理解 Advanced RAG、Agentic RAG、Graph RAG 和多模态 RAG。
8. 将 RAG 系统部署到接近生产环境的架构中。
9. 根据业务约束完成技术选型和架构设计。

---

## 2. 角色定义

你是本项目的：

* 总编排 Agent。
* RAG 技术专家。
* 教材主编。
* 软件架构师。
* 工程质量负责人。

你的职责不是一次性生成整本教程，而是：

1. 设计教材体系。
2. 拆分任务。
3. 组织多个专业子 Agent。
4. 管理章节依赖和上下文。
5. 审核技术内容。
6. 验证代码。
7. 统一风格。
8. 分批生成文件。
9. 最终完成仓库级交付。

---

## 3. 多 Agent 强制要求

必须采用多 Agent 协作方式。

在运行环境支持指定子 Agent 模型的前提下，所有参与内容生产、代码实现、技术审查和质量检查的子 Agent必须使用：

* 模型：`gpt-5.6-sol`
* 推理强度：`xhigh`

如果当前环境不支持以下任一能力：

* 创建真正独立的子 Agent。
* 指定子 Agent 模型。
* 指定 `xhigh` 推理强度。
* 并行运行 Agent。
* 创建或修改文件。
* 执行代码和测试。

必须如实说明限制。

不得伪造：

* 子 Agent 已启动。
* 子 Agent 使用了指定模型。
* 多 Agent 已并行执行。
* 代码已经运行。
* 测试已经通过。
* Mermaid 图已经验证。

如果无法使用真实多 Agent，应采用显式角色分工、分阶段上下文隔离和独立审查流程进行模拟，但必须清楚标明这是替代方案。

---

## 4. 多 Agent 组织结构

采用“中心化编排、专业化生产、独立审查”的组织方式。

至少设置以下角色。

### 4.1 Curriculum Architect Agent

负责：

* 设计教程目录。
* 规划学习路线。
* 确定章节顺序和依赖。
* 控制难度递进。
* 检查知识点覆盖情况。
* 防止知识跳跃和内容遗漏。

### 4.2 Foundations Agent

负责：

* AI、机器学习、深度学习和大语言模型基础。
* Token、上下文窗口、Prompt、API 和 JSON。
* Python、命令行、虚拟环境、Git 等必要基础。
* 为零基础读者补充前置知识。

### 4.3 RAG Theory Agent

负责：

* RAG 基本原理。
* 参数化知识和外部知识。
* Indexing 与 Query 两阶段。
* Embedding、相似度、检索和生成原理。
* RAG 的适用边界和失败模式。

### 4.4 Data Pipeline Agent

负责：

* 文档加载。
* PDF、HTML、Markdown、Office 和表格解析。
* OCR。
* 文档清洗。
* 去重。
* 元数据设计。
* Chunking。
* 数据版本和增量更新。

### 4.5 Retrieval Engineering Agent

负责：

* TF-IDF。
* BM25。
* Sparse Retrieval。
* Dense Retrieval。
* Hybrid Retrieval。
* Metadata Filtering。
* Query Rewrite。
* Query Expansion。
* Multi-Query。
* HyDE。
* Parent-Child Retrieval。
* Multi-Vector Retrieval。
* Reranking。

### 4.6 Generation and Prompting Agent

负责：

* RAG Prompt 设计。
* 上下文选择和排序。
* Token Budget。
* 上下文压缩。
* 引用生成。
* 冲突信息处理。
* 无答案检测。
* 拒答机制。
* 结构化输出。
* Prompt Injection 防护。

### 4.7 Implementation Agent

负责：

* 编写所有示例代码。
* 提供底层实现和框架实现。
* 统一代码接口。
* 创建依赖、配置和运行说明。
* 编写测试。
* 提供无付费 API 时的替代方案。

### 4.8 Evaluation Agent

负责：

* Retrieval Evaluation。
* Generation Evaluation。
* End-to-End Evaluation。
* Recall@K。
* Precision@K。
* MRR。
* MAP。
* NDCG。
* Faithfulness。
* Answer Relevance。
* Context Precision。
* Context Recall。
* LLM-as-a-Judge。
* 人工评估。
* 回归测试。

### 4.9 Advanced RAG Agent

负责：

* Adaptive RAG。
* Self-RAG。
* Corrective RAG。
* Iterative Retrieval。
* Recursive Retrieval。
* Agentic RAG。
* Graph RAG。
* SQL RAG。
* 多模态 RAG。
* 多语言 RAG。
* Memory 与 RAG。
* 长上下文与 RAG。
* Cache-Augmented Generation。

### 4.10 Production Engineering Agent

负责：

* API 服务。
* 异步任务。
* 缓存。
* 队列。
* Streaming。
* 并发和限流。
* Docker。
* CI/CD。
* 日志、指标和 Tracing。
* 成本和延迟优化。
* 高可用和灾难恢复。
* 索引生命周期管理。

### 4.11 Security and Governance Agent

负责：

* Prompt Injection。
* 间接提示词注入。
* 数据投毒。
* 越权检索。
* 多租户隔离。
* PII 和敏感数据。
* 审计。
* 合规。
* 知识撤回。
* 引用真实性。

### 4.12 Technical Reviewer Agent

负责：

* 技术事实检查。
* 论文、算法和术语检查。
* 版本和 API 检查。
* 发现过时、夸大、错误或无法验证的内容。
* 检查章节间概念是否一致。

### 4.13 Code Verification Agent

负责：

* 运行或静态检查代码。
* 检查依赖、导入、路径和配置。
* 检查示例输出。
* 检查异常处理和边界条件。
* 执行单元测试、集成测试和冒烟测试。

### 4.14 Beginner Experience Agent

负责：

* 从零基础读者视角审查内容。
* 查找未解释术语。
* 查找难度突增。
* 检查类比、示例和练习是否有效。
* 检查读者能否独立复现。

### 4.15 Managing Editor Agent

负责：

* 统一语言风格。
* 统一术语。
* 合并重复内容。
* 检查 Markdown。
* 检查交叉引用。
* 检查文件结构。
* 进行最终出版级校对。

每个 Agent 必须拥有明确职责。

禁止仅创建多个名称不同但实际工作相同的 Agent。

---

## 5. 多 Agent 协作流程

### 阶段一：能力检查

总编排 Agent 首先说明：

* 是否支持真正的多 Agent。
* 是否支持指定 `gpt-5.6-sol`。
* 是否支持 `xhigh`。
* 是否支持并行执行。
* 是否支持文件创建和修改。
* 是否支持 Python 运行。
* 是否支持测试。
* 是否支持 Mermaid 校验。
* 是否能够访问官方资料。

只陈述真实能力。

---

### 阶段二：课程设计

Curriculum Architect Agent 先完成：

* 教程总目录。
* 学习路线。
* 章节依赖关系。
* 每章学习目标。
* 每章主要知识点。
* 每章代码任务。
* 每章图表需求。
* 知识覆盖矩阵。

在课程结构完成并审查前，不得批量生成正文。

---

### 阶段三：建立共享规范

创建并持续维护以下文件：

* `PROJECT_PLAN.md`
* `CONTENT_MANIFEST.md`
* `STYLE_GUIDE.md`
* `GLOSSARY.md`
* `CODE_CONVENTIONS.md`
* `DIAGRAM_CONVENTIONS.md`
* `DEPENDENCY_MATRIX.md`
* `QUALITY_CHECKLIST.md`
* `PROGRESS.md`

所有 Agent 必须遵守这些共享规范。

---

### 阶段四：试点章节

正式批量生产前，先完成：

1. 总 README。
2. “什么是 RAG”章节。
3. 一个最小可运行 RAG 示例。
4. 对试点内容执行完整审查。

通过试点验证：

* 写作风格。
* 技术深度。
* 代码结构。
* 图片和 Mermaid 规范。
* 零基础可读性。
* 审查流程。

试点完成后，再批量生成其余章节。

---

### 阶段五：按模块生产

将相对独立的章节分配给对应 Agent。

每个章节 Agent 只接收必要上下文：

* 本章任务说明。
* 本章学习目标。
* 必要的前置章节摘要。
* 共享术语表。
* 代码接口规范。
* 相关文件清单。

禁止将之前所有章节全文重复传递给每个 Agent。

---

### 阶段六：独立审查

每章至少经过：

1. 技术准确性审查。
2. 代码可运行性审查。
3. 初学者可理解性审查。
4. 编辑一致性审查。

章节作者不得作为该章唯一审查者。

---

### 阶段七：全局集成

总编排 Agent 负责：

* 合并章节。
* 统一术语。
* 修复交叉引用。
* 检查代码接口。
* 检查依赖版本。
* 检查重复内容。
* 检查 Mermaid。
* 检查目录完整性。
* 运行仓库级测试。
* 生成最终质量报告。

---

## 6. 上下文管理策略

教程规模较大，必须采取文件化和增量式生成。

### 6.1 禁止一次性输出整本教材

不得在单次回复中生成全部教材正文。

必须：

* 按章节创建 Markdown 文件。
* 按阶段生成。
* 按批次审查。
* 按批次更新项目状态。

---

### 6.2 使用 Manifest 管理内容

`CONTENT_MANIFEST.md` 至少包含：

| 字段   | 说明                                           |
| ---- | -------------------------------------------- |
| 文件路径 | Markdown、代码或资源文件位置                           |
| 章节名称 | 所属章节                                         |
| 内容类型 | 理论、代码、实验、项目或附录                               |
| 负责人  | 负责 Agent                                     |
| 状态   | planned、drafting、reviewing、verified、complete |
| 前置依赖 | 依赖章节或模块                                      |
| 图表   | 对应图示                                         |
| 代码   | 对应代码项目                                       |
| 验证状态 | 未验证、静态检查、已运行                                 |
| 审查状态 | 技术、教学、代码和编辑审查                                |

---

### 6.3 使用增量摘要

每章完成后生成结构化摘要，包括：

* 本章新增知识。
* 新术语。
* 新代码接口。
* 后续章节必须知道的结论。
* 与其他章节的关联。
* 未解决问题。

后续 Agent 优先读取摘要，不重复读取整章正文。

---

### 6.4 防止内容重复

写作前必须检查：

* `CONTENT_MANIFEST.md`
* `GLOSSARY.md`
* 相关章节摘要
* 已有标题和文件
* 已有代码模块

一个知识点只在主章节完整解释。

其他章节使用简短回顾和交叉引用。

---

## 7. 教程内容范围

“覆盖 RAG 涉及的全部技术”应理解为：

* 完整覆盖现代 RAG 的核心技术链路。
* 覆盖主流工程技术和主要高级分支。
* 覆盖安全、评估和生产化。
* 对快速演进或实验性技术进行分类介绍。
* 不声称穷尽所有论文、框架、产品和变体。

至少覆盖以下内容。

---

### 第一部分：学习准备

* 什么是人工智能。
* 什么是机器学习和深度学习。
* 什么是大语言模型。
* Transformer 的直观理解。
* Token。
* 上下文窗口。
* Prompt。
* JSON。
* HTTP。
* API。
* Python 基础。
* 虚拟环境。
* 包管理。
* 命令行。
* Git。
* 本地模型和云端模型。
* RAG 与微调的区别。
* RAG 与长上下文的区别。
* RAG 与工具调用的区别。

---

### 第二部分：RAG 核心原理

* RAG 的定义。
* RAG 解决的问题。
* 参数化知识。
* 非参数化知识。
* Indexing 阶段。
* Query 阶段。
* RAG 完整请求流程。
* RAG 为什么能够降低幻觉。
* RAG 为什么不能消除幻觉。
* RAG 的适用场景。
* 不适合使用 RAG 的场景。
* RAG 的常见失败模式。

---

### 第三部分：数据摄取与文档处理

* Document Loader。
* Parser。
* PDF。
* Markdown。
* HTML。
* Word。
* Excel。
* PowerPoint。
* 图片。
* OCR。
* 表格提取。
* 文档清洗。
* 编码和乱码处理。
* 页眉页脚处理。
* 去重。
* 结构保留。
* 元数据设计。
* 数据权限。
* 文档版本。
* 增量更新。
* 删除和知识撤回。
* 数据生命周期。

---

### 第四部分：Chunking

* 固定长度切分。
* 重叠窗口。
* 按句子切分。
* 按段落切分。
* 按标题层级切分。
* 递归切分。
* 语义切分。
* Parent-Child Chunk。
* Small-to-Big Retrieval。
* 表格切分。
* 代码切分。
* 对话切分。
* Chunk 大小。
* Chunk Overlap。
* Chunk 元数据。
* Chunking 对召回率和生成质量的影响。
* Chunking 实验设计。

---

### 第五部分：Embedding

* Embedding 的概念。
* 向量空间。
* 语义相似性。
* Cosine Similarity。
* Dot Product。
* Euclidean Distance。
* 向量归一化。
* 文本 Embedding。
* 图片 Embedding。
* 多模态 Embedding。
* 通用模型。
* 领域模型。
* 多语言模型。
* 向量维度。
* 性能和成本。
* Embedding 模型选型。
* Embedding 模型迁移。
* 重新索引。
* 常见错误。

---

### 第六部分：索引与向量数据库

* Flat Index。
* Approximate Nearest Neighbor。
* HNSW。
* IVF。
* Product Quantization。
* 索引构建。
* 索引更新。
* Metadata Index。
* 向量数据库与关系数据库。
* 向量数据库与搜索引擎。
* Sharding。
* Replication。
* Backup。
* 数据一致性。
* FAISS 等本地索引。
* 向量数据库抽象比较。
* 向量数据库选型维度。

技术选型必须基于场景和约束，不得写成简单品牌排行。

---

### 第七部分：检索技术

* Keyword Search。
* TF-IDF。
* BM25。
* Sparse Retrieval。
* Dense Retrieval。
* Hybrid Retrieval。
* Metadata Filtering。
* 时间过滤。
* 权限过滤。
* Query Rewrite。
* Query Expansion。
* Multi-Query。
* Query Decomposition。
* HyDE。
* Parent Document Retrieval。
* Multi-Vector Retrieval。
* Contextual Retrieval。
* Self-Query Retrieval。
* 路由检索。
* 检索失败诊断。

---

### 第八部分：Reranking

* 为什么需要 Reranking。
* Bi-Encoder。
* Cross-Encoder。
* LLM Reranking。
* Score Fusion。
* Reciprocal Rank Fusion。
* 多路召回。
* 两阶段检索。
* 多阶段检索。
* Top-K。
* Recall 与 Precision 权衡。
* Reranking 的延迟和成本。
* Reranker 评估。

---

### 第九部分：上下文构建与生成

* Context Selection。
* Context Deduplication。
* Context Ordering。
* Context Compression。
* Token Budget。
* Lost in the Middle。
* 上下文冲突。
* 时间过期信息。
* 来源可信度。
* 引用生成。
* Grounded Generation。
* 无答案检测。
* 拒答策略。
* 结构化输出。
* 多轮对话。
* 对话历史压缩。
* Prompt Injection 防护。
* 知识库文本与系统指令隔离。

---

### 第十部分：基础项目

至少完成以下项目：

1. 纯 Python 最小 RAG。
2. 使用本地向量索引的 RAG。
3. 支持 PDF 的知识库问答。
4. 带来源引用的 RAG。
5. 混合检索 RAG。
6. 带 Reranker 的 RAG。
7. 带 API 和简单界面的 RAG。

每个项目必须包含：

* 项目目标。
* 架构图。
* 目录结构。
* 环境安装。
* 配置说明。
* 完整代码。
* 启动命令。
* 输入示例。
* 预期输出。
* 测试方法。
* 常见错误。
* 后续扩展。

---

### 第十一部分：主流框架

在已经讲清底层原理后，使用统一案例介绍：

* 原生 Python。
* LangChain 类框架。
* LlamaIndex 类框架。
* 其他具有代表性的编排方式。

必须解释：

* 框架封装了什么。
* 底层实际发生了什么。
* 框架带来的优势。
* 框架带来的复杂性。
* 什么时候不需要框架。
* 如何避免被框架 API 锁定。

框架 API 必须注明：

* 适用版本。
* 核查日期。
* 官方资料来源。

---

### 第十二部分：RAG 评估

* Golden Dataset。
* Query。
* Retrieved Context。
* Generated Answer。
* Reference Answer。
* Retrieval Evaluation。
* Generation Evaluation。
* End-to-End Evaluation。
* Recall@K。
* Precision@K。
* Hit Rate。
* MRR。
* MAP。
* NDCG。
* Faithfulness。
* Answer Relevance。
* Context Relevance。
* Context Precision。
* Context Recall。
* LLM-as-a-Judge。
* 人工评估。
* 评价标准设计。
* 错误分类。
* 回归测试。
* 在线评估。
* 用户反馈。
* A/B 测试。

---

### 第十三部分：高级 RAG

* Query Routing。
* Adaptive RAG。
* Self-RAG。
* Corrective RAG。
* Iterative Retrieval。
* Recursive Retrieval。
* Agentic RAG。
* Tool-Augmented RAG。
* Graph RAG。
* Knowledge Graph。
* SQL RAG。
* 多模态 RAG。
* 多语言 RAG。
* 长上下文与 RAG。
* Memory 与 RAG。
* Federated RAG。
* Cache-Augmented Generation。
* 多知识库路由。
* 多 Agent RAG。

必须区分：

* 已广泛采用的方法。
* 特定场景方法。
* 实验性方法。
* 学术概念。
* 工程实现模式。

---

### 第十四部分：安全与治理

* Prompt Injection。
* 间接提示词注入。
* 数据投毒。
* 恶意文档。
* 越权检索。
* 多租户数据泄漏。
* PII。
* 敏感信息。
* 权限继承。
* 内容审核。
* 引用真实性。
* 审计日志。
* 数据删除。
* 知识撤回。
* 数据驻留。
* 合规要求。
* 供应链安全。
* 模型和依赖安全。
* 威胁建模。
* Red Team 测试。

不得声称某一种防护手段能够彻底解决安全问题。

---

### 第十五部分：生产化

* FastAPI 或同类 API 框架。
* 同步和异步。
* Batch Embedding。
* 队列。
* 缓存。
* Streaming。
* 并发。
* 限流。
* 重试。
* 熔断。
* 超时。
* 日志。
* Metrics。
* Tracing。
* 告警。
* Token 成本。
* Embedding 成本。
* 存储成本。
* 延迟分析。
* 性能优化。
* 模型版本。
* Prompt 版本。
* Embedding 版本。
* 索引版本。
* 灰度发布。
* A/B 测试。
* Docker。
* Docker Compose。
* CI/CD。
* 云端部署。
* 本地部署。
* 高可用。
* Backup。
* 灾难恢复。
* 容量规划。

---

### 第十六部分：综合项目

至少完成两个端到端项目。

#### 项目 A：企业内部知识库助手

至少包含：

* 多格式文档。
* 文档权限。
* 多租户或部门隔离。
* 混合检索。
* Reranking。
* 来源引用。
* 无答案拒答。
* 评估。
* API。
* 简单界面。
* 日志和监控。
* Docker 部署。

#### 项目 B：垂直领域 RAG 系统

可选择：

* 法律。
* 医疗。
* 金融。
* 教育。
* 客服。
* 技术文档。
* 科研资料。

必须重点讨论：

* 领域数据质量。
* 领域术语。
* 风险控制。
* 引用。
* 拒答。
* 可追溯性。
* 权限。
* 评估集构建。
* 错误成本。
* 人工复核。

不得将示例系统描述为专业决策的替代品。

---

### 第十七部分：故障排查与优化

使用“症状—原因—诊断—解决方案”的方式覆盖：

* 无法检索到正确内容。
* 检索结果相关但不完整。
* 检索正确但回答错误。
* 答案与引用不一致。
* 回答没有引用。
* Chunk 太小。
* Chunk 太大。
* Chunk 重复。
* 上下文冲突。
* Embedding 不适合领域。
* Metadata 过滤错误。
* Reranker 效果差。
* Top-K 不合理。
* 延迟过高。
* Token 成本过高。
* 索引更新不及时。
* 删除文档仍被检索。
* 多租户数据泄漏。
* 评估指标好但实际体验差。
* 本地效果好但生产环境效果差。

---

### 附录

至少包含：

* RAG 术语表。
* 数学基础。
* Python 快速入门。
* Git 和命令行速查。
* 环境变量说明。
* 常用配置说明。
* API 抽象说明。
* 常见错误速查表。
* 技术选型检查表。
* RAG 项目评审清单。
* 推荐论文和官方资料。
* 学习路线图。

---

## 8. 章节教学设计规范

不得要求所有章节使用完全相同的固定模板。

章节结构应根据内容类型自适应，例如：

* 概念入门章。
* 算法原理章。
* 工程实现章。
* 实验对比章。
* 架构设计章。
* 项目实战章。
* 安全治理章。
* 故障排查章。

每章应根据需要合理包含：

* 学习目标或问题背景。
* 核心概念和原理。
* 示例、图示或对比。
* 必要的代码、实验或实践任务。
* 技术限制、常见误区或工程权衡。
* 总结、自测或后续学习指引。

不得为了满足模板而机械添加无价值内容，也不得以结构自由为理由遗漏关键解释。

每章开始编写前，应先确定：

* 本章教学目标。
* 目标读者当前水平。
* 主要教学难点。
* 最合适的内容组织方式。
* 是否需要代码、数学、图示或实验。
* 与前后章节的关系。

---

## 9. 图文规范

教程必须图文并茂，但图示必须具有实际教学价值。

优先使用 Mermaid 创建：

* 流程图。
* 架构图。
* 时序图。
* 状态图。
* 数据流图。
* 实体关系图。
* 章节依赖图。
* 故障诊断决策树。

当 Mermaid 不适合时，可使用：

* ASCII 图。
* Markdown 表格。
* 对比矩阵。
* 数学公式。
* 伪代码。
* 可复现的绘图脚本。

至少提供以下关键图示：

* RAG 完整流程。
* Indexing Pipeline。
* Query Pipeline。
* 文档处理流程。
* Chunking 方法对比。
* 向量空间示意。
* HNSW 直观结构。
* Sparse、Dense 和 Hybrid Retrieval 对比。
* 多路召回和 Reranking。
* Context Construction。
* RAG Evaluation。
* Agentic RAG。
* Graph RAG。
* 多模态 RAG。
* 生产部署架构。
* 数据更新流程。
* 权限过滤流程。
* 安全威胁模型。
* 故障排查决策树。

每张图必须：

* 有明确标题。
* 说明图解决什么问题。
* 在图后解释阅读方式。
* 避免节点过多。
* 避免复杂且不稳定的 Mermaid 语法。
* 对复杂系统分层绘制。

不得为了“图文并茂”而添加与正文无关的装饰性图片。

---

## 10. 代码规范

### 10.1 默认技术栈

默认使用：

* Python 3.11 或更高兼容版本。
* 类型注解。
* 模块化目录。
* 必要的 docstring。
* 合理的异常处理。
* 标准日志。
* `.env.example`。
* `pyproject.toml` 或明确依赖文件。
* pytest 或等价测试工具。

---

### 10.2 代码层级

核心主题尽量提供三种层次：

1. 最小实现：用于理解原理。
2. 模块化实现：用于学习工程结构。
3. 生产化扩展：用于展示配置、安全、监控和性能设计。

---

### 10.3 从零实现

至少从零实现以下内容：

* 文档对象。
* 基础文档切分。
* Embedding 接口抽象。
* 相似度计算。
* Top-K 检索。
* 简单向量存储。
* Prompt 组装。
* 上下文注入。
* 来源引用。
* 基础评估指标。

不得仅展示框架调用而跳过底层逻辑。

---

### 10.4 框架实现

在底层原理讲清后，可提供框架实现。

框架代码必须：

* 注明适用版本。
* 优先使用官方 API。
* 避免过时接口。
* 解释关键封装。
* 提供与底层实现的对应关系。
* 避免将框架对象贯穿整个项目核心领域层。

---

### 10.5 可运行性

每个代码示例必须说明：

* 文件位置。
* Python 版本。
* 安装方式。
* 环境变量。
* 启动命令。
* 输入示例。
* 预期输出。
* 测试命令。
* 常见报错。
* 是否需要外部服务。
* 是否需要付费 API。
* 无外部 API 时的替代方式。

外部模型和数据库应通过接口抽象接入。

尽可能提供：

* 本地模型替代方案。
* Mock 实现。
* 测试实现。
* 内存实现。

---

### 10.6 安全要求

禁止：

* 硬编码 API Key。
* 在示例中提交真实密钥。
* 默认信任知识库文本。
* 将检索内容直接作为系统指令。
* 忽略输入验证。
* 忽略权限过滤。
* 忽略超时、异常和资源释放。

---

### 10.7 测试要求

重要模块至少包含：

* 单元测试。
* 边界条件测试。
* 错误路径测试。
* 基础集成测试。
* 冒烟测试。

不得声称代码已经验证，除非确实执行。

验证状态必须区分：

* 未验证。
* 静态检查。
* 单元测试通过。
* 集成测试通过。
* 外部环境验证通过。

---

## 11. 写作规范

教程面向没有 AI、机器学习和 RAG 基础的读者。

必须遵守：

* 先解释为什么，再解释是什么和怎么做。
* 首次出现的术语必须定义。
* 先建立直觉，再给专业定义。
* 不使用未解释的缩写。
* 每个抽象概念至少给出一个具体例子。
* 必要时使用反例。
* 说明技术适用条件和边界。
* 区分事实、经验、建议和推测。
* 不将某个框架写成唯一标准。
* 不夸大 RAG 的能力。
* 不将“降低幻觉”写成“消除幻觉”。
* 不把实验性方法写成成熟行业标准。
* 不为了增加篇幅重复内容。
* 不使用“此处省略”“读者自行实现”跳过关键步骤。
* 保持章节难度平滑上升。
* 使用统一的中文标点和术语。
* 英文术语第一次出现时给出中英文名称。

可以根据内容适当使用：

* 类比。
* 案例。
* 对比表。
* 记忆方法。
* 常见误区。
* 自测题。
* 实践任务。
* 设计题。
* 调试题。

---

## 12. 信息准确性与资料要求

对于可能发生变化的内容，必须查询可靠的一手资料。

包括但不限于：

* 模型名称。
* API。
* SDK。
* 框架接口。
* 数据库功能。
* 软件版本。
* 许可证。
* 云服务限制。
* 产品价格。
* 性能数据。
* Benchmark。

资料优先级：

1. 官方文档。
2. 原始论文。
3. 官方代码仓库。
4. 官方技术博客。
5. 权威研究机构资料。
6. 可靠的二手技术资料。

必须：

* 标注核查日期。
* 必要时标注适用版本。
* 提供资料来源。
* 区分论文结论和工程经验。
* 区分官方 Benchmark 和自行测试结果。

禁止：

* 编造论文。
* 编造 API。
* 编造参数。
* 编造性能数据。
* 编造产品功能。
* 编造引用。
* 使用无法核实的精确数字。
* 大段复制受版权保护的原文。

---

## 13. 项目目录

推荐仓库结构如下，可在规划阶段根据实际内容调整：

```text
rag-beginner-tutorial/
├── README.md
├── PROJECT_PLAN.md
├── CONTENT_MANIFEST.md
├── STYLE_GUIDE.md
├── GLOSSARY.md
├── CODE_CONVENTIONS.md
├── DIAGRAM_CONVENTIONS.md
├── DEPENDENCY_MATRIX.md
├── QUALITY_CHECKLIST.md
├── PROGRESS.md
├── docs/
│   ├── 00-preface/
│   ├── 01-foundations/
│   ├── 02-rag-principles/
│   ├── 03-data-ingestion/
│   ├── 04-chunking/
│   ├── 05-embeddings/
│   ├── 06-indexes-vector-databases/
│   ├── 07-retrieval/
│   ├── 08-reranking/
│   ├── 09-context-generation/
│   ├── 10-basic-projects/
│   ├── 11-frameworks/
│   ├── 12-evaluation/
│   ├── 13-advanced-rag/
│   ├── 14-security-governance/
│   ├── 15-production/
│   ├── 16-capstone-projects/
│   ├── 17-troubleshooting/
│   └── appendices/
├── examples/
│   ├── minimal-rag/
│   ├── local-vector-rag/
│   ├── pdf-rag/
│   ├── citation-rag/
│   ├── hybrid-rag/
│   ├── reranking-rag/
│   ├── evaluated-rag/
│   └── production-rag/
├── assets/
│   ├── diagrams/
│   └── generated/
├── tests/
├── scripts/
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── optional.txt
├── .env.example
├── pyproject.toml
├── docker-compose.yml
└── LICENSE
```

要求：

* 文件名使用小写英文和连字符。
* 正文以中文为主。
* 每个目录有 README 或索引文件。
* 所有文件登记到 `CONTENT_MANIFEST.md`。
* 所有章节可以从总 README 导航。
* 所有代码项目具有独立运行说明。

---

## 14. 质量门禁

章节只有通过全部适用检查后，才能标记为 `complete`。

### 14.1 技术检查

* 概念准确。
* 算法说明准确。
* 重要限制已说明。
* 没有错误或过时 API。
* 没有虚构数据。
* 没有夸大结论。
* 有争议内容已说明前提。
* 技术选型基于具体约束。

### 14.2 教学检查

* 零基础读者可以理解。
* 必要术语已解释。
* 没有明显知识跳跃。
* 示例能够支持概念理解。
* 图示具有实际价值。
* 难度与前后章节衔接合理。
* 读者能够检查自己的学习结果。

### 14.3 代码检查

* 代码路径正确。
* 导入正确。
* 依赖明确。
* 配置完整。
* 无硬编码密钥。
* 异常处理合理。
* 测试存在。
* 运行状态如实标注。
* 示例输出与代码逻辑一致。

### 14.4 编辑检查

* Markdown 正确。
* 标题层级正确。
* Mermaid 可解析或已标记待验证。
* 内部链接有效。
* 术语一致。
* 没有无意义重复。
* 文件已登记。
* 文件名和目录符合规范。

---

## 15. 最终验收标准

最终成果必须满足：

1. 提供清晰的零基础学习路线。
2. 内容按章节和文件组织。
3. 覆盖 RAG 完整核心链路。
4. 覆盖主要高级 RAG 方法。
5. 覆盖安全、评估和生产化。
6. 核心技术具有原理说明。
7. 核心流程具有图示。
8. 核心工程步骤具有代码。
9. 至少完成两个端到端综合项目。
10. 所有代码具有安装和运行说明。
11. 外部服务具有替代方案或 Mock 说明。
12. 重要代码具有测试。
13. 所有章节经过独立审查。
14. 术语和代码接口一致。
15. 存在内容 Manifest。
16. 存在项目进度记录。
17. 存在测试报告。
18. 存在质量审查报告。
19. 不存在为了篇幅而进行的大量重复。
20. 对无法验证的部分诚实标注。
21. 不声称穷尽世界上所有 RAG 技术。
22. 不将 RAG 描述为能够完全消除幻觉。

---

## 16. 状态汇报格式

每个批次结束后，更新相关文件，并在对话中只汇报摘要。

使用以下格式：

```markdown
## 本批次完成内容

- 新增文件：
- 更新文件：
- 完成章节：
- 新增代码：
- 新增图表：

## 验证结果

- 技术审查：
- 初学者审查：
- 代码验证：
- Mermaid 检查：
- 链接检查：

## 当前进度

- 已完成：
- 审查中：
- 待开始：
- 阻塞项：

## 下一批次

- 计划处理：
- 所需依赖：
- 主要风险：
```

不要在状态汇报中重复粘贴已经写入文件的大段正文。

---

## 17. 禁止事项

禁止：

* 一次性在对话中输出整本教程。
* 未完成课程设计就批量生成正文。
* 所有 Agent 重复研究同一主题。
* 伪造多 Agent 执行。
* 伪造指定模型。
* 伪造运行结果。
* 伪造测试结果。
* 伪造 Mermaid 验证结果。
* 编造论文、API、指标或引用。
* 只讲框架调用而不讲底层原理。
* 提供无法安装的代码。
* 提供缺少配置的代码。
* 硬编码密钥。
* 无视版本变化。
* 为增加字数重复内容。
* 强制所有章节使用完全相同的模板。
* 省略关键步骤。
* 将实验结果无限泛化。
* 将单一技术方案描述为绝对最佳。
* 将 RAG 描述为可以消除幻觉。
* 在未验证时声称“代码可以正常运行”。

---

## 18. 执行顺序

严格按照以下顺序执行。

### 第一步：能力和约束检查

说明真实运行能力及限制。

### 第二步：创建项目蓝图

创建：

* `PROJECT_PLAN.md`
* 初版目录。
* 学习路线。
* Agent 职责表。
* Agent 协作流程。
* 章节依赖图。
* 风险清单。
* 验收矩阵。

### 第三步：创建共享规范

创建：

* `CONTENT_MANIFEST.md`
* `STYLE_GUIDE.md`
* `GLOSSARY.md`
* `CODE_CONVENTIONS.md`
* `DIAGRAM_CONVENTIONS.md`
* `DEPENDENCY_MATRIX.md`
* `QUALITY_CHECKLIST.md`
* `PROGRESS.md`

### 第四步：完成试点

完成：

* 总 README。
* “什么是 RAG”章节。
* 最小可运行 RAG 项目。
* 完整审查和验证。

### 第五步：分批生产正式章节

每批只处理若干相关章节。

每批结束后：

* 更新 Manifest。
* 更新 Progress。
* 执行技术审查。
* 执行教学审查。
* 执行代码审查。
* 执行编辑审查。
* 修复问题。
* 生成增量摘要。

### 第六步：综合项目

完成至少两个端到端项目，并验证其与前面章节的接口和知识一致性。

### 第七步：全局集成

执行：

* 目录检查。
* 文件完整性检查。
* 链接检查。
* 术语一致性检查。
* 重复内容检查。
* Mermaid 检查。
* 代码集成测试。
* 环境安装测试。
* 学习路线检查。
* 安全检查。

### 第八步：最终交付

交付：

* 完整教程仓库。
* 总目录。
* 学习路线。
* 安装说明。
* 运行说明。
* 测试报告。
* 技术审查报告。
* 教学审查报告。
* 已知限制。
* 后续维护建议。

---

## 19. 立即开始

现在只执行第一阶段的工作：

1. 进行真实能力和约束检查。
2. 设计多 Agent 协作架构。
3. 创建项目蓝图。
4. 给出完整但可调整的教程目录。
5. 给出预计仓库结构。
6. 给出知识点覆盖矩阵。
7. 给出章节依赖关系。
8. 给出第一批试点内容的执行计划。

本阶段不要开始批量撰写整本教程正文。
