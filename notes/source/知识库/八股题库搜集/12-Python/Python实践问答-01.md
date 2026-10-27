# Python实践问答

<a id="k8996e68d3a1d"></a>

## AIGC和AI Agent项目中，Python基础能力应该重点掌握哪些？

AIGC/Agent 项目考的不是“会不会语法”，而是能不能把 Python 写成可靠工程。

高频清单：

- **数据结构**：list、dict、set、tuple、deque、heapq、Counter
- **对象模型**：传参、作用域、闭包、装饰器、类方法、魔术方法
- **IO 序列化**：JSON/JSONL、pathlib、流式读写
- **并发**：threading、multiprocessing、asyncio、池
- **类型校验**：typing、dataclass、Pydantic
- **服务化**：FastAPI、校验、异常、日志、健康检查
- **数据处理**：NumPy、Pillow、OpenCV、Torch Tensor
- **安全**：禁滥用 eval、不拼接 SQL、密钥进环境变量
- **可观测**：logging、request_id、token 用量、延迟、工具调用日志
- **工程化**：venv/uv、pyproject、依赖锁定、可复现部署

面试总结句：<font color=DeepSkyBlue>基础扎实 = 数据结构选对 + 并发模型选对 + 边界校验到位 + 可观测可复现。</font>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L1178)，来源许可：GPL-3.0。

<a id="kdf4b724a1b40"></a>

## classmethod

1. 类方法：第一个参数是 `cls`，指向类本身。
2. 可以读写类属性，常用于替代构造器（alternate constructor）。
3. 适合需要访问/修改类级状态，或按类创建实例的场景。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E8%BF%9B%E9%98%B6%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L634)，来源许可：GPL-3.0。

<a id="kcb70165b9a08"></a>

## Coding (Python)

**1) FizzBuzz.** Print numbers from 1 to 100

* If it’s a multiplier of 3, print “Fizz”
* If it’s a multiplier of 5, print “Buzz”
* If both 3 and 5 — “Fizz Buzz"
* Otherwise, print the number itself

Example of output: 1, 2, Fizz, 4, Buzz, Fizz, 7, 8, Fizz, Buzz, 11, Fizz, 13, 14, Fizz Buzz, 16, 17, Fizz, 19, Buzz, Fizz, 22, 23, Fizz, Buzz, 26, Fizz, 28, 29, Fizz Buzz, 31, 32, Fizz, 34, Buzz, Fizz, ...

```python
for i in range(1, 101):
    if i % 3 == 0 and i % 5 == 0:
        print('Fizz Buzz')
    elif i % 3 == 0:
        print('Fizz')
    elif i % 5 == 0:
        print('Buzz')
    else:
        print(i)
```

**2) Factorial**. Calculate a factorial of a number

* `factorial(5)` = 5! = 1 * 2 * 3 * 4 * 5 = 120
* `factorial(10)` = 10! = 1 * 2 * 3 * 4 * 5 * 6 * 7 * 8 * 9 * 10 = 3628800

```python
def factorial(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
```

We can also write this function using recursion:

```python
def factorial(n: int):
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n - 1)
```

**3) Mean**. Compute the mean of number in a list

* `mean([4, 36, 45, 50, 75]) = 42`
* `mean([]) = NaN` (use `float('NaN')`)

<img src="img/formula_mean.png" />

```python
def mean(numbers):
    if len(numbers) > 0:
        return sum(numbers) / len(numbers)
    return float('NaN')
```

**4) STD**. Calculate the standard deviation of elements in a list.

* `std([1, 2, 3, 4]) = 1.29`
* `std([1]) = NaN` (use `float('NaN')`)
* `std([]) = NaN`

<img src="img/formula_std.png" />

```python
from math import sqrt
from statistics import mean

def std_dev(numbers):
    if len(numbers) > 1:
        avg = mean(numbers)
        var = sum((i - avg) ** 2 for i in numbers) / (len(numbers) - 1)
        std = sqrt(var)
        return std
    return float('NaN')
```

**5) RMSE**. Calculate the RMSE (root mean squared error) of a model. The function takes in two lists: one with actual values, one with predictions.

* `rmse([1, 2], [1, 2]) = 0`
* `rmse([1, 2, 3], [3, 2, 1]) = 1.63`

<img src="img/formula_rmse.png" />

```python
import math

def rmse(y_true, y_pred):
    assert len(y_true) == len(y_pred), 'different sizes of the arguments'
    squares = sum((x - y)**2 for x, y in zip(y_true, y_pred))
    return math.sqrt(squares / len(y_true))
```

**6) Remove duplicates**. Remove duplicates in list. The list is not sorted and the order of elements from the original list should be preserved.

* `[1, 2, 3, 1]` ⇒ `[1, 2, 3]`
* `[1, 3, 2, 1, 5, 3, 5, 1, 4]` ⇒ `[1, 3, 2, 5, 4]`

```python
def remove_duplicates(lst):
    new_list = []
    mentioned_values = set()
    for elem in lst:
        if elem not in mentioned_values:
            new_list.append(elem)
            mentioned_values.add(elem)
    return new_list

# The above solution checks the values into a set and it is O(1) efficient using
# a few of lines.
# A shorter solution follows: it is O(n^2) but can be fine when lst has no "too
# many elements" - the quantity depends by the running box.
def remove_duplicates2(lst):
    new_list = []
    for elem in lst:
        if elem not in new_list:
            new_list.append(elem)
    return new_list
```

**7) Count**. Count how many times each element in a list occurs.

`[1, 3, 2, 1, 5, 3, 5, 1, 4]` ⇒  
* 1: 3 times
* 2: 1 time
* 3: 2 times
* 4: 1 time
* 5: 2 times

```python
numbers = [1, 3, 2, 1, 5, 3, 5, 1, 4]
counter = dict()
for elem in numbers:
    counter[elem] = counter.get(elem, 0) + 1
```
or
```python
from collections import Counter

numbers = [1, 3, 2, 1, 5, 3, 5, 1, 4]
counter = Counter(numbers)
```

**8) Palindrome**. Is string a palindrome? A palindrome is a word which reads the same backward as forwards.

* “ololo” ⇒ Yes
* “cafe” ⇒ No

```python
def is_palindrome(s):
    return s == s[::-1]
```
or
```python
def is_palindrome(s):
    for i in range(len(s) // 2):
        if s[i] != s[-i - 1]:
            return False
    return True
```

**9) Counter**. We have a list with identifiers of form “id-SITE”. Calculate how many ids we have per site.

<img src="img/counter_1.png" />

```python
def counter(lst):
    ans = {}
    for i in lst:
        site = i[-2:]
        ans[site] = ans.get(site, 0) + 1
    return ans
```

**10) Top counter**. We have a list with identifiers of form “id-SITE”. Show the top 3 sites. You can break ties in any way you want.

<img src="img/counter_2_top.png" />

```python
def top_counter(lst):
    site_dict = counter(lst)  # using last problem's solution
    top_keys = sorted(site_dict, reverse=True, key=site_dict.get)[:3]
    return {key: site_dict[key] for key in top_keys}
```

**11) RLE**. Implement RLE (run-length encoding): encode each character by the number of times it appears consecutively.

* `'aaaabbbcca'` ⇒ `[('a', 4), ('b', 3), ('c', 2), ('a', 1)]`
* (note that there are two groups of 'a')

```python
def rle(s):
    ans, cur, num = [], None, 0
    for i in range(len(s)):
        if i == 0:
            cur, num = s[i], 1
        elif cur != s[i]:
            ans.append((cur, num))
            cur, num = s[i], 1
        else:
            num += 1
        if i == len(s) - 1:
            ans.append((cur, num))
    return ans
```

Using itertools.groupby
```python
import itertools

def rle(s):
    return [(l, len(list(g))) for l, g in itertools.groupby(s)]
```

**12) Jaccard**. Calculate the Jaccard similarity between two sets: the size of intersection divided by the size of union.

* `jaccard({'a', 'b', 'c'}, {'a', 'd'}) = 1 / 4`

<img src="img/formula_jaccard.png" />

```python
def jaccard(a, b):
    return len(a & b) / len(a | b)
```

**13) IDF**. Given a collection of already tokenized texts, calculate the IDF (inverse document frequency) of each token.

* input example: `[['interview', 'questions'], ['interview', 'answers']]`

<img src="img/formula_idf_1.png" />

Where:

* t is the token,
* n(t) is the number of documents that t occurs in,
* N is the total number of documents

