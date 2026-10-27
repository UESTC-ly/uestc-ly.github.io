# 数据库与SQL

本章以 MySQL 8.4 的 InnoDB 为主要实现背景。关系模型、SQL 语义和 SQL 标准隔离级别属于更通用的概念；引擎的索引、Read View 与锁行为需要另外注明，不能把不同层次的回答直接拼在一起。

<a id="m932a4974b446"></a>

## 关系模型、约束与范式

关系型数据库把数据组织成表，并用键、约束和事务维护关联。主键标识一行，唯一约束防止某组值重复，外键表达并限制引用关系；这些约束与应用层“先查再插”不同，能够在并发提交时提供数据库侧的最终检查。

范式主要减少因事实重复存储而产生的更新、插入和删除异常。规范化有助于维护一致性，但业务查询也可能为了读取成本采用适度冗余。反范式需要同时设计冗余字段的更新与校正机制，不能把“少一次 JOIN”直接当作无代价的优化。先确定事实归属与唯一性，再决定如何为访问路径建立派生数据。

来源：[wolverinn/Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Database.md#L163)。

<a id="mb60d3e3e8e62"></a>

## 一条 SQL 的执行路径

查询通常先经过连接与权限检查、语法分析和语义处理，再由优化器选择执行方案，最后由执行器按方案调用存储引擎获取数据。优化器决定连接次序、访问索引和部分转换；存储引擎负责实际的数据页、记录、锁与事务实现，因此“SQL 一样”不保证每次都选择同一计划。

分析性能时要定位时间花在哪一层：等锁、扫描过多、排序、回表、网络传输或连接资源不足，不能统一归因于“没有索引”。MySQL 8 已移除早期的查询缓存，旧架构图里的查询缓存步骤不能直接用于现代版本。预处理和缓冲池也不是同一个缓存概念。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L231)；[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L560)。

<a id="me6a6cf5458ae"></a>

## B+ 树索引为何适合数据库

磁盘和内存之间通常按页交换数据，索引的目标是减少查找需要触达的页数。B+ 树的内部节点主要保存键和子节点指针，一页可以容纳较多分支，从而降低树高；叶子保存有序条目并便于范围扫描。查等值、取区间、按键有序读取可以复用同一结构。

哈希结构对等值定位有优势，但不天然提供范围顺序；二叉平衡树每节点分支少，直接映射到页存储时可能需要更深路径。索引不是免费副本：写入还要维护它，占用空间并增加页分裂或合并等成本。是否建索引要结合过滤能力、更新频率和实际查询方式。

来源：[forthespada/InterviewGuide](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-01-03-MySQL.md#L187)；[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L445)。

<a id="mf3b7e59789f7"></a>

## 聚簇索引、二级索引与覆盖查询

InnoDB 的聚簇索引叶子保存整行记录，通常按主键组织；二级索引叶子保存自己的索引键及主键值。通过二级索引找到主键后，再沿聚簇索引取得其他列，称为回表。若查询所需的列已能从所选索引获得，则可形成覆盖访问，减少额外读取。

主键的长度会影响二级索引的空间成本，主键是否连续也会影响插入位置与页维护。覆盖索引描述一次查询与索引的关系，不是独立的树种类，也不意味着任何情况下都不会访问聚簇记录。不要把 `SELECT *` 机械等同于“索引失效”；它通常影响覆盖机会和优化器成本选择。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L476)；[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L539)。

<a id="me980e8bac32f"></a>

## 联合索引与最左前缀

联合索引按列次序构成字典序。对于 `(a,b,c)`，先按 a 排序，同一个 a 内再按 b、c 排序；因此约束 a 后更容易继续收窄 b 的区间，而只约束 b 往往无法直接定位完整的连续区间。最左前缀解释的是这种排序结构，不是优化器必须遵守的一条简单口令。

遇到范围条件后，后续列通常不能继续把所有结果压缩成一个更小的连续扫描区间，但仍可能参与索引条件下推、过滤或覆盖查询。函数、隐式转换、前导通配符等是否影响访问，要看表达式、比较类型、索引类型和版本。应通过执行计划验证“扫描范围是否变大、是否回表、如何排序”，而不是把所有情况概括成“后面的索引都失效”。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L484)；[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L551)。

