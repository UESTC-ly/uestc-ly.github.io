# SQL查询与练习

<a id="k51614cb5112a"></a>

## 试卷发布当天作答人数和平均分

**描述**：现有用户信息表 `user_info`（`uid` 用户 ID，`nick_name` 昵称, `achievement` 成就值, `level` 等级, `job` 职业方向, `register_time` 注册时间），示例数据如下：

| id  | uid  | nick_name | achievement | level | job  | register_time       |
| --- | ---- | --------- | ----------- | ----- | ---- | ------------------- |
| 1   | 1001 | 牛客 1 号 | 3100        | 7     | 算法 | 2020-01-01 10:00:00 |
| 2   | 1002 | 牛客 2 号 | 2100        | 6     | 算法 | 2020-01-01 10:00:00 |
| 3   | 1003 | 牛客 3 号 | 1500        | 5     | 算法 | 2020-01-01 10:00:00 |
| 4   | 1004 | 牛客 4 号 | 1100        | 4     | 算法 | 2020-01-01 10:00:00 |
| 5   | 1005 | 牛客 5 号 | 1600        | 6     | C++  | 2020-01-01 10:00:00 |
| 6   | 1006 | 牛客 6 号 | 3000        | 6     | C++  | 2020-01-01 10:00:00 |

**释义**：用户 1001 昵称为牛客 1 号，成就值为 3100，用户等级是 7 级，职业方向为算法，注册时间 2020-01-01 10:00:00

试卷信息表 `examination_info`（`exam_id` 试卷 ID, `tag` 试卷类别, `difficulty` 试卷难度, `duration` 考试时长, `release_time` 发布时间） 示例数据如下：

| id  | exam_id | tag  | difficulty | duration | release_time        |
| --- | ------- | ---- | ---------- | -------- | ------------------- |
| 1   | 9001    | SQL  | hard       | 60       | 2021-09-01 06:00:00 |
| 2   | 9002    | C++  | easy       | 60       | 2020-02-01 10:00:00 |
| 3   | 9003    | 算法 | medium     | 80       | 2020-08-02 10:00:00 |

试卷作答记录表 `exam_record`（`uid` 用户 ID, `exam_id` 试卷 ID, `start_time` 开始作答时间, `submit_time` 交卷时间, `score` 得分） 示例数据如下：

| id  | uid  | exam_id | start_time          | submit_time         | score  |
| --- | ---- | ------- | ------------------- | ------------------- | ------ |
| 1   | 1001 | 9001    | 2021-07-02 09:01:01 | 2021-09-01 09:41:01 | 70     |
| 2   | 1002 | 9003    | 2021-09-01 12:01:01 | 2021-09-01 12:21:01 | 60     |
| 3   | 1002 | 9002    | 2021-09-02 12:01:01 | 2021-09-02 12:31:01 | 70     |
| 4   | 1002 | 9001    | 2021-09-01 19:01:01 | 2021-09-01 19:40:01 | 80     |
| 5   | 1002 | 9003    | 2021-08-01 12:01:01 | 2021-08-01 12:21:01 | 60     |
| 6   | 1002 | 9002    | 2021-08-02 12:01:01 | 2021-08-02 12:31:01 | 70     |
| 7   | 1002 | 9001    | 2021-09-01 19:01:01 | 2021-09-01 19:40:01 | 85     |
| 8   | 1002 | 9002    | 2021-07-06 12:01:01 | (NULL)              | (NULL) |
| 9   | 1003 | 9002    | 2021-09-07 10:01:01 | 2021-09-07 10:31:01 | 86     |
| 10  | 1003 | 9003    | 2021-09-08 12:01:01 | 2021-09-08 12:11:01 | 40     |
| 11  | 1003 | 9003    | 2021-09-01 13:01:01 | 2021-09-01 13:41:01 | 70     |
| 12  | 1003 | 9001    | 2021-09-08 14:01:01 | (NULL)              | (NULL) |
| 13  | 1003 | 9002    | 2021-09-08 15:01:01 | (NULL)              | (NULL) |
| 14  | 1005 | 9001    | 2021-09-01 12:01:01 | 2021-09-01 12:31:01 | 90     |
| 15  | 1005 | 9002    | 2021-09-01 12:01:01 | 2021-09-01 12:31:01 | 88     |
| 16  | 1005 | 9002    | 2021-09-02 12:11:01 | 2021-09-02 12:31:01 | 89     |

请计算每张 SQL 类别试卷发布后，当天 5 级以上的用户作答的人数 `uv` 和平均分 `avg_score`，按人数降序，相同人数的按平均分升序，示例数据结果输出如下：

| exam_id | uv  | avg_score |
| ------- | --- | --------- |
| 9001    | 3   | 81.3      |

解释：只有一张 SQL 类别的试卷，试卷 ID 为 9001，发布当天（2021-09-01）有 1001、1002、1003、1005 作答过，但是 1003 是 5 级用户，其他 3 位为 5 级以上，他们三的得分有[70,80,85,90]，平均分为 81.3（保留 1 位小数）。

**思路**：这题看似很复杂，但是先逐步将“外边”条件拆分，然后合拢到一起，答案就出来，多表查询反正记住：由外向里，抽丝剥茧。

先把三种表连起来，同时给定一些条件，比如题目中要求`等级> 5`的用户，那么可以先查出来

