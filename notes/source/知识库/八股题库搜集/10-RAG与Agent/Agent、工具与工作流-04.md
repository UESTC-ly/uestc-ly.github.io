# Agent、工具与工作流

<a id="k3cb7a7a568bb"></a>

## 你读过 DeepSeek-Harness 的源码吗？——你觉得它的核心设计亮点是什么？有什么你觉得可以改进的地方？

**回答：**

这道题必须诚实区分“完整读过源码”“读过公开部分”“了解其设计思想但没有逐文件阅读”。如果没有实际阅读，就不应声称知道内部模块、性能数字或线上架构。基于公开代码能够确认的内容，应具体指向模块、调用路径和可复现实验；无法确认的部分直接标记为推测。

阅读一个 Agent Harness，我会沿着一条任务从入口到终态的路径检查：任务对象怎样创建；上下文怎样组装；模型输出怎样解析；工具怎样注册和调用；状态怎样持久化；错误怎样传播；取消和超时怎样处理；事件怎样记录；测试怎样覆盖循环和恢复。比起文件数量，我更关注三个不变量：

1. 任意工具副作用是否都经过权限、参数和幂等检查；
2. 任意一步失败后是否能恢复或明确进入失败终态；
3. 任意最终答案是否能追溯到模型决策、工具结果和证据。

如果公开实现确实把模型调用、工具执行、状态管理和事件观测放在清晰的运行时边界内，这会是核心亮点：模型不再直接驱动不可控代码，而是通过协议向 Harness 提议动作。另一个亮点可能是把 Loop 设计成可插拔组件，使不同任务可以替换规划、验证和停止策略；但具体是否如此必须以代码为证。

改进方向通常包括：严格的类型化状态和 schema 版本；工具调用的取消、幂等和副作用分类；持久化 checkpoint 与崩溃恢复；长 Observation 的结构化裁剪；多租户凭证隔离；故障注入和隐藏评测；以及对模型、Prompt、工具版本的可复现锁定。源码阅读的最终结论应落到调用链和测试证据上，而不是泛泛评价“架构先进”。

<a id="deepseek-agent-20260908-q16"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/DeepSeek%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L760)，来源许可：GPL-3.0。

<a id="k0a6429a28dd0"></a>

## 候选人：团队 Agent 目前主要负责什么垂类业务方向？

**回答：**

这是向招聘团队了解业务的问题，无法从题目确定该团队实际方向。不能把“字节”推导成必然做电商、广告或内部效率工具。

有效追问应落到任务形态：服务内部员工还是外部客户；主要做知识问答、代码开发、经营分析还是业务执行；Agent 能执行哪些真实动作；线上成功如何定义；目前最大瓶颈是模型、数据、工具、工程还是用户流程。

还可以了解岗位负责的边界：偏模型训练、Harness 与工具工程、业务集成还是评测平台，实习生能否参与完整反馈循环。团队若能清晰描述真实用户、任务指标、失败案例与迭代机制，比仅列举技术名词更能帮助判断岗位匹配度。

<a id="bytedance-agent-autumn-20260916-q28"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%AD%97%E8%8A%82%E8%B7%B3%E5%8A%A8%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1741)，来源许可：GPL-3.0。

<a id="ke1ba8f66cb22"></a>

## 全都是实习相关问题，涉及Agent就狂追问，问了问数字指标，还有业务上下游，代码框架。

**回答：**

这一条将第 3～12 题概括为连续的实习追问，没有展开十道独立问题，因此应直接回答项目深挖的组织方法，而不补造题目。可以提前把同一段实习整理成一张“可追问地图”，保证每一层都能回到真实证据。

建议准备六个层次：

1. **业务上下游：** 谁提出请求、输入数据来自哪里、Agent 输出给哪个系统、失败会影响谁、人工在哪个环节接管。
2. **系统架构：** 接入、任务状态、Context Builder、模型、RAG/Memory、工具、消息队列、数据库、缓存、评测和监控如何连接。
3. **Agent 决策：** 为什么使用 Workflow、ReAct 或 Planner-Executor；哪些步骤由模型决策，哪些规则必须由代码控制。
4. **代码边界：** 自己负责哪些包、接口、状态结构和工具；使用了哪些开源组件；为什么改造默认实现；关键异常路径如何测试。
5. **数字指标：** 数据量、并发、P95、Token、成本、任务成功率、工具正确率、恢复率以及实验置信度。每个数字都要知道计算公式和数据来源。
6. **失败案例：** 最难的 bad case、定位证据、根因、替代方案、最终结果和仍未解决的边界。

回答项目追问时采用“先结论、再机制、后证据”的三段式。例如先说瓶颈是工具结果不确定导致重复副作用，再解释超时、幂等和状态回读机制，最后给 trace、故障注入或线上指标。这样既不会想到什么说什么，也能让面试官清楚地区分团队架构、个人贡献和真实效果。

<a id="xiaohongshu-agent-dev-20260812-q4"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%B0%8F%E7%BA%A2%E4%B9%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L918)，来源许可：GPL-3.0。

<a id="k3c2a240562f1"></a>

## 分钟版本怎么展开？

3 分钟版本可以按下面的顺序：

1. 业务问题与成功标准；
2. 一次请求的完整链路；
3. 两个关键技术选择；
4. 一个最有代表性的 Badcase；
5. 结果与自己的职责边界。

不要按“Spring AI、Redis、Milvus、MCP……”的顺序报技术栈。技术栈应该出现在具体决策里，而不是单独占一段。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/interview-questions/agent-project-interview-guide.md#L108)，来源许可：Apache-2.0。

<a id="kf20ff77ff6bc"></a>

## 单Agent处理复杂长周期任务时，引入多智能体（Multi Agent）架构的核心优势有哪些？

<a id="batch4-p2-q15"></a>

**相关解释：** [Agent常见模式（ReAct/Plan and Execute等）](../15-%E5%89%8D%E7%AB%AF%E4%B8%8E%E6%B5%8F%E8%A7%88%E5%99%A8/React%E4%B8%8E%E7%BB%84%E4%BB%B6%E7%8A%B6%E6%80%81-01.md#k93a12d0c9256)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L416)，来源许可：GPL-3.0。

<a id="k505991f276cc"></a>

## 单次LLM打分评判算不算Agent？和多轮工具调用Agent核心区别在哪？

**回答：**

通常不算。单次 LLM 打分是一个模型推理组件：输入一次、输出一次，系统没有持续状态，也没有根据环境反馈自主决定下一步。把 LLM 放进流程，并不会自动把流程变成 Agent。

更严格地说，Agent 至少包含一个闭环：感知当前状态，围绕目标做决策，执行动作，读取环境观察，再更新状态并决定继续、重试、改计划还是停止。可以写成：

$$
s_t \rightarrow a_t \rightarrow o_{t+1} \rightarrow s_{t+1}
$$

单次打分只有 $x\rightarrow score$；多轮工具调用 Agent 则需要维护任务状态、选择工具、生成参数、消费工具返回、处理失败，并在预算或完成条件下终止。它面对的是动态环境，不只是静态文本映射。

但“调用很多次工具”也不是 Agent 的充分条件。如果工具顺序完全由固定代码写死，它更接近 Workflow。Agent 的关键是模型对分支和动作有一定决策权，并且这种决策受到权限、状态机、预算、重试策略和人工审批约束。

工程风险也不同。一次打分主要关注准确率、校准、时延和一致性；Agent 还要评估任务完成率、工具选择正确率、参数正确率、无效步骤数、失败恢复率、越权率和总成本。轨迹越长，单步错误越容易累积。

因此更本质的边界是：LLM Scorer 是“认知函数”，Agent 是“带状态的目标驱动控制系统”。模型是不是用了 ReAct、有没有显式输出思维链，都不是决定性标准。

<a id="alibaba-taotian-agent-20260722-q7"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L606)，来源许可：GPL-3.0。

<a id="kbefe23906816"></a>

## 原生多模态工具调用如何弥补文本式工具调用的不足？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

多模态模型的下一步是从看懂走向能执行，也就是多模态智能体。2025 年 12 月发布的 GLM-4.6V 把原生多模态工具调用作为主要特性[20]。

传统的文本式工具调用为纯文本场景设计，要么先由 MLLM 把图像转成文字描述再驱动工具，要么用纯文本 LLM 加旁挂视觉模型的级联管线。放到多模态智能体场景里，会暴露三类问题：

1. **输入侧丢信息。** 图像、截图、文档页要先转成文字描述才能进入工具调用，版式、细节和视觉证据大量丢失。

2. **输出侧看不懂视觉结果。** 工具返回的统计图表、渲染后的网页截图、检索到的商品图本身是图像，纯文本模型无法理解，难以纳入后续推理。

3. **感知和动作割裂。** 看懂和执行分属不同的模型或环节，管线复杂，误差逐级累积，形成感知和动作之间的鸿沟（perception-action gap）。

GLM-4.6V 用原生多模态工具调用（native multimodal tool calling）把感知和动作接起来，具体做法有三项：

1. **图像直接作为工具参数。** 图像、截图、文档页可以直接作为工具参数传入，不用先转成文字，信息损失少，管线也更简单[20]。

2. **看懂工具返回的图像。** 搜索结果、统计图表、渲染后的网页截图、检索到的商品图等工具返回内容，模型能直接理解，并纳入后续推理和最终输出[20]。

3. **工具调用纳入强化学习目标。** 训练时把工具调用行为放进通用的强化学习目标，提升模型在复杂工具链中的任务规划、指令遵循和格式遵循能力[20]。

GLM-4.6V 训练时上下文扩到 128K，提供 GLM-4.6V（106B 总参数，激活 12B）和 GLM-4.6V-Flash（9B）两个版本[17,20]，用同一个模型完成以图像为主的端到端智能体流程。

> **面试速答**：文本式工具调用要先把图像转成文字，丢版式和细节；工具返回的图表、截图看不懂；感知和执行分在不同模型里，误差累积。GLM-4.6V 让图像直接作为工具参数，能理解工具返回的图像并继续推理，还把工具调用纳入强化学习目标，用一个模型完成看图、调用和执行。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E5%A4%9A%E6%A8%A1%E6%80%81%E5%9F%BA%E7%A1%80%EF%BC%88%E7%B2%BE%E5%8D%8E%E7%89%88%EF%BC%89/4_AI%E5%A4%9A%E6%A8%A1%E6%80%81%E4%B8%BB%E6%B5%81%E6%A8%A1%E5%9E%8B%E6%A0%B8%E5%BF%83%E6%8A%80%E6%9C%AF%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L672)，来源许可：GPL-3.0。

<a id="k582c28478775"></a>

## 回顾一下你们整个agent的开发和设计，如果让你重新开发，你会有哪些方面的优化或者修改？

**回答：**

复盘应从已观察到的失败和维护成本出发，按影响与投入排序。可以先统一任务、会话、步骤和事件模型，明确终态、取消、重试、检查点与副作用；这样上下文压缩、断线重连和模型切换才能共享可靠状态基础。

其次建立模型与工具能力适配层：业务逻辑不绑定某个供应商的原始消息对象，工具接口版本化，鉴权与幂等放在运行时。对简单确定任务使用工作流，对开放探索任务使用受控 loop，避免所有请求都经过昂贵规划。

第三，把评测与可观测性前置。每个变更都有回归任务、真实结果校验和成本记录；历史事故进入故障注入集，长任务保留可恢复产物。第四，优化上下文和数据链路：按预算检索、按需加载工具、限制高基数指标、统一队列背压与版本管理。

推进时采用逐模块迁移与灰度，保留可用基线和回滚路径。优先修复高频失败与不可恢复状态，再优化局部 Token 或推理耗时。框架替换只有在明确减少维护成本或提升指标时才值得做。

<a id="alibaba-qwen-20260916-q32"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L2326)，来源许可：GPL-3.0。

<a id="k5797ee3d1742"></a>

## 在Agent开发过程中，上下文为什么需要进行压缩？压缩后可能导致信息缺失，应该如何解决？

**回答：**

上下文压缩不仅因为窗口有限，还因为长上下文会增加成本与延迟、稀释注意力，并让重复日志、过期状态和失败轨迹干扰当前决策。增长最快的内容往往是工具 schema、搜索结果、代码和日志，而不只是聊天轮数。

一次调用的预算可以写成：

$$
B_{\text{system}}+B_{\text{tools}}+B_{\text{state}}+
B_{\text{history}}+B_{\text{retrieval}}+B_{\text{query}}+
B_{\text{reserved output}} \le B_{\text{window}}
$$

解决信息缺失的关键不是写一个更长的摘要，而是采用“**分层状态 + 可逆引用 + 按需展开**”：

