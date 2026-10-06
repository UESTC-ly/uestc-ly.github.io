---
tags:
  - MySQL
  - SQL
  - 数据库语言
  - 语法
created: 2026-06-08
updated: 2026-06-08
---

# mysql语言

> 本文件聚焦“使用 MySQL 时需要掌握的语言体系”。如果想看更完整的数据建模与查询示例，继续阅读 [[02-SQL语言与数据建模]]；如果关注执行效率，阅读 [[03-MySQL索引与查询优化]]。

## 1. MySQL 语言是什么

MySQL 的主要交互语言是 **SQL（Structured Query Language）**，但 MySQL 并不是只支持标准 SQL，它还有自己的方言、函数、存储程序、管理语句和诊断语句。

可以把 MySQL 语言分成五层：

| 层级 | 作用 | 示例 |
|---|---|---|
| DDL | 定义数据库对象 | `CREATE TABLE`、`ALTER TABLE`、`DROP INDEX` |
| DML | 修改数据 | `INSERT`、`UPDATE`、`DELETE`、`REPLACE` |
| DQL | 查询数据 | `SELECT`、`JOIN`、`GROUP BY`、窗口函数 |
| DCL | 控制权限 | `CREATE USER`、`GRANT`、`REVOKE` |
| TCL | 控制事务 | `START TRANSACTION`、`COMMIT`、`ROLLBACK` |

---

## 2. DDL：数据定义语言

DDL 用来创建、修改、删除数据库对象。

### 2.1 数据库

```sql
CREATE DATABASE app_db
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;

SHOW DATABASES;
USE app_db;
DROP DATABASE app_db;
```

要点：

- 新系统优先使用 `utf8mb4`。
- 删除数据库是高危操作，生产必须先确认备份与环境。

### 2.2 表

```sql
CREATE TABLE users (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(64) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  status TINYINT NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

常见表级操作：

```sql
SHOW TABLES;
DESC users;
SHOW CREATE TABLE users\G
ALTER TABLE users ADD COLUMN last_login_at DATETIME NULL;
ALTER TABLE users ADD INDEX idx_status_created(status, created_at);
DROP TABLE users;
```

DDL 注意事项：

- 大表 `ALTER TABLE` 可能锁表或消耗大量 I/O。
- 生产变更前确认是否支持 Online DDL / Instant DDL。
- 结构变更必须有回滚方案。

---

## 3. DML：数据操作语言

DML 用来写入、修改、删除数据。

### 3.1 INSERT

```sql
INSERT INTO users(username, email)
VALUES ('alice', 'alice@example.com');
```

批量插入：

```sql
INSERT INTO users(username, email)
VALUES
  ('alice', 'alice@example.com'),
  ('bob', 'bob@example.com');
```

冲突更新：

```sql
INSERT INTO users(username, email)
VALUES ('alice', 'alice@example.com')
ON DUPLICATE KEY UPDATE
  username = VALUES(username),
  updated_at = CURRENT_TIMESTAMP;
```

### 3.2 UPDATE

```sql
UPDATE users
SET status = 0,
    updated_at = NOW()
WHERE id = 1001;
```

安全要点：

- `UPDATE` 必须有明确 `WHERE`。
- 大批量更新要分批执行。
- 条件列最好有索引，否则可能扫描并锁住大量记录。

### 3.3 DELETE

```sql
DELETE FROM users
WHERE id = 1001;
```

批量删除模板：

```sql
DELETE FROM logs
WHERE created_at < NOW() - INTERVAL 90 DAY
ORDER BY id
LIMIT 1000;
```

### 3.4 REPLACE

```sql
REPLACE INTO config_items(config_key, config_value)
VALUES ('site_name', 'demo');
```

注意：`REPLACE` 语义接近“先删再插”，可能触发自增变化、外键、触发器等副作用。多数业务更推荐 `INSERT ... ON DUPLICATE KEY UPDATE`。

---

## 4. DQL：数据查询语言

### 4.1 SELECT 基础

```sql
SELECT id, username, email
FROM users
WHERE status = 1
ORDER BY created_at DESC
LIMIT 20;
```

执行顺序的逻辑理解：

```text
FROM/JOIN -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY -> LIMIT
```

### 4.2 WHERE 条件

```sql
SELECT * FROM orders
WHERE user_id = 1001
  AND status IN ('PAID', 'SHIPPED')
  AND created_at >= '2026-01-01';
