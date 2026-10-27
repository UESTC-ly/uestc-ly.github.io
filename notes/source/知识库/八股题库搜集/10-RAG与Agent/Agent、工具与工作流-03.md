# Agent、工具与工作流

<a id="kdaae235cfaa2"></a>

## Workflow 和 Agent Runtime 是什么关系？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

Workflow 描述节点、依赖、条件和状态转移；Agent Runtime 提供一次运行所需的模型、工具、权限、上下文和预算管理。工作流引擎可能已经包含部分运行时能力，两者是职责划分，不必强行部署成两个服务。

一种组合是 Workflow 固定预约的确认与提交顺序，Agent 节点处理自然语言收集和例外解释。另一种是 Runtime 驱动动态任务，并调用某个确定性工作流完成稳定子流程。关键是明确谁持有权威任务状态、谁负责重试和取消。

若两层都重试写操作，单次超时可能变成多次预约。应统一 run 标识、幂等键、终止状态和事件语义，并区分节点失败与业务拒绝。编排框架能够恢复状态，不代表外部服务的事务也随之恢复。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/03_Agent%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81%E7%BC%96%E6%8E%92%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L637)，来源许可：GPL-3.0。

<a id="k70b40120851c"></a>

## Workflow、Graph 与 Loop

相关内容：[《AI 工作流中的 Workflow、Graph 与 Loop：从概念到实现》](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/agent/workflow-graph-loop.md)、[《Loop Engineering 是什么？为什么说它是新瓶装旧酒？》](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/agent/loop-engineering.md)

工作流题主要检查流程结构、状态保存和循环控制。除了解释 Node、Edge、State，还要准备中断恢复、并行更新和停止条件等工程问题。外层 Loop Engineering 在这里指把已有循环接到 CI、定时任务和停止条件上的工程实践，重点是如何调度、验证和停止。

常见面试题：

- 为什么 AI 系统需要工作流？
- Workflow、Graph、Loop 三者是什么关系？
- Graph Loop 和 Agent Loop 有什么区别？
- 外层 Loop 由谁触发下一轮：CI 事件、定时任务、目标检查还是人工审批？
- 外层 Loop 与一次任务内部的 Agent Loop 有什么区别，状态和验证结果怎样交接？
- 哪些任务不适合无人值守？缺少可靠验收信号、涉及高风险写操作或需要业务判断时，怎样停止并转人工？
- Loop 如何防止死循环？
- State 的更新策略怎么选？Replace、Append、Reducer 分别适合什么字段？
- 条件边和动态路由有什么区别？
- 工具调用失败时，哪些错误适合重试？认证失败和非幂等写操作怎么处理？
- 工作流中断后怎么恢复？
- 工作流有哪些特有的安全风险？

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/interview-questions/agent-interview-questions.md#L116)，来源许可：Apache-2.0。

<a id="k7753d9c71fed"></a>

## 一个复杂任务里，怎么结合规划、执行和反思这几种机制？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

把复杂任务拆成规划器、执行器和验证器的有界循环。规划器提出子目标及依赖；执行器在每一步使用工具；验证器检查可观察结果，只有失败或目标变化时才更新计划。反思记录能改变下次行动的经验，避免每一步都额外调用模型。

例如知识库问答加课程预约：先核查规则、收集课程与时间、查询可约状态、获得用户确认，再提交预约。确认后库存变化，应重新查询并请求确认新的方案，不能沿旧计划继续提交。

用任务状态记录步骤版本、输入依据、产物、重试次数和结束原因。限制重规划次数，重复失败时转为澄清、降级或人工处理。规划、反思和执行的质量最终用完整任务成功率、错误副作用和成本检验，不能只看计划文字是否详尽。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/03_Agent%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81%E7%BC%96%E6%8E%92%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L361)，来源许可：GPL-3.0。

<a id="kc0808d32a584"></a>

## 一个完整 Agent Harness 通常包含哪些模块？

完整 Agent Harness 通常包含九个模块：

1. **Task Dataset**

   任务输入、初始状态、用户目标、权限范围、风险标签和期望结果。

2. **Environment Builder**

   构造仓库、网页、数据库、文件系统、API mock、用户模拟器或沙箱。

3. **Agent Runner**

   以固定模型、prompt、工具、策略、随机种子和预算运行 Agent。

4. **Tool / API Simulator**

   模拟真实工具返回、异常、延迟、权限错误和边界情况。

5. **Trace Collector**

   记录模型调用、工具调用、状态变化、审批事件、成本和耗时。

6. **Evaluator / Grader**

   评估最终状态、最终答案、执行轨迹、安全行为和成本。

7. **Report Dashboard**

   展示通过率、失败分类、版本对比、趋势和 trace 链接。

8. **Regression Gate**

   接入 CI/CD，新版本退化时阻止发布。

9. **Failure Feedback Loop**

   将线上失败转成新任务，补充到回归集和安全集。

工程上可以简化为四层：

$$
\text{Dataset} \rightarrow \text{Run} \rightarrow \text{Judge} \rightarrow \text{Gate}
$$

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/08_Agent_Harness_Engineering%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L105)，来源许可：GPL-3.0。

<a id="kc0809ebc0951"></a>

## 一个完整的Agent系统通常包含哪些核心模块？相比传统LLM Chatbot，它最大的区别是什么？

**回答：**

完整 Agent 通常至少包含以下模块：

1. **接入与身份层：** 用户、租户、会话、鉴权、配额、输入校验和风险分级。
2. **任务与状态层：** 目标、约束、计划、步骤状态、工具结果、产物引用、checkpoint 和终止条件。长任务状态不能只存在 Prompt 中。
3. **上下文构建层：** 按当前步骤选择系统规则、近期对话、结构化状态、RAG 证据、长期记忆和候选工具，并管理 Token 预算。
4. **决策与编排层：** 意图路由、规划、模型选择、Workflow/状态机/ReAct 循环、重规划和停止策略。
5. **工具执行层：** 工具注册、Schema、参数校验、权限、超时、幂等、限流、沙箱、结果裁剪和副作用确认。
6. **知识与记忆层：** 文档索引、检索、用户或项目记忆、事件日志、写入门控、冲突处理和过期删除。
7. **验证与治理层：** 规则校验、测试、业务状态验收、重试、熔断、降级、回滚、人工审批和安全审计。
8. **可观测与评测层：** 全链路 Trace、模型/Prompt/工具版本、Token、延迟、任务成功率、工具正确率、成本和安全指标。

传统 LLM Chatbot 通常是“输入 -> 一次或有限次生成 -> 文本输出”，状态和外部知识可能存在，但模型一般不负责动态选择并执行多步动作。Agent 的核心区别不是多了一层 Prompt，而是存在一个受约束的闭环：

$$
s_t \xrightarrow{\text{decide}} a_t
\xrightarrow{\text{tool/environment}} o_{t+1}
\xrightarrow{\text{validate/update}} s_{t+1}
$$

模型给出下一步候选决策，Harness 负责权限与执行，外部环境返回真实 Observation，状态更新后再决定下一步。终止也应由外部验收条件确认，而不是模型说“已经完成”。固定步骤的业务仍优先使用 Workflow，不能为了使用 Agent 而把确定性流程模型化。

<a id="bilibili-ai-agent-20260818-q3"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%93%94%E5%93%A9%E5%93%94%E5%93%A9%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L44)，来源许可：GPL-3.0。

<a id="kf5aeaeeff19d"></a>

## 一个终端/IDE 编码 Agent 的典型架构是什么？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

典型架构可以分为八层：

1. **入口层**

   CLI、IDE 插件、Web、SDK、远程 session。

2. **会话层**

   保存 messages、session id、用户配置、当前工作目录、模型选择、预算、权限模式。

3. **上下文层**

   收集系统提示词、项目说明、Git 状态、打开文件、选区、历史摘要、记忆。

4. **模型循环层**

   负责模型调用、streaming、tool-call loop、重试、token 统计、停止条件。

5. **工具层**

   文件读写、搜索、Bash、Git、LSP、Web、MCP、Notebook、子 Agent、Skills。

6. **权限层**

   判断工具是否允许、是否需要确认、是否被策略拒绝、是否运行在沙箱中。

7. **UI/交互层**

   展示 diff、命令输出、权限弹窗、进度、成本、任务列表和错误。

8. **观测和持久化层**

   记录 transcript、tool trace、session restore、cost、diagnostics、telemetry。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/02_%E7%BC%96%E7%A0%81Agent%E4%B8%8EAgentOS%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L104)，来源许可：GPL-3.0。

<a id="kae20f82adeb2"></a>

## 上下文信息如何支撑多步任务？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

本节只给出上下文工程的总览视角；Memory 类型、Memory vs RAG、Context Engine、记忆生命周期、存储架构、隐私治理和 Skills 渐进式上下文，统一见 [05_Agent记忆与上下文工程高频考点.md](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/05_Agent记忆与上下文工程高频考点.md)。

上下文工程是决定“当前这次模型调用应该看到什么”的技术。

Agent 面临的问题：

- 上下文窗口有限。
- 工具结果可能很长。
- 历史对话会污染当前任务。
- 项目文件太多。
- 记忆可能过期或冲突。
- 不同工具需要不同上下文。

上下文工程的目标：

- 保留任务相关信息。
- 去掉无关噪声。
- 控制 token 成本。
- 提高工具选择准确性。
- 降低幻觉和遗忘。
- 让长任务可持续执行。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/01_AIGC%E6%97%B6%E4%BB%A3AI%20Agent%E5%9F%BA%E7%A1%80%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L567)，来源许可：GPL-3.0。

<a id="k21868351976a"></a>

## 上下文压缩时，你怎么做信息丢失的评估？——用模型打分还是规则？如果压缩丢了关键信息导致 Agent 后面决策错误，你能检测到吗？怎么恢复？

**回答：**

上下文压缩的目标不是让文本更短，而是保留后续决策所需的最小充分状态。压缩前先把信息分为硬约束、已确认事实、未完成目标、工具结果、证据引用、用户偏好、过程噪声和可重建内容。硬约束、权限、金额、时间、ID、错误状态和未完成任务不能仅依靠自由摘要保留，应写入结构化状态。

评估需要规则与模型结合：

- **规则校验：** 比较实体、数字、日期、ID、否定词、权限和状态枚举；检查所有未完成任务、工具结果引用和约束是否存在。
- **任务重放：** 把压缩结果输入后续决策器，与未压缩上下文的工具选择、参数和终态比较。
- **检索式覆盖：** 对关键事实生成查询，检查压缩上下文是否能找回对应证据。
- **模型评审：** 让独立评审器按事实保真、任务可继续性和冗余度打分，但必须用人工标注校准，并防止评审器与生成模型共享同一错误。

可以定义关键事实保留率：

$$
\mathrm{Retention}=
\frac{\sum_i w_i\,\mathbf{1}[f_i\text{ 在压缩后可正确恢复}]}
{\sum_i w_i}
$$

其中高风险约束的权重 $w_i$ 应显著高于普通闲聊。若压缩后工具选择与 gold context 不一致，或规则检测发现关键字段丢失，就在继续执行前阻断。

发生错误时要能恢复：保留原始事件日志和分段消息，压缩结果只是派生缓存；从最近完整 checkpoint 重新压缩，或按当前失败点检索相关原文；对高风险任务直接扩大上下文并降低自动执行权限；如果已产生副作用，先查询外部状态再决定补偿。真正可靠的设计是“可丢弃的摘要 + 不可丢失的结构化状态 + 可重放的原始事件”，而不是把一次模型摘要当成唯一事实来源。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/DeepSeek%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L670)，来源许可：GPL-3.0。

<a id="k4d8ae7b84e78"></a>

## 上下文太长怎么办？记忆和上下文是怎么处理的

**回答：**

上下文是当前一次模型调用实际可见的内容；记忆是跨调用保存的状态、事实或经验，只有被选择并注入后才进入当前上下文。长期记忆可以保存在数据库、文档或向量索引中，不意味着模型会自动记住全部历史。

先建立 token 预算，为系统规则、当前问题、关键状态、工具证据和输出留空间。近期必要对话可以保留原文，已完成步骤压缩成结构化摘要，长文档和日志保存在外部，仅按需读取。工具调用与对应返回结果应成对保留或按接口约定整体压缩，避免产生不合法的消息序列。

