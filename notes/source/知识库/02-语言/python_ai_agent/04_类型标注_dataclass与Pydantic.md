# 04. 类型标注、`dataclass` 与 Pydantic

> 目标读者：已经会写基础 Python，希望把代码提升到可维护、可测试，并能安全承接大模型输入/工具输出的学习者。
>
> 本章示例按 Python 3.11+ 编写。代码中的类型标注主要服务于阅读、IDE、静态检查和重构；真正接收外部数据（HTTP、环境变量、模型生成的 JSON、工具参数）时，还需要运行时校验。

## 学习目标

学完本章后，你应当能够：

1. 用现代语法表达基础类型、容器、联合类型、字面量和可复用的类型别名。
2. 区分 `TypedDict`、`Protocol`、泛型、`Callable` 与具体的运行时对象。
3. 使用 `isinstance`、`is None`、`TypeGuard` 等方式进行类型缩窄，并理解静态类型检查和运行时检查的边界。
4. 用 `dataclass` 表达进程内的领域对象，用 `default_factory` 正确处理可变字段，用 `frozen`/`slots` 控制对象行为。
5. 用 Pydantic v2 定义输入模型、嵌套模型、工具参数和结构化输出，并完成校验、序列化和反序列化。
6. 知道何时选 `dataclass`、何时选 Pydantic，并把模型校验放在 Agent 系统的正确边界。

## 0. 运行本章示例

在笔记项目根目录执行。下面的命令创建一个隔离环境并安装 Pydantic；不要把包安装到系统 Python：

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate                 # macOS/Linux
# Windows PowerShell：.venv\Scripts\Activate.ps1
python -m pip install "pydantic>=2.11,<3" "pydantic-settings>=2.11,<3"
```

每个代码块都可以复制到一个 `.py` 文件中运行。例如：

```bash
python 04_type_demo.py
```

若你的环境只有 `python` 命令，后续命令中的 `python3` 可替换为 `python`。

## 1. 类型标注的定位：给人和工具看的契约

### 1.1 基础类型与容器

Python 变量本身没有“声明后不可改变类型”的限制，但标注可以说明函数的输入、输出和数据结构：

```python
from collections.abc import Iterable, Mapping, Sequence

user_id: int = 42
name: str = "Ada"
enabled: bool = True
score: float = 0.95
tags: list[str] = ["python", "agent"]
scores: dict[str, float] = {"planning": 0.95}
unique_tags: set[str] = {"python", "agent"}
point: tuple[int, int] = (10, 20)
words: tuple[str, ...] = ("one", "two", "three")

def average(values: Sequence[float]) -> float:
    return sum(values) / len(values)

def print_items(items: Iterable[str]) -> None:
    for item in items:
        print(item)

def get_name(record: Mapping[str, str]) -> str:
    return record["name"]
```

推荐优先使用 `list[str]`、`dict[str, int]` 等内置泛型，而不是旧式的 `typing.List`、`typing.Dict`。`Sequence` 表示可按下标访问的序列（如 `list`、`tuple`），`Iterable` 表示可以被 `for` 遍历；参数应尽量接受更抽象的接口，返回值再根据需要具体化。

常见特殊类型：

| 类型 | 含义 | 使用提醒 |
| --- | --- | --- |
| `Any` | 放弃静态检查，任意值都可通过 | 只在边界或确实无法描述时使用，避免污染调用链 |
| `object` | 所有对象的共同父类型 | 比 `Any` 安全；使用前通常要缩窄 |
| `None` | 空值，通常写在联合类型中 | `None` 不是“未提供”的唯一表示，需明确业务语义 |
| `Never` | 理论上不会正常返回 | 可用于总是抛异常或无限循环的函数 |
| `Final` | 约定一个名称不再重新绑定 | 主要由静态检查器检查，不是运行时常量保护 |

### 1.2 联合类型、`Optional` 和默认值

Python 3.10+ 推荐用 `A | B` 表示联合类型：

```python
def normalize(value: str | bytes) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return value.strip()

def find_user(user_id: int) -> str | None:
    # 找不到时返回 None
    return "Ada" if user_id == 1 else None
```

`Optional[str]` 等价于 `str | None`，只是旧式写法仍很常见。注意“允许为 `None`”与“参数可以省略”是两件事：

```python
def f(value: str | None) -> None:  # 调用者仍应传入 value
    ...

def g(value: str | None = None) -> None:  # value 可以省略
    ...
```

Pydantic v2 也遵循这一语义：`field: str | None` 默认仍是必填字段；若要可省略，显式写 `field: str | None = None`。

### 1.3 类型别名、`Literal` 与有限状态

类型别名让业务概念有名字。Python 3.11 写法如下；Python 3.12 才可使用 `type UserId = int` 的新语法：

```python
from typing import Literal, TypeAlias

UserId: TypeAlias = int
AgentStatus: TypeAlias = Literal["queued", "running", "completed", "failed"]

def set_status(status: AgentStatus) -> None:
    print(f"status={status}")

set_status("running")
# 静态检查器会拒绝 set_status("unknown")；运行时 Python 默认不会拒绝。
```

`Literal` 适合表达动作名、状态、工具类别等有限选项。若选项会由服务端动态变化，不要把动态数据硬编码成 `Literal`。

### 1.4 `TypedDict`：给“字典形状”加静态契约

`TypedDict` 仍然是普通字典，不能在运行时自动验证键和值。它适合描述内部 JSON-like 数据，特别是逐步迁移旧代码时：

```python
from typing import Literal, NotRequired, TypedDict

class Message(TypedDict):
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    tool_name: NotRequired[str]

message: Message = {"role": "user", "content": "搜索 Python 文档"}
```

`NotRequired` 表示键可以缺少；这不等于键存在但值为 `None`。外部不可信输入若必须验证，应使用 Pydantic 或手写校验，而不是只写 `TypedDict`。

### 1.5 `Protocol`：按能力而不是按继承关系编程

`Protocol` 支持结构化子类型（鸭子类型的静态版本）。只要对象具有所需方法，通常不必显式继承协议：

```python
from collections.abc import Sequence
from typing import Protocol

