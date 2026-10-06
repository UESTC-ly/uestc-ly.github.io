# MySQL 索引与查询优化

> 适用范围：以 MySQL 8.x / InnoDB 为主。复习时先看“性能排查清单”，再回到具体章节定位原因。相关笔记：[[01-MySQL基础与体系结构]]、[[04-InnoDB事务锁与日志]]、[[05-MySQL运维高可用安全与面试]]、[[05-MySQL运维高可用安全与面试]]。

## 1. 一句话总览

索引的核心价值不是“加速一切查询”，而是让 MySQL 少读数据、少排序、少回表、少临时表。优化查询时要同时看四件事：

1. **访问路径**：是否能用到合适索引。
2. **过滤效率**：索引列的选择性是否足够高。
3. **额外代价**：是否发生回表、排序、临时表、文件排序。
4. **执行计划可信度**：优化器统计信息是否准确。

常见判断公式：

```text
查询成本 ≈ 扫描行数 + 回表次数 + 排序/临时表成本 + JOIN 中间结果成本
```

---

## 2. B+Tree 索引

InnoDB 默认使用 **B+Tree** 组织大多数普通索引。

### 2.1 为什么是 B+Tree

B+Tree 的特点：

- **多路平衡树**：树高低，通常 2～4 层即可覆盖大量数据。
- **非叶子节点只存键和指针**：单页能放更多键，减少 I/O。
- **叶子节点有序并通过链表连接**：适合范围扫描、排序、分页。
- **所有数据都在叶子层**：路径长度稳定。

适合的查询：

```sql
WHERE id = 100
WHERE created_at BETWEEN '2026-01-01' AND '2026-02-01'
ORDER BY created_at
WHERE user_id = 1 ORDER BY created_at DESC
```

不擅长的查询：

```sql
WHERE name LIKE '%abc'       -- 前导通配符破坏有序匹配
WHERE YEAR(created_at) = 2026 -- 对索引列做函数，普通索引通常失效
WHERE a <> 10                -- 选择性可能很差，优化器可能放弃索引
```

### 2.2 页、局部性与范围扫描

InnoDB 以页为单位读写数据。B+Tree 索引的优势来自“按顺序定位 + 连续扫描”：

- 等值查询：从根节点一路定位到叶子节点。
- 范围查询：定位起点后沿叶子链表向后扫。
- 排序优化：如果索引顺序和 `ORDER BY` 一致，可以避免额外排序。

---

## 3. 聚簇索引与二级索引

### 3.1 聚簇索引（Clustered Index）

InnoDB 表数据本身按聚簇索引组织。聚簇索引的叶子节点保存整行数据。

聚簇索引选择顺序：

1. 显式定义的 `PRIMARY KEY`。
2. 第一个非空唯一索引。
3. InnoDB 内部生成隐藏 row id。

实践建议：

- 主键应稳定、短、递增或大致递增。
- 避免频繁更新主键。
- 避免过长主键，因为二级索引叶子节点会存主键值。

### 3.2 二级索引（Secondary Index）

二级索引叶子节点保存：

```text
二级索引键值 + 主键值
```

如果查询列不全在二级索引里，MySQL 需要根据主键再查聚簇索引，这叫 **回表**。

示例：

```sql
CREATE INDEX idx_user_created ON orders(user_id, created_at);

SELECT amount
FROM orders
WHERE user_id = 10
  AND created_at >= '2026-01-01';
```

如果 `amount` 不在 `idx_user_created` 中，执行路径通常是：

```text
idx_user_created 定位记录 -> 取主键 -> 回聚簇索引读 amount
```

### 3.3 回表成本

回表不一定慢，但大量随机回表会慢。优化方向：

- 减少扫描行数。
- 使用覆盖索引。
- 只查询必要列，避免 `SELECT *`。
- 对高频查询建立更贴合的联合索引。

相关：[[04-InnoDB事务锁与日志]] 中的锁范围也常受索引路径影响。

---

## 4. 联合索引与最左前缀

### 4.1 联合索引的排序方式

联合索引 `idx(a, b, c)` 的 B+Tree 排序不是三棵树，而是一棵按以下顺序排序的树：

```text
a -> b -> c
```

可以高效支持：

