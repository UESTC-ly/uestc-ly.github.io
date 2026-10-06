# Redis 学习索引

## 总览

| 顺序 | 笔记 | 主题 | 重点能力 |
|---:|---|---|---|
| 01 | [[01-Redis概览与环境准备]] | Redis 定位、安装、CLI、配置 | 建立学习环境与基础心智模型 |
| 02 | [[02-数据类型与核心命令]] | 核心数据结构与命令 | 能根据业务场景选择数据类型 |
| 03 | [[03-持久化机制RDB-AOF]] | RDB、AOF、恢复 | 能评估数据安全与性能折中 |
| 04 | [[04-内存模型与淘汰策略]] | 内存、过期、淘汰 | 能控制容量和避免 OOM 风险 |
| 05 | [[05-事务Lua与管道]] | 事务、Lua、Pipeline | 能处理原子操作与批量请求 |
| 06 | [[06-发布订阅Stream与消息队列]] | Pub/Sub、Stream、队列 | 能设计轻量消息场景 |
| 07 | [[07-复制哨兵与高可用]] | Replication、Sentinel | 能理解故障转移与高可用边界 |
| 08 | [[08-Cluster分片与扩展]] | Cluster、slot、扩缩容 | 能理解分片扩展与多 key 限制 |
| 09 | [[09-性能优化与监控]] | 延迟、慢查询、监控 | 能定位常见性能瓶颈 |
| 10 | [[10-生产实践故障排查与学习路线]] | 生产清单、故障排查、路线 | 能形成上线与排障方法论 |

## 按问题查找

### 我刚开始学 Redis

- [[01-Redis概览与环境准备]]
- [[02-数据类型与核心命令]]

### 我想理解数据会不会丢

- [[03-持久化机制RDB-AOF]]
- [[07-复制哨兵与高可用]]

### 我遇到内存爆了或 key 过期异常

- [[04-内存模型与淘汰策略]]
- [[09-性能优化与监控]]

### 我需要原子扣库存、限流或批量写入

- [[05-事务Lua与管道]]
- [[02-数据类型与核心命令]]

### 我想用 Redis 做消息队列

- [[06-发布订阅Stream与消息队列]]
- [[10-生产实践故障排查与学习路线]]

### 我准备上生产

- [[07-复制哨兵与高可用]]
- [[08-Cluster分片与扩展]]
- [[09-性能优化与监控]]
- [[10-生产实践故障排查与学习路线]]

## 建议实验清单

- 本地启动 Redis，使用 `redis-cli PING`、`INFO`、`CONFIG GET` 验证环境。
- 对每种核心数据结构写 3 个命令示例。
- 分别开启 RDB、AOF，观察文件生成与恢复行为。
- 设置 `maxmemory` 与淘汰策略，写入数据触发淘汰。
- 使用 Pipeline 对比单条命令与批量命令耗时。
- 创建 Stream 消费组并模拟 pending message。
- 搭建一主一从，观察复制延迟与主从切换。
- 搭建 3 主 3 从 Cluster，练习 reshard。
- 用 `SLOWLOG`、`LATENCY DOCTOR`、`MEMORY USAGE` 诊断性能问题。

## 关键词地图

- 数据结构：String、Hash、List、Set、ZSet、Bitmap、HyperLogLog、Geo、Stream
- 持久化：RDB、AOF、appendfsync、BGREWRITEAOF、混合持久化
- 内存：maxmemory、LRU、LFU、TTL、lazyfree、big key、hot key
- 原子性：MULTI、EXEC、WATCH、Lua、EVAL、Pipeline
- 消息：Pub/Sub、Stream、Consumer Group、Pending Entries List
- 高可用：replica、Sentinel、failover、quorum、split-brain
- 集群：hash slot、MOVED、ASK、reshard、replica migration
- 监控：INFO、SLOWLOG、LATENCY、MONITOR、redis-benchmark
