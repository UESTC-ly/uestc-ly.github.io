---
tags:
  - MySQL
  - 数据库
  - 知识体系
  - Obsidian索引
created: 2026-06-08
updated: 2026-06-08
---

# MySQL 知识体系总览

> 这是当前目录下 MySQL 笔记的入口页。建议从基础、SQL、索引、InnoDB、运维五条主线逐步复习。

## 1. 分卷目录

| 顺序 | 笔记 | 主题定位 | 适合解决的问题 |
|---:|---|---|---|
| 01 | [[01-MySQL基础与体系结构]] | MySQL 是什么、如何运行、有哪些核心组件 | 入门、版本选择、安装连接、逻辑架构、存储引擎 |
| 02 | [[02-SQL语言与数据建模]] | SQL 语言、表设计、查询表达能力 | 建表、数据类型、约束、JOIN、CTE、窗口函数、过程对象 |
| 附 | [[mysql语言]] | MySQL 语言速查 | DDL、DML、DQL、DCL、TCL、MySQL 方言与常见坑 |
| 03 | [[03-MySQL索引与查询优化]] | 索引结构、执行计划、SQL 性能优化 | 慢查询、EXPLAIN、联合索引、分页、排序、JOIN 优化 |
| 04 | [[04-InnoDB事务锁与日志]] | InnoDB 并发控制与崩溃恢复 | 事务、隔离级别、MVCC、锁、死锁、redo/undo/binlog |
| 05 | [[05-MySQL运维高可用安全与面试]] | 生产运维、高可用、安全、故障与面试 | 备份恢复、复制、GTID、组复制、监控、调参、安全、Runbook |

## 2. 推荐学习路线

### 2.1 入门路线

1. [[01-MySQL基础与体系结构]]：先建立整体地图。
2. [[02-SQL语言与数据建模]]：掌握 SQL 与表设计；需要语法速查时看 [[mysql语言]]。
3. [[03-MySQL索引与查询优化]]：理解为什么 SQL 会快或慢。
4. [[04-InnoDB事务锁与日志]]：理解并发与数据安全。
5. [[05-MySQL运维高可用安全与面试]]：进入生产实践。

### 2.2 面试路线

1. 索引：B+Tree、聚簇索引、联合索引、最左前缀、覆盖索引。
2. 事务：ACID、隔离级别、MVCC、Read View、快照读/当前读。
3. 锁：行锁、间隙锁、Next-Key Lock、死锁排查。
4. 日志：undo、redo、binlog、两阶段提交、崩溃恢复。
5. 优化：EXPLAIN、慢查询、分页、JOIN、排序、临时表。
6. 运维：备份恢复、复制延迟、GTID、高可用、安全加固。

### 2.3 生产排障路线

1. 先看 [[05-MySQL运维高可用安全与面试]] 的 Runbook。
2. SQL 慢：跳转 [[03-MySQL索引与查询优化]]。
3. 锁等待/死锁：跳转 [[04-InnoDB事务锁与日志]]。
4. 表结构/SQL 写法问题：跳转 [[02-SQL语言与数据建模]]。
5. 版本、参数、工具不清楚：跳转 [[01-MySQL基础与体系结构]]。

## 3. 核心知识点总表

### 3.1 基础架构

- MySQL Server 层与存储引擎层分离。
- 连接器、解析器、优化器、执行器共同完成 SQL 执行。
- InnoDB 是默认且最常用的事务型存储引擎。
- `information_schema`、`performance_schema`、`mysql`、`sys` 是排查与管理的重要系统库。

### 3.2 SQL 与建模

- DDL 定义结构，DML 修改数据，DQL 查询数据，DCL 管权限，TCL 控事务。
- 表设计优先保证业务语义、约束正确、查询路径清晰。
- 数据类型要“够用且精确”：金额避免浮点，时间统一时区策略，字符集优先 `utf8mb4`。
- 范式减少冗余，反范式换取查询性能；反范式必须有一致性维护策略。

### 3.3 索引与优化

