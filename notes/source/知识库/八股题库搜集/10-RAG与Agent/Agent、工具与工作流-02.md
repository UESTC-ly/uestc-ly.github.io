# Agent、工具与工作流

<a id="k1fbdc169a926"></a>

## Agent记忆模块如何迭代更新，新旧经验冲突时该怎样取舍留存？

**回答：**

Agent Memory 应被设计成有治理的状态系统，而不是一张不断追加聊天记录的表。成熟链路通常是：候选提取、写入判断、结构化、去重与冲突检测、版本化保存、检索使用、反馈更新和过期清理。

写入前先判断长期价值。一次性的寒暄、低置信推测和敏感信息默认不进入长期记忆；明确偏好、稳定身份事实、未完成任务状态、反复出现的问题和经过验证的成功经验才是候选。每条记录至少包含 `subject`、`predicate`、`value`、`scope`、`source`、`timestamp`、`confidence`、`valid_from/to` 和权限标签。

新旧记忆冲突时不能简单遵循“新数据覆盖旧数据”。应按以下维度决策：

- 权威性：用户明确更正、业务主库或工具执行结果，高于模型推断和历史摘要。
- 时效性：对地址、职位、偏好等可变化事实，较新的高置信记录优先，但旧版本保留审计链。
- 适用范围：工作场景与生活场景的偏好可能同时成立，应该按 scope 并存，而不是互相覆盖。
- 证据强度：多次独立观测可以提升置信度；单次异常不应立即改写长期事实。
- 风险等级：影响付款、权限、医疗或合规的记忆不能只靠自动合并，应重新确认或人工复核。

对于真正矛盾且无法自动裁决的记录，系统应保留两个版本并标记 `conflicted`，在相关任务出现时主动澄清。对成功/失败经验，还要区分“相关性”和“因果性”：一次成功轨迹不等于其中每一步都值得固化为 Skill。

遗忘同样重要。可以使用 TTL、时间衰减、低命中淘汰、用户删除和版本压缩；但法律要求、授权状态和审计记录应按制度管理，不能被通用衰减策略误删。

本质判断是：记忆系统的质量不取决于存得多，而取决于能否把正确、适用、可追溯的信息在正确时机取出来，并避免旧错误变成长期先验。

<a id="alibaba-taotian-agent-20260722-q9"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L648)，来源许可：GPL-3.0。

<a id="k394a300e5cee"></a>

## Agent陷入死循环或重复调用，怎么兜底？

**面试官：** Agent陷入死循环或重复调用同一个工具，你们的系统有什么兜底机制？

**回答：**

死循环治理要同时限制资源消耗和识别“没有进展”。固定最大 15 步、同一工具每分钟 5 次可以作为某个业务的配置，但不能当成普适答案。搜索任务、代码任务和高风险交易的合理预算完全不同。

可以设计六层保护：

1. **硬预算。** 限制总步骤、模型 Token、工具次数、总耗时、金额、外部请求数和并行度。任何一个预算耗尽都进入受控终止，而不是继续请求模型“再试一次”。
2. **调用指纹。** 对 `tool_name + 规范化参数 + 关键环境版本` 做哈希。连续重复相同调用且环境未变化时，不再次执行副作用工具，而是返回缓存结果或明确告知重复。
3. **进展不变量。** 观察已解决子目标数、错误类型、文件哈希、数据库状态、测试通过数或检索到的新证据。若若干步后状态没有增量，即使工具参数略有变化，也可能是循环。
4. **错误分类与重试策略。** 仅对瞬时错误重试，并采用指数退避和随机抖动；参数错误、权限错误和确定性业务拒绝不应盲目重试。
5. **熔断与降级。** 某工具持续失败时打开 Circuit Breaker，切换备用工具、回退到只读模式、请求用户补充信息或转人工。
6. **可恢复终止。** 退出前保存 Checkpoint、已完成事项、失败原因和下一步建议，使用户或人工能够从断点继续。

不建议依赖“最近几轮 Thought 语义相似度”作为主要检测手段。一方面模型的隐式推理未必可见或适合持久化，另一方面语言表述可以变化但行为仍然重复。应优先基于可观察的 Action、参数、环境状态和任务进度检测。

副作用工具还必须使用幂等键和执行前置条件。即使 Agent 重复调用，支付、发信、发布和删除操作也不能重复生效。高风险动作应采用准备、确认、提交的两阶段交互，并在提交前再次校验用户授权和当前状态。

**真正的兜底不是“发现循环后报错”，而是让系统在任何重复、超时和失败路径下都能控制成本、阻止重复副作用，并留下可恢复状态。**

<a id="alibaba-cloud-agent-algo-20260901-q10"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1484)，来源许可：GPL-3.0。

<a id="kcb7eefb2743c"></a>

## Agent项目2，对比项目1，在Agent设计层面有什么差异？

**回答：**

对比两次真实项目的决策结构，而不是只列“一个用了框架 A，另一个用了框架 B”。若项目细节不能公开，可以说明抽象架构和自己参与范围。

| 比较维度 | 应回答的问题 |
| --- | --- |
| 任务与验收 | 输出分析报告，还是改变外部系统状态？ |
| 控制权 | 固定节点、动态选工具，还是多代理分工？ |
| 上下文 | 单次检索、会话记忆，还是跨运行经验？ |
| 执行边界 | 只读、可恢复写入、哪些步骤需要确认？ |
| 可靠性 | 是否持久化检查点、幂等、补偿和回放？ |
| 评测 | 正确性、任务完成率、失败恢复、成本如何量化？ |

例如一个离线报告系统可以采用固定检索与生成链，另一个资源操作系统更需要资源解析、授权确认和执行状态机。这是说明比较方法的例子，不能直接充当自己的两个项目。

最后解释差异的业务原因和实测代价。如果第二个项目增加了动态规划，应说明它解决了哪些原先无法覆盖的任务，是否付出了更高延迟或调试成本；没有相应证据时，不必声称架构更先进。

<a id="meituan-agent-20261012-18fa4134-q13"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%BE%8E%E5%9B%A2%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L934)，来源许可：GPL-3.0。

<a id="k2fd99d818bd8"></a>

## AI Agent 中的 Harness Engineering 是什么？

Harness Engineering 指围绕 Agent 构建一套可复现、可运行、可评估、可回放、可上线门禁的工程系统。它不只是“写几个测试用例”，而是把 Agent 放进接近真实业务的受控环境里，让它真正执行任务，然后系统性记录和评估结果。

可以把它理解成：

$$
\text{Agent Harness} =
\text{Tasks} + \text{Environment} + \text{Runner} + \text{Trace} + \text{Grader} + \text{Report} + \text{Gate}
$$

Agent Harness 的目标是回答五个问题：

- Agent 能否完成任务？
- Agent 是如何完成或失败的？
- 新版本相比旧版本是否退化？
- 失败是模型问题、工具问题、上下文问题、权限问题还是环境问题？
- 当前版本是否可以上线、灰度或扩大权限？

**面试金句：**

Harness Engineering 是 Agent 从 demo 走向生产的质量基础设施。没有 Harness，就只能靠人工试用和主观感觉判断 Agent 是否变好。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/08_Agent_Harness_Engineering%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L47)，来源许可：GPL-3.0。

<a id="k8c2727f262d4"></a>

## AI Agent 为什么需要 OCR 和 UI Grounding？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐⭐ (5/5)**

GUI Agent、浏览器 Agent、手机 Agent 和办公自动化 Agent 都需要理解屏幕上的文字、按钮、输入框、菜单和状态反馈。OCR 是其中最基础的感知能力之一。

一个典型 GUI Agent 流程：

```text
屏幕截图
  -> OCR 识别文字
  -> UI 元素检测/分割
  -> 坐标 grounding
  -> LLM 规划下一步动作
  -> 点击/输入/滚动
  -> 观察新截图并继续循环
```

OCR 在这里解决“屏幕上写了什么”，UI Grounding 解决“该在哪里点击”。二者结合后，Agent 才能完成登录、搜索、填写表单、下载文件、读取弹窗等任务。

工程上要注意：

- OCR 坐标要和屏幕坐标系一致；
- 小字号、低对比度、缩放比例会影响识别；
- 图标按钮可能没有文字，需要结合图标识别或 accessibility tree；
- Agent 不能盲目执行 OCR 到的恶意指令，需要安全策略过滤。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BB%8F%E5%85%B8%E6%A8%A1%E5%9E%8B/OCR%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L329)，来源许可：GPL-3.0。

<a id="ka5f26a661365"></a>

## AI Agent 如何调用目标跟踪模型完成视频理解任务？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐⭐ (5/5)**

在 AI Agent 系统中，目标跟踪通常不是孤立模型，而是视觉工具链的一部分。一个典型视频 Agent 可以这样工作：

```text
用户问题：找出视频中第一个拿起黑色背包的人，并说明他随后去了哪里

LLM 解析任务
  -> 开放词汇检测：black backpack / person
  -> 分割模型：获得人物和背包 mask
  -> 跟踪模型：跨帧维护人物 ID 和背包轨迹
  -> 事件检测：识别“拿起”“离开”“进入房间”等动作
  -> 多模态总结：生成自然语言答案
```

目标跟踪在这里承担“时序记忆”的角色：它让 Agent 知道某个对象在时间轴上的连续身份和状态变化。

工程上需要注意：

- 跟踪结果要带置信度，不能把不确定轨迹当作事实；
- 需要保留关键帧证据，方便回溯和人工审核；
- 复杂任务中应结合检测、分割、ReID、动作识别、VLM 推理；
- 对安防、身份识别、医疗等高风险场景，应加入权限、隐私和误判防护。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BB%8F%E5%85%B8%E6%A8%A1%E5%9E%8B/%E7%9B%AE%E6%A0%87%E8%B7%9F%E8%B8%AA%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L270)，来源许可：GPL-3.0。

<a id="k00c2577a9d82"></a>

## AI 视频统一系统、创作工作流与未来趋势

> 前面章节分别讨论了基础概念、核心架构、模型路线、长视频生成和训练工程；本章进一步回答：为什么视频生成、编辑、理解、音频、多模态控制和交互式创作正在走向统一视频智能系统，以及这些能力如何从脚本分镜走到多轮迭代的成片工作流。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E8%A7%86%E9%A2%91%E5%9F%BA%E7%A1%80%EF%BC%88%E7%B2%BE%E5%8D%8E%E7%89%88%EF%BC%89/06_AI%E8%A7%86%E9%A2%91%E7%BB%9F%E4%B8%80%E7%B3%BB%E7%BB%9F%E3%80%81%E5%88%9B%E4%BD%9C%E5%B7%A5%E4%BD%9C%E6%B5%81%E4%B8%8E%E6%9C%AA%E6%9D%A5%E8%B6%8B%E5%8A%BF.md#L1)，来源许可：GPL-3.0。

<a id="k65e392c772d8"></a>

## AIGC 时代的自进化 Agent 是什么？

自进化 Agent 是指不仅能完成任务，还能从任务执行、用户反馈、工具失败、历史对话和环境状态中沉淀经验，并把这些经验转化为可复用的记忆、技能、策略或评测样本的 Agent 系统。

可以用一个闭环理解：

$$
\text{Task} \rightarrow \text{Trace} \rightarrow \text{Reflection} \rightarrow \text{Memory / Skill / Policy} \rightarrow \text{Curator} \rightarrow \text{Better Task Execution}
$$

普通 Agent 关注“当前任务能不能做完”；自进化 Agent 进一步关注：

- 做完后哪些经验值得保留？
- 哪些失败应转成回归样本？
- 哪些重复流程应沉淀为 Skill？
- 哪些旧 Skill 已经过期或互相重复？
- 哪些长期记忆可能污染未来任务？
- 哪些工具调用模式应被 guardrail 约束？

