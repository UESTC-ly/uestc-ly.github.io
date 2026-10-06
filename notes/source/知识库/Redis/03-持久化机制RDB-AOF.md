# 03 - 持久化机制：RDB 与 AOF

> 目标读者：已经知道 Redis 是内存数据库，想理解“数据如何落盘、宕机后如何恢复、该怎么配置”的学习者。本文以 Redis 7.x 开源版为主；不同发行版或云服务可能隐藏部分配置入口。

## 学习目标

学完本篇，你应该能够：

- 说清楚 Redis 持久化的四种选择：无持久化、RDB、AOF、RDB + AOF。
- 理解 RDB 快照与 AOF 追加日志的工作方式、优缺点和恢复顺序。
- 能根据“缓存 / 会话 / 订单状态 / 队列”等场景选择合适策略。
- 会使用常见命令检查持久化状态、触发保存、重写 AOF、修复文件。
- 了解 Redis 7.x AOF 多文件机制与 `appenddirname` 的变化。

---

## 核心概念

### 1. Redis 为什么需要持久化？

Redis 的主要数据结构在内存中，读写速度快，但进程退出、机器重启或故障时，内存数据会丢失。持久化就是把数据写入磁盘，使 Redis 重启后可以恢复数据。

Redis 常见模式：

| 模式 | 说明 | 适合场景 |
|---|---|---|
| 无持久化 | 完全不落盘 | 纯缓存、可从源数据重建 |
| RDB | 定期生成某一时刻的数据快照 | 备份、灾难恢复、冷启动加载快 |
| AOF | 记录每次写命令，重启时重放 | 更高数据安全性 |
| RDB + AOF | 两者同时开启 | 大多数需要恢复能力的生产场景 |

> 重要：Redis 持久化不是传统数据库事务日志的完全替代。它降低数据丢失窗口，但还要结合复制、Sentinel/Cluster、备份、磁盘可靠性和应用幂等设计。

---

### 2. RDB：快照持久化

RDB（Redis Database）会在某个时间点把内存数据生成一个紧凑的二进制快照文件，默认文件名常见为 `dump.rdb`。

典型过程：

1. Redis 根据 `save` 规则或命令触发快照。
2. 主进程 `fork()` 子进程。
3. 子进程把当前数据集写入临时 RDB 文件。
4. 写入成功后，用新文件替换旧文件。

#### RDB 的优点

- 文件紧凑，适合备份与跨环境迁移。
- 重启加载通常比重放大量 AOF 更快。
- 子进程写盘，主进程主要继续处理请求。

#### RDB 的风险

- 可能丢失上一次快照之后的数据。
- `fork()` 在大内存实例上可能带来瞬时延迟和额外内存压力。
- 如果磁盘慢，后台保存可能持续较久。

---

### 3. AOF：追加日志持久化

AOF（Append Only File）会把 Redis 收到的写命令追加到日志文件中。重启时 Redis 重新执行这些命令，恢复出数据集。

AOF 的关键点：

- 只记录会修改数据的命令。
- 可以配置 `fsync` 策略控制“写到操作系统缓存”与“真正刷到磁盘”的频率。
- 日志会越来越大，需要 AOF rewrite（重写）压缩为“恢复当前数据集所需的最小命令集合”。

#### Redis 7.x 的 AOF 多文件机制

Redis 7.0 起，AOF 不再只是单个文件模型，而是使用一个 AOF 目录（由 `appenddirname` 指定）管理：

- base AOF：重写后生成的基础文件，可是 RDB 格式或 AOF 格式。
- incremental AOF：重写期间和之后新增的增量写命令。
- manifest：记录当前有效 AOF 文件集合。

这让 AOF 重写和切换更清晰，也减少某些大文件替换风险。排障时不要只找单个 `.aof` 文件，还要检查 AOF 目录与 manifest。

---

### 4. RDB 与 AOF 同时开启时，Redis 用谁恢复？

如果 RDB 和 AOF 都开启，Redis 重启时通常优先使用 AOF，因为 AOF 一般包含更完整的写入历史，数据丢失窗口更小。

恢复直觉：

```text
只有 RDB      -> 加载 RDB
只有 AOF      -> 重放 AOF
RDB + AOF     -> 优先使用 AOF
都没有        -> 空数据启动
```

---

## 关键命令 / 配置

### RDB 相关配置

```conf
# Redis 7 默认配置文件中常见形式：满足条件时触发快照
save 3600 1
save 300 100
save 60 10000

# 禁用自动 RDB 快照
save ""

# RDB 文件名与目录
dbfilename dump.rdb
dir /var/lib/redis

# 后台保存失败后是否停止接收写入，默认通常为 yes
stop-writes-on-bgsave-error yes

# RDB 文件压缩与校验
rdbcompression yes
rdbchecksum yes
```

常用命令：

```bash
# 阻塞保存：不建议在生产高峰使用
SAVE

# 后台保存：常用
BGSAVE

# 查看持久化状态
INFO persistence

# 查看上次保存时间
LASTSAVE
```

### AOF 相关配置

```conf
# 开启 AOF
appendonly yes

# Redis 7.x AOF 目录名
appenddirname "appendonlydir"

# AOF 文件名基础前缀；Redis 7 会配合 manifest 使用
appendfilename "appendonly.aof"

# 刷盘策略：安全性 always > everysec > no；性能通常相反
appendfsync everysec

# AOF 重写触发条件
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# AOF 重写期间是否避免 fsync 竞争；可能增加风险窗口
no-appendfsync-on-rewrite no

# AOF 文件异常截断时是否尽量加载
aof-load-truncated yes
```


常用命令：

