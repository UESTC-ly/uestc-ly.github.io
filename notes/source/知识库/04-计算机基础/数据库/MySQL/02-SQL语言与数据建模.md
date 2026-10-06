---
tags:
  - MySQL
  - SQL
  - 数据建模
  - 数据库
aliases:
  - SQL语言与数据建模
  - MySQL SQL
---

# 02-SQL语言与数据建模

> 复习定位：本笔记把 SQL 语言分类、MySQL 数据建模、查询写法和常见坑串成一条主线。先掌握“表如何设计”，再掌握“数据如何写入、查询、授权、提交”。关联：[[01-MySQL基础与体系结构]]、[[03-MySQL索引与查询优化]]、[[04-InnoDB事务锁与日志]]、[[05-MySQL运维高可用安全与面试]]。

## 1. SQL 的五类语言

| 类别 | 全称 | 作用 | 常见语句 | 是否常自动提交 |
|---|---|---|---|---|
| DDL | Data Definition Language | 定义库、表、列、索引、视图等结构 | `CREATE`、`ALTER`、`DROP`、`TRUNCATE` | 多数会隐式提交 |
| DML | Data Manipulation Language | 修改表中数据 | `INSERT`、`UPDATE`、`DELETE`、`REPLACE` | 受事务控制 |
| DQL | Data Query Language | 查询数据 | `SELECT` | 不修改数据 |
| DCL | Data Control Language | 权限控制 | `GRANT`、`REVOKE`、`CREATE USER` | 多数会隐式提交 |
| TCL | Transaction Control Language | 事务控制 | `START TRANSACTION`、`COMMIT`、`ROLLBACK`、`SAVEPOINT` | 控制事务边界 |

记忆方式：

- **DDL 管结构**：对象存在不存在、字段是什么类型。
- **DML 管数据变化**：增删改。
- **DQL 管读取**：查。
- **DCL 管权限**：谁能做什么。
- **TCL 管一致性边界**：什么时候确认，什么时候撤销。

## 2. DDL：数据库、表、列与结构变更

### 2.1 数据库设计

```sql
CREATE DATABASE app_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

DROP DATABASE app_db;
```

建议：

- 默认使用 `utf8mb4`，避免 emoji、少数民族文字、扩展字符写入失败。
- 同一业务库内尽量统一字符集和排序规则，减少连接、比较、排序时的隐式转换。
- 数据库名使用小写蛇形命名：`app_db`、`order_service`。

### 2.2 表设计模板

```sql
CREATE TABLE user_account (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  email VARCHAR(255) NOT NULL,
  display_name VARCHAR(100) NOT NULL,
  status TINYINT UNSIGNED NOT NULL DEFAULT 1,
  created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uk_user_account_email (email),
  KEY idx_user_account_status_created_at (status, created_at)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci;
```

设计要点：

- 表名表达业务实体，使用单数或复数要统一；推荐 `user_account`、`order_item`。
- 主键优先选择稳定、短、递增或近似递增的字段，减少 B+Tree 页分裂；详见 [[03-MySQL索引与查询优化]]。
- 每张业务表建议保留 `created_at`、`updated_at`；需要审计时再增加 `created_by`、`updated_by`、`deleted_at`。
- 结构变更前先评估锁表、重建表、复制延迟和回滚方案；线上 DDL 见 [[05-MySQL运维高可用安全与面试]]。

### 2.3 ALTER / DROP / TRUNCATE

```sql
ALTER TABLE user_account
  ADD COLUMN last_login_at DATETIME(6) NULL,
  ADD KEY idx_user_account_last_login_at (last_login_at);

ALTER TABLE user_account
  MODIFY COLUMN display_name VARCHAR(150) NOT NULL;

DROP TABLE user_account;
TRUNCATE TABLE user_account;
```

区别：

- `DELETE FROM table`：逐行删除，通常记录行级日志，可带 `WHERE`，可回滚。
- `TRUNCATE TABLE`：清空整表，属于 DDL，通常更快，不能带 `WHERE`，会重置自增计数，需谨慎。
- `DROP TABLE`：删除表结构和数据。

