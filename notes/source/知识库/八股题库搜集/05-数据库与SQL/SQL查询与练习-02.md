# SQL查询与练习

<a id="k14ac517d3019"></a>

## 根据指定记录是否存在输出不同情况（困难）

**描述**：

现有用户信息表 `user_info`（`uid` 用户 ID，`nick_name` 昵称, `achievement` 成就值, `level` 等级, `job` 职业方向, `register_time` 注册时间）：

| id  | uid  | nick_name   | achievement | level | job  | register_time       |
| --- | ---- | ----------- | ----------- | ----- | ---- | ------------------- |
| 1   | 1001 | 牛客 1 号   | 19          | 0     | 算法 | 2020-01-01 10:00:00 |
| 2   | 1002 | 牛客 2 号   | 1200        | 3     | 算法 | 2020-01-01 10:00:00 |
| 3   | 1003 | 进击的 3 号 | 22          | 0     | 算法 | 2020-01-01 10:00:00 |
| 4   | 1004 | 牛客 4 号   | 25          | 0     | 算法 | 2020-01-01 10:00:00 |
| 5   | 1005 | 牛客 555 号 | 2000        | 7     | C++  | 2020-01-01 10:00:00 |
| 6   | 1006 | 666666      | 3000        | 6     | C++  | 2020-01-01 10:00:00 |

试卷作答记录表 `exam_record`（`uid` 用户 ID, `exam_id` 试卷 ID, `start_time` 开始作答时间, `submit_time` 交卷时间, `score` 得分）：

| id  | uid  | exam_id | start_time          | submit_time         | score  |
| --- | ---- | ------- | ------------------- | ------------------- | ------ |
| 1   | 1001 | 9001    | 2020-01-02 09:01:01 | 2020-01-02 09:21:59 | 80     |
| 2   | 1001 | 9001    | 2021-05-02 10:01:01 | (NULL)              | (NULL) |
| 3   | 1001 | 9002    | 2021-02-02 19:01:01 | 2021-02-02 19:30:01 | 87     |
| 4   | 1001 | 9002    | 2021-09-01 12:01:01 | (NULL)              | (NULL) |
| 5   | 1001 | 9003    | 2021-09-02 12:01:01 | (NULL)              | (NULL) |
| 6   | 1001 | 9004    | 2021-09-03 12:01:01 | (NULL)              | (NULL) |
| 7   | 1002 | 9001    | 2020-01-01 12:01:01 | 2020-01-01 12:31:01 | 99     |
| 8   | 1002 | 9003    | 2020-02-01 12:01:01 | 2020-02-01 12:31:01 | 82     |
| 9   | 1002 | 9003    | 2020-02-02 12:11:01 | (NULL)              | (NULL) |
| 10  | 1002 | 9002    | 2021-05-05 18:01:01 | (NULL)              | (NULL) |
| 11  | 1002 | 9001    | 2021-09-06 12:01:01 | (NULL)              | (NULL) |
| 12  | 1003 | 9003    | 2021-02-06 12:01:01 | (NULL)              | (NULL) |
| 13  | 1003 | 9001    | 2021-09-07 10:01:01 | 2021-09-07 10:31:01 | 89     |

请你筛选表中的数据，当有任意一个 0 级用户未完成试卷数大于 2 时，输出每个 0 级用户的试卷未完成数和未完成率（保留 3 位小数）；若不存在这样的用户，则输出所有有作答记录的用户的这两个指标。结果按未完成率升序排序。

由示例数据结果输出如下：

| uid  | incomplete_cnt | incomplete_rate |
| ---- | -------------- | --------------- |
| 1004 | 0              | 0.000           |
| 1003 | 1              | 0.500           |
| 1001 | 4              | 0.667           |

**解释**：0 级用户有 1001、1003、1004；他们作答试卷数和未完成数分别为：6:4、2:1、0:0；

存在 1001 这个 0 级用户未完成试卷数大于 2，因此输出这三个用户的未完成数和未完成率（1004 未作答过试卷，未完成率默认填 0，保留 3 位小数后是 0.000）；

结果按照未完成率升序排序。

附：如果 1001 不满足『未完成试卷数大于 2』，则需要输出 1001、1002、1003 的这两个指标，因为试卷作答记录表里只有这三个用户的作答记录。

**思路**：

先把可能满足条件**“0 级用户未完成试卷数大于 2”**的 SQL 写出来

```sql
SELECT ui.uid UID
FROM user_info ui
LEFT JOIN exam_record er ON ui.uid = er.uid
WHERE ui.uid IN
    (SELECT ui.uid
     FROM user_info ui
     LEFT JOIN exam_record er ON ui.uid = er.uid
     WHERE er.submit_time IS NULL
       AND ui.LEVEL = 0 )
GROUP BY ui.uid
HAVING sum(IF(er.submit_time IS NULL, 1, 0)) > 2
```

然后再分别写出两种情况的 SQL 查询语句：

情况 1. 查询存在条件要求的 0 级用户的试卷未完成率

```sql
SELECT
	tmp1.uid uid,
	sum(
	IF
	( er.submit_time IS NULL AND er.start_time IS NOT NULL, 1, 0 )) incomplete_cnt,
	round(
		sum(
		IF
		( er.submit_time IS NULL AND er.start_time IS NOT NULL, 1, 0 ))/ count( tmp1.uid ),
		3
	) incomplete_rate
FROM
	(
	SELECT DISTINCT
		ui.uid
	FROM
		user_info ui
		LEFT JOIN exam_record er ON ui.uid = er.uid
	WHERE
		er.submit_time IS NULL
		AND ui.LEVEL = 0
	) tmp1
	LEFT JOIN exam_record er ON tmp1.uid = er.uid
GROUP BY
	tmp1.uid
ORDER BY
	incomplete_rate
```

情况 2. 查询不存在条件要求时所有有作答记录的 yong 用户的试卷未完成率

```sql
SELECT
	ui.uid uid,
	sum( CASE WHEN er.submit_time IS NULL AND er.start_time IS NOT NULL THEN 1 ELSE 0 END ) incomplete_cnt,
	round(
		sum(
		IF
		( er.submit_time IS NULL AND er.start_time IS NOT NULL, 1, 0 ))/ count( ui.uid ),
		3
	) incomplete_rate
FROM
	user_info ui
	JOIN exam_record er ON ui.uid = er.uid
GROUP BY
	ui.uid
ORDER BY
	incomplete_rate
```

拼在一起，就是答案

```sql
WITH host_user AS
  (SELECT ui.uid UID
   FROM user_info ui
   LEFT JOIN exam_record er ON ui.uid = er.uid
   WHERE ui.uid IN
       (SELECT ui.uid
        FROM user_info ui
        LEFT JOIN exam_record er ON ui.uid = er.uid
        WHERE er.submit_time IS NULL
          AND ui.LEVEL = 0 )
   GROUP BY ui.uid
   HAVING sum(IF (er.submit_time IS NULL, 1, 0))> 2),
     tt1 AS
  (SELECT tmp1.uid UID,
                   sum(IF (er.submit_time IS NULL
                           AND er.start_time IS NOT NULL, 1, 0)) incomplete_cnt,
                   round(sum(IF (er.submit_time IS NULL
                                 AND er.start_time IS NOT NULL, 1, 0))/ count(tmp1.uid), 3) incomplete_rate
   FROM
     (SELECT DISTINCT ui.uid
      FROM user_info ui
      LEFT JOIN exam_record er ON ui.uid = er.uid
      WHERE er.submit_time IS NULL
        AND ui.LEVEL = 0 ) tmp1
   LEFT JOIN exam_record er ON tmp1.uid = er.uid
   GROUP BY tmp1.uid
   ORDER BY incomplete_rate),
     tt2 AS
  (SELECT ui.uid UID,
                 sum(CASE
                         WHEN er.submit_time IS NULL
                              AND er.start_time IS NOT NULL THEN 1
                         ELSE 0
                     END) incomplete_cnt,
                 round(sum(IF (er.submit_time IS NULL
                               AND er.start_time IS NOT NULL, 1, 0))/ count(ui.uid), 3) incomplete_rate
   FROM user_info ui
   JOIN exam_record er ON ui.uid = er.uid
   GROUP BY ui.uid
   ORDER BY incomplete_rate)
  (SELECT tt1.*
   FROM tt1
   LEFT JOIN
     (SELECT UID
      FROM host_user) t1 ON 1 = 1
   WHERE t1.uid IS NOT NULL )
UNION ALL
  (SELECT tt2.*
   FROM tt2
   LEFT JOIN
     (SELECT UID
      FROM host_user) t2 ON 1 = 1
   WHERE t2.uid IS NULL)
```

V2 版本（根据上面做出的改进，答案缩短了，逻辑更强）：

```sql
SELECT
	ui.uid,
	SUM(
	IF
	( start_time IS NOT NULL AND score IS NULL, 1, 0 )) AS incomplete_cnt,#3.试卷未完成数
	ROUND( AVG( IF ( start_time IS NOT NULL AND score IS NULL, 1, 0 )), 3 ) AS incomplete_rate #4.未完成率

FROM
	user_info ui
	LEFT JOIN exam_record USING ( uid )
WHERE
CASE

		WHEN (#1.当有任意一个0级用户未完成试卷数大于2时
		SELECT
			MAX( lv0_incom_cnt )
		FROM
			(
			SELECT
				SUM(
				IF
				( score IS NULL, 1, 0 )) AS lv0_incom_cnt
			FROM
				user_info
				JOIN exam_record USING ( uid )
			WHERE
				LEVEL = 0
			GROUP BY
				uid
			) table1
			)> 2 THEN
			uid IN ( #1.1找出每个0级用户
			SELECT uid FROM user_info WHERE LEVEL = 0 ) ELSE uid IN ( #2.若不存在这样的用户，找出有作答记录的用户
			SELECT DISTINCT uid FROM exam_record )
		END
		GROUP BY
			ui.uid
	ORDER BY
	incomplete_rate #5.结果按未完成率升序排序
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-05.md#L340)，来源许可：Apache-2.0。

<a id="k8f3dd71df3f0"></a>

## 检索产品名称和描述（一）

`Products` 表如下：

【问题】编写 SQL 语句，从 `Products` 表中检索产品名称（`prod_name`）和描述（`prod_desc`），仅返回描述中包含 `toy` 一词的产品名称。

```sql
SELECT prod_name, prod_desc
FROM Products
WHERE prod_desc LIKE '%toy%'
```

**相关解释：** [检索产品名称和描述（二）](SQL%E6%9F%A5%E8%AF%A2%E4%B8%8E%E7%BB%83%E4%B9%A0-02.md#k2fb043ad3f45)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L413)，来源许可：Apache-2.0。

<a id="kecb1ab58f3b0"></a>

## 检索产品名称和描述（三）

`Products` 表如下：

| prod_name | prod_desc        |
| --------- | ---------------- |
| a0011     | usb              |
| a0019     | iphone13         |
| b0019     | gucci t-shirts   |
| c0019     | gucci toy        |
| d0019     | lego carrots toy |

【问题】编写 SQL 语句，从 `Products` 表中检索产品名称（`prod_name`）和描述（`prod_desc`），仅返回描述中同时出现 `toy` 和 `carrots` 的产品。有好几种方法可以执行此操作，但对于这个挑战题，请使用 `AND` 和两个 `LIKE` 比较。

```sql
SELECT prod_name, prod_desc
FROM Products
WHERE prod_desc LIKE '%toy%' AND prod_desc LIKE "%carrots%"
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L458)，来源许可：Apache-2.0。