```python
from math import log10

def idf1(docs):
    docs = [set(doc) for doc in docs]
    n_tokens = {}
    for doc in docs:
        for token in doc:
            n_tokens[token] = n_tokens.get(token, 0) + 1
    ans = {}
    for token in n_tokens:
        ans[token] = log10(len(docs) / (1 + n_tokens[token]))
    return ans
```

```python
import math

def idf2(docs):
    n_docs = len(docs)

    docs = [set(doc) for doc in docs]
    all_tokens = set.union(*docs)

    idf_coefficients = {}
    for token in all_tokens:
        n_docs_w_token = sum(token in doc for doc in docs)
        idf_c = math.log10(n_docs / (1 + n_docs_w_token))
        idf_coefficients[token] = idf_c

    return idf_coefficients
```

**14) PMI**. Given a collection of already tokenized texts, find the PMI (pointwise mutual information) of each pair of tokens. Return top 10 pairs according to PMI.

PMI is used for finding collocations in text — things like “New York” or “Puerto Rico”. For two consecutive words, the PMI between them is:

<img src="img/formula_pmi_1.png" />

The higher the PMI, the more likely these two tokens form a collection. We can estimate PMI by counting:

<img src="img/formula_pmi_2.png" />

Where:
* N is the total number of tokens in the text,
* c(t1, t2) is the number of times t1 and t2 appear together,
* c(t1) and c(t2) — the number of times they appear separately.

```python
import math

def pmi(docs):
    n_pairs = {}
    n_tokens = {}

    docs = [tuple(doc) for doc in docs]
    for doc in docs:
        for token in doc:
            n_tokens[token] = n_tokens.get(token, 0) + 1

        n_pairs[doc] = n_pairs.get(doc, 0) + 1
        ans = {}
        for pair in n_pairs:
            ans[pair] = math.log2(n_pairs[pair] * (sum(n_tokens.values())) / (n_tokens[pair[0]] * n_tokens[pair[1]]))

        srt = sorted(ans.items(), key=lambda x: x[1], reverse=True)[:10]

    return srt
```

### 参考资料

- [alexeygrigorev/data-science-interviews](https://github.com/alexeygrigorev/data-science-interviews/blob/919f44547ef5ffc2bd59674fd301940529f4c1a8/technical.md#L228)，来源许可：CC-BY-4.0。

<a id="kf8154e659887"></a>

## list

- ```lst[a:b]```：左闭右开
- ```lst.append(value)```：在末尾添加元素，复杂度O(1)
- ```lst.pop()```：弹出列表末尾元素，复杂度O(1)
- ```lst.pop(index)```：弹出任意位置元素，将后面的元素前移，复杂度O(n)
- ```lst.insert(index, value)```：插入元素，后面的元素后移，复杂度O(n)
- ```lst.remove(value)```：移除等于value的第一个元素，后面的元素前移，复杂度O(n)
- ```lst.count(value)```：计数值为value的元素个数
- ```lst.sort(reverse = False)```：排序，默认升序

### 参考资料

- [Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Python%20Handbook.md#L161)，来源许可：GPL-3.0。

<a id="k85117a5fc755"></a>

## ProcessPoolExecutor怎么使用?

`ProcessPoolExecutor` 是 `concurrent.futures` 中的进程池封装，比 `multiprocessing.Pool` 更高层，和 `ThreadPoolExecutor` 接口几乎一致，适合快速把 CPU 密集任务并行化。

### 基本用法

```python
from concurrent.futures import ProcessPoolExecutor, as_completed
import time

def cpu_task(n: int) -> int:
    time.sleep(0.5)  # 模拟计算
    return n * n

if __name__ == "__main__":
    numbers = list(range(8))

    with ProcessPoolExecutor(max_workers=4) as ex:
        # 方式 1：map，保持输入顺序
        print(list(ex.map(cpu_task, numbers)))

    with ProcessPoolExecutor(max_workers=4) as ex:
        # 方式 2：submit + as_completed，谁先完成谁先处理
        futs = [ex.submit(cpu_task, n) for n in numbers]
        for fut in as_completed(futs):
            print(fut.result())
```

### 主要 API

- `submit(fn, *args, **kwargs)` → 返回 `Future`
- `map(func, iterable)` → 惰性结果迭代器
- `shutdown(wait=True)` → `with` 退出时自动调用
- `Future.result(timeout=...)` / `Future.add_done_callback(...)`

### 与 multiprocessing.Pool 的比较

| | ProcessPoolExecutor | multiprocessing.Pool |
|--|---------------------|---------------------|
| 接口风格 | Future / concurrent.futures | map/apply_async |
| 与线程池一致性 | 高 | 低 |
| 取消任务 | Future.cancel（已运行的不可取消） | 终止较麻烦 |
| 推荐度（新代码） | 更推荐 | 维护旧代码时仍常见 |

### 一线场景

**1. 批量图像预处理 / 解码**

```python
from concurrent.futures import ProcessPoolExecutor
from PIL import Image

def process_image(path: str):
    img = Image.open(path).convert("RGB").resize((224, 224))
    return path, list(img.getdata())  # 或返回 numpy bytes

if __name__ == "__main__":
    paths = [...]  # 上千张
    with ProcessPoolExecutor(max_workers=8) as ex:
        for path, pixels in ex.map(process_image, paths, chunksize=16):
            ...
```

**2. 与 asyncio 组合**

```python
import asyncio
from concurrent.futures import ProcessPoolExecutor

def heavy(x):
    return sum(i * i for i in range(x))

async def main():
    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor(max_workers=4) as pool:
        tasks = [loop.run_in_executor(pool, heavy, 10**6) for _ in range(4)]
        print(await asyncio.gather(*tasks))

asyncio.run(main())
```

<font color=DeepSkyBlue>注意：worker 函数必须定义在可导入模块顶层；Windows 下主模块加 `if __name__ == "__main__":`。`chunksize` 对大量小任务能显著降低调度开销。</font>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E8%BF%9B%E9%98%B6%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L1245)，来源许可：GPL-3.0。

<a id="k4010b77c2e4a"></a>

## Python

- [Coding Interview Patterns: Nail Your Next Coding Interview](https://geni.us/q7svoz) (**Main Recommendation**)
    - An insider’s perspective on what interviewers are truly looking for and why.
    - 101 real coding interview problems with detailed solutions.
    - Intuitive explanations that guide you through each problem as if you were solving it in a live interview.
    - 1000+ diagrams to illustrate key concepts and patterns.	

### 参考资料

- [jwasham/coding-interview-university](https://github.com/jwasham/coding-interview-university/blob/717298bf219a30d7fb0671285c5f057b1bb74b27/README.md#L344)，来源许可：CC-BY-SA-4.0。

<a id="k0f43a1344d08"></a>

## Python中$*args$和$kwargs$的区别？

$*args$ 和 $**kwargs$ 主要用于函数定义，把不定数量的参数传给函数。

### $*args$

$*args$ 接收<font color=DeepSkyBlue>非键值对的可变位置参数</font>，在函数内是 tuple。

```python
def test_var_args(f_arg, *argv):
    print("first normal arg:", f_arg)
    for arg in argv:
        print("another arg through *argv:", arg)

test_var_args('hello', 'python', 'ddd', 'test')

-----------------结果如下-----------------------
first normal arg: hello
another arg through *argv: python
another arg through *argv: ddd
another arg through *argv: test
```

### $**kwargs$

$**kwargs$ 接收<font color=DeepSkyBlue>不定长度的键值对参数</font>，在函数内是 dict。

```python
def greet_me(**kwargs):
    for key, value in kwargs.items():
        print("{0} == {1}".format(key, value))

greet_me(name="yasoob")

-----------结果如下-------------
name == yasoob
```

### 一线实践：包装、透传与签名对齐

**1. 写通用 wrapper 时必须透传**

```python
import time
from functools import wraps

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.perf_counter()-t0:.3f}s")
        return result
    return wrapper
```

**2. 调用第三方 SDK 时组装参数**

```python
def chat(prompt: str, **kwargs):
    defaults = {"model": "gpt-4o-mini", "temperature": 0.7}
    defaults.update(kwargs)
    return client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        **defaults,
    )

chat("hi", temperature=0.2, max_tokens=64)
```

**3. 强制关键字参数与位置限定（Python 3）**

```python
def train(data, *, lr: float = 1e-4, batch_size: int = 32):
    ...

# train(data, 1e-3)          # TypeError
train(data, lr=1e-3)          # 正确，意图更清晰
```

<font color=DeepSkyBlue>面试常问：函数调用时 `f(*seq, **mapping)` 是「解包」；定义时是「收集」。二者方向相反。</font>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E8%BF%9B%E9%98%B6%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L466)，来源许可：GPL-3.0。

<a id="kb1fc5906cd24"></a>

## Python中__new__和__init__有什么区别？

- `__new__`：创建并返回实例（静态方法语义）。
- `__init__`：初始化已创建的实例，不能返回非 None。

```python
class ModelClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, endpoint):
        self.endpoint = endpoint  # 每次构造仍会跑
```

注意：单例 + `__init__` 每次都会执行，需用 `_inited` 防护重复初始化。业务代码更推荐模块级单例/依赖注入。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L1089)，来源许可：GPL-3.0。

<a id="k31a294ea9d93"></a>

## Python中assert的作用？

**常见问法：** Python中assert的作用?

`assert` 用于断言条件为真，失败时抛 `AssertionError`。用来表达“开发者认为这里必然成立”的不变量。

```python
def softmax(x):
    assert x.ndim >= 1, "expect at least 1-d input"
    ...
```

注意：

1. `python -O` 会去掉 assert，<font color=DeepSkyBlue>不要用它做对外输入校验</font>。
2. 对外参数、用户输入、API 边界应用显式 `if` + 业务异常，或 Pydantic。
3. assert 适合内部契约、单测、算法前置条件。

```python
# 坏：生产校验用 assert
assert user_age >= 0  # -O 下消失

# 好
if user_age < 0:
    raise ValueError("age must be >= 0")
```

### 补充说明

与第 8 题相同：断言内部不变量；`-O` 会移除；不用于对外校验。

```python
def top_k(scores, k):
    assert 0 < k <= len(scores)
    ...
```

测试中很常用：

```python
def test_chunk():
    assert len(chunk("abc", 2)) == 2
```

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L200)，来源许可：GPL-3.0。
- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L504)，来源许可：GPL-3.0。

