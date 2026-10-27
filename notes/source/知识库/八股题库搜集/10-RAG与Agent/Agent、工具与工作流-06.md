# Agent、工具与工作流

<a id="k3018b4829270"></a>

## 短期记忆的具体实现方式是什么？

**回答：**

短期记忆不是一个单独的神秘模块，它本质上是当前任务继续执行所必需的工作状态。它既包括送入模型的近期上下文，也包括不一定直接放进 Prompt 的结构化状态，例如当前目标、执行计划、已完成步骤、工具返回引用和待确认事项。

我会把短期记忆拆成三层：

| 层次 | 主要内容 | 处理方式 |
|---|---|---|
| 固定约束 | System 指令、权限、安全边界、输出契约 | 高优先级保留，版本化管理 |
| 工作集 | 最近对话、当前计划、未完成步骤、关键工具结果 | 每轮更新，按任务相关性裁剪 |
| 历史压缩 | 更早轮次的结构化摘要和事件引用 | 达到预算或阶段边界时生成 |

工程上可以使用“近期窗口 + 结构化摘要 + 外部原始事件存储”。近期窗口保留最后若干轮完整交互；摘要不是泛泛复述，而应固定字段，例如 `goal`、`constraints`、`completed_steps`、`open_questions`、`artifacts`、`decisions` 和对应的事件 ID。这样能减少摘要遗漏关键约束，也方便回溯原文。

短期状态可以存在 Workflow state、会话数据库或检查点存储中；Prompt 只是它的一种投影视图。每次模型调用前，由 Context Builder 根据 Token 预算选择哪些状态进入上下文。这样即使模型窗口变化，底层任务状态仍保持稳定。

最后要强调：KV Cache 是推理加速状态，不等于 Agent Memory；聊天记录也不等于短期记忆。短期记忆的标准是“它是否帮助当前任务正确继续”，而不是“它是否最近出现过”。

<a id="moonshot-agent-dev-20260721-q3"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E6%9C%88%E4%B9%8B%E6%9A%97%E9%9D%A2%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L76)，来源许可：GPL-3.0。

<a id="kec83758ffdda"></a>

## 秒版本怎么说？

30 秒版本只回答项目是什么、为什么需要 Agent、你负责什么和最难的问题是什么。

这里还是以智能售后工单 Agent 为例：

> 我做的是一个智能售后工单 Agent。除了知识库问答，它还会根据用户描述动态查询订单、检索售后政策、补充缺失信息，并在用户确认后创建工单。整体采用固定工作流加局部 Agent Loop：鉴权、权限校验、确认和写入是确定性节点，模型只负责意图理解、信息补全和下一步工具选择。
>
> 我主要负责 Agent 编排、工具治理和评测。项目里最典型的两个问题是相似工具误选，以及写接口超时后无法判断是否已执行，我们分别用工具契约优化和“幂等键 + 状态查询 + 对账”解决。

千万不用讲太细节，比较聪明的做法是预留下自己提前准备好可被追问的内容：为什么是混合架构、工具怎么治理、写操作为什么不能盲目重试、评测怎么做。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/interview-questions/agent-project-interview-guide.md#L96)，来源许可：Apache-2.0。

<a id="k859adbb55916"></a>

## 第 1 课：先定义业务，再选 Agent 形态

