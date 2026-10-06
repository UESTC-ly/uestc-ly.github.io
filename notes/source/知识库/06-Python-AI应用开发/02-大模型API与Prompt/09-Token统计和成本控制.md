# 第 09 课：Token 统计和成本控制

> 本课解决三个工程问题：一次请求到底消耗了多少 Token、这次调用大约花费多少钱、随着对话变长如何控制成本和延迟。
>
> **内容来源说明**：项目资料已明确将“Token 统计和成本控制”列为本阶段课程，并指出生产应用需要统计 System、历史消息、当前输入和预留输出的总 Token。本笔记在此基础上补充通用的 API 使用、估算、计费、监控和优化方法；不同模型服务商的字段名、价格和缓存计费规则可能不同，应以实际服务商文档和账单为准。

## 1. 学习目标

完成本课后，应能够：

1. 解释 Token 与字符、单词之间的区别；
2. 区分输入 Token、输出 Token、总 Token 和缓存 Token；
3. 从 API 响应中读取实际用量；
4. 在请求前粗略估算输入规模，并为输出预留预算；
5. 根据价格表计算单次请求和累计调用成本；
6. 识别长上下文、Few-shot、工具调用、重试和过长输出带来的成本；
7. 设计 Token 预算、历史裁剪、摘要、模型路由和成本监控策略；
8. 避免把流式输出误认为“更省 Token”，或把本地估算当成服务商最终计费结果。

---

## 2. 为什么需要统计 Token

大模型 API 通常不是按“请求次数”单独计费，而是根据输入和输出的 Token 数量计费。Token 统计至少有四个用途：

### 2.1 计算成本

单次调用的价格通常与以下因素有关：

- 输入 Token 数；
- 输出 Token 数；
- 是否命中缓存输入；
- 是否使用了不同价格档位的模型；
- 某些模型是否另外计费推理 Token、工具调用或其他特殊 Token。

如果不统计用量，就无法解释“用户增加后为什么账单快速增长”。

### 2.2 防止超过上下文窗口

模型的上下文窗口不是无限的。一次请求的输入、历史消息、工具定义、当前问题和输出预算共同占用窗口。

可以用下面的近似关系理解请求规模：

$$
\text{请求所需上下文} \approx \text{System} + \text{历史消息} + \text{当前输入} + \text{工具定义} + \text{预留输出}
$$

如果总量超过模型限制，请求可能失败；即使没有超过，过长的上下文也会增加成本和延迟。

### 2.3 控制延迟

输入越长，模型需要处理的上下文通常越多；输出越长，生成时间通常也越长。因此 Token 预算既是成本控制工具，也是延迟控制工具。

### 2.4 发现提示词和代码中的浪费

统计后经常能发现：

- 每轮都重复发送一份很长的 System Prompt；
- Few-shot 示例数量过多；
- 历史消息无限追加；
- 工具 Schema 描述非常冗长；
- 要求输出 JSON，却预留了远超实际需要的输出长度；
- 重试时完整重复发送相同上下文；
- 检索系统把大量无关文档全部塞进上下文。

---

## 3. Token 是什么

### 3.1 Token 不是字符，也不是单词

Token 是模型分词器处理文本时使用的离散单位。一个 Token 可能对应：

- 一个完整的常见英文单词；
- 一个英文单词的一部分；
- 一个或多个汉字；
- 标点符号；
- 空格或换行相关片段；
- 代码中的关键字、运算符或标识符片段；
- JSON 的括号、引号、字段名和值的一部分。

因此不能简单地认为“一个汉字等于一个 Token”或“一个单词等于一个 Token”。实际数量取决于具体模型使用的 Tokenizer。

### 3.2 相同语义，不同写法可能有不同 Token 数

下面这些内容表达的含义可能相近，但 Token 数可能不同：

- 简洁指令与冗长指令；
- 中文、英文或中英混合文本；
- 自然语言与重复字段很多的 JSON；
- 可读代码与压缩后的代码；
- 带大量空行和注释的文本；
- 重复的历史对话和工具说明。

优化目标不是盲目删除所有文字，而是在不降低任务质量的前提下减少无效上下文。

### 3.3 Tokenizer 与模型通常需要匹配

