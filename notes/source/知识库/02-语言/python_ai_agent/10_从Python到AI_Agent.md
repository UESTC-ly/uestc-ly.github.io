# 10. 从 Python 到 AI Agent：原理、实现与项目

## 学习目标

完成本章后，你应该能够：

- 用工程语言解释 AI Agent，而不是把它理解成“会聊天的模型”；
- 区分模型、工具、状态、运行循环、记忆、检索和 API 边界；
- 不依赖 Agent 框架，实现一个最小、类型明确、可测试的 Agent；
- 使用 Pydantic 验证工具参数和模型结构化输出；
- 为模型调用和工具调用设计超时、错误边界、步数限制与日志；
- 使用假模型进行确定性测试；
- 判断什么时候适合引入现成框架、队列、数据库或沙箱；
- 识别提示词注入、越权工具调用、敏感信息泄漏和无限循环等风险。

本章不绑定具体模型厂商或 Agent 框架。模型 SDK 更新很快，但 Python 基础、边界设计和测试方法相对稳定。

---

## 1. AI Agent 到底是什么

一个实用定义是：

> Agent 是一个受约束的运行系统。它接收目标和上下文，让模型提出下一步动作，由程序验证并执行动作，再把结果反馈给模型，直到得到最终结果或触发停止条件。

最小循环：

```text
用户目标
   ↓
构造上下文 ───────────────┐
   ↓                      │
模型决定：回答还是调用工具 │
   ↓                      │
程序验证并执行工具         │
   ↓                      │
把工具结果写入状态 ────────┘
   ↓
最终回答 / 超时 / 达到步数上限 / 失败
```

模型不是整个 Agent。模型只负责生成候选决策，程序负责权限、验证、执行、超时、状态、审计和停止。

### 1.1 Agent 的自主程度是一条连续谱

```text
普通函数 → 固定工作流 → 带模型分支的工作流 → 受限 Agent 循环 → 高自主系统
确定性高                                                           不确定性高
测试简单                                                           成本/风险更高
```

- 普通函数：输入和步骤明确，例如计算税率；
- 固定工作流：程序决定“检索→重排→生成”；
- 模型分支：模型只在有限路由中选择；
- 受限 Agent：模型可重复选择白名单工具，但有步数、预算和权限限制；
- 高自主系统：可动态规划长期任务，需要更强沙箱、审批、恢复和评测。

自主程度不是能力排名。能用固定工作流稳定完成的任务，不应为了“像 Agent”而增加开放循环。

### 1.2 关键组成

| 组成 | 职责 | Python 知识 |
|---|---|---|
| 请求/响应模型 | 约束外部输入输出 | 类型标注、Pydantic |
| 消息与状态 | 保存一次运行的上下文 | 列表、dataclass、类 |
| 工具注册表 | 按名称发现和调度工具 | 字典、Protocol、Callable |
| Agent 循环 | 控制步骤与终止 | 函数、异常、循环、状态机 |
| 模型适配器 | 隔离具体模型 SDK | Protocol、依赖注入、async I/O |
| 工具执行器 | 验证权限、参数并执行 I/O | Pydantic、异常、asyncio |
| 可观测性 | 记录运行 ID、耗时与错误 | logging、上下文管理器 |
| API 层 | 接收请求并流式返回 | FastAPI、Uvicorn、异步生成器 |
| 测试 | 不依赖真实模型验证逻辑 | pytest、fixture、fake/mock |

### 1.3 Agent、工作流与聊天机器人

- **聊天机器人**：主要是对话输入到文本输出，可能没有工具和显式状态机；
- **工作流**：步骤由程序预先确定，结果稳定、易测试；
- **Agent**：允许模型在受控动作集合中选择下一步，路径更灵活，但不确定性更高。

优先使用确定性工作流。只有当任务路径难以预先枚举，且模型决策带来的价值高于额外风险时，才增加 Agent 自主性。很多生产系统是“固定工作流 + 少数模型决策点”，不是无限自主循环。

### 1.4 把 Agent 循环看成状态机

状态机比“模型自由思考”更适合工程实现：

```text
START
  ↓
MODEL_DECISION ── final ──→ COMPLETED
  │ tool
  ↓
VALIDATE_TOOL ── invalid ─→ MODEL_DECISION（反馈稳定错误）
  │ valid
  ↓
EXECUTE_TOOL ── recoverable error ─→ MODEL_DECISION
  │ success                         │
  └─────────────────────────────────┘

任意活动状态 ── timeout/cancel/budget ─→ STOPPED
任意活动状态 ── internal error ────────→ FAILED
```

每次转换都要有进入条件、输出事件和停止条件。这样日志、测试和恢复才能围绕状态转换设计。

---

## 2. 从用户输入到工具执行的边界

至少存在三种不可信输入：

1. 用户输入；
2. 模型生成的工具名和参数；
3. 工具返回的网页、文件或外部 API 内容。

因此必须形成明确链路：

```text
模型候选动作
  → 结构验证
  → 工具白名单
  → 调用权限与策略检查
  → 参数规范化
  → 超时/并发/大小限制
  → 执行
  → 结果清洗与截断
  → 写回上下文
```

不要因为工具调用来自模型，就把它当作可信函数调用。模型可能生成不存在的名称、错误类型、超大参数或越权路径。

### 2.1 信任边界表

| 数据来源 | 默认信任级别 | 必要处理 |
|---|---|---|
| 用户请求 | 不可信 | 认证、授权、长度、类型和内容策略 |
| 模型决策 | 不可信候选动作 | schema、白名单、权限、预算、审批 |
| 工具结果 | 不可信外部数据 | 大小限制、类型验证、来源标记、提示注入隔离 |
| 服务端配置 | 受控但可能错误 | 启动时验证、密钥隔离、最小权限 |
| 内部状态 | 仅在不变量成立后可信 | 封装、版本、并发控制、持久化校验 |

“不可信”不等于恶意，而是程序不能假设它必然满足格式、权限和业务不变量。

### 2.2 数据指令与控制指令分离

搜索结果中出现“忽略系统规则”只是检索到的文本。可以在内部协议中明确标记来源：

```python
from typing import Literal

from pydantic import BaseModel, ConfigDict


class ContextItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: Literal["user", "tool", "system"]
    source_id: str
    content: str
    trusted_as_instruction: bool = False
```

这个字段本身不能提供安全保证，但能迫使上下文构造器区分数据来源。真正权限仍由程序策略控制。

---

## 3. 先设计协议，再连接模型

### 3.1 消息协议

常见角色包括：

- `system`：系统约束；
- `user`：用户内容；
- `assistant`：模型内容；
- `tool`：工具执行结果。

不同模型 SDK 的消息格式并不完全相同。业务层应该使用自己的稳定模型，在适配器中转换成 SDK 格式，而不是让厂商对象渗透到整个项目。

内部消息模型还应按实际需求考虑：

- 稳定 `message_id`，便于去重和追踪；
- `created_at` 或单调递增顺序号；
- 工具调用 ID，使调用和结果一一对应；
- 内容类型，例如文本、图片或结构化片段；
- 可见性，区分给模型、给用户和仅内部审计的数据；
- schema 版本，支持持久化消息迁移。

不要把某个模型厂商的所有响应字段照搬成领域模型。只保留业务真正依赖的稳定语义，其余放进适配器元数据。

### 3.2 决策协议

一次模型决策可以是：

- 调用一个或多个工具；
- 直接给最终回答；
- 请求更多信息；
- 在某些系统中，产生需要人工审批的动作。