```sql
WHERE a = ?
WHERE a = ? AND b = ?
WHERE a = ? AND b = ? AND c = ?
WHERE a = ? AND b BETWEEN ? AND ?
WHERE a = ? ORDER BY b, c
```

通常不能完整利用：

```sql
WHERE b = ?
WHERE c = ?
WHERE b = ? AND c = ?
```

因为缺少最左列 `a`。

### 4.2 最左前缀原则

最左前缀原则：联合索引从最左列开始连续匹配；中间断开后，后续列通常不能继续用于定位。

对 `idx(a, b, c)`：

| 条件 | 可用于定位的列 | 说明 |
|---|---:|---|
| `a = 1` | a | 命中最左列 |
| `a = 1 AND b = 2` | a,b | 连续命中 |
| `a = 1 AND c = 3` | a | b 缺失，c 不能用于定位 |
| `b = 2 AND c = 3` | 无或较弱 | 缺少 a |
| `a > 1 AND b = 2` | a | a 是范围条件，b 多数情况下不能继续缩小定位范围 |

### 4.3 范围条件后的列

对 `idx(a, b, c)`：

```sql
WHERE a = 1 AND b > 10 AND c = 3
```

通常：

- `a` 用于等值定位。
- `b` 用于范围扫描。
- `c` 可能不能继续缩小扫描范围，但可能通过索引下推参与过滤。

### 4.4 联合索引列顺序

经验顺序：

1. 等值过滤列。
2. 高选择性列。
3. 范围列。
4. 排序 / 分组列。
5. 覆盖查询所需列。

但不要机械套用。最终以真实 SQL、数据分布和 `EXPLAIN ANALYZE` 为准。

---

## 5. 覆盖索引

覆盖索引指查询需要的列都能从索引中取得，不需要回表。

示例：

```sql
CREATE INDEX idx_user_status_created
ON orders(user_id, status, created_at);

SELECT user_id, status, created_at
FROM orders
WHERE user_id = 10
  AND status = 'PAID'
ORDER BY created_at DESC
LIMIT 20;
```

如果查询列都在 `idx_user_status_created` 中，执行计划可能显示：

```text
Extra: Using index
```

注意：

- 覆盖索引不是越宽越好。
- 宽索引会增加写入成本、页分裂概率、缓存占用。
- 高频读路径值得覆盖；低频查询不要盲目加宽索引。

---

## 6. 索引下推（Index Condition Pushdown, ICP）

索引下推是 MySQL 在存储引擎层先用索引列过滤，减少回表。

示例：

```sql
CREATE INDEX idx_user_created_status
ON orders(user_id, created_at, status);

SELECT *
FROM orders
WHERE user_id = 10
  AND created_at >= '2026-01-01'
  AND status = 'PAID';
```

如果 `status` 不能继续作为定位条件，但它在索引里，ICP 可以在索引扫描阶段先过滤 `status`，减少回表。执行计划可能显示：

```text
Extra: Using index condition
```

ICP 的意义：

- 不能改变 B+Tree 的排序规则。
- 不能让“断开的列”重新变成完整定位条件。
- 可以减少不必要的聚簇索引读取。

---

## 7. 索引类型

### 7.1 普通索引

```sql
CREATE INDEX idx_email ON users(email);
```

用于加速查询，不保证唯一性。

### 7.2 唯一索引

```sql
CREATE UNIQUE INDEX uk_email ON users(email);
```

特点：

- 保证键值唯一。
- 可作为业务约束，不只是性能工具。
- 对优化器更有价值，因为等值命中最多返回一行或少量行。

### 7.3 前缀索引

```sql
CREATE INDEX idx_name_prefix ON users(name(20));
```

适合较长字符串列。优点是索引更小，缺点是：

- 选择性可能下降。
- 不能完整覆盖原字段值。
- 前缀长度需要按真实数据分布评估。

评估方式：

```sql
SELECT
  COUNT(DISTINCT name) / COUNT(*) AS full_selectivity,
  COUNT(DISTINCT LEFT(name, 20)) / COUNT(*) AS prefix_selectivity
FROM users;
```

### 7.4 全文索引

