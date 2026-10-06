# RAG 零基础系统教程项目计划

> 状态：课程蓝图与共享规范已完成四轮独立技术、初学者/编辑和证据审查；最终对 commit `710d644` 的三 lane re-review 全部 PASS，B0 已 verified。本文不是教程正文。
>
> 范围：只完成课程设计、文件级目录、学习路径、依赖、代码与图表任务、覆盖矩阵和试点计划；不批量撰写章节。
>
> 权威输入：仓库内 `SPECIFICATION.md`、课程架构 Agent 产物，以及 2026-07-17 完成的独立技术、初学者/编辑和证据审查。`.omx/context/` 只保留编排上下文，不再是规格真源。

## 1. 设计结论

1. 保留 17 个主部分与附录，但把“共享规范、代码核心、验证报告”提升为跨章节基础设施，避免每个项目复制一套接口。
2. 教学顺序坚持“直觉与最低前置 → 底层可运行实现 → 数据与检索工程 → 生成与引用 → 评估 → 框架 → 高级架构 → 安全与生产 → 综合项目与故障诊断”。
3. 框架章节不得早于底层最小实现；高级 RAG 不得早于检索、生成和评估；生产章节不得早于安全、评估和至少一个完整项目。
4. 代码采用三层：教学最小实现、可复用模块化核心、生产化扩展。外部模型、向量库和框架都通过适配器接入。
5. 每个主目录必须有 README.md；每章完成后必须产生 `summaries/chapters/<chapter-id>.md`，正式文件登记到 CONTENT_MANIFEST.md。
6. Mermaid 当前只允许标记为“静态检查”或“待渲染验证”；发现真实渲染器后才能升级验证状态。
7. Advanced RAG 使用成熟度标签，禁止把论文概念、特定场景模式和广泛工程实践混为一类。
8. 本蓝图建议由 Leader 集成到 PROJECT_PLAN.md；共享规范、正式章节和代码仍应按“蓝图评审 → 规范 → 试点 → 批次生产”的门禁创建。

第 8 项在本文件发布时已完成。后续状态以 `PROGRESS.md` 与
`CONTENT_MANIFEST.md` 为准。

### 1.1 独立审查后的强制修正

| 修正项 | 决策 | 证据位置 |
|---|---|---|
| 原子需求追踪 | 新增 `ACCEPTANCE_MATRIX.md`，所有章节、项目、图表和最终验收使用稳定 ID，Manifest 必须反向引用 | `ACCEPTANCE_MATRIX.md`、`QUALITY_CHECKLIST.md` |
| 能力证据 | 能力结论与运行证据分离；模型、推理强度、测试、Mermaid 分别记录 | `reports/capability-audit.md` |
| 资料与版本 | 根级 `SOURCE_REGISTER.md` 为可变事实的证据账本，章节仍需就近引用 | `SOURCE_REGISTER.md` |
| 审查证据 | 技术、代码、初学者、编辑、图表、链接和最终验收使用独立报告 | `reports/README.md` |
| 零基础入口 | 增加准备度检查、跨平台环境冒烟、安全基线和“先试跑、后拆解”双阶段 | 00-preface 计划、`DEPENDENCY_MATRIX.md` |
| 早期评估与安全 | 第 12、14 部分保留完整理论，但从试点开始建立最小评估和安全默认值 | 00、01、03、07、09、10 的任务 |
| 数学前置 | 正文就地解释最低数学，附录负责推导和补救，不以“概念预告”形成循环 | `DEPENDENCY_MATRIX.md` |
| Advanced RAG | 改用来源、成熟度、适用场景、证据、复杂度和安全风险六维标签；主线默认选修 | 13-01、`STYLE_GUIDE.md` |
| 依赖真源 | `pyproject.toml` 是 Python 依赖唯一真源；requirements 文件仅作导出或场景安装入口 | `CODE_CONVENTIONS.md` |
| 数据许可 | 示例语料必须记录来源、许可、PII 状态和可再分发性 | `DATA_LICENSES.md`、`THIRD_PARTY_NOTICES.md` |

## 2. 当前能力与约束审计

| 能力 | 当前证据 | 规划结论 |
|---|---|---|
| 独立多 Agent | OMX tmux 团队已有 worker-1、worker-2、worker-3 与 leader-fixed | 可执行真实并行分工；Worker 1 不冒充其他审查角色 |
| 指定模型 | 当前 Worker 元数据解析为 gpt-5.6-sol；OMX_TEAM_WORKER_LAUNCH_ARGS 在本进程为空 | 可陈述当前模型元数据；xhigh 启动证据必须由 Leader 的运行时审计保留，本报告不伪造 |
| 原生子 Agent | 当前原生 spawn 表面不能选择或证明模型与推理强度 | 不使用原生子 Agent替代规定的 OMX worker；并行审查由 worker-2 与 worker-3 提供 |
| 文件与 Git | 当前工作树可写，Git 2.50.1 | 可创建和提交规划输入 |
| Python | Python 3.13.3；教程目标为 Python 3.11+ | 可运行作者侧检查；教程代码必须保持 3.11+ 兼容 |
| 测试 | pytest 9.0.3 可用 | 试点与后续代码可执行 pytest；规划 Markdown 本身采用结构检查 |
| Mermaid | mmdc 未安装 | 仅做静态语法检查，不声称渲染通过 |
| 官方资料 | 当前网络不稳定；2026-07-17 复核为 HTTP 000/解析或 SSL 失败 | 写作时逐项检索；失败时不得凭记忆补造版本敏感事实，证据见 reports/runtime-evidence.md |
| 新依赖 | 用户禁止未经批准增加依赖 | 本阶段不增加项目依赖；作者侧临时工具必须单独报告 |

## 3. 分阶段学习路径与通关条件

| 阶段 | 读者路径 | 通关证据 |
|---|---|---|
| L0 准备 | 00 → 01 | 能解释 LLM、Token、上下文、API、Python 环境，并区分 RAG、微调、长上下文、工具调用 |
| L1 建立 RAG 心智模型 | 02 → 试点最小 RAG | 能手画 Indexing/Query 流程并运行无付费 API 的最小示例 |
| L2 建立知识库 | 03 → 04 → 05 → 06 | 能把多格式输入转成带元数据的 Chunk，并说明 Embedding 与索引取舍 |
| L3 提升检索与回答质量 | 07 → 08 → 09 | 能实现稀疏、稠密、混合、重排、上下文构建、引用和拒答 |
| L4 工程比较与评估 | 10 → 12 → 11 | 先完成项目与评估，再比较框架；能用数据而非直觉判断改动 |
| L5 安全与生产，含高级选修 | 14 → 15；13 按需选修 | 能完成威胁建模并设计可观测、可回滚的服务；选修读者还能区分高级方法成熟度 |
| L6 综合交付 | 16 → 17 | 能完成两个端到端项目，并用“症状—原因—诊断—解决方案”闭环排障 |

通关原则：

- 未通过上一阶段的“读者可操作证据”，不得只靠阅读跳到后续阶段。
- 每个阶段至少包含一次可运行任务、一次自测或设计题、一次失败路径练习。
- 附录按需旁路，不作为强制串行章节，但首次出现的基础缺口必须链接到对应附录。