Hermes Agent 这类项目的启发在于：Agent 不只是一次性执行器，而可以成为长期运行的个人/团队智能工作台，持续维护自己的技能库、记忆库、会话历史和工具生态。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/09_%E8%87%AA%E8%BF%9B%E5%8C%96Agent%E4%B8%8E%E5%A4%9A%E5%B9%B3%E5%8F%B0%E8%BF%90%E8%A1%8C%E6%97%B6%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L47)，来源许可：GPL-3.0。

<a id="k0324f7193d80"></a>

## AI视频经典的工作流有哪些？

本问答Rocky将根据AI视频领域的发展阶段持续更新，将最有价值的AI视频工作流分享给大家：

1. 文生视频：可以使用Sora、可灵、CogVideoX + LoRA + ControlNet组成的工作流。
2. 图生视频：可以使用SVD + LoRA + ControlNet组成的工作流。
3. 视频编辑（视频生视频）：AnimateDiff + LoRA + ControlNet组成的工作流。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E8%A7%86%E9%A2%91%E5%9F%BA%E7%A1%80/01_AI%E8%A7%86%E9%A2%91%E6%A0%B8%E5%BF%83%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86.md#L140)，来源许可：GPL-3.0。

<a id="kd5b8c88fe04f"></a>

## Atropos / RL 环境对工具调用 Agent 有什么启发？

Hermes Agent 的 Atropos 环境体现了一种重要趋势：把工具调用 Agent 放进可交互环境中做 rollout、评分和训练，而不是只训练单轮问答。

通用架构：

```text
Dataset Item -> Prompt -> Agent Loop -> Tool Calls -> Environment State -> Reward -> Training / Eval
```

关键组件：

- BaseEnv：管理 worker、server、日志和评测。
- Agent Loop：多轮调用模型和工具。
- ToolContext：让 reward function 访问同一个 sandbox 状态。
- Terminal / Browser / File 工具：提供真实交互能力。
- Reward Function：运行测试、检查文件、比较状态。
- Tool Call Parser：把模型原始输出转成结构化工具调用。

启发：

- Agent 训练必须关注工具执行后的状态。
- Reward 不应只看文本答案。
- 同一个 task_id 要绑定同一个 sandbox。
- 评测环境和训练环境最好共用底层工具抽象。
- 多模型 tool calling 格式不统一，需要解析层。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/09_%E8%87%AA%E8%BF%9B%E5%8C%96Agent%E4%B8%8E%E5%A4%9A%E5%B9%B3%E5%8F%B0%E8%BF%90%E8%A1%8C%E6%97%B6%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L631)，来源许可：GPL-3.0。

<a id="ke5f9b425c0ac"></a>

## CLAUDE.md / AGENTS.md 这类项目记忆文件有什么作用？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

本节从代码仓库工程实践解释项目记忆文件；项目记忆作为上下文工程模式、与 Skill / Memory / RAG 的关系，见 [05_Agent记忆与上下文工程高频考点.md](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/05_Agent记忆与上下文工程高频考点.md)。

它们是给 Agent 看的项目说明书。

常见内容：

- 项目简介。
- 目录结构。
- 构建命令。
- 测试命令。
- 代码规范。
- 常见坑。
- 提交流程。
- 禁止操作。
- 重要设计约束。

价值：

- 减少每次都重新探索项目。
- 保持团队规范一致。
- 降低工具误用。
- 让 Agent 更快进入有效工作状态。

区别：

- `AGENTS.md` 更偏开放格式和多 Agent 通用约定。
- `CLAUDE.md` 是特定生态中的项目/用户记忆文件。

本质上，二者都属于项目级 Agent 指令与记忆入口：让 Agent 在进入仓库前知道“这里如何构建、如何测试、哪些边界不能碰、团队偏好是什么”。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/02_%E7%BC%96%E7%A0%81Agent%E4%B8%8EAgentOS%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L366)，来源许可：GPL-3.0。

<a id="kf278e4de3223"></a>

## CLI Agent 和 IDE Agent 的体验差异是什么？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

| 维度 | CLI | IDE |
| --- | --- | --- |
| 优势 | 接近真实开发环境，命令强 | 有编辑器上下文和可视化 |
| 上下文 | cwd、Git、Shell、文件系统 | 打开文件、选区、诊断、项目树 |
| 展示 | 文本流、命令输出 | diff、inline edit、问题面板 |
| 用户 | 终端熟练开发者 | 日常 IDE 开发者 |
| 风险 | 命令副作用更强 | 编辑器状态同步复杂 |

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/02_%E7%BC%96%E7%A0%81Agent%E4%B8%8EAgentOS%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L591)，来源许可：GPL-3.0。

<a id="k12791948ffd8"></a>

## CLI、TUI、IM、邮件、Webhook 等入口如何统一到同一个 Agent Runtime？

关键是把“入口适配”和“Agent 执行”解耦。

推荐分层：

1. **Platform Adapter**

   负责接入具体平台，例如 Slack、Telegram、Email、API Server、Webhook。

2. **Message Normalizer**

   把平台消息转成统一事件格式：user_id、channel_id、thread_id、text、attachments、reply_to、timestamp。

3. **Session Router**

   根据用户、频道、工作区、任务类型路由到正确 session。

4. **Command Registry**

   统一 slash command，避免 CLI、IM、TUI 各自维护一套命令。

5. **Runtime Adapter**

   调用 Agent Runtime，处理流式响应、工具调用、权限请求和中断。

6. **Delivery Layer**

   把结果转换回平台格式，例如 Markdown、图片、文件、语音、分片消息。

工程要点：

- 入口层不直接拼 prompt。
- session id 不能只用用户名，必须包含平台和上下文。
- 平台支持能力不同，需要 feature negotiation。
- 高风险工具审批要能从远程平台回传。
- 消息发送失败要可重试和去重。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/09_%E8%87%AA%E8%BF%9B%E5%8C%96Agent%E4%B8%8E%E5%A4%9A%E5%B9%B3%E5%8F%B0%E8%BF%90%E8%A1%8C%E6%97%B6%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L173)，来源许可：GPL-3.0。

<a id="k9909f3e120ca"></a>

## Context Engine 的 ingest / assemble / compact / after-turn 生命周期如何理解？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

Context Engine 是 AgentOS 中负责“上下文生命周期”的模块。它决定模型每一轮看到什么、历史如何压缩、长期记忆如何更新。

典型生命周期：

1. **ingest**

   摄取新信息，例如用户消息、工具结果、文件变化、网页内容、语音转写、外部事件。

2. **assemble**

   为当前 turn 拼装上下文，包括 system prompt、开发者指令、项目规则、session 摘要、相关记忆、检索片段、打开文件、当前任务状态。

3. **compact**

   当上下文接近 token 预算时，把历史压缩成结构化摘要，保留目标、约束、已完成动作、重要文件、失败尝试、下一步。

4. **after-turn**

   模型回复和工具调用结束后，更新任务状态、写入记忆、保存 trace、触发后处理 hook。

好的 Context Engine 要处理：

- prompt authority：系统指令、项目规则、用户消息、工具输出的优先级不能混乱。
- token budget：核心目标、当前文件、错误日志优先，低价值历史可压缩。
- provenance：记忆和检索片段要保留来源，避免把不可信内容当系统指令。
- phase awareness：探索、实现、验证、总结阶段需要不同上下文。
- subagent context：子 Agent 只拿必要上下文，结束后返回摘要而不是倾倒全部历史。

一句话：Context Engine 是 Agent 的“工作记忆调度器”，比简单 RAG 更关注 turn 生命周期和指令优先级。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/02_%E7%BC%96%E7%A0%81Agent%E4%B8%8EAgentOS%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L1063)，来源许可：GPL-3.0。

<a id="k865752e7c9b4"></a>

## Crew / Team 型 Agent 适合什么场景？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

Crew / Team 型 Agent 会给不同 Agent 分配固定角色，例如：

- Planner：制定计划。
- Researcher：检索资料。
- Engineer：实现代码。
- Reviewer：审查质量。
- Tester：运行测试。
- Writer：整理文档。

适合场景：

- 角色边界清晰。
- 任务可拆分。
- 每个角色需要不同工具或提示词。
- 输出需要多轮审查。
- 可以接受更高延迟和成本。

不适合：

- 简单问答。
- 强实时交互。
- 高度耦合、难以拆分的任务。
- 工具权限难以隔离的任务。

工程建议：

- 明确每个 Agent 的输入、输出和停止条件。
- 给每个 Agent 独立上下文，避免互相污染。
- 由 Supervisor 汇总而不是让所有 Agent 共享完整历史。
- 对写文件、发消息、执行命令等副作用操作设置单一责任人。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/03_Agent%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81%E7%BC%96%E6%8E%92%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L543)，来源许可：GPL-3.0。

<a id="kf36ac84a925c"></a>

## CrewAI、AutoGen、Google ADK、LlamaIndex Agent 如何对比？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

| 框架 | 核心定位 | 适合场景 |
| --- | --- | --- |
| CrewAI | Crew + Agent + Task + Process | 角色分工明确的业务流程 |
| AutoGen | 多 Agent 对话和协作 | 研究型多 Agent、代码协作、模拟讨论 |
| Google ADK | Agent 开发工具包，支持 A2A | Google/Gemini 生态、多 Agent 服务化 |
| LlamaIndex Agent | 数据连接和知识增强 | RAG Agent、企业知识库、文档问答 |
| LangGraph | 有状态图和持久执行 | 复杂工作流、长期任务、human-in-loop |
| OpenAI Agents SDK | 通用 Agent SDK | 工具调用、handoff、guardrail、tracing |

选择建议：

- 数据密集型：LlamaIndex。
- 状态复杂：LangGraph。
- 多角色协作：CrewAI/AutoGen。
- 标准 SDK 和工具生态：OpenAI Agents SDK。
- Google 生态和 A2A：Google ADK。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/01_AIGC%E6%97%B6%E4%BB%A3AI%20Agent%E5%9F%BA%E7%A1%80%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L497)，来源许可：GPL-3.0。

<a id="k683e230eaf08"></a>

## Dify、Coze、Copilot Studio、Vertex AI Agent Builder、Bedrock Agents 适合什么场景？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

| 平台 | 更适合场景 | 注意点 |
| --- | --- | --- |
| Dify | 私有化、知识库问答、工作流、快速 PoC | 复杂代码 Agent 和强定制需二次开发 |
| Coze | 面向业务和内容场景的 Bot / Agent 快速搭建 | 企业深度治理取决于部署和权限体系 |
| Copilot Studio | 微软 365 / Dynamics / Power Platform 生态 | 适合已在微软生态的企业 |
| Vertex AI Agent Builder | Google Cloud 数据和搜索生态 | 适合 GCP 企业用户 |
| Bedrock Agents | AWS 生态、企业托管 Agent | 适合 AWS 上的业务系统集成 |

选型时要问：

- 数据是否允许进入云平台。
- 是否支持私有化。
- 是否能接企业 IAM。
- 是否支持现有工具和知识库。
- 是否支持评测、trace 和审计。
- 低代码能力能否覆盖业务复杂度。
- 是否存在平台锁定风险。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/07_%E4%BC%81%E4%B8%9A%E7%BA%A7Agent%E5%B9%B3%E5%8F%B0%E4%B8%8E%E4%BA%A7%E5%93%81%E8%90%BD%E5%9C%B0%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L844)，来源许可：GPL-3.0。

<a id="kec34fea6c10c"></a>

## Environment Simulator / Sandbox 的核心价值是什么？

Environment Simulator / Sandbox 的价值是让 Agent 在可控环境中执行真实动作，但不会伤害真实系统。

它解决四个问题：

1. **可复现**

   每次评测从同一个初始状态开始。