同一段文本在不同模型的 Tokenizer 中可能被切分成不同数量的 Token。因此：

- 最可靠的用量来自 API 返回的 `usage`；
- 本地 Tokenizer 只能在与服务端模型匹配时作为较准确的预估；
- 使用不匹配的 Tokenizer 时，只能把结果当作粗略估算；
- 模型升级后，原来的估算结果也应重新校验。

---

## 4. 常见用量指标

不同服务商的字段名称可能略有差异，但通常可以从以下概念理解。

| 指标 | 含义 | 是否通常计费 |
|---|---|---|
| Input Tokens | 发送给模型的输入 Token，包括消息、指令、历史、工具定义等 | 通常计费 |
| Output Tokens | 模型生成的 Token | 通常计费 |
| Total Tokens | 输入 Token 与输出 Token 的合计 | 常用于统计，不一定直接作为独立价格项 |
| Cached Input Tokens | 服务商复用的输入 Token | 可能按较低价格计费，规则依服务商而定 |
| Reasoning Tokens | 某些模型报告的内部推理相关 Token | 可能计入输出或单独计费，需查服务商规则 |

基础关系通常是：

$$
\text{Total Tokens} = \text{Input Tokens} + \text{Output Tokens}
$$

如果服务商还返回缓存或推理字段，不要在没有查清定义的情况下简单重复相加，否则可能造成统计错误。

---

## 5. 从 API 响应读取实际用量

### 5.1 非流式响应

OpenAI 兼容接口通常会在响应中提供 `usage` 对象。常见字段如下：

```python
response = client.chat.completions.create(
    model="your-model",
    messages=[
        {"role": "user", "content": "用一句话解释什么是 Token。"}
    ],
)

print(response.choices[0].message.content)

usage = response.usage
if usage is not None:
    print("输入 Token:", usage.prompt_tokens)
    print("输出 Token:", usage.completion_tokens)
    print("总 Token:", usage.total_tokens)
```

不同 SDK 或兼容服务可能使用以下等价名称：

- `prompt_tokens`：输入 Token；
- `completion_tokens`：输出 Token；
- `input_tokens`：输入 Token；
- `output_tokens`：输出 Token；
- `total_tokens`：总 Token。

工程代码不要假设所有服务商字段完全相同，最好在适配层统一成自己的内部格式：

```python
from dataclasses import dataclass
from typing import Any


@dataclass
class TokenUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cached_input_tokens: int = 0


def normalize_usage(usage: Any) -> TokenUsage:
    """把不同 OpenAI 兼容服务的常见 usage 字段归一化。"""
    if usage is None:
        return TokenUsage()

    def read(*names: str) -> int:
        for name in names:
            value = getattr(usage, name, None)
            if value is None and isinstance(usage, dict):
                value = usage.get(name)
            if value is not None:
                try:
                    return int(value)
                except (TypeError, ValueError):
                    pass
        return 0

    input_tokens = read("prompt_tokens", "input_tokens")
    output_tokens = read("completion_tokens", "output_tokens")
    total_tokens = read("total_tokens")

    if total_tokens == 0:
        total_tokens = input_tokens + output_tokens

    # 缓存字段的具体嵌套结构因服务商而异，这里只处理一个常见示例。
    cached_input_tokens = read("cached_input_tokens")
    return TokenUsage(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        cached_input_tokens=cached_input_tokens,
    )
```

> 这段代码用于说明“适配层”的思路，不保证覆盖所有服务商字段。正式接入时，应根据实际响应样例补充字段映射，并保留原始 `usage` 以便审计。

### 5.2 流式响应

流式输出会把结果拆成多个片段返回。用量信息可能：

- 出现在最后一个 chunk；
- 需要在请求中显式开启用量返回选项；
- 由服务商通过额外字段提供；
- 在流式过程中不可用，只能在请求结束后通过其他接口获得。

因此流式代码必须考虑“文本已经显示，但最终 usage 还未到达”的情况。不能只统计收到的字符数来代替 Token 用量。

### 5.3 没有 usage 时怎么办

如果响应没有提供用量，可以按可靠性从高到低采用：

1. 查询服务商提供的调用日志或账单明细；
2. 使用与服务端完全匹配的 Tokenizer 进行本地估算；
3. 使用近似比例进行容量规划，并在上线后用真实数据校准。

