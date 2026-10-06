---
title: MySQL 基础与体系结构
created: 2026-06-08
updated: 2026-06-08
tags: [MySQL, 数据库, InnoDB, 体系结构]
type: tutorial
status: complete
---

# 01. MySQL 基础与体系结构

## 学习目标

本章建立 MySQL 的长期复习框架。读完后应能回答：

- MySQL 是什么，适合解决哪些问题。
- MySQL 8.x/9.x 的版本线应如何稳健理解。
- 如何安装、启动、连接 MySQL，并识别客户端与服务器的边界。
- MySQL 的逻辑架构如何从 SQL 请求走到存储引擎。
- InnoDB 为什么是现代 MySQL 的核心。
- 系统库、配置文件、字符集、权限和常用工具分别负责什么。
- 后续应按什么路线学习 [[02-SQL语言与数据建模]]、[[03-MySQL索引与查询优化]]、[[04-InnoDB事务锁与日志]]、[[05-MySQL运维高可用安全与面试]]。

## 一句话总览

MySQL 是一个关系型数据库管理系统。应用程序通过客户端协议把 SQL 发送给 MySQL Server，Server 负责连接、解析、优化、执行，再通过存储引擎读写数据文件和日志文件。

```text
应用程序 / 命令行客户端
        │
        │ MySQL Protocol（TCP/IP 或 Unix Socket）
        ▼
MySQL Server
  ├─ 连接与权限
  ├─ SQL 解析
  ├─ 优化器
  ├─ 执行器
  └─ 存储引擎 API
        │
        ▼
InnoDB / 其他存储引擎
  ├─ 数据页与索引页
  ├─ Buffer Pool
  ├─ Redo Log
  ├─ Undo Log
  └─ 表空间文件
```

复习时先分清三层：

1. **SQL 层**：你写的 SQL、权限、优化器、执行计划。
2. **存储引擎层**：InnoDB 如何组织数据、索引、事务、锁和日志。
3. **运维层**：配置、账号、备份、复制、监控、升级。

## MySQL 概览

MySQL 的核心特点：

- **关系模型**：用库、表、行、列、约束组织数据。
- **SQL 接口**：用 `SELECT`、`INSERT`、`UPDATE`、`DELETE`、DDL、DCL 管理数据。
- **客户端/服务器架构**：服务器进程长期运行，客户端按连接发送请求。
- **插件式存储引擎**：同一个 MySQL Server 可以支持不同存储引擎；业务表通常使用 InnoDB。
- **事务能力**：InnoDB 支持 ACID、MVCC、行级锁和崩溃恢复。
- **生态成熟**：有复制、备份、连接器、监控、迁移和管理工具。

适合 MySQL 的场景：

- Web 应用、订单、用户、支付、内容管理等 OLTP 业务。
- 读多写少或中高并发的结构化数据服务。
- 需要事务、索引、约束、备份恢复和复制的系统。

不应只靠 MySQL 解决的场景：

- 大规模全文检索：通常接入搜索引擎。
- 超大规模离线分析：通常接入数仓或湖仓系统。
- 极高写入吞吐的时序/日志场景：可能需要专用时序库、日志系统或分区架构。

## 版本路线：MySQL 8.x 与 9.x

版本选择要看 **官方支持周期、发布类型、业务稳定性和客户端兼容性**，不要只看数字大小。以下表述截至 2026-06；生产升级前必须重新核对官方发布页面。

### 稳健理解

- **MySQL 8.0**：曾是很长时间的主流 8.x 版本，包含窗口函数、CTE、JSON 增强、默认 `utf8mb4`、数据字典等重要能力。新项目不应只因为“熟悉”就停留在旧小版本。
- **MySQL 8.4 LTS**：8.x 长期支持线，适合需要稳定生命周期、保守升级节奏的生产系统。
- **MySQL 9.x**：9.x 不是一个单一含义。早期 9.x 小版本属于更快迭代的创新发布线；后续 9.x 中也会出现 LTS 发布。生产选型时应看具体小版本的 release model，而不是把“9.x”简单等同于实验版或必然最新版。
- **升级策略**：生产环境优先选择仍在支持期内的 LTS；需要新特性时，再评估创新发布线或新 LTS 的兼容性、驱动支持和回滚方案。

