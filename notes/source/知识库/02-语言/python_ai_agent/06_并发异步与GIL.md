# 06. 并发、异步与 GIL：为 AI Agent 设计可靠的执行器

> 适用版本：Python 3.11+  
> 本章目标：理解同步、并发、并行的边界，能为 Agent 的工具调用、网络请求、流式输出、超时、取消和限流选择合适的执行模型。

## 学习目标

完成本章后，你应该能够：

1. 用自己的话解释同步、并发、并行，以及 I/O 密集型和 CPU 密集型工作的区别。
2. 说清楚进程、线程、协程的执行模型、开销、隔离性和适用场景。
3. 使用 `threading`、`concurrent.futures` 和 `multiprocessing` 编写可控的并发代码。
4. 理解 CPython GIL 的基本机制，知道它为什么限制纯 Python 线程的 CPU 并行，又为什么不等于“线程没有用”。
5. 使用 `asyncio` 的事件循环、协程、Task、Future、`async/await`、`TaskGroup`、超时、取消、信号量和队列。
6. 把阻塞式 SDK 或文件操作安全地桥接到异步服务中，并正确清理资源。
7. 为 AI Agent 实现并行工具调用、流式事件、超时、取消、限流和背压。
8. 能根据工作负载、第三方库特性和部署环境选择线程、进程或协程。

---

## 1. 先建立三个概念：同步、并发、并行

### 1.1 同步（synchronous）

同步描述的是**调用者要不要等当前操作完成后才能继续**。下面的程序在 `sleep` 返回以前不会执行第二句打印：

```python
import time


def fetch(name: str, seconds: float) -> str:
    time.sleep(seconds)  # 模拟网络等待
    return f"{name} 完成"


print(fetch("A", 1))
print(fetch("B", 1))
```

两项工作总耗时大约 2 秒。同步不一定低效：当步骤有严格的数据依赖，或者任务非常短时，直接顺序执行通常最简单。

### 1.2 并发（concurrency）

并发是**在一个时间段内管理多个未完成的工作**。它不保证同一时刻真的执行两项工作，而是让一个工作等待 I/O 时推进另一个工作。

例如，协程 A 等待 HTTP 响应时，事件循环可以运行协程 B。单核机器也能得到更好的 I/O 利用率。

### 1.3 并行（parallelism）

并行是**同一时刻使用多个执行单元**，比如多个 CPU 核心真正同时运行多个进程。并行通常用来缩短 CPU 计算时间，但会引入进程间通信、数据拷贝、同步和调度开销。

可以用这句话区分：

> 并发关注“同时处理多件事”，并行关注“同时执行多件事”。

### 1.4 I/O 密集型和 CPU 密集型

| 工作类型 | 大部分时间花在哪里 | 典型 Agent 工作 | 常见选择 |
| --- | --- | --- | --- |
| I/O 密集型 | 等网络、磁盘、数据库、模型服务 | 调多个工具 API、读取对象存储、等待 LLM 流 | `asyncio`；没有异步 SDK 时用线程 |
| CPU 密集型 | 计算、压缩、解析、图像/音频处理 | 本地向量计算、文档切分、批量重排、OCR 前处理 | 多进程、释放 GIL 的 C 扩展、专用计算服务 |
| 混合型 | I/O 后接少量计算 | 请求模型后解析 JSON、保存结果 | 协程负责 I/O，必要时把重计算放线程/进程 |

异步并不意味着“必然更快”。它主要减少了等待期间浪费的线程和进程资源。若任务是纯 Python 计算，`async def` 仍然只能在当前线程中运行；若没有主动 `await`，它甚至会阻塞整个事件循环。

### 1.5 用时间线理解“变快”的来源

假设两个独立的远程调用各等待 0.3 秒：

```text
顺序：  A 等待 0.3s  ───────────────>  B 等待 0.3s  ───────────────>  总计约 0.6s
并发：  A 等待 0.3s  ───────────────>
        B 等待 0.3s  ───────────────>                         总计约 0.3s
```

并发版本节省的是等待重叠的时间，不是让单个远程服务处理得更快。若 A 的结果是 B 的输入，就不能按这条时间线并发；若远端每秒只允许 2 次请求，盲目增加本地并发还会得到更多 `429` 和重试。

下面的可运行示例同时展示 I/O 等待和 CPU 循环：

```python
from __future__ import annotations

import asyncio
import time


async def io_task(name: str) -> str:
    await asyncio.sleep(0.2)
    return name


def cpu_task(limit: int) -> int:
    total = 0
    for number in range(limit):
        total += number * number
    return total


async def main() -> None:
    started = time.perf_counter()
    await asyncio.gather(io_task("A"), io_task("B"))
    print(f"两个 I/O 等待约 {time.perf_counter() - started:.2f}s")

    # 下面的同步 CPU 循环会直接占用事件循环线程；async def 并没有使它并行。
    started = time.perf_counter()
    cpu_task(300_000)
    print(f"CPU 循环约 {time.perf_counter() - started:.2f}s")


asyncio.run(main())
```

在 Agent 中，先画出步骤依赖图，再决定哪些节点能并发；不要从“调用次数多”直接推导“应该使用 gather”。

---

## 2. 进程、线程与协程的基本模型

### 2.1 对比表

| 维度 | 进程（process） | 线程（thread） | 协程（coroutine） |
| --- | --- | --- | --- |
| 调度者 | 操作系统 | 操作系统 | Python 事件循环（用户态协作式） |
| 地址空间 | 相互隔离 | 共享同一进程内存 | 通常共享所在进程内存 |
| 切换/创建开销 | 高 | 中 | 低 |
| 是否能利用多核执行纯 Python | 能（进程间各自有解释器） | CPython 默认受 GIL 限制 | 不能；通常只有一个事件循环线程 |
| 适合 | CPU 并行、故障隔离 | 阻塞 I/O、没有异步接口的库 | 大量可等待的异步 I/O |
| 主要风险 | 序列化、内存、启动与 IPC 成本 | 竞态、死锁、共享状态 | 忘记 `await`、阻塞事件循环、取消处理不当 |

这三种模型可以组合。例如 FastAPI 的一个进程内运行一个事件循环；异步端点用协程处理网络 I/O；某个只能同步调用的 SDK 用 `asyncio.to_thread()` 放到线程；真正重的本地计算则提交到进程池。

### 2.2 协作式与抢占式

线程和进程由操作系统抢占式调度，代码可能在任意指令边界被切换，因此共享变量必须考虑同步。

协程是协作式调度：只有执行到 `await`，或者主动把控制权交回事件循环时，另一个任务才有机会运行。下面的循环没有 `await`，会霸占事件循环：

```python
import asyncio


async def bad_cpu_loop() -> None:
    for _ in range(10_000_000):
        pass  # 没有让出控制权


async def main() -> None:
    await asyncio.gather(bad_cpu_loop(), asyncio.sleep(0.1))
    # sleep 不能按预期及时运行，因为 bad_cpu_loop 阻塞了事件循环。


asyncio.run(main())
```

把纯 Python 循环写成 `async def` 不会自动变成异步；需要把工作放到线程/进程，或拆成小块并显式让出控制权（后者只解决响应性，不能获得 CPU 并行）。

### 2.3 生命周期、切换点和共享状态

三种执行单元可以按生命周期粗略理解：

| 执行单元 | 典型生命周期 | 谁触发切换 | 结束时结果在哪里 |
| --- | --- | --- | --- |
| 进程 | 创建 → 启动 → 执行 → 退出/被终止 → `join` | 操作系统抢占 | `exitcode`、IPC、Future 或持久化存储 |
| 线程 | 创建 → `start` → 运行 → 返回/异常 → `join` | 操作系统抢占 | 共享内存、Future 或队列 |
| 协程 | 创建对象 → Task 调度 → 执行到 `await` 暂停 → 恢复 → 返回/异常/取消 | 事件循环协作式调度 | Task/Future 的结果或异常 |