本章最小实现只保留“调用一个工具”和“最终回答”，先把核心边界做正确。

候选决策的解析步骤应是：

1. SDK 响应转换为普通 Python 数据；
2. `TypeAdapter` 或 Pydantic 判别联合做运行时验证；
3. 验证动作是否在当前状态允许；
4. 验证预算、权限和审批条件；
5. 执行，或返回模型可修正的稳定错误。

静态返回类型 `-> Decision` 只帮助开发者和检查器，不能证明远程模型的 JSON 真的有效。

### 3.3 工具协议

一个工具至少需要：

- 稳定名称；
- 面向模型的简短说明；
- 参数 schema；
- 执行函数；
- 超时和错误策略；
- 权限与副作用级别。

工具描述既是模型的选择依据，也是人类维护的接口文档。好的描述应回答：何时使用、何时不要使用、参数含义、返回范围和副作用。避免模糊地写“用于处理数据”。

```text
search_knowledge_base
用途：从已授权的内部知识库检索最多 10 条相关片段。
不要用于：实时订单状态、互联网搜索或写入数据。
输入：query（具体问题）、top_k（1..10）。
输出：source_id、title、snippet；可能截断。
副作用：只读。
```

工具名和参数名应稳定。一旦持久化到运行记录、评测集或模型提示中，随意改名会成为协议迁移。

读取天气和删除文件不能只因为都是函数就享有相同权限。

---

## 4. 项目结构

一个适合练习并可逐步扩展的结构：

```text
mini-agent/
├── pyproject.toml
├── src/
│   └── mini_agent/
│       ├── __init__.py
│       ├── models.py       # 稳定数据协议
│       ├── tools.py        # 工具抽象与注册表
│       ├── runtime.py      # Agent 控制循环
│       ├── providers.py    # 真实/假模型适配器
│       └── api.py          # FastAPI 边界
└── tests/
    ├── test_tools.py
    ├── test_runtime.py
    └── test_api.py
```

本章先用一个文件展示可运行实现，理解后再按上面的职责拆分。过早拆出大量目录只会增加跳转成本。

### 4.1 依赖方向

```text
api.py ──────→ runtime.py ─────→ tools.py
  │                │                 │
  └──────────→ models.py ←───────────┘
                   ↑
providers.py ──────┘
```

`runtime.py` 依赖自己定义的 `Model` 协议，而不是依赖具体供应商。`providers.py` 实现协议并把外部响应转换为内部模型。这样测试 runtime 时只需注入假模型。

### 4.2 配置与客户端的创建位置

- 配置在应用启动时验证一次；
- HTTP/模型客户端在 lifespan 或组合根创建并复用连接池；
- runtime 接收已经构造的依赖；
- 工具函数不应每次调用都重新读取环境变量和创建客户端；
- 测试传入内存 fake。

“组合根”是把具体实现装配起来的少数入口，例如 FastAPI lifespan 或命令行 `main()`。

---

## 5. 一个可运行的最小 Agent

安装 Pydantic：

```bash
python -m pip install "pydantic>=2"
```

将以下代码保存为 `mini_agent.py`：

```python
from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass, field
from typing import Annotated, Any, Literal, Protocol, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError


# ---------- 稳定数据协议 ----------


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Message(StrictModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    name: str | None = None


class ToolCall(StrictModel):
    name: str = Field(min_length=1)
    arguments: dict[str, Any]


class ToolDecision(StrictModel):
    kind: Literal["tool"] = "tool"
    call: ToolCall


class FinalDecision(StrictModel):
    kind: Literal["final"] = "final"
    answer: str


Decision: TypeAlias = Annotated[
    ToolDecision | FinalDecision,
    Field(discriminator="kind"),
]
RawDecision: TypeAlias = Decision | dict[str, Any]
DECISION_ADAPTER: TypeAdapter[Decision] = TypeAdapter(Decision)


class AgentResult(StrictModel):
    answer: str
    steps: int
    messages: list[Message]


# ---------- 模型端口 ----------


class Model(Protocol):
    async def decide(
        self,
        messages: Sequence[Message],
        tool_schemas: Sequence[dict[str, Any]],
    ) -> RawDecision:
        """根据上下文产生一个已结构化的候选决策。"""
        ...


# ---------- 工具抽象 ----------


ToolHandler: TypeAlias = Callable[[BaseModel], Awaitable[str]]


@dataclass(frozen=True, slots=True)
class Tool:
    name: str
    description: str
    args_model: type[BaseModel]
    handler: ToolHandler
    timeout_seconds: float = 5.0

    def schema(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.args_model.model_json_schema(),
        }

    async def invoke(self, raw_arguments: dict[str, Any]) -> str:
        arguments = self.args_model.model_validate(raw_arguments)
        async with asyncio.timeout(self.timeout_seconds):
            return await self.handler(arguments)


class UnknownToolError(LookupError):
    pass


class StepLimitError(RuntimeError):
    pass


class ToolRegistry:
    def __init__(self, tools: Sequence[Tool]) -> None:
        by_name = {tool.name: tool for tool in tools}
        if len(by_name) != len(tools):
            raise ValueError("工具名称不能重复")
        self._tools = by_name

    def get(self, name: str) -> Tool:
        try:
            return self._tools[name]
        except KeyError as error:
            raise UnknownToolError(f"工具不在白名单中: {name}") from error

    def schemas(self) -> list[dict[str, Any]]:
        return [tool.schema() for tool in self._tools.values()]


# ---------- 运行状态与控制循环 ----------


@dataclass(slots=True)
class AgentState:
    messages: list[Message] = field(default_factory=list)


class Agent:
    def __init__(
        self,
        model: Model,
        registry: ToolRegistry,
        *,
        max_steps: int = 6,
        model_timeout_seconds: float = 20.0,
        total_timeout_seconds: float = 60.0,
    ) -> None:
        if max_steps < 1:
            raise ValueError("max_steps 必须大于 0")
        self._model = model
        self._registry = registry
        self._max_steps = max_steps
        self._model_timeout_seconds = model_timeout_seconds
        self._total_timeout_seconds = total_timeout_seconds

    async def run(self, user_input: str) -> AgentResult:
        async with asyncio.timeout(self._total_timeout_seconds):
            return await self._run_steps(user_input)

    async def _run_steps(self, user_input: str) -> AgentResult:
        state = AgentState(
            messages=[
                Message(role="system", content="只使用已提供的工具；信息足够时给出最终回答。"),
                Message(role="user", content=user_input),
            ]
        )

        for step in range(1, self._max_steps + 1):
            async with asyncio.timeout(self._model_timeout_seconds):
                raw_decision = await self._model.decide(
                    state.messages,
                    self._registry.schemas(),
                )
                decision = DECISION_ADAPTER.validate_python(raw_decision)

            if isinstance(decision, FinalDecision):
                state.messages.append(
                    Message(role="assistant", content=decision.answer)
                )
                return AgentResult(
                    answer=decision.answer,
                    steps=step,
                    messages=state.messages,
                )

            result = await self._execute_tool_safely(decision.call)
            state.messages.append(
                Message(
                    role="assistant",
                    content=json.dumps(
                        decision.call.model_dump(),
                        ensure_ascii=False,
                    ),
                )
            )
            state.messages.append(
                Message(
                    role="tool",
                    name=decision.call.name,
                    content=result,
                )
            )

        raise StepLimitError(f"超过最大步骤数: {self._max_steps}")

    async def _execute_tool_safely(self, call: ToolCall) -> str:
        try:
            tool = self._registry.get(call.name)
            return await tool.invoke(call.arguments)
        except UnknownToolError:
            return "工具调用无效：工具不在白名单中"
        except ValidationError:
            # ValidationError 可能包含原始输入，不应原样反馈给模型。
            return "工具调用无效：参数未通过验证"
        except TimeoutError:
            return "工具执行超时"
        except Exception:
            # 真实项目应在这里记录带 run_id 的完整异常，
            # 但只把安全、稳定的错误文本反馈给模型。
            return "工具执行失败"


# ---------- 示例工具 ----------


class CalculatorArgs(StrictModel):
    left: float
    right: float
    operation: Literal["add", "subtract", "multiply", "divide"]


async def calculator(arguments: BaseModel) -> str:
    args = CalculatorArgs.model_validate(arguments)
    await asyncio.sleep(0)  # 让出事件循环，仅用于演示异步工具接口

    if args.operation == "add":
        value = args.left + args.right
    elif args.operation == "subtract":
        value = args.left - args.right
    elif args.operation == "multiply":
        value = args.left * args.right
    else:
        if args.right == 0:
            raise ValueError("除数不能为零")
        value = args.left / args.right
    return str(value)


# ---------- 确定性的假模型 ----------


class ScriptedModel:
    def __init__(self, decisions: Sequence[Decision]) -> None:
        self._decisions = iter(decisions)

    async def decide(
        self,
        messages: Sequence[Message],
        tool_schemas: Sequence[dict[str, Any]],
    ) -> RawDecision:
        del messages, tool_schemas
        try:
            return next(self._decisions)
        except StopIteration as error:
            raise RuntimeError("假模型没有更多预设决策") from error


async def main() -> None:
    registry = ToolRegistry(
        [
            Tool(
                name="calculator",
                description="执行两个数字的基础四则运算",
                args_model=CalculatorArgs,
                handler=calculator,
            )
        ]
    )
    model = ScriptedModel(
        [
            ToolDecision(
                call=ToolCall(
                    name="calculator",
                    arguments={"left": 12, "right": 8, "operation": "add"},
                )
            ),
            FinalDecision(answer="12 + 8 = 20"),
        ]
    )
    agent = Agent(model=model, registry=registry)

    result = await agent.run("计算 12 + 8")
    print(result.answer)
    print(f"步骤数: {result.steps}")


if __name__ == "__main__":
    asyncio.run(main())
```