```sql
SELECT DISTINCT u_info.uid
FROM examination_info e_info
INNER JOIN exam_record record
INNER JOIN user_info u_info
WHERE e_info.exam_id = record.exam_id
  AND u_info.uid = record.uid
  AND u_info.LEVEL > 5
```

接着注意题目中要求：`每张sql类别试卷发布后，当天作答用户`，注意其中的==当天==，那我们马上就要想到要用到时间的比较。

对试卷发布日期和开始考试日期进行比较：`DATE(e_info.release_time) = DATE(record.start_time)`；不用担心`submit_time` 为 null 的问题，后续在 where 中会给过滤掉。

**答案**：

```sql
SELECT record.exam_id AS exam_id,
       COUNT(DISTINCT u_info.uid) AS uv,
       ROUND(SUM(record.score) / COUNT(u_info.uid), 1) AS avg_score
FROM examination_info e_info
INNER JOIN exam_record record
INNER JOIN user_info u_info
WHERE e_info.exam_id = record.exam_id
  AND u_info.uid = record.uid
  AND DATE (e_info.release_time) = DATE (record.start_time)
  AND submit_time IS NOT NULL
  AND tag = 'SQL'
  AND u_info.LEVEL > 5
GROUP BY record.exam_id
ORDER BY uv DESC,
         avg_score ASC
```

注意最后的分组排序！先按人数排，若一致，按平均分排。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-03.md#L662)，来源许可：Apache-2.0。

<a id="kd4238799c93b"></a>

## 试卷完成数同比 2020 年的增长率及排名变化（困难）

**描述**：

现有试卷信息表 `examination_info`（`exam_id` 试卷 ID, `tag` 试卷类别, `difficulty` 试卷难度, `duration` 考试时长, `release_time` 发布时间）：

| id  | exam_id | tag    | difficulty | duration | release_time        |
| --- | ------- | ------ | ---------- | -------- | ------------------- |
| 1   | 9001    | SQL    | hard       | 60       | 2021-01-01 10:00:00 |
| 2   | 9002    | C++    | hard       | 80       | 2021-01-01 10:00:00 |
| 3   | 9003    | 算法   | hard       | 80       | 2021-01-01 10:00:00 |
| 4   | 9004    | PYTHON | medium     | 70       | 2021-01-01 10:00:00 |

试卷作答记录表 `exam_record`（`uid` 用户 ID, `exam_id` 试卷 ID, `start_time` 开始作答时间, `submit_time` 交卷时间, `score` 得分）：

| id  | uid  | exam_id | start_time          | submit_time         | score |
| --- | ---- | ------- | ------------------- | ------------------- | ----- |
| 1   | 1001 | 9001    | 2020-08-02 10:01:01 | 2020-08-02 10:31:01 | 89    |
| 2   | 1002 | 9001    | 2020-04-01 18:01:01 | 2020-04-01 18:59:02 | 90    |
| 3   | 1001 | 9001    | 2020-04-01 09:01:01 | 2020-04-01 09:21:59 | 80    |
| 5   | 1002 | 9001    | 2021-03-02 19:01:01 | 2021-03-02 19:32:00 | 20    |
| 8   | 1003 | 9001    | 2021-05-02 12:01:01 | 2021-05-02 12:31:01 | 98    |
| 13  | 1003 | 9001    | 2020-01-02 10:01:01 | 2020-01-02 10:31:01 | 89    |
| 9   | 1001 | 9002    | 2020-02-02 12:01:01 | 2020-02-02 12:20:01 | 99    |
| 10  | 1002 | 9002    | 2021-02-02 12:01:01 | 2020-02-02 12:43:01 | 81    |
| 11  | 1001 | 9002    | 2020-01-02 19:01:01 | 2020-01-02 19:59:01 | 69    |
| 16  | 1002 | 9002    | 2020-02-02 12:01:01 |                     |       |
| 17  | 1002 | 9002    | 2020-03-02 12:11:01 |                     |       |
| 18  | 1001 | 9002    | 2021-05-05 18:01:01 |                     |       |
| 4   | 1002 | 9003    | 2021-01-20 10:01:01 | 2021-01-20 10:10:01 | 81    |
| 6   | 1001 | 9003    | 2021-04-02 19:01:01 | 2021-04-02 19:40:01 | 89    |
| 15  | 1002 | 9003    | 2021-01-01 18:01:01 | 2021-01-01 18:59:02 | 90    |
| 7   | 1004 | 9004    | 2020-05-02 12:01:01 | 2020-05-02 12:20:01 | 99    |
| 12  | 1001 | 9004    | 2021-09-02 12:11:01 |                     |       |
| 14  | 1002 | 9004    | 2020-01-01 12:11:01 | 2020-01-01 12:31:01 | 83    |

请计算 2021 年上半年各类试卷的做完次数相比 2020 年上半年同期的增长率（百分比格式，保留 1 位小数），以及做完次数排名变化，按增长率和 21 年排名降序输出。

由示例数据结果输出如下：

| tag | exam_cnt_20 | exam_cnt_21 | growth_rate | exam_cnt_rank_20 | exam_cnt_rank_21 | rank_delta |
| --- | ----------- | ----------- | ----------- | ---------------- | ---------------- | ---------- |
| SQL | 3           | 2           | -33.3%      | 1                | 2                | 1          |

