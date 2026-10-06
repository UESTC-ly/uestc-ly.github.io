# 第 05 课：JSON Schema

> 所属阶段：第二阶段——大模型 API 与 Prompt  
> 本课主题：用 JSON Schema 把模型输出定义成可验证的数据契约  
> 前置课程：[第 04 课：Structured Output](./04-Structured-Output.md)

---

## 1. 学习目标

完成本课后，应能够：

1. 解释 JSON、JSON Schema 与 Structured Output 之间的关系；
2. 读懂 `type`、`properties`、`required`、`enum` 和 `additionalProperties` 等常用关键字；
3. 为分类、信息抽取和数据转换任务设计一个实用的 Schema；
4. 将 JSON Schema 传给 OpenAI 兼容接口，并理解严格模式的边界；
5. 在应用侧对模型返回值执行 JSON 解析、Schema 校验和业务校验；
6. 识别“格式正确但业务错误”、字段设计过度复杂以及 Schema 版本不兼容等问题。

---

## 2. 为什么需要 JSON Schema

大模型默认输出的是自然语言。即使在 Prompt 中要求“请返回 JSON”，模型也可能出现以下问题：

- 少一个字段；
- 字段类型不一致，例如有时返回数字，有时返回字符串；
- 枚举值拼写不统一，例如 `high`、`High`、`高` 混用；
- 多返回解释文字、Markdown 代码围栏或额外字段；
- 数组元素格式不一致；
- JSON 语法合法，但内容不满足程序的业务要求。

JSON Schema 的作用，是用一个机器可读的规则描述输出数据的结构。它可以规定：

- 根节点是对象、数组还是基本类型；
- 对象允许哪些字段；
- 字段的类型是什么；
- 哪些字段必须出现；
- 字符串或数字允许的取值范围；
- 数组元素的类型；
- 是否允许额外字段。

因此，JSON Schema 不只是“让模型看起来像 JSON”，而是把模型输出变成下游程序可以检查的数据契约。

---

## 3. JSON、JSON Schema 和 Structured Output 的区别

### 3.1 JSON 是数据

JSON 是一种数据交换格式。例如：

```json
{
  "sentiment": "mixed",
  "priority": 3,
  "summary": "物流速度快，但包装有破损。",
  "keywords": ["物流", "包装"]
}
```

它描述的是某一次具体的结果，但没有说明：

- `priority` 是否必须是整数；
- `priority` 是否只能在 1 到 5 之间；
- `sentiment` 是否只能取固定的几个值；
- 是否允许多一个 `debug` 字段。

### 3.2 JSON Schema 是数据规则

JSON Schema 描述“什么样的 JSON 才是合法的”。它不是业务数据本身，而是数据的结构约束。

### 3.3 Structured Output 是模型调用能力

Structured Output 是一种模型输出机制：调用方把结构约束传给模型服务，让模型尽量按照约定的 Schema 返回结果。

三者可以这样理解：

```text
JSON Schema：定义规则
Structured Output：在模型调用时使用规则约束输出
JSON：模型最终返回的数据
应用侧校验：再次确认返回数据确实符合规则
```

即使服务商支持 Structured Output，应用侧仍然应该保留解析和校验逻辑。远程服务可能发生版本变化、参数不兼容、截断、拒答、网络异常或 SDK 行为差异。

---

## 4. JSON Schema 的核心结构