- 系统规则、权限、当前目标、硬约束和输出契约固定保留，不交给有损摘要决定；
- 最近交互和未完成步骤保留原文，已完成阶段压缩为 `goal / decisions / completed / open / artifacts / risks` 等结构化字段；
- 原始消息、工具结果和大文件保存在外部事件/对象存储中，摘要记录事件 ID 与 artifact 句柄，需要时精确回读；
- 对关键实体、数字、否定条件、截止时间和审批状态做确定性抽取与一致性校验；
- 按 Token 软水位、阶段完成、工具返回突增或目标切换触发压缩，不按固定轮数机械总结；
- 使用“增量摘要 + 周期性从原始事件重建”，避免摘要的摘要不断累积误差。

评测应构造必须依赖早期约束的长任务，比较简单截断、滑动窗口、结构化摘要和检索式压缩的任务成功率、关键信息保留率、Token、延迟与恢复能力。Rocky认为，上下文压缩的本质不是删字，而是把不可管理的对话流水升级为可恢复、可验证的任务状态。

<a id="insta360-agent-20260809-q9"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%BD%B1%E7%9F%B3%E5%88%9B%E6%96%B0%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L175)，来源许可：GPL-3.0。

<a id="k87449d9076bc"></a>

## 在Agent项目中，常见的规划（Planning）、记忆（Memory）、工具调用（Tool Use）和执行模块分别承担什么职责？

**回答：**

- **Planning：** 把用户目标、约束和可用资源拆成有依赖关系的步骤，明确每一步的输入、产物、工具和完成条件。复杂任务要把计划外置、版本化；环境变化或步骤失败时进行局部重规划，而不是每轮无条件重写全部计划。
- **Memory：** 保存当前任务状态和跨会话可复用的信息。短期记忆负责目标、计划、最近对话和工具结果的连续性；长期记忆保存经过筛选的偏好、事实、事件或经验，并带作用域、来源、置信度、时间和权限。
- **Tool Use：** 把模型意图映射为结构化工具调用，负责工具发现、Schema、参数、权限、超时、幂等和结果回传。工具不是模型的“外挂函数”，而是有副作用、有容量限制和失败语义的外部系统。
- **Execution：** 驱动状态机或 Agent Loop，执行当前可执行步骤，写入 Observation 和 checkpoint，运行验证器，并决定继续、重试、重规划、降级或人工接管。

四者不是四个必须独立部署的模型。小任务可以由一个编排器完成，长任务则应把规划和状态外置、把工具执行交给确定性运行时。面试时应说明哪些动作由模型决定、哪些规则由代码强制，以及失败后如何恢复，这比单纯背诵模块名更重要。

<a id="bilibili-ai-agent-20260818-q4"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%93%94%E5%93%A9%E5%93%94%E5%93%A9%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L70)，来源许可：GPL-3.0。

<a id="kbe43c6881b70"></a>

## 在做视频剪辑Agent项目遇到的最大挑战是什么？

**回答：**

最大挑战不是“调用模型生成脚本”，而是把一个开放式创作任务拆成稳定、可验证、可恢复的工程流程。视频剪辑 Agent 涉及文本理解、素材检索、镜头规划、时间轴对齐、字幕生成、音频处理、画面渲染和质量评估，任何一个环节出错都会让最终成片不可用。

我会把挑战拆成三层。第一层是任务结构化。用户说“帮我剪一个小红书风格的视频”，这不是一个确定指令，需要先抽取主题、目标受众、视频时长、节奏、镜头风格、口播/字幕比例、素材约束，再生成可执行的剪辑脚本。这里必须让大模型输出结构化 JSON 或 DSL，而不是自由文本。

第二层是多模态一致性。文案、镜头、字幕、配音、BGM、转场必须在时间轴上对齐。文本生成模型只懂语义，不天然理解帧率、时长、采样率、分辨率、字幕安全区，所以需要工程规则和媒体处理工具做约束。

第三层是稳定性与可恢复。Agent 链路长，模型调用、素材下载、转码、ASR/TTS、渲染都可能失败。我的做法是把流程拆成可重试节点，每个节点有输入输出 schema、超时、重试、降级和日志 trace。真正的挑战是把创意工作流变成“非确定性生成 + 确定性校验 + 可回滚执行”的系统。

<a id="xiaohongshu-ai-fullstack-20260702-q5"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%B0%8F%E7%BA%A2%E4%B9%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L155)，来源许可：GPL-3.0。

<a id="k374c9dccdf7f"></a>

## 基于 LangChain 开发 Agent 时，如果工具调用连续失败，如何设计一套不会失控的容错机制？

**回答：**

把容错分为工具适配层、编排层和业务提交层。LangChain 可以组织模型和工具调用，LangGraph 一类状态编排可以提供检查点与恢复能力，但框架本身不自动保证业务幂等、总预算或外部事务一致性。

**工具适配层**设置连接超时、读取超时和每次调用 deadline，返回结构化错误码。对网络抖动、限流或暂时不可用，按操作是否可重试进行退避；对参数错误，交给模型有限次数修正；对权限拒绝，不让模型通过变换参数绕过策略。404 是否可以重试要结合数据最终一致性等业务契约，不能只看 HTTP 码。

**编排层**保存任务状态、证据、预算与在途调用。重试由一层统筹，避免 SDK 重试、工具重试和 Agent 重规划相乘。比如三层各最多尝试三次，极端情况下会放大到 27 次下游请求。按依赖设置熔断与并发隔离，预算超限进入明确终止或人工接管状态。LangGraph 的递归／步数限制是兜底，不是主要业务停止条件。

**业务提交层**处理副作用：同一业务动作在重试和恢复中使用同一个幂等键，参数变化视为新动作并重新授权。请求发送后超时，先查询操作状态；幂等记录与业务更新应在服务端原子完成。仅在本地写入“已执行”后再调用远端，会产生漏执行；远端成功后才写本地状态，又会出现重复窗口。

可以把决策规则明确为：

```text
cancelled or budget exhausted -> terminate
write outcome unknown        -> reconcile by idempotency key
permission denied            -> fail or await valid authorization
invalid arguments            -> bounded repair + validation
safe transient failure       -> bounded retry with backoff
repeated invalid trajectory  -> bounded replan or escalate
verified postcondition       -> finish
```

检查点记录了图执行进度，并不等于外部系统执行了“恰好一次”。恢复时必须核对副作用。在实现中使用与锁定版本相符的工具包装器、middleware 或图节点重试策略，避免把旧教程里的 API 名称当作跨版本通用接口。验收用故障注入覆盖请求前失败、执行后回包丢失、限流、进程重启与预算耗尽，同时检查请求放大率和重复写入数。

<a id="baidu-agent-20260922-r3-q3"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%99%BE%E5%BA%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1197)，来源许可：GPL-3.0。

<a id="k0dc348a59373"></a>

## 多 Agent / A2A Harness 应该如何设计？

多 Agent Harness 要评估的不只是单个 Agent 能力，还包括任务分配、handoff、协作协议、冲突处理和最终一致性。

需要记录：

- 哪个 Agent 接收任务。
- 是否选择了正确协作者。
- handoff message 是否包含足够上下文。
- remote Agent 返回的 artifact 是否被正确使用。
- 多 Agent 是否重复工作或互相覆盖。
- 失败时是否回退到单 Agent 或人审。
- A2A 调用链是否可追踪。

评测任务：

- 研究 Agent 调用数据分析 Agent。
- 编码 Agent 调用代码审查 Agent。
- 客服 Agent 调用退款审批 Agent。
- 办公 Agent 调用日程、邮件、知识库多个 Agent。

判分维度：

- 最终任务完成率。
- handoff 成功率。
- 上下文丢失率。
- artifact 可用性。
- 冲突解决能力。
- 调用成本。
- 责任边界是否清晰。

多 Agent Harness 最容易漏掉的是“协作成本”。如果多个 Agent 带来大量重复搜索、互相等待和状态不一致，即使最终成功，也可能不适合生产。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/08_Agent_Harness_Engineering%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L543)，来源许可：GPL-3.0。

<a id="kd5df390031b3"></a>

## 多 Agent 协作可以采用哪些控制结构？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

多 Agent 编排的目标是让多个具有不同角色、工具、记忆或权限的 Agent 协同完成任务。常见模式包括：

- Supervisor：一个上级 Agent 分配任务和汇总结果。
- Router：根据输入类型选择最合适的 Agent。
- Swarm：多个 Agent 自组织协作或交接。
- Debate：多个 Agent 生成不同观点，再由 judge 决策。
- Crew / Team：角色固定的团队协作。
- Pipeline：多个 Agent 按固定顺序处理任务。
- Blackboard：多个 Agent 读写共享工作区。
- Market / Bidding：Agent 根据能力声明竞争任务。

实际工程里，最常见的是 Supervisor、Router、Pipeline 和 Team，因为它们可控、可观测、容易落地。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/03_Agent%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81%E7%BC%96%E6%8E%92%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L502)，来源许可：GPL-3.0。

<a id="kbd32361ec093"></a>

## 多 Agent 协作是怎么实现的？——通信模式是什么？如果子 Agent 返回的结果是自然语言（而不是结构化数据），主 Agent 怎么解析？怎么保证解析不出错？

**回答：**

多 Agent 协作首先要定义角色和边界，而不是简单复制多个模型。常见通信模式包括：

- **编排器-工作者：** 主 Agent 拆分任务，子 Agent 返回结果，适合有明确依赖的任务。
- **黑板模式：** 子 Agent 把中间结果写入共享任务空间，其他 Agent 订阅或读取，适合并行研究。
- **流水线模式：** 一个 Agent 的结构化输出作为下一个 Agent 的输入，适合固定阶段。
- **评审模式：** 生成 Agent 与验证 Agent 分离，适合高风险结论，但要防止评审也只是重复生成。

我更倾向于让通信协议以结构化消息为主，至少包含 `task_id`、`agent_id`、`schema_version`、`status`、`result`、`evidence`、`confidence`、`errors` 和 `side_effects`。主 Agent 不应直接相信自然语言结果，而应做以下降级处理：

1. 优先要求子 Agent 按 JSON Schema 输出，并在接收端使用严格解析器校验类型、必填字段、枚举和长度；
2. 对 Markdown、代码块或带解释的 JSON 做受限提取，但把它视为兼容层，不把正则表达式当成可靠协议；
3. 解析失败时返回可定位的校验错误，允许子 Agent 只修复格式，不重新生成整个事实结论；
4. 对关键字段做确定性校验，例如 ID 是否存在、数值是否越界、证据引用是否可回查；
5. 对有副作用的结果采用两阶段提交或人工确认，解析成功不等于允许执行。

自然语言不可避免时，可以通过“语义解析器 -> schema 校验 -> 事实验证 -> 置信度门控”转成内部对象；无法验证的字段应标记为 `unknown`，不能默认为空字符串或模型猜测。这样保证的是协议和风险边界，而不是保证模型永远不出错。多 Agent 还要处理消息重复、乱序、超时、版本冲突和权限隔离，最好用任务 ID、消息 ID、状态版本和幂等键贯穿全链路。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/DeepSeek%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L506)，来源许可：GPL-3.0。

<a id="kca70017e7074"></a>

## 多 Agent 导购系统架构（Supervisor/Worker 角色、各 Agent 模型、通信机制）

**回答：**

Supervisor 负责意图解析、任务拆分、预算和最终合并；Worker 按领域承担商品检索、库存、价格、优惠、配送和售后等职责。通信消息应带 `trace_id/task_id/attempt/schema_version`、权限和 Deadline，长任务用可靠队列和持久化状态，不能只依赖易丢消息的 Pub/Sub。

结果合并优先使用确定性规则和业务状态校验：价格、库存、优惠由工具回执决定，模型只负责解释；冲突时保留证据和版本，必要时转人工。评估要覆盖正常、缺货、价格变化、工具超时、恶意商品描述和多 Agent 重复操作。

<a id="tencent-llm-collection-20260903-q49"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E8%85%BE%E8%AE%AF%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L843)，来源许可：GPL-3.0。

<a id="k2806b70ad913"></a>

## 多 Agent 并发有什么性能问题？

**回答：**

多 Agent 并发不是简单把多个协程一起启动。它会同时放大模型、工具、状态和协调四类瓶颈。

1. **模型网关瓶颈。** Fan-out 会快速消耗 RPM/TPM，并触发 429；每个子 Agent 重复携带系统 Prompt、工具 schema 和公共上下文，Token 与费用近似随分支数增长。
2. **尾延迟放大。** 汇总节点通常等待最慢分支。并发分支越多，出现一个慢模型、慢工具或重试的概率越高，最终 P95/P99 可能反而上升。
3. **下游资源争用。** 浏览器、数据库连接池、Redis、向量库、文件句柄和第三方 API 都有容量上限；上游无限并发只会把等待转移到下游队列。
4. **共享状态竞争。** 多个 Agent 同时修改计划、Memory、文件或业务记录会产生丢失更新、重复副作用和顺序不一致，需要版本、锁、幂等与单写者策略。
5. **重复探索和上下文膨胀。** 子 Agent 可能检索同一资料、调用同一工具；汇总全部轨迹会挤占上下文并增加信息冲突。
6. **协调故障。** 可能出现互相等待、循环交接、部分成功、取消传播失败，以及 Supervisor 成为串行瓶颈。