class Retriever(Protocol):
    def search(self, query: str, *, limit: int = 5) -> Sequence[str]:
        ...

class InMemoryRetriever:
    def search(self, query: str, *, limit: int = 5) -> list[str]:
        return [f"结果：{query}"][:limit]

def answer(query: str, retriever: Retriever) -> str:
    return "\n".join(retriever.search(query))

print(answer("什么是协程？", InMemoryRetriever()))
```

如果需要在运行时使用 `isinstance(value, Retriever)`，为协议添加 `@runtime_checkable`。运行时检查通常只能检查“是否有这个属性”，不能可靠检查参数类型和返回类型，因此不能代替测试或 Pydantic 校验。

### 1.6 泛型与 `Callable`

泛型把“结构相同、元素类型不同”表达为一个可复用的抽象：

```python
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")

@dataclass
class Result(Generic[T]):
    value: T | None = None
    error: str | None = None

def first(items: list[T]) -> T:
    if not items:
        raise ValueError("items 不能为空")
    return items[0]

number_result: Result[int] = Result(value=200)
text_result: Result[str] = Result(value="ok")
```

`Callable` 描述函数的参数和返回值：

```python
from collections.abc import Callable

Handler = Callable[[str, int], str]

def run_handler(handler: Handler, text: str) -> str:
    return handler(text, 1)
```

复杂装饰器若希望保留被装饰函数的参数类型，可以进一步学习 `ParamSpec` 和 `Concatenate`；在 Agent 工具注册器中，它们比写成 `Callable[..., Any]` 更安全。

### 1.7 类型缩窄与 `TypeGuard`

静态检查器不会因为一个变量标注为联合类型就自动知道它的具体分支。通过条件判断进行类型缩窄：

```python
def stringify(value: int | str | None) -> str:
    if value is None:
        return "<empty>"
    if isinstance(value, int):
        return str(value + 1)
    return value.upper()
```

对于可复用的复杂判断，可返回 `TypeGuard[T]`：

```python
from typing import TypeGuard

def is_str_list(value: object) -> TypeGuard[list[str]]:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)

def join_if_valid(value: object) -> str:
    if is_str_list(value):
        return ", ".join(value)
    return ""
```

类型缩窄是静态工具根据代码路径做出的推断。它不会自动把运行时错误变成安全结果；外部输入仍须先验证。

### 1.8 静态类型与运行时类型的边界

```python
def add(a: int, b: int) -> int:
    return a + b

result = add("1", "2")  # 多数静态检查器报错；运行时实际得到字符串 "12"
print(result, type(result))
```

可以把数据流分成两层：

```text
网络/文件/环境变量/LLM JSON
        │ 运行时验证：Pydantic、显式解析、权限检查
        ▼
可信的领域对象与函数调用
        │ 静态约束：mypy/Pyright、IDE、代码审查
        ▼
可维护的业务逻辑
```

类型标注不是权限系统、序列化协议或安全边界。`cast()` 只是告诉静态检查器“相信我”，不会转换或验证对象；不要把 `cast()` 当作校验函数。

### 1.9 注解如何求值：运行时对象、字符串和静态检查

类型注解写在源代码里，但它有两个容易混淆的生命周期：

1. **解释器定义阶段**：类或函数定义时，Python 可能立即求值注解表达式，并把结果放到 `__annotations__`。
2. **静态检查阶段**：mypy、Pyright、IDE 等读取源码/AST，独立推断类型，不会把标注变成运行时检查器。

```python
from __future__ import annotations

from typing import get_type_hints

class Node:
    def __init__(self, value: str, next_node: Node | None = None) -> None:
        self.value = value
        self.next_node = next_node

def describe(node: Node) -> list[str]:
    return [node.value]

print(Node.__init__.__annotations__)  # 使用 future 注解时，部分值会以字符串保存
print(get_type_hints(Node.__init__))   # 在可信模块上下文中解析为真正的类型对象
```

`from __future__ import annotations` 必须放在文件开头（仅允许出现在模块文档字符串之后），可以让前向引用更容易书写，也减少定义顺序问题。`typing.get_type_hints()` 会在运行时解析名称，可能执行属性访问或读取模块全局环境；不要把它当成对不可信源码的沙箱工具。框架（如 FastAPI、Pydantic）会自行读取注解，具体解析规则以框架为准。

如果库要支持 Python 3.11，不能使用 Python 3.12 才加入的 `type Alias = ...` 语法；应使用 `Alias: TypeAlias = ...`。注解解析失败通常来自：导入缺失、前向引用名称不在命名空间、循环导入或运行时对象与静态标注不一致。

### 1.10 `Any`、`object` 与 `Unknown` 的安全梯度

这三个词经常被混用，但它们承担不同职责：

| 表达 | 静态含义 | 访问属性/调用 | 适合 Agent 的位置 |
| --- | --- | --- | --- |
| `Any` | 放弃对该值的大部分检查，向上下游传播“动态” | 静态检查器通常全部放行 | 第三方无类型边界、临时迁移；应尽快收窄 |
| `object` | 任何 Python 对象，但不知道它的能力 | 不能直接调用或访问未知属性，必须先缩窄 | 不可信 JSON 尚未解析前的安全占位 |
| `Unknown` | 某些检查器（尤其 Pyright）用于“类型未知”的内部概念 | 通常要求先检查才能安全使用 | 逐步引入严格检查时的信号；不是 Python 运行时类型 |

Python 标准 `typing` 没有一个可以在运行时实例化的 `Unknown`。若函数接收模型输出，宁可先写 `object`，再通过 Pydantic/`TypeGuard` 验证，也不要为了消除报错直接改成 `Any`：

```python
from typing import Any

def unsafe_title(payload: Any) -> str:
    return payload["title"].strip()  # 任意错误都被推迟到运行时

def safe_title(payload: object) -> str:
    if not isinstance(payload, dict):
        raise TypeError("payload 必须是字典")
    title = payload.get("title")
    if not isinstance(title, str):
        raise TypeError("title 必须是字符串")
    return title.strip()