核心阅读：[第 1 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/01_AIGC时代AI%20Agent基础高频考点.md#q-002)、[第 2 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/01_AIGC时代AI%20Agent基础高频考点.md#q-003)、[第 3 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/05_Agent记忆与上下文工程高频考点.md#q-002)、[第 6 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/01_AIGC时代AI%20Agent基础高频考点.md#q-007)、[第 69 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/01_AIGC时代AI%20Agent基础高频考点.md#q-031)、[第 70 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/01_AIGC时代AI%20Agent基础高频考点.md#q-032)。

先列出十个真实风格的请求，例如“课程面向什么基础”“周六还有名额吗”“以后优先找晚课”“帮我预约下周的 Python 入门”。为每个请求标出所需事实、是否改变业务状态、失败代价和成功判据。只有问答的需求，不强行引入规划器；库存问题不能只检索课程介绍。

把知识、记忆和实时业务拆开：规则由知识库提供；用户自己确认的偏好由记忆提供；场次和库存由预约服务提供。遇到“这次要上午，平常还是晚课”时，当前选择与长期偏好应同时成立，各有作用范围。

**实验。** 不调用模型，手工给十个请求选择问答、RAG、工具或 Agent/Workflow 组合，并画出数据流。记录每个模块是否更新模型参数，区分 Prompt、RAG、微调和预训练。

**验收。** 对任一字段都能说出权威来源，对任一写操作都能说出授权和验收位置。若设计中的“预约成功”仅依据模型文本，先修正架构再进入下一课。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%83%AD%E9%97%A8AI%E5%AD%A6%E4%B9%A0%E6%A0%B8%E5%BF%83%E8%AF%BE%E7%A8%8B%E4%B8%8E%E6%95%99%E7%A8%8B/16_AI_Agent%E5%B7%A5%E7%A8%8B%E5%AE%9E%E6%88%98%EF%BC%9A%E5%9F%BA%E7%A1%8080%E9%97%AE%E5%AD%A6%E4%B9%A0AI%20Agent.md#L61)，来源许可：GPL-3.0。

<a id="kce926ecd7630"></a>

## 第 10 课：把个人助手看成持续运行的系统

核心阅读：[第 7 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/02_编码Agent与AgentOS工程高频考点.md#q-040)、[第 71 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/02_编码Agent与AgentOS工程高频考点.md#q-041)、[第 72 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/02_编码Agent与AgentOS工程高频考点.md#q-031)、[第 73 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/05_Agent记忆与上下文工程高频考点.md#q-028)、[第 74 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/05_Agent记忆与上下文工程高频考点.md#q-032)、[第 75 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/05_Agent记忆与上下文工程高频考点.md#q-021)。

通过编码 Agent 与个人助手的架构对比，区分产品入口和执行核心。OpenCode、Gemini CLI、Codex CLI、Claude Code 的选型用同任务、同仓库和相同验收比较；模型名单和套餐不作为这门课的固定知识。

用 OpenClaw 理解 Gateway、Runtime、会话、工作空间与记忆的关系，但不要把通用“短中长期记忆”分类硬套成官方固定模块。阅读实际版本的记忆文档，分别说明消息、摘要、日常记录、持久事实及可选用户资料如何进入上下文。

**实验。** 以 Markdown 为可维护记忆，SQLite FTS5 为词法索引，建立内容哈希与索引水位。修改文件、删除段落、模拟索引损坏，再从合法文件重建。中文匹配先确定 tokenizer 或预处理方式；向量索引属于另一个职责。

**验收。** 能解释主数据与索引谁是权威，能说明持久文件不等于每轮全部注入。后台总结只提升经审核的信息，不能把历史授权无期限延长。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%83%AD%E9%97%A8AI%E5%AD%A6%E4%B9%A0%E6%A0%B8%E5%BF%83%E8%AF%BE%E7%A8%8B%E4%B8%8E%E6%95%99%E7%A8%8B/16_AI_Agent%E5%B7%A5%E7%A8%8B%E5%AE%9E%E6%88%98%EF%BC%9A%E5%9F%BA%E7%A1%8080%E9%97%AE%E5%AD%A6%E4%B9%A0AI%20Agent.md#L179)，来源许可：GPL-3.0。

<a id="kc59058dc7709"></a>

## 第 11 课：用事务和幂等完成一次预约

核心阅读：[第 76 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/07_企业级Agent平台与产品落地高频考点.md#q-028)、[第 77 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/07_企业级Agent平台与产品落地高频考点.md#q-009)、[第 78 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/07_企业级Agent平台与产品落地高频考点.md#q-031)、[第 79 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/07_企业级Agent平台与产品落地高频考点.md#q-019)。

业务服务负责名额、价格、约束和最终结果。网关负责入口路由与通用策略，Nacos 负责服务发现与配置等能力；业务请求一般不会由 Nacos 代为执行。MongoDB、PostgreSQL、Redis 只是可选组合，首先定义每类数据的权威写入点。

将确认与提交分开。确认绑定具体方案、用户和版本，后续改字段必须重新确认。真正提交时重新检查名额，依靠事务与并发条件更新保证不会超卖，依靠幂等键保证同一意图重试返回原结果。

**运行控制层实验。** 打开[配套实验代码](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%83%AD%E9%97%A8AI%E5%AD%A6%E4%B9%A0%E6%A0%B8%E5%BF%83%E8%AF%BE%E7%A8%8B%E4%B8%8E%E6%95%99%E7%A8%8B/examples/agent_course_assistant.py)，从仓库根目录执行：

```bash
python3 "热门AI学习核心课程与教程/examples/agent_course_assistant.py"
```

示例会在临时目录建立 SQLite 数据库，执行 RRF 排名、只读记忆查询、偏好更正与删除，以及预约确认与幂等提交。它通过重新打开数据库模拟请求方丢失响应后的重试；还会拒绝参数变化、身份变化和过期方案。测试结果输出 JSON，临时数据随后清理。

**接入真实系统时继续补齐。** 示例中的 user_id 代表已经通过认证的调用者；HTTP 服务必须从真实会话绑定身份，不能从模型参数取值。还需密钥与隐私管理、业务级唯一约束、跨进程并发压测、取消补偿和监控。SQL 示例与 pgvector 参数应在你部署的实际版本上验证执行计划。

**验收。** 在“提交成功—响应未到达”的窗口恢复，只产生一笔预约；使用同一幂等键却修改参数必须失败；确认过期或库存改变必须重新收集有效确认。业务库、运行状态与最终回答对得上。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%83%AD%E9%97%A8AI%E5%AD%A6%E4%B9%A0%E6%A0%B8%E5%BF%83%E8%AF%BE%E7%A8%8B%E4%B8%8E%E6%95%99%E7%A8%8B/16_AI_Agent%E5%B7%A5%E7%A8%8B%E5%AE%9E%E6%88%98%EF%BC%9A%E5%9F%BA%E7%A1%8080%E9%97%AE%E5%AD%A6%E4%B9%A0AI%20Agent.md#L191)，来源许可：GPL-3.0。

<a id="k04d42e510d54"></a>

## 第 3 课：编排服从任务，恢复服从副作用

核心阅读：[第 10 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/03_Agent设计模式与工作流编排高频考点.md#q-006)、[第 11 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/03_Agent设计模式与工作流编排高频考点.md#q-011)、[第 12 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/03_Agent设计模式与工作流编排高频考点.md#q-013)、[第 13 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/03_Agent设计模式与工作流编排高频考点.md#q-025)、[第 14 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/03_Agent设计模式与工作流编排高频考点.md#q-016)、[第 15 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/07_企业级Agent平台与产品落地高频考点.md#q-029)、[第 16 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/07_企业级Agent平台与产品落地高频考点.md#q-030)、[第 17 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/03_Agent设计模式与工作流编排高频考点.md#q-026)、[第 18 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/03_Agent设计模式与工作流编排高频考点.md#q-027)、[第 19 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/03_Agent设计模式与工作流编排高频考点.md#q-024)、[第 80 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/03_Agent设计模式与工作流编排高频考点.md#q-028)。

给课程规则查询使用轻量路径；给多条件筛选使用局部 ReAct；给预约使用固定状态机。复杂目标可先制定计划，但实际执行要允许按新证据修改。反思仅在能改善下一次行动的节点触发，不把每个工具响应都变成一轮自评。

建立意图集合 `knowledge_query、booking_query、booking_create、memory_read、memory_update、cancel、unknown`。规则处理明确命令，模型处理表达变化，服务端白名单决定处理器。多意图请求先拆解依赖，未知意图澄清；不要让用户文本选择任意类名或内网地址。

**LangGraph 实验。** 先用普通状态机完成流程，再选择需要持久化或条件转移的部分迁入图。State 保存槽位、确认版本和回执引用；Node 返回状态更新；Edge 描述控制路径。配置 checkpointer 与线程标识，再测试暂停恢复。恢复前后的副作用应使用相同幂等键。

**故障注入。** 在工具成功后、checkpoint 保存前停止进程；再次恢复，检查业务库有没有第二笔预约。另测确认节点恢复时，节点开头代码被重跑的情形。没有真实使用过 LangGraph，就把这部分写成实验计划，并如实说明当前实现。

**验收。** 能解释 Workflow 与 Runtime 谁负责重试、取消和权威状态；能用 trace 证明没有双重重试扩大副作用。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%83%AD%E9%97%A8AI%E5%AD%A6%E4%B9%A0%E6%A0%B8%E5%BF%83%E8%AF%BE%E7%A8%8B%E4%B8%8E%E6%95%99%E7%A8%8B/16_AI_Agent%E5%B7%A5%E7%A8%8B%E5%AE%9E%E6%88%98%EF%BC%9A%E5%9F%BA%E7%A1%8080%E9%97%AE%E5%AD%A6%E4%B9%A0AI%20Agent.md#L85)，来源许可：GPL-3.0。

<a id="kee9547914b56"></a>

## 第 6 课：回答质量要沿证据链验收

核心阅读：[第 41 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/10_Agent_RAG与混合检索工程高频考点.md#q-022)、[第 42 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/10_Agent_RAG与混合检索工程高频考点.md#q-023)、[第 43 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/10_Agent_RAG与混合检索工程高频考点.md#q-024)、[第 44 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/10_Agent_RAG与混合检索工程高频考点.md#q-025)、[第 45 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/10_Agent_RAG与混合检索工程高频考点.md#q-026)、[第 46 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/10_Agent_RAG与混合检索工程高频考点.md#q-027)。

用文档块表关联正文、元数据、向量与全文字段。关键 ACL 与版本条件不可只存在于提示词。召回、重排、父文档展开和缓存命中都要维持用户可见范围；即使 ANN 先扫描候选再过滤，也不允许未授权正文进入外部模型。

设计四类问题：有直接答案、需要跨段证据、资料冲突和没有答案。先把标准证据直接给生成器，测生成环节的上限；再恢复实际检索，检查质量损失来自哪一阶段。引用必须落到正确文档版本与位置。

**实验。** 给两个用户配置不同文档权限，查询相同问题，验证任何一方都看不到另一方正文。再更新或删除文档，检查向量、全文、父块与答案缓存是否一致失效。权限过滤后候选不足，使用补召回或降级，不能取消过滤。

**性能实验。** 分别记录改写、Embedding、两路召回、重排、首 Token 与完整响应时间。流式开关主要比较首字体验；完整耗时是否改善要独立测量。优化方案必须附质量回归，而非只报告“快了多少”。

**验收。** 无答案时能拒绝无依据的结论，证据冲突时能表达范围与不确定性。保留合理拒答率，避免用“全拒答”获得零幻觉的表面成绩。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%83%AD%E9%97%A8AI%E5%AD%A6%E4%B9%A0%E6%A0%B8%E5%BF%83%E8%AF%BE%E7%A8%8B%E4%B8%8E%E6%95%99%E7%A8%8B/16_AI_Agent%E5%B7%A5%E7%A8%8B%E5%AE%9E%E6%88%98%EF%BC%9A%E5%9F%BA%E7%A1%8080%E9%97%AE%E5%AD%A6%E4%B9%A0AI%20Agent.md#L127)，来源许可：GPL-3.0。

<a id="k94f2dcf8525b"></a>

## 第 7 课：让记忆可读、可改、可删除

核心阅读：[第 25 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/10_Agent_RAG与混合检索工程高频考点.md#q-006)、[第 47 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/05_Agent记忆与上下文工程高频考点.md#q-006)、[第 48 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/05_Agent记忆与上下文工程高频考点.md#q-029)、[第 49 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/05_Agent记忆与上下文工程高频考点.md#q-016)、[第 50 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/05_Agent记忆与上下文工程高频考点.md#q-018)、[第 51 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/05_Agent记忆与上下文工程高频考点.md#q-011)、[第 52 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/05_Agent记忆与上下文工程高频考点.md#q-014)、[第 53 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/05_Agent记忆与上下文工程高频考点.md#q-030)、[第 54 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/05_Agent记忆与上下文工程高频考点.md#q-013)、[第 55 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/05_Agent记忆与上下文工程高频考点.md#q-031)、[第 56 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/05_Agent记忆与上下文工程高频考点.md#q-012)。

将消息日志、任务状态、会话摘要、结构化偏好和语义记忆分开。身份精确查询，偏好有作用范围，历史经历可语义检索。调用模型时保留最近完整交互与有效摘要，不因窗口裁剪丢掉一个仍待执行的工具调用。

为以下对话编写预期结果：“我平常喜欢晚课”“这次选上午”“以后都选上午”“你知道我偏好什么吗”“假设我喜欢周末课”“忘掉我的时间偏好”。这六句分别考验长期写入、临时覆盖、永久更正、只读查询、假设过滤和删除。

**实验。** 偏好记录包含用户、字段、值、范围、状态、版本和证据。读取函数不改变记录；写入需声明依据；更正将旧版本失效；删除同步清理索引，并用 tombstone 或等效机制防止后台摘要重新引入。Active 等状态是项目约定，按实际需要定义。

**摘要实验。** 用消息水位推进增量摘要，在摘要保存前后分别注入失败，检查是否重复或漏摘要。人工抽查金额、日期、当前目标与待确认事项，关键值回查结构化状态。

**验收。** 当前临时请求不会无意覆盖永久偏好；读取偏好不会写入猜测；已删除信息不会通过搜索、缓存或后台整理再次出现。语义相近的否定句不能直接归并。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%83%AD%E9%97%A8AI%E5%AD%A6%E4%B9%A0%E6%A0%B8%E5%BF%83%E8%AF%BE%E7%A8%8B%E4%B8%8E%E6%95%99%E7%A8%8B/16_AI_Agent%E5%B7%A5%E7%A8%8B%E5%AE%9E%E6%88%98%EF%BC%9A%E5%9F%BA%E7%A1%8080%E9%97%AE%E5%AD%A6%E4%B9%A0AI%20Agent.md#L141)，来源许可：GPL-3.0。

<a id="k18505feda619"></a>

## 第3点我说了智能体上架的流程每次都重复单一，可以作为切入点，面试官询问：怎么设计这个智能体？需要有哪些skill和tool，共享一下屏幕写一下提示词，这个智能体验收的标准是什么？哪些步骤需要人工来复核？通过率和不通过率测试集怎么构建？

**回答：**

这个问题是二面的核心，回答要像真实方案设计，而不是泛泛说“用 LangChain 调工具”。

可以把智能体设计成“上架 Copilot + 发布前检查器”。输入是智能体说明、工具 schema、权限说明、测试样例、业务方需求和发布环境；输出是上架材料、测试报告、风险清单、缺失项提示和发布建议。主流程用 workflow 固定住：读取材料 -> 规范检查 -> 工具连通性测试 -> 生成测试集 -> 执行回归 -> 产出报告 -> 人工复核 -> 发布。

Skill 可以包括：需求摘要 skill、上架文档生成 skill、工具 schema 校验 skill、prompt 规范检查 skill、测试用例生成 skill、风险识别 skill、发布报告生成 skill。Tool 可以包括：文档读取、代码仓库读取、API schema validator、接口 ping/curl、权限查询、测试执行器、日志查询、发布平台 API、消息通知。

提示词要明确边界，例如：你是智能体上架审核助手，只能基于提供材料生成结论；缺字段必须列出，不允许编造；高风险操作必须标记人工复核；输出必须包含缺失项、测试项、风险项、建议结论和引用材料片段。验收标准包括：材料完整率、schema 校验通过率、测试用例覆盖率、一次上架通过率、人工修改次数、误放行率、误拦截率、平均上架耗时。

人工复核点包括：业务语义是否正确、权限是否合规、高风险工具是否允许调用、发布窗口和灰度策略、最终上线确认。测试集要分通过集和不通过集：通过集覆盖标准上架样例；不通过集覆盖缺字段、schema 错误、权限缺失、危险工具、接口不可达、prompt 越权、测试失败、文档与代码不一致等。真正成熟的设计，是让模型负责理解和生成，让工具负责验证，让人负责风险决策。

<a id="bytedance-ai-fde-20260712-q13"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%AD%97%E8%8A%82%E8%B7%B3%E5%8A%A8%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L908)，来源许可：GPL-3.0。

<a id="k35a28f4dc0e9"></a>

## 简单介绍一下自己的经历，以及为什么选择AI Agent方向？

**回答：**

这道题不能背一段与简历脱节的模板。高质量回答应在 60～90 秒内形成“经历主线 -> 能力证据 -> 方向选择 -> 岗位匹配”的闭环。

可以按下面的结构组织，但必须替换成自己的真实信息：

1. **一句话定位。** 说明学历或工作年限、主技术栈，以及当前最能代表自己的方向。例如：“我主要做 Java 后端与大模型应用工程，最近一段经历集中在检索增强和工具型 Agent。”
2. **选择两段最相关的证据。** 不按时间流水账复述简历，而是讲清“业务问题、个人职责、关键机制、验证结果”。如果项目只做到离线验证，就明确说离线指标；不要把课程项目包装成生产系统。
3. **解释为什么是 Agent。** 有说服力的原因通常是：传统后端擅长确定性流程和系统可靠性，LLM 擅长理解非结构化意图与动态决策，Agent 工程的价值在于用 Harness 把模型、工具、状态和验证组织起来，完成仅靠单次生成无法完成的长链任务。
4. **落到岗位。** 说明自己能带来的具体能力，例如工具/API 设计、状态机、检索与记忆、Java 并发、可观测性、评测和故障恢复，而不是只说“看好 AI 前景”。

一个可直接改写的结尾是：“我选择 AI Agent，并不是因为它是新名词，而是因为它把模型能力与真实软件系统连接起来。我的后端工程经验能解决权限、状态、并发和可靠性问题，已有的大模型项目经验又让我理解上下文、工具调用和评测，因此这个方向与我的能力积累是连续的。”

<a id="insta360-agent-20260809-q2"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%BD%B1%E7%9F%B3%E5%88%9B%E6%96%B0%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L35)，来源许可：GPL-3.0。

<a id="k587b29a1c0ee"></a>

## 简单介绍一下自己的背景，以及选择AI Agent方向的原因。

**回答：**

建议用 60～90 秒完成“背景 -> 证据 -> 方向选择 -> 岗位匹配”的闭环，而不是罗列课程和模型名称。背景部分说明自己的学历或工作阶段、主技术栈，以及最相关的项目；项目部分说明业务目标、个人负责的模块、关键技术决策和可验证结果；最后解释为什么从传统开发转向 Agent。

选择 AI Agent 的本质理由不是“它是热点”，而是它把大模型的语义理解与真实软件系统的工具、状态和业务验收连接起来。传统软件擅长确定性流程，大模型擅长处理自然语言和开放式任务，但单次生成容易缺少事实、状态和执行能力。Agent 工程要解决的正是如何让模型在权限、预算、工具协议、记忆和验证器约束下完成多步任务。

比较稳妥的结尾是：“我选择 AI Agent，是因为它与我已有的工程能力是连续的。我可以用后端能力处理状态、并发、权限、幂等和可观测性，再结合模型调用、RAG、工具编排和评测，把模型能力变成可交付的业务流程。”其中项目数字必须来自真实记录；没有线上数据就明确说是离线评测或故障回放结果。

<a id="bilibili-ai-agent-20260818-q2"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%93%94%E5%93%A9%E5%93%94%E5%93%A9%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L33)，来源许可：GPL-3.0。

<a id="k540f9b0c39e0"></a>

## 简单介绍下视频生成Agent完整项目？

**回答：**

这个项目可以讲成一个面向创作者的自动视频生产 Agent。用户输入主题、目标平台、视频风格、时长和素材约束，系统自动生成文案、拆解剪辑脚本、检索或生成素材、编排时间轴、生成字幕和配音，最后渲染出可编辑的视频草稿。

架构上分为五层。第一层是交互层，负责收集用户需求、展示脚本和成片、支持人工修改。第二层是 Agent 编排层，用 LangGraph/工作流引擎管理状态和节点流转。第三层是模型能力层，包括 LLM 文案生成、VLM 画面理解、TTS、ASR、embedding/rerank。第四层是工具层，包括素材检索、媒体转码、字幕渲染、FFmpeg 合成、封面生成。第五层是评测与观测层，记录每个节点输入输出、耗时、错误、质量分和用户反馈。

核心难点是把创作任务变成可执行 DAG。大模型生成的是意图和结构化计划，真正执行靠确定性工具。每个节点都有 schema、校验、重试和降级。比如脚本生成失败就重试修复 JSON，素材不足就扩大检索或生成替代素材，渲染失败就定位具体片段。

项目价值不是“自动生成一个视频”这么简单，而是把视频生产从人工串行流程变成可追踪、可评估、可编辑的智能生产线。

<a id="xiaohongshu-ai-fullstack-20260702-q14"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%B0%8F%E7%BA%A2%E4%B9%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L296)，来源许可：GPL-3.0。

<a id="kda7eb0bef535"></a>

## 简单讲讲你的Agent项目？

**回答：**

我会先用一句话定义项目：这是一个面向长链任务的 Agent 系统，以 ReAct 为基本决策循环，结合工具调用、RAG、短期工作记忆和长期记忆，让模型能够围绕目标持续执行，而不是只生成一次答案。

核心执行链路可以抽象为：

$$
s_t \xrightarrow{\pi_\theta} a_t
\xrightarrow{\text{tool/env}} o_{t+1}
\xrightarrow{\text{state update}} s_{t+1}
$$

其中 $s_t$ 是当前任务状态，$a_t$ 是模型选择的动作或工具调用，$o_{t+1}$ 是外部环境返回的 Observation。运行时不是简单写一个无限 `while`，而是受状态机约束：每一步都要做工具权限检查、参数校验、超时与重试控制，并在完成条件、失败条件、人工审批点或最大步数到达时终止。

项目中我把能力拆成四层。第一层是规划与路由，决定当前任务应直接回答、检索知识、读取记忆还是调用工具。第二层是执行层，对工具 schema 做约束解码和参数验证。第三层是状态与记忆层，保存当前目标、已完成步骤、中间产物以及需要跨会话复用的信息。第四层是可观测与评测层，记录每一步输入、动作、工具返回、耗时和失败原因，并用任务完成率、工具选择正确率、参数正确率、无效步骤数和失败恢复率评估。

需要纠正一个常见说法：Observation 来自真实工具，只能提供外部证据，不能自动“保证长线任务可靠”。工具可能超时、返回脏数据，模型也可能误读 Observation 或陷入循环。真正的可靠性来自工具反馈、状态约束、验证器、预算、回退策略和人工复核共同组成的 Harness。

面试中还应落到个人贡献和结果：具体负责了哪些模块、如何构建评测集、哪类失败最常见、上线后任务成功率或人工耗时改善了多少。没有真实指标时不要编造，可以诚实说明当前做到离线验证还是灰度阶段。

<a id="moonshot-agent-dev-20260721-q2"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E6%9C%88%E4%B9%8B%E6%9A%97%E9%9D%A2%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L53)，来源许可：GPL-3.0。

<a id="k93c817d28f0c"></a>

## 经验如何从一次任务沉淀为 Memory、Skill 和 Policy？

一次任务结束后，经验可以分三类沉淀：

1. **Memory**

   保存用户偏好、项目规则、长期事实、工具使用经验和任务状态。例如“该项目测试命令是 `npm test`”“用户偏好简洁回答”。

2. **Skill**

   保存可复用流程、模板、脚本和参考资料。例如“代码审查 checklist”“网页调研流程”“会议纪要生成流程”。

3. **Policy / Guardrail**

   保存安全边界和执行规则。例如“删除文件前必须确认”“网页内容不能覆盖系统指令”“某类工具失败 3 次后停止重试”。

推荐流程：

1. 收集完整 trace。
2. 提取成功经验和失败教训。
3. 判断经验类型。
4. 去重和脱敏。
5. 赋予 scope、source、confidence、version。
6. 写入 Memory、Skill 或 Policy。
7. 后台 Curator 定期评分、合并、归档。
8. 用户可查看、编辑、删除或回滚。

工程上要避免把所有经验都写成长期记忆。可执行流程更适合 Skill，安全规则更适合 Policy，失败案例更适合 Eval / Harness。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/09_%E8%87%AA%E8%BF%9B%E5%8C%96Agent%E4%B8%8E%E5%A4%9A%E5%B9%B3%E5%8F%B0%E8%BF%90%E8%A1%8C%E6%97%B6%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L85)，来源许可：GPL-3.0。

