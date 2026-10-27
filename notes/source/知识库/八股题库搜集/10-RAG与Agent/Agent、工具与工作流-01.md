# Agent、工具与工作流

<a id="k58f95dae0317"></a>

## 6）Skill 和 MCP 有什么区别？

**回答：**

Skill 和 MCP 解决的是不同层次的问题。

**Skill 更像可复用的能力包或工作流说明。** 它通常包含触发条件、领域知识、执行步骤、提示模板、脚本、资源和验收规则，告诉 Agent“遇到某类任务应该如何完成”。Skill 可以是纯指令，也可以调用本地工具；它的重点是流程和方法。

**MCP 是工具与上下文的协议层。** 它规定客户端和服务器如何发现、描述、调用工具，以及读取资源、提示模板和结构化结果。MCP 解决的是“模型/Agent 如何以统一方式连接外部能力”，重点是接口契约、能力发现、权限和传输。

两者可以组合：Skill 规定“先读取项目规范，再调用代码检查工具并运行测试”，MCP Server 提供读取文件、查询数据库或执行测试的标准化工具。Skill 不等于 MCP Server，MCP 也不会自动提供业务流程、任务分解和质量标准。

设计时要把职责分开：Skill 负责方法、顺序和决策边界；MCP 负责受控能力暴露、参数 schema、权限、超时和结果协议。这样既能复用工作流，也能替换底层工具实现。

<a id="mihoyo-agent-20260801-q7"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%B1%B3%E5%93%88%E6%B8%B8%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L114)，来源许可：GPL-3.0。

<a id="k9d6e28328bac"></a>

## 8）个人agent项目深挖

**回答：**

这道题不能套一个虚构项目答案。我的回答结构会严格围绕真实项目展开：

1. **业务目标。** 谁在什么场景下遇到什么问题，原流程的成本、延迟或错误点是什么，成功指标是什么。
2. **完整链路。** 用户输入经过意图理解、状态构建、规划/路由、工具调用、观察结果、重试/反思和最终输出的过程；画清同步、异步和人工确认边界。
3. **状态与数据。** 说明短期上下文、长期记忆、RAG 文档、工具返回、任务 ID 和持久化方式，解释多轮与并发时如何隔离。
4. **关键技术选择。** 为什么采用固定 Workflow、ReAct 或图式编排，为什么选某个模型/框架/向量库，替代方案的成本和缺点是什么。
5. **可靠性。** 结构化输出、参数校验、超时、重试、幂等、熔断、权限、审计、人工审批和失败降级怎么做。
6. **效果证明。** 离线评测集、成功率、工具调用正确率、任务完成率、延迟、成本和线上反馈如何定义，改动是否有消融或 A/B 证据。

项目深挖的本质是证明“我理解系统为什么这样工作，并且能定位它为什么失败”。没有亲自实现的模块要明确边界，不把框架默认行为说成自己的设计；面试官继续追问时，能落到一次真实请求的输入、状态变化、工具参数、日志和最终结果。

<a id="mihoyo-agent-20260801-q9"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%B1%B3%E5%93%88%E6%B8%B8%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L146)，来源许可：GPL-3.0。

<a id="kbae7b3783757"></a>

## A2A 中 Message、Task、Part、Artifact 如何理解？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

| 概念 | 含义 | 例子 |
| --- | --- | --- |
| Message | 一次通信消息 | 用户请求、Agent 追问、状态说明 |
| Task | 一个需要跟踪状态的工作单元 | “分析这份财报并生成摘要” |
| Part | Message 或 Artifact 中的内容片段 | text part、file part、data part |
| Artifact | 任务产出的结果对象 | 报告、图表、代码文件、结构化 JSON |

可以这样理解：

- Message 是沟通。
- Task 是任务容器。
- Part 是内容的基本组成。
- Artifact 是可交付成果。

为什么需要这些抽象？

- Agent 协作不只是发一句文本。
- 任务可能持续很久，需要状态。
- 输入输出可能是多模态的。
- 最终结果可能包含多个文件或结构化对象。
- Client 需要区分中间消息和最终交付物。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/04_MCP%E4%B8%8EA2A%E5%8D%8F%E8%AE%AE%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L608)，来源许可：GPL-3.0。

<a id="k4bcebfaa7a03"></a>

## A2A 和 MCP 分别解决什么问题？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

MCP 解决“Agent 如何使用工具和上下文”的问题。

A2A 解决“Agent 如何和其他 Agent 服务通信协作”的问题。

| 维度 | MCP | A2A |
| --- | --- | --- |
| 连接对象 | 工具、数据源、上下文服务器 | 独立 Agent 服务 |
| 关系 | Agent-to-Tool | Agent-to-Agent |
| 核心能力 | 工具调用、资源访问、提示模板 | 任务委托、状态通信、远程能力调用 |
| 典型场景 | 连接 GitHub、数据库、文件系统 | 调用金融分析 Agent、客服 Agent、代码审查 Agent |

本地子 Agent 通常在同一进程内通信，延迟低，适合模块化分工；远程 Agent 更适合跨团队、跨服务、跨组织协作。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/01_AIGC%E6%97%B6%E4%BB%A3AI%20Agent%E5%9F%BA%E7%A1%80%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L379)，来源许可：GPL-3.0。

<a id="kd462d43fa56f"></a>

## A2A 如何支持流式响应和异步通知？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

Agent 任务经常不是一次请求马上返回，尤其是研究、代码生成、数据分析、浏览器自动化等场景。A2A 因此需要支持长任务。

常见机制：

1. **Streaming**

   Remote Agent 在任务执行过程中持续发送状态、文本片段、工具进度或中间结果。

2. **Task Status**

   Task 可以有 submitted、working、input-required、completed、failed、canceled 等状态，Client 能跟踪进度。

3. **Input Required**

   当 Remote Agent 需要用户补充信息时，可以把任务状态切到需要输入，而不是直接失败。

4. **Push Notification**

   对长时间任务，Remote Agent 可以在完成后通过推送通知 Client，而不是要求 Client 一直保持连接。

5. **Artifact Delivery**

   最终结果以 Artifact 形式交付，支持文本、文件、结构化数据等多种 Part。

面试中可以说：A2A 的长任务能力使它更像 Agent 服务协议，而不是简单聊天 API。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/04_MCP%E4%B8%8EA2A%E5%8D%8F%E8%AE%AE%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L638)，来源许可：GPL-3.0。

<a id="kfee16d56f849"></a>

## A2A 适合哪些多 Agent 协作场景？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

A2A 适合“跨系统、跨团队、跨框架”的 Agent 协作：

- 企业内不同部门 Agent 互调。
- 一个总控 Agent 调用专业分析 Agent。
- 跨供应商 Agent 服务集成。
- 多模态 Agent 和业务 Agent 协作。
- 研究 Agent 调用代码 Agent、数据 Agent、文档 Agent。
- 客服 Agent 调用工单 Agent、订单 Agent、物流 Agent。

不一定需要 A2A 的场景：

- 单应用内部的多个函数。
- 同一个进程里的子 Agent。
- 固定 DAG 工作流。
- 只是为了调用数据库或文件系统。

这些场景用 Function Calling、MCP 或内部工作流可能更简单。

一句话：如果你要接的是工具，用 MCP；如果你要接的是另一个独立 Agent 服务，用 A2A。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/04_MCP%E4%B8%8EA2A%E5%8D%8F%E8%AE%AE%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L668)，来源许可：GPL-3.0。

<a id="k614e7547de69"></a>

## Agent Builder 应该提供哪些能力？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

Agent Builder 是给开发者、业务专家或运营人员构建 Agent 的界面或工具。

核心能力：

- Agent 角色和系统指令配置。
- 模型选择和模型路由配置。
- 工具选择和权限配置。
- MCP Server / API 连接。
- 知识库绑定。
- Memory 策略配置。
- Workflow / 多 Agent 编排。
- 输入输出模板。
- 测试样例和模拟运行。
- Trace 调试。
- 发布、版本、回滚。
- 权限审批和分享。

高级能力：

- 自动生成工具 Schema。
- 从 OpenAPI 生成 Tool。
- 从文档生成知识库。
- 从历史工单生成测试集。
- Prompt 版本对比。
- 多模型 A/B 测试。
- 安全策略预检。

面试中要注意：Builder 不应该让业务人员绕过治理。所有工具、模型、知识库和发布都要经过平台权限和评测门禁。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/07_%E4%BC%81%E4%B8%9A%E7%BA%A7Agent%E5%B9%B3%E5%8F%B0%E4%B8%8E%E4%BA%A7%E5%93%81%E8%90%BD%E5%9C%B0%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L196)，来源许可：GPL-3.0。

<a id="k3af4c3e46bd3"></a>

## Agent Card 的作用是什么？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

Agent Card 是 Remote Agent 的能力说明书，类似服务发现文档。

它通常描述：

- Agent 名称和描述。
- 服务端点 URL。
- 支持的认证方式。
- 支持的输入输出模式。
- 支持的能力，例如 streaming、push notification、state transition history。
- skills 或具体能力列表。
- 版本、提供方、文档链接。

Agent Card 的价值：

- Client 可以发现 Remote Agent 能做什么。
- 上层 Router 可以根据能力选择合适 Agent。
- 企业可以构建 Agent Registry。
- 可以在调用前判断认证和模态是否匹配。

面试中可以类比：OpenAPI 描述 API 服务能力，Agent Card 描述 Agent 服务能力。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/04_MCP%E4%B8%8EA2A%E5%8D%8F%E8%AE%AE%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L583)，来源许可：GPL-3.0。

<a id="k5b2483e9b812"></a>

## Agent Curator 的本质是什么？

Agent Curator 是后台知识维护器。它定期检查 Agent 产生的 Skill、记忆、模板和流程资产，判断哪些应该保留、合并、修订、归档或标记过期。

Curator 的职责：

- 统计 Skill 使用情况。
- 识别重复或过期 Skill。
- 合并相似流程。
- 修订低质量说明。
- 归档长期未用 Skill。
- 生成维护报告。
- 尊重 pinned / official / bundled 资产。
- 不直接删除，优先可恢复归档。

典型触发方式：

- 定期 cron。
- gateway 空闲时触发。
- 手动 dry-run。
- 版本升级后触发检查。
- 大量新 Skill 产生后触发。

Curator 体现了自进化 Agent 的一个关键工程原则：知识资产不能只增不减，否则长期运行后会变成噪声库。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/09_%E8%87%AA%E8%BF%9B%E5%8C%96Agent%E4%B8%8E%E5%A4%9A%E5%B9%B3%E5%8F%B0%E8%BF%90%E8%A1%8C%E6%97%B6%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L373)，来源许可：GPL-3.0。

<a id="k0e2e3ca7a4a0"></a>

## Agent Guardrails 的边界如何快速概括？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

Guardrails 应覆盖四类边界：

1. **输入边界**

   检测恶意请求、越权请求、敏感数据、注入攻击。

2. **工具边界**

   检查工具参数、权限、资源范围、是否需要用户确认。

3. **输出边界**

   检查最终回答是否包含敏感信息、违规内容、虚假承诺。

4. **状态边界**

   防止错误记忆写入、敏感数据进入长期记忆、跨用户数据污染。

Guardrails 可以是规则、分类器、小模型、策略引擎或人工审批。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/01_AIGC%E6%97%B6%E4%BB%A3AI%20Agent%E5%9F%BA%E7%A1%80%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L728)，来源许可：GPL-3.0。

<a id="k5e9c1b165ad3"></a>

## Agent Harness 为什么必须记录完整 Trace？

Agent 的成败往往藏在中间步骤里。完整 Trace 是 Harness 的事实依据。

Trace 应记录：

- 输入消息。
- system / developer / policy 版本。
- 模型调用参数。
- 每次模型输出。
- 工具选择和参数。
- 工具返回、错误和耗时。
- 权限审批请求和结果。
- RAG 检索内容。
- Memory 读写。
- handoff / subagent 事件。
- 环境状态变化。
- token、成本和延迟。
- guardrail 命中。
- final answer 和 artifact。