```

`object` 不能保证业务字段存在，但它迫使你显式处理不确定性；对重复出现的结构，应升级为 `TypedDict`（静态形状）或 Pydantic（运行时校验）。

### 1.11 联合类型的可读性、容器不变性和缩窄策略

`A | B` 描述的是“值可能属于 A 或 B”，不是“两个值同时存在”。联合分支越多，调用者越难推理，通常应抽取成 `dataclass`/Pydantic 模型或使用判别字段：

```python
from typing import Literal, TypedDict

class ToolMessage(TypedDict):
    kind: Literal["tool"]
    name: str

class TextMessage(TypedDict):
    kind: Literal["text"]
    content: str

Message = ToolMessage | TextMessage

def message_label(message: Message) -> str:
    if message["kind"] == "tool":
        return f"tool:{message['name']}"
    return message["content"]
```

对泛型容器要注意可变性：`list[Dog]` 不能在类型安全上当作 `list[Animal]`，因为调用者可能向后者写入一只不是 `Dog` 的 `Animal`。只读参数优先使用协变的 `Sequence[Animal]`：

```python
from collections.abc import Sequence

class Animal:
    pass

class Dog(Animal):
    pass

def count_animals(animals: Sequence[Animal]) -> int:
    return len(animals)

dogs: list[Dog] = [Dog(), Dog()]
print(count_animals(dogs))  # Sequence 只读接口允许这种安全传递
```

`Optional[T]` 只是一种写法糖，等价于 `T | None`；它不代表异常、缺失键、空字符串或空列表。Agent 请求要分别决定“字段缺失”“字段显式为 null”和“字段为空字符串”是否有不同意义，再选择默认值和校验规则。

### 1.12 `TypeAlias`、`Literal` 和可演进的状态机

类型别名应表达领域概念，而不是给每个简单类型机械加名字：

```python
from typing import Literal, TypeAlias

RunId: TypeAlias = str
Action: TypeAlias = Literal["call_tool", "respond", "ask_user"]

def transition(action: Action) -> str:
    return {
        "call_tool": "执行工具",
        "respond": "输出答案",
        "ask_user": "等待补充信息",
    }[action]

print(transition("respond"))
```

`Literal` 由静态检查器约束拼写，但 Python 运行时仍可接收动态字符串；需要运行时约束时，使用 Pydantic 的 `Literal` 字段或显式集合检查。状态选项会随服务端配置动态变化时，使用 `str` 加运行时注册表更合适，不要每次改配置都修改类型源码。

### 1.13 `TypedDict` 的 required/optional 细节

```python
from typing import NotRequired, Required, TypedDict

class RunContext(TypedDict, total=False):
    request_id: Required[str]
    user_id: NotRequired[str]
    metadata: NotRequired[dict[str, str]]

context: RunContext = {"request_id": "req-1"}
```

`total=False` 会让字段默认可缺失，`Required` 可把其中字段重新设为必需，`NotRequired` 可明确表示可缺失。它们影响静态工具对“键可能不存在”的提示；运行时 `RunContext` 仍然只是 `dict`，不会阻止 `{"request_id": 123}`。将 LLM 输出从字典转成 `RunContext` 之前，仍须用 Pydantic 或显式解析。

### 1.14 `Protocol` 的运行时检查与测试替身

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Clock(Protocol):
    def now(self) -> float:
        ...

class FakeClock:
    def __init__(self, value: float) -> None:
        self.value = value

    def now(self) -> float:
        return self.value

clock = FakeClock(10.0)
print(isinstance(clock, Clock))  # True；这里只检查所需属性是否存在
```

`runtime_checkable` 的 `isinstance` 不会验证方法参数和返回值签名，也不能验证行为契约（例如“时间必须单调递增”）。Agent 测试中，`Protocol` 用于注入模型客户端、检索器、时钟或事件发布器；测试替身还要用测试断言验证调用结果和副作用。

### 1.15 `TypeVar`、边界与类型安全的返回值

```python
from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")
NumberT = TypeVar("NumberT", int, float)

def first_item(items: Sequence[T]) -> T:
    if not items:
        raise ValueError("序列不能为空")
    return items[0]

def add_numbers(left: NumberT, right: NumberT) -> NumberT:
    return left + right

print(first_item(["a", "b"]))
print(add_numbers(1, 2))
```

无约束 `T` 表示“输入和输出保持同一类型关系”；约束 `NumberT` 表示只能是列出的几种类型。也可用 `TypeVar("T", bound=ProtocolName)` 表示“满足某种能力的任意子类型”。不要在函数内部把 `T` 强行转换成某个具体类型，否则标注的泛型关系就失真。

### 1.16 `Callable`、回调和保留签名的装饰器

简单回调用 `Callable[[参数类型...], 返回类型]`：

```python
from collections.abc import Callable

Formatter = Callable[[str], str]

def render(text: str, formatter: Formatter) -> str:
    return formatter(text)

print(render("hello", str.upper))
```

装饰器若写成 `Callable[..., Any]`，会丢失参数信息。更严格的通用装饰器可以使用 `ParamSpec`：

```python
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def traced(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@traced
def add(left: int, right: int) -> int:
    return left + right

print(add(1, 2))
```

`ParamSpec` 主要帮助静态检查器保留被包装函数的调用签名；它不在运行时检查参数。工具注册器仍需在注册时验证名字唯一、参数模型存在，并在执行前做权限检查。

### 1.17 类型缩窄的完整流程

当数据来自 JSON 时，可以先做便宜的形状判断，再交给模型验证：

```python
from typing import TypeGuard

def looks_like_mapping(value: object) -> TypeGuard[dict[str, object]]:
    return isinstance(value, dict) and all(isinstance(key, str) for key in value)

def get_action(raw: object) -> str:
    if not looks_like_mapping(raw):
        raise TypeError("输出必须是字符串键字典")
    action = raw.get("action")
    if not isinstance(action, str):
        raise ValueError("action 必须是字符串")
    return action

print(get_action({"action": "respond"}))
```

`TypeGuard` 的返回值是给静态检查器看的承诺；如果实现错误，检查器也会被误导。因此应为守卫函数写测试。对于复杂嵌套和跨字段约束，直接使用 Pydantic 通常比手写多层 `isinstance` 更清晰。

## 2. `dataclass`：轻量的进程内数据对象

