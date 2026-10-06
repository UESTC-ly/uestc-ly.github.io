# 06-发布订阅、Stream 与消息队列

> Redis 7.x 通用视角：Redis 可以做消息传递，但不同机制适合不同场景。本章比较 Pub/Sub、Stream 与基于 List 的队列，帮助你从“能用”走向“选对”。

## 学习目标

学完本篇，你应该能够：

- 理解 Redis Pub/Sub 的即时广播模型与可靠性限制。
- 使用 `PUBLISH` / `SUBSCRIBE` / `PSUBSCRIBE` 完成基础发布订阅。
- 理解 Redis Stream 的追加日志、消息 ID、消费者组与 ACK。
- 使用 `XADD` / `XREAD` / `XGROUP` / `XREADGROUP` / `XACK` 构建可靠消费。
- 区分 Pub/Sub、Stream、List 队列的适用场景。
- 识别 Redis 用作消息队列时的常见风险：堆积、重复消费、丢消息、阻塞与内存控制。

## 核心概念

### 1. Pub/Sub：即时广播

Pub/Sub 是发布订阅模型：

- 发布者向 channel 发送消息。
- 当前在线订阅该 channel 的客户端立即收到消息。
- Redis 不保存普通 Pub/Sub 消息。
- 订阅者离线期间的消息会丢失。

示例：

```redis
SUBSCRIBE news.sports
```

另一个客户端：

```redis
PUBLISH news.sports "team A won"
```

适合：

- 在线通知。
- 实时广播。
- 低可靠要求的事件分发。
- 多实例应用间的轻量信号。

不适合：

- 订单、支付、库存等必须可靠处理的业务消息。
- 需要消息堆积、重放、确认、失败重试的场景。

### 2. Pattern Pub/Sub：模式订阅

`PSUBSCRIBE` 支持通配模式：

```redis
PSUBSCRIBE news.*
```

可收到：

- `news.sports`
- `news.finance`
- `news.weather`

注意：模式匹配增加管理复杂度，频道命名要有规范。

### 3. Sharded Pub/Sub（Redis 7.x）

Redis 7.0 引入 Sharded Pub/Sub，主要用于 Redis Cluster 场景，让频道消息限制在对应分片传播，减少集群广播开销。

常见命令：

```redis
SSUBSCRIBE shard-channel
SPUBLISH shard-channel "hello"
SUNSUBSCRIBE shard-channel
```

学习建议：

- 单机或普通入门场景先掌握 `PUBLISH` / `SUBSCRIBE`。
- Cluster 中频道数量大、消息量高时，再评估 Sharded Pub/Sub。

### 4. Stream：可持久化的消息日志

Redis Stream 是 Redis 5.0 引入的数据结构，类似追加日志：

- 每条消息有唯一 ID。
- 消息按时间与序列追加。
- 可以从指定 ID 开始读取。
- 支持消费者组。
- 支持确认（ACK）和 Pending Entries List（PEL，待确认列表）。

添加消息：

```redis
XADD orders * userId 1001 amount 99.5
```

其中：

- `orders` 是 Stream key。
- `*` 表示由 Redis 自动生成消息 ID。
- 后面是 field-value 格式的消息体。

消息 ID 形如：

```text
1710000000000-0
```

前半部分通常是毫秒时间戳，后半部分是同毫秒内的序列号。

### 5. Stream 消费模式

#### 普通读取：XREAD

```redis
XREAD COUNT 10 BLOCK 5000 STREAMS orders 0
```

含义：

- 从 `orders` 的 ID `0` 之后开始读。
- 最多读取 10 条。
- 没有消息时最多阻塞 5000ms。

读取新消息常用：

```redis
XREAD BLOCK 0 STREAMS orders $
```

`$` 表示从当前最新位置之后的新消息开始读，不读取历史消息。

#### 消费者组：XGROUP + XREADGROUP

消费者组适合多个消费者分摊处理同一个 Stream。

创建消费者组：

```redis
XGROUP CREATE orders order-workers 0 MKSTREAM
```

读取消息：

```redis
XREADGROUP GROUP order-workers worker-1 COUNT 10 BLOCK 5000 STREAMS orders >
```

含义：

- 使用消费者组 `order-workers`。
- 当前消费者名是 `worker-1`。
- `>` 表示只读取从未投递给该组的新消息。

处理完成后确认：

```redis
XACK orders order-workers 1710000000000-0
```

### 6. PEL：待确认消息

消费者组中，消息被投递但未 `XACK` 时，会进入 PEL。

PEL 用于：

- 发现消费者崩溃后未处理完的消息。
- 查询积压与超时消息。
- 将消息转移给其他消费者继续处理。

常见命令：

```redis
XPENDING orders order-workers
XAUTOCLAIM orders order-workers worker-2 60000 0-0 COUNT 10
```