运行：

```bash
python mini_agent.py
```

预期输出：

```text
12 + 8 = 20
步骤数: 2
```

### 5.1 这段实现刻意做了什么

- 使用 `Protocol` 让运行时不依赖具体模型 SDK；
- 工具只来自 `ToolRegistry` 白名单；
- 每个工具用拒绝未知字段的 Pydantic 模型验证参数；
- 使用带判别字段的联合类型，在运行时验证真实模型适配器返回的决策；
- 模型调用、工具调用和整轮运行都有分层超时；
- `max_steps` 防止无限循环；
- 内部记录完整消息，但给模型的工具失败文本保持稳定且安全；
- 使用 `ScriptedModel` 让流程在无网络、无密钥时可测试。

### 5.2 这段实现尚未解决什么

- 没有持久化会话；
- 没有真实模型适配器；
- 没有并行工具调用；
- 没有重试与退避；
- 没有请求级日志上下文；
- 没有审批和副作用分级；
- 没有 token/成本预算；
- 工具调用没有稳定 `call_id`；生产记录需要用它关联调用、结果、日志和评测行；
- 没有处理工具结果过大或包含恶意指令；
- 没有流式事件协议。

最小实现的价值是暴露这些边界，而不是假装几十行代码就是完整生产系统。

### 5.3 按一次运行理解代码

以“计算 12 + 8”为例：

1. `Agent.run` 建立总超时，并创建初始 system/user 消息；
2. `ScriptedModel` 返回 `ToolDecision`；
3. `DECISION_ADAPTER` 再做一次运行时验证；
4. 注册表按名称查找 `calculator`，未知名称不会被动态导入；
5. `CalculatorArgs` 验证参数，拒绝多余字段和非法 operation；
6. 工具在自己的 5 秒预算内执行；
7. 调用和结果分别追加到消息历史；
8. 下一次模型决策返回 `FinalDecision`；
9. runtime 记录最终 assistant 消息并返回 `AgentResult`。

这里存在三层不同的“有效”：

- JSON/对象结构有效：Pydantic 能解析；
- 动作有效：工具存在且当前允许调用；
- 业务有效：例如除数不为零、用户有权读取目标数据。

结构验证不能替代权限与业务验证。

### 5.4 为什么分别需要最大步数和总超时

`max_steps` 限制模型—工具循环次数，无法限制单步无限等待；总超时限制墙钟时间，但若每步极快，仍可能在预算内产生大量调用和成本。因此还可加入：

- 最大模型调用次数；
- 最大工具调用次数；
- token/金额预算；
- 单工具结果字节上限；
- 重复动作检测。

预算是多维度的，不能只用一个 `timeout` 代表全部资源。

### 5.5 错误为什么要分为“对内”和“对外”

内部日志需要异常类型、堆栈、run ID 和安全的诊断字段；反馈给模型或客户端的错误需要稳定、有限、脱敏。`ValidationError` 可能包含原始输入，SDK 异常可能包含 URL 或请求片段，所以不能直接 `str(error)` 对外返回。

可修正错误可以反馈“参数未通过验证”；系统内部错误应终止或进入受控恢复，而不是让模型根据堆栈猜测下一步。

---

## 6. 如何接入真实模型

为每个 SDK 写适配器，实现 `Model` 协议：

下面是沿用本章 `Message`、`Decision`、`DECISION_ADAPTER` 等定义的设计骨架，不是独立脚本：

```python
class ProviderModel:
    def __init__(self, client: object, model_name: str) -> None:
        self._client = client
        self._model_name = model_name

    async def decide(
        self,
        messages: Sequence[Message],
        tool_schemas: Sequence[dict[str, Any]],
    ) -> Decision:
        # 1. 把内部 Message 转换成厂商消息格式
        # 2. await 异步 SDK，并传入工具 schema
        # 3. 把厂商响应转换成内部字典
        # 4. 使用 DECISION_ADAPTER.validate_python(raw) 做运行时验证
        # 5. 只返回通过验证的 ToolDecision 或 FinalDecision
        raise NotImplementedError
```

适配器层应该吸收：

- SDK 消息类型差异；
- 工具 schema 格式差异；
- 流式事件格式；
- usage/token 字段差异；
- 厂商异常到内部异常的映射；
- 响应 ID 和追踪元数据。

不要让运行循环直接判断某厂商的响应类。这样更换模型、加入假模型和做回放测试都会容易很多。

### 6.1 适配器的职责清单

适配器不是简单的字段重命名器。它通常还负责：

| 职责 | 例子 |
|---|---|
| 请求转换 | 内部消息、工具 schema → SDK 请求 |
| 响应标准化 | 文本、工具调用、结束原因 → 内部 Decision |
| 用量归一 | 输入/输出 token、缓存 token、成本元数据 |
| 错误映射 | 限流、认证、超时、内容拒绝 → 内部异常类型 |
| 追踪 | 保存 provider request ID，而不污染业务协议 |
| 流式拼装 | SDK delta → 内部结构化事件 |

