# SQL查询与练习

<a id="ka54919c1153a"></a>

## Agent+RAG 项目背景、技术方案（文档解析、分块、向量数据库选型与存储、检索流程）

**回答：**

<a id="tencent-llm-collection-20260903-q44"></a>

**相关解释：** [正常来说，一个query进了RAG之后，整体的工作流程是怎样的？](../10-RAG%E4%B8%8EAgent/Agent%E3%80%81%E5%B7%A5%E5%85%B7%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81-05.md#kf95403e9fa89)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E8%85%BE%E8%AE%AF%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L794)，来源许可：GPL-3.0。

<a id="k3b6a3687354e"></a>

## MRAG 1.0、2.0和3.0在文档解析与索引、检索策略和生成模块设计上有哪些核心差异？

核心差异：  
• MRAG 1.0：伪多模态架构，依赖OCR和独立模态模型（如CLIP+VQA）生成文本描述，导致信息损失（如图像细粒度特征丢失）。检索仅支持文本模态，生成阶段通过拼接文本描述和查询输入LLM。  

• MRAG 2.0：引入统一MLLM（如BLIP-2）处理多模态输入，保留原始数据（如图像像素）。跨模态检索通过双编码器对齐文本-图像嵌入（如CLIP的对比学习），生成阶段直接输入多模态数据。  

• MRAG 3.0：端到端多模态，新增搜索规划模块（动态路由检索）和多模态输出增强（如Native MLLM生成图文混合响应）。文档解析保留截图向量化（DSE方法），解决PDF/HTML等半结构化数据的信息损失问题。  

优化点：  
• 信息保留：1.0的OCR错误率（约15%）导致检索噪声，3.0的截图向量化将文档结构信息保留率提升至92%（论文实验4.2）。  

• 检索效率：2.0的跨模态检索延迟（200ms）高于3.0的动态规划（50ms），因后者通过公式(1)的$RC$模块跳过不必要检索（如$Q$为纯文本时直接调用$a_{\text{text}}$）。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E5%A4%9A%E6%A8%A1%E6%80%81%E5%9F%BA%E7%A1%80/%E5%A4%9A%E6%A8%A1%E6%80%81-%E5%89%8D%E6%B2%BF%E6%8A%80%E6%9C%AF.md#L178)，来源许可：GPL-3.0。

<a id="k7cba6c163681"></a>

## MySQL 的 B+Tree 索引为什么适合范围查询？

**回答：**

B+Tree 把索引项按键有序组织，内部节点负责导航，叶子页保存索引记录，叶子页之间可顺序遍历。范围查询先定位下界，再扫描后续叶子记录，直到到达上界，从而复用相邻键的有序性，避免对每条结果重新从根查找。

InnoDB 的索引按页管理，较高扇出使树高通常较低。典型范围扫描的代价可理解为一次树下降，加上覆盖目标区间的叶子页访问；缓存、页分裂、记录宽度和磁盘布局都会影响实际 IO。逻辑相邻的叶子页不保证物理磁盘连续，不能把“链表连接”直接等同于完全顺序磁盘读。

聚簇索引的叶子记录包含整行数据；二级索引叶子记录包含二级键和主键等信息，查询非覆盖字段时通常需要回表。范围命中比例大、二级索引回表多时，优化器仍可能选择全表扫描。

哈希结构擅长等值定位，但不天然支持有序区间；B+Tree 同时服务等值、范围、部分排序和联合索引前缀访问。是否避免排序，还要看 `ORDER BY`、前导列条件和扫描方向是否匹配。**适合范围查询的原因是有序页结构与范围扫描能力，不是“建了索引就一定更快”。**

<a id="baidu-agent-20260922-r1-q8"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%99%BE%E5%BA%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L852)，来源许可：GPL-3.0。

<a id="kd4cfef443c12"></a>

## PostgreSQL 做中文全文检索，需要怎么处理分词？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐ (3/5)**

PostgreSQL 默认全文配置不应被假定为高质量中文分词器。中文缺少显式空格边界，需要评估分词扩展、自定义解析配置，或在应用层分词后以一致规则写入和查询。拼接空格只是表示分词结果，不能替代分词质量。

应用层方案可先对标题、正文分词，再交给 `simple` 配置建立词项；查询也走同一分词、词典和归一化版本。扩展方案则需考虑安装权限、部署兼容性、词典维护和备份恢复。不要声称所有托管数据库都允许安装任意中文扩展。

测试行业词、课程名、人名、英文缩写、数字和错误码，记录漏分与过分。索引字段与查询字段使用不同词典会系统性漏召回；切换分词器后应重建全文字段和索引，并验证旧查询回归。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/10_Agent_RAG%E4%B8%8E%E6%B7%B7%E5%90%88%E6%A3%80%E7%B4%A2%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L257)，来源许可：GPL-3.0。

<a id="kc201506ef5e8"></a>

## PostgreSQL 全文检索怎么实现？tsvector、tsquery 和 GIN 索引分别起什么作用？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

`tsvector` 保存经配置解析、词典处理后的词项及可选位置；`tsquery` 表达匹配条件；`@@` 判断文档是否满足查询；GIN 索引加速候选匹配。相关性排序通常在匹配后计算，GIN 并不直接给出最终语义排序。

```sql
CREATE INDEX chunks_fts_gin ON chunks USING GIN (fts);

SELECT chunk_id, content,
       ts_rank_cd(fts, websearch_to_tsquery('simple', $1)) AS score
FROM chunks
WHERE tenant_id = $2
  AND visibility = 'public'
  AND is_active = true
  AND fts @@ websearch_to_tsquery('simple', $1)
ORDER BY score DESC, chunk_id
LIMIT $3;
```

上例只展示租户内公开块的检索，不代表完整 ACL。SQL 中的位置占位符使用绑定参数；中文查询须先执行与入库一致的分词或使用合适配置。`websearch_to_tsquery` 对普通搜索输入较友好，`to_tsquery` 则要求理解查询语法；不要把任意用户字符串直接拼成 SQL。

写入时同步更新全文字段，修改分词配置后重建相应数据。标题与正文可用 `setweight` 区分权重，实际索引使用情况以 `EXPLAIN (ANALYZE, BUFFERS)` 为准。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/10_Agent_RAG%E4%B8%8E%E6%B7%B7%E5%90%88%E6%A3%80%E7%B4%A2%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L233)，来源许可：GPL-3.0。

<a id="kd1c9a43a0b53"></a>

## SQL 类别高难度试卷得分的截断平均值（较难）

**描述**： 牛客的运营同学想要查看大家在 SQL 类别中高难度试卷的得分情况。

请你帮她从`exam_record`数据表中计算所有用户完成 SQL 类别高难度试卷得分的截断平均值（去掉一个最大值和一个最小值后的平均值）。

示例数据：`examination_info`（`exam_id` 试卷 ID, tag 试卷类别, `difficulty` 试卷难度, `duration` 考试时长, `release_time` 发布时间）

| id  | exam_id | tag  | difficulty | duration | release_time        |
| --- | ------- | ---- | ---------- | -------- | ------------------- |
| 1   | 9001    | SQL  | hard       | 60       | 2020-01-01 10:00:00 |
| 2   | 9002    | 算法 | medium     | 80       | 2020-08-02 10:00:00 |

示例数据：`exam_record`（uid 用户 ID, exam_id 试卷 ID, start_time 开始作答时间, submit_time 交卷时间, score 得分）

| id  | uid  | exam_id | start_time          | submit_time         | score  |
| --- | ---- | ------- | ------------------- | ------------------- | ------ |
| 1   | 1001 | 9001    | 2020-01-02 09:01:01 | 2020-01-02 09:21:01 | 80     |
| 2   | 1001 | 9001    | 2021-05-02 10:01:01 | 2021-05-02 10:30:01 | 81     |
| 3   | 1001 | 9001    | 2021-06-02 19:01:01 | 2021-06-02 19:31:01 | 84     |
| 4   | 1001 | 9002    | 2021-09-05 19:01:01 | 2021-09-05 19:40:01 | 89     |
| 5   | 1001 | 9001    | 2021-09-02 12:01:01 | (NULL)              | (NULL) |
| 6   | 1001 | 9002    | 2021-09-01 12:01:01 | (NULL)              | (NULL) |
| 7   | 1002 | 9002    | 2021-02-02 19:01:01 | 2021-02-02 19:30:01 | 87     |
| 8   | 1002 | 9001    | 2021-05-05 18:01:01 | 2021-05-05 18:59:02 | 90     |
| 9   | 1003 | 9001    | 2021-09-07 12:01:01 | 2021-09-07 10:31:01 | 50     |
| 10  | 1004 | 9001    | 2021-09-06 10:01:01 | (NULL)              | (NULL) |

根据输入你的查询结果如下：

| tag | difficulty | clip_avg_score |
| --- | ---------- | -------------- |
| SQL | hard       | 81.7           |

从`examination_info`表可知，试卷 9001 为高难度 SQL 试卷，该试卷被作答的得分有[80,81,84,90,50]，去除最高分和最低分后为[80,81,84]，平均分为 81.6666667，保留一位小数后为 81.7

**输入描述：**

输入数据中至少有 3 个有效分数

**思路一：** 要找出高难度 sql 试卷，肯定需要联 examination_info 这张表，然后找出高难度的课程，由 examination_info 得知，高难度 sql 的 exam_id 为 9001，那么等下就以 exam_id = 9001 作为条件去查询；

先找出 9001 号考试 `select * from exam_record where exam_id = 9001`

然后，找出最高分 `select max(score) 最高分 from exam_record where exam_id = 9001`

接着，找出最低分 `select min(score) 最低分 from exam_record where exam_id = 9001`

在查询出来的分数结果集当中，去掉最高分和最低分，最直观能想到的就是 NOT IN 或者 用 NOT EXISTS 也行，这里以 NOT IN 来做

首先将主体写出来`select tag, difficulty, round(avg(score), 1) clip_avg_score from examination_info info INNER JOIN exam_record record`

**小 tips** : MYSQL 的 `ROUND()` 函数 ,`ROUND(X)`返回参数 X 最近似的整数 `ROUND(X,D)`返回 X ,其值保留到小数点后 D 位,第 D 位的保留方式为四舍五入。

再将上面的 "碎片" 语句拼凑起来即可， 注意在 NOT IN 中两个子查询用 UNION ALL 来关联，用 union 把 max 和 min 的结果集中在一行当中，这样形成一列多行的效果。

**答案一：**

```sql
SELECT tag, difficulty, ROUND(AVG(score), 1) clip_avg_score
	FROM examination_info info  INNER JOIN exam_record record
		WHERE info.exam_id = record.exam_id
			AND  record.exam_id = 9001
				AND record.score NOT IN(
					SELECT MAX(score)
						FROM exam_record
							WHERE exam_id = 9001
								UNION ALL
					SELECT MIN(score)
						FROM exam_record
							WHERE exam_id = 9001
				)
```

这是最直观，也是最容易想到的解法，但是还有待改进，这算是投机取巧过关，其实严格按照题目要求应该这么写：

