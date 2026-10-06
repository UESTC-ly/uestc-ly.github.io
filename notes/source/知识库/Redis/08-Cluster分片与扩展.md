# 08 - Cluster 分片与扩展

> 目标：理解 Redis Cluster 如何通过哈希槽实现数据分片、如何完成节点扩容和故障转移；能判断什么时候该用 Cluster，什么时候 Sentinel 或单机更合适。

## 学习目标

学完本章，你应该能够：

- 解释 Redis Cluster 的核心模型：节点、哈希槽、主从复制、故障转移。
- 理解 16384 个 hash slots 与 key 到 slot 的映射关系。
- 读懂 `MOVED`、`ASK`、hash tag、多 key 操作限制等 Cluster 特有行为。
- 使用 `redis-cli --cluster` 创建集群、查看状态、扩容、迁移槽。
- 了解 Cluster 的高可用边界、数据一致性边界和常见运维风险。
- 根据业务规模、数据量、吞吐量、可用性需求选择单机、Sentinel 或 Cluster。

## 核心概念

### 1. 为什么需要 Cluster

单个 Redis 实例受限于：

- 单机内存容量。
- 单线程命令执行模型下的单节点吞吐上限。
- 单点故障风险。
- 大实例 RDB / AOF 重写、恢复、迁移成本较高。

Redis Cluster 通过 **分片（sharding）** 把数据分散到多个 master 节点，每个 master 负责一部分哈希槽，并可配置 replica 提供故障转移能力。

适合场景：

- 数据量超过单机内存舒适区。
- 写入或读取压力超过单节点能力。
- 希望 Redis 原生管理分片和主从故障转移。

不一定适合场景：

- 数据量很小，单机或 Sentinel 已足够。
- 业务大量依赖跨 key 原子操作。
- 客户端或运维体系尚不支持 Cluster。

### 2. 哈希槽（Hash Slot）

Redis Cluster 固定有 **16384 个哈希槽**，每个 key 会映射到一个 slot：

```text
slot = CRC16(key) mod 16384
```

Cluster 不是“每个节点负责一段 key 名称”，而是“每个 master 负责一组 slot”。例如：

```text
master-1: slots 0 - 5460
master-2: slots 5461 - 10922
master-3: slots 10923 - 16383
```

当客户端访问某个 key 时，需要知道该 key 属于哪个 slot，以及哪个节点负责这个 slot。

### 3. Hash Tag

如果 key 中包含 `{...}`，Redis Cluster 只对花括号内的内容计算 slot。

示例：

```text
user:{1001}:profile
user:{1001}:orders
cart:{1001}
```

这些 key 的 hash tag 都是 `1001`，会落到同一个 slot，因此可以执行部分多 key 操作。

常见用途：

- 同一用户相关数据放在同一 slot。
- 需要 `MGET`、`MSET`、Lua 脚本或事务同时操作多个 key。

注意：hash tag 过度集中会造成热点 slot，削弱分片效果。

### 4. Cluster 节点角色

Cluster 中的 Redis 节点分为：

- **Master**：负责一部分 slots，处理这些 slots 的读写。
- **Replica**：复制某个 master，master 故障时可被提升。

Cluster 的高可用依赖 master-replica 结构。只有 master 没有 replica 时，该 master 故障后，它负责的 slots 会不可用，严重时整个集群进入不可用状态。

### 5. MOVED 与 ASK 重定向

Cluster 客户端访问错误节点时，会收到重定向响应。

#### MOVED

`MOVED` 表示某个 slot 已经稳定归属于另一个节点：

```text
(error) MOVED 3999 127.0.0.1:7001
```

客户端应更新 slot 路由表，之后直接访问正确节点。

#### ASK

`ASK` 通常出现在 slot 迁移过程中，表示“这次请求临时去另一个节点问”。客户端一般需要先发送 `ASKING`，再执行命令。

使用支持 Cluster 的客户端时，这些细节通常由客户端自动处理。

### 6. 多 key 操作限制

Redis Cluster 要求大多数多 key 命令涉及的 key 必须在同一个 slot，否则会报错：

```text
(error) CROSSSLOT Keys in request don't hash to the same slot
```

例如：

```bash
MSET user:1:name Alice user:2:name Bob
```

如果两个 key 不在同一个 slot，就会失败。

使用 hash tag 后：

```bash
MSET user:{1}:name Alice user:{1}:email alice@example.com
```

这两个 key 位于同一 slot，可以执行。

### 7. Cluster 与 Sentinel 的区别