---

## 6. 请求前估算 Token

### 6.1 估算的用途

请求前估算主要用于：

- 判断是否可能超过上下文窗口；
- 决定保留多少历史；
- 判断是否需要摘要或检索；
- 计算动态 `max_tokens`；
- 在超大输入到达模型前提前拒绝或截断；
- 预估成本并做预算告警。

估算不是最终计费凭证。

### 6.2 使用匹配的 Tokenizer

如果模型服务商公开了匹配的 Tokenizer，可以进行本地估算。以兼容的 Tokenizer 库为例：

```python
# 示例：只有在该 Tokenizer 与目标模型匹配或官方明确兼容时才使用
import tiktoken


def count_text_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    return len(encoding.encode(text))


text = "请把下面的文本总结成三条要点。"
print(count_text_tokens(text))
```

对于聊天消息，不能只把所有 `content` 字符串简单拼接后计数，因为服务端还可能计算：

- `role`；
- 消息边界和格式开销；
- name 等附加字段；
- 工具定义；
- 多模态内容的特殊计费方式。

如果没有官方聊天 Token 计算方法，应把本地结果标为估算值，并通过实际 `usage` 校准。

### 6.3 预留输出空间

假设模型上下文窗口为 $C$，输入 Token 估算为 $I$，希望预留输出空间 $O$，安全余量为 $S$，则应满足：

$$
I + O + S \leq C
$$

可用的最大输出预算近似为：

$$
O_{\max} = C - I - S
$$

安全余量用于覆盖 Tokenizer 估算误差、消息格式开销和服务商实现差异。不要把整个上下文窗口都分配给输入和输出，否则边界请求容易失败。

---

## 7. 成本计算

### 7.1 基础公式

假设价格表以“每一百万 Token 的价格”表示：

- 输入价格为 $P_i$；
- 输出价格为 $P_o$；
- 输入 Token 数为 $I$；
- 输出 Token 数为 $O$。

则单次请求成本近似为：

$$
\text{Cost} = \frac{I}{1{,}000{,}000} \times P_i + \frac{O}{1{,}000{,}000} \times P_o
$$

如果存在缓存输入价格 $P_c$，并且缓存输入 Token 数为 $C_i$，非缓存输入 Token 数为 $I-C_i$，则可以近似写成：

$$
\text{Cost} = \frac{I-C_i}{1{,}000{,}000} \times P_i + \frac{C_i}{1{,}000{,}000} \times P_c + \frac{O}{1{,}000{,}000} \times P_o
$$

实际计费可能还涉及批处理、区域、上下文长度、推理档位、图片输入、工具执行或其他项目，必须以当前价格表为准。

### 7.2 Python 成本计算示例

```python
from decimal import Decimal


def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    input_price_per_million: str,
    output_price_per_million: str,
    cached_input_tokens: int = 0,
    cached_input_price_per_million: str | None = None,
) -> Decimal:
    """按每百万 Token 的价格估算一次请求成本。"""
    input_tokens = max(0, input_tokens)
    output_tokens = max(0, output_tokens)
    cached_input_tokens = min(max(0, cached_input_tokens), input_tokens)

    input_price = Decimal(input_price_per_million)
    output_price = Decimal(output_price_per_million)

    normal_input_tokens = input_tokens - cached_input_tokens
    cost = (
        Decimal(normal_input_tokens) / Decimal(1_000_000) * input_price
        + Decimal(output_tokens) / Decimal(1_000_000) * output_price
    )

    if cached_input_price_per_million is not None:
        cached_price = Decimal(cached_input_price_per_million)
        cost += Decimal(cached_input_tokens) / Decimal(1_000_000) * cached_price
    else:
        # 没有缓存价格时，按普通输入价格估算，避免无依据地假设免费。
        cost += Decimal(cached_input_tokens) / Decimal(1_000_000) * input_price

    return cost


cost = estimate_cost(
    input_tokens=2_000,
    output_tokens=500,
    input_price_per_million="1.00",
    output_price_per_million="3.00",
)
print(cost)
```

示例中的价格只是占位参数，不代表任何具体服务商的当前价格。

### 7.3 计算月度成本