Trace 有四个用途：

- **Debug**：定位失败发生在哪一步。
- **Grading**：评价轨迹是否合规。
- **Audit**：追踪谁批准了什么动作。
- **Dataset Mining**：把失败 trace 转成新评测样本。

OpenAI 的 trace grading 也体现了这个趋势：Agent 评测不再只看最终输出，而是对端到端决策、工具调用和执行轨迹做结构化评分。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/08_Agent_Harness_Engineering%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L294)，来源许可：GPL-3.0。

<a id="k6681b8dc7736"></a>

## Agent Harness 如何接入 CI/CD 和发布门禁？

Agent 发布对象不仅是代码，还包括模型、prompt、tool schema、MCP Server、memory policy、RAG index、guardrail、workflow 和权限策略。Harness 应该成为这些变更的发布门禁。

典型流程：

1. 开发者修改 prompt、工具或策略。
2. 触发 smoke eval。
3. 关键场景通过后运行 regression eval。
4. 安全集和红队样本检查。
5. 与基线版本对比。
6. 指标达标后允许灰度。
7. 灰度阶段持续收集 trace。
8. 线上失败回流到 Harness。

门禁规则示例：

- smoke set 通过率必须 100%。
- regression set 通过率不能下降超过 1%。
- safety set 零高危越权。
- 平均成本不能上升超过 20%。
- P95 延迟不能超过阈值。
- 新版本不得增加敏感信息泄露风险。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/08_Agent_Harness_Engineering%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L578)，来源许可：GPL-3.0。

<a id="kd057290eeca2"></a>

## Agent Harness 应该输出哪些核心指标？

指标应覆盖质量、安全、稳定性、成本和工程效率。

| 指标类别 | 典型指标 |
| --- | --- |
| 任务质量 | success rate、pass@1、pass@k、exact match、state match |
| 稳定性 | 多次运行方差、一致性、重试成功率 |
| 工具使用 | 工具调用成功率、参数错误率、无效调用率 |
| 轨迹质量 | 平均步骤数、循环调用率、反思次数、handoff 成功率 |
| 安全 | 越权率、注入攻击成功率、敏感信息泄露率、高风险动作确认率 |
| 成本 | token、费用、工具成本、人工审批次数 |
| 延迟 | 平均耗时、P95/P99、超时率 |
| 回归 | 新版本相比基线的提升、退化、失败类型变化 |

生产中还应关注：

- cost per successful task。
- human takeover rate。
- false allow / false block。
- data leakage incidents。
- rollback rate。
- trace coverage。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/08_Agent_Harness_Engineering%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L372)，来源许可：GPL-3.0。

<a id="k6d182fd4e4d2"></a>

## Agent Harness 的任务数据应该如何设计？

Agent Harness 的任务数据不是简单的 prompt 列表，而是可执行任务规格。一个高质量任务样本应该能让不同 Agent 在同样条件下运行，并被同样规则评估。

推荐任务结构：

```yaml
task_id: customer_refund_001
domain: retail
difficulty: medium
risk_level: high
input:
  user_message: "我想退掉昨天买的蓝色外套"
initial_state:
  database_snapshot: snapshots/retail_001.sql
  policy_doc: policies/refund_policy.md
tools:
  allowed:
    - search_order
    - inspect_item
    - create_refund_request
  denied:
    - direct_refund_payment
expected:
  final_response_contains:
    - "需要确认订单"
  final_database_state:
    refund_status: "pending_review"
  forbidden_actions:
    - "直接退款"
grading:
  outcome_weight: 0.5
  safety_weight: 0.3
  trajectory_weight: 0.2
```

关键是把任务从“自然语言请求”升级成“输入 + 环境 + 约束 + 期望状态 + 判分规则”。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/08_Agent_Harness_Engineering%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L153)，来源许可：GPL-3.0。

<a id="kb8eb5f0033af"></a>

## Agent Loop 的核心设计是什么？——每一步的输入输出格式是什么？如果 LLM 返回的 Tool Call 不合法，怎么处理？如果执行完工具后观察结果太长，怎么截断？

**回答：**

Agent Loop 的核心是一个受预算约束的状态转换器，而不是 `while True` 加一次模型调用。每一步至少有以下状态：任务目标、当前计划、历史事件、可用工具、权限与预算、模型提议、工具结果、验证结果和停止原因。

输入给模型的内容应尽量结构化，包括系统策略、用户目标、当前状态摘要、相关证据、允许工具 schema、最近 Observation 和明确的终止条件。模型输出则限定为 `final`、`tool_call`、`ask_user`、`replan` 或 `fail` 等有限动作类型，并要求参数符合 JSON Schema。服务端不能把模型输出直接拼成 shell 命令或 URL。

一个抽象的循环是：

```python
def run_agent_loop(model, task_id, max_steps):
    for step in range(max_steps):
        state = load_checkpoint(task_id)
        if cancelled(state) or budget_exhausted(state):
            return fail("cancelled_or_budget_exhausted")

        proposal = model.decide(build_context(state))
        action = parse_and_validate(proposal, allowed_tools(state))
        if action.is_invalid:
            record_error(state, action.error)
            if action.retryable and state.format_retries < FORMAT_RETRY_LIMIT:
                state.format_retries += 1
                save_checkpoint(state)
                continue
            return fail("invalid_action")

        if action.type == "final":
            return verify_final(action, state)
        if action.type == "ask_user":
            return pause_for_user(action)

        result = execute_with_policy(action, state)
        observation = normalize_and_bound(result)
        state = apply_observation(state, observation)
        save_checkpoint(state)

    return fail("max_steps_exceeded")
```

非法 Tool Call 要区分格式错误、schema 错误、权限错误、业务参数错误和工具不存在。格式错误可以进行一次受限修复；权限和业务错误应直接拒绝并告知模型或用户；工具不存在不能通过模糊匹配随便替换；重复副作用必须依靠幂等键和执行记录判断。每个重试都应消耗预算并记录原因。

Observation 截断不能只取前 N 个字符。应先结构化解析，保留状态码、错误、关键字段、摘要、分页游标、证据 ID 和结果统计；大列表按相关性或确定性规则筛选，并把完整结果放在受控存储中，给模型返回引用。对日志、代码和文档可以采用头尾保留、分块摘要、查询相关片段和按 token 预算压缩。截断后要保留 `truncated=true`，否则模型会把不完整结果误认为完整结果。对于最终决策所需的金额、ID、权限和错误字段，应设置不可丢弃字段，超预算时暂停或请求用户，而不是静默删除。

<a id="deepseek-agent-20260908-q10"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/DeepSeek%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L599)，来源许可：GPL-3.0。

<a id="ke911792a9079"></a>

## Agent Memory

相关内容：[《AI Agent 记忆系统：短期记忆、长期记忆与记忆演化机制》](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/agent/agent-memory.md)

Memory 题会追到信息从哪里来、保存多久、什么时候读取，以及出现过期或冲突后怎么处理。聊天记录、当前任务状态和跨会话记忆需要分别讨论。

常见面试题：

- Agent 的短期记忆和长期记忆有什么区别？
- Agent 记忆系统要解决哪些核心问题？
- 向量记忆和 Markdown 记忆分别适合什么场景？
- Auto Memory 是什么？它为什么不能无限自动写入？
- 哪些团队共享记忆适合走 Git 和 Code Review，哪些更适合数据库？
- 记忆压缩、记忆过期、记忆冲突应该怎么处理？
- 如何避免长期记忆污染上下文？
- 面试里怎么讲“有记忆”不是简单保存聊天记录？

![Agent 记忆分类全景图](https://oss.javaguide.cn/github/javaguide/ai/agent/agent-memory-memory-taxonomy.svg)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/interview-questions/agent-interview-questions.md#L42)，来源许可：Apache-2.0。

<a id="k7e6ed18c606e"></a>

## Agent Memory 和普通聊天历史有什么区别？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

普通聊天历史通常只是按时间顺序保存消息；Agent Memory 是经过筛选、结构化、检索和治理的长期信息资产。

| 维度 | 聊天历史 | Agent Memory |
| --- | --- | --- |
| 存储方式 | 原始消息列表 | 结构化记录、向量、图、事件、摘要 |
| 写入策略 | 默认保存全部 | 选择性写入 |
| 检索方式 | 最近 N 轮或全文搜索 | 语义检索、时间检索、任务检索、规则检索 |
| 更新机制 | 很少更新 | 可增删改、合并、衰减、遗忘 |
| 风险控制 | 弱 | 隐私、权限、来源、过期、污染治理 |
| 作用 | 维持对话连续 | 支撑个性化、任务状态、经验复用、工具优化 |

例如“用户喜欢科幻电影”如果只存在聊天历史里，过几周后很难被准确找回；如果被提取为个人记忆，就可以在推荐电影、礼物或活动时被检索和使用。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/05_Agent%E8%AE%B0%E5%BF%86%E4%B8%8E%E4%B8%8A%E4%B8%8B%E6%96%87%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L82)，来源许可：GPL-3.0。

<a id="ke80170af92a9"></a>

## Agent Pattern、Prompt Pattern、Workflow Pattern 有什么区别？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

| 类型 | 关注点 | 典型例子 | 风险 |
| --- | --- | --- | --- |
| Prompt Pattern | 如何引导模型输出更好的推理或格式 | CoT、Plan-and-Solve、Self-Consistency | 依赖模型遵循指令，稳定性有限 |
| Agent Pattern | 模型如何循环感知、推理、行动、反思 | ReAct、Reflection、Tool Use、Memory | 工具副作用、上下文漂移、成本增加 |
| Workflow Pattern | 系统如何用确定性流程编排模型和工具 | Router、State Machine、Human Approval、DAG | 灵活性下降，流程设计成本高 |

三者不是互斥关系。一个成熟 Agent 系统通常会同时使用：

- Prompt Pattern 提升单次模型推理质量。
- Agent Pattern 让模型具备多步行动能力。
- Workflow Pattern 用工程边界约束模型行为。

例如，一个代码修复 Agent 可以使用 Plan-and-Solve 生成计划，用 ReAct 循环读取文件和运行测试，再用 Workflow 强制经过“生成 diff -> 运行测试 -> 人工 review -> 创建 PR”的流程。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/03_Agent%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81%E7%BC%96%E6%8E%92%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L73)，来源许可：GPL-3.0。

<a id="ke4d868a0e565"></a>

## Agent Runner 如何保证可复现、可对比、可回放？

Agent Runner 是 Harness 的执行核心。它要保证同一个任务在不同版本上尽量公平可比。

关键设计：

- 固定 model / prompt / tool / policy / memory / RAG index 版本。
- 固定温度、top_p、最大轮数、最大工具调用数。
- 固定环境快照和随机种子。
- 每个任务独立 sandbox。
- 每次运行分配 run_id。
- 记录完整版本组合。
- 工具调用结果可缓存或可重放。
- 支持 timeout、cancel、retry 和 cleanup。
- 支持批量并发，但不能让任务之间共享脏状态。

Runner 输出至少包含：

- run_id。
- task_id。
- agent_version。
- final_status。
- trace_id。
- cost。
- latency。
- score。
- failure_tags。
- artifacts。

面试中可以说：Runner 的核心不是“把 Agent 调起来”，而是让每次运行成为可复现的实验。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/08_Agent_Harness_Engineering%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L261)，来源许可：GPL-3.0。

<a id="k281f37f5676e"></a>

## Agent 为什么会选错相似工具？

系统里有两个名字很像的工具。`query_after_sale_policy` 查询通用售后政策，不需要具体订单；`check_after_sale_eligibility` 接收订单号，判断这笔订单能否申请售后。用户已经提供订单号时，Agent 本应调用后一个工具，却选了前一个。它返回的政策说明可能没有事实错误，却回答不了“我的订单到底能不能申请”。

排查要先看 Trace。订单号没有进入模型上下文，说明状态组装出了问题；模型看到了订单号却仍然选错，才继续检查两个工具的名称、描述和参数是否容易混淆。固定输入后一次只改工具描述、Prompt 或模型，也能判断究竟是哪项修改让错误消失。

