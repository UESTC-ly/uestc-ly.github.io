# 07. NumPy 与 Pandas 基础

## 学习目标

完成本章后，你应该能够：

- 解释 NumPy 数组与 Python 列表的核心区别；
- 创建、索引、变形和批量计算多维数组；
- 理解 `shape`、`dtype`、轴、广播、视图与副本；
- 用 Pandas 的 `Series` 和 `DataFrame` 读取、筛选、清洗、聚合和连接表格数据；
- 对缺失值、重复值、时间列和类别列进行基本处理；
- 分析 Agent 日志、评测数据和向量相似度；
- 知道什么时候不应该使用 NumPy/Pandas。

安装：

```bash
python -m pip install numpy pandas
```

如果项目使用 `uv`：

```bash
uv add numpy pandas
```

本章中的完整示例会包含导入和输入构造；紧跟完整示例的短代码块用于继续演示同一变量，需与上一个代码块在同一 Python 会话中执行。

## 1. 两个库分别解决什么问题

NumPy 的核心是同质、多维数组 `ndarray`，擅长批量数值计算。Pandas 建立在 NumPy 等数组能力之上，核心是带标签的一维 `Series` 和二维 `DataFrame`，擅长表格数据处理。

| 场景 | 首选 |
|---|---|
| 向量、矩阵、数值批处理 | NumPy |
| CSV、日志、评测表、缺失值、分组统计 | Pandas |
| 少量异构业务对象 | Python 列表/字典/dataclass |
| 超大数据或分布式查询 | 数据库、Polars、DuckDB、Spark 等，按需求评估 |

AI Agent 常见用途包括：

- 计算嵌入向量的余弦相似度；
- 整理工具调用记录；
- 计算准确率、成功率、成本和延迟分位数；
- 清洗问答评测集；
- 比较不同提示词或模型版本的实验结果。

它们通常用于 Agent 的数据与评测层，不负责 Agent 的控制循环。

### 1.1 从 Python 对象到分析表

三种数据表示各有边界：

```text
业务对象层                 数值计算层                  表格分析层
Message / ToolCall   →    ndarray              →    DataFrame
类型可异构、语义明确        同质、紧凑、按轴计算          带列名、索引、缺失值语义
```

- 运行中的一条工具调用适合 Pydantic 模型或 dataclass；
- 成千上万条向量适合 NumPy 数组；
- 成千上万条运行记录适合 Pandas DataFrame；
- 长期持久化和并发查询仍应交给文件格式、数据库或数据仓库。

不要为了使用 Pandas 而在 API 请求处理中不断把单个对象转换为一行 DataFrame。转换本身有成本，而且 DataFrame 不是事务数据库。

### 1.2 先问数据形状，再写代码

开始计算前写清楚：

```text
query_embedding:       (embedding_dim,)
document_embeddings:  (document_count, embedding_dim)
similarity_scores:     (document_count,)
```

对表格则写清楚“一行代表什么”和“哪一列唯一”：

```text
一行 = 一次工具调用
唯一键 = call_id
run_id 可以重复，因为一次运行可调用多个工具
```

很多数组广播错误和表格重复错误，本质上都是没有先定义形状与粒度。

---

## 2. NumPy 数组基础

### 2.1 数组与列表的区别

Python 列表可以混合存放不同类型，元素通常是对象引用；NumPy 数组通常使用一个统一 `dtype`，数据以适合批量计算的方式存储。

```python
import numpy as np

python_values = [1, 2, 3]
array = np.array([1, 2, 3], dtype=np.int64)

print(array)
print(array.shape)  # (3,)
print(array.dtype)  # 通常为 int64，具体默认值受平台影响
print(array.ndim)   # 1
print(array.size)   # 3
```

`ndarray` 可以理解为“数据缓冲区 + 解释缓冲区的元数据”。关键元数据包括：

- `shape`：每个轴有多少元素；
- `dtype`：一个元素占多少字节、如何解释这些字节；
- `strides`：沿每个轴移动一步需要跨过多少字节；
- `ndim`：轴的数量；
- `size`：元素总数。

```python
import numpy as np

matrix = np.arange(6, dtype=np.int32).reshape(2, 3)
print(matrix.shape)    # (2, 3)
print(matrix.strides)  # 常见输出为 (12, 4)：换一行跨 12 字节，换一列跨 4 字节
print(matrix.nbytes)   # 24：6 个 int32
```

`strides` 的具体数字与内存布局、类型大小有关，不应作为跨平台业务契约。理解它的作用是知道转置和切片可能只改变“看数据的方式”，并未复制全部数据。

列表的 `*` 是重复，数组的 `*` 是逐元素乘法：

```python
print([1, 2, 3] * 2)              # [1, 2, 3, 1, 2, 3]
print(np.array([1, 2, 3]) * 2)    # [2 4 6]
```

### 2.2 常用创建方式

```python
import numpy as np

a = np.array([1.0, 2.0, 3.0])
zeros = np.zeros((2, 3))
ones = np.ones((2, 2), dtype=np.float32)
sequence = np.arange(0, 10, 2)       # [0 2 4 6 8]
samples = np.linspace(0, 1, 5)       # 包含端点的 5 个等距数
identity = np.eye(3)

rng = np.random.default_rng(seed=42)
random_values = rng.normal(loc=0.0, scale=1.0, size=(2, 3))
```

需要可复现实验时，创建局部随机数生成器并设置种子；不要在大型项目各处反复修改全局随机状态。

常用创建函数的选择：

| 函数 | 语义 | 常见用途 |
|---|---|---|
| `np.array(data)` | 从现有数据构造 | 把列表/元组转为数组 |
| `np.asarray(data)` | 尽量避免不必要复制 | 接受“数组或类似数组”的函数边界 |
| `zeros/ones/full` | 用固定值初始化 | 掩码、计数器、默认矩阵 |
| `arange` | 按步长生成 | 整数索引；浮点步长可能积累误差 |
| `linspace` | 按数量生成等距点 | 需要明确包含端点的采样 |
| `empty` | 只分配内存、不初始化 | 会立即覆盖所有元素的性能敏感代码 |

`np.empty` 中的值是未定义旧内存内容，读取后再决定是否覆盖属于错误用法。