因此要比较的不是单 Agent 与多 Agent 的“智能感”，而是单位成功任务成本、临界路径延迟、工具负载、重复工作率和最终质量。任务不可并行、共享状态强耦合或结果聚合困难时，多 Agent 往往比单 Agent + 工具更差。

<a id="xiaohongshu-agent-dev-20260812-q8"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%B0%8F%E7%BA%A2%E4%B9%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L989)，来源许可：GPL-3.0。

<a id="k3458b5313467"></a>

## 多 Agent 系统如何做到 workspace、auth、session 隔离？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

多 Agent 系统中，“一个 Agent”不只是一个 prompt，而是一组隔离资源：

- persona / system prompt。
- workspace / cwd。
- agent directory / state。
- session store。
- memory store。
- auth profile。
- tool policy。
- sandbox policy。
- channel binding。

推荐设计：

1. **Workspace 隔离**

   不同 Agent 默认使用不同工作区。即使共享同一仓库，也要明确只读/读写边界和文件所有权。

2. **Auth 隔离**

   不同 Agent 使用不同 token、cookie、MCP credential、云账号或最小权限角色。不要让客服 Agent 复用工程 Agent 的代码仓库权限。

3. **Session 隔离**

   每个 Agent 维护独立会话历史和压缩摘要，避免人格、任务和上下文混杂。

4. **Tool Policy 隔离**

   不同 Agent 可用工具不同。例如代码 Agent 可以读写仓库，客服 Agent 只能查知识库和创建工单。

5. **Memory 隔离**

   长期记忆默认分域保存。跨 Agent 检索必须做权限过滤、脱敏和来源标注。

6. **Channel Binding**

   将特定 channel、account、peer 绑定到特定 Agent，并支持最具体规则优先。

一个常见误区是只给不同 Agent 换 system prompt，却复用同一工作目录、会话存储和凭证。这样看起来是多 Agent，实际上只是多个名字共用同一个安全边界。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/02_%E7%BC%96%E7%A0%81Agent%E4%B8%8EAgentOS%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L970)，来源许可：GPL-3.0。

<a id="kd2570c3b418d"></a>

## 多 Agent 系统的评测方案，如何验证功能正确性和反幻觉能力

**回答：**

<a id="tencent-llm-collection-20260903-q50"></a>

**相关解释：** [介绍最终各个指标](../09-%E5%A4%A7%E6%A8%A1%E5%9E%8B%E8%AE%AD%E7%BB%83%E4%B8%8E%E6%8E%A8%E7%90%86/%E6%A8%A1%E5%9E%8B%E5%BA%94%E7%94%A8%E4%B8%8E%E5%B7%A5%E7%A8%8B%E5%AE%9E%E8%B7%B5-05.md#ke63b7edb3e39)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E8%85%BE%E8%AE%AF%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L852)，来源许可：GPL-3.0。

<a id="k99a3ce542707"></a>

## 多Agent之间通信方式是什么？如何做任务分发和结果合并？

**面试官：** 多Agent之间怎么通信？如何做任务分发和结果合并？

**回答：**

多 Agent 通信首先要选择协作拓扑，而不是先选择 Redis 还是 gRPC。常见结构包括 Supervisor-Worker、Planner-Executor、黑板系统、事件驱动协作和点对点会话。生产中通常优先采用中心编排或共享任务状态，因为它更容易控制权限、预算、重试和审计。

通信方式可按可靠性需求选择：

- 同进程低延迟协作：内存队列、Channel、`asyncio.Queue`，但进程退出后状态会丢失。
- 同集群同步调用：gRPC/HTTP，适合短请求和明确响应，不适合把长任务可靠性全部压在连接上。
- 异步可靠任务：Kafka、RabbitMQ、Redis Streams 或云消息队列，支持确认、重试、消费组和死信。Redis Pub/Sub 不保存消息，消费者离线时会丢失，不能直接作为关键任务总线。
- 长周期工作流：使用持久化工作流引擎或事件溯源状态机，支持 Checkpoint、补偿和恢复。

任务分发时，Planner 应输出结构化任务：`task_id`、父任务、依赖、输入 Artifact、能力标签、优先级、Deadline、预算、权限和验收条件。Router 根据 Agent 能力、负载、数据位置、风险等级和历史质量调度。Worker 通过租约领取任务，使用幂等键执行，并通过 Heartbeat 防止任务永久卡死；租约到期后可以重派，但必须用 Fencing Token 防止旧 Worker 迟到写入。

结果合并不能只依赖“多数投票”。多个 Agent 可能共享同一模型和同一错误，因此错误高度相关。更可靠的方法是按任务类型选择 Verifier：代码用测试和静态分析，检索用证据覆盖与引用，计算用程序复算，业务操作用环境状态和事务回执。对可拼接结果按 Schema 合并；对互斥结论保留证据、置信度和冲突原因，再由独立 Judge 或人工决策。

所有消息应至少带有 `trace_id`、`task_id`、`attempt`、`schema_version`、`producer`、时间、幂等键和 Artifact 引用，并限制 Agent 只能访问完成任务所需的工具与数据。

**多 Agent 系统的价值不在于“Agent 数量更多”，而在于能否把任务分解、隔离执行、可靠传递和可验证合并做成一条闭环。**

<a id="alibaba-cloud-agent-algo-20260901-q11"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1508)，来源许可：GPL-3.0。

<a id="ka840d342d24b"></a>

## 多个Agent同时修改同一个文件，如何避免冲突？

**面试官：** 多个Agent同时修改同一个文件，如何避免冲突？

**回答：**

最优先的原则不是“给同一个文件加一把更大的锁”，而是尽量减少共享可变状态。可以先按模块、目录、函数或任务所有权拆分，让多个 Agent 在独立 Workspace、分支或 Git Worktree 中工作，最后通过 Patch 合并。只有确实需要修改同一逻辑区域时，才进入冲突控制。

一种可靠的工程链路是：

1. 每个 Agent 从同一个基线提交或文件哈希开始，在隔离工作区产生结构化 Patch。
2. 提交前执行 Compare-And-Swap：确认目标文件当前哈希仍等于读取时的基线哈希。
3. 若基线未变化，原子应用 Patch；若已变化，使用三方合并，即 Base、Current、Agent Result，而不是覆盖写入。
4. 只在“检查版本 + 应用 Patch + 更新版本”的短临界区加锁，避免把模型思考和工具执行时间放进锁内。
5. 合并后运行解析器、格式化、类型检查、测试和领域不变量校验。文本无冲突不代表语义无冲突。

乐观并发控制适合冲突概率低、Agent 任务较长的场景；悲观锁适合短事务和高冲突热点，但必须设置租约、持有者 Token、超时和 Fencing Token，避免锁过期后旧持有者继续写入。仅使用 Redis `SET NX PX` 而没有 Fencing，无法完全防止暂停进程恢复后的陈旧写。

对于代码仓库，Git 的 Patch 和三方合并通常优于直接共享文件锁；对于结构化文档，可以按 AST、JSON Patch 或数据库行级版本合并。所谓“让 LLM 仲裁冲突”只能作为生成候选合并结果，最终仍要由确定性校验和测试验证。

还要处理原子落盘：先写临时文件、`fsync`，再原子重命名，避免进程崩溃留下半个文件。写操作应带 `operation_id`，重试时保持幂等。

**多 Agent 协同的关键是隔离、版本、Patch、短临界区和验证闭环；锁只是其中一个工具，不能替代语义合并。**

<a id="alibaba-cloud-agent-algo-20260901-q9"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1459)，来源许可：GPL-3.0。

<a id="kcce78385b484"></a>

## 多个子 Agent 如何分工、分发任务和合并全局状态？为什么没有采用去中心化协作？

**回答：**

可以采用中心编排器维护权威任务图和全局状态。Planner 把目标拆成带输入、输出 schema、依赖、预算和权限的子任务；Router 根据能力注册表、工具、负载和历史质量选择子 Agent；无依赖任务并发执行，有依赖任务由 DAG/状态机调度。每个子 Agent 只接收完成任务所需的最小上下文。

子 Agent 返回结构化结果、证据、置信度、版本和副作用记录，而不是任意自然语言。Reducer 根据任务 ID 和状态版本合并：集合结果去重，数值按业务规则聚合，事实保留来源，冲突进入仲裁。共享状态使用单写者、乐观锁或事件溯源，避免多个 Agent 静默覆盖。

没有采用去中心化协作，通常因为任务需要统一权限、预算、停止条件、审计和最终输出。点对点自治会引入消息风暴、重复劳动、环路、状态分叉与难以复现的问题；对于一个组织内的受控业务系统，中心编排更容易保证不变量和故障恢复。

中心化不等于单点。编排服务可以多副本部署，状态持久化，任务按键分区，Worker 横向扩展。只有当参与方跨组织自治、中心信任不可接受或网络长期分区时，才值得承担去中心化协议的成本。

<a id="pinduoduo-ai-agent-20260816-q31"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E6%8B%BC%E5%A4%9A%E5%A4%9A%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L647)，来源许可：GPL-3.0。

<a id="k7b8be9550a78"></a>

## 多任务共享为什么会产生负迁移，如何定位和缓解？

**难度评分：⭐⭐⭐⭐⭐ (5/5)  |  考察频率：⭐⭐⭐⭐⭐ (5/5)**

负迁移是指引入其他任务后，目标任务的验证表现反而低于单任务训练或原有基线。它不只来自梯度方向冲突，也可能来自采样比例、损失尺度、共享容量和训练阶段切换。

**先区分四类来源。** 生成希望保留多样性，编辑强调输入保持，理解追求语义判别，目标本身可能拉动共享参数朝不同方向更新。高频或高损失任务还会主导优化；长视频任务占用更多 token 和显存时，按 batch 计数相同也不代表训练贡献相同。共享层容量不足、归一化统计不兼容，以及后期只微调一个任务，也会造成容量竞争或任务遗忘。

**定位要从分任务曲线开始。** 固定评测集和推理配置，分别对照单任务模型、共享前的 checkpoint 与联合训练版本。同步记录各任务的采样量、有效 token 数、损失尺度和共享层梯度范数；必要时查看梯度余弦相似度，判断是持续冲突，还是某个任务仅因更新量过大而占优。随后依次做任务配比、共享深度和任务分支消融，避免一次更改多个因素。

**修复手段要对应原因。** 数据或更新量失衡时调整任务采样和损失归一化；梯度持续冲突时可尝试 GradNorm、PCGrad 等权重或梯度处理方法；共享容量不足时增加任务专用适配器、归一化层或稀疏专家；阶段微调造成遗忘时保留任务回放与全任务回归。若隔离后仍无正迁移，继续强行共享通常没有收益，应减少共享层或改为任务路由。

> **面试速答**：负迁移可能来自目标和梯度冲突，也可能只是任务采样、损失尺度、token 数或共享容量失衡。排查时先固定评测协议，对照单任务与联合训练结果，再看分任务曲线、更新量、梯度范数和共享深度消融。修复应与原因对应：调采样和损失、处理冲突梯度、增加任务专用路径或减少共享，并用全任务回归确认没有把问题转移到其他能力。

参考资料：[GradNorm](https://arxiv.org/abs/1711.02257)、[Gradient Surgery for Multi-Task Learning（PCGrad）](https://arxiv.org/abs/2001.06782)、[Multi-Task Learning as Multi-Objective Optimization](https://arxiv.org/abs/1810.04650)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E8%A7%86%E9%A2%91%E5%9F%BA%E7%A1%80%EF%BC%88%E7%B2%BE%E5%8D%8E%E7%89%88%EF%BC%89/06_AI%E8%A7%86%E9%A2%91%E7%BB%9F%E4%B8%80%E7%B3%BB%E7%BB%9F%E3%80%81%E5%88%9B%E4%BD%9C%E5%B7%A5%E4%BD%9C%E6%B5%81%E4%B8%8E%E6%9C%AA%E6%9D%A5%E8%B6%8B%E5%8A%BF.md#L156)，来源许可：GPL-3.0。

<a id="k50653773e002"></a>

## 多平台 Agent Gateway 的核心价值是什么？

多平台 Agent Gateway 是把不同用户入口统一接入同一个 Agent Runtime 的控制平面。它让 Agent 不只活在终端或网页里，而能从 CLI、TUI、Telegram、Discord、Slack、邮件、Webhook、智能家居、会议工具等多个入口接收任务、发送结果、请求审批和恢复会话。

典型架构：

$$
\text{CLI / TUI / IM / Email / Webhook}
\rightarrow \text{Gateway}
\rightarrow \text{Session Router}
\rightarrow \text{Agent Runtime}
\rightarrow \text{Tools / Memory / Skills}
$$

核心价值：

- 多端入口统一。
- 会话连续性。
- 平台权限隔离。
- 消息格式适配。
- 媒体和文件处理。
- 工具进度推送。
- 权限审批回调。
- cron / background task 通知。
- 统一日志、审计和可观测性。

Hermes Agent 的多平台 Gateway 启发是：长期运行 Agent 的“用户界面”不应该绑定在一个终端窗口，而应通过统一 Gateway 在不同平台保持同一个智能体工作流。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/09_%E8%87%AA%E8%BF%9B%E5%8C%96Agent%E4%B8%8E%E5%A4%9A%E5%B9%B3%E5%8F%B0%E8%BF%90%E8%A1%8C%E6%97%B6%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L145)，来源许可：GPL-3.0。