下面是一个最小的对象 Schema：

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string"
    },
    "age": {
      "type": "integer",
      "minimum": 0
    }
  },
  "required": ["name", "age"],
  "additionalProperties": false
}
```

它表示：

- 根数据必须是对象；
- 对象有 `name` 和 `age` 两个字段；
- `name` 必须是字符串；
- `age` 必须是整数，并且不能小于 0；
- `name` 和 `age` 都必须出现；
- 不允许出现未定义的额外字段。

### 4.1 `type`

`type` 用来规定数据类型，常见取值包括：

| 类型 | 示例 |
|---|---|
| `object` | `{ "name": "Ada" }` |
| `array` | `["python", "json"]` |
| `string` | `"positive"` |
| `integer` | `3` |
| `number` | `0.95` |
| `boolean` | `true` |
| `null` | `null` |

注意，JSON 中的 `3` 是数字，`"3"` 是字符串。二者在 Schema 中不是同一种类型。

### 4.2 `properties`

`properties` 定义对象中各个字段的 Schema：

```json
{
  "type": "object",
  "properties": {
    "title": {"type": "string"},
    "tags": {
      "type": "array",
      "items": {"type": "string"}
    }
  }
}
```

仅写入 `properties` 并不意味着字段必填。字段是否必须出现，由 `required` 决定。

### 4.3 `required`

`required` 是字段名称数组：

```json
{
  "required": ["title", "tags"]
}
```

这表示两个字段都必须出现。它不表示字段一定有非空内容：

- `"title": ""` 可能仍然是合法的字符串；
- `"tags": []` 可能仍然是合法的数组。

如果还需要非空约束，应增加 `minLength` 或 `minItems`。

### 4.4 `additionalProperties`

```json
{
  "additionalProperties": false
}
```

表示对象只能出现 `properties` 中声明的字段。

设置为 `false` 的优点：

- 防止模型随意增加字段；
- 让下游数据结构更稳定；
- 更早发现字段名拼写错误。

但也要注意：如果需求允许未来扩展，直接禁止额外字段可能增加版本升级成本。是否设置为 `false`，应根据接口是否需要严格契约决定。使用部分模型服务的严格 Structured Output 时，服务商可能要求对象显式禁止额外字段，具体以实际接口文档为准。

### 4.5 `enum`

`enum` 限制字段只能取预定义值：

```json
{
  "type": "string",
  "enum": ["positive", "negative", "neutral", "mixed"]
}
```

枚举值应该使用稳定、适合程序处理的标识符。展示给用户的中文名称可以在应用层映射，不建议让同一字段同时混用中英文值。

### 4.6 常见范围约束

字符串：

```json
{
  "type": "string",
  "minLength": 1,
  "maxLength": 200
}
```

数字：

```json
{
  "type": "number",
  "minimum": 0,
  "maximum": 1
}
```

数组：

```json
{
  "type": "array",
  "items": {"type": "string"},
  "minItems": 1,
  "maxItems": 10,
  "uniqueItems": true
}
```

正则模式：

```json
{
  "type": "string",
  "pattern": "^[A-Z]{2}-[0-9]{4}$"
}
```

`pattern` 适合简单格式约束，不适合承载复杂业务逻辑。并且，一些模型服务的 Structured Output 只支持 JSON Schema 的子集，使用 `pattern`、`oneOf`、`$ref` 等关键字前，应先确认服务商是否支持。

---

## 5. 一个完整的评价分析 Schema

假设任务是分析客服评价，程序需要以下结果：

- `sentiment`：情感类别；
- `priority`：处理优先级，范围为 1 到 5；
- `summary`：一句话摘要；
- `keywords`：关键词列表；
- `needs_human_review`：是否需要人工复核。

可以设计为：

```python
review_schema = {
    "type": "object",
    "properties": {
        "sentiment": {
            "type": "string",
            "enum": ["positive", "negative", "neutral", "mixed"]
        },
        "priority": {
            "type": "integer",
            "minimum": 1,
            "maximum": 5
        },
        "summary": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200
        },
        "keywords": {
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 10
        },
        "needs_human_review": {
            "type": "boolean"
        }
    },
    "required": [
        "sentiment",
        "priority",
        "summary",
        "keywords",
        "needs_human_review"
    ],
    "additionalProperties": False
}
```

对应的合法数据：

```json
{
  "sentiment": "mixed",
  "priority": 3,
  "summary": "物流速度快，但包装有破损。",
  "keywords": ["物流", "包装"],
  "needs_human_review": false
}
```

下面这些数据不合法：

```json
{
  "sentiment": "一般",
  "priority": "3",
  "summary": "物流不错",
  "keywords": ["物流"],
  "needs_human_review": false,
  "confidence": 0.8
}
```

原因包括：

1. `sentiment` 不在枚举范围内；
2. `priority` 是字符串，不是整数；
3. `confidence` 没有在 `properties` 中声明，而 `additionalProperties` 为 `false`。

---

## 6. 在模型调用中使用 JSON Schema

不同服务商的参数名称和 SDK 封装可能不同。下面使用项目上一课中提到的 OpenAI 兼容 Chat Completions 风格，重点是理解 `response_format` 的结构；实际项目中应以所使用服务商的接口文档为准。

```python
import json
import os