设每天请求数为 $N$，平均输入 Token 为 $I_d$，平均输出 Token 为 $O_d$，每月天数为 $D$，则月度成本近似为：

$$
\text{Monthly Cost} \approx D \times N \times \left(\frac{I_d}{1{,}000{,}000}P_i + \frac{O_d}{1{,}000{,}000}P_o\right)
$$

规划时不要只看平均值，还应观察：

- P50：典型请求；
- P95：较长或较贵的请求；
- 最大值：异常输入、错误循环或恶意输入；
- 按用户、功能、模型和租户分组的成本。

---

## 8. 哪些内容会消耗输入 Token

一次聊天请求的输入不只有用户最后一句话，还可能包括：

1. System Prompt；
2. 历史 User / Assistant 消息；
3. 当前 User 消息；
4. Few-shot 示例；
5. JSON Schema 或响应格式定义；
6. Function / Tool 定义、参数描述和使用规则；
7. 检索到的文档片段；
8. 图片、音频等多模态输入对应的计费单位；
9. 应用附加的元数据或格式包装。

### 8.1 工具定义尤其容易被忽视

Tool Calling 的工具名称、描述、参数名称、参数类型、枚举值和字段说明都可能进入模型上下文。工具越多、描述越长，每次请求的输入成本越高。

优化工具定义时可以：

- 使用清晰但简洁的描述；
- 删除模型不需要知道的内部实现细节；
- 只为当前场景注册相关工具；
- 避免重复描述相同规则；
- 统一字段命名，减少歧义和修复轮次。

### 8.2 结构化输出也有上下文成本

JSON Schema 能提高格式稳定性，但 Schema 本身可能增加输入 Token。设计 Schema 时应在“约束足够明确”和“描述足够简洁”之间平衡。

---

## 9. 对话历史为什么会让成本增长

如果每轮请求都把完整历史重新发送给模型，第 $n$ 轮的输入通常包含前面所有轮次。即使每轮新增内容相近，累计输入也会近似呈线性增长，整个会话的累计消耗则可能呈平方级增长趋势。

设每轮新增历史平均为 $m$ 个 Token，进行 $n$ 轮请求，则只考虑历史重复发送时，累计输入约为：

$$
m + 2m + 3m + \cdots + nm = \frac{n(n+1)}{2}m
$$

这不是所有系统的精确计费公式，但能说明“无限追加历史”为什么会越来越贵。

### 9.1 历史管理策略

#### 策略一：保留最近若干轮

优点：实现简单、保留近期上下文；

缺点：可能丢失早期关键事实，且每轮消息长度不一致时不够精确。

#### 策略二：按 Token 预算保留历史

基本流程：

1. 计算固定 System Prompt、当前输入和预留输出；
2. 得到历史可使用的 Token 预算；
3. 从最近一轮开始向前加入历史；
4. 加入下一轮会超预算时停止；
5. 保留完整的消息结构，不要随意拆开 Tool 调用链。

#### 策略三：摘要旧历史

将早期多轮对话压缩成结构化摘要，例如：

- 用户目标；
- 已确认事实；
- 已做出的决定；
- 未解决问题；
- 重要约束；
- 不应遗忘的实体和数值。

摘要本身也会消耗 Token，因此应在历史达到阈值时批量执行，而不是每轮都摘要。

#### 策略四：长期信息外置

不要把所有历史都永久塞进上下文。可以将稳定事实、用户偏好或业务数据保存到外部存储，在需要时检索相关内容。长期记忆与上下文窗口不是同一概念。

---

## 10. 成本控制的主要方法

### 10.1 控制输入长度

- 删除重复的规则和背景；
- 压缩过长的 System Prompt；
- 只注入与当前任务相关的检索结果；
- 限制 Few-shot 示例数量；
- 对历史消息实施 Token 预算；
- 对用户上传内容先做预处理、切分和过滤；
- 避免把原始日志、完整数据库记录直接放入 Prompt。

### 10.2 控制输出长度

- 设置合理的 `max_tokens` 或等价参数；
- 明确要求回答格式和长度；
- 对分类、抽取任务使用紧凑的结构化输出；
- 不要要求模型重复输入内容；
- 对不需要解释的任务明确“只输出结果”；
- 监控 `finish_reason`，区分正常结束和因长度上限被截断。