<a id="kb1c04e215bbe"></a>

## 多平台 Agent 的可观测性和本地行为画像如何设计？

多平台 Agent 的可观测性要同时服务 debug、安全审计、成本治理和用户体验优化。

建议记录：

- session / user / platform / channel / workspace。
- 模型和 provider。
- slash command。
- 工具调用和结果。
- Skill 加载和使用。
- Memory 读写。
- Context compression。
- 任务状态和后台事件。
- 权限审批。
- 成本、token、延迟。
- 错误和重试。
- 插件触发事件。

本地行为画像可以用于：

- 展示用户 Agent 使用情况。
- 发现高价值技能。
- 识别低效工具链。
- 生成成就或使用洞察。
- 辅助 Curator 判断 Skill 生命周期。
- 构造个人化推荐。

注意：

- 行为画像必须本地优先或租户隔离。
- 敏感内容脱敏。
- 用户可关闭、导出、删除。
- 不应把娱乐化指标凌驾于安全和隐私之上。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/09_%E8%87%AA%E8%BF%9B%E5%8C%96Agent%E4%B8%8E%E5%A4%9A%E5%B9%B3%E5%8F%B0%E8%BF%90%E8%A1%8C%E6%97%B6%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L564)，来源许可：GPL-3.0。

<a id="kbb6a2f3f9751"></a>

## 多条件控制发生冲突时，统一系统应该如何处理？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐⭐ (5/5)**

多条件控制不能简单做特征相加或统一调高引导强度（guidance）。冲突可能发生在语义、空间、时间和约束强度四个层面，处理顺序应从输入约束开始，再进入模型融合和采样调度。

1. **先统一坐标并识别硬冲突。** 把 mask、轨迹、首尾帧和音频事件转换到同一分辨率、帧率与时间轴，检查是否存在无法同时满足的要求。例如两个条件修改同一区域却要求不同结果，属于显式冲突；参考图只有正脸而文本要求转身，更接近信息不足和外推风险，不能直接归为逻辑矛盾。
2. **明确硬约束和软偏好。** 非编辑区域保持、指定首尾帧或安全规则通常需要更高优先级；风格、构图和运动幅度可以作为软约束。优先级应来自任务协议或用户选择，不能把 identity、pose、text 等模态预先排成一张固定顺序表。
3. **按空间和时间隔离作用域。** 不同条件尽量控制不同区域、帧段或网络层。作用域重叠时再使用门控、条件权重或分阶段生成，减少多个条件同时争夺同一批 token。
4. **训练和推理分别处理。** 训练阶段需要覆盖常见条件组合、随机缺失和不同强度；推理阶段可以调节引导强度、门控或时间调度。条件 dropout 能提高缺失条件下的鲁棒性，却不会自动教会模型解决语义矛盾。
5. **无法可靠裁决时交给用户确认。** 对高影响且互斥的要求，直接让用户确认优先级通常比模型自行猜测更稳妥。自动降权适合低风险偏好，不适合悄悄改写明确指令。

验证时既要看每个条件单独的遵循度，也要看联合成功率和非目标区域保持。可以固定随机种子，依次移除或替换某个条件，观察结果是否只在预期作用域内变化；再按条件组合建立失败矩阵，定位是某条条件路径失效，还是两条路径同时存在时发生竞争。

> **面试速答**：多条件冲突先在输入层解决：统一坐标和时间轴，区分真正互斥、信息不足与强度失衡；随后明确硬约束和软偏好，再按空间、时间和网络层隔离作用域。模型侧可以用门控、引导强度和分阶段生成，但高影响冲突应让用户确认。评估时逐个移除条件并检查变化范围，不能只看最终视频的整体观感。

参考资料：[VideoComposer](https://arxiv.org/abs/2306.02018)、[VACE](https://arxiv.org/abs/2503.07598)、[Classifier-Free Diffusion Guidance](https://arxiv.org/abs/2207.12598)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E8%A7%86%E9%A2%91%E5%9F%BA%E7%A1%80%EF%BC%88%E7%B2%BE%E5%8D%8E%E7%89%88%EF%BC%89/06_AI%E8%A7%86%E9%A2%91%E7%BB%9F%E4%B8%80%E7%B3%BB%E7%BB%9F%E3%80%81%E5%88%9B%E4%BD%9C%E5%B7%A5%E4%BD%9C%E6%B5%81%E4%B8%8E%E6%9C%AA%E6%9D%A5%E8%B6%8B%E5%8A%BF.md#L225)，来源许可：GPL-3.0。

<a id="k00a5e70c0d24"></a>

## 多租户平台应怎样建立身份与资源边界？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

企业平台必须支持多租户、多部门、多角色和多数据域。Agent 的权限治理比普通应用更复杂，因为 Agent 既代表用户行动，又有自己的工具、记忆、策略和运行环境。

关键治理对象：

- 用户。
- 租户。
- 部门。
- Agent。
- 工具。
- 数据源。
- 知识库。
- 记忆。
- 会话。
- 工作流。
- 模型。
- 外部系统凭证。

权限判断不应只问“用户有没有权限”，还要问：

- 当前 Agent 有没有权限？
- 当前任务有没有权限？
- 当前工具有没有权限？
- 当前参数是否越界？
- 当前环境是否允许？
- 是否需要审批？

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/07_%E4%BC%81%E4%B8%9A%E7%BA%A7Agent%E5%B9%B3%E5%8F%B0%E4%B8%8E%E4%BA%A7%E5%93%81%E8%90%BD%E5%9C%B0%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L336)，来源许可：GPL-3.0。

<a id="kbfbe8152a422"></a>

## 多通道 Agent 如何做会话路由和用户隔离？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

多通道 Agent 会同时面对私聊、群聊、工作区、Webhook、定时任务、IDE、CLI 等来源。核心问题是：同一条消息应该进入哪个 session，以及哪些上下文绝不能互相看到。

常见路由维度：

- channel：Slack、Discord、Telegram、Web、CLI、IDE、Email。
- account：同一平台上的不同账号或 workspace。
- peer：私聊对象、群、频道、组织。
- agent：不同人格、职责或工作区的 Agent。
- source type：用户消息、系统事件、cron、webhook、后台任务回调。

常见 session scope：

| Scope | 适用场景 | 风险 |
| --- | --- | --- |
| main session | 单用户本地 Agent | 简单但不适合多人 |
| per-peer session | 每个私聊对象独立上下文 | 能避免用户间上下文泄露 |
| per-channel-peer session | 同一平台不同群/频道隔离 | 适合团队协作 |
| per-account-channel-peer session | 多账号、多组织、多平台 | 最安全但管理复杂 |

关键原则：

- 私聊默认必须隔离，不能让 Alice 的上下文出现在 Bob 的会话中。
- 群聊与私聊应分离，群聊中的上下文不能自动进入私人会话。
- 自动任务和 webhook 应有独立上下文或明确绑定上下文。
- 路由规则要可解释，冲突时采用“最具体规则优先”。
- session reset、daily reset、idle reset、manual reset 要有明确策略。
- transcript、memory、tool trace 要跟 session id 强绑定。

面试回答时可以强调：多通道 Agent 的安全事故往往不是模型能力不足，而是会话边界设计错误导致上下文串线。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/02_%E7%BC%96%E7%A0%81Agent%E4%B8%8EAgentOS%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L932)，来源许可：GPL-3.0。

<a id="k498f62c9e095"></a>

## 大模型如何获得 Function Calling 能力？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

Function Calling 能力通常来自多阶段训练和产品工程配合：

1. **预训练**

   模型学习大量代码、JSON、API 文档和自然语言结构，为格式化输出打基础。

2. **监督微调**

   使用带工具描述、用户请求、函数选择、参数生成的样本，让模型学会根据语义选择工具。

3. **偏好优化**

   通过人类或自动评估反馈，让模型更倾向于正确工具、正确参数和合适的拒绝。

4. **工具调用运行时**

   模型 API 或 Agent Runtime 提供 tool schema、tool choice、parallel tool calls、structured output、retry 等工程能力。

5. **在线评测与纠错**

   用真实日志评估工具选择准确率、参数正确率、调用成功率和安全违规率。

训练数据通常包含：

- 用户自然语言请求。
- 可用工具列表。
- 工具描述和参数 Schema。
- 正确工具选择。
- 正确参数 JSON。
- 工具返回结果。
- 最终自然语言回答。
- 不应调用工具的负样本。

面试中可以说：Function Calling 不是“模型天生会调用工具”，而是模型能力、结构化输出训练、API 运行时和工具治理共同形成的结果。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/04_MCP%E4%B8%8EA2A%E5%8D%8F%E8%AE%AE%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L225)，来源许可：GPL-3.0。

<a id="kfa545507153e"></a>

## 如何判断一个图片理解 Agent 的评测指标是否足够完整？

**回答：**

先明确任务是图片问答、OCR、定位、审核还是编辑，再建立“感知 → 推理与工具 → 最终任务 → 成本与风险”的分层指标。分类准确率只能描述其中一小部分能力，不能代表整个 Agent 的可用性。

| 层次 | 指标示例 | 容易漏掉的问题 |
| --- | --- | --- |
| 感知识别 | OCR 字符错误率、检测 AP、区域 IoU | 小字、旋转、低清、跨语言与遮挡 |
| 回答与证据 | 任务正确率、事实支持率、对象幻觉率 | 看不清仍肯定回答、证据与结论错配 |
| 工具轨迹 | 工具选择、参数正确率、恢复成功率 | 反复调用、坐标转换错误、执行越界 |
| 编辑约束 | 目标编辑成功、区域外差异、文字识别结果 | 非目标对象变形、文字残留、多轮漂移 |
| 审核决策 | 分类别 precision/recall、误放与误拦率 | 低频高风险类别被总体准确率掩盖 |
| 线上运行 | p95/p99 延迟、失败率、人工接管、成功任务成本 | 队列等待、超大图和并发显存不足 |

例如高风险内容只占 1%，一个全部判正常的系统也能达到 99% 准确率，却没有审核价值。需按类别、尺寸、语言、来源设备和困难样本切片，报告置信区间，并检查高风险类别的漏检。

图片编辑中的像素一致性、感知相似度和语义约束分别回答不同问题：PSNR/SSIM 高不代表没有改错关键文字，语义相似也不保证区域外像素未变。对于严格局部编辑，区域外应做直接差异检查；对于重新编码的输出，还要把编码误差与模型改动分开。

人工或模型评审应有明确 rubric、盲评和冲突复核。模型裁判可以扩展覆盖面，但要用人工标注评估偏差；相同图像或同源近重复不能跨训练集和测试集泄漏。**完整性意味着覆盖真实失败模式，并将指标与业务损失关联，而不是把指标列表写得很长。**

<a id="baidu-agent-20260922-r2-q10"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%99%BE%E5%BA%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1108)，来源许可：GPL-3.0。

<a id="keada3668c63e"></a>

## 如何回答“请设计一个企业级 Agent Harness 平台”？

可以按八层架构回答：

1. **Dataset 层**

   管理任务集、风险标签、数据版本、脱敏样本、历史失败样本。

2. **Environment 层**

   提供 Docker / VM / 浏览器 / 数据库 / API mock / 用户模拟器 / 多 Agent 网络。

3. **Runner 层**

   批量运行 Agent，固定版本组合，支持并发、重试、timeout、取消和清理。

4. **Trace 层**

   采集模型调用、工具调用、状态变化、权限审批、成本和 artifact。

5. **Grading 层**

   支持规则判分、测试判分、状态比较、LLM-as-Judge、人审和组合评分。

6. **Report 层**

   展示通过率、失败分类、版本对比、成本、延迟、风险和趋势。

7. **Gate 层**

   接入 CI/CD、Prompt 发布、Tool 发布、模型切换、策略变更和灰度门禁。