### 2.3 `shape`、维度和轴

```python
matrix = np.array(
    [
        [10, 20, 30],
        [40, 50, 60],
    ]
)

print(matrix.shape)  # (2, 3)：2 行，3 列
print(matrix.ndim)   # 2
```

“轴”是聚合时最容易混淆的概念：

```python
print(matrix.sum())         # 210，所有元素
print(matrix.sum(axis=0))   # [50 70 90]，压缩行，得到每列和
print(matrix.sum(axis=1))   # [ 60 150]，压缩列，得到每行和
```

记忆方式不是死记“0 是列、1 是行”，而是：`axis=n` 表示该轴在结果中被消掉。

再看一个三维例子。若形状为 `(batch, item, feature) = (2, 3, 4)`：

- `sum(axis=0)` 消掉 batch，结果形状 `(3, 4)`；
- `sum(axis=1)` 消掉 item，结果形状 `(2, 4)`；
- `sum(axis=2)` 消掉 feature，结果形状 `(2, 3)`；
- `sum(axis=(0, 1))` 同时消掉两个轴，结果形状 `(4,)`。

```python
import numpy as np

batch = np.ones((2, 3, 4))
print(batch.sum(axis=0).shape)       # (3, 4)
print(batch.sum(axis=1).shape)       # (2, 4)
print(batch.sum(axis=(0, 1)).shape)  # (4,)
```

在 Agent 评测中，可以把维度命名写进变量名或注释，避免把“案例轴”和“模型版本轴”聚合反了。

### 2.4 `dtype` 与类型转换

```python
import numpy as np

scores = np.array([1, 2, 3], dtype=np.int32)
float_scores = scores.astype(np.float64)

print(float_scores)        # [1. 2. 3.]
print(float_scores.dtype)  # float64
```

注意：

- 整数数组使用真除法 `/` 时通常会产生浮点结果，而 `//` 表示向下取整除法；
- 低精度类型更省内存，但可能损失范围或精度；
- 字符串混入数值序列可能让整个数组变成字符串类型；
- `astype` 默认返回新数组，转换失败会抛出异常。

不要为了“省内存”盲目改类型，应结合数值范围、精度和下游库要求。

#### 整数溢出与浮点精度

固定宽度类型不会像 Python `int` 一样自动扩展：

```python
import numpy as np

value = np.array([127], dtype=np.int8)
print(value + np.array([1], dtype=np.int8))  # [-128]，发生溢出

a = np.array([0.1, 0.2], dtype=np.float64)
print(a.sum() == 0.3)              # 可能为 False
print(np.isclose(a.sum(), 0.3))    # True
```

浮点比较通常使用 `np.isclose` / `np.allclose` 并根据业务精度设置容差。金额最好使用最小货币单位的整数或 `decimal.Decimal`，不要默认用二进制浮点做精确财务结算。

---

## 3. 索引、切片与布尔筛选

### 3.1 基本索引

```python
values = np.array([10, 20, 30, 40, 50])

print(values[0])       # 10
print(values[-1])      # 50
print(values[1:4])     # [20 30 40]
print(values[::2])     # [10 30 50]
```

二维数组可以一次提供多个轴的索引：

```python
matrix = np.array([[1, 2, 3], [4, 5, 6]])

print(matrix[1, 2])    # 6
print(matrix[:, 1])    # [2 5]，所有行的第 2 列
print(matrix[0, :])    # [1 2 3]，第 1 行
```

### 3.2 布尔掩码

```python
latencies_ms = np.array([120, 850, 300, 1_200, 95])
slow_mask = latencies_ms > 500

print(slow_mask)                 # [False  True False  True False]
print(latencies_ms[slow_mask])   # [ 850 1200]
```

组合条件时，每个条件要加括号，并使用 `&`、`|`、`~`：

```python
selected = latencies_ms[(latencies_ms >= 100) & (latencies_ms <= 900)]
print(selected)  # [120 850 300]
```

不能写成 `and`，因为 `and` 处理单个布尔值，不能逐元素组合数组。

### 3.3 花式索引

```python
values = np.array([10, 20, 30, 40])
print(values[[3, 0, 0]])  # [40 10 10]
```

使用整数数组或布尔数组的花式索引通常返回副本；普通切片通常返回视图。这会影响修改行为和内存。

基本索引、布尔索引和花式索引的区别：

| 写法 | 选择依据 | 常见返回语义 |
|---|---|---|
| `a[1:4]` | 连续位置范围 | 通常是共享数据的视图 |
| `a[a > 0]` | 条件 | 新数组 |
| `a[[3, 0, 0]]` | 任意位置列表 | 新数组，可重排和重复 |

条件替换可以直接赋值，也可以用 `np.where` 构造新结果：

```python
import numpy as np

scores = np.array([0.2, 0.8, 0.4])
labels = np.where(scores >= 0.5, "pass", "fail")
print(labels)  # ['fail' 'pass' 'fail']
```

`np.where` 的两个分支都可能先参与数组构造，不应把具有副作用或昂贵网络请求的函数放在分支表达式里。

---

## 4. 视图、副本与变形

### 4.1 切片通常共享数据

```python
source = np.array([1, 2, 3, 4])
view = source[1:3]
view[0] = 99

print(source)  # [ 1 99  3  4]
```

如果需要隔离修改，显式复制：

```python
source = np.array([1, 2, 3, 4])
independent = source[1:3].copy()
independent[0] = 99

print(source)  # [1 2 3 4]
```

调试共享内存时可以使用：

```python
import numpy as np

source = np.arange(6)
view = source[::2]
copy = source[[0, 2, 4]]

print(np.shares_memory(source, view))  # True
print(np.shares_memory(source, copy))  # False
```

函数如果会原地修改数组，应在名称、文档和类型约定中明确说明。对公共 API，更安全的默认通常是返回新结果；性能敏感处再提供显式 `inplace` 或输出缓冲区方案。

### 4.2 改变形状

```python
values = np.arange(12)
matrix = values.reshape(3, 4)
flat = matrix.ravel()

print(matrix)
# [[ 0  1  2  3]
#  [ 4  5  6  7]
#  [ 8  9 10 11]]
print(flat.shape)  # (12,)
```

`-1` 可以让 NumPy 推断一个维度：