> `max_tokens` 通常是上限，不代表每次都会消耗这么多 Token；但上限设置过大可能影响预算规划，设置过小则可能导致输出截断。

### 10.3 模型路由

不同任务不必都使用最昂贵的模型。可以根据任务复杂度选择：

- 简单分类、改写、字段提取：低成本模型；
- 复杂推理、代码生成或高风险任务：能力更强的模型；
- 首次失败或校验失败时：有条件地升级模型，而不是所有请求都使用高价模型。

路由策略必须同时监控质量，不能只按价格选择。

### 10.4 缓存

适合缓存的内容包括：

- 相同输入的确定性或近似确定性请求；
- 稳定的检索结果；
- 结构化抽取的中间结果；
- 不经常变化的系统说明或预处理结果。

缓存键应包含会影响结果的因素，例如：

```text
模型版本 + Prompt 版本 + 输入内容哈希 + 采样参数 + Schema 版本
```

缓存需要考虑过期时间、隐私、数据更新和错误结果失效问题。

### 10.5 避免无效重试

重试可能重复消耗输入和输出 Token。应当：

- 只对临时错误重试；
- 使用指数退避和最大重试次数；
- 对认证错误、参数错误和上下文超限错误不要盲目重试；
- 使用请求 ID 做幂等和审计；
- 记录每次重试的成本归属；
- 对 Tool Calling 工作流防止同一工具陷入循环。

### 10.6 流式输出不等于更省 Token

流式输出主要改善用户感知延迟，让用户更早看到首个片段。只要输入和最终输出内容相同，流式与非流式的 Token 消耗通常不会因为传输方式不同而自动减少。

流式输出可以改善体验，但仍需控制：

- 输入上下文长度；
- 输出上限；
- 中途取消后的计费规则；
- 断线重连是否造成重复请求。

---

## 11. 一个带预算的请求流程

可以把成本控制放在请求适配层，而不是散落在各个业务函数中。

```python
from dataclasses import dataclass


@dataclass
class RequestBudget:
    context_limit: int
    reserved_output: int
    safety_margin: int = 256

    @property
    def max_input_tokens(self) -> int:
        return max(
            0,
            self.context_limit - self.reserved_output - self.safety_margin,
        )


def prepare_messages(messages: list[dict], budget: RequestBudget) -> list[dict]:
    """示例：实际项目应按消息轮次裁剪，而不是简单切字符串。"""
    # 这里的 estimate_messages_tokens 只是待接入的项目函数。
    estimated = estimate_messages_tokens(messages)
    if estimated <= budget.max_input_tokens:
        return messages

    # 生产实现可替换为：摘要旧历史、保留最近轮次、检索相关事实等。
    system_messages = [m for m in messages if m.get("role") == "system"]
    recent_messages = messages[-4:]
    candidate = system_messages + recent_messages

    if estimate_messages_tokens(candidate) > budget.max_input_tokens:
        raise ValueError("输入上下文超过预算，需要进一步压缩或拒绝请求")
    return candidate
```

上例中的 `estimate_messages_tokens` 没有实现，因为它必须根据目标服务商和模型选择合适的 Tokenizer。实际流程应包含：

1. 接收业务请求；
2. 组装消息、工具和 Schema；
3. 估算输入 Token；
4. 按预算裁剪、摘要或拒绝；
5. 计算合理的输出预算；
6. 发起请求；
7. 读取真实 `usage`；
8. 计算成本并记录日志；
9. 根据真实数据校准估算器。

---

## 12. 监控与日志设计

### 12.1 每次请求建议记录的字段

建议记录结构化日志，而不是只打印完整 Prompt：

```python
record = {
    "request_id": request_id,
    "user_id": user_id,
    "conversation_id": conversation_id,
    "feature": "document_summary",
    "model": model_name,
    "prompt_version": prompt_version,
    "schema_version": schema_version,
    "input_tokens": usage.input_tokens,
    "output_tokens": usage.output_tokens,
    "total_tokens": usage.total_tokens,
    "cached_input_tokens": usage.cached_input_tokens,
    "estimated_cost": str(cost),
    "latency_ms": latency_ms,
    "finish_reason": finish_reason,
    "retry_count": retry_count,
    "success": success,
}
```