8. **Feedback 层**

   将线上失败、人工反馈、事故复盘自动转成新 eval case。

关键设计原则：

- 任务和环境必须版本化。
- 能确定性判分就不要依赖 LLM-as-Judge。
- 每次运行必须有 trace 和 artifact。
- 安全集必须独立于普通功能集。
- 评测要覆盖多次运行稳定性，而不只看 pass@1。
- Harness 不能拥有生产高危权限，只能 dry-run 或在沙箱执行。
- 报告必须能告诉团队“该修模型、工具、上下文、策略还是产品流程”。

**高分总结：**

企业级 Agent Harness 平台的核心不是做排行榜，而是做持续质量门禁。它把 Agent 的每一次变更都变成可复现、可比较、可审计的实验。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/08_Agent_Harness_Engineering%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L727)，来源许可：GPL-3.0。

<a id="k34f241f7733e"></a>

## 如何回答“请设计一个企业级 Agent 协议平台”？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

注意这里设计的是“协议平台”，不是完整 Agent 平台。回答重点应落在 MCP/A2A 接入、能力发现、认证授权、调用链审计和协议兼容；完整平台架构题见 [07_企业级Agent平台与产品落地高频考点.md](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/07_企业级Agent平台与产品落地高频考点.md)。

可以按六层回答：

1. **接入层**

   支持 Web、IDE、IM、API、Webhook、Cron 等入口。

2. **Agent Host / Runtime 层**

   管理模型调用、工具调用、上下文、session、流式响应、任务状态和 tracing。

3. **MCP 工具层**

   建设 MCP Registry 和 Tool Gateway，统一接入数据库、知识库、文件系统、Git、工单、日志、浏览器等工具。

4. **A2A Agent 层**

   建设 Agent Registry，通过 Agent Card 管理远程 Agent 能力、认证方式、输入输出模式和 SLA。

5. **编排层**

   使用工作流或图状态机编排复杂流程，支持人审、重试、补偿、断点恢复和任务队列。

6. **治理层**

   统一 IAM、RBAC、租户隔离、审计日志、敏感信息脱敏、Prompt Injection 防御、评测、灰度发布、成本控制和监控告警。

关键指标：

- 工具调用成功率。
- 参数正确率。
- 任务完成率。
- 平均延迟和成本。
- 人工接管率。
- 权限违规率。
- Prompt Injection 拦截率。
- Agent 间调用链可追踪性。

最后补一句：企业级 Agent 协议平台的核心不是“接入最多工具和 Agent”，而是让工具和 Agent 在统一协议、统一权限、统一审计和统一评测下可规模化运行。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/04_MCP%E4%B8%8EA2A%E5%8D%8F%E8%AE%AE%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L792)，来源许可：GPL-3.0。

<a id="k61bad8279b63"></a>

## 如何回答“请设计一个自进化、多平台、可长期运行的 Agent 系统”？

可以按九层架构回答：

1. **入口层**

   CLI、TUI、Web、IM、Email、Webhook、Cron、API Server。

2. **Gateway 层**

   平台适配、消息归一化、session 路由、命令注册、事件分发、权限回调。

3. **Runtime 层**

   模型循环、工具调用、interrupt、resume、streaming、task state、background task。

4. **Provider Router 层**

   多模型接入、能力路由、fallback、凭证解析、成本统计。

5. **Tool / Skill / Plugin 层**

   Tool Registry、Skill Hub、Plugin System、MCP Client、企业工具网关。

6. **Memory / Context 层**

   长期记忆、session search、context engine、compression、user profile、project context。

7. **Self-improvement 层**

   后台复盘、Skill 生成、Curator、知识评分、合并、归档、回滚。

8. **Safety / Governance 层**

   文件安全、命令安全、tool loop guardrails、sandbox、checkpoint、approval、audit。

9. **Eval / Training 层**

   trace、trajectory、harness、reward function、RL environment、失败回流。

关键原则：

- 入口和运行时解耦。
- 工具和技能注册化。
- 自进化只作用于受控知识资产。
- 后台复盘使用受限工具集。
- 所有副作用可审计、可回滚。
- 生产写操作默认需要审批。
- 轨迹数据既用于评测，也用于训练，但必须脱敏和授权。
- 通过 Harness 验证自进化是否真的提升，而不是只相信自我评价。

高分总结：

自进化多平台 Agent 的核心不是“接很多平台、装很多工具”，而是构建一个长期运行的智能操作系统：它能接收多端任务、稳定执行、沉淀经验、维护知识资产，并在严格安全和评测闭环中持续改进。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/09_%E8%87%AA%E8%BF%9B%E5%8C%96Agent%E4%B8%8E%E5%A4%9A%E5%B9%B3%E5%8F%B0%E8%BF%90%E8%A1%8C%E6%97%B6%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L689)，来源许可：GPL-3.0。

<a id="kf98c7cd63aeb"></a>

## 如何处理远程会话或云端执行中的权限请求？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

远程 Agent 通常在云端容器或远程 worker 中执行工具，而用户在本地 UI。此时权限请求需要跨会话桥接：

1. 远程执行器生成工具权限请求。
2. 本地 UI 收到请求并展示工具名、参数、风险说明。
3. 用户允许或拒绝。
4. 本地把 permission response 发回远程 session。
5. 远程继续执行或终止。

关键设计：

- 请求必须有唯一 ID。
- 权限请求可以被取消。
- 断线后要能恢复 pending 状态。
- 本地没有完整工具实现时，也要能展示工具 stub。
- 所有响应要进入审计日志。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/02_%E7%BC%96%E7%A0%81Agent%E4%B8%8EAgentOS%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L306)，来源许可：GPL-3.0。

<a id="k889900e2cc13"></a>

## 如何按运行、编排和接入职责选择 Agent 框架？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

可以按工程定位分为五类：

1. **通用 Agent SDK**

   代表：OpenAI Agents SDK。重点是 agent、tool、handoff、guardrails、tracing、MCP。

2. **图式工作流/状态机框架**

   代表：LangGraph。重点是状态图、持久化执行、人类介入、可恢复任务。

3. **多 Agent 协作框架**

   代表：CrewAI、AutoGen、Google ADK。重点是角色分工、通信、协作、任务编排。

4. **知识型 Agent/RAG 框架**

   代表：LlamaIndex Agent/Workflow。重点是数据连接、检索、索引、知识增强。

5. **编码 Agent 产品**

   代表：Claude Code、Codex、Cursor、Devin、Jules。重点是真实代码仓库读写、测试、提交、审查和任务执行。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/01_AIGC%E6%97%B6%E4%BB%A3AI%20Agent%E5%9F%BA%E7%A1%80%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L430)，来源许可：GPL-3.0。

<a id="ke70757dc7866"></a>

## 如何提升工具调用正确率？

<a id="batch4-p1-q6"></a>

**相关解释：** [Agent常见模式（ReAct/Plan and Execute等）](../15-%E5%89%8D%E7%AB%AF%E4%B8%8E%E6%B5%8F%E8%A7%88%E5%99%A8/React%E4%B8%8E%E7%BB%84%E4%BB%B6%E7%8A%B6%E6%80%81-01.md#k93a12d0c9256)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L199)，来源许可：GPL-3.0。

<a id="kc82b29c6dac5"></a>

## 如何理解 Agent，开发中会遇到哪些问题

**回答：**

Agent 与单次问答的区别，在于它能根据中间结果选择行动并改变外部状态。一个典型循环是：接收目标和约束，形成下一步动作，校验后调用工具，读取结果，决定继续、请求用户补充或结束。

开发中的问题可分为四类：理解错误导致目标偏移；工具名称、参数或顺序选择错误；外部系统超时、限流或部分成功；多轮任务状态丢失、重复执行或预算失控。它们需要不同处理，不能统一靠“让模型再试一次”。

工程上给工具建立明确的输入输出契约，用状态机记录执行过程，为可重试动作配置幂等机制和退避策略，为长任务设置最大步骤、成本与截止时间。把外部文本和工具输出视为待验证数据，避免其中的指令改变系统权限。最终衡量用户目标是否完成，同时记录失败阶段、时延、成本和人工接管率。

**最难的故障往往是执行结果未知。** 例如模型调用“生成素材”后客户端超时，服务器实际上已经创建了任务。此时立即重试可能重复扣费、重复生成；单纯返回“失败”又可能让用户重复提交。可以按下面的状态语义处理：

| 观察到的情况 | 系统应记录的状态 | 后续动作 |
| --- | --- | --- |
| 参数在执行前校验失败 | rejected | 修正输入，不调用业务服务 |
| 服务返回任务 ID | submitted / running | 保存 ID，查询或订阅进度 |
| 写请求超时，无法确认是否受理 | unknown | 用幂等键或业务查询核对结果 |
| 工具响应成功但产物不符合约束 | validation_failed | 保留产物与原因，进入修正步骤 |
| 产物满足格式、内容和交付约束 | completed | 保存产物版本及验收结果 |

幂等键需要绑定租户、业务操作和用户这一次意图，并记录请求参数摘要。同一个键携带不同参数应报冲突；用户主动要求“再生成一版”则属于新操作。服务端还需要原子去重或唯一约束，客户端仅生成一个字符串不构成幂等保证。数据库提交和外部调用分离时，可以使用事务 outbox、状态核对及补偿机制，但不能据此声称跨所有外部服务严格 exactly-once。

![Agent任务从决策到验收的闭环](https://raw.githubusercontent.com/WeThinkIn/AIGC-Interview-Book/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/imgs/baidu_multimodal_agent_20260922_20260924/01_Agent任务闭环.png)

图中把“工具调用成功”与“任务验收通过”分开，是因为 HTTP 200 只能说明某次请求在接口层成功。素材是否包含指定人物、是否保持正确尺寸、是否写入正确工作区，需要进一步校验。**Rocky认为，讲项目时能说明这种状态边界，比只列出使用过的框架更能体现工程判断。**

<a id="baidu-aigc-multimodal-agent-20260922-20260924-r2-q3-2"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%99%BE%E5%BA%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1747)，来源许可：GPL-3.0。

<a id="kfecc833643cf"></a>

## 如何理解Spec Coding和Harness？你认为Harness为什么能够提升Agent完成复杂任务的能力？

**回答：**

**Spec Coding** 是先把模糊意图沉淀为可执行、可验证的规格，再由人和 Agent 围绕规格实现。Spec 不只是需求文档，至少应包含目标、非目标、接口与数据契约、不变量、边界场景、验收测试和风险约束。它解决的是“要做对什么”。

**Harness** 是模型外部的运行与治理环境，负责上下文组装、工具发现、权限、执行沙箱、任务状态、checkpoint、超时重试、验证、trace、成本预算和人工接管。它解决的是“模型如何在真实环境中持续行动，并且让每一步可控、可恢复、可评估”。模型是概率决策内核，Harness 更接近 Agent 的运行时与控制系统。

二者的关系是：Spec 为任务提供目标函数和验收条件，Harness 把这些条件落实为运行约束和反馈。复杂任务之所以受益于 Harness，主要有五个原因：

- 把大目标拆成有状态的多步循环，模型每次只基于当前状态选择下一动作；
- 将代码搜索、编译、测试、浏览器或业务 API 的真实结果反馈给模型，减少纯语言猜测；
- 用权限、schema、状态机和预算约束动作空间，降低越权、死循环和无效调用；
- 通过 checkpoint、幂等、重试和回滚，让长任务能从局部失败恢复；
- 记录完整轨迹并用最终状态、测试、安全和成本判分，支持回归优化。

因此，同一个模型放进不同 Harness，复杂任务成功率可能差很多。Rocky认为，Spec 决定“终点和护栏”，Harness 决定“道路、仪表盘和故障恢复”；二者共同把一次性代码生成升级为可交付的软件工程。

<a id="insta360-agent-20260809-q4"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%BD%B1%E7%9F%B3%E5%88%9B%E6%96%B0%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L68)，来源许可：GPL-3.0。

<a id="k73b81f1a3210"></a>

## 如何用 Harness 做失败样本回流和持续优化？

失败样本回流流程：

1. 从线上 trace、用户反馈、人工接管、事故复盘中收集失败。
2. 给失败打标签：理解失败、上下文失败、工具失败、权限失败、策略失败、环境失败。
3. 清洗敏感信息。
4. 固化初始环境和期望状态。
5. 写成可复现 Task Spec。
6. 加入 regression / safety / business set。
7. 修复 prompt、工具、上下文、策略或产品流程。
8. 重新运行 Harness 验证。

注意：

- 不是所有失败都应该靠改 prompt。
- 工具错误应修工具 schema 或返回结构。
- 权限错误应修 policy。
- 上下文错误应修 retrieval / memory / compaction。
- 用户目标模糊应修产品交互和澄清流程。