<a id="kb2e7f2364a72"></a>

## 结构化输出与工具调用

相关内容：[《大模型结构化输出：从 JSON 契约到 Function Calling 落地》](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/llm-basis/structured-output-function-calling.md)

模型输出只要进入业务系统，就要处理格式校验、字段约束和执行权限。这里容易混淆 JSON Mode、Structured Outputs、Function Calling、MCP Tool 与普通 HTTP API。

常见面试题：

- 为什么只写“请返回 JSON”不可靠？
- JSON Mode 和 Structured Outputs 有什么区别？
- JSON Schema 在大模型应用里解决什么问题？
- Function Calling 的完整链路是什么？
- Function Calling 和 MCP 有什么区别？
- MCP Tool 和普通 HTTP API 有什么关系？
- Agent Skill 和 Function Calling 是一回事吗？
- 结构化输出失败后怎么处理？
- 工具调用为什么必须做安全治理？
- 面试里怎么一句话概括结构化输出？

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/interview-questions/llm-interview-questions.md#L55)，来源许可：Apache-2.0。

<a id="k404b96b69705"></a>

## 综合设计题

项目面试除了考概念，还会继续追问架构、选型依据、效果证据和线上失败。完整的回答组织方法可以参考 [《Agent 项目面试怎么讲？从系统架构、技术选型到 Badcase 复盘》](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/interview-questions/agent-project-interview-guide.md)。

综合题会把前面的组件放进同一个任务里，重点检查选型和故障处理：

- 如果让 Agent 完成一次需要调用多个工具的长任务，你会如何拆分执行步骤？
- 哪些节点适合交给模型判断，哪些节点应该由规则或代码控制？
- Agent 的计划、工具结果和中间状态如何保存？中断后怎样恢复？
- 工具包含写操作时，权限、参数校验、二次确认和审计怎么设计？
- 什么情况下需要 Multi-Agent？如何控制通信成本和状态一致性？
- 你会记录哪些 Trace，并用哪些指标评估任务完成率、工具调用和执行轨迹？

### 补充说明

- 如何设计一个多 Agent 系统，让它支持任务拆分、并行执行、状态共享、冲突处理和失败恢复？参考：[《多 Agent 协作系统设计：任务拆分、状态共享、冲突处理与失败恢复》](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/agent/multi-agent.md)
- 如何设计一个带权限控制、引用溯源和知识库更新能力的企业 RAG 系统？
- 如何设计一个支持长任务、工具调用、中断恢复和人工接管的 Agent 平台？
- 智能客服流量突然增加，同时模型供应商开始限流，系统应该如何排队、降级和保护核心请求？
- 模型或 Prompt 升级后，结构化输出成功率和答案质量下降，如何定位并回滚？
- Agent 可以查询订单并发起退款时，权限、参数校验、二次确认、幂等和审计怎么设计？
- 如何设计一个支持实时打断、低延迟和故障降级的语音客服系统？

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/interview-questions/agent-interview-questions.md#L137)，来源许可：Apache-2.0。
- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/interview-questions/ai-system-design-interview-questions.md#L113)，来源许可：Apache-2.0。

<a id="k48e633b53b6d"></a>

## 编码 Agent Harness 应该如何设计？

编码 Agent Harness 的目标是评估 Agent 是否能在真实代码仓库里理解问题、修改代码、运行测试、控制 diff，并避免破坏用户工作区。

典型流程：

1. 准备 repo base commit。
2. 注入 issue、失败测试或需求说明。
3. 启动隔离容器或临时工作区。
4. 给 Agent 文件读写、搜索、Shell、Git、测试工具。
5. 限制网络、密钥和危险命令。
6. 运行 Agent 生成 patch。
7. 应用 patch 并运行测试。
8. 检查 diff 范围、测试结果、安全策略和日志。
9. 输出 score、trace 和失败标签。

常见判分维度：

- 是否解决 issue。
- 相关测试是否通过。
- 是否引入回归。
- diff 是否最小。
- 是否修改无关文件。
- 是否运行必要测试。
- 是否泄露 secret。
- 是否执行危险命令。
- 是否覆盖用户未提交改动。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/08_Agent_Harness_Engineering%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L398)，来源许可：GPL-3.0。

<a id="ka55cb99df2b6"></a>

## 编码 Agent 与传统 IDE Copilot 有什么区别？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

| 维度 | 传统 Copilot | 编码 Agent |
| --- | --- | --- |
| 交互方式 | 用户写代码，模型补全/建议 | 用户给目标，Agent 读写运行验证 |
| 上下文 | 当前文件或局部工程 | 仓库、历史、工具结果、项目记忆 |
| 行动能力 | 主要生成代码 | 可编辑文件、运行命令、查日志、提交变更 |
| 自主性 | 低，用户主导 | 中高，Agent 可规划多步 |
| 验证 | 用户运行测试 | Agent 可自行运行测试并迭代 |
| 风险 | 生成错误代码 | 可能执行危险命令或改错文件 |

一句话：

Copilot 更像副驾驶，编码 Agent 更像可以接手一张工单的初级工程执行者，但需要权限和审查。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/02_%E7%BC%96%E7%A0%81Agent%E4%B8%8EAgentOS%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L83)，来源许可：GPL-3.0。

<a id="k18eb06d18678"></a>

## 编码 Agent 常见失败模式有哪些？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

| 失败模式 | 原因 | 缓解 |
| --- | --- | --- |
| 改错文件 | 搜索不充分，误解架构 | 先定位引用和测试，要求计划 |
| 覆盖用户改动 | 未检查 dirty state | 写前检查 diff |
| 测试没跑 | 任务结束过早 | Todo 中强制验证步骤 |
| 幻觉 API | 未读类型定义或文档 | LSP/rg/官方文档 |
| 命令危险 | 权限过宽 | 沙箱和审批 |
| 上下文污染 | 历史过长且无关 | 压缩和选择性保留 |
| 长任务漂移 | 缺少显式计划 | Plan Mode + TODO |
| 子 Agent 冲突 | 写同一文件 | 明确文件所有权 |
| Prompt injection | 工具返回恶意内容 | 内容隔离和策略检查 |

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/02_%E7%BC%96%E7%A0%81Agent%E4%B8%8EAgentOS%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L773)，来源许可：GPL-3.0。

<a id="k171d81f4e038"></a>

## 编码 Agent 的 tracing 和 telemetry 应该记录什么？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

建议记录：

- 用户目标。
- 模型版本。
- 系统提示词版本。
- 工具列表。
- 每次工具调用和参数。
- 权限请求和结果。
- 文件变更 diff。
- 命令输出和退出码。
- 测试结果。
- 子 Agent 任务和结论。
- 上下文压缩边界。
- token、耗时、费用。
- 最终交付摘要。

隐私要求：