知识抽取任务的工作记忆应优先保存当前文档版本、抽取范围、本体版本、已确认实体映射、待解决歧义和未完成操作。长期记忆只写入经过确认的事实，并附带时间、适用范围、证据和权限，支持更新、撤回与冲突处理。模型对自身输出的总结不能直接变成可信事实。

摘要会丢细节，向量检索也可能漏召回，所以关键证据应保留可回读定位。对实体归一等高风险决策，应重新读取原始语境与术语定义。评测除了 token 节省，还要看约束保持、跨轮一致性、错误记忆传播和权限隔离。

<a id="01ai-kg-intern-20261021-de81855b-q07"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%9B%B6%E4%B8%80%E4%B8%87%E7%89%A9%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L123)，来源许可：GPL-3.0。

<a id="ka6429e8ce5cb"></a>

## 上下文有哪些部分组成，怎么做上下文工程，如何防止上下文爆炸，压缩之后上下文缩小了多少

**回答：**

Agent 上下文通常由系统约束、用户目标、近期对话、任务状态、工具 Schema、工具观察、检索证据、长期记忆和输出预算组成。上下文工程的核心是预算分配与状态选择，不是简单扩大窗口。

可用近期窗口、结构化任务状态、阶段摘要、外部记忆检索、工具结果分页/聚合、Artifact 引用和动态截断。压缩比例不能凭经验承诺，必须报告压缩前后 Token、事实保真率、未完成任务召回率、下游成功率和延迟；否则“缩小了 80%”没有意义。

<a id="tencent-llm-collection-20260903-q59"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E8%85%BE%E8%AE%AF%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L937)，来源许可：GPL-3.0。

<a id="k95df902bd36f"></a>

## 上下文窗口溢出时如何处理？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

常见策略：

1. **滑动窗口**

   保留最近消息，丢弃早期内容。简单但容易丢失关键决策。

2. **摘要压缩**

   将历史对话、工具结果、任务状态压缩成摘要。

3. **语义检索**

   将历史消息和文件切片向量化，按需检索。

4. **结构化状态**

   把任务进度、TODO、约束、已完成动作保存为结构化对象。

5. **工具结果折叠**

   长 stdout、搜索结果、文件内容只保留摘要和引用。

6. **分层上下文**

   系统指令、任务目标、计划、相关文件、历史摘要按优先级拼接。

7. **子 Agent 隔离**

   把探索性任务交给子 Agent，主 Agent 只接收结论。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/01_AIGC%E6%97%B6%E4%BB%A3AI%20Agent%E5%9F%BA%E7%A1%80%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L637)，来源许可：GPL-3.0。

<a id="k93d3b483bc97"></a>

## 上下文预算不足时有哪些处理层次？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

上下文窗口溢出是 Agent 的高频工程问题。典型来源包括：

- 长时间对话。
- 多步骤 ReAct。
- 大量工具返回。
- 浏览器 DOM / AXTree。
- 代码仓库文件。
- 日志和测试输出。
- 多 Agent 汇报。

解决思路不是单一“换长上下文模型”，而是组合治理：

- 滑动窗口。
- 摘要压缩。
- 语义压缩。
- 选择性保留。
- 内容裁剪。
- 外部记忆。
- 分层上下文。
- 子 Agent 汇总。
- 长上下文模型。
- 混合模型策略。

目标是保证模型看到的不是“最多信息”，而是“对当前决策最有用的信息”。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/05_Agent%E8%AE%B0%E5%BF%86%E4%B8%8E%E4%B8%8A%E4%B8%8B%E6%96%87%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L415)，来源许可：GPL-3.0。

<a id="k56d1498fdcd0"></a>

## 上线的agent服务在突然有一天关键业务用例开始返回错误答案，甚至可能影响线上服务，作为agent的负责人，会怎么定位问题，如何保障系统不受影响？

**回答：**

先止损再定位：按用例、模型版本、Prompt、知识库版本、工具版本、地域和租户切分错误率；关闭高风险自动动作，切换上一个稳定版本或只读/人工模式，保留请求快照和 trace。然后回放同一输入，逐层检查数据、检索、工具、上下文组装、模型响应和后处理。

定位要比较最近变更、索引 freshness、权限过滤、模型路由、第三方 API、评测集和线上分布。修复后先用回归集、对抗集和影子流量验证，再小比例灰度。必须设置错误率、越权、金额和投诉等自动回滚门槛。

<a id="tencent-llm-collection-20260903-q70"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E8%85%BE%E8%AE%AF%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1040)，来源许可：GPL-3.0。

<a id="k720caee5ff9b"></a>

## 不同记忆类型如何按用途与时效组织？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

Agent Memory 可以从时间、功能和来源三个角度划分。

按时间划分：

- 短期记忆：当前对话窗口内的信息。
- 工作记忆：当前任务状态、计划、待办、工具结果摘要。
- 中期记忆：会话摘要、阶段性任务总结、近期项目上下文。
- 长期记忆：跨会话保留的用户偏好、稳定事实、经验和知识。

按功能划分：

- 个人记忆：用户画像、偏好、习惯、约束。
- 任务记忆：任务轨迹、成功策略、失败经验、SOP。
- 工具记忆：工具成功率、参数偏好、失败原因、成本和延迟。
- 项目记忆：仓库规则、团队规范、构建命令、架构约束。
- 安全记忆：用户撤回、禁止记录、敏感信息策略、权限边界。

按数据结构划分：

- 原始事件日志。
- 对话摘要。
- Key-Value 记忆。
- 向量记忆。
- 图记忆。
- 表格化用户画像。
- 文件或项目级记忆文档。

不同类型的记忆不应混在一个大向量库里粗暴检索。高质量 Memory 系统通常会分层、分域、分权限管理。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/05_Agent%E8%AE%B0%E5%BF%86%E4%B8%8E%E4%B8%8A%E4%B8%8B%E6%96%87%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L119)，来源许可：GPL-3.0。

<a id="kdefc093ef268"></a>

## 业务场景从试验到生产需要哪些验收阶段？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

推荐阶段：

1. **场景筛选**

   选择高频、低风险、可评估、有明确 ROI 的场景。

2. **PoC**

   用有限数据和工具验证可行性。

3. **Pilot**

   小范围真实用户试用，收集失败样本和反馈。

4. **受控生产**

   接入权限、审计、评测、监控、灰度，限制自动化边界。

5. **规模化**

   扩展到更多团队、更多工具、更多场景。

6. **平台化**

   沉淀工具、知识库、评测、模板、Agent 和 Skill 市场。

每个阶段的目标不同：PoC 验证“能不能做”，Pilot 验证“用户愿不愿用”，生产验证“能不能稳定安全地做”，平台化验证“能不能规模化复用”。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/07_%E4%BC%81%E4%B8%9A%E7%BA%A7Agent%E5%B9%B3%E5%8F%B0%E4%B8%8E%E4%BA%A7%E5%93%81%E8%90%BD%E5%9C%B0%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L486)，来源许可：GPL-3.0。

<a id="k5cfb27e7ef0f"></a>

## 业务方向：Agentic RL训练，2B方向

**回答：**

这条更像面试官披露的信息，而不是需要候选人作答的问题。反问的目标应是确认岗位的真实训练闭环和工程约束，而不是继续展示名词。

可以围绕以下方向提问：2B 是模型参数规模、业务线代号还是专项名称；当前 Agentic RL 的主要任务是工具调用、多轮客服、代码/数据分析还是通用政企 Agent；训练使用 PPO、GRPO、OPD 或混合方案的原因；环境和 verifier 如何构造；rollout 是在线真实系统、沙箱还是用户模拟器；最主要瓶颈是环境吞吐、reward 可靠性、长轨迹稳定性还是线上泛化；岗位需要负责算法、训练框架、推理基础设施还是评测平台中的哪些部分。

对政企业务还应询问：数据是否可出域、权限和审计如何进入训练/评测、硬约束由哪一层执行、人工接管的业务标准、上线采用何种灰度和回滚机制。最后可以问新人前三个月的交付目标及评价标准。

好的反问能帮助候选人判断“Agentic RL”是论文复现、内部平台建设还是已经连接真实业务状态的训练闭环，也让面试官看到候选人关注的是可验证、可部署和可治理的系统能力。

<a id="alibaba-cloud-ai-infra-20260823-end"></a>

<a id="alibaba-cloud-agent-algo-20260901"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1212)，来源许可：GPL-3.0。

<a id="k3c543a6fe28a"></a>

## 两个 Agent 给出冲突结论时如何仲裁？什么情况下需要人工介入？

**回答：**

先区分事实冲突、推理冲突和偏好冲突。事实冲突应回到权威数据源、工具结果和时间版本，而不是让第三个模型凭语言流畅度投票；推理冲突可要求双方提供证据与可执行检验，再由规则、测试或独立验证器判定；偏好冲突需要业务目标和优先级，通常不存在纯技术上的唯一答案。

仲裁器可以使用结构化输入：结论、证据 ID、置信度、时间、模型/工具版本和验收测试。优先级通常是确定性约束与实时业务状态高于模型判断，受信数据高于二手摘要，可执行测试高于自评。LLM Critic 可以帮助发现遗漏，但不应既生成又作为唯一裁判，因为会有自洽、位置和风格偏差。

人工介入适用于高风险或不可逆动作、证据相互矛盾且无法自动验证、低置信度、超出预算/重试上限、权限升级、用户意图不明确以及法律合规要求。人工界面要展示差异、证据、历史动作和可选操作，而不是只给两段长答案。

仲裁结果和人工选择应写回评测集，用于改进路由、工具和规则。目标不是让所有 Agent 达成表面一致，而是在成本可控的条件下得到可验证、可追责的决定。

<a id="pinduoduo-ai-agent-20260816-q32"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E6%8B%BC%E5%A4%9A%E5%A4%9A%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L660)，来源许可：GPL-3.0。

<a id="k28ef5c53f093"></a>

## 两个QA同时输入相同查询，Agent给出的报告是否一致？

**回答：**

不保证逐字一致，先定义业务上需要哪种一致性。可区分文字表达一致、结构化结论一致、证据快照一致，以及外部动作只执行一次。四者需要的措施不同。

同一查询也可能因用户权限、会话历史、知识版本、时间窗口、外部环境和模型随机性不同而得到不同结果。要做可比实验，应固定这些条件；温度设为 0 只能减少采样变化，无法普遍保证端到端确定性。

对于事实报告，可固定结构化字段和证据快照，再渲染文本；对于相同权限与上下文下的重复读取，可合并正在执行的请求或缓存已完成结果。缓存键至少考虑租户/权限范围、标准化查询、数据和模型策略版本；权限变化或时效到期必须失效。

有副作用的任务要用业务幂等键、唯一约束和状态机去重，不能仅靠“相同 prompt”或一个短期锁。两个 QA 是否应复用结果也需要看是不是同一次业务操作。

验收关注结论、证据和动作的一致性，同时记录允许的措辞差异。生成文本一致，并不能证明测试对象或执行环境一致。

**幂等键还需要绑定请求内容。** 可以为幂等记录保存规范化请求摘要。相同作用域、相同键和相同摘要，应复用已有操作状态；键相同而摘要不同，应返回冲突并要求调用方纠正。摘要需要覆盖环境、资源 ID、业务参数及适用版本，而不只是用户输入文本。

并发下先查询“有没有相同键”再插入仍有竞态，最终去重必须依赖数据库唯一约束或具有同等原子性的机制。若结果缓存用于多个用户，权限等价性应由服务端判断，不能相信客户端自报的 permission 字段。缓存命中也要遵守当前的访问控制与数据撤回规则。

<a id="meituan-agent-20261012-18fa4134-q10"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%BE%8E%E5%9B%A2%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L866)，来源许可：GPL-3.0。

<a id="k5673bb13f4de"></a>

## 个人助手的入口、执行与数据层如何配合？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

本章使用 AgentOS 讨论“运行时工程层”，重点是入口、Gateway、Session、Runtime、Context Engine、Tool Policy 和后台任务。企业平台中的 Builder、Registry、Marketplace、多租户产品治理和商业选型，见 [07_企业级Agent平台与产品落地高频考点.md](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/07_企业级Agent平台与产品落地高频考点.md)。