```

常见谓词：

- `=`、`<>`、`>`、`>=`、`<`、`<=`
- `BETWEEN ... AND ...`
- `IN (...)`
- `LIKE`
- `IS NULL` / `IS NOT NULL`
- `EXISTS`

### 4.3 JOIN

```sql
SELECT o.id, o.amount, u.username
FROM orders AS o
JOIN users AS u ON u.id = o.user_id
WHERE o.status = 'PAID';
```

常见 JOIN：

| 类型 | 含义 |
|---|---|
| `INNER JOIN` | 只保留两边都匹配的行 |
| `LEFT JOIN` | 保留左表全部行，右表不匹配补 NULL |
| `RIGHT JOIN` | 保留右表全部行，较少使用 |
| `CROSS JOIN` | 笛卡尔积，需谨慎 |

### 4.4 GROUP BY 与 HAVING

```sql
SELECT user_id, COUNT(*) AS order_count, SUM(amount) AS total_amount
FROM orders
WHERE status = 'PAID'
GROUP BY user_id
HAVING total_amount > 1000
ORDER BY total_amount DESC;
```

区别：

- `WHERE` 过滤分组前的行。
- `HAVING` 过滤分组后的聚合结果。

### 4.5 子查询

```sql
SELECT *
FROM users
WHERE id IN (
  SELECT user_id
  FROM orders
  WHERE status = 'PAID'
);
```

相关子查询：

```sql
SELECT *
FROM users u
WHERE EXISTS (
  SELECT 1
  FROM orders o
  WHERE o.user_id = u.id
    AND o.status = 'PAID'
);
```

### 4.6 CTE

```sql
WITH paid_orders AS (
  SELECT user_id, SUM(amount) AS total_amount
  FROM orders
  WHERE status = 'PAID'
  GROUP BY user_id
)
SELECT *
FROM paid_orders
WHERE total_amount > 1000;
```

CTE 适合把复杂 SQL 拆成可读的逻辑步骤。

### 4.7 窗口函数

```sql
SELECT
  user_id,
  id AS order_id,
  amount,
  ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn
FROM orders;
```

常见窗口函数：

- `ROW_NUMBER()`
- `RANK()`
- `DENSE_RANK()`
- `LAG()` / `LEAD()`
- `SUM() OVER (...)`

---

## 5. DCL：权限控制语言

### 5.1 用户

```sql
CREATE USER 'app_user'@'%' IDENTIFIED BY 'strong_password';
ALTER USER 'app_user'@'%' IDENTIFIED BY 'new_strong_password';
DROP USER 'app_user'@'%';
```

### 5.2 授权

```sql
GRANT SELECT, INSERT, UPDATE, DELETE
ON app_db.*
TO 'app_user'@'%';

SHOW GRANTS FOR 'app_user'@'%';

REVOKE DELETE
ON app_db.*
FROM 'app_user'@'%';
```

权限原则：

- 最小权限。
- 应用账号不使用 root。
- 读写账号、只读账号、运维账号分离。
- 权限变更要审计。

---

## 6. TCL：事务控制语言

```sql
START TRANSACTION;

UPDATE account SET balance = balance - 100 WHERE id = 1;
UPDATE account SET balance = balance + 100 WHERE id = 2;

COMMIT;
```

回滚：

```sql
ROLLBACK;
```

保存点：

```sql
START TRANSACTION;
SAVEPOINT before_update;
UPDATE orders SET status = 'CANCELLED' WHERE id = 1001;
ROLLBACK TO SAVEPOINT before_update;
COMMIT;
```

隔离级别：

```sql
SELECT @@transaction_isolation;
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;
```

事务细节见 [[04-InnoDB事务锁与日志]]。

---

## 7. MySQL 特有语法与常用扩展

### 7.1 LIMIT

```sql
SELECT * FROM orders
ORDER BY id DESC
LIMIT 20 OFFSET 40;
```

深分页优化见 [[03-MySQL索引与查询优化]]。

### 7.2 UPSERT

```sql
INSERT INTO daily_stats(stat_date, pv)
VALUES ('2026-06-08', 1)
ON DUPLICATE KEY UPDATE pv = pv + 1;
```

### 7.3 JSON

```sql
SELECT JSON_EXTRACT(profile, '$.city') AS city
FROM users;