## 4. 预计仓库结构

    rag-beginner-tutorial/
    ├── README.md
    ├── PROJECT_PLAN.md
    ├── ACCEPTANCE_MATRIX.md
    ├── CONTENT_MANIFEST.md
    ├── STYLE_GUIDE.md
    ├── GLOSSARY.md
    ├── CODE_CONVENTIONS.md
    ├── DIAGRAM_CONVENTIONS.md
    ├── DEPENDENCY_MATRIX.md
    ├── QUALITY_CHECKLIST.md
    ├── PROGRESS.md
    ├── SOURCE_REGISTER.md
    ├── DATA_LICENSES.md
    ├── THIRD_PARTY_NOTICES.md
    ├── pyproject.toml
    ├── .env.example
    ├── LICENSE
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
    ├── src/rag_tutorial_core/
    │   ├── documents.py
    │   ├── chunking.py
    │   ├── embeddings.py
    │   ├── similarity.py
    │   ├── vector_store.py
    │   ├── sparse_retrieval.py
    │   ├── retrieval.py
    │   ├── reranking.py
    │   ├── context.py
    │   ├── prompting.py
    │   ├── citations.py
    │   ├── evaluation.py
    │   ├── permissions.py
    │   ├── observability.py
    │   └── adapters/
    ├── examples/
    │   ├── minimal-rag/
    │   ├── local-vector-rag/
    │   ├── pdf-rag/
    │   ├── citation-rag/
    │   ├── hybrid-rag/
    │   ├── reranking-rag/
    │   ├── api-ui-rag/
    │   └── evaluated-rag/
    ├── capstones/
    │   ├── enterprise-knowledge-assistant/
    │   └── domain-rag-system/
    ├── assets/diagrams/
    ├── data/
    │   ├── README.md
    │   └── sample-corpus/
    ├── tests/
    │   ├── unit/
    │   ├── integration/
    │   ├── smoke/
    │   ├── security/
    │   └── fixtures/
    ├── scripts/
    │   ├── check-links.py
    │   ├── check-manifest.py
    │   ├── check-mermaid.py
    │   ├── check-source-register.py
    │   └── run-smoke-tests.py
    ├── reports/
    │   ├── README.md
    │   ├── capability-audit.md
    │   ├── test-report.md
    │   ├── technical-review.md
    │   ├── code-verification.md
    │   ├── beginner-review.md
    │   ├── editorial-review.md
    │   ├── diagram-validation.md
    │   ├── link-check.md
    │   ├── acceptance-evidence.md
    │   ├── known-limitations.md
    │   └── final-quality-report.md
    ├── summaries/
    │   ├── README.md
    │   └── chapters/
    └── requirements/
        ├── base.txt
        ├── dev.txt
        └── optional.txt

目录规则：

- docs 下每个目录包含 README.md；每章的增量摘要统一放在 `summaries/chapters/<chapter-id>.md`，避免一个目录内多章共用一个含义不清的 summary。
- 每个 examples 与 capstones 子项目包含 README.md、src 或 app 目录、tests、配置示例和运行状态说明。
- src/rag_tutorial_core 只放依赖较轻的领域接口与教学实现；框架对象不得渗透核心领域层。
- 版本敏感依赖集中在 optional.txt 或对应项目 extra，不强迫所有读者安装。
- `pyproject.toml` 是依赖声明真源；`requirements/*.txt` 必须标明由何种 extra 导出，不能维护第二套版本约束。
- 每个命令块标注 shell；Windows PowerShell 与 macOS/Linux 差异必须就近说明或链接到附录。
- 命名规范的明确例外：Markdown、目录、资源和可执行脚本使用小写英文与连字符；Python 可导入包和模块遵循语言约束使用 snake_case。CODE_CONVENTIONS.md 必须记录该例外，避免产生不可正常 import 的模块名。

## 5. 共享规范与协作架构

| 文件 | 必含内容 | 主要维护角色 |
|---|---|---|
| PROJECT_PLAN.md | 阶段、批次、职责、风险、门禁、验收矩阵 | Leader + Curriculum Architect |
| CONTENT_MANIFEST.md | 路径、章节、类型、负责人、状态、依赖、图、代码、验证、四类审查 | Managing Editor |
| STYLE_GUIDE.md | 中文风格、术语首次定义、事实/经验/建议/推测标签、章节类型模板 | Managing Editor + Beginner Experience |
| GLOSSARY.md | 中英术语、缩写、首次出现、禁用表述、同义词 | Foundations + Technical Reviewer |
| CODE_CONVENTIONS.md | Python 3.11+、类型、异常、日志、接口、配置、测试、Mock | Implementation + Code Verification |
| DIAGRAM_CONVENTIONS.md | Mermaid 子集、标题、教学问题、阅读说明、静态/渲染状态 | Managing Editor |
| DEPENDENCY_MATRIX.md | 章节前置、代码接口、资料版本、跨章术语 | Curriculum Architect |
| QUALITY_CHECKLIST.md | 技术、教学、代码、编辑四门禁 | 四类独立审查角色 |
| PROGRESS.md | 批次状态、阻塞、验证、下一步 | Leader |
| ACCEPTANCE_MATRIX.md | 原子 requirement_id、负责人、依赖、证据、验证方法、审查者和状态 | Leader + 四类 Reviewer |
| SOURCE_REGISTER.md | 可变事实、版本、核查日期、官方来源、证据等级和复核日期 | Technical Reviewer |
| DATA_LICENSES.md | 示例数据来源、许可、PII、再分发与删除要求 | Data + Security |

后续专业角色边界：

- Foundations 只负责零基础前置，不重复完整 RAG 原理。
- Theory 定义核心心智模型；Data、Retrieval、Generation 章节引用它而不重讲。
- Implementation 提供统一接口；框架章节只实现 adapters。
- Evaluation 在每个项目中提供测试契约，不等到第 12 部分才首次出现“如何验证”。
- Security 参与数据摄取、检索过滤、上下文隔离和生产部署的跨章审查。
- Technical、Code、Beginner、Editorial Reviewer 必须独立于章节作者。

### 5.1 多 Agent 职责与交接

所有参与正文生产、代码实现、技术审查和质量检查的 OMX worker 使用
`gpt-5.6-sol` 与 `xhigh`。如果后续运行时不能证明这两项，必须暂停该 lane 或明确
使用角色模拟，不能伪造模型证据。

| 角色 | 独占职责 | 主要产物 | 不能替代的审查 |
|---|---|---|---|
| Curriculum Architect | 目录、路线、依赖、难度与覆盖 | PROJECT_PLAN、DEPENDENCY_MATRIX | 不能自批课程结构 |
| Foundations | AI/ML/LLM 与最低 Python/API 前置 | 00、01、基础附录 | 技术与初学者审查 |
| RAG Theory | RAG 原理、两阶段、边界与失败模式 | 02 | 技术审查 |
| Data Pipeline | 多格式解析、清洗、元数据、版本和撤回 | 03、数据 fixture | 代码与安全审查 |
| Retrieval Engineering | 稀疏/稠密/混合、查询变换、重排 | 07、08、检索示例 | 技术与评估审查 |
| Generation and Prompting | 上下文、引用、拒答、结构化输出和注入隔离 | 09、生成示例 | 技术与安全审查 |
| Implementation | 核心接口、最小/模块化/生产代码、配置 | src、examples、capstones | Code Verification |
| Evaluation | 测试集、指标、Judge、人工与在线评估 | 12、evaluation fixtures | 技术审查 |
| Advanced RAG | 高级方法、术语消歧和六维成熟度 | 13 | Technical Reviewer |
| Production Engineering | API、队列、缓存、可观测、部署与恢复 | 15、部署工件 | Code/Security Verification |
| Security and Governance | 威胁、权限、PII、审计、供应链和 Red Team | 14、安全测试 | 独立技术复核 |
| Technical Reviewer | 事实、算法、术语、版本、来源和跨章一致性 | technical-review | 不写被审章节结论 |
| Code Verification | 导入、依赖、运行、边界、单元/集成/冒烟证据 | code-verification、test-report | 不代替教学审查 |
| Beginner Experience | 未解释术语、难度跳跃、复现和练习有效性 | beginner-review | 不代替技术审查 |
| Managing Editor | 术语、重复、Markdown、导航、Manifest 和出版校对 | editorial-review、Manifest | 不作为作者唯一 reviewer |

交接使用文件而非复制全文：章节任务说明、学习目标、必要前置摘要、术语增量、代码
接口和相关文件清单。作者完成后写 `summaries/chapters/<chapter-id>.md`，四类 reviewer
各自记录发现、修复和复核证据。

### 5.2 生产批次