适配器不应决定用户是否有权调用工具，也不应在内部悄悄无限重试；这些属于 runtime 或策略层。

### 6.2 模型能力是配置，不是不变量

不同模型可能不支持相同工具 schema、上下文长度、结构化输出或流式事件。启动时可以验证能力配置，运行时仍要处理供应商拒绝、内容过滤和格式错误。不要因为模型宣称支持 JSON 就跳过 Pydantic 验证。

### 6.3 同步 SDK 怎么办

如果只有阻塞客户端，不要在高并发 `async def` 中直接调用。可以暂时使用：

```python
import asyncio
from collections.abc import Callable


async def call_blocking_sdk(
    blocking_call: Callable[[str], str],
    request: str,
) -> str:
    return await asyncio.to_thread(blocking_call, request)
```

这只是把阻塞工作移到线程，不会让它本身变成真正异步，也不会自动解决线程安全、取消和连接池问题。优先使用 SDK 的原生异步客户端。

线程中的阻塞请求在外层协程取消后未必能立即停止；应同时配置 SDK/HTTP 客户端自身的连接和读取超时。`to_thread` 解决事件循环被阻塞的问题，不提供强制终止任意线程的能力。

---

## 7. 工具设计原则

### 7.1 工具要窄而明确

不推荐：

```text
execute_anything(command: str)
```

更合适：

```text
get_order_status(order_id: str)
search_knowledge_base(query: str, top_k: int)
create_draft_ticket(title: str, description: str)
```

窄接口更容易描述、验证、授权、测试和审计。

工具粒度也不能无限小。如果完成一次订单查询必须让模型连续调用五个只返回内部 ID 的低层函数，步骤和失败面都会增加。理想工具围绕一个清晰业务能力，参数由模型有可能正确提供，结果足够支持下一步判断。

判断粒度时问：

- 这个操作能否独立授权？
- 是否有稳定输入输出契约？
- 模型是否理解参数含义？
- 失败后能否明确重试或修正？
- 合并后是否会掩盖高风险副作用？

### 7.2 读与写分离

查询通常是低风险读操作，发送、购买、删除、修改配置则有副作用。为工具标记能力：

```python
from enum import StrEnum


class SideEffect(StrEnum):
    READ_ONLY = "read_only"
    REVERSIBLE_WRITE = "reversible_write"
    IRREVERSIBLE_WRITE = "irreversible_write"
```

生产系统可以规定：

- 经过授权、范围受限且不读取高敏感数据的只读工具可以按策略自动执行；
- 可逆写操作需要明确上下文或策略许可；
- 不可逆/外部生产操作必须人工确认或走审批系统。

#### 幂等性

相同请求执行多次，最终效果与执行一次相同，称为幂等。查询通常天然幂等，创建付款通常不是。对可能重试的写工具，使用服务端幂等键：

```python
class CreateTicketArgs(StrictModel):
    title: str
    description: str
    idempotency_key: str
```

幂等键必须由业务系统持久化检查；仅在 Agent 内存中记住调用不能覆盖进程重启和网络响应丢失。

### 7.3 返回结构化、有限结果

工具结果最好包含明确状态和有限数据：

下面的模型沿用本章前面定义的 `StrictModel`：

```python
class SearchResult(StrictModel):
    title: str
    snippet: str
    source_id: str


class SearchOutput(StrictModel):
    items: list[SearchResult]
    truncated: bool
    next_cursor: str | None = None
```

不要把任意大网页、数据库全表或完整文件直接塞回模型上下文。设置条数、字节数和字段白名单，并保留可追溯来源。

`truncated` 要显式告诉模型结果是否被截断，否则模型可能把“只返回前 10 条”误解为“总共只有 10 条”。游标也不应允许模型绕过用户的数据范围授权。

### 7.4 错误也要有协议

模型需要知道能否修正，但不需要内部堆栈和密钥：

```python
class ToolError(StrictModel):
    code: Literal[
        "invalid_arguments",
        "timeout",
        "not_found",
        "temporary_failure",
        "rate_limited",
        "permission_denied",
    ]
    message: str
    retryable: bool
```

内部日志保留详细异常；外部结果使用稳定、脱敏的错误码。不要把 `repr(exception)` 无条件发送给用户或模型。

错误码应让调用方知道下一步：

| 错误 | 是否重试 | 下一步 |
|---|---|---|
| `invalid_arguments` | 否，原样重试无效 | 修正参数 |
| `not_found` | 通常否 | 更换标识或向用户澄清 |
| `temporary_failure` | 有界重试 | 指数退避并遵守总预算 |
| `rate_limited` | 延迟后可能 | 读取 retry-after、降低并发 |
| `permission_denied` | 否 | 终止并返回授权提示 |

不要把所有异常都映射成 `temporary_failure`，否则 Agent 会反复重试永久错误。

### 7.5 工具注册时就验证元数据

注册表可以在应用启动时拒绝重复名称、空描述、缺少参数模型和不合法超时。比起运行到一半才发现配置错误，启动失败更容易定位。

工具还可携带策略元数据：副作用级别、允许角色、结果大小、默认超时、是否可并发、是否需要审批。这些元数据由执行器读取，不能只写在给模型看的描述里。

---

## 8. 状态、短期记忆与长期记忆

“记忆”不是一个单一组件。

### 8.1 运行状态

只在当前 Agent 运行期间存在：消息、已用步数、工具结果、预算、取消状态。适合 `dataclass`，并由运行时显式传递。

状态对象应维护不变量，例如剩余预算不能为负、工具结果必须关联已有 call ID。不要让任意工具直接修改全局状态；执行器返回结构化事件，由 runtime 统一更新。

```python
from dataclasses import dataclass, field


@dataclass(slots=True)
class RunBudget:
    max_steps: int
    used_steps: int = 0
    used_tool_calls: int = 0

    def consume_step(self) -> None:
        if self.used_steps >= self.max_steps:
            raise RuntimeError("step budget exhausted")
        self.used_steps += 1
```

真实系统可把预算错误定义为明确领域异常；示例重点是由一个对象维护规则，而不是在循环各处分散 `+= 1`。

### 8.2 会话历史

跨多个用户轮次保存。需要数据库、会话 ID、并发控制、数据生命周期和隐私策略。不能只使用全局字典，否则多进程部署、重启和内存增长都会出问题。

会话持久化至少要考虑：

- 同一会话并发写入时的顺序或乐观锁；
- 消息去重和幂等请求 ID；
- 用户是否有权访问该 session ID；
- 删除、导出和保留期限；
- schema 升级；
- 工具结果中敏感数据的单独存储策略。

客户端提供的 session ID 只是标识，不是授权证明。

### 8.3 长期知识/检索

通常来自文档索引或业务数据库。它不是“把所有旧消息永久塞给模型”，而是根据当前查询检索有限、相关、可引用的内容。

一个典型检索管道：

```text
用户问题
  → 查询改写（可选）
  → 权限/元数据过滤
  → 召回候选文档
  → 重排
  → 截取有限片段
  → 附 source_id 放入上下文
  → 生成答案并返回引用
```

检索权限要在查询层执行，不能先检索所有用户文档再要求模型“不要使用无权内容”。索引还要记录嵌入模型和切分版本，否则重建后相似度不可比较。

### 8.4 摘要

长对话可以摘要，但摘要是有损压缩。必须区分：

- 不可丢失的结构化事实；
- 可压缩的自然语言上下文；
- 需要重新从权威系统读取的实时数据。

账户余额、订单状态等不能只依赖旧摘要。