修复时，先把两个工具的职责和前置条件写清楚，并把订单号放进简短的状态摘要。如果路由规则能够由代码确定，例如只有拿到订单号才能检查具体订单，就直接缩小这一轮暴露给模型的工具集合。代码会先排除不满足前置条件的工具，没有订单号的请求也不会被 Prompt 里的固定优先级带偏。

最后把“有订单号”“没有订单号”“订单不属于当前用户”和“订单号格式错误”放进同一组回归测试。样本多了以后，再用工具混淆矩阵观察两个工具是否仍被频繁选错。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/interview-questions/agent-project-interview-guide.md#L377)，来源许可：Apache-2.0。

<a id="ke1b61325a2b1"></a>

## Agent 为什么需要 Human-in-the-loop？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

Agent 的不确定性来自模型推理、工具执行、环境变化和用户目标模糊。Human-in-the-loop 是把人类判断放在关键边界上。

典型场景：

- 删除、覆盖、发布、支付、发邮件等不可逆操作。
- 访问敏感数据。
- 低置信度或多方案选择。
- 需求不明确。
- 安全策略触发。
- 需要业务负责人审批。

交互方式：

- 让用户确认计划。
- 在工具执行前弹出权限审批。
- 生成 diff 后等待确认。
- 给出多个方案供选择。
- 失败时请求补充信息。

面试要点：企业级 Agent 不追求完全无人值守，而是把自主执行限制在可控边界内。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/01_AIGC%E6%97%B6%E4%BB%A3AI%20Agent%E5%9F%BA%E7%A1%80%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L291)，来源许可：GPL-3.0。

<a id="k756c14959125"></a>

## Agent 互操作为什么需要标准化接口？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

AIGC 时代的 Agent 不再只是聊天窗口，而是需要连接工具、数据、服务、其他 Agent 和真实业务系统。没有标准协议时，每个应用都要单独适配：

- 模型如何发现工具？
- 工具参数如何描述？
- 工具结果如何返回？
- 文件、数据库、知识库如何作为上下文暴露？
- 多个 Agent 如何互相发现、发消息、交接任务？
- 权限、认证、审计、流式响应如何统一？

如果每个模型应用、每个工具、每个 Agent 都用私有协议，生态会变成大量孤岛。协议标准化的价值是把“模型能力”“工具能力”“Agent 服务能力”解耦，让不同组件可以被复用、治理和替换。

可以用三层来理解：

| 层级 | 代表能力 | 解决的问题 |
| --- | --- | --- |
| Function Calling / Tool Use | 单个模型调用应用内工具 | 模型如何调用函数 |
| MCP | Agent 应用连接外部工具、资源、提示模板 | 工具和上下文如何标准化接入 |
| A2A | Agent 服务之间通信与协作 | Agent 如何互相发现、请求、交付结果 |

面试中可以总结：Function Calling 是工具调用能力，MCP 是工具和上下文接入协议，A2A 是 Agent 服务互操作协议。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/04_MCP%E4%B8%8EA2A%E5%8D%8F%E8%AE%AE%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L44)，来源许可：GPL-3.0。

<a id="k6a7dae01564e"></a>

## Agent 优化有哪些常见手段？

**回答：**

可以从模型、上下文、工具、编排、系统和评估六层回答：

1. **模型层：** 模型路由、提示模板、结构化输出、必要时微调/蒸馏，控制温度和最大输出。
2. **上下文层：** 只注入任务相关信息，做摘要、压缩、去重、优先级排序和检索，避免无边界拼接历史。
3. **工具层：** 减少工具重叠，提供清晰 schema、示例、错误码、权限和幂等语义，让工具返回机器可读结果。
4. **编排层：** 简单任务使用 Workflow，复杂任务使用图式状态机；限制最大步数，加入路由、验证、反思和人工审批。
5. **系统层：** 并行调用、缓存、批处理、异步化、超时、重试、熔断、限流、checkpoint 和灰度发布。
6. **评估层：** 建立任务集和轨迹集，评估最终结果、工具选择、参数正确率、过程效率、成本、延迟和安全。

优化的原则是先测量再修改。Agent 的问题可能来自错误规划，也可能来自工具契约、检索证据、上下文过长或服务超时；只改 Prompt 往往会把系统问题掩盖成偶然的模型波动。

<a id="alibaba-agent-20260802-q5"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L844)，来源许可：GPL-3.0。

<a id="k08ebcbc936ff"></a>

## Agent 可观测性和 tracing 应该记录什么？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

Agent tracing 应记录：

- 用户输入。
- 系统指令版本。
- 模型调用参数。
- 每次模型输出。
- 工具调用名称、参数、结果、耗时。
- handoff 事件。
- guardrail 结果。
- 权限审批记录。
- token、成本、延迟。
- 错误和重试。
- 最终输出。

可观测性的目标：

- Debug 为什么选错工具。
- 复现失败案例。
- 统计成本和延迟。
- 做安全审计。
- 构造评测数据集。
- 持续优化 prompt、工具和策略。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/01_AIGC%E6%97%B6%E4%BB%A3AI%20Agent%E5%9F%BA%E7%A1%80%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L752)，来源许可：GPL-3.0。

<a id="ke409dd5fec16"></a>

## Agent 和 Workflow 应该如何取舍？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

可以从任务确定性、风险和反馈方式来判断。

| 场景 | 更适合 Agent | 更适合 Workflow |
| --- | --- | --- |
| 任务边界 | 模糊、需要探索 | 明确、步骤稳定 |
| 工具选择 | 需要动态判断 | 工具固定 |
| 结果验证 | 需要多轮信息收集 | 有清晰规则 |
| 风险等级 | 低到中，可人工兜底 | 高风险、强合规 |
| 用户期望 | 希望系统自主推进 | 希望系统可预测 |

经验原则：

- 可枚举、可审计、强合规的任务优先 Workflow。
- 需要探索、推理、动态选择工具的任务适合 Agent。
- 生产系统里常用混合模式：Workflow 管大边界，Agent 处理局部不确定性。

例如报销审批、身份认证、支付转账更适合 Workflow；代码排障、研究调研、复杂数据分析更适合 Agent；企业客服常用 Workflow 控制关键节点，再让 Agent 负责理解用户意图和生成回复。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/03_Agent%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81%E7%BC%96%E6%8E%92%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L95)，来源许可：GPL-3.0。

<a id="kae85c382778e"></a>

## Agent 基础

相关内容：[《AI Agent 核心概念：Agent Loop、Plan-and-Execute、结构化任务契约、Agentic Workflows、Tools 注册》](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/agent/agent-basis.md)、[《多 Agent 协作系统设计：任务拆分、状态共享、冲突处理与失败恢复》](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/agent/multi-agent.md)

工具调用完整链路、权限、二次确认、幂等、审计、超时和 Java 示例，见 [结构化输出与 Function Calling](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/llm-basis/structured-output-function-calling.md)；任务完成率、工具调用和执行轨迹等评测指标，见 [Agent 应用怎么评测](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/llm-basis/llm-evaluation.md#agent-应用怎么评测)。

这部分通常从 Agent 的定义开始，随后追问运行循环和编排方式。准备时要能分清 Chatbot、Workflow 与 Agent 在任务路径、状态和工具使用上的差别。

常见面试题：

- AI Agent 是什么？和普通 Chatbot 有什么区别？
- Agent = LLM + Planning + Memory + Tools 这条公式怎么理解？
- Agent Loop 的完整流程是什么？
- Agent 和传统编程、Workflow 的核心区别是什么？
- ReAct、Plan-and-Execute、Reflection、Multi-Agent 分别适合什么场景？
- Tools 注册时，工具 description 为什么很关键？
- 什么时候用纯 Agent，什么时候用 Workflow 或 Agentic Workflow？
- Multi-Agent 协作的主要问题是什么？为什么生产里不能盲目上多 Agent？

![AI Agent 核心架构](https://oss.javaguide.cn/github/javaguide/ai/agent/agent-core-arch.png)

![Agent Loop 工作流程](https://oss.javaguide.cn/github/javaguide/ai/agent/agent-loop-flow.png)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/interview-questions/agent-interview-questions.md#L19)，来源许可：Apache-2.0。

<a id="k517564a672da"></a>

## Agent 如何做自我总结、状态恢复和跨会话连续性？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

典型方案：

- 每次长任务结束时生成 session summary。
- 将计划、已完成步骤、未完成事项、关键文件、失败尝试保存为结构化状态。
- 下次 resume 时先注入摘要，再按需加载历史细节。
- 对项目约定和用户偏好写入长期记忆。
- 对工具失败和环境信息保存为诊断记录。

好的恢复摘要应包含：

- 用户目标。
- 当前进度。
- 修改过的文件。
- 已运行的命令和结果。
- 未解决问题。
- 下一步建议。
- 重要约束和风险。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/01_AIGC%E6%97%B6%E4%BB%A3AI%20Agent%E5%9F%BA%E7%A1%80%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L671)，来源许可：GPL-3.0。

<a id="k47d9308c55d6"></a>

## Agent 如何选择工具、调用工具并处理工具失败？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

推荐流程：

1. **工具发现**

   将当前可用工具、能力范围、参数 Schema 注入上下文，或通过 MCP/tool search 动态发现。

2. **工具选择**

   模型根据任务意图选择工具；对于高风险工具，先解释意图并等待授权。

3. **参数生成**

   使用 JSON Schema 约束参数；必要时让模型先生成计划，再生成工具参数。

4. **执行与观测**

   工具执行器返回结构化结果、错误码、stderr/stdout、资源链接或状态变更。

5. **失败恢复**

   根据错误类型重试、换工具、缩小范围、请求用户输入或终止。

6. **结果验证**

   检查是否满足目标，例如测试是否通过、文件是否存在、数据库状态是否符合预期。

工具失败分类：

- 参数错误：让模型修正参数。
- 权限错误：请求用户授权或降级。
- 环境错误：提示依赖缺失。
- 网络错误：重试或换源。
- 语义错误：重新规划。
- 安全错误：停止执行。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/01_AIGC%E6%97%B6%E4%BB%A3AI%20Agent%E5%9F%BA%E7%A1%80%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L252)，来源许可：GPL-3.0。

<a id="kf5577ca584a6"></a>

## Agent 如何避免把错误经验固化为长期知识？

需要从写入、检索、维护三个阶段治理。

写入阶段：

- 只写高置信、可验证、稳定的信息。
- 区分事实、偏好、猜测、失败教训。
- 工具输出和网页内容默认不可信。
- 写入前做去重、脱敏和 prompt injection 检测。
- 高风险经验需要用户确认。

检索阶段：

- 记忆带 source、time、confidence、scope。
- 当前用户指令优先于长期记忆。
- 过期记忆降权。
- 冲突记忆不直接注入，先澄清或选择最新可信来源。

维护阶段：

- Curator 定期识别陈旧和重复知识。
- 低质量 Skill 标记 stale。
- 错误记忆支持删除和更正。
- 线上失败回流到 Eval Harness。
- 关键知识资产版本化和可回滚。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/09_%E8%87%AA%E8%BF%9B%E5%8C%96Agent%E4%B8%8E%E5%A4%9A%E5%B9%B3%E5%8F%B0%E8%BF%90%E8%A1%8C%E6%97%B6%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L462)，来源许可：GPL-3.0。

<a id="k2e84e9c7c801"></a>

## Agent 宿主与框架选型

**回答：**

框架选型首先取决于任务约束。需要明确系统是内部助手、生产业务入口，还是面向用户的多模态工作台，再评估宿主能否支持所需模型、工具接入、状态持久化、权限隔离、人工确认、观测和部署方式。

**宿主提供运行环境，框架提供开发抽象，业务代码定义具体能力。** 使用现成宿主并不等于没有工程工作，自建框架也不代表能力更强。回答应展示自己为什么采用某种组合，以及它在哪些需求下会失效。

<a id="baidu-aigc-multimodal-agent-20260922-20260924-r1-q4-1"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%99%BE%E5%BA%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1462)，来源许可：GPL-3.0。

<a id="k92a6ee2a752c"></a>

