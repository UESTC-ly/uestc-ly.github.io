# 01-Redis 概览与环境准备

> 适用版本：以 Redis 7.x 为主。部分命令在 Redis 6.x 或更早版本中也可用，但 ACL、多线程 I/O、函数、RESP3、部分配置项和模块生态在不同版本间存在差异。

## 学习目标

学习本章后，你应该能够：

- 说清 Redis 是什么、适合解决哪些问题、不适合解决哪些问题。
- 理解 Redis 的核心特征：内存存储、单线程命令执行模型、数据结构服务器、持久化、高可用与集群。
- 在本地启动一个 Redis 7.x 环境，并使用 `redis-cli` 完成连接、读写和基础诊断。
- 认识常见配置项的作用，能区分开发环境和生产环境配置关注点。
- 建立学习 Redis 的全局地图，为后续数据类型、持久化、复制、哨兵、集群和性能优化打基础。

## 核心概念

### Redis 是什么

Redis（Remote Dictionary Server）是一个开源的内存数据结构服务器。它常被称为“缓存数据库”，但更准确地说，它是一个支持多种数据结构、可选持久化、可用于缓存、计数器、排行榜、消息队列、分布式锁、会话存储、限流等场景的键值数据库。

Redis 的基本模型是：

```text
客户端 -> Redis 命令 -> Redis Server -> 内存中的 key-value 数据结构
```

其中 value 不只是字符串，还可以是 Hash、List、Set、Sorted Set、Stream、Bitmap、HyperLogLog、Geospatial 等结构。

### Redis 的主要特点

| 特点 | 说明 | 学习时要关注 |
| --- | --- | --- |
| 内存优先 | 主要数据保存在内存中，读写延迟低 | 内存容量、淘汰策略、持久化风险 |
| 数据结构丰富 | 原生命令支持多种结构 | 根据业务模型选择合适结构 |
| 单线程命令执行 | 核心命令通常在单线程事件循环中执行 | 避免慢命令、大 key、阻塞操作 |
| 可持久化 | 支持 RDB、AOF、混合持久化 | 数据安全与性能之间的取舍 |
| 高可用 | 支持复制、哨兵、集群 | 主从切换、分片、故障恢复 |
| 原子命令 | 单条命令执行具备原子性 | 可用于计数、抢占、条件写入 |
| 扩展能力 | 支持 Lua、Functions、Modules | 复杂逻辑要谨慎控制耗时 |

> 注意：Redis 不是“万能加速器”。如果数据模型、过期策略、内存估算、持久化和高可用设计不清晰，Redis 也可能成为系统瓶颈或数据风险点。

### Redis 常见使用场景

#### 1. 缓存

把数据库或外部接口的热点结果放入 Redis，减少后端压力。

```text
应用先查 Redis
命中：直接返回
未命中：查数据库 -> 写入 Redis -> 返回
```

常见问题：缓存穿透、缓存击穿、缓存雪崩、双写一致性。

#### 2. 计数器

利用 `INCR`、`DECR` 等原子命令实现访问量、点赞数、库存预扣等计数。

#### 3. 排行榜

使用 Sorted Set 按分数排序，例如积分榜、热度榜、延迟队列。

#### 4. 分布式协调

通过 `SET key value NX EX seconds` 实现基础分布式锁。生产环境还需要考虑锁续期、唯一 token、释放锁原子性、故障场景。

#### 5. 消息与事件流

List 可实现简单队列；Stream 更适合消费组、消息 ID、确认机制等更完整的消息流场景。

### Redis 与关系型数据库的区别

| 维度 | Redis | MySQL/PostgreSQL 等关系型数据库 |
| --- | --- | --- |
| 主要存储介质 | 内存为主 | 磁盘为主，缓存辅助 |
| 数据模型 | key-value + 多数据结构 | 表、行、列、关系、SQL |
| 查询方式 | 按 key 或结构命令访问 | SQL 查询、索引、事务 |
| 典型优势 | 低延迟、高并发、原子结构操作 | 强一致事务、复杂查询、长期存储 |
| 典型风险 | 内存成本、数据丢失窗口、大 key | 慢查询、锁竞争、扩展复杂 |

Redis 常作为关系型数据库的补充，而不是简单替代。

## 环境准备

### 方式一：Docker 启动 Redis 7.x

适合快速学习与实验。

```bash
docker run --name redis7-study -p 6379:6379 -d redis:7
```

连接：

```bash
docker exec -it redis7-study redis-cli
```

验证：

```redis
PING
SET hello redis
GET hello
```

预期：

```text
PONG
OK
"redis"
```

停止与删除容器：

```bash
docker stop redis7-study
docker rm redis7-study
```

### 方式二：macOS 使用 Homebrew

```bash
brew install redis
redis-server --version
redis-server
```

另开终端连接：

```bash
redis-cli
```

如果作为服务运行：

```bash
brew services start redis
brew services stop redis
```

### 方式三：源码编译

适合想了解 Redis 构建过程或调试源码的学习者。

```bash
git clone https://github.com/redis/redis.git
cd redis
make
src/redis-server --version
src/redis-server
```

> 学习阶段建议优先使用 Docker 或 Homebrew，减少环境干扰。生产环境请使用明确版本、配置文件、数据目录和监控方案。

## 关键命令/配置

### 基础连接命令

```bash
redis-cli -h 127.0.0.1 -p 6379
redis-cli -a 'your-password'
redis-cli --raw
```

常用交互命令：

```redis
PING
ECHO "hello redis"
SELECT 0
DBSIZE
INFO server
INFO memory
INFO stats
CONFIG GET maxmemory
```

说明：

