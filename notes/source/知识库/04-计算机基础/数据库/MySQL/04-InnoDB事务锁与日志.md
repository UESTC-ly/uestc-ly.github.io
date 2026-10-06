---
tags:
  - MySQL
  - InnoDB
  - 事务
  - 锁
  - MVCC
  - 日志
  - 数据库
created: 2026-06-08
updated: 2026-06-08
---

# 04 - InnoDB 事务、锁与日志

> 本篇定位：解释 MySQL 默认存储引擎 InnoDB 如何保证“并发正确性”和“崩溃可恢复性”。学习顺序建议：先读 [[01-MySQL基础与体系结构]]，再读本篇，最后结合 [[03-MySQL索引与查询优化]] 和 [[05-MySQL运维高可用安全与面试]] 做性能与故障排查。

## 目录

- [[#1. 核心问题：InnoDB 在解决什么]]
- [[#2. 事务与 ACID]]
- [[#3. 隔离级别与并发现象]]
- [[#4. MVCC 与 Read View]]
- [[#5. 快照读、当前读与一致性读]]
- [[#6. InnoDB 锁体系]]
- [[#7. 间隙锁与 Next-Key Lock]]
- [[#8. 死锁分析与处理]]
- [[#9. Undo Log、Redo Log、Binlog]]
- [[#10. 两阶段提交与崩溃恢复]]
- [[#11. Buffer Pool 与内存结构]]
- [[#12. Change Buffer、Doublewrite、AHI]]
- [[#13. Checkpoint、刷脏页与写入路径]]
- [[#14. 事务设计实践]]
- [[#15. 排查命令与诊断模板]]
- [[#16. 高频面试题]]
- [[#17. 复习清单]]
- [[#18. 参考资料]]

---

## 1. 核心问题：InnoDB 在解决什么

InnoDB 的核心职责不是“把数据放进文件”这么简单，而是在高并发和故障环境下同时满足：

1. **正确性**：事务提交后结果符合业务约束，未提交事务不能污染其他事务。
2. **并发性**：多个事务同时读写时，尽量减少互相阻塞。
3. **持久性**：数据库进程、操作系统或机器异常后，已提交事务可恢复。
4. **可恢复性**：未提交事务回滚，已提交事务重做。
5. **可观测性**：通过状态表、错误日志、性能模式和慢查询定位问题。

一句话模型：

> **MVCC 负责“读不挡写、写不挡读”；锁负责“写写冲突与约束正确性”；Redo/Undo/Binlog 负责“回滚、恢复与复制”。**

与其他笔记关系：

- 表结构、SQL 与事务语句见 [[02-SQL语言与数据建模]]。
- 索引结构会影响锁范围，见 [[03-MySQL索引与查询优化]]。
- Binlog 复制、备份恢复、故障处理见 [[05-MySQL运维高可用安全与面试]]。

---

## 2. 事务与 ACID

### 2.1 事务定义

事务是一组逻辑操作，要么全部成功，要么全部失败。典型转账：

```sql
START TRANSACTION;
UPDATE account SET balance = balance - 100 WHERE id = 1;
UPDATE account SET balance = balance + 100 WHERE id = 2;
COMMIT;
```

如果第二条失败，需要回滚第一条：

```sql
ROLLBACK;
```

### 2.2 ACID

| 特性 | 含义 | InnoDB 主要机制 |
|---|---|---|
| Atomicity 原子性 | 事务内操作不可分割 | undo log |
| Consistency 一致性 | 事务前后满足约束 | 约束、锁、事务隔离、业务逻辑 |
| Isolation 隔离性 | 并发事务互相隔离 | MVCC、锁、隔离级别 |
| Durability 持久性 | 提交后故障不丢 | redo log、刷盘策略 |

注意：一致性不是单个机制保证的，而是数据库机制 + 应用约束 + 业务代码共同保证。

### 2.3 自动提交

MySQL 默认开启自动提交：

```sql
SELECT @@autocommit;
```

- `autocommit = 1`：每条语句默认一个事务。
- 显式 `START TRANSACTION` 后，直到 `COMMIT` / `ROLLBACK` 才结束。
- DDL 通常伴随隐式提交，不能简单当作普通 DML 回滚。

### 2.4 事务边界

常见事务控制语句：

```sql
START TRANSACTION;
SAVEPOINT s1;
ROLLBACK TO SAVEPOINT s1;
RELEASE SAVEPOINT s1;
COMMIT;
ROLLBACK;
```

实践原则：

- 事务越短越好。
- 不要在事务中等待用户输入、远程 API、长时间计算。
- 事务中访问顺序保持一致，减少死锁。
- 只把必须原子化的数据库操作放进一个事务。

---

## 3. 隔离级别与并发现象

### 3.1 四种隔离级别

```sql
SELECT @@transaction_isolation;
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;
```

| 隔离级别 | 脏读 | 不可重复读 | 幻读 | MySQL/InnoDB 说明 |
|---|---:|---:|---:|---|
| READ UNCOMMITTED | 可能 | 可能 | 可能 | 几乎不用 |
| READ COMMITTED | 避免 | 可能 | 可能 | 每条一致性读创建新 Read View |
| REPEATABLE READ | 避免 | 避免 | InnoDB 通过 MVCC + next-key lock 处理很多幻读场景 | MySQL 默认 |
| SERIALIZABLE | 避免 | 避免 | 避免 | 并发低，读也可能加锁 |

### 3.2 脏读

读到其他事务未提交的数据。如果对方回滚，本事务读到的数据从未真实存在。

### 3.3 不可重复读

同一事务中两次读取同一行，结果不同。通常因为另一事务提交了更新。

### 3.4 幻读

同一事务中两次按条件读取，第二次出现或消失了符合条件的行。通常与范围查询和插入有关。

### 3.5 MySQL 默认 REPEATABLE READ 的特点

InnoDB 默认隔离级别为 `REPEATABLE READ`。在普通一致性读中，同一事务复用 Read View，因此多次快照读结果稳定；在当前读（如 `SELECT ... FOR UPDATE`、`UPDATE`、`DELETE`）中，需要通过锁约束并发修改。

关键不要混淆：

- **快照读**依赖 MVCC，不加锁。
- **当前读**读最新已提交版本，并可能加锁。
- 幻读讨论必须说明是快照读还是当前读。

---

## 4. MVCC 与 Read View

### 4.1 MVCC 是什么

MVCC（Multi-Version Concurrency Control，多版本并发控制）通过保存数据行的多个历史版本，让读操作可以读取某个时间点的一致性快照。

直觉：

```text
当前行记录 + undo log 版本链 + Read View 可见性规则 = 一致性读
```

### 4.2 隐藏字段

InnoDB 聚簇索引记录中包含内部隐藏信息，常见概念：

- `DB_TRX_ID`：最近修改该行的事务 ID。
- `DB_ROLL_PTR`：指向 undo log 中旧版本的指针。
- `DB_ROW_ID`：无显式主键且无合适唯一键时生成的隐藏行 ID。

### 4.3 Undo 版本链

当事务更新一行：

```sql
UPDATE user SET age = 20 WHERE id = 1;
```

InnoDB 会：

1. 在当前记录写入新值。
2. 记录旧值到 undo log。
3. 当前记录的回滚指针指向旧版本。
4. 多次更新形成版本链。

### 4.4 Read View 包含什么

Read View 是一致性读的“可见性快照”，典型包含：

- 创建 Read View 时活跃事务 ID 列表。
- 当前系统将要分配的下一个事务 ID。
- 当前事务 ID。
- 活跃事务中的最小 ID。

判断思路：

1. 创建该版本的事务如果是本事务，通常可见。
2. 如果版本事务 ID 早于活跃事务最小 ID，说明已提交，可见。
3. 如果版本事务 ID 大于等于下一个事务 ID，说明是未来事务，不可见。
4. 如果版本事务 ID 在活跃事务列表中，不可见。
5. 否则可见。

### 4.5 RC 与 RR 的 Read View 差异

| 隔离级别 | Read View 创建时机 | 结果 |
|---|---|---|
| READ COMMITTED | 每条一致性读语句创建 | 同一事务内可能读到其他事务新提交的数据 |
| REPEATABLE READ | 事务第一次一致性读创建并复用 | 同一事务内快照稳定 |

示例：

```sql
-- T1
START TRANSACTION;
SELECT balance FROM account WHERE id = 1; -- 创建 Read View

-- T2
UPDATE account SET balance = balance + 100 WHERE id = 1;
COMMIT;

-- T1
SELECT balance FROM account WHERE id = 1; -- RR 下仍读旧快照
COMMIT;
```

---

## 5. 快照读、当前读与一致性读

### 5.1 快照读

普通 `SELECT` 通常是快照读：

```sql
SELECT * FROM orders WHERE user_id = 10;
```

特点：

- 不加行锁。
- 通过 MVCC 读取可见版本。
- 在 RR 下同一事务内结果稳定。

### 5.2 当前读

以下语句通常需要读取最新版本并加锁：

```sql
SELECT * FROM orders WHERE id = 1 FOR UPDATE;
SELECT * FROM orders WHERE id = 1 LOCK IN SHARE MODE;
UPDATE orders SET status = 'PAID' WHERE id = 1;
DELETE FROM orders WHERE id = 1;
INSERT INTO orders(id, status) VALUES (1, 'NEW');
```

MySQL 8.0+ 推荐使用标准写法：

```sql
SELECT * FROM orders WHERE id = 1 FOR SHARE;
```

### 5.3 一致性读与锁定读

| 读类型 | 示例 | 是否加锁 | 用途 |
|---|---|---|---|
| 一致性读 | `SELECT ...` | 通常不加锁 | 报表、查询、普通业务读 |
| 共享锁读 | `SELECT ... FOR SHARE` | 加共享锁 | 防止被其他事务修改 |
| 排他锁读 | `SELECT ... FOR UPDATE` | 加排他锁 | 准备更新前锁定 |

实践建议：

- 查询展示用快照读。
- 先读后改且要求并发正确，用 `FOR UPDATE`。
- 不要为了“保险”滥用锁定读，会降低并发。

---

## 6. InnoDB 锁体系

### 6.1 锁粒度

| 锁粒度 | 说明 | 场景 |
|---|---|---|
| 表锁 | 锁整张表 | DDL、元数据锁、特殊操作 |
| 行锁 | 锁索引记录 | InnoDB 常规 DML |
| 间隙锁 | 锁索引记录之间的范围 | 防止范围插入幻影行 |
| Next-Key Lock | 记录锁 + 前方间隙锁 | RR 下范围当前读常见 |

InnoDB 的“行锁”实际锁的是**索引记录**。如果查询不走索引，可能扫描并锁住大量记录，甚至表现得像锁表。因此索引设计直接影响锁范围，见 [[03-MySQL索引与查询优化]]。

### 6.2 共享锁与排他锁

| 锁 | 兼容性 | 说明 |
|---|---|---|
| S Lock 共享锁 | S 与 S 兼容 | 允许多个事务读，阻止写 |
| X Lock 排他锁 | 与 S/X 都不兼容 | 修改行时使用 |

```sql
SELECT * FROM product WHERE id = 1 FOR SHARE;
SELECT * FROM product WHERE id = 1 FOR UPDATE;
```

### 6.3 意向锁

意向锁是表级锁，用于表示事务将要或已经在表中某些行上加锁：

- IS：意向共享锁。
- IX：意向排他锁。

作用：快速判断表锁与行锁是否冲突，避免逐行检查。

### 6.4 记录锁

Record Lock 锁定索引中的某条记录。

```sql
START TRANSACTION;
UPDATE users SET name = 'A' WHERE id = 100;
-- 锁定 PRIMARY 索引 id=100 的记录
```

### 6.5 表级元数据锁 MDL

MySQL 执行 DML/DDL 时会获取 Metadata Lock。

典型问题：

1. 长事务执行 `SELECT` 后未提交，持有表的 MDL 读锁。
2. 另一个会话执行 `ALTER TABLE` 等待 MDL 写锁。
3. 后续所有访问该表的语句可能排队，形成雪崩。

排查：

```sql
SHOW FULL PROCESSLIST;
SELECT * FROM performance_schema.metadata_locks;
```

### 6.6 AUTO-INC 锁

自增列插入涉及 AUTO-INC 机制。参数：

```sql
SHOW VARIABLES LIKE 'innodb_autoinc_lock_mode';
```

一般理解：

- 自增值保证分配，不保证业务连续。
- 回滚、失败插入、复制模式都可能造成自增间隙。
- 不要把自增 ID 连续性作为业务含义。

---

## 7. 间隙锁与 Next-Key Lock

### 7.1 为什么需要间隙锁

在 RR 隔离级别下，如果事务执行范围当前读：

```sql
SELECT * FROM orders WHERE amount BETWEEN 100 AND 200 FOR UPDATE;
```

除了已有记录，还需要阻止其他事务在范围内插入新记录，否则同一事务再次当前读可能出现幻影行。

### 7.2 Gap Lock

Gap Lock 锁定索引记录之间的“间隙”，不锁定记录本身。

例如索引值：

```text
10, 20, 30
```

可能存在间隙：

```text
(-∞,10), (10,20), (20,30), (30,+∞)
```

### 7.3 Next-Key Lock

Next-Key Lock = Record Lock + Gap Lock，锁定一个左开右闭区间。

如果扫描到索引记录 20，可能锁住 `(10,20]`。

### 7.4 唯一索引等值查询

通常情况下，唯一索引等值命中具体记录，可以退化为记录锁：

```sql
UPDATE users SET name = 'x' WHERE id = 1;
```

如果唯一索引等值查询未命中，仍可能锁住插入位置的间隙，防止其他事务插入该键。

### 7.5 非唯一索引范围查询

```sql
UPDATE orders SET status = 'CHECKING'
WHERE user_id = 10 AND created_at >= '2026-01-01';
```

如果 `user_id, created_at` 上有联合索引，锁范围与索引扫描范围相关；如果没有合适索引，锁范围可能扩大。

### 7.6 减少间隙锁影响

- 用唯一索引精确定位要更新的行。
- 避免在大范围内 `FOR UPDATE`。
- 把批量任务拆小批。
- 保持事务短。
- 必要时评估 `READ COMMITTED`，但必须理解语义变化。

---

## 8. 死锁分析与处理

### 8.1 死锁定义

两个或多个事务互相等待对方释放锁，形成环：

```text
T1 持有 A，等待 B
T2 持有 B，等待 A
```

InnoDB 会检测死锁，选择一个事务回滚：

```text
ERROR 1213 (40001): Deadlock found when trying to get lock; try restarting transaction
```

### 8.2 常见死锁原因

1. 多事务更新顺序不一致。
2. 缺少索引导致扫描锁范围过大。
3. 范围更新与插入冲突。
4. 外键级联或唯一约束检查引入额外锁。
5. 长事务持锁时间过长。

### 8.3 典型案例：更新顺序相反

```sql
-- T1
START TRANSACTION;
UPDATE account SET balance = balance - 10 WHERE id = 1;
UPDATE account SET balance = balance + 10 WHERE id = 2;

-- T2
START TRANSACTION;
UPDATE account SET balance = balance - 10 WHERE id = 2;
UPDATE account SET balance = balance + 10 WHERE id = 1;
```

解决：统一按主键升序访问：

```text
所有转账都先锁 id 小的账户，再锁 id 大的账户。
```

### 8.4 查看最近一次死锁

```sql
SHOW ENGINE INNODB STATUS\G
```

重点阅读：

- `LATEST DETECTED DEADLOCK`
- 两个事务执行的 SQL
- 等待的锁类型
- 持有的锁类型
- 使用的索引

### 8.5 死锁处理原则

- 应用层必须能重试可重入事务。
- 重试要有次数上限和退避。
- 事务内操作保持固定顺序。
- 为 WHERE 条件建立合适索引。
- 拆分大事务。
- 监控死锁频率，偶发死锁不等于系统异常，频繁死锁才需要结构性治理。

---

## 9. Undo Log、Redo Log、Binlog

### 9.1 三类日志对比

| 日志 | 所属 | 主要用途 | 是否 InnoDB 特有 |
|---|---|---|---|
| undo log | InnoDB | 回滚、MVCC 旧版本 | 是 |
| redo log | InnoDB | 崩溃恢复、持久性 | 是 |
| binlog | MySQL Server 层 | 复制、时间点恢复、审计 | 否 |

### 9.2 Undo Log

用途：

1. 事务回滚时恢复旧值。
2. MVCC 一致性读沿版本链找到可见版本。

注意：

- 长事务会阻碍 undo 清理，造成历史版本堆积。
- 长事务还可能导致备份、DDL、主从延迟等问题。

查看事务：

```sql
SELECT *
FROM information_schema.innodb_trx\G
```

### 9.3 Redo Log

Redo log 记录物理页修改，用于崩溃恢复。

WAL（Write-Ahead Logging）原则：

> 修改数据页前，先确保相应 redo 已持久化到日志。

提交时不一定立刻把数据页写回磁盘，但必须保证 redo 满足持久性策略。

关键参数：

```sql
SHOW VARIABLES LIKE 'innodb_flush_log_at_trx_commit';
```

常见值：

| 值 | 提交行为 | 持久性 | 性能 |
|---|---|---|---|
| 1 | 每次提交写入并 fsync redo | 最强 | 较低 |
| 2 | 每次提交写入 OS cache，约每秒 fsync | 可能丢 1 秒 | 较高 |
| 0 | 约每秒写入并 fsync | 可能丢 1 秒以上 | 高 |

生产核心交易一般使用 `1`。

### 9.4 Binlog

Binlog 是 Server 层二进制日志，用于：

- 主从复制。
- 时间点恢复（PITR）。
- 数据审计与增量订阅。

常见格式：

| 格式 | 说明 |
|---|---|
| STATEMENT | 记录 SQL，可能受非确定函数影响 |
| ROW | 记录行变化，复制更可靠，日志更大 |
| MIXED | 混合模式 |

生产通常更偏向 `ROW`。

关键参数：

```sql
SHOW VARIABLES LIKE 'binlog_format';
SHOW VARIABLES LIKE 'sync_binlog';
```

`sync_binlog=1` 持久性更强，但性能成本更高。

---

## 10. 两阶段提交与崩溃恢复

### 10.1 为什么需要两阶段提交

一次事务提交同时涉及：

- InnoDB redo log
- MySQL binlog

如果两者不一致，会出现：

- 本机恢复后有数据，但 binlog 没有，副本丢事务。
- binlog 有事务，但本机恢复后没有，主从不一致。

### 10.2 基本流程

简化理解：

```text
1. InnoDB 写 redo，状态 prepare
2. Server 写 binlog
3. InnoDB 写 redo，状态 commit
```

崩溃恢复时根据 redo 状态与 binlog 是否完整决定提交或回滚。

### 10.3 崩溃点分析

| 崩溃位置 | 恢复判断 |
|---|---|
| redo prepare 前 | 事务未提交，回滚 |
| redo prepare 后、binlog 前 | binlog 无完整事务，回滚 |
| binlog 后、redo commit 前 | binlog 完整，提交 |
| redo commit 后 | 提交 |

### 10.4 组提交

为了降低 fsync 成本，MySQL 支持 binlog group commit，把多个事务的刷盘合并。理解点：

- 持久性参数越严格，fsync 越频繁。
- 组提交提升吞吐，但仍要在延迟与安全之间权衡。
- 高并发小事务场景中组提交效果明显。

### 10.5 恢复类型

| 类型 | 依赖 | 目的 |
|---|---|---|
| 崩溃恢复 | redo + undo | 数据库异常退出后自动恢复 |
| 事务回滚 | undo | 用户主动回滚或死锁牺牲事务 |
| 时间点恢复 | 全量备份 + binlog | 恢复到误删前某一时刻 |
| 复制恢复 | binlog/relay log | 副本追赶主库 |

---

## 11. Buffer Pool 与内存结构

### 11.1 Buffer Pool 是什么

Buffer Pool 是 InnoDB 最重要的内存区域，用来缓存：

- 数据页。
- 索引页。
- undo 页。
- 自适应哈希相关结构。
- 插入缓冲相关页。

读写路径：

```text
查询 -> 先查 Buffer Pool -> 未命中再读磁盘页 -> 放入 Buffer Pool
更新 -> 修改 Buffer Pool 中页 -> 标记脏页 -> 后台刷盘
```

### 11.2 页

InnoDB 默认页大小通常为 16KB。B+Tree、Buffer Pool、redo 记录等都围绕页工作。

### 11.3 LRU 改进

传统 LRU 容易被全表扫描污染。InnoDB Buffer Pool 使用改进 LRU，把列表分为：

- young 区：热点页。
- old 区：新读入页先进入 old 区。

参数：

```sql
SHOW VARIABLES LIKE 'innodb_old_blocks_pct';
SHOW VARIABLES LIKE 'innodb_old_blocks_time';
```

### 11.4 Buffer Pool 参数

```sql
SHOW VARIABLES LIKE 'innodb_buffer_pool_size';
SHOW VARIABLES LIKE 'innodb_buffer_pool_instances';
```

经验：

- 专用数据库服务器上，Buffer Pool 往往占内存大头。
- 不要机械设置为 80%，需要给连接、排序、临时表、OS cache、备份等留空间。
- 观察命中率、脏页比例、刷盘压力后调整。

### 11.5 脏页

被修改但尚未刷入数据文件的页称为脏页。脏页不代表不安全，只要 redo 已持久化，崩溃后可重放恢复。

---

## 12. Change Buffer、Doublewrite、AHI

### 12.1 Change Buffer

Change Buffer 用于缓存对二级索引页的变更，特别是非唯一二级索引页不在 Buffer Pool 时，可以先缓冲变更，之后读入页面时再合并。

适合：

- 写多读少。
- 非唯一二级索引。
- 插入/更新/删除二级索引键。

不适合：

- 唯一索引，因为必须检查唯一性。
- 写后立即大量读，合并成本可能转移到读路径。

参数：

```sql
SHOW VARIABLES LIKE 'innodb_change_buffering';
SHOW VARIABLES LIKE 'innodb_change_buffer_max_size';
```

### 12.2 Doublewrite Buffer

Doublewrite 解决“页写到一半崩溃”的 torn page 问题。

简化流程：

```text
脏页 -> doublewrite 区域 -> fsync -> 数据文件真实位置
```

崩溃后如果数据页损坏，可从 doublewrite 中找到完整页，再结合 redo 恢复。

### 12.3 Adaptive Hash Index

自适应哈希索引（AHI）是 InnoDB 根据访问模式自动为热点页建立的哈希访问路径。

特点：

- 对等值热点查询可能有帮助。
- 高并发下可能引入争用。
- 是否启用需要基于压测和监控判断。

参数：

```sql
SHOW VARIABLES LIKE 'innodb_adaptive_hash_index';
```

---

## 13. Checkpoint、刷脏页与写入路径

### 13.1 Checkpoint 作用

Redo log 容量有限，如果一直只写 redo 不刷数据页，恢复时间会变长，redo 也会被写满。Checkpoint 标记：

> 到某个 LSN 之前的脏页已经或正在安全落盘，崩溃恢复只需从 checkpoint 后开始重放。

### 13.2 LSN

LSN（Log Sequence Number）是日志序列号，用来表示 redo 写入位置和页刷新进度。

查看状态：

```sql
SHOW ENGINE INNODB STATUS\G
```

关注：

- Log sequence number
- Log flushed up to
- Pages flushed up to
- Last checkpoint at

### 13.3 刷脏页触发因素

- Buffer Pool 空间不足。
- Redo log 接近写满。
- 后台线程周期性刷新。
- 正常关闭。
- Checkpoint 推进需求。

### 13.4 写入路径简化

```text
1. 修改 Buffer Pool 中的数据页
2. 生成 undo，支持回滚和旧版本
3. 生成 redo，记录页级修改
4. 提交时按策略刷 redo
5. 数据页稍后异步刷盘
6. 若开启 binlog，还要完成 binlog 与 redo 的一致提交
```

### 13.5 写性能调优方向

- 减少不必要索引，降低二级索引维护成本。
- 批量写入但控制事务大小。
- 避免热点行频繁更新。
- 合理设置 redo 容量和刷盘策略。
- 避免 Buffer Pool 太小导致频繁读写磁盘。

---

## 14. 事务设计实践

### 14.1 保持事务短小

反例：

```text
开启事务 -> 查数据库 -> 调第三方支付 API -> 等用户确认 -> 更新订单 -> 提交
```

问题：持锁时间长、连接占用、死锁概率增加。

改进：

```text
创建待支付订单并提交 -> 调支付 API -> 支付回调中短事务更新状态
```

### 14.2 固定访问顺序

批量更新多行时统一排序：

```sql
SELECT id FROM account WHERE id IN (3,1,2) ORDER BY id FOR UPDATE;
```

### 14.3 用索引缩小锁范围

```sql
-- 危险：无索引 status 时可能扫描大量记录
UPDATE orders SET status = 'TIMEOUT'
WHERE status = 'NEW' AND created_at < NOW() - INTERVAL 30 MINUTE;

-- 建议：为批处理条件设计组合索引
CREATE INDEX idx_status_created ON orders(status, created_at);
```

### 14.4 乐观锁

适合冲突不高场景：

```sql
UPDATE product
SET stock = stock - 1,
    version = version + 1
WHERE id = 100
  AND stock > 0
  AND version = 7;
```

影响行数为 1 表示成功，为 0 表示版本冲突或库存不足。

### 14.5 悲观锁

适合冲突高或必须串行化场景：

```sql
START TRANSACTION;
SELECT stock FROM product WHERE id = 100 FOR UPDATE;
UPDATE product SET stock = stock - 1 WHERE id = 100 AND stock > 0;
COMMIT;
```

注意：悲观锁必须配合短事务。

### 14.6 幂等与重试

死锁、锁等待超时、网络抖动都要求应用具备幂等重试能力。

实践：

- 每个外部请求有业务唯一键。
- 写入前检查状态。
- 重试只包裹可重入事务。
- 区分“未知提交结果”和“明确失败”。

### 14.7 批处理事务

大批量更新建议分批：

```sql
UPDATE orders
SET archived = 1
WHERE archived = 0
ORDER BY id
LIMIT 1000;
```

循环执行，直到影响行数为 0。优势：

- 降低单事务 undo/redo 压力。
- 缩短锁持有时间。
- 降低复制延迟。
- 更容易中断和恢复。

---

## 15. 排查命令与诊断模板

### 15.1 查看事务

```sql
SELECT
  trx_id,
  trx_state,
  trx_started,
  trx_wait_started,
  trx_mysql_thread_id,
  trx_query
FROM information_schema.innodb_trx
ORDER BY trx_started;
```

### 15.2 查看锁等待

MySQL 8.0+ 可结合 `performance_schema`：

```sql
SELECT *
FROM performance_schema.data_lock_waits\G
```

```sql
SELECT *
FROM performance_schema.data_locks\G
```

### 15.3 查看 InnoDB 状态

```sql
SHOW ENGINE INNODB STATUS\G
```

关注：

- `TRANSACTIONS`
- `LATEST DETECTED DEADLOCK`
- `BUFFER POOL AND MEMORY`
- `LOG`
- `ROW OPERATIONS`

### 15.4 查看长事务

```sql
SELECT
  trx_mysql_thread_id AS thread_id,
  TIMESTAMPDIFF(SECOND, trx_started, NOW()) AS trx_seconds,
  trx_state,
  trx_query
FROM information_schema.innodb_trx
WHERE trx_started < NOW() - INTERVAL 60 SECOND
ORDER BY trx_started;
```

### 15.5 查看等待线程

```sql
SHOW FULL PROCESSLIST;
```

或者：

```sql
SELECT *
FROM performance_schema.threads
WHERE PROCESSLIST_STATE IS NOT NULL;
```

### 15.6 锁等待超时参数

```sql
SHOW VARIABLES LIKE 'innodb_lock_wait_timeout';
```

错误：

```text
ERROR 1205 (HY000): Lock wait timeout exceeded; try restarting transaction
```

区别：

- 死锁：InnoDB 检测到环，主动回滚一个事务，错误 1213。
- 锁等待超时：等待超过阈值，错误 1205。

### 15.7 诊断模板

```text
问题：接口变慢 / SQL 卡住 / 订单无法更新

1. 是否存在长事务？
   - information_schema.innodb_trx
2. 是否存在锁等待？
   - performance_schema.data_lock_waits
3. 等待 SQL 和持锁 SQL 分别是什么？
   - SHOW FULL PROCESSLIST
4. 使用了哪个索引？锁范围是否过大？
   - EXPLAIN
5. 是否有 DDL 等待 MDL？
   - performance_schema.metadata_locks
6. 是否近期发布了批处理或大事务？
7. 临时处理：是否可安全 kill blocker？
8. 根治：索引、事务边界、访问顺序、批量大小。
```

---

## 16. 高频面试题

### 16.1 MVCC 解决了什么问题？

MVCC 通过行版本链和 Read View，让普通 SELECT 可以读取一致性快照，不必等待正在写入的事务释放锁，从而提升读写并发。它主要解决读写冲突，不解决写写冲突；写写冲突仍需锁。

### 16.2 RR 下为什么普通 SELECT 可重复读？

因为 InnoDB 在 RR 下通常在事务第一次一致性读时创建 Read View，并在事务内复用。后续普通 SELECT 根据同一个可见性快照沿 undo 版本链找到可见版本。

### 16.3 当前读和快照读有什么区别？

- 快照读：普通 SELECT，读符合 Read View 的历史版本，不加锁。
- 当前读：UPDATE/DELETE/INSERT、`SELECT ... FOR UPDATE/FOR SHARE`，读取最新可见记录并加锁。

### 16.4 为什么索引会影响锁？

InnoDB 行锁锁的是索引记录。WHERE 条件能用高选择性索引时，锁范围小；不能用索引时，扫描范围变大，锁住的记录更多，并发更差。

### 16.5 Redo、Undo、Binlog 区别？

- Undo：回滚和 MVCC 旧版本。
- Redo：InnoDB 崩溃恢复，保证提交事务持久性。
- Binlog：Server 层日志，用于复制和时间点恢复。

### 16.6 两阶段提交解决什么？

解决 redo log 与 binlog 的一致性问题，避免主库崩溃恢复后的数据与用于复制/恢复的 binlog 不一致。

### 16.7 什么是间隙锁？

间隙锁锁定索引记录之间的范围，阻止其他事务在该范围插入新记录，主要用于 RR 下当前读防止幻读。

### 16.8 死锁如何处理？

短期：捕获错误并重试。长期：统一访问顺序、补充索引、缩短事务、拆分批处理、减少范围锁、定位死锁日志。

### 16.9 为什么长事务危险？

长事务会长时间持锁，阻碍 undo 清理，扩大历史版本链，影响 DDL、备份、复制延迟和系统稳定性。

### 16.10 `innodb_flush_log_at_trx_commit=1` 为什么更安全？

因为每次事务提交都要求 redo log 写入并刷盘，数据库崩溃后已提交事务更可靠地恢复。代价是更多 fsync，性能可能下降。

---

## 17. 复习清单

### 17.1 必背概念

- ACID
- 隔离级别
- 脏读、不可重复读、幻读
- MVCC
- Read View
- Undo 版本链
- 快照读与当前读
- 共享锁与排他锁
- 意向锁
- 记录锁、间隙锁、Next-Key Lock
- 死锁
- Undo Log
- Redo Log
- Binlog
- 两阶段提交
- Buffer Pool
- Dirty Page
- Checkpoint
- Doublewrite

### 17.2 必会命令

```sql
SELECT @@transaction_isolation;
SHOW ENGINE INNODB STATUS\G
SELECT * FROM information_schema.innodb_trx\G
SELECT * FROM performance_schema.data_locks\G
SELECT * FROM performance_schema.data_lock_waits\G
SHOW FULL PROCESSLIST;
SHOW VARIABLES LIKE 'innodb_flush_log_at_trx_commit';
SHOW VARIABLES LIKE 'sync_binlog';
```

### 17.3 必会分析路径

1. SQL 是否在事务中？事务是否过长？
2. SQL 是快照读还是当前读？
3. WHERE 条件走了什么索引？
4. 锁的是记录、间隙还是 next-key？
5. 是否存在锁等待或死锁？
6. Redo/Undo/Binlog 中哪个机制相关？
7. 是否可通过缩短事务、补索引、统一顺序解决？

### 17.4 与其他主题联动

- SQL 写法：[[02-SQL语言与数据建模]]
- 索引与执行计划：[[03-MySQL索引与查询优化]]
- 复制与恢复：[[05-MySQL运维高可用安全与面试]]
- 基础架构：[[01-MySQL基础与体系结构]]

---

## 18. 参考资料

> 以下为本笔记建议继续阅读的官方文档入口；具体版本以当前生产环境版本为准。

- MySQL 8.4 Reference Manual - InnoDB Storage Engine: <https://dev.mysql.com/doc/refman/8.4/en/innodb-storage-engine.html>
- MySQL 8.4 Reference Manual - InnoDB Transaction Model: <https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-model.html>
- MySQL 8.4 Reference Manual - InnoDB Locking: <https://dev.mysql.com/doc/refman/8.4/en/innodb-locking.html>
- MySQL 8.4 Reference Manual - InnoDB Multi-Versioning: <https://dev.mysql.com/doc/refman/8.4/en/innodb-multi-versioning.html>
- MySQL 8.4 Reference Manual - InnoDB Redo Log: <https://dev.mysql.com/doc/refman/8.4/en/innodb-redo-log.html>
- MySQL 8.4 Reference Manual - Binary Log: <https://dev.mysql.com/doc/refman/8.4/en/binary-log.html>

---

## 验证记录

- 本文件由主 agent 在第 4 子 agent 网络中断后补齐。
- 文件仅写入当前 MySQL 知识库目录。
- SQL 示例用于学习与排查模板，未连接真实 MySQL 实例执行。
- 建议在个人测试库中复现实验：隔离级别、快照读/当前读、死锁、锁等待、redo/binlog 参数差异。
