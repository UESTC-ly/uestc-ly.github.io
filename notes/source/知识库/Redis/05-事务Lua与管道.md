# 05-事务、Lua 与管道

> Redis 7.x 通用视角：本章关注 Redis 中“把多条命令组织起来执行”的三种方式：事务（Transaction）、Lua 脚本（Scripting）与管道（Pipeline）。它们经常被混用，但解决的问题不同。

## 学习目标

学完本篇，你应该能够：

- 区分 **事务、Lua、管道** 的用途与边界。
- 使用 `MULTI` / `EXEC` / `DISCARD` / `WATCH` 编写基本事务。
- 理解 Redis 事务的“顺序执行”与传统数据库 ACID 事务的差异。
- 使用 Lua 脚本把多步读写封装为原子操作。
- 使用 Pipeline 减少网络往返，提高批量操作吞吐量。
- 判断什么时候该用事务、Lua、管道，什么时候不该用。

## 核心概念

### 1. Redis 事务是什么

Redis 事务是一组命令的队列化执行：

```redis
MULTI
SET user:1:name "Alice"
INCR stats:user_count
EXEC
```

执行流程：

1. `MULTI` 开启事务。
2. 后续命令不立即执行，而是进入队列，通常返回 `QUEUED`。
3. `EXEC` 提交事务，Redis 按顺序执行队列中的命令。
4. `DISCARD` 放弃事务队列。

Redis 事务保证：

- 队列中的命令在 `EXEC` 后按顺序连续执行。
- 执行期间不会穿插其他客户端命令。
- Redis 不提供传统关系型数据库那种自动回滚机制。

> 记忆：Redis 事务更像“命令批次的原子排队执行”，不是完整的数据库事务系统。

### 2. 事务中的错误

Redis 事务错误分两类：

#### 入队错误

命令语法错误、参数数量错误等会导致命令无法入队。Redis 2.6.5 之后，如果事务中出现入队错误，`EXEC` 会拒绝执行整个事务。

```redis
MULTI
SET a 1
INCR        # 参数错误
EXEC        # 整个事务失败
```

#### 执行期错误

命令已经成功入队，但执行时类型不匹配等错误不会导致其他命令回滚。

```redis
SET name "Alice"
MULTI
INCR name       # 执行时报错：value is not an integer
SET flag ok     # 仍会执行
EXEC
```

结果中会包含某条命令的错误，但其他命令仍可能成功。

### 3. WATCH：乐观锁

`WATCH` 用于监视一个或多个 key，实现乐观并发控制。

```redis
WATCH balance:user:1
GET balance:user:1
MULTI
DECRBY balance:user:1 100
INCRBY balance:user:2 100
EXEC
```

如果被 `WATCH` 的 key 在 `EXEC` 前被其他客户端修改，则 `EXEC` 返回空结果（事务未执行）。客户端应重新读取并重试。

适合场景：

- 秒杀库存扣减。
- 账户余额变更。
- “读 -> 判断 -> 写”的轻量并发控制。

不适合场景：

- 高冲突热点 key，因为重试成本高。
- 复杂多步逻辑，此时 Lua 通常更直接。

### 4. Lua 脚本：服务器端原子逻辑

Lua 脚本在 Redis 服务端执行，脚本执行期间 Redis 不会处理其他命令，因此脚本整体具有原子性。

典型用途：

- 先读后写且必须原子。
- 多 key 条件判断。
- 限流、扣库存、释放锁。
- 避免 `WATCH` 高冲突重试。

基本命令：

```redis
EVAL "return redis.call('GET', KEYS[1])" 1 mykey
```

参数含义：

- 第一个参数：Lua 脚本文本。
- 第二个参数：`KEYS` 数量。
- 后续若干个参数：先是 key，进入 `KEYS` 数组；再是普通参数，进入 `ARGV` 数组。

示例：库存大于 0 才扣减。

```redis
EVAL "
local stock = tonumber(redis.call('GET', KEYS[1]) or '0')
if stock <= 0 then
  return 0
end
redis.call('DECR', KEYS[1])
return 1
" 1 product:1001:stock
```