```bash
# 手动触发 AOF 重写
BGREWRITEAOF

# 查看 AOF / RDB 状态
INFO persistence

# 动态打开 AOF（会触发初始重写，生产环境需评估 IO）
CONFIG SET appendonly yes

# 检查配置值
CONFIG GET appendonly
CONFIG GET appendfsync
CONFIG GET appenddirname
```

离线修复工具（服务停止后使用）：

```bash
redis-check-rdb dump.rdb
redis-check-aof --fix appendonly.aof
```

Redis 7.x 多文件 AOF 场景下，实际文件可能位于 `appenddirname` 目录中，修复前要先确认 manifest 和文件路径。

---

## 示例

### 示例 1：纯缓存，不要求 Redis 自身恢复

适合：商品详情缓存、热点配置缓存、可从 MySQL/服务端重建的数据。

```conf
save ""
appendonly no
maxmemory 4gb
maxmemory-policy allkeys-lru
```

思路：把 Redis 当缓存层，数据源另有权威存储。宕机后允许缓存冷启动。

---

### 示例 2：需要较快恢复，允许丢失数分钟数据

适合：可容忍短时间丢失的统计、排行榜缓存、临时状态。

```conf
save 300 100
save 60 10000
appendonly no
```

思路：使用 RDB 作为低成本恢复点。备份也更方便。

---

### 示例 3：希望尽量少丢数据的普通业务

适合：会话、限流计数、任务状态等“不能轻易丢，但也不是金融级强一致”的场景。

```conf
save 3600 1
save 300 100
save 60 10000
appendonly yes
appendfsync everysec
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
```

思路：RDB 方便备份，AOF 降低数据丢失窗口。`everysec` 是常见折中：性能较好，极端故障下可能丢失约 1 秒左右写入。

---

### 示例 4：观察一次 AOF 重写

```bash
redis-cli INFO persistence | grep -E 'aof_|rdb_'
redis-cli BGREWRITEAOF
redis-cli INFO persistence | grep -E 'aof_rewrite|aof_current|aof_base'
```

观察点：

- `aof_rewrite_in_progress` 是否从 `1` 回到 `0`。
- AOF 文件大小是否下降。
- `latest_fork_usec` 是否异常偏高，提示 fork 成本较大。

---

## 常见误区

### 误区 1：开启 RDB 就不会丢数据

RDB 是“时间点快照”。如果每 5 分钟生成一次快照，故障时可能丢失最近几分钟写入。

### 误区 2：AOF everysec 等于绝对不丢

`appendfsync everysec` 依赖后台刷盘。机器断电、内核或磁盘异常时，仍可能丢失最近约 1 秒数据。

### 误区 3：`appendfsync always` 一定适合核心业务

`always` 更安全但性能开销明显，延迟可能不可接受。很多系统更应该通过“Redis + 主数据库 + 幂等重放 + 消息队列 + 备份”组合保证可靠性。

### 误区 4：AOF 文件只会变大，无法控制

AOF 会自动或手动重写。重写不是复制旧日志，而是根据当前数据集生成更短的恢复命令。

### 误区 5：复制可以替代持久化

主从复制解决可用性和读扩展，但主节点误删数据会同步到副本。如果没有持久化或备份，误操作仍可能无法恢复。

### 误区 6：大内存 Redis 做快照完全无影响

RDB/AOF rewrite 都需要 `fork()`。写入频繁时，Copy-on-Write 可能带来额外内存消耗；大实例还可能出现 fork 延迟。

---

## 实践检查清单

### 上线前

- [ ] 明确 Redis 中的数据是否有权威来源，能否重建。
- [ ] 明确可接受的数据丢失窗口：0 秒、约 1 秒、几分钟、完全可丢。
- [ ] 选择持久化策略：无持久化 / RDB / AOF / RDB + AOF。
- [ ] 配置 `dir` 到可靠磁盘，并确保权限正确。
- [ ] 为 RDB/AOF 文件所在磁盘设置容量告警。
- [ ] 如果开启 AOF，评估 `appendfsync` 策略和重写阈值。
- [ ] 如果实例很大，压测 `BGSAVE` / `BGREWRITEAOF` 的 fork 延迟和内存峰值。

### 运行中

- [ ] 定期查看 `INFO persistence`。
- [ ] 关注 `rdb_last_bgsave_status`、`aof_last_bgrewrite_status`。
- [ ] 关注 `latest_fork_usec`，识别 fork 抖动。
- [ ] 监控磁盘使用率、IO 延迟、AOF 增长速度。
- [ ] 定期做恢复演练：不要只备份，不验证可恢复。

### 故障恢复

- [ ] 先备份现场 RDB/AOF 文件，再尝试修复。
- [ ] 确认 Redis 7.x AOF 目录、manifest、base/incr 文件是否完整。
- [ ] 使用 `redis-check-rdb` 或 `redis-check-aof` 前，确保 Redis 进程已停止或操作副本文件。
- [ ] 恢复后用业务校验脚本检查关键 key 数量、TTL、数据一致性。

---

## 速记：如何选择？

```text
只做缓存，可重建       -> 无持久化或仅 RDB
需要备份、冷启动快     -> RDB
希望少丢数据           -> AOF everysec
生产通用稳妥方案       -> RDB + AOF everysec + 备份 + 恢复演练
极端低丢失要求         -> 不要只靠 Redis；引入权威数据库/日志/队列设计
```

---

## 延伸阅读关键词

- Redis persistence
- RDB snapshot
- Append Only File / AOF
- AOF rewrite
- Redis 7 multi-part AOF / manifest
- `appendfsync everysec`
- `BGSAVE` / `BGREWRITEAOF`
- Copy-on-Write
- `INFO persistence`
- disaster recovery drill