## Agent 常用评测基准有哪些？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

| 基准 | 评估重点 |
| --- | --- |
| SWE-bench / SWE-bench Verified | 真实 GitHub issue 修复能力 |
| WebArena | 浏览器环境中的网页任务执行 |
| OSWorld | 操作系统/GUI 任务执行 |
| GAIA | 需要工具和多步推理的通用助理任务 |
| AgentBench | 多环境 Agent 能力 |
| τ-bench | 工具-用户-Agent 多轮交互和规则遵循 |
| HumanEval/MBPP | 代码生成基础能力 |
| 自建业务评测 | 企业流程、API 状态变更、规则合规 |

生产评估不要只看一次成功率，还要看：

- pass@k 或多次运行稳定性。
- 工具调用错误率。
- 任务完成时间。
- 成本。
- 安全拒绝准确率。
- 人工接管率。
- 回滚率。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/01_AIGC%E6%97%B6%E4%BB%A3AI%20Agent%E5%9F%BA%E7%A1%80%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L779)，来源许可：GPL-3.0。

<a id="kcc81de629871"></a>

## Agent 平台和单个 Agent 应用有什么区别？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

| 维度 | 单个 Agent 应用 | 企业级 Agent 平台 |
| --- | --- | --- |
| 目标 | 解决一个具体场景 | 支撑多个团队和多个场景 |
| 工具接入 | 应用内写死 | Tool Registry / MCP Registry |
| 模型调用 | 单应用配置 | 模型网关统一路由和治理 |
| 权限 | 应用自管 | 企业 IAM / RBAC / ABAC |
| 记忆和数据 | 局部存储 | 多租户隔离、统一存储策略 |
| 评测 | 手工或少量脚本 | Eval Harness + 回归门禁 |
| 发布 | 应用部署 | Agent / Prompt / Tool / Policy 联合版本 |
| 监控 | 日志和错误 | Trace、成本、质量、安全、审计全链路 |

单个 Agent 应用关注“这个 Agent 能不能完成任务”；企业 Agent 平台关注“很多 Agent 能不能持续、合规、稳定地运行”。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/07_%E4%BC%81%E4%B8%9A%E7%BA%A7Agent%E5%B9%B3%E5%8F%B0%E4%B8%8E%E4%BA%A7%E5%93%81%E8%90%BD%E5%9C%B0%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L72)，来源许可：GPL-3.0。

<a id="k50e1aeba7721"></a>

## Agent 平台如何建设可观测性和审计？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

本节关注企业平台需要提供的可观测性与审计产品能力；trace 里具体应该记录什么、如何定位失败、如何做 LLM-as-Judge 与失败样本回流，见 [06_Agent安全评测与AgentOps高频考点.md](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/06_Agent安全评测与AgentOps高频考点.md)。

可观测性关注运行质量，审计关注责任追踪。

可观测性：

- 请求量。
- 任务成功率。
- 工具成功率。
- 平均延迟和 P95/P99。
- token 和费用。
- 人工接管率。
- 失败分类。
- guardrail 拦截率。
- 用户满意度。

审计：

- 谁发起任务。
- 哪个 Agent 执行。
- 使用哪个模型和 prompt。
- 调用哪些工具。
- 访问哪些资源。
- 权限如何批准。
- 是否产生外部副作用。
- 最终交付是什么。

企业平台应支持：

- Trace 链路查询。
- 按租户和用户过滤。
- 敏感字段脱敏。
- 日志保留策略。
- 审计导出。
- 安全告警。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/07_%E4%BC%81%E4%B8%9A%E7%BA%A7Agent%E5%B9%B3%E5%8F%B0%E4%B8%8E%E4%BA%A7%E5%93%81%E8%90%BD%E5%9C%B0%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L714)，来源许可：GPL-3.0。

<a id="k0c26264a2c05"></a>

## Agent 平台如何支持长任务和后台任务？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

长任务需要任务系统，而不是只依赖同步对话。

核心能力：

- Task id。
- 状态机：queued、running、waiting_approval、succeeded、failed、cancelled、timeout。
- 任务队列。
- 断点恢复。
- 超时和取消。
- 进度事件。
- 后台通知。
- 人工审批。
- 结果归档。
- 幂等 key。

适合后台任务的场景：

- 长文档分析。
- 代码仓库扫描。
- 数据报表生成。
- 多网页调研。
- 批量工单处理。
- 视频、图片、音频处理。

面试中可以说：企业 Agent 平台必须从“请求-响应”架构升级到“任务-事件-状态”架构。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/07_%E4%BC%81%E4%B8%9A%E7%BA%A7Agent%E5%B9%B3%E5%8F%B0%E4%B8%8E%E4%BA%A7%E5%93%81%E8%90%BD%E5%9C%B0%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L754)，来源许可：GPL-3.0。

<a id="kcf08ee75aa1c"></a>

## Agent 平台如何设计发布、灰度和回滚？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

本节关注平台如何把发布能力产品化，例如版本包、灰度维度、回滚开关和状态兼容；AgentOps 视角下的评测门禁、失败回流和事故响应，见 [06_Agent安全评测与AgentOps高频考点.md](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/06_Agent安全评测与AgentOps高频考点.md)。

Agent 发布对象包括：

- prompt。
- model。
- tool schema。
- MCP Server。
- workflow。
- memory policy。
- guardrail policy。
- skill。
- RAG index。
- permission policy。

发布流程：

1. 版本打包。
2. 运行 smoke eval。
3. 运行 regression eval。
4. 安全策略扫描。
5. 小流量灰度。
6. 指标监控。
7. 扩大灰度或回滚。

灰度维度：

- 用户。
- 租户。
- 团队。
- 场景。
- 工具权限。
- 模型版本。

回滚要求：

- 记录每次任务使用的版本组合。
- 保留旧版本 prompt、工具和策略。
- 工作流状态向前/向后兼容。
- 外部副作用有补偿方案。
- RAG index 和 Memory 策略可版本化。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/07_%E4%BC%81%E4%B8%9A%E7%BA%A7Agent%E5%B9%B3%E5%8F%B0%E4%B8%8E%E4%BA%A7%E5%93%81%E8%90%BD%E5%9C%B0%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L668)，来源许可：GPL-3.0。

<a id="k321e5f6d2d7d"></a>

## Agent 怎么通过定期总结，把历史记录转化为长期记忆？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

周期性总结可以把大量历史记录压缩为候选事实、决策、稳定偏好和可复用经验。流程宜为：选择尚未总结的范围，提取候选，关联证据，检查主体与权限，去重和冲突处理，审核后提交，再推进处理水位。

原始日志、阶段摘要和长期记忆应分开。一次失败、临时决定或模型自己的猜测不应直接成为稳定事实。总结任务需要读取已删除与已否决标记，防止从旧日志重新生成用户已经撤回的信息。

增量执行采用版本或消息水位，使重试不会重复写入；写入前比较当前记忆版本，避免覆盖更新。评估总结覆盖率、误提升率和删除一致性，而不只看压缩比例。记忆整理任务可定期触发，也可在上下文压缩前触发，具体机制由系统实现决定。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/05_Agent%E8%AE%B0%E5%BF%86%E4%B8%8E%E4%B8%8A%E4%B8%8B%E6%96%87%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L401)，来源许可：GPL-3.0。

<a id="kb6ae8b6d0a0f"></a>

## Agent 理解、问题处理与 Tool 定位

**回答：**

Agent 可以理解为围绕目标持续执行“观察—决策—行动—反馈”的系统：模型根据当前上下文选择下一步，外部工具执行动作，工具结果进入后续决策，并由运行环境限制权限、步数和资源。

需要区分模型本身与整个系统。模型可能提出调用建议，真正的授权、参数校验和执行由应用完成。业务中也可以让固定工作流负责关键步骤，只在需要理解与选择的位置使用模型，不必把所有流程都交给自由规划。

<a id="baidu-aigc-multimodal-agent-20260922-20260924-r2-q3-1"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%99%BE%E5%BA%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1738)，来源许可：GPL-3.0。

<a id="k3595b3374ba8"></a>

## Agent 的工具调用成功率是怎么定义的？项目最初的数据是多少，后来如何提升？

**回答：**

“工具调用成功”至少要分层定义，不能只看 HTTP 200。第一层是工具选择正确；第二层是参数 schema、类型和业务约束正确；第三层是执行成功且没有超时、重复副作用或权限违规；第四层是结果被 Agent 正确理解并用于完成任务。端到端任务成功率通常比单次调用成功率更有意义。

可以分别统计：

$$
\mathrm{ExecutionSuccess}=\frac{\text{执行成功的合法调用数}}{\text{发起的工具调用数}}
$$

$$
\mathrm{TaskSuccess}=\frac{\text{满足任务验收条件的样本数}}{\text{全部有效任务数}}
$$

分母要说明是否排除用户取消、外部服务不可用和无权限请求；重试后的成功要同时记录首调成功率与最终成功率，避免用大量重试掩盖问题。对写操作还要统计重复副作用率和人工拦截率。

提升通常来自工具描述去重、结构化输出、参数枚举和示例、服务端校验、错误码可读化、模型路由、有限重试、幂等键、结果验证以及针对失败轨迹的回归集。工具多时还可先按意图缩小候选集合，减少相似工具误选。

“最初的数据是多少”必须引用真实评测集或线上 trace，说明样本量、时间窗口和口径；若没有可靠记录，应直接说明。面试中可讲自己的分析与改进方法，但不能用虚构百分比替代证据。

<a id="pinduoduo-ai-agent-20260816-q13"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E6%8B%BC%E5%A4%9A%E5%A4%9A%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L329)，来源许可：GPL-3.0。

<a id="k7ae693af5eb5"></a>

## Agent 的目标、行动与反馈分别意味着什么？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

AI Agent 是以大模型为核心，能够围绕目标进行感知、规划、调用工具、执行动作、观察反馈、维护状态并持续迭代的智能系统。

一个简化定义：

```math
\text{Agent} = \text{LLM} + \text{Tools} + \text{Memory} + \text{Planning} + \text{Control Loop} + \text{Environment}
```
相比普通大模型问答，Agent 的关键不在“回答一句话”，而在“完成一个任务”。它需要：

- 理解用户目标。
- 拆解任务步骤。
- 选择合适工具。
- 调用外部 API、数据库、浏览器、文件系统或代码环境。
- 根据工具结果修正计划。
- 在多轮交互中保持状态。
- 在危险操作前请求确认。
- 输出可验证结果。

**面试金句：**

大模型是 Agent 的大脑，工具是手脚，记忆是上下文连续性，规划是任务分解，权限和评估是工程落地的刹车系统。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/01_AIGC%E6%97%B6%E4%BB%A3AI%20Agent%E5%9F%BA%E7%A1%80%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L48)，来源许可：GPL-3.0。

<a id="kf24a2567e786"></a>

## Agent 的评测基准与多步可靠性问题如何应对？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐ (3/5)**

Agent 评测要在可执行环境中运行任务并检查终态；多步任务的成功率随步数连乘下降，工程上需要用检查点、高危确认和沙箱让错误可以回退且不直接生效。感知、决策、执行的闭环和这三项机制如图 6-6 所示：

1. **可执行基准。** OSWorld（2024）包含 369 个真实电脑任务，在虚拟机中执行，用脚本检查终态，环境支持 Ubuntu、Windows 和 macOS；论文另有 43 个 Windows 任务用于分析[26]。在原始协议下，人类成功率为 72.36%，当时最好的模型为 12.24%，失分主要来自 GUI 定位和操作知识[26]。后来的榜单、步数上限和 OSWorld-Verified 都修改过评测协议，不同版本的成功率不能直接比较，上文 72.36% 与 12.24% 的差距是 2024 年原始协议下的结果。AndroidWorld 在 20 个真实安卓应用上构建了 116 个程序化任务，任务参数随机生成，以避免模型记住测试题[27]；WebArena 则面向自托管网站上的任务[28]。

2. **多步衰减。** 没有回滚机制时，任务成功要求每一步都成功，端到端成功率随步数连乘下降：