- `PING`：检查连接是否正常。
- `SELECT`：选择逻辑库，默认 0。Redis Cluster 模式下通常只使用 0 号库。
- `DBSIZE`：返回当前库 key 数量，不等同于业务记录数。
- `INFO`：查看服务状态，是排查问题的重要入口。
- `CONFIG GET`：查看运行时配置。部分配置可用 `CONFIG SET` 临时修改，但生产环境应同步到配置文件或部署系统。

### 常见配置项

以下配置通常位于 `redis.conf`，不同安装方式路径不同。

```conf
bind 127.0.0.1
port 6379
protected-mode yes
requirepass yourStrongPassword

daemonize no
dir /var/lib/redis
dbfilename dump.rdb

save 900 1
save 300 10
save 60 10000

appendonly no
appendfsync everysec

maxmemory 1gb
maxmemory-policy allkeys-lru

loglevel notice
slowlog-log-slower-than 10000
slowlog-max-len 128
```

重点理解：

| 配置 | 作用 | 学习提示 |
| --- | --- | --- |
| `bind` | 监听地址 | 不要随意暴露到公网 |
| `protected-mode` | 保护模式 | 开发机安全兜底，生产仍需网络隔离和认证 |
| `requirepass` | 简单密码认证 | Redis 6+ 更推荐理解 ACL |
| `dir` / `dbfilename` | RDB 文件位置 | 确保数据目录可写且可备份 |
| `save` | RDB 快照规则 | 数据安全与性能的折中 |
| `appendonly` | 是否开启 AOF | 需要更低数据丢失窗口时常开启 |
| `appendfsync` | AOF 刷盘策略 | `everysec` 是常见折中 |
| `maxmemory` | 最大内存 | 缓存场景必须设置容量上限 |
| `maxmemory-policy` | 内存淘汰策略 | 决定内存满时如何处理 key |
| `slowlog-*` | 慢日志 | 定位慢命令和大 key 问题 |

### Redis 7.x 版本视角

Redis 7.x 相比早期版本，在 Functions、ACL、复制、集群、性能与命令能力方面持续增强。入门阶段可以先掌握通用命令和核心机制，再逐步学习：

- Redis 6.x 引入 ACL、多线程 I/O 等重要能力。
- Redis 7.x 强化 Functions，可作为 Lua 脚本之外的服务端逻辑组织方式。
- Redis 7.2 之后许可与发行版本讨论较多，学习命令和架构时仍可按 Redis 7.x 通用能力理解。

## 示例

### 示例 1：一次完整的本地交互

```redis
PING
SET user:1:name "Ada"
GET user:1:name
EXPIRE user:1:name 60
TTL user:1:name
DEL user:1:name
EXISTS user:1:name
```

说明：

- `SET` 写入字符串。
- `EXPIRE` 设置过期时间。
- `TTL` 查看剩余生存时间。
- `DEL` 删除 key。
- `EXISTS` 判断 key 是否存在。

### 示例 2：带过期时间的缓存写入

推荐使用一条原子命令：

```redis
SET article:1001 '{"title":"Redis intro"}' EX 300
```

不要写成两步：

```redis
SET article:1001 '{"title":"Redis intro"}'
EXPIRE article:1001 300
```

原因：两步之间如果应用崩溃，key 可能没有过期时间，形成脏缓存或长期占用内存。

### 示例 3：查看内存与慢日志

```redis
INFO memory
SLOWLOG GET 10
SLOWLOG LEN
```

如果发现 `used_memory` 持续增长，需要进一步排查：

- 是否没有设置 TTL。
- 是否存在大 key。
- 是否过期策略不合理。
- 是否 `maxmemory` 与淘汰策略未配置。

## 常见误区

### 误区 1：Redis 很快，所以任何数据都可以放进去

Redis 快的前提是命令足够轻、数据结构使用合理、网络和内存没有成为瓶颈。超大 value、超大集合、全量扫描命令都可能造成阻塞。

### 误区 2：Redis 是内存数据库，所以不用关心持久化

缓存可以允许丢失，业务状态通常不能随意丢失。是否开启 RDB/AOF，取决于数据是否可重建、允许丢失多少秒、恢复时间要求是多少。

### 误区 3：设置了密码就安全了

Redis 安全还包括网络隔离、防火墙、最小权限 ACL、禁用危险命令或限制访问、不要暴露公网、日志与审计。

### 误区 4：`KEYS *` 是查看 key 的常规方式

`KEYS` 会遍历整个 key 空间，生产环境可能阻塞 Redis。排查时优先使用 `SCAN` 渐进式遍历。

### 误区 5：逻辑库可以替代多租户隔离

Redis 的逻辑库隔离能力有限，Cluster 模式也不支持多逻辑库的常规使用。不同环境、租户或业务线通常应使用独立实例、前缀规范或明确隔离方案。

## 实践检查清单

- [ ] 能启动 Redis 7.x，并通过 `redis-cli` 执行 `PING`。
- [ ] 能完成 `SET`、`GET`、`DEL`、`EXPIRE`、`TTL` 的基础操作。
- [ ] 能解释 Redis 为什么快，以及哪些操作会让它变慢。
- [ ] 能说出 Redis 和关系型数据库的边界。
- [ ] 能查看 `INFO server`、`INFO memory`、`INFO stats`。
- [ ] 能说明 RDB 与 AOF 是什么，以及是否需要开启取决于什么。
- [ ] 能解释为什么缓存 key 应该设置过期时间。
- [ ] 能说出至少 3 个 Redis 生产环境安全注意点。

## 延伸阅读关键词

- Redis 7.x 官方文档
- Redis data structures
- redis-cli
- redis.conf
- RDB persistence
- AOF persistence
- Redis ACL
- Redis slowlog
- Redis maxmemory policy
- Redis single-threaded event loop
- Redis cache aside pattern