from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

review_schema = {
    "type": "object",
    "properties": {
        "sentiment": {
            "type": "string",
            "enum": ["positive", "negative", "neutral", "mixed"]
        },
        "priority": {
            "type": "integer",
            "minimum": 1,
            "maximum": 5
        },
        "summary": {"type": "string", "minLength": 1},
        "keywords": {
            "type": "array",
            "items": {"type": "string"}
        },
        "needs_human_review": {"type": "boolean"}
    },
    "required": [
        "sentiment",
        "priority",
        "summary",
        "keywords",
        "needs_human_review"
    ],
    "additionalProperties": False
}

response = client.chat.completions.create(
    model=os.environ["LLM_MODEL"],
    messages=[
        {
            "role": "system",
            "content": (
                "你是客服评价分析器。根据用户评价判断情感、优先级、摘要和关键词。"
                "只能依据输入内容，不要臆造事实。"
            ),
        },
        {
            "role": "user",
            "content": "物流很快，但是包装有破损，客服态度不错。",
        },
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "review_analysis",
            "strict": True,
            "schema": review_schema,
        },
    },
)
```

这里的关键点是：

- `name` 是本次结构的名称，便于日志和调试；
- `schema` 是真正的 JSON Schema；
- `strict` 表示希望服务端严格遵守 Schema，但是否支持以及支持哪些关键字取决于具体服务；
- Schema 约束结构，System Prompt 仍然负责任务语义、判定标准和边界条件。

### 6.1 JSON Mode 与 JSON Schema 模式

两者不要混淆：

| 模式 | 主要保证 | 不能保证 |
|---|---|---|
| 普通文本输出 | 模型返回文本 | JSON 语法和字段结构 |
| JSON Mode | 通常保证结果是合法 JSON | 必填字段、枚举、字段类型和完整业务结构 |
| JSON Schema / Structured Output | 按 Schema 约束结构 | 事实一定正确、业务判断一定正确、服务永不出错 |

JSON Schema 模式更适合：

- 分类结果要进入数据库；
- 信息抽取结果要交给后续程序；
- Agent 工作流中的节点需要稳定输入；
- 多个模型或服务之间需要统一输出协议。

---

## 7. Schema 设计原则

### 7.1 从下游真正需要的数据开始

不要因为模型可以输出很多内容，就把所有可能字段都放进 Schema。先回答：

1. 下游程序会读取哪些字段？
2. 哪些字段会进入数据库或消息队列？
3. 哪些字段用于路由、排序或人工审核？
4. 哪些信息只需要放在自然语言解释中？

如果下游只需要分类和置信等级，就不必设计十几个解释字段。

### 7.2 字段名稳定，含义单一

不推荐：

```json
{
  "result": "negative, priority 5, needs escalation"
}
```

推荐拆成具有明确含义的字段：

```json
{
  "sentiment": "negative",
  "priority": 5,
  "needs_escalation": true
}
```

一个字段最好只表达一个概念，避免下游再次解析自然语言。

### 7.3 尽量使用枚举统一值域

如果下游只支持四类情感，就使用 `enum`，不要让模型自由生成标签。枚举设计应考虑：

- 值的数量是否足够覆盖业务；
- 是否需要 `unknown` 或 `other`；
- 是否需要 `mixed` 表示正负信息并存；
- 值是否方便写数据库查询和统计。

不要为了“看起来灵活”而使用过于开放的字符串。

### 7.4 可选字段与 `null` 要明确区分

以下三种状态含义不同：

1. 字段缺失：没有提供该字段；
2. 字段为 `null`：字段存在，但当前没有值；
3. 字段为空字符串或空数组：字段有值，但值为空。

例如，联系人电话可能使用：

```json
{
  "type": ["string", "null"]
}
```

但某些模型服务的严格 Schema 子集不支持任意写法的联合类型。若服务商不支持，可以改为：

```json
{
  "type": "object",
  "properties": {
    "available": {"type": "boolean"},
    "value": {"type": "string"}
  },
  "required": ["available", "value"],
  "additionalProperties": false
}
```

无论采用哪种形式，都要在接口文档中写清楚语义。

### 7.5 约束应该服务于业务，不要盲目复杂化

复杂 Schema 会带来：

- 模型更难稳定生成；
- 服务商兼容性更差；
- 调试成本更高；
- 版本升级更困难。

应该优先使用简单的对象、数组、字符串、数字、布尔值和枚举。只有下游确实需要时，才加入复杂的嵌套、条件结构或联合类型。

### 7.6 是否允许额外字段要提前决定

两种常见策略：

**严格闭合结构**：

```json
"additionalProperties": false
```

适合数据库写入、稳定 API 和自动化工作流。

**开放扩展结构**：

```json
"additionalProperties": true
```

适合探索性任务或需要兼容未来字段的场景，但下游必须忽略未知字段，不能因为多了字段就崩溃。

---

## 8. Python 中的本地校验

模型服务返回后，不应该只调用 `json.loads` 就直接进入业务流程。至少要经过以下步骤：

```text
读取响应
  ↓