### 8.5 上下文窗口是预算，不是数据库

放入上下文的每段内容都会占用 token、增加延迟，并可能分散模型注意力。上下文构建可以按以下优先级：

1. 必须遵守的系统/策略约束；
2. 当前用户请求；
3. 完成当前动作所需的最新结构化状态；
4. 经权限过滤的相关检索片段；
5. 必要的近期对话或摘要。

去除重复、限制单条长度，并记录每类内容的 token 预算。不要简单按“最新 N 条消息”假设一定足够。

### 8.6 记忆写入也需要质量门槛

模型推断、用户陈述和权威业务事实不是同一可信度。长期记忆应带来源、时间、主体和可撤销性；高风险事实从权威工具重新读取。否则一次模型幻觉可能被持久化并在后续会话反复强化。

---

## 9. 并发、超时、取消和重试

### 9.1 并行工具调用

只有互不依赖的工具调用才适合并发。例如同时查询天气与汇率：

```python
import asyncio


async def fetch_weather(city: str) -> str:
    await asyncio.sleep(0.01)
    return f"{city}: sunny"


async def fetch_exchange_rate(base: str, quote: str) -> float:
    await asyncio.sleep(0.01)
    return 0.14


async def query_trip_context() -> tuple[str, float]:
    # 两个调用互不依赖，所以适合放进同一个 TaskGroup。
    async with asyncio.TaskGroup() as group:
        weather_task = group.create_task(fetch_weather("Shanghai"))
        rate_task = group.create_task(fetch_exchange_rate("CNY", "USD"))

    return weather_task.result(), rate_task.result()


async def main() -> None:
    weather, rate = await query_trip_context()
    print(weather, rate)


if __name__ == "__main__":
    asyncio.run(main())
```

若第二个工具依赖第一个结果，就应顺序执行。并发前还要检查副作用：两个写工具可能互相冲突。

并发收集结果时要先定义失败语义：

- fail-fast：任一关键调用失败就取消同组任务；
- best-effort：保留成功结果，并把每个失败结构化返回；
- quorum：达到足够成功数即可停止剩余任务；
- fallback：主工具失败后才启动备选工具。

`TaskGroup` 默认更接近结构化的 fail-fast。若希望 best-effort，通常在每个子任务内部把可预期异常转换为结果，同时继续传播 `CancelledError`。

### 9.2 限制并发

```python
import asyncio


semaphore = asyncio.Semaphore(5)


async def remote_call(request: str) -> str:
    await asyncio.sleep(0.01)
    return request.upper()


async def limited_call(request: str) -> str:
    async with semaphore:
        return await remote_call(request)


async def main() -> None:
    results = await asyncio.gather(
        *(limited_call(str(index)) for index in range(10))
    )
    print(results)


if __name__ == "__main__":
    asyncio.run(main())
```

限制应与外部 API 配额、连接池和系统容量匹配，不是越大越好。

信号量限制“同时运行数”，不能直接实现“每分钟请求数”。速率限制还需要令牌桶、漏桶或外部配额器。多进程部署时，每个进程一个内存信号量也无法形成全局限制。

### 9.3 超时分层

常见超时层次：

- 单次网络连接/读取超时；
- 单个工具超时；
- 单次模型调用超时；
- 整个 Agent 运行总超时；
- API 网关或客户端超时。

内层超时应小于外层总预算，并预留清理和返回错误的时间。

#### 使用绝对截止时间传播预算

如果每层都重新给“10 秒”，嵌套调用可能累计远超总预算。更可靠的做法是记录单调时钟截止时间：

```python
import asyncio


async def run_with_deadline(deadline: float) -> str:
    loop = asyncio.get_running_loop()
    remaining = deadline - loop.time()
    if remaining <= 0:
        raise TimeoutError("budget exhausted before call")

    async with asyncio.timeout(remaining):
        await asyncio.sleep(0.01)
        return "ok"
```

下游始终根据同一个 deadline 计算剩余时间，避免预算被层层重置。

### 9.4 取消不是普通失败

任务取消时应尽快清理资源并继续传播取消，不要用宽泛的异常捕获阻断它。上下文管理器和 `finally` 用于关闭客户端、回滚临时状态。

取消是请求“尽快停止”，不是任意位置强制杀死代码。协程通常在下一个 `await` 收到取消；CPU 密集循环若长期没有 `await`，既阻塞事件循环，也不能及时响应取消。

`asyncio.shield` 只适合极少数必须完成的短清理或提交动作。滥用 shield 会让客户端断开后工作继续消耗资源。

### 9.5 只重试暂时性错误

适合有限重试：网络瞬断、服务 429/部分 5xx、短暂连接问题。

不应原样重试：参数验证失败、无权限、工具不存在、上下文过大、业务规则拒绝。

写操作重试前还要有幂等键，否则第一次已经成功但响应丢失时，第二次可能重复执行。

### 9.6 重试必须服从总预算

指数退避可以写成“等待时间逐次增加，并加入随机抖动”，但仍要限制最大次数和最大等待。每次重试前检查：

- 错误是否被分类为暂时性；
- 请求是否幂等；
- 剩余 deadline 是否足够完成下一次尝试；
- `Retry-After` 或服务端配额提示；
- 是否已经被取消。

模型格式错误通常更适合一次带明确信息的修正尝试，而不是无限重复相同提示。

### 9.7 并发预算的层级

一个 Agent 服务可能同时需要：

- 每请求工具并发上限；
- 每用户并发上限；
- 每进程连接池上限；
- 全服务供应商配额；
- 后台任务队列容量。

只在最内层加一个 Semaphore 无法解决所有层级。先定义保护的资源，再决定限流器放在哪里。

---

## 10. 可观测性

### 10.1 一次运行至少记录什么

- `run_id` / `request_id`；
- Agent 和模型版本；
- 步骤编号；
- 模型调用耗时、状态、token/成本（如果提供）；
- 工具名、耗时、状态、错误码；
- 最终停止原因：完成、超时、取消、步数上限或失败。

日志事件尽量使用稳定名称和字段，而不是只写自然语言：

```text
event=tool.completed run_id=r1 step=2 tool=search ok=true elapsed_ms=184
```

同一个字段在不同事件中保持相同类型。`elapsed_ms` 不要有时写整数、有时写“184ms”字符串，否则后续 Pandas/指标系统难以聚合。

### 10.2 不应默认记录什么

- API 密钥、Cookie、Authorization 头；
- 未脱敏的个人信息；
- 工具完整参数和响应中的秘密；
- 模型隐藏推理；
- 无限制的网页或文件全文。

日志应支持调试，同时遵守最小化收集和保留策略。

脱敏不是简单把字段名含 `password` 的值替换掉。密钥可能出现在 URL、异常消息、HTTP 头、模型输入和工具结果中。更安全的默认是字段白名单：只记录明确允许的元数据，对正文使用长度、哈希或受控采样。

### 10.3 指标与追踪

日志回答“发生了什么”，指标观察整体趋势，追踪把一次请求跨组件串起来。初学项目先做结构化日志和少量指标，不必一开始搭建复杂平台。

常见指标：

- 请求成功率；
- 各停止原因数量；
- 端到端 P50/P95/P99 延迟；
- 每工具错误率与耗时；
- 平均步骤数；
- 单次请求 token 和成本；
- 触发并发限制/超时的次数。

### 10.4 日志、指标和追踪如何配合