### 5. Redis Functions（Redis 7.x 推荐了解）

Redis 7.x 支持 Redis Functions，用于把 Lua 函数加载到 Redis 中，以库的形式复用。

常见命令：

```redis
FUNCTION LOAD "#!lua name=mylib\nredis.register_function('pingx', function(keys, args) return 'pong' end)"
FCALL pingx 0
FUNCTION LIST
FUNCTION DELETE mylib
```

学习建议：

- 初学阶段先掌握 `EVAL` / `EVALSHA`。
- 生产中脚本较多、需要版本化与复用时，再学习 Functions。

### 6. Pipeline：减少网络往返

Pipeline 不是事务。它只是客户端一次性发送多条命令，减少 RTT（Round Trip Time，网络往返时间）。

普通方式：

```text
客户端 -> SET a 1 -> Redis -> OK
客户端 -> SET b 2 -> Redis -> OK
客户端 -> GET a   -> Redis -> 1
```

Pipeline：

```text
客户端一次发送：SET a 1 / SET b 2 / GET a
Redis 依次返回：OK / OK / 1
```

特点：

- 提升批量写入、批量读取性能。
- 命令仍是一条条执行，不具备事务语义。
- 中间可能穿插其他客户端命令，除非配合 `MULTI` / `EXEC`。

## 关键命令 / 配置

### 事务命令

| 命令 | 作用 |
|---|---|
| `MULTI` | 开启事务，后续命令进入队列 |
| `EXEC` | 执行事务队列 |
| `DISCARD` | 丢弃事务队列 |
| `WATCH key [key ...]` | 监视 key，配合乐观锁 |
| `UNWATCH` | 取消当前客户端的所有监视 |

### Lua / Function 命令

| 命令 | 作用 |
|---|---|
| `EVAL script numkeys key [key ...] arg [arg ...]` | 执行 Lua 脚本 |
| `EVALSHA sha1 numkeys key [key ...] arg [arg ...]` | 通过脚本 SHA1 执行已缓存脚本 |
| `SCRIPT LOAD script` | 加载脚本并返回 SHA1 |
| `SCRIPT EXISTS sha1 [sha1 ...]` | 判断脚本是否存在 |
| `SCRIPT FLUSH` | 清空脚本缓存 |
| `SCRIPT KILL` | 终止未写入数据的长时间运行脚本 |
| `FUNCTION LOAD` | Redis 7.x 加载函数库 |
| `FCALL function numkeys key [key ...] arg [arg ...]` | 调用函数 |
| `FUNCTION LIST` | 查看函数库 |

### 相关配置

| 配置 | 说明 |
|---|---|
| `lua-time-limit` | Lua 脚本最大建议执行时间，默认通常为 5000ms；超过后 Redis 会记录慢脚本并允许 `SCRIPT KILL` 等处理 |

> 注意：不要把 Lua 写成复杂长任务。Redis 单线程执行命令，长脚本会阻塞其他请求。

## 示例

### 示例 1：基础事务

```redis
MULTI
SET article:1:title "Redis Transaction"
INCR article:1:views
EXPIRE article:1:views 86400
EXEC
```

适合：多个命令必须按顺序一次提交，但不需要读取中间结果决定后续命令。

### 示例 2：使用 WATCH 实现安全扣减

伪流程：

```text
1. WATCH stock:1001
2. GET stock:1001
3. 如果库存 <= 0：UNWATCH，返回失败
4. MULTI
5. DECR stock:1001
6. EXEC
7. 如果 EXEC 为空：说明被并发修改，重试
```

Redis 命令示意：

```redis
WATCH stock:1001
GET stock:1001
MULTI
DECR stock:1001
EXEC
```

客户端必须负责判断 `GET` 的值，并处理 `EXEC` 失败重试。

### 示例 3：Lua 原子释放分布式锁

释放锁时不能简单 `DEL lock:key`，否则可能误删别人的锁。应先判断 value 是否匹配。