解释：2020 年上半年有 3 个 tag 有作答完成的记录，分别是 C++、SQL、PYTHON，它们被做完的次数分别是 3、3、2，做完次数排名为 1、1（并列）、3；

2021 年上半年有 2 个 tag 有作答完成的记录，分别是算法、SQL，它们被做完的次数分别是 3、2，做完次数排名为 1、2；具体如下：

| tag    | start_year | exam_cnt | exam_cnt_rank |
| ------ | ---------- | -------- | ------------- |
| C++    | 2020       | 3        | 1             |
| SQL    | 2020       | 3        | 1             |
| PYTHON | 2020       | 2        | 3             |
| 算法   | 2021       | 3        | 1             |
| SQL    | 2021       | 2        | 2             |

因此能输出同比结果的 tag 只有 SQL，从 2020 到 2021 年，做完次数 3=>2，减少 33.3%（保留 1 位小数）；排名 1=>2，后退 1 名。

**思路：**

本题难点在于长整型的数据类型要求不能有负号产生，用 cast 函数转换数据类型为 signed。

以及用到的`增长率计算公式：(exam_cnt_21-exam_cnt_20)/exam_cnt_20`

做完次数排名变化（2021 年和 2020 年比排名升了或者降了多少）

计算公式：`exam_cnt_rank_21 - exam_cnt_rank_20`

在 MySQL 中，`CAST()` 函数用于将一个表达式的数据类型转换为另一个数据类型。它的基本语法如下：

```sql
CAST(expression AS data_type)

-- 将一个字符串转换成整数
SELECT CAST('123' AS INT);
```

示例就不一一举例了，这个函数很简单

**答案**：

```sql
SELECT
  tag,
  exam_cnt_20,
  exam_cnt_21,
  concat(
    round(
      100 * (exam_cnt_21 - exam_cnt_20) / exam_cnt_20,
      1
    ),
    '%'
  ) AS growth_rate,
  exam_cnt_rank_20,
  exam_cnt_rank_21,
  cast(exam_cnt_rank_21 AS signed) - cast(exam_cnt_rank_20 AS signed) AS rank_delta
FROM
  (
    #2020年、2021年上半年各类试卷的做完次数和做完次数排名
    SELECT
      tag,
      count(
        IF (
          date_format(start_time, '%Y%m%d') BETWEEN '20200101'
          AND '20200630',
          start_time,
          NULL
        )
      ) AS exam_cnt_20,
      count(
        IF (
          substring(start_time, 1, 10) BETWEEN '2021-01-01'
          AND '2021-06-30',
          start_time,
          NULL
        )
      ) AS exam_cnt_21,
      rank() over (
        ORDER BY
          count(
            IF (
              date_format(start_time, '%Y%m%d') BETWEEN '20200101'
              AND '20200630',
              start_time,
              NULL
            )
          ) DESC
      ) AS exam_cnt_rank_20,
      rank() over (
        ORDER BY
          count(
            IF (
              substring(start_time, 1, 10) BETWEEN '2021-01-01'
              AND '2021-06-30',
              start_time,
              NULL
            )
          ) DESC
      ) AS exam_cnt_rank_21
    FROM
      examination_info
      JOIN exam_record USING (exam_id)
    WHERE
      submit_time IS NOT NULL
    GROUP BY
      tag
  ) main
WHERE
  exam_cnt_21 * exam_cnt_20 <> 0
ORDER BY
  growth_rate DESC,
  exam_cnt_rank_21 DESC
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-04.md#L436)，来源许可：Apache-2.0。

<a id="kb74287e80184"></a>

## 近三个月未完成为 0 的用户完成情况

**描述**：

现有试卷作答记录表 `exam_record`（`uid`:用户 ID, `exam_id`:试卷 ID, `start_time`:开始作答时间, `submit_time`:交卷时间，为空的话则代表未完成, `score`:得分）：

| id  | uid  | exam_id | start_time          | submit_time         | score  |
| --- | ---- | ------- | ------------------- | ------------------- | ------ |
| 1   | 1006 | 9003    | 2021-09-06 10:01:01 | 2021-09-06 10:21:02 | 84     |
| 2   | 1006 | 9001    | 2021-08-02 12:11:01 | 2021-08-02 12:31:01 | 89     |
| 3   | 1006 | 9002    | 2021-06-06 10:01:01 | 2021-06-06 10:21:01 | 81     |
| 4   | 1006 | 9002    | 2021-05-06 10:01:01 | 2021-05-06 10:21:01 | 81     |
| 5   | 1006 | 9001    | 2021-05-01 12:01:01 | (NULL)              | (NULL) |
| 6   | 1001 | 9001    | 2021-09-05 10:31:01 | 2021-09-05 10:51:01 | 81     |
| 7   | 1001 | 9003    | 2021-08-01 09:01:01 | 2021-08-01 09:51:11 | 78     |
| 8   | 1001 | 9002    | 2021-07-01 09:01:01 | 2021-07-01 09:31:00 | 81     |
| 9   | 1001 | 9002    | 2021-07-01 12:01:01 | 2021-07-01 12:31:01 | 81     |
| 10  | 1001 | 9002    | 2021-07-01 12:01:01 | (NULL)              | (NULL) |

找到每个人近三个有试卷作答记录的月份中没有试卷是未完成状态的用户的试卷作答完成数，按试卷完成数和用户 ID 降序排名。由示例数据结果输出如下：

| uid  | exam_complete_cnt |
| ---- | ----------------- |
| 1006 | 3                 |

**解释**：用户 1006 近三个有作答试卷的月份为 202109、202108、202106，作答试卷数为 3，全部完成；用户 1001 近三个有作答试卷的月份为 202109、202108、202107，作答试卷数为 5，完成试卷数为 4，因为有未完成试卷，故过滤掉。

**思路:**

1. `找到每个人近三个有试卷作答记录的月份中没有试卷是未完成状态的用户的试卷作答完成数`首先看这句话，肯定要先根据人进行分组
2. 最近三个月，可以采用连续重复排名，倒序排列，排名<=3
3. 统计作答数
4. 拼装剩余条件
5. 排序

**答案**：

```sql
SELECT UID,
       count(score) exam_complete_cnt