- 可关闭遥测。
- 敏感文件脱敏。
- 不上传密钥。
- 企业可配置日志保留周期。
- 用户可查看和删除历史。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/02_%E7%BC%96%E7%A0%81Agent%E4%B8%8EAgentOS%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L745)，来源许可：GPL-3.0。

<a id="kd62e4b4520ce"></a>

## 编码 Agent 的上下文工程有哪些特殊难点？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

本节只把编码 Agent 作为上下文工程的典型案例，说明“相关性、新鲜度、可验证性”为什么重要；编码 Agent 的工具、权限、IDE/CLI、远程会话和 AgentOS 工程实现，见 [02_编码Agent与AgentOS工程高频考点.md](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/02_编码Agent与AgentOS工程高频考点.md)。

编码 Agent 的上下文工程更难，因为代码任务需要精确、可验证、跨文件一致。

难点：

- 大仓库文件太多，不能全塞上下文。
- 相关代码分散在多个模块。
- 类型定义、测试、配置、文档都可能关键。
- 用户可能有未提交改动，不能覆盖。
- 命令输出和测试日志很长。
- 代码修改后上下文会过期。
- LSP、搜索、文件读取、Git diff 需要协同。

策略：

- 先用 `rg` / 文件索引定位，再读关键片段。
- 每次写入前检查当前 diff。
- 保留修改文件清单和关键行位置。
- 测试失败只保留错误附近日志。
- 对仓库规则使用 `AGENTS.md` / 项目记忆文件。
- 对长任务定期 compact，保留目标、改动、验证结果和下一步。
- 子 Agent 只返回摘要，不把探索历史全部倒回主上下文。

面试中可以说：编码 Agent 的上下文工程核心是“相关性 + 新鲜度 + 可验证性”。读错旧文件或漏读测试，比上下文少一点更危险。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/05_Agent%E8%AE%B0%E5%BF%86%E4%B8%8E%E4%B8%8A%E4%B8%8B%E6%96%87%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L499)，来源许可：GPL-3.0。

<a id="k67062561dd64"></a>

## 编码 Agent 的工程能力应如何分层？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

编码 Agent 与 AgentOS 工程系统的核心价值，是把大模型从“代码建议器”升级为“可受控的软件工程任务执行器”和“可长期运行的智能工作台”。Claude Code、Codex、Cursor、Devin、Jules、OpenClaw 等项目都可以作为案例来理解这一趋势，但面试中更重要的是抽象出通用架构能力，而不是记住某个产品的命令或术语。

这类系统不只是补全一段函数，而是可以围绕一个目标执行完整工程闭环：

```math
\text{理解需求} \rightarrow \text{读取代码} \rightarrow \text{制定计划} \rightarrow \text{编辑文件} \rightarrow \text{运行测试} \rightarrow \text{修复错误} \rightarrow \text{总结交付}
```
编码 Agent 的关键能力包括：

- 仓库级代码理解。
- 文件读写和增量编辑。
- Shell 命令执行。
- 搜索、索引和 LSP 语义能力。
- Git diff、commit、PR、review。
- 项目规则和记忆加载。
- 权限审批和沙箱。
- 长任务上下文压缩和恢复。
- 子 Agent 并行探索。
- 工具调用 tracing 和成本统计。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/02_%E7%BC%96%E7%A0%81Agent%E4%B8%8EAgentOS%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L59)，来源许可：GPL-3.0。

<a id="kfb5a17e21208"></a>

## 编码 Agent 的效果与成本应如何一起验收？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

本章的评测只围绕编码 Agent：issue 修复、测试、diff、代码质量、仓库权限和工程交付。通用 Agent Benchmark、Eval Harness、AgentOps 和事故响应，见 [06_Agent安全评测与AgentOps高频考点.md](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/06_Agent安全评测与AgentOps高频考点.md)。

编码 Agent 评估应该同时看任务成功、工程质量、安全和成本。

指标包括：

- Issue 修复成功率。
- 测试通过率。
- 编译/lint 通过率。
- diff 大小和侵入性。
- 是否覆盖边界 case。
- 是否引入回归。
- 人工 review 通过率。
- 平均任务时长。
- 工具调用次数。
- token 和费用。
- 权限请求次数。
- 失败恢复能力。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/02_%E7%BC%96%E7%A0%81Agent%E4%B8%8EAgentOS%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L695)，来源许可：GPL-3.0。

<a id="k2a4ce22246e2"></a>

## 背景复盘 fork 为什么要限制工具集？

背景复盘 fork 是指任务结束后，另起一个受限 Agent 进程或子任务来总结经验、写入记忆或更新 Skill。

必须限制工具集，原因是：

- 复盘任务不应该执行 Shell、浏览器点击、发消息等副作用工具。
- 复盘上下文可能包含不可信网页和工具输出。
- 复盘目标是知识整理，不是继续完成原任务。
- 后台任务无人监督，风险更高。
- 限制工具能降低成本、减少跑偏。

推荐权限：

| 工具类型 | 是否允许 |
| --- | --- |
| memory add/update | 允许，但需脱敏和 scope |
| skill read/update | 允许，最好限定 agent-created |
| file read | 仅允许特定知识目录 |
| shell / browser / email | 默认禁止 |
| web search | 谨慎，通常不需要 |
| delete | 禁止，改用 archive |

面试金句：后台复盘 fork 应该像“图书管理员”，不是“另一个无人值守执行者”。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/09_%E8%87%AA%E8%BF%9B%E5%8C%96Agent%E4%B8%8E%E5%A4%9A%E5%B9%B3%E5%8F%B0%E8%BF%90%E8%A1%8C%E6%97%B6%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L437)，来源许可：GPL-3.0。

<a id="k88272915b0c9"></a>

## 自我介绍，并选择一个最熟悉的 Agent 项目做深入介绍。

**回答：**

二面的自我介绍应比一面更聚焦判断与取舍。用约一分钟交代背景和岗位相关经历，然后主动选择一个自己拥有关键设计权、数据最完整的 Agent 项目，不要同时铺开多个浅项目。

项目深挖建议用“业务不变量 -> 为什么需要 Agent -> 受控执行架构 -> 最难问题 -> 评测与复盘”组织。先说明哪些步骤可以确定性 Workflow 完成，哪些步骤需要模型根据动态 Observation 规划；再讲状态、工具、知识、权限和停止条件；最后给出失败案例，例如工具误选、上下文污染、重复副作用或长任务中断，以及如何通过 schema、状态机、幂等、checkpoint 和回归集修复。

个人贡献必须落到代码和决策边界：负责哪些服务、设计了什么接口、推动了哪组实验、排除了什么错误假设。指标需说明定义、基线、样本和观测窗口。没有上线数据时可以报告离线任务集和故障注入结果，但要区分两者。

一个成熟收口是：Agent 的价值不在“自主”这个词，而在不确定环境中通过受约束的多步决策完成任务；生产质量来自模型、工具契约、状态管理和评测共同作用。

<a id="pinduoduo-ai-agent-20260816-q20"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E6%8B%BC%E5%A4%9A%E5%A4%9A%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L487)，来源许可：GPL-3.0。

<a id="kf573cbebd8ca"></a>

## 自我介绍，重点讲一下实习经历和 AI Agent 相关项目。

**回答：**

这道题不是让候选人复述简历，而是要求在两三分钟内建立一条可以被继续追问的技术主线。推荐按照“个人定位 -> 一段最相关经历 -> 一个 Agent 项目 -> 与岗位的匹配点”展开，并且只讲自己真正做过的内容。

一个稳妥的结构是：先用一句话说明专业背景和技术方向；再选一段与岗位最相关的实习，交代业务目标、团队上下游和个人职责；然后用一个 Agent 项目说明输入、决策循环、工具、知识、状态和评测闭环；最后总结自己在模型应用与后端工程之间的能力连接。不要把“使用 LangChain、向量库、Redis”当成项目价值，技术栈必须与具体问题绑定。

项目介绍至少要回答四个问题：系统为谁解决什么问题；为什么这里需要 Agent 而不是固定 Workflow；自己负责了哪个可验证模块；上线前后用什么指标判断有效。工具调用正确率、任务完成率、端到端延迟、单任务成本等数字必须来自真实日志，并说明样本范围、统计口径和观测窗口，不能临场编造。

面试收口可以落到岗位匹配：自己既理解 RAG、上下文和工具调用的模型侧机制，也能处理并发、幂等、可观测性和故障恢复等工程问题。这样后续问题会自然进入项目深挖，而不是停留在框架名词层面。

<a id="pinduoduo-ai-agent-20260816-q2"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E6%8B%BC%E5%A4%9A%E5%A4%9A%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L162)，来源许可：GPL-3.0。

<a id="kfbd2d884ebc5"></a>

## 自我维护型 Skill 系统如何做评分、合并、归档和回滚？

推荐生命周期：

```text
created -> active -> stale -> archived -> restored / deleted by human
```

评分维度：

- 最近使用时间。
- 使用频率。
- 成功任务占比。
- 是否被用户显式调用。
- 是否和其他 Skill 重复。
- 是否依赖失效工具。
- 是否包含过时链接或命令。
- 是否存在安全风险。

合并策略：

- 只合并作用域相同、目标相似、内容互补的 Skill。
- 保留来源和变更记录。
- 对合并结果生成 diff 和报告。
- 高价值 Skill 需要人工确认。

归档策略：

- pinned / 官方 / 内置 Skill 不自动归档。
- 用户创建或 Agent 创建的低使用 Skill 可归档。
- 归档可恢复，不直接删除。
- 归档原因写入 metadata。

回滚策略：

- 每次修改 Skill 前保存版本。
- 维护报告记录变更。
- 支持按 skill 或按 curator run 恢复。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/09_%E8%87%AA%E8%BF%9B%E5%8C%96Agent%E4%B8%8E%E5%A4%9A%E5%B9%B3%E5%8F%B0%E8%BF%90%E8%A1%8C%E6%97%B6%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L398)，来源许可：GPL-3.0。

<a id="k6fb1a6e45c96"></a>

## 自进化 Agent 和普通长期记忆 Agent 有什么区别？

| 维度 | 普通长期记忆 Agent | 自进化 Agent |
| --- | --- | --- |
| 核心目标 | 记住用户偏好和历史事实 | 从历史中改进能力和流程 |
| 写入对象 | Memory 为主 | Memory、Skill、Policy、Eval Case、Tool Hint |
| 更新方式 | 交互后写入记忆 | 后台复盘、评分、合并、归档、主动修订 |
| 风险 | 记忆污染、隐私泄露 | 错误能力固化、自我强化偏差、权限扩张 |
| 工程要求 | 检索、CRUD、权限、遗忘 | Curator、版本、回滚、审计、质量评分 |

一句话区分：

- 长期记忆 Agent 让系统“记得过去”。
- 自进化 Agent 让系统“从过去中改进未来行为”。

面试中可以强调：自进化不等于让 Agent 随意改自己，而是在严格边界内对可审计、可回滚的知识资产进行维护。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/09_%E8%87%AA%E8%BF%9B%E5%8C%96Agent%E4%B8%8E%E5%A4%9A%E5%B9%B3%E5%8F%B0%E8%BF%90%E8%A1%8C%E6%97%B6%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L68)，来源许可：GPL-3.0。

<a id="k3979181af259"></a>

## 节课与学习节奏

每节建议安排一次机制学习、一次实验和一次口述复盘。已有后端经验的读者可用两到三周完成首轮；时间安排只是建议，不以天数代替验收。

