# 08. FastAPI、Uvicorn 与 Agent API

> 适用版本：Python 3.11+、FastAPI 当前稳定版、Pydantic v2   
> 本章目标：把一个可取消、可限时、返回结构化数据的假 Agent 暴露为 HTTP API，并掌握部署与测试边界。

## 学习目标

完成本章后，你应该能够：

1. 看懂 Agent API 中最常见的 HTTP 请求、响应、状态码、JSON、Header 和流式响应。
2. 使用 FastAPI 定义路由、路径参数、查询参数、请求体和响应模型。
3. 使用 Pydantic v2 校验工具输入，限制字段，生成稳定的结构化响应。
4. 使用依赖注入共享会话存储、Agent 执行器和鉴权逻辑。
5. 处理验证错误、业务错误、超时、取消和未预期异常。
6. 理解中间件、应用 lifespan、异步端点、`StreamingResponse` 和 WebSocket 的用途。
7. 知道 Uvicorn 是什么，能区分本地开发启动和生产部署。
8. 运行并测试一个不接真实模型的最小 Agent API，并知道它距离生产还缺少什么。

---

## 1. HTTP/API：只掌握 Agent 开发够用的部分

### 1.1 一次 HTTP 交互

客户端发送请求，服务端返回响应：

```text
请求：
POST /v1/sessions/9d.../messages HTTP/1.1
Content-Type: application/json
Authorization: Bearer <token>

{"message": "帮我查天气", "tools": [{...}]}

响应：
HTTP/1.1 200 OK
Content-Type: application/json
X-Request-ID: ...

{"session_id": "9d...", "answer": "...", "tool_results": [...]}
```

关键部分：

- **方法（method）**：`GET` 读取资源，`POST` 创建或触发动作，`PUT/PATCH` 更新，`DELETE` 删除。
- **路径（path）**：资源位置，例如 `/v1/sessions/{session_id}/messages`。
- **查询参数（query）**：`?limit=20&cursor=...`，适合过滤、分页和可选开关，不宜放大段提示词。
- **请求体（body）**：通常使用 JSON，适合消息、工具调用和配置。
- **Header**：传输元数据，如 `Content-Type`、认证信息、请求 ID、缓存策略。
- **状态码**：`2xx` 成功，`4xx` 客户端输入/权限问题，`5xx` 服务端或上游依赖问题。

### 1.2 Agent API 常见状态码

| 状态码 | 用法 | 示例 |
| --- | --- | --- |
| `200 OK` | 请求成功并返回结果 | Agent 回答、会话详情 |
| `201 Created` | 创建资源成功 | 创建会话 |
| `202 Accepted` | 已接收，后台异步处理 | 长任务返回 task ID |
| `400 Bad Request` | 语法或业务输入不合法 | 参数组合不允许 |
| `401 Unauthorized` | 没有有效身份凭证 | token 缺失或过期 |
| `403 Forbidden` | 身份存在但无权限 | 访问其他租户会话 |
| `404 Not Found` | 资源不存在 | session ID 不存在 |
| `409 Conflict` | 与当前状态冲突 | 幂等键重复但内容不同 |
| `422 Unprocessable Entity` | JSON 可解析但字段校验失败 | `message` 为空 |
| `429 Too Many Requests` | 触发限流 | 超出模型/工具配额 |
| `500 Internal Server Error` | 未预期服务端错误 | 程序 bug |
| `502/503/504` | 上游失败、服务不可用、超时 | 模型网关超时 |

API 一旦对外使用，状态码、错误 JSON 结构、字段名称和流式事件格式就是契约。不要让异常堆栈直接泄露给客户端。

### 1.3 一次请求的生命周期

从客户端看，请求是一次调用；从服务端看，它要经过多个边界：

```text
客户端
  → DNS / TCP / TLS（可能由代理完成）
  → 反向代理或网关
  → Uvicorn 解析 HTTP/ASGI
  → FastAPI 中间件
  → 路由参数与 Pydantic 校验
  → 依赖注入
  → Agent service / 工具 / 模型
  → 响应模型或 StreamingResponse
  → 中间件收尾、访问日志、连接关闭
```

不同阶段的超时和错误含义不同：连接还未建立时是网络错误；请求已到达但 JSON 不合法时是 422；模型上游超时通常是 504；响应头已发出后流式生成失败，只能发送一个 `error` 事件或关闭连接，不能再把 HTTP 状态码改成 500。

请求 ID 应在最外层生成并向下传递。一次 Agent 回合还应有独立的 `run_id`，因为同一个 HTTP 请求可能重试、触发多个工具或异步交给后台任务；不要把数据库主键、API key 或完整提示词当作 request ID。

### 1.4 幂等性、重试和 Agent 写操作

幂等表示同一个请求执行一次或多次，最终资源状态相同。它和“是否安全”不是完全一回事：

| 方法 | 常见语义 | 通常是否幂等 | Agent 注意事项 |
| --- | --- | --- | --- |
| `GET` | 读取 | 是（应无副作用） | 仍需鉴权，读取敏感数据不能随意缓存 |
| `PUT` | 用完整表示覆盖 | 是 | 重试前确认资源版本/乐观锁 |
| `PATCH` | 部分更新 | 取决于操作 | `increment` 等操作可能非幂等 |
| `DELETE` | 删除 | 通常是 | 第一次成功、第二次可返回 404 或保持删除状态 |
| `POST` | 创建/触发动作 | 通常否 | 用 `Idempotency-Key` 把重试绑定到同一业务动作 |

网络客户端可能在响应丢失后重试，服务端无法知道第一次 POST 是否已经成功。发送邮件、扣款、创建工单等 Agent 工具必须使用幂等键、业务去重表或事务状态；“给模型加一句不要重复”不是幂等机制。

重试要同时有次数、总时间和抖动上限，并只针对明确的暂时性错误（连接中断、429、部分 5xx）。参数错误、权限错误和业务拒绝不应重试。每次重试都要把剩余 Agent 预算传给下游，不能每一层都重新获得完整 timeout。

---

## 2. 安装与目录结构

建议让 `uv` 直接管理项目环境和依赖（本项目其他章节也会介绍 Poetry、Conda 等工具）：

```bash
uv init
uv add fastapi "uvicorn[standard]"
uv add --dev pytest httpx
```

后续统一使用 `uv run ...`，首次运行时 `uv` 会按锁文件创建或更新项目的 `.venv`，通常不必手动激活。若只是学习底层虚拟环境操作，也可以先运行 `uv venv`，然后在 macOS/Linux 执行 `source .venv/bin/activate`，在 Windows PowerShell 执行 `.venv\Scripts\Activate.ps1`。

也可以使用 pip：

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install "fastapi" "uvicorn[standard]" "pytest" "httpx"
```

一个小型项目可从以下结构开始：

```text
agent_api/
├── app/
│   ├── __init__.py
│   └── main.py
├── tests/
│   └── test_api.py
└── pyproject.toml
```

随着项目变大，再按 `routers/`、`schemas/`、`services/`、`repositories/`、`core/` 拆分。拆分的目标是隔离 HTTP 适配层与 Agent 业务层，而不是制造大量空目录。

### 2.1 ASGI、FastAPI 和 Uvicorn 的三层关系

ASGI 是 Python 异步 Web 服务器与应用之间的接口约定。可以把请求路径理解为：

```text
Uvicorn（服务器进程）
  └─ 调用 ASGI application(scope, receive, send)
       └─ FastAPI（路由、依赖、校验、OpenAPI）
            └─ 你的 Agent service / runtime / tools
```

ASGI 应用概念上接收三类信息：

- `scope`：协议、方法、路径、Header、客户端等连接元数据；
- `receive`：从客户端接收请求体、断开事件或 WebSocket 消息；
- `send`：向客户端发送响应头、响应体 chunk 或 WebSocket 帧。

HTTP 普通响应通常是“先发送 headers，再发送一个或多个 body chunk，最后标记结束”；流式响应会多次发送 body chunk；WebSocket 在握手后持续收发消息。FastAPI 把这些底层事件转换成更适合业务的函数参数和 Response 对象，Uvicorn 则负责 socket、协议解析、事件循环和进程启动。

不要在 Agent runtime 中依赖 `Request`、`WebSocket` 或 `Response`。把认证后的用户、租户、截止时间和取消信号整理成普通领域对象，runtime 才能被 HTTP、CLI、任务队列和测试复用。

### 2.2 开发依赖与可复现环境

学习阶段可以用 `uv pip install` 快速安装；项目阶段要把运行依赖、测试依赖和锁文件纳入 `pyproject.toml`。不要因为示例能在全局 Python 中启动，就认为团队环境可复现：

```text
运行依赖：fastapi、uvicorn、pydantic、异步 HTTP 客户端
测试依赖：pytest、pytest-asyncio/anyio、httpx
开发依赖：ruff、mypy/pyright、pre-commit
```

依赖版本应由项目管理工具锁定；升级 FastAPI/Pydantic 时要同时运行请求校验、响应序列化、OpenAPI、流式响应和 WebSocket 测试。Pydantic v1 与 v2 的 API（例如 `model_validate`、`model_dump`）不同，不要把两个版本的写法混在一个环境。

---

## 3. FastAPI 基础：路由、参数和模型

### 3.1 路由与参数来源

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/v1/sessions/{session_id}")
async def get_session(session_id: str, verbose: bool = False):
    return {"id": session_id, "verbose": verbose}
```