<a id="kfb03b1b89a52"></a>

## Python中if "__name__" == __main__'的作用?

当模块被直接运行时 `__name__` 为 `"__main__"`；被 import 时为模块名。

作用：

1. 脚本入口与可复用库代码分离。
2. **Windows/macOS spawn 多进程必须保护入口**，否则子进程会再次执行主逻辑。

```python
def main():
    print("run as script")

if __name__ == "__main__":
    main()
```

```python
# 多进程模板（Windows 必写）
from multiprocessing import Process

def worker():
    print("hi")

if __name__ == "__main__":
    Process(target=worker).start()
```

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L475)，来源许可：GPL-3.0。

<a id="k826ea707c402"></a>

## python中index使用注意事项

`list.index(x)` 返回第一个匹配下标；找不到抛 `ValueError`。

```python
xs = [1, 2, 3, 2]
print(xs.index(2))       # 1（只返回首次出现）
print(xs.index(2, 2))    # 3（从下标 2 起找）

# 安全写法
i = xs.index(2) if 2 in xs else -1
# 或
try:
    i = xs.index(9)
except ValueError:
    i = None
```

注意：

1. 有重复元素时别假设“唯一索引”。
2. 查多个匹配用列表推导/`enumerate`。
3. dict 键查找 O(1)，比在 list 上反复 `index` 快得多。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L636)，来源许可：GPL-3.0。

<a id="kea32fb7d8b66"></a>

## Python中is和==的区别？

- `is`：比较身份（`id`），是否同一对象。
- `==`：比较值（可重载 `__eq__`）。

```python
a = [1, 2]
b = [1, 2]
print(a == b)   # True
print(a is b)   # False

x = None
print(x is None)  # True，推荐

# 小整数/驻留字符串可能 is 也为 True，但不可依赖
```

经验：判断 None/True/False/哨兵对象用 `is`；比较业务值用 `==`。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L753)，来源许可：GPL-3.0。

<a id="k3732f1fb37e4"></a>

## Python中None代表什么含义？

`None` 是 `NoneType` 的唯一实例，表示“无值/空/未初始化”。

```python
x = None
print(x is None)      # 推荐
# print(x == None)    # 不推荐，自定义 __eq__ 可能干扰

def find_model(name: str):
    return registry.get(name)  # 不存在返回 None

model = find_model("llama")
if model is None:
    raise KeyError("model not found")
```

一线建议：能用哨兵就用哨兵区分“缺省”和“合法空值”；API 边界用 Optional/None + 显式校验（Pydantic）。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L298)，来源许可：GPL-3.0。

<a id="k6a1c26b7d861"></a>

## Python中Numpy的broadcasting机制？

NumPy 的 broadcasting 让不同形状的数组在算术运算时自动对齐，避免显式循环或 `tile`/`repeat`。

```python
>>> import numpy as np
>>> a = np.array([1, 2, 3])
>>> b = np.array([6, 6, 6])
>>> c = a + b
>>> c
array([7, 8, 9])
```

形状不一致时，broadcasting 会把标量/低维数组扩展到兼容形状（<font color=DeepSkyBlue>不真正分配复制内存</font>）：

```python
>>> d = a + 5
>>> d
array([6, 7, 8])
```

多维示例：

```python
>>> e = np.ones((3, 3))
>>> e + a   # a.shape=(3,) 被广播成 (3,3)
array([[2., 3., 4.],
       [2., 3., 4.],
       [2., 3., 4.]])

>>> b = np.arange(3).reshape((3, 1))
>>> b + a
array([[1, 2, 3],
       [2, 3, 4],
       [3, 4, 5]])
```

### 规则总结

1. 从右向左对齐 shape；缺的维度用 1 补齐。
2. 长度为 1 的维度被扩展成另一数组对应维度的长度。
3. 两边对应维度既不相等、也不为 1，则报错。

```python
>>> a = np.arange(3)          # (3,)
>>> b = np.ones((3, 2))       # (3, 2)
>>> a + b
ValueError: operands could not be broadcast together with shapes (3,) (3,2)
```

### 一线实践：broadcasting 在 AI 里的真实用法

```python
import numpy as np

# 1) 批量归一化：减均值除标准差（mean/std 形状 (C,) 或 (C,1,1)）
x = np.random.randn(32, 3, 224, 224)  # NCHW
mean = x.mean(axis=(0, 2, 3), keepdims=True)
std = x.std(axis=(0, 2, 3), keepdims=True) + 1e-6
x_norm = (x - mean) / std

# 2) 注意力 mask：把 (B,1,1,T) 广播到 (B,H,T,T)
scores = np.random.randn(2, 8, 16, 16)  # B,H,T,T
mask = np.ones((2, 1, 1, 16)) * -1e9
masked = scores + mask

# 3) 余弦相似度批量计算
emb = np.random.randn(1000, 512)
emb = emb / np.linalg.norm(emb, axis=1, keepdims=True)  # keepdims 才能广播
query = np.random.randn(1, 512)
query = query / np.linalg.norm(query, axis=1, keepdims=True)
sims = emb @ query.T  # (1000, 1)
```

<font color=DeepSkyBlue>Torch 中 broadcasting 规则相同，是写自定义层、loss、mask 时必须吃透的基础。</font>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E8%BF%9B%E9%98%B6%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L549)，来源许可：GPL-3.0。

<a id="k3b31913fc1db"></a>

## Python中PIL和OpenCV处理图像的区别？

| | Pillow (PIL) | OpenCV |
|--|--------------|--------|
| 定位 | 通用图像读写/简单处理 | 计算机视觉全栈 |
| 颜色 | RGB | 默认 BGR |
| 依赖 | 轻 | 较重（含大量 CV 算子） |
| 与深度学习 | torchvision 常用 | 传统视觉、部署前处理常见 |

```python
from PIL import Image
import numpy as np

img = Image.open("cat.jpg").convert("RGB")
arr = np.asarray(img)  # HWC, RGB

# 训练前处理更常见 torch/PIL；传统视觉流水线常用 cv2
```

注意通道顺序：`cv2.imread` 得到 BGR，进 torch 前常要 `[:, :, ::-1]` 或 `cv2.cvtColor`。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L428)，来源许可：GPL-3.0。

<a id="ke35f7fafc738"></a>

## Python中range和xrange的区别？

这是 Python 2 时代的考点。在 **Python 3 中只有 `range`，没有 `xrange`**。

| | Python 2 `range` | Python 2 `xrange` | Python 3 `range` |
|--|------------------|-------------------|------------------|
| 返回 | list | xrange 对象（惰性） | range 对象（惰性） |
| 内存 | 大 | 小 | 小 |

```python
# Python 3
r = range(10)
print(type(r))       # <class 'range'>
print(list(r))       # [0, 1, ..., 9]
print(r[3], 3 in r)  # 支持索引和成员判断，O(1)

for i in range(0, 10, 2):
    print(i)
```