FROM
  (SELECT *, DENSE_RANK() OVER (PARTITION BY UID
                             ORDER BY date_format(start_time, '%Y%m') DESC) dr
   FROM exam_record) t1
WHERE dr <= 3
GROUP BY UID
HAVING count(dr)= count(score)
ORDER BY exam_complete_cnt DESC,
         UID DESC
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-04.md#L247)，来源许可：Apache-2.0。

<a id="kd4f106e9a95e"></a>

## 返回 2020 年 1 月的所有订单的订单号和订单日期

`Orders` 订单表如下：

| order_num | order_date          |
| --------- | ------------------- |
| a0001     | 2020-01-01 00:00:00 |
| a0002     | 2020-01-02 00:00:00 |
| a0003     | 2020-01-01 12:00:00 |
| a0004     | 2020-02-01 00:00:00 |
| a0005     | 2020-03-01 00:00:00 |

【问题】编写 SQL 语句，返回 2020 年 1 月的所有订单的订单号（`order_num`）和订单日期（`order_date`），并按订单日期升序排序

```sql
SELECT order_num, order_date
FROM Orders
WHERE month(order_date) = '01' AND YEAR(order_date) = '2020'
ORDER BY order_date
```

也可以用通配符来做：

```sql
SELECT order_num, order_date
FROM Orders
WHERE order_date LIKE '2020-01%'
ORDER BY order_date
```

知识点：

- 日期格式：`YYYY-MM-DD`
- 时间格式：`HH:MM:SS`

日期和时间处理相关的常用函数：

| 函 数           | 说 明                          |
| --------------- | ------------------------------ |
| `ADDDATE()`     | 增加一个日期（天、周等）       |
| `ADDTIME()`     | 增加一个时间（时、分等）       |
| `CURDATE()`     | 返回当前日期                   |
| `CURTIME()`     | 返回当前时间                   |
| `DATE()`        | 返回日期时间的日期部分         |
| `DATEDIFF`      | 计算两个日期之差               |
| `DATE_FORMAT()` | 返回一个格式化的日期或时间串   |
| `DAY()`         | 返回一个日期的天数部分         |
| `DAYOFWEEK()`   | 对于一个日期，返回对应的星期几 |
| `HOUR()`        | 返回一个时间的小时部分         |
| `MINUTE()`      | 返回一个时间的分钟部分         |
| `MONTH()`       | 返回一个日期的月份部分         |
| `NOW()`         | 返回当前日期和时间             |
| `SECOND()`      | 返回一个时间的秒部分           |
| `TIME()`        | 返回一个日期时间的时间部分     |
| `YEAR()`        | 返回一个日期的年份部分         |

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L578)，来源许可：Apache-2.0。

<a id="kda4a5dcb3456"></a>

## 返回产品名称和与之相关的订单号

`Products` 表为产品信息表含有字段 `prod_id` 产品 id、`prod_name` 产品名称

`OrderItems` 表为订单信息表含有字段 `order_num` 订单号和产品 id `prod_id`

【问题】使用外连接（left join、 right join、full join）联结 `Products` 表和 `OrderItems` 表，返回产品名称（`prod_name`）和与之相关的订单号（`order_num`）的列表，并按照产品名称升序排序。

```sql
SELECT prod_name, order_num
FROM Products
LEFT JOIN OrderItems
USING(prod_id)
ORDER BY prod_name
```

