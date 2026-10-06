# 原子验收与证据矩阵

本矩阵把硬性交付拆成稳定 requirement-id。`planned` 只说明已经安排路径，不能作为
完成证据。章节写作前，负责人必须把对应内容 ID 加入 `CONTENT_MANIFEST.md`；完成时
填写真实 evidence 和 reviewer 结论。

字段：需求、planned path、owner、依赖、完成证据、验证方法、独立 reviewer、状态。

## 最终验收

| ID | 需求 | planned path | owner | 依赖 | 完成证据 | 验证方法 | reviewer | 状态 |
|---|---|---|---|---|---|---|---|---|
| AC01 | 清晰零基础学习路线 | README.md；00；appendices/12 | Curriculum | 无 | 导航与通关任务 | 链接和初学者走查 | Beginner | planned |
| AC02 | 按章节和文件组织 | docs；CONTENT_MANIFEST.md | Editor | AC01 | 目录与 Manifest | manifest checker | Editorial | planned |
| AC03 | 完整核心链路 | docs/02-09 | Theory/Data/Retrieval/Generation | 01 | 章节与代码 | coverage check | Technical | planned |
| AC04 | 主要高级方法 | docs/13 | Advanced | 07/09/12 | 六维方法矩阵 | source + coverage check | Technical | planned |
| AC05 | 安全、评估、生产 | docs/12、14、15 | Evaluation/Security/Production | 10 | 章节、测试、报告 | coverage + tests | Technical | planned |
| AC06 | 核心技术有原理 | docs/02、04-09 | Domain authors | 01 | 原理、例子、限制 | technical review | Technical | planned |
| AC07 | 核心流程有图 | D01 至 D20 | Diagram owners | 对应章节 | 图源与说明 | render/static report | Editorial | planned |
| AC08 | 核心工程有代码 | src、examples、capstones | Implementation | 02-09 | 代码与 README | tests + smoke | Code Verification | planned |
| AC09 | 两个端到端项目 | CAP-01、CAP-02 | Capstone owners | 11/12/14/15 | 两个独立项目 | e2e + review | Review Board | planned |
| AC10 | 所有代码有安装运行说明 | 各项目 README | Implementation | AC08 | README | command audit | Code Verification | planned |
| AC11 | 外部服务有替代或 Mock | adapters；各 README | Implementation | AC08 | Mock/内存实现 | offline tests | Code Verification | planned |
| AC12 | 重要代码有测试 | tests | Test Engineer | AC08 | 测试与报告 | pytest | Code Verification | planned |
| AC13 | 所有章节独立审查 | reports；Manifest | Review Board | 章节 draft | 四类审查记录 | reviewer identity audit | Managing Editor | planned |
| AC14 | 术语和接口一致 | GLOSSARY；CODE_CONVENTIONS | Editor/Implementation | shared specs | 术语/契约检查 | glossary + contract tests | Technical | planned |
| AC15 | 存在内容 Manifest | CONTENT_MANIFEST.md | Editor | 无 | 当前清单 | manifest checker | Editorial | verified |
| AC16 | 存在进度记录 | PROGRESS.md | Leader | 无 | 批次记录 | status audit | Editorial | verified |
| AC17 | 存在测试报告 | reports/test-report.md | Test Engineer | tests | 真实命令与结果 | evidence audit | Code Verification | planned |
| AC18 | 存在质量审查报告 | reports | Review Board | AC13 | 各报告 | report index audit | Managing Editor | planned |
| AC19 | 无大量重复 | Manifest 主讲字段；summaries | Editor | 章节 | 重复检查报告 | heading/text similarity review | Editorial | planned |
| AC20 | 无法验证处诚实标注 | Manifest；known-limitations | All | 无 | 分级状态 | claim/evidence audit | Technical | planned |
| AC21 | 不声称穷尽所有技术 | STYLE_GUIDE；00；13 | Editor | 无 | 文本检查 | forbidden-claim search | Technical | planned |
| AC22 | 不声称 RAG 消除幻觉 | STYLE_GUIDE；02 | Theory | 无 | 文本检查 | forbidden-claim search | Technical | planned |

## 共享交付物