```sql
CREATE FULLTEXT INDEX ft_title_body ON articles(title, body);

SELECT *
FROM articles
WHERE MATCH(title, body) AGAINST ('mysql optimizer');
```

适合自然语言搜索。不要用普通 B+Tree 索引硬扛大段文本包含搜索。

### 7.5 空间索引

空间索引用于 GIS 类型，例如 `POINT`、`GEOMETRY`。适合地理范围、位置关系查询。

```sql
CREATE SPATIAL INDEX sp_location ON stores(location);
```

### 7.6 函数索引

MySQL 8.0 支持函数索引，可优化表达式查询。

```sql
CREATE INDEX idx_lower_email ON users ((LOWER(email)));

SELECT *
FROM users
WHERE LOWER(email) = 'a@example.com';
```

如果查询经常对列做函数，优先考虑：

1. 能否改写为不对列做函数。
2. 能否增加生成列并建索引。
3. 是否需要函数索引。

### 7.7 不可见索引

不可见索引不会被优化器默认使用，但仍会维护。

```sql
ALTER TABLE orders ALTER INDEX idx_old INVISIBLE;
ALTER TABLE orders ALTER INDEX idx_old VISIBLE;
```

用途：

- 删除索引前先灰度验证影响。
- 判断某个索引是否真的被查询依赖。

注意：不可见索引仍有写入维护成本，不是“禁用维护”。

---

## 8. 选择性与基数

### 8.1 定义

- **基数（cardinality）**：索引列不同值的数量。
- **选择性（selectivity）**：不同值数量 / 总行数。

```text
选择性越高，索引过滤效果通常越好。
```

示例：

| 列 | 可能值 | 选择性 | 是否适合单列索引 |
|---|---:|---:|---|
| `id` | 几乎每行不同 | 高 | 是 |
| `email` | 几乎每行不同 | 高 | 是 |
| `gender` | 少量值 | 低 | 通常不适合单独建索引 |
| `status` | 少量值 | 低 | 可放入联合索引，服务过滤/排序/覆盖 |

### 8.2 低选择性列也可能有用

低选择性列不是永远不能建索引。它可能适合：

- 和高选择性列组成联合索引。
- 配合排序避免 filesort。
- 覆盖高频查询。
- 当目标值极少见时，例如 `status = 'FAILED'` 只占 0.1%。

### 8.3 查看统计信息

```sql
SHOW INDEX FROM orders;
ANALYZE TABLE orders;
```

`SHOW INDEX` 中的 `Cardinality` 是估算值，不是精确值。统计信息过旧时，优化器可能选错执行计划。

---

## 9. EXPLAIN 与 EXPLAIN ANALYZE

### 9.1 EXPLAIN 看什么

```sql
EXPLAIN
SELECT *
FROM orders
WHERE user_id = 10
ORDER BY created_at DESC
LIMIT 20;
```

重点字段：

| 字段 | 含义 | 关注点 |
|---|---|---|
| `type` | 访问类型 | `ALL` 通常危险；`range/ref/eq_ref/const` 更好 |
| `possible_keys` | 可能使用的索引 | 候选索引，不等于实际使用 |
| `key` | 实际使用索引 | 是否命中预期索引 |
| `key_len` | 使用索引长度 | 判断联合索引用了几列 |
| `rows` | 预估扫描行数 | 估算是否离谱 |
| `filtered` | 预估过滤比例 | 过滤是否发生太晚 |
| `Extra` | 额外信息 | 排序、临时表、覆盖索引、ICP |

常见 `Extra`：

| Extra | 含义 |
|---|---|
| `Using index` | 覆盖索引 |
| `Using index condition` | 索引下推 |
| `Using where` | 服务器层继续过滤 |
| `Using filesort` | 需要额外排序 |
| `Using temporary` | 使用临时表，常见于分组/去重/复杂排序 |

### 9.2 访问类型大致优先级

从好到差大致为：

```text
system/const -> eq_ref -> ref -> range -> index -> ALL
```

不要只看 `type`。一个扫描 10 行的 `ALL` 可能没问题，一个扫描 1000 万行的 `range` 也可能很慢。

### 9.3 EXPLAIN ANALYZE

`EXPLAIN ANALYZE` 会实际执行查询，并返回真实耗时、真实行数、循环次数。