```sql
SELECT tag,
       difficulty,
       ROUND(AVG(score), 1) clip_avg_score
FROM examination_info info
INNER JOIN exam_record record
WHERE info.exam_id = record.exam_id
  AND record.exam_id =
    (SELECT examination_info.exam_id
     FROM examination_info
     WHERE tag = 'SQL'
       AND difficulty = 'hard' )
  AND record.score NOT IN
    (SELECT MAX(score)
     FROM exam_record
     WHERE exam_id =
         (SELECT examination_info.exam_id
          FROM examination_info
          WHERE tag = 'SQL'
            AND difficulty = 'hard' )
     UNION ALL SELECT MIN(score)
     FROM exam_record
     WHERE exam_id =
         (SELECT examination_info.exam_id
          FROM examination_info
          WHERE tag = 'SQL'
            AND difficulty = 'hard' ) )
```

然而你会发现，重复的语句非常多，所以可以利用`WITH`来抽取公共部分

**`WITH` 子句介绍**：

`WITH` 子句，也称为公共表表达式（Common Table Expression，CTE），是在 SQL 查询中定义临时表的方式。它可以让我们在查询中创建一个临时命名的结果集，并且可以在同一查询中引用该结果集。

基本用法：

```sql
WITH cte_name (column1, column2, ..., columnN) AS (
    -- 查询体
    SELECT ...
    FROM ...
    WHERE ...
)
-- 主查询
SELECT ...
FROM cte_name
WHERE ...
```

`WITH` 子句由以下几个部分组成：

- `cte_name`: 给临时表起一个名称，可以在主查询中引用。
- `(column1, column2, ..., columnN)`: 可选，指定临时表的列名。
- `AS`: 必需，表示开始定义临时表。
- `CTE 查询体`: 实际的查询语句，用于定义临时表中的数据。

`WITH` 子句的主要用途之一是增强查询的可读性和可维护性，尤其在涉及多个嵌套子查询或需要重复使用相同的查询逻辑时。通过将这些逻辑放在一个命名的临时表中，我们可以更清晰地组织查询，并消除重复代码。

此外，`WITH` 子句还可以在复杂的查询中实现递归查询。递归查询允许我们在单个查询中执行对同一表的多次迭代，逐步构建结果集。这在处理层次结构数据、组织结构和树状结构等场景中非常有用。

**小细节**：MySQL 5.7 版本以及之前的版本不支持在 `WITH` 子句中直接使用别名。

下面是改进后的答案：

```sql
WITH t1 AS
  (SELECT record.*,
          info.tag,
          info.difficulty
   FROM exam_record record
   INNER JOIN examination_info info ON record.exam_id = info.exam_id
   WHERE info.tag = "SQL"
     AND info.difficulty = "hard" )
SELECT tag,
       difficulty,
       ROUND(AVG(score), 1)
FROM t1
WHERE score NOT IN
    (SELECT max(score)
     FROM t1
     UNION SELECT min(score)
     FROM t1)
```

**思路二：**

- 筛选 SQL 高难度试卷：`where tag="SQL" and difficulty="hard"`
- 计算截断平均值：`(和-最大值-最小值) / (总个数-2)`:
  - `(sum(score) - max(score) - min(score)) / (count(score) - 2)`
  - 有一个缺点就是，如果最大值和最小值有多个，这个方法就很难筛选出来, 但是题目中说了----->**`去掉一个最大值和一个最小值后的平均值`**, 所以这里可以用这个公式。

**答案二：**

```sql
SELECT info.tag,
       info.difficulty,
       ROUND((SUM(record.score)- MIN(record.score)- MAX(record.score)) / (COUNT(record.score)- 2), 1) AS clip_avg_score
FROM examination_info info,
     exam_record record
WHERE info.exam_id = record.exam_id
  AND info.tag = "SQL"
  AND info.difficulty = "hard";
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-03.md#L20)，来源许可：Apache-2.0。

<a id="k573939254c73"></a>

## 什么是覆盖索引查询？

根据官方文档介绍，覆盖查询是以下的查询：

- 所有的查询字段是索引的一部分。
- 结果中返回的所有字段都在同一索引中。
- 查询中没有字段等于`null`。

由于所有出现在查询中的字段是索引的一部分， MongoDB 无需在整个数据文档中检索匹配查询条件和返回使用相同索引的查询结果。因为索引存在于内存中，从索引中获取数据比通过扫描文档读取数据要快得多。

举个例子：我们有如下 `users` 集合:

```json
{
   "_id": ObjectId("53402597d852426020000002"),
   "contact": "987654321",
   "dob": "01-01-1991",
   "gender": "M",
   "name": "Tom Benzamin",
   "user_name": "tombenzamin"
}
```

我们在 `users` 集合中创建联合索引，字段为 `gender` 和 `user_name` :

```sql
db.users.ensureIndex({gender:1,user_name:1})
```

现在，该索引会覆盖以下查询：

```sql
db.users.find({gender:"M"},{user_name:1,_id:0})
```

为了让指定的索引覆盖查询，必须显式地指定 `_id: 0` 来从结果中排除 `_id` 字段，因为索引不包括 `_id` 字段。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mongodb/mongodb-questions-02.md#L90)，来源许可：Apache-2.0。

<a id="k8b861fc77562"></a>

## 从 Customers 表中检索所有的 ID

现有表 `Customers` 如下：

| cust_id |
| ------- |
| A       |
| B       |
| C       |

编写 SQL 语句，从 `Customers` 表中检索所有的 `cust_id`。

```sql
SELECT cust_id
FROM Customers
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L20)，来源许可：Apache-2.0。

<a id="kf4835f22f665"></a>

## 从 Products 表中检索所有的产品名称以及对应的销售总数

`Products` 表中检索所有的产品名称：`prod_name`、产品 id：`prod_id`

| prod_id | prod_name |
| ------- | --------- |
| a0001   | egg       |
| a0002   | sockets   |
| a0013   | coffee    |
| a0003   | cola      |

`OrderItems` 代表订单商品表，订单产品：`prod_id`、售出数量：`quantity`

| prod_id | quantity |
| ------- | -------- |
| a0001   | 105      |
| a0002   | 1100     |
| a0002   | 200      |
| a0013   | 1121     |
| a0003   | 10       |
| a0003   | 19       |
| a0003   | 5        |

【问题】

编写 SQL 语句，从 `Products` 表中检索所有的产品名称（`prod_name`），以及名为 `quant_sold` 的计算列，其中包含所售产品的总数（在 `OrderItems` 表上使用子查询和 `SUM(quantity)` 检索）。

```sql
# 写法 1：子查询
SELECT p.prod_name, tb.quant_sold
FROM (SELECT prod_id, Sum(quantity) AS quant_sold
    FROM OrderItems
    GROUP BY prod_id) AS tb,
  Products p
WHERE tb.prod_id = p.prod_id

# 写法 2：连接表
SELECT p.prod_name, Sum(o.quantity) AS quant_sold
FROM Products p,
  OrderItems o
WHERE p.prod_id = o.prod_id
GROUP BY p.prod_name（这里不能用 p.prod_id，会报错）
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L1122)，来源许可：Apache-2.0。

<a id="k9e508b6fa636"></a>

## 作答试卷得分大于过 80 的人的用户等级分布

**描述**：

现有用户信息表 `user_info`（`uid` 用户 ID，`nick_name` 昵称, `achievement` 成就值, `level` 等级, `job` 职业方向, `register_time` 注册时间）：

试卷信息表 `examination_info`（`exam_id` 试卷 ID, `tag` 试卷类别, `difficulty` 试卷难度, `duration` 考试时长, `release_time` 发布时间）：

试卷作答信息表 `exam_record`（`uid` 用户 ID, `exam_id` 试卷 ID, `start_time` 开始作答时间, `submit_time` 交卷时间, `score` 得分）：

| id  | uid  | exam_id | start_time          | submit_time         | score  |
| --- | ---- | ------- | ------------------- | ------------------- | ------ |
| 1   | 1001 | 9001    | 2021-09-01 09:01:01 | 2021-09-01 09:41:01 | 79     |
| 2   | 1002 | 9003    | 2021-09-01 12:01:01 | 2021-09-01 12:21:01 | 60     |
| 3   | 1002 | 9002    | 2021-09-01 12:01:01 | 2021-09-01 12:31:01 | 70     |
| 4   | 1002 | 9001    | 2021-09-01 19:01:01 | 2021-09-01 19:40:01 | 80     |
| 5   | 1002 | 9003    | 2021-08-01 12:01:01 | 2021-08-01 12:21:01 | 60     |
| 6   | 1002 | 9002    | 2021-09-01 12:01:01 | 2021-09-01 12:31:01 | 70     |
| 7   | 1002 | 9001    | 2021-09-01 19:01:01 | 2021-09-01 19:40:01 | 85     |
| 8   | 1002 | 9002    | 2021-09-01 12:01:01 | (NULL)              | (NULL) |
| 9   | 1003 | 9002    | 2021-09-07 10:01:01 | 2021-09-07 10:31:01 | 86     |
| 10  | 1003 | 9003    | 2021-09-08 12:01:01 | 2021-09-08 12:11:01 | 40     |
| 11  | 1003 | 9003    | 2021-09-01 13:01:01 | 2021-09-01 13:41:01 | 81     |
| 12  | 1003 | 9001    | 2021-09-01 14:01:01 | (NULL)              | (NULL) |
| 13  | 1003 | 9002    | 2021-09-08 15:01:01 | (NULL)              | (NULL) |
| 14  | 1005 | 9001    | 2021-09-01 12:01:01 | 2021-09-01 12:31:01 | 90     |
| 15  | 1005 | 9002    | 2021-09-01 12:01:01 | 2021-09-01 12:31:01 | 88     |
| 16  | 1005 | 9002    | 2021-09-02 12:11:01 | 2021-09-02 12:31:01 | 89     |

统计作答 SQL 类别的试卷得分大于过 80 的人的用户等级分布，按数量降序排序（保证数量都不同）。示例数据结果输出如下：

| level | level_cnt |
| ----- | --------- |
| 6     | 2         |
| 5     | 1         |

解释：9001 为 SQL 类试卷，作答该试卷大于 80 分的人有 1002、1003、1005 共 3 人，6 级两人，5 级一人。

**思路：**这题和上一题都是一样的数据，只是查询条件改变了而已，上一题理解了，这题分分钟做出来。

**答案**：

```sql
SELECT u_info.LEVEL AS LEVEL,
       count(u_info.uid) AS level_cnt
FROM examination_info e_info
INNER JOIN exam_record record
INNER JOIN user_info u_info
WHERE e_info.exam_id = record.exam_id
  AND u_info.uid = record.uid
  AND record.score > 80
  AND submit_time IS NOT NULL
  AND tag = 'SQL'