**相关解释：** [返回产品名称和每一项产品的总订单数](SQL%E6%9F%A5%E8%AF%A2%E4%B8%8E%E7%BB%83%E4%B9%A0-03.md#k27aee249c7cb)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L1567)，来源许可：Apache-2.0。

<a id="k27aee249c7cb"></a>

## 返回产品名称和每一项产品的总订单数

`Products` 表为产品信息表含有字段 `prod_id` 产品 id、`prod_name` 产品名称

| prod_id | prod_name |
| ------- | --------- |
| a0001   | egg       |
| a0002   | sockets   |
| a0013   | coffee    |
| a0003   | cola      |
| a0023   | soda      |

`OrderItems` 表为订单信息表含有字段 `order_num` 订单号和产品 id `prod_id`

| prod_id | order_num |
| ------- | --------- |
| a0001   | a105      |
| a0002   | a1100     |
| a0002   | a200      |
| a0013   | a1121     |
| a0003   | a10       |
| a0003   | a19       |
| a0003   | a5        |

【问题】

使用 OUTER JOIN 联结 `Products` 表和 `OrderItems` 表，返回产品名称（`prod_name`）和每一项产品的总订单数（不是订单号），并按产品名称升序排序。

```sql
SELECT prod_name, COUNT(order_num) AS orders
FROM Products
LEFT JOIN OrderItems
USING(prod_id)
GROUP BY prod_name
ORDER BY prod_name
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L1601)，来源许可：Apache-2.0。

<a id="k6eae3bcf98e1"></a>

## 返回产品并且按照价格排序

有表 `Products`：

| prod_id | prod_name | prod_price |
| ------- | --------- | ---------- |
| a0011   | egg       | 3          |
| a0019   | sockets   | 4          |
| b0019   | coffee    | 15         |

【问题】编写 SQL 语句，返回 `Products` 表中所有价格在 3 美元到 6 美元之间的产品的名称（`prod_name`）和价格（`prod_price`），然后按价格对结果进行排序。

```sql
SELECT prod_name, prod_price
FROM Products
WHERE prod_price BETWEEN 3 AND 6
ORDER BY prod_price

# 或者
SELECT prod_name, prod_price
FROM Products
WHERE prod_price >= 3 AND prod_price <= 6
ORDER BY prod_price
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L249)，来源许可：Apache-2.0。

<a id="k493089109c8c"></a>

## 返回固定价格的产品

有表 `Products`：

| prod_id | prod_name      | prod_price |
| ------- | -------------- | ---------- |
| a0018   | sockets        | 9.49       |
| a0019   | iphone13       | 600        |
| b0018   | gucci t-shirts | 1000       |

【问题】从 `Products` 表中检索产品 ID（`prod_id`）和产品名称（`prod_name`），只返回价格为 9.49 美元的产品。

```sql
SELECT prod_id, prod_name
FROM Products
WHERE prod_price = 9.49
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L209)，来源许可：Apache-2.0。

<a id="k29f4d4de175a"></a>

## 返回所有价格在 3 美元到 6 美元之间的产品的名称和价格

有表 `Products`：

【问题】编写 SQL 语句，返回所有价格在 3 美元到 6 美元之间的产品的名称（`prod_name`）和价格（`prod_price`），使用 AND 操作符，然后按价格对结果进行升序排序。

```sql
SELECT prod_name, prod_price
FROM Products
WHERE prod_price >= 3 and prod_price <= 6
ORDER BY prod_price
```

**相关解释：** [返回产品并且按照价格排序](SQL%E6%9F%A5%E8%AF%A2%E4%B8%8E%E7%BB%83%E4%B9%A0-03.md#k6eae3bcf98e1)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L349)，来源许可：Apache-2.0。

<a id="k5c041eef75b5"></a>

## 返回更多的产品

`OrderItems` 表含有：订单号 `order_num`，`quantity`产品数量

| order_num | quantity |
| --------- | -------- |
| a1        | 105      |
| a2        | 1100     |
| a2        | 200      |
| a4        | 1121     |
| a5        | 10       |
| a2        | 19       |
| a7        | 5        |

【问题】从 `OrderItems` 表中检索出所有不同且不重复的订单号（`order_num`），其中每个订单都要包含 100 个或更多的产品。

```sql
SELECT order_num
FROM OrderItems
GROUP BY order_num
HAVING SUM(quantity) >= 100
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L276)，来源许可：Apache-2.0。

<a id="kf90fc0dfc0f4"></a>

## 返回更高价格的产品

有表 `Products`：

| prod_id | prod_name      | prod_price |
| ------- | -------------- | ---------- |
| a0018   | sockets        | 9.49       |
| a0019   | iphone13       | 600        |
| b0019   | gucci t-shirts | 1000       |

【问题】编写 SQL 语句，从 `Products` 表中检索产品 ID（`prod_id`）和产品名称（`prod_name`），只返回价格为 9 美元或更高的产品。

```sql
SELECT prod_id, prod_name
FROM Products
WHERE prod_price >= 9
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L229)，来源许可：Apache-2.0。

<a id="k725afbed755a"></a>

## 返回每个订单号各有多少行数

`OrderItems` 表包含每个订单的每个产品

| order_num |
| --------- |
| a002      |
| a002      |
| a002      |
| a004      |
| a007      |

【问题】编写 SQL 语句，返回每个订单号（`order_num`）各有多少行数（`order_lines`），并按 `order_lines` 对结果进行升序排序。

```sql
SELECT order_num, Count(order_num) AS order_lines
FROM OrderItems
GROUP BY order_num
ORDER BY order_lines
```

知识点：

1. `count(*)`,`count(列名)`都可以，区别在于，`count(列名)`是统计非 NULL 的行数；
2. `order by` 最后执行，所以可以使用列别名；
3. 分组聚合一定不要忘记加上 `group by` ,不然只会有一行结果。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L732)，来源许可：Apache-2.0。

<a id="k819aa2182939"></a>

## 返回每个顾客不同订单的总金额

我们需要一个顾客 ID 列表，其中包含他们已订购的总金额。

`OrderItems` 表代表订单信息，`OrderItems` 表有订单号：`order_num` 和商品售出价格：`item_price`、商品数量：`quantity`。

| order_num | item_price | quantity |
| --------- | ---------- | -------- |
| a0001     | 10         | 105      |
| a0002     | 1          | 1100     |
| a0002     | 1          | 200      |
| a0013     | 2          | 1121     |
| a0003     | 5          | 10       |
| a0003     | 1          | 19       |
| a0003     | 7          | 5        |

`Orders` 表订单号：`order_num`、顾客 id：`cust_id`

| order_num | cust_id |
| --------- | ------- |
| a0001     | cust10  |
| a0002     | cust1   |
| a0003     | cust1   |
| a0013     | cust2   |

【问题】

编写 SQL 语句，返回顾客 ID（`Orders` 表中的 `cust_id`），并使用子查询返回 `total_ordered` 以便返回每个顾客的订单总数，将结果按金额从大到小排序。

```sql
# 写法 1：子查询
SELECT o.cust_id, SUM(tb.total_ordered) AS `total_ordered`
FROM (SELECT order_num, SUM(item_price * quantity) AS total_ordered
    FROM OrderItems
    GROUP BY order_num) AS tb,
  Orders o