<a id="k2fb043ad3f45"></a>

## 检索产品名称和描述（二）

`Products` 表如下：

| prod_name | prod_desc      |
| --------- | -------------- |
| a0011     | usb            |
| a0019     | iphone13       |
| b0019     | gucci t-shirts |
| c0019     | gucci toy      |
| d0019     | lego toy       |

【问题】编写 SQL 语句，从 `Products` 表中检索产品名称（`prod_name`）和描述（`prod_desc`），仅返回描述中未出现 `toy` 一词的产品，最后按”产品名称“对结果进行排序。

```sql
SELECT prod_name, prod_desc
FROM Products
WHERE prod_desc NOT LIKE '%toy%'
ORDER BY prod_name
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L435)，来源许可：Apache-2.0。

<a id="k61dd9bc5e161"></a>

## 检索产品名称和描述（四）

`Products` 表如下：

| prod_name | prod_desc        |
| --------- | ---------------- |
| a0011     | usb              |
| a0019     | iphone13         |
| b0019     | gucci t-shirts   |
| c0019     | gucci toy        |
| d0019     | lego toy carrots |

【问题】编写 SQL 语句，从 Products 表中检索产品名称（prod_name）和描述（prod_desc），仅返回在描述中以**先后顺序**同时出现 toy 和 carrots 的产品。提示：只需要用带有三个 `%` 符号的 `LIKE` 即可。

```sql
SELECT prod_name, prod_desc
FROM Products
WHERE prod_desc LIKE '%toy%carrots%'
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L480)，来源许可：Apache-2.0。

<a id="k03c7e8e21abb"></a>

## 检索供应商名称

`Vendors` 表有字段供应商名称（`vend_name`）、供应商国家（`vend_country`）、供应商州（`vend_state`）

【问题】编写 SQL 语句，从 `Vendors` 表中检索供应商名称（`vend_name`），仅返回加利福尼亚州的供应商（这需要按国家[USA]和州[CA]进行过滤，没准其他国家也存在一个 CA）

```sql
SELECT vend_name
FROM Vendors
WHERE vend_country = 'USA' AND vend_state = 'CA'
```

**相关解释：** [检查 SQL 语句](%E6%95%B0%E6%8D%AE%E6%A8%A1%E5%9E%8B%E4%B8%8E%E6%95%B0%E6%8D%AE%E5%BA%93%E5%9F%BA%E7%A1%80-02.md#k95787f0c1cda)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L305)，来源许可：Apache-2.0。

<a id="k85548a3795e2"></a>

## 检索并列出已订购产品的清单

`OrderItems` 表包含了所有已订购的产品（有些已被订购多次）。

| prod_id | order_num | quantity |
| ------- | --------- | -------- |
| BR01    | a1        | 105      |
| BR02    | a2        | 1100     |
| BR02    | a2        | 200      |
| BR03    | a4        | 1121     |
| BR017   | a5        | 10       |
| BR02    | a2        | 19       |
| BR017   | a7        | 5        |

【问题】编写 SQL 语句，查找所有订购了数量至少 100 个的 `BR01`、`BR02` 或 `BR03` 的订单。你需要返回 `OrderItems` 表的订单号（`order_num`）、产品 ID（`prod_id`）和数量（`quantity`），并按产品 ID 和数量进行过滤。

```sql
SELECT order_num, prod_id, quantity
FROM OrderItems
WHERE prod_id IN ('BR01', 'BR02', 'BR03') AND quantity >= 100
```

### 补充说明

表 `OrderItems` 含有非空的列 `prod_id` 代表商品 id，包含了所有已订购的商品（有些已被订购多次）。

| prod_id |
| ------- |
| a1      |
| a2      |
| a3      |
| a4      |
| a5      |
| a6      |
| a7      |

编写 SQL 语句，检索并列出所有已订购商品（`prod_id`）的去重后的清单。

```sql
SELECT DISTINCT prod_id
FROM OrderItems
```

知识点：`DISTINCT` 用于返回列中的唯一不同值。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L325)，来源许可：Apache-2.0。
- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L39)，来源许可：Apache-2.0。

<a id="k88b93f7b14ae"></a>

## 检索所有列

现在有 `Customers` 表（表中含有列 `cust_id` 代表客户 id，`cust_name` 代表客户姓名）

| cust_id | cust_name |
| ------- | --------- |
| a1      | andy      |
| a2      | ben       |
| a3      | tony      |
| a4      | tom       |
| a5      | an        |
| a6      | lee       |
| a7      | hex       |

需要编写 SQL 语句，检索所有列。

```sql
SELECT cust_id, cust_name
FROM Customers
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L64)，来源许可：Apache-2.0。

<a id="k4a88482e8844"></a>

## 检索每个顾客的名称和所有的订单号（一）

`Customers` 表代表顾客信息含有顾客 id `cust_id` 和 顾客名称 `cust_name`

`Orders` 表代表订单信息含有订单号 `order_num` 和顾客 id `cust_id`

【问题】使用 INNER JOIN 编写 SQL 语句，检索每个顾客的名称（`Customers` 表中的 `cust_name`）和所有的订单号（`Orders` 表中的 `order_num`），最后根据顾客姓名 `cust_name` 升序返回。

```sql
SELECT cust_name, order_num
FROM Customers
INNER JOIN Orders
USING(cust_id)
ORDER BY cust_name
```

**相关解释：** [返回顾客名称和相关订单号以及每个订单的总价](SQL%E6%9F%A5%E8%AF%A2%E4%B8%8E%E7%BB%83%E4%B9%A0-03.md#k48316d2abd47)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L1498)，来源许可：Apache-2.0。

<a id="k21a70d0172e6"></a>

## 检索每个顾客的名称和所有的订单号（二）

`Orders` 表代表订单信息含有订单号 `order_num` 和顾客 id `cust_id`

`Customers` 表代表顾客信息含有顾客 id `cust_id` 和 顾客名称 `cust_name`

| cust_id  | cust_name |
| -------- | --------- |
| cust10   | andy      |
| cust1    | ben       |
| cust2    | tony      |
| cust22   | tom       |
| cust221  | an        |
| cust2217 | hex       |
| cust40   | ace       |

【问题】检索每个顾客的名称（`Customers` 表中的 `cust_name`）和所有的订单号（Orders 表中的 `order_num`），列出所有的顾客，即使他们没有下过订单。最后根据顾客姓名 `cust_name` 升序返回。

```sql
SELECT cust_name, order_num
FROM Customers
LEFT JOIN Orders
USING(cust_id)
ORDER BY cust_name
```

**相关解释：** [返回顾客名称和相关订单号以及每个订单的总价](SQL%E6%9F%A5%E8%AF%A2%E4%B8%8E%E7%BB%83%E4%B9%A0-03.md#k48316d2abd47)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L1532)，来源许可：Apache-2.0。

<a id="k9387f4389643"></a>

## 检索顾客名称并且排序

有表 `Customers`，`cust_id` 代表客户 id，`cust_name` 代表客户姓名。

| cust_id | cust_name |
| ------- | --------- |
| a1      | andy      |
| a2      | ben       |
| a3      | tony      |
| a4      | tom       |
| a5      | an        |
| a6      | lee       |
| a7      | hex       |

从 `Customers` 中检索所有的顾客名称（`cust_name`），并按从 Z 到 A 的顺序显示结果。

```sql
SELECT cust_name
FROM Customers
ORDER BY cust_name DESC
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L91)，来源许可：Apache-2.0。

<a id="k07567cfaf867"></a>

## 每个 6/7 级用户活跃情况（困难）

**描述**：

现有用户信息表 `user_info`（`uid` 用户 ID，`nick_name` 昵称, `achievement` 成就值, `level` 等级, `job` 职业方向, `register_time` 注册时间）：

| id  | uid  | nick_name | achievement | level | job  | register_time       |
| --- | ---- | --------- | ----------- | ----- | ---- | ------------------- |
| 1   | 1001 | 牛客 1 号 | 3100        | 7     | 算法 | 2020-01-01 10:00:00 |
| 2   | 1002 | 牛客 2 号 | 2300        | 7     | 算法 | 2020-01-01 10:00:00 |
| 3   | 1003 | 牛客 3 号 | 2500        | 7     | 算法 | 2020-01-01 10:00:00 |
| 4   | 1004 | 牛客 4 号 | 1200        | 5     | 算法 | 2020-01-01 10:00:00 |
| 5   | 1005 | 牛客 5 号 | 1600        | 6     | C++  | 2020-01-01 10:00:00 |
| 6   | 1006 | 牛客 6 号 | 2600        | 7     | C++  | 2020-01-01 10:00:00 |

试卷信息表 `examination_info`（`exam_id` 试卷 ID, `tag` 试卷类别, `difficulty` 试卷难度, `duration` 考试时长, `release_time` 发布时间）：

| id  | exam_id | tag  | difficulty | duration | release_time        |
| --- | ------- | ---- | ---------- | -------- | ------------------- |
| 1   | 9001    | SQL  | hard       | 60       | 2021-09-01 06:00:00 |
| 2   | 9002    | C++  | easy       | 60       | 2021-09-01 06:00:00 |
| 3   | 9003    | 算法 | medium     | 80       | 2021-09-01 10:00:00 |

试卷作答记录表 `exam_record`（`uid` 用户 ID, `exam_id` 试卷 ID, `start_time` 开始作答时间, `submit_time` 交卷时间, `score` 得分）：

| uid  | exam_id | start_time          | submit_time         | score  |
| ---- | ------- | ------------------- | ------------------- | ------ |
| 1001 | 9001    | 2021-09-01 09:01:01 | 2021-09-01 09:31:00 | 78     |
| 1001 | 9001    | 2021-09-01 09:01:01 | 2021-09-01 09:31:00 | 81     |
| 1005 | 9001    | 2021-09-01 19:01:01 | 2021-09-01 19:30:01 | 85     |
| 1005 | 9002    | 2021-09-01 12:01:01 | 2021-09-01 12:31:02 | 85     |
| 1006 | 9003    | 2021-09-07 10:01:01 | 2021-09-07 10:21:59 | 84     |
| 1006 | 9001    | 2021-09-07 10:01:01 | 2021-09-07 10:21:01 | 81     |
| 1002 | 9001    | 2020-09-01 13:01:01 | 2020-09-01 13:41:01 | 81     |
| 1005 | 9001    | 2021-09-01 14:01:01 | (NULL)              | (NULL) |

题目练习记录表 `practice_record`（`uid` 用户 ID, `question_id` 题目 ID, `submit_time` 提交时间, `score` 得分）：

| uid  | question_id | submit_time         | score |
| ---- | ----------- | ------------------- | ----- |
| 1001 | 8001        | 2021-08-02 11:41:01 | 60    |
| 1004 | 8001        | 2021-08-02 19:38:01 | 70    |
| 1004 | 8002        | 2021-08-02 19:48:01 | 90    |
| 1001 | 8002        | 2021-08-02 19:38:01 | 70    |
| 1004 | 8002        | 2021-08-02 19:48:01 | 90    |
| 1006 | 8002        | 2021-08-04 19:58:01 | 94    |
| 1006 | 8003        | 2021-08-03 19:38:01 | 70    |
| 1006 | 8003        | 2021-08-02 19:48:01 | 90    |
| 1006 | 8003        | 2020-08-01 19:38:01 | 80    |