| ID | 需求 | planned path | owner | 依赖 | 完成证据 | 验证方法 | reviewer | 状态 |
|---|---|---|---|---|---|---|---|---|
| ART-PLAN | 项目计划、路线、职责、依赖、风险 | PROJECT_PLAN.md | Leader/Curriculum | 无 | 已创建 | structure check | Technical + Beginner | verified |
| ART-MANIFEST | 内容与状态清单 | CONTENT_MANIFEST.md | Editor | ART-PLAN | 已创建 | path coverage | Editorial | verified |
| ART-STYLE | 写作与教学规范 | STYLE_GUIDE.md | Editor/Beginner | ART-PLAN | 已创建 | rule review | Beginner | verified |
| ART-GLOSSARY | 中英术语和主解释路径 | GLOSSARY.md | Foundations | ART-STYLE | 已创建 | duplicate/first-use audit | Technical | verified |
| ART-CODE | Python、接口、安全和测试规范 | CODE_CONVENTIONS.md | Implementation | ART-PLAN | 已创建 | code policy review | Code Verification | verified |
| ART-DIAGRAM | 图示结构和验证等级 | DIAGRAM_CONVENTIONS.md | Editor | ART-STYLE | 已创建 | diagram policy review | Editorial | verified |
| ART-DEPS | 四类章节能力依赖且无循环 | DEPENDENCY_MATRIX.md | Curriculum | ART-PLAN | 已创建 | cycle/manual audit | Beginner | verified |
| ART-QUALITY | 四类质量门禁 | QUALITY_CHECKLIST.md | Review Board | ART-PLAN | 已创建 | gate coverage | Technical | verified |
| ART-PROGRESS | 批次、阻塞和下一步 | PROGRESS.md | Leader | ART-PLAN | 已创建 | state consistency | Editorial | verified |
| ART-ACCEPTANCE | 原子需求到证据追踪 | ACCEPTANCE_MATRIX.md | Leader | ART-PLAN | 本文件 | ID/path checker | Technical | verified |
| ART-SOURCES | 版本敏感事实来源账本 | SOURCE_REGISTER.md | Technical Reviewer | ART-PLAN | 已创建 | source field audit | Technical | verified |
| ART-REPORTS | 测试和质量报告索引 | reports/README.md | Editor | ART-QUALITY | 已创建 | file/index audit | Editorial | verified |
| ART-SPEC | 仓库内持久化的用户权威规格 | SPECIFICATION.md | Leader | 无 | 原始 1,618 行规格 | checksum/line count | Technical | verified |
| ART-DATA-LICENSES | 数据许可登记模板 | DATA_LICENSES.md | Data/Security | ART-QUALITY | 已创建 | schema review | Editorial | verified |
| ART-THIRD-PARTY | 第三方资产登记模板 | THIRD_PARTY_NOTICES.md | Security/Editor | ART-QUALITY | 已创建 | schema review | Technical | verified |
| ART-VERIFY | 可复现规划验证脚本 | scripts/verify-planning.sh | Code Verification | ART-MANIFEST | 脚本与输出 | execute script | Technical | verified |
| ART-RUNTIME | 多 Agent/模型/环境原始运行证据 | reports/runtime-evidence.md | Leader | ART-REPORTS | 命令与捕获输出 | evidence audit | Technical | verified |
| ART-REVIEW-EVIDENCE | 独立 reviewer 原始结论与任务时间 | reports/review-evidence.md | Leader/Reviewers | ART-REPORTS | mailbox transcription | provenance audit | Technical | verified |

## 七个基础项目

| ID | 需求 | planned path | owner | 依赖 | 完成证据 | 验证方法 | reviewer | 状态 |
|---|---|---|---|---|---|---|---|---|
| BASIC-01 | 纯 Python 最小 RAG | examples/minimal-rag；10-01 | Implementation | 02；完整回访依赖 04-09 | 试点实现与测试已存在；10-01 完整回访仍 planned | unit + smoke | Code + Beginner | reviewing |
| BASIC-02 | 本地向量索引 RAG | examples/local-vector-rag；10-02 | Implementation | 05/06 | 项目与 Flat/本地索引 | unit + integration | Code | planned |
| BASIC-03 | PDF 知识库问答 | examples/pdf-rag；10-03 | Data/Implementation | 03/04/06 | PDF fixture 与问答 | integration | Code + Security | planned |
| BASIC-04 | 带来源引用 RAG | examples/citation-rag；10-04 | Generation | 09 | 引用对象与错配测试 | integration | Technical | planned |
| BASIC-05 | 混合检索 RAG | examples/hybrid-rag；10-05 | Retrieval | 07 | 稀疏/稠密双路 | retrieval evaluation | Technical | planned |
| BASIC-06 | 带 Reranker RAG | examples/reranking-rag；10-06 | Retrieval | 08 | 两阶段检索 | evaluation + latency | Technical | planned |
| BASIC-07 | API 和简单界面 RAG | examples/api-ui-rag；10-07 | Implementation | BASIC-04/06 | API/UI/README | smoke + input validation | Code + Beginner | planned |