GROUP BY LEVEL
ORDER BY level_cnt DESC
```

**相关解释：** [每个 6/7 级用户活跃情况（困难）](SQL%E6%9F%A5%E8%AF%A2%E4%B8%8E%E7%BB%83%E4%B9%A0-02.md#k07567cfaf867)；[试卷发布当天作答人数和平均分](SQL%E6%9F%A5%E8%AF%A2%E4%B8%8E%E7%BB%83%E4%B9%A0-03.md#k51614cb5112a)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-03.md#L754)，来源许可：Apache-2.0。

<a id="k49f5207c37cd"></a>

## 修复串列了的记录

**描述**：现有试卷信息表 `examination_info`（`exam_id` 试卷 ID, `tag` 试卷类别, `difficulty` 试卷难度, `duration` 考试时长, `release_time` 发布时间）：

| id  | exam_id | tag            | difficulty | duration | release_time        |
| --- | ------- | -------------- | ---------- | -------- | ------------------- |
| 1   | 9001    | 算法           | hard       | 60       | 2021-01-01 10:00:00 |
| 2   | 9002    | 算法           | hard       | 80       | 2021-01-01 10:00:00 |
| 3   | 9003    | SQL            | medium     | 70       | 2021-01-01 10:00:00 |
| 4   | 9004    | 算法,medium,80 |            | 0        | 2021-01-01 10:00:00 |

录题同学有一次手误将部分记录的试题类别 tag、难度、时长同时录入到了 tag 字段，请帮忙找出这些录错了的记录，并拆分后按正确的列类型输出。

由示例数据结果输出如下：

| exam_id | tag  | difficulty | duration |
| ------- | ---- | ---------- | -------- |
| 9004    | 算法 | medium     | 80       |

**思路**：

先来学习下本题要用到的函数

`SUBSTRING_INDEX` 函数用于提取字符串中指定分隔符的部分。它接受三个参数：原始字符串、分隔符和指定要返回的部分的数量。

以下是 `SUBSTRING_INDEX` 函数的语法：

```sql
SUBSTRING_INDEX(str, delimiter, count)
```

- `str`：要进行分割的原始字符串。
- `delimiter`：用作分割的字符串或字符。
- `count`：指定要返回的部分的数量。
  - 如果 `count` 大于 0，则返回从左边开始的前 `count` 个部分（以分隔符为界）。
  - 如果 `count` 小于 0，则返回从右边开始的前 `count` 个部分（以分隔符为界），即从右侧向左计数。

下面是一些示例，演示了 `SUBSTRING_INDEX` 函数的使用：

1. 提取字符串中的第一个部分：

```sql
   SELECT SUBSTRING_INDEX('apple,banana,cherry', ',', 1);
   -- 输出结果：'apple'
```

2. 提取字符串中的最后一个部分：

```sql
   SELECT SUBSTRING_INDEX('apple,banana,cherry', ',', -1);
   -- 输出结果：'cherry'
```

3. 提取字符串中的前两个部分：

```sql
   SELECT SUBSTRING_INDEX('apple,banana,cherry', ',', 2);
   -- 输出结果：'apple,banana'
```

4. 提取字符串中的最后两个部分：

```sql
   SELECT SUBSTRING_INDEX('apple,banana,cherry', ',', -2);
   -- 输出结果：'banana,cherry'
```

**答案**：

```sql
SELECT
	exam_id,
	substring_index( tag, ',', 1 ) tag,
	substring_index( substring_index( tag, ',', 2 ), ',',- 1 ) difficulty,
	substring_index( tag, ',',- 1 ) duration
FROM
	examination_info
WHERE
	difficulty = ''
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-05.md#L815)，来源许可：Apache-2.0。

<a id="k6efe075e728d"></a>

## 倒排索引和 RAG 检索有什么关系？

倒排索引从“词项”映射到“包含该词项的文档列表”。

结构示例：

```text
token_a -> doc1, doc7, doc20
token_b -> doc3, doc7
token_c -> doc2, doc20
```

传统搜索引擎会在倒排索引基础上计算 TF-IDF、BM25 等相关性分数。

RAG 中倒排索引仍然有价值：

- 精确召回关键词、实体名、编号、API 名称。
- 弥补纯向量检索对数字、代码、专有名词不稳定的问题。
- 与向量检索做 hybrid search。
- 为 reranker 提供候选池。

典型 RAG 检索链路：

1. Query 改写或抽取关键词。
2. 倒排索引召回关键词相关文档。
3. 向量索引召回语义相关文档。
4. 合并去重。
5. reranker 重排。
6. 送入 LLM 生成答案。

面试金句：向量检索擅长语义相似，倒排索引擅长精确匹配；生产级 RAG 通常需要两者结合。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84%26%E7%AE%97%E6%B3%95%E5%9F%BA%E7%A1%80/05_%E5%AD%97%E7%AC%A6%E4%B8%B2%E4%B8%8E%E9%AB%98%E7%BA%A7%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L322)，来源许可：GPL-3.0。

<a id="k9cec395d3c40"></a>

## 列出供应商及其可供产品的数量

有 `Vendors` 表含有 `vend_id` （供应商 id）

| vend_id |
| ------- |
| a0002   |
| a0013   |
| a0003   |
| a0010   |

有 `Products` 表含有 `vend_id`（供应商 id）和 prod_id（供应产品 id）

| vend_id | prod_id              |
| ------- | -------------------- |
| a0001   | egg                  |
| a0002   | prod_id_iphone       |
| a00113  | prod_id_tea          |
| a0003   | prod_id_vivo phone   |
| a0010   | prod_id_huawei phone |

【问题】列出供应商（`Vendors` 表中的 `vend_id`）及其可供产品的数量，包括没有产品的供应商。你需要使用 OUTER JOIN 和 COUNT()聚合函数来计算 `Products` 表中每种产品的数量，最后根据 vend_id 升序排序。

注意：`vend_id` 列会显示在多个表中，因此在每次引用它时都需要完全限定它。

```sql
SELECT v.vend_id, COUNT(prod_id) AS prod_id
FROM Vendors v
LEFT JOIN Products p
USING(vend_id)
GROUP BY v.vend_id
ORDER BY v.vend_id
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L1638)，来源许可：Apache-2.0。

<a id="k769e5f543870"></a>

## 创建联合索引时字段的放置顺序，会不会影响查询效率？为什么？

**回答：**

会影响。以下以 MySQL InnoDB 的 B+Tree 联合索引为例：索引 `(a,b,c)` 按 a、再 b、再 c 的字典序组织，同一 a 的记录相邻，在相同 a 内按 b 排序，再在相同 a、b 内按 c 排序。索引顺序决定哪些条件能够形成连续、可高效定位的扫描范围。

`a=? AND b=?` 通常能利用前两列定位；`a=? AND b>? AND c=?` 中，常规范围定位通常不能继续用 c 把整个范围压成同样精确的区间，但 c 仍可能用于索引条件下推、过滤或覆盖查询。不能把“不能继续缩小搜索区间”说成“后面的列完全失效”。

列顺序应结合高频查询的过滤、排序、分组和覆盖需求：常用的租户等值条件、业务状态与时间范围，往往需要一起考虑。对所有列都等值查询的场景，不同排列可能都能精确定位，区别更多体现在其他查询的复用。把“选择性最高的列永远排第一”当通用规则是不严谨的。

索引也有写入、缓存和存储成本。通过真实数据分布、统计信息与 `EXPLAIN` 比较候选方案；`EXPLAIN ANALYZE` 会实际执行查询，应在可控环境使用。SQL 中 `WHERE` 条件书写顺序通常由优化器处理，不等于索引定义里的列顺序。

<a id="hengsheng-ai-dev-20260923-q7"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E6%81%92%E7%94%9F%E7%94%B5%E5%AD%90%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L154)，来源许可：GPL-3.0。

<a id="k91763ebbc08b"></a>

## 删除记录（一）

**描述**：现有一张试卷作答记录表 `exam_record`，其中包含多年来的用户作答试卷记录，结构如下表：

作答记录表`exam_record：` **`start_time`** 是试卷开始时间`submit_time` 是交卷，即结束时间。

| Filed       | Type       | Null | Key | Extra          | Default | Comment  |
| ----------- | ---------- | ---- | --- | -------------- | ------- | -------- |
| id          | int(11)    | NO   | PRI | auto_increment | (NULL)  | 自增 ID  |
| uid         | int(11)    | NO   |     |                | (NULL)  | 用户 ID  |
| exam_id     | int(11)    | NO   |     |                | (NULL)  | 试卷 ID  |
| start_time  | datetime   | NO   |     |                | (NULL)  | 开始时间 |
| submit_time | datetime   | YES  |     |                | (NULL)  | 提交时间 |
| score       | tinyint(4) | YES  |     |                | (NULL)  | 得分     |

**要求**：请删除`exam_record`表中作答时间小于 5 分钟整且分数不及格（及格线为 60 分）的记录；

**思路**：这一题虽然是练习删除，仔细看确是考察对时间函数的用法，这里提及的分钟数比较，常用的函数有 **`TIMEDIFF`**和**`TIMESTAMPDIFF`** ，两者用法稍有区别，后者更为灵活，这都是看个人习惯。

1.　 `TIMEDIFF`：两个时间之间的差值

```sql
TIMEDIFF(time1, time2)
```

两者参数都是必须的，都是一个时间或者日期时间表达式。如果指定的参数不合法或者是 NULL，那么函数将返回 NULL。

对于这题而言，可以用在 minute 函数里面，因为 TIMEDIFF 计算出来的是时间的差值，在外面套一个 MINUTE 函数，计算出来的就是分钟数。

2. `TIMESTAMPDIFF`：用于计算两个日期的时间差

```sql
TIMESTAMPDIFF(unit,datetime_expr1,datetime_expr2)
# 参数说明
#unit: 日期比较返回的时间差单位，常用可选值如下:
SECOND：秒
MINUTE：分钟
HOUR：小时
DAY：天
WEEK：星期
MONTH：月
QUARTER：季度
YEAR：年
# TIMESTAMPDIFF函数返回datetime_expr2 - datetime_expr1的结果（人话： 后面的 - 前面的  即2-1），其中datetime_expr1和datetime_expr2可以是DATE或DATETIME类型值（人话：可以是“2023-01-01”， 也可以是“2023-01-01- 00:00:00”）
```

这题需要进行分钟的比较，那么就是 TIMESTAMPDIFF(MINUTE, 开始时间， 结束时间) < 5

**答案**：

```sql
DELETE FROM exam_record WHERE MINUTE (TIMEDIFF(submit_time , start_time)) < 5 AND score < 60
```

```sql
DELETE FROM exam_record WHERE TIMESTAMPDIFF(MINUTE, start_time, submit_time) < 5 AND score < 60
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-02.md#L156)，来源许可：Apache-2.0。

<a id="k84fdba2fe5e8"></a>

## 删除记录（三）

**描述**：现有一张试卷作答记录表 exam_record，其中包含多年来的用户作答试卷记录，结构如下表：

**要求**：请删除`exam_record`表中所有记录，==并重置自增主键==

**思路**：这题考察对三种删除语句的区别，注意高亮部分，要求重置主键；

- `DROP`: 清空表，删除表结构，不可逆
- `TRUNCATE`: 格式化表，不删除表结构，不可逆
- `DELETE`：删除数据，可逆

这里选用`TRUNCATE`的原因是：TRUNCATE 只能作用于表；`TRUNCATE`会清空表中的所有行，但表结构及其约束、索引等保持不变；`TRUNCATE`会重置表的自增值；使用`TRUNCATE`后会使表和索引所占用的空间会恢复到初始大小。

这题也可以采用`DELETE`来做，但是在删除后，还需要手动`ALTER`表结构来设置主键初始值；

同理也可以采用`DROP`来做，直接删除整张表，包括表结构，然后再新建表即可。

**答案**：

```sql
TRUNCATE  exam_record;
```