请统计每个 6/7 级用户总活跃月份数、2021 年活跃天数、2021 年试卷作答活跃天数、2021 年答题活跃天数，按照总活跃月份数、2021 年活跃天数降序排序。由示例数据结果输出如下：

| uid  | act_month_total | act_days_2021 | act_days_2021_exam |
| ---- | --------------- | ------------- | ------------------ |
| 1006 | 3               | 4             | 1                  |
| 1001 | 2               | 2             | 1                  |
| 1005 | 1               | 1             | 1                  |
| 1002 | 1               | 0             | 0                  |
| 1003 | 0               | 0             | 0                  |

**解释**：6/7 级用户共有 5 个，其中 1006 在 202109、202108、202008 共 3 个月活跃过，2021 年活跃的日期有 20210907、20210804、20210803、20210802 共 4 天，2021 年在试卷作答区 20210907 活跃 1 天，在题目练习区活跃了 3 天。

**思路：**

这题的关键在于`CASE WHEN THEN`的使用，不然要写很多的`left join` 因为会产生很多的结果集。

`CASE WHEN THEN`语句是一种条件表达式，用于在 SQL 中根据条件执行不同的操作或返回不同的结果。

语法结构如下：

```sql
CASE
    WHEN condition1 THEN result1
    WHEN condition2 THEN result2
    ...
    ELSE result
END
```

在这个结构中，可以根据需要添加多个`WHEN`子句，每个`WHEN`子句后面跟着一个条件（condition）和一个结果（result）。条件可以是任何逻辑表达式，如果满足条件，将返回对应的结果。

最后的`ELSE`子句是可选的，用于指定当所有前面的条件都不满足时的默认返回结果。如果没有提供`ELSE`子句，则默认返回`NULL`。

例如：

```sql
SELECT score,
    CASE
        WHEN score >= 90 THEN '优秀'
        WHEN score >= 80 THEN '良好'
        WHEN score >= 60 THEN '及格'
        ELSE '不及格'
    END AS grade
FROM student_scores;
```

在上述示例中，根据学生成绩（score）的不同范围，使用 CASE WHEN THEN 语句返回相应的等级（grade）。如果成绩大于等于 90，则返回"优秀"；如果成绩大于等于 80，则返回"良好"；如果成绩大于等于 60，则返回"及格"；否则返回"不及格"。

那了解到了上述的用法之后，回过头看看该题，要求列出不同的活跃天数。

```sql
count(distinct act_month) as act_month_total,
count(distinct case when year(act_time)='2021'then act_day end) as act_days_2021,
count(distinct case when year(act_time)='2021' and tag='exam' then act_day end) as act_days_2021_exam,
count(distinct case when year(act_time)='2021' and tag='question'then act_day end) as act_days_2021_question
```

这里的 tag 是先给标记，方便对查询进行区分，将考试和答题分开。

找出试卷作答区的用户

```sql
SELECT
		uid,
		exam_id AS ans_id,
		start_time AS act_time,
		date_format( start_time, '%Y%m' ) AS act_month,
		date_format( start_time, '%Y%m%d' ) AS act_day,
		'exam' AS tag
	FROM
		exam_record
```

紧接着就是答题作答区的用户

```sql
SELECT
		uid,
		question_id AS ans_id,
		submit_time AS act_time,
		date_format( submit_time, '%Y%m' ) AS act_month,
		date_format( submit_time, '%Y%m%d' ) AS act_day,
		'question' AS tag
	FROM
		practice_record
```

最后将两个结果进行`UNION` 最后别忘了将结果进行排序 （这题有点类似于分治法的思想）

**答案**：

```sql
SELECT user_info.uid,
       count(DISTINCT act_month) AS act_month_total,
       count(DISTINCT CASE
                          WHEN YEAR (act_time)= '2021' THEN act_day
                      END) AS act_days_2021,
       count(DISTINCT CASE
                          WHEN YEAR (act_time)= '2021'
                               AND tag = 'exam' THEN act_day
                      END) AS act_days_2021_exam,
       count(DISTINCT CASE
                          WHEN YEAR (act_time)= '2021'
                               AND tag = 'question' THEN act_day
                      END) AS act_days_2021_question
FROM
  (SELECT UID,
          exam_id AS ans_id,
          start_time AS act_time,
          date_format(start_time, '%Y%m') AS act_month,
          date_format(start_time, '%Y%m%d') AS act_day,
          'exam' AS tag
   FROM exam_record
   UNION ALL SELECT UID,
                    question_id AS ans_id,
                    submit_time AS act_time,
                    date_format(submit_time, '%Y%m') AS act_month,
                    date_format(submit_time, '%Y%m%d') AS act_day,
                    'question' AS tag
   FROM practice_record) total
RIGHT JOIN user_info ON total.uid = user_info.uid
WHERE user_info.LEVEL IN (6,
                          7)
GROUP BY user_info.uid
ORDER BY act_month_total DESC,
         act_days_2021 DESC
```

<!-- @include: @article-footer.snippet.md -->

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-03.md#L1128)，来源许可：Apache-2.0。

<a id="kfe18972bc16b"></a>

## 每个供应商成本最低的产品

有 `Products` 表，含有字段 `prod_price` 代表产品价格，`vend_id` 代表供应商 id

| vend_id | prod_price |
| ------- | ---------- |
| a0011   | 100        |
| a0019   | 0.1        |
| b0019   | 1000       |
| b0019   | 6980       |
| b0019   | 20         |

【问题】编写 SQL 语句，返回名为 `cheapest_item` 的字段，该字段包含每个供应商成本最低的产品（使用 `Products` 表中的 `prod_price`），然后从最低成本到最高成本对结果进行升序排序。

```sql
SELECT vend_id, Min(prod_price) AS cheapest_item
FROM Products
GROUP BY vend_id
ORDER BY cheapest_item
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L761)，来源许可：Apache-2.0。

<a id="k602b92392964"></a>

## 每个题目和每份试卷被作答的人数和次数

**描述**：

现有试卷作答记录表 exam_record（uid 用户 ID, exam_id 试卷 ID, start_time 开始作答时间, submit_time 交卷时间, score 得分）：

| id  | uid  | exam_id | start_time          | submit_time         | score  |
| --- | ---- | ------- | ------------------- | ------------------- | ------ |
| 1   | 1001 | 9001    | 2021-09-01 09:01:01 | 2021-09-01 09:41:01 | 81     |
| 2   | 1002 | 9002    | 2021-09-01 12:01:01 | 2021-09-01 12:31:01 | 70     |
| 3   | 1002 | 9001    | 2021-09-01 19:01:01 | 2021-09-01 19:40:01 | 80     |
| 4   | 1002 | 9002    | 2021-09-01 12:01:01 | 2021-09-01 12:31:01 | 70     |
| 5   | 1004 | 9001    | 2021-09-01 19:01:01 | 2021-09-01 19:40:01 | 85     |
| 6   | 1002 | 9002    | 2021-09-01 12:01:01 | (NULL)              | (NULL) |

题目练习表 practice_record（uid 用户 ID, question_id 题目 ID, submit_time 提交时间, score 得分）：

| id  | uid  | question_id | submit_time         | score |
| --- | ---- | ----------- | ------------------- | ----- |
| 1   | 1001 | 8001        | 2021-08-02 11:41:01 | 60    |
| 2   | 1002 | 8001        | 2021-09-02 19:30:01 | 50    |
| 3   | 1002 | 8001        | 2021-09-02 19:20:01 | 70    |
| 4   | 1002 | 8002        | 2021-09-02 19:38:01 | 70    |
| 5   | 1003 | 8001        | 2021-08-02 19:38:01 | 70    |
| 6   | 1003 | 8001        | 2021-08-02 19:48:01 | 90    |
| 7   | 1003 | 8002        | 2021-08-01 19:38:01 | 80    |

请统计每个题目和每份试卷被作答的人数和次数，分别按照"试卷"和"题目"的 uv & pv 降序显示，示例数据结果输出如下：

| tid  | uv  | pv  |
| ---- | --- | --- |
| 9001 | 3   | 3   |
| 9002 | 1   | 3   |
| 8001 | 3   | 5   |
| 8002 | 2   | 2   |

**解释**：“试卷”有 3 人共练习 3 次试卷 9001，1 人作答 3 次 9002；“刷题”有 3 人刷 5 次 8001，有 2 人刷 2 次 8002

**思路**：这题的难点和易错点在于`UNION`和`ORDER BY` 同时使用的问题

有以下几种情况：使用`union`和多个`order by`不加括号，报错！

`order by`在`union`连接的子句中不起作用；

比如不加括号：

```sql
SELECT exam_id AS tid,
       COUNT(DISTINCT UID) AS uv,
       COUNT(UID) AS pv
FROM exam_record
GROUP BY exam_id
ORDER BY uv DESC,
         pv DESC
UNION
SELECT question_id AS tid,
       COUNT(DISTINCT UID) AS uv,
       COUNT(UID) AS pv
FROM practice_record
GROUP BY question_id
ORDER BY uv DESC,
         pv DESC
```

直接报语法错误，如果没有括号，只能有一个`order by`

还有一种`order by`不起作用的情况，但是能在子句的子句中起作用，这里的解决方案就是在外面再套一层查询。

**答案**：

```sql
SELECT *
FROM
  (SELECT exam_id AS tid,
          COUNT(DISTINCT exam_record.uid) uv,
          COUNT(*) pv
   FROM exam_record
   GROUP BY exam_id
   ORDER BY uv DESC, pv DESC) t1
UNION
SELECT *
FROM
  (SELECT question_id AS tid,
          COUNT(DISTINCT practice_record.uid) uv,
          COUNT(*) pv
   FROM practice_record
   GROUP BY question_id
   ORDER BY uv DESC, pv DESC) t2;
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-03.md#L828)，来源许可：Apache-2.0。

<a id="k09bd7b0d6f4b"></a>

## 每份试卷每月作答数和截止当月的作答总数

**描述:**

现有试卷作答记录表 exam_record（uid 用户 ID, exam_id 试卷 ID, start_time 开始作答时间, submit_time 交卷时间, score 得分）：

请输出每份试卷每月作答数和截止当月的作答总数。
由示例数据结果输出如下：

| exam_id | start_month | month_cnt | cum_exam_cnt |
| ------- | ----------- | --------- | ------------ |
| 9001    | 202001      | 2         | 2            |
| 9001    | 202002      | 1         | 3            |
| 9001    | 202003      | 3         | 6            |
| 9001    | 202005      | 1         | 7            |
| 9002    | 202001      | 1         | 1            |
| 9002    | 202002      | 3         | 4            |
| 9002    | 202003      | 1         | 5            |

解释：试卷 9001 在 202001、202002、202003、202005 共 4 个月有被作答记录，每个月被作答数分别为 2、1、3、1，截止当月累积作答总数为 2、3、6、7。

**思路：**

这题就两个关键点：统计截止当月的作答总数、输出每份试卷每月作答数和截止当月的作答总数

这个是关键`**sum(count(*)) over(partition by exam_id order by date_format(start_time,'%Y%m'))**`

**答案**：

```sql
SELECT exam_id,
       date_format(start_time, '%Y%m') AS start_month,
       count(*) AS month_cnt,
       sum(count(*)) OVER (PARTITION BY exam_id
                           ORDER BY date_format(start_time, '%Y%m')) AS cum_exam_cnt
FROM exam_record
GROUP BY exam_id,
         start_month
```