| 批次 | 范围 | 硬门禁 |
|---|---|---|
| B0 | 蓝图、共享规范和证据账本 | 本计划与九个共享文件 verified |
| B1 | README、00 的准备度/环境/安全、01 的最低术语、02-01、minimal-rag 试点 | 三平台走查、四类独立审查、unit/smoke、D01 诚实状态 |
| B2 | 01 其余基础与补救附录 | 零基础主线与补救路线完整 |
| B3 | 02 其余、03、04 | 数据许可、安全基线、单变量实验 |
| B4 | 05、06 | 数值边界、Flat 基线、索引权衡 |
| B5 | 07、08、09 | 检索评估、引用一致性、权限与注入隔离 |
| B6 | 七个基础项目、12、11 | 项目测试先于框架对照结论 |
| B7 | 13、14、15 | 来源复核、安全回归、生产模拟边界 |
| B8 | 两个 capstone、16、17 | e2e、安全、评估、部署和人工复核 |
| B9 | 附录、全局集成和最终报告 | 所有 AC 与 requirement-id 有当前证据 |

## 6. 主依赖图

    00 --> 01 --> 02 --> pilot
    02 --> 03 --> 04 --> 05 --> 06 --> 07 --> 08 --> 09 --> 10
    10 --> 12
    10 --> 11
    12 --> 11
    07 --> 13
    09 --> 13
    12 --> 13
    03 --> 14
    07 --> 14
    09 --> 14
    12 --> 14
    10 --> 15
    12 --> 15
    14 --> 15
    11 --> 16
    12 --> 16
    14 --> 16
    15 --> 16
    13 -.按项目选用.-> 16
    03 --> 17
    04 --> 17
    05 --> 17
    06 --> 17
    07 --> 17
    08 --> 17
    09 --> 17
    12 --> 17
    14 --> 17
    15 --> 17
    appendices -.按需补充.-> 01
    appendices -.按需补充.-> 16

关键依赖决策：

- 12-evaluation 放在 11-frameworks 的完整比较之前，防止框架比较沦为 API 展示；目录编号仍保留用户要求，学习路线明确建议 10 → 12 → 11。
- 14-security 独立于 13-advanced；它横切 03、07、09、12，并成为 15-production 与 16-capstones 的硬门禁。
- 17-troubleshooting 是综合回看，不是新知识堆放区；每个诊断必须链接到真正负责原理的主章节。
- 13-advanced-rag 是默认选修支线，不是安全、生产和两个综合项目的统一硬前置；只有明确采用高级模式的项目才建立依赖。
- 试点中的 `minimal-rag` 是直觉试跑；10-01 是完成 04 至 09 后的完整回访。同一路径分两个教学层次，不构成循环。

## 7. 文件级课程、目标、依赖、代码和图表任务

记号：

- “无”表示本章不需要新增可执行代码，但可有短伪代码或命令。
- Dxx 对应第 9 节图表登记表。
- 每个目录还需要 README.md；每章摘要统一登记到 `summaries/chapters/`，本表只列教学文件。

### 00-preface

| 文件 | 学习目标与主要知识 | 前置 | 代码任务 | 图表 |
|---|---|---|---|---|
| docs/00-preface/01-how-to-use-this-tutorial.md | 理解学习路线、通关证据、环境路线、本地/云端替代、验证状态 | 无 | scripts/run-smoke-tests.py 的使用说明 | D20 |
| docs/00-preface/02-capabilities-scope-and-honesty.md | 理解能力边界、资料等级、版本核查、成熟度标签、禁止夸大 | 无 | 无 | 无 |
| docs/00-preface/03-readiness-check.md | 判断 Python、命令行、HTTP/JSON 和数学缺口，并进入对应补救路线 | 无 | 无付费自检命令 | 准备度分流图 |
| docs/00-preface/04-environment-smoke-test.md | 在 Windows PowerShell、macOS 和 Linux 上完成 Python 3.11+ 环境与最小测试 | 00-03 | scripts/run-smoke-tests.py | 环境验证流程 |
| docs/00-preface/05-security-baseline.md | 建立密钥、输入、知识库文本、权限、隐私和外部服务的最低安全默认值 | 无 | 安全配置自检 | 信任边界简图 |

### 01-foundations

| 文件 | 学习目标与主要知识 | 前置 | 代码任务 | 图表 |
|---|---|---|---|---|
| docs/01-foundations/01-ai-ml-dl-llm-transformer.md | 建立 AI、ML、DL、LLM 和 Transformer 的直觉关系 | 00 | 无 | 简化 Transformer 信息流 |
| docs/01-foundations/02-tokens-context-and-prompts.md | 理解 Token、上下文窗口、Prompt 与限制 | 01-01 | scripts/count-tokens-demo.py，允许 Mock tokenizer | Token 与上下文预算示意 |
| docs/01-foundations/03-json-http-and-apis.md | 能读写 JSON，理解 HTTP 请求、API、状态码和超时 | 01-02 | examples/http-json-demo/，本地 Mock 服务 | API 请求时序 |
| docs/01-foundations/04-python-environments-cli-and-git.md | 完成 Python、虚拟环境、包管理、命令行、Git 最低前置 | 00 | examples/python-basics/ 与最小 pytest | 环境与项目目录关系 |
| docs/01-foundations/05-rag-neighbors-and-model-options.md | 区分本地/云端模型，RAG/微调/长上下文/工具调用 | 01-01 | 选型决策函数伪代码 | 技术选择决策树 |
| docs/01-foundations/06-minimum-measurement-discipline.md | 直观理解固定语料、查询、相关性标签、Hit/Recall@K、延迟和成本记录 | 01-04、02-03 | 最小离线评估 fixture | 最小实验闭环 |

### 02-rag-principles

| 文件 | 学习目标与主要知识 | 前置 | 代码任务 | 图表 |
|---|---|---|---|---|
| docs/02-rag-principles/01-what-is-rag.md | 定义 RAG、解决的问题、为什么只能降低而不能消除幻觉 | 01 | examples/minimal-rag 的概念性入口 | D01 |
| docs/02-rag-principles/02-parametric-and-external-knowledge.md | 区分参数化与外部知识，理解新鲜度、可追溯性与边界 | 02-01 | 无 | 知识来源对比 |
| docs/02-rag-principles/03-indexing-and-query-stages.md | 理解 Indexing、Query 两阶段与完整请求流 | 02-01 | 流程对象的最小数据类 | D02、D03 |
| docs/02-rag-principles/04-use-cases-and-non-use-cases.md | 按业务约束判断适用与不适用场景 | 02-02 | 场景选择练习 | 适用性决策树 |
| docs/02-rag-principles/05-failure-modes-and-boundaries.md | 识别检索、上下文、生成、数据、安全失败模式 | 02-03 | 失败注入测试设计 | 失败链路图 |

### 03-data-ingestion

| 文件 | 学习目标与主要知识 | 前置 | 代码任务 | 图表 |
|---|---|---|---|---|
| docs/03-data-ingestion/01-document-model-loaders-and-parsers.md | 从零实现 Document，区分 Loader 与 Parser | 02 | src/rag_tutorial_core/documents.py + 单测 | D04 |
| docs/03-data-ingestion/02-pdf-ocr-images-and-untrusted-files.md | 理解 PDF 文本层、扫描件、OCR、图片、恶意文件、资源限制和失败边界 | 03-01、00-05 | examples/pdf-rag/ingest.py，OCR 为可选适配器 | PDF/OCR 分流 |
| docs/03-data-ingestion/03-markdown-html-and-office.md | 处理 Markdown、HTML、Word、Excel、PowerPoint | 03-01 | 各格式 fixture 与适配器契约测试 | 格式适配器图 |
| docs/03-data-ingestion/04-tables-layout-and-structure.md | 保留标题、页码、表格、布局与结构语义 | 03-02、03-03 | 表格与层级节点中间表示 | 表格提取与回退 |
| docs/03-data-ingestion/05-cleaning-encoding-and-deduplication.md | 处理编码、乱码、页眉页脚、清洗、规范化和去重 | 03-01 | cleaning.py 与重复检测边界测试 | 清洗管线 |
| docs/03-data-ingestion/06-metadata-permissions-and-provenance.md | 设计来源、页码、时间、权限、租户和血缘元数据 | 03-04 | permissions.py 的过滤前置契约 | D17 |
| docs/03-data-ingestion/07-versioning-incremental-update-and-deletion.md | 设计文档版本、增量更新、删除、知识撤回和生命周期 | 03-05、03-06 | 增量 diff、墓碑记录和撤回测试 | D16 |