FastAPI 根据函数签名判断参数来源：

- 路径中出现的 `{session_id}` 是路径参数。
- 简单类型（如 `bool`、`int`、`str`）且不在路径中，通常是查询参数。
- Pydantic `BaseModel` 参数通常是 JSON 请求体。
- `Header`、`Cookie`、`Path`、`Query`、`Body` 可以显式表达约束和来源。

类型标注不仅帮助 IDE，也让 FastAPI 生成 OpenAPI 文档，并让 Pydantic 在进入业务代码前校验输入。

路径、查询和请求体是不同的契约，最好分别限制：

```python
from typing import Annotated

from fastapi import FastAPI, Path, Query


app = FastAPI()


@app.get("/v1/sessions/{session_id}/messages")
async def list_messages(
    session_id: Annotated[str, Path(min_length=8, max_length=64)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    include_tools: bool = False,
) -> dict[str, object]:
    return {
        "session_id": session_id,
        "limit": limit,
        "include_tools": include_tools,
    }
```

显式约束的价值不只是生成文档：它把错误挡在 Agent 运行时之前，减少无效模型调用和工具计费。路径参数适合资源身份，查询参数适合过滤/分页，请求体适合消息和复杂选项；不要把大段提示词、秘密或可变状态塞进 URL，因为 URL 可能进入代理和访问日志。

参数解析顺序可以抽象为“HTTP 解析 → 类型转换 → 约束校验 → 依赖 → 路由函数”。路由函数因此可以假设 `limit` 已经是 1 到 100 的整数，但仍需做业务级权限和资源存在性检查。

### 3.2 Pydantic 请求模型与响应模型

```python
from typing import Any, Literal

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI()


class ToolCall(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Literal["search", "weather"]
    arguments: dict[str, Any] = Field(default_factory=dict)


class AgentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(min_length=1, max_length=4_000)
    tools: list[ToolCall] = Field(default_factory=list, max_length=8)


class AgentResponse(BaseModel):
    session_id: str
    answer: str
    tool_results: list[dict[str, Any]]


@app.post("/v1/agent", response_model=AgentResponse)
async def run_agent(payload: AgentRequest) -> AgentResponse:
    return AgentResponse(
        session_id="demo",
        answer=f"收到：{payload.message}",
        tool_results=[],
    )
```

这里的 `extra="forbid"` 会拒绝未声明字段，能尽早发现客户端拼写错误，也避免把任意字段悄悄传进工具执行器。需要向后兼容时，可以选择 `extra="ignore"`，但要明确记录这一取舍。

`response_model` 会过滤和序列化返回值。它是 API 边界上的安全网：即便内部对象有调试字段，也不会自动全部暴露出去。不要把 ORM 对象、异常对象或模型 SDK 响应原样返回；定义稳定的响应模型。

Pydantic 在这里承担的是运行时边界验证，不是权限系统，也不是业务流程：

```text
JSON bytes
   ↓ FastAPI 解析
Python dict
   ↓ Pydantic model_validate / 请求模型
类型转换 + 字段约束 + 嵌套校验
   ↓
AgentRequest / ToolCall
   ↓ 仍需做授权、配额、URL/路径策略和幂等检查
工具执行
```

默认 Pydantic 会进行部分合理的类型转换，例如把可解析的数字字符串转成数字。对工具参数而言，是否接受这种转换要按风险决定；金额、ID、权限级别等字段通常更适合严格类型。`ConfigDict(strict=True)` 可以提高模型整体严格度，但仍不能替代业务规则检查。

响应模型也有边界作用：它负责筛选字段、序列化日期/UUID、生成 OpenAPI schema；它不会自动截断大结果、隐藏模型推理、检查用户是否有权看到字段。高敏感字段应设计成根本不出现在响应模型中，而不是依赖客户端忽略。

### 3.3 依赖注入

依赖是由 FastAPI 解析和调用的可复用函数，适合放置：

- 当前用户和租户鉴权；
- 数据库会话、HTTP 客户端或 Agent 执行器；
- 路径资源存在性检查；
- 限流、请求上下文和配置。

依赖会形成一张有向图，而不是简单的“函数调用列表”：

```text
send_message
  ├─ require_session
  │    └─ get_store
  ├─ get_agent
  └─ request context / auth dependency
```

FastAPI 会先解析依赖，再把结果注入路由；默认会在一次请求中缓存同一个依赖的结果。依赖应该是可替换的边界，测试时可用 `app.dependency_overrides` 注入 fake store、fake agent 或测试用户。依赖本身也可能是 `async def`，若声明为普通 `def`，FastAPI 会把它放入线程池执行；不要在同步依赖中调用异步函数而不等待。

```python
from fastapi import Depends, Header, HTTPException


async def require_api_key(x_api_key: str | None = Header(default=None)) -> str:
    if x_api_key != "development-only-key":
        raise HTTPException(status_code=401, detail="invalid API key")
    return x_api_key


@app.get("/private", dependencies=[Depends(require_api_key)])
async def private_route() -> dict[str, bool]:
    return {"ok": True}
```

示例中的密钥只用于说明依赖注入，不能放进生产代码或 Git。生产鉴权应验证签名、过期时间、发行方、受众、租户和权限，并从密钥管理系统读取配置。

---

## 4. 可运行的最小 Agent API

以下单文件示例可保存为 `app/main.py`，然后按照后文的 Uvicorn 命令启动。它覆盖：

- 会话创建和会话存在性检查；
- 工具输入的 Pydantic 校验与白名单；
- 并行执行假工具；
- 每个工具超时和整轮 Agent 总超时；
- 结构化 JSON 响应；
- SSE 风格的流式响应；
- 依赖注入、中间件、生命周期、验证错误和通用错误处理。

### 4.1 `app/main.py`