### 2.1 基本字段、默认值与 `default_factory`

`@dataclass` 自动生成 `__init__`、`__repr__`、`__eq__` 等方法，适合表示已经在程序内部具有可信结构的对象：

```python
from dataclasses import dataclass, field

@dataclass
class AgentState:
    request_id: str
    messages: list[str] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)
    max_steps: int = 8

state = AgentState("req-001")
state.messages.append("用户：解释迭代器")
print(state)
```

绝对不要写 `messages: list[str] = []` 或 `metadata: dict[str, str] = {}`。可变对象会被多个实例共享；`default_factory` 会在每次实例化时新建一个对象。

字段顺序遵循普通函数参数规则：没有默认值的字段放在有默认值字段之前。`field()` 可指定 `default`、`default_factory`、`init`、`repr`、`compare` 和 `metadata`。

### 2.2 `frozen`、`slots`、`post_init` 与派生字段

```python
from dataclasses import dataclass, field

@dataclass(frozen=True, slots=True)
class ToolCall:
    name: str
    arguments: dict[str, object] = field(default_factory=dict)
    normalized_name: str = field(init=False)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("工具名不能为空")
        object.__setattr__(self, "normalized_name", self.name.strip().lower())

call = ToolCall(" Search ", {"query": "Python"})
print(call.normalized_name)
```

- `frozen=True` 禁止通过普通赋值重新绑定字段，并使对象通常可哈希（是否可哈希还取决于字段）。它是浅不可变的：如果字段内有 `list`/`dict`，容器内部仍可变。
- `slots=True` 用槽位存储字段，通常能减少对象开销，并阻止随意添加未声明的属性；需要动态属性时不要使用它。
- `__post_init__` 在自动生成的 `__init__` 之后运行，适合做简单不变量检查或计算派生字段。它不会自动递归验证嵌套数据。
- `ClassVar` 字段不是实例字段，不会参与生成的 `__init__`：

```python
from dataclasses import dataclass
from typing import ClassVar

@dataclass
class RetryPolicy:
    attempts: int = 3
    default_backoff: ClassVar[float] = 0.5
```

常用辅助函数：`dataclasses.asdict()` 递归转成字典，`dataclasses.replace(obj, field=value)` 创建修改后的副本。若对象要接收不可信 JSON，不要仅依赖 `dataclass` 的标注。

### 2.3 生成的方法与字段生命周期

可以把 `dataclass` 看成一个“根据字段声明生成样板代码”的装饰器，而不是一个验证框架。默认情况下它主要生成：

| 生成项 | 作用 | 何时调整 |
| --- | --- | --- |
| `__init__` | 按字段接收构造参数 | `init=False`、`kw_only=True` 可改变参数形状 |
| `__repr__` | 输出便于调试的表示 | 密钥/大文本字段应设 `repr=False` |
| `__eq__` | 按字段比较相等性 | `compare=False` 排除缓存/运行时字段 |
| `__hash__` | 由 `frozen` 等配置决定 | 可变对象不要随意启用 `unsafe_hash` |
| 排序方法 | `order=True` 时生成 | 只有确有全序语义时才启用 |

字段大致经历“类定义 → 构造参数 → `__post_init__` → 正常使用 → 序列化/复制”的生命周期：

```python
from dataclasses import asdict, dataclass, field, replace

@dataclass
class RunState:
    run_id: str
    messages: list[str] = field(default_factory=list, repr=False)
    step_count: int = field(default=0, compare=False)

    def add_message(self, message: str) -> None:
        self.messages.append(message)
        self.step_count += 1

state = RunState("run-1")
state.add_message("开始")
copied = replace(state, run_id="run-2")
print(asdict(state))
print(copied.run_id, copied.messages is state.messages)
```

`replace()` 会重新构造对象；对于普通字段，结果通常是浅复制，嵌套可变对象仍可能共享。若要完全隔离消息历史，应显式复制列表。`asdict()` 会递归复制 dataclass 字段，但不应直接用来输出秘密或大规模对象。

### 2.4 `dataclass` 继承、默认字段和不变量

继承时，父类字段会参与子类构造函数，默认字段仍不能排在无默认字段之前：

```python
from dataclasses import dataclass

@dataclass
class Event:
    event_id: str

@dataclass
class ToolEvent(Event):
    tool_name: str
    success: bool = True

event = ToolEvent(event_id="e-1", tool_name="search")
print(event)
```

当父类已经有默认字段、子类又要添加无默认字段时，可能出现 `TypeError: non-default argument follows default argument`。解决方式包括：使用 `kw_only=True`、调整继承层次、把配置组合而不是继承，或让新增字段也有合理默认值。Agent 的状态对象通常更适合组合（例如 `RunState` 持有 `RetryPolicy`）而不是深层继承。

`__post_init__` 适合校验局部不变量，但不要在其中联网或读取全局可变配置：

```python
from dataclasses import dataclass

@dataclass
class RetryPolicy:
    max_attempts: int = 3
    backoff_s: float = 0.5

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts 必须至少为 1")
        if self.backoff_s < 0:
            raise ValueError("backoff_s 不能为负数")
```

如果类通过自定义 `__init__` 构造，`__post_init__` 不会自动被调用；自定义构造逻辑时要明确是否需要手动调用或改用类方法工厂。

### 2.5 选择 `frozen`、`slots`、`kw_only` 的标准

- 值对象（ID、策略、不可变请求快照）优先考虑 `frozen=True`；若内部有列表，应改为元组或在边界复制。
- 大量短生命周期对象（事件、消息元数据）且不需要动态属性时考虑 `slots=True`；先用基准测试确认收益。
- 参数很多、未来容易增加字段的配置对象可使用 `kw_only=True`，避免位置参数错位：

```python
from dataclasses import dataclass

@dataclass(kw_only=True, slots=True)
class AgentLimits:
    max_steps: int = 8
    timeout_s: float = 30.0

limits = AgentLimits(timeout_s=10.0)
print(limits)
```

`frozen` 是对象属性重新绑定的限制，不是并发安全保证；`slots` 是布局/属性限制，也不是序列化协议。需要跨进程或网络传输时仍要定义明确的 schema。