```text
request trace
├── model span: 850 ms, tokens=...
├── tool span: search 180 ms
└── tool span: weather 120 ms

metrics: 全服务每分钟成功率/P95
logs: 某一次失败的离散事件和安全诊断字段
```

指标发现“天气工具错误率升高”，追踪定位延迟在哪一段，日志查看具体错误类型。三者通过 `run_id`/trace ID 关联，但不需要在每个系统复制完整敏感请求。

### 10.5 停止原因是重要产品信号

把所有未成功运行归为 `error` 会失去信息。至少区分：用户取消、客户端断开、系统超时、供应商限流、步数耗尽、权限拒绝、输入验证失败和内部错误。它们的修复负责人和产品含义完全不同。

---

## 11. 测试 Agent，而不是“问几句感觉不错”

### 11.1 测试金字塔

1. **纯函数/模型测试**：参数验证、状态转换、结果截断；
2. **工具单元测试**：用假 HTTP/数据库边界；
3. **运行时测试**：用 `ScriptedModel` 预设决策；
4. **API 测试**：测试请求、响应、错误与超时；
5. **少量真实模型评测**：检查质量、成本、延迟和回归。

真实模型测试较慢、有成本且不完全确定，不能代替底层确定性测试。

测试重点不是某个具体句子，而是系统不变量。例如：

- 未知工具永远不会执行；
- 参数验证失败时 handler 调用次数为 0；
- 取消会传播，不会转为普通工具错误；
- 步数耗尽必然停止；
- 同一个幂等键不会产生两次外部副作用；
- 对外错误不含输入秘密。

### 11.2 最小运行时测试

保存本章实现后，可以写：

```python
import pytest

from mini_agent import (
    Agent,
    CalculatorArgs,
    FinalDecision,
    ScriptedModel,
    StepLimitError,
    Tool,
    ToolCall,
    ToolDecision,
    ToolRegistry,
    calculator,
)


def build_registry() -> ToolRegistry:
    return ToolRegistry(
        [
            Tool(
                name="calculator",
                description="四则运算",
                args_model=CalculatorArgs,
                handler=calculator,
            )
        ]
    )


@pytest.mark.asyncio
async def test_agent_executes_tool_then_returns_answer() -> None:
    model = ScriptedModel(
        [
            ToolDecision(
                call=ToolCall(
                    name="calculator",
                    arguments={"left": 2, "right": 3, "operation": "multiply"},
                )
            ),
            FinalDecision(answer="结果是 6"),
        ]
    )
    agent = Agent(model, build_registry())

    result = await agent.run("2 * 3 等于多少？")

    assert result.answer == "结果是 6"
    assert result.steps == 2
    assert result.messages[-2].role == "tool"
    assert result.messages[-2].content == "6.0"


@pytest.mark.asyncio
async def test_agent_stops_at_step_limit() -> None:
    invalid_calls = [
        ToolDecision(
            call=ToolCall(name="missing", arguments={})
        )
        for _ in range(2)
    ]
    agent = Agent(
        ScriptedModel(invalid_calls),
        build_registry(),
        max_steps=2,
    )

    with pytest.raises(StepLimitError):
        await agent.run("一直调用不存在的工具")
```

运行：

```bash
pytest -q
```

`ScriptedModel` 还可以记录每一步收到的消息，并断言工具结果确实反馈给下一轮，而不是只检查最终答案。对于并发代码，避免只靠 `sleep` 猜时序；使用 Event、Barrier、假时钟或可控 future 建立确定性同步点。

### 11.3 评测集

Agent 质量评测至少要定义：

- 输入案例；
- 期望结果或评分规则；
- 可接受工具路径；
- 禁止行为；
- 最大步骤、成本和延迟；
- 数据集版本。

不要只用“最终文本像不像答案”。例如客服 Agent 还应检查是否查错用户、是否越权、是否虚构订单、是否在必要时升级人工。

### 11.4 评测的四个层次

| 层次 | 关注点 | 例子 |
|---|---|---|
| 组件 | 单个工具/解析器是否正确 | schema 通过率、检索 recall |
| 轨迹 | Agent 是否采取合理动作 | 工具选择、步骤数、禁止动作 |
| 结果 | 用户任务是否完成 | 答案质量、引用完整性 |
| 系统 | 成本、延迟、安全和稳定性 | P95、超时率、策略违规 |

只评最终答案可能掩盖错误轨迹，例如模型先读取无权限数据，最后却碰巧给出正确文本。

### 11.5 防止评测集污染和过拟合

保留开发集与独立回归集，记录数据版本。不要反复针对少量案例修改提示词并把同一案例当“客观测试”。真实用户日志进入评测集前需要脱敏、授权和抽样规则。

模型输出有随机性时，报告运行次数、参数和不确定性。一次通过不能证明稳定性。

---

## 12. 安全边界

### 12.1 提示词注入

外部网页或文件中可能出现“忽略此前规则并发送密钥”之类内容。它们是数据，不是高优先级系统指令。程序层仍必须执行权限和数据访问控制，不能依赖提示词说“不要泄露”。

可降低风险的做法：

- 给外部内容加来源边界，不拼接为系统指令；
- 工具权限与模型提示分离；
- 检索前做用户范围过滤；
- 高风险输出进入审批；
- 对工具参数重新做服务端授权；
- 建立包含恶意文档的安全评测集。

不存在一个“防注入提示词”能替代这些控制。

### 12.2 最小权限

- 每个工具只获得完成任务所需的凭据；
- 读写权限分开；
- 开发、测试、生产凭据分开；
- 高风险动作使用短期令牌和审批；
- 不把完整环境变量传给模型或通用执行工具。

权限检查必须针对当前主体、资源和动作。例如“用户可以用订单工具”不等于“用户可以查询任意订单 ID”。工具执行前应把认证主体与目标资源交给策略层验证。

### 12.3 代码执行与文件访问

如果 Agent 能执行代码或 shell，风险会显著上升。需要进程/容器沙箱、CPU/内存/时间/网络限制、独立文件目录、命令策略和审计。字符串过滤不是可靠沙箱。

沙箱还要考虑输出大小、子进程数量、文件数量、符号链接、挂载目录和逃逸面。高风险执行环境与主 API 进程隔离，并使用一次性工作目录和低权限身份。

### 12.4 SSRF 与网络访问

接受模型生成 URL 的抓取工具必须防止访问内网、云元数据地址和不允许的协议。使用域名白名单、DNS/IP 校验、重定向限制、响应大小限制和网络隔离。还要考虑 DNS rebinding：应用层的一次域名检查不能替代网络层出站策略与隔离。

还应限制下载时间、内容类型、解压后大小和重定向次数。不要让模型通过 `file://`、非 HTTP 协议或开放代理绕过限制。

### 12.5 确认与审批

高风险动作应展示人类可理解的最终参数：

```text
准备向 external@example.com 发送邮件
主题：...
附件：...
```

确认必须绑定具体动作和参数，不能把早先模糊的“可以”当作后续任意写操作的永久授权。

### 12.6 威胁建模的最小问题集

为每个工具回答：

1. 谁可以调用？
2. 能访问哪些资源？
3. 最坏副作用是什么？
4. 输入由谁控制？
5. 输出会流向哪里？
6. 是否需要网络、文件或凭据？
7. 能否撤销、去重和审计？
8. 超时或部分失败后系统处于什么状态？

把答案转成代码策略和测试，而不是只留在设计文档。

---

## 13. 用 FastAPI 暴露 Agent 时的分层

推荐边界：