$$
P_{\text{task}}=\prod_{t=1}^{n}p_t\approx p^{\,n}
$$

其中 $`p_t`$ 为第 $`t`$ 步的成功率，$`n`$ 为步数。若单步成功率 $`p=0.95`$、任务需要 $`n=20`$ 步，则 $`0.95^{20}\approx 0.36`$，这是一个算术示例，并非某个产品的实测值。$`p`$ 提高到 0.99 时，同样 20 步的成功率约回升到 0.82。另一个方向是把高频操作序列封装为单个工具，以缩短 $`n`$。

3. **可靠性机制。** 工程上常用三项机制：

    （1）检查点。关键节点保存状态，失败时回到最近的检查点，不必从头开始。

    （2）高危确认。删除、支付、发送类操作设置二次确认，必要时直接拒绝执行。

    （3）沙箱。操作先在隔离环境中跑通，再作用于真实环境，这与幻觉治理中「模型输出不直接生效」的原则一致。

![GUI Agent 感知决策执行闭环示意图](https://raw.githubusercontent.com/WeThinkIn/AIGC-Interview-Book/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E5%A4%9A%E6%A8%A1%E6%80%81%E5%9F%BA%E7%A1%80%EF%BC%88%E7%B2%BE%E5%8D%8E%E7%89%88%EF%BC%89/images/6-6-GUIAgent感知决策执行闭环示意图.png)

<p align="center">图 6-6 GUI Agent 感知决策执行闭环示意图</p>

> **面试速答**：Agent 评测要在环境中执行任务并检查终态。OSWorld 2024 年原始协议下的 369 个任务上，人类成功率为 72.36%，当时最好的模型为 12.24%，后来的协议已经改变。没有回滚时成功率随步数连乘，0.95 的 20 次方约为 0.36，工程上用检查点、高危确认和沙箱应对。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E5%A4%9A%E6%A8%A1%E6%80%81%E5%9F%BA%E7%A1%80%EF%BC%88%E7%B2%BE%E5%8D%8E%E7%89%88%EF%BC%89/6_AI%E5%A4%9A%E6%A8%A1%E6%80%81%E4%B8%8B%E6%B8%B8%E5%BA%94%E7%94%A8%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L375)，来源许可：GPL-3.0。

<a id="k98cb3547adb1"></a>

## agent 调用工具这个过程是怎么优化的？

**回答：**

该条目未提供足够的具体题面或项目事实，不能为了完整而补造内部实现、指标或个人经历。面试中应先澄清问题边界，再按“目标与约束 -> 核心机制 -> 方案取舍 -> 正确性/复杂度 -> 验证与风险”回答，并把没有证据的部分明确标注为假设。

<a id="tencent-llm-collection-20260903-q140"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E8%85%BE%E8%AE%AF%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1692)，来源许可：GPL-3.0。

<a id="k0a367f7427d1"></a>

## Agent 身份和用户身份为什么要分开？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

用户身份代表“谁发起任务”，Agent 身份代表“哪个自动化主体在执行”。二者必须分开，否则会出现权限放大。

分开的原因：

- 同一用户可以启动不同风险等级的 Agent。
- 同一 Agent 可被多个用户使用。
- Agent 应有自己的工具范围和凭证。
- 审计需要知道是用户手动操作还是 Agent 自动操作。
- 企业需要限制 Agent 不能继承用户所有权限。

推荐做法：

- 每次工具调用携带 user_id 和 agent_id。
- Agent 使用 scoped credential。
- 高风险操作使用 on-behalf-of 模式并要求用户确认。
- 审计日志同时记录用户、Agent、任务和工具。
- Agent 权限默认小于等于用户权限。

一句话：用户授权不等于 Agent 可自动行动，Agent 身份是企业控制自动化风险的关键边界。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/07_%E4%BC%81%E4%B8%9A%E7%BA%A7Agent%E5%B9%B3%E5%8F%B0%E4%B8%8E%E4%BA%A7%E5%93%81%E8%90%BD%E5%9C%B0%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L392)，来源许可：GPL-3.0。

<a id="kd79c6236ef7b"></a>

## Agent 轨迹数据如何用于训练、评测和自我改进？

Agent 轨迹数据是指模型在执行任务时产生的完整对话、推理、工具调用、工具结果、环境状态和最终输出。它既可以用于评测，也可以用于训练下一代工具调用模型。

典型用途：

- 失败分析。
- Eval Harness 样本构造。
- SFT 数据生成。
- RL rollout。
- Tool Call Parser 训练。
- Reward Function 设计。
- Skill 发现。
- 工具 schema 优化。
- 用户行为洞察。

轨迹数据应包含：

- messages。
- tool calls。
- tool results。
- reasoning 或 scratchpad。
- environment state。
- final answer。
- reward / score。
- failure tags。
- model / prompt / tool version。

注意：轨迹数据高度敏感，包含用户输入、工具结果和潜在密钥，必须脱敏、授权和权限隔离后才能用于训练。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/09_%E8%87%AA%E8%BF%9B%E5%8C%96Agent%E4%B8%8E%E5%A4%9A%E5%B9%B3%E5%8F%B0%E8%BF%90%E8%A1%8C%E6%97%B6%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L601)，来源许可：GPL-3.0。

<a id="k1ef21c519fc3"></a>

## Agent 项目的 Badcase 应该怎么复盘？

只说“模型答错了，然后优化 Prompt”，无法说明根因是否找对。一个合格的 Badcase 复盘要留下可复现的定位证据。

可以按下面七步回答：

1. **保存现场。** 保留输入、模型与 Prompt 版本、上下文、检索结果、工具请求与响应及外部状态。
2. **描述现象。** 写清预期结果、实际结果和影响范围。
3. **分层假设。** 分别检查数据、检索、上下文、模型、工具、编排和第三方系统。
4. **控制变量。** 一次只替换一个变量，避免同时修改模型、Prompt 和检索参数。
5. **确认根因。** 拿出能够稳定复现问题的证据，不能停在相关性上。
6. **实施修复。** 说明修复放在哪一层，并解释为什么不能只改 Prompt。
7. **加入回归用例。** 把原始 Case 和相邻边界 Case 加入回归集，再观察线上指标。

下面看两个容易被追问的例子。回答自己的项目时，先交代证据属于真实生产事故、离线故障注入还是设计预案。没有生产记录，就不要把模拟复现说成线上事故。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/interview-questions/agent-project-interview-guide.md#L361)，来源许可：Apache-2.0。

<a id="k3612eb161d72"></a>

## Agent 项目的技术选型应该回答哪些问题？

前五个问题用于解释每一项选择，第六个问题决定方案能否经得住验证：

1. 当时的业务约束是什么？
2. 比较过哪些候选方案？
3. 为什么当前方案更合适？
4. 它牺牲了什么，又如何控制代价？
5. 用什么评测或运行数据验证？
6. 如果约束变化，什么情况下会换方案？

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/interview-questions/agent-project-interview-guide.md#L151)，来源许可：Apache-2.0。

<a id="kad0c205ea8f9"></a>

## Agent 项目的指标应该怎么讲？

面试时先讲任务有没有完成，再补充执行过程、成本和安全。一个脱离测试集与统计口径的“准确率 85%”，很难说明项目是否真的可用。

| 要回答的问题 | 可用指标                                      |
| ------------ | --------------------------------------------- |
| 任务完成了吗 | 任务完成率、最终业务状态正确率、事实有据率    |
| 执行过程对吗 | 工具选择与参数正确率、多余调用率、越权调用数  |
| 成本能接受吗 | 端到端 P50/P95、模型调用数、Token、单任务成本 |
| 失败后可控吗 | 故障恢复率、转人工率、重复副作用数、误拦截率  |

说完指标，还要交代测试集从哪里来、怎样判定成功、同一个任务运行几次，以及相对哪个版本比较。已经上线的项目可以再补自助解决率、处理时长等业务指标，同时说明统计时间和对照组。项目还没有上线，就展示离线评测集和错误分布，不要把实验结果包装成生产数据。

售后案例中，工单是否正确创建属于 Outcome；调用了哪些工具、参数是否正确、有没有越权或重复执行，则要回到 Trace 检查。开放任务可能有多条正确路径，评测时先验证最终业务状态和必须满足的安全规则，不要求执行顺序和一条 Golden Sequence 完全一致。

一条固定输入和成功条件组成一个 Task，每次执行是一次 Trial。Agent 输出有随机性，关键任务需要运行多次。Grader 可以使用代码规则、LLM-as-Judge 或人工，Eval Harness 负责执行这些 Trial、保存 Trace 并汇总结果。

![Eval Harness 从读取评测集到执行评分并进入发布门禁的运行流程](https://oss.javaguide.cn/github/javaguide/ai/llm/llm-evaluation-eval-harness-flow.webp)

完整方法可以看 [AI 应用评测体系](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/llm-basis/llm-evaluation.md)。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/interview-questions/agent-project-interview-guide.md#L340)，来源许可：Apache-2.0。

<a id="kfe3b207121a5"></a>

## Agent 项目面试到底在考什么？

先看面试官为什么这么问。Agent 项目不像 CRUD 项目有成熟的评价标准，面试官没法只凭“做过”两个字判断你的水平，只能靠追问来核实三件事：

1. **项目是不是真的。** 真做过的人说得出约束、数据和踩过的坑，背项目的人只能复述架构图。追问到第三层，两者的差距会立刻显现。
2. **你有没有做技术决策的能力。** Agent 领域同样没有银弹，同一个问题可以用 Prompt、工作流、RAG、工具调用或 Multi-Agent 解决。面试官想知道：面对你的具体约束，你能不能权衡出合理方案，而不是教程/网上是这么做的，或者 AI 直接给你提供的方案。
3. **你对系统边界的认知。** 模型输出不可靠、状态可能不一致、工具会失败——知道这些风险、并且用工程手段兜住的人，才是能上生产的人。

对应地，“项目效果很好”“架构可扩展”“模型准确率高”这类回答为什么不行？因为它们是结论，不是论证。面试官听到的信息量是零：既判断不了真假，也判断不了你的参与深度。真正有区分度的回答，是把约束、选择、代价和证据放到一起：

> 在什么约束下，我做了什么选择；它解决了什么问题，又引入了什么代价；最后用什么证据确认这个选择有效。

这四样东西缺一个，回答都会塌：

- 缺**约束**，选择就变成“大家都这么用”，体现不出判断力；
- 缺**代价**，说明没真正上过线——任何方案都有代价，Multi-Agent 拆了之后调试成本、上下文传递、延迟都会上升；
- 缺**证据**，效果就只是主观感受，“工具选错率从 8% 降到 2%，评测集 200 条”才可核对；
- 缺**替代方案**，面试官无法确认你是做过权衡，还是只会一种做法。

例如，“我们用了 Multi-Agent 提升效果”没有交代拆分的原因和代价。回答时可以补上这次决策的经过。

> 最初是单 Agent，工具数量增加后，退款政策查询和工单写入的工具容易选错。我们没有直接拆成多个 Agent，而是先缩减工具集、重写工具描述并补充路由评测，选错率从 8% 降到 3%。后来不同业务域需要独立上下文，并改由不同团队维护，我们才按业务域拆分 Agent。代价是跨域任务需要一层路由，整体延迟多了几百毫秒，所以我们把路由做成了基于意图分类的轻量调度，而不是再引入一个“管理 Agent”。

对比一下就能看出差别：原版回答只有“用了什么”，展开版交代了现象（工具选错）、选择（先治理工具再拆分）、替代方案（不拆也能解决一部分问题）、判断依据（路由评测数据）和代价（延迟增加及其应对）。面试官从这段话里能同时核实项目的真实性和你的决策过程，这比报出一串框架名的信息密度高得多。

而且这段回答还有一个作用：它主动给面试官留了追问的钩子——路由评测怎么做、意图分类为什么不用 LLM 路由、上下文怎么传递。这些钩子应该都是你提前准备好的领域，让深挖发生在你的主场，而不是被动地被问到知识盲区。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/interview-questions/agent-project-interview-guide.md#L28)，来源许可：Apache-2.0。

<a id="k2116d7641b9f"></a>

## Agent 项目面试怎么讲？从系统架构、技术选型到 Badcase 复盘

Agent/AI 应用方向的面试，基本不会停留在背概念，一般都是结合你的项目往深了问：为什么这样设计、线上出过什么问题、怎么定位和修复。

如果你在面试之前，只背 ReAct、RAG、Memory、MCP、Function Calling 等核心概念，通常应付不了面试追问：

1. 你做的到底是不是 Agent，为什么不能用普通接口或固定工作流解决？
2. 一个请求进来后，经过了哪些组件，状态和数据怎么流转？
3. 关键方案是根据什么约束选出来的，代价是什么？
4. 项目失败过什么，你怎么定位、修复并防止它再次发生？

为了方便大家更容易理解，我在文中会以一个智能售后工单 Agent 为例，来串起来这些问题。

不论你的项目是不是类似的，都没关系，文中分享的方法都是通用的。你在准备自己的项目时，业务背景、职责、数据规模和指标都要换成真实内容。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/interview-questions/agent-project-interview-guide.md#L2)，来源许可：Apache-2.0。

<a id="kb2034a31eb21"></a>

## AGENTS.md、Skills、Memory 文件为什么重要？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

Agent 不只需要工具，还需要知道“这个项目怎么工作”。AGENTS.md、Skills、Memory 文件解决的是项目级上下文和可复用知识的问题。

**AGENTS.md**：面向编码 Agent 的项目说明文件，包含构建命令、测试命令、代码规范、目录结构、提交要求等。

**Skills**：可按需加载的能力包，通常包含 `SKILL.md`、脚本、模板、参考资料，让 Agent 在特定任务中获得专业流程。

**Memory 文件**：保存长期偏好、项目约定、团队知识、历史决策，帮助跨会话复用经验。

三者对比：

| 类型 | 解决问题 | 生命周期 |
| --- | --- | --- |
| AGENTS.md | 项目级通用指令 | 随代码仓库长期存在 |
| Skill | 任务级专业能力 | 按需加载和复用 |
| Memory | 个体/团队历史经验 | 持续积累和更新 |

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/01_AIGC%E6%97%B6%E4%BB%A3AI%20Agent%E5%9F%BA%E7%A1%80%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L400)，来源许可：GPL-3.0。