**相关解释：** [每月及截止当月的答题情况（较难）](%E6%95%B0%E6%8D%AE%E6%A8%A1%E5%9E%8B%E4%B8%8E%E6%95%B0%E6%8D%AE%E5%BA%93%E5%9F%BA%E7%A1%80-02.md#kd0270f6f8e7f)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-04.md#L696)，来源许可：Apache-2.0。

<a id="k4f04629c5abd"></a>

## 每类试卷得分前三名

**描述**：

现有试卷信息表 `examination_info`（`exam_id` 试卷 ID, `tag` 试卷类别, `difficulty` 试卷难度, `duration` 考试时长, `release_time` 发布时间）：

| id  | exam_id | tag  | difficulty | duration | release_time        |
| --- | ------- | ---- | ---------- | -------- | ------------------- |
| 1   | 9001    | SQL  | hard       | 60       | 2021-09-01 06:00:00 |
| 2   | 9002    | SQL  | hard       | 60       | 2021-09-01 06:00:00 |
| 3   | 9003    | 算法 | medium     | 80       | 2021-09-01 10:00:00 |

试卷作答记录表 `exam_record`（`uid` 用户 ID, `exam_id` 试卷 ID, `start_time` 开始作答时间, `submit_time` 交卷时间, score 得分）：

| id  | uid  | exam_id | start_time          | submit_time         | score  |
| --- | ---- | ------- | ------------------- | ------------------- | ------ |
| 1   | 1001 | 9001    | 2021-09-01 09:01:01 | 2021-09-01 09:31:00 | 78     |
| 2   | 1002 | 9001    | 2021-09-01 09:01:01 | 2021-09-01 09:31:00 | 81     |
| 3   | 1002 | 9002    | 2021-09-01 12:01:01 | 2021-09-01 12:31:01 | 81     |
| 4   | 1003 | 9001    | 2021-09-01 19:01:01 | 2021-09-01 19:40:01 | 86     |
| 5   | 1003 | 9002    | 2021-09-01 12:01:01 | 2021-09-01 12:31:51 | 89     |
| 6   | 1004 | 9001    | 2021-09-01 19:01:01 | 2021-09-01 19:30:01 | 85     |
| 7   | 1005 | 9003    | 2021-09-01 12:01:01 | 2021-09-01 12:31:02 | 85     |
| 8   | 1006 | 9003    | 2021-09-07 10:01:01 | 2021-09-07 10:21:01 | 84     |
| 9   | 1003 | 9003    | 2021-09-08 12:01:01 | 2021-09-08 12:11:01 | 40     |
| 10  | 1003 | 9002    | 2021-09-01 14:01:01 | (NULL)              | (NULL) |

找到每类试卷得分的前 3 名，如果两人最大分数相同，选择最小分数大者，如果还相同，选择 uid 大者。由示例数据结果输出如下：

| tid  | uid  | ranking |
| ---- | ---- | ------- |
| SQL  | 1003 | 1       |
| SQL  | 1004 | 2       |
| SQL  | 1002 | 3       |
| 算法 | 1005 | 1       |
| 算法 | 1006 | 2       |
| 算法 | 1003 | 3       |

**解释**：有作答得分记录的试卷 tag 有 SQL 和算法，SQL 试卷用户 1001、1002、1003、1004 有作答得分，最高得分分别为 81、81、89、85，最低得分分别为 78、81、86、40，因此先按最高得分排名再按最低得分排名取前三为 1003、1004、1002。

**答案**：

```sql
SELECT tag,
       UID,
       ranking
FROM
  (SELECT b.tag AS tag,
          a.uid AS UID,
          ROW_NUMBER() OVER (PARTITION BY b.tag
                             ORDER BY b.tag,
                                      max(a.score) DESC,
                                      min(a.score) DESC,
                                      a.uid DESC) AS ranking
   FROM exam_record a
   LEFT JOIN examination_info b ON a.exam_id = b.exam_id
   GROUP BY b.tag,
            a.uid) t
WHERE ranking <= 3
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-04.md#L75)，来源许可：Apache-2.0。

<a id="k39c99999da25"></a>

## 注册当天就完成了试卷的名单第三页（较难）

**描述**：现有用户信息表 `user_info`（`uid` 用户 ID，`nick_name` 昵称, `achievement` 成就值, `level` 等级, `job` 职业方向, `register_time` 注册时间）：

| id  | uid  | nick_name    | achievement | level | job  | register_time       |
| --- | ---- | ------------ | ----------- | ----- | ---- | ------------------- |
| 1   | 1001 | 牛客 1       | 19          | 0     | 算法 | 2020-01-01 10:00:00 |
| 2   | 1002 | 牛客 2 号    | 1200        | 3     | 算法 | 2020-01-01 10:00:00 |
| 3   | 1003 | 牛客 3 号 ♂ | 22          | 0     | 算法 | 2020-01-01 10:00:00 |
| 4   | 1004 | 牛客 4 号    | 25          | 0     | 算法 | 2020-01-01 10:00:00 |
| 5   | 1005 | 牛客 555 号  | 4000        | 7     | 算法 | 2020-01-11 10:00:00 |
| 6   | 1006 | 牛客 6 号    | 25          | 0     | 算法 | 2020-01-02 11:00:00 |
| 7   | 1007 | 牛客 7 号    | 25          | 0     | 算法 | 2020-01-02 11:00:00 |
| 8   | 1008 | 牛客 8 号    | 25          | 0     | 算法 | 2020-01-02 11:00:00 |
| 9   | 1009 | 牛客 9 号    | 25          | 0     | 算法 | 2020-01-02 11:00:00 |
| 10  | 1010 | 牛客 10 号   | 25          | 0     | 算法 | 2020-01-02 11:00:00 |
| 11  | 1011 | 666666       | 3000        | 6     | C++  | 2020-01-02 10:00:00 |

试卷信息表 examination_info（exam_id 试卷 ID, tag 试卷类别, difficulty 试卷难度, duration 考试时长, release_time 发布时间）：

| id  | exam_id | tag  | difficulty | duration | release_time        |
| --- | ------- | ---- | ---------- | -------- | ------------------- |
| 1   | 9001    | 算法 | hard       | 60       | 2020-01-01 10:00:00 |
| 2   | 9002    | 算法 | hard       | 80       | 2020-01-01 10:00:00 |
| 3   | 9003    | SQL  | medium     | 70       | 2020-01-01 10:00:00 |

试卷作答记录表 `exam_record`（`uid` 用户 ID, `exam_id` 试卷 ID, `start_time` 开始作答时间, `submit_time` 交卷时间, `score` 得分）：

| id  | uid  | exam_id | start_time          | submit_time         | score |
| --- | ---- | ------- | ------------------- | ------------------- | ----- |
| 1   | 1001 | 9001    | 2020-01-02 09:01:01 | 2020-01-02 09:21:59 | 80    |
| 2   | 1002 | 9003    | 2020-01-20 10:01:01 | 2020-01-20 10:10:01 | 81    |
| 3   | 1002 | 9002    | 2020-01-01 12:11:01 | 2020-01-01 12:31:01 | 83    |
| 4   | 1003 | 9002    | 2020-01-01 19:01:01 | 2020-01-01 19:30:01 | 75    |
| 5   | 1004 | 9002    | 2020-01-01 12:01:01 | 2020-01-01 12:11:01 | 60    |
| 6   | 1005 | 9002    | 2020-01-01 12:01:01 | 2020-01-01 12:41:01 | 90    |
| 7   | 1006 | 9001    | 2020-01-02 19:01:01 | 2020-01-02 19:32:00 | 20    |
| 8   | 1007 | 9002    | 2020-01-02 19:01:01 | 2020-01-02 19:40:01 | 89    |
| 9   | 1008 | 9003    | 2020-01-02 12:01:01 | 2020-01-02 12:20:01 | 99    |
| 10  | 1008 | 9001    | 2020-01-02 12:01:01 | 2020-01-02 12:31:01 | 98    |
| 11  | 1009 | 9002    | 2020-01-02 12:01:01 | 2020-01-02 12:31:01 | 82    |
| 12  | 1010 | 9002    | 2020-01-02 12:11:01 | 2020-01-02 12:41:01 | 76    |
| 13  | 1011 | 9001    | 2020-01-02 10:01:01 | 2020-01-02 10:31:01 | 89    |

![](https://oss.javaguide.cn/github/javaguide/database/sql/D2B491866B85826119EE3474F10D3636.png)

找到求职方向为算法工程师，且注册当天就完成了算法类试卷的人，按参加过的所有考试最高得分排名。排名榜很长，我们将采用分页展示，每页 3 条，现在需要你取出第 3 页（页码从 1 开始）的人的信息。

由示例数据结果输出如下：

| uid  | level | register_time       | max_score |
| ---- | ----- | ------------------- | --------- |
| 1010 | 0     | 2020-01-02 11:00:00 | 76        |
| 1003 | 0     | 2020-01-01 10:00:00 | 75        |
| 1004 | 0     | 2020-01-01 11:00:00 | 60        |

解释：除了 1011 其他用户的求职方向都为算法工程师；算法类试卷有 9001 和 9002，11 个用户注册当天都完成了算法类试卷；计算他们的所有考试最大分时，只有 1002 和 1008 完成了两次考试，其他人只完成了一场考试，1002 两场考试最高分为 81，1008 最高分为 99。

按最高分排名如下：

| uid  | level | register_time       | max_score |
| ---- | ----- | ------------------- | --------- |
| 1008 | 0     | 2020-01-02 11:00:00 | 99        |
| 1005 | 7     | 2020-01-01 10:00:00 | 90        |
| 1007 | 0     | 2020-01-02 11:00:00 | 89        |
| 1002 | 3     | 2020-01-01 10:00:00 | 83        |
| 1009 | 0     | 2020-01-02 11:00:00 | 82        |
| 1001 | 0     | 2020-01-01 10:00:00 | 80        |
| 1010 | 0     | 2020-01-02 11:00:00 | 76        |
| 1003 | 0     | 2020-01-01 10:00:00 | 75        |
| 1004 | 0     | 2020-01-01 11:00:00 | 60        |
| 1006 | 0     | 2020-01-02 11:00:00 | 20        |

每页 3 条，第三页也就是第 7~9 条，返回 1010、1003、1004 的行记录即可。

**思路**：

1. 每页三条，即需要取出第三页的人的信息，要用到`limit`

2. 统计求职方向为算法工程师且注册当天就完成了算法类试卷的人的**信息和每次记录的得分**，先求满足条件的用户，后用 left join 做连接查找信息和每次记录的得分

**答案**：

```sql
SELECT t1.uid,
       LEVEL,
       register_time,
       max(score) AS max_score
FROM exam_record t
JOIN examination_info USING (exam_id)
JOIN user_info t1 ON t.uid = t1.uid
AND date(t.submit_time) = date(t1.register_time)
WHERE job = '算法'
  AND tag = '算法'
GROUP BY t1.uid,
         LEVEL,
         register_time
ORDER BY max_score DESC
LIMIT 6,3
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-05.md#L712)，来源许可：Apache-2.0。

<a id="kf9cd47ddba95"></a>

## 海量数据去重和检索为什么需要高级索引结构？

当数据规模很小时，数组遍历和哈希表已经足够；当数据达到百万、千万、亿级，内存、延迟和 IO 成本会变成主要问题。

高级索引结构解决的问题：

- 快速判断元素是否存在。
- 快速过滤不可能候选。
- 支持关键词检索。
- 支持相似向量检索。
- 降低内存占用。
- 控制查询延迟。

AIGC 系统中常见：

- 训练数据去重。
- 网页抓取 URL 去重。
- RAG 文档检索。
- 向量数据库。
- Prompt / Response 安全扫描。
- embedding cache 命中判断。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84%26%E7%AE%97%E6%B3%95%E5%9F%BA%E7%A1%80/05_%E5%AD%97%E7%AC%A6%E4%B8%B2%E4%B8%8E%E9%AB%98%E7%BA%A7%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L241)，来源许可：GPL-3.0。