成熟团队会把 Harness 当作 Agent 的“质量飞轮”：线上失败越多，评测集越强，发布越稳。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/08_Agent_Harness_Engineering%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L620)，来源许可：GPL-3.0。

<a id="k26821153f516"></a>

## 如何用 Trace 还原 Agent 的执行过程？

普通接口抛出异常时，状态码和异常栈通常能指出出错位置。Agent 即使没有抛异常，也可能在前几轮拿错文档、选错工具，最后生成一段看起来合理的错误答案。Trace 按时间还原这段执行过程，记录系统实际看到的输入、产生的输出和执行的动作。它不保存模型的私有思维链，也不能证明模型内部为什么作出某个判断。

以一次售后工单请求为例，Trace 可以按下面的顺序记录。

1. 请求进入系统时生成 `requestId` 和 `runId`，同时关联脱敏后的用户、租户标识，以及本次运行使用的代码、Prompt 和工具 Schema 版本。
2. 每次调用模型时保存脱敏后的输入摘要与模型输出，并记录 Token、耗时和停止原因，避免只留下最终回答。
3. 发生检索时记录查询内容、命中文档 ID、分数和真正注入模型的片段，并带上知识库版本。
4. 调用工具时生成 `toolCallId`，记录参数摘要、权限判定、执行结果和错误类型。重试还要带上 `attempt`、父 Span 和幂等键摘要，才能看出同一个动作执行了几次。
5. 任务结束或暂停时记录状态变化、Checkpoint、人工确认、最终 Outcome、总调用数、总成本和降级原因。

排查时从最终结果往前看，找到第一次偏离预期的位置。检索阶段拿错文档，就查切块、召回和 Reranker；证据已经正确，Agent 却选错工具，再查上下文与模型；工具返回成功而业务状态没有变化，则检查工具适配器和结果核验。这样能把“回答错了”缩小到某一次检索、模型调用或工具执行。

模型输入、工具参数和检索片段可能包含个人信息或业务机密，生产环境通常只保存脱敏摘要，并配合采样、访问控制和保留期限。排障需要的字段可以留下，完整原文不应默认长期保存。

回放某一次请求看 Trace，观察一段时间的延迟和错误率看 Metrics，核对谁批准了退款等外部操作看 Audit，比较不同模型或 Prompt 版本看 Eval Record。具体异常日志可以挂到对应 Span 上。这些记录通过同一个 `runId` 关联，不需要塞进一张大表。

`Session`、`Run`、`Trace`、`Span` 和 `Attempt` 的划分、异步任务的上下文传播，以及采样和敏感数据处理，详见 [AI 可观测性与 Trace](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/system-design/ai-observability.md)。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/interview-questions/agent-project-interview-guide.md#L399)，来源许可：Apache-2.0。

<a id="k23cdeb32b268"></a>

## 如何用一个案例讲清 Agent 项目？

假设项目是一个智能售后工单 Agent。用户可以用自然语言描述问题，系统会查询订单、检索售后政策、判断还缺哪些信息，并在用户确认后创建售后工单。

这里故意同时放入了三类能力：

- 检索售后政策，属于 RAG；
- 查询订单、创建工单，属于工具调用；
- 根据当前信息决定继续查询、追问还是结束，属于 Agent 决策。

其中，“创建工单”会修改外部状态，不能只依赖模型输出一个合法 JSON。权限校验、用户确认、幂等和执行结果核验都必须由业务系统负责。

项目中的 Agent Loop 可以采用 ReAct 这类执行方式：模型提出下一步动作，拿到环境返回的 Observation 后，再决定继续调用工具还是结束。

ReAct 指的是动作与观察交错推进，不是调用一次工具就算完成了 Agent 设计。生产 Trace 记录动作、工具结果、状态摘要和可核验依据即可，不需要保存模型的私有思维链。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/interview-questions/agent-project-interview-guide.md#L80)，来源许可：Apache-2.0。

<a id="k51f65012686a"></a>

## 如何组织主 Agent、子 Agent 与技能资源？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

复杂编码任务常常需要并行探索、分工实现和专业流程。子 Agent 和 Skills 分别解决两个问题：

- **子 Agent**：把任务拆给另一个模型会话，隔离上下文，支持并行。
- **Skills**：把可复用的专业知识、流程、模板和脚本打包，按需加载。

它们能降低主 Agent 上下文压力，并提升复杂任务的专业度。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/02_%E7%BC%96%E7%A0%81Agent%E4%B8%8EAgentOS%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L474)，来源许可：GPL-3.0。

<a id="k1d6112ce2e1c"></a>

## 如何给 Agent Loop 设置退出边界？

Agent 拿不到关键信息时，可能反复查询同一个订单，或者连续调用参数相同的工具。模型仍在返回下一步动作，任务却没有任何进展。如果执行器不主动终止，这个循环会一直消耗时间和 Token。

任务开始时，执行器要确定总截止时间、模型和工具的最大调用次数，以及 Token 和费用预算。每次准备调用模型或工具前，先检查剩余预算；单个工具还要有自己的超时时间，避免一次慢调用占满整条任务的期限。

次数没有超限也可能陷入死循环。系统可以比较连续几步的工具名、规范化参数和 State 版本。相同动作反复出现，或者执行多步后状态仍未变化，就按“无进展”停止。遇到退款等高风险动作则暂停任务，等待用户确认。

停止后要记录具体原因，并根据已完成的部分决定返回当前结果还是转人工。这些判断由执行框架或业务代码执行，Prompt 里的“最多调用十次”只能作为行为提示，不能代替系统限制。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/interview-questions/agent-project-interview-guide.md#L322)，来源许可：Apache-2.0。

<a id="kdf0fb91fc52e"></a>

## 如何编写一个智能体，帮助用户规划一次包含机票预订、酒店安排和景点游览的旅行？需要配置哪些工具？如何确保系统在面对不完整或矛盾的信息时仍能提供合理建议？

采用基于工具调用的智能体架构

> 用户输入 → 智能体分析任务意图 → 规划任务流程 → 多工具调用 → 整合回复结果

![img](https://pic3.zhimg.com/v2-0bd6934418581ff5cf5c232fef6bd5d8_1440w.jpg)

方法：

- 利用 LLM 分析用户输入中缺失的关键信息（如日期、预算、偏好），主动进行“反问式追问”
- 设定默认值与容错机制，未指定预算则设定默认中档；未指定具体日期，则提示最近可用时间段。
- 多轮规划修正能力，使用 ReAct 思维链提示结构，支持思考—行动—观察—再决策循环，自动纠偏

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/04-ai-algorithms/llm/llm-interview-questions.md#L271)，来源许可：GPL-3.0。

<a id="k2a567f622930"></a>

## 如何设计 Agent Marketplace / Skill Marketplace？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐ (3/5)**

本节从企业平台治理角度讨论 Marketplace 的上架、审核、权限和下架；Skill 在长期运行 Agent 中如何被自动评分、合并、归档和回滚，见 [09_自进化Agent与多平台运行时高频考点.md](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/09_自进化Agent与多平台运行时高频考点.md)。

Agent Marketplace 管可复用 Agent，Skill Marketplace 管可复用能力包或流程。

核心字段：

- 名称和描述。
- 适用场景。
- owner 和维护团队。
- 输入输出。
- 所需工具和数据权限。
- 风险等级。
- 版本。
- 示例任务。
- 评测结果。
- 安全审核状态。
- SLA 和支持方式。

上架流程：

1. 提交 Agent / Skill。
2. 自动检查元数据、依赖、权限。
3. 运行安全评测和功能评测。
4. 人工审核高风险能力。
5. 灰度给小范围用户。
6. 收集反馈和 trace。
7. 正式发布。

下架机制同样重要：

- owner 失联。
- 工具依赖失效。
- 评测回归。
- 安全风险。
- 成本过高。
- 业务规则过期。

Marketplace 的核心不是数量，而是可信、可评测、可治理。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/07_%E4%BC%81%E4%B8%9A%E7%BA%A7Agent%E5%B9%B3%E5%8F%B0%E4%B8%8E%E4%BA%A7%E5%93%81%E8%90%BD%E5%9C%B0%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L437)，来源许可：GPL-3.0。

<a id="kb38a5c20737c"></a>

## 如何设计一个企业级 AI Agent 系统？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

这里给出的是总览型答题框架，适合面试开场快速搭骨架；企业级 Agent Builder、Runtime、模型网关、Registry、多租户、Marketplace、平台选型等展开内容，见 [07_企业级Agent平台与产品落地高频考点.md](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/07_企业级Agent平台与产品落地高频考点.md)。

可以按以下框架回答：

1. **场景定义**

   明确是客服、数据分析、研发提效、运营自动化、企业搜索还是流程审批。

2. **能力边界**

   定义 Agent 能做什么、不能做什么、哪些动作需要人工确认。

3. **模型与路由**

   简单任务用便宜模型，复杂规划用强模型，敏感任务走人工。

4. **工具和协议**

   用 Function Calling 接业务 API，用 MCP 接标准工具，用 A2A 接远程专用 Agent。

5. **状态和记忆**

   会话状态、任务状态、长期记忆、企业知识库分开管理。

6. **工作流编排**

   确定性流程用 workflow，开放任务用 Agent，复杂流程用状态图。

7. **安全与权限**

   RBAC、审批、沙箱、审计、数据脱敏、prompt injection 防护。

8. **评估与观测**

   离线任务集、线上 tracing、人工反馈、失败样本回流。

9. **上线策略**

   从只读建议模式开始，再开放低风险工具，最后逐步开放写操作。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/01_AIGC%E6%97%B6%E4%BB%A3AI%20Agent%E5%9F%BA%E7%A1%80%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L808)，来源许可：GPL-3.0。

<a id="kf5cc165eaff5"></a>

## 如何设计一个能够避免循环调用的 Agent 状态机？

**回答：**

由运行时控制合法迁移，模型仅提出候选动作。可以设计如下路径，其中每个箭头都带有守卫条件和预算检查：

```text
INIT -> PLAN -> VALIDATE_ACTION -> EXECUTE -> VERIFY_RESULT
                      |                         |
                      v                         v
               WAIT_APPROVAL              DONE / REPLAN
                      |                         |
                      +----> VALIDATE_ACTION <--+

任何活动状态 -> FAILED / CANCELLED / DEADLINE_EXCEEDED
执行结果未知 -> RECONCILE -> VERIFY_RESULT
```

状态中保存任务契约、计划版本、已完成步骤、证据版本、在途动作、幂等键、错误分类与剩余预算。检查点应落在可恢复位置；恢复后先核对在途工具的真实状态，防止进程崩溃把已经完成的外部写入再执行一次。

循环检测至少有三层：相同状态版本下的同参数无效重复；多个动作之间的往返循环；计划不断改写但成功条件距离没有改善。动作指纹用于告警与拦截，不能把所有重复查询视为非法，因为轮询和瞬时故障恢复本来就需要重复。

真正保证运行在资源意义上有界的是步数、时间、调用和费用预算，每个回到计划或执行的循环都必须消耗预算，不能在重规划时补回。每个外部调用有有限超时，等待审批有明确挂起与恢复状态，终止状态不得自动重新进入执行。

这能保证本地编排不无限执行，不能承诺任何任务都成功，也不能保证失联的远端操作已经取消。用故障注入验证重复参数、A/B 往返、工具永不返回、重启恢复和审批后状态变化，才算验证了状态机，而不只是画了一张流程图。

<a id="baidu-agent-20260922-r2-q9"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%99%BE%E5%BA%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1081)，来源许可：GPL-3.0。

<a id="k357cf18a8c8a"></a>

## 如何设计企业内可用的编码 Agent？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

建议路线：

1. **只读阶段**

   先做代码问答、搜索、解释、review，不允许写文件。

2. **建议阶段**

   生成 patch，但由开发者应用。

3. **受控写入阶段**

   允许修改分支内文件，但所有 diff 需审查。

4. **验证阶段**

   允许运行测试、lint、构建，但禁止危险命令。

5. **PR 阶段**

   自动创建 PR，必须人工 review 后合并。

6. **持续优化**

   用真实任务、失败 case、review 反馈优化工具、prompt 和策略。

企业必备能力：

- SSO/RBAC。
- 仓库权限继承。
- 审计日志。
- 网络隔离。
- secret scanning。
- 私有 MCP Server。
- 模型和数据策略。
- 评测集和灰度发布。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/02_%E7%BC%96%E7%A0%81Agent%E4%B8%8EAgentOS%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L793)，来源许可：GPL-3.0。

<a id="k0cad2a10920d"></a>

## 如何评估一个 Agent 场景是否值得做？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

可以从八个维度评估：