检查错误、拒答和结束原因
  ↓
检查文本内容是否为空
  ↓
解析 JSON
  ↓
执行 JSON Schema 校验
  ↓
执行业务校验
  ↓
交给下游处理
```

### 8.1 使用 `jsonschema` 校验

安装依赖的示例：

```text
jsonschema
```

校验代码：

```python
import json
from jsonschema import Draft202012Validator


def validate_review_content(content: str, schema: dict) -> dict:
    if not content or not content.strip():
        raise ValueError("模型返回了空内容")

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError("模型返回的内容不是合法 JSON") from exc

    validator = Draft202012Validator(schema)
    errors = sorted(
        validator.iter_errors(data),
        key=lambda error: list(error.path),
    )

    if errors:
        details = []
        for error in errors:
            path = ".".join(str(item) for item in error.path) or "$"
            details.append(f"{path}: {error.message}")
        raise ValueError("JSON Schema 校验失败：" + "; ".join(details))

    return data
```

如果实际使用的模型服务只支持 JSON Schema 的一个子集，本地校验器仍然可以使用更完整的标准校验规则；但应保证发送给服务端的 Schema 与服务端支持范围兼容。

### 8.2 业务校验仍然不可省略

Schema 校验通过，只说明数据的形状符合规则。例如下面的结果可能通过 Schema：

```json
{
  "sentiment": "negative",
  "priority": 1,
  "summary": "用户要求退款。",
  "keywords": ["退款"],
  "needs_human_review": false
}
```

但如果原始评价中没有提到退款，或者高风险负面评价不应设置为优先级 1，那么它仍然是业务错误。

可以增加应用侧规则：

```python
def check_review_business_rules(data: dict) -> None:
    if data["sentiment"] == "negative" and data["priority"] >= 4:
        if not data["needs_human_review"]:
            raise ValueError("高优先级负面评价必须进入人工复核")

    if len(data["summary"].strip()) == 0:
        raise ValueError("摘要不能是空字符串")
```

Schema 负责通用结构，业务代码负责领域规则。不要试图用一个 Schema 表达全部业务逻辑。

---

## 9. 更安全的响应处理

项目上一课已经强调：模型返回空内容时，不能直接解析。实际应用还应结合结束原因、拒答信息和错误字段判断具体原因。

一个简化的处理示例：

```python
import json


def extract_json_content(response) -> dict:
    # 具体属性名称可能随 SDK 或服务商不同而变化。
    # 这里展示处理顺序，不代表所有兼容接口都完全相同。
    if getattr(response, "error", None):
        raise RuntimeError(f"模型请求错误：{response.error}")

    choices = getattr(response, "choices", None) or []
    if not choices:
        raise ValueError("模型响应中没有 choices")

    choice = choices[0]
    message = getattr(choice, "message", None)
    if message is None:
        raise ValueError("模型响应中没有 message")

    refusal = getattr(message, "refusal", None)
    if refusal:
        raise ValueError(f"模型拒答：{refusal}")

    content = getattr(message, "content", None)
    if not content or not content.strip():
        finish_reason = getattr(choice, "finish_reason", None)
        raise ValueError(
            f"模型返回了空内容，finish_reason={finish_reason!r}"
        )

    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError("模型内容无法解析为 JSON") from exc