**相关解释：** [删除记录（一）](SQL%E6%9F%A5%E8%AF%A2%E4%B8%8E%E7%BB%83%E4%B9%A0-01.md#k91763ebbc08b)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-02.md#L244)，来源许可：Apache-2.0。

<a id="k06562cb9f207"></a>

## 删除记录（二）

**描述**：现有一张试卷作答记录表`exam_record`，其中包含多年来的用户作答试卷记录，结构如下表：

作答记录表`exam_record`：`start_time` 是试卷开始时间，`submit_time` 是交卷时间，即结束时间，如果未完成的话，则为空。

**要求**：请删除`exam_record`表中未完成作答==或==作答时间小于 5 分钟整的记录中，开始作答时间最早的 3 条记录。

**思路**：这题比较简单，但是要注意题干中给出的信息，结束时间，如果未完成的话，则为空，这个其实就是一个条件

还有一个条件就是小于 5 分钟，跟上题类似，但是这里是**或**，即两个条件满足一个就行；另外就是稍微考察到了排序和 limit 的用法。

**答案**：

```sql
DELETE FROM exam_record WHERE submit_time IS null OR TIMESTAMPDIFF(MINUTE, start_time, submit_time) < 5
ORDER BY start_time
LIMIT 3
# 默认就是asc， desc是降序排列
```

**相关解释：** [删除记录（一）](SQL%E6%9F%A5%E8%AF%A2%E4%B8%8E%E7%BB%83%E4%B9%A0-01.md#k91763ebbc08b)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-02.md#L214)，来源许可：Apache-2.0。

<a id="kc0a6610957e3"></a>

## 各用户等级的不同得分表现占比（较难）

**描述**：

现有用户信息表 `user_info`（`uid` 用户 ID，`nick_name` 昵称, `achievement` 成就值, `level` 等级, `job` 职业方向, `register_time` 注册时间）：

试卷作答记录表 exam_record（uid 用户 ID, exam_id 试卷 ID, start_time 开始作答时间, submit_time 交卷时间, score 得分）：

| id  | uid  | exam_id | start_time          | submit_time         | score  |
| --- | ---- | ------- | ------------------- | ------------------- | ------ |
| 1   | 1001 | 9001    | 2020-01-02 09:01:01 | 2020-01-02 09:21:59 | 80     |
| 2   | 1001 | 9001    | 2021-05-02 10:01:01 | (NULL)              | (NULL) |
| 3   | 1001 | 9002    | 2021-02-02 19:01:01 | 2021-02-02 19:30:01 | 75     |
| 4   | 1001 | 9002    | 2021-09-01 12:01:01 | 2021-09-01 12:11:01 | 60     |
| 5   | 1001 | 9003    | 2021-09-02 12:01:01 | 2021-09-02 12:41:01 | 90     |
| 6   | 1001 | 9001    | 2021-06-02 19:01:01 | 2021-06-02 19:32:00 | 20     |
| 7   | 1001 | 9002    | 2021-09-05 19:01:01 | 2021-09-05 19:40:01 | 89     |
| 8   | 1001 | 9004    | 2021-09-03 12:01:01 | (NULL)              | (NULL) |
| 9   | 1002 | 9001    | 2020-01-01 12:01:01 | 2020-01-01 12:31:01 | 99     |
| 10  | 1002 | 9003    | 2020-02-01 12:01:01 | 2020-02-01 12:31:01 | 82     |
| 11  | 1002 | 9003    | 2020-02-02 12:11:01 | 2020-02-02 12:41:01 | 76     |

为了得到用户试卷作答的定性表现，我们将试卷得分按分界点[90,75,60]分为优良中差四个得分等级（分界点划分到左区间），请统计不同用户等级的人在完成过的试卷中各得分等级占比（结果保留 3 位小数），未完成过试卷的用户无需输出，结果按用户等级降序、占比降序排序。

由示例数据结果输出如下：

| level | score_grade | ratio |
| ----- | ----------- | ----- |
| 3     | 良          | 0.667 |
| 3     | 优          | 0.333 |
| 0     | 良          | 0.500 |
| 0     | 中          | 0.167 |
| 0     | 优          | 0.167 |
| 0     | 差          | 0.167 |

解释：完成过试卷的用户有 1001、1002；完成了的试卷对应的用户等级和分数等级如下：

| uid  | exam_id | score | level | score_grade |
| ---- | ------- | ----- | ----- | ----------- |
| 1001 | 9001    | 80    | 0     | 良          |
| 1001 | 9002    | 75    | 0     | 良          |
| 1001 | 9002    | 60    | 0     | 中          |
| 1001 | 9003    | 90    | 0     | 优          |
| 1001 | 9001    | 20    | 0     | 差          |
| 1001 | 9002    | 89    | 0     | 良          |
| 1002 | 9001    | 99    | 3     | 优          |
| 1002 | 9003    | 82    | 3     | 良          |
| 1002 | 9003    | 76    | 3     | 良          |

因此 0 级用户（只有 1001）的各分数等级比例为：优 1/6，良 1/6，中 1/6，差 3/6；3 级用户（只有 1002）各分数等级比例为：优 1/3，良 2/3。结果保留 3 位小数。

**思路**：

先把 **“将试卷得分按分界点[90,75,60]分为优良中差四个得分等级”**这个条件写出来，这里可以用到`case when`

```sql
CASE
		WHEN a.score >= 90 THEN
		'优'
		WHEN a.score < 90 AND a.score >= 75 THEN
		'良'
		WHEN a.score < 75 AND a.score >= 60 THEN
	'中' ELSE '差'
END
```

这题的关键点就在于这，其他剩下的就是条件拼接了

**答案**：

```sql
SELECT a.LEVEL,
       a.score_grade,
       ROUND(a.cur_count / b.total_num, 3) AS ratio
FROM
  (SELECT b.LEVEL AS LEVEL,
          (CASE
               WHEN a.score >= 90 THEN '优'
               WHEN a.score < 90
                    AND a.score >= 75 THEN '良'
               WHEN a.score < 75
                    AND a.score >= 60 THEN '中'
               ELSE '差'
           END) AS score_grade,
          count(1) AS cur_count
   FROM exam_record a
   LEFT JOIN user_info b ON a.uid = b.uid
   WHERE a.submit_time IS NOT NULL
   GROUP BY b.LEVEL,
            score_grade) a
LEFT JOIN
  (SELECT b.LEVEL AS LEVEL,
          count(b.LEVEL) AS total_num
   FROM exam_record a
   LEFT JOIN user_info b ON a.uid = b.uid
   WHERE a.submit_time IS NOT NULL
   GROUP BY b.LEVEL) b ON a.LEVEL = b.LEVEL
ORDER BY a.LEVEL DESC,
         ratio DESC
```

**相关解释：** [根据指定记录是否存在输出不同情况（困难）](SQL%E6%9F%A5%E8%AF%A2%E4%B8%8E%E7%BB%83%E4%B9%A0-02.md#k14ac517d3019)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-05.md#L566)，来源许可：Apache-2.0。

<a id="kf475590565df"></a>

## 向量数据库检索出来的历史信息，如果语义相关但时间太久，能直接用吗？

<a id="batch4-p1-q9"></a>

### 补充说明

<a id="batch4-p2-q5"></a>

**相关解释：** [Embedding模型与Reranker差异，二者训练Loss区别](../10-RAG%E4%B8%8EAgent/RAG%E4%B8%8E%E6%A3%80%E7%B4%A2%E5%A2%9E%E5%BC%BA-01.md#k1abf61aa73cc)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%BF%AB%E6%89%8B%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L193)，来源许可：GPL-3.0。
- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%BF%AB%E6%89%8B%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L258)，来源许可：GPL-3.0。

<a id="k2b6e83a79dc6"></a>

## 向量相似度检索不能实现关键词的精确匹配，基于倒排索引的关键词检索不能匹配语义相近的词，如何解决这对矛盾？为什么需要重排序模型？

为解决语义检索与关键词匹配的矛盾，我采用混合检索架构：

1. 向量检索召回语义相近文本，解决同义词、表达差异问题；
2. 关键词检索通过倒排索引确保精确命中重要术语；
3. 融合策略：两种方式结合，互补召回，提升覆盖率与准确性。

重排序模型的作用是对初步召回结果进行语义理解与排序优化，解决召回阶段排序不准的问题。它通常使用跨编码器或大模型，根据查询与文档间深层语义关系重新打分，提升最终输出质量。

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/04-ai-algorithms/llm/llm-interview-questions.md#L311)，来源许可：GPL-3.0。

<a id="k0d167f42f076"></a>

## 向量索引为什么是 AIGC 检索系统的核心结构？

向量索引用于快速查找与 query embedding 最相似的候选向量，是 RAG、推荐、图像检索、多模态检索的核心。

如果有 $N$ 个文档向量，每个维度为 $d$，精确搜索需要计算 query 与所有向量的距离，复杂度约为 $O(Nd)$。当 $N$ 达到千万或亿级时，精确搜索延迟和成本很高。

向量索引的目标：

- 降低查询延迟。
- 控制内存占用。
- 在召回率和速度之间权衡。
- 支持增量插入、删除和过滤。

常见距离：

- 内积。
- 余弦相似度。
- 欧氏距离。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84%26%E7%AE%97%E6%B3%95%E5%9F%BA%E7%A1%80/05_%E5%AD%97%E7%AC%A6%E4%B8%B2%E4%B8%8E%E9%AB%98%E7%BA%A7%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L356)，来源许可：GPL-3.0。

<a id="kf8ef1f101d14"></a>

## 在使用 LIKE 进行模糊查询时，索引什么情况下会失效？

**回答：**

LIKE 能否使用 B+ 树索引，关键看模式是否有固定左前缀。

`like 'abc%'` 通常可以使用索引，因为 B+ 树可以定位到以 `abc` 开头的范围，再向后扫描。它本质上等价于在有序索引中查找 `[abc, abd)` 这样的范围。

`like '%abc'` 和 `like '%abc%'` 通常不能有效使用普通 B+ 树索引，因为匹配条件不是从字符串左侧开始，索引无法定位起始范围，只能扫描大量数据。

`like '_abc%'` 这类以下划线或通配符开头的模式，也无法利用固定左前缀。对索引列做函数后再 LIKE，例如 `where lower(name) like 'abc%'`，如果没有函数索引，也会影响索引使用。

如果确实需要中缀匹配，可以考虑全文索引、倒排索引、ngram 分词、Elasticsearch/OpenSearch，或者额外维护反转字段来支持后缀匹配。例如要查 `'%abc'`，可以维护 reverse_name，转成反向前缀查询。

<a id="bytedance-ai-agent-hard-20260602-q16"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%AD%97%E8%8A%82%E8%B7%B3%E5%8A%A8%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L618)，来源许可：GPL-3.0。

<a id="k7412bd24586b"></a>

## 大小写混乱时的筛选统计（较难）

**描述**：

现有试卷信息表 `examination_info`（`exam_id` 试卷 ID, `tag` 试卷类别, `difficulty` 试卷难度, `duration` 考试时长, `release_time` 发布时间）：

| id  | exam_id | tag  | difficulty | duration | release_time        |
| --- | ------- | ---- | ---------- | -------- | ------------------- |
| 1   | 9001    | 算法 | hard       | 60       | 2021-01-01 10:00:00 |
| 2   | 9002    | C++  | hard       | 80       | 2021-01-01 10:00:00 |
| 3   | 9003    | C++  | hard       | 80       | 2021-01-01 10:00:00 |
| 4   | 9004    | sql  | medium     | 70       | 2021-01-01 10:00:00 |
| 5   | 9005    | C++  | hard       | 80       | 2021-01-01 10:00:00 |
| 6   | 9006    | C++  | hard       | 80       | 2021-01-01 10:00:00 |
| 7   | 9007    | C++  | hard       | 80       | 2021-01-01 10:00:00 |
| 8   | 9008    | SQL  | medium     | 70       | 2021-01-01 10:00:00 |
| 9   | 9009    | SQL  | medium     | 70       | 2021-01-01 10:00:00 |
| 10  | 9010    | SQL  | medium     | 70       | 2021-01-01 10:00:00 |

试卷作答信息表 `exam_record`（`uid` 用户 ID, `exam_id` 试卷 ID, `start_time` 开始作答时间, `submit_time` 交卷时间, `score` 得分）：

| id  | uid  | exam_id | start_time          | submit_time         | score  |
| --- | ---- | ------- | ------------------- | ------------------- | ------ |
| 1   | 1001 | 9001    | 2020-01-01 09:01:01 | 2020-01-01 09:21:59 | 80     |
| 2   | 1002 | 9003    | 2020-01-20 10:01:01 | 2020-01-20 10:10:01 | 81     |
| 3   | 1002 | 9002    | 2020-02-01 12:11:01 | 2020-02-01 12:31:01 | 83     |
| 4   | 1003 | 9002    | 2020-03-01 19:01:01 | 2020-03-01 19:30:01 | 75     |
| 5   | 1004 | 9002    | 2020-03-01 12:01:01 | 2020-03-01 12:11:01 | 60     |
| 6   | 1005 | 9002    | 2020-03-01 12:01:01 | 2020-03-01 12:41:01 | 90     |
| 7   | 1006 | 9001    | 2020-05-02 19:01:01 | 2020-05-02 19:32:00 | 20     |
| 8   | 1007 | 9003    | 2020-01-02 19:01:01 | 2020-01-02 19:40:01 | 89     |
| 9   | 1008 | 9004    | 2020-02-02 12:01:01 | 2020-02-02 12:20:01 | 99     |
| 10  | 1008 | 9001    | 2020-02-02 12:01:01 | 2020-02-02 12:31:01 | 98     |
| 11  | 1009 | 9002    | 2020-02-02 12:01:01 | 2020-01-02 12:43:01 | 81     |
| 12  | 1010 | 9001    | 2020-01-02 12:11:01 | (NULL)              | (NULL) |
| 13  | 1010 | 9001    | 2020-02-02 12:01:01 | 2020-01-02 10:31:01 | 89     |

试卷的类别 tag 可能出现大小写混乱的情况，请先筛选出试卷作答数小于 3 的类别 tag，统计将其转换为大写后对应的原本试卷作答数。

如果转换后 tag 并没有发生变化，不输出该条结果。

由示例数据结果输出如下：

| tag | answer_cnt |
| --- | ---------- |
| C++ | 6          |

解释：被作答过的试卷有 9001、9002、9003、9004，他们的 tag 和被作答次数如下：

| exam_id | tag  | answer_cnt |
| ------- | ---- | ---------- |
| 9001    | 算法 | 4          |
| 9002    | C++  | 6          |
| 9003    | c++  | 2          |
| 9004    | sql  | 2          |

作答次数小于 3 的 tag 有 c++和 sql，而转为大写后只有 C++本来就有作答数，于是输出 c++转化大写后的作答次数为 6。

**思路**：

首先，这题有点混乱，9004 根据示例数据查出来只有 1 次，这里显示有 2 次。

先看一下大小写转换函数：

1.`UPPER(s)`或`UCASE(s)`函数可以将字符串 s 中的字母字符全部转换成大写字母；

2.`LOWER(s)`或者`LCASE(s)`函数可以将字符串 s 中的字母字符全部转换成小写字母。

难点在于相同表做连接要查询不同的值

**答案**：

```sql
WITH a AS
  (SELECT tag,
          COUNT(start_time) AS answer_cnt
   FROM exam_record er
   JOIN examination_info ei ON er.exam_id = ei.exam_id
   GROUP BY tag)
SELECT a.tag,
       b.answer_cnt
FROM a
INNER JOIN a AS b ON UPPER(a.tag)= b.tag #a小写 b大写
AND a.tag != b.tag
WHERE a.answer_cnt < 3;
```

<!-- @include: @article-footer.snippet.md -->

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-05.md#L958)，来源许可：Apache-2.0。

<a id="k274cfcffd6af"></a>

## 如何构建一个 AI 照片助手，能够对用户的上万张照片进行索引，根据用户的查询高效地检索相关照片？

构建 AI 照片助手的简要方案：

1. **照片预处理**：对所有照片进行去重、清晰度检测和格式统一。
2. **特征提取**：使用预训练的视觉模型（如ResNet、CLIP）提取每张照片的视觉特征向量。
3. **索引构建**：利用高效的向量数据库（如FAISS、Milvus）建立照片特征的索引，支持快速相似度搜索。
4. **查询解析**：将用户查询转换为语义向量（文本转向量），如使用CLIP文本编码器或其他文本嵌入模型。
5. **相似度检索**：在索引中用查询向量检索最相似的照片特征，返回相关照片。
6. **排序与过滤**：根据时间、地点、标签等元数据对结果进行二次排序和筛选。
7. **用户反馈**：允许用户标记相关或不相关照片，用于后续模型微调和提升检索效果。

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/04-ai-algorithms/llm/llm-interview-questions.md#L375)，来源许可：GPL-3.0。

<a id="k7053c728556c"></a>

## 如果我有一个联合索引abc，查询条件是b等于1 and c等于2，这个查询能用到这个联合索引吗？

**回答：**

不能仅凭缺少 a 就回答“绝对不能用”。对于 `(a,b,c)` 且仅有 `b=1 AND c=2` 的查询，**通常无法按完整最左前缀直接定位一个连续的精确区间**，但是否使用这个索引还存在几种可能。

| 执行方式 | 能否发生 | 需要注意的边界 |
|---|---|---|
| 普通前缀查找 | 缺少 a 时通常不具备直接前缀定位条件 | 不是简单的 `(a,b,c)` 等值查找 |
| 全索引扫描 | 优化器可能选择 | 尤其索引覆盖查询时，扫描索引可能比扫描整行便宜，但仍要读大量索引项 |
| Skip Scan | 支持该优化且满足限制时可能选择 | 遍历不同前导值再做后续范围查找，前导列基数与成本很关键 |
| 全表扫描或其他索引 | 也可能选择 | 由选择性、覆盖情况、统计信息和成本决定 |

MySQL 8.x 的 Skip Scan 不是无条件通用能力，适用查询形态、覆盖列、单表及分组等存在限制，最终以具体版本和执行计划为准。`b=1 AND c=2` 并不保证一定触发这一优化。

可以比较 `SELECT b,c ...` 与 `SELECT * ...` 的计划：前者更可能由索引覆盖，后者可能需要大量回表。看 `key`、访问类型、估计/实际扫描行数、`Extra` 和查询耗时，区分“选了索引”和“高效用了索引”。如果这类 b、c 条件是核心高频查询，再评估 `(b,c)` 或其他符合整体负载的索引。

<a id="hengsheng-ai-dev-20260923-q8"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E6%81%92%E7%94%9F%E7%94%B5%E5%AD%90%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L167)，来源许可：GPL-3.0。