## 3. 数据库、表、列设计原则

### 3.1 从业务概念到表

建模顺序：

1. **识别实体**：用户、订单、商品、支付、库存。
2. **识别关系**：一对一、一对多、多对多。
3. **识别生命周期**：创建、状态变更、取消、删除、归档。
4. **识别查询路径**：按什么条件查？按什么维度统计？是否分页？
5. **识别一致性要求**：强一致、最终一致、是否需要事务。

示例：订单与订单明细。

```sql
CREATE TABLE sales_order (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  order_no VARCHAR(32) NOT NULL,
  user_id BIGINT UNSIGNED NOT NULL,
  order_status TINYINT UNSIGNED NOT NULL DEFAULT 10,
  total_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uk_sales_order_order_no (order_no),
  KEY idx_sales_order_user_created_at (user_id, created_at)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

CREATE TABLE sales_order_item (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  order_id BIGINT UNSIGNED NOT NULL,
  product_id BIGINT UNSIGNED NOT NULL,
  quantity INT UNSIGNED NOT NULL,
  unit_price DECIMAL(12,2) NOT NULL,
  PRIMARY KEY (id),
  KEY idx_sales_order_item_order_id (order_id),
  CONSTRAINT fk_sales_order_item_order
    FOREIGN KEY (order_id) REFERENCES sales_order(id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;
```

### 3.2 列设计 checklist

- 字段是否允许 `NULL`？如果业务上必填，使用 `NOT NULL`。
- 是否需要默认值？默认值不能掩盖业务错误。
- 金额是否使用 `DECIMAL`？不要用 `FLOAT` / `DOUBLE` 存钱。
- 时间是否需要微秒？需要排序精度时用 `DATETIME(6)` 或 `TIMESTAMP(6)`。
- 状态码是否有字典？在应用层或字典表维护含义。
- 字符串长度是否有业务上限？不要把所有字段都设成 `TEXT`。
- 是否需要唯一约束？手机号、邮箱、订单号等业务唯一字段应由数据库兜底。

## 4. 数据类型选型

### 4.1 整数

| 类型 | 常见用途 | 说明 |
|---|---|---|
| `TINYINT` | 状态、布尔值、小枚举 | `BOOLEAN` 在 MySQL 中通常等价于 `TINYINT(1)` |
| `INT` | 数量、普通计数 | 注意有符号与无符号范围 |
| `BIGINT` | 主键、雪花 ID、大计数 | 分布式 ID 常用 |

建议：

- 主键常用 `BIGINT UNSIGNED`，为长期增长留空间。
- 不要依赖 `INT(11)` 里的显示宽度；它不是可存储位数。
- 计数字段用 `UNSIGNED` 前要确认是否永远不会为负。

### 4.2 小数与金额

```sql
amount DECIMAL(12,2) NOT NULL
rate DECIMAL(8,6) NOT NULL
```

- 金额使用 `DECIMAL(p, s)`，其中 `p` 是总位数，`s` 是小数位数。
- `FLOAT` / `DOUBLE` 是近似值，适合科学计算，不适合财务结算。

### 4.3 字符串

| 类型 | 适合场景 | 注意点 |
|---|---|---|
| `CHAR(n)` | 固定长度编码，如国家码、短 hash | 会补齐，空间可能浪费 |
| `VARCHAR(n)` | 大多数字符串 | `n` 是字符长度，不是字节长度 |
| `TEXT` | 长文本 | 通常不建议直接频繁排序、分组、全量返回 |
| `ENUM` | 小而稳定的枚举 | 变更枚举值需要 DDL，跨语言维护不灵活 |

### 4.4 日期时间

| 类型 | 特点 | 适合场景 |
|---|---|---|
| `DATE` | 日期 | 生日、自然日 |
| `TIME` | 时间或时间间隔 | 时分秒 |
| `DATETIME` | 不随时区转换 | 业务本地时间、审计时间 |
| `TIMESTAMP` | 存储与时区有关，受连接时区影响 | 跨时区事件时间 |

