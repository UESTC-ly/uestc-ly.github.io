# 第一课：OpenAI 兼容接口

> 所属阶段：第二阶段——大模型 API 与 Prompt  
> 本课主题：理解并调用 OpenAI 兼容的大模型 API  
> 说明：本文基于行业中常见的 OpenAI 兼容接口整理。不同服务商的模型名称、参数和扩展能力可能不同，应以实际服务商文档为准。

## 1. 学习目标

完成本课后，应能够：

1. 解释什么是 OpenAI 兼容接口；
2. 理解 API Key、Base URL、Model 和 Endpoint 的作用；
3. 使用 HTTP 和 Python SDK 发起一次非流式对话请求；
4. 从响应中提取文本、结束原因和 Token 用量；
5. 使用环境变量管理连接配置；
6. 定位常见的认证、路径、模型和限流错误；
7. 判断一个接口是“完全兼容”还是“部分兼容”。

---

## 2. 什么是 OpenAI 兼容接口

OpenAI 兼容接口不是某个特定模型，而是一套被许多大模型服务采用的 API 调用形式。

通常只需要替换以下配置，就可以用近似相同的代码调用不同服务商：

- `api_key`：访问服务所需的密钥；
- `base_url`：服务地址；
- `model`：模型标识；
- 部分请求参数：例如最大输出长度、采样参数等。

典型调用关系如下：

```text
Python 应用
    │
    │ OpenAI SDK / HTTP 请求
    ▼
OpenAI 兼容 API
    │
    ├── 服务商 A 的模型
    ├── 服务商 B 的模型
    └── 本地推理服务
```

它的主要价值是降低应用与模型服务之间的耦合，使切换模型、接入本地模型和实现多模型路由更加容易。

### 2.1 “兼容”不等于“完全相同”

不同服务商可能只实现 OpenAI API 的一部分能力。常见差异包括：

- 支持的 Endpoint 不同；
- 模型名称不同；
- 某些参数被忽略或不被支持；
- Token 统计字段不完整；
- Tool Calling、Structured Output 或多模态能力不一致；
- 错误响应的结构不同；
- 最大上下文长度和最大输出长度不同。

因此，兼容接口可以统一基本调用方式，但不能假设所有高级功能都能无差别迁移。

---

## 3. 一次 API 调用的核心要素

### 3.1 API Key

API Key 用于身份认证和用量归属，通常通过请求头发送：

```http
Authorization: Bearer YOUR_API_KEY
```

安全要求：

- 不要把真实密钥直接写入代码；
- 不要把 `.env` 文件提交到 Git；
- 不要在日志中输出完整密钥；
- 客户端网页或移动端不应直接持有服务端密钥；
- 泄露后应立即撤销并重新生成。

### 3.2 Base URL

Base URL 表示 API 服务的基础地址，例如：

```text
https://api.example.com/v1
```

使用 OpenAI Python SDK 时，通常将它传给 `base_url`。需要特别检查服务商提供的地址是否已经包含 `/v1`，避免拼成重复路径：

```text
错误示例：https://api.example.com/v1/v1/chat/completions
```

### 3.3 Endpoint

经典的文本对话兼容接口通常是：

```text
POST /v1/chat/completions
```

完整地址等于：

```text
Base URL + Endpoint
```

OpenAI 官方还有较新的 Responses API，但许多第三方所谓的“OpenAI 兼容”主要指 Chat Completions API。接入前要确认服务商实际支持哪一种接口。

### 3.4 Model

`model` 是服务端公布的模型标识，不应根据展示名称自行猜测。例如：

```json
{
  "model": "provider-model-id"
}
```

如果出现 `model_not_found` 或 HTTP 404，应优先确认：

1. 模型名称是否正确；
2. 当前 API Key 是否有权使用该模型；
3. Base URL 是否属于正确的服务区域或项目；
4. 服务商是否要求使用部署名称而不是原始模型名称。

### 3.5 Messages

Chat Completions 使用 `messages` 表示对话历史：

```json
[
  {"role": "system", "content": "你是一名简洁的 Python 助手。"},
  {"role": "user", "content": "什么是列表推导式？"}
]
```

三个常见角色：

- `system`：定义助手的身份、任务和约束；
- `user`：用户输入；
- `assistant`：模型之前的回答。