### 04-chunking

| 文件 | 学习目标与主要知识 | 前置 | 代码任务 | 图表 |
|---|---|---|---|---|
| docs/04-chunking/01-fixed-sentence-and-paragraph-chunking.md | 从零实现固定长度、重叠、句子和段落切分 | 03 | src/rag_tutorial_core/chunking.py + 单测 | D05 |
| docs/04-chunking/02-structure-aware-and-recursive-chunking.md | 使用标题层级、结构边界和递归策略 | 04-01、03-04 | 结构递归切分器 | D05 |
| docs/04-chunking/03-semantic-parent-child-and-small-to-big.md | 先用直观相似度理解语义切分，再学习 Parent-Child、Small-to-Big；向量细节后置到 05 | 04-01 | Parent/child ID 映射与 Mock 相似度 | Parent-child 流程 |
| docs/04-chunking/04-table-code-and-conversation-chunking.md | 处理表格、代码和对话的特殊边界 | 04-02 | 三类策略 fixture | 特殊切分对比 |
| docs/04-chunking/05-size-overlap-metadata-and-quality.md | 解释 Chunk 大小、Overlap、元数据对召回与生成的影响 | 04-01 | 参数扫描实验 | 质量权衡曲线 |
| docs/04-chunking/06-designing-chunking-experiments.md | 使用 01-06 的最小测量纪律建立受控实验；完整评估方法留在 12 | 04-05、01-06 | examples/chunking-lab/ | 实验设计图 |

### 05-embeddings

| 文件 | 学习目标与主要知识 | 前置 | 代码任务 | 图表 |
|---|---|---|---|---|
| docs/05-embeddings/01-embedding-and-vector-space-intuition.md | 理解 Embedding、向量空间和语义邻近 | 01、04 | Embedding 接口与确定性 Mock | D06 |
| docs/05-embeddings/02-similarity-metrics-and-normalization.md | 从零实现 Cosine、Dot Product、Euclidean 与归一化 | 05-01 | similarity.py + 数值边界测试 | 距离度量对比 |
| docs/05-embeddings/03-text-model-selection.md | 比较通用、领域、多语言、维度、性能和成本 | 05-01 | 模型能力记录结构，不固化品牌排行 | 选型矩阵 |
| docs/05-embeddings/04-image-and-multimodal-embeddings.md | 理解图片与多模态 Embedding 的输入输出边界 | 05-01 | 可选图像适配器接口 + Mock | 多模态向量路径 |
| docs/05-embeddings/05-batching-caching-and-cost.md | 设计批处理、缓存、吞吐、失败重试和成本记录 | 05-01、15 概念预告 | embedding batcher | 批处理时序 |
| docs/05-embeddings/06-migration-reindexing-and-common-errors.md | 处理模型迁移、维度变化、重新索引和常见错误 | 05-02、03-07 | 版本不匹配与重建索引测试 | 迁移状态图 |

### 06-indexes-vector-databases

| 文件 | 学习目标与主要知识 | 前置 | 代码任务 | 图表 |
|---|---|---|---|---|
| docs/06-indexes-vector-databases/01-flat-and-ann-indexes.md | 理解 Flat、ANN、召回与延迟权衡 | 05 | 从零简单向量存储与 Top-K | 索引选择概览 |
| docs/06-indexes-vector-databases/02-hnsw-intuition.md | 理解 HNSW 分层图直觉、关键参数和限制 | 06-01 | 小规模邻接图实验 | D07 |
| docs/06-indexes-vector-databases/03-ivf-and-product-quantization.md | 理解 IVF、PQ、压缩与精度权衡 | 06-01 | 可复现实验或伪实现 | IVF/PQ 数据流 |
| docs/06-indexes-vector-databases/04-local-faiss-and-metadata-indexes.md | 使用本地索引并组合 Metadata Index | 06-01、03-06 | examples/local-vector-rag/ | 本地索引组件图 |
| docs/06-indexes-vector-databases/05-database-boundaries-and-abstractions.md | 比较向量库、关系库、搜索引擎与抽象接口 | 06-04 | adapters/vector_store.py 契约测试 | 存储边界图 |
| docs/06-indexes-vector-databases/06-sharding-replication-backup-and-consistency.md | 理解 Sharding、Replication、Backup、更新、一致性与选型维度 | 06-05、03-07 | 故障场景设计，不宣称虚构性能 | 分布式拓扑 |

### 07-retrieval

| 文件 | 学习目标与主要知识 | 前置 | 代码任务 | 图表 |
|---|---|---|---|---|
| docs/07-retrieval/01-keyword-tfidf-bm25-and-sparse.md | 从关键词到 TF-IDF、BM25 与 Sparse Retrieval | 04、03 | sparse_retrieval.py + 指标单测 | 稀疏检索流程 |
| docs/07-retrieval/02-dense-and-hybrid-retrieval.md | 比较 Dense 与 Hybrid，理解互补性 | 05、06、07-01 | hybrid-rag 的双路召回 | D08 |
| docs/07-retrieval/03-metadata-time-and-permission-filters.md | 正确执行元数据、时间和权限过滤 | 03-06、07-02 | 过滤前后顺序与越权测试 | D17 |
| docs/07-retrieval/04-query-rewrite-expansion-and-multi-query.md | 实现 Query Rewrite、Expansion、Multi-Query | 07-02 | 查询变换接口与合并测试 | 查询变换管线 |
| docs/07-retrieval/05-query-decomposition-and-hyde.md | 理解 Query Decomposition 与 HyDE 的收益和风险 | 07-04 | 可关闭的策略适配器 + Mock | 分解与 HyDE 对比 |
| docs/07-retrieval/06-parent-multi-vector-and-contextual-retrieval.md | 实现 Parent Document、Multi-Vector、Contextual Retrieval | 04-03、07-02 | 父文档回取与多向量映射 | 多表示检索图 |
| docs/07-retrieval/07-self-query-and-routing.md | 理解 Self-Query、路由检索和多知识源选择 | 07-03、07-04 | 结构化过滤解析器与路由器 | 路由决策图 |
| docs/07-retrieval/08-retrieval-failure-diagnostics.md | 系统诊断无召回、漏召回、误过滤和域偏移 | 07-01 至 07-07、12 概念预告 | 诊断 notebook 或脚本 | 检索诊断树 |

### 08-reranking

| 文件 | 学习目标与主要知识 | 前置 | 代码任务 | 图表 |
|---|---|---|---|---|
| docs/08-reranking/01-why-rerank-bi-encoder-and-cross-encoder.md | 理解为什么重排以及 Bi/Cross Encoder 差异 | 07 | reranker 接口与 Mock | D09 |
| docs/08-reranking/02-llm-reranking.md | 评估 LLM Reranking 的可解释性、延迟、成本和注入风险 | 08-01、09 概念预告 | 结构化打分适配器 | LLM 重排边界 |
| docs/08-reranking/03-score-fusion-and-rrf.md | 实现 Score Fusion 与 Reciprocal Rank Fusion | 07-02、08-01 | RRF 从零实现与单测 | D09 |
| docs/08-reranking/04-multi-stage-top-k-recall-and-precision.md | 设计多路召回、两/多阶段检索、Top-K 与 Recall/Precision 权衡 | 08-03 | reranking-rag 管线 | D09 |
| docs/08-reranking/05-reranker-evaluation-latency-and-cost.md | 用离线指标与延迟成本验证重排器 | 08-04、12-02 | 参数扫描与报告 | 重排评估矩阵 |

### 09-context-generation