2. **可隔离**

   文件、数据库、浏览器、网络和密钥不会污染生产环境。

3. **可注入异常**

   可以模拟 API 超时、权限不足、页面变化、工具失败和用户反悔。

4. **可判分**

   评测结束后可以比较数据库、文件 diff、页面状态或 artifact。

不同场景的环境设计不同：

| 场景 | 环境模拟重点 |
| --- | --- |
| 编码 Agent | Git repo、base commit、依赖环境、测试命令、Docker 沙箱 |
| 浏览器 Agent | 页面 DOM、登录态、表单、按钮、弹窗、网络响应 |
| 客服 Agent | 用户模拟器、订单数据库、政策文档、业务 API |
| 数据分析 Agent | 数据库快照、查询权限、指标口径、报表模板 |
| 多 Agent | Agent Card、消息总线、任务状态、handoff artifact |

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/08_Agent_Harness_Engineering%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L229)，来源许可：GPL-3.0。

<a id="k263871ef370f"></a>

## Function Calling 为什么还不等于完整 Agent？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

Function Calling 只解决“如何调用一个函数”这一局部问题。完整 Agent 还需要：

- 目标理解。
- 任务分解。
- 多步规划。
- 多工具选择。
- 工具结果解释。
- 失败恢复。
- 记忆和上下文管理。
- 权限审批。
- 长任务状态。
- 人机协作。
- 可观测性和评测。

对比：

| 能力 | Function Calling | Agent |
| --- | --- | --- |
| 单次工具调用 | 支持 | 支持 |
| 多步循环 | 不一定 | 核心能力 |
| 任务状态 | 通常无 | 必须有 |
| 记忆 | 不负责 | 常见核心模块 |
| 规划 | 不负责 | 常见核心模块 |
| 权限和审计 | 依赖宿主 | 必须系统化 |
| 自主性 | 低到中 | 中到高 |

一句话：Function Calling 是 Agent 的工具接口，Agent 是围绕目标、状态、工具、记忆和反馈构建的行动系统。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/04_MCP%E4%B8%8EA2A%E5%8D%8F%E8%AE%AE%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L264)，来源许可：GPL-3.0。

<a id="k037fe4cfa904"></a>

## Function Calling、MCP 和 Agent 分别负责什么？

Function Calling 让模型用结构化参数表达“想调用哪个函数”；MCP 负责 Host、Client 和 Server 之间的上下文交换，可提供 Resources、Prompts、Tools 等原语；Agent 负责结合目标和状态决定下一步做什么。

它们不在同一个层次，也不能互相替代。

如果工具只服务于当前应用，直接注册本地函数通常更简单。如果同一套能力要被多个 Agent、IDE 或模型客户端复用，再评估 MCP。采用 MCP 后，权限、参数校验和副作用治理仍然要在业务侧完成。

![Function Calling 完整调用链路：模型生成调用意图，业务侧执行工具](https://oss.javaguide.cn/github/javaguide/ai/llm/structured-output-function-calling-function-calling-pipeline.png)

这部分容易被追问，建议配合 [大模型结构化输出详解](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/llm-basis/structured-output-function-calling.md) 和 [MCP 协议详解](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/agent/mcp.md) 一起复习。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/interview-questions/agent-project-interview-guide.md#L215)，来源许可：Apache-2.0。

<a id="ka164a6e4b092"></a>

## Function Calling、MCP、A2A 分别解决什么问题？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

| 技术 | 主要对象 | 核心问题 | 典型例子 |
| --- | --- | --- | --- |
| Function Calling | 模型与应用内函数 | 模型如何输出结构化函数名和参数 | 查询天气、调用订单 API |
| MCP | Agent 应用与工具/数据源 | 如何用标准方式接入外部工具、资源和上下文 | GitHub、数据库、文件系统、浏览器、知识库 |
| A2A | Agent 与 Agent | 独立 Agent 服务如何发现能力、发送任务、返回结果 | 研究 Agent 调用财务分析 Agent |

三者之间不是替代关系，而是递进关系：

1. Function Calling 让模型能“调用函数”。
2. MCP 让工具和上下文能“以标准服务形式被调用”。
3. A2A 让一个 Agent 能“把任务交给另一个 Agent 服务”。

一个企业级 Agent 系统中，三者经常同时存在：

- 用 Function Calling 调应用内业务函数。
- 用 MCP 接企业知识库、数据库、代码仓库和浏览器。
- 用 A2A 调用其他部门或其他平台提供的专用 Agent。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/04_MCP%E4%B8%8EA2A%E5%8D%8F%E8%AE%AE%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L73)，来源许可：GPL-3.0。

<a id="k9e481d0d45d7"></a>

## Function Calling和Tool Calling的执行流程是什么？模型是如何判断需要调用工具，以及生成对应参数的？

**回答：**

Function Calling 和 Tool Calling 的核心机制相同：服务端向模型提供工具名称、描述、参数 JSON Schema 和使用约束；模型根据用户目标与当前上下文决定直接回答，或输出结构化的工具调用意图。真正执行函数的是应用侧运行时，不是模型本身。

标准流程是：

1. 应用注册当前允许的工具及 Schema；
2. 模型读取用户问题、系统规则、工具描述和历史 Observation，产生文本回复或 `tool_calls`；
3. 应用解析调用名和参数，进行 Schema、类型、权限、资源状态、预算和安全策略校验；
4. 合法调用进入工具运行时，工具返回结构化结果或结构化错误；
5. 应用把结果以工具消息写回上下文；
6. 模型根据 Observation 决定继续调用、修正参数、请求用户补充信息或生成最终答案；
7. 外部验证器检查任务是否真的完成。

模型并不是通过执行代码“判断”是否需要工具，而是在训练和上下文条件下预测工具调用或普通文本的概率。它是否选对工具取决于工具描述、候选集合、模型能力、当前状态和示例。参数合法不等于业务正确，所以必须由服务端再次校验；有副作用的调用还需要幂等键、状态回读和人工审批。Function/Tool Calling 是协议和输出形态，不自动等于完整 Agent。

<a id="bilibili-ai-agent-20260818-q12"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%93%94%E5%93%A9%E5%93%94%E5%93%A9%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L198)，来源许可：GPL-3.0。

<a id="k3248479f6c6b"></a>

## Graph-of-Thought 为什么比树结构更灵活？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐ (3/5)**

树结构假设每个 thought 只有一个父节点，分支之间相对独立。但真实复杂任务中，经常需要：

- 合并两个分支的信息。
- 对同一个中间结论反复修正。
- 从多个证据共同支持一个判断。
- 在图中形成依赖关系，而不是简单层级。

Graph-of-Thought 把 thought 看成图节点，把推理关系看成边。这样可以支持：

- aggregation：聚合多个 thought。
- refinement：迭代改进某个 thought。
- branching：生成多个候选方向。
- scoring：对节点或路径打分。
- pruning：删除低质量分支。

适合场景：

- 研究综述。
- 多文档问答。
- 复杂决策分析。
- 多 Agent 辩论结果聚合。
- 代码架构方案比较。

代价是工程复杂度更高，需要维护图状态、依赖关系、节点评分和终止条件。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/03_Agent%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81%E7%BC%96%E6%8E%92%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L407)，来源许可：GPL-3.0。

<a id="kfc508eaa2668"></a>

## GUI Agent 如何实现界面理解与精确定位？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

GUI Agent 对定位的要求比通用检测更高：检测框偏几个像素通常仍可接受，点击一个几十像素见方的图标时偏出图标即为失败。高分辨率截图中的小图标对视觉分辨率和 token 预算的要求也比自然图像更高。坐标采用归一化、千分制还是绝对像素，见 [5.4.6.1](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E5%A4%9A%E6%A8%A1%E6%80%81%E5%9F%BA%E7%A1%80%EF%BC%88%E7%B2%BE%E5%8D%8E%E7%89%88%EF%BC%89/4_AI多模态主流模型核心技术高频考点.md#q5-4-6-1)。界面理解有结构化辅助和纯视觉两条路线：

1. **结构化辅助。** 这条路线读取操作系统提供的控件树（accessibility tree）或网页 DOM，获得控件列表。Set-of-Mark 在截图上叠加带编号的标记框，把预测坐标改为选择编号[22]。这条路线在工程上稳定，但依赖系统接口，遇到 canvas 渲染和游戏界面时拿不到控件树，路线随之失效。

2. **纯视觉。** 这条路线只使用截图。CogAgent（CVPR 2024）有 18B 参数，高分辨率分支支持 $`1120\times 1120`$ 的输入，说明只依靠截图也能完成 GUI 任务[23]。OS-Atlas 开源了跨平台的 GUI 定位语料，包含超过 1300 万个界面元素[24]。UI-TARS 只以截图为输入，把感知、定位和动作生成统一进一个端到端模型[25]。能拿到控件树时结构化路线仍然更稳，纯视觉路线覆盖拿不到控件树的界面。

动作空间需要覆盖点击、输入、滚动、长按和组合键，桌面端与移动端的动作并不相同。训练数据是截图与动作组成的轨迹，来源包括人工录制、规则合成以及模型自主探索后筛选，标注成本高于普通图文对。

> **面试速答**：GUI 点击偏出图标即为失败，定位要求比通用检测高。一条路线读取控件树或 DOM，或用 Set-of-Mark 把坐标改为编号，但 canvas 和游戏界面会失效；另一条只看截图，CogAgent 用高分辨率分支证明可行，OS-Atlas 补充定位数据，UI-TARS 把感知和动作放进一个模型。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E5%A4%9A%E6%A8%A1%E6%80%81%E5%9F%BA%E7%A1%80%EF%BC%88%E7%B2%BE%E5%8D%8E%E7%89%88%EF%BC%89/6_AI%E5%A4%9A%E6%A8%A1%E6%80%81%E4%B8%8B%E6%B8%B8%E5%BA%94%E7%94%A8%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L359)，来源许可：GPL-3.0。

<a id="k0ab6ea059b6d"></a>

## Harness Engineering

相关内容：[《Harness Engineering：六层检查框架、上下文管理与工程实践》](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/agent/harness-engineering.md)

Harness Engineering 把注意力放到模型外部的执行环境，包括任务管理、上下文供给、工具反馈、验证和错误恢复。相关问题通常要求把这些抽象概念落到具体组件。

常见面试题：

- Harness Engineering 是什么？它和 Prompt Engineering、Context Engineering 有什么关系？
- 为什么说 Agent = Model + Harness？
- JavaGuide AI Agent 专题归纳的 Harness 六层检查框架分别解决什么问题？
- 模型能力升级后，Harness 里的某些机制为什么需要重新验证？
- 上下文污染、代码熵积累、工具调用可靠性分别怎么治理？
- Agent 工程里为什么需要评测器、验证器和任务状态管理？
- 一线团队做 Agent 工程化时，共同遇到的难点是什么？

![Harness 和 Prompt/Context Engineering 的关系](https://oss.javaguide.cn/github/javaguide/ai/harness/harness-engineering-layers-arch.png)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/interview-questions/agent-interview-questions.md#L98)，来源许可：Apache-2.0。

<a id="ka9f5a47245ed"></a>

## Harness 如何服务线上 Shadow Mode 和灰度发布？

**Shadow Mode** 指新 Agent 旁路运行，不对真实用户产生副作用。它可以用真实流量评估新版本，但不会真正执行写操作。

典型设计：

- 线上请求同时发送给旧版本和新版本。
- 新版本工具调用进入 mock 或 dry-run。
- 比较两者输出、工具计划、成本和安全风险。
- 高风险动作只记录，不执行。
- 抽样人工复核差异。

**灰度发布** 则允许新版本服务一小部分真实用户或低风险任务。

Harness 在灰度中负责：

- 选择灰度任务。
- 记录版本组合。
- 检查 guardrail 命中。
- 对异常 trace 自动标注。
- 触发自动回滚。
- 将灰度失败回流到评测集。

面试中可以说：Shadow Mode 解决“能不能观察真实分布”，Canary 解决“能不能小规模承担真实责任”。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/08_Agent_Harness_Engineering%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L643)，来源许可：GPL-3.0。