### 版本选择清单

- [ ] 目标版本是否仍在官方支持期内。
- [ ] 连接器、ORM、中间件是否支持目标版本。
- [ ] 认证插件、字符集、保留字、SQL 行为是否有不兼容变化。
- [ ] 备份恢复、复制、监控、审计工具是否兼容。
- [ ] 是否有完整的预生产升级演练和回滚方案。

参考：[[05-MySQL运维高可用安全与面试]]、[[05-MySQL运维高可用安全与面试]]。

## 安装与连接

### 安装方式

常见安装方式：

| 环境 | 常见方式 | 适用场景 |
| --- | --- | --- |
| macOS | 官方 DMG、Homebrew、Docker | 本地学习、开发环境 |
| Linux | 官方 Yum/APT 仓库、通用二进制包、Docker | 测试与生产环境 |
| Windows | MySQL Installer、ZIP 包、Docker Desktop | 本地学习、开发环境 |
| 云环境 | 云厂商 RDS / Cloud SQL / HeatWave | 生产托管服务 |

生产环境优先使用：

1. 官方仓库或云厂商托管服务。
2. 明确版本号，不使用不可控的“latest”。
3. 单独的数据目录、日志目录、备份目录。
4. 可重复执行的安装脚本或基础设施配置。

### 启动与确认客户端

本机已验证以下命令可执行：

```bash
mysql --version
```

示例输出：

```text
mysql  Ver 9.7.0 for macos15 on arm64 (MySQL Community Server - GPL)
```

查看服务端可用的默认参数时，可先不用连接数据库：

```bash
mysqld --verbose --help | grep -E '^(character-set-server|collation-server|default-storage-engine)'
```

本机验证输出：

```text
character-set-server                                         utf8mb4
collation-server                                             utf8mb4_0900_ai_ci
default-storage-engine                                       InnoDB
```

### 连接模板

以下连接命令是模板，需要替换为真实主机、端口、账号和密码。本笔记未保存任何数据库密码；因此只验证了客户端命令存在，没有验证这些模板能登录你的实例。

```bash
mysql -h 127.0.0.1 -P 3306 -u app_user -p
```

使用 Unix Socket 连接本机服务：

```bash
mysql --protocol=SOCKET -u root -p
```

执行单条 SQL：

```bash
mysql -h 127.0.0.1 -P 3306 -u app_user -p -e "SELECT VERSION();"
```

连接排错顺序：

1. MySQL Server 是否启动。
2. 主机与端口是否正确，默认端口通常是 `3306`。
3. 本机连接使用 TCP 还是 Socket。
4. 账号名和来源主机是否匹配，例如 `'app_user'@'%'` 与 `'app_user'@'localhost'` 是不同账号。
5. 防火墙、安全组、容器端口映射是否放通。
6. 认证插件与客户端版本是否兼容。

## 客户端/服务器模型

MySQL 不是“打开一个文件就读写数据”的程序，而是长期运行的服务器进程。客户端只是入口。

### 角色划分

| 角色           | 例子                      | 责任                    |
| ------------ | ----------------------- | --------------------- |
| 客户端程序        | `mysql`、应用程序、GUI 工具、连接器 | 建立连接，发送 SQL，接收结果      |
| MySQL Server | `mysqld`                | 认证、权限、解析、优化、执行、调用存储引擎 |
| 存储引擎         | InnoDB、MEMORY 等         | 管理数据页、索引、锁、事务、日志      |
| 数据文件         | 表空间、日志、配置、临时文件          | 持久化数据和运行状态            |

### 一条 SQL 的典型路径

1. 客户端发起连接。
2. Server 完成认证，检查账号来源和权限。
3. 客户端发送 SQL 文本。
4. Server 解析 SQL，生成语法树。
5. 预处理阶段检查表、列、函数、权限等对象。
6. 优化器选择访问路径和连接顺序。
7. 执行器按计划调用存储引擎接口。
8. 存储引擎读取或修改数据页、索引页和日志。
9. Server 返回结果集、影响行数或错误码。

后续优化学习的重点是第 6 步到第 8 步，见 [[03-MySQL索引与查询优化]]。