每个 BASIC 项目还必须具备目标、架构图、目录、安装、配置、完整代码、启动、输入、
预期输出、测试、常见错误和扩展，并说明外部服务、费用与离线替代。

## 两个综合项目

| ID | 需求 | planned path | owner | 依赖 | 完成证据 | 验证方法 | reviewer | 状态 |
|---|---|---|---|---|---|---|---|---|
| CAP-01 | 企业内部知识库助手：多格式、权限/租户、Hybrid、Rerank、引用、拒答、评估、API/UI、监控、Docker | capstones/enterprise-knowledge-assistant；16-02/03 | Capstone Team | 11/12/14/15 | 项目、威胁模型、测试、部署 | e2e/security/smoke | Review Board | planned |
| CAP-02 | 垂直领域 RAG：数据质量、术语、风险、引用、拒答、追溯、权限、评估集、错误成本、人工复核 | capstones/domain-rag-system；16-04/05 | Capstone Team | 11/12/14/15 | 项目、dataset card、风险声明 | e2e/human review audit | Review Board | planned |

## 关键图示

| ID | 需求 | planned path | owner | 依赖 | 完成证据 | 验证方法 | reviewer | 状态 |
|---|---|---|---|---|---|---|---|---|
| D01 | RAG 完整流程 | 02-01；assets/diagrams/rag-end-to-end.mmd | Theory | 02 | 图源、阅读说明与 static-checked 证据；未渲染 | static/render report | Editorial | reviewing |
| D02 | Indexing Pipeline | 02-03 | Theory | 02 | 图源+阅读说明 | static/render report | Technical | planned |
| D03 | Query Pipeline | 02-03 | Theory | 02 | 图源+阅读说明 | static/render report | Technical | planned |
| D04 | 文档处理流程 | 03-01 | Data | 03 | 图源+阅读说明 | static/render report | Technical | planned |
| D05 | Chunking 方法对比 | 04-01/02 | Data | 04 | 表格+简图 | visual review | Beginner | planned |
| D06 | 向量空间示意 | 05-01 | Embedding | 05 | 可复现图源 | script/render | Technical | planned |
| D07 | HNSW 直观结构 | 06-02 | Index | 06 | 分层图 | visual review | Beginner | planned |
| D08 | Sparse/Dense/Hybrid 对比 | 07-02 | Retrieval | 07 | 对比图 | static/render report | Technical | planned |
| D09 | 多路召回与 Reranking | 08 | Retrieval | 08 | 多阶段图 | static/render report | Technical | planned |
| D10 | Context Construction | 09-01/02 | Generation | 09 | 数据流图 | static/render report | Technical | planned |
| D11 | RAG Evaluation | 12-01/05 | Evaluation | 12 | 评估闭环 | static/render report | Technical | planned |
| D12 | Agentic RAG | 13-04 | Advanced | 13 | 预算/停止/失败图 | technical review | Technical | planned |
| D13 | Graph RAG | 13-05 | Advanced | 13 | 非唯一实现分层图 | source + technical review | Technical | planned |
| D14 | 多模态 RAG | 13-07 | Advanced | 13 | 多模态解析/表示图 | technical review | Technical | planned |
| D15 | 生产部署架构 | 15-08；16-03 | Production | 15 | 控制/数据面图 | architecture review | Technical | planned |
| D16 | 数据更新流程 | 03-07 | Data/Production | 03 | 版本/墓碑/回滚图 | lifecycle review | Technical | planned |
| D17 | 权限过滤流程 | 03/07/14 | Security | 14 | 全链路授权图 | security review | Technical Reviewer（非作者） | planned |
| D18 | 安全威胁模型 | 14-01/02 | Security | 14 | 信任边界图 | threat-model review | Technical Reviewer（非作者） | planned |
| D19 | 故障排查决策树 | 17 | Troubleshooting | 17 | 分层决策树 | scenario coverage | Beginner | planned |
| D20 | 章节依赖与学习路线 | 00-01 | Curriculum | ART-DEPS | 路线图 | dependency consistency | Beginner | planned |