## 3. Pydantic v2：运行时数据边界

### 3.1 安装与最小模型

在已激活的虚拟环境中执行：

```bash
python -m pip install "pydantic>=2.11,<3" "pydantic-settings>=2.11,<3"
```

Pydantic 模型会在实例化时解析和校验数据：

```python
from pydantic import BaseModel, ConfigDict, Field

class UserInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: str = Field(min_length=1, max_length=80)
    age: int = Field(ge=0, le=150)

user = UserInput(name=" Ada ", age="36")
print(user.name, type(user.age))  # Ada  <class 'int'>
print(user.model_dump())
```

默认情况下 Pydantic 会做适度的类型转换（例如可解析的数字字符串转为整数），但转换不是业务校验的全部。需要严格行为时，使用 `ConfigDict(strict=True)` 或对字段设置严格类型，并为业务规则写验证器。

### 3.2 字段约束、配置与验证器

下面是一个可独立运行的 Agent 工具参数模型：

```python
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

class SearchArgs(BaseModel):
    model_config = ConfigDict(
        extra="forbid",              # 拒绝模型多生成的未知字段
        str_strip_whitespace=True,
    )

    query: str = Field(min_length=1, max_length=200, description="搜索关键词")
    top_k: int = Field(default=5, ge=1, le=20)
    language: Literal["zh", "en"] = "zh"

    @field_validator("query")
    @classmethod
    def query_must_have_text(cls, value: str) -> str:
        if not any(char.isalnum() for char in value):
            raise ValueError("query 至少要包含字母或数字")
        return value

class SearchResult(BaseModel):
    title: str
    url: str
    score: float = Field(ge=0, le=1)

class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult] = Field(default_factory=list)

class AgentDecision(BaseModel):
    """约束 Agent 的可执行决策；rationale 只记录简短理由，不保存隐式思维链。"""

    model_config = ConfigDict(extra="forbid")

    action: Literal["tool", "final", "ask_user"]
    reason_summary: str = Field(min_length=1, max_length=500)
    # 当前示例只有 search 工具，因此名称与参数模型保持一一对应。
    tool_name: Literal["search"] | None = None
    tool_args: SearchArgs | None = None

    @model_validator(mode="after")
    def check_tool_fields(self) -> "AgentDecision":
        if self.action == "tool" and (self.tool_name is None or self.tool_args is None):
            raise ValueError("action=tool 时必须提供 tool_name 和 tool_args")
        if self.action != "tool" and (self.tool_name is not None or self.tool_args is not None):
            raise ValueError("非 tool 动作不应携带工具调用字段")
        return self

args = SearchArgs.model_validate({"query": "  Python typing  ", "top_k": 3})
decision = AgentDecision.model_validate(
    {
        "action": "tool",
        "reason_summary": "需要检索资料",
        "tool_name": "search",
        "tool_args": args.model_dump(),
    }
)
print(decision.model_dump(mode="json"))
print(AgentDecision.model_json_schema())
```

这个 `AgentDecision` 是“只有一个搜索工具”的教学模型，不是任意工具都安全适用的通用协议。工具增加后，应像 3.5 节那样使用判别联合，或通过服务端工具注册表把每个工具名映射到自己的参数模型并再次校验，避免出现“名称是 calculator，参数却是 SearchArgs”的错配。

Pydantic v2 中常用 API：

| API | 作用 |
| --- | --- |
| `Model.model_validate(data)` | 从 Python 字典/对象校验并构造模型 |
| `Model.model_validate_json(text)` | 从 JSON 字符串校验并构造模型 |
| `model.model_dump()` | 转为 Python 字典 |
| `model.model_dump(mode="json")` | 产生更适合 JSON 的 Python 值 |
| `model.model_dump_json()` | 序列化为 JSON 字符串 |
| `Model.model_json_schema()` | 生成 JSON Schema，可给工具注册或结构化输出使用 |
| `Field(...)` | 约束、默认值、描述、别名等字段元数据 |
| `@field_validator` | 一个或多个字段的自定义校验 |
| `@model_validator` | 需要同时查看多个字段的不变量校验 |

验证器应保持确定性、快速、无外部副作用。网络请求、数据库查询和模型调用不应放进字段验证器。

### 3.3 Pydantic v2 的校验管线与模式选择

一次 `Model.model_validate(data)` 可以按以下顺序理解：

```text
输入 Python 对象/JSON
        ↓
字段和模型配置决定 schema
        ↓
before/wrap 验证器（需要时先预处理）
        ↓
核心类型解析与字段约束（如 int、Literal、ge/le）
        ↓
after 字段验证器
        ↓
after 模型验证器（跨字段不变量）
        ↓
成功得到模型，或集中抛出 ValidationError
```

验证器模式的选择：

- `mode="before"`：收到原始输入，适合兼容旧格式或清理外层数据；输入类型可能是任何对象，必须谨慎。
- 默认 `mode="after"`：字段已完成类型解析，适合检查规范化后的值。
- `mode="wrap"`：在核心验证前后包裹流程，适合记录或有条件地转换异常；复杂度更高，少用。
- `@model_validator(mode="after")`：字段都通过后检查互相依赖的规则。

```python
from pydantic import BaseModel, ValidationError, field_validator

class PositiveBatch(BaseModel):
    values: list[int]

    @field_validator("values", mode="before")
    @classmethod
    def split_csv(cls, value: object) -> object:
        if isinstance(value, str):
            return [part.strip() for part in value.split(",")]
        return value

try:
    PositiveBatch.model_validate({"values": "1, 2, 3"})
    PositiveBatch.model_validate({"values": [1, "bad"]})
except ValidationError as exc:
    print(exc.errors())  # 每条错误包含 location、type、message 等结构化信息
```

上例的 `before` 验证器只做输入形状兼容；真正的整数解析仍由 Pydantic 完成。不要在 `before` 中假设值一定是字符串，也不要直接修改可能被其他分支共享的可变输入。

宽松和严格模式的取舍：