WHERE tb.order_num = o.order_num
GROUP BY o.cust_id
ORDER BY total_ordered DESC;

# 写法 2：连接表
SELECT b.cust_id, Sum(a.quantity * a.item_price) AS total_ordered
FROM OrderItems a,Orders b
WHERE a.order_num = b.order_num
GROUP BY cust_id
ORDER BY total_ordered DESC
```

关于写法一详细介绍可以参考： [issue#2402：写法 1 存在的错误以及修改方法](https://github.com/Snailclimb/JavaGuide/issues/2402)。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L1070)，来源许可：Apache-2.0。

<a id="k6d69a6bd007a"></a>

## 返回订单数量总和不小于 100 的所有订单的订单号

`OrderItems` 代表订单商品表，包括：订单号 `order_num` 和订单数量 `quantity`。

| order_num | quantity |
| --------- | -------- |
| a1        | 105      |
| a2        | 1100     |
| a2        | 200      |
| a4        | 1121     |
| a5        | 10       |
| a2        | 19       |
| a7        | 5        |

【问题】请编写 SQL 语句，返回订单数量总和不小于 100 的所有订单号，最后结果按照订单号升序排序。

```sql
# 直接聚合
SELECT order_num
FROM OrderItems
GROUP BY order_num
HAVING Sum(quantity) >= 100
ORDER BY order_num

# 子查询
SELECT a.order_num
FROM (SELECT order_num, Sum(quantity) AS sum_num
    FROM OrderItems
    GROUP BY order_num
    HAVING sum_num >= 100) a
ORDER BY a.order_num
```

知识点：

- `where`：过滤过滤指定的行，后面不能加聚合函数（分组函数）。
- `having`：过滤分组，与 `group by` 连用，不能单独使用。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L784)，来源许可：Apache-2.0。

<a id="k6b571b8bfc50"></a>

## 返回购买 prod_id 为 BR01 的产品的所有顾客的电子邮件（一）

你想知道订购 BR01 产品的日期，有表 `OrderItems` 代表订单商品信息表，`prod_id` 为产品 id；`Orders` 表代表订单表有 `cust_id` 代表顾客 id 和订单日期 `order_date`；`Customers` 表含有 `cust_email` 顾客邮件和 `cust_id` 顾客 id

`OrderItems` 表：

| prod_id | order_num |
| ------- | --------- |
| BR01    | a0001     |
| BR01    | a0002     |
| BR02    | a0003     |
| BR02    | a0013     |

`Orders` 表：

| order_num | cust_id | order_date          |
| --------- | ------- | ------------------- |
| a0001     | cust10  | 2022-01-01 00:00:00 |
| a0002     | cust1   | 2022-01-01 00:01:00 |
| a0003     | cust1   | 2022-01-02 00:00:00 |
| a0013     | cust2   | 2022-01-01 00:20:00 |

`Customers` 表代表顾客信息，`cust_id` 为顾客 id，`cust_email` 为顾客 email

| cust_id | cust_email        |
| ------- | ----------------- |
| cust10  | <cust10@cust.com> |
| cust1   | <cust1@cust.com>  |
| cust2   | <cust2@cust.com>  |

【问题】返回购买 `prod_id` 为 `BR01` 的产品的所有顾客的电子邮件（`Customers` 表中的 `cust_email`），结果无需排序。

提示：这涉及 `SELECT` 语句，最内层的从 `OrderItems` 表返回 `order_num`，中间的从 `Customers` 表返回 `cust_id`。

```sql
# 写法 1：子查询
SELECT cust_email
FROM Customers
WHERE cust_id IN (SELECT cust_id
    FROM Orders
    WHERE order_num IN (SELECT order_num
        FROM OrderItems
        WHERE prod_id = 'BR01'))

# 写法 2: 连接表（inner join）
SELECT c.cust_email
FROM OrderItems a,Orders b,Customers c
WHERE a.order_num = b.order_num AND b.cust_id = c.cust_id AND a.prod_id = 'BR01'

# 写法 3：连接表（left join）
SELECT c.cust_email
FROM Orders a LEFT JOIN
  OrderItems b ON a.order_num = b.order_num LEFT JOIN
  Customers c ON a.cust_id = c.cust_id