不要在日志中记录不必要的敏感原文、密钥或个人信息。可以记录哈希、长度、版本号和分类标签，以支持统计与排查。

### 12.2 关键监控指标

| 指标 | 用途 |
|---|---|
| 平均输入 Token | 观察 Prompt 是否持续膨胀 |
| P50 / P95 输入 Token | 发现长尾请求 |
| 平均输出 Token | 观察回答是否过长 |
| P95 总 Token | 规划上下文与成本容量 |
| 单次请求成本 | 找出高成本功能 |
| 每用户 / 每租户成本 | 配额、计费和异常检测 |
| 缓存命中率 | 判断缓存策略是否有效 |
| 重试率 | 发现网络、限流或参数问题 |
| 上下文超限率 | 检查裁剪和预算策略 |
| 输出截断率 | 检查输出预算是否过小 |
| 首 Token 延迟和总延迟 | 平衡体验与上下文长度 |

### 12.3 成本预算和告警

可以按以下层级设置预算：

- 单次请求上限；
- 单用户每日上限；
- 单租户每月上限；
- 单个功能或模型的月度预算；
- 异常增长告警阈值。

超过预算时可以采取：

- 切换到低成本模型；
- 降低历史保留量；
- 禁止高成本工具；
- 要求用户确认；
- 暂停请求并返回可解释提示。

---

## 13. 常见错误与排查方法

### 错误一：用字符数代替 Token 数

**问题**：中文、英文、代码和 JSON 的字符到 Token 比例不同，字符数不能直接用于计费。

**改进**：使用服务端真实 `usage`，或使用匹配 Tokenizer 进行估算。

### 错误二：只统计当前用户输入

**问题**：忽略了 System Prompt、历史消息、Few-shot、工具定义和 Schema。

**改进**：统计完整请求上下文。

### 错误三：把 `max_tokens` 当成实际输出用量

**问题**：它是输出上限，不是模型一定会生成的数量。

**改进**：使用响应中的实际 output usage，同时把上限纳入预算。

### 错误四：把流式 chunk 数量当成 Token 数

**问题**：一个 chunk 可能包含多个 Token，也可能只包含半个词、标点或空内容。

**改进**：读取最终 usage，或使用服务商提供的专门统计机制。

### 错误五：忽略重试成本

**问题**：请求失败后重复提交完整上下文，可能导致成本翻倍甚至进入重试循环。

**改进**：限制重试次数，按错误类型分类，并记录重试消耗。

### 错误六：把所有历史都保存并发送

**问题**：上下文越积越长，成本和延迟不断增长，模型还可能受到无关信息干扰。

**改进**：按 Token 预算裁剪、摘要或外部检索。

### 错误七：本地估算与服务端真实用量差异很大

**可能原因**：

- Tokenizer 不匹配；
- 聊天消息格式开销未计算；
- 工具定义和 Schema 被忽略；
- 多模态内容采用另一套计费方式；
- 服务商字段或计费规则发生变化。

**改进**：抽样对比“本地估算 vs API usage”，计算误差并定期校准。

### 错误八：成本统计使用浮点数

**问题**：金额累计时可能出现精度误差。

**改进**：金额计算使用 `Decimal` 或整数的最小货币单位，并保留价格版本。

---

## 14. 一个实用的成本分析示例

假设某功能每天有 $10{,}000$ 次调用，平均每次：

- 输入 $1{,}500$ Token；
- 输出 $300$ Token；
- 每月按 $30$ 天计算。

则月度输入和输出量约为：

$$
\text{月输入 Token} = 10{,}000 \times 1{,}500 \times 30 = 450{,}000{,}000
$$

$$
\text{月输出 Token} = 10{,}000 \times 300 \times 30 = 90{,}000{,}000
$$

如果输入价格为每百万 Token $P_i$，输出价格为每百万 Token $P_o$，则：

$$
\text{月成本} = 450 \times P_i + 90 \times P_o
$$

这个例子说明，即使单次请求看起来很小，在高调用量下也会迅速形成可观成本。进一步优化时，应优先查找占比最大的部分：