| 文件 | 学习目标与主要知识 | 前置 | 代码任务 | 图表 |
|---|---|---|---|---|
| docs/09-context-generation/01-context-selection-deduplication-and-ordering.md | 选择、去重和排序检索上下文 | 08 | context.py + 单测 | D10 |
| docs/09-context-generation/02-compression-token-budget-and-lost-in-the-middle.md | 处理压缩、Token Budget 与 Lost in the Middle | 09-01、01-02 | 预算分配器与截断边界测试 | D10 |
| docs/09-context-generation/03-conflicts-freshness-and-source-trust.md | 处理冲突、过期信息与来源可信度 | 03-06、09-01 | 冲突标记与来源排序策略 | 冲突处理流程 |
| docs/09-context-generation/04-grounded-generation-and-citations.md | 从零实现 Prompt 组装、上下文注入、Grounded Generation 和引用 | 02、09-01 | prompting.py、citations.py + citation-rag | 引用数据流 |
| docs/09-context-generation/05-no-answer-detection-and-refusal.md | 设计无答案检测、拒答、阈值和不确定性表述 | 09-04、12 概念预告 | 拒答策略与负例测试 | 拒答决策树 |
| docs/09-context-generation/06-structured-output-and-conversations.md | 实现结构化输出、多轮历史和历史压缩 | 01-03、09-02 | schema 验证与历史摘要 Mock | 对话状态图 |
| docs/09-context-generation/07-prompt-injection-and-instruction-isolation.md | 隔离知识库文本与系统指令，理解防御不是绝对安全 | 09-04、14 概念预告 | 不可信上下文封装与攻击 fixture | 指令边界图 |

### 10-basic-projects

每个项目文件必须包含目标、架构、目录、安装、配置、完整代码、启动、输入、预期输出、测试、常见错误和扩展。

| 文件 | 项目目标 | 前置 | 代码目录 | 图表 |
|---|---|---|---|---|
| docs/10-basic-projects/01-minimal-python-rag.md | 纯 Python、内存数据、确定性 Mock、从零完成最小 RAG | 02、04、05、06、09 | examples/minimal-rag/ | D01 |
| docs/10-basic-projects/02-local-vector-rag.md | 使用本地向量索引并可重建 | 06-04、10-01 | examples/local-vector-rag/ | 本地组件图 |
| docs/10-basic-projects/03-pdf-knowledge-base.md | 支持 PDF、扫描件回退与页码来源 | 03-02、10-02 | examples/pdf-rag/ | PDF 摄取图 |
| docs/10-basic-projects/04-citation-rag.md | 生成可核对来源引用并检测引用不一致 | 09-04、10-03 | examples/citation-rag/ | 引用链路 |
| docs/10-basic-projects/05-hybrid-rag.md | BM25 + Dense + Fusion | 07-02、08-03 | examples/hybrid-rag/ | D08、D09 |
| docs/10-basic-projects/06-reranking-rag.md | Hybrid 后接 Reranker，并报告质量/延迟变化 | 08 | examples/reranking-rag/ | D09 |
| docs/10-basic-projects/07-api-and-ui-rag.md | 同步 API、简单界面、输入验证、基础超时和错误反馈；Streaming、并发和韧性留到 15 | 10-06 | examples/api-ui-rag/ | 服务时序 |

### 11-frameworks

| 文件 | 学习目标与主要知识 | 前置 | 代码任务 | 图表 |
|---|---|---|---|---|
| docs/11-frameworks/01-what-frameworks-abstract.md | 把框架对象映射回底层 Document、Retriever、Prompt、Generator | 10、12 | 框架映射表与端口接口 | 封装层次图 |
| docs/11-frameworks/02-langchain-case-study.md | 使用统一案例介绍 LangChain 类框架，标注版本、核查日期与官方源 | 11-01 | adapters/langchain_adapter.py + 契约测试 | 调用链映射 |
| docs/11-frameworks/03-llamaindex-case-study.md | 使用同一案例介绍 LlamaIndex 类框架并对照底层 | 11-01 | adapters/llamaindex_adapter.py + 契约测试 | 调用链映射 |
| docs/11-frameworks/04-composition-alternatives.md | 介绍其他代表性编排方式与不用框架的场景 | 11-01 | 轻量函数组合示例 | 方案对比矩阵 |
| docs/11-frameworks/05-portability-versioning-and-lock-in.md | 解释优势、复杂性、API 锁定、适用版本与迁移策略 | 11-02 至 11-04 | 跨适配器契约测试 | 可移植架构 |

### 12-evaluation

| 文件 | 学习目标与主要知识 | 前置 | 代码任务 | 图表 |
|---|---|---|---|---|
| docs/12-evaluation/01-golden-datasets-and-error-taxonomy.md | 构建 Query、Context、Answer、Reference Answer 与错误分类 | 10 | tests/fixtures/golden-dataset.jsonl | D11 |
| docs/12-evaluation/02-retrieval-metrics.md | 从零实现 Recall@K、Precision@K、Hit Rate、MRR、MAP、NDCG | 12-01、07 | evaluation.py + 单测 | 指标选择图 |
| docs/12-evaluation/03-generation-and-context-metrics.md | 理解 Faithfulness、Answer Relevance、Context Relevance/Precision/Recall | 12-01、09 | 可插拔指标接口与确定性样例 | 生成评估链 |
| docs/12-evaluation/04-llm-as-a-judge-and-human-review.md | 设计 Judge 与人工量表，说明偏差、泄漏、成本和复核 | 12-03 | rubric schema 与盲评流程 | Judge 流程 |
| docs/12-evaluation/05-end-to-end-and-regression-testing.md | 建立端到端评估、阈值、回归测试和失败定位 | 12-02 至 12-04 | examples/evaluated-rag/ + pytest | D11 |
| docs/12-evaluation/06-online-evaluation-feedback-and-ab-testing.md | 设计在线指标、用户反馈和 A/B 测试 | 12-05、15 概念预告 | 事件 schema 与分析脚本 | 在线反馈环 |
| docs/12-evaluation/07-evaluation-design-and-reporting.md | 区分官方 Benchmark、自测、经验结论和不可验证部分 | 12 | reports/test-report.md 模板 | 证据等级矩阵 |

### 13-advanced-rag

本部分所有方法使用六维标签：概念来源、采用成熟度、适用场景、证据强度、运行复杂度和安全风险。标签不是互斥类别；正文必须说明术语可能存在多种实现语境。

| 文件 | 学习目标与主要知识 | 前置 | 代码任务 | 图表 |
|---|---|---|---|---|
| docs/13-advanced-rag/01-maturity-map-and-selection.md | 区分广泛采用、特定场景、实验性、学术概念、工程模式 | 12 | 成熟度登记表 | 成熟度地图 |
| docs/13-advanced-rag/02-query-routing-and-adaptive-rag.md | Query Routing、Adaptive RAG、多知识库路由 | 07-07、12 | 路由策略实验 | 自适应路由图 |
| docs/13-advanced-rag/03-self-rag-and-corrective-rag.md | Self-RAG、Corrective RAG 的论文概念与工程近似 | 12、13-01 | 状态机 Mock，不伪造论文复现 | 反思/纠错状态图 |
| docs/13-advanced-rag/04-iterative-recursive-agentic-and-tool-rag.md | Iterative、Recursive、Agentic、Tool-Augmented RAG | 07、09、12 | 有预算和停止条件的循环 | D12 |
| docs/13-advanced-rag/05-graph-rag-and-knowledge-graphs.md | Graph RAG、Knowledge Graph、实体关系与适用边界 | 06、07、12 | 小型图检索 Mock | D13 |
| docs/13-advanced-rag/06-sql-rag.md | SQL RAG、结构化查询、权限和查询安全 | 07-07、14 概念预告 | 只读 SQL 适配器与验证 | SQL RAG 流程 |
| docs/13-advanced-rag/07-multimodal-and-multilingual-rag.md | 多模态与多语言 RAG 的表示、检索和评估 | 03、05、12 | 双语与图文 fixture | D14 |
| docs/13-advanced-rag/08-long-context-memory-and-cache-augmented-generation.md | 长上下文、Memory、Cache-Augmented Generation 与 RAG 边界 | 01、09、12 | 策略对比实验 | 记忆层次图 |
| docs/13-advanced-rag/09-federated-and-multi-agent-rag.md | Federated、多知识库、多 Agent RAG 的路由、隐私和失败模式 | 13-02、14、15 概念预告 | 联邦路由 Mock | 多知识源拓扑 |

建议成熟度初始标签（写作时须用一手资料复核）：