| 维度 | 判断问题 |
| --- | --- |
| 频率 | 任务是否高频重复？ |
| 价值 | 自动化后能节省多少时间或提升多少收入？ |
| 可验证性 | 结果是否容易判断对错？ |
| 风险 | 失败是否可接受、可回滚？ |
| 工具完备性 | Agent 是否能拿到必要工具和数据？ |
| 权限清晰度 | 数据和动作权限是否明确？ |
| 人审成本 | 人类能否快速审核结果？ |
| 数据可用性 | 是否有历史样本和评测集？ |

优先做：

- 高频、低风险、可验证、工具齐全的任务。
- 人类审核成本低的任务。
- 已有 SOP 的任务。
- 能从历史数据构造评测集的任务。

慎重做：

- 低频高风险任务。
- 结果难验证任务。
- 需要大量主观判断的任务。
- 权限边界不清的任务。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/07_%E4%BC%81%E4%B8%9A%E7%BA%A7Agent%E5%B9%B3%E5%8F%B0%E4%B8%8E%E4%BA%A7%E5%93%81%E8%90%BD%E5%9C%B0%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L568)，来源许可：GPL-3.0。

<a id="k0dc2748971ac"></a>

## 如何避免把无关文件塞满上下文？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

策略：

- 先搜索后读取，避免盲目打开大量文件。
- 只读相关片段，而不是整文件。
- 对重复工具输出做折叠。
- 对日志只保留错误附近上下文。
- 用子 Agent 探索并返回摘要。
- 用结构化计划记录状态，而不是保留所有历史。
- 将低价值历史压缩成 summary。
- 根据任务阶段切换上下文：探索、实现、验证、总结。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/02_%E7%BC%96%E7%A0%81Agent%E4%B8%8EAgentOS%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L453)，来源许可：GPL-3.0。

<a id="k457af1ede4c3"></a>

## 如果 Agent 在调用工具时出现参数类型正确但业务含义错误，如何发现并阻止？

**回答：**

JSON Schema 能限制类型、枚举和结构，也能表达部分静态值域，但无法自动知道当前订单归谁、操作人是否有权限、状态是否允许迁移。这类错误必须在模型之外设置**语义验证与执行授权关卡**。

第一层解析和协议校验：拒绝未知字段、非法枚举、缺失参数、超过范围的值，以及单位不明确的金额。第二层业务校验：读取权威状态，检查租户归属、资源版本、金额单位、合法状态迁移和时间范围。第三层授权：由服务端身份绑定权限，不信任模型自己填写的 `tenant_id`、`is_admin` 或审批结果。

高风险动作先生成具体预览，审批必须绑定操作内容、资源版本、有效期和请求主体。仅仅存在一个 `approval_id` 字符串，并不代表审批有效；参数变化后不能沿用旧审批。工具返回文本和检索文档属于数据，不能因其写着“管理员已批准”就提升权限。

还要避免检查与执行之间的竞态。比如校验时订单可取消，执行前已经发货，应在事务中再次确认，或者通过条件更新验证版本与状态：

```sql
UPDATE orders
SET status = 'CANCELLED', version = version + 1
WHERE tenant_id = :trusted_tenant
  AND order_id = :order_id
  AND version = :expected_version
  AND status = 'PENDING';
```

该语句假设取消 `PENDING` 订单符合业务规则；仍须先校验身份、审批与业务幂等。影响行数为零表示条件未满足，要查明是状态冲突、版本变化还是资源不存在，不能让模型反复尝试不同订单号。

对模型解释出的业务意图也要验证。即使所有参数都合法，取消 A 订单与用户要求修改 B 订单仍然不一致。最终需将候选动作与用户任务契约对照；存在关键歧义时澄清，不猜测执行。

<a id="baidu-agent-20260922-r2-q5"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%99%BE%E5%BA%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L994)，来源许可：GPL-3.0。

<a id="k9c7d5287de93"></a>

## 如果 Agent 效果不达预期，你怎么判断瓶颈在哪？——是模型能力不够？工具调用不准？上下文丢失？还是评测标准有问题？怎么区分？

**回答：**

先固定模型、Prompt、工具版本、检索索引和评测集，建立一条可回放的基线，然后将端到端失败拆成阶段性指标。不能看到最终回答错误就直接归因于模型。

可以采用“分层替换 + 轨迹定位”的诊断矩阵：

| 检查项 | 替换或对照实验 | 主要判断 |
| --- | --- | --- |
| 评测标准 | 人工复核、双标注、对照参考答案 | 标准是否不可判定或偏置 |
| 模型能力 | 用强模型/人工 oracle 固定工具和证据 | 强模型也失败则不一定是当前模型 |
| 工具调用 | 给定正确工具和参数，跳过模型选参 | 仍失败则检查工具或执行器 |
| 上下文 | 注入人工整理的最小充分上下文 | 恢复成功说明检索/压缩/组装有问题 |
| 检索 | 给定 gold evidence，比较召回与生成 | gold 成功而真实检索失败，瓶颈在知识链路 |
| 规划 | 给定人工计划，只评估执行 | 区分计划错误与执行错误 |

同时检查轨迹事件：是否选择了错误工具、参数是否通过 schema、检索是否命中支持证据、压缩前后关键事实是否保留、Observation 是否被下一步消费、是否提前停止或陷入循环。用受控 ablation 比较：

$$
\Delta_i = M(\text{system with component }i\text{ replaced by oracle})
-M(\text{baseline})
$$

其中 $M$ 可以是任务成功率或事实支持率。$\Delta_i$ 越大，说明该组件更可能是当前瓶颈，但还需要统计显著性和分桶验证。

最后要关注评测与线上目标是否一致。若离线评分下降但用户任务完成率提升，可能是评测标准错配；若离线提升而线上没有变化，可能是数据分布、延迟、权限或交互流程问题。模型能力不足只能在工具、证据、上下文和评测均被控制后再下结论。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/DeepSeek%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L568)，来源许可：GPL-3.0。

<a id="kbf85dd70544e"></a>

## 如果 Agent 跑了 20 分钟还没结束，用户等不及了要取消，你的系统怎么响应？——取消后，已经在执行的工具调用怎么处理？任务状态怎么回滚？

**回答：**

取消是跨层传播的控制信号，不是前端断开连接就结束。请求层生成 `cancel_token`，通过任务队列、Agent Loop、模型流式请求和工具执行器逐层传递；每个耗时阶段在安全点检查，并将任务状态从 `RUNNING` 原子地改为 `CANCELLING`，防止新的步骤继续提交。

工具调用分三类处理：

1. **可安全中断的纯读操作：** 取消 HTTP 请求、释放连接和临时资源，标记为 cancelled。
2. **支持取消协议的可中断写操作：** 向工具发送 cancel，等待确认或超时后进入补偿流程。
3. **不可撤销的副作用：** 不能假设取消等于回滚。必须使用幂等键、操作状态查询、事务或补偿动作；例如支付提交后取消，只能查询最终状态并做业务允许的退款/冲正，不能重新执行。

任务状态最好使用显式状态机：

$$
RUNNING\rightarrow CANCELLING\rightarrow
\begin{cases}
CANCELLED, & \text{所有可控子任务已停止};\\
UNKNOWN\_IN\_FLIGHT, & \text{副作用状态无法确认};\\
COMPLETED, & \text{取消到达前已完成}.
\end{cases}
$$

“回滚”也要分层：内存中的规划和未提交状态可以恢复到最近 checkpoint；数据库事务可以回滚未提交写入；已经提交的外部副作用只能通过查询和补偿，不能把事件日志删掉假装没发生。用户界面应收到明确状态和任务 ID，允许稍后查询；后台还要设置 orphan task 扫描、资源租约、最大运行时和告警，防止客户端断开后任务泄漏。

<a id="deepseek-agent-20260908-q11"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/DeepSeek%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L644)，来源许可：GPL-3.0。

<a id="k0c7321546627"></a>

## 如果Agent接入大量工具，如何避免工具描述过长导致Prompt膨胀？有哪些优化方式？

**回答：**

核心原则是**工具渐进披露**：模型不需要在每一轮看到所有工具的完整 Schema。可以采用以下方案：

1. 先用规则、小模型或轻量 LLM 做意图/领域路由，只暴露当前任务可能用到的工具；
2. 建立工具目录，第一阶段只给工具名、短描述、标签和能力摘要，模型选定候选后再加载详细 Schema；
3. 合并高度相似的工具，统一参数模型，减少重复描述；
4. 将稳定的工具文档放在外部检索库，按需获取示例、错误码和约束；
5. 对多 Agent 采用按角色分配工具，子 Agent 只看到自己的最小权限集合；
6. 对参数枚举、默认值和必填项使用结构化 Schema，减少自然语言冗余；
7. 缓存版本化的公共工具描述，监控工具 Token 占比和选择错误率；
8. 对工具结果做裁剪、摘要和结构化投影，避免 Observation 反过来造成上下文膨胀。

工具发现本身也要可验证。目录搜索不能把不存在的工具、过期版本或越权工具暴露给模型；工具被选中后仍要由服务端做权限和 Schema 校验。应通过任务成功率、工具选择准确率、参数解析率、Token、P95 延迟和错误率比较“全量工具描述”和渐进披露，而不是只看 Prompt 变短。

<a id="bilibili-ai-agent-20260818-q13"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%93%94%E5%93%A9%E5%93%94%E5%93%A9%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L217)，来源许可：GPL-3.0。

<a id="k1c526c028d57"></a>

## 如果你来做 DeepSeek-Harness 的下一个版本，你会加什么功能？

**回答：**

在没有把某个具体实现细节当成已确认事实的前提下，我会优先补强以下能力：

1. **可恢复任务状态机。** 原生支持事件日志、版本化 checkpoint、暂停/恢复、取消和重放；每次模型决策、工具调用和 Observation 都能关联 `task_id` 与 `step_id`。
2. **策略门控。** 在工具执行前统一检查 schema、权限、预算、数据分级、幂等键和人工确认策略，并允许按工具风险配置不同门槛。
3. **可靠的上下文管理。** 将消息、摘要、证据、记忆和工具结果分层管理，提供 token 预算、关键事实保护、压缩评估和原文回溯，而不是只做字符串截断。
4. **仿真与回放评测。** 支持固定环境、mock 工具、故障注入、隐藏测试、轨迹回放和单步对比，使模型、Prompt、工具描述和策略可以做可重复消融。
5. **失败分类与自动回流。** 从 trace 中区分模型、检索、工具、权限、执行和评测失败，生成待人工确认的修复候选，不直接把失败轨迹当训练正样本。
6. **多租户与密钥隔离。** 让工具凭证、上下文、缓存、事件和长期记忆在租户边界内隔离，默认禁止把敏感信息写入模型 Prompt 和普通日志。
7. **成本与可靠性调度。** 根据任务风险和剩余预算选择模型、并行度、上下文规模和验证强度，对长任务设置阶段性预算和自动降级。

每个功能都要有验收指标。例如恢复能力看 checkpoint 恢复成功率和重复副作用率；上下文能力看关键事实保留率和任务成功率；评测能力看线上 badcase 到回归用例的闭环时间。Harness 的下一个版本不应只增加“更强的自主性”，而应增加“自主性可被验证和撤销”的能力。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/DeepSeek%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L741)，来源许可：GPL-3.0。

<a id="kf477a0e10e45"></a>

## 如果单一智能体的提示词过长，导致性能下降，如何将其拆分为多个智能体，并在合适的时机调用不同的智能体？

当单一智能体的提示词过长，影响性能时，我会采用“模块化智能体架构”解决，具体如下：

1. 功能拆分：将大智能体按功能划分为多个子智能体，例如：行程规划、机票预订、酒店推荐等，每个子体负责单一任务，提示词更短、聚焦。
2. 主控调度器：设计一个主控Agent作为“路由器”，根据用户请求类型或上下文意图，动态调用对应子体。例如：识别“订酒店”意图后，调用酒店智能体。
3. 上下文共享：通过共享存储（如Memory模块）或摘要传递，实现子体间信息协同，避免重复问询。
4. 提示词压缩：对每个子体使用结构化提示+嵌入指令压缩技术，确保上下文长度控制在合理范围内。

这种方式能提升系统响应效率、增强可维护性，并保持智能体的扩展性。

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/04-ai-algorithms/llm/llm-interview-questions.md#L285)，来源许可：GPL-3.0。

<a id="k04d1b58fcb37"></a>

## 如果工具调用一直没有达到成功条件，任务不断重试并最终卡死，你会如何处理？

**回答：**

先把“任务成功”定义为外部可验证的后置条件，再区分瞬时故障、参数错误、执行结果未知和规划无进展。不能让模型通过不断说“再试一次”延长任务，也不能用“状态没变”一个条件直接否决所有重试。