<a id="k2c9608b95b0a"></a>

## 对试卷得分做 min-max 归一化

**描述**：

现有试卷信息表 `examination_info`（`exam_id` 试卷 ID, `tag` 试卷类别, `difficulty` 试卷难度, `duration` 考试时长, `release_time` 发布时间）：

| id  | exam_id | tag    | difficulty | duration | release_time        |
| --- | ------- | ------ | ---------- | -------- | ------------------- |
| 1   | 9001    | SQL    | hard       | 60       | 2020-01-01 10:00:00 |
| 2   | 9002    | C++    | hard       | 80       | 2020-01-01 10:00:00 |
| 3   | 9003    | 算法   | hard       | 80       | 2020-01-01 10:00:00 |
| 4   | 9004    | PYTHON | medium     | 70       | 2020-01-01 10:00:00 |

试卷作答记录表 `exam_record`（`uid` 用户 ID, `exam_id` 试卷 ID, `start_time` 开始作答时间, `submit_time` 交卷时间, `score` 得分）：

| id  | uid  | exam_id | start_time          | submit_time         | score  |
| --- | ---- | ------- | ------------------- | ------------------- | ------ |
| 6   | 1003 | 9001    | 2020-01-02 12:01:01 | 2020-01-02 12:31:01 | 68     |
| 9   | 1001 | 9001    | 2020-01-02 10:01:01 | 2020-01-02 10:31:01 | 89     |
| 1   | 1001 | 9001    | 2020-01-01 09:01:01 | 2020-01-01 09:21:59 | 90     |
| 12  | 1002 | 9002    | 2021-05-05 18:01:01 | (NULL)              | (NULL) |
| 3   | 1004 | 9002    | 2020-01-01 12:01:01 | 2020-01-01 12:11:01 | 60     |
| 2   | 1003 | 9002    | 2020-01-01 19:01:01 | 2020-01-01 19:30:01 | 75     |
| 7   | 1001 | 9002    | 2020-01-02 12:01:01 | 2020-01-02 12:43:01 | 81     |
| 10  | 1002 | 9002    | 2020-01-01 12:11:01 | 2020-01-01 12:31:01 | 83     |
| 4   | 1003 | 9002    | 2020-01-01 12:01:01 | 2020-01-01 12:41:01 | 90     |
| 5   | 1002 | 9002    | 2020-01-02 19:01:01 | 2020-01-02 19:32:00 | 90     |
| 11  | 1002 | 9004    | 2021-09-06 12:01:01 | (NULL)              | (NULL) |
| 8   | 1001 | 9005    | 2020-01-02 12:11:01 | (NULL)              | (NULL) |

在物理学及统计学数据计算时，有个概念叫 min-max 标准化，也被称为离差标准化，是对原始数据的线性变换，使结果值映射到[0 - 1]之间。

转换函数为：