```python
batch = np.arange(24).reshape(2, 3, -1)
print(batch.shape)  # (2, 3, 4)
```

常用组合：

```python
a = np.array([[1, 2], [3, 4]])
b = np.array([[5, 6]])

rows = np.concatenate([a, b], axis=0)
columns = np.concatenate([a, np.array([[7], [8]])], axis=1)
stacked = np.stack([a, a], axis=0)

print(rows.shape)     # (3, 2)
print(columns.shape)  # (2, 3)
print(stacked.shape)  # (2, 2, 2)，新增了一个轴
```

`concatenate` 沿已有轴连接，`stack` 新增轴。

转置不会“交换数据含义”，只会交换轴：

```python
import numpy as np

matrix = np.arange(6).reshape(2, 3)
transposed = matrix.T
print(transposed.shape)  # (3, 2)
```

如果原来的轴代表 `(document, feature)`，转置后就是 `(feature, document)`。在矩阵乘法前检查含义而不是只检查形状能否相乘。

---

## 5. 向量化与广播

### 5.1 向量化

“向量化”指把逐元素的 Python 循环表达为数组运算：

```python
latencies_ms = np.array([100.0, 250.0, 400.0])
latencies_s = latencies_ms / 1_000
normalized = (latencies_ms - latencies_ms.mean()) / latencies_ms.std()

print(latencies_s)
print(normalized)
```

它通常更简洁，也能利用底层优化。但不要把所有逻辑强行变成难懂的数组技巧；可读性和正确性优先。

NumPy 的逐元素函数常称为 ufunc，例如 `np.add`、`np.exp`、`np.maximum`。它们支持按元素计算、广播和可选输出缓冲区：

```python
import numpy as np

logits = np.array([-1.0, 0.0, 1.0])
probabilities = 1 / (1 + np.exp(-logits))
print(probabilities)
```

向量化减少的是 Python 层循环开销，不等于算法复杂度自动降低。对一百万个向量做全量比较仍是大计算，只是每步执行更高效。

### 5.2 广播规则

广播允许不同形状的数组进行逐元素运算。比较形状时从最右侧开始，每一维必须：

- 相等；或
- 其中一个为 1；或
- 其中一个不存在。

```python
matrix = np.array([[1, 2, 3], [4, 5, 6]])  # (2, 3)
offset = np.array([10, 20, 30])             # (3,)

print(matrix + offset)
# [[11 22 33]
#  [14 25 36]]
```

给每一行除以自己的和，需要保留被压缩的维度：

```python
weights = np.array([[1.0, 2.0], [3.0, 1.0]])
row_sums = weights.sum(axis=1, keepdims=True)  # shape: (2, 1)
normalized = weights / row_sums

print(normalized)
# [[0.33333333 0.66666667]
#  [0.75       0.25      ]]
```

广播不会自动理解业务含义。形状“恰好能算”不代表逻辑正确，关键数组应通过断言或类型/测试验证形状。

#### 手工判断广播

从最右边对齐形状：

```text
(8, 1, 4)
   (3, 4)
-----------
(8, 3, 4)   # 1 可扩展成 3，缺失的最左维可视为 1
```

而 `(8, 2, 4)` 与 `(3, 4)` 不兼容，因为倒数第二维 2 和 3 既不相等，也没有一个为 1。遇到错误时先打印形状，而不是随意增加 `reshape`：

```python
assert documents.shape[1] == query.shape[0], (
    f"embedding 维度不一致: {documents.shape=} {query.shape=}"
)
```

---

## 6. 聚合、排序和缺失数值

```python
values = np.array([3.0, 1.0, 8.0, 2.0])

print(values.min())
print(values.max())
print(values.mean())
print(np.median(values))
print(np.percentile(values, 95))
print(np.sort(values))
print(np.argsort(values))  # 返回排序后的原位置索引
```

浮点缺失值常用 `np.nan`：

```python
values = np.array([1.0, np.nan, 3.0])

print(values.mean())      # nan
print(np.nanmean(values)) # 2.0
print(np.isnan(values))   # [False  True False]
```

不能用 `values == np.nan` 判断缺失值，因为 NaN 与自身也不相等。缺失数据是否应该忽略、填补还是报错是业务决策，不能只是换用 `nanmean` 就结束。

排序和聚合还要考虑：

- 空数组的某些聚合没有定义，会产生警告或异常；
- 百分位数是样本描述，不是性能承诺；
- 极端值会显著影响平均数，中位数更稳健但也会丢失尾部信息；
- 多次对同一大数组排序成本高，Top-K 可考虑 `np.argpartition`。

```python
import numpy as np

scores = np.array([0.2, 0.9, 0.1, 0.8, 0.7])
k = 2
candidate_indices = np.argpartition(scores, -k)[-k:]
top_indices = candidate_indices[np.argsort(scores[candidate_indices])[::-1]]
print(top_indices)  # [1 3]
```

`argpartition` 只保证分区，不保证分区内部有序，所以最后仍需对候选项排序。

---

## 7. Agent 场景：余弦相似度

嵌入模型通常把文本映射为向量。余弦相似度比较向量方向：

```python
import numpy as np
import numpy.typing as npt


def cosine_similarity(
    query: npt.NDArray[np.float64],
    documents: npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]:
    """计算一个查询向量与多条文档向量的余弦相似度。"""
    if query.ndim != 1:
        raise ValueError("query 必须是一维向量")
    if documents.ndim != 2:
        raise ValueError("documents 必须是二维矩阵")
    if documents.shape[1] != query.shape[0]:
        raise ValueError("向量维度不一致")

    query_norm = np.linalg.norm(query)
    document_norms = np.linalg.norm(documents, axis=1)
    if query_norm == 0 or np.any(document_norms == 0):
        raise ValueError("零向量没有定义良好的余弦相似度")

    return (documents @ query) / (document_norms * query_norm)


query = np.array([1.0, 0.0, 1.0])
documents = np.array(
    [
        [1.0, 0.0, 1.0],
        [0.0, 1.0, 0.0],
        [1.0, 1.0, 0.0],
    ]
)

scores = cosine_similarity(query, documents)
top_indices = np.argsort(scores)[::-1]
print(scores)
print(top_indices)
```