<a id="k5363e07d01db"></a>

## 海量日志、文档TopK、外排序和bitmap如何支撑RAG与评测？

海量数据处理在AI系统中非常常见。比如：统计最常失败的工具、找最常触发幻觉的query、分析最高频检索文档、构建评测集、去重网页语料。

### TopK

当数据量可以分块处理时，常见方法是：

1. 按hash切分到多个小文件或分区。
2. 每个分区用哈希表统计频次。
3. 每个分区维护小根堆得到局部TopK。
4. 汇总局部TopK后再次堆排序得到全局TopK。

在AIGC服务中，可用于统计高频prompt模板、高频错误、热门知识库文档。

### 外排序

当数据无法全部放入内存时，先分块排序，再多路归并。它适合大规模日志按时间、用户、query、耗时排序，也适合离线评测结果归并。

### bitmap

bitmap用bit表示元素是否存在，适合大规模整数集合的存在性判断、去重、交并集计算。例如用户ID去重、文档ID召回覆盖率、评测样本命中率。

面试金句：海量数据题在AI工程中不是抽象算法题，而是日志分析、语料治理、RAG召回评估和系统排障的底层能力。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%95%B0%E6%8D%AE%E5%BA%93%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L179)，来源许可：GPL-3.0。

<a id="k2c4b5cc13f82"></a>

## 满足条件的用户的试卷完成数和题目练习数（困难）

**描述**：

现有用户信息表 user_info（uid 用户 ID，nick_name 昵称, achievement 成就值, level 等级, job 职业方向, register_time 注册时间）：

| id  | uid  | nick_name | achievement | level | job  | register_time       |
| --- | ---- | --------- | ----------- | ----- | ---- | ------------------- |
| 1   | 1001 | 牛客 1 号 | 3100        | 7     | 算法 | 2020-01-01 10:00:00 |
| 2   | 1002 | 牛客 2 号 | 2300        | 7     | 算法 | 2020-01-01 10:00:00 |
| 3   | 1003 | 牛客 3 号 | 2500        | 7     | 算法 | 2020-01-01 10:00:00 |
| 4   | 1004 | 牛客 4 号 | 1200        | 5     | 算法 | 2020-01-01 10:00:00 |
| 5   | 1005 | 牛客 5 号 | 1600        | 6     | C++  | 2020-01-01 10:00:00 |
| 6   | 1006 | 牛客 6 号 | 2000        | 6     | C++  | 2020-01-01 10:00:00 |

试卷信息表 examination_info（exam_id 试卷 ID, tag 试卷类别, difficulty 试卷难度, duration 考试时长, release_time 发布时间）：

| id  | exam_id | tag  | difficulty | duration | release_time        |
| --- | ------- | ---- | ---------- | -------- | ------------------- |
| 1   | 9001    | SQL  | hard       | 60       | 2021-09-01 06:00:00 |
| 2   | 9002    | C++  | hard       | 60       | 2021-09-01 06:00:00 |
| 3   | 9003    | 算法 | medium     | 80       | 2021-09-01 10:00:00 |

试卷作答记录表 exam_record（uid 用户 ID, exam_id 试卷 ID, start_time 开始作答时间, submit_time 交卷时间, score 得分）：

| id  | uid  | exam_id | start_time          | submit_time         | score |
| --- | ---- | ------- | ------------------- | ------------------- | ----- |
| 1   | 1001 | 9001    | 2021-09-01 09:01:01 | 2021-09-01 09:31:00 | 81    |
| 2   | 1002 | 9002    | 2021-09-01 12:01:01 | 2021-09-01 12:31:01 | 81    |
| 3   | 1003 | 9001    | 2021-09-01 19:01:01 | 2021-09-01 19:40:01 | 86    |
| 4   | 1003 | 9002    | 2021-09-01 12:01:01 | 2021-09-01 12:31:51 | 89    |
| 5   | 1004 | 9001    | 2021-09-01 19:01:01 | 2021-09-01 19:30:01 | 85    |
| 6   | 1005 | 9002    | 2021-09-01 12:01:01 | 2021-09-01 12:31:02 | 85    |
| 7   | 1006 | 9003    | 2021-09-07 10:01:01 | 2021-09-07 10:21:01 | 84    |
| 8   | 1006 | 9001    | 2021-09-07 10:01:01 | 2021-09-07 10:21:01 | 80    |

题目练习记录表 practice_record（uid 用户 ID, question_id 题目 ID, submit_time 提交时间, score 得分）：

| id  | uid  | question_id | submit_time         | score |
| --- | ---- | ----------- | ------------------- | ----- |
| 1   | 1001 | 8001        | 2021-08-02 11:41:01 | 60    |
| 2   | 1002 | 8001        | 2021-09-02 19:30:01 | 50    |
| 3   | 1002 | 8001        | 2021-09-02 19:20:01 | 70    |
| 4   | 1002 | 8002        | 2021-09-02 19:38:01 | 70    |
| 5   | 1004 | 8001        | 2021-08-02 19:38:01 | 70    |
| 6   | 1004 | 8002        | 2021-08-02 19:48:01 | 90    |
| 7   | 1001 | 8002        | 2021-08-02 19:38:01 | 70    |
| 8   | 1004 | 8002        | 2021-08-02 19:48:01 | 90    |
| 9   | 1004 | 8002        | 2021-08-02 19:58:01 | 94    |
| 10  | 1004 | 8003        | 2021-08-02 19:38:01 | 70    |
| 11  | 1004 | 8003        | 2021-08-02 19:48:01 | 90    |
| 12  | 1004 | 8003        | 2021-08-01 19:38:01 | 80    |

请你找到高难度 SQL 试卷得分平均值大于 80 并且是 7 级的红名大佬，统计他们的 2021 年试卷总完成次数和题目总练习次数，只保留 2021 年有试卷完成记录的用户。结果按试卷完成数升序，按题目练习数降序。

示例数据输出如下：

| uid  | exam_cnt | question_cnt |
| ---- | -------- | ------------ |
| 1001 | 1        | 2            |
| 1003 | 2        | 0            |

解释：用户 1001、1003、1004、1006 满足高难度 SQL 试卷得分平均值大于 80，但只有 1001、1003 是 7 级红名大佬；1001 完成了 1 次试卷 1001，练习了 2 次题目；1003 完成了 2 次试卷 9001、9002，未练习题目（因此计数为 0）

**思路：**

先将条件进行初步筛选，比如先查出做过高难度 sql 试卷的用户

```sql
SELECT
	record.uid
FROM
	exam_record record
	INNER JOIN examination_info e_info ON record.exam_id = e_info.exam_id
	JOIN user_info u_info ON record.uid = u_info.uid
WHERE
	e_info.tag = 'SQL'
	AND e_info.difficulty = 'hard'
```

然后根据题目要求，接着再往里叠条件即可；

但是这里又要注意：

第一：不能`YEAR(submit_time)= 2021`这个条件放到最后，要在`ON`条件里，因为左连接存在返回左表全部行，右表为 null 的情形，放在 `JOIN`条件的 `ON` 子句中的目的是为了确保在连接两个表时，只有满足年份条件的记录会进行连接。这样可以避免其他年份的记录被包含在结果中。即 1001 做过 2021 年的试卷，但没有练习过，如果把条件放到最后，就会排除掉这种情况。

第二，必须是`COUNT(distinct er.exam_id) exam_cnt, COUNT(distinct pr.id) question_cnt，`要加 distinct，因为有左连接产生很多重复值。

**答案**：

```sql
SELECT er.uid AS UID,
       count(DISTINCT er.exam_id) AS exam_cnt,
       count(DISTINCT pr.id) AS question_cnt
FROM exam_record er
LEFT JOIN practice_record pr ON er.uid = pr.uid
AND YEAR (er.submit_time)= 2021
AND YEAR (pr.submit_time)= 2021
WHERE er.uid IN
    (SELECT er.uid
     FROM exam_record er
     LEFT JOIN examination_info ei ON er.exam_id = ei.exam_id
     LEFT JOIN user_info ui ON er.uid = ui.uid
     WHERE tag = 'SQL'
       AND difficulty = 'hard'
       AND LEVEL = 7
     GROUP BY er.uid
     HAVING avg(score) > 80)
GROUP BY er.uid
ORDER BY exam_cnt,
         question_cnt DESC
```

可能细心的小伙伴会发现，为什么明明将条件限制了`tag = 'SQL' AND difficulty = 'hard'`，但是用户 1003 仍然能查出两条考试记录，其中一条的考试`tag`为 `C++`; 这是由于`LEFT JOIN`的特性，即使没有与右表匹配的行，左表的所有记录仍然会被保留。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-03.md#L1013)，来源许可：Apache-2.0。

<a id="kf767fee803b9"></a>

## 确定 Products 表中价格不超过 10 美元的最贵产品的价格

`Products` 表如下，`prod_price` 代表商品的价格。

| prod_price |
| ---------- |
| 9.49       |
| 600        |
| 1000       |

【问题】编写 SQL 语句，确定 `Products` 表中价格不超过 10 美元的最贵产品的价格（`prod_price`）。将计算所得的字段命名为 `max_price`。

```sql
SELECT Max(prod_price) AS max_price
FROM Products
WHERE prod_price <= 10
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L691)，来源许可：Apache-2.0。

<a id="k308dbf203766"></a>

## 确定哪些订单购买了 prod_id 为 BR01 的产品（一）

表 `OrderItems` 代表订单商品信息表，`prod_id` 为产品 id；`Orders` 表代表订单表有 `cust_id` 代表顾客 id 和订单日期 `order_date`

`OrderItems` 表：

| prod_id | order_num |
| ------- | --------- |
| BR01    | a0001     |
| BR01    | a0002     |
| BR02    | a0003     |
| BR02    | a0013     |

`Orders` 表：

【问题】

```sql
# 写法 1：子查询
SELECT cust_id,order_date
FROM Orders
WHERE order_num IN
    (SELECT order_num
     FROM OrderItems
     WHERE prod_id = 'BR01' )
ORDER BY order_date;

# 写法 2: 连接表
SELECT b.cust_id, b.order_date
FROM OrderItems a,Orders b
WHERE a.order_num = b.order_num AND a.prod_id = 'BR01'
ORDER BY order_date
```

**相关解释：** [确定哪些订单购买了 prod_id 为 BR01 的产品（二）](SQL%E6%9F%A5%E8%AF%A2%E4%B8%8E%E7%BB%83%E4%B9%A0-02.md#k18999d3a5b66)；[返回购买 prod_id 为 BR01 的产品的所有顾客的电子邮件（一）](SQL%E6%9F%A5%E8%AF%A2%E4%B8%8E%E7%BB%83%E4%B9%A0-03.md#k6b571b8bfc50)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L966)，来源许可：Apache-2.0。

<a id="k18999d3a5b66"></a>

## 确定哪些订单购买了 prod_id 为 BR01 的产品（二）

表 `OrderItems` 代表订单商品信息表，`prod_id` 为产品 id；`Orders` 表代表订单表有 `cust_id` 代表顾客 id 和订单日期 `order_date`

`OrderItems` 表：

| prod_id | order_num |
| ------- | --------- |
| BR01    | a0001     |
| BR01    | a0002     |
| BR02    | a0003     |
| BR02    | a0013     |

`Orders` 表：

【问题】

编写 SQL 语句，使用子查询来确定哪些订单（在 `OrderItems` 中）购买了 `prod_id` 为 "BR01" 的产品，然后从 `Orders` 表中返回每个产品对应的顾客 ID（`cust_id`）和订单日期（`order_date`），按订购日期对结果进行升序排序。

提示：这一次使用连接和简单的等连接语法。

```sql
# 写法 1：子查询
SELECT cust_id, order_date
FROM Orders
WHERE order_num IN (SELECT order_num
    FROM OrderItems
    WHERE prod_id = 'BR01')