关键切换点不同：线程和进程即使代码没有显式等待，也可能在任意时刻被切换；协程通常只有执行到可等待的 `await` 才让出控制权。因此异步函数内部的“检查后再写入”虽然常常没有线程抢占，但只要中间有 `await`，其他协程就可能修改同一个状态。

竞态条件是“结果取决于时序”的错误。例如库存扣减不能写成“读取库存 → `await` → 判断 → 写回”的无保护流程；两个协程可能都读取到同一个旧值。锁保护的是业务不变量，而不是某一行语句：

```python
from __future__ import annotations

import asyncio


class Wallet:
    def __init__(self, balance: int) -> None:
        self.balance = balance
        self._lock = asyncio.Lock()

    async def withdraw(self, amount: int) -> bool:
        async with self._lock:
            if amount > self.balance:
                return False
            # 临界区内不做慢速网络调用；这里只更新本地不变量。
            self.balance -= amount
            return True


async def main() -> None:
    wallet = Wallet(100)
    results = await asyncio.gather(
        wallet.withdraw(80),
        wallet.withdraw(80),
    )
    print(results, wallet.balance)  # 一个 True、一个 False、余额 20


asyncio.run(main())
```

“原子性”要分层理解：某些 CPython 内置操作在特定实现中不会被线程打断，但这不是 Python 语言层面的业务事务保证；`counter += 1` 也不是可依赖的跨线程复合操作。不要依赖 GIL 保护业务状态，使用锁、队列、数据库事务或不可变消息。

线程版本使用 `threading.Lock`，进程版本则需要 `multiprocessing.Lock`、共享内存原语或外部存储；`asyncio.Lock` 只适用于同一个事件循环。

---

## 3. GIL：知道边界，避免过度简化

### 3.1 它是什么

在默认的 CPython 实现中，GIL（Global Interpreter Lock，全局解释器锁）是保护解释器内部状态的一把锁。传统 CPython 运行时通常要求：**同一个解释器中的一个线程在某一时刻执行 Python 字节码**。线程仍然可以被切换，也仍然能等待 I/O，但多个线程不会让纯 Python 字节码在多个 CPU 核心上同时执行。

GIL 不是 Python 语言规范要求的特性：

- 这里讨论的是默认 CPython 的常见行为，不应推断到 PyPy、Jython 等实现。
- 某些 C/C++ 扩展在执行不需要访问 Python 对象的长计算时会主动释放 GIL，因此线程可能在扩展代码中并行运行。
- 阻塞 I/O 通常允许线程释放 GIL，所以线程很适合把多个网络/文件等待重叠起来。
- Python 3.13 起存在可选的 free-threaded（无 GIL）构建；依赖是否兼容、性能收益和部署方式仍要单独验证。本章以 Python 3.11+ 的默认 CPython 行为作为保守基线。

### 3.2 实际影响

| 说法 | 是否准确 | 更准确的理解 |
| --- | --- | --- |
| “有 GIL，所以线程完全没用” | 错 | I/O 密集任务可以显著受益；线程还适合桥接同步 SDK |
| “多线程能让纯 Python 计算用满多个核” | 通常错 | 默认 CPython 中同一进程的 Python 字节码受 GIL 限制 |
| “多进程一定更快” | 错 | 进程有启动、序列化、IPC、内存和调度成本；小任务可能更慢 |
| “`async def` 能绕过 GIL” | 错 | 协程通常仍在一个线程中执行；它解决的是等待并发 |
| “NumPy/Pandas 线程总能并行” | 错 | 某些底层操作可能释放 GIL，某些操作仍可能受限，要基准测试 |

判断性能时测量端到端延迟、吞吐、CPU、内存和外部服务限额，而不要只看代码形式。

### 3.3 GIL 与切换、扩展模块和 free-threaded 构建

默认 CPython 会在解释器运行过程中安排线程切换；切换频率不是业务级同步机制，`sys.setswitchinterval()` 也不应拿来修复竞态。线程在等待阻塞 I/O 时通常会释放 GIL，另一个线程可以执行 Python 代码；某些 C/C++ 扩展在长计算期间也会释放 GIL。

因此要区分三件事：

1. **并发等待**：线程或协程在等待网络/磁盘时推进其他工作；
2. **Python 字节码并行**：默认 CPython 同一解释器中通常受 GIL 限制；
3. **底层扩展并行**：NumPy 等库的具体操作是否释放 GIL、是否启动自己的线程，要看实现和版本。

Python 3.13 起有可选的 free-threaded CPython 构建。它不是把现有程序自动变成线性加速：扩展兼容性、线程安全假设、锁竞争和内存开销都要重新测试。部署时应把解释器构建、依赖兼容性和 benchmark 一起固定，不能只因为“无 GIL”就改变并发模型。

---

## 4. 线程：阻塞 I/O 的轻量并发

### 4.1 `threading.Thread` 的基本用法

当需要少量长期线程、明确的生命周期或线程之间共享内存时，可以直接使用 `threading`：

```python
from __future__ import annotations

import threading
import time


def download(name: str, seconds: float, results: list[str], lock: threading.Lock) -> None:
    time.sleep(seconds)  # 模拟阻塞 I/O；等待时其他线程可以运行
    with lock:
        results.append(f"{name}: done")


def main() -> None:
    results: list[str] = []
    lock = threading.Lock()
    threads = [
        threading.Thread(
            target=download,
            args=("tool-a", 0.2, results, lock),
            name="tool-a-worker",
        ),
        threading.Thread(
            target=download,
            args=("tool-b", 0.1, results, lock),
            name="tool-b-worker",
        ),
    ]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()  # 主线程等待工作线程结束

    print(results)


if __name__ == "__main__":
    main()
```

`list.append` 在某些 CPython 版本上是一个原子操作，并不代表任意复合逻辑都安全。不要把“GIL”当作业务级锁；多个步骤（先读、再判断、再写）仍可能发生竞态。用 `Lock` 明确保护共享不变量，或优先使用消息队列、不可变结果和线程安全容器。

### 4.2 `ThreadPoolExecutor`：批量提交阻塞任务

线程池复用线程，避免为每个短任务都创建新线程：

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


def call_sync_tool(tool_name: str) -> str:
    time.sleep(0.2)  # 代表 requests、同步数据库驱动等阻塞调用
    return f"{tool_name} 返回结果"


def main() -> None:
    tool_names = ["search", "calendar", "weather"]
    with ThreadPoolExecutor(max_workers=3, thread_name_prefix="agent-tool") as pool:
        futures = {
            pool.submit(call_sync_tool, name): name for name in tool_names
        }

        # as_completed 按完成顺序消费；异常会在 future.result() 处重新抛出。
        for future in as_completed(futures):
            name = futures[future]
            try:
                print(name, future.result())
            except Exception as exc:
                print(name, "失败:", exc)


if __name__ == "__main__":
    main()