```sql
EXPLAIN ANALYZE
SELECT *
FROM orders
WHERE user_id = 10
ORDER BY created_at DESC
LIMIT 20;
```

用途：

- 对比优化器估算行数和实际行数。
- 找出真正耗时的执行节点。
- 判断是否存在统计信息失真。

注意：它会执行 SQL。对写入语句或高成本查询要谨慎，先在测试环境或只读事务中验证。

---

## 10. 优化器与统计信息

### 10.1 优化器做什么

优化器负责在多个执行方案中选择成本最低的路径，包括：

- 选择哪个索引。
- 决定 JOIN 顺序。
- 判断是否使用范围扫描。
- 判断是否使用排序、临时表、索引合并。
- 估算扫描行数和过滤比例。

优化器不是“总是正确”，它依赖统计信息和成本模型。

### 10.2 统计信息失真

常见原因：

- 表数据变化很大，但统计信息未刷新。
- 列值分布高度倾斜。
- 多列相关性强，但优化器按独立分布估算。
- 低基数列在不同值上的分布差异极大。

处理方式：

```sql
ANALYZE TABLE orders;
```

对于分布倾斜明显的列，可以考虑直方图统计信息（是否使用取决于版本和场景）。

### 10.3 不要滥用 hint

优化器 hint 或 `FORCE INDEX` 可以救急，但要谨慎：

```sql
SELECT *
FROM orders FORCE INDEX (idx_user_created)
WHERE user_id = 10
ORDER BY created_at DESC
LIMIT 20;
```

风险：

- 数据分布变化后，强制索引可能反而变慢。
- 掩盖统计信息问题。
- 增加后续维护成本。

优先级：

```text
改 SQL / 改索引 / 刷统计信息 > 使用 hint
```

---

## 11. 慢查询日志

慢查询日志用于发现真实慢 SQL。

常见配置项：

```sql
SHOW VARIABLES LIKE 'slow_query_log';
SHOW VARIABLES LIKE 'long_query_time';
SHOW VARIABLES LIKE 'log_queries_not_using_indexes';
```

临时开启示例：

```sql
SET GLOBAL slow_query_log = ON;
SET GLOBAL long_query_time = 1;
```

关注指标：

- `Query_time`：执行总时间。
- `Lock_time`：等待锁时间。
- `Rows_examined`：扫描行数。
- `Rows_sent`：返回行数。

判断线索：

```text
Rows_examined 很高，Rows_sent 很低 -> 过滤效率差，索引可能不合适
Lock_time 高 -> 关注锁竞争，见 [[04-InnoDB事务锁与日志]]
Query_time 高但扫描少 -> 可能是锁、网络、临时表、排序或资源瓶颈
```

生产环境建议使用 `pt-query-digest` 或平台化采集做聚合分析，避免只盯单条日志。

---

## 12. 常见 SQL 优化

### 12.1 避免 SELECT *

问题：

- 增加网络传输。
- 增加回表概率。
- 降低覆盖索引机会。
- 表结构变化时影响调用方。

建议：只取必要列。

```sql
SELECT id, status, created_at
FROM orders
WHERE user_id = 10;
```

### 12.2 避免对索引列做函数或隐式转换

低效写法：

```sql
WHERE DATE(created_at) = '2026-01-01'
```

更好写法：

```sql
WHERE created_at >= '2026-01-01'
  AND created_at <  '2026-01-02'
```

隐式转换示例：

```sql
-- phone 是 varchar 时，不要写 phone = 13800138000
WHERE phone = '13800138000'
```

### 12.3 LIKE 优化

可用索引：

```sql
WHERE name LIKE 'abc%'
```

通常难用普通 B+Tree 索引：

```sql
WHERE name LIKE '%abc'
WHERE name LIKE '%abc%'
```

替代方案：全文索引、搜索引擎、倒排索引、冗余反转列等。

### 12.4 OR 与 UNION

复杂 `OR` 可能导致索引利用变差。可以评估改写为 `UNION ALL`：

```sql
SELECT id FROM orders WHERE user_id = 10
UNION ALL
SELECT id FROM orders WHERE merchant_id = 20;
```

前提：两边结果是否可能重复。如果可能重复，用 `UNION` 或增加排重条件。