## 逻辑架构

可以把 MySQL Server 分成四层理解。

### 连接层

连接层负责：

- 网络连接或 Socket 连接。
- TLS/SSL 安全连接。
- 用户认证。
- 连接线程、连接状态、会话变量。
- 初步权限检查。

常见问题：

- 连接数耗尽。
- 慢连接或认证失败。
- 连接池配置过大，把数据库压垮。
- 应用端没有及时释放连接。

### SQL 层

SQL 层负责：

- 解析 SQL。
- 校验对象和权限。
- 查询重写。
- 优化器生成执行计划。
- 执行器处理结果集、排序、聚合、临时表。

这里是 `EXPLAIN`、慢查询日志和优化器分析的主要关注区域。

### 存储引擎层

存储引擎层通过统一接口向 SQL 层提供能力。InnoDB 负责现代业务表最重要的能力：

- 聚簇索引组织表数据。
- 二级索引。
- 行级锁。
- MVCC。
- Redo/Undo 日志。
- 崩溃恢复。

### 文件与日志层

重要文件类型：

- 表空间文件：保存表和索引数据。
- Redo Log：保证崩溃恢复。
- Undo Log：支持回滚和 MVCC。
- Binary Log：支持复制、恢复和 CDC。
- Error Log：记录启动、停止、崩溃和错误信息。
- Slow Query Log：记录慢 SQL。
- 配置文件：保存启动参数和客户端参数。

日志深入见 [[05-MySQL运维高可用安全与面试]]。

## 存储引擎

MySQL 的存储引擎决定表如何存储、是否支持事务、锁粒度和适用场景。

查看存储引擎：

```sql
SHOW ENGINES;
```

查看表使用的引擎：

```sql
SHOW TABLE STATUS LIKE 'users';
```

建表时显式指定 InnoDB：

```sql
CREATE TABLE users (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  email VARCHAR(255) NOT NULL UNIQUE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
```

常见引擎对比：

| 引擎 | 是否常用于业务表 | 关键特点 | 备注 |
| --- | --- | --- | --- |
| InnoDB | 是 | 事务、行级锁、MVCC、崩溃恢复、外键 | 现代 MySQL 默认与首选引擎 |
| MEMORY | 少量场景 | 数据在内存中，重启丢失 | 适合临时或缓存类数据，不替代 Redis |
| CSV | 很少 | 用 CSV 文件存储 | 适合导入导出或特殊调试 |
| ARCHIVE | 很少 | 压缩归档 | 只适合特定归档场景 |
| MyISAM | 不建议新业务使用 | 非事务、表级锁 | 老系统可能仍存在，迁移需谨慎 |
| NDB | 特定场景 | 集群存储引擎 | 架构和运维模型不同于普通 InnoDB |

工程建议：

- 新业务表默认使用 InnoDB。
- 不要为了“读快”轻易选择 MyISAM；事务、安全恢复和锁粒度通常更重要。
- 如果发现老表不是 InnoDB，先评估外键、全文索引、锁、停机窗口和数据校验，再迁移。

## InnoDB 基础

InnoDB 是学习 MySQL 的核心，因为大多数生产表都依赖它。

### InnoDB 解决的问题

- **事务**：一组 SQL 要么全部成功，要么全部回滚。
- **并发**：多个会话同时读写时保持一致性。
- **崩溃恢复**：进程或机器异常后尽量恢复到一致状态。
- **索引组织**：按主键组织数据，二级索引指向主键。

### 聚簇索引

InnoDB 表数据按主键聚簇存储。主键不是单纯的约束，它决定数据行的物理组织方式。

主键选择建议：

- 短：减少二级索引体积。
- 稳定：不要更新主键。
- 尽量递增：减少页分裂，改善写入局部性。
- 明确：每张业务表都应有主键。

常见选择：

```sql
id BIGINT PRIMARY KEY AUTO_INCREMENT
```

随机 UUID 作为主键会影响插入局部性。若必须使用全局唯一 ID，可评估有序 UUID、ULID、雪花 ID 或业务无关的自增代理键。

### Buffer Pool

Buffer Pool 是 InnoDB 的内存缓存，保存热数据页和索引页。