| 课次 | 核心问题 | 必交产物 |
| --- | --- | --- |
| 1 | 哪些部分需要 Agent | 需求边界、模块图与权威数据表 |
| 2 | 一个请求怎样跑完 | 状态机、事件轨迹与取消策略 |
| 3 | 如何规划、路由与恢复 | 路由测试集、图定义与恢复实验 |
| 4 | 文档怎样变成证据 | 解析抽检、切分对照和入库契约 |
| 5 | 怎样做好混合检索 | 双路召回、RRF 与重排实验 |
| 6 | 怎样证明回答可靠 | 可回答性、引用与延迟评估 |
| 7 | 怎样正确地记住用户 | 读写分离、冲突与删除实验 |
| 8 | 工具、Skill 与协议怎样配合 | 工具 Schema、Skill 包与协议边界图 |
| 9 | 怎样限制错误行动与成本 | 注入测试、权限断言与预算策略 |
| 10 | 长期助手怎样持续运行 | Gateway/Runtime 分工与记忆维护方案 |
| 11 | 怎样完成一次可靠预约 | 确认、幂等、并发与故障恢复实验 |
| 12 | 怎样把项目变成面试证据 | 复现实验、指标卡和答辩记录 |

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%83%AD%E9%97%A8AI%E5%AD%A6%E4%B9%A0%E6%A0%B8%E5%BF%83%E8%AF%BE%E7%A8%8B%E4%B8%8E%E6%95%99%E7%A8%8B/16_AI_Agent%E5%B7%A5%E7%A8%8B%E5%AE%9E%E6%88%98%EF%BC%9A%E5%9F%BA%E7%A1%8080%E9%97%AE%E5%AD%A6%E4%B9%A0AI%20Agent.md#L42)，来源许可：GPL-3.0。

<a id="kc1f4bb4f4f12"></a>

## 行动能力扩大后，系统需要管理哪些权限风险？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

本节只做风险地图和高频概念索引；Guardrails、Prompt Injection、权限沙箱、Benchmark、Eval Harness、Tracing、灰度发布、事故响应和 AgentOps 的工程细节，统一见 [06_Agent安全评测与AgentOps高频考点.md](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/06_Agent安全评测与AgentOps高频考点.md)。企业级平台架构与产品落地见 [07_企业级Agent平台与产品落地高频考点.md](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/07_企业级Agent平台与产品落地高频考点.md)。

Agent 可以调用工具，因此它不仅会“说错话”，还可能“做错事”。安全边界比普通 Chatbot 更重要。

高风险包括：

- 删除或覆盖文件。
- 泄露密钥、隐私、商业数据。
- 执行恶意命令。
- 调用生产 API。
- 发送邮件或消息。
- 下单、转账、审批。
- 被网页或工具返回内容 prompt injection。

因此生产级 Agent 必须有：

- 最小权限。
- 沙箱。
- 工具审批。
- 审计日志。
- 输入输出 guardrails。
- 敏感信息检测。
- 速率和预算限制。
- 回滚和人工介入。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/01_AIGC%E6%97%B6%E4%BB%A3AI%20Agent%E5%9F%BA%E7%A1%80%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L699)，来源许可：GPL-3.0。

<a id="k4122d2e969b6"></a>

## 视频 Agent 与单一生成或编辑模型有什么本质区别？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐⭐ (5/5)**

单一生成或编辑模型解决的是一次映射：接收文本、图像、视频或控制条件，输出一次生成结果。视频 Agent 位于这些模型之上，负责围绕用户目标连续做决策。它需要观察当前素材和执行结果，选择下一步操作，并根据反馈调整计划。

这条边界可以从四个能力判断：

1. **理解当前状态。** 不只解析文字指令，还要识别素材中的主体、镜头、动作、时间范围和已有问题。若用户要求“只修改第二个镜头中的外套颜色”，系统必须先定位镜头、主体和编辑作用域。
2. **维护目标与约束。** Agent 要区分需要改变的内容和必须保持的内容，并在多步执行中持续检查角色身份、非编辑区域、时长和用户已确认的选择。
3. **规划并执行动作。** 根据任务依赖选择生成、分割、跟踪、局部编辑、续写、配音或剪辑工具，而不是把所有要求重新塞给一个模型。
4. **观察结果并调整。** 每次执行后检查目标是否满足；失败时可以修改参数、更换工具、回退到旧版本，必要时向用户确认。

因此，能调用多个模型并不自动等于 Agent。固定顺序执行的一组工具更接近工作流；只有系统能依据中间状态改变后续动作，才具备基本的 Agent 决策特征。反过来，视频 Agent 也不一定采用多 Agent 架构，单个规划器同样可以管理多种视频工具。

> **面试速答**：生成或编辑模型负责完成一次条件映射，视频 Agent 则围绕目标维护状态，规划和调用工具，观察执行结果，再决定继续、修正、回退还是请求确认。区分关键不是模型数量，而是系统能否根据中间结果动态改变后续动作。