```python
from __future__ import annotations

import asyncio
import json
import logging
import time
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Literal, Self
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, ConfigDict, Field, model_validator
from starlette.websockets import WebSocketDisconnect


logger = logging.getLogger("agent-api")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")


class StrictModel(BaseModel):
    """所有 API 模型默认拒绝未声明字段。"""

    model_config = ConfigDict(extra="forbid")


class SessionResponse(StrictModel):
    id: UUID
    created_at: datetime


class SearchArgs(StrictModel):
    query: str = Field(min_length=1, max_length=500)


class WeatherArgs(StrictModel):
    city: str = Field(min_length=1, max_length=100)


class ToolCall(StrictModel):
    # Literal 是第一层白名单；动态工具系统还应在服务端再次检查权限。
    name: Literal["search", "weather"]
    arguments: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_arguments_for_tool(self) -> Self:
        args_model = SearchArgs if self.name == "search" else WeatherArgs
        args_model.model_validate(self.arguments)
        return self


class AgentRequest(StrictModel):
    message: str = Field(min_length=1, max_length=4_000)
    tools: list[ToolCall] = Field(default_factory=list, max_length=8)
    # 防止单个请求无限占用模型/工具资源。
    timeout_s: float = Field(default=5.0, ge=0.1, le=30.0)


class ToolResult(StrictModel):
    name: str
    ok: bool
    data: Any | None = None
    error: str | None = None


class AgentResponse(StrictModel):
    session_id: UUID
    answer: str
    tool_results: list[ToolResult]
    elapsed_ms: int = Field(ge=0)


class HealthResponse(StrictModel):
    status: Literal["ok"]


class SessionStore:
    """演示用的进程内会话存储；生产环境应换成数据库或 Redis。"""

    def __init__(self) -> None:
        self._history: dict[UUID, list[dict[str, str]]] = {}
        self._lock = asyncio.Lock()

    async def create(self) -> SessionResponse:
        session = SessionResponse(id=uuid4(), created_at=datetime.now(timezone.utc))
        async with self._lock:
            self._history[session.id] = []
        return session

    async def exists(self, session_id: UUID) -> bool:
        async with self._lock:
            return session_id in self._history

    async def append_turn(self, session_id: UUID, user: str, assistant: str) -> None:
        async with self._lock:
            if session_id not in self._history:
                raise KeyError(session_id)
            self._history[session_id].extend(
                [{"role": "user", "content": user}, {"role": "assistant", "content": assistant}]
            )


Tool = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]


async def fake_search(arguments: dict[str, Any]) -> dict[str, Any]:
    args = SearchArgs.model_validate(arguments)
    await asyncio.sleep(0.15)
    return {"query": args.query, "items": ["result-1", "result-2"]}


async def fake_weather(arguments: dict[str, Any]) -> dict[str, Any]:
    args = WeatherArgs.model_validate(arguments)
    await asyncio.sleep(0.10)
    return {"city": args.city, "temperature_c": 26, "condition": "sunny"}


class FakeAgentExecutor:
    """不调用真实模型的 Agent 执行器，用于学习和 API 测试。"""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {
            "search": fake_search,
            "weather": fake_weather,
        }

    async def _run_tool(self, call: ToolCall) -> ToolResult:
        tool = self._tools.get(call.name)
        if tool is None:
            return ToolResult(name=call.name, ok=False, error="tool is not allowed")

        try:
            # 单个工具预算小于整轮 Agent 预算。
            async with asyncio.timeout(2.0):
                data = await tool(call.arguments)
            return ToolResult(name=call.name, ok=True, data=data)
        except TimeoutError:
            return ToolResult(name=call.name, ok=False, error="tool timeout")
        except asyncio.CancelledError:
            # 外层超时、服务关闭等取消信号必须继续传播；部分客户端断开也会走此路径。
            raise
        except Exception as exc:
            # 只记录非敏感元数据；生产日志还需按数据策略脱敏和控权。
            logger.error("tool failed name=%s error_type=%s", call.name, type(exc).__name__)
            return ToolResult(name=call.name, ok=False, error="tool execution failed")

    async def run(
        self,
        session_id: UUID,
        message: str,
        calls: list[ToolCall],
    ) -> AgentResponse:
        started = time.perf_counter()
        results: list[ToolResult | None] = [None] * len(calls)

        async def run_at(index: int, call: ToolCall) -> None:
            results[index] = await self._run_tool(call)

        # 工具之间独立时并行；TaskGroup 会在外层取消时正确取消子任务。
        async with asyncio.TaskGroup() as group:
            for index, call in enumerate(calls):
                group.create_task(run_at(index, call), name=f"tool-{index}-{call.name}")

        tool_results = [result for result in results if result is not None]
        successful = [result for result in tool_results if result.ok]
        answer = f"已处理消息：{message}"
        if successful:
            answer += f"；成功执行 {len(successful)} 个工具。"
        else:
            answer += "；本轮没有成功的工具结果。"

        return AgentResponse(
            session_id=session_id,
            answer=answer,
            tool_results=tool_results,
            elapsed_ms=round((time.perf_counter() - started) * 1000),
        )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """应用启动时创建共享资源，退出时释放真实客户端/连接池。"""

    app.state.sessions = SessionStore()
    app.state.agent = FakeAgentExecutor()
    # 真实项目可以在这里创建 async HTTP client、数据库连接池等。
    try:
        yield
    finally:
        # 例如：await app.state.http_client.aclose()
        logger.info("application shutdown: resources released")


app = FastAPI(
    title="Learning Agent API",
    version="0.1.0",
    lifespan=lifespan,
)

# 只允许明确的前端来源；不要在 allow_origins=* 时开启 credentials。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)


@app.middleware("http")
async def request_observability(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", uuid4().hex)
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except asyncio.CancelledError:
        logger.info("request cancelled method=%s path=%s", request.method, request.url.path)
        raise
    except Exception:
        logger.exception("unhandled request error path=%s", request.url.path)
        raise

    elapsed_ms = round((time.perf_counter() - started) * 1000)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-Ms"] = str(elapsed_ms)
    logger.info(
        "request method=%s path=%s status=%s elapsed_ms=%s request_id=%s",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
        request_id,
    )
    return response


def get_store(request: Request) -> SessionStore:
    return request.app.state.sessions


def get_agent(request: Request) -> FakeAgentExecutor:
    return request.app.state.agent


async def require_session(
    session_id: UUID,
    store: SessionStore = Depends(get_store),
) -> UUID:
    if not await store.exists(session_id):
        raise HTTPException(status_code=404, detail="session not found")
    return session_id


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "detail": "request validation failed",
            "errors": jsonable_encoder(exc.errors()),
        },
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("internal error path=%s", request.url.path, exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "internal server error"})


@app.get("/healthz", response_model=HealthResponse, tags=["system"])
async def healthz() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/v1/tools", response_model=list[str], tags=["tools"])
async def list_tools(agent: FakeAgentExecutor = Depends(get_agent)) -> list[str]:
    return sorted(agent._tools)


@app.post(
    "/v1/sessions",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["sessions"],
)
async def create_session(store: SessionStore = Depends(get_store)) -> SessionResponse:
    return await store.create()


@app.post(
    "/v1/sessions/{session_id}/messages",
    response_model=AgentResponse,
    tags=["agent"],
)
async def send_message(
    payload: AgentRequest,
    session_id: UUID = Depends(require_session),
    store: SessionStore = Depends(get_store),
    agent: FakeAgentExecutor = Depends(get_agent),
) -> AgentResponse:
    try:
        # 这是 API 业务操作总预算；外层超时会取消正在运行的 TaskGroup。
        async with asyncio.timeout(payload.timeout_s):
            result = await agent.run(session_id, payload.message, payload.tools)
            await store.append_turn(session_id, payload.message, result.answer)
    except TimeoutError as exc:
        raise HTTPException(status_code=504, detail="agent turn timed out") from exc

    return result


def sse(event: str, data: Any) -> str:
    """生成最小 SSE 帧；生产实现应考虑 data 中的换行、事件 ID 和重连。"""

    encoded = json.dumps(data, ensure_ascii=False, default=str)
    return f"event: {event}\ndata: {encoded}\n\n"


async def stream_agent(
    payload: AgentRequest,
    session_id: UUID,
    store: SessionStore,
    agent: FakeAgentExecutor,
) -> AsyncIterator[str]:
    try:
        # 预算覆盖 Agent、事件发送间隔和会话写入；网关还应设置匹配的超时。
        async with asyncio.timeout(payload.timeout_s):
            yield sse("status", {"state": "started", "session_id": str(session_id)})
            result = await agent.run(session_id, payload.message, payload.tools)

            for tool_result in result.tool_results:
                yield sse("tool", tool_result.model_dump(mode="json"))
            for token in result.answer.split():
                yield sse("token", token)
                await asyncio.sleep(0.02)  # 模拟上游 token 到达

            await store.append_turn(session_id, payload.message, result.answer)
            yield sse("done", result.model_dump(mode="json"))
    except TimeoutError:
        yield sse("error", {"code": "agent_timeout", "message": "agent turn timed out"})
    except asyncio.CancelledError:
        # 外层取消或部分客户端断开路径：关闭上游流/工具，不要吞掉取消异常。
        logger.info("stream cancelled session_id=%s", session_id)
        raise


@app.post(
    "/v1/sessions/{session_id}/messages/stream",
    response_class=StreamingResponse,
    tags=["agent"],
)
async def stream_message(
    payload: AgentRequest,
    session_id: UUID = Depends(require_session),
    store: SessionStore = Depends(get_store),
    agent: FakeAgentExecutor = Depends(get_agent),
) -> StreamingResponse:
    return StreamingResponse(
        stream_agent(payload, session_id, store, agent),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.websocket("/ws/echo")
async def websocket_echo(websocket: WebSocket) -> None:
    """WebSocket 最小示例；真实 Agent 还需鉴权、心跳、消息大小和背压。"""

    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            await websocket.send_json({"type": "echo", "content": message})
    except WebSocketDisconnect:
        logger.info("websocket disconnected")
```

运行后，访问 `http://127.0.0.1:8000/docs` 可以看到 OpenAPI 交互文档。创建会话并发送消息：

```bash
curl -s -X POST http://127.0.0.1:8000/v1/sessions

# 把上一步返回的 UUID 替换到路径中
curl -s -X POST \
  http://127.0.0.1:8000/v1/sessions/<SESSION_ID>/messages \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "查询上海天气",
    "tools": [{"name": "weather", "arguments": {"city": "上海"}}],
    "timeout_s": 5
  }'

curl -N -X POST \
  http://127.0.0.1:8000/v1/sessions/<SESSION_ID>/messages/stream \
  -H 'Content-Type: application/json' \
  -d '{"message":"流式回答","tools":[]}'
```

### 4.2 示例代码的设计解读

- `SessionStore` 使用 `asyncio.Lock` 保护同一事件循环内的共享状态；它只是演示，多个 Uvicorn worker 或多个容器之间不会共享这份字典。
- `ToolCall.name` 使用 `Literal` 做输入白名单，执行器仍保留服务端字典查找，避免把用户输入直接当作 Python 函数名或命令执行。
- 每个工具有 2 秒预算，整轮有请求指定的更大预算。超时由 `asyncio.timeout` 触发取消，`TaskGroup` 负责管理并行工具 Task。
- 工具普通异常被转换为 `ToolResult(ok=False)`，独立工具仍可返回；外层取消产生的 `CancelledError` 不被吞掉。客户端断开也可能表现为 ASGI 断开事件或后续发送失败，具体取决于协议和服务器阶段。
- `response_model=AgentResponse` 固定了 JSON 契约。流式端点不返回普通 JSON，而是返回 SSE 帧；最后的 `done` 事件携带同样的结构化结果。
- `lifespan` 是创建和关闭共享资源的边界。真实的异步 HTTP 客户端、数据库池和模型连接应在这里初始化/关闭。
- 中间件统一生成请求 ID、耗时 Header 和日志。生产日志需要脱敏，不能记录 API key、完整提示词、模型密钥或隐私数据。

