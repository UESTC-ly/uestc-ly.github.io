# Agent、确定性 Workflow 与状态机

## 1. Agent 与 Workflow 的区别

| 维度 | 确定性 Workflow | Agent |
|---|---|---|
| 下一步由谁决定 | 代码、配置或状态机 | 模型在约束内提出建议 |
| 路径 | 预先定义，容易测试 | 动态变化，适应性更强 |
| 可预测性 | 高 | 较低，需要预算和护栏 |
| 成本 | 通常稳定 | 可能随循环次数变化 |
| 风险 | 主要是代码和外部系统风险 | 还增加越权、循环、错误规划风险 |
| 适用任务 | 固定审批、ETL、订单流程 | 信息不完整、需要选择工具和策略的任务 |

两者不是二选一。推荐使用**确定性骨架 + 局部 Agent 节点**：例如流程的鉴权、审批、扣款和状态更新由代码控制；模型只负责分类、抽取、生成候选计划或选择只读查询工具。

## 2. 判断是否需要 Agent

可以按以下问题判断：

1. 下一步是否依赖刚刚获得的非结构化信息？
2. 可选工具或路径是否很多，且无法全部写成简单条件？
3. 任务是否允许一定程度的探索和不确定性？
4. 是否有足够的预算、人工兜底和失败恢复机制？

如果答案大多是否定的，应优先写 Workflow。不要因为使用了 LLM 就把整个业务流程称为 Agent。

## 3. 状态机的基本概念

状态机至少包含：

- **状态（State）**：当前阶段及其数据；
- **事件（Event）**：模型结果、工具结果、用户批准、超时或取消；
- **守卫条件（Guard）**：是否满足转移条件；
- **动作（Action）**：进入或离开状态时执行的操作；
- **转移（Transition）**：从一个状态到另一个状态；
- **终止状态**：成功、失败、取消或等待人工。

一个订单售后任务可以是：

```text
RECEIVED
   ↓
PLANNING → NEEDS_USER_INPUT
   ↓
CHECKING_ORDER
   ↓
WAITING_APPROVAL → SUBMITTING_REFUND
   ↓                         ↓
COMPLETED                  COMPENSATING / FAILED
```

## 4. 显式状态结构

状态不要只存在 Prompt 中。可以保存成类似结构：

```python
state = {
    "schema_version": 1,
    "task_id": "task_001",
    "user_id": "user_123",
    "status": "WAITING_APPROVAL",
    "messages": [],
    "plan": {"steps": []},
    "artifacts": {},
    "tool_calls": [],
    "retry_counts": {},
    "pending_approval": None,
    "last_error": None,
    "checkpoint_version": 7,
}
```

状态应区分：

- **事实**：业务 API 已确认的结果；
- **候选**：模型生成的计划、分类或参数；
- **控制信息**：重试次数、超时、审批和版本；
- **敏感信息**：尽量只存引用，不把密钥或完整隐私数据放进状态。

## 5. 状态转移的伪代码

```python
def handle_event(state, event):
    status = state["status"]

    if status == "RECEIVED" and event.type == "START":
        return transition(state, "PLANNING")

    if status == "PLANNING" and event.type == "PLAN_READY":
        validate_plan(event.plan)
        if contains_side_effect(event.plan):
            return transition(state, "WAITING_APPROVAL", pending=event.plan)
        return transition(state, "CHECKING_ORDER", plan=event.plan)

    if status == "WAITING_APPROVAL" and event.type == "APPROVED":
        verify_approval_scope(event, state)
        return transition(state, "SUBMITTING_REFUND")

    if event.type == "CANCEL":
        return transition(state, "CANCELLED")

    raise InvalidTransition(status, event.type)
```

每次转移都应校验当前版本，避免两个 Worker 同时消费同一任务而互相覆盖。

## 6. 状态持久化与检查点

可靠的持久化至少要考虑：

- **原子写入**：状态和事件记录不能只写一半；
- **乐观并发控制**：使用版本号或 compare-and-swap；
- **幂等消费**：同一事件重复到达时不会重复产生副作用；
- **检查点**：在关键工具调用前后保存状态；
- **恢复**：进程重启后从最后一个一致状态继续；
- **Schema 版本**：状态结构升级时提供迁移；
- **保留和删除**：根据任务类型和隐私政策清理历史。

对有副作用的动作，建议先写入“准备执行”状态，再使用幂等键调用外部服务，收到确定结果后再写入“已完成”。不能把“请求已发出”误记成“业务已成功”。

## 7. 事件溯源与快照

两种常见方式：

- **快照**：直接保存当前完整状态，读取快；
- **事件溯源**：保存事件序列，通过重放得到状态，审计性强。

实际系统常采用“事件日志 + 周期性快照”。日志内容应包含任务 ID、事件 ID、状态版本、操作者和时间，但要对敏感字段脱敏。

## 8. Agent 与状态机的组合

推荐结构：

```text
状态机决定当前允许进入哪个阶段
    ↓
Agent 节点在该阶段内提出候选动作
    ↓
策略层验证候选动作
    ↓
执行器完成工具调用
    ↓
事件写入并驱动状态转移
```

这样可以把模型的不确定性限制在一个状态节点内，不让它任意跳过审批、直接进入完成状态或修改内部控制字段。

下一步：学习 [工具权限控制与可靠性](./04-工具权限控制与可靠性.md)。