消息角色和多轮上下文会在后续课程中详细学习。本课只需要知道：服务端通常不会自动记住本地程序之前的对话，应用需要在后续请求中重新传入必要的历史消息。

---

## 4. 使用 HTTP 直接调用

先理解底层 HTTP 请求，有助于排查 SDK 封装之外的问题。

```bash
curl "${LLM_BASE_URL}/chat/completions" \
  -H "Authorization: Bearer ${LLM_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "provider-model-id",
    "messages": [
      {
        "role": "system",
        "content": "你是一名简洁的 Python 助手。"
      },
      {
        "role": "user",
        "content": "用一句话解释 Python 装饰器。"
      }
    ],
    "temperature": 0.2
  }'
```

这里假设 `LLM_BASE_URL` 已经包含 `/v1`。如果服务商给出的 Base URL 不包含 `/v1`，需要按其文档调整。

### 4.1 请求体的常见字段

| 字段 | 作用 | 注意事项 |
|---|---|---|
| `model` | 指定模型 | 必填，名称由服务商定义 |
| `messages` | 对话消息列表 | Chat Completions 的核心输入 |
| `temperature` | 控制采样随机性 | 范围和实际效果可能因模型而异 |
| `max_tokens` | 限制最大输出 Token | 部分模型改用其他字段或不支持 |
| `stream` | 是否使用流式输出 | 本课先使用 `false` |
| `stop` | 遇到指定内容时停止生成 | 并非所有模型都支持 |

不要仅凭参数被服务端接受，就认定它一定生效。有些兼容服务会静默忽略不支持的参数。

---

## 5. 使用 Python OpenAI SDK 调用

### 5.1 安装依赖

```bash
python -m pip install openai python-dotenv
```

> 这里只记录需要执行的命令；当前笔记没有在本机执行安装。

### 5.2 配置环境变量

项目根目录可以使用 `.env` 保存本地配置：

```dotenv
LLM_API_KEY=replace-with-your-key
LLM_BASE_URL=https://api.example.com/v1
LLM_MODEL=provider-model-id
```

`.gitignore` 中应包含：

```gitignore
.env
.env.*
!.env.example
```

可以额外提供不含真实密钥的 `.env.example`：

```dotenv
LLM_API_KEY=
LLM_BASE_URL=
LLM_MODEL=
```

### 5.3 最小可运行示例

```python
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.environ["LLM_API_KEY"]
base_url = os.environ["LLM_BASE_URL"]
model = os.environ["LLM_MODEL"]

client = OpenAI(
    api_key=api_key,
    base_url=base_url,
)

response = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "system",
            "content": "你是一名简洁、准确的 Python 助手。",
        },
        {
            "role": "user",
            "content": "用一句话解释 Python 装饰器。",
        },
    ],
    temperature=0.2,
)

print(response.choices[0].message.content)
```

### 5.4 为什么使用通用环境变量名

如果程序可能切换不同服务商，使用下面这样的应用级名称会更加灵活：

```text
LLM_API_KEY
LLM_BASE_URL
LLM_MODEL
```

业务代码不需要绑定某个服务商的环境变量名称，只需修改部署配置即可切换模型服务。

---

## 6. 理解响应结构

典型响应经过简化后类似：

```json
{
  "id": "chatcmpl-example",
  "object": "chat.completion",
  "model": "provider-model-id",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Python 装饰器是在不修改原函数代码的情况下扩展其行为的可调用对象。"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 28,
    "total_tokens": 53
  }
}
```

### 6.1 文本内容

最常见的文本读取方式：

```python
content = response.choices[0].message.content
```

生产代码不应盲目假设 `choices[0]` 永远存在，还需要检查空响应、拒答、工具调用或服务商的非标准返回。

### 6.2 结束原因

```python
finish_reason = response.choices[0].finish_reason
```

常见值包括：

- `stop`：正常结束；
- `length`：达到长度限制；
- `tool_calls`：模型希望调用工具；
- `content_filter`：被内容安全策略截断。

具体枚举值可能因服务商而异。

### 6.3 Token 用量

```python
usage = response.usage

if usage is not None:
    print("输入 Token：", usage.prompt_tokens)
    print("输出 Token：", usage.completion_tokens)
    print("总 Token：", usage.total_tokens)
```

Token 用量可用于成本统计和上下文控制，但兼容服务可能不返回 `usage`，或者统计口径与其他服务不同。