### 4.3 一次调用的状态机与失败边界

把“路由函数返回一个对象”想成完整服务是不够的。一次 JSON 调用至少经历下面这些状态：

```text
连接建立
  → 请求体读取
  → 路由匹配
  → 参数/Pydantic 校验
  → 依赖解析（会话、存储、执行器）
  → Agent 运行（模型 + 工具 Task）
  → 写入会话历史
  → 响应模型序列化
  → 发送响应并记录完成
```

其中每个箭头都可能失败。比如 JSON 解析或字段校验失败时，`send_message` 根本不会被调用；会话不存在时，`require_session` 直接返回 404；工具超时可能只是某个 `ToolResult(ok=False)`，整轮超时则由外层 `asyncio.timeout` 取消 Agent 并返回 504。将这些边界分开，客户端才知道是“修正输入”“重试上游”还是“稍后查询任务”。

同步 JSON 端点的关键时序是：

```text
T0  验证 message/tools/timeout_s
T1  检查 session_id
T2  启动独立工具 Task（若有）
T3  所有工具完成或整轮预算耗尽
T4  成功结果写入 SessionStore
T5  Pydantic 序列化 AgentResponse，发送 200
```

`T4` 很重要：示例在写历史成功后才返回结果；如果希望“响应发送成功”和“历史写入”具备更强的一致性，应使用数据库事务或持久化事件，而不是依赖进程内字典。反过来，如果工具已经产生外部副作用，`T3` 之后在 `T4` 超时并不代表副作用被撤销，因此写操作要有幂等键和补偿策略。

流式端点的时序不同：

```text
发送 HTTP headers（通常状态码已经确定为 200）
  → status
  → tool / token / heartbeat ...
  → done 或 error
  → 关闭迭代器和连接
```

第一帧发出后，不能再把 HTTP 状态码改成 504。示例把可表达的超时编码成 SSE `error` 事件；客户端必须把 `done` 视为成功终点，把 `error`、断线或无终止事件视为不完整回合。若 `append_turn` 失败，模型答案可能已经显示给用户，服务端应通过事件 ID、持久化运行记录和重试接口恢复，而不是假设客户端一定会重新提交同一 POST。

下面的纯 Python 小例子展示了“只提交完整回合”的状态转移，便于在没有启动 FastAPI 时理解边界：

```python
from dataclasses import dataclass


@dataclass
class RunState:
    state: str = "created"
    answer: str | None = None

    def begin(self) -> None:
        if self.state != "created":
            raise RuntimeError("run already started")
        self.state = "running"

    def complete(self, answer: str) -> None:
        if self.state != "running":
            raise RuntimeError("run is not running")
        self.answer = answer
        self.state = "completed"

    def fail(self) -> None:
        if self.state == "completed":
            raise RuntimeError("completed run cannot fail")
        self.state = "failed"


run = RunState()
run.begin()
run.complete("假 Agent 已完成")
print(run.state, run.answer)
```

这里的状态机只是领域层示意，并没有替代数据库事务或分布式工作流。真实 Agent 还应给每个回合分配 `run_id`，记录 `created/running/completed/failed/cancelled` 和取消原因，以便重试、计费、审计和断线恢复。

---

## 5. FastAPI 的关键能力

### 5.1 错误处理

业务可预期的错误用 `HTTPException`：

```python
from fastapi import HTTPException


if not user_can_access_session:
    raise HTTPException(status_code=403, detail="forbidden")
```

输入模型失败时 FastAPI 返回 422；可以注册 `RequestValidationError` 处理器，把错误格式统一为团队契约。未知异常应在服务端记录完整堆栈、向客户端返回通用 500，不要泄漏内部路径和上游响应。

区分三类错误：

1. **客户端输入错误**：字段缺失、类型错误、超出长度，通常 422/400。
2. **可恢复的上游错误**：模型 429、工具超时、网络错误，通常映射为 429/502/504，并附带可重试信息。
3. **程序错误**：断言失败、状态不一致、未处理异常，记录并返回 500，不能伪装成用户输入错。

### 5.1.1 异常边界：谁负责转换，谁负责记录

建议把异常转换放在“最接近契约边界”的一层：

| 异常位置 | 例子 | 领域层动作 | HTTP 层动作 |
| --- | --- | --- | --- |
| 请求解析/模型校验 | 缺少 `message`、未知工具字段 | 不进入 Agent | 422，返回字段错误位置 |
| 鉴权/资源检查 | token 过期、会话不属于租户 | 抛出领域拒绝 | 401/403/404，避免泄露资源存在性 |
| 工具执行 | 第三方 429、工具超时 | 封装为可观察的工具失败或上抛可恢复错误 | 200 + `ToolResult(ok=False)`，或整轮 429/504 |
| Agent 总预算 | `TimeoutError` | 取消子任务并记录剩余预算 | JSON 504；流式则发送 `error` 事件 |
| 客户端断开 | 取消异常、ASGI 断开事件或发送失败 | 清理上游；若收到取消则继续传播 | 通常无法再发送响应，不伪装为 500 |
| 程序 bug | `KeyError`、状态不变量失败 | 记录完整堆栈和 `run_id` | 通用 500，不返回内部细节 |

不要在每一层都写 `except Exception: return ...`。这样会把取消、超时和程序 bug 混成同一种“工具失败”，既阻止正确清理，也让监控失去意义。至少要单独处理并重新抛出 `asyncio.CancelledError`；对 `TimeoutError` 要知道它是某个局部工具预算还是整轮预算产生的。由于业务库也可能主动抛出同名的内置 `TimeoutError`，生产代码最好为“预算超时”和“上游声明超时”保留不同的错误类别，避免错误码和重试策略混淆。

一个通用异常处理器应做到“客户端稳定、服务端可诊断”：

```python
from fastapi import Request
from fastapi.responses import JSONResponse


@app.exception_handler(RuntimeError)
async def domain_error_handler(request: Request, exc: RuntimeError) -> JSONResponse:
    # 生产环境应从 request.state 取 request_id，并记录 run_id/错误类别。
    logger.warning("domain error path=%s type=%s", request.url.path, type(exc).__name__)
    return JSONResponse(
        status_code=409,
        content={"code": "domain_conflict", "message": "request conflicts with state"},
    )
```

示例只把 `RuntimeError` 映射为 409 是一种项目约定，不是 FastAPI 的默认规则。不要用异常类型替代明确的错误代码：多个上游可能都是 `TimeoutError`，但客户端需要知道是模型、工具还是网关超时。建议在内部错误对象中保存 `category`、`retryable`、`run_id` 和原始异常（仅日志可见），在 HTTP/SSE 层只输出稳定的 `code`、简短 `message`、`request_id`。

### 5.2 中间件

中间件包住每个请求，适合做请求 ID、访问日志、耗时、CORS、压缩和安全 Header。它不适合承载复杂 Agent 业务逻辑，否则会让所有路由共享隐式行为。

注意流式响应：响应对象返回后，流的实际发送可能还在进行；如果要测量“完整流耗时”，需要在异步生成器或发送层额外记录，而不能只依赖 `call_next` 返回时刻。

### 5.2.1 中间件的洋葱模型与流式边界

多个 HTTP 中间件通常按“先进后出”包住路由：

```text
请求进入
  → Middleware A 前置
    → Middleware B 前置
      → 路由/StreamingResponse
    ← Middleware B 后置
  ← Middleware A 后置
响应离开
```

因此请求 ID、认证、CORS 和访问日志的顺序会影响观察结果。例如，日志中间件放在异常转换外侧，才能看到未处理异常；放在流式生成器外侧时，`call_next` 返回通常只表示“拿到了响应对象”，不表示最后一个 token 已经发出。完整流耗时应由生成器在 `try/finally` 中记录，或者在 ASGI `send` 层观察 `http.response.body` 的 `more_body=False`。

一个最小的流式清理模式如下：

```python
import asyncio
import json
import logging
import time
from collections.abc import AsyncIterator


logger = logging.getLogger("stream-example")


def sse(event: str, data: object) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


async def tracked_stream() -> AsyncIterator[str]:
    started = time.perf_counter()
    try:
        yield sse("status", {"state": "started"})
        for token in ("hello", "agent"):
            yield sse("token", {"text": token})
            await asyncio.sleep(0)
        yield sse("done", {"ok": True})
    finally:
        elapsed_ms = round((time.perf_counter() - started) * 1000)
        logger.info("stream finished elapsed_ms=%s", elapsed_ms)


async def main() -> None:
    async for chunk in tracked_stream():
        print(chunk, end="")


asyncio.run(main())
```