### 12.5 IN 与 EXISTS

不要机械地说 `IN` 一定慢或 `EXISTS` 一定快。应看：

- 子查询结果规模。
- 是否能半连接优化。
- 关联列是否有索引。
- `EXPLAIN ANALYZE` 的真实行数。

### 12.6 大批量写入

批量写入优化方向：

- 合并多行插入。
- 控制事务大小。
- 减少不必要二级索引。
- 避免频繁随机主键插入。
- 关注 redo log、binlog、刷盘策略，见 [[05-MySQL运维高可用安全与面试]]。

---

## 13. 分页优化

### 13.1 深分页问题

低效写法：

```sql
SELECT *
FROM orders
ORDER BY id
LIMIT 1000000, 20;
```

MySQL 需要跳过大量记录，再返回 20 条。即使使用索引，也可能扫描很多行。

### 13.2 延迟关联

先用覆盖索引取主键，再回表取完整数据：

```sql
SELECT o.*
FROM orders o
JOIN (
  SELECT id
  FROM orders
  ORDER BY id
  LIMIT 1000000, 20
) t ON t.id = o.id;
```

适合宽表。内部子查询尽量走覆盖索引。

### 13.3 游标分页

更推荐用“上一页最后一个值”继续查：

```sql
SELECT id, created_at, status
FROM orders
WHERE id > 1000000
ORDER BY id
LIMIT 20;
```

如果按时间倒序：