AgentOS 可以理解为把 Agent 从“单次对话应用”升级为“长期运行的智能操作系统层”。它不只管理模型调用，还要管理消息入口、会话、工具、权限、上下文、任务、事件、自动化和多 Agent 隔离。

通用分层如下：

1. **交互入口层**

   包括 CLI、IDE、Web、移动端、桌面端、聊天软件、语音入口、Webhook、定时任务等。它解决“用户和外部事件从哪里进入 Agent”的问题。

2. **Gateway 控制平面**

   负责统一接入消息、维护连接、路由会话、调度运行时、转发事件、管理认证、暴露状态和处理重连。

3. **Session 与 Channel 层**

   管理不同来源的上下文边界，例如用户私聊、群聊、项目空间、定时任务、浏览器会话、远程工作区。

4. **Agent Runtime 层**

   负责模型循环、工具调用、上下文拼装、streaming、重试、停止条件和 turn 生命周期。

5. **Context Engine 层**

   负责记忆、项目知识、历史摘要、token 预算、上下文压缩和检索增强。

6. **Tool / Skill / Plugin 层**

   提供文件系统、Shell、浏览器、代码工具、消息发送、日历、任务系统、媒体生成、企业 API、MCP Server 等能力。

7. **安全与治理层**

   包括沙箱、工具策略、权限审批、密钥隔离、审计日志、敏感内容脱敏、数据保留策略。

8. **任务与自动化层**

   支持后台任务、cron、hook、workflow、异步通知、断线恢复和长任务状态追踪。

面试中可以总结为：AgentOS 的核心不是“多接几个工具”，而是把 Agent 的入口、运行时、上下文、安全和任务生命周期系统化。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/02_%E7%BC%96%E7%A0%81Agent%E4%B8%8EAgentOS%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L840)，来源许可：GPL-3.0。

<a id="k00bd2313573a"></a>

## 个人记忆、任务记忆、工具记忆分别解决什么问题？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

| 记忆类型 | 核心问题 | 示例 |
| --- | --- | --- |
| 个人记忆 | Agent 如何更懂用户 | 偏好正式语气、喜欢科幻、对坚果过敏 |
| 任务记忆 | Agent 如何从任务经验中复用策略 | 某类 bug 修复先跑单测，再改 mock |
| 工具记忆 | Agent 如何更好地选择和使用工具 | 某搜索工具对中文文档命中率低，某 API 经常超时 |

个人记忆提升个性化；任务记忆提升复用和自我改进；工具记忆提升工具选择效率和稳定性。

一个成熟系统会把它们分开存储：

- 个人记忆按 user_id 隔离。
- 任务记忆按 task_type、domain、project、agent_role 分类。
- 工具记忆按 tool_id、参数模式、调用环境记录。

不要把工具失败记录写进用户个人画像，也不要把用户隐私写进全局任务记忆库。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/05_Agent%E8%AE%B0%E5%BF%86%E4%B8%8E%E4%B8%8A%E4%B8%8B%E6%96%87%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L164)，来源许可：GPL-3.0。

<a id="k65099ca75927"></a>

## 为什么 2025-2026 年 Agent 从 Demo 走向工程系统？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

原因主要有六个：

1. **模型工具调用能力增强**

   主流模型能更稳定地产生 JSON、调用函数、理解工具错误并修复计划。

2. **协议标准化**

   MCP 标准化了“模型应用如何接入工具和上下文”；A2A 标准化了“Agent 服务之间如何通信”。

3. **框架成熟**

   OpenAI Agents SDK、LangGraph、CrewAI、AutoGen、Google ADK 等框架提供了 handoff、guardrails、tracing、memory、durable execution 等工程能力。

4. **编码 Agent 证明价值**

   Claude Code、Codex、Cursor、Devin、Jules 等工具让 Agent 在真实代码仓库中执行读写、测试、调试和提交。

5. **评测体系更清晰**

   SWE-bench、WebArena、OSWorld、GAIA、τ-bench 等让 Agent 不再只靠 demo 评估。

6. **企业需求明确**

   企业更关心自动化办公、数据分析、客服、研发提效、运营执行和知识工作流，这些都适合工具型 Agent。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/01_AIGC%E6%97%B6%E4%BB%A3AI%20Agent%E5%9F%BA%E7%A1%80%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L102)，来源许可：GPL-3.0。

<a id="k86171068a73a"></a>

## 为什么 Agent 比普通 LLM 更需要 Harness Engineering？

普通 LLM 评测通常关注“输入 -> 输出”是否正确。Agent 评测更难，因为 Agent 有工具调用、环境状态、长任务、多轮交互、权限审批和真实副作用。

Agent Harness 必须覆盖：

- **Outcome**：最终任务是否完成。
- **Trajectory**：中间步骤是否合理。
- **Tool Use**：是否选对工具、参数是否正确。
- **State Change**：数据库、文件、工单、页面状态是否符合预期。
- **Safety**：是否越权、泄密、误执行高风险动作。
- **Cost / Latency**：是否在预算内完成。
- **Robustness**：多次运行是否稳定。
- **Recoverability**：失败后是否可重试、可回滚、可恢复。

例如一个客服 Agent 最终回答看似正确，但如果它在中间调用了越权订单查询工具，或者错误修改了数据库状态，这就是严重失败。只看最终文本会漏掉这些风险。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/08_Agent_Harness_Engineering%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L88)，来源许可：GPL-3.0。

<a id="kf4f9b975f984"></a>

## 为什么 Agent 生态开始广泛使用 MCP

**回答：**

可以从采用动因回答：当模型应用与外部系统数量都增加时，统一连接协议能够降低重复编写适配器的成本，让同一能力更容易被多个兼容的宿主复用。能力发现和结构化 schema 也有助于减少手工维护接口描述的负担。

这里不需要把“广泛使用”量化为未经核实的市场占有率。其价值主要在于互操作和生态复用，而不是天然带来更高的推理质量。最终收益仍取决于协议兼容性、服务器质量、权限设计与运维成本。

小型系统如果只有几个固定接口，直接接 API 可能更简单；需要连接多种宿主、复用外部工具或统一插件接入时，MCP 的收益更明显。工具描述、返回内容和第三方服务器都需要建立信任边界，标准化连接不会自动消除提示注入或越权风险。

<a id="baidu-aigc-multimodal-agent-20260922-20260924-r2-q6"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%99%BE%E5%BA%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1891)，来源许可：GPL-3.0。

<a id="ka223ba3ffc5a"></a>

## 为什么 Bash 和文件写入工具必须强权限控制？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

Bash 和文件写入工具有真实副作用：

- 删除文件。
- 覆盖用户未保存工作。
- 修改配置。
- 泄露环境变量。
- 安装未知依赖。
- 访问网络。
- 提交或推送代码。
- 运行消耗资源的进程。

风险控制策略：

- 命令分类：只读、写入、网络、破坏性、长时间运行。
- 高风险命令强制确认。
- 禁止 `rm -rf`、`git reset --hard` 等除非用户明确要求。
- 写文件前检查是否有用户未保存或未归属改动。
- 使用 diff 展示变更。
- 对命令输出做脱敏。
- 限制工作目录。

面试中可以说：编码 Agent 最大风险不是“回答错”，而是“自动把错执行到真实仓库里”。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/02_%E7%BC%96%E7%A0%81Agent%E4%B8%8EAgentOS%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L279)，来源许可：GPL-3.0。

<a id="kee337f01897c"></a>

## 为什么 Worktree 隔离、Checkpoint 和 Rollback 对 Agent 很重要？

Agent 会自动编辑文件、运行命令、安装依赖、生成代码。没有隔离和回滚，错误动作会直接污染用户工作区。

**Worktree 隔离**：

- 每个 Agent 会话在独立 Git worktree 中工作。
- 多个 Agent 可并行探索。
- 避免覆盖用户未提交改动。
- 便于比较和选择最终 patch。

**Checkpoint**：

- 在高风险操作前保存文件系统快照或 Git 状态。
- 记录工具调用前后的 diff。
- 支持恢复到安全点。

**Rollback**：

- 当 Agent 改错、测试失败、用户不满意或命令产生副作用时恢复。
- 可按任务、文件或 checkpoint 回滚。

工程原则：

- 只读任务不需要重 checkpoint。
- 写文件、批量替换、依赖升级、格式化、迁移脚本前应 checkpoint。
- 回滚操作本身也要审计。
- 对生产 API 副作用不能只靠本地 rollback，需要补偿事务。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/09_%E8%87%AA%E8%BF%9B%E5%8C%96Agent%E4%B8%8E%E5%A4%9A%E5%B9%B3%E5%8F%B0%E8%BF%90%E8%A1%8C%E6%97%B6%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L535)，来源许可：GPL-3.0。

<a id="kec4b238865de"></a>

## 为什么GLM-4.6V需引入原生多模态工具调用能力？

传统工具调用依赖文本中转，导致多模态信息在转换中损耗。例如，将图像转为文本描述再调用搜索工具，可能丢失视觉细节（如图表颜色、布局比例）。GLM-4.6V通过URL直接传递图像/视频参数，实现端到端的多模态工具调用。  

以视觉网页搜索为例：用户上传商品截图询问“哪里能买到此物？”模型首先识别图像中的关键实体（如鞋子型号），自动触发多模态搜索工具（如Google Lens），工具返回的结果包含同类商品图片、价格、链接等混合信息。模型随后执行多模态对齐：比较截图与搜索结果图像的相似度，筛选最相关条目，最终生成含图片对比、价格分析的结构化报告。此过程避免人工截图中转，且直接理解搜索结果中的视觉信息（如折扣标签图标），形成“感知-检索-推理-输出”的闭环。  

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E5%A4%9A%E6%A8%A1%E6%80%81%E5%9F%BA%E7%A1%80/GLM-V%E7%B3%BB%E5%88%97%E6%A8%A1%E5%9E%8B%E6%A0%B8%E5%BF%83%E8%80%83%E7%82%B9.md#L71)，来源许可：GPL-3.0。

<a id="kf3c4670cff70"></a>

## 为什么不同模型需要不同 Tool Call Parser？

不同模型和推理服务的工具调用格式并不完全一致。

常见差异：

- OpenAI 风格 structured `tool_calls`。
- XML / ChatML `<tool_call>`。
- JSON 数组。
- Mistral `[TOOL_CALLS]`。
- Qwen / DeepSeek / Kimi / GLM 等各自格式。
- 原始 `/generate` endpoint 只返回文本，需要客户端解析。

Tool Call Parser 的作用：

- 从原始文本中提取工具名和参数。
- 处理 malformed JSON。
- 保留普通文本和工具调用边界。
- 为 Agent Loop 提供统一结构。
- 为训练生成 token mask 和 reward 对齐。

工程风险：

- 解析错误会导致工具误调用。
- 宽松解析可能被 prompt injection 利用。
- 多工具调用顺序必须保留。
- 解析失败要有 fallback 和失败标签。
- Parser 需要随模型版本更新。

面试中可以说：Tool Call Parser 是模型输出协议和 Agent Runtime 之间的适配层，决定了原始模型是否能可靠进入工具调用闭环。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/09_%E8%87%AA%E8%BF%9B%E5%8C%96Agent%E4%B8%8E%E5%A4%9A%E5%B9%B3%E5%8F%B0%E8%BF%90%E8%A1%8C%E6%97%B6%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L658)，来源许可：GPL-3.0。

<a id="k4d1bf6795dd7"></a>

## 为什么企业 Agent 平台需要控制平面？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

控制平面负责管理 Agent 的入口、配置、权限、路由、版本、状态和治理。没有控制平面，每个 Agent 应用都会各自管理工具、凭证、日志、评测和发布，最终变成不可控的影子 IT。

控制平面通常负责：

- Agent 注册和配置。
- 模型供应商和模型版本管理。
- Tool / MCP Server / Agent 服务注册。
- 用户、租户、角色和权限。
- 会话、任务和后台作业管理。
- 安全策略和审批流程。
- 评测集、发布门禁和灰度策略。
- 成本、限流和配额。
- 全链路 tracing 和审计。

数据平面则负责实际执行：