---

## 7. 更稳健的单次调用示例

```python
import os

from dotenv import load_dotenv
from openai import APIConnectionError, APIStatusError, OpenAI

load_dotenv()


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"缺少环境变量：{name}")
    return value


client = OpenAI(
    api_key=require_env("LLM_API_KEY"),
    base_url=require_env("LLM_BASE_URL"),
    timeout=30.0,
    max_retries=2,
)


def chat_once(user_input: str) -> str:
    try:
        response = client.chat.completions.create(
            model=require_env("LLM_MODEL"),
            messages=[
                {
                    "role": "system",
                    "content": "你是一名简洁、准确的 Python 助手。",
                },
                {"role": "user", "content": user_input},
            ],
            temperature=0.2,
        )
    except APIConnectionError as exc:
        raise RuntimeError("无法连接模型服务，请检查网络和 Base URL") from exc
    except APIStatusError as exc:
        raise RuntimeError(
            f"模型服务返回错误：status={exc.status_code}"
        ) from exc

    if not response.choices:
        raise RuntimeError("模型响应中没有 choices")

    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("模型没有返回文本内容")

    return content


if __name__ == "__main__":
    print(chat_once("用一句话解释 Python 装饰器。"))
```

这个示例加入了：

- 必需环境变量校验；
- 请求超时；
- SDK 基础重试；
- 网络异常和 HTTP 状态异常处理；
- 空响应检查。

完整的超时、重试、指数退避和限流策略将在后续课程单独学习。

---
## 8. 同步与异步客户端

大模型 API 调用本质上是网络 I/O：客户端发送请求后，需要等待服务端完成排队、模型推理和响应传输。OpenAI Python SDK 提供两套对应的客户端：

- `OpenAI`：同步客户端；
- `AsyncOpenAI`：异步客户端。

两者调用的 API 结构基本一致，仍然使用 `chat.completions.create()`、`model` 和 `messages` 等字段。主要差别不在模型能力，而在程序如何等待网络请求，以及如何组织多个并发任务。

### 8.1 同步客户端的执行方式

同步调用会暂停当前执行流，直到请求返回后才继续执行：

```text
发送请求
    ↓
等待服务端响应
    ↓
读取完整响应
    ↓
执行后续代码
```

最小同步示例：

```python
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.environ["LLM_API_KEY"],
    base_url=os.environ["LLM_BASE_URL"],
    timeout=30.0,
    max_retries=2,
)

response = client.chat.completions.create(
    model=os.environ["LLM_MODEL"],
    messages=[
        {
            "role": "system",
            "content": "你是一名简洁、准确的 Python 助手。",
        },
        {
            "role": "user",
            "content": "用一句话解释 Python 装饰器。",
        },
    ],
    temperature=0.2,
)

if not response.choices:
    raise RuntimeError("模型响应中没有 choices")

content = response.choices[0].message.content
if not content:
    raise RuntimeError("模型没有返回文本内容")

print(content)
```

代码执行顺序是严格串行的：

```text
加载配置
  → 创建客户端
  → 发送请求
  → 等待响应
  → 校验响应
  → 输出文本
```

同步客户端适合：

- 命令行程序和一次性脚本；
- 本地学习、调试和接口连通性测试；
- 请求量较小的后台任务；
- 项目本身采用同步框架；
- 更重视代码直观性，而不是大量并发。

同步并不意味着不能实现并发。如果确实需要并行发送同步请求，可以使用线程池；不过对于以网络等待为主的任务，原生异步客户端通常更容易控制。

### 8.2 异步客户端的执行方式

异步客户端使用 `AsyncOpenAI`。调用网络 API 时需要使用 `await`：

```python
import asyncio
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()


async def main() -> None:
    async with AsyncOpenAI(
        api_key=os.environ["LLM_API_KEY"],
        base_url=os.environ["LLM_BASE_URL"],
        timeout=30.0,
        max_retries=2,
    ) as client:
        response = await client.chat.completions.create(
            model=os.environ["LLM_MODEL"],
            messages=[
                {
                    "role": "system",
                    "content": "你是一名简洁、准确的 Python 助手。",
                },
                {
                    "role": "user",
                    "content": "用一句话解释异步编程。",
                },
            ],
            temperature=0.2,
        )

        if not response.choices:
            raise RuntimeError("模型响应中没有 choices")

        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("模型没有返回文本内容")

        print(content)


if __name__ == "__main__":
    asyncio.run(main())
```