```redis
EVAL "
if redis.call('GET', KEYS[1]) == ARGV[1] then
  return redis.call('DEL', KEYS[1])
else
  return 0
end
" 1 lock:order:1001 request-id-abc
```

含义：只有锁的值等于当前请求标识时才删除。

### 示例 4：Pipeline 批量写入

伪代码：

```python
pipe = redis.pipeline(transaction=False)
for i in range(1000):
    pipe.set(f"user:{i}:score", i)
results = pipe.execute()
```

说明：

- `transaction=False` 表示普通 Pipeline，不自动包裹 `MULTI/EXEC`。
- 如果客户端库默认把 pipeline 当事务，需要查看库文档。

### 示例 5：Pipeline + MULTI

如果既想减少网络往返，又想事务执行，可以把事务命令也通过 Pipeline 发送：

```redis
MULTI
SET a 1
SET b 2
EXEC
```

客户端可能一次性发送这四条命令，但事务语义来自 `MULTI/EXEC`，不是 Pipeline 本身。

## 常见误区

### 误区 1：Redis 事务会自动回滚

不会。执行期某条命令失败，不会自动撤销之前或之后的命令。

### 误区 2：Pipeline 等于事务

不等于。Pipeline 只优化网络性能，不提供原子性或隔离性。

### 误区 3：Lua 脚本可以写任意复杂业务

不建议。Lua 会阻塞 Redis 主线程。脚本应短小、确定、可快速完成。

### 误区 4：WATCH 能解决所有并发问题

`WATCH` 是乐观锁。热点 key 高并发下可能频繁失败重试，反而降低吞吐。

### 误区 5：Lua 脚本里的 key 可以随便拼

在 Redis Cluster 中，脚本访问的 key 应通过 `KEYS` 显式传入，且相关 key 需要位于同一 hash slot。不要在脚本内部动态拼接未声明 key。

### 误区 6：EVALSHA 永远可用

脚本缓存可能因重启、`SCRIPT FLUSH` 等原因丢失。客户端应在 `NOSCRIPT` 时回退到 `EVAL` 或重新 `SCRIPT LOAD`。

## 实践检查清单

### 选择工具

- [ ] 只是批量执行、减少网络延迟：优先 Pipeline。
- [ ] 多条命令需要连续顺序执行：考虑 `MULTI/EXEC`。
- [ ] 需要“读 -> 判断 -> 写”的原子逻辑：优先 Lua。
- [ ] 低冲突并发更新：可考虑 `WATCH`。
- [ ] 高冲突热点更新：优先 Lua 或重新设计数据模型。

### 写事务

- [ ] 明确事务中每条命令是否可能执行期失败。
- [ ] 不依赖事务中前一条命令的结果来决定后一条命令；如需要，改用 Lua 或客户端拆分。
- [ ] 使用 `WATCH` 时处理 `EXEC` 返回空结果的重试逻辑。

### 写 Lua

- [ ] 脚本短小、无长循环、无阻塞操作。
- [ ] key 通过 `KEYS` 传入，参数通过 `ARGV` 传入。
- [ ] Redis Cluster 下确认所有 key 在同一 hash slot。
- [ ] 客户端处理 `NOSCRIPT`。
- [ ] 对返回值约定清楚，例如 `1` 成功、`0` 失败、负数表示异常状态。

### 用 Pipeline

- [ ] 控制单批次大小，避免一次发送过多命令导致内存或响应堆积。
- [ ] 保证按返回顺序解析结果。
- [ ] 区分客户端库中的 pipeline 是否默认开启事务。

## 延伸阅读关键词

- Redis Transaction
- MULTI EXEC DISCARD WATCH
- Optimistic Locking
- Redis Lua Scripting
- EVAL EVALSHA SCRIPT LOAD NOSCRIPT
- Redis Functions FCALL Redis 7
- Redis Pipeline RTT
- Redis Cluster hash slot Lua KEYS
- lua-time-limit