```python
from pydantic import BaseModel, ConfigDict, StrictInt, ValidationError

class LaxRequest(BaseModel):
    count: int

class StrictRequest(BaseModel):
    model_config = ConfigDict(strict=True)
    count: int

print(LaxRequest.model_validate({"count": "3"}).count)  # 可能解析为 3
try:
    StrictRequest.model_validate({"count": "3"})
except ValidationError:
    print("严格模式拒绝字符串")

class FieldStrictRequest(BaseModel):
    count: StrictInt
```

宽松模式适合已知格式、需要兼容表单/环境变量的输入；严格模式适合工具参数、金额、计数、权限级别等不应隐式转换的边界。`bool` 与 `int` 的兼容性也可能让宽松校验产生意外，关键字段应使用严格类型并配合测试。模式选择应在项目边界统一，不要一部分模型宽松、一部分模型无说明。

### 3.4 `Field`、别名和错误信息设计

`Field` 不只是写范围，也可以描述 JSON Schema、默认工厂和外部字段名：

```python
from pydantic import BaseModel, Field

class ToolPage(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=200,
        description="用户可见的搜索关键词，不要包含凭证",
        examples=["Python 迭代器"],
    )
    page_size: int = Field(default=10, ge=1, le=50, alias="pageSize")

page = ToolPage.model_validate({"query": "Python", "pageSize": 5})
print(page.page_size)
print(page.model_dump(by_alias=True))
```

字段描述会进入 JSON Schema，可能被工具注册器或模型调用协议使用；描述要准确、短小，不要把秘密或执行权限藏在描述中。面向外部协议时用 `alias` 固定 wire format，内部 Python 名称保持符合 PEP 8。Pydantic 2.11+ 推荐用 `validate_by_name` 与 `validate_by_alias` 分别控制是否接受字段名和别名；旧代码常见的 `populate_by_name=True` 在新版本中已不推荐，迁移时要配合项目的版本下限测试输入兼容性。

### 3.5 嵌套模型与判别联合

当一个字段可能是几种结构时，使用带判别字段的联合比“很多可选字段”更清晰：

```python
from typing import Annotated, Literal

from pydantic import BaseModel, Field

class SearchCall(BaseModel):
    kind: Literal["search"]
    query: str

class CalculatorCall(BaseModel):
    kind: Literal["calculator"]
    expression: str

ToolCall = Annotated[SearchCall | CalculatorCall, Field(discriminator="kind")]

class Plan(BaseModel):
    calls: list[ToolCall]

plan = Plan.model_validate(
    {"calls": [{"kind": "search", "query": "Python"}]}
)
print(type(plan.calls[0]).__name__)
```

判别联合让 Pydantic 能根据 `kind` 选择分支并给出局部错误路径，也让 Agent 工具协议更容易演进。执行前仍需把 `kind` 映射到白名单注册表，不能直接把模型生成的字符串当作 Python 函数名。

### 3.6 `TypeAdapter`：不必为每个片段创建模型类

`TypeAdapter` 可验证任意类型（包括列表、联合、标准库类型和 TypedDict），适合工具返回值或配置片段：

```python
from typing import Literal

from pydantic import TypeAdapter, ValidationError

adapter = TypeAdapter(list[Literal["read", "write"]])
print(adapter.validate_python(["read", "write"]))
print(adapter.dump_json(["read"]))

try:
    adapter.validate_json('["delete"]')
except ValidationError as exc:
    print(exc.errors()[0]["type"])
```

选择标准：有多个字段、方法和业务不变量时定义 `BaseModel`；只有一个可复用类型表达式时使用 `TypeAdapter`。两者都提供运行时校验，但 `TypeAdapter` 不生成模型类属性，也没有 `model_dump()` 这类实例 API。

### 3.7 嵌套模型、别名与序列化

嵌套模型把复杂输出拆成可复用的结构：

```python
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class Citation(BaseModel):
    title: str
    url: str

class FinalAnswer(BaseModel):
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    answer: str = Field(min_length=1)
    citations: list[Citation] = Field(default_factory=list)
    generated_at: datetime
    trace_id: str = Field(alias="traceId")

payload = {
    "answer": "迭代器按需产生值。",
    "citations": [{"title": "Python 文档", "url": "https://docs.python.org/3/"}],
    "generated_at": "2025-01-01T00:00:00Z",
    "traceId": "trace-001",
}
answer = FinalAnswer.model_validate(payload)
print(answer.model_dump(by_alias=True, mode="json"))
```

选择 `extra="forbid"` 还是 `extra="ignore"` 要看边界：工具参数和 Agent 决策通常应该拒绝未知字段，兼容第三方响应时才可能选择忽略。`model_dump(exclude_none=True)` 可以省略空值，但不要因此丢掉业务上“明确为 null”的语义。

### 3.8 `BaseSettings`：从环境变量读取配置

配置是另一个不可信边界。使用 `pydantic-settings` 的 `BaseSettings` 可把环境变量解析为类型化配置：

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AGENT_",
        env_file=".env",
        extra="ignore",
    )

    model_name: str = "default-model"
    request_timeout_s: float = Field(default=30.0, gt=0)
    debug: bool = False

settings = Settings()
print(settings.model_name, settings.request_timeout_s)
```

运行前可设置环境变量：

```bash
AGENT_MODEL_NAME=my-model AGENT_REQUEST_TIMEOUT_S=10 python settings_demo.py
```

`.env` 适合本地开发，不应提交真实密钥；生产环境优先使用平台 Secret/环境变量。不要把 API key 放进日志、异常文本、模型提示词或 `model_dump()` 的调试输出。

`BaseSettings` 的读取顺序也应写进项目说明：明确传入的构造参数通常优先于环境变量，环境变量优先于默认值；`.env` 是本地便利来源，不应成为生产秘密管理系统。需要嵌套设置时可以约定分隔符，但要避免把任意环境变量自动映射成权限字段：

```python
import os

from pydantic_settings import BaseSettings, SettingsConfigDict

class ServiceSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AGENT_", extra="ignore")

    timeout_s: float = 30.0
    environment: str = "development"