真实检索系统还需考虑：向量归一化、批量大小、索引结构、元数据过滤、距离度量与模型版本。数据量较大时应使用专门的向量索引，而不是每次对全部向量做 NumPy 全量扫描。

### 7.1 为什么余弦相似度要检查零向量

公式为：

```text
cos(q, d) = (q · d) / (||q|| × ||d||)
```

点积衡量同方向成分，范数把向量长度归一化。零向量的范数为 0，分母也为 0，因此不能给出有意义的方向相似度。静默加一个很小的 epsilon 虽能避免除零，却可能把上游坏数据伪装成合法分数；是否这样处理必须是显式产品决策。

如果所有文档向量已提前归一化为单位长度，查询也在请求时归一化，余弦相似度就可以简化为矩阵乘法 `documents @ query`。这能减少重复计算，但需要在写入索引时验证归一化不变量。

---

## 8. Pandas 核心对象

### 8.1 `Series`

`Series` 是带索引的一维数据：

```python
import pandas as pd

latency = pd.Series(
    [120, 340, 210],
    index=["search", "calculator", "weather"],
    name="latency_ms",
)

print(latency["search"])  # 120
print(latency.mean())
```

索引不是普通“行号”。Series 运算默认按索引标签对齐：

```python
import pandas as pd

left = pd.Series([1, 2], index=["a", "b"])
right = pd.Series([10, 20], index=["b", "c"])
print(left + right)
# a     NaN
# b    12.0
# c     NaN
```

这对时间序列和业务主键很有用，但也可能产生意外缺失值。若业务要求按位置计算，先确认长度并使用 NumPy 数组；若要求按键计算，显式检查索引集合。

### 8.2 `DataFrame`

`DataFrame` 是带行列标签的二维表：

```python
import pandas as pd

calls = pd.DataFrame(
    {
        "tool": ["search", "calculator", "search"],
        "latency_ms": [320, 15, 450],
        "success": [True, True, False],
    }
)

print(calls)
print(calls.shape)   # (3, 3)
print(calls.dtypes)
print(calls.head())
print(calls.info())
```

`info()` 直接打印摘要并返回 `None`，不要误以为它返回一个新的 DataFrame。

### 8.3 列类型决定可用操作

Pandas 新代码常见类型包括：

| 类型 | 示例 | 说明 |
|---|---|---|
| `int64` / `float64` | 延迟、分数 | NumPy 固定宽度数值；传统整数不能表示缺失 |
| `Int64` / `boolean` | 可缺失计数、状态 | Pandas 可空扩展类型，注意大小写 |
| `string` | 工具名、错误码 | 统一字符串操作和 `pd.NA` |
| `category` | 少量重复类别 | 用编码存储类别，适合低基数列 |
| `datetime64[ns, UTC]` | 请求时间 | 带时区时间，便于窗口分析 |

读取后先看 `df.info()` 和关键列取值范围，再开始统计。`object` 往往意味着列里混入多种 Python 对象，需要进一步检查。

---

## 9. 读取与写出数据

### 9.1 CSV

```python
import pandas as pd

df = pd.read_csv(
    "agent_calls.csv",
    usecols=["timestamp", "tool", "latency_ms", "success"],
    parse_dates=["timestamp"],
)

df.to_csv("agent_calls_clean.csv", index=False)
```

明确指定列和日期解析通常比读完再修正更可靠。面对大文件可以考虑：

- `usecols` 只读所需列；
- `dtype` 指定类型；
- `chunksize` 分块处理；
- 使用 Parquet 保留更丰富的类型并提高分析效率。

### 9.2 JSON 与 JSON Lines

普通 JSON 可能是一个数组；JSON Lines 通常每行一个对象，更适合流式日志：

```python
df = pd.read_json("runs.jsonl", lines=True)
df.to_json("runs_clean.jsonl", orient="records", lines=True, force_ascii=False)
```

如果记录中有嵌套对象，可以使用 `pd.json_normalize`：

```python
records = [
    {"run_id": "r1", "usage": {"input_tokens": 100, "output_tokens": 20}},
    {"run_id": "r2", "usage": {"input_tokens": 80, "output_tokens": 30}},
]

usage = pd.json_normalize(records)
print(usage.columns.tolist())
# ['run_id', 'usage.input_tokens', 'usage.output_tokens']
```

不要把未知深度的任意模型输出直接扁平化后当成稳定表结构；先定义数据契约和版本。

### 9.3 读取时就控制 schema

先读取再“猜类型”容易让脏数据传播。CSV 没有可靠类型元数据，可以明确指定：

```python
import pandas as pd

schema = {
    "call_id": "string",
    "run_id": "string",
    "tool": "string",
    "success": "boolean",
}

calls = pd.read_csv(
    "agent_calls.csv",
    dtype=schema,
    parse_dates=["timestamp"],
    na_values=["", "null", "N/A"],
)
```

这段示例假设文件存在。`dtype` 不能替代完整业务验证，例如负延迟在类型上仍是合法数字。生产管道应在读取后检查：必需列、唯一键、允许值、数值范围和时间范围。

### 9.4 分块与 Parquet

文件大于可用内存时可以分块：

```python
import pandas as pd

total_failures = 0
for chunk in pd.read_csv("agent_calls.csv", chunksize=100_000):
    total_failures += (~chunk["success"].astype("boolean")).sum()

print(total_failures)
```

分块聚合必须能组合局部结果。总数和求和容易组合，精确中位数不能简单对“各块中位数”再取中位数。

Parquet 是列式格式，通常比 CSV 更好地保留类型，并支持只读部分列。但它仍不是数据质量保证；写入前应固定 schema，跨版本变更要记录迁移策略。

---

## 10. 选择列、筛选行与赋值

```python
import pandas as pd

df = pd.DataFrame(
    {
        "tool": ["search", "weather", "search", "calculator"],
        "latency_ms": [500, 120, 900, 10],
        "success": [True, True, False, True],
    }
)

tool_series = df["tool"]
subset = df[["tool", "latency_ms"]]
slow_failures = df[(df["latency_ms"] > 400) & (~df["success"])]

print(tool_series)
print(subset)
print(slow_failures)
```

### 10.1 `loc` 与 `iloc`