建议：

- 服务端统一时区策略，例如统一存 UTC，展示时再转换。
- 需要高精度排序时使用 `DATETIME(6)` / `TIMESTAMP(6)`。
- 避免把时间存成字符串；字符串不利于范围查询、排序和函数处理。

### 4.5 JSON

MySQL 支持 `JSON` 类型与 JSON 函数，适合存放结构可变、查询频率不高或字段不稳定的数据。

适合：

- 第三方回调原始 payload。
- 可选扩展属性。
- 灰度阶段尚未稳定的字段。

不适合：

- 高频过滤、排序、JOIN 的核心字段。
- 必须强约束的数据。
- 可清晰建模成关系表的一对多明细。

## 5. 约束、主键与外键

### 5.1 常见约束

| 约束 | 作用 | 示例 |
|---|---|---|
| `NOT NULL` | 禁止空值 | `email VARCHAR(255) NOT NULL` |
| `DEFAULT` | 默认值 | `status TINYINT NOT NULL DEFAULT 1` |
| `PRIMARY KEY` | 行唯一标识 | `PRIMARY KEY (id)` |
| `UNIQUE` | 业务唯一 | `UNIQUE KEY uk_email (email)` |
| `FOREIGN KEY` | 引用完整性 | `FOREIGN KEY (user_id) REFERENCES user_account(id)` |
| `CHECK` | 条件约束 | `CHECK (amount >= 0)` |

### 5.2 主键设计

优先原则：

- **稳定**：不会更新。
- **唯一**：不与业务语义冲突。
- **短**：索引体积更小。
- **有序或近似有序**：插入更友好。

常见方案：

- 自增 `BIGINT`：简单、高效；分库分表时要处理全局唯一。
- 雪花 ID：全局唯一、近似有序；需要保证时钟与生成器稳定。
- UUID：全局唯一；随机 UUID 对索引局部性不友好，可考虑有序 UUID 或二进制存储。

### 5.3 外键取舍

外键优点：

- 数据库层保证引用完整性。
- 防止孤儿记录。
- 建模语义清晰。

外键代价：

- 写入和删除会增加检查成本。
- 复杂级联可能放大锁等待。
- 在高并发、分库分表、跨服务场景中难以维护。

实践建议：

- 单体应用、强一致核心数据：可以使用外键。
- 微服务、分库分表、高写入场景：常在应用层保证关系，并通过索引、异步校验、数据修复任务兜底。
- 无论是否创建外键，引用列都应建索引。

## 6. 范式与反范式

### 6.1 范式速记

| 范式 | 核心要求 | 解决问题 |
|---|---|---|
| 1NF | 字段原子，不存列表 | 消除重复组 |
| 2NF | 非主属性完全依赖主键 | 消除对联合主键的部分依赖 |
| 3NF | 非主属性不传递依赖主键 | 消除传递依赖 |
| BCNF | 每个决定因素都是候选键 | 更严格地消除异常依赖 |

例：订单表中直接存 `product_name`、`product_price` 是否违反范式？

- 如果它们代表“商品当前信息”，应放到商品表。
- 如果它们代表“下单瞬间快照”，放在订单明细中是合理反范式。

### 6.2 反范式的合理场景

反范式不是随意重复数据，而是为性能、审计或历史快照付出可控冗余。

常见场景：

- 订单明细保存商品名称、成交价，避免商品改名影响历史订单。
- 用户表保存 `order_count`、`last_order_at`，减少统计查询。
- 报表宽表预聚合，降低在线计算压力。

反范式必须回答：

1. 冗余字段由谁维护？应用、触发器、定时任务还是消息队列？
2. 不一致时如何发现？校验 SQL、监控、对账任务。
3. 不一致时如何修复？补偿任务、重算、人工修复流程。

## 7. DML：写入、更新、删除

### 7.1 INSERT