```text
FastAPI 路由
  → 验证请求、认证、请求 ID、总超时
  → 调用 Agent service
  → Agent runtime 调模型和工具
  → 将内部结果转换为稳定 API 响应
```

路由函数不应包含完整 Agent 循环。Agent runtime 也不应依赖 FastAPI 的 `Request` 对象。这样运行时可以在命令行、后台任务和测试中复用。

API 层还负责把内部失败映射为稳定协议：

| 内部情况 | 典型 API 行为 |
|---|---|
| 请求 schema 错误 | 4xx 验证响应 |
| 未认证/无权限 | 401/403，不调用 Agent |
| 会话不存在 | 404 或按产品定义创建 |
| 整轮超时 | 504 或异步任务状态超时 |
| 内部异常 | 通用 5xx + request ID，详细信息只进受控日志 |

HTTP 状态码不能表达所有 Agent 结束状态，响应体还可包含稳定 `stop_reason`。已经成功建立的 SSE 流通常无法中途改 HTTP 状态码，因此需要结构化 `run.failed` 事件。

### 13.1 同步响应还是流式响应

- 短任务：普通 JSON 响应简单可靠；
- 长生成：Server-Sent Events（SSE）适合服务器单向推送事件；
- 双向实时交互：可考虑 WebSocket；
- 很长任务：创建任务后返回 ID，通过轮询/事件查询状态。

流式协议应该发送结构化事件，例如 `message.delta`、`tool.started`、`tool.completed`、`run.failed`，而不是把调试日志直接混入文本流。

事件应包含单调序号或 event ID，客户端才能检测缺失、去重或重连。不要把内部完整工具参数默认广播给前端。

### 13.2 后台任务与持久化

超过普通 HTTP 生命周期的任务不能只用进程内 `create_task` 后立即返回：进程重启、部署或 worker 回收会丢失任务。需要持久化任务记录、队列/worker、幂等提交、心跳和恢复策略。

是否引入任务队列取决于真实任务持续时间与可靠性要求；短请求无需为了“可扩展”提前分布式化。

---

## 14. 何时引入 Agent 框架

先问框架是否解决了你真实需要的问题：

- 多节点状态机和条件分支；
- 持久化检查点与恢复；
- 统一工具协议；
- 人工审批；
- 追踪与评测集成；
- 多模型/多 Agent 编排。

引入前检查：

- 核心状态能否导出和迁移？
- 错误、取消和超时语义是否清楚？
- 是否可以注入假模型并做确定性测试？
- 工具参数是否仍有严格验证？
- 框架版本升级会影响哪些持久化数据？
- 是否为了十几行循环引入了大量隐式抽象？

框架能减少样板代码，但不能替你完成权限、数据契约、测试、安全和业务判断。

### 14.1 用小型试验评估框架

不要先把整个产品迁入框架。选一个代表性流程验证：

- 能否注入假模型和假工具；
- 超时、取消和异常是否按预期传播；
- 状态是否能序列化、版本化和迁移；
- tracing 是否暴露足够信息且可脱敏；
- 框架升级时持久化检查点是否兼容；
- 不使用框架专属云服务时核心能力是否仍可运行。

把试验结果与“直接实现”基线比较代码量、延迟、可测性和运维复杂度。

### 14.2 避免框架对象穿透全部代码

即使采用框架，工具参数、领域状态和 API 响应仍优先使用自己的模型。把框架事件在适配层转换，减少未来迁移面积。

---

## 15. 多 Agent 不是默认答案

多 Agent 系统引入：

- 更多模型调用和成本；
- 更长延迟；
- 状态同步与责任边界；
- 失败传播；
- 评测难度；
- 循环对话和重复工作。

只有当任务能清晰拆成具有独立上下文、输出契约和验证方式的角色时，多 Agent 才可能有价值。例如“研究—写作—事实核查”可以形成明确工件；让多个 Agent 自由聊天通常很难保证收敛。

在代码中，多 Agent 更像受控任务图，而不是虚拟会议室：

```text
规划器输出任务列表
   ├── 研究任务 A → 带来源的结构化结果
   ├── 研究任务 B → 带来源的结构化结果
   └── 数据任务 C → 表格结果
              ↓
整合器只接受通过 schema 的结果
              ↓
验证器检查声明与证据
```

### 15.1 并行的前提是任务真正独立

如果 B 必须读取 A 的结果，就不能把二者同时开始。适合并行的任务通常：

- 输入边界独立；
- 输出 schema 明确；
- 不写同一资源；
- 能分别验证；
- 合并规则预先定义。

拆分开销包括重复上下文、模型调用成本、结果冲突和整合时间。小任务直接由一个 Agent 完成可能更快。

### 15.2 主 Agent/协调器仍需负责什么

- 把目标拆成有验收标准的任务；
- 分配文件或资源所有权，避免冲突写入；
- 收集结构化结果；
- 处理失败、超时和部分完成；
- 解决冲突并运行最终验证；
- 对最终交付负责，而不是简单拼接子结果。

### 15.3 多 Agent 的停止条件

限制每个子任务的轮次、总成本和重试。Agent 互相反复评论却不产生新证据是无效循环。协调器应在结果满足契约、失败不可恢复或总预算耗尽时停止。

---

## 16. 综合项目：研究助理 Agent

### 16.1 需求

构建一个研究助理，它能够：

1. 接收一个问题；
2. 调用本地知识库搜索工具；
3. 必要时调用计算器；
4. 生成包含来源 ID 的回答；
5. 在缺乏证据时明确说明；
6. 记录工具耗时和停止原因；
7. 通过 FastAPI 暴露接口；
8. 在无网络和无模型密钥条件下完成主要测试。

### 16.2 约束

- 最多 6 步；
- 单工具超时 3 秒，整次运行 20 秒；
- 最大并发工具数 3；
- 工具结果最多 5 条，每条摘要限制长度；
- 只允许只读工具自动执行；
- 外部输入和模型决策均用 Pydantic 验证；
- 日志不得包含密钥和完整用户文档；
- 核心测试使用 `ScriptedModel`。

把约束写成测试或配置，而不是只放在 README：

- `max_steps` 和 timeout 是 runtime 构造参数；
- Pydantic `Field` 限制 top_k、文本长度和额外字段；
- Semaphore 限制实际并发；
- 结果序列化前执行条数/字节截断；
- 安全测试断言未知工具 handler 从未调用。

### 16.3 建议里程碑

#### 里程碑 A：纯 Python 领域层

- 定义消息、工具调用、最终回答和错误模型；
- 实现注册表；
- 实现本地搜索和计算器；
- 为参数验证与工具结果写测试。

交付证据：无需 FastAPI 和真实模型即可执行 `pytest tests/test_tools.py`；每个工具说明副作用和错误码。

#### 里程碑 B：Agent 循环

- 注入 `Model` 协议；
- 实现工具反馈和最大步数；
- 加入总超时与取消；
- 覆盖正常、未知工具、参数错误、超时、步数耗尽测试。

交付证据：预设脚本能复现相同轨迹；取消测试不会留下 pending task；对外错误不含原始异常文本。

#### 里程碑 C：API

- `POST /runs` 接收问题；
- `GET /healthz` 检查应用状态（路径名称可按团队约定，但应保持一致）；
- 统一错误响应；
- 使用 FastAPI lifespan 创建和关闭共享客户端；
- 使用测试客户端或 HTTPX 验证协议。

交付证据：OpenAPI 能展示请求/响应 schema；多余字段返回验证错误；无权限请求不会进入 runtime。