<a id="ma7fc08fa0437"></a>

## 执行计划与慢 SQL 的定位顺序

执行计划展示数据库预计如何获取结果，重点看访问路径、连接次序、估计扫描行数、过滤比例，以及是否需要额外排序或临时表。估计成本来自统计信息，分布变化或列间相关性可能让估计失准，所以需要在适当环境结合实际执行指标核实。

先确认 SQL、参数和慢的时间范围，再区分锁等待与执行开销；之后检查是否读了远多于返回结果的数据。优化可从缩小结果、改写不必要的计算、调整索引、减少回表和改善分页着手。线上诊断还要观察并发与资源竞争；单次测试很快并不代表高并发下仍快。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L966)；[wolverinn/Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Database.md#L335)。

<a id="mdfe42275d0da"></a>

## 事务 ACID 与业务不变量

事务把一组数据库操作组织成一个提交单位。原子性让部分失败能回滚；持久性描述提交后的保存保证；隔离性限制并发操作之间的相互影响；一致性要求操作在约束和业务规则下把合法状态变成合法状态。这里的一致性不是“所有事务每次都读到相同数值”。

转账等操作需要把相关更新放进同一事务，并保证余额、唯一性等规则确实被检查。事务不能自动修复错误业务逻辑，持久性也受到存储、刷盘配置和故障模型影响。事务边界应尽量短，避免长时间持锁或占用连接；与外部服务的原子协作不能仅靠本地 `COMMIT` 获得。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L606)；[wolverinn/Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Database.md#L33)。

<a id="mbeb600e43254"></a>

## 隔离级别与并发异常

脏读涉及未提交的数据；不可重复读关注同一记录在再次读取时变化；幻读关注同一条件的结果集合发生变化。SQL 标准通过不同隔离级别限制这些现象，但具体数据库可以提供更强的某些行为。丢失更新又涉及读后写入的竞争，不能仅靠背一张异常表判断业务安全。

InnoDB 默认通常是可重复读，但会话与部署可修改。其普通一致性读通过 MVCC 维持快照，锁定读另用锁约束并发。可串行化要求效果等价于某个串行次序，不表示数据库只能逐个执行整笔事务。回答隔离问题时必须同时说明数据库、隔离级别、普通读还是锁定读，不能把标准 RR 与 InnoDB 的具体防幻读手段混为一谈。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L740)；[MySQL 8.4 隔离级别](https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html)。

<a id="md77bc1ff049c"></a>

## MVCC、Read View 与快照读

MVCC 通过记录的多个版本，让读取能够避开某些读写冲突。InnoDB 使用事务信息、undo 中的旧版本与 Read View 的可见性判断，决定当前查询能看到哪个版本。它不是简单地给每行附两个“创建版本、删除版本”字段就完成所有判断。

在读已提交下，每次一致性读建立新的视图；在可重复读下，同一事务通常复用首次一致性读建立的视图，显式一致性快照可改变建立时机。因此“RR 一律从 BEGIN 时刻取快照”不准确。事务也能看到自己的修改。普通一致性读与 `FOR UPDATE` 等锁定读走不同协议，后者不能当作固定快照查询来推理。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L865)；[MySQL 8.4 隔离级别](https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html)。

<a id="m42d54a862990"></a>

## 记录锁、间隙锁与 Next-Key Lock

InnoDB 的锁定读和写操作通过索引记录上的锁协调并发。记录锁保护已有索引记录；间隙锁主要限制范围内插入；Next-Key Lock 把记录与其前方间隙组合起来。在可重复读中，范围锁定扫描常用它限制符合条件的新记录出现。