| 类别 | 初始归类 |
|---|---|
| 广泛工程实践 | Hybrid Retrieval、Reranking、Metadata Filtering、Query Routing、引用与拒答 |
| 特定场景方法 | Parent-Child、Multi-Vector、SQL RAG、Graph RAG、多模态、多语言、Federated |
| 工程实现模式 | Agentic、Tool-Augmented、Iterative、Recursive、多知识库、多 Agent RAG |
| 论文或实验性概念 | Self-RAG、Corrective RAG、部分 Adaptive RAG 与 Cache-Augmented Generation 变体 |

### 14-security-governance

| 文件 | 学习目标与主要知识 | 前置 | 代码任务 | 图表 |
|---|---|---|---|---|
| docs/14-security-governance/01-threat-modeling-rag.md | 识别资产、信任边界、攻击面、影响和缓解 | 03、07、09 | threat-model.yaml 示例 | D18 |
| docs/14-security-governance/02-prompt-injection-and-malicious-documents.md | Prompt Injection、间接注入、恶意文档与分层防御 | 09-07、14-01 | 攻击 fixture 与拒绝/隔离测试 | D18 |
| docs/14-security-governance/03-data-poisoning-and-supply-chain.md | 数据投毒、依赖/模型供应链、安全更新 | 03-07、14-01 | 摄取准入与来源校验测试 | 投毒路径图 |
| docs/14-security-governance/04-authorization-tenancy-and-permission-inheritance.md | 防止越权检索、多租户泄漏，正确继承权限 | 03-06、07-03 | permissions.py 安全单测 | D17 |
| docs/14-security-governance/05-pii-moderation-residency-and-compliance.md | PII、敏感信息、内容审核、数据驻留与合规边界 | 14-01 | 脱敏接口与审计事件 | 数据处理边界 |
| docs/14-security-governance/06-audit-citation-deletion-and-knowledge-withdrawal.md | 审计、引用真实性、删除、知识撤回和可追溯性 | 03-07、09-04 | 撤回后不可检索集成测试 | 撤回审计链 |
| docs/14-security-governance/07-red-teaming-and-defense-in-depth.md | 设计 Red Team 场景，说明任何单一措施都不彻底 | 14-02 至 14-06、12 | 安全回归集 | 防御纵深图 |

### 15-production

| 文件 | 学习目标与主要知识 | 前置 | 代码任务 | 图表 |
|---|---|---|---|---|
| docs/15-production/01-api-sync-async-and-streaming.md | FastAPI 或同类 API、同步/异步、Streaming | 10-07、14 | production-rag API | 请求时序 |
| docs/15-production/02-batch-embedding-jobs-and-queues.md | Batch Embedding、异步任务与队列 | 03-07、05-05 | 可恢复任务状态机 | 队列工作流 |
| docs/15-production/03-caching-concurrency-and-rate-limits.md | 缓存、并发、限流与租户配额 | 15-01、14-04 | 缓存键与限流测试 | 并发控制图 |
| docs/15-production/04-retries-circuit-breakers-and-timeouts.md | 重试、熔断、超时、资源释放与幂等 | 15-01、15-02 | 故障注入测试 | 韧性状态图 |
| docs/15-production/05-logging-metrics-tracing-and-alerting.md | 日志、Metrics、Tracing、告警与关联 ID | 15-01、12 | observability.py 与 Mock exporter | 可观测性链路 |
| docs/15-production/06-cost-latency-performance-and-capacity.md | Token/Embedding/存储成本、延迟、优化和容量规划 | 05、06、08、15-05 | 基准脚本，明确硬件与数据 | 成本延迟分解 |
| docs/15-production/07-versioning-rollouts-and-ab-testing.md | 模型、Prompt、Embedding、索引版本；灰度与 A/B | 03-07、05-06、12-06 | 版本清单与回滚测试 | 发布状态图 |
| docs/15-production/08-docker-cicd-cloud-and-local-deployment.md | Docker、Compose、CI/CD、云端与本地部署 | 15-01 至 15-07、14 | Dockerfile、compose、CI 冒烟 | D15 |
| docs/15-production/09-high-availability-backup-and-disaster-recovery.md | 高可用、Backup、灾难恢复、RPO/RTO 取舍 | 06-06、15-08 | 恢复演练脚本与记录模板 | HA/DR 拓扑 |

### 16-capstone-projects

| 文件 | 学习目标与主要知识 | 前置 | 代码任务 | 图表 |
|---|---|---|---|---|
| docs/16-capstone-projects/01-delivery-contract-and-evidence.md | 统一两个项目的范围、接口、测试、审查和证据标准 | 11 至 15 | capstones 共享契约 | 交付证据图 |
| docs/16-capstone-projects/02-enterprise-knowledge-assistant-design.md | 多格式、权限、租户/部门隔离、Hybrid、Rerank、引用、拒答 | 16-01 | capstones/enterprise-knowledge-assistant/ | 企业架构 |
| docs/16-capstone-projects/03-enterprise-knowledge-assistant-operations.md | 评估、API、简单界面、日志监控、Docker 与撤回 | 16-02 | 端到端、安全、恢复测试 | D15、D17 |
| docs/16-capstone-projects/04-domain-rag-system-design.md | 选择一个垂直领域，处理数据质量、术语、权限、评估集 | 16-01 | capstones/domain-rag-system/ | 领域数据流 |
| docs/16-capstone-projects/05-domain-risk-human-review-and-traceability.md | 风险、引用、拒答、可追溯、错误成本、人工复核；不替代专业决策 | 16-04、14 | 人工复核队列与审计测试 | 人工复核闭环 |

### 17-troubleshooting

所有文件统一使用“症状—可能原因—最小诊断—修复—防回归”结构。

| 文件 | 覆盖症状 | 前置 | 代码任务 | 图表 |
|---|---|---|---|---|
| docs/17-troubleshooting/01-retrieval-and-chunking-problems.md | 无法检索、相关但不完整、Chunk 太小/大/重复、Embedding 不适合、过滤错误、Top-K/Reranker 差 | 03 至 08、12 | 诊断脚本与对照集 | D19 |
| docs/17-troubleshooting/02-generation-context-and-citation-problems.md | 检索正确但回答错误、答案与引用不一致、无引用、上下文冲突 | 09、12 | 引用一致性检查 | D19 |
| docs/17-troubleshooting/03-freshness-index-and-deletion-problems.md | 索引更新不及时、删除后仍可检索、版本错配 | 03-07、05-06、06、15-07 | 撤回与重建检查 | D19 |
| docs/17-troubleshooting/04-latency-cost-and-production-gap.md | 延迟高、Token 成本高、本地好生产差 | 08、15 | 性能分解与故障注入 | D19 |
| docs/17-troubleshooting/05-security-and-tenancy-incidents.md | 多租户数据泄漏、权限错误、恶意文档 | 14、15 | 事件响应演练 | D19 |
| docs/17-troubleshooting/06-good-metrics-bad-experience.md | 指标好但体验差，离线/在线分歧 | 12、15 | 反馈分层分析 | D19 |

### appendices

| 文件 | 目的 |
|---|---|
| docs/appendices/01-glossary.md | RAG 术语表；与根 GLOSSARY.md 同源生成或交叉引用 |
| docs/appendices/02-math-primer.md | 向量、矩阵、距离、概率与指标最低数学基础 |
| docs/appendices/03-python-quickstart.md | Python 快速入门 |
| docs/appendices/04-git-and-cli-cheatsheet.md | Git 和命令行速查 |
| docs/appendices/05-environment-variables.md | 环境变量、安全与 .env.example |
| docs/appendices/06-common-configuration.md | 常用配置与默认值解释 |
| docs/appendices/07-api-abstractions.md | 外部模型、Embedding、Retriever、VectorStore、Reranker 接口 |
| docs/appendices/08-common-errors.md | 常见错误速查 |
| docs/appendices/09-technology-selection-checklist.md | 基于场景约束的选型检查表 |
| docs/appendices/10-project-review-checklist.md | RAG 项目评审清单 |
| docs/appendices/11-papers-and-official-sources.md | 推荐论文、官方文档和官方仓库 |
| docs/appendices/12-learning-roadmap.md | 学习路线图与后续维护建议 |
| docs/appendices/13-version-and-source-register.md | 版本、核查日期、来源等级、许可证和变更风险 |