<a id="k76a8c40faab8"></a>

## Harness 通常需要管理哪些内容？Workspace 和抽象文件系统分别起什么作用？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

运行 Harness 管理模型调用、工具集合、权限、上下文、任务状态、循环预算、工作环境、错误处理和验收。Workspace 为一次任务或一个项目提供文件、产物、配置及执行位置；它便于组织状态，但目录名称本身不是安全隔离机制。

抽象文件系统用统一的读、写、列目录接口连接本地磁盘、对象存储或远端容器。它隐藏的是后端差异，仍需明确定义原子写、版本、锁、权限与路径语义。不能假设对象存储的重命名行为与本地文件系统完全相同。

实现时对路径规范化并检查边界，防止 `..`、符号链接或挂载点绕过限制；给工具挂载最小范围，敏感配置独立管理。文件快照有助于恢复本地改动，外部 API 的业务副作用则要通过幂等、补偿或人工核对处理，不能靠回滚工作目录撤销。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/02_%E7%BC%96%E7%A0%81Agent%E4%B8%8EAgentOS%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L328)，来源许可：GPL-3.0。

<a id="k609aa41ab92f"></a>

## Harness、Benchmark、Eval、AgentOps 有什么区别？

| 概念 | 核心含义 | 例子 |
| --- | --- | --- |
| Benchmark | 标准化任务集和指标 | SWE-bench、WebArena、OSWorld、GAIA、tau-bench |
| Eval | 一次评估过程或评估配置 | 在某个数据集上评估新 prompt、新模型、新工具 |
| Harness | 执行 eval 的工程框架 | 准备环境、运行 Agent、收集 trace、判分、生成报告 |
| AgentOps | Agent 上线后的运营治理体系 | tracing、监控、灰度、回滚、事故响应、失败回流 |

关系可以这样理解：

- Benchmark 提供“考卷”。
- Eval 定义“这次考试怎么考”。
- Harness 提供“考场、监考、阅卷和成绩单”。
- AgentOps 把成绩用于“发布、灰度、回滚和持续改进”。

面试中要避免把 Benchmark 等同于 Harness。公开 Benchmark 只是外部参考；企业真正需要的是能跑自家工具、自家流程、自家权限和自家数据的 Harness。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/08_Agent_Harness_Engineering%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L70)，来源许可：GPL-3.0。

<a id="k8c331d56114c"></a>

## Hooks 在编码 Agent 中有什么价值？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

Hooks 是在 Agent 生命周期关键点插入自定义逻辑。

常见类型：

- session_start：会话开始时加载上下文。
- pre_tool：工具调用前做安全检查。
- post_tool：工具调用后记录结果或更新状态。
- pre_compact：压缩前保存重要信息。
- post_compact：压缩后验证摘要。
- post_sampling：模型输出后触发文档更新或检查。

价值：

- 安全：阻止危险工具调用。
- 审计：记录所有关键动作。
- 自动化：任务结束后更新文档、生成报告。
- 质量：运行格式化、lint、测试。
- 记忆：提取长期偏好和项目知识。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/02_%E7%BC%96%E7%A0%81Agent%E4%B8%8EAgentOS%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L526)，来源许可：GPL-3.0。

<a id="k6db12f16a573"></a>

## Hooks、Cron/Webhook、Background Task 在 AgentOS 中分别解决什么问题？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

三者都和自动化有关，但职责不同：

| 机制 | 核心作用 | 典型场景 |
| --- | --- | --- |
| Hooks | 在 Agent 生命周期关键点插入逻辑 | 消息预处理、工具调用前审批、压缩前保存、会话结束归档 |
| Cron/Webhook | 从时间或外部系统触发 Agent | 每日总结、CI 失败通知、工单事件、监控告警 |
| Background Task | 追踪异步长任务状态 | 长时间构建、代码生成、浏览器任务、媒体处理、远程子任务 |

Hooks 常见触发点：

- message received / preprocessed / sent。
- session start / end。
- before prompt build。
- before model call。
- before / after tool call。
- before / after compaction。
- agent end。
- gateway startup / shutdown。

Background Task 常见状态：

```math
\text{queued} \rightarrow \text{running} \rightarrow \text{succeeded / failed / timed\_out / cancelled / lost}
```
设计要点：

- Hooks 必须可观测，失败策略要明确，是阻断、跳过还是降级。
- Cron/Webhook 触发的任务要绑定 session 或创建独立 session。
- Background Task 是活动账本，不一定是调度器本身。
- 任务完成通知要支持直接推送，也要支持离线后排队等待用户回来。
- 自动化能力要受 Tool Policy 和权限模型约束。

面试中可以说：Hooks 解决“生命周期扩展”，Cron/Webhook 解决“外部触发”，Background Task 解决“异步状态追踪”。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/02_%E7%BC%96%E7%A0%81Agent%E4%B8%8EAgentOS%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L1097)，来源许可：GPL-3.0。

<a id="k4d7b46e4e640"></a>

## IDE Bridge 通常需要传递哪些信息？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

IDE Bridge 需要双向通信：

**IDE 到 Agent：**

- 当前 workspace。
- 打开的文件。
- 光标位置和选区。
- 诊断信息。
- 用户点击的文件引用。
- IDE 配置和语言服务状态。

**Agent 到 IDE：**

- 打开文件。
- 展示 diff。
- 定位行号。
- 请求用户确认。
- 显示进度和通知。
- 应用编辑。

安全要点：

- Bridge 连接需要身份认证。
- 本地端口不应被任意网页调用。
- 远程控制要有 trusted device 或 token。
- 权限回调必须可审计。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/02_%E7%BC%96%E7%A0%81Agent%E4%B8%8EAgentOS%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L607)，来源许可：GPL-3.0。

<a id="k2c3049ab3213"></a>

## LangGraph 为什么适合复杂 Agent 工作流？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

LangGraph 的核心是把 Agent 工作流表示为有状态图：

- 节点是 LLM、工具、判断逻辑或子流程。
- 边表示控制流。
- State 保存中间状态。
- Checkpointer 支持持久化和恢复。
- Human-in-the-loop 可以插入审批和修改。

适合场景：

- 多步骤业务流程。
- 长时间运行任务。
- 需要失败恢复。
- 需要可视化和可观测。
- 需要人工审批。
- 需要多个 Agent/工具协作。

与普通链式调用相比，LangGraph 更像“Agent 工作流引擎”，而不是简单 prompt pipeline。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/01_AIGC%E6%97%B6%E4%BB%A3AI%20Agent%E5%9F%BA%E7%A1%80%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L474)，来源许可：GPL-3.0。

<a id="k47c524abbd72"></a>

## LangGraph 的 State、Node、Edge 分别是什么？怎么配合完成流程编排？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

LangGraph 的 State 表达运行过程中各节点共享的数据契约；Node 是处理状态并返回更新的函数；Edge 决定下一步转移，可为固定边或根据状态选择的条件边。图由入口开始，沿可用路径执行，直到结束或暂停。

例如 State 保存消息、意图、槽位、确认状态和工具结果；意图节点输出分类；条件边把请求分到知识检索或预约子图；预约子图在字段完整且确认有效时进入提交。并行节点修改同一字段时，应定义合适的 reducer，不能默认并发写会安全合并。

持久化需要配置 checkpointer 和稳定的线程标识；暂停恢复还要按框架契约提供恢复输入。Node 应将可重放计算与业务副作用分开，用户身份由可信入口注入。State 不是把所有工具原始输出无限追加的大字典，应保留必要值与大对象引用。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/03_Agent%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81%E7%BC%96%E6%8E%92%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L647)，来源许可：GPL-3.0。

<a id="k71c14ba3b8ec"></a>

## LATS / MCTS-style Agent 的核心思想是什么？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐ (3/5)**

LATS 可以理解为把语言模型 Agent 和树搜索结合起来。它通常包含：

- 生成候选行动。
- 执行动作并获得环境反馈。
- 对状态进行价值评估。
- 根据搜索策略选择下一步。
- 从成功或失败轨迹中反思学习。

MCTS-style Agent 的关键不是只让模型“想一步”，而是让系统在多条行动轨迹中搜索更优路径。

典型流程：

1. Selection：选择当前最有潜力的节点。
2. Expansion：扩展多个候选 thought/action。
3. Simulation：模拟或执行后续步骤。
4. Evaluation：评估结果价值。
5. Backpropagation：把价值反馈给上层节点。

适合：

- Web 交互任务。
- 游戏或环境探索。
- 复杂工具链任务。
- 需要试错和回溯的决策。

局限：

- token 和工具调用成本高。
- 需要可靠的 value function。
- 搜索树可能爆炸。
- 对实时性要求高的产品不友好。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/03_Agent%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81%E7%BC%96%E6%8E%92%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L436)，来源许可：GPL-3.0。

<a id="k3b7dc702db88"></a>

## MCP Server 的工具粒度应该如何划分？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

工具粒度要在“过细”和“过粗”之间平衡。

过细的问题：

- 模型需要多次调用才能完成简单任务。
- 调用链变长，延迟和失败率上升。
- 模型容易选错相近工具。

过粗的问题：

- 工具像黑箱，模型难以控制。
- 参数复杂，Schema 难以写清。
- 权限难以精细化。
- 副作用风险集中。

推荐原则：

- 一个 Tool 对应一个清晰业务意图。
- 读写分离，例如 `search_issues` 和 `create_issue` 分开。
- 查询类工具支持过滤、分页和字段选择。
- 修改类工具支持 dry-run 或 preview。
- 高风险工具需要显式确认字段，例如 `confirm=true` 不能由模型自动填充。
- 对频繁组合使用的步骤，可以封装为安全的复合工具。

例如数据库 MCP 不应该只暴露 `execute_sql`，而应优先暴露 `list_tables`、`describe_table`、`query_readonly`、`run_approved_report` 等更可控工具。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/04_MCP%E4%B8%8EA2A%E5%8D%8F%E8%AE%AE%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L439)，来源许可：GPL-3.0。

<a id="k598dde43c202"></a>

## MCP 与 Agent Skills

相关内容：[《什么是 Model Context Protocol (MCP)？和 Function Calling、Agent 什么关系？》](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/agent/mcp.md)、[《Agent Skills 是什么？和 Prompt、MCP 到底差在哪？》](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/agent/skills.md)

Function Calling、MCP 和 Skills 位于不同环节：模型需要表达调用意图，宿主需要接入工具，Agent 还要加载完成任务所需的流程与资料。这组题经常继续追问权限、参数校验、超时和审计。

常见面试题：

- MCP 解决什么问题？为什么常被类比成 AI 领域的 USB-C？
- MCP Client、MCP Server、Host 分别是什么？
- MCP 的 Tools、Resources、Prompts 分别解决什么问题？
- MCP 和 Function Calling 有什么区别？
- 生产级 MCP Server 要做哪些安全治理？
- Agent Skills 是什么？它和 Prompt、MCP、Function Calling 的边界是什么？
- Skills 为什么要延迟加载？
- Skill 路由怎么做？为什么它和 RAG 相似但目标不同？
- 写一个 `SKILL.md` 最容易踩哪些坑？

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/interview-questions/agent-interview-questions.md#L80)，来源许可：Apache-2.0。

<a id="k7d8103566f3c"></a>

## MCP 与普通 API 的差异

**回答：**

MCP 是连接模型应用与外部能力的一套协议约定。普通 API 可以提供同样的业务功能；差异在于是否统一了能力发现、消息结构、会话生命周期和调用方式。