- 模型推理。
- 工具调用。
- RAG 检索。
- 代码执行。
- 浏览器操作。
- 业务 API 调用。

面试中可以说：控制平面决定“能不能做、用什么做、谁来审计”，数据平面负责“真正去做”。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/07_%E4%BC%81%E4%B8%9A%E7%BA%A7Agent%E5%B9%B3%E5%8F%B0%E4%B8%8E%E4%BA%A7%E5%93%81%E8%90%BD%E5%9C%B0%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L93)，来源许可：GPL-3.0。

<a id="k90bfb7e50816"></a>

## 为什么先做单 Agent，而不是直接 Multi-Agent？

单 Agent 的状态、Trace 和故障链路更短，通常也更容易评测。工具多并不等于必须拆成多个 Agent，可以先尝试：

- 按场景动态加载工具；
- 合并功能重叠的工具；
- 重写名称、描述和参数 Schema；
- 用代码路由处理边界清楚的分类；
- 为复杂任务隔离子上下文。

任务可以独立拆分，不同角色又需要大量专属上下文、差异明显的工具权限或独立维护责任时，Multi-Agent 带来的收益才可能抵消通信、成本和调试开销。

多 Agent 也不等于并行。它可以按固定顺序执行，可以在没有依赖的分支并行，也可以由 Manager 动态委派，或者把当前回合 Handoff 给 Specialist。

面试时要继续说明：拓扑由代码固定还是由模型决定，上下文是共享还是隔离，Agent 之间用什么结果契约，部分失败和并行写冲突怎样处理，最终由谁对结果负责。

关于 Multi-Agent 相关问题的总结，可以参考[多 Agent 协作系统设计](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/agent/multi-agent.md)这篇文章。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/interview-questions/agent-project-interview-guide.md#L176)，来源许可：Apache-2.0。

<a id="kaebc26ebcc0e"></a>

## 为什么多 Agent 不一定比单 Agent 更好？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

多 Agent 会带来额外复杂度：

- 通信成本增加。
- 上下文重复和信息丢失。
- 角色之间可能相互矛盾。
- 多个 Agent 可能争抢同一工具或文件。
- 错误会跨 Agent 传播。
- 调试难度大幅上升。
- token 和延迟成本更高。

什么时候单 Agent 更好？

- 任务短。
- 工具少。
- 目标明确。
- 不需要角色分工。
- 用户希望快速得到结果。

什么时候多 Agent 值得？

- 任务天然可拆。
- 需要并行探索。
- 需要互相审查。
- 不同子任务需要不同权限。
- 需要专家角色分工。

一句话：多 Agent 不是能力放大器的免费午餐，它更像组织管理。组织结构设计不好，人多反而更乱。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/03_Agent%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81%E7%BC%96%E6%8E%92%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L578)，来源许可：GPL-3.0。

<a id="kcafaa40dbb30"></a>

## 为什么很多 Agent 项目失败在“过度自主”？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

过度自主指系统给 Agent 太多目标、太多工具和太少约束，期望它自动完成复杂任务。常见后果包括：

- 计划过大，无法收敛。
- 工具调用过多，成本和延迟不可控。
- 中间结果没有验证，错误逐步放大。
- 上下文越来越长，任务目标逐渐漂移。
- 权限过宽，容易产生真实副作用。
- 没有人工审批，失败后难以追责。

优化思路：

- 把大任务切成可验证的小任务。
- 让 Agent 每一步产生结构化状态。
- 对高风险工具加入审批。
- 用 Workflow 限制关键路径。
- 设置最大步数、预算和超时。
- 在关键节点引入测试、评估器或人工确认。

一句话：生产级 Agent 的核心不是“让模型想做什么就做什么”，而是“让模型在明确边界内自主解决局部不确定性”。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/03_Agent%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81%E7%BC%96%E6%8E%92%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L121)，来源许可：GPL-3.0。

<a id="k3eaa6b6163b4"></a>

## 为什么生产级 Agent 需要 Provider Router 和 Tool Registry？

生产级 Agent 通常需要接入多个模型、多个工具、多个平台和多个技能。如果没有统一 Router 和 Registry，就会出现模型调用散落在各处、工具 schema 重复定义、权限不可治理、可观测性难以统一的问题。

**Provider Router** 负责：

- 多模型供应商接入。
- 模型能力查询。
- fallback。
- 成本和速率限制。
- reasoning / vision / tool calling 能力适配。
- API key 和凭证解析。

**Tool Registry** 负责：

- 工具 schema 注册。
- handler 调度。
- toolset 分组。
- 可用性检查。
- 权限和风险标记。
- 结果大小限制。
- 动态工具刷新，例如 MCP。

一句话：Provider Router 解决“用哪个脑”，Tool Registry 解决“有哪些手脚、能不能用、怎么审计”。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/09_%E8%87%AA%E8%BF%9B%E5%8C%96Agent%E4%B8%8E%E5%A4%9A%E5%B9%B3%E5%8F%B0%E8%BF%90%E8%A1%8C%E6%97%B6%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L267)，来源许可：GPL-3.0。

<a id="k34edfe7dfee8"></a>

## 为什么用 Agent，而不是普通 Workflow？

固定 Workflow 可以读取中间状态、走条件分支，也可以把 Agent 放进某个节点。选择方案时，需要确认下一步究竟由预定义代码或图规则控制，还是由模型在运行时选择动作、工具和路径。

在售后案例中，鉴权、确认、工单写入和审计都能提前确定，应该放进 Workflow。用户可能只说“坏了”，也可能提供订单号、故障照片和已经尝试过的处理方式；如果候选路径难以靠有限规则穷举，并且评测证明模型决策确实带来收益，查询订单、检索政策还是继续追问这一小段才适合交给 Agent。

反过来，如果工单类别、必填字段和处理规则都有限且稳定，“意图分类 + 表单补齐 + 固定规则”可能已经够用。自然语言入口本身不能证明项目必须使用 Agent。

这个案例适合采用混合架构：

> 用确定性 Workflow 固定安全边界，在路径不确定的局部嵌入 Agent Loop。

关于 Workflow、Graph 和 Loop 的区别，可以继续看 [AI 工作流中的 Workflow、Graph 与 Loop](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/agent/workflow-graph-loop.md)。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/interview-questions/agent-project-interview-guide.md#L162)，来源许可：Apache-2.0。

<a id="kece0bf4d0b82"></a>

## 为什么编码 Agent 是 Agent 工程落地最快的场景？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

原因有五个：

1. **工具环境明确**

   代码仓库、文件系统、Shell、Git、测试框架天然适合工具调用。

2. **反馈可验证**

   编译、测试、lint、类型检查、CI 都能提供客观反馈。

3. **上下文结构化**

   代码文件、依赖、错误日志、diff、issue 都是相对结构化的信息。

4. **用户愿意审查**

   开发者可以 review diff，适合 human-in-the-loop。

5. **ROI 清晰**

   修 bug、写测试、重构、文档、代码审查都能直接节省工程时间。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/02_%E7%BC%96%E7%A0%81Agent%E4%B8%8EAgentOS%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L142)，来源许可：GPL-3.0。

<a id="kc5f58efc0a12"></a>

## 为什么自进化 Agent 必须有防失控机制？

自进化 Agent 的风险比普通 Agent 更高，因为它可能改变未来行为。

主要风险：

- 把模型猜测写成事实。
- 把一次偶然成功固化为通用流程。
- 把恶意网页或用户注入写入 Skill。
- 自动修改高价值 Skill 导致能力退化。
- 删除仍然有用的旧经验。
- 后台任务无限运行或消耗过多成本。
- 自我强化错误偏好。
- 逐步扩大权限边界。

防失控机制：

- 自进化任务使用受限工具集。
- 只允许修改特定目录或特定类型资产。
- 内置 Skill / 官方 Skill 默认只读或 pinned。
- 自动删除改为归档，可恢复。
- 写入前做敏感信息和 prompt injection 检查。
- Curator 产出报告和 diff。
- 用户可暂停、自定义周期、手动 dry-run。
- 关键变更需要人工审批。
- 所有变更进入审计日志。

面试金句：自进化 Agent 的核心不是“自动改自己”，而是“在可审计、可回滚、可约束的知识生命周期中持续改进”。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/09_%E8%87%AA%E8%BF%9B%E5%8C%96Agent%E4%B8%8E%E5%A4%9A%E5%B9%B3%E5%8F%B0%E8%BF%90%E8%A1%8C%E6%97%B6%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L114)，来源许可：GPL-3.0。

<a id="kfda43fd954fe"></a>

## 为什么要用agent解决这个场景

**回答：**

先判断场景是否存在运行时才能确定的步骤：用户请求开放、需要多次查数据或调用工具，且下一步依赖上一步结果时，Agent 有价值。若只是固定字段抽取或确定顺序的审批，用分类器加工作流更容易验收。

可以比较三条基线：固定工作流、单次模型调用、受约束 Agent。保持模型和工具一致，统计端到端完成率、重试、延迟、成本与人工接管。只有动态决策收益覆盖复杂度时，才能说明“为什么用”。

例如售后查询可能需要先识别订单，再根据物流状态决定查询轨迹或售后规则；查询部分可动态编排，退款等写操作仍由业务权限和确认机制控制。这里是设计示例，个人项目应替换为实际经历。

<a id="jd-damodel-20251211-20260205-p3-q2"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E4%BA%AC%E4%B8%9C%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L395)，来源许可：GPL-3.0。

<a id="kd5af3a3ca50e"></a>

## 为什么说 MCP 像 Agent 工具生态的 USB-C？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

MCP 的目标是为模型应用连接外部上下文和工具提供统一接口。它像 USB-C 的地方在于：

- 应用不需要为每个工具写一套私有集成。
- 工具提供方可以按统一协议暴露能力。
- 同一个 MCP Server 可以被不同 Agent Host 复用。
- 工具、资源、提示模板可以被动态发现。
- 本地工具和远程服务可以采用统一交互模型。

没有 MCP 时：

```math
\text{Agent App} \times \text{Tool Provider} = N \times M \text{ 个私有连接器}
```
有 MCP 后：

```math
\text{Agent Host} \leftrightarrow \text{MCP Client} \leftrightarrow \text{MCP Server} \leftrightarrow \text{Tool/Data Source}
```
当然，MCP 不是万能的。它主要标准化“工具和上下文接入”，不负责所有业务权限、工作流编排和多 Agent 协作。实际落地时还需要 RBAC、审计、沙箱、评测、模型网关和业务系统治理。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/04_MCP%E4%B8%8EA2A%E5%8D%8F%E8%AE%AE%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L99)，来源许可：GPL-3.0。

<a id="k0db14ea55c09"></a>

## 为什么超时不能直接判定为执行失败？

面试官问“模型或工具超时了怎么办”，不少人的第一反应是“重试几次不就行了”。如果继续追问“写操作已经执行成功，只是响应丢了呢”，原来的回答就不够用了。

这时再按原样重试一次，可能导致重复创建工单或重复退款。

问题出在对超时的理解上。超时只说明调用方在期限内没拿到结果，服务端那边可能是三种状态里的任何一种：请求根本没到达、正在执行、已经执行完但响应丢在了网络上。调用方无法区分，所以不能把超时直接当成失败。

查询类接口好办，读操作没有副作用，可以在总时间预算内对瞬时错误做有限重试。写操作不行，创建工单、退款这类请求一旦盲重试，就可能造成重复副作用。

更稳妥的方案是：

1. 创建逻辑动作时生成一次稳定的 `actionId`，并用它参与业务幂等键；同一动作在 SDK 重试、消息重投和人工恢复中始终复用，新动作才生成新 ID；
2. 服务端用唯一约束或请求记录识别重复请求；
3. 同一幂等键携带不同参数时确定性拒绝，不能静默返回第一次结果；
4. 超时后先按幂等键查询执行状态；
5. 状态仍不明确时进入对账或人工处理，而不是无限重试；
6. 将最终业务对象 ID 回写到任务状态和审计日志。