```sql
INSERT INTO user_account (email, display_name, status)
VALUES ('a@example.com', 'Alice', 1);

INSERT INTO user_account (email, display_name, status)
VALUES
  ('b@example.com', 'Bob', 1),
  ('c@example.com', 'Carol', 1);
```

要点：

- 显式列名，避免表结构变更导致位置错配。
- 批量插入比逐条插入更高效，但要控制单批大小。
- 遇到唯一冲突时，可用 `INSERT ... ON DUPLICATE KEY UPDATE`，但要确认幂等语义。

```sql
INSERT INTO user_account (email, display_name, status)
VALUES ('a@example.com', 'Alice', 1)
ON DUPLICATE KEY UPDATE
  display_name = VALUES(display_name),
  updated_at = CURRENT_TIMESTAMP(6);
```

### 7.2 UPDATE

```sql
UPDATE user_account
SET status = 2,
    updated_at = CURRENT_TIMESTAMP(6)
WHERE id = 1001;
```

安全要点：

- 必须带可命中索引的 `WHERE`，避免全表更新。
- 先用同样条件 `SELECT` 预览影响范围。
- 需要批量修复时分批更新，降低锁持有时间。

### 7.3 DELETE

```sql
DELETE FROM user_account
WHERE id = 1001;
```

建议：

- 业务数据优先考虑软删除：`deleted_at`、`is_deleted`。
- 物理删除前确认外键、审计、归档和恢复策略。
- 大批量删除应分批执行，避免长事务、undo 膨胀和复制延迟。

## 8. DQL：SELECT 查询基础

### 8.1 SELECT 执行逻辑顺序

书写顺序：

```sql
SELECT ...
FROM ...
JOIN ... ON ...
WHERE ...
GROUP BY ...
HAVING ...
ORDER BY ...
LIMIT ...;
```

逻辑处理顺序可理解为：

1. `FROM` / `JOIN`
2. `WHERE`
3. `GROUP BY`
4. 聚合函数
5. `HAVING`
6. 窗口函数
7. `SELECT`
8. `DISTINCT`
9. `ORDER BY`
10. `LIMIT`

注意：窗口函数在 MySQL 中只能出现在 `SELECT` 列表或 `ORDER BY` 中，不能直接放在 `WHERE`。

### 8.2 WHERE 条件

```sql
SELECT id, email, status
FROM user_account
WHERE status = 1
  AND created_at >= '2026-01-01'
ORDER BY id DESC
LIMIT 20;
```

常见谓词：

- 比较：`=`、`<>`、`>`、`>=`、`<`、`<=`
- 范围：`BETWEEN ... AND ...`
- 集合：`IN (...)`
- 模糊：`LIKE 'abc%'`
- 空值：`IS NULL`、`IS NOT NULL`

坑：

- `NULL` 不能用 `= NULL` 判断。
- `LIKE '%abc'` 通常无法有效利用普通 B+Tree 索引。
- 对索引列使用函数可能导致索引失效：`DATE(created_at) = '2026-01-01'` 可改成范围查询。

### 8.3 ORDER BY / LIMIT

```sql
SELECT id, order_no, created_at
FROM sales_order
WHERE user_id = 1001
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

建议：

- 排序字段尽量与索引匹配。
- 分页使用稳定排序键，避免翻页时重复或遗漏。
- 深分页 `LIMIT 100000, 20` 成本高，可改用游标分页：

```sql
SELECT id, order_no, created_at
FROM sales_order
WHERE user_id = 1001
  AND (created_at, id) < ('2026-06-01 00:00:00', 900000)
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

## 9. JOIN

### 9.1 JOIN 类型

| 类型 | 含义 | 常见用途 |
|---|---|---|
| `INNER JOIN` | 两边都匹配才返回 | 查询有关联的记录 |
| `LEFT JOIN` | 保留左表全部记录 | 查主表及可选明细 |
| `RIGHT JOIN` | 保留右表全部记录 | 少用，可改写成 `LEFT JOIN` |
| `CROSS JOIN` | 笛卡尔积 | 生成组合，需谨慎 |