os.environ["AGENT_TIMEOUT_S"] = "12.5"
settings = ServiceSettings()
print(settings.timeout_s, settings.environment)
```

真实项目不要在模块导入时无条件创建全局 `Settings()` 并打印内容；测试需要通过构造参数或 monkeypatch 注入配置，避免测试顺序和进程环境互相影响。

### 3.9 序列化、反序列化和字段暴露

Pydantic 的“模型对象”与“传输格式”应明确区分：

```python
from datetime import datetime, timezone

from pydantic import BaseModel, SecretStr

class InternalConfig(BaseModel):
    model_name: str
    api_key: SecretStr
    created_at: datetime

config = InternalConfig(
    model_name="demo",
    api_key="do-not-log",
    created_at=datetime.now(timezone.utc),
)
print(config.model_dump(mode="json", exclude={"api_key"}))
print(config.model_dump_json(exclude={"api_key"}))
```

`model_dump()` 默认产生 Python 值；`mode="json"` 会把日期等值转换为 JSON 友好表示；`model_dump_json()` 直接输出字符串。`exclude`/`include` 是字段暴露策略的一部分，尤其适合把内部配置和用户响应分开。`SecretStr` 的打印表示会遮蔽值，但如果主动调用 `get_secret_value()` 或把原始输入写日志，仍然会泄露。

输入和输出要测试往返契约：

```python
from pydantic import BaseModel

class ToolResult(BaseModel):
    items: list[str]
    truncated: bool = False

raw = '{"items": ["a", "b"], "truncated": false}'
result = ToolResult.model_validate_json(raw)
round_trip = ToolResult.model_validate(result.model_dump(mode="json"))
assert round_trip == result
```

序列化成功不代表数据可以安全地发送给模型或用户；仍需限制结果长度、去除内部字段、脱敏和内容安全检查。

## 4. `dataclass` 与 Pydantic 如何分工

一个实用边界是：

| 场景 | 推荐 | 原因 |
| --- | --- | --- |
| Agent 内部状态、队列项、策略对象 | `dataclass` | 轻量、明确、构造快，不强行做输入解析 |
| HTTP 请求/响应、配置、LLM JSON、工具参数 | Pydantic | 需要运行时校验、错误定位和 JSON Schema |
| 只需给 IDE/检查器提示的字典 | `TypedDict` | 无运行时开销，但不提供验证 |
| 需要由调用方提供能力的接口 | `Protocol` | 解耦实现，便于替换和测试 |

典型 Agent 工具流水线：

```text
模型生成 JSON
   ↓ model_validate_json()
Pydantic ToolArgs（拒绝未知字段、校验范围）
   ↓ 业务授权/限流/超时
工具函数（接收已验证参数）
   ↓
Pydantic ToolResult 或内部 dataclass
   ↓ model_dump_json()
模型/HTTP 响应
```

验证通过不代表操作被授权。工具调用仍应检查用户权限、URL/路径白名单、资源额度、超时和重试策略。Pydantic 的 JSON Schema 可以帮助模型生成格式正确的参数，但模型仍可能生成危险或不符合业务意图的值。

### 4.1 Agent 工具 Schema 与结构化输出的闭环

一个稳健的工具注册记录可以同时保存名称、参数模型和执行函数：

```python
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, Field

class WeatherArgs(BaseModel):
    city: str = Field(min_length=1, max_length=80)

class ToolSpec:
    def __init__(
        self,
        name: str,
        args_model: type[BaseModel],
        execute: Callable[[BaseModel], Any],
    ) -> None:
        self.name = name
        self.args_model = args_model
        self.execute = execute

def fake_weather(args: BaseModel) -> dict[str, str]:
    weather = WeatherArgs.model_validate(args)
    return {"city": weather.city, "condition": "sunny"}