这里有三个关键语法：

#### `async def`

`async def` 定义的是协程函数：

```python
async def call_model(prompt: str) -> str:
    ...
```

调用协程函数时，通常不会直接得到最终字符串，而是得到一个等待执行的协程对象。

#### `await`

`await` 用于等待一个异步操作完成：

```python
response = await client.chat.completions.create(...)
```

它会暂停当前协程，但不会像同步调用那样阻塞整个事件循环。等待网络响应期间，事件循环可以去运行其他已经准备好的协程。

#### `asyncio.run()`

普通 Python 脚本需要一个入口来启动事件循环：

```python
asyncio.run(main())
```

`asyncio.run()` 适合在脚本的最外层使用。在 FastAPI 异步路由、Jupyter Notebook 或其他已经运行事件循环的环境中，不要再次嵌套调用它，应直接使用 `await`。

### 8.3 同步和异步的核心区别

下面两段代码调用的是相同类型的接口，但等待方式不同：

```python
# 同步
response = client.chat.completions.create(...)
```

```python
# 异步
response = await async_client.chat.completions.create(...)
```

同步调用期间，当前线程会被网络等待占用；异步调用期间，当前协程会暂停并把执行权交回事件循环。

需要准确理解两点：

1. 异步不会让模型本身更快生成 Token，单次请求的服务端推理时间通常不会因为使用异步客户端而改变；
2. 异步可以在等待一个请求时处理其他请求，因此在多用户、多任务或批量调用场景中通常能提高整体吞吐量。

可以用下面的模型理解：

```text
同步：任务 A 请求 → 等待 A 完成 → 任务 B 请求 → 等待 B 完成

异步：任务 A 请求 → A 等待时处理任务 B → B 等待时处理任务 C
```

### 8.4 异步不等于自动并发

下面的代码虽然使用了异步客户端，但请求仍然是串行的：

```python
async def summarize_all(texts: list[str], client) -> list[str]:
    results = []

    for text in texts:
        response = await client.chat.completions.create(
            model=os.environ["LLM_MODEL"],
            messages=[
                {
                    "role": "user",
                    "content": f"请总结以下文本：\n{text}",
                }
            ],
        )
        results.append(response.choices[0].message.content or "")

    return results
```

执行顺序仍然是：

```text
请求 1 完成 → 请求 2 完成 → 请求 3 完成
```

如果任务之间互不依赖，可以先创建多个协程，再交给 `asyncio.gather()` 并发等待：

```python
import asyncio
import os


async def summarize_one(text: str, client) -> str:
    response = await client.chat.completions.create(
        model=os.environ["LLM_MODEL"],
        messages=[
            {
                "role": "user",
                "content": f"请总结以下文本：\n{text}",
            }
        ],
    )

    if not response.choices:
        raise RuntimeError("模型响应中没有 choices")

    return response.choices[0].message.content or ""


async def summarize_all(texts: list[str], client) -> list[str]:
    tasks = [summarize_one(text, client) for text in texts]
    return await asyncio.gather(*tasks)
```

`asyncio.gather()` 的结果顺序通常与传入任务的顺序一致，即使后创建的任务先返回，也会放回对应的位置。但并发请求不能无限增加，否则可能触发服务商的并发、RPM（每分钟请求数）或 TPM（每分钟 Token 数）限制。

### 8.5 使用信号量限制并发数

可以使用 `asyncio.Semaphore` 控制同时进入 API 调用部分的任务数量：

```python
import asyncio
import os


async def summarize_one(
    text: str,
    client,
    semaphore: asyncio.Semaphore,
) -> str:
    async with semaphore:
        response = await client.chat.completions.create(
            model=os.environ["LLM_MODEL"],
            messages=[
                {
                    "role": "user",
                    "content": f"请总结以下文本：\n{text}",
                }
            ],
        )

        if not response.choices:
            raise RuntimeError("模型响应中没有 choices")

        return response.choices[0].message.content or ""


async def summarize_all(texts: list[str], client) -> list[str]:
    semaphore = asyncio.Semaphore(5)
    tasks = [
        summarize_one(text, client, semaphore)
        for text in texts
    ]
    return await asyncio.gather(*tasks)
```

