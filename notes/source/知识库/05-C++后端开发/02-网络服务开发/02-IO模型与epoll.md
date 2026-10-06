# IO 模型与 epoll

## 学习目标

- 区分同步/异步与阻塞/非阻塞，不把两组概念混在一起。
- 理解 `select`、`poll`、`epoll` 的差异和适用边界。
- 掌握 epoll 的 LT、ET、`EPOLLONESHOT`、惊群问题和事件循环结构。
- 能解释 Reactor 与 Proactor 的区别。

## 核心原理

### 概念分离

阻塞/非阻塞关注调用线程是否等待资源就绪；同步/异步关注 IO 完成是谁负责推进和通知。

| 维度 | 选项 | 含义 |
| --- | --- | --- |
| 等待方式 | 阻塞 | 调用线程在资源未就绪时睡眠 |
| 等待方式 | 非阻塞 | 调用立即返回，需要之后重试 |
| 完成模型 | 同步 | 应用线程主动发起读写，内核返回结果 |
| 完成模型 | 异步 | 应用提交请求，完成后由内核/运行时通知 |

Linux 下常见的 epoll Reactor 通常是“同步非阻塞 IO”：epoll 通知 fd 可读可写，应用线程再调用 `read`/`write`。

### 用户视角与内核视角

用户态看到的是“哪些 fd 有事件”；内核态维护的是兴趣集合、就绪队列和每个 fd 对应文件对象上的回调关系。`epoll_ctl` 修改兴趣集合，`epoll_wait` 把就绪事件复制回用户态。fd 关闭、复用和连接对象销毁如果没有顺序约束，就会出现旧事件携带旧指针的问题。

事件循环的最小状态流：

```text
register interest -> epoll_wait returns events -> drain read/write -> update interest -> run timers
```

`epoll_wait` 返回 0 只是超时，不是错误；返回 -1 且 `errno=EINTR` 通常继续循环；其他错误才需要记录并考虑重建或退出。

### select、poll、epoll

| 模型 | 特点 | 典型问题 |
| --- | --- | --- |
| `select` | fd 集合用位图表达，接口历史悠久 | fd 数量限制、每次复制和遍历 |
| `poll` | 用数组表达 fd，无固定 `FD_SETSIZE` 限制 | 每次仍需线性扫描 |
| `epoll` | 内核维护兴趣集合，就绪事件返回给用户态 | 使用复杂度更高，边沿触发要求严格 drain |

epoll 的优势主要来自：

- 兴趣集合通过 `epoll_ctl` 增量维护。
- `epoll_wait` 返回就绪 fd 列表，避免每次扫描全部 fd。
- 适合大量长连接、活跃连接比例低的场景。

### select/poll/epoll 取舍

`select` 和 `poll` 在小规模工具程序中仍然有价值，接口简单、可移植性好。`epoll` 适合 Linux 大量连接服务，但它把复杂度转移到连接生命周期、边沿触发 drain、事件掩码更新和跨线程归属上。不要为了“高性能”在几十个 fd 的管理脚本里引入复杂 epoll 状态机。

### LT 与 ET

| 模式 | 行为 | 工程要求 |
| --- | --- | --- |
| LT 水平触发 | 只要 fd 仍可读/可写，下次还会通知 | 容错更好，适合初学和多数业务 |
| ET 边沿触发 | 状态从不可用变可用时通知一次 | fd 必须非阻塞，读写直到 `EAGAIN` |

ET 模式常见 bug：收到一次可读事件只读一小段，缓冲区仍有数据，但之后没有新边沿，连接就“卡住”。

### RDHUP、HUP、ERR 的处理顺序

`EPOLLRDHUP` 表示对端关闭了写方向，常用于发现半关闭；`EPOLLHUP` 和 `EPOLLERR` 可能与可读事件同时返回。稳妥顺序通常是先 drain 已到达数据，再读取 `SO_ERROR`，最后根据连接状态关闭或进入半关闭。直接看到 HUP 就释放对象，可能丢掉内核缓冲区里已经收到但未处理的数据。

### EPOLLONESHOT

`EPOLLONESHOT` 表示事件触发一次后自动禁用该 fd 的事件，需要处理完后用 `epoll_ctl(..., EPOLL_CTL_MOD, ...)` 重新启用。