面试可答：`xrange` 是 Py2 遗留；Py3 的 `range` 已融合其惰性优点。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L88)，来源许可：GPL-3.0。

<a id="kf31d1865b872"></a>

## Python中remove，del以及pop之间的区别？

| 操作 | 作用 | 返回 | 失败行为 |
|------|------|------|----------|
| `list.remove(x)` | 删除第一个值为 x 的元素 | None | ValueError |
| `del lst[i]` | 删除下标 i | None | IndexError |
| `list.pop(i=-1)` | 删除并返回下标 i | 元素值 | IndexError |
| `dict.pop(k)` | 删键并返回值 | 值 | KeyError（可给默认值） |

```python
xs = [1, 2, 3, 2]
xs.remove(2)     # [1, 3, 2]
last = xs.pop()  # 2
del xs[0]        # [3]

d = {"a": 1}
print(d.pop("b", None))  # None，安全
```

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L408)，来源许可：GPL-3.0。

<a id="k088839ef4ff1"></a>

## Python中switch-case语句的实现？

Python 3.10+ 有 `match-case`（结构模式匹配）；更早版本用 if-elif、dict 分发或策略对象。

```python
# 3.10+ match
def handle(action: str):
    match action:
        case "search":
            return do_search()
        case "calc":
            return do_calc()
        case _:
            raise ValueError(action)
```

```python
# dict 分发（配置化更友好）
handlers = {
    "search": do_search,
    "calc": do_calc,
}

def handle(action: str):
    fn = handlers.get(action)
    if fn is None:
        raise ValueError(action)
    return fn()
```

Agent 工具路由场景更推荐 dict/注册表，便于插件化扩展。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L791)，来源许可：GPL-3.0。

<a id="k4fb61254825f"></a>

## Python中tuple、list和dict有什么区别？

| | tuple | list | dict |
|--|-------|------|------|
| 可变性 | 否 | 是 | 是 |
| 有序 | 是 | 是 | 插入序（3.7+） |
| 访问 | 下标 | 下标 | 键 |
| 可作 key | 是（元素需可哈希） | 否 | 键本身需可哈希 |
| 典型 | 记录、坐标、多返回值 | 动态序列 | 索引、配置、缓存 |

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L986)，来源许可：GPL-3.0。

<a id="k2e8b9598a38f"></a>

## Python中type()和isinstance()的区别？

- `type(x)` 返回精确类型。
- `isinstance(x, T)` 接受继承关系，更常用。

```python
class Animal: ...
class Dog(Animal): ...

d = Dog()
print(type(d) is Dog)          # True
print(isinstance(d, Animal))   # True
print(type(d) is Animal)       # False
```

需要严格类型时用 `type(x) is T`；大多数业务判断用 `isinstance`。多重类型：`isinstance(x, (int, float))`。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L773)，来源许可：GPL-3.0。

<a id="kf2307496d786"></a>

## python中一共都有哪些数据结构？

与第 10 题互补，再补几个 AI 工程高频结构：

```python
from collections import defaultdict, Counter, deque
from dataclasses import dataclass, field
import heapq

# 检索候选
cand = defaultdict(list)
cand["query1"].append({"doc": "d1", "score": 0.8})

# 滑动窗口指标
window = deque(maxlen=100)
window.append(0.12)

# TopK
top = heapq.nlargest(3, scores)

@dataclass
class Message:
    role: str
    content: str
    tool_calls: list = field(default_factory=list)
```

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L608)，来源许可：GPL-3.0。

<a id="k3b09a26f07d5"></a>

## Python中互换变量有不用创建临时变量的方法吗？

有，Python 元组打包/解包是最常见写法：

```python
a, b = 1, 2
a, b = b, a
print(a, b)  # 2 1
```

也可用异或（仅整数演示，可读性差，工程不推荐）：

```python
a ^= b
b ^= a
a ^= b
```

一线常用场景：

```python
left, right = right, left
key, value = mapping.popitem()
```

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L226)，来源许可：GPL-3.0。

<a id="k2c213e374be0"></a>

## Python中全局变量与局部变量之间的区别？

- 局部变量：函数内定义，作用域仅函数。
- 全局变量：模块顶层定义，整个模块可见。
- 函数内默认读全局；写全局需 `global`；嵌套函数改外层需 `nonlocal`。

```python
cache = {}  # 模级全局，慎用

def put(key, value):
    global cache
    cache[key] = value

def make_counter():
    n = 0
    def inc():
        nonlocal n
        n += 1
        return n
    return inc
```

一线建议：少用可变全局状态；用类、依赖注入、模块级常量、上下文对象传递。多线程共享可变全局要加锁。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L450)，来源许可：GPL-3.0。

<a id="kf8d1dd2de04a"></a>

## Python中单下划线、双下划线、前后双下划线分别代表什么？

| 写法 | 含义 |
|------|------|
| `_x` | 约定“内部使用” |
| `__x` | 类私有（name mangling：`_Class__x`） |
| `__x__` | 魔术方法/特殊属性，不要自造 |
| `_` | 一次性占位/无关变量 |

```python
class Client:
    def __init__(self):
        self.api_key = "public-ish"   # 公开
        self._session = None          # 内部
        self.__secret = "s"           # 真·类私有

    def __repr__(self):               # 魔术方法
        return "Client(...)"
```

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L1037)，来源许可：GPL-3.0。

<a id="k0fcd8189971a"></a>

## python中如何无损打开图像，并无损保存图像?

“无损”取决于格式与参数，不是所有保存都无损。

```python
from PIL import Image

# PNG/WebP(lossless)/BMP 相对无损；JPEG 本身有损
img = Image.open("input.png")
img.save("output.png", optimize=True)           # 无损
img.save("output.webp", lossless=True, quality=100)

# 避免不必要的模式转换
img = Image.open("input.png")  # 保持 mode，别无谓 convert RGB
img.save("output.png")
```

注意：

1. JPEG `quality=95` 仍是有损；要无损请换 PNG/WebP lossless。
2. 处理浮点图像（科学数据）用 NumPy/`tifffile`，别走 8-bit JPEG。
3. 元数据（EXIF）可能在重编码时丢失，需要 `exif`/`pnginfo` 显式保留。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L522)，来源许可：GPL-3.0。

<a id="kb401aa46690e"></a>

## Python中如何设计插件化工具注册机制？

Agent/RAG/评测框架几乎都需要「可插拔工具」。目标：新增工具不改核心调度代码。

### 1. 装饰器注册（最常用）

```python
# registry.py
_TOOL_REGISTRY: dict[str, dict] = {}

def register_tool(name: str | None = None, description: str = "", schema: dict | None = None):
    def deco(fn):
        key = name or fn.__name__
        _TOOL_REGISTRY[key] = {
            "fn": fn,
            "description": description or (fn.__doc__ or "").strip(),
            "schema": schema or {},
        }
        return fn
    return deco

def get_tool(name: str):
    return _TOOL_REGISTRY[name]

def list_tools():
    return [
        {"name": k, "description": v["description"], "schema": v["schema"]}
        for k, v in _TOOL_REGISTRY.items()
    ]
```

```python
# tools/search.py
from registry import register_tool

@register_tool(
    name="web_search",
    description="Search the web",
    schema={
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"],
    },
)
async def web_search(query: str) -> str:
    return f"results for {query}"
```

### 2. 入口点自动发现（pkgutil / importlib）

```python
import importlib, pkgutil

def autodiscover(package_name: str = "app.tools"):
    pkg = importlib.import_module(package_name)
    for _, mod_name, _ in pkgutil.iter_modules(pkg.__path__):
        importlib.import_module(f"{package_name}.{mod_name}")
    # import 时装饰器已注册
```

### 3. 基于 ABC / Protocol 的插件类

```python
from typing import Protocol

class Tool(Protocol):
    name: str
    async def run(self, **kwargs) -> str: ...

class EchoTool:
    name = "echo"
    async def run(self, text: str) -> str:
        return text
```

### 4. 执行器与安全边界

```python
import asyncio

async def invoke_tool(call: dict) -> str:
    tool = get_tool(call["name"])
    try:
        result = await asyncio.wait_for(tool["fn"](**call["args"]), timeout=30)
        return str(result)
    except asyncio.TimeoutError:
        return f"tool {call['name']} timeout"
    except Exception as e:
        return f"tool {call['name']} failed: {e}"
```

### 5. 工程增强