`Semaphore(5)` 的含义是最多允许 5 个请求同时执行。它只限制“同时进行中的请求数”，并不等同于服务商的每分钟请求限制。例如，请求返回很快时，即使并发数只有 5，也可能在一分钟内发送很多请求。因此生产代码还需要结合服务商的 RPM、TPM、并发数和账户额度设计限流策略。

大批量任务还可以采用分批处理或异步队列，避免一次性创建数万个协程：

```python
async def summarize_in_batches(
    texts: list[str],
    client,
    batch_size: int = 20,
) -> list[str]:
    results: list[str] = []

    for start in range(0, len(texts), batch_size):
        batch = texts[start:start + batch_size]
        results.extend(await summarize_all(batch, client))

    return results
```

### 8.6 并发任务中的异常处理

`asyncio.gather()` 默认会在任务发生异常时向调用方传播异常。批量任务如果希望“单个失败不影响其他任务”，可以使用 `return_exceptions=True`：

```python
async def summarize_all_safely(
    texts: list[str],
    client,
) -> list[str | Exception]:
    tasks = [summarize_one(text, client) for text in texts]
    return await asyncio.gather(
        *tasks,
        return_exceptions=True,
    )


results = await summarize_all_safely(texts, client)

for index, result in enumerate(results):
    if isinstance(result, Exception):
        print(f"第 {index} 个任务失败：{result}")
    else:
        print(f"第 {index} 个任务成功：{result}")
```

是否允许部分成功，应由业务决定：

- 搜索结果摘要可以允许部分失败，并记录失败项后补偿处理；
- 财务、订单或数据写入任务通常不能静默跳过失败项；
- 需要重试时，应只重试失败任务，而不是重新发送整批请求。

还应区分异常类型：网络断开、超时、服务端临时错误和限流通常可能暂时恢复；认证失败、模型不存在、参数错误则不应无限重试。具体异常分类和退避策略见后面的错误处理章节。

### 8.7 同步流式输出

非流式调用会等待完整答案返回；流式调用则在模型生成过程中逐块返回内容。同步客户端的流式读取方式是普通 `for` 循环：

```python
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["LLM_API_KEY"],
    base_url=os.environ["LLM_BASE_URL"],
)

stream = client.chat.completions.create(
    model=os.environ["LLM_MODEL"],
    messages=[
        {"role": "user", "content": "写一段 Python 入门介绍。"}
    ],
    stream=True,
)

for chunk in stream:
    if not chunk.choices:
        continue

    text = chunk.choices[0].delta.content or ""
    print(text, end="", flush=True)

print()
```

流式响应中的某些数据块可能没有文本内容，例如开始标记、结束标记或其他元数据，因此不能假设每个 `chunk` 都有可打印的文字。不同兼容服务的增量字段、结束原因和最终用量统计也可能存在差异，需要以实际响应为准。

### 8.8 异步流式输出

异步客户端读取流时使用 `async for`，不能使用普通的 `for`：

```python
import os

from openai import AsyncOpenAI


async def stream_answer() -> None:
    async with AsyncOpenAI(
        api_key=os.environ["LLM_API_KEY"],
        base_url=os.environ["LLM_BASE_URL"],
    ) as client:
        stream = await client.chat.completions.create(
            model=os.environ["LLM_MODEL"],
            messages=[
                {"role": "user", "content": "写一段 Python 入门介绍。"}
            ],
            stream=True,
        )

        async for chunk in stream:
            if not chunk.choices:
                continue

            text = chunk.choices[0].delta.content or ""
            print(text, end="", flush=True)

        print()
```

异步流式输出适合：

- 命令行中实时显示生成内容；
- Web 服务通过 SSE 或 WebSocket 推送给前端；
- 长回答或复杂任务需要尽早展示首个 Token；
- 在等待模型后续内容时同时处理其他 I/O 任务。

流式输出会增加状态管理复杂度。应用通常需要自行累积增量文本：

```python
parts: list[str] = []

async for chunk in stream:
    if not chunk.choices:
        continue

    text = chunk.choices[0].delta.content or ""
    parts.append(text)
    send_to_frontend(text)

full_content = "".join(parts)
```

如果最终结果需要保存、校验或解析 JSON，不能只把每个片段直接交给解析器，而应在流结束后拼接完整文本，再执行统一校验。前端展示和后端最终结果保存可以使用不同的数据通道。