复习重点：

- 读查询命中 Buffer Pool 时不一定需要读磁盘。
- 写入通常先修改内存页，再通过日志和刷脏机制落盘。
- Buffer Pool 太小会放大磁盘 I/O。

### Redo 与 Undo

- **Redo Log**：记录物理层面的变更，用于崩溃恢复。
- **Undo Log**：保存旧版本，用于事务回滚和 MVCC 一致性读。

口诀：

- Redo 负责“已经提交的修改不能丢”。
- Undo 负责“未提交的修改可以回滚，旧版本可以被读到”。

### MVCC 与锁

InnoDB 通过 MVCC 支持一致性读，通过行锁和间隙锁等机制控制并发写入。

入门阶段先记住：

- 普通 `SELECT` 多数情况下是快照读。
- `UPDATE`、`DELETE`、`SELECT ... FOR UPDATE` 会涉及锁。
- 行锁依赖索引；条件不命中索引时，锁范围可能扩大。
- 长事务会拖累 Undo 清理和并发性能。

深入见 [[04-InnoDB事务锁与日志]]。

## 系统库

MySQL 自带几个重要系统库。不要把它们当成普通业务库随意修改。

| 系统库 | 作用 | 常见用途 |
| --- | --- | --- |
| `mysql` | 保存账号、权限、时区、系统对象等元数据 | 用户和权限管理、系统配置 |
| `information_schema` | 标准化元数据视图 | 查看库、表、列、索引、约束 |
| `performance_schema` | 性能事件与等待信息 | 分析连接、锁、I/O、语句性能 |
| `sys` | 基于 `performance_schema` 的易读视图 | 快速定位慢 SQL、热点表、等待事件 |

常用查询：

```sql
SELECT table_schema, table_name, engine
FROM information_schema.tables
WHERE table_schema = 'app';
```

```sql
SELECT user, host
FROM mysql.user;
```

权限注意：不同账号看到的系统库内容可能不同；生产排查时应使用只读诊断账号或受控 DBA 账号。

## 配置文件

MySQL 可以从命令行参数、配置文件和持久化系统变量读取配置。生产环境应把关键配置纳入版本管理或基础设施管理。

### 常见配置文件位置

不同平台不同，常见位置包括：

- Linux：`/etc/my.cnf`、`/etc/mysql/my.cnf`、`/etc/mysql/mysql.conf.d/`。
- macOS：`/etc/my.cnf`、`/usr/local/mysql/my.cnf`、Homebrew 安装目录下的配置路径。
- Windows：`my.ini`。
- Docker：通常通过挂载配置文件或环境变量注入。

### 配置文件结构

典型结构：

```ini
[client]
default-character-set=utf8mb4

[mysqld]
port=3306
bind-address=127.0.0.1
character-set-server=utf8mb4
collation-server=utf8mb4_0900_ai_ci
default-storage-engine=InnoDB
```

分组含义：

- `[client]`：客户端程序读取，例如 `mysql`、`mysqldump`。
- `[mysqld]`：服务器进程读取。
- `[mysql]`：`mysql` 命令行客户端专用。
- `[mysqldump]`：`mysqldump` 专用。

### 配置排错原则

1. 区分启动参数、全局变量、会话变量。
2. 修改配置文件后通常需要重启服务才能生效。
3. `SET GLOBAL` 只影响运行中实例，不一定持久化。
4. `SET PERSIST` 可持久化部分系统变量，但仍要纳入配置审计。
5. 不要在不知道影响面的情况下复制“性能优化模板”。

查看变量：

```sql
SHOW VARIABLES LIKE 'character_set_server';
SHOW VARIABLES LIKE 'collation_server';
SHOW VARIABLES LIKE 'default_storage_engine';
```

## 字符集与排序规则

字符集决定能存哪些字符，排序规则决定如何比较和排序字符。

### 推荐默认值

新项目通常使用：

```sql
CREATE DATABASE app
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;
```

原因：

- `utf8mb4` 支持完整 Unicode，包括 emoji 和较多扩展字符。
- 老的 `utf8` 在 MySQL 语境中容易与 `utf8mb3` 混淆，不应作为新项目默认选择。
- `utf8mb4_0900_ai_ci` 是 MySQL 8.0 以来常见默认排序规则，基于 Unicode 9.0，大小写不敏感、重音不敏感。