`XAUTOCLAIM` 可把空闲超过指定时间的 pending 消息转移给当前消费者。

### 7. List 队列：简单任务队列

在 Stream 之前，常用 List 实现队列：

```redis
LPUSH jobs "job-1"
BRPOP jobs 0
```

特点：

- 简单、高效。
- 适合单队列、简单任务分发。
- 缺少 Stream 那种内建消息 ID、消费者组、pending、重放能力。

更可靠的 List 队列会使用“处理中队列”：

```redis
BRPOPLPUSH jobs processing 0
```

消费者处理成功后再从 `processing` 删除对应任务。但这需要客户端自己实现恢复、扫描与重试逻辑。

## 关键命令 / 配置

### Pub/Sub 命令

| 命令 | 作用 |
|---|---|
| `PUBLISH channel message` | 向频道发布消息 |
| `SUBSCRIBE channel [channel ...]` | 订阅频道 |
| `UNSUBSCRIBE [channel ...]` | 取消订阅频道 |
| `PSUBSCRIBE pattern [pattern ...]` | 按模式订阅 |
| `PUNSUBSCRIBE [pattern ...]` | 取消模式订阅 |
| `PUBSUB CHANNELS [pattern]` | 查看活跃频道 |
| `PUBSUB NUMSUB channel [channel ...]` | 查看频道订阅者数量 |
| `SPUBLISH` / `SSUBSCRIBE` | Redis 7.x Sharded Pub/Sub |

### Stream 命令

| 命令 | 作用 |
|---|---|
| `XADD key ID field value [field value ...]` | 添加消息 |
| `XRANGE key start end [COUNT count]` | 正序范围查询 |
| `XREVRANGE key end start [COUNT count]` | 倒序范围查询 |
| `XLEN key` | 查看 Stream 长度 |
| `XREAD [COUNT n] [BLOCK ms] STREAMS key ID` | 普通读取 |
| `XGROUP CREATE key group ID [MKSTREAM]` | 创建消费者组 |
| `XREADGROUP GROUP group consumer STREAMS key >` | 消费者组读取新消息 |
| `XACK key group ID [ID ...]` | 确认消息 |
| `XPENDING key group` | 查看待确认消息 |
| `XCLAIM` / `XAUTOCLAIM` | 转移超时 pending 消息 |
| `XDEL key ID [ID ...]` | 删除消息 |
| `XTRIM key MAXLEN ...` | 裁剪 Stream |
| `XINFO STREAM key` | 查看 Stream 信息 |
| `XINFO GROUPS key` | 查看消费者组信息 |
| `XINFO CONSUMERS key group` | 查看消费者信息 |

### List 队列命令

| 命令 | 作用 |
|---|---|
| `LPUSH key value` | 从左侧压入任务 |
| `RPUSH key value` | 从右侧压入任务 |
| `LPOP key` / `RPOP key` | 弹出任务 |
| `BLPOP key timeout` / `BRPOP key timeout` | 阻塞弹出任务 |
| `BRPOPLPUSH source destination timeout` | 阻塞弹出并放入处理中队列 |
| `LMOVE` / `BLMOVE` | Redis 6.2+ 推荐的移动式弹出命令，可替代 `RPOPLPUSH` / `BRPOPLPUSH` 场景 |

### 相关配置与内存控制

| 配置 / 选项 | 说明 |
|---|---|
| `XADD key MAXLEN ~ n * ...` | 近似限制 Stream 长度，控制内存 |
| `XTRIM key MAXLEN ~ n` | 裁剪 Stream |
| `client-output-buffer-limit pubsub ...` | 限制 Pub/Sub 客户端输出缓冲区，慢订阅者可能被断开 |
| `maxmemory` / eviction policy | Redis 总内存与淘汰策略会影响消息保留 |

## 示例

### 示例 1：最小 Pub/Sub

客户端 A：

```redis
SUBSCRIBE chat.room.1
```

客户端 B：

```redis
PUBLISH chat.room.1 "hello redis"
```

客户端 A 收到消息。

适合聊天室在线消息提示，但如果客户端 A 离线，就收不到这条消息。

### 示例 2：使用 Stream 写入订单事件

```redis
XADD order-events * type created orderId 1001 userId 42 amount 199.00
XADD order-events * type paid orderId 1001 payChannel card
```

查看全部：

```redis
XRANGE order-events - +
```

查看长度：

```redis
XLEN order-events
```

### 示例 3：创建消费者组并消费

创建组，从头开始消费历史消息：

```redis
XGROUP CREATE order-events order-service 0 MKSTREAM
```

消费者 `worker-a` 读取新消息：

```redis
XREADGROUP GROUP order-service worker-a COUNT 5 BLOCK 5000 STREAMS order-events >
```

处理成功后确认：

```redis
XACK order-events order-service 1710000000000-0
```

### 示例 4：查看并接管超时消息