示例：

```sql
SELECT o.order_no, o.created_at, u.email
FROM sales_order AS o
JOIN user_account AS u
  ON u.id = o.user_id
WHERE o.created_at >= '2026-01-01';
```

### 9.2 LEFT JOIN 常见坑

```sql
-- 找出没有订单的用户
SELECT u.id, u.email
FROM user_account AS u
LEFT JOIN sales_order AS o
  ON o.user_id = u.id
WHERE o.id IS NULL;
```

注意：

- `LEFT JOIN` 右表过滤条件如果写在 `WHERE`，可能把外连接变成内连接。
- 右表过滤条件通常放在 `ON` 中：

```sql
SELECT u.id, u.email, o.order_no
FROM user_account AS u
LEFT JOIN sales_order AS o
  ON o.user_id = u.id
 AND o.order_status = 20;
```

## 10. 聚合与 GROUP BY

```sql
SELECT user_id,
       COUNT(*) AS order_count,
       SUM(total_amount) AS total_amount,
       MAX(created_at) AS last_order_at
FROM sales_order
WHERE created_at >= '2026-01-01'
GROUP BY user_id
HAVING COUNT(*) >= 3;
```

要点：

- `WHERE` 过滤聚合前的行，`HAVING` 过滤聚合后的组。
- 开启 `ONLY_FULL_GROUP_BY` 时，`SELECT` 中的非聚合列必须与分组逻辑兼容。
- `COUNT(*)` 统计行数；`COUNT(column)` 不统计 `NULL`。
- `SUM()`、`AVG()` 遇到空组可能返回 `NULL`，可用 `COALESCE()` 处理。

## 11. 子查询

### 11.1 标量子查询

```sql
SELECT id, order_no, total_amount
FROM sales_order
WHERE total_amount > (
  SELECT AVG(total_amount)
  FROM sales_order
);
```

### 11.2 IN / EXISTS

```sql
SELECT u.id, u.email
FROM user_account AS u
WHERE EXISTS (
  SELECT 1
  FROM sales_order AS o
  WHERE o.user_id = u.id
);
```

选择建议：

- 需要判断存在性时优先考虑 `EXISTS`。
- `IN` 子查询要注意 `NULL` 语义。
- 复杂子查询应配合 `EXPLAIN` 查看是否被优化为半连接或物化；详见 [[03-MySQL索引与查询优化]]。

## 12. CTE：公共表表达式

CTE 使用 `WITH` 定义临时命名结果集，让复杂 SQL 更可读。

```sql
WITH recent_orders AS (
  SELECT id, user_id, total_amount, created_at
  FROM sales_order
  WHERE created_at >= '2026-01-01'
), user_order_summary AS (
  SELECT user_id,
         COUNT(*) AS order_count,
         SUM(total_amount) AS total_amount
  FROM recent_orders
  GROUP BY user_id
)
SELECT u.email, s.order_count, s.total_amount
FROM user_order_summary AS s
JOIN user_account AS u
  ON u.id = s.user_id;
```

递归 CTE 可用于层级结构、序列生成：

```sql
WITH RECURSIVE seq AS (
  SELECT 1 AS n
  UNION ALL
  SELECT n + 1 FROM seq WHERE n < 10
)
SELECT n FROM seq;
```

注意：

- CTE 提升可读性，但不等于一定更快。
- 递归 CTE 必须有终止条件。
- 多次引用同一复杂结果时，CTE 可减少重复表达。

## 13. 窗口函数

窗口函数对“当前行相关的一组行”计算结果，不会像 `GROUP BY` 一样把多行压缩成一行。

### 13.1 排名

```sql
SELECT user_id,
       order_no,
       total_amount,
       ROW_NUMBER() OVER (
         PARTITION BY user_id
         ORDER BY total_amount DESC, id DESC
       ) AS rn
FROM sales_order;
```

常用函数：