MCP 解决的是互操作问题。它本身不是规划算法，也不会自动保证工具选择正确、业务权限合理或执行结果可信。

<a id="baidu-aigc-multimodal-agent-20260922-20260924-r2-q5-1"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%99%BE%E5%BA%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1855)，来源许可：GPL-3.0。

<a id="k229ad699dcdb"></a>

## MCP 与普通 API 调用有什么区别

**回答：**

普通 API 往往由业务系统自行定义路径、字段、鉴权和文档；模型应用接入时需要编写适配代码，并向模型提供工具描述。MCP 在这些业务能力之上约定了一套面向模型应用的交互形式。

典型架构中，Host 是承载模型与交互的应用，Client 是其连接某个 MCP Server 的协议组件，Server 暴露 Tools、Resources 或 Prompts 等能力。具体支持哪些能力，需要在初始化时协商，不能假定所有服务器都实现全部特性。

| 维度 | 普通业务 API | MCP |
| --- | --- | --- |
| 接入描述 | 常见为接口文档或 OpenAPI 等规范 | 约定能力发现及对应消息结构 |
| 工具发现 | 由业务自行设计 | 可通过 `tools/list` 列举工具及输入 schema |
| 工具调用 | 按具体接口协议调用 | 可通过 `tools/call` 发起工具调用 |
| 传输 | HTTP、RPC 等多种形式 | 以所实现协议版本支持的传输为准，如 stdio、Streamable HTTP |
| 业务实现 | 数据库或实际服务 | 可以包装现有 API，也可以直接实现能力 |

MCP 使用 JSON-RPC 2.0 消息，并不等于“HTTP 接口加一层提示词”。接入方仍要处理鉴权、错误、超时和资源生命周期；远程 HTTP 与本地进程连接也不能套用同一套安全假设。

从调用生命周期看，模型建议使用某个工具后，Host 先进行权限与参数检查，再由对应 Client 把请求发给 Server，Server 可能继续调用已有业务 API。Server 返回内容后，Host 需要关联请求、解释错误并把可信的结果送回模型。MCP 协议的请求 ID 用于匹配响应，业务任务 ID 用于查询长期任务，业务幂等键用于去重，这三个标识承担不同职责。

协议层错误与工具执行错误也应区分。以 MCP 2025-06-18 的 Tools 规范为例，工具执行错误可以在调用结果里用 `isError` 表达，并提供模型能够处理的说明；工具不存在等协议问题通过相应协议错误返回。`readOnlyHint`、`destructiveHint` 等 annotations 是提示信息，不能代替服务端鉴权，也不能把不可信 Server 的声明直接当作授权依据。版本升级时应重新核对兼容性，不能把一个版本的行为概括为永久保证。

<a id="baidu-aigc-multimodal-agent-20260922-20260924-r2-q5-2"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%99%BE%E5%BA%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1864)，来源许可：GPL-3.0。

<a id="kd9323abfdfad"></a>

## MCP 在编码 Agent 中通常如何使用？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

本节只说明 MCP 在编码场景中的工具接入方式；MCP 协议结构、传输、能力协商和安全设计，见 [04_MCP与A2A协议高频考点.md](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/04_MCP与A2A协议高频考点.md)。

编码 Agent 可通过 MCP 接入：

- GitHub/GitLab。
- Issue/PR 系统。
- 数据库。
- 文档平台。
- 浏览器自动化。
- 云服务。
- 内部代码搜索。
- 企业知识库。

优势：

- 工具连接器复用。
- 本地和远程工具统一协议。
- Server 可独立维护。
- 支持资源、提示模板和工具发现。

风险：

- MCP Server 本身可能暴露敏感能力。
- 工具返回内容可能包含 prompt injection。
- 远程 MCP 必须做认证和授权。
- 工具描述要清楚标注副作用。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/02_%E7%BC%96%E7%A0%81Agent%E4%B8%8EAgentOS%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L658)，来源许可：GPL-3.0。

<a id="k3493536f1e85"></a>

## MCP 连接与能力协商有哪些基本要素？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

MCP，全称 Model Context Protocol，是一种开放协议，用来标准化模型应用如何向大模型提供上下文，以及如何连接外部工具和数据源。

MCP 的经典架构包括：

```math
\text{MCP Host} \rightarrow \text{MCP Client} \rightarrow \text{MCP Server}
```
其中：

- Host 是用户实际使用的 AI 应用。
- Client 是 Host 内部维护的协议连接。
- Server 是暴露工具、资源和提示模板的服务。

MCP Server 可以连接：

- 本地文件系统。
- Git 仓库。
- 数据库。
- 浏览器。
- 企业知识库。
- 设计工具。
- 云服务。
- 业务 API。
- 内部搜索和日志系统。

它的核心价值是把工具生态从“每个应用各自集成”变成“标准服务器可复用”。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/04_MCP%E4%B8%8EA2A%E5%8D%8F%E8%AE%AE%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L306)，来源许可：GPL-3.0。

<a id="k6f6dce04685f"></a>

## MCP、A2A、OpenAPI、LangGraph、Agent SDK 如何协同？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

| 技术 | 角色定位 |
| --- | --- |
| OpenAPI | 描述传统 HTTP API |
| Function Calling | 让模型选择函数并生成参数 |
| MCP | 把工具、资源、提示模板标准化暴露给 Agent Host |
| A2A | 让独立 Agent 服务之间互操作 |
| LangGraph | 用图状态机编排可持久化 Agent 工作流 |
| Agent SDK | 提供 Agent、Tool、Handoff、Guardrails、Tracing 等开发框架 |

协同方式：

- 业务系统已有 OpenAPI，可以包装成 Function Tool 或 MCP Tool。
- Agent Host 通过 MCP 接工具，通过 A2A 接其他 Agent。
- LangGraph 负责编排多步骤状态机。
- Agent SDK 负责模型调用、工具调用、handoff、guardrails 和 tracing。
- 企业平台统一做权限、审计、评测和发布。

一个实际例子：

1. 用户让办公 Agent 生成季度经营分析。
2. Agent 用 MCP 查询数据仓库和文档库。
3. Agent 用 A2A 调用财务分析 Agent 生成指标解释。
4. LangGraph 管理“取数 -> 分析 -> 生成报告 -> 人工审批 -> 发布”的状态。
5. Agent SDK 记录 tracing，并在敏感动作前触发 guardrail。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/04_MCP%E4%B8%8EA2A%E5%8D%8F%E8%AE%AE%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L729)，来源许可：GPL-3.0。

<a id="k739181edc58d"></a>

## MCP是什么？Agent通过MCP调用工具的流程是什么？

**面试官：** MCP是什么？Agent通过MCP调用工具的流程是什么？

**面试官追问：** 你觉得MCP能成为标准吗？

**回答：**

MCP，即 Model Context Protocol，是一种面向 AI 应用与外部能力之间连接的开放协议。它解决的不是模型“会不会决定调用工具”，而是 Host、Client 与 Server 之间如何发现能力、协商版本、传输请求、返回内容并管理连接生命周期。Tools、Resources、Prompts 是常见的 Server 能力；较新的协议还在能力协商下支持日志、Sampling、Elicitation、Tasks 等扩展。

更准确的角色关系是：

- **Host** 是承载 Agent 的应用，例如 IDE、桌面客户端或业务服务，负责权限、上下文、模型调用和用户交互。
- **MCP Client** 运行在 Host 内部，通常与一个 MCP Server 建立一个逻辑连接。
- **MCP Server** 暴露工具、资源或提示模板，并连接本地文件、数据库、SaaS 或企业系统。

典型调用流程如下：

1. Client 通过 `initialize` 与 Server 协议握手，协商协议版本和双方能力，然后发送 initialized 通知。
2. Host 根据需要通过 `tools/list` 等方法发现能力，将经过权限过滤的工具 Schema 提供给模型。
3. 模型基于用户请求生成结构化工具调用意图。注意，这一步通常属于模型 API 或 Agent Runtime，而不是 MCP 协议替模型做决策。
4. Host 校验工具名、参数 Schema、用户权限、风险级别和是否需要人工批准。
5. Client 通过 JSON-RPC 2.0 向 Server 发起 `tools/call`。本地常见传输是 stdio，远程常见传输是 Streamable HTTP。
6. Server 执行能力并返回结构化内容、错误状态或资源引用。Host 对结果做大小限制、脱敏、可信度标记和 Prompt Injection 防护。
7. Host 将工具结果关联到原始调用，再交回模型继续推理，直到产生最终回答或触发下一次工具调用。

关于“能否成为标准”，到当前阶段已经不能再回答“OpenAI 和 Google 是否跟进还不确定”。OpenAI Agents SDK 与 Google ADK 均已提供 MCP 集成，主流开发工具和 Agent 生态也在广泛接入。更合理的判断是：**MCP 已经成为 Agent 工具与上下文连接层最有影响力的开放协议之一，但“广泛采用”不等于所有系统都必须统一成一个运行时。**

它仍有三类边界：第一，协议统一接口，不统一工具语义、数据质量和业务事务；第二，远程 Server 带来授权、Token 转发、供应链和 Prompt Injection 风险；第三，低延迟、强事务、超高吞吐的内部调用仍可能直接使用 gRPC、HTTP 或消息系统。MCP 的长期价值更像 Agent 世界的连接协议，而不是替代所有服务协议。

<a id="alibaba-cloud-agent-algo-20260901-q5"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1333)，来源许可：GPL-3.0。

<a id="k534c70048229"></a>

## Model-native Harness 和传统脚本 Harness 有什么区别？

| 维度 | 传统脚本 Harness | Model-native Harness |
| --- | --- | --- |
| 运行方式 | 外部脚本调用模型 API | 与 Agent SDK / Runtime 深度集成 |
| 工具支持 | 手动 mock 或简单函数 | 原生工具调用、文件、命令、沙箱 |
| Trace | 需要自行记录 | 运行时原生 trace |
| 安全 | 依赖脚本隔离 | 原生权限、sandbox、approval |
| 任务类型 | 偏离线输入输出 | 支持长任务、文件编辑、多工具、多轮 |
| 上线闭环 | 需要额外接入 CI/CD | 更容易接入 eval、trace、deploy gate |

传统脚本 Harness 仍然有价值，尤其适合轻量评测和自定义任务。但复杂 Agent 更需要 Runtime 级 Harness，因为它要评估真实工具执行、上下文组装、权限审批和环境状态变化。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/08_Agent_Harness_Engineering%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L714)，来源许可：GPL-3.0。

<a id="k88932b435485"></a>

## Multi Agent系统中的路由（Router）节点，依据哪些规则和逻辑，将任务分发给对应的子Agent？

<a id="batch4-p2-q16"></a>

**相关解释：** [Agent常见模式（ReAct/Plan and Execute等）](../15-%E5%89%8D%E7%AB%AF%E4%B8%8E%E6%B5%8F%E8%A7%88%E5%99%A8/React%E4%B8%8E%E7%BB%84%E4%BB%B6%E7%8A%B6%E6%80%81-01.md#k93a12d0c9256)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L422)，来源许可：GPL-3.0。

<a id="ke3cf8dbb0d15"></a>

## NLP 与强化学习、元学习、Agent 有什么联系？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐ (3/5)**

NLP 与强化学习：

- 对话系统可以看作序列决策。
- RLHF 用强化学习根据人类偏好优化语言模型。
- Agent 工具调用可视为策略选择。

NLP 与元学习：

- 少样本学习、prompt learning、in-context learning 都与快速适配有关。
- 大模型通过上下文示例完成任务，体现了某种元学习能力。

NLP 与 Agent：

- LLM 负责理解指令、规划步骤、生成工具调用。
- RAG 提供知识。
- 外部工具执行动作。
- 记忆系统维护长期状态。

从经典 NLP 到 Agent 的转变是：模型不再只是处理文本，而是通过文本接口组织工具、知识和行动。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BB%8F%E5%85%B8%E6%A8%A1%E5%9E%8B/%E8%87%AA%E7%84%B6%E8%AF%AD%E8%A8%80%E5%A4%84%E7%90%86%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L302)，来源许可：GPL-3.0。