## 8. 代码任务总表与验证层级

| 核心义务 | 首次实现位置 | 复用位置 | 最低验证 |
|---|---|---|---|
| Document 对象 | src/rag_tutorial_core/documents.py | 所有摄取与项目 | 单元、序列化边界 |
| 基础文档切分 | chunking.py | 所有项目 | 单元、边界、Unicode |
| Embedding 接口抽象 | embeddings.py | Dense/Hybrid/多模态 | Mock 契约、批处理错误 |
| 相似度计算 | similarity.py | 简单向量库 | 数值单元、零向量 |
| Top-K 检索 | vector_store.py | minimal/local/pdf | 排序、并列、空库 |
| 简单向量存储 | vector_store.py | minimal/local | 增删查、持久化或明确内存态 |
| Prompt 组装与上下文注入 | prompting.py、context.py | 所有生成项目 | 预算、空上下文、注入隔离 |
| 来源引用 | citations.py | citation 与 capstones | 页码/来源、缺失、错配 |
| 基础评估指标 | evaluation.py | evaluated 与 capstones | 手算对照、空集合、重复命中 |
| 权限过滤 | permissions.py | enterprise 与 production | 跨租户拒绝、继承、删除 |

统一运行状态枚举：

- unverified：未验证。
- static-checked：只通过静态检查。
- unit-passed：单元测试通过。
- integration-passed：基础集成测试通过。
- external-verified：真实外部服务或环境验证通过。

每个代码项目必须明确：

- Python 版本、安装方式、环境变量、启动与测试命令。
- 输入样例、预期输出、外部服务/付费 API 需求。
- 本地、Mock、内存替代方案。
- 常见错误、资源释放、超时与错误路径。

## 9. 图表登记表

| ID | 必需图示 | 主文件 | 验证要求 |
|---|---|---|---|
| D01 | RAG 完整流程 | 02-01、10-01 | 静态语法；试点必须人工阅读检查 |
| D02 | Indexing Pipeline | 02-03 | 静态语法 |
| D03 | Query Pipeline | 02-03 | 静态语法 |
| D04 | 文档处理流程 | 03-01 | 静态语法 |
| D05 | Chunking 方法对比 | 04-01、04-02 | 表格 + 简图 |
| D06 | 向量空间示意 | 05-01 | Mermaid 不适合时用可复现绘图脚本 |
| D07 | HNSW 直观结构 | 06-02 | 分层绘制，避免过多节点 |
| D08 | Sparse、Dense、Hybrid 对比 | 07-02 | 静态语法 |
| D09 | 多路召回和 Reranking | 08-01、08-03、08-04 | 静态语法 |
| D10 | Context Construction | 09-01、09-02 | 静态语法 |
| D11 | RAG Evaluation | 12-01、12-05 | 静态语法 |
| D12 | Agentic RAG | 13-04 | 必须显示预算、停止和失败路径 |
| D13 | Graph RAG | 13-05 | 分层图，不暗示唯一实现 |
| D14 | 多模态 RAG | 13-07 | 显示不同模态的解析与表示 |
| D15 | 生产部署架构 | 15-08、16-03 | 分控制面/数据面 |
| D16 | 数据更新流程 | 03-07 | 显示版本、墓碑、重建和回滚 |
| D17 | 权限过滤流程 | 03-06、07-03、14-04 | 权限必须在返回内容前生效 |
| D18 | 安全威胁模型 | 14-01、14-02 | 显示信任边界和多层缓解 |
| D19 | 故障排查决策树 | 17 | 分多张图，禁止单图过载 |
| D20 | 章节依赖与学习路线 | 00-01 | 与 DEPENDENCY_MATRIX.md 一致 |

每张图必须有标题、教学问题、阅读说明、复杂度控制和验证状态；装饰性图片不计入完成度。

## 10. 技术主题覆盖矩阵

| 范围 | 完整主题集合 | 计划文件 |
|---|---|---|
| 学习准备 | AI、ML、DL、LLM、Transformer、Token、上下文窗口、Prompt、JSON、HTTP、API、Python、虚拟环境、包管理、命令行、Git、本地/云端模型、RAG 与微调/长上下文/工具调用 | 01-01 至 01-05；附录 02 至 07 |
| RAG 原理 | 定义、问题、参数化/非参数化知识、Indexing、Query、完整流程、降低但不消除幻觉、适用/不适用场景、失败模式 | 02-01 至 02-05 |
| 数据摄取 | Loader、Parser、PDF、Markdown、HTML、Word、Excel、PowerPoint、图片、OCR、表格、清洗、编码、页眉页脚、去重、结构、元数据、权限、版本、增量、删除、撤回、生命周期 | 03-01 至 03-07 |
| Chunking | 固定、重叠、句子、段落、标题层级、递归、语义、Parent-Child、Small-to-Big、表格、代码、对话、大小、Overlap、元数据、质量影响、实验 | 04-01 至 04-06 |
| Embedding | 概念、向量空间、语义相似、Cosine、Dot、Euclidean、归一化、文本、图片、多模态、通用/领域/多语言、维度、性能、成本、选型、迁移、重索引、错误 | 05-01 至 05-06 |
| 索引与向量库 | Flat、ANN、HNSW、IVF、PQ、构建、更新、Metadata Index、关系库/搜索引擎边界、Sharding、Replication、Backup、一致性、本地 FAISS、抽象比较、选型维度 | 06-01 至 06-06 |
| 检索 | Keyword、TF-IDF、BM25、Sparse、Dense、Hybrid、Metadata/时间/权限过滤、Query Rewrite、Query Expansion、Multi-Query、Decomposition、HyDE、Parent、Multi-Vector、Contextual、Self-Query、路由、失败诊断 | 07-01 至 07-08 |
| Reranking | 必要性、Bi-Encoder、Cross-Encoder、LLM Reranking、Score Fusion、RRF、多路召回、两/多阶段、Top-K、Recall/Precision、延迟、成本、评估 | 08-01 至 08-05 |
| 上下文与生成 | Selection、Dedup、Ordering、Compression、Token Budget、Lost in the Middle、冲突、过期、来源信任、引用、Grounded、无答案、拒答、结构化输出、多轮、历史压缩、Injection、防指令混淆 | 09-01 至 09-07 |
| 七个基础项目 | 纯 Python、本地向量、PDF、引用、Hybrid、Reranker、API+简单界面；每个项目具备完整运行与测试说明 | 10-01 至 10-07；对应 examples |
| 框架 | 原生 Python、LangChain 类、LlamaIndex 类、其他编排；封装、底层、优劣、不用框架、锁定规避、版本/日期/官方源 | 11-01 至 11-05 |
| 评估 | Golden、Query、Retrieved Context、Generated/Reference Answer、Retrieval/Generation/E2E、Recall、Precision、Hit、MRR、MAP、NDCG、Faithfulness、Answer Relevance、Context Relevance、Context Precision、Context Recall、LLM-as-a-Judge、人工、标准、错误、回归、在线、反馈、A/B | 12-01 至 12-07 |
| 高级 RAG | Routing、Adaptive、Self、Corrective、Iterative、Recursive、Agentic、Tool、Graph、Knowledge Graph、SQL、多模态、多语言、长上下文、Memory、Federated、CAG、多知识库、多 Agent；成熟度分类 | 13-01 至 13-09 |
| 安全治理 | Prompt/间接注入、投毒、恶意文档、越权、多租户、PII、敏感信息、权限继承、审核、引用真实性、审计、删除、撤回、驻留、合规、供应链、模型依赖安全、威胁建模、Red Team | 14-01 至 14-07 |
| 生产化 | API、同步/异步、Batch、队列、缓存、Streaming、并发、限流、重试、熔断、超时、日志、Metrics、Tracing、告警、各类成本、延迟、优化、四类版本、灰度、A/B、Docker、Docker Compose、CI/CD、云/本地、高可用、Backup、DR、容量 | 15-01 至 15-09 |
| 综合项目 | 企业助手全部要求；垂直领域数据质量、术语、风险、引用、拒答、追溯、权限、评估集、错误成本、人工复核与非专业替代声明 | 16-01 至 16-05；capstones |
| 故障排查 | 用户列出的 20 类症状全部按症状—原因—诊断—解决方案覆盖 | 17-01 至 17-06 |
| 附录 | 术语、数学、Python、Git/CLI、环境变量、配置、API 抽象、错误、选型、项目评审、论文/官方资料、路线图 | appendices 01 至 13 |