<a id="k1e008397184c"></a>

## Agents中对于神经记忆网络的稀疏激活​的步骤是什么？

仿生海马体的三阶段检索：

​​（1）模式完成​​：输入线索→激活相关记忆片段；

​​（2）模式分离​​：相似记忆差异化编码（如"咖啡杯"vs"茶杯"）；

​​（3）模式精炼​​：前额叶调控最终召回内容；

​​（4）性能​​：在LegalBot法律咨询系统中，检索准确率提升至89%，误检率降低至2.1%

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E5%A4%9A%E6%A8%A1%E6%80%81%E5%9F%BA%E7%A1%80/%E5%A4%9A%E6%A8%A1%E6%80%81-%E5%89%8D%E6%B2%BF%E6%8A%80%E6%9C%AF.md#L368)，来源许可：GPL-3.0。

<a id="k9d635fab40e1"></a>

## Agent、Environment、State、Action、Reward 分别是什么？

**难度评分：⭐⭐ (2/5)  |  考察频率：⭐⭐⭐⭐⭐ (5/5)**

强化学习五个基本元素：

| 概念 | 含义 | 例子 |
| --- | --- | --- |
| Agent | 做决策的智能体 | 机器人、游戏 AI、LLM Agent |
| Environment | 智能体交互的环境 | 游戏地图、网页、用户反馈系统 |
| State | 当前环境状态 | 位置、历史对话、页面 DOM |
| Action | 智能体可执行动作 | 移动、点击、调用工具、生成回答 |
| Reward | 行动后的反馈 | 得分、成功率、人类偏好、任务完成 |

![强化学习交互流程](https://raw.githubusercontent.com/WeThinkIn/AIGC-Interview-Book/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BB%8F%E5%85%B8%E6%A8%A1%E5%9E%8B/imgs/强化学习交互流程.png)

在 LLM Agent 中：

- State 是上下文、任务进度、工具返回结果。
- Action 是下一步回复或工具调用。
- Reward 可以来自任务成功、用户评分、自动评测或偏好模型。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BB%8F%E5%85%B8%E6%A8%A1%E5%9E%8B/%E5%BC%BA%E5%8C%96%E5%AD%A6%E4%B9%A0%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L59)，来源许可：GPL-3.0。

<a id="kf72b0fd824a6"></a>

## agent三次调用都报错，你会怎么办

**回答：**

三次报错后先停止无差别重试，查看调用轨迹，确认失败发生在模型服务、参数生成、工具执行还是结果解析阶段。记录错误码、请求标识、参数摘要、耗时与是否产生外部副作用，同时避免在日志中泄露密钥和敏感数据。

可恢复的网络超时、限流或服务暂时不可用，可以在总时间和次数预算内退避重试并加入抖动；限流遵守服务端提示。参数类型、字段缺失、枚举不合法等确定性错误，先依据工具 schema 和明确错误反馈修复参数；权限不足、资源不存在、依赖未配置时，应终止或转人工，反复调用相同参数通常不会改善。

对有副作用的调用尤其要谨慎。超时只代表没有及时收到响应，不代表操作未成功；提交任务、写入图谱或创建记录前后应有幂等键和状态查询，先核实执行结果，再决定是否重试。并发尝试还需防止多个分支重复执行相同操作。

如果已经连续失败，应触发熔断或切换明确可用的降级路径，例如只输出已验证的抽取候选、保留任务状态等待恢复，或要求补充必要信息。面向用户说明哪一步未完成，而不是把部分结果包装成成功。后续把失败样本纳入回归，检查是工具契约、提示词还是服务稳定性问题。

将错误处理落实到执行器时，可以使用下面的决策表。三次只是题目给定的现象，实际重试预算应由操作语义、总时限和服务约束决定。

| 失败类型 | 下一步动作 | 关键检查 |
|---|---|---|
| 读操作遇到临时网络故障或限流 | 有界退避重试 | 总时限、限流提示、熔断状态 |
| 参数缺失或类型错误 | 按 schema 修复后重新校验 | 不重复发送相同错误参数 |
| 写操作超时，结果未知 | 先查询操作状态 | 幂等键是否稳定、操作是否已提交 |
| 权限不足或确定的业务约束冲突 | 终止该路径并反馈 | 不通过换参数绕过权限与约束 |

幂等键应标识同一次业务意图，并在该操作的重试中保持不变；每次重试都生成新键，会失去去重作用。真正的新任务则应使用新的业务身份。

<a id="01ai-kg-intern-20261021-de81855b-q05"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%9B%B6%E4%B8%80%E4%B8%87%E7%89%A9%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L82)，来源许可：GPL-3.0。

<a id="k49502aef53a4"></a>

## Agent上下文超限了怎么处理？

**面试官：** Agent执行多步任务时，对话历史加工具返回结果很容易超限，你有什么处理方案？

**面试官追问：** 三种策略分别在什么场景下用？

**回答：**

Agent 上下文治理的核心不是“把旧消息删掉”，而是在有限 Token 预算内，持续保留完成当前任务所必需的状态、证据和约束。一个成熟方案通常分为五层。

第一层是**预算与优先级管理**。先为 System Instruction、工具 Schema、当前用户请求、近期对话、任务状态、检索证据和输出预留独立预算。System 约束、权限边界和当前目标不能被普通历史消息挤出上下文。

第二层是**近期窗口**。保留最近若干轮原始消息，适合强依赖局部指代、短期状态快速变化的实时对话。但窗口不应只按“轮数”截断，而应按 Token、消息类型和任务依赖截断。机械丢弃最早消息可能删掉长期有效的用户约束。

第三层是**结构化状态与摘要**。把历史对话压缩成任务状态，例如目标、已确认事实、未完成子任务、约束、决策及证据引用。摘要应支持版本号、更新时间和可追溯来源；发生冲突时，新事实不能静默覆盖旧事实，而应记录“旧值、当前值、变更依据”。

第四层是**外部记忆检索**。把长期历史、文档和经验存入可检索存储，按语义、关键词、时间、实体、会话和权限联合召回。向量相似度只表示“像”，不表示“当前有效”，因此还要考虑新鲜度、来源可信度、用户归属和业务权限。

第五层是**工具结果压缩**。Agent 最容易被日志、网页全文、数据库大结果集和代码构建输出撑爆。应在工具层先做分页、字段投影、去重、统计聚合、错误摘要和 Artifact 引用，只把决策所需片段送回模型，而不是把原始输出全部塞回上下文。

场景选择可以这样回答：

- 短对话和低风险客服：近期窗口加少量结构化槽位即可。
- 长周期任务：近期窗口、任务状态、阶段摘要和 Artifact 引用组合使用。
- 跨会话个性化：使用权限隔离的长期记忆检索，并设置过期、确认和删除机制。
- 知识问答：重点是检索外部证据，而不是把所有历史对话永久保留。
- 高风险操作：关键参数、用户确认、审批结果和工具回执必须保留为不可丢失的结构化状态。

摘要模型不一定越小越好。小模型成本低，但数字、否定关系、权限条件和未完成事项一旦压错，后续所有步骤都会在错误状态上继续。应使用专门评测集比较事实保真率、未完成任务召回率、压缩率和下游成功率，再决定模型与策略。**上下文压缩的目标不是最短，而是让 Agent 在更少 Token 中仍然保持任务连续性、事实一致性和可恢复性。**

**超限错误的恢复边界。** 若请求前估算未能避免供应商的上下文超限错误，应重新计算实际模型预算，压缩后有限重试，保持工具调用和结果配对，避免重复执行已完成的副作用。更换长上下文模型必须检查授权、费用和协议；最小必要输入仍超限时应拆分任务或外置产物。

<a id="alibaba-cloud-agent-algo-20260901-q3"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1277)，来源许可：GPL-3.0。

<a id="kd027c742d9ba"></a>

## Agent中数据是怎么交互的

**回答：**

Agent 中的数据通常沿“用户请求—任务状态—模型上下文—工具调用—执行结果—验收”流动。模型输出结构化工具名与参数，由运行时做 schema 和业务校验；工具返回结构化状态、数据或对象引用，运行时再选择必要信息进入下一轮上下文。

会话 ID、单次调用 ID、业务任务 ID、资产版本和幂等键承担不同职责。大文件保存在对象存储，消息传授权引用；长任务保存可靠检查点，不能只依赖聊天摘要恢复执行。

多组件通过同步 RPC、事件或消息队列协作，需定义超时、重试、去重、顺序和版本协议。工具结果是数据，不能自动提升成系统指令；敏感数据按用户与租户隔离，日志保留足够诊断信息并控制访问。

<a id="jd-damodel-20251211-20260205-p8"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E4%BA%AC%E4%B8%9C%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1183)，来源许可：GPL-3.0。

<a id="k49ba19c77777"></a>

## Agent中的Memory通常如何实现？短期记忆和长期记忆分别解决什么问题？

**回答：**

短期记忆解决当前任务的连续性：模型要知道用户目标、约束、最近对话、计划、已经完成的步骤、工具结果和待确认事项。实现上通常把结构化任务状态放在 Workflow checkpoint、Redis 或数据库中，把最近消息保留为窗口，把已完成阶段压缩为摘要和事件引用；Prompt 只是这些状态在当前步骤的投影视图。KV Cache 是推理加速状态，不是 Agent Memory。

长期记忆解决跨会话复用：例如经过确认的用户偏好、项目约定、历史事件和可复用经验。不同数据使用不同存储：稳定事实和权限关系用关系表或 KV，事件用 append-only log，自然语言经验用向量加全文混合索引，实体关系复杂时再考虑图结构。每条记忆应带用户/租户/项目作用域、来源、时间、置信度、有效期、权限和原始事件引用。