ORDER BY order_date

# 写法 2：连接表 inner join
SELECT cust_id, order_date
FROM Orders o INNER JOIN
  (SELECT order_num
    FROM OrderItems
    WHERE prod_id = 'BR01') tb ON o.order_num = tb.order_num
ORDER BY order_date

# 写法 3：写法 2 的简化版
SELECT cust_id, order_date
FROM Orders
INNER JOIN OrderItems USING(order_num)
WHERE OrderItems.prod_id = 'BR01'
ORDER BY order_date
```

**相关解释：** [返回购买 prod_id 为 BR01 的产品的所有顾客的电子邮件（一）](SQL%E6%9F%A5%E8%AF%A2%E4%B8%8E%E7%BB%83%E4%B9%A0-03.md#k6b571b8bfc50)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L1351)，来源许可：Apache-2.0。

<a id="k0eefc0c707ed"></a>

## 确定已售出产品的总数

`OrderItems` 表代表售出的产品，`quantity` 代表售出商品数量。

| quantity |
| -------- |
| 10       |
| 100      |
| 1000     |
| 10001    |
| 2        |
| 15       |

【问题】编写 SQL 语句，确定已售出产品的总数。

```sql
SELECT Sum(quantity) AS items_ordered
FROM OrderItems
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L648)，来源许可：Apache-2.0。

<a id="k5702c12c508a"></a>

## 确定已售出产品项 BR01 的总数

`OrderItems` 表代表售出的产品，`quantity` 代表售出商品数量，产品项为 `prod_id`。

| quantity | prod_id |
| -------- | ------- |
| 10       | AR01    |
| 100      | AR10    |
| 1000     | BR01    |
| 10001    | BR010   |

【问题】修改创建的语句，确定已售出产品项（`prod_id`）为"BR01"的总数。

```sql
SELECT Sum(quantity) AS items_ordered
FROM OrderItems
WHERE prod_id = 'BR01'
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L670)，来源许可：Apache-2.0。

<a id="kdbda9732e476"></a>

## 第二快/慢用时之差大于试卷时长一半的试卷（较难）

**描述**：

现有试卷信息表 `examination_info`（`exam_id` 试卷 ID, `tag` 试卷类别, `difficulty` 试卷难度, `duration` 考试时长, `release_time` 发布时间）：

试卷作答记录表 `exam_record`（`uid` 用户 ID, `exam_id` 试卷 ID, `start_time` 开始作答时间, `submit_time` 交卷时间, `score` 得分）：

| id  | uid  | exam_id | start_time          | submit_time         | score  |
| --- | ---- | ------- | ------------------- | ------------------- | ------ |
| 1   | 1001 | 9001    | 2021-09-01 09:01:01 | 2021-09-01 09:51:01 | 78     |
| 2   | 1001 | 9002    | 2021-09-01 09:01:01 | 2021-09-01 09:31:00 | 81     |
| 3   | 1002 | 9002    | 2021-09-01 12:01:01 | 2021-09-01 12:31:01 | 81     |
| 4   | 1003 | 9001    | 2021-09-01 19:01:01 | 2021-09-01 19:59:01 | 86     |
| 5   | 1003 | 9002    | 2021-09-01 12:01:01 | 2021-09-01 12:31:51 | 89     |
| 6   | 1004 | 9002    | 2021-09-01 19:01:01 | 2021-09-01 19:30:01 | 85     |
| 7   | 1005 | 9001    | 2021-09-01 12:01:01 | 2021-09-01 12:31:02 | 85     |
| 8   | 1006 | 9001    | 2021-09-07 10:02:01 | 2021-09-07 10:21:01 | 84     |
| 9   | 1003 | 9001    | 2021-09-08 12:01:01 | 2021-09-08 12:11:01 | 40     |
| 10  | 1003 | 9002    | 2021-09-01 14:01:01 | (NULL)              | (NULL) |
| 11  | 1005 | 9001    | 2021-09-01 14:01:01 | (NULL)              | (NULL) |
| 12  | 1003 | 9003    | 2021-09-08 15:01:01 | (NULL)              | (NULL) |

找到第二快和第二慢用时之差大于试卷时长的一半的试卷信息，按试卷 ID 降序排序。由示例数据结果输出如下：

| exam_id | duration | release_time        |
| ------- | -------- | ------------------- |
| 9001    | 60       | 2021-09-01 06:00:00 |

**解释**：试卷 9001 被作答用时有 50 分钟、58 分钟、30 分 1 秒、19 分钟、10 分钟，第二快和第二慢用时之差为 50 分钟-19 分钟=31 分钟，试卷时长为 60 分钟，因此满足大于试卷时长一半的条件，输出试卷 ID、时长、发布时间。

**思路：**

第一步，找到每张试卷完成时间的顺序排名和倒序排名 也就是表 a；

第二步，与通过试卷信息表 b 建立内连接，并根据试卷 id 分组，利用`having`筛选排名为第二个数据，将秒转化为分钟并进行比较，最后再根据试卷 id 倒序排序就行

**答案**：

```sql
SELECT a.exam_id,
       b.duration,
       b.release_time
FROM
  (SELECT exam_id,
          row_number() OVER (PARTITION BY exam_id
                             ORDER BY timestampdiff(SECOND, start_time, submit_time) DESC) rn1,
          row_number() OVER (PARTITION BY exam_id
                            ORDER BY timestampdiff(SECOND, start_time, submit_time) ASC) rn2,
                                              timestampdiff(SECOND, start_time, submit_time) timex
   FROM exam_record
   WHERE score IS NOT NULL ) a
INNER JOIN examination_info b ON a.exam_id = b.exam_id
GROUP BY a.exam_id
HAVING (max(IF (rn1 = 2, a.timex, 0))- max(IF (rn2 = 2, a.timex, 0)))/ 60 > b.duration / 2
ORDER BY a.exam_id DESC
```

**相关解释：** [满足条件的用户的试卷完成数和题目练习数（困难）](SQL%E6%9F%A5%E8%AF%A2%E4%B8%8E%E7%BB%83%E4%B9%A0-02.md#k2c4b5cc13f82)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-04.md#L136)，来源许可：Apache-2.0。

<a id="kbfd82b1e6b30"></a>

## 筛选昵称规则和试卷规则的作答记录（较难）

**描述**：

现有用户信息表 `user_info`（`uid` 用户 ID，`nick_name` 昵称, `achievement` 成就值, `level` 等级, `job` 职业方向, `register_time` 注册时间）：

| id  | uid  | nick_name    | achievement | level | job  | register_time       |
| --- | ---- | ------------ | ----------- | ----- | ---- | ------------------- |
| 1   | 1001 | 牛客 1 号    | 1900        | 2     | 算法 | 2020-01-01 10:00:00 |
| 2   | 1002 | 牛客 2 号    | 1200        | 3     | 算法 | 2020-01-01 10:00:00 |
| 3   | 1003 | 牛客 3 号 ♂ | 2200        | 5     | 算法 | 2020-01-01 10:00:00 |
| 4   | 1004 | 牛客 4 号    | 2500        | 6     | 算法 | 2020-01-01 10:00:00 |
| 5   | 1005 | 牛客 555 号  | 2000        | 7     | C++  | 2020-01-01 10:00:00 |
| 6   | 1006 | 666666       | 3000        | 6     | C++  | 2020-01-01 10:00:00 |

试卷信息表 `examination_info`（`exam_id` 试卷 ID, `tag` 试卷类别, `difficulty` 试卷难度, `duration` 考试时长, `release_time` 发布时间）：

| id  | exam_id | tag | difficulty | duration | release_time        |
| --- | ------- | --- | ---------- | -------- | ------------------- |
| 1   | 9001    | C++ | hard       | 60       | 2020-01-01 10:00:00 |
| 2   | 9002    | c#  | hard       | 80       | 2020-01-01 10:00:00 |
| 3   | 9003    | SQL | medium     | 70       | 2020-01-01 10:00:00 |

试卷作答记录表 `exam_record`（`uid` 用户 ID, `exam_id` 试卷 ID, `start_time` 开始作答时间, `submit_time` 交卷时间, `score` 得分）：

| id  | uid  | exam_id | start_time          | submit_time         | score  |
| --- | ---- | ------- | ------------------- | ------------------- | ------ |
| 1   | 1001 | 9001    | 2020-01-02 09:01:01 | 2020-01-02 09:21:59 | 80     |
| 2   | 1001 | 9001    | 2021-05-02 10:01:01 | (NULL)              | (NULL) |
| 4   | 1001 | 9001    | 2021-06-02 19:01:01 | 2021-06-02 19:32:00 | 20     |
| 3   | 1001 | 9002    | 2021-02-02 19:01:01 | 2021-02-02 19:30:01 | 87     |
| 5   | 1001 | 9002    | 2021-09-05 19:01:01 | 2021-09-05 19:40:01 | 89     |
| 6   | 1001 | 9002    | 2021-09-01 12:01:01 | (NULL)              | (NULL) |
| 11  | 1002 | 9001    | 2020-01-01 12:01:01 | 2020-01-01 12:31:01 | 81     |
| 16  | 1002 | 9001    | 2021-09-06 12:01:01 | 2021-09-06 12:21:01 | 80     |
| 17  | 1002 | 9001    | 2021-09-06 12:01:01 | (NULL)              | (NULL) |
| 18  | 1002 | 9001    | 2021-09-07 12:01:01 | (NULL)              | (NULL) |
| 7   | 1002 | 9002    | 2021-05-05 18:01:01 | 2021-05-05 18:59:02 | 90     |
| 12  | 1002 | 9002    | 2020-02-01 12:01:01 | 2020-02-01 12:31:01 | 82     |
| 13  | 1002 | 9002    | 2020-02-02 12:11:01 | 2020-02-02 12:31:01 | 83     |
| 9   | 1003 | 9001    | 2021-09-07 10:01:01 | 2021-09-07 10:31:01 | 89     |
| 8   | 1003 | 9003    | 2021-02-06 12:01:01 | (NULL)              | (NULL) |
| 10  | 1004 | 9002    | 2021-08-06 12:01:01 | (NULL)              | (NULL) |
| 14  | 1005 | 9001    | 2021-02-01 11:01:01 | 2021-02-01 11:31:01 | 84     |
| 15  | 1006 | 9001    | 2021-02-01 11:01:01 | 2021-09-01 11:31:01 | 84     |

找到昵称以"牛客"+纯数字+"号"或者纯数字组成的用户对于字母 c 开头的试卷类别（如 C,C++,c#等）的已完成的试卷 ID 和平均得分，按用户 ID、平均分升序排序。由示例数据结果输出如下：

| uid  | exam_id | avg_score |
| ---- | ------- | --------- |
| 1002 | 9001    | 81        |
| 1002 | 9002    | 85        |
| 1005 | 9001    | 84        |
| 1006 | 9001    | 84        |

解释：昵称满足条件的用户有 1002、1004、1005、1006；

c 开头的试卷有 9001、9002；

满足上述条件的作答记录中，1002 完成 9001 的得分有 81、80，平均分为 81（80.5 取整四舍五入得 81）；

1002 完成 9002 的得分有 90、82、83，平均分为 85；

**思路**：

还是老样子，既然给出了条件，就先把各个条件先写出来

找到昵称以"牛客"+纯数字+"号"或者纯数字组成的用户： 我最开始是这么写的：`nick_name LIKE '牛客%号' OR nick_name REGEXP '^[0-9]+$'`，如果表中有个 “牛客 H 号” ，那也能通过。

所以这里还得用正则： `nick_name LIKE '^牛客[0-9]+号'`

对于字母 c 开头的试卷类别： `e_info.tag LIKE 'c%'` 或者 `tag regexp '^c|^C'` 第一个也能匹配到大写 C

**答案**：

```sql
SELECT UID,
       exam_id,
       ROUND(AVG(score), 0) avg_score