WHERE b.prod_id = 'BR01'
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L1011)，来源许可：Apache-2.0。

<a id="k627e774884c7"></a>

## 返回购买 prod_id 为 BR01 的产品的所有顾客的电子邮件（二）

有表 `OrderItems` 代表订单商品信息表，`prod_id` 为产品 id；`Orders` 表代表订单表有 `cust_id` 代表顾客 id 和订单日期 `order_date`；`Customers` 表含有 `cust_email` 顾客邮件和 cust_id 顾客 id

`OrderItems` 表：

| prod_id | order_num |
| ------- | --------- |
| BR01    | a0001     |
| BR01    | a0002     |
| BR02    | a0003     |
| BR02    | a0013     |

`Orders` 表：

`Customers` 表代表顾客信息，`cust_id` 为顾客 id，`cust_email` 为顾客 email

【问题】返回购买 `prod_id` 为 BR01 的产品的所有顾客的电子邮件（`Customers` 表中的 `cust_email`），结果无需排序。

提示：涉及到 `SELECT` 语句，最内层的从 `OrderItems` 表返回 `order_num`，中间的从 `Customers` 表返回 `cust_id`，但是必须使用 INNER JOIN 语法。

```sql
SELECT cust_email
FROM Customers
INNER JOIN Orders using(cust_id)
INNER JOIN OrderItems using(order_num)
WHERE OrderItems.prod_id = 'BR01'
```