参考资料：[ReAct](https://arxiv.org/abs/2210.03629)、[StoryAgent](https://arxiv.org/abs/2411.04925)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E8%A7%86%E9%A2%91%E5%9F%BA%E7%A1%80%EF%BC%88%E7%B2%BE%E5%8D%8E%E7%89%88%EF%BC%89/06_AI%E8%A7%86%E9%A2%91%E7%BB%9F%E4%B8%80%E7%B3%BB%E7%BB%9F%E3%80%81%E5%88%9B%E4%BD%9C%E5%B7%A5%E4%BD%9C%E6%B5%81%E4%B8%8E%E6%9C%AA%E6%9D%A5%E8%B6%8B%E5%8A%BF.md#L319)，来源许可：GPL-3.0。

<a id="k40a87aa99e9e"></a>

## 视频 Agent 如何在生成失败或需求变化后决定重生成、局部编辑、续写还是人工确认？

**难度评分：⭐⭐⭐⭐⭐ (5/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

修复路径不能只按“问题大小”选择，还要同时看问题的作用范围、现有内容的保留价值、操作是否可验证，以及自动判断的可信度。基本原则是选择**可验收、可回滚且对已确认内容扰动最小的充分操作**。

**先确定问题位于哪一层**

- 脚本事件、整体风格或镜头规划错误，根因位于上游。继续做局部修补容易累积不一致，应回到分镜或镜头生成阶段。
- 错误能稳定定位到对象、区域和时间段，而且其他内容已经通过验收，优先局部编辑。局部错误不代表一定适合编辑；若模型无法可靠保持非目标区域，重生成可能更稳。
- 已有内容正确，只缺少后续动作或时长时，可以续写。前提是镜头尾部状态足够稳定，且新事件不要求改写前面的因果关系。
- 指令含糊、条件互斥、修改范围不清，或自动评估置信度不足时，应让用户确认。系统不能把“多试几次”当作解决语义冲突的方法。

**再比较修复成本与连带影响**

局部编辑的计算量未必最低，但通常能保留更多已确认内容；整段重生成实现简单，却可能引入新的身份、构图和运动变化。若同一镜头已经连续修补多次，局部补丁之间开始相互影响，回到较早版本重新生成往往比继续叠加修改更可靠。

**执行后同时检查改变与保持**

复核不能只看目标问题是否消失，还要检查非编辑区域、角色身份、镜头节奏和上下游衔接。通过后生成新版本并更新项目状态；未通过则回滚，不能让失败结果继续进入配音、组接等下游阶段。需求变化较大时，建立新分支通常比直接覆盖已确认版本更安全。

> **面试速答**：先定位问题属于脚本、镜头还是局部区域，再结合保留价值、可编辑性和判断置信度选择操作。局部且可稳定约束的问题优先编辑，已有前缀正确且只缺后续内容时续写，上游或全局错误应重生成；条件冲突和高影响修改交给用户确认。任何修复都要同时验证目标变化和非目标保持，并支持版本回滚。

参考资料：[ReAct](https://arxiv.org/abs/2210.03629)、[AgentBoard](https://arxiv.org/abs/2401.13178)、[Crayotter](https://arxiv.org/abs/2606.07636)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E8%A7%86%E9%A2%91%E5%9F%BA%E7%A1%80%EF%BC%88%E7%B2%BE%E5%8D%8E%E7%89%88%EF%BC%89/06_AI%E8%A7%86%E9%A2%91%E7%BB%9F%E4%B8%80%E7%B3%BB%E7%BB%9F%E3%80%81%E5%88%9B%E4%BD%9C%E5%B7%A5%E4%BD%9C%E6%B5%81%E4%B8%8E%E6%9C%AA%E6%9D%A5%E8%B6%8B%E5%8A%BF.md#L464)，来源许可：GPL-3.0。

<a id="kdcc67bb3fcdb"></a>

## 视频 Agent 如何把创作需求转化为可执行的任务计划？

**难度评分：⭐⭐⭐⭐⭐ (5/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

任务计划不能只是把长指令拆成若干短 prompt。它需要明确每一步处理什么对象、依赖哪些输入、调用什么能力，以及完成后如何验收。

以“把人物外套改成红色，再将镜头延长 3 秒，其他内容保持不变”为例，较稳妥的计划是：先定位人物和目标镜头，得到跨帧一致的编辑区域；再执行局部换色并检查背景与动作是否保持；局部编辑通过后，才以新镜头的尾部状态进行续写。若先续写再换色，编辑范围会扩大，跨帧保持也更难。

规划时主要处理四类信息：

- **目标与验收条件**：把“要什么”和“怎样算完成”写清楚，例如目标颜色、延长时长以及非编辑区域保持。
- **依赖与执行顺序**：将任务组织成有依赖关系的步骤。后续步骤应引用前一步确认过的资产，而不是重复解析原始需求。
- **工具与参数绑定**：根据作用范围和约束强度选择工具。局部外观修改需要分割或跟踪提供空间约束，视频延展则需要镜头尾部状态和运动上下文。
- **异常分支**：预先定义工具失败、结果不合格和条件冲突时的处理方式。低风险问题可以自动重试；目标含糊或修改范围可能扩大时，应暂停并询问用户。

完整的执行闭环如图6-2所示。每次工具调用都会产生新的可观察状态，规划器据此继续执行或更新计划，而不是一次生成整条动作序列后盲目跑到底。

  <img src="./imgs/ch06/fig-6-02-video-agent-execution-loop.png" alt="视频 Agent 从用户目标与约束出发，理解素材和项目状态、规划任务图、选择工具执行并检查结果，再根据状态继续、重规划、回退或请求人工确认" width="780">
  <p>图6-2 视频 Agent 从需求理解到执行反馈的决策闭环</p>

> **面试速答**：视频 Agent 应先把需求转成目标、保持约束和验收条件，再按依赖关系生成任务图，为每个步骤绑定工具、输入输出和异常分支。执行过程中每完成一步都要检查结果并回写状态；条件冲突或高影响修改不能靠自动重试掩盖，应及时请求用户确认。

参考资料：[ReAct](https://arxiv.org/abs/2210.03629)、[UniVA](https://arxiv.org/abs/2511.08521)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E8%A7%86%E9%A2%91%E5%9F%BA%E7%A1%80%EF%BC%88%E7%B2%BE%E5%8D%8E%E7%89%88%EF%BC%89/06_AI%E8%A7%86%E9%A2%91%E7%BB%9F%E4%B8%80%E7%B3%BB%E7%BB%9F%E3%80%81%E5%88%9B%E4%BD%9C%E5%B7%A5%E4%BD%9C%E6%B5%81%E4%B8%8E%E6%9C%AA%E6%9D%A5%E8%B6%8B%E5%8A%BF.md#L338)，来源许可：GPL-3.0。

<a id="k607e64e27072"></a>

## 让你设计一个从数据中提取实体的关系的agent你会怎么设计？

**回答：**

首先确认输入数据类型、领域和输出契约：文本、表格还是数据库记录，允许哪些实体和关系类型，是否需要否定、时间或条件修饰，以及哪些结果必须人工复核。题目中的“实体的关系”可以理解为同时抽取实体及其关系，设计中应分别给出产物和验证标准。

可采用“解析与定位 → 实体提及抽取 → 候选实体检索与链接 → 关系抽取 → 约束与证据校验 → 复核 → 版本化入库”的工作流。解析保留文档 ID、版本、段落和字符区间；分块时保留标题和必要邻近上下文；实体提及保留原文名称与位置，再关联规范实体 ID，不直接用名称作为永久主键。

模型按 schema 输出候选实体与关系，关系包含主体、谓词、客体和证据区间，必要时记录否定、时间与条件。代码检查 ID 引用是否存在、类型是否符合规则、证据区间是否有效，模型或人工再检查文本是否真正支持该关系。例如“尚无证据表明药物 A 可治疗疾病 B”不能抽成肯定治疗关系。

Agent 只在需要决策的环节动态调用工具，例如检索术语定义、补读交叉引用、对低置信度链接请求专家确认；固定格式校验和入库采用确定性逻辑。约束调用次数、权限和输出规模，为任务和写入设置幂等键，保存节点状态与产物引用，以支持失败恢复。

候选事实和已确认事实分开管理，入库采用稳定实体 ID 与事实身份规则，保留证据、抽取器和本体版本。矛盾事实应记录冲突及适用条件，不直接覆盖；错误合并应可撤回。每次更新后用人工标注集评估实体、关系、链接以及端到端查询，并把失败案例纳入回归。

<a id="01ai-kg-intern-20261021-de81855b-q15"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%9B%B6%E4%B8%80%E4%B8%87%E7%89%A9%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L262)，来源许可：GPL-3.0。

<a id="k7ac9bf55176c"></a>

## 记忆从候选事实到失效删除要经过哪些阶段？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

Agent Memory 不是简单的“保存一句话”，而是一个生命周期：

```math
\text{Ingest} \rightarrow \text{Filter} \rightarrow \text{Extract} \rightarrow \text{Normalize} \rightarrow \text{Store} \rightarrow \text{Retrieve} \rightarrow \text{Use} \rightarrow \text{Update / Forget}
```
1. **Ingest**

   接收用户消息、工具结果、任务状态、反馈和外部事件。

2. **Filter**

   判断是否有记忆价值，过滤闲聊、临时信息、敏感信息和不可信内容。

3. **Extract**

   提取结构化记忆，例如偏好、事实、约束、任务经验。

4. **Normalize**

   标准化格式，添加 user_id、source、timestamp、confidence、scope、ttl、topic。

5. **Store**

   写入合适存储：关系库、向量库、图数据库、事件日志等。

6. **Retrieve**

   根据当前任务检索相关记忆。

7. **Use**

   将记忆以有边界的方式注入上下文。

8. **Update / Forget**

   合并、修改、降权、归档或删除记忆。

高质量 Memory 系统最重要的是“选择性”。不是所有内容都值得记住，错误记忆比没有记忆更危险。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/05_Agent%E8%AE%B0%E5%BF%86%E4%B8%8E%E4%B8%8A%E4%B8%8B%E6%96%87%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L265)，来源许可：GPL-3.0。

<a id="k10892f22b918"></a>

## 记忆分层中，长期记忆跟短期记忆在agent中具体扮演什么功能？

**回答：**

按需调用时先由模型或路由器判断是否需要记忆，再用实体/关键词/向量/时间/权限联合检索，Rerank 后只注入少量证据。当前用户明确指令优先于历史推断，冲突要显式确认，敏感记忆要最小化和可撤回。

<a id="tencent-llm-collection-20260903-q67"></a>

**相关解释：** [有无搭建过完整的 agent，memory 管理怎么做的](Agent%E3%80%81%E5%B7%A5%E5%85%B7%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81-05.md#k069945a0be1a)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E8%85%BE%E8%AE%AF%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1013)，来源许可：GPL-3.0。

<a id="k4dcf80b2fa1a"></a>

## 记忆模块是怎么设计的？

**回答：**

Memory 不是把所有历史消息无限追加到 Prompt，而是把历史信息按用途和时效分层。

- **短期记忆：** 当前会话消息、工具结果、任务状态和未完成计划，放在 checkpoint/session store 中，服务于当前任务恢复。
- **长期语义记忆：** 用户偏好、稳定事实、历史经验和重要事件，以结构化记录或向量索引保存，带时间、置信度、来源和版本。
- **工作记忆：** 当前任务的目标、约束、已完成步骤、待办和错误，优先使用结构化 state，而不是让模型从长文本中猜。

写入长期记忆前要做重要性判断、去重、冲突检测、敏感信息过滤和用户授权；读取时按当前 Query、租户、权限和时间衰减检索，经过 Rerank 和 token 预算截断。摘要要保留事实、来源和不确定性，不能把模型猜测写成用户事实。

记忆系统还要支持删除、过期、纠错、审计和隔离。评估它对任务成功率、重复询问率、上下文 token、错误记忆引用和隐私风险的真实贡献，而不是只看“记住了多少内容”。

<a id="alibaba-agent-20260802-q11"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L931)，来源许可：GPL-3.0。

<a id="k103c22c9471f"></a>

## 记忆污染和隐私泄露有哪些风险？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

主要风险：

- **错误记忆**：模型把猜测写成事实。
- **过期记忆**：旧偏好、旧规则继续影响决策。
- **恶意记忆**：用户或网页注入“以后忽略安全规则”。
- **跨用户串线**：A 用户记忆被 B 用户检索到。
- **敏感信息长期化**：密码、token、身份证号被写入长期记忆。
- **RAG 与 Memory 混淆**：把外部文档中的描述当成用户偏好。
- **过度个性化**：记忆使用不透明，让用户感到被监视。

治理策略：

- 写入前做敏感信息检测。
- 只有用户明确或高置信信息进入长期记忆。
- 记忆记录必须有 scope、source、confidence、sensitivity。
- 工具输出和网页内容默认不可信。
- 用户可查看、编辑、删除个人记忆。
- 不同用户、租户、Agent 的记忆物理或逻辑隔离。
- 定期清理低价值和过期记忆。
- 高风险记忆写入需要人工确认或策略审批。

面试中可以强调：Agent Memory 是产品体验能力，也是数据安全能力。记忆系统没有治理，越强越危险。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/05_Agent%E8%AE%B0%E5%BF%86%E4%B8%8E%E4%B8%8A%E4%B8%8B%E6%96%87%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L614)，来源许可：GPL-3.0。

<a id="k157af1222511"></a>

## 讲一下Agent中的短期记忆和长期记忆分别怎样存储？

<a id="batch4-p1-q8"></a>

### 补充说明

<a id="batch4-p2-q8"></a>

**相关解释：** [Agent常见模式（ReAct/Plan and Execute等）](../15-%E5%89%8D%E7%AB%AF%E4%B8%8E%E6%B5%8F%E8%A7%88%E5%99%A8/React%E4%B8%8E%E7%BB%84%E4%BB%B6%E7%8A%B6%E6%80%81-01.md#k93a12d0c9256)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%BF%AB%E6%89%8B%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L187)，来源许可：GPL-3.0。
- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%BF%AB%E6%89%8B%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L276)，来源许可：GPL-3.0。

<a id="kc299a8f37c55"></a>

## 讲一下上下文工程（Context Engineering），Agent 的记忆（Memory）是怎么做的？

**回答：**

上下文工程是指围绕模型上下文窗口进行信息选择、组织、压缩、注入和验证的工程体系。它不只是 prompt engineering。Prompt engineering 更关注指令怎么写；context engineering 更关注在每一轮模型调用时，应该把哪些任务目标、用户状态、历史对话、检索证据、工具结果、约束条件和输出格式放进去，以及如何控制成本和噪声。

一个 Agent 的上下文通常包括几类信息：系统指令、当前用户输入、短期对话历史、长期记忆、RAG 检索证据、工具调用结果、任务计划、执行状态、权限和安全约束。上下文工程要解决的问题是：哪些信息必须保留，哪些可以摘要，哪些应该检索，哪些应该丢弃，哪些需要结构化。

Agent Memory 可以分为短期记忆和长期记忆。短期记忆通常是当前会话内的历史消息、任务计划、已调用工具结果和中间状态。由于上下文窗口有限，短期记忆一般需要滑动窗口、摘要压缩、重要事件提取。长期记忆则是跨会话保存的用户偏好、稳定事实、项目配置、历史任务结果、失败经验等，通常存到数据库、向量库或结构化 profile 中。

从类型上还可以分为 semantic memory、episodic memory 和 procedural memory。Semantic memory 存稳定知识和用户偏好；episodic memory 存某次交互或任务经历；procedural memory 存执行流程、工具使用方法、skill 或工作流。

实现时通常有四个动作：写入、检索、压缩和遗忘。写入时要判断哪些信息值得长期保存，不能把所有对话都写入；检索时要根据当前任务从记忆库召回相关内容；压缩时把长历史变成结构化摘要；遗忘时处理过期、冲突、敏感或低价值记忆。

关键风险是记忆污染和隐私问题。错误记忆会长期影响 Agent 行为，敏感信息也不能随意持久化。因此需要置信度、来源、时间戳、权限、可删除机制和人工反馈。面试总结可以说：Agent Memory 不是把聊天记录塞回 prompt，而是一个有读写策略、检索策略、压缩策略、冲突解决和安全边界的状态管理系统。

<a id="bytedance-ai-agent-hard-20260602-q7"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%AD%97%E8%8A%82%E8%B7%B3%E5%8A%A8%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L452)，来源许可：GPL-3.0。

<a id="kf9fb8c197e9a"></a>

## 讲一下你怎么理解Harness？

**回答：**

Harness 是模型外部的运行与治理环境，决定 Agent 看见什么上下文、能调用哪些工具、动作如何执行、状态如何持久化、失败怎样恢复以及结果如何验证。模型负责给出概率性的下一步决策，Harness 把这种决策约束在真实软件系统可以接受的边界内。

一个完整 Harness 通常包括：

- Context Builder：系统规则、任务状态、近期历史、Memory/RAG 和工具的选择与压缩；
- Tool Runtime：schema、权限、沙箱、超时、幂等、限流和副作用确认；
- State/Checkpoint：目标、计划、步骤、artifact、错误和审批状态；
- Control Loop：Workflow、ReAct、Planner-Executor、最大步数、预算和终止条件；
- Reliability/Safety：重试、熔断、降级、回滚、人工接管、注入防护和密钥隔离；
- Trace/Eval：模型与 Prompt 版本、工具轨迹、最终状态、成本、延迟、判分和回归门禁。

需要区分两个常见语境：Runtime Harness 负责线上运行和控制，Eval Harness 负责构造任务/环境、回放轨迹、评分和版本比较。二者可以共享 trace、沙箱和验证器，但不是同一个概念。

Harness 提升复杂任务能力，不是让模型参数突然变强，而是把长任务外化为可见状态，把真实工具结果反馈给模型，把错误限制在可恢复步骤里，并用验证器替代“模型自称完成”。同一个模型放进不同 Harness，任务完成率、成本和安全性可以有显著差异。

<a id="xiaohongshu-agent-dev-20260812-q7"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%B0%8F%E7%BA%A2%E4%B9%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L969)，来源许可：GPL-3.0。

<a id="k022b8fa7be8e"></a>

## 讲一下长时记忆和短时记忆的底层实现方式？

**回答：**

短时记忆维持当前任务连续性，长时记忆支撑跨会话复用。二者底层都不等于“把聊天记录放进向量库”，而是不同生命周期的数据系统。

**短时/工作记忆**通常由三部分组成：最近若干轮原始消息；结构化任务状态，如目标、计划、已完成步骤、工具结果和待确认项；较早历史的摘要与事件引用。状态可放在进程内、Redis、关系数据库或 Workflow checkpoint store 中，每次模型调用前由 Context Builder 按 Token 预算投影进 Prompt。KV Cache 只是推理加速缓存，不是 Agent Memory。

**长时记忆**通常按类型分库存储：用户稳定偏好和身份事实适合关系表/画像 KV；具体历史事件适合 append-only event log；自然语言经验适合向量 + 全文混合索引；实体关系复杂时才考虑图数据库。每条记录至少带 `tenant/user/project scope`、来源、时间、置信度、有效期、权限和原始事件引用。