## 11. 最终验收覆盖矩阵

本节是最终验收摘要。原子需求、项目、图表和模块主题的负责人、依赖、证据、验证方法与独立 reviewer 以 `ACCEPTANCE_MATRIX.md` 为准。

| AC | 验收要求 | 计划证据 |
|---|---|---|
| AC01 | 清晰零基础学习路线 | README.md、00-01、appendices/12-learning-roadmap.md、D20 |
| AC02 | 按章节和文件组织 | docs 全目录、各 README、CONTENT_MANIFEST.md |
| AC03 | 完整核心链路 | 02 至 09、10-01 |
| AC04 | 主要高级方法 | 13-01 至 13-09 |
| AC05 | 安全、评估、生产 | 12、14、15 |
| AC06 | 核心技术原理 | 02、04 至 09 |
| AC07 | 核心流程图示 | D01 至 D20 登记与验证状态 |
| AC08 | 核心工程代码 | src/rag_tutorial_core、examples、capstones |
| AC09 | 两个端到端项目 | capstones 两目录、16-02 至 16-05 |
| AC10 | 安装运行说明 | 每个项目 README、pyproject、requirements |
| AC11 | 外部服务替代/Mock | adapters、Mock、内存实现、各项目 README |
| AC12 | 重要代码有测试 | tests/unit、integration、smoke 与 reports/test-report.md |
| AC13 | 所有章节独立审查 | CONTENT_MANIFEST 四类审查状态、四份 review report |
| AC14 | 术语与接口一致 | GLOSSARY.md、CODE_CONVENTIONS.md、契约测试 |
| AC15 | 内容 Manifest | CONTENT_MANIFEST.md 与 check-manifest.py |
| AC16 | 进度记录 | PROGRESS.md |
| AC17 | 测试报告 | reports/test-report.md |
| AC18 | 质量审查报告 | technical、beginner、editorial、final-quality 报告 |
| AC19 | 无大量重复 | Manifest 主讲章节字段、summary、重复检查 |
| AC20 | 无法验证诚实标注 | 运行状态枚举、来源登记、Known limitations |
| AC21 | 不声称穷尽所有技术 | 00-02、13-01、STYLE_GUIDE 禁用表述 |
| AC22 | 不声称消除幻觉 | 02-01、STYLE_GUIDE、QUALITY_CHECKLIST |

## 12. 第一批试点执行计划

### 12.1 试点文件

1. README.md：读者入口、学习路线、环境分流、验证状态说明。
2. docs/02-rag-principles/01-what-is-rag.md：概念入门章。
3. examples/minimal-rag/：纯 Python 最小可运行 RAG。
4. assets/diagrams/rag-end-to-end.mmd：D01。
5. tests/unit/test_minimal_rag.py 与 tests/smoke/test_minimal_rag_cli.py。
6. reports/pilot-review-report.md：技术、代码、初学者、编辑四类独立结论。

### 12.2 试点顺序

| 步骤 | 产出 | 门禁 |
|---|---|---|
| P1 | 先批准共享术语、代码接口、图表最小规范 | 无未定义核心术语；接口不依赖付费服务 |
| P2 | 写 README 与“什么是 RAG” | 不夸大；先直觉后定义；链接有效 |
| P3 | 实现 minimal-rag | Python 3.11+；Mock/内存默认；无密钥；完整运行说明 |
| P4 | 运行单元与冒烟测试 | 记录真实命令、输出和环境；失败不得伪装为通过 |
| P5 | 静态检查 Mermaid | 明确“未渲染”；人工检查教学价值 |
| P6 | 四类独立审查 | 作者不得是唯一审查者；阻塞项全部关闭或升级 |
| P7 | 更新 Manifest、Progress 与报告 | 所有状态与证据一致后才允许批量生产 |

### 12.3 试点成功判据

- 完全无 API Key 也能运行并得到确定性输出。
- 读者能指出语料、Chunk、Embedding、Top-K、上下文、Prompt、回答与引用各自的位置。
- 至少覆盖空语料、空查询、Top-K 越界、零向量或无答案等错误/边界路径。
- README 到章节、章节到代码、代码到测试的链接全部可达。
- D01 有标题、教学问题、阅读说明，且只声明实际完成的验证级别。
- 四类审查形成独立证据；任何“模型/版本/API 当前行为”都附官方来源与核查日期。

## 13. 风险与待 Leader 决策

| 风险 | 影响 | 建议 |
|---|---|---|
| xhigh 启动参数在 Worker 进程中不可见 | 无法由本报告独立证明推理强度 | Leader 保存 tmux/OMX 启动审计；任何报告不得自行补写证据 |
| mmdc 不存在 | Mermaid 不能声称渲染通过 | 先做静态检查；是否授权安装作者侧工具由 Leader/用户决定 |
| 框架与数据库 API 变化快 | 教程易过时 | 版本、核查日期、官方源登记到 appendices/13；适配器隔离 |
| 课程体量大 | 重复、术语漂移、上下文膨胀 | Manifest + summary + 主讲章节 + 批次门禁 |
| 七个基础项目可能复制大量代码 | 维护成本和初学者困惑 | 共享 rag_tutorial_core，但每项目 README 明确复用边界 |
| 高级方法成熟度争议 | 容易把论文概念写成标准实践 | 13-01 强制成熟度标签；Technical Reviewer 独立复核 |
| 安全章节过晚才介入 | 早期示例形成不安全习惯 | 在 03、07、09 嵌入安全提示，14 做系统化整合 |
| 评估被放在项目之后 | 读者可能先凭感觉调参 | 每个早期项目包含最小验证；第 12 部分再系统化 |
| 垂直领域选择未定 | 数据、风险与复核流程不确定 | 试点后按可获得公开数据、风险和教学价值决策 |
| 外部 Responses 传输不稳定 | 长审查报告可能中断 | 报告使用文件/邮箱落盘与紧凑 delta；不能把重连过程当作审查通过证据 |

## 14. 审查结论与进入下一阶段的门禁

课程结构已经完成真实多 Agent 设计和两类独立审查。独立审查的原始结论为“有条件通过/有条件不通过”，本文件已经吸收其 P0/P1 修复，但只有以下证据全部存在时才能进入试点：

1. 九个用户指定共享规范文件已创建并通过 Markdown 结构检查。
2. `ACCEPTANCE_MATRIX.md` 可从每个硬性项目、关键图和 AC01-AC22 追到 planned path、证据、验证方法和 reviewer。
3. `DEPENDENCY_MATRIX.md` 不含硬循环，并区分“必须已会、首次讲、只需直觉、选修深入”。
4. `reports/capability-audit.md` 只陈述真实能力；Mermaid 保持“未验证/静态检查”，不得写成渲染通过。
5. `CONTENT_MANIFEST.md` 登记所有当前文件并提供后续章节的扩展字段。
6. 当前批次不含章节正文、教程代码通过或 Mermaid 渲染通过的声明。

## 15. 移交与边界

- Leader 集成目标：PROJECT_PLAN.md、CONTENT_MANIFEST.md 初稿、DEPENDENCY_MATRIX.md 与第一批任务清单。
- Worker 2 已完成需求级技术审查和实际蓝图 delta，重点问题已经写入 1.1、目录、依赖和风险。
- Worker 3 已完成需求级初学者/总编审查和实际蓝图 delta，准备度、跨平台、导航、摘要与依赖真源问题已经写入本计划。
- 未决产品选择（API/UI 技术、垂直领域、框架版本）在相关批次开始前基于约束和官方资料决策，不在蓝图阶段伪装成已选定。
- 当前批次无章节正文、无教程依赖、无代码运行通过声明、无 Mermaid 渲染通过声明。