<a id="k3633f66317f6"></a>

## OpenAI Agents SDK 的核心能力有哪些？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

OpenAI Agents SDK 面向生产级 Agent 编排，核心能力包括：

- **Agent**：定义模型、指令、工具、输出类型和 handoffs。
- **Tools**：函数工具、托管工具、MCP 工具、代码/浏览器/文件等执行能力。
- **Handoffs**：把任务转交给专门 Agent。
- **Guardrails**：对输入、输出、工具调用做安全和质量检查。
- **Tracing**：记录模型调用、工具调用、handoff、guardrail、自定义事件。
- **Sessions/Memory**：保存多轮会话状态。
- **Structured Output**：约束最终输出格式。

面试重点：

OpenAI Agents SDK 把 Agent 从“提示词 + 函数调用”提升到“可观测、可防护、可编排的工程系统”。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/01_AIGC%E6%97%B6%E4%BB%A3AI%20Agent%E5%9F%BA%E7%A1%80%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L456)，来源许可：GPL-3.0。

<a id="kb960bae8b286"></a>

## OpenAI Agents SDK、LangGraph、Semantic Kernel、Google ADK 如何对比？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

| 框架 | 核心特点 | 更适合 |
| --- | --- | --- |
| OpenAI Agents SDK | Agent、Tool、Handoff、Guardrails、Tracing | 快速构建通用 Agent 和多 Agent handoff |
| LangGraph | 状态图、持久化、人机协作、可恢复流程 | 复杂工作流和长期任务 |
| Semantic Kernel | 企业插件、Planner、与微软生态集成 | 企业系统智能化、.NET/Java 场景 |
| Google ADK | Agent 开发、多 Agent、A2A 生态 | Google/Gemini 生态和服务化 Agent |

选择建议：

- 需要轻量 Agent SDK 和 tracing：OpenAI Agents SDK。
- 需要复杂状态机和 durable execution：LangGraph。
- 企业微软技术栈：Semantic Kernel / Copilot Studio。
- Google 云和 A2A 生态：Google ADK / Vertex AI Agent Builder。

真实项目中也可以组合使用：用 LangGraph 管状态，用 MCP 接工具，用 A2A 接远程 Agent，用模型网关管理多模型。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/07_%E4%BC%81%E4%B8%9A%E7%BA%A7Agent%E5%B9%B3%E5%8F%B0%E4%B8%8E%E4%BA%A7%E5%93%81%E8%90%BD%E5%9C%B0%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L820)，来源许可：GPL-3.0。

<a id="k06b5bfd48627"></a>

## OpenClaw 这类个人助手型 Agent，和普通聊天产品有什么区别？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐ (3/5)**

OpenClaw 这类个人助手型系统关注持续服务：多入口消息、会话、工具执行、工作空间、长期记忆和后台任务，使用户可以跨时间推进目标。普通聊天产品主要围绕当前对话响应，但也可能加入其中部分能力，因此应比较实际职责，而非只按品牌分类。

个人助手需要处理入口断线、任务仍在运行、多个设备共享身份、定时触发与用户打断。持久状态和事件路由让任务跨越单次生成周期，工具及记忆让系统能延续上下文并影响环境。

持续运行同时扩大了误记忆、权限继承和重复执行的影响范围。应检查会话隔离、任务取消、凭证边界、删除和审计；长期存在的偏好不等于长期授权。部署时按具体版本、插件和配置核对功能，不将某一版默认行为泛化到全部个人助手。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/02_%E7%BC%96%E7%A0%81Agent%E4%B8%8EAgentOS%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L1016)，来源许可：GPL-3.0。

<a id="kac50f3cfc8cd"></a>

## Outcome Grading、Trajectory Grading、State Grading 如何区分？

| Grading 类型 | 评估对象 | 适合场景 |
| --- | --- | --- |
| Outcome Grading | 最终答案或最终 artifact | 问答、报告、代码 patch、客服回复 |
| Trajectory Grading | 中间计划、工具调用、权限请求、观察解释 | 工具型 Agent、多步任务、安全审计 |
| State Grading | 最终环境状态 | 数据库、文件系统、订单状态、页面状态 |
| Safety Grading | 是否越权、泄密、误执行危险操作 | 企业 Agent、浏览器 Agent、编码 Agent |
| Cost Grading | token、耗时、工具次数、人工审批次数 | 生产上线和平台治理 |

例子：

- 编码 Agent：Outcome 看测试是否通过，Trajectory 看是否读了相关文件、是否乱改无关文件，State 看 diff 是否符合预期。
- 客服 Agent：Outcome 看回复是否正确，Trajectory 看是否遵守政策，State 看订单数据库是否变成期望状态。
- 浏览器 Agent：Outcome 看任务是否完成，Trajectory 看是否点击危险按钮前确认，State 看页面或后台状态是否正确。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/08_Agent_Harness_Engineering%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L324)，来源许可：GPL-3.0。

<a id="k3fad101c5ba0"></a>

## PaddleOCR、PP-OCRv5、PaddleOCR-VL 对 AIGC 和 Agent 应用有什么参考价值？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

PaddleOCR 是 OCR 和文档智能工程落地中很常见的开源体系，PP-OCRv5 代表轻量高精度文字识别路线，PaddleOCR-VL 代表文档视觉语言模型路线。它们对 AIGC 和 Agent 应用有几个参考价值：

- **从 OCR 到 LLM-ready 文档解析**：现代 OCR 工具不只输出文字，还会输出 Markdown、JSON、版面结构、表格结构和坐标信息，方便进入 RAG、Agent workflow 和知识库；
- **轻量 OCR 仍然有价值**：PP-OCRv5 这类方案强调单模型覆盖简体中文、繁体中文、英文、日文、拼音、手写体、竖排文本、生僻字等复杂场景，成本和延迟通常优于通用 VLM；
- **文档 VLM 正在增强结构解析**：PaddleOCR-VL 这类模型关注文档元素定位、复杂版面解析、扫描扭曲、屏幕拍摄、表格和图文混排理解；
- **工程部署能力强**：生产系统通常需要 CPU/GPU/国产硬件、多平台、服务化、浏览器端或边缘端部署能力；
- **与 Agent 生态结合紧密**：OCR 输出可以作为文档 Agent、GUI Agent、RAG 系统、自动化办公系统的结构化观测；
- **对复杂文档更关注结构**：票据、合同、论文、扫描件、网页截图不只是文字集合，更需要表格、标题、段落、阅读顺序和字段关系。

面试中可以这样回答：

> AIGC 时代的 OCR 不再只是“图片转文字”，而是“把 PDF、图片、截图转成大模型可理解、可检索、可引用、可执行的结构化数据”。

工程选型时可以采用组合策略：高频、低延迟、可控场景优先用 PP-OCRv5 这类专用 OCR；复杂文档解析、图文混排理解和开放问题问答则结合 PaddleOCR-VL 或其他文档多模态模型；最终进入 RAG/Agent 前统一转换为带坐标、页码、置信度和结构层级的中间表示。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BB%8F%E5%85%B8%E6%A8%A1%E5%9E%8B/OCR%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L470)，来源许可：GPL-3.0。

<a id="ka021f3f33ce3"></a>

## Plugin System 如何扩展平台、工具、记忆和可观测性？

Plugin System 的目标是让 Agent 平台在不修改核心代码的情况下扩展能力。

可扩展对象包括：

- Gateway Platform：新增 IM、邮件、会议、企业协作工具适配器。
- Tool：新增业务 API、浏览器能力、文件处理、媒体处理。
- Skill：新增领域流程和模板。
- Memory Provider：接入 Honcho、mem0、Supermemory 或企业记忆服务。
- Context Engine：替换默认压缩器，接入图结构上下文或长期上下文模型。
- Observability：接入 Langfuse、OpenTelemetry、企业日志平台。
- Dashboard Tab：新增分析、配置、成就、审计页面。

插件注册应包含：

- manifest。
- 权限声明。
- 依赖检查。
- 初始化和卸载。
- hooks。
- config schema。
- 版本兼容范围。
- 安全策略。

风险控制：

- 插件默认最小权限。
- 高风险插件必须显式启用。
- 插件 API 与核心状态解耦。
- 记录插件触发的工具调用和副作用。
- 平台适配插件要有认证和消息来源校验。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/09_%E8%87%AA%E8%BF%9B%E5%8C%96Agent%E4%B8%8E%E5%A4%9A%E5%B9%B3%E5%8F%B0%E8%BF%90%E8%A1%8C%E6%97%B6%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L338)，来源许可：GPL-3.0。

<a id="ke516f60d36f0"></a>

## RBAC、ABAC、租户隔离在 Agent 中如何落地？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

| 机制 | 作用 | Agent 场景 |
| --- | --- | --- |
| RBAC | 基于角色授权 | 运营可创建客服 Agent，研发可使用代码工具 |
| ABAC | 基于属性授权 | 数据等级、部门、地域、时间、任务风险共同判断 |
| Tenant Isolation | 租户隔离 | 不同客户的数据、记忆、trace、工具配置互不可见 |

落地建议：

- RBAC 管基础角色和平台操作。
- ABAC 管细粒度数据和工具访问。
- 租户隔离管数据边界。
- 高风险工具加审批流。
- 所有工具调用带 user_id、agent_id、tenant_id、task_id。
- RAG 和 Memory 检索前先做权限过滤。
- Trace 和日志也要按租户隔离。

例子：用户是财务经理，有权查看财务数据；但一个客服 Agent 即使由该用户启动，也不应自动继承全部财务权限，除非任务、工具和审批都满足条件。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/07_%E4%BC%81%E4%B8%9A%E7%BA%A7Agent%E5%B9%B3%E5%8F%B0%E4%B8%8E%E4%BA%A7%E5%93%81%E8%90%BD%E5%9C%B0%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L366)，来源许可：GPL-3.0。

<a id="k7b10257a6529"></a>

## Reflection 机制判断问题：在 Reflection 机制中，我们该如何判断一个 Agent 执行失败是由于知识缺失，还是工具调用错误导致的呢？

**回答：**

要依据轨迹证据诊断，不能只让模型自报原因。先检查授权数据中是否存在正确知识，以及检索是否把它找出来：知识不存在是覆盖问题，知识存在但漏召回是检索问题，已召回却误用是理解或推理问题。

工具侧检查是否选择正确接口、schema 与参数是否合法、业务权限是否满足、服务是否超时或返回错误。HTTP 成功还需检查结果内容与目标是否一致；写入超时则可能是状态未知，不能立即重试。

可以做替换实验：人工给正确证据后是否恢复，给正确工具参数后是否恢复，回放工具结果是否仍失败。多因素可能同时存在，按证据记录主因和次因；分别采取补知识、改检索、修参数、恢复服务或重规划。

<a id="jd-damodel-20251211-20260205-p9-q4"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E4%BA%AC%E4%B8%9C%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1401)，来源许可：GPL-3.0。

<a id="k3d8cfb3c691c"></a>

## Reflection 机制里,如何判断一个 Agent 的失败是由知识缺失还是工具调用错误引起的?

**回答：**

要依据轨迹证据诊断，不能只让模型自报原因。先检查授权数据中是否存在正确知识，以及检索是否把它找出来：知识不存在是覆盖问题，知识存在但漏召回是检索问题，已召回却误用是理解或推理问题。