```

注意：`future.cancel()` 只能取消尚未开始执行的任务。已经在运行的线程无法被安全地强制杀掉；要实现可取消的业务操作，需让函数自己检查 `threading.Event`，或者使用底层客户端的超时选项。

### 4.3 线程常见同步原语

- `Lock`：互斥访问一段临界区。
- `RLock`：同一线程可以重复获取；只在确有递归/嵌套需求时使用。
- `Event`：一个线程通知其他线程某个条件已发生。
- `Semaphore`：限制同时进入资源的线程数。
- `Condition`：等待某个由共享状态表达的条件。
- `queue.Queue`：线程安全的生产者/消费者队列，通常优于手写共享列表。

锁要短、明确、同一顺序获取；不要在持锁期间执行长时间网络请求，否则容易造成吞吐下降甚至死锁。

### 4.4 线程生命周期、daemon 和优雅退出

`Thread.start()` 只能调用一次；`join()` 等待线程结束，带 `timeout` 时只表示“最多等这么久”，不会自动终止线程。`daemon=True` 的线程不会阻止解释器退出，适合极少数无需清理的辅助工作，不适合写文件、提交订单或持有数据库连接的 Agent 任务。

推荐让工作函数检查停止事件，并由拥有者负责 `join`：

```python
from __future__ import annotations

import threading
import time


def poll_tools(stop: threading.Event) -> None:
    while not stop.is_set():
        print("poll once")
        # wait 比 sleep 更容易在收到停止信号时提前醒来。
        stop.wait(0.05)


def main() -> None:
    stop = threading.Event()
    thread = threading.Thread(target=poll_tools, args=(stop,), name="poller")
    thread.start()
    time.sleep(0.12)
    stop.set()
    thread.join(timeout=1.0)
    if thread.is_alive():
        raise RuntimeError("线程未能在关闭期限内退出")


if __name__ == "__main__":
    main()
```

若线程需要传递多个结果，优先用 `queue.Queue`；生产者只负责放入消息，消费者只负责取出和确认，能减少共享可变状态。线程无法被安全强杀，因此“请求超时”不等于“底层工作已经停止”。

---

## 5. `concurrent.futures`：用统一接口切换线程池与进程池

`Future` 表示一个尚未完成或已完成的结果。`ThreadPoolExecutor` 和 `ProcessPoolExecutor` 都支持 `submit`、`map`、`Future.result` 等接口，因此可以先抽象“提交任务”，再根据负载选择执行器。

### 5.1 进程池运行 CPU 工作

```python
from concurrent.futures import ProcessPoolExecutor


def count_primes(limit: int) -> int:
    """故意使用纯 Python 计算，便于观察进程池适用场景。"""
    count = 0
    for number in range(2, limit):
        is_prime = all(number % divisor for divisor in range(2, int(number**0.5) + 1))
        count += int(is_prime)
    return count


def main() -> None:
    limits = [20_000, 21_000, 22_000, 23_000]
    # 进程池任务必须尽量是模块顶层可导入、可 pickle 的函数。
    with ProcessPoolExecutor() as pool:
        results = list(pool.map(count_primes, limits))
    print(results)


if __name__ == "__main__":
    # Windows/macOS 的 spawn 模式尤其需要这个保护，避免子进程重复执行顶层代码。
    main()
```

进程池会序列化函数参数和返回值。不能把打开的 socket、锁、闭包或某些不可 pickle 的对象直接传进去。大对象频繁跨进程传输时，复制成本可能抵消并行收益。生产环境应测量不同 `max_workers`，而不是盲目使用 CPU 核数。

### 5.2 `multiprocessing.Process` 与 `Queue`

需要更明确的进程生命周期或长驻工作进程时，可以直接使用 `multiprocessing`：

```python
from multiprocessing import Process, Queue


def worker(jobs: Queue, results: Queue) -> None:
    while True:
        job = jobs.get()
        if job is None:  # 哨兵：通知工作进程退出
            break
        job_id, value = job
        results.put((job_id, value * value))


def main() -> None:
    jobs: Queue = Queue()
    results: Queue = Queue()
    process = Process(target=worker, args=(jobs, results), name="square-worker")
    process.start()

    for job_id, value in enumerate([2, 3, 4]):
        jobs.put((job_id, value))
    jobs.put(None)

    for _ in range(3):
        print(results.get())
    process.join()


if __name__ == "__main__":
    main()
```

真实系统还要考虑：队列满时的背压、子进程异常、优雅退出、超时后如何回收、父进程退出时的孤儿进程，以及容器环境中的信号处理。Agent 服务通常把重计算交给独立任务队列或计算服务，而不是在请求进程里随意创建进程。

### 5.3 Executor 的生命周期、Future 和序列化边界

`Executor` 是资源拥有者：退出 `with` 时会等待已提交的工作完成。对请求级短任务来说，这可能导致接口在异常后仍等待很久；需要在应用关闭时统一管理池，并对每个 Future 的结果设置读取预算。

```python
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import time


def slow_call() -> str:
    time.sleep(1)
    return "done"


def main() -> None:
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(slow_call)
        try:
            print(future.result(timeout=0.05))
        except TimeoutError:
            print("读取结果超时；线程中的函数仍可能继续执行")
            # cancel 只能取消尚未开始的 future，不能强制终止运行中的线程。
            print("cancelled:", future.cancel())
        print("最终结果:", future.result())


if __name__ == "__main__":
    main()
```

进程池和线程池的主要差异不只在 GIL：`ProcessPoolExecutor` 要 pickle 函数、参数和返回值；闭包、打开的 socket、锁、生成器和很多第三方客户端不可直接传递。大对象复制会很慢，进程池任务应传递紧凑数据或文件/共享内存标识。跨平台时把创建池和提交任务放在 `if __name__ == "__main__"` 下，并为进程函数提供模块顶层定义。

进程池 worker 异常会在 `Future.result()` 重新抛出；不要只调用 `submit()` 而丢掉 Future 引用，否则错误可能直到进程池关闭才被发现。

---

## 6. `asyncio` 的心智模型

`asyncio` 是基于 `async/await` 的异步 I/O 框架。典型流程如下：

```text
事件循环（event loop）
  ├─ 运行 Task A，A 执行到 await 网络 I/O ──┐
  ├─ 运行 Task B，B 执行到 await 定时器   ───┤──> I/O 就绪，恢复对应 Task
  └─ 处理回调、Future、取消和超时          ──┘
```

### 6.1 协程函数、协程对象、Task、Future

```python
import asyncio