它常用于多线程 Reactor，避免同一个连接被多个线程同时处理。但它不是自动并发安全：连接对象、输出缓冲区和关闭流程仍需要清晰的所有权规则。

### ONESHOT 的重新武装

使用 `EPOLLONESHOT` 后，每次处理完事件都要 `EPOLL_CTL_MOD` 重新启用。重新武装必须在连接状态、输入输出缓冲区和关闭标志都更新之后进行，否则可能漏事件或让另一个线程拿到过期状态。若处理过程中决定关闭，应先从 epoll 删除或保证后续事件不会再访问对象。

### 惊群

惊群指多个线程或进程同时等待同一类事件，但只有一个能真正处理，其他被唤醒后又失败或无事可做。

常见来源：

- 多进程/多线程同时 `accept` 同一个监听 fd。
- 多线程等待同一个 epoll 实例。
- 没有合理分配连接归属，导致跨线程争抢。

Linux 提供了 `EPOLLEXCLUSIVE` 等机制缓解部分 accept 惊群，实际行为以 `epoll_ctl(2)` 文档和目标内核为准。工程上更常见的方案是一个 acceptor 接入后分发到固定 IO 线程。

### Reactor 与 Proactor

| 模型 | 核心思想 | 应用做什么 |
| --- | --- | --- |
| Reactor | 就绪通知 | 收到可读/可写后自己执行读写 |
| Proactor | 完成通知 | 提交异步 IO，请求完成后处理结果 |

epoll 更自然地实现 Reactor。Linux `io_uring` 可以支持更接近 Proactor 的完成模型，但具体能力、限制和内核版本相关，使用前应查官方文档。

### Reactor 数据流

一个 Reactor 服务的职责不是只调用 `epoll_wait`，还包括定时器、跨线程唤醒和背压：

```text
fd event -> Connection::handleEvent -> read/write buffer -> Codec -> callback
timer event -> close idle / retry connect / deadline
wakeup event -> run queued cross-thread functors
```

这样拆分后，业务线程不用直接碰 fd；它只把结果投递回 IO 线程，IO 线程按连接状态决定是否还能发送。

## 工程实践/示例

### Reactor 事件循环伪代码

```cpp
while (running) {
    int n = epoll_wait(epollFd, events, maxEvents, timeoutMs);
    for (int i = 0; i < n; ++i) {
        auto* conn = static_cast<Connection*>(events[i].data.ptr);

        auto flags = events[i].events;
        if (flags & EPOLLIN) {
            conn->readUntilEagain();
        }
        if (!conn->closed() && (flags & EPOLLOUT)) {
            conn->writeUntilEagain();
        }
        // HUP/RDHUP 可能与可读数据同时出现：先 drain，再更新半关闭状态。
        if (!conn->closed() && (flags & (EPOLLHUP | EPOLLRDHUP))) {
            conn->markReadHalfClosed();  // 对端关闭发送方向，本端读方向将到达 EOF
        }
        if (!conn->closed() && (flags & EPOLLERR)) {
            conn->recordSocketError();  // 用 SO_ERROR 读取并记录具体错误
            conn->close();
        }
        if (!conn->closed()) {
            conn->refreshInterest();
        }
    }
    timerQueue.runExpired();
}
```

`EPOLLHUP`/`EPOLLRDHUP` 可能与 `EPOLLIN` 同时返回。若协议允许 TCP 半关闭，应该先读取已经到达的数据，再把对端读方向标为关闭，并由连接状态机决定排空写缓冲还是立即关闭；不要看到 HUP 就无条件丢弃未读数据。`EPOLLERR` 的具体错误可通过 `getsockopt(fd, SOL_SOCKET, SO_ERROR, ...)` 获取。

### ET 读循环要点

```cpp
void readUntilEagain(int fd, std::string& input) {
    char buf[4096];
    while (true) {
        ssize_t n = ::read(fd, buf, sizeof(buf));
        if (n > 0) {
            input.append(buf, static_cast<size_t>(n));
        } else if (n == 0) {
            throw PeerClosed{};
        } else if (errno == EINTR) {
            continue;
        } else if (errno == EAGAIN || errno == EWOULDBLOCK) {
            break;
        } else {
            throw IoError{};
        }
    }
}
```