```sql
SELECT id, created_at, status
FROM orders
WHERE (created_at, id) < ('2026-06-01 12:00:00', 12345)
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

配套索引：

```sql
CREATE INDEX idx_created_id ON orders(created_at, id);
```

---

## 14. JOIN 优化

### 14.1 基本原则

JOIN 优化重点：让驱动表尽量小，让被驱动表能用索引快速匹配。

```sql
SELECT o.id, u.email
FROM orders o
JOIN users u ON u.id = o.user_id
WHERE o.created_at >= '2026-01-01';
```

建议：

- `orders(created_at, user_id)` 支持过滤后连接。
- `users(id)` 通常是主键。
- 只返回必要列。

### 14.2 JOIN 字段类型必须一致

避免：

```text
orders.user_id 是 BIGINT
users.id 是 VARCHAR
```

类型不一致可能导致隐式转换，破坏索引使用或增加比较成本。

### 14.3 小表驱动大表不是绝对规则

优化器会估算成本并重排 JOIN 顺序。真正要看：

- 过滤后行数。
- 连接列索引。
- 是否产生巨大中间结果。
- `EXPLAIN ANALYZE` 的循环次数。

### 14.4 避免无条件笛卡尔积

```sql
-- 危险：缺少 ON 条件
SELECT *
FROM users u
JOIN orders o;
```

笛卡尔积会快速放大中间结果，拖垮排序、临时表和网络传输。

---

## 15. 排序、分组与临时表

### 15.1 ORDER BY 使用索引

索引可以帮助排序，但条件苛刻。对索引 `idx(user_id, created_at)`：

```sql
WHERE user_id = 10
ORDER BY created_at
```

通常可以利用索引顺序。

不容易利用：

```sql
WHERE user_id > 10
ORDER BY created_at
```

因为范围扫描后整体顺序不一定满足 `created_at` 排序。

### 15.2 filesort

`Using filesort` 不一定是磁盘排序，也不一定必然很慢。它表示 MySQL 需要额外排序过程。

优化方向：

- 建立匹配 `WHERE + ORDER BY` 的联合索引。
- 降低排序行数。
- 减少排序字段宽度。
- 使用覆盖索引。
- 对业务允许的场景改成游标分页。

### 15.3 临时表

`Using temporary` 常见于：

- `GROUP BY`
- `DISTINCT`
- 复杂 `ORDER BY`
- 派生表 / 子查询物化
- 聚合后排序

优化方向：

- 先过滤再分组。
- 让分组列或排序列匹配索引。
- 减少中间结果列。
- 拆分复杂查询。

---

## 16. 建索引的取舍

### 16.1 索引的成本

索引会带来：

- 写入维护成本。
- 占用磁盘和 Buffer Pool。
- 页分裂和随机写。
- 优化器选择空间变大。
- DDL 维护成本。

不要把索引当作免费的加速器。

### 16.2 冗余索引

例如已有：

```sql
INDEX idx_a_b(a, b)
INDEX idx_a(a)
```

`idx_a` 可能是冗余索引，因为 `idx_a_b` 的最左前缀已经包含 `a`。但删除前要确认：

- 是否有查询依赖更小索引减少 I/O。
- 是否有外键或唯一约束需求。
- 是否能通过不可见索引验证。

### 16.3 什么时候该建联合索引

满足多个条件时更值得：

- SQL 高频且性能敏感。
- 过滤条件稳定。
- 返回行数远小于总行数。
- 能同时服务过滤、排序、覆盖。
- 写入成本可接受。

---

## 17. 性能排查清单

### 17.1 先确认问题边界

- [ ] 是单条 SQL 慢，还是整体数据库慢？
- [ ] 是偶发慢，还是稳定慢？
- [ ] 慢在执行、锁等待、网络、应用处理，还是连接池？
- [ ] 数据量、参数、时间段是否变化？

### 17.2 看真实 SQL

- [ ] 从慢查询日志或 APM 取真实 SQL。
- [ ] 确认绑定参数，不只看模板。
- [ ] 记录返回行数和扫描行数。
- [ ] 确认是否 `SELECT *`。

### 17.3 看执行计划

- [ ] `EXPLAIN` 的 `key` 是否符合预期？
- [ ] `rows` 是否过大？
- [ ] `Extra` 是否有 `Using filesort` / `Using temporary`？
- [ ] 是否有 `Using index` 或 `Using index condition`？
- [ ] 用 `EXPLAIN ANALYZE` 对比估算和实际。

### 17.4 看索引设计

- [ ] 条件是否满足最左前缀？
- [ ] 联合索引列顺序是否匹配查询？
- [ ] 是否因为函数、隐式转换、前导通配符导致索引失效？
- [ ] 是否有大量回表？
- [ ] 是否可用覆盖索引？
- [ ] 是否有冗余或无效索引？

### 17.5 看数据分布与统计信息

- [ ] 选择性是否足够？
- [ ] 是否存在严重数据倾斜？
- [ ] `SHOW INDEX` 的基数是否明显不可信？
- [ ] 是否需要 `ANALYZE TABLE`？

### 17.6 看 JOIN、排序、分页

- [ ] JOIN 被驱动表连接列是否有索引？
- [ ] JOIN 后中间结果是否过大？
- [ ] 排序是否能利用索引？
- [ ] 是否深分页？能否改游标分页？
- [ ] 分组 / 去重是否产生大临时表？

### 17.7 看系统与锁

- [ ] 慢查询中的 `Lock_time` 是否高？
- [ ] 是否有长事务阻塞，见 [[04-InnoDB事务锁与日志]]？
- [ ] Buffer Pool 命中率、I/O、CPU 是否异常？
- [ ] redo / binlog / replication 是否成为瓶颈，见 [[05-MySQL运维高可用安全与面试]]？

---

## 18. 复习速记

- B+Tree 适合等值、范围、排序，不适合前导模糊匹配。
- InnoDB 聚簇索引叶子节点存整行；二级索引叶子节点存主键。
- 回表是二级索引到聚簇索引的再次查找；覆盖索引可以避免回表。
- 联合索引遵守最左前缀；范围条件后的列通常不能继续定位。
- ICP 不能改变最左前缀，但能在索引层提前过滤，减少回表。
- 索引选择看选择性、基数、查询频率、排序需求和写入成本。
- `EXPLAIN` 看估算，`EXPLAIN ANALYZE` 看真实执行。
- 慢查询优化先看 `Rows_examined / Rows_sent`，再看执行计划。
- 深分页优先改游标分页或延迟关联。
- JOIN 优化重点是小中间结果和被驱动表索引。
- `Using filesort` / `Using temporary` 是信号，不是结论；结合行数和耗时判断。

---

## 19. 参考

- MySQL 8.4 Reference Manual：InnoDB 索引、优化器、EXPLAIN、慢查询日志。
- 官方文档入口：https://dev.mysql.com/doc/refman/8.4/en/