真实生成器的 `finally` 中还应取消模型流、释放工具连接、记录是 `completed`、`timeout` 还是 `client_disconnected`。不要在中间件里读取或缓存完整响应正文来做日志：这会破坏流式特性，并可能把提示词、token 或隐私数据写入日志。

### 5.3 生命周期（lifespan）

推荐用 `lifespan` 管理应用级资源：

```python
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.client = await create_async_client()
    try:
        yield
    finally:
        await app.state.client.aclose()


app = FastAPI(lifespan=lifespan)
```

不要在模块导入时建立需要网络或凭证的连接，也不要每个请求创建一个新的连接池。使用多 worker 时，每个 worker 都会执行一次 lifespan，因此连接数和内存会按 worker 数量增长。

### 5.3.1 `lifespan` 的所有权、失败和关闭顺序

`lifespan` 中 `yield` 之前是启动阶段，`yield` 之后的 `finally` 是关闭阶段。只有成功走到 `yield`，应用才应开始接收正常请求：

```text
进程启动
  → 创建配置/连接池/模型客户端
  → 任一必需资源失败：启动失败，不接流量
  → yield：应用 ready
  → 接收请求
  → 停止接收新请求
  → 等待/取消在途 Agent
  → 关闭模型客户端、HTTP 客户端、数据库池
  → 进程退出
```

资源关闭顺序通常与依赖关系相反：先停止使用连接池的 Agent/后台任务，再关闭连接池；先停止事件生产，再关闭队列消费者。不要把一个需要 `await` 的客户端放在全局变量中却没有关闭路径，也不要在 `finally` 中吞掉关闭异常而完全不记录。

每个 Uvicorn worker 都会独立执行一次 lifespan。若初始化的是本地模型、线程池或连接池，应按 worker 数量计算内存、文件描述符和上游连接预算；若资源必须全局唯一，应改由外部服务或单独的 worker 管理，而不是假设 `app.state` 会跨进程共享。

### 5.4 `async def` 端点与阻塞代码

异步端点的原则：

```python
@app.get("/data")
async def get_data():
    return await async_client.get("https://example.com")
```

如果在其中调用 `requests.get`、`time.sleep`、同步数据库驱动或大段 CPU 循环，会阻塞事件循环，拖慢同一 worker 的其他请求。换成异步库；无法替换时用 `await asyncio.to_thread(sync_function, ...)`，并设置线程池、客户端 timeout 和并发上限。

普通 `def` 路由/依赖由 FastAPI 放到线程池执行，但这不是“代码自动变成异步”：线程池仍有限，阻塞操作仍消耗线程，纯 Python CPU 工作仍受默认 CPython GIL 影响。对 Agent API，优先显式选择异步客户端，只有兼容层才放线程。

### 5.4.1 同步兼容层的桥接决策

`asyncio.to_thread()` 适合短时、可取消等待意义上的同步 I/O；它不会强行终止已经在线程中运行的函数。超时取消的是等待该线程结果的协程，底层函数可能继续跑到自然返回。因此桥接的函数必须有自己的连接超时、读取超时和资源上限，不能把 `to_thread` 当成进程级沙箱。

```python
import asyncio


def blocking_lookup(query: str) -> str:
    # 这里模拟 requests/同步 SDK 调用；真实函数必须配置客户端 timeout。
    return f"result:{query}"


async def lookup_for_route(query: str) -> str:
    try:
        async with asyncio.timeout(1.0):
            return await asyncio.to_thread(blocking_lookup, query)
    except TimeoutError:
        # 这里只能保证路由不再等待；不能保证 blocking_lookup 已停止。
        raise
```

选择顺序可以是：先找原生异步客户端；无法替换且是 I/O，再桥接到有上限的线程池；若是长时间 CPU 工作，考虑进程池或独立任务队列；若必须在超时后立即停止不可信代码，使用独立进程/沙箱。每个请求都 `to_thread` 而不设并发上限，可能把线程池和下游连接同时打满。

### 5.5 流式响应

`StreamingResponse` 接受同步或异步迭代器：

```python
import asyncio
from collections.abc import AsyncIterator
from fastapi.responses import StreamingResponse

# 沿用前文创建的 app。

async def chunks() -> AsyncIterator[bytes]:
    for item in ["first", "second"]:
        yield (item + "\\n").encode()
        await asyncio.sleep(0.1)


@app.get("/stream")
async def stream() -> StreamingResponse:
    return StreamingResponse(chunks(), media_type="text/plain")
```

常用协议：

- **SSE（Server-Sent Events）**：服务端单向推送，浏览器易消费；使用 `text/event-stream`，每个事件以空行分隔。
- **NDJSON**：每行一个 JSON 对象，适合命令行和服务间消费。
- **WebSocket**：双向长连接，适合实时交互、客户端中途发取消或多路事件。

流式 Agent 要定义事件 schema，例如 `status`、`tool_call`、`tool_result`、`token`、`error`、`done`；定义心跳、序号、重连、幂等和断线后的状态恢复。不要把任意 Python 对象直接 `yield` 给客户端。

### 5.5.1 SSE 帧、缓冲和背压

SSE 不是“把字符串不断打印出来”这么简单。一个事件由若干行组成，以空行结束；常用字段包括 `event`、`data`、`id` 和 `retry`：

```text
event: token
id: 17
data: {"text":"你好"}

```

`data` 中若含换行，应拆成多个 `data:` 行；客户端按空行组装事件。生产 API 通常把事件内容限制为 JSON，并为每个回合提供单调递增序号。`id` 只能帮助客户端重连定位，不会自动让事件持久化或去重。

```python
import json


def sse_frame(event: str, data: dict[str, object], event_id: int) -> str:
    encoded = json.dumps(data, ensure_ascii=False)
    # 每个 data 行都必须有前缀；这里把换行转成多行 SSE 数据。
    lines = encoded.splitlines() or [""]
    return "".join(
        [f"event: {event}\n", f"id: {event_id}\n"]
        + [f"data: {line}\n" for line in lines]
        + ["\n"]
    )


print(sse_frame("token", {"text": "你好"}, event_id=1))
```

服务器生成器 `yield` 出一个 chunk 不代表客户端已经在屏幕上看到它：代理、服务器和浏览器都可能缓冲。生产配置通常要关闭代理缓冲、设置 `Cache-Control: no-cache`，并用心跳保持空闲连接。生成器若持续生产而网络发送很慢，ASGI 服务器的发送过程会形成反压；仍应限制 token 队列、单连接缓存和最大流时间，避免无限积压。

客户端断开时，生成器往往收到 `CancelledError` 或发送失败；应在 `finally` 中停止模型/工具任务。若已发送 `done` 后再发生日志或关闭异常，不要向客户端追加第二个 `error` 终点；服务端要依靠运行记录区分“业务完成”和“传输完成”。

### 5.6 WebSocket 简介

WebSocket 通过一次 HTTP 升级建立长连接，之后双方都可以发送消息。它不是自动解决鉴权、连接数、背压和可靠投递的方案：

- 连接建立时验证 token、租户和会话权限；
- 限制帧大小、并发连接数和单连接发送速率；
- 使用 ping/pong 或应用层心跳清理死连接；
- 客户端断开时取消 Agent Task，并关闭上游模型流；
- 若需要断线重连，给事件分配递增 ID 或使用持久化事件日志；
- 多副本部署时，考虑 sticky session、共享状态或专门的消息系统。

### 5.6.1 WebSocket 状态机与取消

可以把 WebSocket 看成一个长期存在的会话状态机：

```text
CONNECTING --accept--> OPEN --close/断网--> CLOSING --> CLOSED
                         │
                         ├─ receive message
                         ├─ send event（可能等待网络背压）
                         └─ Agent Task / heartbeat
```

`accept()` 前可以拒绝握手；进入 `OPEN` 后，`receive_*` 和 `send_*` 都可能抛出断开相关异常。一个连接应有明确的所有者负责创建和取消 Agent Task。以下短例沿用前文创建的 `app`：

```python
import asyncio

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect


@app.websocket("/ws/agent")
async def websocket_agent(websocket: WebSocket) -> None:
    await websocket.accept()
    agent_task: asyncio.Task[str] | None = None
    try:
        message = await websocket.receive_text()
        agent_task = asyncio.create_task(
            asyncio.sleep(0.05, result=f"已处理：{message}"),
            name="fake-agent-run",
        )
        answer = await agent_task
        await websocket.send_json({"type": "done", "answer": answer})
    except WebSocketDisconnect:
        if agent_task is not None:
            agent_task.cancel()
            await asyncio.gather(agent_task, return_exceptions=True)
    finally:
        if agent_task is not None and not agent_task.done():
            agent_task.cancel()
            await asyncio.gather(agent_task, return_exceptions=True)
```

这是教学示例，不包含鉴权和多消息协议。真实服务还要限制单连接是否允许并行回合、定义客户端取消消息、避免“旧回合 token”串入新回合，并把长期任务的可靠状态放到外部存储。若只是服务端单向推送，SSE 通常比 WebSocket 更简单；只有确实需要双向实时消息、客户端取消或交互控制时才选择 WebSocket。