1. **JSON Schema 自动生成**：从函数签名 + type hints 推导，供 LLM function calling。
2. **权限与配额**：注册时声明 `requires=["network"]`，运行时校验。
3. **版本与冲突**：同名工具注册时报错或覆盖策略可配置。
4. **热加载**：开发期 `importlib.reload`，生产用独立 worker 进程更新。
5. **测试**：每个工具提供 `dry_run` 或 Fake，避免单测打真外部服务。

### 一个更完整的最小闭环

```python
# __init__.py of tools package
autodiscover("app.tools")

TOOLS = list_tools()  # 交给 LLM 的 tool schema 列表

async def agent_step(user_msg: str, tool_calls: list[dict]):
    outputs = await asyncio.gather(*(invoke_tool(c) for c in tool_calls))
    return outputs
```

<font color=DeepSkyBlue>总结：装饰器注册 + 自动发现 + 统一 invoke 超时/错误处理，是当前一线 Agent 工具系统的标准骨架；Schema 从类型注解推导，可显著减少手写错误。</font>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E8%BF%9B%E9%98%B6%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L2682)，来源许可：GPL-3.0。

<a id="k84641761819c"></a>

## Python中常见的切片操作

语法：`seq[start:stop:step]`（含 start，不含 stop）。

```python
s = "hello world"
print(s[0:5])     # hello
print(s[::-1])    # dlrow olleh
print(s[::2])     # hlowrd

xs = list(range(10))
print(xs[2:8:2])  # [2, 4, 6]
print(xs[-3:])    # [7, 8, 9]

# 切片产生浅拷贝
a = [1, 2, 3]
b = a[:]          # 新 list，元素引用相同
a[0] = 99
print(b)          # [1, 2, 3]
```

注意：切片不会 IndexError，越界返回空序列；步长为负表示反向。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L352)，来源许可：GPL-3.0。

<a id="k1b38cedb66f3"></a>

## python中文件有哪些打开模式，它们的区别是什么？

| 模式 | 含义 |
|------|------|
| `r` | 只读（默认） |
| `w` | 写，清空原文件 |
| `a` | 追加 |
| `x` | 独占创建，已存在则失败 |
| `b` | 二进制 |
| `t` | 文本（默认） |
| `+` | 读写 |

```python
with open("log.txt", "a", encoding="utf-8") as f:
    f.write("line\n")

with open("model.bin", "rb") as f:
    data = f.read()
```

注意：Windows 换行、编码显式 `encoding="utf-8"`、大文件别一次 `read()`。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L930)，来源许可：GPL-3.0。

<a id="k1bbb56b2529e"></a>

## Python中有哪些常用的设计模式？

Python 支持多种设计模式。下面按创建型 / 结构型 / 行为型给出在 AI 工程中真正常用的几类。

### 创建型模式

**1. 单例模式（Singleton）**

保证全局唯一实例。AI 服务里常见于：全局配置、tokenizer、模型缓存、客户端连接。

```python
class Settings:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
        return cls._instance

    def __init__(self):
        if self._loaded:
            return
        self.api_key = "..."
        self._loaded = True
```

更推荐用模块级变量、`lru_cache` 或 FastAPI 的 `lifespan`/依赖注入，而不是手写 `__new__` 单例。

**2. 工厂方法（Factory Method）**

按类型创建对象。多模型路由、多数据源适配时非常常见。

```python
def build_model(cfg: dict):
    kind = cfg["type"]
    if kind == "hf":
        from transformers import AutoModel
        return AutoModel.from_pretrained(cfg["name"])
    if kind == "torch":
        return TorchModel(cfg)
    raise ValueError(f"unknown model type: {kind}")
```

**3. 抽象工厂（Abstract Factory）**

创建一组相关对象。例如：不同后端（OpenAI / 本地 vLLM）各自提供 client + tokenizer + encoder。

### 结构型模式

**1. 适配器（Adapter）**

统一不同 SDK/接口。把各家 LLM API 适配成同一个 `chat(messages) -> str`。

```python
class OpenAIAdapter:
    def __init__(self, client, model: str):
        self.client = client
        self.model = model

    def chat(self, messages: list[dict]) -> str:
        resp = self.client.chat.completions.create(
            model=self.model, messages=messages
        )
        return resp.choices[0].message.content

class VLLMAdapter:
    def __init__(self, base_url: str, model: str):
        ...
    def chat(self, messages: list[dict]) -> str:
        ...

def get_adapter(cfg) -> object:
    return OpenAIAdapter(...) if cfg["provider"] == "openai" else VLLMAdapter(...)
```

**2. 装饰器模式（Decorator）**

动态叠加能力：重试、缓存、打点、脱敏，而不改核心调用链。

**3. 代理（Proxy）**

控制访问：懒加载模型、权限校验、远程调用封装。

```python
class LazyModelProxy:
    def __init__(self, factory):
        self._factory = factory
        self._model = None

    def __getattr__(self, name):
        if self._model is None:
            self._model = self._factory()
        return getattr(self._model, name)
```

### 行为型模式

**1. 观察者（Observer）**

事件总线：训练完成、评测结束、webhook 回调。

```python
class EventBus:
    def __init__(self):
        self._subs: dict[str, list] = {}

    def on(self, event: str, fn):
        self._subs.setdefault(event, []).append(fn)

    def emit(self, event: str, payload):
        for fn in self._subs.get(event, []):
            fn(payload)

bus = EventBus()
bus.on("train_done", lambda p: print("save ckpt", p["step"]))
bus.emit("train_done", {"step": 1000})
```

**2. 策略（Strategy）**

可替换算法：不同重试策略、不同采样策略、不同 chunk 切分策略。

```python
class ChunkStrategy:
    def split(self, text: str) -> list[str]:
        raise NotImplementedError

class FixedSizeChunk(ChunkStrategy):
    def __init__(self, size: int = 512):
        self.size = size
    def split(self, text: str):
        return [text[i:i+self.size] for i in range(0, len(text), self.size)]

class RecursiveChunk(ChunkStrategy):
    def split(self, text: str):
        # 按段落/句子优先切分
        ...

def chunk(text: str, strategy: ChunkStrategy):
    return strategy.split(text)
```

**3. 模板方法（Template Method）**

训练/评测骨架固定，步骤由子类实现：`load_data` → `forward` → `loss` → `optimize`。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E8%BF%9B%E9%98%B6%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L714)，来源许可：GPL-3.0。

<a id="k51b3a7b03363"></a>

## Python中有哪些高级的逐元素矩阵级计算操作？

在 NumPy/Torch 中，应尽量用向量化逐元素/矩阵级运算代替 Python 循环。

### 常用操作

```python
import numpy as np

a = np.random.randn(4, 8)
b = np.random.randn(4, 8)

# 逐元素
a + b
a * b
np.maximum(a, 0)          # ReLU
np.exp(a)
np.log(np.abs(a) + 1e-8)
np.clip(a, -1, 1)

# 归约
a.sum(axis=-1, keepdims=True)
a.mean(axis=0)
np.max(a, axis=-1)
np.linalg.norm(a, axis=-1, keepdims=True)

# 矩阵级
a @ b.T                   # 矩阵乘
np.einsum("ij,jk->ik", a, b.T)

# 条件
np.where(a > 0, a, 0)     # 类似 mask
```

### Torch 对应

```python
import torch
import torch.nn.functional as F

x = torch.randn(2, 8, 16)
y = torch.randn(2, 8, 16)

F.relu(x)
F.softmax(x, dim=-1)
F.mse_loss(x, y)
torch.einsum("bhd,bmd->bhm", x, y)
x.masked_fill(y < 0, 0.0)
```

### 一线高频：注意力打分

```python
def attention_scores(q, k, scale=None):
    # q: (B,H,T,D)  k: (B,H,S,D)
    if scale is None:
        scale = q.shape[-1] ** -0.5
    return torch.matmul(q, k.transpose(-2, -1)) * scale
```

### 性能建议

1. 用 `keepdims=True` 方便广播，避免 `reshape` 错误。
2. `einsum` 可读性与性能的折中，复杂收缩优先考虑。
3. 能 `matmul`/`conv` 就不要写双层 for。
4. 注意 dtype/设备一致；混合精度时显式 cast。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E8%BF%9B%E9%98%B6%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L1883)，来源许可：GPL-3.0。

<a id="k7e2388b58280"></a>

## python中海象运算符的介绍

`:=` 在表达式中赋值（Python 3.8+）。

```python
while (n := len(data)) > 0:
    print(n)
    data.pop()

if (m := re.search(r"\d+", text)) is not None:
    print(m.group())
```

适合：避免重复计算/重复调用、条件内赋值。过度使用会伤可读性。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L970)，来源许可：GPL-3.0。