- `ROW_NUMBER()`：连续编号，不并列。
- `RANK()`：并列同名次，后续名次跳号。
- `DENSE_RANK()`：并列同名次，后续名次不跳号。
- `LAG()` / `LEAD()`：取前一行 / 后一行。
- `SUM() OVER (...)`：累计和、分区总和。

### 13.2 每个用户金额最高的订单

```sql
WITH ranked_orders AS (
  SELECT o.*,
         ROW_NUMBER() OVER (
           PARTITION BY user_id
           ORDER BY total_amount DESC, id DESC
         ) AS rn
  FROM sales_order AS o
)
SELECT id, user_id, order_no, total_amount
FROM ranked_orders
WHERE rn = 1;
```

注意：MySQL 没有通用的 `QUALIFY` 用法时，通常用子查询或 CTE 过滤窗口函数结果。

## 14. 视图

视图是保存的查询定义，用于封装复杂查询、控制暴露字段或提供稳定接口。

```sql
CREATE OR REPLACE VIEW v_active_user AS
SELECT id, email, display_name, created_at
FROM user_account
WHERE status = 1;

SELECT * FROM v_active_user;
```

适合：

- 隐藏敏感字段。
- 复用复杂查询。
- 为报表或应用提供稳定读取接口。

注意：

- 视图不是天然缓存；查询视图仍可能访问底层表。
- 复杂视图叠加可能造成优化困难。
- 不要用视图掩盖糟糕的数据模型。

## 15. 存储过程、函数、触发器与事件

### 15.1 存储过程

```sql
DELIMITER //

CREATE PROCEDURE mark_user_inactive(IN p_user_id BIGINT UNSIGNED)
BEGIN
  UPDATE user_account
  SET status = 0,
      updated_at = CURRENT_TIMESTAMP(6)
  WHERE id = p_user_id;
END//

DELIMITER ;

CALL mark_user_inactive(1001);
```

适合：

- 数据库内部批处理。
- 多语句封装。
- 权限隔离或运维脚本。

不适合：

- 把大量业务逻辑藏在数据库中，导致应用和数据库逻辑割裂。
- 高复杂度流程控制。

### 15.2 存储函数

```sql
DELIMITER //

CREATE FUNCTION cents_to_yuan(p_cents BIGINT)
RETURNS DECIMAL(12,2)
DETERMINISTIC
RETURN p_cents / 100.0//

DELIMITER ;
```

要点：

- 函数用于表达式求值，必须返回值。
- 函数可读性好，但在索引列上滥用函数会影响优化。
- 创建函数涉及权限、确定性声明和二进制日志设置，应按环境规范执行。

### 15.3 触发器

```sql
CREATE TRIGGER bi_user_account
BEFORE INSERT ON user_account
FOR EACH ROW
SET NEW.email = LOWER(NEW.email);
```

适合：

- 简单审计记录。
- 数据标准化。
- 强制某些数据库层规则。

风险：

- 隐式副作用强，调用方不易察觉。
- 可能增加锁等待和调试难度。
- 多触发器顺序、复制、权限都需要明确规范。

### 15.4 事件

事件是 MySQL 内部定时任务，依赖 Event Scheduler。

```sql
CREATE EVENT ev_archive_old_orders
ON SCHEDULE EVERY 1 DAY
DO
  INSERT INTO archived_order
  SELECT * FROM sales_order
  WHERE created_at < CURRENT_DATE - INTERVAL 365 DAY;
```

建议：

- 事件适合轻量级、数据库内闭环任务。
- 复杂调度优先使用外部任务系统，便于监控、重试、告警。
- 必须确认 `event_scheduler` 状态、权限和任务幂等性。

## 16. JSON 操作

### 16.1 读取与更新 JSON 字段

```sql
CREATE TABLE webhook_log (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  provider VARCHAR(50) NOT NULL,
  payload JSON NOT NULL,
  created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

SELECT id,
       JSON_EXTRACT(payload, '$.event_type') AS event_type,
       payload ->> '$.customer.email' AS customer_email
FROM webhook_log;

UPDATE webhook_log
SET payload = JSON_SET(payload, '$.processed', true)
WHERE id = 1;
```