工具侧检查是否选择正确接口、schema 与参数是否合法、业务权限是否满足、服务是否超时或返回错误。HTTP 成功还需检查结果内容与目标是否一致；写入超时则可能是状态未知，不能立即重试。

可以做替换实验：人工给正确证据后是否恢复，给正确工具参数后是否恢复，回放工具结果是否仍失败。多因素可能同时存在，按证据记录主因和次因；分别采取补知识、改检索、修参数、恢复服务或重规划。

<a id="jd-damodel-20251211-20260205-p8-q7"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E4%BA%AC%E4%B8%9C%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1281)，来源许可：GPL-3.0。

<a id="kbd3f10237688"></a>

## review agent怎么确保他的评价是正确的？

**回答：**

不能保证一个 review Agent 的评价天然正确，应将它视为需要校准的测量工具。首先定义评分标准、证据要求和不确定性处理，再用人类金标与确定性检查验证它。

能用程序验证的部分优先用程序：测试是否通过、文件是否存在、数据库状态是否满足、是否越权、数字是否一致。语言质量、解释完整性等难以完全程序化的部分，再使用模型评分，并要求引用可核验的证据位置。

建立双人独立标注与分歧仲裁的校准集，覆盖短答案、长答案、不同风格、边界失败与对抗样本。测评分器对错误的漏检、对正确结果的误杀和与人工判断的一致性；高一致性也不是绝对正确，应结合业务错误成本。

控制位置偏差、长度偏好、同模型自我偏好与提示注入：比较答案时随机交换顺序，隐藏不必要的模型身份，将被评内容明确视为数据，并固定评分器版本。多评审或跨模型复核可以减少部分相关错误，但不能替代独立证据。高风险或低置信结果进入人工审查。

<a id="alibaba-qwen-20260916-q30"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L2294)，来源许可：GPL-3.0。

<a id="k23c5cb446ee8"></a>

## RLAIF、Constitutional AI 和 Agent RL 有什么关系？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐ (3/5)**

RLAIF，Reinforcement Learning from AI Feedback，使用 AI 模型提供反馈，而不是完全依赖人工偏好。

Constitutional AI：

- 设定一组原则或宪法。
- 让模型根据原则自我批评和修改。
- 使用 AI feedback 进行对齐训练。

Agent RL：

- 奖励来自任务完成、工具调用成功、环境反馈或自动评测。
- 更关注多步规划和长期目标。

关系：

| 方法 | 反馈来源 | 典型目标 |
| --- | --- | --- |
| RLHF | 人类偏好 | 对齐人类偏好 |
| RLAIF | AI 反馈 | 降低人工成本 |
| Constitutional AI | 原则 + AI 反馈 | 安全、规范、可控 |
| Agent RL | 环境和任务反馈 | 提升行动成功率 |

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BB%8F%E5%85%B8%E6%A8%A1%E5%9E%8B/%E5%BC%BA%E5%8C%96%E5%AD%A6%E4%B9%A0%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L347)，来源许可：GPL-3.0。

<a id="k909fbb52c6a5"></a>

## Roots、Sampling、Elicitation 分别解决什么问题？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

除了 Tools、Resources、Prompts，MCP 还包含一些容易被忽略但很重要的能力：

| 能力 | 解决的问题 | 例子 |
| --- | --- | --- |
| Roots | Host 告诉 Server 当前可访问的边界 | 当前工作区、项目根目录、允许读取的路径 |
| Sampling | Server 请求 Host 代为调用模型 | MCP Server 需要模型帮助总结或推理 |
| Elicitation | Server 请求 Host 向用户补充信息 | 工具执行前需要用户选择账号或确认参数 |

Roots 的意义是边界控制。文件类 Server 不应该默认扫描整台机器，而应该只在 Host 提供的 roots 内工作。

Sampling 的意义是让 Server 在需要模型能力时不必自己持有模型密钥，而是通过 Host 受控请求模型。

Elicitation 的意义是把“工具执行中需要用户补充信息”变成标准交互，而不是让 Server 私下弹窗或阻塞。

面试中可以说：Tools / Resources / Prompts 是 MCP 的常用表层能力，Roots / Sampling / Elicitation 则体现了 MCP 对安全边界、模型调用权和用户交互权的工程化考虑。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/04_MCP%E4%B8%8EA2A%E5%8D%8F%E8%AE%AE%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L361)，来源许可：GPL-3.0。

<a id="k483f62e50eb8"></a>

## Skill Hub / Skill Marketplace 如何设计？

Skill Hub 是可复用能力包的分发和治理系统。它和 Tool Registry 不同：Tool 是可执行动作，Skill 是任务流程、模板、参考资料和可选脚本。

Skill Hub 应支持：

- skill 元数据：名称、描述、标签、版本、作者、来源。
- 能力依赖：需要哪些工具、环境变量、平台。
- 安全扫描：路径穿越、敏感文件访问、恶意脚本、prompt injection。
- 启用范围：全局、用户、团队、项目、平台。
- 条件激活：工具可用时才注入。
- 文档和示例。
- 使用统计。
- 评分和反馈。
- pinned / archived / deprecated 状态。
- 外部目录和社区来源同步。

面试中可以强调：Skill Marketplace 不是 prompt 集市，而是带有依赖、权限、版本、审计和生命周期治理的能力分发系统。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/09_%E8%87%AA%E8%BF%9B%E5%8C%96Agent%E4%B8%8E%E5%A4%9A%E5%B9%B3%E5%8F%B0%E8%BF%90%E8%A1%8C%E6%97%B6%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L319)，来源许可：GPL-3.0。

<a id="k882355df8011"></a>

## skills和mcp的区别

**回答：**
Skill 通常组织完成某类任务所需的方法、步骤、脚本或资源，具体含义取决于宿主平台；MCP 则约定模型应用与外部能力之间的连接、能力发现和调用方式。Tool 是可执行的动作接口，可以经 MCP 暴露，也可以由应用直接接入。三者处于不同层次，可以组合使用。

例如“制作商品宣传图”可以是一项 Skill，规定素材检查、生成、编辑和验收流程；“创建图片生成任务”“查询生成进度”是 Tool；MCP 为兼容宿主提供发现与调用这些工具的协议。Skill 不自动提供执行权限，MCP 也不会自动完成任务规划或保证调用正确，应用仍需校验参数、权限、状态与最终结果。

关于零散功能的组织方式，见[Skill 与 Tool 的边界](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%99%BE%E5%BA%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#baidu-aigc-multimodal-agent-20260922-20260924-r2-q3-3)；关于协议层的具体机制，见[MCP 与普通 API 的差异](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%99%BE%E5%BA%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#baidu-aigc-multimodal-agent-20260922-20260924-r2-q5-1)。

<a id="batch3-p3-q9"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%99%BE%E5%BA%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L297)，来源许可：GPL-3.0。

<a id="ka1207e518602"></a>

## Skill、MCP、Function Calling、Workflow、SubAgent，分别解决什么问题，你在项目中如何组合使用？

**回答：**

这几个概念处在不同层次，可以组合使用。先说明职责，再用一条真实调用链解释它们如何协作。

| 概念 | 主要解决的问题 | 不自动保证的能力 |
| --- | --- | --- |
| Skill | 封装任务方法、领域约束、脚本和资源 | 不自动提供权限、隔离或执行引擎 |
| MCP | 宿主/客户端与服务端交换工具、资源等能力的标准协议 | 不决定完整规划，也不保证工具可信 |
| Function Calling | 模型按工具契约提出函数名和结构化参数 | 实际执行、授权和业务校验由应用负责 |
| Workflow | 显式定义控制流、状态、分支与恢复 | 持久化和容错是否具备取决于实现 |
| SubAgent | 将子任务委派给具有独立上下文或配置的代理执行 | 不天然获得新进程隔离，也不必然更准 |

例如测试报告任务由 Workflow 管理状态；Skill 提供测试设计方法；模型通过 Function Calling 提出读取接口文档的调用；应用把请求转给 MCP 客户端和对应服务；执行器验证权限与参数后取得结果。复杂模块的分析可以交给子代理，但主流程仍负责证据合并和最终验收。

子代理的输出是待验证产物，不能因为来自另一个代理就视为正确。所有调用应传递任务 ID、权限范围、时间/费用预算和结果 schema，避免权限在跨层调用中丢失。

这些层不是每个项目都要齐全。已有稳定 SDK 的单工具任务可以直接调用；固定小流程不需要子代理。合理组合的依据是可维护性、边界与效果，而不是把五个名词全部放进架构图。

![图3Skill与Agent执行系统的职责划分](https://raw.githubusercontent.com/WeThinkIn/AIGC-Interview-Book/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/imgs/meituan-agent-20261012-18fa4134/03_Skill与Agent执行系统的职责划分.png)

图 3：不同概念承担不同职责。Skill 可以提供方法与脚本，Function Calling 表达调用意图，MCP 提供能力交互协议，Workflow 管理流程，SubAgent 接受有边界的子任务；是否采用某一层取决于业务需要。

**用一个故障检验概念是否真正落地。** 若子代理建议调用删除工具，父流程仍需检查它是否属于原始目标、目标资源是否唯一、当前身份是否有权限、审批是否覆盖此次参数。MCP 服务端接受请求也不能替代业务授权；Function Calling 输出符合 schema 也不能证明操作正确。把决策、通信与执行分别讲清楚，比把五个名称串成固定流水线更准确。

<a id="meituan-agent-20261012-18fa4134-q22"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%BE%8E%E5%9B%A2%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1115)，来源许可：GPL-3.0。

<a id="ka8f0567b9de6"></a>

## Smoke Eval、Regression Eval、Safety Eval、Canary Eval 如何分层？

| Eval 层级 | 目的 | 运行频率 |
| --- | --- | --- |
| Smoke Eval | 快速发现明显不可用 | 每次提交或 prompt 变更 |
| Regression Eval | 防止历史问题复发 | PR、发布前 |
| Safety Eval | 检查越权、泄密、注入、高风险动作 | 发布前、策略变更前 |
| Robustness Eval | 检查异常工具、网络错误、用户反悔 | 定期或重大变更前 |
| Canary Eval | 小流量真实环境验证 | 灰度阶段 |
| Shadow Eval | 线上旁路评估，不产生副作用 | 生产观测阶段 |

建议分层：

- **小而快**：smoke set，几十个高价值任务。
- **中等规模**：regression set，覆盖历史失败和核心业务。
- **高风险专项**：safety / red-team set。
- **真实分布**：从线上 trace 抽样构造 canary / shadow set。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/08_Agent_Harness_Engineering%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L602)，来源许可：GPL-3.0。

<a id="k5c65d5776579"></a>

## Supervisor、Router、Swarm、Debate 如何对比？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

| 模式 | 核心思想 | 优点 | 风险 |
| --- | --- | --- | --- |
| Supervisor | 上级 Agent 拆分任务并协调下级 | 控制强，适合复杂项目 | 上级成为瓶颈 |
| Router | 根据任务类型路由到专门 Agent | 简单高效，适合意图分发 | 路由错误会影响结果 |
| Swarm | Agent 之间动态交接和协作 | 灵活，适合开放任务 | 可控性和调试难度高 |
| Debate | 多方提出观点，由评审选择 | 可提升复杂判断质量 | 成本高，可能互相强化错误 |

选择建议：

- 客服和办公自动化优先 Router。
- 研究报告和软件工程任务适合 Supervisor。
- 创意、开放探索可以尝试 Swarm。
- 高价值决策、方案评审可以使用 Debate。

面试中要注意：多 Agent 编排本质是组织结构设计，不是 Agent 数量越多越先进。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/03_Agent%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81%E7%BC%96%E6%8E%92%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L519)，来源许可：GPL-3.0。

<a id="k2f5e9bde9765"></a>

## SWE-bench Harness 给编码 Agent 评测带来哪些启发？