| 对比项 | Sentinel | Cluster |
|---|---|---|
| 主要目标 | 主从高可用 | 分片扩展 + 高可用 |
| 数据分布 | 每个副本保存全量数据 | 数据分散到多个 master |
| 扩容方式 | 通常垂直扩容或手动拆分 | 迁移 slots 到新节点 |
| 客户端要求 | 支持 Sentinel 发现 master | 支持 Cluster slot 路由 |
| 多 key 操作 | 单实例语义，限制少 | 必须同 slot |
| 运维复杂度 | 中等 | 较高 |

## 关键命令 / 配置

### Cluster 基础配置

每个节点都需要开启 cluster 模式：

```conf
port 7000
cluster-enabled yes
cluster-config-file nodes-7000.conf
cluster-node-timeout 5000
appendonly yes
```

常用配置说明：

```conf
# 开启 Cluster 模式
cluster-enabled yes

# 节点自动维护的集群拓扑文件，不建议手工编辑
cluster-config-file nodes.conf

# 节点超时判断时间，影响故障检测速度
cluster-node-timeout 5000

# replica 是否允许在 master 故障时参与故障转移
cluster-replica-no-failover no

# 当部分 slots 不可用时，集群是否停止服务
cluster-require-full-coverage yes
```

版本差异：旧资料里可能看到 `cluster-slave-no-failover`，Redis 5.0 后更推荐 `cluster-replica-no-failover`，旧名称通常仍兼容。

### 创建集群

假设已有 6 个节点：`7000` 到 `7005`，创建 3 master + 3 replica：

```bash
redis-cli --cluster create \
  127.0.0.1:7000 127.0.0.1:7001 127.0.0.1:7002 \
  127.0.0.1:7003 127.0.0.1:7004 127.0.0.1:7005 \
  --cluster-replicas 1
```

### 使用 Cluster 客户端模式

```bash
# -c 表示自动处理 MOVED / ASK 重定向
redis-cli -c -p 7000

SET user:1 Alice
GET user:1
CLUSTER KEYSLOT user:1
CLUSTER NODES
CLUSTER INFO
```

### 查看集群状态

```bash
redis-cli --cluster check 127.0.0.1:7000
redis-cli --cluster info 127.0.0.1:7000

redis-cli -p 7000 CLUSTER INFO
redis-cli -p 7000 CLUSTER NODES
redis-cli -p 7000 CLUSTER SLOTS
```

### 扩容与迁移

添加一个新节点：

```bash
redis-cli --cluster add-node 127.0.0.1:7006 127.0.0.1:7000
```

将新节点作为 replica：

```bash
redis-cli --cluster add-node 127.0.0.1:7007 127.0.0.1:7000 \
  --cluster-slave --cluster-master-id <master-node-id>
```

Redis 7.x 文档中更推荐 `replica` 术语，但 `redis-cli --cluster` 的部分参数和输出仍可能保留 `slave` 历史名称。

重新分配 slots：

```bash
redis-cli --cluster reshard 127.0.0.1:7000
```

自动均衡 slots：

```bash
redis-cli --cluster rebalance 127.0.0.1:7000
```

### 故障转移相关命令

```bash
# 在 replica 上手动触发故障转移
redis-cli -p 7003 CLUSTER FAILOVER

# 更激进的手动切换，常用于特殊维护场景，需谨慎
redis-cli -p 7003 CLUSTER FAILOVER TAKEOVER
```

## 示例：本机创建 3 主 3 从 Cluster

> 学习环境示例，不代表生产部署建议。生产中应跨主机、跨机架或跨可用区部署，并配置认证、TLS、监控和备份。

### 1. 准备配置文件

目录结构：

```text
cluster-lab/
  7000/redis.conf
  7001/redis.conf
  7002/redis.conf
  7003/redis.conf
  7004/redis.conf
  7005/redis.conf
```

每个配置只需修改 `port`、`dir`、`cluster-config-file`：

```conf
port 7000
dir ./7000
cluster-enabled yes
cluster-config-file nodes-7000.conf
cluster-node-timeout 5000
appendonly yes
protected-mode no
```

### 2. 启动节点

```bash
redis-server 7000/redis.conf
redis-server 7001/redis.conf
redis-server 7002/redis.conf
redis-server 7003/redis.conf
redis-server 7004/redis.conf
redis-server 7005/redis.conf
```

### 3. 创建集群

```bash
redis-cli --cluster create \
  127.0.0.1:7000 127.0.0.1:7001 127.0.0.1:7002 \
  127.0.0.1:7003 127.0.0.1:7004 127.0.0.1:7005 \
  --cluster-replicas 1
```

确认后，Redis 会分配 slots，并为每个 master 分配一个 replica。

### 4. 写入与查询

```bash
redis-cli -c -p 7000

127.0.0.1:7000> SET user:1 Alice
-> Redirected to slot [10778] located at 127.0.0.1:7001
OK
127.0.0.1:7001> GET user:1
"Alice"
127.0.0.1:7001> CLUSTER KEYSLOT user:1
(integer) 10778
```