#### 里程碑 D：评测

- 建立至少 20 个案例；
- 定义答案正确性、来源完整性、禁止行为、步骤和延迟指标；
- 用 Pandas 生成按案例类别的成功率和 P95；
- 保存 Agent/提示词/数据集版本。

交付证据：报告可从固定 JSONL/Parquet 输入重建，同时显示样本数、失败分类、质量、延迟和成本。

### 16.4 验收清单

- [ ] 项目可从锁文件重建；
- [ ] `ruff check`、格式化检查、类型检查和 pytest 通过；
- [ ] 模型 SDK 只存在于适配器层；
- [ ] 工具只通过注册表调用；
- [ ] 参数错误不会进入工具实现；
- [ ] 未知工具不会被动态导入或执行；
- [ ] 模型与工具都有超时；
- [ ] 取消能清理资源；
- [ ] 步数、并发、结果大小和总耗时有上限；
- [ ] 写操作与只读操作有不同策略；
- [ ] 错误对外脱敏，对内可追踪；
- [ ] 核心测试不依赖真实网络；
- [ ] 评测报告同时包含指标和样本量；
- [ ] README 说明架构、运行方式、限制和风险。

---

## 17. 常见反模式

### 反模式 1：一个巨大 `agent()` 函数

验证、模型调用、工具执行、日志和 API 混在一起，导致无法替换和测试。按稳定边界拆分，而不是按“看起来高级”的层数拆分。

识别信号：测试必须启动 Web 服务才能验证工具参数；更换模型 SDK 需要修改权限逻辑；任何异常都在同一个 `try/except` 处理。

### 反模式 2：用松散字典贯穿全项目

键名拼写、缺失字段和嵌套结构直到运行深处才报错。外部边界使用 Pydantic，内部状态使用 dataclass/TypedDict/明确类。

不是所有字典都要消灭：动态 JSON 元数据可以保留字典，但稳定核心字段应建模，并限制动态区域的用途和大小。

### 反模式 3：捕获所有异常然后继续

无限吞错会让 Agent 在错误状态继续循环。区分可修正候选动作、暂时性外部错误、不可恢复系统错误和取消。

尤其不要把 `CancelledError` 变成“工具失败后继续”，否则客户端断开或总超时无法停止工作。

### 反模式 4：没有上限的自动重试和 Agent 步骤

会造成成本、限流和副作用放大。所有循环、重试、并发、结果大小和时间都要有界。

除了上限，还要记录停止原因，以便区分任务本身太复杂、工具持续失败和提示/决策逻辑循环。

### 反模式 5：测试依赖真实模型“自由发挥”

难以稳定复现，也不能精确覆盖失败分支。核心控制流使用假模型；真实模型用于更高层质量评测。

mock 不应只返回“成功”，还要覆盖畸形决策、未知工具、超时、限流、空流和中途取消。

### 反模式 6：把模型文本当成授权

模型说“用户已经同意”不构成权限证据。授权来自程序可验证的身份、策略和针对具体动作的确认。

工具结果中的网页也不能提升权限；外部内容没有资格修改系统策略。

### 反模式 7：为了 Agent 而 Agent

固定函数就能完成的任务却增加循环决策，带来成本和不确定性。先建立确定性基线，再只在需要的决策点引入模型。

衡量 Agent 的增量价值：它是否提高任务覆盖率或减少大量人工规则？如果只让流程更难解释，就应退回固定工作流。

---

## 18. 练习题

### 练习 1：工具注册表

扩展注册表，使其拒绝空名称、重复名称和不符合命名规则的工具。添加 `list_names()`，并为正常和错误路径写测试。

提示：在构造阶段完成验证；验收包含名称顺序是否稳定，以及注册失败后对象是否处于半初始化状态。

### 练习 2：结构化错误

把最小实现中的工具错误字符串改成 `ToolError` 模型。区分参数错误、未知工具、超时和内部失败，确保内部异常信息不泄露。

验收：每个错误码都有 `retryable` 语义；构造一个包含秘密的异常，证明响应中不出现秘密。

### 练习 3：运行总超时

为整个 `Agent.run` 增加总超时，使它小于各步骤最大耗时之和。测试慢模型和慢工具都能及时结束，并确认取消被传播。

提示：使用可控 Event 而不是长时间 `sleep`；验收运行结束后没有未完成任务。

### 练习 4：并发只读工具

扩展决策协议，允许一次返回多个只读工具调用。使用 `TaskGroup` 并发执行，用信号量限制为 3。定义其中一个失败时是取消全部还是收集部分结果，并写测试证明语义。

验收：记录最大同时运行数；输入顺序与结果关联不会因完成顺序不同而错位。

### 练习 5：假模型回放

让 `ScriptedModel` 同时校验每一步收到的最后一条消息，避免测试只预设输出却不验证工具结果是否正确反馈。

提示：每个脚本步骤同时保存“期望最后角色/内容谓词”和“返回决策”。

### 练习 6：请求级日志

使用 `contextvars.ContextVar` 传播 `run_id`，让模型调用和工具调用日志自动包含同一 ID。验证并发运行两个 Agent 时 ID 不串线。

验收：并发测试收集日志记录并按 run ID 分组；任务结束后上下文恢复原值。

### 练习 7：FastAPI 接口

为最小 Agent 增加 `POST /runs`，请求包含 `question` 和可选 `session_id`，响应包含答案、步骤和 `run_id`。覆盖请求验证、正常回答、超时和内部错误。

验收：响应模型不会泄露内部 messages；请求断开时上游工作被取消。

### 综合练习 8：研究助理

完成第 16 节项目，并提交：

- 架构说明；
- 工具与权限表；
- 测试报告；
- 20 条评测集和汇总结果；
- 已知限制与下一步计划。

---

## 19. 下一阶段学习方向

完成综合项目后，可按目标选择：

### 偏 Agent 应用工程

- 具体模型 SDK 的异步调用、流式输出、工具调用和结构化输出；
- 检索增强生成（RAG）、文档切分、索引和引用；
- 状态机、人工审批、任务恢复；
- 追踪、评测、缓存、成本控制。

### 偏后端与平台

- 数据库事务和连接池；
- Redis、任务队列、事件系统；
- OAuth/鉴权、密钥管理、配额；
- 容器、部署、监控、弹性与故障恢复。

### 偏机器学习与数据

- 线性代数、概率统计；
- 向量检索与排序；
- PyTorch 与 Transformer 基础；
- 数据集构建、自动评测与实验设计。

先根据项目瓶颈选择，不必同时学习所有方向。

---

## 20. 小结

- Agent 是受约束的运行系统，模型只是候选决策组件；
- 稳定的内部协议和模型适配器能隔离易变 SDK；
- 所有模型工具调用都必须经过 schema、白名单、权限和资源限制；
- 超时、取消、重试、步数和并发必须有明确且可测试的语义；
- `Protocol + Pydantic + dataclass + asyncio + pytest + FastAPI` 足以搭建清晰的 Agent 基础；
- 使用假模型测试控制逻辑，再用版本化评测集测试真实模型质量；
- 工作流通常比开放式自主循环更可靠，多 Agent 只有在任务边界和输出契约清晰时才值得；
- 安全不能靠提示词保证，必须落实在权限、沙箱、网络、审批和数据边界中。

如果你能完成本章综合项目并解释每个边界的理由，就已经跨过“会写 Python 脚本”，进入“能设计和验证 AI Agent 系统”的阶段。