## 内容覆盖分组

每行是可独立审查的内容单元；详细 planned file 见 `PROJECT_PLAN.md` 第 7 节。

| ID | 内容单元 | planned path | owner | reviewer | 状态 |
|---|---|---|---|---|---|
| M00-01 | 使用方式、学习路线、能力范围和诚实状态 | 00-01/02 | Curriculum/Editor | Beginner + Technical | planned |
| M00-02 | 准备度检查、三平台环境冒烟和补救分流 | 00-03/04 | Foundations | Beginner + Code Verification | planned |
| M00-03 | 密钥、输入、知识文本、权限和隐私安全基线 | 00-05 | Security | Technical Reviewer（非作者） | planned |
| M01-01 | AI、机器学习、深度学习、LLM、Transformer 直觉 | 01-01 | Foundations | Beginner/Technical | planned |
| M01-02 | Token、上下文窗口、Prompt | 01-02 | Foundations | Beginner | planned |
| M01-03 | JSON、HTTP、API | 01-03 | Foundations | Code/Beginner | planned |
| M01-04 | Python、虚拟环境、包管理、命令行、Git | 01-04；appendices 03/04 | Foundations | Beginner | planned |
| M01-05 | 本地/云端模型；RAG 与微调、长上下文、工具调用 | 01-05 | Foundations/Theory | Technical | planned |
| M02-01 | RAG 定义、问题、参数化/外部知识、两阶段和完整流程 | 02-01/02/03 | Theory | Technical | planned |
| M02-02 | 降低但不消除幻觉、适用/不适用、失败模式 | 02-04/05 | Theory | Technical/Beginner | planned |
| M03-01 | Loader/Parser 与 PDF、Markdown、HTML、Office、图片、OCR | 03-01/02/03 | Data | Technical/Code | planned |
| M03-02 | 表格、结构、清洗、编码、页眉页脚、去重 | 03-04/05 | Data | Technical | planned |
| M03-03 | 元数据、权限、版本、增量、删除、撤回、生命周期 | 03-06/07 | Data/Security | Technical + Code Verification（非作者） | planned |
| M04-01 | 固定/重叠/句子/段落/标题/递归切分 | 04-01/02 | Data | Code/Beginner | planned |
| M04-02 | 语义、Parent-Child、Small-to-Big 及特殊内容切分 | 04-03/04 | Data | Technical | planned |
| M04-03 | Chunk 大小/Overlap/元数据/质量影响/实验 | 04-05/06 | Data/Evaluation | Technical | planned |
| M05-01 | Embedding、向量空间、相似度、归一化 | 05-01/02 | Embedding | Technical/Code | planned |
| M05-02 | 文本/图片/多模态、通用/领域/多语言模型和选型 | 05-03/04 | Embedding | Technical | planned |
| M05-03 | 维度、性能、成本、迁移、重索引和错误 | 05-05/06 | Embedding/Production | Technical | planned |
| M06-01 | Flat/ANN/HNSW/IVF/PQ | 06-01/02/03 | Index | Technical | planned |
| M06-02 | 构建/更新/Metadata Index/FAISS/存储边界/选型 | 06-04/05 | Index | Technical/Code | planned |
| M06-03 | Sharding/Replication/Backup/一致性 | 06-06 | Index/Production | Technical | planned |
| M07-01 | Keyword/TF-IDF/BM25/Sparse/Dense/Hybrid | 07-01/02 | Retrieval | Technical/Code | planned |
| M07-02 | Metadata/时间/权限过滤 | 07-03 | Retrieval/Security | Technical + Code Verification（非作者） | planned |
| M07-03 | Rewrite/Expansion/Multi-Query/Decomposition/HyDE | 07-04/05 | Retrieval | Technical | planned |
| M07-04 | Parent/Multi-Vector/Contextual/Self-Query/路由/诊断 | 07-06/07/08 | Retrieval | Technical | planned |
| M08-01 | Bi/Cross Encoder、LLM Rerank、Score Fusion、RRF | 08-01/02/03 | Retrieval | Technical | planned |
| M08-02 | 多路/两阶段/多阶段、Top-K、Recall/Precision、延迟/成本/评估 | 08-04/05 | Retrieval/Evaluation | Technical | planned |
| M09-01 | 选择/去重/排序/压缩/Token Budget/Lost in the Middle | 09-01/02 | Generation | Technical | planned |
| M09-02 | 冲突/过期/来源信任/引用/Grounded | 09-03/04 | Generation | Technical | planned |
| M09-03 | 无答案/拒答/结构化输出/多轮/历史压缩 | 09-05/06 | Generation | Technical/Beginner | planned |
| M09-04 | Prompt Injection 与知识/系统指令隔离 | 09-07 | Generation/Security | Technical Reviewer（非作者） | planned |
| M10-01 | 七个基础项目的目标、架构、目录、安装、配置、代码、启动、输入、输出、测试、错误和扩展 | 10-01 至 10-07；BASIC-01 至 BASIC-07 | Implementation | Code + Beginner + Technical | planned |
| M11-01 | 原生 Python、LangChain 类、LlamaIndex 类和代表性编排对照 | 11-01/02/03/04 | Framework | Technical/Code | planned |
| M11-02 | 封装、优劣、复杂性、不用框架、避免锁定、版本/日期/官方源 | 11-05 | Framework | Technical | planned |
| M12-01 | Golden 数据结构与 Retrieval/Generation/E2E 评估 | 12-01 | Evaluation | Technical | planned |
| M12-02 | Recall/Precision/Hit/MRR/MAP/NDCG | 12-02 | Evaluation | Technical/Code | planned |
| M12-03 | Faithfulness/Answer Relevance/Context Relevance/Precision/Recall | 12-03/04 | Evaluation | Technical | planned |
| M12-04 | LLM Judge、人工、标准、错误、回归、在线、反馈、A/B | 12-05/06/07 | Evaluation | Technical | planned |
| M13-01 | Routing/Adaptive/Self/Corrective/Iterative/Recursive | 13-02/03 | Advanced | Technical | planned |
| M13-02 | Agentic/Tool/Multi-Agent/Multi-knowledge routing | 13-04/09 | Advanced | Technical/Security | planned |
| M13-03 | Graph/Knowledge Graph/SQL/多模态/多语言 | 13-05/06/07/08 | Advanced | Technical | planned |
| M13-04 | 长上下文/Memory/Federated/CAG 与六维成熟度 | 13-01/08/09 | Advanced | Technical | planned |
| M14-01 | Injection/间接注入/投毒/恶意文档/供应链 | 14-01/02/03 | Security | Technical + Code Verification（非作者） | planned |
| M14-02 | 越权/租户/PII/敏感信息/权限继承/审核/驻留/合规 | 14-04/05 | Security | Technical + Code Verification（非作者） | planned |
| M14-03 | 引用真实性/审计/删除/撤回/威胁建模/Red Team | 14-01/06/07 | Security | Technical + Code Verification（非作者） | planned |
| M15-01 | API/同步异步/Batch/队列/缓存/Streaming/并发/限流 | 15-01/02/03 | Production | Code/Security | planned |
| M15-02 | 重试/熔断/超时/日志/Metrics/Tracing/告警 | 15-04/05 | Production | Code | planned |
| M15-03 | Token/Embedding/存储成本、延迟、优化、容量 | 15-06 | Production | Technical | planned |
| M15-04 | 四类版本、灰度、A/B、Docker/Compose、CI/CD、云/本地 | 15-07/08 | Production | Code/Technical | planned |
| M15-05 | 高可用、Backup、灾难恢复 | 15-09 | Production | Technical | planned |
| M16-01 | 企业内部知识库助手全部硬性能力 | 16-01/02/03；CAP-01 | Capstone Team | Review Board（非作者） | planned |
| M16-02 | 垂直领域数据、风险、追溯、评估和人工复核全部硬性能力 | 16-01/04/05；CAP-02 | Capstone Team | Review Board（非作者） | planned |
| M17-01 | 无法检索到正确内容 | 17-01 | Troubleshooting | Technical/Beginner | planned |
| M17-02 | 检索结果相关但不完整 | 17-01 | Troubleshooting | Technical/Beginner | planned |
| M17-03 | 检索正确但回答错误 | 17-02 | Troubleshooting | Technical/Beginner | planned |
| M17-04 | 答案与引用不一致 | 17-02 | Troubleshooting | Technical/Beginner | planned |
| M17-05 | 回答没有引用 | 17-02 | Troubleshooting | Technical/Beginner | planned |
| M17-06 | Chunk 太小 | 17-01 | Troubleshooting | Technical/Beginner | planned |
| M17-07 | Chunk 太大 | 17-01 | Troubleshooting | Technical/Beginner | planned |
| M17-08 | Chunk 重复 | 17-01 | Troubleshooting | Technical/Beginner | planned |
| M17-09 | 上下文冲突 | 17-02 | Troubleshooting | Technical/Beginner | planned |
| M17-10 | Embedding 不适合领域 | 17-01 | Troubleshooting | Technical/Beginner | planned |
| M17-11 | Metadata 过滤错误 | 17-01 | Troubleshooting | Technical/Beginner | planned |
| M17-12 | Reranker 效果差 | 17-01 | Troubleshooting | Technical/Beginner | planned |
| M17-13 | Top-K 不合理 | 17-01 | Troubleshooting | Technical/Beginner | planned |
| M17-14 | 延迟过高 | 17-04 | Troubleshooting | Technical/Beginner | planned |
| M17-15 | Token 成本过高 | 17-04 | Troubleshooting | Technical/Beginner | planned |
| M17-16 | 索引更新不及时 | 17-03 | Troubleshooting | Technical/Beginner | planned |
| M17-17 | 删除文档仍被检索 | 17-03 | Troubleshooting | Technical/Security | planned |
| M17-18 | 多租户数据泄漏 | 17-05 | Troubleshooting/Security | Technical + Code Verification（非作者） | planned |
| M17-19 | 评估指标好但实际体验差 | 17-06 | Troubleshooting/Evaluation | Technical/Beginner | planned |
| M17-20 | 本地效果好但生产环境效果差 | 17-04 | Troubleshooting/Production | Technical/Beginner | planned |
| APP-01 | 术语、数学、Python、Git/CLI、环境变量、配置、API 抽象 | appendices 01-07 | Foundations/Implementation | Beginner | planned |
| APP-02 | 错误、选型、项目评审、论文/官方源、路线图、版本来源 | appendices 08-13 | Editor/Technical | Technical | planned |