### 16.2 JSON_TABLE

`JSON_TABLE()` 可以把 JSON 文档展开成关系表形态，适合解析数组。

```sql
SELECT jt.product_id, jt.quantity
FROM webhook_log AS w,
JSON_TABLE(
  w.payload,
  '$.items[*]'
  COLUMNS (
    product_id BIGINT PATH '$.product_id',
    quantity INT PATH '$.quantity'
  )
) AS jt
WHERE w.id = 1;
```

注意：

- JSON 字段不应替代清晰的关系模型。
- 高频查询的 JSON 路径可考虑生成列 + 索引。
- JSON 结构变化需要版本字段或兼容解析。

## 17. 时间处理

### 17.1 当前时间

```sql
SELECT NOW(), CURRENT_TIMESTAMP(6), CURRENT_DATE, UTC_TIMESTAMP(6);
```

- `NOW()` / `CURRENT_TIMESTAMP` 返回当前日期时间。
- `CURRENT_DATE` 返回当前日期。
- `UTC_TIMESTAMP()` 返回 UTC 时间。

### 17.2 时间范围查询

推荐半开区间：

```sql
SELECT id, order_no
FROM sales_order
WHERE created_at >= '2026-06-01 00:00:00'
  AND created_at <  '2026-07-01 00:00:00';
```

原因：

- 避免 `BETWEEN` 在日末精度上的边界问题。
- 适配 `DATETIME(6)` 微秒精度。
- 更容易命中范围索引。

### 17.3 日期计算

```sql
SELECT DATE_ADD(CURRENT_DATE, INTERVAL 7 DAY) AS next_week,
       DATE_SUB(CURRENT_DATE, INTERVAL 1 MONTH) AS last_month,
       TIMESTAMPDIFF(DAY, '2026-01-01', CURRENT_DATE) AS days_passed;
```

坑：

- 不要对列包函数再比较：`DATE(created_at) = ...`。
- 明确连接时区：`SELECT @@time_zone, @@system_time_zone;`。
- 跨时区系统要统一存储、转换和展示策略。

## 18. DCL：用户与权限

```sql
CREATE USER 'report_user'@'%' IDENTIFIED BY 'strong_password_here';

GRANT SELECT ON app_db.* TO 'report_user'@'%';

REVOKE SELECT ON app_db.* FROM 'report_user'@'%';

DROP USER 'report_user'@'%';
```

权限原则：

- 最小权限：只给完成任务所需权限。
- 分离账号：应用账号、报表账号、运维账号不要混用。
- 限制来源：生产账号不要随意使用 `'%'`。
- 定期审计：检查长期不用账号和过宽权限。

常见权限层级：全局、库、表、列、例程。权限设计详见 [[05-MySQL运维高可用安全与面试]]。

## 19. TCL：事务控制

```sql
START TRANSACTION;

UPDATE account
SET balance = balance - 100
WHERE id = 1;

UPDATE account
SET balance = balance + 100
WHERE id = 2;

COMMIT;
```

回滚：

```sql
START TRANSACTION;

UPDATE account
SET balance = balance - 100
WHERE id = 1;

ROLLBACK;
```

保存点：

```sql
START TRANSACTION;

SAVEPOINT before_step_2;

UPDATE account SET balance = balance - 100 WHERE id = 1;

ROLLBACK TO SAVEPOINT before_step_2;

COMMIT;
```

复习重点：

- 事务只对支持事务的存储引擎有效，InnoDB 支持事务。
- DDL 常隐式提交，不能把所有结构变更当成普通 DML 回滚。
- 长事务会持有锁、占用 undo、影响 purge；详见 [[04-InnoDB事务锁与日志]]。
- 隔离级别会影响脏读、不可重复读、幻读和锁行为。

## 20. SQL 编写规范

### 20.1 命名规范