### 8.9 在 FastAPI 中使用异步客户端

FastAPI 的异步路由中应优先使用 `AsyncOpenAI`，避免同步网络调用阻塞事件循环。客户端可以在应用生命周期中创建和关闭，而不是每个请求都创建一次：

```python
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from openai import AsyncOpenAI


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.llm_client = AsyncOpenAI(
        api_key=os.environ["LLM_API_KEY"],
        base_url=os.environ["LLM_BASE_URL"],
        timeout=30.0,
        max_retries=2,
    )

    try:
        yield
    finally:
        await app.state.llm_client.close()


app = FastAPI(lifespan=lifespan)


@app.post("/ask")
async def ask(request: Request) -> dict[str, str]:
    body = await request.json()
    prompt = body["prompt"]
    client: AsyncOpenAI = request.app.state.llm_client

    response = await client.chat.completions.create(
        model=os.environ["LLM_MODEL"],
        messages=[{"role": "user", "content": prompt}],
    )

    if not response.choices:
        raise RuntimeError("模型响应中没有 choices")

    return {
        "answer": response.choices[0].message.content or ""
    }
```

这个示例体现了几个实践原则：

- 应用启动时建立客户端，便于复用底层连接；
- 每个请求只负责构造消息和读取结果；
- 应用关闭时释放客户端资源；
- 异步路由中使用 `await` 调用异步 SDK；
- 服务端密钥保留在后端，不能发送给浏览器或移动端。

实际项目还应使用 Pydantic 定义请求和响应模型，并将模型名称、超时、并发上限等配置集中管理。

### 8.10 在异步代码中调用同步函数

如果某个第三方库只有同步 API，不能直接在异步路由中调用耗时的同步网络函数：

```python
# 不推荐：会阻塞事件循环
async def bad_handler(prompt: str):
    return sync_client.chat.completions.create(...)
```

可以临时使用线程执行同步函数：

```python
import asyncio


def sync_call(prompt: str):
    return sync_client.chat.completions.create(
        model=os.environ["LLM_MODEL"],
        messages=[{"role": "user", "content": prompt}],
    )


async def call_from_async_code(prompt: str):
    return await asyncio.to_thread(sync_call, prompt)
```

这种方式适合兼容旧代码或没有异步接口的库，但它仍然会占用线程资源。若 SDK 已经提供原生异步客户端，优先使用原生异步客户端，不要把所有同步调用都包装到线程中。

### 8.11 客户端复用、超时和资源管理

不建议每次调用都重新创建客户端：

```python
# 不推荐：每次请求都新建客户端

def ask(prompt: str) -> str:
    client = OpenAI(...)
    response = client.chat.completions.create(...)
    return response.choices[0].message.content or ""
```

重复创建客户端可能导致连接池无法复用、连接建立开销增加和资源释放不及时。更好的方式是让客户端成为应用级对象，或者由 Web 框架的生命周期管理。

客户端配置中的 `timeout` 和 `max_retries` 也需要经过业务设计：

```python
client = AsyncOpenAI(
    api_key=os.environ["LLM_API_KEY"],
    base_url=os.environ["LLM_BASE_URL"],
    timeout=30.0,
    max_retries=2,
)
```

需要注意：

- SDK 的自动重试规则可能因版本和异常类型而不同；
- 业务层再次重试时，要避免与 SDK 重试叠加造成请求次数失控；
- 超时并不一定意味着服务端没有处理请求，再次重试可能产生重复调用；
- 涉及扣费、工具调用或数据写入时，应评估请求是否可以安全重放；
- 长时间流式请求应设置合理的空闲超时，并处理客户端主动断开连接的情况。

如果需要约束整个异步任务的最大执行时间，还可以在应用层增加超时：

```python
import asyncio


async def call_with_business_timeout(client, prompt: str):
    return await asyncio.wait_for(
        client.chat.completions.create(
            model=os.environ["LLM_MODEL"],
            messages=[{"role": "user", "content": prompt}],
        ),
        timeout=60,
    )
```

SDK 请求超时和业务级超时可以同时存在，但应明确谁负责取消任务、记录日志和向用户返回什么错误。

### 8.12 常见错误

#### 错误一：忘记 `await`

```python
response = async_client.chat.completions.create(...)
```