完整生命周期是：候选提取 -> 敏感性/重要性过滤 -> 去重和结构化 -> 写入 -> 按需检索 -> 权限、时效和相关性重排 -> 注入 -> 冲突更新、过期或删除。当前用户明确指令优先于旧偏好，业务主库的实时事实优先于历史摘要，模型推断不能覆盖明确事实。记忆系统的目标不是保留最多，而是在正确作用域内提供可纠正、可追溯且对未来任务有价值的信息。

<a id="bilibili-ai-agent-20260818-q17"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%93%94%E5%93%A9%E5%93%94%E5%93%A9%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L280)，来源许可：GPL-3.0。

<a id="k5216ad7d5508"></a>

## Agent中的短期记忆和长期记忆分别有什么作用？通常会如何实现？

**回答：**

短期记忆服务于**当前任务连续性**，长期记忆服务于**跨会话复用**。划分标准不是存储介质，而是生命周期、作用域和是否值得在未来任务中继续使用。

| 类型 | 典型内容 | 生命周期 | 常见实现 |
| --- | --- | --- | --- |
| 短期/工作记忆 | 当前目标、计划、最近对话、已完成步骤、工具结果、待确认事项 | 一次任务或会话 | Workflow state、Redis/数据库会话表、checkpoint、近期窗口与结构化摘要 |
| 长期记忆 | 稳定偏好、身份事实、项目约定、历史决策、经过验证的经验 | 跨会话 | 关系数据库/画像表、事件日志、向量或全文索引；按用户、租户、项目隔离 |

短期状态应以结构化字段为主，Prompt 只是状态的一个投影视图。长任务中保留原始事件和 artifact 引用，在阶段边界生成摘要；即使上下文压缩，任务状态仍能恢复。KV Cache 是推理加速状态，不等于 Agent Memory。

长期记忆需要完整生命周期：候选提取 -> 重要性与敏感性过滤 -> 结构化写入 -> 按需检索 -> 冲突更新 -> 衰减/过期/删除。每条记忆应带 `scope`、来源、时间、置信度、有效期和权限。当前用户明确指令优先于旧偏好，业务主库实时状态优先于历史摘要，模型推断不能覆盖用户明确事实。

不是每轮都注入全部记忆。Context Builder 只召回与当前目标相关且通过权限、时效和冲突检查的少量内容。好的 Memory 系统不是“记得越多越好”，而是能在正确的任务、正确的时间，以可追溯的方式取回正确状态。

<a id="insta360-agent-20260809-q8"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%BD%B1%E7%9F%B3%E5%88%9B%E6%96%B0%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L157)，来源许可：GPL-3.0。

<a id="k324959cc34a7"></a>

## Agent体系中Skill、Memory、RAG三大组件分别解决什么核心问题？

**回答：**

三者分别回答 Agent 系统中的三个不同问题：Skill 解决“怎么做”，Memory 解决“过去发生过什么、哪些经验值得复用”，RAG 解决“当前需要哪些外部知识”。它们可以共享检索基础设施，但语义和生命周期不同。

| 组件 | 核心对象 | 典型内容 | 更新方式 |
|---|---|---|---|
| Skill | 可复用的程序性能力 | 指令、Workflow、工具 schema、脚本、验收规则 | 版本化发布、测试后升级 |
| Memory | 与主体和历史交互有关的状态或经验 | 用户偏好、任务进度、历史决策、成功/失败经验 | 经过写入门控后增量更新、合并或遗忘 |
| RAG | 任务所需的外部知识 | 文档、商品信息、制度、代码、数据库记录 | 随知识源更新并重建或增量维护索引 |

Skill 不是一段泛化 Prompt，而是能够被稳定调用、具有输入输出契约和验收标准的能力包。例如“生成商品上架材料”这一 Skill 可以封装字段检查、文案生成、风险校验和发布工具。

Memory 的关键不是把聊天记录永久保存，而是选择性地写入可复用状态。短期记忆服务于当前任务，长期记忆保存跨会话仍有价值的偏好、事实和经验。它必须带时间、来源、置信度、权限和可删除机制，否则错误会被长期放大。

RAG 是检索增强生成范式：根据当前查询从外部知识库召回证据，再经过过滤、重排和上下文组装提供给模型。它主要解决参数知识不新鲜、企业私有知识不可见和回答不可追溯问题。

三者会发生组合：Memory 的读取可以用向量检索实现，但检索到的是主体历史；Skill 内部也可以调用 RAG，但检索的是任务知识。区分它们时不要按“是否用了向量库”分类，而要看信息表达的是程序、经历还是外部事实。

<a id="alibaba-taotian-agent-20260722-q8"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L627)，来源许可：GPL-3.0。

<a id="kdb9e4bfcd830"></a>

## agent原理

**回答：**
Agent 可以视为由模型提出动作、运行时授权执行、工具反馈环境观察的任务系统。任务状态包含目标、硬性约束、证据、在途动作和剩余预算；模型输出不能直接决定是否越权、是否完成，也不能自行重置预算。

固定流程优先使用确定性工作流；环境未知时可用 ReAct 式动态探索，长任务可以用结构化计划与检查点。需要为外部写入设置幂等键、结果核对和事务约束，为重试与重规划设置独立但统一受总预算限制的上限。反思结果仍须验证，不能凭“模型自认正确”结束。

具体状态、循环检测与恢复设计可结合[避免循环调用的 Agent 状态机](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%99%BE%E5%BA%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#baidu-agent-20260922-r2-q8)进一步展开。

<a id="batch3-p3-q8"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%99%BE%E5%BA%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L287)，来源许可：GPL-3.0。

<a id="k9d382097e54d"></a>

## Agent取消机制怎么做？

**面试官：** 一个Agent任务耗时很长，用户等不及了，怎样停止这个任务？这个机制你实际尝试过吗？

**回答：**

Agent 取消机制的本质是**可传播的协作式取消 + 资源级强制终止 + 状态一致性恢复**。只在主循环里放一个布尔标记，只能停止下一步调度，不能保证当前网络请求、子进程、数据库事务或外部工具真正停下来。

完整设计可以分为六层：

1. **任务状态机。** 每个任务具有 `task_id`、`RUNNING/CANCELLING/CANCELLED/SUCCEEDED/FAILED` 状态、截止时间和父子任务关系。取消请求必须幂等，多次取消返回同一个最终状态。
2. **取消令牌传播。** 从 HTTP 请求或交互层生成 Cancellation Token，向 Planner、Agent Loop、模型流式请求、工具调用和子任务逐层传播。每个耗时阶段都在安全点检查，而不是只在循环开头检查。
3. **Deadline 与超时。** 将剩余时间预算传给下游，区分连接超时、首 Token 超时、空闲读取超时和总耗时。超时本质上是由系统发起的取消，也必须走同一条清理链路。
4. **底层中止。** 对支持取消的 HTTP 客户端主动关闭请求或流；对子进程先发送优雅终止信号，超时后再强制终止进程组；对容器或沙箱可以直接回收执行单元。`Future.cancel()` 或 `Thread.interrupt()` 只是发出信号，目标代码不响应时并不等于任务已经停止。
5. **副作用治理。** 已执行的发邮件、扣款、写文件等动作不能靠取消“回滚”。工具应支持幂等键、事务、预提交、补偿动作和操作日志。取消时停止未来动作，并对已提交副作用执行明确的补偿或人工确认。
6. **资源清理与观测。** 在 `finally`、`whenComplete` 或上下文管理器中释放连接、文件句柄、锁、临时目录和 GPU Session；记录取消来源、传播延迟、未能中止的子任务和最终一致性结果。

Java 中 `CompletableFuture.orTimeout()` 只会让 Future 以超时异常完成，通常不会自动停止已经运行的底层任务；丢弃 Future 更不会释放连接。正确做法是让执行函数显式接收取消令牌或 Deadline，并使用能够中止请求的客户端 API。对于不可协作的第三方 SDK，应把调用隔离到独立进程、容器或受控 Worker，通过终止执行单元形成最后一道边界。

实际项目回答应给出可验证证据，例如“取消请求 P95 多久生效”“正在进行的工具是否真正停止”“已产生副作用如何恢复”，而不是只说自己使用了某个并发类。面试式结论是：**取消不是线程 API 问题，而是从用户请求一直传播到资源和副作用的一条系统契约。**

<a id="alibaba-cloud-agent-algo-20260901-q4"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1311)，来源许可：GPL-3.0。

<a id="kd7c77c87cc75"></a>

## Agent在执行任务时，如果调用外部工具或API出现超时、异常等情况，一般应该如何设计容错机制？

**回答：**

容错的第一步不是重试，而是**分类**。至少区分瞬时故障（超时、限流、5xx）、永久故障（参数错误、权限不足、资源不存在）、业务冲突（状态已变化）、响应不确定（请求可能已执行但客户端没收到结果）和语义失败（工具成功返回，但结果不满足任务）。不同类型不能使用同一策略。

工程上我会这样设计：

- 为整项任务设置总 deadline，再向每次模型和工具调用分配子预算，防止局部重试耗尽全局时间；
- 只对明确可重试错误采用**有上限的指数退避加 jitter**，尊重服务端 `Retry-After`；
- 写操作使用幂等键、业务唯一约束或状态机 CAS；结果不确定时先查询状态，不能直接重放副作用；
- 连续失败触发熔断，半开探测后恢复；必要时切换备用工具、模型或降级路径；
- 每一步执行前后写 checkpoint，记录输入、工具版本、调用 ID、状态差异和 artifact，支持恢复、补偿或人工接管；
- 参数错误、权限不足等永久故障不自动重试，而是回到模型重规划、向用户补充信息或请求授权；
- 对不可逆、高风险动作设置人工确认，恢复逻辑本身也要经过权限与安全校验。

![Agent可靠执行、错误分类与恢复闭环](https://raw.githubusercontent.com/WeThinkIn/AIGC-Interview-Book/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/images/insta360-agent-reliability-recovery-loop.png)

评测不能只看“最终成功”。还要看恢复成功率、重复副作用率、平均重试次数、P95/P99 延迟、熔断次数和人工接管率，并通过工具超时、429、5xx、脏响应、重复回包和状态库故障做故障注入。容错的目标不是隐藏错误，而是把错误转化为可分类、可限制、可恢复的状态迁移。

<a id="insta360-agent-20260809-q6"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%BD%B1%E7%9F%B3%E5%88%9B%E6%96%B0%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L115)，来源许可：GPL-3.0。

<a id="ke50b2ecbf10a"></a>

## Agent在执行过程中，肯定不可避免地要去调用一些工具，这些工具都有固定地入参，需要模型结合上下文去提供，然后在这个过程中，如何去保障工具调用的可靠性？

**回答：**

工具调用可靠性不能依赖模型“自己多想几遍”，而应采用模型提出候选动作、运行时确定性校验、工具执行和结果验证的分层架构。

1. **Schema 约束。** 用 JSON Schema/函数调用定义参数类型、枚举、范围、必填项和字段关系；拒绝无法解析或多余字段，避免把自然语言直接拼成 SQL、Shell 或 URL。
2. **上下文与身份校验。** 运行时补充不可由模型决定的用户身份、租户、权限和服务端时间；模型只能提供业务参数，不能自行声明管理员权限。
3. **执行前检查。** 校验权限、资源存在性、前置状态、金额/范围、幂等键和风险等级。高风险动作采用预览 -> 用户确认 -> 提交，必要时人工审批。
4. **失败分类。** 区分参数错误、权限拒绝、资源不存在、业务冲突、瞬时网络错误和服务端故障；只有可恢复错误重试，并限制次数与总时间。
5. **执行隔离。** 文件、代码和网络工具放在沙箱/容器中，限制域名、系统调用、资源和文件路径；工具结果视为不可信数据，防止 Prompt Injection 反向改变系统指令。
6. **结果验证。** 工具返回不等于业务成功。用数据库状态、测试、签名回执或确定性规则验证；返回结构中关联 `tool_call_id`、状态、错误码、版本、延迟和结果引用。
7. **可观测与评测。** 记录工具选择准确率、参数准确率、执行成功率、重试率、重复副作用率、恢复率和 P95 延迟，并用故障注入验证超时、断网、空结果、恶意返回和版本冲突。