<a id="k990af44cdc4e"></a>

## Python中的lambda表达式？

Lambda 表达式即匿名函数，语法为：

```python
lambda 参数: 表达式
```

### 主要特征

1. 可有任意数量参数，但只能有一个表达式（不能写语句）。
2. 适合简短、一次性的逻辑。
3. 调用时求值并返回表达式结果。

### 示例

```python
f = lambda x: x * 2
print(f(3))  # 6

g = lambda x, y: x + y
print(g(2, 3))  # 5

words = ["apple", "hi", "banana"]
print(sorted(words, key=lambda w: len(w)))
# ['hi', 'apple', 'banana']
```

### 一线实践

```python
# 1) pandas / 结果排序
df["score"] = df["text"].apply(lambda t: len(t.split()))

# 2) 按置信度排序评测结果
results.sort(key=lambda r: r["confidence"], reverse=True)

# 3) 简单默认工厂（注意：默认参数求值时机）
handlers = {
    "sum": lambda xs: sum(xs),
    "mean": lambda xs: sum(xs) / len(xs),
}
```

### 优点与局限

- 优点：简洁、便于和 `sorted`/`map`/`filter` 组合。
- 局限：只能单表达式；复杂逻辑请用 `def`，否则可读性变差。

<font color=DeepSkyBlue>不要写过长的 lambda；需要复用、调试或加文档时，升级成命名函数。</font>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E8%BF%9B%E9%98%B6%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L862)，来源许可：GPL-3.0。

<a id="k406f19cd014b"></a>

## Python中的主要数据结构都有哪些？

内置：`list`、`tuple`、`dict`、`set`、`frozenset`、`str`、`bytes`、`bytearray`、`range`。

标准库补充：`collections.deque`、`Counter`、`defaultdict`、`OrderedDict`、`heapq`、`queue`、`dataclasses`。

| 结构 | 有序 | 可变 | 典型用途 |
|------|------|------|----------|
| list | 是 | 是 | 通用序列 |
| tuple | 是 | 否 | 不可变记录、dict key |
| dict | 插入序 | 是 | 键值索引、配置 |
| set | 否 | 是 | 去重、成员判断 |
| deque | 是 | 是 | 两端 O(1) 操作、滑动窗口 |
| Counter | 插入序 | 是 | 计数 |

```python
from collections import Counter, deque, defaultdict
import heapq

tokens = ["a", "b", "a"]
print(Counter(tokens))          # Counter({'a': 2, 'b': 1})

recent = deque(maxlen=100)      # 无界日志的替代
scores = [3, 1, 2]
heapq.heapify(scores)           # 最小堆
```

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L252)，来源许可：GPL-3.0。

<a id="k970090e7016d"></a>

## Python是解释语言还是编译语言？

准确说：Python 是<font color=DeepSkyBlue>先编译成字节码，再由虚拟机解释执行</font>，日常语境下归为解释型语言。

- 源码 `.py` 会被编译成 `.pyc`（字节码），由 CPython 解释器逐条执行。
- 优点：跨平台、迭代快、胶水能力强。
- 缺点：纯 Python 热路径比 C/C++/Rust 慢。

一线常见分工：Python 负责编排与业务，计算密集部分交给 NumPy/Torch/CUDA/C++ 扩展。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L55)，来源许可：GPL-3.0。

<a id="k72240f6b9068"></a>

## Python设计模式在AI Agent系统中如何落地？

Agent 系统是设计模式最能体现价值的地方之一。

### 1. 策略：不同的规划/工具选择策略

```python
class Planner:
    def plan(self, state) -> list[dict]:
        raise NotImplementedError

class ReActPlanner(Planner):
    def plan(self, state):
        return [{"tool": "search", "args": {"q": state["query"]}}]

class OneShotPlanner(Planner):
    def plan(self, state):
        return [{"tool": "final", "args": {"content": state["query"]}}]

class Agent:
    def __init__(self, planner: Planner):
        self.planner = planner

    def step(self, state):
        return self.planner.plan(state)
```

### 2. 观察者：轨迹与监控

```python
class Tracer:
    def __init__(self):
        self.events = []
    def on(self, event: str, payload: dict):
        self.events.append((event, payload))

agent_tracer = Tracer()
# 每个 step/tool_call/llm_request 都 emit，便于回放与评测
```

### 3. 责任链：中间件（鉴权、脱敏、限流、审计）

```python
class Middleware:
    async def __call__(self, request, call_next):
        raise NotImplementedError

class RateLimit(Middleware):
    def __init__(self, rpm: int):
        self.sem = asyncio.Semaphore(rpm)
    async def __call__(self, request, call_next):
        async with self.sem:
            return await call_next(request)
```

### 4. 备忘录：会话状态快照

```python
@dataclass
class AgentState:
    messages: list
    scratchpad: dict

    def snapshot(self):
        return copy.deepcopy(self)

    def restore(self, snap):
        self.messages = snap.messages
        self.scratchpad = snap.scratchpad
```

### 5. 代理：工具网关

```python
class ToolGateway:
    def __init__(self, tools: dict, policy):
        self.tools = tools
        self.policy = policy

    async def invoke(self, name, args):
        if not self.policy.allow(name, args):
            raise PermissionError(name)
        return await self.tools[name](**args)
```

### 6. 工厂：按配置构建 Agent 拓扑

```python
def build_agent(cfg: dict):
    planner = ReActPlanner() if cfg["mode"] == "react" else OneShotPlanner()
    tools = load_tools(cfg["tools"])
    return Agent(planner=planner, tools=ToolGateway(tools, DefaultPolicy()))
```

<font color=DeepSkyBlue>落地原则：模式服务于可替换、可观测、可测试；不要为了「用了模式」而过度抽象。</font>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E8%BF%9B%E9%98%B6%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L2509)，来源许可：GPL-3.0。

<a id="k2004fec05837"></a>

## 一线实践：什么时候必须分清？

**1. 配置/超参对象被多个组件共享时**

```python
base_cfg = {"lr": 1e-4, "layers": [12, 24, 36]}

# 错误：改 trainer 的 layers 会同时改掉 eval 的
trainer_cfg = base_cfg
eval_cfg = base_cfg

# 正确：需要独立可变副本时用深拷贝
import copy
trainer_cfg = copy.deepcopy(base_cfg)
eval_cfg = copy.deepcopy(base_cfg)
trainer_cfg["layers"].append(48)
# eval_cfg["layers"] 不受影响
```

**2. 缓存历史消息 / 对话上下文**

```python
history = [{"role": "user", "content": "hi"}]
snapshot = history.copy()       # 浅拷贝：append 历史不影响 snapshot 长度
# 但若原地改 history[0]["content"]，snapshot 也会变
snapshot = copy.deepcopy(history)  # 彻底隔离
```

**3. Torch 张量与自定义对象**

```python
import torch

a = torch.randn(3, 3)
b = a.clone()              # 推荐：张量自己的拷贝语义
c = copy.deepcopy(a)       # 也可用，但 clone/ detach 语义更清晰
d = a.detach().clone()     # 断梯度 + 拷贝
```

<font color=DeepSkyBlue>经验法则：默认优先浅拷贝；只有当子对象会被原地修改且不希望波及副本时，才用 deepcopy（深拷贝大对象成本高）。</font>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E8%BF%9B%E9%98%B6%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L372)，来源许可：GPL-3.0。

<a id="keb0d0a806a62"></a>

## 一线实践：和 AI 服务相关的关键点

```python
import gc
import torch

# 1) 大对象用完及时断开，别指望 GC 立刻帮你收 GPU 显存
model = None
gc.collect()
torch.cuda.empty_cache()

# 2) 循环引用常见于：回调闭包、双向链表、缓存对象图
# 可用 weakref 打破环
import weakref
class Node:
    def __init__(self):
        self.parent = None
        self.children = []

parent = Node()
child = Node()
parent.children.append(child)
child.parent = weakref.ref(parent)  # 弱引用，不增加引用计数

# 3) 长驻服务里不要滥用 gc.disable()；必要时用 gc.freeze() 减少全量扫描
```

<font color=DeepSkyBlue>注意：Python GC 只管 CPU 侧对象；CUDA 显存、C 扩展里的原生内存需要显式释放（`.detach()`、`del`、`empty_cache`、上下文退出）。</font>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E8%BF%9B%E9%98%B6%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L436)，来源许可：GPL-3.0。

<a id="k68f16ffc1784"></a>

## 为什么要加在解释器,而不是在其他层?