### 排序规则后缀

常见后缀：

| 后缀 | 含义 | 影响 |
| --- | --- | --- |
| `_ci` | case-insensitive | 大小写不敏感 |
| `_cs` | case-sensitive | 大小写敏感 |
| `_ai` | accent-insensitive | 重音不敏感 |
| `_as` | accent-sensitive | 重音敏感 |
| `_bin` | binary | 按字节比较 |

### 工程注意事项

- 唯一索引会受排序规则影响。
- 登录名、邮箱、标签等字段要明确是否大小写敏感。
- 跨库 join 或比较时，字符集/排序规则不一致可能导致隐式转换或报错。
- 迁移老库时，要先评估字符集转换对索引长度、唯一性和应用展示的影响。

深入见 [[02-SQL语言与数据建模]]。

## 账号与权限入门

MySQL 账号由 **用户名 + 来源主机** 共同决定。

```text
'app_user'@'127.0.0.1'
'app_user'@'%'
'app_user'@'localhost'
```

它们是不同账号。`localhost` 还可能走 Unix Socket，不一定等同于 `127.0.0.1`。

### 最小权限示例

以下 SQL 是权限配置模板，需要在有权限的管理账号下执行，并替换密码和库名：

```sql
CREATE USER 'app_user'@'%' IDENTIFIED BY 'change-me-strong-password';

GRANT SELECT, INSERT, UPDATE, DELETE
ON app.*
TO 'app_user'@'%';

SHOW GRANTS FOR 'app_user'@'%';
```

只读账号：

```sql
CREATE USER 'app_readonly'@'%' IDENTIFIED BY 'change-me-strong-password';

GRANT SELECT
ON app.*
TO 'app_readonly'@'%';
```

撤销权限：

```sql
REVOKE DELETE
ON app.*
FROM 'app_user'@'%';
```

### 权限原则

- 应用账号不要使用 `root`。
- 生产账号按职责拆分：应用写账号、只读账号、迁移账号、备份账号、运维诊断账号。
- 不要长期使用 `'user'@'%'` 暴露全网访问；应配合网络边界、TLS 和来源限制。
- 不要把密码写入脚本、笔记或仓库；优先使用密钥管理、环境变量或 `mysql_config_editor`。
- 升级前检查认证插件兼容性。现代 MySQL 默认倾向 `caching_sha2_password`，老客户端可能不兼容。

深入见 [[05-MySQL运维高可用安全与面试]]。

## 常用工具

本机验证存在的常用命令：

| 工具 | 作用 | 本机验证 |
| --- | --- | --- |
| `mysql` | 命令行客户端 | 已验证存在 |
| `mysqladmin` | 管理与状态检查 | 已验证存在 |
| `mysqldump` | 逻辑备份导出 | 已验证存在 |
| `mysql_config_editor` | 保存加密登录路径 | 已验证存在 |
| `mysqlcheck` | 检查、修复、分析表 | 已验证存在 |
| `mysqlshow` | 快速查看库表 | 已验证存在 |
| `mysqlimport` | 导入文本数据 | 已验证存在 |
| `perror` | 查询错误码含义 | 已验证存在 |
| `mysqlrouter` | InnoDB Cluster/Router 相关路由 | 已验证存在 |
| `mysqlsh` | MySQL Shell，支持 AdminAPI 和脚本化管理 | 本机未安装 |

常用命令模板：

```bash
mysqladmin -h 127.0.0.1 -P 3306 -u app_user -p ping
```

```bash
mysqldump -h 127.0.0.1 -P 3306 -u backup_user -p --single-transaction app > app.sql
```

```bash
perror 1045
```

备份提醒：`mysqldump` 是逻辑备份工具；大库生产备份通常还要评估物理备份、binlog、恢复时间目标和恢复演练。见 [[05-MySQL运维高可用安全与面试]]。

## 学习路线

建议按“能用 → 能解释 → 能排错 → 能设计”的顺序学习。

### 第一阶段：基础使用