```

生产代码还应记录但谨慎处理以下信息：

- 请求的模型和接口版本；
- Schema 名称和版本；
- `finish_reason`；
- 解析失败的安全摘要；
- 校验失败字段；
- 请求 ID 或追踪 ID。

不要在日志中无条件记录用户的敏感原文、访问令牌或完整隐私数据。

---

## 10. 使用 Pydantic 作为 Schema 来源

手写 JSON Schema 适合学习和简单场景。Python 项目也可以使用 Pydantic 先定义数据模型，再生成 Schema 和执行本地校验：

```python
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ReviewAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sentiment: Literal["positive", "negative", "neutral", "mixed"]
    priority: int = Field(ge=1, le=5)
    summary: str = Field(min_length=1, max_length=200)
    keywords: list[str] = Field(default_factory=list, max_length=10)
    needs_human_review: bool


review_schema = ReviewAnalysis.model_json_schema()

result = ReviewAnalysis.model_validate_json(
    '{"sentiment":"mixed","priority":3,"summary":"包装有破损",'
    '"keywords":["包装"],"needs_human_review":false}'
)
```

这种方式的优点：

- 类型定义和校验规则集中在一个 Python 类中；
- 可以复用类型检查和错误信息；
- 能生成供接口调用的 JSON Schema；
- 业务代码获得更明确的属性访问方式。

但也有注意事项：

- Pydantic 生成的 Schema 可能包含服务商不支持的关键字；
- 需要检查 `model_json_schema()` 的结果；
- 不同 Pydantic 版本和 SDK 的解析方法可能不同；
- 不要把“Pydantic 能校验”误认为“模型一定能生成”。

当 Schema 作为公共接口契约时，应把生成结果固定、审查并进行兼容性测试，而不是每次无审查地自动变化。

---

## 11. 常见失败场景与处理策略

### 11.1 Schema 本身不被服务端接受

可能原因：

- 使用了服务商不支持的关键字；
- 对象结构缺少严格模式要求的配置；
- `required` 与字段定义不一致；
- Schema 不是合法 JSON；
- Schema 深度或字段数量超过服务限制。

处理方法：

1. 先使用本地 JSON 校验器检查 Schema 本身；
2. 逐步删减复杂关键字，定位不兼容部分；
3. 查看服务商的 Structured Output 子集说明；
4. 为 Schema 保存版本和测试样例。

### 11.2 返回内容是合法 JSON，但 Schema 校验失败

可能原因：

- 模型服务没有启用真正的 Schema 约束；
- 调用参数写错，实际回退成普通文本模式；
- 模型或服务商对部分约束支持不完整；
- 返回被截断；
- 代码使用了与请求不一致的 Schema。

处理方法：

- 记录请求使用的 Schema 名称和版本；
- 检查完整响应中的错误信息和结束原因；
- 不要直接把失败结果写入数据库；
- 在安全边界内进行有限次数重试；
- 必要时把失败结果放入人工复核队列。

### 11.3 Schema 校验通过，但字段含义错误

例如：

- 把“物流很快但包装破损”判断为纯正面；
- 关键词并未出现在原文中；
- 摘要漏掉了退款金额；
- 低风险与高风险的优先级规则不一致。

处理方法：

- 在 Prompt 中明确分类标准；
- 用 Few-shot 覆盖边界案例；
- 增加业务规则校验；
- 建立人工标注集和离线评测；
- 对关键结果要求证据字段或原文片段，但不要让不必要的解释字段过度复杂化。

### 11.4 重试导致重复副作用

如果结构化输出后还会发送邮件、扣款或写入外部系统，不能简单地“失败就重试”。应：

- 将模型分析与副作用执行分开；
- 为请求设置幂等键；
- 先完成解析和校验，再执行副作用；
- 记录处理状态，避免重复执行。

---

## 12. Schema 版本管理

一旦 Schema 被多个服务使用，它就是接口契约，应该进行版本管理。

### 12.1 为 Schema 标记版本

可以在应用配置中保存：

```python
SCHEMA_NAME = "review_analysis"
SCHEMA_VERSION = "v1"
```

也可以增加字段：

```json
{
  "schema_version": "v1",
  "sentiment": "mixed",
  "priority": 3
}
```

是否把版本字段放进模型输出，要根据下游需要决定。至少应在请求日志、数据库记录或消息元数据中保留版本。

### 12.2 兼容性原则

通常更容易兼容的修改：

- 增加下游可以忽略的可选字段；
- 放宽某个字段的合法范围，但要评估业务影响；
- 增加枚举值，同时确保消费者能处理未知值。

风险较高的修改：

- 删除字段；
- 修改字段类型；
- 把可选字段改成必填；
- 修改枚举值含义；
- 修改单位、时区或数值范围；
- 改变 `null`、空字符串和字段缺失的语义。

生产环境中，重大变化可以创建 `v2`，并通过适配层同时支持旧版本一段时间。

---

## 13. 测试清单

### 13.1 Schema 静态测试

- Schema 本身是合法 JSON；
- 所有 `required` 字段都在 `properties` 中；
- 枚举列表没有重复值；
- 数值范围没有互相矛盾；
- 对象是否允许额外字段符合接口约定；
- 服务商支持所使用的关键字。

### 13.2 数据样例测试

至少准备：

- 正常样例；
- 最小合法样例；
- 空数组样例；
- 边界数值样例；
- 缺少必填字段的非法样例；
- 类型错误样例；
- 多余字段样例；
- 枚举值错误样例；
- 内容中包含提示注入的样例；
- 空输入和超长输入样例。

### 13.3 集成测试

使用真实的调用方式验证：

- `response_format` 是否被服务端接受；
- 服务端是否真的返回目标结构；
- 拒答和截断时应用是否安全失败；
- 不同模型是否都支持该 Schema；
- 重试是否会造成重复副作用；
- Schema 升级后旧消费者是否仍能工作。

---

## 14. JSON Schema 与 Prompt 的分工

JSON Schema 解决的是“输出长什么样”，Prompt 解决的是“应该如何完成任务”。二者不能互相替代。

不够完整的设计：

```text
请输出符合 Schema 的结果。
```

更好的设计应同时说明：

1. 任务目标；
2. 字段含义；
3. 分类标准；
4. 不确定时的处理方式；
5. 不允许依据输入之外的信息猜测；
6. Schema 只规定结构，所有字段仍必须符合业务定义。

例如：

```text
你负责分析客服评价。