async def fetch(name: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return f"{name} done"


async def main() -> None:
    coroutine = fetch("A", 0.2)       # 只创建协程对象，还未开始执行
    task = asyncio.create_task(        # 把协程交给事件循环调度
        fetch("B", 0.1),
        name="fetch-B",
    )
    print(await coroutine)             # 此处才开始运行 A
    print(await task)                  # 等待已经在后台运行的 B


asyncio.run(main())                   # 创建、运行并关闭顶层事件循环
```

- `async def` 定义协程函数；调用它得到协程对象。
- `await` 等待一个可等待对象，并在等待期间把控制权交还事件循环。
- `Task` 是事件循环中被调度的协程，适合表示一个并发中的工作。
- `Future` 是一个低层级的“未来结果容器”，通常由库或事件循环创建；应用代码更常使用 Task。
- 只写 `fetch("A", 1)` 而不 `await` 或 `create_task`，会产生“协程从未等待”的警告，工作也不会按期执行。

应用代码优先使用 `asyncio.run()`、`TaskGroup`、`timeout()` 等高层 API，不要手动操作事件循环；在已有异步框架（如 FastAPI）中，不要再次调用 `asyncio.run()`。

### 6.2 顺序等待和并发等待

```python
from __future__ import annotations

import asyncio
import time


async def fake_http(name: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return f"{name}: ok"


async def sequential() -> list[str]:
    return [
        await fake_http("A", 0.3),
        await fake_http("B", 0.2),
    ]


async def concurrent() -> list[str]:
    return await asyncio.gather(
        fake_http("A", 0.3),
        fake_http("B", 0.2),
    )


async def main() -> None:
    started = time.perf_counter()
    print(await sequential())
    print(f"顺序耗时约 {time.perf_counter() - started:.1f}s")

    started = time.perf_counter()
    print(await concurrent())
    print(f"并发耗时约 {time.perf_counter() - started:.1f}s")


asyncio.run(main())
```

这里并发版本大约耗时最长的 0.3 秒，而不是总和 0.5 秒；它只是在两个**可等待的模拟 I/O**之间重叠等待。真实网络服务可能受带宽、连接池、远端限流和服务端排队影响，吞吐不一定线性增加。

### 6.3 `gather` 与 `TaskGroup`

`asyncio.gather` 适合收集一组结果，并按传入顺序返回：

```python
import asyncio


async def task_a() -> str:
    await asyncio.sleep(0.05)
    return "A"


async def task_b() -> str:
    await asyncio.sleep(0.01)
    return "B"


async def main() -> None:
    results = await asyncio.gather(task_a(), task_b())
    print(results)  # ['A', 'B']：按传入顺序，而不是完成顺序


asyncio.run(main())
```

默认情况下，一个 awaitable 抛出异常时，异常会传给调用者；其他 awaitable 不会自动因为这个异常而全部取消。需要把失败当作结果时可以使用 `return_exceptions=True`，但必须明确区分异常对象和正常返回值：

```python
import asyncio


async def call_tool(name: str) -> str:
    await asyncio.sleep(0.01)
    if name == "search":
        raise RuntimeError("search unavailable")
    return f"{name}: ok"


async def main() -> None:
    results = await asyncio.gather(
        call_tool("search"),
        call_tool("weather"),
        return_exceptions=True,
    )
    for result in results:
        if isinstance(result, asyncio.CancelledError):
            print("工具被取消")
        elif isinstance(result, Exception):
            print("工具失败", result)
        else:
            print("工具成功", result)


asyncio.run(main())
```

Python 3.11 的 `TaskGroup` 更适合结构化并发：离开 `async with` 前会等待所有子任务；一个子任务抛出 `CancelledError` 之外的异常时，默认取消同组其他任务，并在退出时汇总异常。`KeyboardInterrupt` 和 `SystemExit` 有特殊的重新抛出规则，不应把它们当作普通业务异常处理。

```python
import asyncio


async def call(name: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return f"{name}: ok"


async def main() -> None:
    async with asyncio.TaskGroup() as group:
        search_task = group.create_task(call("search", 0.2))
        weather_task = group.create_task(call("weather", 0.1))

    # 上下文退出后，两个任务都已结束，可以安全读取结果。
    print(search_task.result(), weather_task.result())


asyncio.run(main())
```

`gather` 和 `TaskGroup` 的失败语义不要混用：

| API | 结果顺序 | 一个子任务失败时 | 适用倾向 |
| --- | --- | --- | --- |
| `gather(..., return_exceptions=False)` | 输入顺序 | 立即把第一个异常交给调用者，其他任务通常继续 | 需要快速拿到异常，且能管理剩余任务 |
| `gather(..., return_exceptions=True)` | 输入顺序 | 把异常放进结果列表 | 独立工具调用，失败也要收集部分结果 |
| `TaskGroup` | 通过保存的 Task 读取 | 子任务出现非取消异常时取消同组其他任务，退出时通常抛出异常组 | 结构化生命周期、失败即停止 |

如果选择 `gather` 的默认行为，调用方必须考虑“异常已经返回，但其他任务仍在运行”的窗口。不要在捕获异常后才调用 `gather_task.cancel()`，因为此时 gather 可能已经标记完成；要么在每个子任务内部把异常转成结果，要么使用 `TaskGroup`。

`TaskGroup` 的异常可以用 `except*` 按类型拆分：

```python
from __future__ import annotations

import asyncio


async def one() -> None:
    await asyncio.sleep(0)
    raise ValueError("参数错误")


async def two() -> None:
    await asyncio.sleep(0)
    raise ConnectionError("上游断开")


async def main() -> None:
    try:
        async with asyncio.TaskGroup() as group:
            group.create_task(one())
            group.create_task(two())
    except* ValueError as errors:
        print("可反馈给模型的参数错误数:", len(errors.exceptions))
    except* ConnectionError as errors:
        print("可重试的连接错误数:", len(errors.exceptions))


asyncio.run(main())
```

真实 Agent 中还要决定：失败工具是返回 `ToolResult(ok=False)`，还是让同组任务全部取消。这个决定应写进协议和测试，而不是依赖某个并发 API 的默认行为。

对于 Agent 工具调用，是否“一个工具失败就取消全部”是业务决策：强依赖链适合 `TaskGroup` 的 fail-fast；互相独立的工具可在每个任务内部捕获异常，返回统一的 `ToolResult`，避免一项失败丢掉其他结果。

### 6.4 事件循环到底在做什么

事件循环可以看作一个“就绪队列 + I/O 监听器 + 定时器”的循环：

```text
取出一个就绪 Task
    ↓
运行到 return / 异常 / await
    ├─ await 未完成的 I/O/Future → 注册回调，Task 暂停
    ├─ await 已完成的对象       → Task 继续推进
    └─ return/异常               → Task 完成
    ↓
处理已就绪 socket、定时器和其他回调，再取下一个 Task
```

一个事件循环线程一次只运行一个 Task。网络系统调用在内核中等待时，线程不必忙等；I/O 就绪后，事件循环恢复对应 Task。`await` 本身不是“开新线程”，而是告诉当前协程“我暂时没有可执行的工作”。

应用入口使用 `asyncio.run(main())` 创建并关闭循环；FastAPI/Uvicorn 已经拥有事件循环，路由中只需 `await`，不要再次调用 `asyncio.run()`。同一线程中不能嵌套运行两个正在运行的事件循环。

### 6.5 Future 是如何被完成的

Future 是一个低层级的状态容器：等待中 → `set_result`/`set_exception` → 完成。应用通常不手动创建 Future，但理解它有助于看懂异步客户端和 `run_in_executor`：

```python
from __future__ import annotations

import asyncio


async def future_demo() -> str:
    loop = asyncio.get_running_loop()
    future: asyncio.Future[str] = loop.create_future()
    loop.call_later(0.05, future.set_result, "I/O ready")
    return await future


async def main() -> None:
    print(await future_demo())


asyncio.run(main())
```

真实 I/O 库会在 socket 可读时完成 Future；线程池桥接则在工作线程结束后把结果安全地投递回事件循环。不要在另一个线程直接调用 `future.set_result`，需要使用 `loop.call_soon_threadsafe`。

---

## 7. 超时、取消与资源清理

### 7.1 `asyncio.timeout` 与 `wait_for`

Python 3.11 推荐用 `asyncio.timeout()` 上下文管理器表达一个作用域的截止时间：

```python
import asyncio


async def long_call() -> str:
    await asyncio.sleep(2)
    return "finished"


async def main() -> None:
    try:
        async with asyncio.timeout(0.5):
            result = await long_call()
    except TimeoutError:
        # TimeoutError 在 timeout 上下文外捕获。
        print("请求超时")
    else:
        print(result)


asyncio.run(main())
```

`asyncio.wait_for(aw, timeout)` 更适合对单个 awaitable 加超时；超时发生时会取消目标 Task，并等待其完成取消流程，因此总耗时可能略超过给定秒数。`asyncio.timeout()` 也通过取消实现，但把取消转换为外部可捕获的 `TimeoutError`。两个 API 都不能强制停止一个不合作的同步函数。

### 7.2 取消是协作式的

取消 Task 会在下一个可取消的 `await` 处抛出 `asyncio.CancelledError`。应在 `finally` 中清理资源，并通常在清理完成后继续抛出取消异常：

```python
import asyncio


class FakeConnection:
    async def request(self) -> str:
        await asyncio.sleep(1)
        return "ok"

    async def close(self) -> None:
        print("connection closed")


async def use_connection() -> None:
    connection = await open_connection()
    try:
        await connection.request()
    except asyncio.CancelledError:
        # 可记录“客户端取消”，但不要把取消静默吞掉。
        raise
    finally:
        await connection.close()


async def open_connection() -> FakeConnection:
    await asyncio.sleep(0)
    return FakeConnection()


async def main() -> None:
    task = asyncio.create_task(use_connection())
    await asyncio.sleep(0.01)
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)


asyncio.run(main())
```

不要在宽泛的 `except Exception` 中处理取消逻辑；`CancelledError` 直接继承自 `BaseException`，但显式捕获后如果不重新抛出，会破坏 `TaskGroup` 和超时管理器的取消语义。只有在确实需要抑制取消时，才使用 `contextlib.suppress(asyncio.CancelledError)`，并确认调用方知道任务已经被取消。

### 7.3 预算式超时

Agent 往往有总预算和子调用预算：

```python
import asyncio


async def agent_turn() -> str:
    # 整个回合最多 10 秒；内部工具还可以有各自更短的 timeout。
    async with asyncio.timeout(10):
        return await call_model_and_tools()


async def call_model_and_tools() -> str:
    async with asyncio.timeout(3):
        await asyncio.sleep(0.1)
    return "answer"
```

子超时不应无限叠加到大于总预算。生产代码还应把模型 SDK、HTTP 客户端、数据库驱动自身的连接和读取超时配置好，因为外层协程超时未必能中断底层阻塞调用。

### 7.4 `shield`：保护一个不可中断的收尾动作

`asyncio.shield(awaitable)` 只保护内部 awaitable 不因**外层 Task 被取消**而取消；外层等待表达式仍会抛出 `CancelledError`。它不应被当成“忽略客户端取消”的通用开关，因为被 shield 的工作可能继续占用资源。

下面的示例演示一种严格受限的策略：外层请求被取消后，仍等待一个很短的幂等提交完成，但清理完成后继续向调用方传播取消状态。代码保存了内部 Task 的强引用：

```python
from __future__ import annotations

import asyncio


async def commit_idempotently() -> str:
    await asyncio.sleep(0.08)
    return "committed"


async def request() -> str:
    commit_task = asyncio.create_task(commit_idempotently(), name="commit")
    try:
        return await asyncio.shield(commit_task)
    except asyncio.CancelledError:
        # 外层请求已取消；这里选择等待短小的幂等收尾完成。
        result = await commit_task
        print("请求取消，但提交结果:", result)
        raise


async def main() -> None:
    request_task = asyncio.create_task(request(), name="request")
    await asyncio.sleep(0.01)
    request_task.cancel()
    try:
        await request_task
    except asyncio.CancelledError:
        print("提交已收尾，请求仍保持取消状态")


asyncio.run(main())
```

只有在业务明确要求“即使调用方消失也必须完成”的短小、幂等收尾时才使用 `shield`。模型生成、普通搜索和大文件传输通常应随请求取消；若任务必须脱离请求继续，应交给持久化任务队列。

---

## 8. 限流、信号量与队列背压

### 8.1 `Semaphore` 限制并发量

`gather` 一次创建几千个 Task 可能耗尽连接池、内存或远端配额。用 `Semaphore` 控制同时运行的工具调用：

```python
import asyncio


async def call_remote(name: str, limit: asyncio.Semaphore) -> str:
    async with limit:
        # 只有拿到许可后才占用远程连接/配额。
        await asyncio.sleep(0.1)
        return f"{name}: ok"


async def main() -> None:
    limit = asyncio.Semaphore(5)
    names = [f"tool-{index}" for index in range(20)]
    results = await asyncio.gather(*(call_remote(name, limit) for name in names))
    print(results)


asyncio.run(main())
```

信号量应覆盖真正消耗受限资源的部分；如果把慢速的后处理也放在 `async with` 中，会降低可用吞吐。信号量不是跨进程、跨实例的全局限流器；多副本服务要用网关、Redis 或服务商提供的配额机制。

### 8.2 `asyncio.Queue` 的生产者/消费者

队列能同时提供任务传递和背压：队列达到 `maxsize` 后，生产者在 `put` 处等待，不会无限制创建任务。

```python
import asyncio


async def producer(queue: asyncio.Queue[str]) -> None:
    for index in range(10):
        await queue.put(f"job-{index}")
    # 每个消费者都需要一个哨兵。
    for _ in range(2):
        await queue.put("STOP")


async def consumer(name: str, queue: asyncio.Queue[str]) -> None:
    while True:
        item = await queue.get()
        try:
            if item == "STOP":
                return
            await asyncio.sleep(0.05)  # 模拟处理
            print(name, item)
        finally:
            queue.task_done()


async def main() -> None:
    queue: asyncio.Queue[str] = asyncio.Queue(maxsize=3)
    async with asyncio.TaskGroup() as group:
        group.create_task(producer(queue))
        group.create_task(consumer("worker-1", queue))
        group.create_task(consumer("worker-2", queue))


asyncio.run(main())
```

如果需要等待所有任务处理完再退出，可以在合适的位置 `await queue.join()`；调用 `task_done()` 的次数必须与 `put()` 的项目数匹配，否则 `join()` 会永久等待。

### 8.3 异步同步原语的边界

`asyncio.Lock`、`asyncio.Event`、`asyncio.Semaphore` 和 `asyncio.Condition` 只协调**同一事件循环中的协程**，不是线程安全或进程安全的。反过来，`threading.Lock` 不能在协程中直接等待；获取它可能阻塞整个事件循环。跨线程/跨进程通信必须选对应的线程/进程原语或外部协调服务。

### 8.4 限流和背压的层次

Semaphore 只限制“已经创建并正在等待资源”的协程数，不能自动限制请求入口，也不能跨 Uvicorn worker 共享计数。一个完整的 Agent 服务通常有三层上限：

1. **入口上限**：限制同时处理的 HTTP/WebSocket 请求数；
2. **回合上限**：限制每个 Agent 回合的工具数量、token、费用和总时间；
3. **依赖上限**：限制某个模型、数据库或工具供应商的并发和 QPS。

队列是入口和执行器之间的缓冲区。队列满时应拒绝、降级或让生产者等待，并给等待设置超时；无限队列只是把“过载”延后成内存耗尽。

```python
from __future__ import annotations

import asyncio


async def submit_with_backpressure(
    queue: asyncio.Queue[str],
    job: str,
    wait_seconds: float = 0.1,
) -> bool:
    try:
        async with asyncio.timeout(wait_seconds):
            await queue.put(job)
    except TimeoutError:
        # 队列持续满时，调用方可以返回 429/503 或进入降级路径。
        return False
    return True


async def main() -> None:
    queue: asyncio.Queue[str] = asyncio.Queue(maxsize=1)
    await queue.put("existing")
    print(await submit_with_backpressure(queue, "new"))  # False


asyncio.run(main())
```

`put_nowait()`/`get_nowait()` 适合明确的“立即成功或失败”语义；默认 `put()`/`get()` 适合需要等待的流水线。每个取消路径都要思考队列中的任务是否需要重新入队、标记失败或补偿。

---

## 9. 将阻塞代码桥接到异步程序

### 9.1 `asyncio.to_thread`

没有异步接口的同步 SDK（例如只提供阻塞式 HTTP 客户端）不能直接在 `async def` 中调用。使用 `to_thread` 把它交给默认线程池：

```python
import asyncio
import time


def sync_search(query: str) -> str:
    time.sleep(0.5)
    return f"{query}: result"


async def search(query: str) -> str:
    return await asyncio.to_thread(sync_search, query)


async def main() -> None:
    results = await asyncio.gather(
        search("python"),
        search("agent"),
    )
    print(results)


asyncio.run(main())
```

`to_thread` 主要解决阻塞 I/O。由于默认 CPython 的 GIL，纯 Python CPU 函数放到线程通常不能实现多核并行；需要 CPU 并行时考虑 `ProcessPoolExecutor` 或能释放 GIL 的库。注意线程池也有大小上限，应该为底层客户端设置超时和并发限制。

`to_thread` 返回的协程被取消时，等待方会尽快收到 `CancelledError`，但已经开始执行的同步函数通常仍会在线程中继续运行。要让它真正尽早停止，函数本身需要接受停止事件，或调用底层客户端的取消/超时 API：

```python
from __future__ import annotations

import asyncio
import threading


def sync_poll(stop: threading.Event) -> str:
    while not stop.wait(0.02):
        pass
    return "stopped cooperatively"


async def main() -> None:
    stop = threading.Event()
    task = asyncio.create_task(asyncio.to_thread(sync_poll, stop))
    await asyncio.sleep(0.05)
    stop.set()
    print(await task)


asyncio.run(main())
```

为了避免留下无法停止的线程，生产代码应把停止信号放进同步函数的 API 设计；若第三方库不支持取消，使用进程隔离通常比线程强杀更可控。

### 9.2 `run_in_executor`

需要指定自定义线程池、进程池或兼容旧代码时，可以使用：

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor


def legacy_call(value: int) -> int:
    return value * 2


async def main() -> None:
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_workers=4) as pool:
        result = await loop.run_in_executor(pool, legacy_call, 21)
    print(result)


asyncio.run(main())
```

不要在每次请求中创建线程池；在应用生命周期内复用有限的执行器，或者使用框架/库提供的连接池。进程池函数同样要能被 pickle，并注意应用服务器多进程会造成池的乘法增长。

### 9.3 资源清理

异步资源（HTTP 客户端、数据库连接、文件、流）通常支持异步上下文管理器：

```python
import asyncio
from contextlib import asynccontextmanager


class FakeClient:
    async def __aenter__(self) -> "FakeClient":
        print("open")
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        print("close")

    async def get(self, url: str) -> str:
        await asyncio.sleep(0)
        return url


async def main() -> None:
    async with FakeClient() as client:
        print(await client.get("https://example.com"))


asyncio.run(main())
```

在 FastAPI 中通常在 lifespan 中创建一个共享的异步客户端，在 lifespan 退出时关闭，而不是每个请求重复创建连接池。若一次要管理多个资源，可使用 `contextlib.AsyncExitStack` 集中注册清理动作。

### 9.4 异步资源的所有权和关闭顺序

异步资源要有明确的 owner：谁创建，谁关闭；谁把连接借给工具，谁在取消或异常后归还。推荐把资源生命周期画成嵌套关系：

```text
应用 lifespan
  └─ HTTP client / DB pool
       └─ Agent 回合
            └─ 单次工具请求 / 响应流
```

内层工具失败时只关闭自己的响应；请求取消时先停止上游流，再释放工具级响应，最后由应用退出关闭共享池。不要在工具函数里关闭由 lifespan 创建的共享客户端，否则另一个并发请求会突然收到“client is closed”。

```python
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator


class FakeClient:
    async def aclose(self) -> None:
        print("client closed")

    async def stream(self) -> AsyncIterator[str]:
        try:
            for item in ["a", "b", "c"]:
                await asyncio.sleep(0.02)
                yield item
        finally:
            print("upstream stream closed")


@asynccontextmanager
async def lifespan() -> AsyncIterator[FakeClient]:
    client = FakeClient()
    try:
        yield client
    finally:
        await client.aclose()


async def consume(client: FakeClient) -> None:
    async for item in client.stream():
        print(item)


async def main() -> None:
    async with lifespan() as client:
        await consume(client)


asyncio.run(main())
```

`finally` 即使上层抛出异常或取消也会执行；如果清理本身需要等待，给清理设置合理预算，并避免在清理代码里无条件吞掉取消。对必须完成的极短提交动作，可以结合上一节的 `shield`，但要记录它可能延长关闭时间。

---

## 10. 调试和观测异步程序

### 10.1 开启 asyncio 调试

开发环境可以使用：

```bash
PYTHONASYNCIODEBUG=1 python app.py
```

或者：

```python
import asyncio


async def main() -> None:
    await asyncio.sleep(0)


asyncio.run(main(), debug=True)
```

调试模式可以帮助发现未等待的协程、较慢的回调和错误的事件循环使用。生产环境不要仅依赖 debug 模式，应该记录请求 ID、Task 名称、工具名、耗时、超时和取消原因，并避免记录密钥、完整提示词和敏感用户数据。

### 10.2 常见诊断方法

- 警告 `coroutine was never awaited`：检查调用处是否遗漏 `await` 或 `create_task`。
- 请求偶发全部变慢：搜索事件循环线程中的 `time.sleep`、同步 HTTP、同步文件/数据库调用和大段 CPU 循环。
- Task 泄漏：保存创建的 Task 引用，在应用关闭时取消并等待；不要创建“失联”的后台 Task。
- 取消没有生效：确认代码在可取消的 `await` 处让出控制权；底层阻塞调用需要库级 timeout 或放到线程/进程。
- 任务完成顺序和结果顺序不同：`as_completed` 按完成顺序，`gather` 按输入顺序。

可用 `asyncio.current_task().get_name()`、`asyncio.all_tasks()`（调试用途）和应用级指标观察任务生命周期。

### 10.3 观测一个 Agent 回合的时序

不要只记录“请求开始/结束”两个时间点。至少给每个回合和子调用带上 `run_id`、`task_name`、`tool_name`、`started_at`、`finished_at`、状态和错误类别：

```text
run.start
  ├─ model.start → model.done / model.timeout
  ├─ tool.search.start → tool.search.done / failed / cancelled
  ├─ tool.weather.start → tool.weather.done / timeout
  └─ run.done / run.timeout / run.cancelled / run.step_limit
```

用单调时钟（`time.perf_counter()` 或 `loop.time()`）计算耗时，不要用系统墙上时钟做时长相减；墙上时钟可能因校时发生跳变。日志字段和用户可见错误分开：日志保留足够诊断的信息，返回值只暴露稳定、脱敏的错误码。

可以用 `asyncio.all_tasks()` 定位测试结束后仍存活的 Task：

```python
from __future__ import annotations

import asyncio


async def inspect_tasks() -> None:
    current = asyncio.current_task()
    tasks = [task for task in asyncio.all_tasks() if task is not current]
    for task in tasks:
        print(task.get_name(), task.done(), task.cancelling())


async def main() -> None:
    background = asyncio.create_task(asyncio.sleep(0.2), name="temporary")
    await inspect_tasks()
    await background


asyncio.run(main())
```

调试代码不要在生产请求路径上遍历所有 Task；生产使用指标、trace 和采样日志。若启用 `PYTHONASYNCIODEBUG=1`，同时关注慢回调、未等待协程和关闭阶段的资源警告。

---

## 11. AI Agent 实战：并行工具调用、流式响应与取消

### 11.1 可控的并行工具调用

下面的执行器模拟三个工具，具备：每个工具独立超时、全局并发上限、失败转为结构化结果、总预算和结构化输出。它不接真实模型，便于直接运行：

```python
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Awaitable, Callable


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class ToolResult:
    name: str
    ok: bool
    data: Any = None
    error: str | None = None


Tool = Callable[[dict[str, Any]], Awaitable[Any]]


async def fake_search(arguments: dict[str, Any]) -> dict[str, Any]:
    await asyncio.sleep(0.2)
    return {"query": arguments["query"], "items": ["result-1", "result-2"]}


async def fake_weather(arguments: dict[str, Any]) -> dict[str, Any]:
    await asyncio.sleep(0.1)
    return {"city": arguments["city"], "temperature": 26}


class ToolRunner:
    def __init__(self, tools: dict[str, Tool], max_concurrency: int = 4) -> None:
        self.tools = tools
        self.limit = asyncio.Semaphore(max_concurrency)

    async def run_one(self, call: ToolCall, timeout_seconds: float = 1.0) -> ToolResult:
        tool = self.tools.get(call.name)
        if tool is None:
            return ToolResult(call.name, False, error="unknown tool")

        try:
            async with self.limit:
                async with asyncio.timeout(timeout_seconds):
                    data = await tool(call.arguments)
            return ToolResult(call.name, True, data=data)
        except TimeoutError:
            return ToolResult(call.name, False, error="tool timeout")
        except asyncio.CancelledError:
            # 让上层总预算或客户端取消正常传播。
            raise
        except Exception:
            # 详细异常仅进入受控、脱敏的内部日志；不直接反馈给模型或客户端。
            return ToolResult(call.name, False, error="tool execution failed")

    async def run_many(self, calls: list[ToolCall]) -> list[ToolResult]:
        # gather 保持调用顺序；每个 run_one 已将普通工具异常转为结果。
        return await asyncio.gather(*(self.run_one(call) for call in calls))


async def main() -> None:
    runner = ToolRunner({"search": fake_search, "weather": fake_weather})
    calls = [
        ToolCall("search", {"query": "asyncio"}),
        ToolCall("weather", {"city": "Shanghai"}),
        ToolCall("not_registered", {}),
    ]
    async with asyncio.timeout(3):  # Agent 回合总预算
        for result in await runner.run_many(calls):
            print(result)


asyncio.run(main())
```

这个示例把单工具 timeout 放在获取 Semaphore 之后，因此“等待并发许可”的时间不计入该工具预算；如果排队本身也必须受预算约束，可以把 `asyncio.timeout()` 放在 `async with self.limit` 外层，并为等待许可超时返回单独的结果。生产 Agent 通常同时记录排队耗时和执行耗时，否则只看工具执行时间会低估过载。

真实 Agent 还应加入：工具参数模型校验、工具白名单、幂等键、重试退避、远端服务的速率限制、调用链追踪、结果大小限制和敏感数据脱敏。不要为了“并行”而并行：有依赖关系的工具（先查订单再查物流）必须按依赖图顺序执行。

### 11.2 流式响应：异步生成器

异步生成器逐步产生事件，让客户端在 Agent 仍工作时就收到 token、工具状态或最终结果：

```python
from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator


async def agent_stream(prompt: str) -> AsyncIterator[str]:
    try:
        yield "event: status\ndata: thinking\n\n"
        await asyncio.sleep(0.1)
        yield "event: tool\ndata: search started\n\n"
        await asyncio.sleep(0.2)
        for token in ["根据", "工具结果", "，答案是", "……"]:
            yield f"event: token\ndata: {token}\n\n"
            await asyncio.sleep(0.05)
        yield "event: done\ndata: true\n\n"
    except asyncio.CancelledError:
        # 客户端断开或请求超时：清理上游模型流/工具资源后传播取消。
        raise


async def consume() -> None:
    async for event in agent_stream("查询天气"):
        print(event, end="")


asyncio.run(consume())
```

Web 层可以把它包装成 SSE 或 `StreamingResponse`。流式协议要定义事件类型、序号、结束标记、错误格式和重连策略；不要假设每个网络 chunk 恰好对应一个 token。生成器被取消时必须关闭上游连接，避免客户端离开后模型调用仍计费。

### 11.3 客户端断开、取消和后台任务

在 Web 框架中，客户端断开通常表现为请求 Task 被取消或发送失败。将 Agent 回合直接绑定到请求生命周期时，收到取消就应停止无意义的模型/工具调用；若业务要求“即使客户端离开也继续”，应把任务交给持久化任务队列并返回任务 ID，而不是在请求中创建一个无人管理的 Task。

后台 Task 的最小管理模式：

```python
import asyncio


async def run_background() -> None:
    try:
        await asyncio.sleep(10)
    finally:
        print("background cleanup")


async def owner() -> None:
    task = asyncio.create_task(run_background(), name="agent-background")
    try:
        await asyncio.sleep(0.1)
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)


asyncio.run(owner())
```

### 11.4 Agent 回合的完整状态机

一个可审计的 Agent 回合至少要经过这些状态：

```text
RECEIVED
   ↓ 校验输入、建立 run_id、计算截止时间
PLANNING
   ↓ 调模型，等待模型 I/O
DECIDED ───────────────→ FINAL
   ↓ 工具名/参数/schema/权限检查
TOOL_RUNNING
   ├─ 成功 → TOOL_SUCCEEDED ─┐
   ├─ 可修正错误 → TOOL_FAILED ─┤→ 把有限结果写回上下文
   ├─ 超时 → TOOL_TIMED_OUT ───┤
   └─ 取消 → CANCELLED         │
                               └→ 回到 PLANNING（受 max_steps 限制）
```

请求级总预算应从入口传入，而不是每个工具自己重新开始计时。可以用 `loop.time()` 计算剩余预算：

```python
from __future__ import annotations

import asyncio


async def model_call(remaining: float) -> str:
    async with asyncio.timeout(remaining):
        await asyncio.sleep(0.02)
        return "model decision"


async def tool_call(remaining: float) -> str:
    async with asyncio.timeout(remaining):
        await asyncio.sleep(0.02)
        return "tool result"


async def run_turn(total_seconds: float = 0.2) -> str:
    loop = asyncio.get_running_loop()
    deadline = loop.time() + total_seconds

    remaining = deadline - loop.time()
    decision = await model_call(remaining)
    del decision

    remaining = deadline - loop.time()
    if remaining <= 0:
        raise TimeoutError("agent budget exhausted before tool")
    result = await tool_call(remaining)
    return result


asyncio.run(run_turn())
```

生产实现还应把清理时间、序列化响应时间和网关截止时间纳入预算；子调用可以有更短的硬上限，但不能重新获得已经消耗的总预算。预算耗尽时要记录停止原因，不能把它伪装成模型回答。

### 11.5 并行工具的依赖图和结果合并

模型一次返回多个工具调用时，可以先构建依赖图：

```text
用户问题
  ├─ search(city) ──┐
  ├─ weather(city) ──┼─→ 汇总器
  └─ account(user) ──┘
```

只有同一层、互不依赖且权限允许的节点才放进一个 `TaskGroup`。结果合并时保留调用 ID、输入摘要、成功/失败、来源和耗时；不要只把多个字符串拼起来，否则后续模型难以区分哪个结果对应哪个调用。写操作通常要单独串行化，或用幂等键和业务事务保护。

### 11.6 流式输出的事件时序

流式 Agent 不只是“把字符串分片”：

```text
stream.open
  → run.started
  → model.delta*                 # 可选
  → tool.started
  → tool.completed / tool.failed
  → message.delta*
  → run.completed / run.failed / run.cancelled
  → stream.close
```

事件应包含 `run_id`、递增序号、事件类型和可校验的数据。客户端断开时，服务端要取消上游模型和工具；如果业务要求断开后继续，改用任务 ID + 持久化状态，而不是让一个无人管理的请求 Task 继续运行。SSE 已发送响应头后无法再修改 HTTP 状态码，所以超时通常表现为一个结构化 `error` 事件。

---

## 12. 场景选择表

| 问题 | 首选 | 选择理由 | 注意事项 |
| --- | --- | --- | --- |
| 同时请求 100 个异步 HTTP 接口 | `asyncio` + 异步 HTTP 客户端 | 一个线程管理大量等待 | 连接池、Semaphore、超时、远端限流 |
| 只有同步 HTTP/数据库 SDK | `asyncio.to_thread` 或线程池 | 避免阻塞事件循环 | 线程池大小、SDK 线程安全、库级 timeout |
| 纯 Python 大量计算 | 进程池/多进程 | 每个进程有独立解释器，可利用多核 | pickle、内存、启动和 IPC 成本 |
| NumPy/Pandas 重计算 | 先基准测试；线程或进程 | 底层实现可能释放 GIL | 线程安全、BLAS 自带线程造成过量并发 |
| 任务有严格先后依赖 | 顺序 `await` 或依赖图 | 并行会改变语义 | 只并行真正独立的分支 |
| 长时间任务且客户端不必等待 | 外部任务队列/工作进程 | 请求和任务生命周期解耦 | 持久化状态、重试、幂等、任务取消 |
| 共享小状态的后台 I/O | 线程 + 锁/队列 | 线程可复用同步库 | 竞态、死锁、优雅退出 |
| 跨实例全局限流 | 网关/Redis/服务商配额 | 本地 Semaphore 只作用于一个进程 | 分布式一致性和故障恢复 |

决策顺序建议：先确认是否能用异步库；再确认任务是等待还是计算；然后估算并发上限、生命周期和取消语义；最后基准测试。不要仅凭“async”“thread”或“process”这个词判断速度。

---

## 13. 常见坑清单

1. **在异步端点里调用 `time.sleep()`。** 改用 `await asyncio.sleep()`；真实阻塞库用 `to_thread`。
2. **忘了 `await`。** 协程对象不会自动运行，通常会出现运行时警告。
3. **无界 `create_task`。** 用户输入可以触发成千上万个任务，需用 Semaphore、Queue 或批量窗口。
4. **把 `asyncio.Lock` 当成线程锁。** 它只保护同一事件循环中的协程。
5. **吞掉 `CancelledError`。** 会导致超时、TaskGroup 和服务关闭异常；清理后通常要重新抛出。
6. **用线程强制杀任务。** Python 没有安全的线程强杀 API；设计可取消函数或将任务隔离到可回收进程。
7. **进程池传递不可 pickle 的对象。** 把函数放在模块顶层，参数/返回值使用简单数据结构。
8. **在每个请求创建客户端和线程池。** 这会浪费连接、线程和握手成本；在应用生命周期中复用并在退出时关闭。
9. **把本地并发当作远端容量。** 并发调用可能触发模型供应商 429、连接池耗尽或费用失控。
10. **只测平均耗时。** Agent 更应观察 p95/p99、取消率、超时率、队列长度、CPU 和内存。

---

## 练习题

1. **同步改异步：** 用 `asyncio.gather` 改写两个顺序 `time.sleep` 的模拟 HTTP 调用，并用 `perf_counter` 比较两种写法；解释为什么总耗时接近最大等待时间。
2. **并发窗口：** 实现一个 `map_with_limit(items, limit, worker)`，要求最多同时运行 `limit` 个协程，并保持结果顺序；使用 Semaphore 或 Queue 均可。
3. **超时与取消：** 写一个 Agent 回合函数，设置总超时 2 秒、每个工具超时 0.5 秒；让一个工具故意卡住，验证其他工具结果是否仍能返回。
4. **可靠清理：** 实现一个支持 `async with` 的假 HTTP 客户端，统计打开/关闭次数；在任务被取消时确认关闭动作仍执行。
5. **阻塞桥接：** 用 `asyncio.to_thread` 并行调用两个同步函数；再把其中一个改成纯 Python CPU 循环，说明为什么它不一定获得多核加速，并用进程池做对比。
6. **生产者/消费者：** 用 `asyncio.Queue(maxsize=2)` 写三个生产者和两个消费者，加入哨兵与 `queue.join()`，观察生产者在队列满时如何产生背压。
7. **工具依赖图：** 设计“搜索城市 → 查询天气”和“读取用户配置”三个工具的依赖关系，只并行执行独立分支，最后合并结果。
8. **流式 Agent：** 用异步生成器输出 `status/tool/token/done` 四类事件；模拟客户端取消，确保上游任务收到 `CancelledError` 并完成清理。

### 练习提示与验收标准

| 练习 | 提示 | 最低验收标准 |
| --- | --- | --- |
| 1 | 用 `perf_counter`，让两个等待时间不同的任务各运行两次 | 顺序耗时接近等待之和，并发耗时接近最大等待；能解释原因 |
| 2 | 用 Semaphore 保护 worker，或用固定数量消费者读取 Queue | 任意时刻运行中的 worker 不超过 `limit`，结果顺序与输入一致 |
| 3 | 工具内部捕获自己的 `TimeoutError`，回合外层捕获总超时 | 单工具失败不影响独立结果；总预算耗尽时所有子 Task 都结束 |
| 4 | 在 `finally` 里递增关闭计数，并主动 `task.cancel()` | 正常、异常、取消三条路径都只关闭一次资源 |
| 5 | 先运行 I/O 版本，再运行线程和进程版本；记录 CPU/墙上时间 | 能说明 `to_thread` 的取消边界和 GIL 影响，而不是只给出快慢结论 |
| 6 | 先放满小队列，再观察 producer 的 `put` 是否等待 | `queue.join()` 能返回，消费者退出后没有 pending Task 或未匹配 `task_done()` |
| 7 | 为每个节点写输入/输出 schema，再按拓扑层调度 | 独立节点并发，依赖节点不提前执行，合并结果可追溯到调用 ID |
| 8 | 让消费方在中途取消，生成器用 `try/finally` 关闭上游 | 事件顺序正确；取消后上游任务结束且不产生“Task exception was never retrieved” |

通用自检：运行 `PYTHONASYNCIODEBUG=1`、打开日志并查看未完成 Task；再将并发数、延迟、错误和取消率写成测试断言或指标，而不是只凭一次手工输出判断正确。

---

## 小结

- 同步、并发、并行描述的是不同维度；异步通常解决 I/O 等待，不会自动让 CPU 计算更快。
- 进程提供隔离和 CPU 并行，线程适合阻塞 I/O 和同步库桥接，协程适合大量可等待的异步 I/O。
- 默认 CPython 的 GIL 限制同一解释器中纯 Python 字节码的线程并行，但不妨碍线程重叠 I/O，也不覆盖会释放 GIL 的扩展代码。
- `asyncio` 的关键是事件循环和协作式让出控制权；`async def` 本身不是性能开关。
- Agent 执行器应把并行度、总预算、子超时、取消、限流、背压、错误格式和资源清理作为一等设计对象。
- `TaskGroup` 适合结构化并发，`Semaphore` 控制并发上限，`Queue` 提供生产者/消费者背压，`to_thread` 隔离阻塞同步调用。

## 延伸阅读（官方文档）

- [Python 3.11 `asyncio` 总览](https://docs.python.org/3.11/library/asyncio.html)
- [Python 3.11 Coroutines and Tasks](https://docs.python.org/3.11/library/asyncio-task.html)
- [Python 3.11 Event Loop](https://docs.python.org/3.11/library/asyncio-eventloop.html)
- [`threading` 标准库](https://docs.python.org/3.11/library/threading.html)
- [`concurrent.futures` 标准库](https://docs.python.org/3.11/library/concurrent.futures.html)
- [`multiprocessing` 标准库](https://docs.python.org/3.11/library/multiprocessing.html)