## 横切约束

| ID | 约束 | planned path | evidence | reviewer | 状态 |
|---|---|---|---|---|---|
| X-CAP-01 | 真实记录多 Agent/模型/xhigh/文件/Python/测试/Mermaid/资料能力 | reports/capability-audit.md；reports/runtime-evidence.md | runtime audit | Editorial | verified |
| X-SOURCE-01 | 可变事实有版本、日期和一手来源 | SOURCE_REGISTER.md | source rows | Technical | reviewing |
| X-EARLY-EVAL-01 | 试点和早期实验使用最小测量纪律 | 01-06；pilot；04/07/08 | pilot unit/smoke + report；后续章节仍 planned | Technical | reviewing |
| X-EARLY-SEC-01 | 安全基线早于摄取和项目 | 00-05；03/07/09/10 | security checks | Security | planned |
| X-MATH-01 | 正文最低数学+附录深化，无隐藏循环 | 05/06/12；appendix 02 | dependency audit | Beginner | planned |
| X-ADV-01 | Advanced RAG 六维标签和术语消歧 | 13-01；STYLE_GUIDE | method matrix | Technical | planned |
| X-PERM-01 | 权限贯穿摄取、索引、检索、缓存、重排、引用、日志和删除 | 03/07/09/14/15；tests/security | security tests | Technical + Code Verification（非作者） | planned |
| X-WITHDRAW-01 | 撤回覆盖源、Chunk、索引、缓存、队列、副本、备份和审计 | 03/14/15/17 | deletion tests | Technical + Code Verification（非作者） | planned |
| X-DATA-01 | 示例数据来源、许可、PII、可再分发 | DATA_LICENSES.md；data | data audit | Editorial + Technical（非作者） | planned |
| X-SUPPLY-01 | 解析器、依赖、模型和第三方资产供应链边界 | THIRD_PARTY_NOTICES.md；03/14 | dependency audit | Technical Reviewer（非作者） | planned |
| X-PLATFORM-01 | Windows PowerShell 与 macOS/Linux 可复现 | 00-04；appendix 04；各 README | command smoke | Beginner/Code | planned |
| X-EXTERNAL-01 | 云、HA/DR、A/B 和外部性能区分模拟与真实验证 | 15；reports/known-limitations.md | evidence level audit | Technical | planned |