### 5. 验证 hash tag

```bash
redis-cli -c -p 7000

MSET user:{42}:name Bob user:{42}:email bob@example.com
MGET user:{42}:name user:{42}:email
CLUSTER KEYSLOT user:{42}:name
CLUSTER KEYSLOT user:{42}:email
```

两个 `CLUSTER KEYSLOT` 的结果应相同。

### 6. 模拟 master 故障

```bash
# 查看节点关系
redis-cli -p 7000 CLUSTER NODES

# 停掉某个 master，例如 7000
redis-cli -p 7000 SHUTDOWN NOSAVE

# 等待 cluster-node-timeout 后查看集群状态
redis-cli -p 7001 CLUSTER INFO
redis-cli -p 7001 CLUSTER NODES
```

如果 7000 有健康 replica，Cluster 会尝试把它提升为新 master。

## 常见误区

### 误区 1：Cluster 就是“自动无限扩容”

Cluster 能水平扩展，但扩容需要添加节点、迁移 slots、观察热点与客户端表现。迁移期间会产生 `ASK` 重定向和额外网络开销。

### 误区 2：Cluster 解决所有高可用问题

Cluster 可以自动故障转移，但仍是异步复制。master 故障时，未复制到 replica 的写入可能丢失。

### 误区 3：所有 Redis 命令在 Cluster 中都一样

多 key 命令、Lua 脚本、事务等必须考虑 key 是否在同一 slot。初学时最常见的错误就是 `CROSSSLOT`。

### 误区 4：Hash tag 用得越多越好

Hash tag 能让相关 key 同槽，但如果把大量 key 都放到同一个 tag，会制造热点，导致某个 master 压力过大。

### 误区 5：连接任意节点即可，不需要 Cluster 客户端

普通客户端不理解 slot 路由和重定向，会频繁收到 `MOVED` / `ASK`。生产中应使用成熟的 Redis Cluster 客户端或连接池。

### 误区 6：只看节点数量，不看槽分布

节点多不代表负载均衡。应检查 slots 分布、key 数量、内存占用、热 key 和命令耗时。

### 误区 7：Cluster 可以替代备份

Cluster 解决分片和可用性，不解决误删除、程序 bug、批量覆盖等逻辑错误。仍需要 RDB / AOF / 离线备份和恢复演练。

## 实践检查清单

### 设计前检查

- [ ] 单机 Redis 是否已经无法满足内存、吞吐或可用性需求。
- [ ] 业务是否大量依赖跨 key 原子操作。
- [ ] 使用的客户端是否完整支持 Redis Cluster。
- [ ] key 命名是否有清晰规范，必要时是否设计 hash tag。
- [ ] 是否评估热 key、big key 对单个 slot / 节点的影响。

### 部署检查

- [ ] 至少 3 个 master，生产中每个 master 至少 1 个 replica。
- [ ] Master 与其 replica 不在同一故障域。
- [ ] `cluster-node-timeout` 与业务故障恢复目标匹配。
- [ ] 开启认证、必要时开启 TLS，并限制网络访问。
- [ ] 配置持久化与备份策略。
- [ ] 监控 `cluster_state`、slot 覆盖率、节点连接数、复制延迟和慢查询。

### 扩容 / 缩容检查

- [ ] 扩容前记录 `CLUSTER NODES` 与 `redis-cli --cluster check` 输出。
- [ ] 迁移 slots 避开业务高峰。
- [ ] 迁移期间观察 `MOVED` / `ASK`、延迟、CPU、网络和错误率。
- [ ] 迁移后执行 `redis-cli --cluster rebalance` 或检查 slot 分布。
- [ ] 验证客户端路由表能自动刷新。

### 故障演练检查

- [ ] 演练 master 宕机后 replica 是否能被提升。
- [ ] 演练客户端是否能在故障转移后恢复写入。
- [ ] 明确故障期间可能的数据丢失窗口。
- [ ] 验证告警能覆盖节点失联、slot 不完整、复制中断。

## 延伸阅读关键词

- Redis Cluster hash slots
- Redis Cluster hash tags
- Redis MOVED ASK redirection
- Redis Cluster reshard rebalance
- Redis Cluster failover
- Redis CROSSSLOT
- Redis cluster-require-full-coverage
- Redis hot key big key
- Redis Cluster client routing

## 小结

Redis Cluster 用 16384 个哈希槽把数据分散到多个 master，并通过 replica 和故障转移提高可用性。它适合解决单节点容量和吞吐瓶颈，但会带来客户端路由、多 key 限制、slot 迁移和运维复杂度。选择 Cluster 前，应先确认业务真的需要分片扩展，并设计好 key、客户端、监控、备份和故障演练。