这通常得到的是协程对象，而不是 API 响应。应改为：

```python
response = await async_client.chat.completions.create(...)
```

#### 错误二：异步流使用普通 `for`

```python
for chunk in stream:
    ...
```

异步流应使用：

```python
async for chunk in stream:
    ...
```

#### 错误三：在已经运行事件循环的环境中调用 `asyncio.run()`

异步路由或 Notebook 中应直接使用 `await`，不要重复启动事件循环。

#### 错误四：无限制创建并发任务

```python
await asyncio.gather(
    *[call_model(item) for item in thousands_of_items]
)
```

应根据服务商限制使用信号量、分批处理、队列和退避。

#### 错误五：把并发数当成速率限制

信号量只限制同时执行的任务数量，不会自动保证 RPM、TPM 或每日额度不超限。

#### 错误六：在异步 Web 路由中直接调用同步客户端

这会阻塞事件循环，使同一进程中的其他请求也可能受到影响。应使用 `AsyncOpenAI`，或者在确有必要时使用 `asyncio.to_thread()`。

### 8.13 同步和异步的选择原则

| 场景 | 推荐方式 | 原因 |
|---|---|---|
| 单次命令行调用 | 同步客户端 | 控制流简单，容易调试 |
| 本地实验和接口测试 | 同步客户端 | 重点是验证请求和响应 |
| 低并发后台脚本 | 同步客户端 | 不需要引入异步复杂度 |
| FastAPI 异步路由 | 异步客户端 | 避免阻塞事件循环 |
| 批量摘要、分类、抽取 | 异步客户端 | 便于控制 I/O 并发 |
| 高并发 Web 服务 | 异步客户端 | 更适合处理大量等待中的请求 |
| 异步流式响应 | 异步客户端 | 使用 `async for` 持续读取数据 |
| 只有同步第三方库 | 同步客户端或线程 | 根据整体架构选择 |

本节可以归纳为：

1. `OpenAI` 用于同步调用，`AsyncOpenAI` 用于异步调用；
2. 同步调用直接执行，异步调用需要 `await`；
3. 异步客户端的主要收益是提高多请求场景下的资源利用率，而不是加快单次推理；
4. 异步并发必须限制并发数，并结合 RPM、TPM、超时、重试和退避策略；
5. 同步流使用 `for`，异步流使用 `async for`；
6. 长期运行的应用应复用客户端，并在生命周期结束时释放资源；
7. 简单脚本优先同步，异步 Web 服务、批量任务和实时流式输出优先异步。
- 不要在异步路由中直接执行耗时的同步网络请求。

---

## 9. 常见错误与排查方法

### 9.1 HTTP 401：认证失败

可能原因：

- API Key 错误、过期或已撤销；
- 环境变量没有成功加载；
- 请求头缺少 `Bearer`；
- API Key 与 Base URL 不属于同一服务商或项目。

排查时只能确认密钥是否存在，不要打印完整密钥：

```python
api_key = os.getenv("LLM_API_KEY")
print("API Key 是否存在：", bool(api_key))
```

### 9.2 HTTP 403：没有权限

可能原因：

- 当前账号无权访问目标模型；
- 服务区域、组织或项目配置不正确；
- 请求被安全策略拒绝。

### 9.3 HTTP 404：地址或模型不存在

重点检查：

- Base URL 是否正确；
- 是否遗漏或重复添加 `/v1`；
- Endpoint 是否被服务商实现；
- 模型标识是否正确。

### 9.4 HTTP 429：请求过多或额度不足

可能表示：

- 请求频率超过限制；
- 并发数超过限制；
- Token 速率超过限制；
- 账户余额或调用额度不足。

不能对所有 429 进行无限重试。应用需要限制重试次数，并区分暂时性限流与永久性额度问题。

### 9.5 HTTP 5xx：服务端错误

通常是模型服务临时异常，可对幂等或可安全重放的请求进行有限次数重试。重试应配合退避和随机抖动，避免大量客户端同时再次请求。

### 9.6 返回 200，但内容不符合预期

可能原因：

- 服务商忽略了某些参数；
- 提示词不够明确；
- 模型不支持目标能力；
- 返回的是工具调用、拒答或空内容；
- 输出被最大长度截断。

此时应同时检查：

```python
choice = response.choices[0]
print("finish_reason:", choice.finish_reason)
print("content:", choice.message.content)
print("usage:", response.usage)
```