**相关解释：** [返回购买 prod_id 为 BR01 的产品的所有顾客的电子邮件（一）](SQL%E6%9F%A5%E8%AF%A2%E4%B8%8E%E7%BB%83%E4%B9%A0-03.md#k6b571b8bfc50)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L1404)，来源许可：Apache-2.0。

<a id="k6edad8a99b02"></a>

## 返回购买价格为 10 美元或以上产品的顾客列表

`OrderItems` 表示订单商品表，含有字段订单号：`order_num`、订单价格：`item_price`；`Orders` 表代表订单信息表，含有顾客 `id：cust_id` 和订单号：`order_num`

`OrderItems` 表:

| order_num | item_price |
| --------- | ---------- |
| a1        | 10         |
| a2        | 1          |
| a2        | 1          |
| a4        | 2          |
| a5        | 5          |
| a2        | 1          |
| a7        | 7          |

`Orders` 表：

| order_num | cust_id |
| --------- | ------- |
| a1        | cust10  |
| a2        | cust1   |
| a2        | cust1   |
| a4        | cust2   |
| a5        | cust5   |
| a2        | cust1   |
| a7        | cust7   |

【问题】使用子查询，返回购买价格为 10 美元或以上产品的顾客列表，结果无需排序。

```sql
SELECT cust_id
FROM Orders
WHERE order_num IN (SELECT DISTINCT order_num
    FROM OrderItems
    where item_price >= 10)
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L926)，来源许可：Apache-2.0。

<a id="k2ea46c40196a"></a>

## 返回顾客名称和相关订单号

`Customers` 表有字段顾客名称 `cust_name`、顾客 id `cust_id`

`Orders` 订单信息表，含有字段 `order_num` 订单号、`cust_id` 顾客 id

【问题】编写 SQL 语句，返回 `Customers` 表中的顾客名称（`cust_name`）和 `Orders` 表中的相关订单号（`order_num`），并按顾客名称再按订单号对结果进行升序排序。你可以尝试用两个不同的写法，一个使用简单的等连接语法，另外一个使用 INNER JOIN。

```sql
# 隐式内连接
SELECT c.cust_name, o.order_num
FROM Customers c,Orders o
WHERE c.cust_id = o.cust_id
ORDER BY c.cust_name,o.order_num

# 显式内连接
SELECT c.cust_name, o.order_num
FROM Customers c
INNER JOIN Orders o
USING(cust_id)
ORDER BY c.cust_name,o.order_num;
```

**相关解释：** [返回顾客名称和相关订单号以及每个订单的总价](SQL%E6%9F%A5%E8%AF%A2%E4%B8%8E%E7%BB%83%E4%B9%A0-03.md#k48316d2abd47)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L1246)，来源许可：Apache-2.0。

<a id="k48316d2abd47"></a>

## 返回顾客名称和相关订单号以及每个订单的总价

`Customers` 表有字段，顾客名称：`cust_name`、顾客 id：`cust_id`

| cust_id  | cust_name |
| -------- | --------- |
| cust10   | andy      |
| cust1    | ben       |
| cust2    | tony      |
| cust22   | tom       |
| cust221  | an        |
| cust2217 | hex       |

`Orders` 订单信息表，含有字段，订单号：`order_num`、顾客 id：`cust_id`

| order_num | cust_id  |
| --------- | -------- |
| a1        | cust10   |
| a2        | cust1    |
| a3        | cust2    |
| a4        | cust22   |
| a5        | cust221  |
| a7        | cust2217 |

`OrderItems` 表有字段，商品订单号：`order_num`、商品数量：`quantity`、商品价格：`item_price`

| order_num | quantity | item_price |
| --------- | -------- | ---------- |
| a1        | 1000     | 10         |
| a2        | 200      | 10         |
| a3        | 10       | 15         |
| a4        | 25       | 50         |
| a5        | 15       | 25         |
| a7        | 7        | 7          |

【问题】除了返回顾客名称和订单号，返回 `Customers` 表中的顾客名称（`cust_name`）和 `Orders` 表中的相关订单号（`order_num`），添加第三列 `OrderTotal`，其中包含每个订单的总价，并按顾客名称再按订单号对结果进行升序排序。

```sql
# 简单的等连接语法
SELECT c.cust_name, o.order_num, SUM(quantity * item_price) AS OrderTotal
FROM Customers c,Orders o,OrderItems oi
WHERE c.cust_id = o.cust_id AND o.order_num = oi.order_num
GROUP BY c.cust_name, o.order_num
ORDER BY c.cust_name, o.order_num
```

注意，可能有小伙伴会这样写：

```sql
SELECT c.cust_name, o.order_num, SUM(quantity * item_price) AS OrderTotal
FROM Customers c,Orders o,OrderItems oi
WHERE c.cust_id = o.cust_id AND o.order_num = oi.order_num
GROUP BY c.cust_name
ORDER BY c.cust_name,o.order_num
```

这是错误的！只对 `cust_name` 进行聚类确实符合题意，但是不符合 `GROUP BY` 的语法。

select 语句中，如果没有 `GROUP BY` 语句，那么 `cust_name`、`order_num` 会返回若干个值，而 `sum(quantity * item_price)` 只返回一个值，通过 `group by` `cust_name` 可以让 `cust_name` 和 `sum(quantity * item_price)` 一一对应起来，或者说**聚类**，所以同样的，也要对 `order_num` 进行聚类。

> **一句话，select 中的字段要么都聚类，要么都不聚类**

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L1289)，来源许可：Apache-2.0。

<a id="kc8552f7b9734"></a>

## 连续两次作答试卷的最大时间窗（较难）

**描述**

现有试卷作答记录表 `exam_record`（`uid` 用户 ID, `exam_id` 试卷 ID, `start_time` 开始作答时间, `submit_time` 交卷时间, `score` 得分）：

| id  | uid  | exam_id | start_time          | submit_time         | score |
| --- | ---- | ------- | ------------------- | ------------------- | ----- |
| 1   | 1006 | 9003    | 2021-09-07 10:01:01 | 2021-09-07 10:21:02 | 84    |
| 2   | 1006 | 9001    | 2021-09-01 12:11:01 | 2021-09-01 12:31:01 | 89    |
| 3   | 1006 | 9002    | 2021-09-06 10:01:01 | 2021-09-06 10:21:01 | 81    |
| 4   | 1005 | 9002    | 2021-09-05 10:01:01 | 2021-09-05 10:21:01 | 81    |
| 5   | 1005 | 9001    | 2021-09-05 10:31:01 | 2021-09-05 10:51:01 | 81    |

请计算在 2021 年至少有两天作答过试卷的人中，计算该年连续两次作答试卷的最大时间窗 `days_window`，那么根据该年的历史规律他在 `days_window` 天里平均会做多少套试卷，按最大时间窗和平均做答试卷套数倒序排序。由示例数据结果输出如下：

| uid  | days_window | avg_exam_cnt |
| ---- | ----------- | ------------ |
| 1006 | 6           | 2.57         |

**解释**：用户 1006 分别在 20210901、20210906、20210907 作答过 3 次试卷，连续两次作答最大时间窗为 6 天（1 号到 6 号），他 1 号到 7 号这 7 天里共做了 3 张试卷，平均每天 3/7=0.428571 张，那么 6 天里平均会做 0.428571\*6=2.57 张试卷（保留两位小数）；用户 1005 在 20210905 做了两张试卷，但是只有一天的作答记录，过滤掉。

**思路：**

上面这个解释中提示要对作答记录去重，千万别被骗了，不要去重！去重就通不过测试用例。注意限制时间是 2021 年；

而且要注意时间差要+1 天；还要注意==没交卷也算在内==！！！！ （反正感觉这题描述不清，出的不是很好）

**答案**：

```sql
SELECT UID,
       max(datediff(next_time, start_time)) + 1 AS days_window,
       round(count(start_time)/(datediff(max(start_time), min(start_time))+ 1) * (max(datediff(next_time, start_time))+ 1), 2) AS avg_exam_cnt
FROM
  (SELECT UID,
          start_time,
          lead(start_time, 1) OVER (PARTITION BY UID
                                    ORDER BY start_time) AS next_time
   FROM exam_record
   WHERE YEAR (start_time) = '2021' ) a
GROUP BY UID
HAVING count(DISTINCT date(start_time)) > 1
ORDER BY days_window DESC,
         avg_exam_cnt DESC
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-04.md#L200)，来源许可：Apache-2.0。

<a id="k474ad855619f"></a>

## 那么，用了索引就一定能提高查询性能吗？

**不一定。** 大多数情况下，合理使用索引确实比全表扫描快得多。但也有例外：

- **数据量太小**：如果表里的数据非常少（比如就几百条），全表扫描可能比通过索引查找更快，因为走索引本身也有开销。
- **查询结果集占比过大**：如果要查询的数据占了整张表的大部分（比如超过 20%-30%），优化器可能会认为全表扫描更划算，因为通过索引多次回表（随机 I/O）的成本可能高于一次顺序的全表扫描。
- **索引维护不当或统计信息过时**：导致优化器做出错误判断。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L426)，来源许可：Apache-2.0。