![模型调用重试与幂等处理流程](https://oss.javaguide.cn/github/javaguide/ai/llm/llm-api-engineering-retry-idempotency.webp)

重试还需要指数退避、随机抖动、最大次数、总截止时间和重试预算。模型 SDK、网关、HTTP Client、工具适配器和工作流节点不能各自独立重试三次，否则调用次数会被乘法放大。比较稳妥的做法是共享总 Deadline 和 Retry Budget，并在 Trace 中记录每一层的 `attempt`。

调用方超时、Future 被取消或者用户断开 SSE，也不代表远端写操作已经停止。副作用可能稍后成功，所以取消之后仍要保留幂等键、状态查询和对账。参数错误、权限失败和业务拒绝属于确定性错误，应立即失败；限流、临时网络错误等才可能在预算内重试。详细内容见 [超时和重试机制详解](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/high-availability/timeout-and-retry.md) 与 [接口幂等性](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/high-availability/idempotency.md)。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/interview-questions/agent-project-interview-guide.md#L287)，来源许可：Apache-2.0。

<a id="kb20e56e5439c"></a>

## 为什么选择直接根据业务逻辑实现，而不是使用现成的Agent框架？

**回答：**

当流程固定、节点数量有限、业务系统已有任务队列和状态表时，直接实现可以减少抽象层，并让权限、事务和异常处理与现有服务保持一致。这个选择成立的前提，是团队能清楚维护状态转换、重试、可观测性和测试。

代价也需要说明：持久化恢复、复杂分支、人工中断、状态兼容和执行追踪都可能变成自研负担。当流程开始包含多轮工具决策、长时间等待或大量动态分支时，采用成熟编排框架可能更划算。不能只用“框架太重”或“自己写更灵活”作为论据。

可以先将节点函数与编排逻辑解耦，定义稳定的输入输出和产物存储协议，再依据实际复杂度决定是否迁移。用同一个代表性任务比较实现量、恢复能力、调试效率和运行成本，说明选择是有条件的工程判断。

<a id="sftech-ai-dev-20261019-463a64c7-g4-q04"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%A1%BA%E4%B8%B0%E7%A7%91%E6%8A%80%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L416)，来源许可：GPL-3.0。

<a id="k621417dd2506"></a>

## 为什么长期运行 Agent 需要 interrupt、resume、cron 和 background task？

长期运行 Agent 不再是一次请求-响应，而是持续执行任务。

四类能力分别解决：

1. **interrupt**

   用户随时打断错误方向、停止危险操作或修改目标。

2. **resume**

   长任务中断后恢复上下文、计划、文件状态和工具状态。

3. **cron**

   定期触发日报、巡检、备份、监控、知识整理、Curator 维护。

4. **background task**

   让耗时任务在后台运行，并在完成、失败或需要审批时通知用户。

面试中可以说：长期运行 Agent 必须从“同步聊天应用”升级为“事件驱动任务系统”，核心是 task id、状态机、事件流、持久化和可取消性。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/09_%E8%87%AA%E8%BF%9B%E5%8C%96Agent%E4%B8%8E%E5%A4%9A%E5%B9%B3%E5%8F%B0%E8%BF%90%E8%A1%8C%E6%97%B6%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L241)，来源许可：GPL-3.0。

<a id="kf3f66cef86f9"></a>

## 为什么项目采用多 Agent？如果改成单 Agent，会遇到什么问题？

**回答：**

采用多 Agent 应由任务结构决定，而不是为了展示复杂架构。合理理由包括：不同子任务需要差异明显的工具、权限或上下文；任务可以并行；需要把规划、执行和验证隔离；或单个上下文装下全部领域知识会产生工具混淆与信息污染。例如会议系统可把检索、行动项抽取和合规检查作为边界明确的角色。

单 Agent 的优势是状态简单、通信少、延迟和成本低。问题在于工具数量增多后选择空间扩大，异构任务的 Prompt 互相干扰，权限边界难以区分，长轨迹使上下文膨胀，单点错误会影响全局。但这些问题也可以通过单 Agent + 确定性 Workflow、工具路由和模块化状态缓解。

多 Agent 会引入新的代价：任务切分错误、消息复制、全局状态不一致、结论冲突、级联失败和观测困难。每个角色都调用大模型还会放大 token、延迟和方差。因此要用消融实验比较单 Agent、Workflow 和多 Agent，在相同任务集上观察成功率、P95 延迟、成本、冲突率和恢复能力。

成熟回答应说明具体拆分带来了什么可测收益，并明确哪些节点其实是确定性服务而非 Agent。角色名称本身不构成架构价值。

<a id="pinduoduo-ai-agent-20260816-q30"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E6%8B%BC%E5%A4%9A%E5%A4%9A%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L634)，来源许可：GPL-3.0。

<a id="k2ff36addb257"></a>

## 为金融客服场景设计一个RAG和加Agent的系统，从成本和性能综合考虑如何选择资源，例如模型选型、硬件资源，是否需要做一些后训练？

**回答：**

金融客服应采用“规则/工作流优先，RAG 提供受控知识，Agent 负责有限编排”的架构。小模型做路由、分类和改写，较强模型处理复杂解释；知识库使用结构化条款、版本、适用时间和权限，召回后 Rerank 并强制引用。金额、利率、资格、交易状态由后端工具和规则引擎确认，不能由模型自由生成。

硬件按 QPS、P95、上下文、并发和模型精度估算，可用量化、缓存、批处理和分层模型控制成本。后训练优先用于格式、工具调用、领域术语和拒答行为；动态业务知识优先放知识库和工具，不要频繁微调。上线需要灰度、人工接管、审计和回滚。

<a id="tencent-llm-collection-20260903-q68"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E8%85%BE%E8%AE%AF%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1022)，来源许可：GPL-3.0。

<a id="kbdab4a5d0bf0"></a>

## 了解过 spec-drivening 的 code agent 吗？

<a id="batch2-p1-q10"></a>

**相关解释：** [Agent常见模式（ReAct/Plan and Execute等）](../15-%E5%89%8D%E7%AB%AF%E4%B8%8E%E6%B5%8F%E8%A7%88%E5%99%A8/React%E4%B8%8E%E7%BB%84%E4%BB%B6%E7%8A%B6%E6%80%81-01.md#k93a12d0c9256)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E6%8B%BC%E5%A4%9A%E5%A4%9A%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L138)，来源许可：GPL-3.0。

<a id="kb306c31d8b46"></a>

## 什么时候不应该使用 MCP 或 A2A？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

不应该为了追赶概念而滥用协议。

不适合 MCP 的情况：

- 只是应用内一个简单函数，直接 Function Calling 更轻。
- 工具不会被多个 Host 复用。
- 工具没有清晰权限边界。
- 暴露 MCP 会增加不必要的攻击面。
- 团队没有能力维护 Server 版本、安全和监控。

不适合 A2A 的情况：

- Agent 都在同一个进程里，内部函数调用即可。
- 只是固定流程节点，不需要独立 Agent 服务。
- 没有跨团队、跨框架、跨部署互操作需求。
- 延迟敏感，远程 Agent 调用成本过高。
- Remote Agent 的能力和责任边界不清。

选择原则：

- 简单函数用 Function Calling。
- 可复用工具和上下文服务用 MCP。
- 独立 Agent 服务互调用 A2A。
- 强流程控制用 Workflow / LangGraph。
- 高风险生产场景优先治理和权限，而不是优先接更多协议。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/04_MCP%E4%B8%8EA2A%E5%8D%8F%E8%AE%AE%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L762)，来源许可：GPL-3.0。

<a id="k6533e97aec2c"></a>

## 什么时候反思会带来负收益？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

Reflection 不是越多越好。负收益常见于：

- 没有可靠 evaluator，模型只能自说自话。
- 反思内容空泛，不能改变下一步行动。
- 任务很简单，反思增加不必要成本。
- 模型把错误反思写入长期记忆，污染后续任务。
- 多轮反思导致过度修正，偏离原始需求。
- 反思暴露过多中间推理，增加安全和隐私风险。

优化建议：

- 只有失败、低置信度或高风险任务才触发反思。
- 反思必须结构化：失败原因、证据、修正策略、下步行动。
- 反思写入长期记忆前要经过质量过滤。
- 对同一问题设置最大反思轮数。
- 反思要结合外部反馈，例如测试结果、评测器、用户确认。

面试中可以说：Reflection 的价值依赖反馈信号。如果没有外部验证，它很容易从“纠错机制”退化成“更长的幻觉”。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/03_Agent%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81%E7%BC%96%E6%8E%92%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L336)，来源许可：GPL-3.0。

<a id="k5534b78d7424"></a>

## 什么是agent

**回答：**

Agent 是围绕目标执行“观察—决策—行动—反馈”的系统：模型提出下一步，运行时校验权限和参数，工具作用于外部环境，结果再进入后续决策。它适合步骤不确定、需要检索或调用外部能力的任务；固定流程优先用工作流或状态机。

生产实现要限制步数、时间、费用和工具权限，记录任务状态与证据，为写操作配置幂等和结果核对。反思模块可以根据错误类型、工具返回和验收规则选择重试、修正、重规划或人工接管，不能只让模型重新生成一段解释。

<a id="jd-damodel-20251211-20260205-p3-q3"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E4%BA%AC%E4%B8%9C%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L406)，来源许可：GPL-3.0。

<a id="k26f798a07093"></a>

## 什么是人在回路（Human-in-the-loop）机制？在Agent系统开发中，如何合理设计人工审批断点，保障系统运行可靠性？

<a id="batch4-p2-q17"></a>

**相关解释：** [Agent常见模式（ReAct/Plan and Execute等）](../15-%E5%89%8D%E7%AB%AF%E4%B8%8E%E6%B5%8F%E8%A7%88%E5%99%A8/React%E4%B8%8E%E7%BB%84%E4%BB%B6%E7%8A%B6%E6%80%81-01.md#k93a12d0c9256)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L428)，来源许可：GPL-3.0。

<a id="kab983a3fb67d"></a>

## 什么是多智能体通信协议的可扩展性解决方案​？

解决通信瓶颈需要三层设计：

​​（1）协议分层​​：类似TCP/IP的物理-逻辑分离，底层采用轻量级二进制编码（如Protocol Buffers），减少80%传输负载；

​​（2）动态路由​​：基于任务复杂度的自适应拓扑切换，简单任务用星型网络（中心节点处理），复杂任务切换至网状网络；

​​（3）语义压缩​​：通过LLM提炼核心意图，将"建议明天10点会议，需准备销售数据"压缩为<Mt10_SD>；

​​（4）案例​​：阿里云城市大脑项目中，交通信号控制智能体通过这种架构实现2000+节点协同，时延控制在50ms内；

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E5%A4%9A%E6%A8%A1%E6%80%81%E5%9F%BA%E7%A1%80/%E5%A4%9A%E6%A8%A1%E6%80%81-%E5%89%8D%E6%B2%BF%E6%8A%80%E6%9C%AF.md#L356)，来源许可：GPL-3.0。

<a id="k76ac76707926"></a>

## 介绍一下你们的TSM平台和Agent功能

**回答：**

TSM 在不同组织里可能指不同平台，题目没有给出全称、用户和职责，不能据此断言它是某个公开产品。实际回答首先说明自己项目里的准确名称、服务对象和业务边界。

然后把平台能力与 Agent 能力分层：平台负责身份、资源、任务、配置、审计和数据管理；Agent 接收目标，读取授权上下文，选择工具，执行并验证任务。用一个真实场景说明 Agent 如何调用平台已有 API，而不是让模型绕过平台权限直接修改底层资源。

如果按运维或训练服务平台来设计，工具可能包括查询作业状态、检索错误日志、诊断资源瓶颈和生成操作方案；重启、扩缩容或修改配置属于更高风险动作，需要明确权限与审批。这里是条件性设计示例，不代表该 TSM 平台的真实功能。

回答还应交代上线范围、哪些能力只是建议、哪些可自动执行、失败如何转人工，以及成功率与误操作如何度量。未公开的内部实现只依据本人参与的事实说明。

<a id="alibaba-qwen-20260916-q15"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L2132)，来源许可：GPL-3.0。

<a id="k6700c718fe64"></a>

## 介绍你Agent的三个模块

<a id="batch2-p1-q10"></a>