- sentiment 只能表示评价整体情感：positive、negative、neutral 或 mixed。
- 同时存在明显正面和负面信息时使用 mixed。
- priority 为 1 到 5，涉及退款、财产损失、严重服务故障时优先级不低于 4。
- summary 只总结输入中明确出现的事实，不要添加推测。
- keywords 只填写输入中出现或可直接归纳的关键词。
- 无法确定时使用最保守的判断，并在业务允许的字段中表达不确定性。
```

如果某个判断标准非常关键，应该同时放在 Prompt、测试集和业务校验中，而不是只依赖其中一处。

---

## 15. 常见误区

### 误区一：JSON Schema 能保证事实正确

不能。Schema 只能验证结构和部分值域，无法证明模型的摘要、分类或抽取内容与原文事实一致。

### 误区二：写了 `properties` 就代表字段必填

不对。必须在 `required` 中明确列出必填字段。

### 误区三：`required` 能保证字段非空

不对。它只保证字段存在。非空字符串、数组数量和数值范围需要额外约束。

### 误区四：JSON Mode 等于 JSON Schema

不等于。JSON Mode 主要解决合法 JSON，JSON Schema 进一步约束字段结构和值域。

### 误区五：标准 JSON Schema 的所有语法都能直接传给模型服务

不一定。模型服务通常只实现一个子集，尤其是严格结构化输出模式。必须以实际服务商文档和集成测试为准。

### 误区六：Schema 越复杂越专业

不对。复杂度应由下游需求驱动。过度嵌套和大量条件分支会降低可维护性与生成稳定性。

### 误区七：解析成功就可以直接使用

不对。至少还需要 Schema 校验、业务校验和错误处理。

### 误区八：失败时无限重试

不安全。应限制次数，并区分参数错误、限流、超时、拒答、截断、解析失败和业务校验失败。

---

## 16. 实践任务

### 任务一：设计发票信息抽取 Schema

为下面的任务设计 Schema：

```text
从发票文本中抽取发票号码、开票日期、价税合计、购买方名称和商品明细。
```

要求：

- 明确字段类型；
- 规定日期和金额的表示方式；
- 商品明细使用数组；
- 处理缺失字段；
- 禁止额外字段或说明原因。

### 任务二：为意图分类器增加业务校验

设计一个分类器，类别为：

```text
refund、shipping、account、technical、other
```

要求：

- 使用 `enum`；
- 增加 `needs_human_review`；
- 当输入信息不足时不能强行选择具体类别；
- 为每个类别准备至少两个 Few-shot 示例；
- 编写本地 Schema 校验和业务校验。

### 任务三：测试 Schema 版本升级

将评价分析 Schema 从 `v1` 升级到 `v2`，增加一个字段：

```text
risk_level: low、medium、high
```

分别讨论：

- 将它设为必填字段会有什么影响；
- 旧消费者如何处理这个字段；
- 如果删除 `priority`，为什么属于高风险变更；
- 如何设计迁移和回滚方案。

---

## 17. 自测题

### 题目

1. `properties` 和 `required` 分别负责什么？
2. `additionalProperties: false` 有什么作用？
3. 为什么 `"priority": "3"` 不能满足 `{"type": "integer"}`？
4. JSON Mode 与 JSON Schema 模式的核心差别是什么？
5. Schema 校验通过后，为什么还需要业务校验？
6. 什么时候应该使用枚举？
7. 为什么不能默认使用所有标准 JSON Schema 关键字？
8. 模型返回空内容时，为什么不能直接调用 `json.loads`？

### 参考答案

1. `properties` 描述字段及其规则，`required` 指定哪些字段必须出现。
2. 限制对象只能包含已声明的字段，防止未预期字段进入下游。
3. 因为前者是字符串，后者要求整数；JSON 中字符串数字和数字是不同类型。
4. JSON Mode 通常只关注合法 JSON 语法，JSON Schema 还约束字段、类型、枚举、必填项等结构规则。
5. 因为 Schema 主要检查形状和有限的值域，不能证明模型判断符合原文和业务规则。
6. 当字段只能取有限、稳定且可枚举的值时使用，例如情感类别、状态和意图标签。
7. 因为模型服务往往只支持标准 JSON Schema 的子集，复杂关键字可能导致请求被拒绝或约束失效。
8. 空字符串不是有效的 JSON 文档，直接解析会抛出异常；还应结合拒答、错误字段和结束原因判断失败原因。

---

## 18. 本课重点总结

1. JSON 是具体数据，JSON Schema 是描述数据结构的规则，Structured Output 是在模型调用中使用结构约束的能力。
2. 一个实用 Schema 至少要认真设计 `type`、`properties`、`required`、枚举和额外字段策略。
3. `properties` 不会自动让字段必填，非空和范围也需要单独约束。
4. JSON Schema 主要约束结构，不保证模型的事实准确性和业务判断正确性。
5. 模型响应应依次经过错误检查、空内容检查、JSON 解析、Schema 校验和业务校验。
6. 标准 JSON Schema 与模型服务支持的 Schema 子集可能不同，必须结合实际服务文档和集成测试。
7. Schema 一旦被多个系统依赖，就应当像 API 一样进行版本管理和兼容性测试。
8. 设计 Schema 的原则不是越复杂越好，而是让下游真正需要的数据稳定、明确、可验证。

---

## 来源与说明

- 本课与项目中的 [第 04 课：Structured Output](./04-Structured-Output.md) 直接衔接，沿用其中关于结构化输出、JSON 解析和失败处理的学习脉络。
- JSON Schema 关键字、Python 校验示例和接口兼容性说明属于本课整理的通用知识；不同模型服务商、SDK 版本和 OpenAI 兼容接口的具体参数，以实际服务文档和集成测试结果为准。