查看 pending 概览：

```redis
XPENDING order-events order-service
```

把空闲超过 60 秒的消息转给 `worker-b`：

```redis
XAUTOCLAIM order-events order-service worker-b 60000 0-0 COUNT 10
```

处理完成后仍然需要：

```redis
XACK order-events order-service <message-id>
```

### 示例 5：限制 Stream 长度

写入时限制长度：

```redis
XADD order-events MAXLEN ~ 10000 * type created orderId 1002
```

手动裁剪：

```redis
XTRIM order-events MAXLEN ~ 10000
```

`~` 表示近似裁剪，性能更好；如果必须精确长度，可以不用 `~`，但成本更高。

### 示例 6：List 简单队列

生产者：

```redis
LPUSH email-jobs "send welcome email to user 1001"
```

消费者：

```redis
BRPOP email-jobs 0
```

说明：

- 简单任务可用。
- 任务一旦弹出，消费者崩溃可能导致任务丢失。
- 如需可靠性，使用 Stream 消费者组通常更省心。

## 选型速查

| 需求 | 推荐方案 |
|---|---|
| 在线广播，允许离线丢失 | Pub/Sub |
| 需要模式频道订阅 | Pattern Pub/Sub |
| Redis Cluster 大规模频道广播 | Sharded Pub/Sub |
| 可靠消息、可重放、消费者组 | Stream |
| 简单轻量任务队列 | List |
| 需要 ACK、失败接管、积压观察 | Stream |
| 严格复杂消息系统、跨服务大规模治理 | Kafka / RabbitMQ / RocketMQ 等专用 MQ |

## 常见误区

### 误区 1：Pub/Sub 是可靠消息队列

不是。普通 Pub/Sub 不保存消息，订阅者不在线就收不到。

### 误区 2：Stream 消息 XACK 后就从 Stream 删除

不是。`XACK` 只是从消费者组的 PEL 中确认完成，不会删除 Stream 中的消息。删除或裁剪需要 `XDEL` / `XTRIM`。

### 误区 3：读取 `>` 就能重新处理 pending 消息

不能。`>` 只读取从未投递给该消费者组的新消息。要处理 pending，需要用 `XPENDING`、`XCLAIM`、`XAUTOCLAIM`，或用具体 ID 范围读取。

### 误区 4：Stream 自动无限可靠

Stream 仍存储在 Redis 内存/持久化体系中。需要配置持久化、复制、高可用、长度裁剪和监控。否则可能内存膨胀或故障丢数据。

### 误区 5：消费者名可以随便变

消费者组中 consumer 名用于追踪 pending。如果每次启动都生成新名字，可能产生大量闲置 consumer 与难以管理的 PEL。生产中应有稳定命名或清理策略。

### 误区 6：Redis 可以替代所有 MQ

Redis Stream 很强，但如果需要超大规模日志保留、复杂路由、跨数据中心消息治理、严格顺序分区等能力，应评估专用消息系统。

## 实践检查清单

### Pub/Sub

- [ ] 确认业务允许订阅者离线期间丢消息。
- [ ] 设计清晰的 channel 命名规范，例如 `domain.event.scope`。
- [ ] 监控慢订阅者与输出缓冲区。
- [ ] Cluster 高广播量场景评估 Sharded Pub/Sub。

### Stream

- [ ] 每个 Stream 设置合理保留策略：`MAXLEN` 或定期 `XTRIM`。
- [ ] 消费者处理成功后必须 `XACK`。
- [ ] 定期检查 `XPENDING`，处理超时 pending。
- [ ] 消费逻辑具备幂等性，因为消息可能重复投递。
- [ ] 监控 `XLEN`、pending 数、最大 idle 时间、消费者数量。
- [ ] 设计稳定的 group 与 consumer 命名。
- [ ] 明确从 `0`、`$`、`>` 读取的语义差异。

### List 队列

- [ ] 简单场景才使用 `LPUSH` + `BRPOP`。
- [ ] 需要可靠性时，设计处理中队列或改用 Stream。
- [ ] 避免单个大 value，消息体建议存 ID，详情放数据库或 Redis Hash。

### 通用消息处理

- [ ] 消费者逻辑幂等。
- [ ] 有重试、死信或人工补偿方案。
- [ ] 有积压监控与报警。
- [ ] 了解 Redis 持久化与主从切换对消息可靠性的影响。

## 延伸阅读关键词

- Redis Pub/Sub
- PUBLISH SUBSCRIBE PSUBSCRIBE
- Redis Sharded Pub/Sub Redis 7
- Redis Stream
- XADD XREAD XGROUP XREADGROUP XACK
- XPENDING XCLAIM XAUTOCLAIM
- Pending Entries List PEL
- XTRIM MAXLEN approximate trimming
- Redis List queue BRPOP BLMOVE
- Redis Stream vs Kafka