| 失败类型 | 处理方式 |
| --- | --- |
| 只读请求限流、暂时不可用 | 有界重试，遵守 `Retry-After`，指数退避加随机抖动 |
| 参数缺失或不符合约束 | 返回结构化错误，有限次数修正参数并重新校验 |
| 权限拒绝、明确不允许的业务操作 | 终止该动作，必要时等待正规授权 |
| 写操作超时，是否提交未知 | 先按幂等键查询执行状态，不立即重复写入 |
| 工具成功但任务仍无进展 | 检查计划假设和证据，有限重规划或澄清 |

任务运行时维护总体 deadline、调用次数、模型 token、费用、重规划次数和在途调用。预算要跨工具与模型统一累计，不能每次换工具就重置。指数退避可采用 full jitter：

$$
\Delta t_k\sim U\!\left(0,\min(t_{\max},t_0 2^k)\right)
$$

其中 $k$ 是本轮重试序号。等待时间与下一次调用都必须落在剩余 deadline 内，取消应传播到可取消的底层请求。客户端停止等待不代表外部操作已经停止，应继续核对副作用状态。

“没有状态变化”要按任务解释：读取服务暂时 503 后状态未变，仍允许预算内重试；数据库异步任务正在运行，需要退避轮询；同一个模型反复输出相同无效参数，才更像无进展循环。动作指纹应结合工具、规范化参数、任务状态版本和证据变化判断。

超过预算后输出已完成步骤、确定失败项、状态未知项和恢复入口。**能明确终止并保留现场的失败，比伪装成持续工作的死循环更可控。**

<a id="baidu-agent-20260922-r2-q6"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%99%BE%E5%BA%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1020)，来源许可：GPL-3.0。

<a id="k9c41e56640c4"></a>

## 如果工具调用超时或返回空值，你如何设计Prompt让Agent反馈用户？

<a id="batch4-p1-q7"></a>

### 补充说明

<a id="batch4-p2-q7"></a>

**相关解释：** [Agent常见模式（ReAct/Plan and Execute等）](../15-%E5%89%8D%E7%AB%AF%E4%B8%8E%E6%B5%8F%E8%A7%88%E5%99%A8/React%E4%B8%8E%E7%BB%84%E4%BB%B6%E7%8A%B6%E6%80%81-01.md#k93a12d0c9256)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%BF%AB%E6%89%8B%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L181)，来源许可：GPL-3.0。
- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%BF%AB%E6%89%8B%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L270)，来源许可：GPL-3.0。

<a id="kb4389438fafa"></a>

## 如果把这些 Harness 和你实习中的 Agent 项目结合，你会怎么做？是否有必要替换当前方案？

**回答：**

首先定位现有系统的瓶颈：是模型能力、检索质量、工具接口，还是执行状态不可恢复、上下文管理混乱、扩展成本过高。只有后几类问题直接属于 Harness 的主要职责。

接入采用适配方式：企业身份与权限、知识库和消息队列保留独立服务边界，把业务查询、文档读取和受控操作包装为稳定工具；Harness 负责上下文与执行循环。原有 tracing、预算、取消、审计与评测接到扩展点，避免让某个框架专有对象成为业务数据库的核心数据模型。

先选择低风险只读任务做离线回放，再在小流量场景灰度。固定模型、任务、工具和预算，对比任务成功率、工具错误、P95 延迟、成本、摘要后续接成功率与恢复时间。检查状态迁移、多租户隔离、模型供应商切换和框架升级是否可控。

如果现有方案任务边界清楚、运行稳定、扩展成本低，可以只吸收摘要、事件日志和工具中间件等设计。若框架确实能减少大量自建运行时维护，并在相同约束下提升指标，再逐模块替换。替换必须有回退路径，不能同时更换模型、检索、工具和 Harness 后再声称某一项带来了收益。

<a id="bytedance-agent-autumn-20260916-q11"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%AD%97%E8%8A%82%E8%B7%B3%E5%8A%A8%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1390)，来源许可：GPL-3.0。

<a id="kbbd003a09b95"></a>

## 如果要设计一个好的 Agent，除了大模型，还会设计哪些部分

**回答：**

<a id="tencent-llm-collection-20260903-q107"></a>

**相关解释：** [agent 调用工具这个过程是怎么优化的？](Agent%E3%80%81%E5%B7%A5%E5%85%B7%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81-01.md#k98cb3547adb1)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E8%85%BE%E8%AE%AF%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1409)，来源许可：GPL-3.0。

<a id="kba373d1341d4"></a>

## 如果让你从零开始设计一个Agent系统，你认为需要包含哪些关键模块？

**回答：**

我会先问清任务是否真的需要 Agent。固定、低风险、步骤确定的业务优先使用 Workflow；只有任务路径依赖动态观察、工具反馈或开放环境时，才引入 Agent 决策循环。

从零设计时可以分成八层：

1. **接入与身份层：** 用户、租户、会话、鉴权、配额、输入校验和风险等级。
2. **任务与状态层：** 目标、计划、已完成步骤、待办、artifact 引用、checkpoint 和终止条件。状态应外置，不能只存在模型上下文里。
3. **Context Builder：** 组装系统规则、当前工作状态、近期对话、按需长期记忆、RAG 证据和候选工具，并管理 Token 预算。
4. **模型与编排层：** 意图路由、规划、结构化输出、模型选择、Workflow/状态机/Agent loop，以及最大步数和重规划策略。
5. **工具层：** 工具注册、JSON Schema、权限、超时、幂等、速率限制、结果裁剪、沙箱与副作用确认。
6. **知识与记忆层：** 文档检索、用户/项目长期记忆、事件日志、写入门控、冲突更新、过期与删除。
7. **可靠性与安全层：** 验证器、重试/熔断/降级、回滚、人工审批、Prompt Injection 防护、密钥隔离和审计。
8. **可观测与评测层：** trace、模型/Prompt/工具版本、Token、延迟、任务成功率、工具正确率、恢复率、安全违规率和回归门禁。

运行时可以抽象为：

$$
s_t \xrightarrow{\pi_\theta(\cdot\mid c_t)} a_t
\xrightarrow{\text{tool/env}} o_{t+1}
\xrightarrow{\text{validate/update}} s_{t+1}
$$

其中 $c_t$ 是 Context Builder 从完整状态中投影出的当前上下文。终止不能只靠模型输出“完成”，还要检查任务目标、业务状态、测试或验证器。架构的关键不是模块越多越好，而是每个概率决策后都有外部证据，每个副作用前都有确定性约束，每个长任务都有可恢复状态。

<a id="insta360-agent-20260809-q5"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%BD%B1%E7%9F%B3%E5%88%9B%E6%96%B0%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L87)，来源许可：GPL-3.0。

<a id="k637303320d6f"></a>

## 如果设计一个基于 Qwen3.5 的企业级多模态 Copilot（比如能看 PDF、看报表、看界面截图，还能写代码、查文档），会怎么搭架构？怎么用好它的多模态和 Agent 能力？

从“**模型层 – Agent 层 – 工具层 – 数据/知识层 – 监控与反馈层**”五层来设计：

1. **模型层**
   - 主力模型：托管版 Qwen3.5-Plus（享受 1M 上下文、多模态和工具生态）；
   - 备选/本地模型：开源 Qwen3.5-397B-A17B 或中型变体（用于内部高敏场景）。

2. **Agent 层**
   - 使用 Qwen 官方的 Agent 框架或类似 LangChain 的 orchestration：
     - **Planner：** 负责把用户需求分解为一系列子任务（阅读文档→抽取要点→比对多个来源→生成报告）；
     - **Controller：** 根据当前上下文决定调用哪些工具/检索/代码执行；
     - **Memory：** 采用向量数据库存储长期记忆（历史对话、文档索引、任务执行结果）。

3. **工具层（Tooling）**
   - **搜索工具**：内置 Web 搜索，用于实时知识获取；
   - **代码执行工具**：连接沙箱执行环境（Python/R/SQL），支持数据分析、脚本运行；
   - **文件解析工具**：将企业 PDF、Word、Excel、PPT 等转为结构化文本/表格，作为多模态输入；
   - **UI 操作工具**：结合 Qwen3.5 的视觉能力，对 UI 截图进行语义理解并驱动自动化操作（相当于 GUI Agent）。

4. **数据/知识层**
   - 建立企业内部知识索引：
     - 文档向量化（包括文本和截图/扫描件），使用 Qwen3.5 的多模态编码能力；
     - 插件形式的“知识库检索”工具，Agent 在回答问题前先检索相关文档再总结（RAG）。
   - 对财报、报表等结构化数据，构造专门的数据 API 工具，Agent 可通过调用这些工具做精准分析。

5. **监控与反馈层**
   - 日志与度量：
     - 监控调用频次、延迟、失败率、token 消耗；
     - 监控错误类型（事实性错误、安全越权、工具调用失败等）。
   - 反馈闭环：
     - 收集用户评分 + 漏标问题作为 RL 训练数据；
     - 利用 Qwen3.5 的异步 RL 框架持续进行对齐和策略优化。

通过这样分层设计，可以充分用好 Qwen3.5 的：
- 原生多模态能力（看图/看 PDF/看界面）；
- 长上下文（跨文档、跨会话关联分析）；
- Agent + 工具使用能力（检索、代码执行、自动化操作）；

最终形成一个“**既能读懂复杂企业信息，又能主动操作工具和系统**”的企业级 Copilot，而不仅仅是一个聊天问答机器人。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E5%A4%9A%E6%A8%A1%E6%80%81%E5%9F%BA%E7%A1%80/Qwen-VL%E7%B3%BB%E5%88%97%E6%A8%A1%E5%9E%8B%E6%A0%B8%E5%BF%83%E8%80%83%E7%82%B9.md#L1737)，来源许可：GPL-3.0。

<a id="k85f9c7c4bf88"></a>

## 子 Agent 适合处理哪些任务？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

适合：

- 大仓库并行探索。
- 独立模块实现。
- 测试修复。
- 代码审查。
- 文档补充。
- 问题复现。
- 多方案对比。

不适合：

- 需要立即阻塞主流程的下一步。
- 写同一文件的并行任务。
- 模糊且高度耦合的决策。
- 需要强全局一致性的核心设计。

设计要点：

- 子任务要具体、边界清晰。
- 明确可写文件范围。
- 返回变更文件和结论。
- 不要重复分派同一个问题。
- 主 Agent 负责整合和最终验证。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/02_%E7%BC%96%E7%A0%81Agent%E4%B8%8EAgentOS%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L485)，来源许可：GPL-3.0。

<a id="k273d4cca5a44"></a>

## 官方博客提到为 Qwen3.5 搭建了一套异步强化学习框架，用来支撑大规模智能体训练。你能具体说明异步 RL 相对传统同步 RL 的改进点，以及它如何在工具使用、多轮对话等场景中发挥作用吗？

传统的同步 RL（如经典 PPO pipeline）通常是“**采样端 – 训练端 强耦合**”：  
采样（rollout）完成一批 episode → 汇总 → 统一更新 → 再开始下一轮，整个过程容易被最慢的任务拖慢，扩展到大规模 Agent 场景会非常低效。

Qwen3.5 的 **异步 RL 框架**在三个维度上做了拆分和解耦：

1. **采样与训练彻底异步**
   - 大量智能体进程（可能是数万甚至百万级）在不同环境中并行运行（网页、GUI、API 工具等），实时生成 (state, action, reward) 序列；
   - 这些数据被写入分布式缓冲区/消息队列，训练服务端按需拉取，而不是等待“所有人一起结束”；
   - 这样快任务不会被慢任务阻塞，新数据可以源源不断补充，训练端处于持续高负载状态，GPU 利用率更高。

2. **多模态、多任务统一框架**
   - 文本生成、多轮对话、工具调用、视觉交互（比如 UI 截图分析）都以统一的“序列决策”形式表征；
   - 奖励可以来自：
     - 规则（例如工具调用是否成功）；
     - 判别模型（例如一个评估模型给出的质量打分）；
     - 人类反馈（如评级）。
   - 这些多源奖励通过异步框架统一汇入训练过程。

3. **稳定性和工程可运维性**
   - 可在训练端做 **优先级重放**（优先使用有信息量的样本）、多任务混合；
   - 遇到单个环境故障、网络抖动不会影响整体训练，只会少一部分采样源；
   - 易于做 A/B 测试：不同策略的 Agent 可以并行跑，异步汇总结果进行对比更新。

在工具使用、多轮对话场景中，这意味着模型可以通过**持续在线交互**，不断从“真实任务执行结果”中学习，而不是只依赖静态监督数据；也为“会自己用搜索、会调用代码执行器”的 System 2 型智能体打下基础。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E5%A4%9A%E6%A8%A1%E6%80%81%E5%9F%BA%E7%A1%80/Qwen-VL%E7%B3%BB%E5%88%97%E6%A8%A1%E5%9E%8B%E6%A0%B8%E5%BF%83%E8%80%83%E7%82%B9.md#L1624)，来源许可：GPL-3.0。