生命周期是：候选提取 -> 重要性/敏感性过滤 -> 去重与结构化 -> 写入 -> 按需检索 -> 相关性/时效/权限重排 -> 注入 -> 冲突更新或遗忘。当前用户明确表达优先于旧偏好，业务主库实时状态优先于历史摘要，低置信模型推断不能覆盖用户事实。

长期记忆的质量要看召回后是否提高任务成功率、减少重复询问，同时监控错误记忆引用、跨用户串线和隐私删除能力。记忆的目标不是保存最多，而是在正确作用域内保留可纠正、可追溯、未来仍有价值的状态。

<a id="xiaohongshu-agent-dev-20260812-q10"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%B0%8F%E7%BA%A2%E4%B9%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1027)，来源许可：GPL-3.0。

<a id="k5f097956a01e"></a>

## 讲讲agent中的反思模块逻辑

**回答：**

反思模块应消费执行记录与验证证据，输出可执行的修正决策。输入包括目标约束、当前状态、调用参数、工具返回、失败分类和剩余预算；输出可以是补充检索、修正参数、换工具、有限重规划、询问用户或终止。

例如超时后不能确认写入结果，应先核对幂等键对应任务；检索无证据时补检索；输出违背已知约束时修正计划并重新验收。不是所有失败都应该再次调用语言模型。

设置反思次数、总步骤和成本上限，对同状态同动作的重复检测循环。评测反思后的净恢复率、错误修复率和额外延迟，而不是反思文本写得是否像在自我批评。

![Agent 失败证据与恢复动作](https://raw.githubusercontent.com/WeThinkIn/AIGC-Interview-Book/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/imgs/jd-damodel-20251211-20260205/02_Agent失败诊断.png)

图 2：失败诊断沿知识、检索、推理和执行分层，恢复动作由可观测证据触发。写操作状态未知时，先核对业务结果；重复生成相同工具调用可能把一次超时放大成重复订单。

<a id="jd-damodel-20251211-20260205-p7-q15"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E4%BA%AC%E4%B8%9C%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1168)，来源许可：GPL-3.0。

<a id="k4c9e41ffa405"></a>

## 讲讲对 mcp 的理解

**回答：**

MCP 是连接 AI Host/Client 与外部 Server 能力的开放协议，常见能力包括 Tools、Resources 和 Prompts，并通过初始化握手协商版本与能力。模型是否决定调用工具属于 Agent Runtime 或模型 API；MCP 负责发现、调用、返回和生命周期，不负责替业务定义正确性。

调用链通常是 Host 过滤权限并把工具 Schema 暴露给模型，模型生成结构化调用，Client 通过 JSON-RPC 发送 `tools/call`，Server 执行并返回结构化内容，Host 校验大小、权限、可信度和副作用后再写回模型。远程 MCP 还要处理授权、供应链、Prompt Injection、超时、幂等和审计。

<a id="tencent-llm-collection-20260903-q58"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E8%85%BE%E8%AE%AF%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L928)，来源许可：GPL-3.0。

<a id="ke4441fc42eb3"></a>

## 设计一个"多人协作的 Agent 平台"，支持多个用户同时使用，每个用户可以创建多个 Agent，Agent 之间可以协作。——多租户隔离怎么做？Agent 之间的通信怎么设计？权限控制怎么实现？

**回答：**

我会先定义平台边界：用户创建 Agent 配置和工具权限，提交任务后由编排器调度多个 Agent；Agent 可以并行执行子任务，但共享状态和外部副作用必须受控。整体采用“控制面中心化、执行面可水平扩展”的架构。

核心资源层级为 `tenant -> user -> workspace -> agent -> task -> run -> step`。每条资源都带 `tenant_id`，服务端从认证身份推导租户，禁止信任客户端传入的租户字段。数据库使用租户条件、行级策略或独立 schema/实例隔离；缓存、对象存储、向量索引、队列和日志同样使用租户命名空间。高敏租户可以采用物理隔离，普通租户使用逻辑隔离并通过自动化测试验证越权不可见。

Agent 通信不建议直接互相发送任意自然语言，而采用带 schema 的消息总线或任务协议：

```text
Message {
  message_id, tenant_id, task_id, parent_step_id,
  sender_agent, receiver_agent, schema_version,
  type, payload, evidence_refs, deadline,
  idempotency_key, state_version
}
```

编排器维护任务 DAG 或状态图，能并行的子任务放入队列；子 Agent 返回结构化结果、证据、置信度和副作用记录；Reducer 按任务版本合并，冲突进入仲裁 Agent 或人工队列。消息至少一次投递时，消费端用 `message_id` 和幂等键去重；需要严格顺序的共享资源采用单写者、版本号或事务，而不是让多个 Agent 直接覆盖同一状态。

权限分为用户权限、Agent 权限、工具权限和数据权限。使用 RBAC 解决角色授权，用 ABAC 表达租户、资源归属、环境、数据等级和时间等条件；每一次工具调用都在服务端重新鉴权，不能因为模型选择了工具就放行。工具凭证采用短期、最小权限 token，Agent 只能获得任务所需范围；文件、数据库、网络和代码执行进入沙箱。高风险写操作需要审批、额度、双人复核或策略引擎门控。

平台还要具备配额、限流、超时、取消、审计、密钥轮换、敏感信息脱敏和数据删除能力。可观测性要记录租户级成本、延迟、失败和资源使用，但日志默认不保存完整 Prompt、Token 或敏感工具返回。最终用租户越权测试、消息重复测试、故障恢复测试和副作用审计验证设计，而不是只画一张组件图。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/DeepSeek%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L796)，来源许可：GPL-3.0。

<a id="k97a20495f7df"></a>

## 详细区分Workflow和Agent的核心差异与适用场景

**回答：**

Workflow 是预先定义好的流程编排，Agent 是具备一定自主决策能力的任务执行系统。两者都可能调用大模型和工具，但控制权不同：Workflow 的路径主要由工程师设计，Agent 的路径部分由模型根据状态动态决定。

Workflow 的典型特征是流程固定、状态可控、失败路径明确。例如“文档上传 -> OCR -> 分块 -> 向量化 -> 检索 -> 摘要 -> 入库”，每一步做什么基本确定。它适合合规要求高、稳定性要求高、任务边界清楚的业务，比如批处理、报表生成、标准化审核、字段抽取流水线。

Agent 的典型特征是目标驱动、路径开放、工具选择动态。例如用户说“帮我分析这个商家最近订单下降的原因”，系统可能需要查数据、对比指标、生成假设、调用 BI 工具、解释异常、再生成行动建议。Agent 适合开放式、多步骤、需要探索和环境反馈的任务，但风险也更高：可能循环、误用工具、上下文漂移、成本失控。

工程上不要迷信 Agent。可控任务优先 Workflow，开放任务才引入 Agent；成熟系统往往是二者结合：外层用 Workflow 控制预算、权限、审计和停止条件，内部某些节点用 Agent 做规划、检索、工具调用或异常修复。真正的判断标准不是“听起来智能”，而是任务路径是否固定、错误成本多高、是否需要动态决策。

<a id="meituan-llm-algo-20260706-q8"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%BE%8E%E5%9B%A2%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L308)，来源许可：GPL-3.0。

<a id="kfaea0f170da1"></a>

## 详细讲解Agent系统中长短期记忆的设计逻辑，在长时对话场景下，如何实现上下文信息的动态压缩与选择性遗忘？

<a id="batch4-p2-q12"></a>

**相关解释：** [Agent常见模式（ReAct/Plan and Execute等）](../15-%E5%89%8D%E7%AB%AF%E4%B8%8E%E6%B5%8F%E8%A7%88%E5%99%A8/React%E4%B8%8E%E7%BB%84%E4%BB%B6%E7%8A%B6%E6%80%81-01.md#k93a12d0c9256)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L398)，来源许可：GPL-3.0。

<a id="k0d71a096f180"></a>

## 详细阐述大模型实现函数调用（Function Call）的完整流程，模型是如何将自然语言语义转化为标准化结构化参数的？

**回答：**

模型根据系统指令、用户目标、历史观察和工具定义生成条件分布。原生工具调用通常经过相关训练，使模型学会输出工具名称、参数及特定协议结构；具体供应商如何编码控制信息各不相同，不能假设都采用同一种特殊 Token。

可以把决策理解为在“继续回答、调用某工具、请求澄清、结束”等动作之间选择：

```math
a_t\sim\pi_\theta(a\mid x,s_t,\mathcal{T}),
```

其中 $x$ 是当前目标，$`s_t`$ 是可见状态，$\mathcal{T}$ 是允许使用的工具集合。模型基于训练中学到的语义与当前上下文判断何时需要外部信息或动作；它并不天然知道工具调用一定正确。

工具名称、描述、参数定义和互斥边界会影响选择质量。工具很多时，先按权限与任务检索候选工具，再把小集合提供给模型；确定性业务规则可以直接路由。框架负责解析并执行调用，模型负责提出动作，二者职责不同。

评测拆成“是否该调用、选哪一个、参数是否正确、执行是否成功、结果是否被正确使用”。SFT、偏好或强化学习可以改善选择策略，但生产可靠性仍依赖运行时校验、幂等、超时和独立验证。

<a id="batch4-p2-q10"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L372)，来源许可：GPL-3.0。

<a id="k189b4a686637"></a>

## 说一下RSI，以及如果你去设计，怎么在你们现有的agent里加上RSI？

**回答：**

RSI 不是所有 Agent 项目中唯一固定的缩写，首先应确认面试中的含义。若这里指 Recursive Self-Improvement，即递归式自我改进，可以理解为系统利用执行反馈提出并验证改进，再把通过验证的变化应用到后续版本。它不等于多写一段反思，也不意味着必须在线修改模型权重。

在现有 Agent 中，可先实现受控的外层改进循环：收集失败轨迹与真实结果，按根因聚类，生成 Prompt、工具说明、Skills、计划策略或代码补丁候选；候选在隔离环境回放，经过回归、安全与成本评估后，由发布流程接纳。在线 loop 负责完成任务，外层循环负责改进版本，两者状态和权限分开。

```text
执行轨迹与业务结果
  -> 失败归因 -> 候选改进
  -> 沙箱验证 -> 隔离测试集 -> 人工或确定性门禁
  -> 小流量发布 -> 监控与回滚
```

关键约束是评分器、保留测试集、权限和发布门禁不能被同一个改进 Agent 随意修改，否则容易优化评分规则而非真实能力。持续反复使用同一测试集也会过拟合，需要轮换与独立保留集。

先选择低风险、容易验证的改进范围，限制候选数量与总预算，并保留版本差异、证据和回退。这种外层自动改进是可落地的工程方案；是否形成严格意义上的递归能力提升，需要持续证据，不能从一次自我反思成功直接推断。

<a id="alibaba-qwen-20260916-q29"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L2274)，来源许可：GPL-3.0。

<a id="k732dc2cfb5b0"></a>

## 说一下你这个项目Agent用在哪里。

**回答：**

这道题考察的不是“项目里有没有 Agent”这个标签，而是 Agent 是否放在真正需要动态决策的位置。回答时应说明业务入口、决策边界、工具、状态和最终验收。

可以按真实项目组织为：用户或上游系统先提交目标；任务层保存当前目标、约束和进度；Context Builder 选择必要的历史、知识和工具；模型根据当前状态决定下一动作；工具执行后把真实 Observation 写回；验证器根据业务状态决定完成、重试、重规划或人工接管。

关键是讲清**哪里不用 Agent**。鉴权、预算、状态迁移、金额计算、数据写入校验和合规规则应由确定性代码负责；步骤固定的链路使用 Workflow；只有任务路径依赖外部观察、工具结果或开放式语义判断时，才让模型参与决策。