**相关解释：** [Agent常见模式（ReAct/Plan and Execute等）](../15-%E5%89%8D%E7%AB%AF%E4%B8%8E%E6%B5%8F%E8%A7%88%E5%99%A8/React%E4%B8%8E%E7%BB%84%E4%BB%B6%E7%8A%B6%E6%80%81-01.md#k93a12d0c9256)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%95%86%E6%B1%A4%E7%A7%91%E6%8A%80%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L91)，来源许可：GPL-3.0。

<a id="k890de4024ef3"></a>

## 任务分解、计划维护和执行反馈如何协作？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

Plan-and-Solve 和 Plan-and-Execute 都强调“先规划，再执行”，目标是减少模型直接作答时常见的三类错误：

- 步骤缺失。
- 计算错误。
- 任务理解偏差。

它们适合：

- 数学推理。
- 多步骤数据分析。
- 代码修改任务。
- 研究报告生成。
- 企业流程执行。
- 需要中间状态可检查的任务。

核心思想可以表示为：

```math
\text{Task} \rightarrow \text{Plan} \rightarrow \text{Step Execution} \rightarrow \text{Verification} \rightarrow \text{Answer}
```

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/03_Agent%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81%E7%BC%96%E6%8E%92%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L257)，来源许可：GPL-3.0。

<a id="k0aa8806f2217"></a>

## 企业 Agent 产品与开发框架应如何分类？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

可以按定位分类：

| 类型 | 代表 | 适合场景 |
| --- | --- | --- |
| 通用 Agent SDK | OpenAI Agents SDK、Google ADK | 自定义 Agent 应用、多 Agent、工具调用 |
| 工作流 / 状态图 | LangGraph | 复杂流程、长任务、human-in-loop |
| 企业集成框架 | Semantic Kernel | .NET / Java / 企业插件生态 |
| 数据和 RAG Agent | LlamaIndex | 知识库、文档、数据密集型 Agent |
| 多 Agent 协作框架 | AutoGen、CrewAI | 研究探索、角色分工、协作任务 |
| 低代码平台 | Dify、Coze、Copilot Studio | 业务人员快速搭建、客服、知识库 |
| 云厂商 Agent 平台 | Vertex AI Agent Builder、Bedrock Agents、Azure AI Foundry Agent Service | 云上企业集成、托管运行、治理 |

选型关键不是“哪个最火”，而是：

- 是否满足数据和权限要求。
- 是否支持需要的工具生态。
- 是否能接入企业身份系统。
- 是否能评测和观测。
- 是否支持私有化或混合部署。
- 是否能承载长任务和复杂状态。
- 团队是否有维护能力。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/07_%E4%BC%81%E4%B8%9A%E7%BA%A7Agent%E5%B9%B3%E5%8F%B0%E4%B8%8E%E4%BA%A7%E5%93%81%E8%90%BD%E5%9C%B0%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L790)，来源许可：GPL-3.0。

<a id="k3b81298439bd"></a>

## 企业 Agent 平台怎样组织控制面与执行面？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

企业级 Agent 平台通常包括：

1. **Agent Builder**

   创建和配置 Agent、prompt、工具、知识库、工作流和测试样例。

2. **Agent Runtime**

   负责模型调用、工具调用、上下文、状态、streaming、重试、handoff。

3. **Model Gateway**

   统一接入 OpenAI、Anthropic、Google、本地模型、企业私有模型。

4. **Tool / MCP Registry**

   管理工具、MCP Server、OpenAPI、数据库连接器、浏览器、代码执行器。

5. **Agent Registry**

   管理可被复用或 A2A 调用的 Agent 服务。

6. **Knowledge / RAG Platform**

   管理文档、索引、切片、向量、重排、权限过滤。

7. **Memory / Session Store**

   管理会话、任务状态、长期记忆、用户画像和项目记忆。

8. **Workflow Engine**

   支持状态机、DAG、审批、人机协作、重试、补偿、长任务。

9. **Governance**

   IAM、RBAC、ABAC、审计、数据分级、敏感信息脱敏、安全策略。

10. **AgentOps**

   评测、tracing、监控、灰度、回滚、成本治理、失败样本回流。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/07_%E4%BC%81%E4%B8%9A%E7%BA%A7Agent%E5%B9%B3%E5%8F%B0%E4%B8%8E%E4%BA%A7%E5%93%81%E8%90%BD%E5%9C%B0%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L150)，来源许可：GPL-3.0。

<a id="kfa15994789c6"></a>

## 企业内部 MCP Registry / Tool Gateway 应该如何设计？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

企业不会希望每个团队随意接入未知 MCP Server。更合理的做法是建设 MCP Registry 或 Tool Gateway。

核心能力：

- MCP Server 注册、审核、版本管理。
- 工具能力目录和搜索。
- 所属团队、数据分级、风险等级标注。
- 认证、授权、RBAC、SSO。
- 工具调用审计。
- 参数和返回值脱敏。
- 调用限流、配额和成本统计。
- 安全扫描和 Prompt Injection 检测。
- 灰度发布和回滚。
- 工具可用性监控。
- 统一文档和示例。

推荐架构：

```math
\text{Agent Host} \rightarrow \text{Tool Gateway / MCP Registry} \rightarrow \text{Approved MCP Servers} \rightarrow \text{Enterprise Systems}
```
这样做的好处：

- Agent 只能发现被批准的工具。
- 企业可以集中治理工具权限。
- 安全团队能审计所有工具调用。
- 业务团队可以独立发布工具，但不绕过平台治理。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/04_MCP%E4%B8%8EA2A%E5%8D%8F%E8%AE%AE%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L526)，来源许可：GPL-3.0。

<a id="k25778e329b4d"></a>

## 低代码 Agent 平台适合什么场景，不适合什么场景？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

适合：

- 知识库问答。
- 客服机器人。
- 表单收集和简单流程。
- 内容生成。
- 内部助手。
- 快速 PoC。
- 业务人员维护话术和流程。

不适合：

- 高复杂状态机。
- 深度代码仓库操作。
- 高风险生产写操作。
- 强定制工具链。
- 复杂权限和多租户隔离。
- 需要严格评测和回滚的核心业务。

低代码平台的价值是降低构建门槛，但不能替代工程治理。真正生产级的 Agent 仍然需要权限、安全、评测、观测和版本管理。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/07_%E4%BC%81%E4%B8%9A%E7%BA%A7Agent%E5%B9%B3%E5%8F%B0%E4%B8%8E%E4%BA%A7%E5%93%81%E8%90%BD%E5%9C%B0%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L543)，来源许可：GPL-3.0。

<a id="kbf84de1366a4"></a>

## 你了解哪些 Coding Agent？OpenCode、Gemini CLI、Codex CLI 和 Claude Code 有什么区别？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐ (3/5)**

OpenCode、Gemini CLI、Codex CLI 和 Claude Code 都可围绕代码仓库进行文件读取、编辑、命令执行和多步任务处理。比较时应按运行位置、模型接入、项目上下文、权限、恢复机制和团队治理来评估，不能仅按名字推断能力，也不能把产品不同入口的功能混在一起。

| 产品 | 可确认的定位 | 选型时重点核对 |
| --- | --- | --- |
| OpenCode | 开源编码 Agent，支持多模型提供方与终端交互 | 提供方适配、插件和团队部署方式 |
| Gemini CLI | 围绕 Gemini 生态的开源终端 Agent | 认证方式、可用模型、扩展与工具权限 |
| Codex CLI | OpenAI 的本地终端编码 Agent，可读写选定目录并运行命令 | 沙箱与审批配置、项目指令、运行和恢复方式 |
| Claude Code | Anthropic 的编码 Agent 产品，提供终端等入口 | 仓库指令、权限模式、工具与团队工作方式 |

具体模型、计费、支持平台和默认权限会随版本及账户变化，面试时注明实际体验的版本。用同一仓库、相同任务和测试衡量正确性、无关改动、失败恢复、时延与总成本；不要用一次演示宣布某款工具全面领先。没有实际用过的工具应表述为文档了解。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/02_%E7%BC%96%E7%A0%81Agent%E4%B8%8EAgentOS%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L170)，来源许可：GPL-3.0。

<a id="k5486d4bcabb0"></a>

## 你们的这个plan能力是怎么和agent loop配合的？

**回答：**

Plan 表达任务的阶段目标、依赖和验收条件；Agent loop 负责在当前状态下执行一步、观察结果并推进。两者可以结合，但计划不能只是塞进 Prompt 的一段不会更新的文本。

将计划保存为版本化结构，每个步骤包含 `step_id、goal、depends_on、status、expected_artifacts、acceptance`，必要时记录资源预算和权限要求。loop 根据当前可执行步骤组装上下文，让模型提出行动，再由确定性运行时执行与校验。

一个步骤可能需要多轮工具调用，也可能不调用工具。只有验收条件满足才标记完成；独立步骤可并发，有依赖或共享副作用的步骤受控串行。模型提出的新计划需要检查依赖闭环、越权与预算，再以新版本提交。

简单任务直接用短循环更高效，复杂长任务再引入显式计划。规划的收益要抵消额外推理、过时计划和维护成本，不能把计划越长当作推理越好。

<a id="alibaba-qwen-20260916-q16"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L2145)，来源许可：GPL-3.0。

<a id="k7a248631caab"></a>

## 你做的 Agent 系统采用的是什么框架？

<a id="batch1-p1-q3"></a>

**相关解释：** [Agent常见模式（ReAct/Plan and Execute等）](../15-%E5%89%8D%E7%AB%AF%E4%B8%8E%E6%B5%8F%E8%A7%88%E5%99%A8/React%E4%B8%8E%E7%BB%84%E4%BB%B6%E7%8A%B6%E6%80%81-01.md#k93a12d0c9256)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/vivo%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L56)，来源许可：GPL-3.0。

<a id="kf147aeb2a548"></a>

## 你在开发AI Agent的过程中，总结过哪些常用的设计模式，这些设计模式分别适合解决什么类型的问题。

**回答：**

选择 Agent 模式之前先判断是否需要自主决策。步骤固定、输入输出明确的任务，用确定性工作流通常更容易测试和追责；只有路径依赖中间观察、需要工具探索时，才让模型承担更大的调度责任。

| 模式 | 主要机制 | 适用任务与风险 |
|---|---|---|
| Prompt chaining / 固定工作流 | 按已知依赖分步执行 | 提取、校验、生成等稳定流程；错误可能逐步传播 |
| Routing | 先分类再选择模型、工具或子流程 | 多类型请求；路由误判需要兜底 |
| ReAct | 交替选择行动、执行工具并读取观察 | 检索、诊断等动态交互；需限制循环与工具权限 |
| Plan-and-Execute | 先生成阶段计划，再逐步执行 | 依赖较复杂的任务；计划可能随环境变化失效 |
| Evaluator-Optimizer | 评估产物并有界修订 | 存在可操作评价标准的生成与修复；防止自评自证 |
| 并行与协调者-工作者 | 拆成独立子任务后聚合 | 多文档分析和多渠道验证；有重复成本及状态冲突 |
| 人工介入 | 在风险或不确定性节点暂停审批 | 高影响写操作；需持久化状态与避免审批后重复执行 |

这些模式可以组合，但“多 Agent”不是性能或正确性的保证。每增加一个模型调用，都引入延迟、成本和新的失败可能；优先选能完成任务的最小结构。

不论何种模式，系统都需要状态、预算、超时、终止条件、幂等、审计和评测。ReAct 的实现可以记录行动、观察和结构化决策摘要，不必要求模型披露隐藏的逐字思维链。

<a id="hengsheng-ai-dev-20260923-q16"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E6%81%92%E7%94%9F%E7%94%B5%E5%AD%90%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L308)，来源许可：GPL-3.0。

<a id="k23d156fadf90"></a>

## 你如何理解Agent中Harness的概念？

**回答：**

Agent Harness 可以理解为包围模型、让模型能够稳定完成任务的运行时控制层。模型负责在当前上下文中生成判断或动作，但 Harness 负责提供上下文、工具、状态、权限、循环控制、预算、错误处理、验证和观测。它不是单纯的 Prompt 模板，也不是模型本身。

一个生产级 Harness 通常包含：