### 可写事件不要常开

socket 大多数时候都是可写的。如果一直监听 `EPOLLOUT`，事件循环会被无意义唤醒。常见策略：

- 输出缓冲区为空：只监听读事件。
- 有未写完数据：打开写事件。
- 写完后：关闭写事件。

## 故障排查/观测

### epoll 空转和漏事件

CPU 空转常见原因是永久监听 `EPOLLOUT`、错误 fd 没从 epoll 删除、定时器 timeout 计算为 0 后循环忙等。漏事件常见原因是 ET 没读到 `EAGAIN`、ONESHOT 后忘记重新 `MOD`、跨线程关闭导致旧事件访问失效对象。

建议记录：

- 每轮 `epoll_wait` 返回数量和 timeout；
- 每个事件的 mask、fd、连接 id；
- 输入/输出缓冲区长度；
- interest mask 变化；
- `EPOLLERR` 对应的 `SO_ERROR`。

### 最小复现实验

用一个慢客户端只读不写、一个快客户端持续写入，再观察可写事件、输出缓冲区和高水位行为。用 ET 模式故意每次只读 1 字节，可以稳定复现“缓冲区还有数据但不再触发”的问题。

## 推导示例

### LT 与 ET 的读路径对比

LT 下如果一次只读 1KB，而内核缓冲区还有数据，下一次 `epoll_wait` 仍会返回可读。ET 下状态变化已经发生过，如果没有读到 `EAGAIN`，后续可能没有新的边沿触发。因此 ET 的代码复杂度来自“必须 drain”，不是来自 `epoll_wait` 调用本身。

```text
LT: readable remains true -> next wait returns again
ET: not-readable -> readable edge delivered once -> must drain to EAGAIN
```

### ONESHOT 处理线程切换

多线程共享 epoll 时，ONESHOT 可以避免两个工作线程同时处理同一 fd，但处理完后谁负责重新 `MOD` 必须清楚。常见做法是：事件线程取到事件后把连接交给工作线程，工作线程处理完只投递“重新启用”到连接 owner loop，由 owner loop 统一检查状态并 rearm。

### 如何讲 epoll 的优势

不要说“epoll 一定比 select 快”。更准确的说法是：epoll 让内核维护兴趣集合，`epoll_wait` 返回就绪列表，适合大量 fd 但活跃比例低的 Linux 服务；如果 fd 数很少或每个 fd 都很活跃，收益可能不明显，复杂度仍然存在。

### 最小验收清单

- ET 读写都 drain 到 `EAGAIN`。
- `EPOLLERR/HUP/RDHUP` 有顺序处理。
- `EPOLLOUT` 只在有待写数据时开启。
- ONESHOT 处理后有明确 rearm 线程。

## 常见误区

- 把“非阻塞”叫成“异步”。epoll 通知的是就绪，不是读写完成。
- ET 模式不读到 `EAGAIN`。
- 永久监听写事件，导致 CPU 空转。
- 忽略 `EPOLLERR`/`EPOLLHUP`，连接异常后对象仍留在事件循环里。
- 多线程处理同一连接却没有所有权和串行化策略。

## 自测题

1. 同步非阻塞 IO 和异步 IO 的区别是什么？
2. epoll 为什么适合大量低活跃长连接？
3. ET 模式为什么要求 fd 非阻塞？
4. `EPOLLONESHOT` 解决什么问题，不能解决什么问题？
5. 为什么可写事件通常按需开启？

## 实践任务

- 用 epoll 写一个非阻塞 echo server。
- 分别用 LT 和 ET 模式测试，故意只读一次观察 ET 卡住现象。
- 给输出缓冲区加按需 `EPOLLOUT`。
- 用两个线程错误处理同一连接，观察竞态风险，再用 one-shot 或连接归属修正。

## 延伸阅读

- `select(2)`: https://man7.org/linux/man-pages/man2/select.2.html
- `poll(2)`: https://man7.org/linux/man-pages/man2/poll.2.html
- `epoll(7)`: https://man7.org/linux/man-pages/man7/epoll.7.html
- `epoll_ctl(2)`: https://man7.org/linux/man-pages/man2/epoll_ctl.2.html