最后补上可验证结果：Agent 替代了哪段人工流程，成功标准是什么，失败如何回滚，采用什么基线比较。如果项目只是对话问答、单次 RAG 或固定 Prompt 链，也应如实描述，不要为了迎合题目把所有大模型应用都叫 Agent。

<a id="xiaohongshu-agent-dev-20260812-q5"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%B0%8F%E7%BA%A2%E4%B9%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L936)，来源许可：GPL-3.0。

<a id="k7b226f849e2c"></a>

## 课程边界与先修准备

先完成一个单用户、单业务的最小闭环，再扩展模型与数据规模。本文的教学助手支持：查询课程规则、查询场次、读取与更正偏好、收集预约条件、请求确认、提交一次预约、在响应丢失后查询同一结果。支付、跨机构排课和自动退款不在首版范围内。

建议准备一个 Python 环境、Git、SQLite，以及后续检索实验所用的 PostgreSQL/pgvector。连接真实模型时再配置凭证，不把密钥放在仓库。本文附带的控制层示例只依赖 Python 标准库，可先验证关键逻辑；它不包含真实 LLM、Embedding、LangGraph、网关或完整用户认证，不能直接当作生产 Agent 部署。

需要补基础的读者，先掌握函数与异常、JSON Schema、HTTP 超时、SQL 事务与索引，再开始工具写入实验。能运行示例只证明练习代码通过，能解释失效条件并在自己项目中处理，才构成面试证据。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%83%AD%E9%97%A8AI%E5%AD%A6%E4%B9%A0%E6%A0%B8%E5%BF%83%E8%AF%BE%E7%A8%8B%E4%B8%8E%E6%95%99%E7%A8%8B/16_AI_Agent%E5%B7%A5%E7%A8%8B%E5%AE%9E%E6%88%98%EF%BC%9A%E5%9F%BA%E7%A1%8080%E9%97%AE%E5%AD%A6%E4%B9%A0AI%20Agent.md#L11)，来源许可：GPL-3.0。

<a id="kcfdde3ac42cf"></a>

## 跨 Agent 记忆复用如何设计？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

跨 Agent 记忆复用的目标是让多个 Agent 共享经验，但不泄露不该共享的信息。

设计方式：

1. **分域存储**

   按 user、tenant、project、agent_role、task_type 划分记忆空间。

2. **标准 Memory API**

   提供 search、add、update、delete、summarize、merge 等接口。

3. **权限过滤**

   检索前先按用户、租户、项目和 Agent 权限过滤。

4. **来源标注**

   每条记忆标明来自哪个 Agent、哪个任务、何时生成、置信度多少。

5. **共享级别**

   个人偏好默认不共享；任务经验可在同项目或同团队共享；工具记忆可全局共享但需脱敏。

6. **质量审核**

   只有经过验证的成功经验或明确失败教训才能进入共享记忆库。

反例：让所有 Agent 直接读写同一个全局向量库。这会导致隐私泄露、权限串线、记忆污染和错误复用。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/05_Agent%E8%AE%B0%E5%BF%86%E4%B8%8E%E4%B8%8A%E4%B8%8B%E6%96%87%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L580)，来源许可：GPL-3.0。

<a id="k28a99a550390"></a>

## 远程编码 Agent 如何处理 session、interrupt、resume 和 reconnect？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

远程会话的关键是可靠性。

需要设计：

- session id 标识会话。
- WebSocket 或 streaming 接收事件。
- HTTP/控制通道发送用户消息和权限响应。
- interrupt 信号取消当前任务。
- reconnect 策略处理网络波动。
- session not found 的短暂重试。
- compact boundary 表示历史压缩点。
- resume 恢复摘要和状态。
- remote permission bridge 处理云端工具权限。

面试中可以强调：远程 Agent 不是简单把 CLI 放到服务器上，而是要处理流式事件、权限回调、断线恢复和状态一致性。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/02_%E7%BC%96%E7%A0%81Agent%E4%B8%8EAgentOS%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L638)，来源许可：GPL-3.0。

<a id="k1da68ba9064b"></a>

## 选取一个真实问题单，完整描述从Agent接收输入，走完全流程，到产出最终结果的整条链路？

**回答：**

选择一个真实问题单，沿同一个 run_id 讲完输入、决策、工具调用、状态变化与输出，避免只展示架构图。下面是退款接口测试的假设例子，用于说明讲述方式，不代表个人已完成项目。

```text
问题单与需求版本 → 身份/权限/参数校验 → 锁定环境与资源
    → 检索需求、接口契约、历史用例 → 生成可校验的测试计划
    → 校验预期与执行风险 → 必要时人工确认
    → 测试环境执行 → 收集断言、日志与失败证据
    → 汇总报告 → 人工复核/归档 → 经审核回流
```

例如需求新增退款金额上限，系统先明确订单状态、金额单位、版本和环境，再生成上限附近、重复请求、无权限和超时等用例。预期结果取自已确认的业务规则；当前程序返回什么，不能直接作为正确答案。

每个工具调用记录工具及版本、经过校验的参数、开始结束时间、结果状态与证据位置。读取失败时补取或停止；写操作超时则先查询是否已生效，再决定是否重试。报告要区分“计划覆盖”“实际执行”“通过”“失败”“未执行”，不能把生成了用例算成测试成功。

最后讲一条真实异常分支，例如环境不可用如何转入 BLOCKED、恢复后从哪个节点继续，以及哪些副作用通过幂等键避免重复。

**把链路讲到状态和证据。** 假设同一退款测试任务包含“读取订单—生成计划—执行测试—核验结果”四类步骤，报告中的每一个结论都应能回到某次工具执行及对应断言。可以为步骤记录 `run_id、step_id、attempt、input_hash、tool_version、external_operation_id、status、evidence_ref`。其中 attempt 表示同一步的执行尝试，不能用新的 attempt 编号绕过业务幂等。

![图1测试Agent的证据与执行闭环](https://raw.githubusercontent.com/WeThinkIn/AIGC-Interview-Book/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/imgs/meituan-agent-20261012-18fa4134/01_测试Agent的证据与执行闭环.png)

图 1：示意测试 Agent 的执行与验收关系。需求与技术方案约束测试预期，工具返回和外部核验支撑执行结果；图中流程是参考设计，不代表某位候选人的已实现系统。

如果工具调用超时而外部动作可能已经生效，应进入“结果待核对”状态。先根据外部操作 ID 或业务键查询效果，确认成功后补记状态，确认没有执行才考虑安全重试；暂时无法确认时继续阻塞或人工接管。把超时直接标成业务失败再重做，可能造成重复动作。

<a id="meituan-agent-20261012-18fa4134-q03"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%BE%8E%E5%9B%A2%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L677)，来源许可：GPL-3.0。

<a id="k2690d45356e4"></a>

## 选择性保留和内容裁剪适合哪些场景？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

选择性保留是按重要性决定哪些消息进入上下文；内容裁剪是对单条内容删除无关部分。

适合选择性保留的场景：

- 多工具调用中只保留成功结果和关键错误。
- 研究任务中只保留高置信证据。
- 长对话中保留用户明确约束和最终决策。
- 多 Agent 协作中只保留子 Agent 结论，而不是完整对话。

适合内容裁剪的场景：

- 测试日志只保留失败堆栈附近内容。
- 浏览器 DOM 只保留可见区域和相关节点。
- 代码文件只保留相关函数和导入。
- 搜索结果只保留标题、摘要、URL 和关键片段。

工程建议：

- 工具返回结果先结构化再入上下文。
- 日志、网页、代码优先裁剪再摘要。
- 高风险任务保留原始引用位置，方便复查。
- 裁剪规则要可观测，避免重要信息被静默丢弃。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/05_Agent%E8%AE%B0%E5%BF%86%E4%B8%8E%E4%B8%8A%E4%B8%8B%E6%96%87%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L460)，来源许可：GPL-3.0。

<a id="kf1e90d40dd5c"></a>

## 那agent本身修改后，你们如何去衡量此次修改的好坏？

**回答：**

先明确变更是什么：Prompt、工具 Schema、计划策略、记忆压缩、模型、检索或运行时。如果多项同时改变，难以归因，应通过分组实验或消融拆分影响。

在相同任务集、初始环境和预算下，对新旧版本做配对回放，并进行适量重复试验。记录任务级成功、错误类型、尾延迟、成本和高风险违规。利用配对差异、置信区间或 bootstrap 判断改进是否稳定；对同一任务的多次试验，应按任务聚合或分组抽样，避免伪增大样本量。

上线门禁除了整体平均提升，还应要求核心场景和安全约束不明显退化。检查失败是否集中到某类用户、工具或长任务。离线通过后再做受控灰度或按用户/会话分配的 A/B，明确终止与回滚条件。

最终判断是相同约束下的质量、时延和成本取舍，而不是只看一个总分。省 Token 但提高错误操作率，不能直接算作优化。

<a id="alibaba-qwen-20260916-q27"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L2261)，来源许可：GPL-3.0。

<a id="k620e4fc422a3"></a>

## 针对Agent多步推理过程中产生的响应延迟问题，可落地的优化方法有哪些？

<a id="batch4-p2-q20"></a>

**相关解释：** [Agent常见模式（ReAct/Plan and Execute等）](../15-%E5%89%8D%E7%AB%AF%E4%B8%8E%E6%B5%8F%E8%A7%88%E5%99%A8/React%E4%B8%8E%E7%BB%84%E4%BB%B6%E7%8A%B6%E6%80%81-01.md#k93a12d0c9256)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L478)，来源许可：GPL-3.0。

<a id="k5bd619a66fa1"></a>

## 针对长视频理解挑战，分析LLaMA-VID、LongVLM、VideoAgent等模型的长序列处理架构设计

时序建模策略对比：
- 均匀采样：固定间隔采样，计算效率高但可能丢失关键帧
- 自适应采样：基于内容重要性动态选择关键帧
- 分层处理：粗粒度筛选+细粒度分析的多级架构
- 记忆机制：维护长期记忆存储，解决信息遗忘问题

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E8%A7%86%E9%A2%91%E5%9F%BA%E7%A1%80/04_%E8%A7%86%E9%A2%91%E7%90%86%E8%A7%A3%E5%85%B8%E5%9E%8B%E6%A8%A1%E5%9E%8B%E4%B8%8E%E6%9E%B6%E6%9E%84.md#L274)，来源许可：GPL-3.0。

<a id="k907a81ec4930"></a>

## 长上下文与记忆管理

**回答：**

上下文管理的目标是保留完成当前任务所需的有效信息，而不是无差别保存所有历史。短期工作上下文、可恢复的任务状态、长期记忆和原始证据应分开管理。

窗口更大只能缓解容量问题，不能自动解决信息冲突、错误累积、无关内容干扰和调用成本。设计时应同时控制 token 数、状态准确性和历史可追溯性。

<a id="baidu-aigc-multimodal-agent-20260922-20260924-r2-q6-1"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%99%BE%E5%BA%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1902)，来源许可：GPL-3.0。

<a id="kb96dd6d7e7c9"></a>

## 长任务和人工确认怎样恢复？

以退款为例，Agent 已经收集完信息，真正执行前需要等待用户确认。用户可能几小时后才回来，系统不能继续依赖原来的进程和内存状态。暂停时要保存 `runId`、Checkpoint、待执行工具、规范化参数、当前 State、`actionId`，以及工具 Schema 和策略版本。

用户确认时，系统先校验确认人的身份和权限，并检查这次确认是否已经过期。恢复任务后还要重新读取订单状态。等待期间如果退款金额、订单状态、工具 Schema 或策略发生变化，原来的确认立即失效，系统需要展示新参数并再次确认。

部分框架恢复时会从节点起点重新执行。写操作节点因此仍要复用同一个 `actionId`，先查询外部状态，再决定是否执行；确认事件也只能消费一次。这样即使恢复动作被重复触发，也不会重复退款或重复创建工单。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/interview-questions/agent-project-interview-guide.md#L332)，来源许可：Apache-2.0。