- `loc` 按标签选择；
- `iloc` 按整数位置选择。

```python
print(df.loc[0, "tool"])
print(df.loc[df["success"], ["tool", "latency_ms"]])
print(df.iloc[:2, :2])
```

两者切片端点语义不同：标签切片 `loc["a":"c"]` 通常包含结束标签，位置切片 `iloc[0:3]` 遵守 Python 规则、不含位置 3。默认整数索引恰好同时像标签和位置，最容易造成混淆，因此应明确选择 `.loc` 或 `.iloc`。

选择单个标量时还可用 `.at[label, column]` / `.iat[position, column]`，语义更明确；批量代码仍以 `.loc` / `.iloc` 为主。

### 10.2 安全赋值

```python
df.loc[df["latency_ms"] > 400, "speed_class"] = "slow"
df.loc[df["latency_ms"] <= 400, "speed_class"] = "normal"
```

避免链式赋值：

```python
# 不推荐：中间结果可能是视图或副本，语义含糊
# df[df["latency_ms"] > 400]["speed_class"] = "slow"
```

需要独立子表时显式 `.copy()`：

```python
failures = df.loc[~df["success"]].copy()
failures["needs_review"] = True
```

可以用 `assign` 构造新列并保持方法链：

```python
import pandas as pd

calls = pd.DataFrame({"latency_ms": [100, 600], "success": [True, False]})
enriched = calls.assign(
    latency_s=lambda frame: frame["latency_ms"] / 1_000,
    needs_review=lambda frame: (~frame["success"]) | (frame["latency_ms"] > 500),
)
print(enriched)
```

方法链能让数据流从上到下阅读，但一条链过长会难以调试。可在关键质量检查处命名中间表，而不是追求“一行完成”。

---

## 11. 清洗数据

### 11.1 缺失值

```python
import pandas as pd

df = pd.DataFrame(
    {
        "tool": ["search", None, "weather"],
        "latency_ms": [120.0, None, 200.0],
    }
)

print(df.isna().sum())

without_unknown_tool = df.dropna(subset=["tool"])
filled = df.assign(latency_ms=df["latency_ms"].fillna(df["latency_ms"].median()))
```

填补策略必须有语义：缺失耗时填 0 会错误暗示“瞬间完成”；缺失成功状态也不等于失败。必要时保留“未知”这一类别。

#### `None`、`NaN` 与 `pd.NA`

- `None` 是 Python 对象；
- `np.nan` 是特殊浮点值，传统上用于浮点缺失；
- `pd.NA` 是 Pandas 可空类型的统一缺失标记。

`pd.NA` 的真假值是含糊的：

```python
import pandas as pd

status = pd.Series([True, False, pd.NA], dtype="boolean")
print(status.isna())
print(status.fillna(False))
```

把未知状态填为 `False` 等价于把“未知”解释为“失败”，必须由业务规则决定。质量报告通常应单独统计未知数量。

### 11.2 重复值

```python
import pandas as pd

events = pd.DataFrame(
    {
        "run_id": ["r1", "r1", "r2"],
        "timestamp": pd.to_datetime(
            ["2026-08-31T08:00:00Z", "2026-08-31T08:05:00Z", "2026-08-31T09:00:00Z"],
            utc=True,
        ),
    }
)

deduplicated = events.drop_duplicates()
latest_per_run = events.sort_values("timestamp").drop_duplicates(
    subset=["run_id"],
    keep="last",
)
```

第二段假设存在名为 `events` 的 DataFrame。去重前先定义“重复”的业务键；整行相同和同一个 `run_id` 不是同一概念。

去重前建议先观察重复：

```python
duplicate_mask = events.duplicated(subset=["run_id"], keep=False)
print(events.loc[duplicate_mask].sort_values(["run_id", "timestamp"]))
```

`keep="last"` 只有在排序字段可靠、时间精度足够并且时区一致时才表示“最新”。分布式事件可能乱序，还可能需要版本号或摄取序号作为决胜字段。

### 11.3 字符串

```python
tools = pd.Series([" Search ", "WEATHER", None], dtype="string")
normalized = tools.str.strip().str.lower()
print(normalized)
```

Pandas 的 `string` 类型能更明确地表达可缺失文本，通常比混合对象类型更适合新代码。

`.str` 方法通常保留缺失值并进行向量化表达：

```python
import pandas as pd

errors = pd.Series(["Timeout: search", "Validation: query", pd.NA], dtype="string")
error_type = errors.str.extract(r"^(?P<type>[^:]+)")["type"].str.lower()
print(error_type)
```

正则表达式处理外部超长文本时要关注性能和输入上限；简单前缀/分隔符优先使用直接字符串方法。

### 11.4 日期时间

```python
events = pd.DataFrame(
    {"timestamp": ["2026-08-31T08:00:00Z", "2026-08-31T08:00:03Z"]}
)
events["timestamp"] = pd.to_datetime(events["timestamp"], utc=True)
events["minute"] = events["timestamp"].dt.floor("min")
```

日志系统建议在存储层使用带时区时间，常见做法是统一 UTC，在展示层转换成本地时间。不要把无时区和有时区的时间混合计算。

按时间窗口聚合：

```python
import pandas as pd

events = pd.DataFrame(
    {
        "timestamp": pd.to_datetime(
            ["2026-08-31T08:00:00Z", "2026-08-31T08:00:40Z", "2026-08-31T08:01:10Z"],
            utc=True,
        ),
        "latency_ms": [100, 200, 300],
    }
)

per_minute = events.set_index("timestamp").resample("1min")["latency_ms"].mean()
print(per_minute)
```

窗口边界、时区和空窗口处理会影响监控图，应在报表定义中明确。

### 11.5 类型转换

```python
raw = pd.Series(["10", "bad", "30"])
numeric = pd.to_numeric(raw, errors="coerce")
print(numeric)  # bad 变为 NaN
```

`errors="coerce"` 很方便，也可能隐藏上游数据损坏。应统计转换失败数量并设置质量阈值，而不是静默丢弃。

```python
invalid_mask = numeric.isna() & raw.notna()
if invalid_mask.any():
    print("无法解析的原始值:", raw[invalid_mask].tolist())
```

记录少量脱敏样本有助于排查，但不要把包含隐私或密钥的完整原始行写入普通日志。