UPDATE users
SET profile = JSON_SET(profile, '$.city', 'Shanghai')
WHERE id = 1;
```

### 7.4 正则表达式

```sql
SELECT * FROM users
WHERE email REGEXP '^[A-Za-z0-9._%+-]+@example\\.com$';
```

### 7.5 日期时间

```sql
SELECT NOW(), CURRENT_DATE, UTC_TIMESTAMP();

SELECT * FROM orders
WHERE created_at >= NOW() - INTERVAL 7 DAY;
```

### 7.6 条件表达式

```sql
SELECT
  id,
  CASE status
    WHEN 1 THEN 'enabled'
    WHEN 0 THEN 'disabled'
    ELSE 'unknown'
  END AS status_name
FROM users;
```

---

## 8. 管理与诊断语句

```sql
SHOW DATABASES;
SHOW TABLES;
SHOW CREATE TABLE users\G
SHOW INDEX FROM users;
SHOW VARIABLES LIKE 'innodb%';
SHOW STATUS LIKE 'Threads_connected';
SHOW FULL PROCESSLIST;
SHOW ENGINE INNODB STATUS\G
```

执行计划：

```sql
EXPLAIN SELECT * FROM users WHERE email = 'alice@example.com';
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'alice@example.com';
```

---

## 9. SQL 编写规范

1. 关键字大写，表名列名小写：`SELECT id FROM users`。
2. 禁止 `SELECT *` 用于核心接口，明确列名。
3. `UPDATE` / `DELETE` 必须带可控 `WHERE`。
4. 大批量写入分批提交。
5. 金额用 `DECIMAL`，不要用浮点数。
6. 时间字段统一命名和时区策略。
7. 复杂 SQL 先用 `EXPLAIN` 看执行计划。
8. 为业务唯一性建立唯一索引，而不是只靠代码判断。
9. 避免在索引列上做函数计算导致索引失效。
10. 事务要短，避免在事务中调用外部服务。

---

## 10. 常见坑

### 10.1 NULL 比较

```sql
-- 错误
WHERE deleted_at = NULL;

-- 正确
WHERE deleted_at IS NULL;
```

### 10.2 隐式类型转换

```sql
-- phone 是 VARCHAR 时，不要这样写
WHERE phone = 13800138000;

-- 应该这样写
WHERE phone = '13800138000';
```

隐式转换可能导致索引失效或结果异常。

### 10.3 LIKE 前缀通配

```sql
WHERE name LIKE '%abc';
```

前缀 `%` 通常无法利用普通 B+Tree 索引。

### 10.4 NOT IN 与 NULL

```sql
WHERE id NOT IN (SELECT user_id FROM blacklist);
```

如果子查询中存在 NULL，结果可能不符合直觉。可考虑 `NOT EXISTS`。

### 10.5 非确定排序分页

```sql
ORDER BY created_at DESC
LIMIT 20;
```

如果 `created_at` 相同，分页可能抖动。建议补充唯一键：

```sql
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

---

## 11. 复习提纲

- SQL 五大类：DDL、DML、DQL、DCL、TCL。
- DDL 负责结构，DML 负责写入，DQL 负责查询。
- `WHERE` 在分组前过滤，`HAVING` 在分组后过滤。
- JOIN 要写清楚连接条件，避免笛卡尔积。
- 事务语句必须和隔离级别、锁一起理解。
- MySQL 方言包括 `LIMIT`、`ON DUPLICATE KEY UPDATE`、JSON 函数、诊断 `SHOW` 语句等。
- SQL 是否高效，要结合索引、执行计划与数据分布判断。

## 12. 参考资料

- MySQL 8.4 Reference Manual: <https://dev.mysql.com/doc/refman/8.4/en/>
- SQL Statements: <https://dev.mysql.com/doc/refman/8.4/en/sql-statements.html>
- SELECT Statement: <https://dev.mysql.com/doc/refman/8.4/en/select.html>
- Data Types: <https://dev.mysql.com/doc/refman/8.4/en/data-types.html>
- Transactional and Locking Statements: <https://dev.mysql.com/doc/refman/8.4/en/sql-transactional-statements.html>