- 表名、列名、索引名使用小写蛇形：`sales_order_item`。
- 主键：`id`。
- 外键字段：`实体名_id`，如 `user_id`、`order_id`。
- 唯一索引：`uk_表名_字段名`。
- 普通索引：`idx_表名_字段1_字段2`。
- 外键约束：`fk_子表_父表`。

### 20.2 查询规范

- 不写 `SELECT *`，只取需要字段。
- 表别名要短且有含义：`u`、`o`、`oi`。
- 复杂 SQL 分层：CTE / 子查询 / 临时表。
- 大查询先 `EXPLAIN`，再上线。
- UPDATE / DELETE 先 SELECT 预览条件。
- 字符串和时间值使用明确格式，不依赖隐式转换。

### 20.3 可读性格式

```sql
SELECT o.id,
       o.order_no,
       u.email,
       SUM(oi.quantity * oi.unit_price) AS calculated_amount
FROM sales_order AS o
JOIN user_account AS u
  ON u.id = o.user_id
JOIN sales_order_item AS oi
  ON oi.order_id = o.id
WHERE o.created_at >= '2026-01-01'
GROUP BY o.id, o.order_no, u.email
HAVING calculated_amount > 1000
ORDER BY calculated_amount DESC
LIMIT 50;
```

## 21. 常见坑速查

| 坑 | 后果 | 规避 |
|---|---|---|
| `SELECT *` | 多读字段、破坏覆盖索引、接口不稳定 | 明确列名 |
| 忘记 `WHERE` 更新 / 删除 | 全表数据事故 | 开启安全更新，先 SELECT |
| `NULL` 与普通比较 | 条件不符合预期 | 使用 `IS NULL` / `IS NOT NULL` |
| 隐式类型转换 | 索引失效、结果异常 | 参数类型与列类型一致 |
| 对索引列包函数 | 范围扫描变全表扫描 | 改写为范围条件 |
| `LIKE '%keyword%'` | 普通索引难用 | 前缀匹配、全文索引或搜索系统 |
| 深分页 | 扫描大量无用行 | 游标分页 |
| 大事务 | 锁等待、undo 膨胀、复制延迟 | 分批、短事务 |
| 滥用 JSON | 约束弱、查询慢 | 核心字段关系化 |
| 反范式无维护策略 | 数据不一致 | 明确维护和校验机制 |
| 外键级联不受控 | 删除 / 更新放大影响 | 谨慎使用级联动作 |
| 时区不统一 | 时间错乱 | 统一存储和展示策略 |
| DDL 当作可回滚操作 | 结构变更难撤销 | 变更前备份和演练 |

## 22. 复习提纲

1. 能说出 DDL、DML、DQL、DCL、TCL 的边界。
2. 能根据业务实体设计表、主键、唯一约束和索引雏形。
3. 能解释 `VARCHAR`、`TEXT`、`DECIMAL`、`DATETIME`、`TIMESTAMP`、`JSON` 的取舍。
4. 能区分范式和反范式，并说明冗余字段如何维护。
5. 能写出安全的 `INSERT`、`UPDATE`、`DELETE`。
6. 能写出 `JOIN`、聚合、子查询、CTE、窗口函数。
7. 能说明视图、存储过程、函数、触发器、事件的使用边界。
8. 能识别常见 SQL 性能坑和数据一致性坑。

## 23. 官方参考

- [MySQL 8.4 Reference Manual](https://dev.mysql.com/doc/refman/8.4/en/)
- [WITH Common Table Expressions](https://dev.mysql.com/doc/refman/8.4/en/with.html)
- [Window Functions](https://dev.mysql.com/doc/refman/8.4/en/window-functions.html)
- [CREATE PROCEDURE and CREATE FUNCTION](https://dev.mysql.com/doc/refman/8.4/en/create-procedure.html)
- [Using Triggers](https://dev.mysql.com/doc/refman/8.4/en/triggers.html)
- [Event Scheduler](https://dev.mysql.com/doc/refman/8.4/en/event-scheduler.html)
- [JSON Table Functions](https://dev.mysql.com/doc/refman/8.4/en/json-table-functions.html)