---

## 12. 排序、分组和聚合

```python
import pandas as pd

calls = pd.DataFrame(
    {
        "tool": ["search", "search", "weather", "weather"],
        "latency_ms": [300, 900, 100, 150],
        "success": [True, False, True, True],
    }
)

sorted_calls = calls.sort_values("latency_ms", ascending=False)

summary = (
    calls.groupby("tool", as_index=False)
    .agg(
        calls=("tool", "size"),
        success_rate=("success", "mean"),
        avg_latency_ms=("latency_ms", "mean"),
        p95_latency_ms=("latency_ms", lambda s: s.quantile(0.95)),
    )
    .sort_values("p95_latency_ms", ascending=False)
)

print(summary)
```

`groupby` 常被描述为 split–apply–combine：

1. split：按键把行划分为组；
2. apply：对每组计算计数、均值或自定义统计；
3. combine：把各组结果组合成新表。

默认情况下，缺失分组键可能被排除。需要把缺失工具名作为单独组时显式设置并命名未知值：

```python
safe_calls = calls.assign(tool=calls["tool"].fillna("<unknown>"))
counts = safe_calls.groupby("tool", as_index=False, dropna=False).size()
```

自定义 `lambda` 灵活但可能较慢；常用聚合优先使用内置字符串函数。

布尔值的平均值可表达成功率，因为 `True`/`False` 在数值上下文可对应 1/0。为了让读者理解，输出列应命名为 `success_rate`，而不是含糊的 `success_mean`。

### 12.1 `transform` 与 `agg`

- `agg` 通常减少行数，产生组级摘要；
- `transform` 返回与原数据等长的结果，适合组内标准化或回填组统计。

```python
calls["tool_avg_latency"] = calls.groupby("tool")["latency_ms"].transform("mean")
calls["relative_latency"] = calls["latency_ms"] / calls["tool_avg_latency"]
```

### 12.2 透视表与交叉表

比较多个维度时可使用透视表：

```python
import pandas as pd

runs = pd.DataFrame(
    {
        "model": ["a", "a", "b", "b"],
        "category": ["math", "search", "math", "search"],
        "score": [0.8, 0.7, 0.9, 0.6],
    }
)

pivot = runs.pivot_table(
    index="model",
    columns="category",
    values="score",
    aggfunc="mean",
)
print(pivot)
```

透视后的宽表适合展示，长表通常更适合存储、筛选和绘图。若同一个行列组合有多条记录，`pivot` 会报错，而 `pivot_table` 要求你明确聚合函数。

---

## 13. 合并表格

### 13.1 `merge`

```python
runs = pd.DataFrame(
    {
        "run_id": ["r1", "r2"],
        "agent_version": ["v1", "v2"],
    }
)

scores = pd.DataFrame(
    {
        "run_id": ["r1", "r2"],
        "quality_score": [0.8, 0.9],
    }
)

report = runs.merge(scores, on="run_id", how="left", validate="one_to_one")
```

`validate` 可以发现意外的多对多合并，否则行数可能无声膨胀。常用值包括 `one_to_one`、`one_to_many`、`many_to_one`。

连接前先写基数假设：

```text
runs.run_id：唯一
scores.run_id：唯一
期望：one_to_one
```

连接后检查未匹配键：

```python
checked = runs.merge(scores, on="run_id", how="outer", indicator=True, validate="one_to_one")
print(checked["_merge"].value_counts())
```

确认质量后再删除 `_merge`。空值键的匹配语义可能与数据库不同，关键连接键应在合并前处理缺失。

### 13.2 `concat`

```python
week_1 = pd.DataFrame({"run_id": ["r1"]})
week_2 = pd.DataFrame({"run_id": ["r2"]})
all_runs = pd.concat([week_1, week_2], ignore_index=True)
```

`concat` 更像按轴拼接，`merge` 更像数据库按键连接。

纵向拼接前应统一列和类型。若两个批次同名列分别是整数和字符串，结果可能退化为 `object`，后续聚合才暴露问题。

---

## 14. `apply` 不是第一选择

很多初学者把任意 Python 函数放入 `DataFrame.apply`。先寻找内置向量化表达：

```python
import numpy as np
import pandas as pd

df = pd.DataFrame(
    {
        "tool": [" Search ", "WEATHER"],
        "latency_ms": [500, 120],
    }
)

# 推荐：直接使用向量化字符串操作
df["tool"] = df["tool"].str.strip().str.lower()

# 简单条件也可使用向量化选择
import numpy as np
df["speed"] = np.where(df["latency_ms"] > 400, "slow", "normal")
```

`apply` 适合无法直接表达且数据规模可控的复杂行/列逻辑，但它不是自动高性能。若每行需要发网络请求，更不要把请求隐藏在 `apply` 中；显式设计批处理、限流、重试和异步边界。

选择顺序可以是：

1. 直接列运算或 `.str` / `.dt` 方法；
2. `map` 对单列做值映射；
3. `groupby().transform/agg`；
4. 数据规模可控且确实无法向量化时再用 `apply`；
5. 外部 I/O 移出 DataFrame 变换，建立明确任务调度。

`axis=1` 的行级 `apply` 会为每行构造 Series，通常比列运算慢，也更容易产生混合类型。

---

## 15. Agent 场景：分析运行日志

下面的例子从内存记录构建评测报告，真实项目可以换成 `read_json(..., lines=True)`：