![](https://oss.javaguide.cn/github/javaguide/database/sql/29A377601170AB822322431FCDF7EDFE.png)

请你将用户作答高难度试卷的得分在每份试卷作答记录内执行 min-max 归一化后缩放到[0,100]区间，并输出用户 ID、试卷 ID、归一化后分数平均值；最后按照试卷 ID 升序、归一化分数降序输出。（注：得分区间默认为[0,100]，如果某个试卷作答记录中只有一个得分，那么无需使用公式，归一化并缩放后分数仍为原分数）。

由示例数据结果输出如下：

| uid  | exam_id | avg_new_score |
| ---- | ------- | ------------- |
| 1001 | 9001    | 98            |
| 1003 | 9001    | 0             |
| 1002 | 9002    | 88            |
| 1003 | 9002    | 75            |
| 1001 | 9002    | 70            |
| 1004 | 9002    | 0             |

解释：高难度试卷有 9001、9002、9003；

作答了 9001 的记录有 3 条，分数分别为 68、89、90，按给定公式归一化后分数为：0、95、100，而后两个得分都是用户 1001 作答的，因此用户 1001 对试卷 9001 的新得分为(95+100)/2≈98（只保留整数部分），用户 1003 对于试卷 9001 的新得分为 0。最后结果按照试卷 ID 升序、归一化分数降序输出。

**思路：**

注意点：

1. 将高难度的试卷，按每类试卷的得分，利用 max/min (col) over()窗口函数求得各组内最大最小值，然后进行归一化公式计算，缩放区间为[0,100]，即 min_max\*100
2. 若某类试卷只有一个得分，则无需使用归一化公式，因只有一个分 max_score=min_score,score，公式后结果可能会变成 0。
3. 最后结果按 uid、exam_id 分组求归一化后均值，score 为 NULL 的要过滤掉。

最后就是仔细看上面公式 （说实话，这题看起来就很绕）

**答案**：

```sql
SELECT
  uid,
  exam_id,
  round(sum(min_max) / count(score), 0) AS avg_new_score
FROM
  (
    SELECT
      *,
      IF (
        max_score = min_score,
        score,
        (score - min_score) / (max_score - min_score) * 100
      ) AS min_max
    FROM
      (
        SELECT
          uid,
          a.exam_id,
          score,
          max(score) over (PARTITION BY a.exam_id) AS max_score,
          min(score) over (PARTITION BY a.exam_id) AS min_score
        FROM
          exam_record a
          LEFT JOIN examination_info b USING (exam_id)
        WHERE
          difficulty = 'hard'
      ) t
    WHERE
      score IS NOT NULL
  ) t1
GROUP BY
  uid,
  exam_id
ORDER BY
  exam_id ASC,
  avg_new_score DESC;
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-04.md#L592)，来源许可：Apache-2.0。

<a id="k50b228669766"></a>

## 对顾客 ID 和日期排序

有 `Orders` 表：

| cust_id | order_num | order_date          |
| ------- | --------- | ------------------- |
| andy    | aaaa      | 2021-01-01 00:00:00 |
| andy    | bbbb      | 2021-01-01 12:00:00 |
| bob     | cccc      | 2021-01-10 12:00:00 |
| dick    | dddd      | 2021-01-11 00:00:00 |

编写 SQL 语句，从 `Orders` 表中检索顾客 ID（`cust_id`）和订单号（`order_num`），并先按顾客 ID 对结果进行排序，再按订单日期倒序排列。

```sql
# 根据列名排序
# 注意：是 order_date 降序，而不是 order_num
SELECT cust_id, order_num
FROM Orders
ORDER BY cust_id,order_date DESC
```

知识点：`order by` 对多列排序的时候，先排序的列放前面，后排序的列放后面。并且，不同的列可以有不同的排序规则。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L115)，来源许可：Apache-2.0。

<a id="kbd3783b5d833"></a>

## 将两个 SELECT 语句结合起来（一）

表 `OrderItems` 包含订单产品信息，字段 `prod_id` 代表产品 id、`quantity` 代表产品数量

| prod_id | quantity |
| ------- | -------- |
| a0001   | 105      |
| a0002   | 100      |
| a0002   | 200      |
| a0013   | 1121     |
| a0003   | 10       |
| a0003   | 19       |
| a0003   | 5        |
| BNBG    | 10002    |

【问题】将两个 `SELECT` 语句结合起来，以便从 `OrderItems` 表中检索产品 id（`prod_id`）和 `quantity`。其中，一个 `SELECT` 语句过滤数量为 100 的行，另一个 `SELECT` 语句过滤 id 以 BNBG 开头的产品，最后按产品 id 对结果进行升序排序。

```sql
SELECT prod_id, quantity
FROM OrderItems
WHERE quantity = 100
UNION
SELECT prod_id, quantity
FROM OrderItems
WHERE prod_id LIKE 'BNBG%'
ORDER BY prod_id;
```

> **注意**：`UNION` 查询中使用 `ORDER BY` 时，只能在最后一个 `SELECT` 语句之后使用一次，它会对整个组合结果集进行排序。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L1697)，来源许可：Apache-2.0。

<a id="k87cce3cc7ef8"></a>

## 将两个 SELECT 语句结合起来（二）

表 `OrderItems` 包含订单产品信息，字段 `prod_id` 代表产品 id、`quantity` 代表产品数量。

【问题】将两个 `SELECT` 语句结合起来，以便从 `OrderItems` 表中检索产品 id（`prod_id`）和 `quantity`。其中，一个 `SELECT` 语句过滤数量为 100 的行，另一个 `SELECT` 语句过滤 id 以 BNBG 开头的产品，最后按产品 id 对结果进行升序排序。 注意：**这次仅使用单个 SELECT 语句。**

要求只用一条 select 语句，那就用 `or` 不用 `union` 了。

```sql
SELECT prod_id, quantity
FROM OrderItems
WHERE quantity = 100 OR prod_id LIKE 'BNBG%'
ORDER BY prod_id;
```

**相关解释：** [将两个 SELECT 语句结合起来（一）](SQL%E6%9F%A5%E8%AF%A2%E4%B8%8E%E7%BB%83%E4%B9%A0-01.md#kbd3783b5d833)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L1727)，来源许可：Apache-2.0。

<a id="k1b2fe84481b6"></a>

## 得分不小于平均分的最低分

**描述**： 请从试卷作答记录表中找到 SQL 试卷得分不小于该类试卷平均得分的用户最低得分。

示例数据 exam_record 表（uid 用户 ID, exam_id 试卷 ID, start_time 开始作答时间, submit_time 交卷时间, score 得分）：

| id  | uid  | exam_id | start_time          | submit_time         | score  |
| --- | ---- | ------- | ------------------- | ------------------- | ------ |
| 1   | 1001 | 9001    | 2020-01-02 09:01:01 | 2020-01-02 09:21:01 | 80     |
| 2   | 1002 | 9001    | 2021-09-05 19:01:01 | 2021-09-05 19:40:01 | 89     |
| 3   | 1002 | 9002    | 2021-09-02 12:01:01 | (NULL)              | (NULL) |
| 4   | 1002 | 9003    | 2021-09-01 12:01:01 | (NULL)              | (NULL) |
| 5   | 1002 | 9001    | 2021-02-02 19:01:01 | 2021-02-02 19:30:01 | 87     |
| 6   | 1002 | 9002    | 2021-05-05 18:01:01 | 2021-05-05 18:59:02 | 90     |
| 7   | 1003 | 9002    | 2021-02-06 12:01:01 | (NULL)              | (NULL) |
| 8   | 1003 | 9003    | 2021-09-07 10:01:01 | 2021-09-07 10:31:01 | 86     |
| 9   | 1004 | 9003    | 2021-09-06 12:01:01 | (NULL)              | (NULL) |

`examination_info` 表（`exam_id` 试卷 ID, `tag` 试卷类别, `difficulty` 试卷难度, `duration` 考试时长, `release_time` 发布时间）

示例输出数据：

| min_score_over_avg |
| ------------------ |
| 87                 |

**解释**：试卷 9001 和 9002 为 SQL 类别，作答这两份试卷的得分有[80,89,87,90]，平均分为 86.5，不小于平均分的最小分数为 87

**思路**：这类题目第一眼看确实很复杂， 因为不知道从哪入手，但是当我们仔细读题审题后，要学会抓住题干中的关键信息。以本题为例：`请从试卷作答记录表中找到SQL试卷得分不小于该类试卷平均得分的用户最低得分。`你能一眼从中提取哪些有效信息来作为解题思路？

第一条：找到==SQL==试卷得分

第二条：该类试卷==平均得分==

第三条：该类试卷的==用户最低得分==

然后中间的 “桥梁” 就是==不小于==

将条件拆分后，先逐步完成

```sql
-- 找出tag为‘SQL’的得分   【80, 89,87,90】
-- 再算出这一组的平均得分
select  ROUND(AVG(score), 1) from  examination_info info INNER JOIN exam_record record
	where info.exam_id = record.exam_id
	and tag= 'SQL'
```

然后再找出该类试卷的最低得分，接着将结果集`【80, 89,87,90】` 去和平均分数作比较，方可得出最终答案。

**答案**：

```sql
SELECT MIN(score) AS min_score_over_avg
FROM examination_info info
INNER JOIN exam_record record
WHERE info.exam_id = record.exam_id
  AND tag= 'SQL'
  AND score >=
    (SELECT ROUND(AVG(score), 1)
     FROM examination_info info
     INNER JOIN exam_record record
     WHERE info.exam_id = record.exam_id
       AND tag= 'SQL' )
```

其实这类题目给出的要求看似很 “绕”，但其实仔细梳理一遍，将大条件拆分成小条件，逐个拆分完以后，最后将所有条件拼凑起来。反正只要记住：**抓主干，理分支**，问题便迎刃而解。

**相关解释：** [未完成试卷数大于 1 的有效用户（较难）](SQL%E6%9F%A5%E8%AF%A2%E4%B8%8E%E7%BB%83%E4%B9%A0-01.md#k6f525d23bebe)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-03.md#L289)，来源许可：Apache-2.0。

<a id="ka7cf33769f73"></a>

## 按照数量和价格排序

假设有一个 `OrderItems` 表：

| quantity | item_price |
| -------- | ---------- |
| 1        | 100        |
| 10       | 1003       |
| 2        | 500        |

编写 SQL 语句，显示 `OrderItems` 表中的数量（`quantity`）和价格（`item_price`），并按数量由多到少、价格由高到低排序。

```sql
SELECT quantity, item_price
FROM OrderItems
ORDER BY quantity DESC,item_price DESC
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L140)，来源许可：Apache-2.0。

<a id="kb59b51e33fa2"></a>

## 插入记录（一）

**描述**：牛客后台会记录每个用户的试卷作答记录到 `exam_record` 表，现在有两个用户的作答记录详情如下：

- 用户 1001 在 2021 年 9 月 1 日晚上 10 点 11 分 12 秒开始作答试卷 9001，并在 50 分钟后提交，得了 90 分；
- 用户 1002 在 2021 年 9 月 4 日上午 7 点 1 分 2 秒开始作答试卷 9002，并在 10 分钟后退出了平台。

试卷作答记录表`exam_record`中，表已建好，其结构如下，请用一条语句将这两条记录插入表中。

**答案**：

```sql
// 存在自增主键，无需手动赋值
INSERT INTO exam_record (uid, exam_id, start_time, submit_time, score) VALUES
(1001, 9001, '2021-09-01 22:11:12', '2021-09-01 23:01:12', 90),
(1002, 9002, '2021-09-04 07:01:02', NULL, NULL);
```