FROM exam_record
WHERE UID IN
    (SELECT UID
     FROM user_info
     WHERE nick_name RLIKE "^牛客[0-9]+号 $"
       OR nick_name RLIKE "^[0-9]+$")
  AND exam_id IN
    (SELECT exam_id
     FROM examination_info
     WHERE tag RLIKE "^[cC]")
  AND score IS NOT NULL
GROUP BY UID,exam_id
ORDER BY UID,avg_score;
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-05.md#L246)，来源许可：Apache-2.0。

<a id="k6e153511fda6"></a>

## 筛选限定昵称成就值活跃日期的用户（较难）

**描述**：

现有用户信息表 `user_info`（`uid` 用户 ID，`nick_name` 昵称, `achievement` 成就值, `level` 等级, `job` 职业方向, `register_time` 注册时间）：

| id  | uid  | nick_name   | achievement | level | job  | register_time       |
| --- | ---- | ----------- | ----------- | ----- | ---- | ------------------- |
| 1   | 1001 | 牛客 1 号   | 1000        | 2     | 算法 | 2020-01-01 10:00:00 |
| 2   | 1002 | 牛客 2 号   | 1200        | 3     | 算法 | 2020-01-01 10:00:00 |
| 3   | 1003 | 进击的 3 号 | 2200        | 5     | 算法 | 2020-01-01 10:00:00 |
| 4   | 1004 | 牛客 4 号   | 2500        | 6     | 算法 | 2020-01-01 10:00:00 |
| 5   | 1005 | 牛客 5 号   | 3000        | 7     | C++  | 2020-01-01 10:00:00 |

试卷作答记录表 `exam_record`（`uid` 用户 ID, `exam_id` 试卷 ID, `start_time` 开始作答时间, `submit_time` 交卷时间, `score` 得分）：

| id  | uid  | exam_id | start_time          | submit_time         | score  |
| --- | ---- | ------- | ------------------- | ------------------- | ------ |
| 1   | 1001 | 9001    | 2020-01-02 09:01:01 | 2020-01-02 09:21:59 | 80     |
| 3   | 1001 | 9002    | 2021-02-02 19:01:01 | 2021-02-02 19:30:01 | 87     |
| 2   | 1001 | 9001    | 2021-05-02 10:01:01 | (NULL)              | (NULL) |
| 4   | 1001 | 9001    | 2021-06-02 19:01:01 | 2021-06-02 19:32:00 | 20     |
| 6   | 1001 | 9002    | 2021-09-01 12:01:01 | (NULL)              | (NULL) |
| 5   | 1001 | 9002    | 2021-09-05 19:01:01 | 2021-09-05 19:40:01 | 89     |
| 11  | 1002 | 9001    | 2020-01-01 12:01:01 | 2020-01-01 12:31:01 | 81     |
| 12  | 1002 | 9002    | 2020-02-01 12:01:01 | 2020-02-01 12:31:01 | 82     |
| 13  | 1002 | 9002    | 2020-02-02 12:11:01 | 2020-02-02 12:31:01 | 83     |
| 7   | 1002 | 9002    | 2021-05-05 18:01:01 | 2021-05-05 18:59:02 | 90     |
| 16  | 1002 | 9001    | 2021-09-06 12:01:01 | 2021-09-06 12:21:01 | 80     |
| 17  | 1002 | 9001    | 2021-09-06 12:01:01 | (NULL)              | (NULL) |
| 18  | 1002 | 9001    | 2021-09-07 12:01:01 | (NULL)              | (NULL) |
| 8   | 1003 | 9003    | 2021-02-06 12:01:01 | (NULL)              | (NULL) |
| 9   | 1003 | 9001    | 2021-09-07 10:01:01 | 2021-09-07 10:31:01 | 89     |
| 10  | 1004 | 9002    | 2021-08-06 12:01:01 | (NULL)              | (NULL) |
| 14  | 1005 | 9001    | 2021-02-01 11:01:01 | 2021-02-01 11:31:01 | 84     |
| 15  | 1006 | 9001    | 2021-02-01 11:01:01 | 2021-02-01 11:31:01 | 84     |

题目练习记录表 `practice_record`（`uid` 用户 ID, `question_id` 题目 ID, `submit_time` 提交时间, `score` 得分）：

| id  | uid  | question_id | submit_time         | score |
| --- | ---- | ----------- | ------------------- | ----- |
| 1   | 1001 | 8001        | 2021-08-02 11:41:01 | 60    |
| 2   | 1002 | 8001        | 2021-09-02 19:30:01 | 50    |
| 3   | 1002 | 8001        | 2021-09-02 19:20:01 | 70    |
| 4   | 1002 | 8002        | 2021-09-02 19:38:01 | 70    |
| 5   | 1003 | 8002        | 2021-09-01 19:38:01 | 80    |

请找到昵称以『牛客』开头『号』结尾、成就值在 1200~2500 之间，且最近一次活跃（答题或作答试卷）在 2021 年 9 月的用户信息。

由示例数据结果输出如下：

| uid  | nick_name | achievement |
| ---- | --------- | ----------- |
| 1002 | 牛客 2 号 | 1200        |

**解释**：昵称以『牛客』开头『号』结尾且成就值在 1200~2500 之间的有 1002、1004；

1002 最近一次试卷区活跃为 2021 年 9 月，最近一次题目区活跃为 2021 年 9 月；1004 最近一次试卷区活跃为 2021 年 8 月，题目区未活跃。

因此最终满足条件的只有 1002。

**思路**：

先根据条件列出主要查询语句

昵称以『牛客』开头『号』结尾: `nick_name LIKE "牛客%号"`

成就值在 1200~2500 之间：`achievement BETWEEN 1200 AND 2500`

第三个条件因为限定了为 9 月，所以直接写就行：`( date_format( record.submit_time, '%Y%m' )= 202109 OR date_format( pr.submit_time, '%Y%m' )= 202109 )`

**答案**：

```sql
SELECT DISTINCT u_info.uid,
                u_info.nick_name,
                u_info.achievement
FROM user_info u_info
LEFT JOIN exam_record record ON record.uid = u_info.uid
LEFT JOIN practice_record pr ON u_info.uid = pr.uid
WHERE u_info.nick_name LIKE "牛客%号"
  AND u_info.achievement BETWEEN 1200
  AND 2500
  AND (date_format(record.submit_time, '%Y%m')= 202109
       OR date_format(pr.submit_time, '%Y%m')= 202109)
GROUP BY u_info.uid
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-05.md#L158)，来源许可：Apache-2.0。

<a id="ka0d9d84a7e67"></a>

## 级用户高难度试卷的平均用时和平均得分

**描述**：

现有用户信息表 `user_info`（`uid` 用户 ID，`nick_name` 昵称, `achievement` 成就值, `level` 等级, `job` 职业方向, `register_time` 注册时间），数据如下：

| id  | uid  | nick_name | achievement | level | job  | register_time       |
| --- | ---- | --------- | ----------- | ----- | ---- | ------------------- |
| 1   | 1001 | 牛客 1 号 | 10          | 0     | 算法 | 2020-01-01 10:00:00 |
| 2   | 1002 | 牛客 2 号 | 2100        | 6     | 算法 | 2020-01-01 10:00:00 |

试卷信息表 `examination_info`（`exam_id` 试卷 ID, `tag` 试卷类别, `difficulty` 试卷难度, `duration` 考试时长, `release_time` 发布时间），数据如下：

| id  | exam_id | tag  | difficulty | duration | release_time        |
| --- | ------- | ---- | ---------- | -------- | ------------------- |
| 1   | 9001    | SQL  | hard       | 60       | 2020-01-01 10:00:00 |
| 2   | 9002    | SQL  | easy       | 60       | 2020-01-01 10:00:00 |
| 3   | 9004    | 算法 | medium     | 80       | 2020-01-01 10:00:00 |

试卷作答记录表 `exam_record`（`uid` 用户 ID, `exam_id` 试卷 ID, `start_time` 开始作答时间, `submit_time` 交卷时间, `score` 得分），数据如下：

| id  | uid  | exam_id | start_time          | submit_time         | score  |
| --- | ---- | ------- | ------------------- | ------------------- | ------ |
| 1   | 1001 | 9001    | 2020-01-02 09:01:01 | 2020-01-02 09:21:59 | 80     |
| 2   | 1001 | 9001    | 2021-05-02 10:01:01 | (NULL)              | (NULL) |
| 3   | 1001 | 9002    | 2021-02-02 19:01:01 | 2021-02-02 19:30:01 | 87     |
| 4   | 1001 | 9001    | 2021-06-02 19:01:01 | 2021-06-02 19:32:00 | 20     |
| 5   | 1001 | 9002    | 2021-09-05 19:01:01 | 2021-09-05 19:40:01 | 89     |
| 6   | 1001 | 9002    | 2021-09-01 12:01:01 | (NULL)              | (NULL) |
| 7   | 1002 | 9002    | 2021-05-05 18:01:01 | 2021-05-05 18:59:02 | 90     |

请输出每个 0 级用户所有的高难度试卷考试平均用时和平均得分，未完成的默认试卷最大考试时长和 0 分处理。由示例数据结果输出如下：

| uid  | avg_score | avg_time_took |
| ---- | --------- | ------------- |
| 1001 | 33        | 36.7          |

解释：0 级用户有 1001，高难度试卷有 9001，1001 作答 9001 的记录有 3 条，分别用时 20 分钟、未完成（试卷时长 60 分钟）、30 分钟（未满 31 分钟），分别得分为 80 分、未完成（0 分处理）、20 分。因此他的平均用时为 110/3=36.7（保留一位小数），平均得分为 33 分（取整）

**思路**：这题用`IF`是判断的最方便的，因为涉及到 NULL 值的判断。当然 `case when`也可以，大同小异。这题的难点就在于空值的处理，其他的这些查询条件什么的，我相信难不倒大家。

**答案**：

```sql
SELECT UID,
       round(avg(new_socre)) AS avg_score,
       round(avg(time_diff), 1) AS avg_time_took