GIL锁加在解释器一层，也就是说Python调用的Cython解释器上加了GIL锁，因为你python调用的所有线程都是原生线程。原生线程是通过C语言提供原生接口，相当于C语言的一个函数。你一调它，你就控制不了了它了，就必须等它给你返回结果。只要已通过python虚拟机
，再往下就不受python控制了，就是C语言自己控制了。加在Python虚拟机以下加不上去，只能加在Python解释器这一层。

### 参考资料

- [Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Python%20Handbook.md#L84)，来源许可：GPL-3.0。

<a id="k6048f145ded1"></a>

## 为什么说Python是动态语言？

1. 变量无静态类型声明，类型在运行时绑定。
2. 对象类型运行时确定，鸭子类型普遍。
3. 可动态增删属性/方法，自省与元编程能力强。

```python
x = 1
x = "now a string"  # 合法

def greet(obj):
    return obj.speak()  # 只要求有 speak
```

类型注解/Pydantic 可以补上“工程上的静态约束”，但不改变动态语言本质。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L997)，来源许可：GPL-3.0。

<a id="ka7854db78d7f"></a>

## 二、高性能库与工具

| 工具 | 适用场景 |
|------|----------|
| NumPy / Pandas | 数值计算、表格处理 |
| PyTorch | GPU 张量与自动微分 |
| `torch.compile` | 编译加速热点模型 |
| Numba | 数值热循环 JIT |
| Cython / C 扩展 | 真正的计算瓶颈 |
| PyPy | 纯 CPU 的 Python 脚本（兼容性需验证） |
| polars / duckdb | 大规模列式数据分析 |

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E8%BF%9B%E9%98%B6%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L1028)，来源许可：GPL-3.0。

<a id="k08681f0bda2a"></a>

## 五、代码级微优化

1. 局部变量快于全局/属性查找：`range_ = range`、缓存 `self.x` 到局部。
2. 字符串拼接用 `"".join(parts)`，不要在循环里 `s += t`。
3. 异常控制流有成本，不要用异常做普通分支。
4. 批量 I/O：一次读 1MB，不要一次读 1 字节。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E8%BF%9B%E9%98%B6%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L1076)，来源许可：GPL-3.0。

<a id="ka44a6e9e538d"></a>

## 什么是 lambda 表达式？

简单来说，lambda表达式通常是当你需要使用一个函数，但是又不想费脑袋去命名一个函数的时候使用，也就是通常所说的匿名函数。

lambda表达式一般的形式是：关键词lambda后面紧接一个或多个参数，紧接一个冒号“：”，紧接一个表达式

### 参考资料

- [Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Python%20Handbook.md#L121)，来源许可：GPL-3.0。

<a id="kb7af23b830e1"></a>

## 什么是Python中的推导式？Python的推导式一共有多少种？

共 4 种：列表、字典、集合、生成器推导式。

```python
# 列表
squares = [x ** 2 for x in range(10)]
# 字典
mapping = {x: x ** 2 for x in range(5)}
# 集合
unique = {x % 3 for x in range(10)}
# 生成器（惰性）
gen = (x ** 2 for x in range(10))
```

带条件与嵌套：

```python
pairs = [(i, j) for i in range(3) for j in range(3) if i < j]
```

一线注意：推导式过长会伤可读性，改写成普通循环或具名函数；大数据优先生成器，避免一次性物化。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L584)，来源许可：GPL-3.0。

<a id="k91d7684a1c97"></a>

## 什么是Python中的魔术方法?

双下划线方法，用于接入 Python 数据模型。

```python
class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)
    def __repr__(self):
        return f"Vector({self.x}, {self.y})"
    def __len__(self):
        return 2
    def __getitem__(self, i):
        return (self.x, self.y)[i]
```

常见：`__init__`/`__new__`/`__call__`/`__enter__`/`__exit__`/`__iter__`/`__next__`/`__eq__`/`__hash__`/`__str__`/`__repr__`。

自定义可迭代工具、上下文管理器、可调用策略对象时几乎必用。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L867)，来源许可：GPL-3.0。

<a id="kef1a7b8c75e3"></a>

## 什么是python的字符串格式化技术？

主流演进：

```python
name, score = "model", 0.91

# 1) % 格式化（老）
print("score=%.2f" % score)

# 2) str.format
print("name={} score={:.2f}".format(name, score))

# 3) f-string（推荐）
print(f"name={name} score={score:.2f}")

# 4) 模板/安全场景可考虑 template string（3.14 t-string）或 string.Template
```

```python
# 结构化日志不要靠 f-string 拼大 SQL/HTML
import logging
logging.info("request done", extra={"model": name, "score": score})
```

一线：日志与业务字符串优先 f-string；对外拼接关注注入风险（SQL/HTML/Shell）。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L725)，来源许可：GPL-3.0。

<a id="k7f2043764818"></a>

## 介绍一下Python中logging库的作用

标准库日志：分级（DEBUG/INFO/WARNING/ERROR/CRITICAL）、Handler、Formatter、过滤器、层级 logger。

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("agent")

logger.info("tool finished", extra={"tool": "search", "latency_ms": 120})
```

一线建议：

1. 库代码只 `getLogger(__name__)`，不要 `basicConfig`。
2. 服务统一 JSON 日志 + request_id/trace_id。
3. 不要只靠 print；敏感信息（key、完整 prompt）要脱敏。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L1014)，来源许可：GPL-3.0。

<a id="k58529d068430"></a>

## 介绍一下Python中常用的标准库以及功能

| 模块 | 用途 |
|------|------|
| `os`/`sys`/`pathlib` | 路径、环境、解释器 |
| `json`/`csv`/`sqlite3` | 数据序列化与存储 |
| `re` | 正则 |
| `datetime`/`time` | 时间 |
| `logging` | 日志 |
| `typing`/`dataclasses` | 类型与数据类 |
| `collections`/`heapq`/`itertools`/`functools` | 容器与函数工具 |
| `asyncio`/`threading`/`multiprocessing`/`concurrent.futures` | 并发 |
| `subprocess`/`shutil` | 进程与文件 |
| `unittest`/`doctest` | 测试 |
| `argparse`/`tomllib` | CLI 与配置 |

```python
from pathlib import Path
import json