spec = ToolSpec("weather", WeatherArgs, fake_weather)
arguments = spec.args_model.model_validate({"city": "上海"})
result = spec.execute(arguments)
print(result)
print(spec.args_model.model_json_schema()["properties"].keys())
```

生产级注册器还应在注册时拒绝重复名称，在执行前检查用户权限、工具白名单、参数大小、超时和资源配额。对模型返回的结构化决策，推荐以下闭环：

1. 读取模型响应的 JSON 或 SDK 提供的结构化对象；
2. 用 `model_validate_json()`/`model_validate()` 校验结构和跨字段规则；
3. 校验动作名是否在本次请求允许的白名单；
4. 对路径、URL、SQL、表达式等高风险参数做业务安全检查；
5. 在有界超时与取消语义下执行工具；
6. 将工具结果裁剪、脱敏后通过 `model_dump(mode="json")` 反馈给 Agent。

校验失败时可以让模型重新生成，但要限制重试次数，并记录结构化错误类型而不是把完整内部 traceback 直接放进提示词。不要把“模型给出了正确 JSON”误认为“用户已经授权”或“工具操作安全”。

### 4.2 `dataclass` 与 `BaseModel` 决策矩阵

| 判断问题 | 更偏向 `dataclass` | 更偏向 Pydantic `BaseModel` |
| --- | --- | --- |
| 数据是否已经由内部代码构造？ | 是 | 否，来自 JSON/HTTP/环境变量/LLM |
| 是否需要类型转换和详细错误路径？ | 很少 | 是 |
| 是否要生成 JSON Schema？ | 通常不需要 | 工具/结构化输出通常需要 |
| 是否希望对象轻量、少依赖？ | 是 | 可接受运行时验证依赖 |
| 是否包含跨字段约束？ | 简单规则可用 `post_init` | 复杂规则用 `model_validator` |
| 是否需要严格拒绝未知字段？ | 需手写 | `extra="forbid"` 直接表达 |
| 是否是高频不可变值对象？ | `frozen`/`slots` 合适 | 可用，但需要评估验证开销 |
| 是否需要序列化给外部系统？ | 需自行定义协议 | 内置 dump/JSON Schema，更方便 |

两者可以组合：入口先用 Pydantic 验证 `ToolArgs`，应用层转换成不可变 `dataclass` 快照；不要在每一层反复把同一数据来回解析。

## 5. 常见坑与排查清单

1. **把标注当成运行时检查。** `def f(x: int)` 不会自动阻止字符串调用；边界数据需要 Pydantic 或显式校验。
2. **滥用 `Any` 和 `cast`。** 它们会隐藏错误；先定义最小协议或数据模型。
3. **可变默认值共享。** `dataclass` 用 `field(default_factory=list)`；Pydantic 用 `Field(default_factory=list)`。
4. **误解 `Optional`。** `str | None` 表示可为 `None`，不一定表示可以省略；默认值要显式写 `= None`。
5. **混淆 `TypedDict` 与 Pydantic。** 前者只在静态分析时有用，后者会在运行时构造和验证。
6. **`frozen=True` 不是深度不可变。** `frozen` 对象中的列表和字典仍可能被修改；需要不可变集合时使用 `tuple` 或不可变数据结构。
7. **`slots=True` 影响兼容性。** 某些序列化库、动态属性逻辑或继承写法可能依赖 `__dict__`，启用前先测试。
8. **协议运行时检查过于乐观。** `@runtime_checkable` 主要检查属性是否存在，不检查完整的类型签名。
9. **验证器有副作用。** 验证器可能被重复调用；不要在其中发邮件、写数据库或调用 LLM。
10. **默认接受未知字段。** 工具参数模型建议 `extra="forbid"`，否则模型多生成的字段可能被静默忽略，掩盖提示词或调用器 bug。
11. **只验证格式，不验证业务安全。** `url: str` 不等于允许访问任意 URL；仍需 SSRF 防护和域名策略。
12. **把秘密放进模型。** `model_dump()` 和异常信息可能被记录，敏感字段要显式脱敏或排除。

## 6. 练习题

1. 定义 `AgentEvent` 的 `TypedDict`，要求 `kind` 只能是 `"message"`、`"tool_call"`、`"tool_result"`，并让 `payload` 成为可选键。用静态检查器检查一个错误事件。
2. 编写一个 `Protocol`，描述 `VectorStore.search(query, top_k)` 能力；分别用内存实现和测试桩实现它，并说明为何不需要继承协议。
3. 创建泛型 `Result[T]`，补充 `ok(value)` 与 `fail(message)` 工厂函数；让静态检查器能推断 `Result[int]` 和 `Result[str]`。
4. 用 `dataclass(slots=True)` 实现 `RetryConfig`，包含次数、退避时间和抖动开关；在 `__post_init__` 中拒绝负数，并为列表字段正确使用 `default_factory`。
5. 写一个 Pydantic `ToolArgs`，字段包括查询词、分页大小和 `Literal` 排序方式；要求查询词去空白、页大小在合理范围、未知字段报错。
6. 定义一个嵌套的 `AgentResponse`，让 `citations` 使用子模型；分别演示 `model_validate()`、`model_dump()` 和 `model_dump_json()`。
7. 设计 `AgentDecision` 的校验规则：`action="final"` 必须有 `answer`，`action="tool"` 必须有工具名和参数，其他动作不能带多余字段。为每条规则写一个失败用例。
8. 写一个 `Settings`，从 `AGENT_` 前缀环境变量读取超时和调试开关；故意设置非法超时，观察 Pydantic 的错误路径和错误类型。
9. 对比 `dataclass` 和 Pydantic：给同一个 JSON 输入，分别构造对象，记录哪一个会把数字字符串转成整数、哪一个会接受未知字段。
10. 给工具参数加入 URL 字段。除了 Pydantic 的字符串校验，再设计域名白名单、超时和权限检查，并解释为什么“模型输出通过 Schema”仍然不够安全。

### 6.1 练习提示与验收标准

不要只追求“程序能跑”，每题至少提交一段类型清晰的实现和一个失败案例：

| 练习 | 提示 | 最低验收标准 |
| --- | --- | --- |
| 1 | 用 `Literal` 和 `NotRequired` 表达事件形状；再让静态检查器检查错误值 | 合法事件通过；错误 `kind` 在静态检查报告中出现；说明运行时为何仍需验证 |
| 2 | 定义最小 `Protocol`，内存实现和桩实现只需满足方法签名 | `answer()` 不依赖具体实现类；两个实现都能被测试替换 |
| 3 | 让 `Result[T]` 的成功和失败状态有清晰不变量，考虑 `T | None` | `Result[int]`/`Result[str]` 的返回类型可被推断；空结果不会被静默当成功 |
| 4 | `__post_init__` 做边界检查，列表字段只使用工厂 | 两个实例的列表互不共享；非法次数/退避时间抛明确异常 |
| 5 | `Field` 写范围，`extra="forbid"` 拒绝未知键，验证器只做纯逻辑 | 空查询、越界页大小、未知字段各有一个失败用例 |
| 6 | 先构造子模型，再调用父模型的 `model_validate` 和 dump API | JSON 往返结果等价；输出不包含未声明内部字段 |
| 7 | 用判别字段或 `model_validator` 表达动作之间的互斥规则 | 每条规则各有成功/失败测试；错误位置和信息可定位 |
| 8 | 为环境变量准备干净的 monkeypatch；确认 `BaseSettings` 的前缀 | 合法值被解析为目标类型；非法值失败且不会泄露秘密 |
| 9 | 对同一字典分别用 dataclass 构造和 Pydantic 校验 | 写下转换、未知字段和缺失字段的差异，不用“看起来一样”下结论 |
| 10 | Schema 只校验形状，白名单/权限/超时属于执行前策略 | 对非法域名和未授权用户拒绝执行；测试证明 Schema 通过仍可能被策略拦截 |

## 小结

- 类型标注是静态契约，不是运行时安全边界；`Any`、`cast` 和 `TypedDict` 都不会替你验证外部数据。
- `Protocol` 适合 Agent 组件的能力抽象，泛型适合复用容器和结果类型，`Literal` 适合有限状态和动作集合。
- `dataclass` 适合内部领域对象；可变默认值必须用 `default_factory`，`frozen` 和 `slots` 要根据使用方式选择。
- Pydantic v2 适合请求、配置、模型 JSON 和工具参数：用 `Field`、验证器、嵌套模型、`extra="forbid"` 构建明确边界，用 `model_dump`/`model_validate` 做序列化与反序列化。
- Agent 的结构化输出流程应是“解析 → 运行时校验 → 授权/安全检查 → 执行”，Schema 正确不等于操作安全。