- 如果输入成本占主导，优先压缩 Prompt、历史和检索内容；
- 如果输出成本占主导，优先限制回答长度、使用结构化输出和更便宜的模型；
- 如果重试成本高，优先解决错误率和幂等问题；
- 如果固定前缀很长且服务商支持缓存，评估缓存命中率和缓存价格。

---

## 15. 与前后课程的联系

### 15.1 与 Prompt 模板和 Few-shot 的联系

Few-shot 示例通常能提高格式和任务稳定性，但每个示例都会增加输入 Token。应通过小规模评测找到“质量提升与成本增加”的平衡点，而不是默认加入尽可能多的示例。

### 15.2 与多轮对话和上下文管理的联系

多轮对话必须同时处理：

- 上下文窗口限制；
- 历史相关性；
- 输入成本；
- 输出预算；
- 摘要和裁剪带来的信息损失。

因此上下文管理不仅是“把历史保存起来”，也是 Token 预算管理。

### 15.3 与 JSON Schema 和 Tool Calling 的联系

Schema、工具定义和工具结果都可能进入上下文。工具调用可能形成多次模型请求，一次用户操作的总成本应统计整个工作流，而不是只统计最后一次调用：

$$
\text{工作流成本} = \sum_{k=1}^{n} \text{第 }k\text{ 次模型调用成本} + \text{其他服务成本}
$$

### 15.4 与流式输出的联系

流式传输改善的是可感知延迟，不会自动减少 Token 消耗。成本统计仍应以实际输入和输出用量为准。

---

## 16. 实践清单

可以为一个真实功能建立以下检查表：

- [ ] 明确目标模型和对应价格版本；
- [ ] 保存 API 返回的原始 `usage`；
- [ ] 统一不同服务商的 usage 字段；
- [ ] 记录模型、Prompt 版本和 Schema 版本；
- [ ] 请求前估算输入 Token；
- [ ] 为输出预留 Token 和安全余量；
- [ ] 设置合理的输出上限；
- [ ] 对历史消息实施裁剪或摘要；
- [ ] 限制 Few-shot、工具和检索内容的数量；
- [ ] 对重试、工具循环和重复请求做成本统计；
- [ ] 计算单次、每日和每月成本；
- [ ] 监控 P95 Token 和成本，而不仅是平均值；
- [ ] 对异常成本设置告警和熔断；
- [ ] 定期比较本地估算与服务端实际 usage；
- [ ] 对敏感数据进行脱敏，避免把完整 Prompt 写入普通日志。

---

## 17. 本课小结

1. Token 是模型处理文本的计费和容量单位，不等同于字符或单词；
2. 一次请求的输入不仅包括当前问题，还包括 System Prompt、历史、Few-shot、Schema、工具定义和检索内容；
3. 最可靠的统计结果来自 API 返回的实际 `usage`；
4. 本地 Tokenizer 适合做请求前估算，但必须与模型匹配并接受误差；
5. 成本通常由输入 Token、输出 Token、缓存规则和模型价格共同决定；
6. `max_tokens` 是输出上限，不是实际输出用量；
7. 流式输出改善体验，但通常不会自动减少 Token 消耗；
8. 多轮历史、工具调用、重试和长 Schema 是常见的隐性成本来源；
9. 成熟的生产方案应把估算、预算、裁剪、真实 usage、成本计算和监控放在统一的 API 适配层；
10. 成本优化不能只追求 Token 少，还要同时评估回答质量、可靠性、延迟和用户体验。

---

## 18. 复习问题

1. 为什么不能用字符数准确推算 API 计费？
2. 一次聊天请求中，除了当前用户输入，还有哪些内容可能占用输入 Token？
3. `prompt_tokens`、`completion_tokens` 和 `total_tokens` 分别代表什么？
4. 为什么本地 Tokenizer 统计结果可能与 API 返回值不同？
5. 如果上下文窗口为 $C$，输入估算为 $I$，安全余量为 $S$，输出预算应如何计算？
6. 为什么无限追加多轮历史会使总成本增长得很快？
7. Tool Calling 工作流应如何统计多次模型调用的总成本？
8. 流式输出为什么不等于更省 Token？
9. 如何区分输入成本高和输出成本高，并采取不同优化措施？
10. 生产系统为什么需要记录 Prompt 版本、Schema 版本和模型名称？