SWE-bench 的核心启发是：编码 Agent 评测要基于真实仓库、真实 issue、真实测试和可复现环境，而不是只做 LeetCode 式函数生成。

官方 SWE-bench Harness 使用 Docker 构造可复现环境，核心流程包括：

- 为任务准备仓库和依赖环境。
- 应用模型生成的 patch。
- 运行测试命令。
- 根据测试结果判断 issue 是否解决。
- 保存日志和评测结果。

这给企业编码 Harness 的启发：

1. **环境必须可复现**

   使用容器、锁定依赖、固定 base commit。

2. **测试不是唯一指标**

   还要看安全、diff 范围、代码风格、性能和可维护性。

3. **任务要接近真实工作**

   应包含 bug 修复、CI 修复、依赖升级、重构、测试补齐、文档同步。

4. **要防止 benchmark overfitting**

   公开榜单不能替代私有仓库任务集。

5. **日志和失败分类很关键**

   同样失败，可能是定位失败、测试环境失败、工具权限失败或代码生成失败。

面试中可以说：SWE-bench 是编码 Agent Harness 的经典参考，但企业级编码 Harness 还要覆盖私有仓库、权限、dirty worktree、安全策略、review 质量和发布流程。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/08_Agent_Harness_Engineering%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L426)，来源许可：GPL-3.0。

<a id="k221fcf2d09df"></a>

## Task Spec、Environment Spec、Expected Outcome 应该包含什么？

**Task Spec** 描述任务本身：

- task_id。
- 用户输入。
- 任务类型。
- 难度。
- 风险等级。
- 允许工具。
- 禁止动作。
- 最大轮数、最大耗时、最大成本。
- 是否需要人类确认。

**Environment Spec** 描述运行环境：

- 初始数据库快照。
- 初始文件系统。
- 仓库 commit。
- 浏览器页面状态。
- mock API。
- 用户模拟器 persona。
- 网络、权限和密钥配置。
- 随机种子。

**Expected Outcome** 描述应该发生什么：

- 最终文本答案。
- 最终数据库状态。
- 文件 diff。
- 通过的测试。
- 生成的 artifact。
- 不应该发生的动作。
- 必须引用的证据。
- 允许的多种合法路径。

高质量 Harness 不应只依赖“最终答案字符串匹配”。很多 Agent 任务存在多条合理路径，真正关键的是最终状态、业务规则和安全边界。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/08_Agent_Harness_Engineering%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L191)，来源许可：GPL-3.0。

<a id="kd46741468a5f"></a>

## Tool Registry、MCP Registry、Agent Registry 如何分工？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

本节关注 Registry 在企业平台里的资产管理和权限治理；MCP / A2A 的协议字段、能力协商、传输和调用语义，见 [04_MCP与A2A协议高频考点.md](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/04_MCP与A2A协议高频考点.md)。

| Registry | 管理对象 | 典型字段 |
| --- | --- | --- |
| Tool Registry | 应用内函数、OpenAPI 工具、内置工具 | 工具名、Schema、风险等级、owner、版本 |
| MCP Registry | MCP Server 和其暴露能力 | server 地址、transport、tools/resources/prompts、认证方式 |
| Agent Registry | 可被复用或远程调用的 Agent | Agent Card、能力、输入输出、SLA、权限、版本 |

分工原则：

- Tool Registry 管“函数级能力”。
- MCP Registry 管“标准工具服务器”。
- Agent Registry 管“能独立完成任务的 Agent 服务”。

企业场景中，这些 registry 需要统一治理：

- owner 和责任人。
- 数据分级。
- 风险等级。
- 权限范围。
- 调用审计。
- 版本管理。
- 可用性监控。
- 下线和回滚机制。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/07_%E4%BC%81%E4%B8%9A%E7%BA%A7Agent%E5%B9%B3%E5%8F%B0%E4%B8%8E%E4%BA%A7%E5%93%81%E8%90%BD%E5%9C%B0%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L229)，来源许可：GPL-3.0。

<a id="k9e979182def9"></a>

## Toolformer 与 RLHF 对比：Toolformer 采用自监督学习来生成 tool call 数据，这种训练范式和 RLHF 存在哪些差别？并且，为什么 Toolformer 更容易实现泛化呢？

**回答：**

Toolformer 先用少量示范提示语言模型提出潜在 API 调用，把候选实际执行后的结果插入文本，再比较是否降低后续文本的语言建模损失，筛选有帮助的调用。随后用增强文本继续训练，使模型学习何时调用、参数如何写、怎样使用返回信息。

传统 RLHF 通常先收集人类偏好、训练奖励模型，再做策略优化；也存在直接偏好优化等替代方式。两者的监督来源和优化目标不同：Toolformer 利用外部工具结果对预测的帮助筛选训练数据，RLHF 以偏好或奖励引导输出行为。

**‘Toolformer 更容易泛化’不是无条件成立的结论。** 工具提供可组合外部能力，训练也保留自然语言上下文，可能有助于跨任务使用已学工具；但新 API、参数 schema、权限、错误恢复和新领域仍可能超出分布。泛化应固定工具与任务划分，通过未见任务和未见工具测试分别验证，不能从方法名直接推出优于 RLHF。

<a id="jd-damodel-20251211-20260205-p9-q3"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E4%BA%AC%E4%B8%9C%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1390)，来源许可：GPL-3.0。

<a id="ke28f90baa3e7"></a>

## Toolformer 中通过自监督学习生成 tool call 数据,这个训练范式和 RLHF 的差别在哪里?为什么它更容易泛化?

**回答：**

<a id="jd-damodel-20251211-20260205-p8-q8"></a>

**相关解释：** [Toolformer 与 RLHF 对比：Toolformer 采用自监督学习来生成 tool call 数据，这种训练范式和 RLHF 存在哪些差别？并且，为什么 Toolformer 更容易实现泛化呢？](Agent%E3%80%81%E5%B7%A5%E5%85%B7%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81-02.md#k9e979182def9)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E4%BA%AC%E4%B8%9C%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1292)，来源许可：GPL-3.0。

<a id="k8a151d712a82"></a>

## Verl中的AgentLoop的特点是什么？

**回答：**

verl 的 AgentLoop 是面向**多轮 rollout 与 Agentic RL 训练**的轨迹生成抽象。它不是 LangGraph 一类面向线上业务编排的完整 Agent 框架，也不负责规定工具应如何定义；它关心的是如何让用户自定义循环与模型、工具或环境交互，并产出可用于 PPO/GRPO 等训练的准确轨迹。

核心接口是 `AgentLoopBase.run(...)`。自定义实现可以多次调用生成服务、执行工具、与环境交互或反思，最终返回 `AgentLoopOutput`。关键字段包括 `prompt_ids`、`response_ids` 和 `response_mask`：模型自己生成的 token 标为 1，工具 Observation 和 padding 标为 0，使策略损失只作用于策略生成部分。当前实现还可携带多模态数据、轨迹奖励、轮数、指标和额外字段。

它的工程特点包括：

1. **异步并发 rollout。** Worker 为样本启动协程，适合工具等待时间不一致的多轮轨迹。
2. **推理后端抽象。** 可对接 vLLM、SGLang 等异步生成服务，并支持 token-in/token-out 与聊天接口。
3. **请求级负载均衡与粘性会话。** 首轮选择负载较低的推理服务，后续轮次保持到同一实例，利于缓存和会话一致性。
4. **训练与 rollout 协同。** rollout 前同步训练权重并唤醒推理服务，结束后释放 KV Cache、卸载权重，为训练阶段让出资源。
5. **保留原始 token 轨迹。** 多轮 RL 中若把最终 messages 重新套 chat template，工具解析和 decode-encode 可能改变 token，导致轨迹偏离行为策略。AgentLoop 直接维护连续 token 和 mask，避免这一关键 off-policy 误差。
6. **可插拔循环。** 单轮、工具调用或业务自定义 AgentLoop 可以通过配置注册；框架提供调度与训练接口，工具语义、环境状态和终止条件仍由用户实现。

局限也要说明：多轮轨迹的 reward 归因、工具错误、超长上下文、环境可恢复性和并发尾延迟不会因为使用 AgentLoop 自动解决；其 API 在不同版本仍可能演进，生产项目必须锁定版本并以实际代码为准。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1188)，来源许可：GPL-3.0。

<a id="k67fb2a4791b4"></a>

## VideoLLaMB的递归记忆桥接层是如何设计的？其主要优势是什么？

**VideoLLaMB**是一种新颖的长视频理解框架，利用带有递归内存 token 的内存桥接层对 100% 的视频内容进行编码，而不会丢弃关键的视觉提示。

VideoLLaMB的递归记忆桥接层通过在桥接层内集成递归记忆令牌来增强线性层的记忆能力。具体设计如下：

- **记忆token**：在每个视频段前缀固定数量的记忆令牌，表示为[mi;si]，其中mi表示记忆令牌，si表示视频段。

- **自注意力操作**：对包含记忆令牌的视频段应用标准的自注意力操作，生成更新后的记忆令牌和视觉表示，公式如下：
![](https://raw.githubusercontent.com/WeThinkIn/AIGC-Interview-Book/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E8%A7%86%E9%A2%91%E5%9F%BA%E7%A1%80/imgs/VideoLLaMB的自注意力操作.png)

- **递归处理**：这个过程递归进行，遍历语义视频段的同时更新记忆 token，最终生成视频序列的压缩视觉摘要。

**其主要优势包括：**

- **增强记忆能力**：通过递归记忆令牌，桥接层能够增强对视频内容的记忆能力。
- **信息压缩**：记忆令牌能够在保留当前视频场景的同时压缩过去视频的信息，提高计算效率。
- **缓解梯度消失**：通过记忆缓存和检索机制，能够有效缓解梯度消失问题，保留长期依赖信息。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E8%A7%86%E9%A2%91%E5%9F%BA%E7%A1%80/04_%E8%A7%86%E9%A2%91%E7%90%86%E8%A7%A3%E5%85%B8%E5%9E%8B%E6%A8%A1%E5%9E%8B%E4%B8%8E%E6%9E%B6%E6%9E%84.md#L30)，来源许可：GPL-3.0。

<a id="k00e75a094f6d"></a>

## ViT 的网络结构与工作流程是什么？

**难度评分：⭐⭐ (2/5)  |  考察频率：⭐⭐⭐⭐⭐ (5/5)**

ViT（Vision Transformer）用 Transformer 代替 CNN 做视觉特征提取。它几乎没有加入视觉专用的结构，直接把 NLP 里的标准 Transformer Encoder 搬到了图像上[1]。

以 ViT-B/16 为例，输入一张 224×224 的图像，切成 196 个 16×16 的 patch，每个 patch 经线性投影变成一个 768 维向量，相当于 NLP 里的一个 token。再加上位置编码（Position Embedding）和一个可学习的 [CLS] token，一起送进 Transformer Encoder。分类任务取 [CLS] token 的输出，检测、分割等密集预测任务取全部 patch token 的输出。

ViT 去掉了卷积、池化这些人工设计的归纳偏置，完全靠自注意力建模 patch 之间的全局关系。这让它很容易随模型和数据规模扩展，代价是对训练数据量依赖很强。

> **面试速答**：ViT 把图像切成 patch，每个 patch 线性投影成 token，加上位置编码和 [CLS] token 后送进标准 Transformer Encoder。分类取 [CLS] 输出，密集预测取全部 patch 输出。它几乎不带视觉归纳偏置，扩展性好，但很依赖数据量。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E5%A4%9A%E6%A8%A1%E6%80%81%E5%9F%BA%E7%A1%80%EF%BC%88%E7%B2%BE%E5%8D%8E%E7%89%88%EF%BC%89/2_AI%E5%A4%9A%E6%A8%A1%E6%80%81%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L133)，来源许可：GPL-3.0。