for p in Path("data").glob("*.jsonl"):
    with p.open(encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
```

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L890)，来源许可：GPL-3.0。

<a id="k27ef4e17f7d7"></a>

## 介绍一下Python中的sequence和mapping代表的数据结构

`Sequence` 与 `Mapping` 定义在 `collections.abc`，是两类核心容器抽象。

- **Sequence**：按位置有序，支持索引/切片。
- **Mapping**：键值对，按键快速查找。

### Sequence

常见类型：`list`、`tuple`、`str`、`range`、`deque`。

| 操作 | 描述 | 示例 |
|------|------|------|
| `obj[i]` | 索引 | `my_list[0]` |
| `obj[a:b]` | 切片 | `my_list[1:3]` |
| `len(obj)` | 长度 | `len(my_list)` |
| `in` | 成员判断 | `3 in my_list` |
| `for x in obj` | 迭代 | 遍历 |

```python
from collections.abc import Sequence

print(isinstance([1, 2], Sequence))   # True
print(isinstance((1, 2), Sequence))   # True
print(isinstance("hi", Sequence))     # True
print(isinstance({"a": 1}, Sequence)) # False
```

### Mapping

常见类型：`dict`、`defaultdict`、`OrderedDict`、`Counter`、`ChainMap`。

| 操作 | 描述 |
|------|------|
| `obj[k]` / `obj[k]=v` | 读写 |
| `k in obj` | 键存在性 |
| `keys()/values()/items()` | 视图 |
| `obj.get(k, default)` | 安全读取 |

```python
from collections import Counter, defaultdict, ChainMap

tokens = ["a", "b", "a", "c", "a"]
print(Counter(tokens))  # Counter({'a': 3, 'b': 1, 'c': 1})

cfg = ChainMap({"lr": 1e-4}, {"lr": 1e-3, "epochs": 3})  # 前者优先
print(cfg["lr"], cfg["epochs"])
```

### 对比

| | Sequence | Mapping |
|--|----------|---------|
| 组织方式 | 有序位置 | 键值 |
| 访问 | 索引 | 键 |
| 典型 | list/tuple/str | dict/Counter |

### 一线注意

1. **list 不适合频繁头部插入**，用 `deque`。
2. **成员判断 O(1) 用 set/dict**，不要用 list。
3. **Python 3.7+ dict 保序**；需要 LRU 用 `functools.lru_cache` 或 `OrderedDict`。
4. **消息结构、tool call payload、配置**本质上都是 Mapping；序列化前先校验 schema（pydantic）。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E8%BF%9B%E9%98%B6%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L1682)，来源许可：GPL-3.0。

<a id="k7bcc54495366"></a>

## 介绍一下Python中的多态（Polymorphism）思想

多态指同一操作作用于不同对象时产生不同行为。Python 通过动态类型和鸭子类型天然支持多态。

### 鸭子类型

```python
class OpenAIEngine:
    def chat(self, messages):
        return "openai reply"

class LocalEngine:
    def chat(self, messages):
        return "local reply"

def ask(engine, messages):
    return engine.chat(messages)  # 不关心具体类型，有 chat 即可

ask(OpenAIEngine(), [...])
ask(LocalEngine(), [...])
```

### 继承 + 方法重写

```python
from abc import ABC, abstractmethod

class Chunker(ABC):
    @abstractmethod
    def split(self, text: str) -> list[str]:
        ...

class FixedChunker(Chunker):
    def split(self, text: str) -> list[str]:
        return [text[i:i+512] for i in range(0, len(text), 512)]

class SentenceChunker(Chunker):
    def split(self, text: str) -> list[str]:
        return [s.strip() for s in text.split("。") if s.strip()]
```

### 结构化类型：Protocol（typing）

```python
from typing import Protocol

class SupportsChat(Protocol):
    def chat(self, messages: list[dict]) -> str: ...

def run_pipeline(engine: SupportsChat):
    return engine.chat([{"role": "user", "content": "hi"}])
```

类型检查器能做静态校验，运行时仍是鸭子类型。

### 运算符重载

```python
class TensorLike:
    def __init__(self, data):
        self.data = data
    def __add__(self, other):
        return TensorLike(self.data + other.data)
```

### 价值

1. 换模型供应商、换存储后端时，上层业务代码不用改。
2. 测试时注入 Fake/Mock 对象即可。
3. 插件系统天然依赖多态。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E8%BF%9B%E9%98%B6%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L1531)，来源许可：GPL-3.0。

<a id="k1129ae9ccdfe"></a>

## 介绍一下Python中的封装(Encapsulation)思想

封装把数据和操作数据的方法绑在一起，并对外隐藏实现细节，只暴露稳定接口。

### Python 中的「约定式封装」

- `name`：公开
- `_name`：受保护（约定内部使用）
- `__name`：类私有，触发 name mangling（`_ClassName__name`）
- 没有 C++/Java 那种强制访问控制

```python
class Tokenizer:
    def __init__(self, vocab: dict):
        self._vocab = vocab          # 内部实现，外部不应直接改
        self.__version = "1.0"       # 名称改写

    def encode(self, text: str) -> list[int]:
        return [self._vocab.get(t, 0) for t in text.split()]

    def vocab_size(self) -> int:
        return len(self._vocab)
```

### 属性与描述符

```python
from pydantic import BaseModel, Field

class TrainConfig(BaseModel):
    lr: float = Field(1e-4, gt=0, le=1)
    batch_size: int = Field(32, ge=1)

# Pydantic 用类型注解 + 校验做封装，比手写 setter 更省事
cfg = TrainConfig(lr=0.001, batch_size=64)
```

### 一线价值

1. **模型服务对外只暴露 `predict`/`chat`**，内部权重、设备、批处理逻辑可随意改。
2. **配置对象不可随意改字段**，避免运行中被旁路修改导致不可复现。
3. **测试与替换实现更容易**：只要接口不变，内部可以重写。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E8%BF%9B%E9%98%B6%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L1428)，来源许可：GPL-3.0。

<a id="k339702202091"></a>

## 介绍一下Python中耦合和解耦的代码设计思想

- **耦合**：模块间依赖过紧，改一处牵一发动全身。
- **解耦**：通过接口、依赖注入、事件、策略等降低直接依赖。

```python
# 紧耦合：内部直接 new 具体实现
class RAG:
    def __init__(self):
        self.llm = OpenAIClient()  # 写死

# 解耦：依赖注入
class RAG:
    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever

rag = RAG(llm=LocalLLM(), retriever=FaissRetriever())
```

其他手段：Protocol/ABC 定义接口、回调/事件总线、配置驱动工厂、把副作用放到边界。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L824)，来源许可：GPL-3.0。

<a id="k151a654d76d7"></a>

## 介绍一下Python的自省特性

自省（Introspection）指程序在运行时检查自身对象结构的能力：类型、属性、方法、签名、源码等。

### 常用 API

```python
x = 10
print(type(x), isinstance(x, int))  # <class 'int'> True

class Person:
    def __init__(self, name):
        self.name = name
    def greet(self):
        print(f"Hello, {self.name}")

p = Person("Alice")
print(hasattr(p, "name"))           # True
print(getattr(p, "name"))           # Alice
setattr(p, "age", 25)
print(p.__dict__)                   # {'name': 'Alice', 'age': 25}
print(callable(p.greet))            # True
print(dir(p)[:5])                   # 属性与方法列表
```

### inspect 模块

```python
import inspect

def my_function(x: int, y: int = 0) -> int:
    return x + y

print(inspect.signature(my_function))  # (x: int, y: int = 0) -> int
print(inspect.getsource(my_function))
print(inspect.iscoroutinefunction(asyncio.sleep))  # 可判断是否协程
```

### 一线应用

**1. 插件/工具自动发现与注册**

```python
import importlib, pkgutil

def load_tools(package_name: str):
    pkg = importlib.import_module(package_name)
    tools = {}
    for _, mod_name, _ in pkgutil.iter_modules(pkg.__path__):
        mod = importlib.import_module(f"{package_name}.{mod_name}")
        if hasattr(mod, "register"):
            tools.update(mod.register())
    return tools
```

**2. 从函数签名生成 JSON Schema（LLM Function Calling）**

```python
import inspect
from typing import get_type_hints

def fn_schema(fn) -> dict:
    sig = inspect.signature(fn)
    hints = get_type_hints(fn)
    props = {}
    required = []
    for name, param in sig.parameters.items():
        ann = hints.get(name, str)
        props[name] = {"type": {int: "integer", float: "number", str: "string"}.get(ann, "string")}
        if param.default is inspect.Parameter.empty:
            required.append(name)
    return {"name": fn.__name__, "parameters": {"type": "object", "properties": props, "required": required}}
```

**3. 序列化、DI、ORM、ORM 映射、调试器**都依赖自省。

<font color=DeepSkyBlue>自省是 Python 元编程与框架能力的底层原语；写 SDK/Agent 框架时几乎必用。</font>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E8%BF%9B%E9%98%B6%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L1603)，来源许可：GPL-3.0。

<a id="k76514394d4e4"></a>

## 从手动封装到 @ 语法糖

```python
import logging

def use_log(func):
    def wrapper(*args, **kwargs):
        logging.warning("%s is running", func.__name__)
        return func(*args, **kwargs)
    return wrapper

@use_log
def bar():
    print("I am bar")

bar()
------------结果如下------------
WARNING:root:bar is running
I am bar
```

`@use_log` 等价于 `bar = use_log(bar)`。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E8%BF%9B%E9%98%B6%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L251)，来源许可：GPL-3.0。

<a id="kb8f4c6a67ff3"></a>

## 减少重复计算

```python
from functools import lru_cache

@lru_cache(maxsize=1024)
def embed_text(text: str):
    ...  # 调 embedding API 前先查缓存
```

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E8%BF%9B%E9%98%B6%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L1002)，来源许可：GPL-3.0。

<a id="k4af1e3f597fd"></a>

## 合适的数据结构与算法

- 查找用 `set`/`dict`，不要在 list 上做 `in`（O(n)）。
- 频繁两端操作用 `collections.deque`。
- 计数用 `Counter`，去重保持顺序用 `dict.fromkeys`。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E8%BF%9B%E9%98%B6%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L996)，来源许可：GPL-3.0。

<a id="k84334006a0db"></a>

## 向量化优先于 Python 循环

```python
# 慢
result = [x * 2 for x in huge_list]

# 快：NumPy / Torch 向量化
import numpy as np
arr = np.asarray(huge_list)
result = arr * 2
```

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E8%BF%9B%E9%98%B6%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L1012)，来源许可：GPL-3.0。

<a id="kc385425eb806"></a>

## 四、性能分析先行

```bash
python -m cProfile -o out.prof train.py
python -m pstats out.prof  # 交互查看热点

# 逐行分析
pip install line_profiler
kernprof -l -v hot_script.py
```

```python
# 内存
# pip install memory_profiler scalene
```

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E8%BF%9B%E9%98%B6%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L1060)，来源许可：GPL-3.0。