FROM
  (SELECT er.uid,
          IF (er.submit_time IS NOT NULL, TIMESTAMPDIFF(MINUTE, start_time, submit_time), ef.duration) AS time_diff,
          IF (er.submit_time IS NOT NULL,er.score,0) AS new_socre
   FROM exam_record er
   LEFT JOIN user_info uf ON er.uid = uf.uid
   LEFT JOIN examination_info ef ON er.exam_id = ef.exam_id
   WHERE uf.LEVEL = 0 AND ef.difficulty = 'hard' ) t
GROUP BY UID
ORDER BY UID
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-05.md#L97)，来源许可：Apache-2.0。

<a id="k295eb31555d7"></a>

## 组合 Products 表中的产品名称和 Customers 表中的顾客名称

`Products` 表含有字段 `prod_name` 代表产品名称

| prod_name |
| --------- |
| flower    |
| rice      |
| ring      |
| umbrella  |

Customers 表代表顾客信息，cust_name 代表顾客名称

| cust_name |
| --------- |
| andy      |
| ben       |
| tony      |
| tom       |
| an        |
| lee       |
| hex       |

【问题】编写 SQL 语句，组合 `Products` 表中的产品名称（`prod_name`）和 `Customers` 表中的顾客名称（`cust_name`）并返回，然后按产品名称对结果进行升序排序。

```sql
# UNION 结果集中的列名总是等于 UNION 中第一个 SELECT 语句中的列名。
SELECT prod_name
FROM Products
UNION
SELECT cust_name
FROM Customers
ORDER BY prod_name
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L1755)，来源许可：Apache-2.0。

<a id="kcff9b640567e"></a>

## 统计作答次数

有一个试卷作答记录表 `exam_record`，请从中统计出总作答次数 `total_pv`、试卷已完成作答数 `complete_pv`、已完成的试卷数 `complete_exam_cnt`。

示例数据 `exam_record` 表（`uid` 用户 ID, `exam_id` 试卷 ID, `start_time` 开始作答时间, `submit_time` 交卷时间, `score` 得分）：

示例输出：

| total_pv | complete_pv | complete_exam_cnt |
| -------- | ----------- | ----------------- |
| 10       | 7           | 2                 |

解释：表示截止当前，有 10 次试卷作答记录，已完成的作答次数为 7 次（中途退出的为未完成状态，其交卷时间和份数为 NULL），已完成的试卷有 9001 和 9002 两份。

**思路**： 这题一看到统计次数，肯定第一时间就要想到用`COUNT`这个函数来解决，问题是要统计不同的记录，该怎么来写？使用子查询就能解决这个题目(这题用 case when 也能写出来，解法类似，逻辑不同而已)；首先在做这个题之前，让我们先来了解一下`COUNT`的基本用法；

`COUNT()` 函数的基本语法如下所示：

```sql
COUNT(expression)
```

其中，`expression` 可以是列名、表达式、常量或通配符。下面是一些常见的用法示例：

1. 计算表中所有行的数量：

```sql
SELECT COUNT(*) FROM table_name;
```

2. 计算特定列非空（不为 NULL）值的数量：

```sql
SELECT COUNT(column_name) FROM table_name;
```

3. 计算满足条件的行数：

```sql
SELECT COUNT(*) FROM table_name WHERE condition;
```

4. 结合 `GROUP BY` 使用，计算分组后每个组的行数：

```sql
SELECT column_name, COUNT(*) FROM table_name GROUP BY column_name;
```

5. 计算不同列组合的唯一组合数：

```sql
SELECT COUNT(DISTINCT column_name1, column_name2) FROM table_name;
```

在使用 `COUNT()` 函数时，如果不指定任何参数或者使用 `COUNT(*)`，将会计算所有行的数量。而如果使用列名，则只会计算该列非空值的数量。

另外，`COUNT()` 函数的结果是一个整数值。即使结果是零，也不会返回 NULL，这点需要谨记。

**答案**：

```sql
SELECT
	count(*) total_pv,
	( SELECT count(*) FROM exam_record WHERE submit_time IS NOT NULL ) complete_pv,
	( SELECT COUNT( DISTINCT exam_id, score IS NOT NULL OR NULL ) FROM exam_record ) complete_exam_cnt
FROM
	exam_record
```

这里着重说一下`COUNT( DISTINCT exam_id, score IS NOT NULL OR NULL )`这一句，判断 score 是否为 null ，如果是即为真，如果不是返回 null；注意这里如果不加 `or null` 在不是 null 的情况下只会返回 false 也就是返回 0；

`COUNT`本身是不可以对多列求行数的，`distinct`的加入是的多列成为一个整体，可以求出现的行数了;`count distinct`在计算时只返回非 null 的行, 这个也要注意；

另外通过本题 get 到了------>count 加条件常用句式`count( 列判断 or null)`

**相关解释：** [SQL 类别高难度试卷得分的截断平均值（较难）](SQL%E6%9F%A5%E8%AF%A2%E4%B8%8E%E7%BB%83%E4%B9%A0-01.md#kd1c9a43a0b53)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-03.md#L201)，来源许可：Apache-2.0。

<a id="k849d3b991cbc"></a>

## 统计有未完成状态的试卷的未完成数和未完成率

**描述**：

现有试卷作答记录表 `exam_record`（`uid` 用户 ID, `exam_id` 试卷 ID, `start_time` 开始作答时间, `submit_time` 交卷时间, `score` 得分），数据如下：

| id  | uid  | exam_id | start_time          | submit_time         | score  |
| --- | ---- | ------- | ------------------- | ------------------- | ------ |
| 1   | 1001 | 9001    | 2020-01-02 09:01:01 | 2020-01-02 09:21:01 | 80     |
| 2   | 1001 | 9001    | 2021-05-02 10:01:01 | 2021-05-02 10:30:01 | 81     |
| 3   | 1001 | 9001    | 2021-09-02 12:01:01 | (NULL)              | (NULL) |

请统计有未完成状态的试卷的未完成数 incomplete_cnt 和未完成率 incomplete_rate。由示例数据结果输出如下：

| exam_id | incomplete_cnt | complete_rate |
| ------- | -------------- | ------------- |
| 9001    | 1              | 0.333         |

解释：试卷 9001 有 3 次被作答的记录，其中两次完成，1 次未完成，因此未完成数为 1，未完成率为 0.333（保留 3 位小数）

**思路**：

这题只需要注意一个是有条件限制，一个是没条件限制的；要么分别查询条件，然后合并；要么直接在 select 里面进行条件判断。

**答案**：

写法 1：

```sql
SELECT
    exam_id,
    (COUNT(*) - COUNT(submit_time)) AS incomplete_cnt,
    ROUND((COUNT(*) - COUNT(submit_time)) / COUNT(*), 3) AS incomplete_rate
FROM
    exam_record
GROUP BY
    exam_id
HAVING
    (COUNT(*) - COUNT(submit_time)) > 0;
```

利用 `COUNT(*)`统计分组内的总记录数，`COUNT(submit_time)` 只统计 `submit_time` 字段不为 NULL 的记录数（即已完成数）。两者相减，就是未完成数。

写法 2：

```sql
SELECT
    exam_id,
    COUNT(CASE WHEN submit_time IS NULL THEN 1 END) AS incomplete_cnt,
    ROUND(COUNT(CASE WHEN submit_time IS NULL THEN 1 END) / COUNT(*), 3) AS incomplete_rate
FROM
    exam_record
GROUP BY
    exam_id
HAVING
    COUNT(CASE WHEN submit_time IS NULL THEN 1 END) > 0;
```

使用 `CASE` 表达式，当条件满足时返回一个非 `NULL` 值（例如 1），否则返回 `NULL`。然后用 `COUNT` 函数来统计非 `NULL` 值的数量。

写法 3：

```sql
SELECT
    exam_id,
    SUM(submit_time IS NULL) AS incomplete_cnt,
    ROUND(SUM(submit_time IS NULL) / COUNT(*), 3) AS incomplete_rate
FROM
    exam_record
GROUP BY
    exam_id
HAVING
    incomplete_cnt > 0;
```

利用 `SUM` 函数对一个表达式求和。当 `submit_time` 为 `NULL` 时，表达式 `(submit_time IS NULL)` 的值为 1 (TRUE)，否则为 0 (FALSE)。将这些 1 和 0 加起来，就得到了未完成的数量。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-05.md#L20)，来源许可：Apache-2.0。

<a id="ke68b5abd7848"></a>

## 聚簇索引和非聚簇索引的区别，非聚簇索引是如何查询的？

聚簇索引就是按照每张表的主键构造一颗B+树，同时叶子节点中存放的就是整张表的行记录数据，也将聚集索引的叶子节点称为数据页。这个特性决定了索引组织表中数据也是索引的一部分，每张表只能拥有一个聚簇索引。`InnoDB` 通过主键聚集数据，如果没有定义主键，`InnoDB` 会选择非空的唯一索引代替。如果没有这样的索引，`InnoDB` 会隐式的定义一个主键来作为聚簇索引。

在聚簇索引之上创建的索引称之为辅助索引，辅助索引访问数据总是需要二次查找。辅助索引叶子节点存储的不再是行的物理位置，而是主键值。通过辅助索引首先找到的是主键值，再通过主键值找到数据行的数据页，再通过数据页中的 `Page Directory`找到数据行。`InnoDB` 辅助索引的叶子节点并不包含行记录的全部数据，叶子节点除了包含键值外，还包含了相应行数据的聚簇索引键。辅助索引的存在不影响数据在聚簇索引中的组织，所以一张表可以有多个辅助索引。在 `InnoDB` 中有时也称辅助索引为二级索引。

二级索引需要两次索引查找， 二级索引中保存的“行指针”的本质：不是物理地址的指针，而是行的主键值。所以通过二级索引查找行，引擎需要找到二级索引的子节点获得对应主键值，然后根据该值去聚簇索引找到对应行。 出现重复工作：两次B-Tree查找，而非一次。对于InnoDB，自适应哈希索引能够减少这样重复。

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/02-programming-languages/Java/java-fundamentals.md#L242)，来源许可：GPL-3.0。

<a id="k3a94d3ae6f00"></a>

## 范围查询对多列查询的影响

查询中的某个列有范围查询，则其右边所有列都无法使用索引优化查找。

举个例子，假设有一个场景需要查询本周发布的资讯文章，其中的条件是必须是启用状态，且发布时间在这周内。那么，SQL 语句可以写成：

```
select * from news where publish_time >= '2017-01-02' and publish_time <= '2017-01-08' and enable = 1
```

这种情况下，因为范围查询对多列查询的影响，将导致 news_publish_idx(publish_time, enable) 索引中 publish_time 右边所有列都无法使用索引优化查找。换句话说，news_publish_idx(publish_time, enable) 索引等价于 news_publish_idx(publish_time) 。

对于这种情况，我的建议：对于范围查询，务必要注意它带来的副作用，并且尽量少用范围查询，可以通过曲线救国的方式满足业务场景。

例如，上面案例的需求是查询本周发布的资讯文章，因此可以创建一个news_weekth 字段用来存储资讯文章的周信息，使得范围查询变成普通的查询，SQL 可以改写成：

```
select * from news where news_weekth = 1 and enable = 1

```

然而，并不是所有的范围查询都可以进行改造。

对于必须使用范围查询但无法改造的情况，我的建议：不必试图用 SQL 来解决所有问题，可以使用其他数据存储技术控制时间轴，例如 Redis 的 SortedSet 有序集合保存时间，或者通过缓存方式缓存查询结果从而提高性能。

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-01-02-MySQL.md#L420)，来源许可：Apache-2.0。