- InnoDB 表数据按主键聚簇组织。
- 二级索引叶子节点保存主键值，可能需要回表。
- 联合索引遵循最左前缀，但优化器也会基于成本做选择。
- 覆盖索引、索引下推、合理排序索引可显著减少 I/O。
- `EXPLAIN` 看计划，慢查询日志找样本，`EXPLAIN ANALYZE` 看实际执行。

### 3.4 事务、锁与日志

- MVCC 通过 undo 版本链与 Read View 支持一致性读。
- 快照读通常不加锁，当前读会读取最新版本并加锁。
- InnoDB 行锁锁的是索引记录，索引缺失会扩大锁范围。
- redo 保证崩溃恢复，undo 支持回滚和 MVCC，binlog 支持复制和时间点恢复。
- 两阶段提交保证 redo 与 binlog 一致。

### 3.5 运维与高可用

- 备份必须定期恢复演练；没有验证过的备份不等于可用备份。
- 复制延迟要结合 binlog、relay log、事务大小、SQL 线程/并行复制分析。
- GTID 简化主从切换和故障恢复。
- 高可用不是单个组件，而是监控、切换、备份、演练、权限、容量共同组成。
- 安全加固包括最小权限、TLS、密码策略、审计、网络隔离、升级补丁。

## 4. 常用诊断入口

```sql
-- 版本与基础信息
SELECT VERSION();
SHOW VARIABLES LIKE 'version%';

-- 当前连接与运行 SQL
SHOW FULL PROCESSLIST;

-- 执行计划
EXPLAIN FORMAT=TREE SELECT ...;
EXPLAIN ANALYZE SELECT ...;

-- InnoDB 状态
SHOW ENGINE INNODB STATUS\G

-- 长事务
SELECT * FROM information_schema.innodb_trx\G

-- 锁等待（MySQL 8.0+）
SELECT * FROM performance_schema.data_locks\G
SELECT * FROM performance_schema.data_lock_waits\G

-- 关键持久性参数
SHOW VARIABLES LIKE 'innodb_flush_log_at_trx_commit';
SHOW VARIABLES LIKE 'sync_binlog';
```

## 5. 版本阅读建议

- 生产环境优先围绕当前实际部署版本阅读官方手册。
- MySQL 8.4 是 LTS 长期支持线，适合作为稳定生产知识主轴。
- MySQL 9.x 属于持续演进线，学习新特性时要确认生产环境是否已经采用。
- 本目录笔记以 MySQL 8.0/8.4 的通用机制为主，遇到版本差异以官方手册和线上实例为准。

## 6. 官方参考入口

- MySQL Documentation: <https://dev.mysql.com/doc/>
- MySQL 8.4 Reference Manual: <https://dev.mysql.com/doc/refman/8.4/en/>
- MySQL 8.4 InnoDB: <https://dev.mysql.com/doc/refman/8.4/en/innodb-storage-engine.html>
- MySQL 8.4 Optimization: <https://dev.mysql.com/doc/refman/8.4/en/optimization.html>
- MySQL 8.4 Backup and Recovery: <https://dev.mysql.com/doc/refman/8.4/en/backup-and-recovery.html>

## 7. 后续可扩展笔记

如果后续继续细分，可以新增：

- `06-MySQL实验清单.md`：隔离级别、死锁、索引优化实验。
- `07-MySQL参数速查.md`：按连接、内存、日志、复制、InnoDB 分类整理参数。
- `08-MySQL生产故障案例.md`：记录真实故障与复盘。
- `09-MySQL面试题专题.md`：把第 5 卷面试题扩展成题库。

## 8. 本次编排记录

- 主 agent 创建 5 个 gpt-5.5/high 写作子 agent，并按互不重叠文件范围分派任务。
- 子 agent 完成 01、02、03、05 四个分卷。
- 第 4 子 agent 因网络传输中断未落盘，主 agent 接管补齐 [[04-InnoDB事务锁与日志]]。
- 主 agent 统一修正跨文件 Obsidian 内链，并创建本总览页。