---

## 6. Uvicorn：ASGI 应用服务器

FastAPI 是 Web 框架，负责路由、依赖、校验和应用逻辑；Uvicorn 是 ASGI 服务器，负责监听 socket、HTTP/协议处理、将请求交给 FastAPI，并管理事件循环与 worker 启动。

### 6.1 启动命令

假设文件为 `app/main.py` 且对象名为 `app`：

```bash
# 开发：自动重载，代码变化后重启；不要用于生产
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 本地/容器：明确监听地址
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

# 单机多 worker（每个 worker 是独立进程）
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

也可以程序化启动，但 `reload=True` 或 `workers>1` 时要放在 `if __name__ == "__main__"` 保护中：

```python
import uvicorn


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
```

`--reload` 与 `--workers` 是互斥模式，不能同时使用。生产环境应固定依赖、关闭 reload、设置合理的超时/并发/最大请求配置，并让反向代理或平台负责 TLS、域名、健康检查和滚动发布。

### 6.1.1 `module:app`、监听地址与配置来源

`app.main:app` 是“导入 `app/main.py`，取其中名为 `app` 的对象”，不是文件路径字符串随便写。启动失败时先检查：当前工作目录是否能导入包、`app/__init__.py` 是否存在（或是否使用了正确的命名空间包）、模块导入阶段是否执行了不应执行的网络连接。

几个容易混淆的参数：

| 参数 | 作用 | Agent 服务注意事项 |
| --- | --- | --- |
| `--host` | 监听网卡地址 | `127.0.0.1` 只供本机；容器内通常监听 `0.0.0.0`，但安全边界交给网络策略 |
| `--port` | TCP 端口 | 由平台/容器编排注入，避免硬编码多个环境 |
| `--reload` | 代码变化后重启开发进程 | 会增加监视和重启开销，不是生产高可用 |
| `--workers` | 启动多个独立进程 | 每个进程有自己的内存、事件循环和 lifespan |
| `--proxy-headers` | 读取代理转发的 scheme/客户端信息 | 只能和可信代理地址白名单一起使用 |

在生产环境优先使用环境变量、平台配置或明确的启动脚本提供端口、worker 数和日志级别；不要把含密钥的连接串直接写进 shell 历史或命令行参数。启动命令是进程入口，应用代码仍应负责业务 timeout、取消和资源清理，两者不是同一个超时层。

### 6.2 worker 与进程内状态

四个 worker 不是四个共享内存的线程，而是四个独立进程：

```text
负载均衡器
    ├── worker 1：自己的 event loop、SessionStore、连接池
    ├── worker 2：自己的 event loop、SessionStore、连接池
    ├── worker 3：自己的 event loop、SessionStore、连接池
    └── worker 4：自己的 event loop、SessionStore、连接池
```

因此示例中的进程内会话字典在多 worker 下会出现“同一个 session 在某个请求中不存在”的问题。生产会话、任务状态、幂等键和限流计数放在共享数据库/缓存/任务系统；模型客户端是否能在每个进程各开一个连接池，要结合供应商配额和内存评估。

### 6.2.1 worker 数量、事件循环和优雅关闭

一个 worker 通常运行一个主事件循环并处理许多 I/O 等待中的请求；它不是把同一个 Python 堆分给多个 worker。多 worker 的总并发能力同时受下面因素限制：

```text
可接收请求数
  ≤ worker 数 × 每 worker 的可运行任务/连接上限
  ≤ 模型供应商配额、数据库连接池、工具并发和内存预算
```

worker 数增加可能提高 CPU 利用率或隔离阻塞，但也会复制模型客户端、连接池、缓存和 `lifespan` 资源；如果 Agent 请求主要等待同一个上游，盲目增加 worker 反而会触发上游 429。应使用压测和指标决定，而不是把 CPU 核数直接当作 worker 数。

优雅关闭可以理解为：先拒绝新工作，再给在途请求一个有限窗口，超时后取消并释放资源。流式响应尤其要记录“请求取消”和“进程关闭”的不同原因；不要无限等待一个无响应的上游连接。容器的停止宽限期应大于应用的清理窗口，并和反向代理的连接超时协调。

### 6.3 反向代理与安全

常见生产拓扑是：TLS 终止和访问控制在 Nginx、云负载均衡器或网关，Uvicorn 在内网监听。配置 `--proxy-headers`、`--forwarded-allow-ips` 时只信任明确的代理地址，否则客户端可以伪造 scheme、host 或来源 IP。

至少检查：

- HTTPS、认证和授权；
- CORS、Trusted Host、代理 Header；
- 请求体/上传文件/单条消息大小；
- Agent 和工具的超时、并发上限、重试预算；
- 日志脱敏、请求 ID、指标和 trace；
- 容器优雅关闭，给正在流式传输的请求留出退出时间；
- 健康检查不应把“能启动”误当作“模型/数据库完全可用”。

健康检查至少区分两类：存活检查（进程和事件循环还在）以及就绪检查（必需配置/数据库/模型网关可用）。不要让存活检查调用昂贵的模型；就绪检查也应设置很短的超时，避免健康探针本身耗尽 Agent 连接池。部署滚动升级时，旧 worker 可能仍在发送 SSE，应允许连接自然结束或发送可恢复的运行 ID，不能假设 TCP 关闭等于业务取消已经持久化。

---

## 7. 测试 FastAPI Agent API

### 7.1 `TestClient` 测试同步 HTTP 场景

`TestClient` 在测试中把 ASGI 应用包装成类似同步 HTTP 客户端的接口。使用上下文管理器会触发生命周期 startup/shutdown：

```python
# tests/test_api.py
from fastapi import Request
from fastapi.testclient import TestClient

from app.main import app


def test_create_session_and_run_agent() -> None:
    with TestClient(app) as client:
        create_response = client.post("/v1/sessions")
        assert create_response.status_code == 201
        session_id = create_response.json()["id"]

        response = client.post(
            f"/v1/sessions/{session_id}/messages",
            json={
                "message": "查天气",
                "tools": [{"name": "weather", "arguments": {"city": "上海"}}],
                "timeout_s": 3,
            },
        )

        assert response.status_code == 200
        body = response.json()
        assert body["session_id"] == session_id
        assert body["tool_results"][0]["ok"] is True


def test_invalid_tool_input_is_rejected() -> None:
    with TestClient(app) as client:
        session_id = client.post("/v1/sessions").json()["id"]
        response = client.post(
            f"/v1/sessions/{session_id}/messages",
            json={"message": "bad", "tools": [{"name": "shell", "arguments": {}}]},
        )
        assert response.status_code == 422
```

运行：

```bash
uv run pytest -q
```

### 7.1.1 依赖覆盖与隔离外部系统

路由测试不应真的调用模型供应商或第三方工具。依赖覆盖的原则是：只替换依赖图中的边界，不修改被测路由的请求/响应契约。测试结束后要清空覆盖表，否则同一进程中的后续测试会悄悄继续使用 fake：

```python
from fastapi.testclient import TestClient

from app.main import AgentResponse, app, get_agent


class StubAgent:
    async def run(self, session_id, message, calls) -> AgentResponse:
        return AgentResponse(
            session_id=session_id,
            answer="stub answer",
            tool_results=[],
            elapsed_ms=0,
        )


def override_agent() -> StubAgent:
    return StubAgent()


def test_route_with_fake_agent() -> None:
    app.dependency_overrides[get_agent] = override_agent
    try:
        with TestClient(app) as client:
            session_id = client.post("/v1/sessions").json()["id"]
            response = client.post(
                f"/v1/sessions/{session_id}/messages",
                json={"message": "hello", "timeout_s": 1},
            )
        assert response.status_code == 200
        assert response.json()["answer"] == "stub answer"
    finally:
        app.dependency_overrides.clear()
```

若 fake 需要请求上下文，应显式标注 `Request`；否则 FastAPI 可能把未标注参数当成查询参数。不要在测试中读全局变量。对于数据库和缓存，优先覆盖 `get_store`，并在 fake 中提供可观察的调用记录，从而断言“超时后没有追加历史”“权限检查先于工具执行”。

### 7.2 应测试什么

按边界而不是只测“200”组织用例：

- 正常创建会话、发送消息、多个独立工具并行；
- 缺少字段、空消息、过长消息、未知字段、错误类型；
- 不存在会话、越权会话和重复幂等键；
- 工具错误、工具超时、整轮超时；
- 客户端取消/断开后是否取消上游任务并清理资源；
- SSE 事件顺序、`done`/`error` 结束事件和 JSON schema；
- 并发请求下的会话写入、限流和连接池耗尽；
- lifespan 中资源创建失败、关闭时异常；
- 认证、CORS、请求大小和日志脱敏。

异步业务测试可以使用 `pytest.mark.anyio` 和 `httpx.AsyncClient` 的 `ASGITransport`。如果测试依赖 lifespan，应显式使用 lifespan 管理器或框架提供的 fixture，不要把全局真实数据库带进单元测试。

对工具执行器建议单独做单元测试，对 FastAPI 路由做契约测试，对真实模型和第三方工具做少量隔离的集成测试，并为超时/429/断线编写可控的 fake client。

### 7.2.1 流式与异步测试的断言边界

流式测试不要只断言响应状态码。状态码通常在第一帧前就确定，真正的协议正确性在事件序列中：

```python
def test_stream_has_terminal_event() -> None:
    with TestClient(app) as client:
        session_id = client.post("/v1/sessions").json()["id"]
        with client.stream(
            "POST",
            f"/v1/sessions/{session_id}/messages/stream",
            json={"message": "hello", "timeout_s": 2},
        ) as response:
            assert response.status_code == 200
            lines = list(response.iter_lines())

    events = "\n".join(lines)
    assert "event: status" in events
    assert "event: done" in events or "event: error" in events