- 安装 MySQL，熟悉 `mysql` 客户端。
- 掌握库、表、列、主键、唯一约束、外键。
- 掌握基础 DDL 和 DML。
- 理解字符集、排序规则和时间类型。

对应笔记：[[02-SQL语言与数据建模]]。

### 第二阶段：查询与索引

- 学会读 `EXPLAIN`。
- 理解 B+Tree、聚簇索引、二级索引、覆盖索引。
- 设计组合索引。
- 识别全表扫描、filesort、临时表。

对应笔记：[[03-MySQL索引与查询优化]]。

### 第三阶段：事务与并发

- 理解 ACID、隔离级别、MVCC。
- 区分快照读和当前读。
- 理解行锁、间隙锁、next-key lock。
- 学会处理死锁和长事务。

对应笔记：[[04-InnoDB事务锁与日志]]。

### 第四阶段：日志、备份与恢复

- 理解 redo、undo、binlog、relay log。
- 掌握逻辑备份和物理备份的差异。
- 做恢复演练，而不是只做备份。
- 理解时间点恢复和 binlog 保留策略。

对应笔记：[[05-MySQL运维高可用安全与面试]]。

### 第五阶段：复制、高可用与运维

- 理解主从复制、GTID、复制延迟。
- 理解读写分离的一致性问题。
- 掌握监控指标、慢查询、容量规划。
- 学习在线 DDL、迁移和版本升级。

对应笔记：[[05-MySQL运维高可用安全与面试]]、[[05-MySQL运维高可用安全与面试]]。

## 快速复习清单

- [ ] MySQL Server 和 `mysql` 客户端不是同一个东西。
- [ ] 业务表默认使用 InnoDB。
- [ ] InnoDB 表按主键聚簇存储。
- [ ] `utf8mb4` 是新项目默认字符集。
- [ ] 排序规则会影响比较、排序和唯一约束。
- [ ] 账号由 `'user'@'host'` 共同决定。
- [ ] 应用账号不要使用 `root`。
- [ ] `information_schema` 看元数据，`performance_schema` 看性能事件，`sys` 提供易读视图。
- [ ] 配置变更要区分配置文件、`SET GLOBAL` 和 `SET PERSIST`。
- [ ] 生产升级要看具体小版本的 release model 和兼容性说明。

## 本章练习

1. 画出一条 `SELECT` 从客户端到 InnoDB 的执行路径。
2. 解释 MySQL Server、InnoDB、表空间、binlog 的边界。
3. 为什么新业务表通常不建议使用 MyISAM？
4. 为什么邮箱唯一索引必须考虑排序规则？
5. 解释 `'app'@'localhost'` 和 `'app'@'%'` 为什么不是同一个账号。
6. 用自己的话说明 Redo Log 和 Undo Log 的区别。

## 验证记录

- 已在本机验证 `mysql --version`、`mysqld --version`、`mysqladmin --version`、`mysqldump --version` 可执行。
- 已在本机验证 `mysqld --verbose --help` 可显示默认字符集、排序规则和存储引擎。
- 连接命令和 SQL 片段是学习模板；由于未使用真实数据库密码，本笔记未端到端登录实例执行这些 SQL。

## 参考资料

- [MySQL Reference Manual: MySQL Releases](https://dev.mysql.com/doc/refman/9.7/en/mysql-releases.html)
- [MySQL Reference Manual: Installing and Upgrading MySQL](https://dev.mysql.com/doc/refman/9.7/en/installing.html)
- [MySQL Reference Manual: Storage Engines](https://dev.mysql.com/doc/refman/9.7/en/storage-engines.html)
- [MySQL Reference Manual: The InnoDB Storage Engine](https://dev.mysql.com/doc/refman/9.7/en/innodb-storage-engine.html)
- [MySQL Reference Manual: Character Sets, Collations, Unicode](https://dev.mysql.com/doc/refman/9.7/en/charset.html)
- [MySQL Reference Manual: The MySQL Access Privilege System](https://dev.mysql.com/doc/refman/9.7/en/privilege-system.html)
- [MySQL Reference Manual: Server Option and Variable Reference](https://dev.mysql.com/doc/refman/9.7/en/server-option-variable-reference.html)