```python
from __future__ import annotations

import pandas as pd


def build_tool_report(records: list[dict[str, object]]) -> pd.DataFrame:
    required = {"call_id", "run_id", "tool", "latency_ms", "success", "cost_usd"}
    frame = pd.DataFrame.from_records(records)

    missing_columns = required - set(frame.columns)
    if missing_columns:
        raise ValueError(f"缺少列: {sorted(missing_columns)}")

    frame = frame.copy()
    frame["latency_ms"] = pd.to_numeric(frame["latency_ms"], errors="raise")
    frame["cost_usd"] = pd.to_numeric(frame["cost_usd"], errors="raise")
    frame["success"] = frame["success"].astype("boolean")

    non_nullable = ["call_id", "run_id", "tool", "latency_ms", "success", "cost_usd"]
    missing_values = frame[non_nullable].isna().any()
    if missing_values.any():
        columns = missing_values[missing_values].index.tolist()
        raise ValueError(f"以下列包含缺失值: {columns}")

    if frame["call_id"].duplicated().any():
        duplicates = frame.loc[frame["call_id"].duplicated(), "call_id"].tolist()
        raise ValueError(f"call_id 重复: {duplicates}")

    return (
        frame.groupby("tool", as_index=False)
        .agg(
            calls=("call_id", "size"),
            success_rate=("success", "mean"),
            median_latency_ms=("latency_ms", "median"),
            p95_latency_ms=("latency_ms", lambda s: s.quantile(0.95)),
            total_cost_usd=("cost_usd", "sum"),
        )
        .sort_values(["success_rate", "p95_latency_ms"], ascending=[True, False])
    )


records = [
    {"call_id": "c1", "run_id": "r1", "tool": "search", "latency_ms": 400, "success": True, "cost_usd": 0.01},
    {"call_id": "c2", "run_id": "r1", "tool": "weather", "latency_ms": 120, "success": True, "cost_usd": 0.002},
    {"call_id": "c3", "run_id": "r2", "tool": "search", "latency_ms": 800, "success": False, "cost_usd": 0.01},
]

print(build_tool_report(records))
```

这个函数做了几件比“直接 groupby”更重要的事：

1. 验证所需列存在；
2. 显式转换类型，错误数据立即失败；
3. 检查每次工具调用的唯一键 `call_id`；同一个 `run_id` 可以包含多次工具调用；
4. 返回列名明确的稳定摘要。

生产评测还应记录样本规模和置信度。样本很少时，P95 和成功率可能不稳定，不能只看一个数字就决定上线。

### 15.1 指标必须绑定统计粒度

同一份日志可以按不同粒度计算出不同结论：

- 工具调用成功率：分母是工具调用数；
- Agent 运行成功率：分母是运行数，一次运行中任一关键工具失败可能导致整次失败；
- 用户任务完成率：可能需要人工或模型评分，与系统是否返回 HTTP 200 不等价。

因此字段应避免笼统命名为 `success`。更明确的列名可以是 `tool_call_ok`、`run_completed`、`task_score`。

### 15.2 延迟、成本与质量一起看

只优化单一指标容易产生错误方向：更快的模型可能质量下降，更高的成功率可能来自无限重试并带来成本增长。常见评测表至少包含：

| 维度 | 示例指标 | 解释 |
|---|---|---|
| 质量 | accuracy、task_score、citation_precision | 是否完成正确任务 |
| 可靠性 | completion_rate、timeout_rate | 是否稳定完成 |
| 延迟 | P50/P95/P99 | 典型和尾部体验 |
| 成本 | input/output tokens、cost_usd | 单次及总资源消耗 |
| 行为 | steps、tool_calls、retries | Agent 如何得到结果 |
| 安全 | blocked_actions、policy_violations | 是否触碰禁止行为 |

比较版本时优先按同一个 `case_id` 做配对分析，避免两个版本碰巧运行了不同难度的数据。

### 15.3 平均数、百分位数与样本量

- 平均值适合看总体资源消耗，但容易被极端值拉高；
- 中位数/P50 表示典型样本；
- P95/P99 展示尾部，但小样本下非常不稳定；
- 最大值适合发现极端事件，不适合描述总体体验。

报告应同时显示 `count`。例如某工具只有 3 次调用，其 P95 不能与 10 万次调用的工具直接等量比较。

---

## 16. 性能与内存的基本意识

### 16.1 先测量

```python
import pandas as pd

df = pd.DataFrame(
    {
        "tool": ["search", "weather"],
        "latency_ms": [500, 120],
    }
)

print(df.memory_usage(deep=True).sort_values(ascending=False))
```

优化顺序建议：

1. 只读取所需行列；
2. 删除无意义的中间副本；
3. 使用正确类型；
4. 用向量化替代纯 Python 逐行计算；
5. 数据仍过大时，再考虑分块、查询引擎或分布式方案。

除了内存，还应测量时间。Notebook 可使用 `%timeit`，普通脚本可以使用 `time.perf_counter()`；重复运行并避免把文件下载等无关工作混入计时。

性能问题常见来源：

- 重复读取同一文件；
- 循环中不断创建/拼接 DataFrame；
- `object` 列保存大量 Python 对象；
- 行级 `apply`；
- 不必要的深拷贝；
- 合并键重复导致数据爆炸；
- 在分析层逐行调用外部 API。

先用小数据验证语义，再用接近真实规模的数据测量。小样本快不代表算法能线性扩展。

### 16.2 类别类型

重复值很多的低基数字符串列可能适合 `category`：

```python
import pandas as pd

df = pd.DataFrame({"tool": ["search", "search", "weather"]})
df["tool"] = df["tool"].astype("category")
```

它可能减少内存并改善某些操作，但若值几乎都唯一，收益有限，还会增加类型处理复杂度。

类别有固定集合时可以显式声明顺序：

```python
import pandas as pd

severity = pd.CategoricalDtype(
    categories=["low", "medium", "high"],
    ordered=True,
)
values = pd.Series(["high", "low", "medium"], dtype=severity)
print(values.sort_values().tolist())  # ['low', 'medium', 'high']
```

如果出现未声明值会变成缺失，转换后应立即检查。

### 16.3 不要逐行追加 DataFrame

循环中不断 `concat` 小表通常效率差。先收集字典列表，最后一次构造：

```python
records: list[dict[str, object]] = []
for index in range(3):
    records.append({"run_id": f"r{index}", "success": True})

df = pd.DataFrame.from_records(records)
```

实时服务不应把每个请求都追加到常驻 DataFrame 当数据库；使用日志、数据库或消息系统持久化，再离线或批量分析。

### 16.4 什么时候换工具

Pandas 适合单机内存内的交互分析和中等规模管道。出现下列情况时评估其他工具：

- 数据远大于单机内存：分块、数据库、Polars lazy、Spark 等；
- 主要工作是 SQL 聚合：DuckDB 或数据库可能更直接；
- 需要多人并发写入和事务：关系数据库；
- 需要近似最近邻检索：向量索引；
- 需要实时监控：日志/指标系统，而不是常驻 DataFrame。