---

## 10. 如何验证接口的兼容程度

接入一个新的兼容服务时，可以按以下顺序做最小测试。

### 第一步：验证连接

发送最简单的单轮非流式请求，只包含：

- `model`；
- 一条 `user` 消息。

### 第二步：验证基础参数

分别测试：

- `system` 消息；
- `temperature`；
- 最大输出长度；
- `stop`。

### 第三步：检查响应字段

确认是否返回：

- `choices`；
- `message.content`；
- `finish_reason`；
- `usage`。

### 第四步：测试高级能力

按项目需要逐项验证：

- 流式输出；
- JSON 输出；
- Structured Output；
- Tool Calling；
- 图片或音频输入；
- 多轮长上下文。

### 第五步：记录差异

建议为每个模型维护能力表：

| 能力 | 是否支持 | 备注 |
|---|---:|---|
| Chat Completions | 待验证 | Endpoint 和版本 |
| System 消息 | 待验证 | 是否有特殊限制 |
| 流式输出 | 待验证 | 增量字段格式 |
| Structured Output | 待验证 | 支持的 Schema 范围 |
| Tool Calling | 待验证 | 是否支持并行工具调用 |
| Usage 统计 | 待验证 | 流式响应是否返回 |

---

## 11. 应用层配置设计

为了让业务代码与服务商解耦，可以集中定义模型配置：

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class LLMConfig:
    api_key: str
    base_url: str
    model: str
    timeout: float = 30.0
    max_retries: int = 2
```

业务层只依赖配置和统一的调用函数，不应在多个模块中散落 Base URL、模型名称和超时值。

一个简单的分层思路：

```text
业务逻辑
    ↓
LLM 服务封装层
    ↓
OpenAI SDK
    ↓
OpenAI 兼容服务
```

这样做可以为后续的多模型路由、失败降级、缓存和监控打下基础。

---

## 12. 本课实践任务

### 任务一：完成首次调用

使用环境变量配置：

```text
LLM_API_KEY
LLM_BASE_URL
LLM_MODEL
```

向模型发送问题：

```text
请用三点解释 Python 虚拟环境的作用。
```

输出模型返回的文本。

### 任务二：观察响应元数据

在任务一基础上输出：

- 模型名称；
- `finish_reason`；
- 输入 Token 数；
- 输出 Token 数；
- 总 Token 数。

如果服务商没有返回某个字段，程序应输出“未提供”，而不是直接报错。

### 任务三：制造并排查错误

在不泄露真实密钥的前提下，依次测试：

1. 使用错误模型名称；
2. 使用错误 Base URL；
3. 删除 API Key 环境变量；
4. 设置很短的超时时间。

记录每次错误的异常类型、状态码和排查过程。

### 任务四：比较两个兼容服务

如果有两个可用服务，使用相同的消息分别调用，并比较：

- 配置上需要修改哪些字段；
- 响应结构是否一致；
- Token 用量字段是否完整；
- 参数是否都生效；
- 错误格式是否一致。

---

## 13. 自测题

1. OpenAI 兼容接口解决了什么问题？
2. `base_url`、Endpoint 和完整请求地址有什么区别？
3. 为什么不能把 API Key 直接写在代码中？
4. 为什么切换兼容服务时不能只修改 Base URL？
5. `finish_reason="length"` 通常意味着什么？
6. 为什么不能假设每个兼容服务都会返回 `usage`？
7. 异步 Web 应用为什么更适合使用 `AsyncOpenAI`？
8. 收到 401、404 和 429 时，排查方向分别是什么？

---

## 14. 本课小结

本课的核心不是记住某一家服务商的地址，而是掌握统一的调用模型：

```text
API Key + Base URL + Model + Messages
                    ↓
            OpenAI 兼容接口
                    ↓
     Content + Finish Reason + Usage
```

需要牢记：

1. OpenAI 兼容接口降低了模型接入成本，但不保证所有能力完全一致；
2. 密钥、地址和模型名称应通过配置管理；
3. 首次接入应从最小非流式请求开始；
4. 生产代码必须检查异常、空响应和结束原因；
5. 高级能力需要针对每个服务商和模型逐项验证。

下一课将学习 `System`、`User`、`Assistant` 消息的职责，以及如何组织单轮和多轮对话消息。