锁住什么取决于隔离级别、所用索引、查询范围和唯一性等条件。唯一索引对唯一记录的精确查找可只锁记录，但缺失记录、复合条件或范围查询不能直接套用这个结论。未命中合适索引可能扫描并锁定大量记录，这不等于引擎自动把所有情况都转换成一把表锁。分析阻塞要还原实际扫描路径与锁范围。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L801)；[MySQL 8.4 InnoDB 锁](https://dev.mysql.com/doc/refman/8.4/en/innodb-locking.html)。

<a id="meb83d61988f5"></a>

## 乐观并发控制与悲观锁

悲观方案先获得适当的锁再操作共享数据，让冲突者等待或失败；乐观方案先读取并计算，在提交更新时检查前提是否仍成立。典型乐观更新将旧版本号写进 `WHERE`，同时增加版本号，通过受影响行数判断是否成功。

乐观并不表示数据库执行更新时不加锁，而是业务不提前持锁等待整个计算过程。冲突频繁时反复重试可能比等待更贵；冲突较少且计算可重做时，版本校验能缩短占锁时间。扣库存还可把“库存足够”条件放进一条更新，避免读写之间的窗口；跨多行不变量则需进一步设计事务和锁顺序。

来源：[wolverinn/Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Database.md#L58)。

<a id="m6efb01b71345"></a>

## 死锁、锁等待与重试

死锁是多个事务形成循环等待，单向等待则只是阻塞。行锁并发度高也可能死锁，特别是事务以不同次序访问多条记录时。数据库检测死锁后可能回滚某个事务，让其余事务继续；业务必须能识别并按安全边界重试。

减少死锁可从统一访问顺序、缩短事务、减少锁范围与合理索引入手。重试要重新执行整个必要事务，而不是只重发失败的一条中间 SQL；外部副作用需要幂等保护。排查时保存当时的事务、SQL、索引和等待关系，不能把提高锁等待超时当作解决循环依赖的手段。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L784)；[MySQL 8.4 死锁处理](https://dev.mysql.com/doc/refman/8.4/en/innodb-deadlocks-handling.html)。

<a id="m70f91170dc82"></a>

## redo、undo 与 binlog 的职责

redo 面向故障恢复，帮助把已记录的修改重做到数据页；undo 提供回滚所需的信息，也为一致性读重建旧版本；binlog 在服务器层记录变更事件，常用于复制与基于日志的恢复。三者关注的目标不同，不能因都叫日志而相互替代。

提交过程需要协调引擎状态与 binlog，避免恢复后出现两边对事务是否提交的判断不一致。是否能承受操作系统或设备故障，还取决于日志落盘策略、硬件保证及复制方式。面试应说明恢复链路，而不是只背“redo 物理、binlog 逻辑”：实际事件格式和 redo 内容也有实现细节。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L596)。

<a id="m57adc30fcd6a"></a>

## 主从复制与读写分离的一致性

复制把源端的变更传给副本，再由副本应用。异步链路中，网络、日志接收和回放都可能产生延迟，所以主库刚提交并不保证从库立即可读到。读写分离是在访问层分配读写请求，不会自动消除这种可见性差距。

对“写完马上读”的请求，可按业务选择读主库、携带位点等待副本追上或接受有界延迟。读流量分摊需要考虑热点、连接和查询成本，而不只是增加副本数量。主库故障切换还要处理可能的数据缺口、客户端连接与路由变化，复制也不能代替能够按历史时间恢复的备份。

来源：[doocs/advanced-java](https://github.com/doocs/advanced-java/blob/80b89fb9496d7ea3213e402c8c3853399e00c363/docs/high-concurrency/mysql-read-write-separation.md#L17)；[wolverinn/Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Database.md#L388)。

<a id="m5339121c9749"></a>

## 分库分表与分片键

分库分表把数据和负载分散到不同存储单元，目的是突破单实例容量、吞吐或维护成本边界。分片键决定请求能否直接定位分片，也决定数据分布是否均匀。按用户分片便于用户范围访问，却可能让跨用户统计变成多分片聚合。

分片会引入跨分片事务、关联查询、全局唯一性、分页归并和扩容迁移的成本，因此应先验证单库优化、归档、读副本和业务拆分能否满足需求。设计时同时说明路由、热点、扩容和校验方案，不能把“加一个取模”当作完整解决方案。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L1015)；[doocs/advanced-java](https://github.com/doocs/advanced-java/blob/80b89fb9496d7ea3213e402c8c3853399e00c363/docs/high-concurrency/database-shard.md#L1)。

<a id="m348265319c73"></a>

## JOIN、聚合与窗口函数的选择

JOIN 按关联条件把行组合起来；内连接保留匹配行，左连接保留左侧行并对未匹配右侧补 NULL。对右表的过滤放在 `ON` 与放在 `WHERE` 可能不同：后者会在连接完成后过滤，若排除了 NULL 补行，可能失去保留未匹配行的效果。

`GROUP BY` 把多行汇成每组一行，窗口函数则在保留原行的同时计算组内排名、累计值等。求每组最新记录时，先明确并列如何处理，再选择排名函数或关联策略。聚合前后的过滤也要区分：`WHERE` 过滤输入行，`HAVING` 过滤聚合结果。

来源：[wolverinn/Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Database.md#L186)；[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/sql/sql-questions-01.md#L1)。

<a id="m19b081b7822c"></a>

## 深分页与稳定排序

`LIMIT offset,size` 通常需要先读取并跳过前 offset 条符合顺序的数据，页码越深，丢弃的工作越多。若还需要大量回表，成本会继续放大。索引覆盖、先定位主键再回表等方案能减少部分代价，却不会自动消除跳过大量记录的本质。

游标翻页使用上一页最后一条的排序键继续向后查询，适合连续浏览。排序键必须稳定且足以打破并列，例如时间加唯一 ID；否则可能重复或漏项。它与任意跳到第 N 页的能力不同，应按产品访问方式选择，而不是把两者视为同一种分页语义。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/high-performance/high-performance-system-interview-questions.md#L81)。

<a id="m84afe98c24c1"></a>

## 字段类型、NULL 与精确计算

字段类型同时约束表示范围、比较方式和存储成本。精确金额通常用合适精度的 `DECIMAL` 或明确单位的整数，而不是依赖二进制浮点表示十进制金额；手机号等标识符要保留前导零与格式，也不应仅因全是数字就选整数。

NULL 表示缺失或未知，不等于空串或零。一般比较运算遇到 NULL 可能得到未知，过滤只保留结果为真的行；判断空值应使用明确的空值语义。`COUNT(*)` 统计结果行，`COUNT(col)` 不统计该列为 NULL 的行。连接、唯一约束和聚合对 NULL 的具体行为还应按数据库规则判断，不能把它当成一个普通值随意替换。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L121)；[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L176)。

## 专题阅读

- [SQL查询与练习（1）](SQL%E6%9F%A5%E8%AF%A2%E4%B8%8E%E7%BB%83%E4%B9%A0-01.md)
- [SQL查询与练习（2）](SQL%E6%9F%A5%E8%AF%A2%E4%B8%8E%E7%BB%83%E4%B9%A0-02.md)
- [SQL查询与练习（3）](SQL%E6%9F%A5%E8%AF%A2%E4%B8%8E%E7%BB%83%E4%B9%A0-03.md)
- [事务、锁与MVCC](%E4%BA%8B%E5%8A%A1%E3%80%81%E9%94%81%E4%B8%8EMVCC.md)
- [存储、日志与复制](%E5%AD%98%E5%82%A8%E3%80%81%E6%97%A5%E5%BF%97%E4%B8%8E%E5%A4%8D%E5%88%B6.md)
- [数据库综合问答](%E6%95%B0%E6%8D%AE%E5%BA%93%E7%BB%BC%E5%90%88%E9%97%AE%E7%AD%94.md)
- [数据模型与数据库基础（1）](%E6%95%B0%E6%8D%AE%E6%A8%A1%E5%9E%8B%E4%B8%8E%E6%95%B0%E6%8D%AE%E5%BA%93%E5%9F%BA%E7%A1%80-01.md)
- [数据模型与数据库基础（2）](%E6%95%B0%E6%8D%AE%E6%A8%A1%E5%9E%8B%E4%B8%8E%E6%95%B0%E6%8D%AE%E5%BA%93%E5%9F%BA%E7%A1%80-02.md)
- [索引与查询优化](%E7%B4%A2%E5%BC%95%E4%B8%8E%E6%9F%A5%E8%AF%A2%E4%BC%98%E5%8C%96.md)