更换工具前保留一套小型正确性基准，确认新实现的过滤、缺失值、连接和时区语义一致。

---

## 17. 常见坑

### 坑 1：把数组当作单个布尔值

```python
import numpy as np

values = np.array([1, 2, 3])
# if values:  # ValueError：真假含糊
#     ...

if values.size > 0:
    print("非空")
```

需要判断全部或任一元素时使用 `values.all()` / `values.any()`，但要确认这正是业务语义。

### 坑 2：广播得到错误但合法的结果

数组形状可兼容，不代表业务维度对齐。给关键维度命名、断言 `shape`，并用小型手算案例测试。

### 坑 3：忘记切片可能是视图

修改切片前判断是否需要 `.copy()`，尤其在函数边界和共享缓存中。

### 坑 4：把 `NaN` 当普通值比较

使用 `np.isnan`、`pd.isna`、`Series.isna()`。

### 坑 5：依赖 Pandas 隐式索引对齐

两个 `Series` 运算会按标签对齐，不只是按位置：

```python
a = pd.Series([1, 2], index=["x", "y"])
b = pd.Series([10, 20], index=["y", "x"])
print(a + b)  # x=21, y=12
```

这是强大功能，也可能造成意外。明确检查索引，必要时重置或对齐。

### 坑 6：链式赋值

使用 `.loc[...] = ...` 或显式 `.copy()`，不要依赖中间切片是否共享数据。

### 坑 7：多对多连接导致行数爆炸

合并前检查键唯一性，使用 `validate`，合并后核对行数。

### 坑 8：在 `apply` 中做网络请求

这会隐藏失败、限流、超时和并发控制。网络 I/O 应作为明确的异步/任务调度流程。

### 坑 9：评测指标没有分母

报告“成功率 100%”时必须同时报告样本数、数据范围和过滤规则。

### 坑 10：把 Python 列表与数组运算混在一起

列表的 `+` 是拼接，数组的 `+` 是逐元素相加。函数边界应尽早统一类型，并用 `np.asarray` 明确转换。

### 坑 11：无意间使用 `object` 列

混入数字、字符串和对象会让列失去高效向量化能力。读取后检查 `dtypes`，对转换失败进行显式统计。

### 坑 12：连接后不检查行数

连接前后记录行数、唯一键数量和 `_merge` 分布。多对多连接不是必然错误，但必须是明确设计。

### 坑 13：把相关性当因果关系

Pandas 可以快速发现“更长提示词与更高得分相关”，但这不能证明增加提示词长度会提高质量。版本比较需要控制数据集、配对样本和其他变量。

---

## 18. 练习题

### 练习 1：数组操作

创建一个形状为 `(4, 3)` 的数组，包含 1～12。完成：

1. 取第 2 列；
2. 计算每行平均值；
3. 将大于 8 的值替换为 8，但不修改原数组；
4. 把结果变形成 `(2, 6)`。

提示：检查原数组在替换后是否保持不变；验收时同时断言数值和 `shape`。

### 练习 2：归一化

编写函数，把二维数组的每一行缩放到和为 1。处理全零行：你可以选择抛出异常或保留全零，但必须在函数契约中说明并测试。

提示：使用 `sum(axis=1, keepdims=True)`；验收应包含普通行、零行、负值和错误维度。

### 练习 3：Top-K 检索

给定一个查询向量和 100 个文档向量：

- 计算余弦相似度；
- 返回相似度最高的 5 个索引和分数；
- 拒绝维度不匹配和零向量；
- 写至少三个 pytest 用例。

验收：Top-K 顺序稳定；`k` 超范围有明确行为；与一个小型手算例子的结果一致。

### 练习 4：日志清洗

读取“一行代表一次工具调用”的 CSV，包含：`call_id`、`run_id`、`timestamp`、`tool`、`latency_ms`、`success`。

- 解析 UTC 时间；
- 清理工具名首尾空格并转小写；
- 将非法耗时转换失败数量单独记录；
- 按唯一的 `call_id` 去重，保留最新摄取记录；同一个 `run_id` 可以保留多次合法工具调用；
- 输出干净 CSV。

提示：保留非法记录计数和少量脱敏样本；不要在清洗过程中静默改变原始文件。

### 练习 5：工具报告

按工具生成：调用数、成功数、失败率、中位数延迟、P95 延迟。按失败率降序排列，并指出样本少于 10 的工具。

验收：空输入、未知成功状态和缺失工具名都有定义；所有比例同时带分母。

### 练习 6：实验对比

有 `baseline.csv` 和 `candidate.csv`，都包含 `case_id`、`score`、`latency_ms`、`cost_usd`。按 `case_id` 做一对一连接并计算候选版本相对基线的变化。拒绝重复 `case_id`，报告缺失匹配。

提示：使用 `validate="one_to_one"` 和 `indicator=True`；分别报告质量提升但成本上升的案例。

### 综合练习 7：Agent 评测数据管道

设计并实现一个小型评测脚本：

1. 从 JSON Lines 读取运行记录；
2. 验证必需字段和合法值；
3. 输出按 Agent 版本和工具分组的质量、延迟、成本指标；
4. 输出失败类型 Top 10；
5. 将摘要保存为 CSV 或 Parquet；
6. 为缺列、重复 ID、空数据集和正常数据编写测试。

验收重点不是代码行数，而是数据契约、异常路径和结果可解释性。

进一步验收：固定输入数据版本；报告生成过程可重复；输出中包含数据行数、过滤数、时间范围和 Agent 版本。

---

## 19. 小结

- NumPy 用同质多维数组表达批量数值，核心心智模型是 `shape + dtype + axis`；
- 切片可能是视图，修改前要明确是否需要副本；
- 广播和向量化很强，但必须验证维度与业务语义；
- Pandas 用标签组织表格，核心操作是选择、清洗、分组、聚合和连接；
- `.loc`、明确类型、连接验证和稳定列名能减少大量隐蔽错误；
- 在 Agent 开发中，NumPy/Pandas 最有价值的地方通常是向量计算、日志分析和评测，而不是控制 Agent 的运行循环；
- 数据结果必须附带样本规模、过滤规则与异常数据处理方式，才能支持可靠决策。