```

这是最小协议断言，生产测试还应解析每一个空行分隔的事件并检查：序号递增、JSON 可解析、`done` 与 `error` 不同时出现、`error` 带稳定错误码、客户端取消后 fake 上游收到取消。不要把 token 的确切分片当成永远稳定的契约，除非产品明确规定了分片规则。

若使用 `httpx.AsyncClient` + `ASGITransport` 测异步端点，记住 `ASGITransport` 不一定替你管理应用 lifespan；需要按所选版本的测试工具显式启动/关闭 lifespan。测试真实网络代理、TLS、HTTP/2 或多 worker 行为时，应该增加单独的黑盒集成测试，因为进程内 ASGI 测试无法证明这些部署属性。

一组有价值的超时/取消断言如下：

| 场景 | 应断言 | 不应断言 |
| --- | --- | --- |
| 单工具超时 | 该工具 `ok=False`、错误码稳定、其他独立工具仍可完成 | 假定所有工具都被重试 |
| 整轮超时 | HTTP 504 或流式 `error`，子任务收到取消，历史写入策略明确 | 认为外层取消能撤销外部副作用 |
| 客户端断开 | 上游 Task/HTTP 流关闭，记录取消原因 | 期待客户端收到最后一个 JSON |
| 依赖失败 | 请求在 Agent 前返回 401/403/404 | 让工具执行后再检查权限 |

---

## 8. Agent API 的安全与部署注意事项

1. **输入校验与工具白名单**：Pydantic 约束长度、数量、类型；工具名映射到固定注册表，绝不把用户输入拼成 shell、Python 表达式、URL 或 SQL。
2. **提示词与工具隔离**：模型输出的 tool call 仍是不可信输入；服务端重新校验参数、用户权限、资源归属和幂等性。
3. **SSRF 与外部网络**：如果 Agent 能访问 URL，限制协议、域名、内网 IP、重定向次数和响应大小；不要让用户借工具探测云元数据服务。
4. **认证/授权/租户隔离**：验证身份、会话归属和每个工具的权限；不要只靠“session ID 难猜”。
5. **超时与限流**：设置连接、读取、工具、模型和整轮预算；限制每请求工具数、并发请求数、token/费用预算；对 429 使用有上限的指数退避。
6. **取消和优雅关闭**：客户端断开时取消上游；服务退出时停止接收新请求，等待短时间让流结束，最后关闭客户端和连接池。
7. **秘密管理**：API key 放环境变量或秘密管理服务；日志、异常、SSE 事件和 trace 都要脱敏。
8. **状态外置**：多 worker/多副本时，会话、任务状态、事件、锁、限流计数和幂等键放共享存储；不要依赖全局变量。
9. **CORS/代理/Host**：只允许必要的前端来源；正确配置可信代理；生产开启 HTTPS 和安全 Header。
10. **资源上限**：限制请求体、文件、SSE 连接、WebSocket 帧、队列长度和 worker 内存；大任务返回 `202 + task_id`，不要长期占用 HTTP 请求。
11. **可观测性**：记录 request ID、路由、状态码、延迟、超时、取消、工具名和上游错误类别；记录指标 p50/p95/p99、429/5xx、队列长度和费用，但不记录敏感正文。
12. **依赖与镜像**：锁定版本、定期更新安全补丁，使用非 root 容器和最小基础镜像；生产启动命令与本地 reload 命令分开。

### 8.1 认证与授权：身份不等于权限

认证回答“请求是谁发的”，授权回答“它能对哪个租户的哪个会话做什么”。Agent API 至少要在以下边界检查授权：创建/读取会话、发送消息、调用每个工具、读取工具结果和建立 WebSocket；只在入口检查一次并不能防止内部任务绕过边界。

常见请求流程是：

```text
Authorization / Cookie
  → 验证签名、过期时间、issuer、audience
  → 得到 user_id / tenant_id / scopes
  → 加载 session，并检查 session.tenant_id == tenant_id
  → 检查工具所需 scope、资源范围和费用配额
  → 创建 Agent run
```

开发示例中的静态 API key 不能用于生产。生产 JWT 或 opaque token 的验证方式要按身份系统决定；不要只在 JWT 解码后读取 payload 而不验证签名，也不要把 token 原文写日志。返回 404 还是 403 取决于是否需要隐藏资源存在性，但同一租户内的错误契约必须稳定。

### 8.2 CORS、Cookie 与 Host

CORS 是浏览器的跨源读取策略，不是 API 鉴权。`allow_origins` 应列出实际前端来源；如果使用 cookie 或 `Authorization` 凭据，不能把 `*` 当成允许所有可信客户端。Cookie 会话还需要考虑 CSRF（例如 SameSite、CSRF token 和检查 Origin），而纯服务间 Bearer token 通常不依赖浏览器 CSRF 模型。

`TrustedHostMiddleware` 可以拒绝不在允许列表中的 Host，防止错误的 Host 进入生成链接或路由逻辑：

```python
from starlette.middleware.trustedhost import TrustedHostMiddleware


app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["api.example.com", "*.internal.example.com"],
)
```

这不替代反向代理的 Host 校验，也不应把用户提供的 Host 用于生成 OAuth 回调、绝对 URL 或工具目标。生产还应在 TLS 终止层设置 HSTS、限制方法/请求大小，并确认代理转发 Header 的可信来源。

### 8.3 SSRF：URL 校验不是字符串黑名单

如果 Agent 有“抓取 URL”工具，风险来自服务端替用户访问网络：内网服务、云元数据地址、环回地址、重定向后的内网地址都可能被探测。应优先使用域名 allowlist，而不是只拒绝几个字符串；还要限制协议、端口、DNS 解析结果、重定向次数、响应大小和总时间。

下面只演示“解析输入”的第一层，不能独立构成完整 SSRF 防护：

```python
import ipaddress
from urllib.parse import urlsplit


ALLOWED_HOSTS = {"docs.example.com", "api.example.com"}


def validate_fetch_url(raw: str) -> tuple[str, str]:
    parsed = urlsplit(raw)
    if parsed.scheme != "https" or parsed.username or parsed.password:
        raise ValueError("only credential-free HTTPS URLs are allowed")
    host = (parsed.hostname or "").lower().rstrip(".")
    if host not in ALLOWED_HOSTS:
        raise ValueError("host is not allow-listed")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        # 域名仍可能解析到私网；连接器必须在解析后再次检查每个地址。
        return parsed.scheme, host
    if address.is_private or address.is_loopback or address.is_link_local:
        raise ValueError("private address is not allowed")
    return parsed.scheme, host
```

即使域名通过 allowlist，也要防 DNS rebinding：在真正建立连接时解析并校验地址，禁用或严格处理重定向，并避免让 HTTP 客户端自动跟随到未经检查的新主机。不要把 `urlsplit` 的结果直接拼 shell，也不要允许用户控制代理、Unix socket 或自定义协议。

### 8.4 限流、背压和费用预算

HTTP 限流、Agent 并发和模型 token 预算是三层不同控制：

```text
入口：每用户/租户的请求速率、并发连接、请求体大小
  ↓
回合：每个 run 的 deadline、工具数、最大 token/费用
  ↓
下游：模型/搜索/数据库连接池、Semaphore、Queue、供应商配额
```

只做入口 QPS 限流仍可能让一个请求并发调用 8 个工具；只做工具 Semaphore 又不能阻止大量请求在入口排队。被拒绝的请求可返回 429 并带 `Retry-After`，但重试也必须受到总预算和抖动上限约束。长时间 Agent 更适合 `202 Accepted + task_id`，由客户端轮询或订阅事件，而不是让每个连接无限等待。

### 8.5 日志脱敏与可观测性

日志应支持排障，却不应成为第二个数据泄露通道。推荐记录 `request_id`、`run_id`、租户哈希/内部 ID、路由、状态码、耗时、工具名、错误类别和重试次数；默认不记录完整 prompt、模型输出、Bearer token、Cookie、API key、URL 查询串和工具原始响应。若业务确需审计正文，应进入有访问控制、保留期限和加密策略的审计存储，而不是普通应用日志。

结构化日志比字符串拼接更容易过滤敏感字段：

```python
import logging


logger = logging.getLogger("agent-api-example")