- **Context 管理。** 组织系统指令、用户请求、任务状态、历史摘要、检索证据和工具观察，并控制 Token 预算。
- **Tool Runtime。** 暴露版本化工具 Schema，完成参数校验、鉴权、超时、重试、幂等和副作用隔离。
- **Orchestrator。** 驱动 ReAct、Plan-and-Execute 或工作流状态机，限制步数、并发、成本和截止时间。
- **Memory/RAG。** 管理短期状态、长期记忆、文档检索和权限，而不是把所有内容无差别塞给模型。
- **Verifier 与 Guardrail。** 用测试、数据库状态、规则和人工审批判断动作是否可执行、结果是否达标。
- **Observability。** 记录 Trace、Prompt/工具版本、Token、延迟、错误、回放和指标。

因此，Agent 的可靠性不是由模型能力单独决定的，而是模型、Harness 和外部环境共同构成的系统属性。优秀 Harness 的判断标准是：面对工具失败、上下文超限、用户取消、权限变化和模型输出不规范时，系统是否仍能安全、可解释、可恢复地运行。

**具体 Harness 的比较。** DeepSeek Harness 的 `dsh` 基于 Cordis 组织插件，模型适配、工具、会话日志和 Agent 循环均可组合；Pi 提供精简终端执行环境，默认工具为 `read、write、edit、bash`，通过扩展和 Skills 定制工作流。插件生命周期清理不代表已经发生的业务副作用被回滚。对两者的实验应固定模型、任务集、工具权限和预算，比较任务成功率、P95 延迟、每次成功任务成本与恢复能力；DeepSeek Harness 的 developer preview 状态还要求评估兼容性风险。

<a id="bytedance-agent-dev-20260903-q6"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%AD%97%E8%8A%82%E8%B7%B3%E5%8A%A8%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1149)，来源许可：GPL-3.0。

<a id="k9d7926598ceb"></a>

## 你实际使用了 LangGraph 框架吗？哪些流程由 LangGraph 编排，哪些由 Agent Runtime 自己处理？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

先如实回答是否实际使用。若使用过，给出 State Schema、节点、条件边、checkpointer、线程标识和暂停恢复方式，并指出自己实现与框架提供的部分；若只是研究或计划接入，就明确这个边界，不能把自写状态机说成 LangGraph 项目经验。

一种合理分工是 LangGraph 编排意图路由、检索子图、槽位收集、人工确认和恢复；应用 Runtime 负责认证上下文、模型与工具适配、预算、事件发送及业务幂等。框架内部也可能承担部分 Runtime 职责，所以必须以实际代码边界为准。

面试中展示一次失败恢复：哪一步写了 checkpoint，哪一步发起外部写操作，恢复时哪些代码会重跑，如何避免重复预约。再解释为什么选图编排而非简单函数流程；如果业务只有线性三步且无需持久化，额外框架可能没有足够收益。

**回答框架选型时，把状态持有者画出来。** 哪个组件维护图的 checkpoint，哪个服务保存预约事实，哪个模块签发确认凭据，哪个进程负责工具重试，都应能在代码中找到对应位置。两个组件可以共享进程，但不应互相假定对方已经完成授权或幂等。

可以准备一个不依赖大模型的确定性演练：用固定意图和工具返回驱动状态流，注入断连、乱序事件和重启，先证明控制流程满足约束；再接入模型观察识别与决策误差如何进入系统。控制层验证通过不代表模型能力通过，二者结合才构成完整 Agent 验收。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/03_Agent%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81%E7%BC%96%E6%8E%92%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L657)，来源许可：GPL-3.0。

<a id="k25092ef273ed"></a>

## 你平时使用 AI Coding 工具的完整开发工作流是什么？

**回答：**

可以把流程组织成“明确目标、建立证据、受控实现、独立验证、持续反馈”，并用一个真实任务串联。下面是一套可落地的流程，而非对个人经历的代写。

1. 明确输入输出、边界条件和验收标准，检查数据权限、部署约束与已有变更。缺陷先获得最小复现，需求先确认可观察的成功条件。
2. 让 Agent 阅读目录、项目约定、相关模块、依赖版本与已有测试，形成影响范围。对复杂任务写出短计划和待验证假设；小改动不强行增加流程。
3. 在独立分支或工作区中按小步骤实现。将相关文件、接口契约和失败日志提供给 Agent；有依赖的步骤顺序执行，独立调研或模块实现才并行。
4. 按风险验证：语法和类型检查、针对性单测、必要集成测试、真实场景回放。关键算法用独立 oracle，界面用浏览器检查；测试通过之后仍查看代码差异、错误路径和边界。
5. 由开发者确认数据迁移、权限、幂等、性能和依赖风险。发布按团队流程灰度、观测并保留回滚条件，结果回读而不是只看命令退出码。
6. 把反复出现的规范、故障处理和验证命令沉淀为项目说明、自动化检查或 Skills，修复根因后再扩展自动执行范围。

衡量流程看需求到验收的时长、一次通过率、返工率、线上缺陷与人工接管次数。AI 可以承担更多执行工作，工程师仍需对问题定义、验证质量和交付负责。

**八股**

<a id="bytedance-agent-autumn-20260916-q18"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%AD%97%E8%8A%82%E8%B7%B3%E5%8A%A8%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1500)，来源许可：GPL-3.0。

<a id="k193379803600"></a>

## 你平时怎么控制 Agent 并发量？

**回答：**

我会采用分层并发预算，而不是只设置一个全局线程数。

入口层先做鉴权、配额和 admission control；任务进入有界队列，队列满时明确拒绝、降级或延迟执行，不能无限堆积。运行时按 `tenant -> user -> task -> model/tool` 设置并发上限：模型调用受 RPM/TPM 和成本预算约束，浏览器/代码沙箱按实例池约束，数据库和第三方 API 按连接池及对方限额约束。

实现上常用：

- `Semaphore` 限制同时执行的模型或工具调用；
- Token Bucket/Leaky Bucket 控制一段时间内的请求速率；
- Bulkhead 为不同租户、工具和任务类型隔离资源；
- 有界队列与 backpressure 防止生产速度长期高于消费速度；
- 对同一业务实体使用幂等键、版本号或单写者，避免并发副作用；
- 并行分支设置总 deadline、最大 fan-out、取消传播和 partial result 策略。

并发值应通过压测和线上反馈校准。可以根据 429、工具错误率、队列等待和 P95 动态降低上限，稳定后缓慢探测增加，并设置滞回避免振荡。还应合并相同检索、缓存公共上下文，并只向聚合器传结构化结论和证据引用。

本质上，并发控制不是追求“同时跑更多 Agent”，而是在模型配额、下游容量、延迟和成本约束下，让每个成功任务消耗可预测。

<a id="xiaohongshu-agent-dev-20260812-q9"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%B0%8F%E7%BA%A2%E4%B9%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1005)，来源许可：GPL-3.0。

<a id="k46165494e221"></a>

## 你怎么看当前 Agent 技术的发展？现阶段适合落地在哪些场景？

**回答：**

当前 Agent 的主线已经从“给模型接几个工具”转向 Harness 工程：围绕模型建立上下文装配、结构化工具协议、状态机、文件/浏览器/代码执行环境、权限、长任务恢复、评测和可观测性。模型的推理、代码与多模态能力在提高，但单次能力提升不会自动消除长轨迹误差累积，因此系统控制仍是核心。

现阶段最适合三类场景。第一类是高信息密度、结果可验证的数字工作，例如代码修改与测试、数据分析、知识检索、工单处理；第二类是步骤动态但工具边界清晰的流程，如售后调查、运营素材生成与审核、销售研究；第三类是人机协作任务，Agent 生成候选方案，确定性规则和人类负责高风险决策。

不适合完全自治的场景包括高风险且不可逆的资金、医疗、法律和生产控制决策，缺少可靠工具反馈的开放任务，以及成功标准无法定义的长链路。这里可以使用 Agent 辅助，但必须设置审批、预算、权限、Canary、kill switch 和回滚。

判断能否落地可以看四个条件：任务是否可分解；环境是否提供可信 Observation；结果是否可自动或低成本验证；失败是否可恢复。跨周期价值来自可测量的业务闭环，而不是 Agent 数量或演示时的自主步骤数。

<a id="pinduoduo-ai-agent-20260816-q21"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E6%8B%BC%E5%A4%9A%E5%A4%9A%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L500)，来源许可：GPL-3.0。

<a id="k227d9592875d"></a>

## 你最近在关注 Agent 领域的什么新技术？——你说你关注了 DeepSeek-Harness，你怎么理解它和 LangChain 的本质区别？Harness 解决了什么 LangChain 解决不了的问题？

**回答：**

这道题的核心不是比较两个框架的 API 数量，而是区分“应用编排抽象”和“可运行、可观测、可恢复的 Agent 执行时”。如果这里所说的 DeepSeek-Harness 是一个面向 Agent 运行时的 Harness，那么我会先基于它公开的代码和实际使用范围回答，不把未经确认的内部实现当成结论。

LangChain 更像一组构建 LLM 应用的组件和编排抽象：Prompt、模型、Retriever、Tool、Parser、Runnable、Workflow 等可以组合成调用链。它降低了把模型、检索器和工具接在一起的门槛，但应用最终仍然需要自己定义任务状态、重试、超时、权限、幂等、持久化和观测。LangGraph 等状态图抽象已经进一步补足了循环和持久化能力，但这仍属于应用编排层。

Harness 的关注点更靠近运行时控制面：它围绕一次任务维护状态机和执行循环，负责把模型输出解析为下一步动作，校验工具调用，执行受控副作用，写入事件轨迹，处理中断、超时、重试、恢复和停止条件，并为评测或训练保留完整轨迹。可以把两者的边界概括为：

$$
\text{Application Components} \xrightarrow{\text{LangChain-like orchestration}}
\text{Runnable Graph}
\xrightarrow{\text{Harness runtime}}
\text{Auditable Execution}
$$

LangChain 解决“怎样快速组装一次 LLM 应用调用”；Harness 重点解决“这次多步任务怎样在不确定、可失败、有副作用的环境中可靠运行”。例如，模型要求转账时，Harness 需要在真正执行前做 schema 校验、用户授权、金额上限、幂等键和人工确认；工具超时后需要知道该工具是否可能已经成功，不能简单重试造成重复扣款。

因此，Harness 不是天然替代 LangChain。实际系统可以用 LangChain 或其他 SDK 提供模型、检索和工具适配，再由自研 Harness 统一状态、策略、观测与恢复。Harness 也不能解决模型本身的推理能力、事实性和工具选择准确率问题，它只能把失败边界显式化、把不可靠输出限制在可验证的执行协议内。评价一个 Harness 是否有价值，应看任务完成率、错误恢复率、重复副作用率、P95/P99 延迟、单任务成本和轨迹可复现性，而不是看抽象层名字。

<a id="deepseek-agent-20260908-q2"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/DeepSeek%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L408)，来源许可：GPL-3.0。

<a id="k553bcdc30674"></a>

## 你有没有设计过Agent Skill？一个Skill从设计到上线通常需要考虑哪些因素？如何判断效果好坏？

**回答：**

如果真实项目中没有从零设计过 Skill，应该坦诚说明，并讲清自己做过的最接近工作和完整设计方案。Skill 可以理解为围绕一类任务封装的可发现、可执行、可验证能力包，通常包含元数据、触发条件、工作流指令、脚本/模板/资源以及验收规则。它不等于 Tool：Tool 暴露原子动作，Skill 组织“何时、按什么步骤、调用哪些动作、如何验收”。

从设计到上线我会关注七个方面：

1. **任务边界：** 解决什么、不解决什么，输入输出与前置条件是什么；边界过宽会让触发和评测失真。
2. **可发现性：** 名称、描述、触发样本和反例是否让路由器正确选中；详细资料采用渐进式加载，避免每轮灌入全部内容。
3. **执行契约：** 步骤、分支、停止条件、失败兜底、工具 schema、幂等性和 artifact 规范。
4. **安全权限：** 最小权限、密钥隔离、敏感数据处理、写操作确认、沙箱和审计。
5. **可维护性：** 版本、依赖、兼容范围、Owner、变更日志、弃用策略以及与其他 Skill 的组合/冲突。
6. **测试评测：** 正常、边界、歧义、恶意输入、工具异常和版本回归；上线前在隔离环境运行。
7. **发布运营：** 灰度、监控、回滚、失败样本回流和文档同步。