工具描述要短、清晰、互不重叠，并通过命名、示例和反例减少歧义。对于可由规则确定的路由，不必把选择权交给模型。**可靠工具调用的核心是把“模型的概率性动作”包在“确定性接口、权限和验证”之内。**

<a id="bytedance-agent-dev-20260903-q9"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%AD%97%E8%8A%82%E8%B7%B3%E5%8A%A8%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1201)，来源许可：GPL-3.0。

<a id="k51999417a472"></a>

## Agent开发中，知识维护、记忆模块（短期/长期记忆）你是怎么考虑设计的？

**回答：**

知识库、短期状态与长期记忆应分开设计。知识库主要存储业务规范和文档；短期状态记录本次任务已知条件与执行进度；长期记忆保存经过筛选、可跨任务复用的信息。RAG 是检索与上下文构建方式，可以用于知识或记忆，但不等于记忆本身。

短期状态可以包含当前目标、已确认参数、待澄清字段、计划、工具结果引用和检查点。对长对话做摘要时保留资源 ID、明确约束、确认范围和未解决问题；重要状态结构化保存，不能只依赖自然语言摘要。

长期记忆可区分用户偏好、领域事实、经验证的经验和操作规范。写入需要判断准确性、复用价值、权限和保留期限；模型自己的猜测或一次偶发错误不能未经审核就转为长期事实。

读取时先做租户、用户和项目权限过滤，再按相关性、时效性与适用条件排序。过期或冲突信息标记失效或请求澄清；用户偏好不能覆盖业务规则，也不能扩大执行授权。

维护时同步更新文档版本、索引和被替代关系，支持删除、回滚与审计。评测既看记忆命中是否提高任务完成率，也看错误记忆引用、跨用户泄漏、过期信息影响、上下文成本和遗忘/删除是否生效。

![图4知识状态与长期记忆的维护闭环](https://raw.githubusercontent.com/WeThinkIn/AIGC-Interview-Book/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/imgs/meituan-agent-20261012-18fa4134/04_知识状态与长期记忆的维护闭环.png)

图 4：业务规范、当前任务状态和候选长期记忆分开管理。执行日志可以自动记录，跨任务复用的结论则需要经过适用性与证据检查。

**一个具体冲突如何处理？** 假设长期记忆保留“某接口退款上限为旧值”，当前需求文档给出新版本上限。系统应根据接口版本与生效区间选择有效规则，并使旧记忆不再参与当前任务；不能按相似度最高就取旧值，也不能把两者平均。如果版本关系不明确，则先澄清，不把记忆的存在当成事实权威。

删除同样是完整链路：除主存储外，还要处理向量索引、缓存、派生摘要和备份保留规则。不同层可以采用不同物理清除时间，但撤销访问后的在线读取必须尽快按策略拒绝，不能等索引慢慢更新才执行权限控制。

<a id="meituan-agent-20261012-18fa4134-q24"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%BE%8E%E5%9B%A2%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1170)，来源许可：GPL-3.0。

<a id="kf8b5ec4234b7"></a>

## Agent强化学习仅依靠最终结果设计奖励是否够用，多步工具轨迹如何做信用分配？

**回答：**

仅用最终结果奖励在理论上可以训练，因为完整轨迹的回报能够传回前面的决策；但在长链 Agent 中通常不够。轨迹越长，终局奖励越稀疏，方差越大，模型越难判断究竟是哪一次工具选择、哪个参数或哪一步恢复策略导致成功与失败。

最基础的信用分配是回报和优势估计。对第 $t$ 步，折扣回报为：

$$
G_t=\sum_{k=t}^{T}\gamma^{k-t}r_k
$$

再用价值函数或 GAE 构造优势，判断当前动作相对状态基线带来了多少增益。纯终局奖励相当于中间 $r_k$ 大多为零，所有步骤共享一个结果信号，学习效率很低。

工程上通常采用“结果奖励为主、过程信号辅助”。结果层评估任务是否真正完成；过程层可以检查工具是否选对、参数是否合法、观察是否被正确使用、是否重复调用、是否越权、失败后是否恢复，以及步骤数和成本是否合理。对可验证任务，应尽量使用编译器、单元测试、数据库状态、API 返回或业务规则等确定性验证器，而不是完全依赖另一个 LLM 打分。

多步轨迹还可以使用几类方法：训练过程奖励模型给关键步骤打分；对轨迹做分段里程碑奖励；用树搜索或多条 rollout 比较同一状态下的不同动作；通过删除或替换某一步的反事实实验估计该动作的边际贡献；将成功轨迹与失败轨迹做成 step-level 或 trajectory-level 偏好数据。

奖励塑形要防止改变原任务。理论上，形如 $F(s,a,s')=\gamma\Phi(s')-\Phi(s)$ 的 potential-based shaping 更容易保持最优策略不变。若简单奖励“调用了某工具”或“步骤更长”，模型可能学会刷工具次数；若只惩罚长度，又可能跳过必要验证。

所以最终答案是：终局奖励定义“做成没有”，过程奖励帮助回答“哪一步做对了”。二者要结合，而且过程信号必须服务于真实任务成功，不能成为更容易被投机的新目标。

<a id="alibaba-taotian-agent-20260722-q10"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L671)，来源许可：GPL-3.0。

<a id="k0562b7a24d03"></a>

## Agent强化学习场景Reward Hacking问题高发的底层机理

**回答：**

Reward Hacking 是策略学会最大化奖励函数的代理指标，却没有完成真实目标。Agent 场景尤其容易出现：模型通过增加无意义的解释获得 Judge 高分、反复调用工具刷过程奖励、伪造工具成功文本、选择容易但无效的子任务、延长答案获取长度奖励，或利用评测器/模拟器漏洞。

底层原因是奖励函数只是目标的可观测代理，存在规格缺口；模型能力和探索速度超过了奖励设计者发现漏洞的速度；多步环境还会把评估器偏差、工具状态和终局成功混在一起。治理应优先采用确定性 Verifier、真实状态回执和硬约束，再使用模型 Judge；对过程奖励做 held-out 校准，监控“高分失败”反例，随机化评测器，限制工具副作用和调用预算，并用多目标/约束优化而不是让一个软奖励抵消安全违规。

最终指标必须包含真实任务成功率、约束违反率、重复调用率、人工复核结果和分布外测试，而不能只看训练 reward。

<a id="tencent-llm-collection-20260903-q11"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E8%85%BE%E8%AE%AF%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L422)，来源许可：GPL-3.0。

<a id="k324138c80853"></a>

## Agent执行任务时，如果出现重复调用工具、无法结束或者任务循环的问题，应该如何设计保护机制？

**回答：**

我会从“检测、限制、恢复、验收”四层设计：

- **重复检测：** 对规范化后的工具名、参数、当前状态版本和结果摘要计算动作指纹；连续相同调用、同一错误参数重复修正、状态没有变化的调用都应触发告警。不能只比较原始 JSON，因为字段顺序和无关参数可能不同。
- **预算限制：** 设置最大步数、总 deadline、模型调用次数、Token/费用预算、单工具重试次数和最大并行分支数；预算由运行时强制，不能交给模型自己承诺。
- **状态与终止：** 使用显式状态机和 checkpoint，定义外部完成条件、失败条件和升级条件；只有业务状态、测试或验证器满足要求才进入 `DONE`。
- **错误恢复：** 区分瞬时错误、参数错误、权限错误和不确定副作用。可重试错误使用有上限的指数退避；写操作用幂等键并先查询状态；连续失败可重规划、降级到只读/模板流程或人工接管。
- **上下文治理：** 对工具结果做大小上限、摘要和结构化投影，避免模型被无关 Observation 推向循环；保留原始结果引用以便回查。

循环检测不应简单地“看到两次相同调用就停止”，因为有些轮询本来需要等待状态变化。应结合状态版本、时间窗口、进度信号和工具语义判断。例如轮询任务必须要求 `status` 在 deadline 内发生变化，否则转人工。所有中止原因、动作指纹、预算消耗和最终状态都要进入 Trace，才能在回放中修复策略。

<a id="bilibili-ai-agent-20260818-q16"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%93%94%E5%93%A9%E5%93%94%E5%93%A9%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L265)，来源许可：GPL-3.0。

<a id="k9818909f1955"></a>

## Agent沙箱、权限、审计、灰度和回滚如何做？

Agent系统比普通聊天系统更危险，因为它可以调用工具、读写文件、访问网络、执行代码或操作数据库。工程上需要把Agent当成“半自动执行系统”治理。

核心机制：

1. 沙箱：代码执行、shell命令、文件处理在隔离环境中运行，限制CPU、内存、网络、文件系统和执行时间。
2. 权限：按用户、租户、工具、资源设置最小权限。
3. 审计：记录工具调用、参数摘要、结果摘要、操作者、时间、request_id。
4. 策略：危险操作前做规则校验，例如删除文件、发送邮件、改数据库、访问内网。
5. 灰度：新工具、新模型、新Prompt模板先小流量发布。
6. 回滚：保留上一版本模型、配置和工具schema，异常时快速切回。

一个简单的工具治理表可以包括：

| 字段 | 含义 |
| --- | --- |
| tool_name | 工具名 |
| allowed_roles | 可调用角色 |
| network_policy | 可访问域名或网段 |
| filesystem_policy | 可读写路径 |
| timeout_ms | 最大执行时间 |
| require_confirmation | 是否需要人工确认 |
| audit_level | 审计等级 |

面试金句：Agent工程不是让模型“更敢做事”，而是让模型在可控边界内做事。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%B7%A5%E7%A8%8B%E5%9F%BA%E7%A1%80%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L2335)，来源许可：GPL-3.0。

<a id="k38ebb7501629"></a>

## agent用的什么框架有了解吗

**回答：**

首先回答实际使用过的框架、版本范围和具体职责。如果只是读过示例，应明确区分了解与实践；如果没有采用框架，可以介绍由服务代码、模型 SDK、任务队列和状态表构成的实现。

理解框架时，重点看模型接入、工具契约、状态存储、节点编排、循环终止、人工介入和观测能力。LangChain 提供模型、工具、检索等应用构建与集成能力；LangGraph 强调显式状态和图式编排，可结合持久化支持中断与恢复。具体能力取决于版本和配置，接入框架不会自动解决工具权限、业务幂等或结果正确性。

可以用信息抽取任务说明选型：固定的“解析—抽取—校验—归一—入库”流程可先用普通工作流；若需要根据证据不足动态检索术语、等待专家确认再恢复，则持久化编排更有价值。多 Agent 只有在职责分离、并行收益或独立验证带来可测改善时才引入，不为展示框架复杂度拆分角色。

<a id="01ai-kg-intern-20261021-de81855b-q04"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%9B%B6%E4%B8%80%E4%B8%87%E7%89%A9%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L71)，来源许可：GPL-3.0。

<a id="k6a880c5af601"></a>

## Agent自进化机制的核心逻辑，是否属于模型自主迭代训练

**回答：**

Agent 自进化通常是一个闭环系统，而不是模型凭空修改自己的参数：**执行任务 -> 记录轨迹 -> 评估失败 -> 生成经验或改进候选 -> 验证 -> 受控发布**。可进化对象可以是提示词、工具选择策略、记忆、工作流、检索索引、评测集，只有经过训练和发布门禁后，才可能进入模型参数。

因此“自进化”不等于“模型自主迭代训练”。在线直接改权重会带来数据污染、灾难性遗忘、奖励投机和不可审计风险。更可靠的实现是把经验写入版本化 Memory 或候选策略仓库，由独立评测集、回放环境和安全检查验证，达到门槛后再通过离线 SFT、DPO、蒸馏或 RL 更新模型，并保留回滚点。

    一个完整闭环至少要区分探索、评估、训练和发布权限，记录数据入口、策略版本、环境版本和指标变化。没有独立验证集与回滚机制的“自我反思”，更多只是运行时上下文改写，而不是可信的模型进化。

<a id="tencent-llm-collection-20260903-q4"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E8%85%BE%E8%AE%AF%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L294)，来源许可：GPL-3.0。