def safe_log_fields(request_id: str, run_id: str, tool: str, error_type: str) -> dict[str, str]:
    return {
        "request_id": request_id,
        "run_id": run_id,
        "tool": tool,
        "error_type": error_type,
    }


logger.info("agent tool finished", extra=safe_log_fields("req-1", "run-1", "search", "TimeoutError"))
```

还要避免把用户输入作为日志模板：使用 logging 参数或结构化字段，防止换行伪造日志记录；对指标标签使用有限枚举，不能把完整 URL、prompt 或任意 session ID 作为高基数标签。

### 8.6 部署检查清单

上线前可按四个问题检查：

1. **边界是否明确？** TLS、代理信任、Host、CORS、认证、授权和租户隔离是否在正确层执行。
2. **资源是否有上限？** 请求体、连接、worker、线程、队列、工具数、模型 token、费用、超时和重试是否有硬上限。
3. **失败是否可恢复？** 超时/取消/断线/重启后，是否能关闭上游、恢复任务状态、去重写操作，并向客户端给出稳定错误码。
4. **证据是否够用？** 是否有健康检查、p95/p99、429/5xx、取消、队列长度、连接池和费用指标，且日志没有秘密和敏感正文。

部署检查不应只运行一次“接口能返回 200”的冒烟测试；至少要在和生产相近的 worker、代理、连接池和上游限额下演练滚动关闭、模型超时、客户端断开及重复 POST。

---

## 9. 常见坑

1. 在 `async def` 中写 `time.sleep()` 或同步 HTTP 调用，导致整个 worker 的事件循环卡住。
2. 把 `asyncio.create_task` 当作持久化后台队列；请求结束后任务可能失去生命周期管理或在进程重启时丢失。
3. 只设置 FastAPI 外层 timeout，没有设置 HTTP 客户端连接/读取 timeout；底层阻塞调用可能仍无法及时停止。
4. 把进程内字典当作多 worker 的共享会话存储；每个 worker 的内存都是独立的。
5. 让模型生成任意工具名并直接动态导入或执行；必须使用注册表、schema、权限和资源范围检查。
6. 以为 `StreamingResponse` 自动提供可靠消息队列；断线、重连、重复事件和最后结果需要自行设计。
7. 用 `allow_origins=["*"]` 配合 `allow_credentials=True`，造成浏览器凭据策略和安全边界混乱。
8. 将未处理异常的堆栈、上游原始响应或提示词直接返回，导致信息泄露。
9. 生产使用 `--reload`，或者把 `--workers` 设置得很大却没有评估连接数、内存和模型供应商配额。
10. 仅测试 happy path，没有模拟工具超时、取消、429、客户端断开和服务优雅关闭。

### 9.1 看到症状时先查哪一层

| 症状 | 优先排查 | 常见修复方向 |
| --- | --- | --- |
| 所有请求在一个慢调用期间都变慢 | 事件循环是否被 `time.sleep`/同步 SDK 阻塞 | 换异步客户端，或将短时同步 I/O 限制并发后桥接到线程 |
| 流式首字节很快，最后耗时却没有记录 | 中间件只测到 `StreamingResponse` 对象返回 | 在生成器 `finally` 或 ASGI body 结束事件处记录完整耗时 |
| 多 worker 间会话忽有忽无 | 使用了进程内 `dict` | 会话、锁、幂等和任务状态外置到共享存储 |
| 请求超时后第三方仍收到写操作 | 只取消了等待协程，未设计外部副作用 | 下游设置 timeout，使用幂等键/补偿事务/独立进程 |
| 客户端收到 200 后又看到“HTTP 504” | 把 HTTP 状态和流内事件混为一谈 | 首帧后用 SSE `error`/`done`，客户端按终止事件处理 |
| 测试偶尔共享上一个测试的 fake | `dependency_overrides` 未清理 | `try/finally` 清空覆盖表，fixture 使用 yield |
| 外部 URL 校验通过但仍能访问内网 | 只做字符串检查或只检查第一次解析 | allowlist、解析后 IP 检查、重定向限制和连接时再次校验 |
| 429/内存持续上升 | 只有入口 QPS，没有回合/下游背压 | 为 run、工具、队列、连接和 token 设置独立上限 |

---

## 练习题

1. **路由建模：** 为示例增加 `GET /v1/sessions/{session_id}`，返回会话创建时间和消息数；为不存在的会话返回 404。
2. **Pydantic 约束：** 给 `ToolCall` 增加严格的 arguments 模型，分别验证 `search.query` 和 `weather.city`，拒绝未知字段并写出 422 测试。
3. **错误契约：** 定义统一的 `ErrorResponse`，让 401、404、422、504 都包含 `code`、`message`、`request_id`，同时保证 500 不暴露堆栈。
4. **超时实验：** 增加一个延迟 3 秒的假工具，分别设置单工具和整轮 timeout，观察返回的 `ToolResult` 与 HTTP 504 的区别。
5. **流式协议：** 为 SSE 事件增加递增 `id`、`created_at` 和 `done` 标记；写测试确保事件顺序为 `status → tool/token → done`，超时则以 `error` 结束。
6. **取消实验：** 用异步测试客户端中途关闭流，确认 FakeAgent 的子任务收到取消并执行清理；不要把 `CancelledError` 转成普通 500。
7. **鉴权与多租户：** 写一个依赖注入的 API key 到租户映射，并验证用户不能访问其他租户的 session；再将密钥移到环境变量。
8. **部署压测：** 在本地分别用 1、2、4 个 worker 和不同工具并发上限压测，记录 p95、内存、CPU、429 和连接数，解释为什么 worker 数量不是越多越好。

### 练习提示与验收标准

| 题号 | 提示 | 最低验收标准 |
| --- | --- | --- |
| 1 | 复用 `require_session`，不要在路由中复制字典检查 | 已存在会话返回稳定 JSON；随机 UUID 返回 404；至少有一条测试 |
| 2 | 用 `Literal` 分派到 `SearchArgs`/`WeatherArgs`，模型层拒绝未知字段 | 两种工具各有合法/非法案例；非法请求在工具执行前得到 422 |
| 3 | 为领域错误定义 `code`，在异常处理器中加入 request ID | 401/404/422/504 结构一致；500 响应没有堆栈、token 或上游正文 |
| 4 | 分别在 `_run_tool` 和 `send_message` 外层套预算 | 单工具超时不误报整轮超时；整轮超时会取消 TaskGroup 并有明确测试断言 |
| 5 | 先写事件解析器，再检查终止事件和序号 | 正常流恰有一个 `done`；超时/错误恰有一个 `error`；每帧 JSON 可解析 |
| 6 | 使用 fake 上游记录 `CancelledError` 和 `finally` | 客户端中断后上游收到取消且连接/任务释放；不把取消改成 500 |
| 7 | 把认证依赖输出的 tenant 与 session 所属 tenant 比较 | 跨租户访问被拒绝；没有把明文 API key 写入日志或仓库 |
| 8 | 固定请求负载，逐项改变 worker/并发，观察 p95 与上游 429 | 报告至少包含延迟、CPU、内存、错误率和连接数，并能解释瓶颈位置 |

---

## 小结

- FastAPI 用类型标注和 Pydantic 把 HTTP 输入/输出变成明确的契约，并通过依赖注入复用鉴权、存储和执行器。
- `async def` 适合异步 I/O；阻塞同步代码会卡住事件循环，应换异步客户端或桥接到线程。异步也不等于必然更快。
- `lifespan` 管理共享资源的创建与关闭；中间件用于统一的请求级横切逻辑；`StreamingResponse` 和 WebSocket 需要额外定义取消、重连、背压和事件语义。
- Agent API 要在服务端校验模型产生的工具调用，设置工具/整轮超时、并发上限、限流和结构化错误；客户端断开时传播取消。
- Uvicorn 负责 ASGI 服务运行。`--reload` 用于开发；多 worker 是独立进程，进程内状态不能当作共享存储。
- 测试不仅覆盖 200 响应，还要覆盖输入校验、权限、工具异常、超时、取消、流式协议、生命周期和资源边界。

## 延伸阅读（官方文档）

- [FastAPI：异步与并发](https://fastapi.tiangolo.com/async/)
- [FastAPI：请求体与 Pydantic](https://fastapi.tiangolo.com/tutorial/body/)
- [FastAPI：依赖注入](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [FastAPI：错误处理](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [FastAPI：生命周期事件](https://fastapi.tiangolo.com/advanced/events/)
- [FastAPI：流式响应](https://fastapi.tiangolo.com/advanced/stream-data/)
- [FastAPI：WebSocket](https://fastapi.tiangolo.com/advanced/websockets/)
- [Uvicorn：设置](https://www.uvicorn.org/settings/)
- [Uvicorn：部署](https://www.uvicorn.org/deployment/)
- [Pydantic：模型](https://docs.pydantic.dev/latest/concepts/models/)
- [Pydantic：字段](https://docs.pydantic.dev/latest/concepts/fields/)