**相关解释：** [删除记录（一）](SQL%E6%9F%A5%E8%AF%A2%E4%B8%8E%E7%BB%83%E4%B9%A0-01.md#k91763ebbc08b)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-02.md#L26)，来源许可：Apache-2.0。

<a id="ke5888f8eb901"></a>

## 插入记录（三）

**描述**：现在有一套 ID 为 9003 的高难度 SQL 试卷，时长为一个半小时，请你将 2021-01-01 00:00:00 作为发布时间插入到试题信息表`examination_info`，不管该 ID 试卷是否存在，都要插入成功，请尝试插入它。

试题信息表`examination_info`：

| Filed        | Type        | Null | Key | Extra          | Default | Comment      |
| ------------ | ----------- | ---- | --- | -------------- | ------- | ------------ |
| id           | int(11)     | NO   | PRI | auto_increment | (NULL)  | 自增 ID      |
| exam_id      | int(11)     | NO   | UNI |                | (NULL)  | 试卷 ID      |
| tag          | varchar(32) | YES  |     |                | (NULL)  | 类别标签     |
| difficulty   | varchar(8)  | YES  |     |                | (NULL)  | 难度         |
| duration     | int(11)     | NO   |     |                | (NULL)  | 时长(分钟数) |
| release_time | datetime    | YES  |     |                | (NULL)  | 发布时间     |

**答案**：

```sql
REPLACE INTO examination_info VALUES
 (NULL, 9003, "SQL", "hard", 90, "2021-01-01 00:00:00");
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-02.md#L79)，来源许可：Apache-2.0。

<a id="kd0be68bca713"></a>

## 插入记录（二）

**描述**：现有一张试卷作答记录表`exam_record`，结构如下表，其中包含多年来的用户作答试卷记录，由于数据越来越多，维护难度越来越大，需要对数据表内容做精简，历史数据做备份。

表`exam_record`：

我们已经创建了一张新表`exam_record_before_2021`用来备份 2021 年之前的试题作答记录，结构和`exam_record`表一致，请将 2021 年之前的已完成了的试题作答纪录导入到该表。

**答案**：

```sql
INSERT INTO exam_record_before_2021 (uid, exam_id, start_time, submit_time, score)
SELECT uid,exam_id,start_time,submit_time,score
FROM exam_record
WHERE YEAR(submit_time) < 2021;
```

**相关解释：** [删除记录（一）](SQL%E6%9F%A5%E8%AF%A2%E4%B8%8E%E7%BB%83%E4%B9%A0-01.md#k91763ebbc08b)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-02.md#L53)，来源许可：Apache-2.0。

<a id="k44f92d5cd7af"></a>

## 数据库优化中有一个比较常用的手段就是把数据表进行拆分，关于拆分数据表你了解哪些？

拆分其实又分**垂直拆分**和**水平拆分**

案例： 简单购物系统暂设涉及如下表：

1.产品表（数据量10w，稳定）

2.订单表（数据量200w，且有增长趋势）

3.用户表 （数据量100w，且有增长趋势）

以 MySQL 为例讲述下水平拆分和垂直拆分，MySQL能容忍的数量级在百万静态数据可以到千万

**垂直拆分**

解决问题：表与表之间的io竞争

不解决问题：单表中数据量增长出现的压力

方案： 把产品表和用户表放到一个server上 订单表单独放到一个server上

**水平拆分**

解决问题：单表中数据量增长出现的压力

不解决问题：表与表之间的io争夺

方案：**用户表** 通过性别拆分为男用户表和女用户表，**订单表** 通过已完成和完成中拆分为已完成订单和未完成订单，**产品表** 未完成订单放一个server上，已完成订单表盒男用户表放一个server上，女用户表放一个server上(女的爱购物 哈哈)。

<p  id="为什么索引要使用树而不是树或者红黑树"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-01-03-MySQL.md#L154)，来源许可：Apache-2.0。

<a id="k32cceac91ad8"></a>

## 更新记录（一）

**描述**：现在有一张试卷信息表 `examination_info`, 表结构如下图所示：

| Filed        | Type     | Null | Key | Extra          | Default | Comment  |
| ------------ | -------- | ---- | --- | -------------- | ------- | -------- |
| id           | int(11)  | NO   | PRI | auto_increment | (NULL)  | 自增 ID  |
| exam_id      | int(11)  | NO   | UNI |                | (NULL)  | 试卷 ID  |
| tag          | char(32) | YES  |     |                | (NULL)  | 类别标签 |
| difficulty   | char(8)  | YES  |     |                | (NULL)  | 难度     |
| duration     | int(11)  | NO   |     |                | (NULL)  | 时长     |
| release_time | datetime | YES  |     |                | (NULL)  | 发布时间 |

请把**examination_info**表中`tag`为`PYTHON`的`tag`字段全部修改为`Python`。

**思路**：这题有两种解题思路，最容易想到的是直接`update + where`来指定条件更新，第二种就是根据要修改的字段进行查找替换

**答案一**：

```sql
UPDATE examination_info SET tag = 'Python' WHERE tag='PYTHON'
```

**答案二**：

```sql
UPDATE examination_info
SET tag = REPLACE(tag,'PYTHON','Python')

# REPLACE (目标字段，"查找内容","替换内容")
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-02.md#L101)，来源许可：Apache-2.0。

<a id="kdabb02910213"></a>

## 更新记录（二）

**描述**：现有一张试卷作答记录表 exam_record，其中包含多年来的用户作答试卷记录，结构如下表：作答记录表 `exam_record`： **`submit_time`** 为 完成时间 （注意这句话）

**题目要求**：请把 `exam_record` 表中 2021 年 9 月 1 日==之前==开始作答的==未完成==记录全部改为被动完成，即：将完成时间改为'2099-01-01 00:00:00'，分数改为 0。

**思路**：注意题干中的关键字(已经高亮) `" xxx 时间 "`之前这个条件， 那么这里马上就要想到要进行时间的比较 可以直接 `xxx_time < "2021-09-01 00:00:00",` 也可以采用`date()`函数来进行比较；第二个条件就是 `"未完成"`， 即完成时间为 NULL，也就是题目中的提交时间 ----- `submit_time 为 NULL`。

**答案**：

```sql
UPDATE exam_record SET submit_time = '2099-01-01 00:00:00', score = 0 WHERE DATE(start_time) < "2021-09-01" AND submit_time IS null
```

**相关解释：** [删除记录（一）](SQL%E6%9F%A5%E8%AF%A2%E4%B8%8E%E7%BB%83%E4%B9%A0-01.md#k91763ebbc08b)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-02.md#L133)，来源许可：Apache-2.0。

<a id="k0efa64fbaab8"></a>

## 月均完成试卷数不小于 3 的用户爱作答的类别（较难）

**描述**：现有试卷作答记录表 `exam_record`（`uid`：用户 ID, `exam_id`：试卷 ID, `start_time`：开始作答时间, `submit_time`：交卷时间，没提交的话为 NULL, `score`：得分），示例数据如下：

| id  | uid  | exam_id | start_time          | submit_time         | score  |
| --- | ---- | ------- | ------------------- | ------------------- | ------ |
| 1   | 1001 | 9001    | 2021-07-02 09:01:01 | (NULL)              | (NULL) |
| 2   | 1002 | 9003    | 2021-09-01 12:01:01 | 2021-09-01 12:21:01 | 60     |
| 3   | 1002 | 9002    | 2021-09-02 12:01:01 | 2021-09-02 12:31:01 | 70     |
| 4   | 1002 | 9001    | 2021-09-05 19:01:01 | 2021-09-05 19:40:01 | 81     |
| 5   | 1002 | 9002    | 2021-07-06 12:01:01 | (NULL)              | (NULL) |
| 6   | 1003 | 9003    | 2021-09-07 10:01:01 | 2021-09-07 10:31:01 | 86     |
| 7   | 1003 | 9003    | 2021-09-08 12:01:01 | 2021-09-08 12:11:01 | 40     |
| 8   | 1003 | 9001    | 2021-09-08 13:01:01 | (NULL)              | (NULL) |
| 9   | 1003 | 9002    | 2021-09-08 14:01:01 | (NULL)              | (NULL) |
| 10  | 1003 | 9003    | 2021-09-08 15:01:01 | (NULL)              | (NULL) |
| 11  | 1005 | 9001    | 2021-09-01 12:01:01 | 2021-09-01 12:31:01 | 88     |
| 12  | 1005 | 9002    | 2021-09-01 12:01:01 | 2021-09-01 12:31:01 | 88     |
| 13  | 1005 | 9002    | 2021-09-02 12:11:01 | 2021-09-02 12:31:01 | 89     |

试卷信息表 `examination_info`（`exam_id`：试卷 ID, `tag`：试卷类别, `difficulty`：试卷难度, `duration`：考试时长, `release_time`：发布时间），示例数据如下：

| id  | exam_id | tag  | difficulty | duration | release_time        |
| --- | ------- | ---- | ---------- | -------- | ------------------- |
| 1   | 9001    | SQL  | hard       | 60       | 2020-01-01 10:00:00 |
| 2   | 9002    | C++  | easy       | 60       | 2020-02-01 10:00:00 |
| 3   | 9003    | 算法 | medium     | 80       | 2020-08-02 10:00:00 |

请从表中统计出 “当月均完成试卷数”不小于 3 的用户们爱作答的类别及作答次数，按次数降序输出，示例输出如下：

| tag  | tag_cnt |
| ---- | ------- |
| C++  | 4       |
| SQL  | 2       |
| 算法 | 1       |

**解释**：用户 1002 和 1005 在 2021 年 09 月的完成试卷数目均为 3，其他用户均小于 3；然后用户 1002 和 1005 作答过的试卷 tag 分布结果按作答次数降序排序依次为 C++、SQL、算法。

**思路**：这题考察联合子查询，重点在于`月均回答>=3`, 但是个人认为这里没有表述清楚，应该直接说查 9 月的就容易理解多了；这里不是每个月都要>=3 或者是所有答题次数/答题月份。不要理解错误了。

先查询出哪些用户月均答题大于三次

```sql
SELECT UID
FROM exam_record record
GROUP BY UID,
         MONTH (start_time)
HAVING count(submit_time) >= 3
```

有了这一步之后再进行深入，只要能理解上一步(我的意思是不被题目中的月均所困扰)，然后再套一个子查询，查哪些用户包含其中，然后查出题目中所需的列即可。记得排序！！

```sql
SELECT tag,
       count(start_time) AS tag_cnt
FROM exam_record record
INNER JOIN examination_info info ON record.exam_id = info.exam_id
WHERE UID IN
    (SELECT UID
     FROM exam_record record
     GROUP BY UID,
              MONTH (start_time)
     HAVING count(submit_time) >= 3)
GROUP BY tag
ORDER BY tag_cnt DESC
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-03.md#L595)，来源许可：Apache-2.0。

<a id="k08a87162c68e"></a>

## 未完成率较高的 50%用户近三个月答卷情况（困难）

**描述**：

现有用户信息表 `user_info`（`uid` 用户 ID，`nick_name` 昵称, `achievement` 成就值, `level` 等级, `job` 职业方向, `register_time` 注册时间）：

| id  | uid  | nick_name    | achievement | level | job  | register_time       |
| --- | ---- | ------------ | ----------- | ----- | ---- | ------------------- |
| 1   | 1001 | 牛客 1 号    | 3200        | 7     | 算法 | 2020-01-01 10:00:00 |
| 2   | 1002 | 牛客 2 号    | 2500        | 6     | 算法 | 2020-01-01 10:00:00 |
| 3   | 1003 | 牛客 3 号 ♂ | 2200        | 5     | 算法 | 2020-01-01 10:00:00 |

试卷信息表 `examination_info`（`exam_id` 试卷 ID, `tag` 试卷类别, `difficulty` 试卷难度, `duration` 考试时长, `release_time` 发布时间）：

| id  | exam_id | tag    | difficulty | duration | release_time        |
| --- | ------- | ------ | ---------- | -------- | ------------------- |
| 1   | 9001    | SQL    | hard       | 60       | 2020-01-01 10:00:00 |
| 2   | 9002    | SQL    | hard       | 80       | 2020-01-01 10:00:00 |
| 3   | 9003    | 算法   | hard       | 80       | 2020-01-01 10:00:00 |
| 4   | 9004    | PYTHON | medium     | 70       | 2020-01-01 10:00:00 |

试卷作答记录表 `exam_record`（`uid` 用户 ID, `exam_id` 试卷 ID, `start_time` 开始作答时间, `submit_time` 交卷时间, `score` 得分）：

| id  | uid  | exam_id | start_time          | submit_time         | score |
| --- | ---- | ------- | ------------------- | ------------------- | ----- |
| 1   | 1001 | 9001    | 2020-01-01 09:01:01 | 2020-01-01 09:21:59 | 90    |
| 15  | 1002 | 9001    | 2020-01-01 18:01:01 | 2020-01-01 18:59:02 | 90    |
| 13  | 1001 | 9001    | 2020-01-02 10:01:01 | 2020-01-02 10:31:01 | 89    |
| 2   | 1002 | 9001    | 2020-01-20 10:01:01 |                     |       |
| 3   | 1002 | 9001    | 2020-02-01 12:11:01 |                     |       |
| 5   | 1001 | 9001    | 2020-03-01 12:01:01 |                     |       |
| 6   | 1002 | 9001    | 2020-03-01 12:01:01 | 2020-03-01 12:41:01 | 90    |
| 4   | 1003 | 9001    | 2020-03-01 19:01:01 |                     |       |
| 7   | 1002 | 9001    | 2020-05-02 19:01:01 | 2020-05-02 19:32:00 | 90    |
| 14  | 1001 | 9002    | 2020-01-01 12:11:01 |                     |       |
| 8   | 1001 | 9002    | 2020-01-02 19:01:01 | 2020-01-02 19:59:01 | 69    |
| 9   | 1001 | 9002    | 2020-02-02 12:01:01 | 2020-02-02 12:20:01 | 99    |
| 10  | 1002 | 9002    | 2020-02-02 12:01:01 |                     |       |
| 11  | 1002 | 9002    | 2020-02-02 12:01:01 | 2020-02-02 12:43:01 | 81    |
| 12  | 1002 | 9002    | 2020-03-02 12:11:01 |                     |       |
| 17  | 1001 | 9002    | 2020-05-05 18:01:01 |                     |       |
| 16  | 1002 | 9003    | 2020-05-06 12:01:01 |                     |       |

请统计 SQL 试卷上未完成率较高的 50%用户中，6 级和 7 级用户在有试卷作答记录的近三个月中，每个月的答卷数目和完成数目。按用户 ID、月份升序排序。

由示例数据结果输出如下：

| uid  | start_month | total_cnt | complete_cnt |
| ---- | ----------- | --------- | ------------ |
| 1002 | 202002      | 3         | 1            |
| 1002 | 202003      | 2         | 1            |
| 1002 | 202005      | 2         | 1            |

解释：各个用户对 SQL 试卷的未完成数、作答总数、未完成率如下：

| uid  | incomplete_cnt | total_cnt | incomplete_rate |
| ---- | -------------- | --------- | --------------- |
| 1001 | 3              | 7         | 0.4286          |
| 1002 | 4              | 8         | 0.5000          |
| 1003 | 1              | 1         | 1.0000          |

1001、1002、1003 分别排在 1.0、0.5、0.0 的位置，因此较高的 50%用户（排位<=0.5）为 1002、1003；

1003 不是 6 级或 7 级；

有试卷作答记录的近三个月为 202005、202003、202002；

这三个月里 1002 的作答题数分别为 3、2、2，完成数目分别为 1、1、1。

**思路：**

注意点：这题注意求的是所有的答题次数和完成次数，而 sql 类别的试卷是限制未完成率排名，6, 7 级用户限制的是做题记录。

先求出未完成率的排名

```sql
SELECT UID,
       count(submit_time IS NULL
             OR NULL)/ count(start_time) AS num,
       PERCENT_RANK() OVER (
                            ORDER BY count(submit_time IS NULL
                                           OR NULL)/ count(start_time)) AS ranking
FROM exam_record
LEFT JOIN examination_info USING (exam_id)
WHERE tag = 'SQL'
GROUP BY UID
```

再求出最近三个月的练习记录

```sql
SELECT UID,
       date_format(start_time, '%Y%m') AS month_d,
       submit_time,
       exam_id,
       dense_rank() OVER (PARTITION BY UID
                          ORDER BY date_format(start_time, '%Y%m') DESC) AS ranking
FROM exam_record
LEFT JOIN user_info USING (UID)
WHERE LEVEL IN (6,7)
```

**答案**：

```sql
SELECT t1.uid,
       t1.month_d,
       count(*) AS total_cnt,
       count(t1.submit_time) AS complete_cnt
FROM-- 先求出未完成率的排名

  (SELECT UID,
          count(submit_time IS NULL OR NULL)/ count(start_time) AS num,
          PERCENT_RANK() OVER (
                               ORDER BY count(submit_time IS NULL OR NULL)/ count(start_time)) AS ranking
   FROM exam_record
   LEFT JOIN examination_info USING (exam_id)
   WHERE tag = 'SQL'
   GROUP BY UID) t
INNER JOIN
  (-- 再求出近三个月的练习记录
 SELECT UID,
        date_format(start_time, '%Y%m') AS month_d,
        submit_time,
        exam_id,
        dense_rank() OVER (PARTITION BY UID
                           ORDER BY date_format(start_time, '%Y%m') DESC) AS ranking
   FROM exam_record
   LEFT JOIN user_info USING (UID)
   WHERE LEVEL IN (6,7) ) t1 USING (UID)
WHERE t1.ranking <= 3 AND t.ranking >= 0.5 -- 使用限制找到符合条件的记录

GROUP BY t1.uid,
         t1.month_d
ORDER BY t1.uid,
         t1.month_d
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-04.md#L298)，来源许可：Apache-2.0。

<a id="k6f525d23bebe"></a>

## 未完成试卷数大于 1 的有效用户（较难）

**描述**：现有试卷作答记录表 `exam_record`（`uid` 用户 ID, `exam_id` 试卷 ID, `start_time` 开始作答时间, `submit_time` 交卷时间, `score` 得分），示例数据如下：

| id  | uid  | exam_id | start_time          | submit_time         | score  |
| --- | ---- | ------- | ------------------- | ------------------- | ------ |
| 1   | 1001 | 9001    | 2021-07-02 09:01:01 | 2021-07-02 09:21:01 | 80     |
| 2   | 1002 | 9001    | 2021-09-05 19:01:01 | 2021-09-05 19:40:01 | 81     |
| 3   | 1002 | 9002    | 2021-09-02 12:01:01 | (NULL)              | (NULL) |
| 4   | 1002 | 9003    | 2021-09-01 12:01:01 | (NULL)              | (NULL) |
| 5   | 1002 | 9001    | 2021-07-02 19:01:01 | 2021-07-02 19:30:01 | 82     |
| 6   | 1002 | 9002    | 2021-07-05 18:01:01 | 2021-07-05 18:59:02 | 90     |
| 7   | 1003 | 9002    | 2021-07-06 12:01:01 | (NULL)              | (NULL) |
| 8   | 1003 | 9003    | 2021-09-07 10:01:01 | 2021-09-07 10:31:01 | 86     |
| 9   | 1004 | 9003    | 2021-09-06 12:01:01 | (NULL)              | (NULL) |
| 10  | 1002 | 9003    | 2021-09-01 12:01:01 | 2021-09-01 12:31:01 | 81     |
| 11  | 1005 | 9001    | 2021-09-01 12:01:01 | 2021-09-01 12:31:01 | 88     |
| 12  | 1006 | 9002    | 2021-09-02 12:11:01 | 2021-09-02 12:31:01 | 89     |
| 13  | 1007 | 9002    | 2020-09-02 12:11:01 | 2020-09-02 12:31:01 | 89     |

还有一张试卷信息表 `examination_info`（`exam_id` 试卷 ID, `tag` 试卷类别, `difficulty` 试卷难度, `duration` 考试时长, `release_time` 发布时间），示例数据如下：

| id  | exam_id | tag  | difficulty | duration | release_time        |
| --- | ------- | ---- | ---------- | -------- | ------------------- |
| 1   | 9001    | SQL  | hard       | 60       | 2020-01-01 10:00:00 |
| 2   | 9002    | SQL  | easy       | 60       | 2020-02-01 10:00:00 |
| 3   | 9003    | 算法 | medium     | 80       | 2020-08-02 10:00:00 |

请统计 2021 年每个未完成试卷作答数大于 1 的有效用户的数据（有效用户指完成试卷作答数至少为 1 且未完成数小于 5），输出用户 ID、未完成试卷作答数、完成试卷作答数、作答过的试卷 tag 集合，按未完成试卷数量由多到少排序。示例数据的输出结果如下：

| uid  | incomplete_cnt | complete_cnt | detail                                                                      |
| ---- | -------------- | ------------ | --------------------------------------------------------------------------- |
| 1002 | 2              | 4            | 2021-09-01:算法;2021-07-02:SQL;2021-09-02:SQL;2021-09-05:SQL;2021-07-05:SQL |

**解释**：2021 年的作答记录中，除了 1004，其他用户均满足有效用户定义，但只有 1002 未完成试卷数大于 1，因此只输出 1002，detail 中是 1002 作答过的试卷{日期:tag}集合，日期和 tag 间用 **:** 连接，多元素间用 **;** 连接。

**思路：**

仔细读题后，分析出：首先要联表，因为后面要输出`tag`；

筛选出 2021 年的数据

```sql
SELECT *
FROM exam_record er
LEFT JOIN examination_info ei ON er.exam_id = ei.exam_id
WHERE YEAR (er.start_time)= 2021
```

根据 uid 进行分组，然后对每个用户进行条件进行判断，题目中要求`完成试卷数至少为1,未完成试卷数要大于1，小于5`

那么等会儿写 sql 的时候条件应该是：`未完成 > 1 and 已完成 >=1 and 未完成 < 5`

因为最后要用到字符串的拼接，而且还要组合拼接，这个可以用`GROUP_CONCAT`函数，下面简单介绍一下该函数的用法：

基本格式：

```sql
GROUP_CONCAT([DISTINCT] expr [ORDER BY {unsigned_integer | col_name | expr} [ASC | DESC] [, ...]]             [SEPARATOR sep])
```

- `expr`：要连接的列或表达式。
- `DISTINCT`：可选参数，用于去重。当指定了 `DISTINCT`，相同的值只会出现一次。
- `ORDER BY`：可选参数，用于排序连接后的值。可以选择升序 (`ASC`) 或降序 (`DESC`) 排序。
- `SEPARATOR sep`：可选参数，用于设置连接后的值的分隔符。（本题要用这个参数设置 ; 号 ）

`GROUP_CONCAT()` 函数常用于 `GROUP BY` 子句中，将一组行的值连接为一个字符串，并在结果集中以聚合的形式返回。

**答案**：

```sql
SELECT a.uid,
       SUM(CASE
               WHEN a.submit_time IS NULL THEN 1
           END) AS incomplete_cnt,
       SUM(CASE
               WHEN a.submit_time IS NOT NULL THEN 1
           END) AS complete_cnt,
       GROUP_CONCAT(DISTINCT CONCAT(DATE_FORMAT(a.start_time, '%Y-%m-%d'), ':', b.tag)
                    ORDER BY start_time SEPARATOR ";") AS detail
FROM exam_record a
LEFT JOIN examination_info b ON a.exam_id = b.exam_id
WHERE YEAR (a.start_time)= 2021
GROUP BY a.uid
HAVING incomplete_cnt > 1
AND complete_cnt >= 1
AND incomplete_cnt < 5
ORDER BY incomplete_cnt DESC
```

- `SUM(CASE WHEN a.submit_time IS NULL THEN 1 END)` 统计了每个用户未完成的记录数量。
- `SUM(CASE WHEN a.submit_time IS NOT NULL THEN 1 END)` 统计了每个用户已完成的记录数量。
- `GROUP_CONCAT(DISTINCT CONCAT(DATE_FORMAT(a.start_time, '%Y-%m-%d'), ':', b.tag) ORDER BY a.start_time SEPARATOR ';')` 将每个用户的考试日期和标签以逗号分隔的形式连接成一个字符串，并按考试开始时间进行排序。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-03.md#L499)，来源许可：Apache-2.0。