效果要分层判断：路由层看 Skill 触发 precision/recall 和误触发率；执行层看任务成功率、工具参数正确率、平均步骤、恢复率和副作用；效率层看 Token、延迟、成本和人工介入率；安全层看越权和敏感信息事件。还应与“无 Skill 基线”做 A/B 或离线配对回放。一个 Skill 的价值不在于文档写得多，而在于它能否稳定提高单位成本下的任务完成质量。

<a id="insta360-agent-20260809-q13"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%BD%B1%E7%9F%B3%E5%88%9B%E6%96%B0%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L259)，来源许可：GPL-3.0。

<a id="kcecbae0cf61d"></a>

## 你的 Agent 整体架构是分几层的？——每一层的职责是什么？层与层之间的接口是怎么设计的？为什么这么设计？如果换一种分层方式会有什么不同？

**回答：**

我会采用面向职责的六层结构，而不是按具体框架拆层：

1. **接入与会话层：** 负责身份认证、租户识别、流式响应、会话创建和请求取消，不决定业务动作。
2. **策略与编排层：** 维护任务状态机、预算、最大步数、超时、重试和人工接管规则，决定当前是否允许继续执行。
3. **模型决策层：** 负责意图识别、计划生成、工具选择、参数生成和最终语言表达。模型只能提出候选动作，不能绕过服务端策略直接产生副作用。
4. **知识与上下文层：** 管理短期消息、摘要、长期记忆、RAG 证据、权限过滤和 token 预算，向模型提供当前决策所需的最小充分上下文。
5. **工具与执行层：** 统一封装数据库、搜索、代码执行、企业 API 等工具，负责 schema 校验、鉴权、幂等、超时、重试、结果规范化和沙箱隔离。
6. **状态、观测与评测层：** 持久化事件、检查点、工具结果和指标，支持 trace、回放、离线评测、告警和 badcase 回流。

层间接口应该是版本化、结构化和可审计的。例如模型层返回 `ActionProposal`，执行层接收后重新校验；工具层返回包含 `status`、`data`、`error`、`retryable`、`request_id` 的 `ToolResult`；状态层以事件追加和检查点保存为主，而不是只存一段最终文本。典型动作协议可以表示为：

```json
{
  "type": "tool_call",
  "tool_name": "search_orders",
  "arguments": {"user_id": "...", "limit": 20},
  "request_id": "task-42-step-3",
  "expected_output": "order_list"
}
```

这样设计的原因是把“模型不确定性”和“系统确定性”隔开：模型可以规划，但权限、参数范围、预算和副作用由代码执行。若改成纯函数链，路径更简单、延迟更低、可测试性更好，但不适合动态任务；若改成全由一个 Agent 自由调用，开发初期灵活，生产环境却会增加越权、循环、状态丢失和故障定位成本；若所有状态都放在数据库，恢复容易但延迟和序列化成本增加，因此通常采用事件日志加关键检查点的折中。

<a id="deepseek-agent-20260908-q4"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/DeepSeek%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L454)，来源许可：GPL-3.0。

<a id="ka182f1de88ba"></a>

## 你的 Agent 评测体系是怎么搭建的？——评测集覆盖了多少场景？怎么构造的？如果评测集里 30% 的 case 答案有主观性，你怎么处理？

**回答：**

评测体系应分为数据集、执行器、指标和诊断四部分。数据集不能只收集“问答题”，而要覆盖真实任务的入口、工具、权限、长短上下文、失败依赖和风险等级。可以按场景分层：正常路径、歧义请求、知识缺失、工具错误、权限拒绝、长链路、并发、恶意提示和人工接管。

每个 case 至少包含用户目标、初始状态、允许工具、权限范围、参考事实或约束、期望终态、可接受答案集合和风险标签。数据来源包括人工编写的 golden case、线上脱敏样本、历史 badcase、程序生成的边界样本和对抗样本。训练、调参和测试集要按用户/任务/文档去重，避免同一模板泄漏造成虚高成绩。

指标要分层：

- **任务层：** 任务完成率、终态正确率、关键字段准确率、人工接管率。
- **轨迹层：** 工具选择准确率、参数正确率、无效调用率、重试恢复率、停止正确率。
- **证据层：** 检索 Recall@K、引用覆盖率、事实支持率、权限过滤错误率。
- **系统层：** P50/P95/P99 延迟、token 成本、失败率、并发吞吐和副作用次数。

主观性 case 不能强行用一个 exact match。先定义可接受答案的评分维度，例如事实正确、任务完成、覆盖要点、表达清晰、安全合规；对开放式结论建立 rubric，并用两名以上标注者独立评分，报告一致性，如 Cohen's $\kappa$ 或 Krippendorff's $\alpha$。模型评审可以做规模化筛选，但不能单独作为高风险最终标准，要用人工抽检校准评审器偏差。

还要区分“答案多样但都正确”和“没有标准答案”。前者采用集合式参考答案或事实约束，后者使用 pairwise preference、分维度评分和任务结果评估。最终报告平均分之外的置信区间、分桶结果和人工复核样本，避免 70% 客观 case 的高分掩盖 30% 主观 case 的系统性偏差。

<a id="deepseek-agent-20260908-q7"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/DeepSeek%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L530)，来源许可：GPL-3.0。

<a id="k62df01244260"></a>

## 你的agent调了哪些工具？调用工具时参数报错是怎么处理的？

**回答：**

工具清单必须来自实际项目。对于知识抽取 Agent，一个设计示例可以包含文件读取与解析、术语检索、图谱实体查询、结构校验和候选入库工具；这些是解释架构的例子，不能当作个人已经接入的事实。

每个工具定义名称、用途、输入 schema、输出 schema、错误分类和权限边界。模型产出的参数先做结构校验，例如字段是否存在、类型是否匹配、枚举和数值范围是否合法，再做业务校验，例如文档是否可访问、实体 ID 是否存在、关系类型是否被本体允许。结构化输出有助于约束格式，但不能保证参数具有正确业务含义。

参数错误应返回可操作的结构化信息，如字段路径、期望类型和允许取值，再让模型在限定次数内修复。确定性且无歧义的转换可以由代码处理，但不能静默把一个不确定的疾病名称改成另一个实体 ID。缺少关键上下文时应补查或询问，而不是猜测。

工具执行成功后还要验证返回格式、数据版本和任务目标是否满足。写操作增加授权与幂等检查，读工具也限制范围和结果规模。分别统计参数合法率、执行成功率和任务正确率，防止“参数合法”掩盖语义错误。

<a id="01ai-kg-intern-20261021-de81855b-q06"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%9B%B6%E4%B8%80%E4%B8%87%E7%89%A9%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L110)，来源许可：GPL-3.0。

<a id="k3dfd19b341cf"></a>

## 你的Agent里面运行了一个长程的任务，它假设平时只允许需要运行5分钟就能结束。然后你新运行了一次，它运行了15-20分钟，也就是说跟之前比有明显的延迟，然后你会怎么分析这个延迟是什么导致的？

**回答：**

先不要直接归因于模型变慢，而要用同一个 `trace_id` 把一次 Agent 任务拆成阶段和子调用，比较正常样本与异常样本的分布。至少记录总时长、排队时长、每次模型调用的首 Token/总耗时、输入输出 Token、工具等待、重试次数、上下文长度、并行度、节点、模型版本、Prompt 版本、RAG 召回数量和外部依赖状态。

可以按以下顺序定位：

1. **确认范围。** 判断是全部请求变慢，还是特定用户、任务类型、模型路由、地域或时间段异常。
2. **分解关键路径。** 将 15～20 分钟拆成模型生成、工具 I/O、队列等待、锁等待、数据库/向量库、网络重试、人工审批和上下文压缩等阶段。
3. **对比版本与分布。** 检查最近的模型、Prompt、工具 Schema、索引、依赖库、配置、容器发布和流量变化；同时对比输入 Token、工具调用次数和轨迹长度。
4. **识别长尾。** 查看 P50/P95/P99，而不是只看平均值；检查连接池耗尽、线程池排队、限流、GC、CPU、GPU 显存/KV Cache、网络丢包和外部服务限额。
5. **回放与最小复现。** 在脱敏沙箱中固定输入、版本和工具返回，分别关闭 RAG、工具、压缩和重试，找出造成时间增长的变量。

重点关注几类 Agent 特有原因：模型陷入重复工具调用或重规划；上下文增长导致 Prefill 和压缩变慢；工具超时后指数重试；多个任务争抢同一锁或连接池；某个外部接口尾延迟升高；并发任务触发限流；任务状态未正确推进导致循环。每个怀疑都要用 trace 和对照实验验证，不能用“LLM 不稳定”作为结论。

<a id="bytedance-agent-dev-20260903-q7"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%AD%97%E8%8A%82%E8%B7%B3%E5%8A%A8%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1169)，来源许可：GPL-3.0。

<a id="keab04ffff0dd"></a>

## 你觉得 3 年后的 Agent 开发框架会和现在有什么不同？——Harness 会变成什么形态？模型和工程的分界线在哪里？

**回答：**

三年后的框架大概率不会只是更多 Chain、Tool 和 Prompt 模板，而会向“模型原生能力 + 可组合运行时 + 领域策略”发展。具体形态可能包括：

1. **协议更标准化：** 工具、资源、任务、事件、取消、权限和结果 schema 有稳定的跨框架接口，应用不必绑定某个编排库。
2. **执行时更像操作系统：** 统一管理上下文、检查点、调度、沙箱、资源配额、凭证、日志和恢复，模型是其中一个可替换的决策组件。
3. **编排更混合：** 对固定部分使用可验证 Workflow，对不确定部分使用 Agent；计划图和运行时事件可以互相修正。
4. **评测成为一等公民：** 框架原生支持轨迹回放、仿真环境、verifier、灰度、成本预算和线上指标，而不是只提供 tracing 看板。
5. **上下文从文本升级为状态：** 结构化事实、权限、工具结果、代码图、长期记忆和证据引用共同组成模型的工作状态。

Harness 会从“包住模型调用的循环”变成任务运行时：负责资源、权限、可恢复性和证据，而模型负责在给定状态下提出预测或动作建议。分界线不是“模型写的代码还是工程师写的代码”，而是该部分能否用确定性规则、事务和测试验证。模型适合处理开放语义、候选生成、模糊分类和动态规划；工程必须掌握身份、权限、金额、状态提交、幂等、超时、审计和安全边界。

这不是把所有问题都工程化。若一个任务需要真正开放的探索，过度固定会损失能力；但任何不可逆的副作用都应由工程策略和外部验证约束。未来竞争点会从“谁能让模型调用更多工具”转向“谁能让模型在更大任务空间里以可控成本稳定完成，并且失败后可解释、可恢复”。

<a id="deepseek-agent-20260908-q14"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/DeepSeek%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L724)，来源许可：GPL-3.0。

<a id="kee91ab6031cf"></a>

## 你说有些模型不支持工具调用，那工具调用能力是怎么实现的？

**回答：**

先区分接口没有原生 tool calling 字段，与模型本身缺少可靠工具选择能力。前者可以通过结构化文本协议适配；后者即使能输出 JSON，也未必能够稳定选择工具和生成正确参数。

一种兼容方式是在提示中定义可用工具、参数 Schema 与输出协议，让模型输出 `final` 或 `tool_call` 类型的对象。若推理引擎支持 JSON Schema 或 grammar 约束，可限制结构；否则先解析，再做严格校验，有限次数纠正格式错误。不要依靠模糊正则匹配任意自然语言直接执行 Shell。

```json
{
  "type": "tool_call",
  "name": "get_job_status",
  "arguments": {"job_id": "job-123"}
}
```

运行时从白名单解析工具名，补充不可由模型伪造的身份，检查类型、取值、权限和预算，再执行工具并写回 observation。循环中的结果关联 ID 由服务端管理，不能把模型编造的“执行成功”当成真实回执。

结构约束保证可解析性，不保证语义、权限或事实正确。对于可靠性不达标的模型，可以用专门路由器、确定性工作流或支持工具调用的模型承担动作决策；不要强行把所有模型适配为同等能力。

<a id="alibaba-qwen-20260916-q19"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L2171)，来源许可：GPL-3.0。
