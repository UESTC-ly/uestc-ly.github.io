# 事务、锁与MVCC

<a id="kff197a27c31d"></a>

## MongoDB 事务

> MongoDB 事务想要搞懂原理还是比较花费时间的，我自己也没有搞太明白。因此，我这里只是简单介绍一下 MongoDB 事务，想要了解原理的小伙伴，可以自行搜索查阅相关资料。
>
> 这里推荐几篇文章，供大家参考：
>
> - [技术干货| MongoDB 事务原理](https://mongoing.com/archives/82187)
> - [MongoDB 一致性模型设计与实现](https://developer.aliyun.com/article/782494)
> - [MongoDB 官方文档对事务的介绍](https://www.mongodb.com/docs/upcoming/core/transactions/)

我们在介绍 NoSQL 数据的时候也说过，NoSQL 数据库通常不支持事务，为了可扩展和高性能进行了权衡。不过，也有例外，MongoDB 就支持事务。

与关系型数据库一样，MongoDB 事务同样具有 ACID 特性：

- **原子性**（`Atomicity`）：事务是最小的执行单位，不允许分割。事务的原子性确保动作要么全部完成，要么完全不起作用；
- **一致性**（`Consistency`）：执行事务前后，数据保持一致，例如转账业务中，无论事务是否成功，转账者和收款人的总额应该是不变的；
- **隔离性**（`Isolation`）：并发访问数据库时，一个用户的事务不被其他事务所干扰，各并发事务之间数据库是独立的。WiredTiger 存储引擎支持读未提交（ read-uncommitted ）、读已提交（ read-committed ）和快照（ snapshot ）隔离，MongoDB 启动时默认选快照隔离。在不同隔离级别下，一个事务的生命周期内，可能出现脏读、不可重复读、幻读等现象。
- **持久性**（`Durability`）：一个事务被提交之后。它对数据库中数据的改变是持久的，即使数据库发生故障也不应该对其有任何影响。

关于事务的详细介绍这篇文章就不多说了，感兴趣的可以看看我写的[MySQL 常见面试题总结](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md)这篇文章，里面有详细介绍到。

MongoDB 单文档原生支持原子性，也具备事务的特性。当谈论 MongoDB 事务的时候，通常指的是 **多文档** 。MongoDB 4.0 加入了对多文档 ACID 事务的支持，但只支持复制集部署模式下的 ACID 事务，也就是说事务的作用域限制为一个副本集内。MongoDB 4.2 引入了 **分布式事务** ，增加了对分片集群上多文档事务的支持，并合并了对副本集上多文档事务的现有支持。

根据官方文档介绍：

> 从 MongoDB 4.2 开始，分布式事务和多文档事务在 MongoDB 中是一个意思。分布式事务是指分片集群和副本集上的多文档事务。从 MongoDB 4.2 开始，多文档事务（无论是在分片集群还是副本集上）也称为分布式事务。

在大多数情况下，多文档事务比单文档写入会产生更大的性能成本。对于大部分场景来说， [非规范化数据模型（嵌入式文档和数组）](https://www.mongodb.com/docs/upcoming/core/data-model-design/#std-label-data-modeling-embedding) 依然是最佳选择。也就是说，适当地对数据进行建模可以最大限度地减少对多文档事务的需求。

**注意**：

- 从 MongoDB 4.2 开始，多文档事务支持副本集和分片集群，其中：主节点使用 WiredTiger 存储引擎，同时从节点使用 WiredTiger 存储引擎或 In-Memory 存储引擎。在 MongoDB 4.0 中，只有使用 WiredTiger 存储引擎的副本集支持事务。
- 在 MongoDB 4.2 及更早版本中，你无法在事务中创建集合。从 MongoDB 4.4 开始，您可以在事务中创建集合和索引。有关详细信息，请参阅 [在事务中创建集合和索引](https://www.mongodb.com/docs/upcoming/core/transactions/#std-label-transactions-create-collections-indexes)。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mongodb/mongodb-questions-01.md#L235)，来源许可：Apache-2.0。

<a id="k17af8c006101"></a>

## MySQL 的事务隔离级别有哪些？如何保证一致性？

**回答：**

MySQL 标准事务隔离级别有四个：读未提交、读已提交、可重复读、串行化。

读未提交允许读取其他事务未提交的数据，会出现脏读，实际很少使用。读已提交只能读到已提交数据，避免脏读，但同一事务中两次读取同一行可能结果不同，会出现不可重复读。可重复读保证同一事务内多次一致性读看到相同快照，是 InnoDB 默认隔离级别，依靠 MVCC 和必要的锁避免很多并发异常。串行化隔离级别最强，事务近似串行执行，通常通过加锁实现，性能最低。

一致性可以从 ACID 理解。原子性由 undo log 保证，事务失败可以回滚。持久性由 redo log 保证，提交后的修改即使宕机也能恢复。一致性是目标，依赖原子性、隔离性、持久性以及约束、触发器、业务逻辑共同保证。隔离性由锁和 MVCC 保证。

在 InnoDB 中，普通一致性读主要靠 MVCC 读快照，写操作和当前读依赖行锁、间隙锁、next-key lock 等控制并发。除此之外，binlog 和 redo log 的两阶段提交保证主从复制和崩溃恢复之间的一致性。

面试中可以总结：事务一致性不是单个机制保证的，而是 undo log、redo log、锁、MVCC、约束和两阶段提交共同保证的。

<a id="bytedance-ai-agent-hard-20260602-q17"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%AD%97%E8%8A%82%E8%B7%B3%E5%8A%A8%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L633)，来源许可：GPL-3.0。

<a id="kf91a998643c2"></a>

## MySQL 的隔离级别是基于锁实现的吗？

MySQL 的隔离级别基于锁和 MVCC 机制共同实现的。

SERIALIZABLE 隔离级别是通过锁来实现的，READ-COMMITTED 和 REPEATABLE-READ 隔离级别是基于 MVCC 实现的。不过， SERIALIZABLE 之外的其他隔离级别可能也需要用到锁机制，就比如 REPEATABLE-READ 在当前读情况下需要使用加锁读来保证不会出现幻读。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L774)，来源许可：Apache-2.0。

<a id="k51c84ff534c8"></a>

## MySQL 的默认隔离级别是什么?

MySQL InnoDB 存储引擎的默认隔离级别是 **REPEATABLE READ**。可以通过以下命令查看：

- MySQL 8.0 之前：`SELECT @@tx_isolation;`
- MySQL 8.0 及之后：`SELECT @@transaction_isolation;`

```sql
mysql> SELECT @@tx_isolation;
+-----------------+
| @@tx_isolation  |
+-----------------+
| REPEATABLE-READ |
+-----------------+
```

关于 MySQL 事务隔离级别的详细介绍，可以看看我写的这篇文章：[MySQL 事务隔离级别详解](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/transaction-isolation-level.md)。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L756)，来源许可：Apache-2.0。

<a id="kb5b7ec9adbd2"></a>

## MySQL 都有哪些锁？它们的作用分别是什么？

**回答：**

MySQL 锁可以按层次和用途分类。

全局锁会锁住整个数据库实例，典型命令是 `Flush tables with read lock`，常用于全库逻辑备份，但会影响写入。

表级锁锁住整张表，例如 MyISAM 常用表锁，InnoDB 也有表级意向锁和元数据锁。元数据锁 MDL 用于保护表结构，防止查询过程中表结构被修改。意向锁包括 IS 和 IX，用来表示事务准备在表中某些行上加共享锁或排他锁，方便表锁和行锁之间做冲突判断。

行级锁是 InnoDB 并发控制的核心。记录锁锁住索引记录本身；间隙锁锁住索引记录之间的间隙，防止其他事务插入造成幻读；next-key lock 是记录锁加间隙锁，锁住一个左开右闭区间；插入意向锁表示事务想在某个 gap 中插入记录，多个插入不同位置的事务可以并发。

按读写关系还可以分为共享锁和排他锁。共享锁允许多个事务同时读，但阻塞写；排他锁用于写操作，会阻塞其他读写锁请求。

还有自增锁，用于处理 auto_increment 分配；在不同配置下可以有不同的锁粒度。对于外键约束、唯一索引检查，也会引入相应的锁行为。

面试中要强调：InnoDB 行锁是加在索引上的。如果查询条件没有命中索引，可能扫描更多记录并加更多锁，甚至表现得像锁表。锁的目的不是单纯互斥，而是配合隔离级别解决脏写、不可重复读、幻读和并发一致性问题。

<a id="bytedance-ai-agent-hard-20260602-q20"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%AD%97%E8%8A%82%E8%B7%B3%E5%8A%A8%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L680)，来源许可：GPL-3.0。

<a id="k019bf3e05faf"></a>

## MySQL中为什么要有事务回滚机制？

而在 MySQL 中，恢复机制是通过回滚日志（undo log）实现的，所有事务进行的修改都会先记录到这个回滚日志中，然后在对数据库中的对应行进行写入。 当事务已经被提交之后，就无法再次回滚了。

回滚日志作用：
1、能够在发生错误或者用户执行 ROLLBACK 时提供回滚相关的信息

2、在整个系统发生崩溃、数据库进程直接被杀死后，当用户再次启动数据库进程时，还能够立刻通过查询回滚日志将之前未完成的事务进行回滚，这也就需要回滚日志必须先于数据持久化到磁盘上，是我们需要先写日志后写数据库的主要原因。

<p  id="数据库引擎的区别"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-01-01-MySQL.md#L252)，来源许可：Apache-2.0。

<a id="k90e72e572d4f"></a>

## MySQL的 ACID，分别解释一下

**原⼦性：** 事务是最⼩的执⾏单位，不允许分割。事务的原⼦性确保动作要么全部完成，要么全不执行

**一致性：** 执⾏事务前后，数据保持⼀致，多个事务对同⼀个数据读取的结果是相同的

 **隔离性：** 并发访问数据库时，⼀个⽤户的事务不被其他事务所⼲扰，各并发事务之间数据库是独⽴的

 **持久性：** ⼀个事务被提交之后。它对数据库中数据的改变是持久的，即使数据库发⽣故障也不应该对其有任何影响

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/02-programming-languages/Java/java-fundamentals.md#L250)，来源许可：GPL-3.0。

<a id="kf20380b7991d"></a>

## 不可重复读和幻读区别是什么？可以举个例子吗？

**不可重复读的重点是修改，幻读的重点在于新增或者删除。**

例1（同样的条件, 你读取过的数据, 再次读取出来发现值不一样了 ）：事务1中的A先生读取自己的工资为 1000的操作还没完成，事务2中的B先生就修改了A的工资为2000，导致A再读自己的工资时工资变为 2000；这就是不可重复读。

例2（同样的条件, 第1次和第2次读出来的记录数不一样 ）：假某工资单表中工资大于3000的有4人，事务1读取了所有工资大于3000的人，共查到4条记录，这时事务2 又插入了一条工资大于3000的记录，事务1再次读取时查到的记 录就变为了5条，这样就导致了幻读。

<p  id="有四种索引类型可以简单说说吗"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-01-01-MySQL.md#L373)，来源许可：Apache-2.0。

<a id="k4059daf9a2ab"></a>

## 不可重复读和幻读有什么区别？

- 不可重复读：同一事务内，同一条记录被其他事务修改或删除，导致再次读取时记录内容或存在性发生变化。
- 幻读：同一事务内，同一个范围条件查询多次执行时，符合条件的记录集合发生变化，出现新增或消失的记录。

幻读其实可以看作是不可重复读的一种特殊情况，单独把幻读区分出来的原因主要是解决幻读和不可重复读的方案不一样。

举个例子：执行 `delete` 和 `update` 操作的时候，可以直接对记录加锁，保证事务安全。而执行 `insert` 操作的时候，由于记录锁（Record Lock）只能锁住已经存在的记录，为了避免插入新记录，需要依赖间隙锁（Gap Lock）。也就是说执行 `insert` 操作的时候需要依赖 Next-Key Lock（Record Lock+Gap Lock） 进行加锁来保证不出现幻读。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L711)，来源许可：Apache-2.0。

<a id="ke365ed2f0ffd"></a>

## 事务ACID、隔离级别和MVCC在Agent任务系统中有什么价值？

事务是一个不可分割的数据库操作序列，要么全部成功，要么全部失败。ACID分别是：

| 特性 | 含义 | Agent场景 |
| --- | --- | --- |
| 原子性 | 要么全做，要么全不做 | 创建任务、扣费、写状态必须一起成功 |
| 一致性 | 事务前后满足约束 | 任务状态不能从失败跳回运行中 |
| 隔离性 | 并发事务互不干扰 | 多worker不能重复领取同一任务 |
| 持久性 | 提交后可靠保存 | Agent执行记录可恢复、可审计 |

隔离级别用于控制并发下的脏读、不可重复读、幻读等问题。工程中常用的是读已提交和可重复读。隔离级别越高，一致性越强，但并发性能可能越低。

MVCC（多版本并发控制）的核心思想是：读操作读取某个版本快照，写操作生成新版本，读写尽量不互相阻塞。它适合读多写少的业务，例如查询Agent任务状态、读取用户配置、查看RAG文档元数据。

在Agent任务系统中，常见写法是用数据库事务实现“领取任务”：

```sql
UPDATE tasks
SET status = 'running', worker_id = 'worker-1'
WHERE id = 1001 AND status = 'pending';
```

如果影响行数为1，说明领取成功；如果为0，说明已被其他worker领取。这比在应用层先查再改更安全。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%95%B0%E6%8D%AE%E5%BA%93%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L53)，来源许可：GPL-3.0。

<a id="kcd419a825929"></a>

## 事务四大特性（ACID）原子性、一致性、隔离性、持久性？

**常见问法：** 事务四大特性（ACID）原子性、一致性、隔离性、持久性？：第二种回答；事务四大特性（ACID）原子性、一致性、隔离性、持久性？：第一种回答

### **第一种回答**

**原子性**：

一个事务（transaction）中的所有操作，要么全部完成，要么全部不完成，不会结束在中间某个环节。
。事务在执行过程中发生错误，会被恢复（Rollback）到事务开始前的状态，就像这个事务从来没有执行过一样。

**一致性**：

在事务开始之前和事务结束以后，数据库的完整性没有被破坏。这表示写入的资料必须完全符合所有的预设规则，这包含资料的精确度、串联性以及后续数据库可以自发性地完成预定的工作。

**隔离性**：

数据库允许多个并发事务同时对其数据进行读写和修改的能力，隔离性可以防止多个事务并发执行时由于交叉执行而导致数据的不一致。事务隔离分为不同级别，包括读未提交（Read uncommitted）、读提交（read committed）、可重复读（repeatable read）和串行化（Serializable）。

**持久性**：

事务处理结束后，对数据的修改就是永久的，即便系统故障也不会丢失。

### **第二种回答**

**原子性（Atomicity）**

原子性是指事务包含的所有操作要么全部成功，要么全部失败回滚，因此事务的操作如果成功就必须要完全应用到数据库，如果操作失败则不能对数据库有任何影响。

**一致性（Consistency）**

事务开始前和结束后，数据库的完整性约束没有被破坏。比如A向B转账，不可能A扣了钱，B却没收到。

**隔离性（Isolation）**

隔离性是当多个用户并发访问数据库时，比如操作同一张表时，数据库为每一个用户开启的事务，不能被其他事务的操作所干扰，多个并发事务之间要相互隔离。

同一时间，只允许一个事务请求同一数据，不同的事务之间彼此没有任何干扰。比如A正在从一张银行卡中取钱，在A取钱的过程结束前，B不能向这张卡转账。

关于事务的隔离性数据库也提供了多种隔离级别，可以根据实际情况选择合适的级别。  

 **持久性（Durability）**

持久性是指一个事务一旦被提交了，那么对数据库中的数据的改变就是永久性的，即便是在数据库系统遇到故障的情况下也不会丢失提交事务的操作。

<p  id="两个函数有什么区别"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-01-02-MySQL.md#L232)，来源许可：Apache-2.0。
- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-01-02-MySQL.md#L255)，来源许可：Apache-2.0。
- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-01-02-MySQL.md#L234)，来源许可：Apache-2.0。

<a id="kb1ff3ff7f978"></a>

## 什么是 MVCC？

多版本并发控制（Multi-Version Concurrency Control, MVCC），MVCC在每行记录后面都保存有两个隐藏的列，用来存储**创建版本号**和**删除版本号**。

- 创建版本号：创建一个数据行时的事务版本号（**事务版本号**：事务开始时的系统版本号；系统版本号：每开始一个新的事务，系统版本号就会自动递增）；
- 删除版本号：删除操作时的事务版本号；
- 各种操作：
  - 插入操作时，记录创建版本号；
  - 删除操作时，记录删除版本号；
  - 更新操作时，先记录删除版本号，再新增一行记录创建版本号；
  - 查询操作时，要符合以下条件才能被查询出来：删除版本号未定义或大于当前事务版本号（删除操作是在当前事务启动之后做的）；创建版本号小于或等于当前事务版本号（创建操作是事务完成或者在事务启动之前完成）

通过版本号减少了锁的争用，**提高了系统性能**；可以实现**提交读**和**可重复读**两种隔离级别，未提交读无需使用MVCC

快照读与当前读

使用 MVCC 读取的是快照中的数据，这样可以减少加锁所带来的开销：

```
select * from table ...;
```

当前读读取的是最新的数据，需要加锁。以下第一个语句需要加 S 锁，其它都需要加 X 锁：

```
select * from table where ? lock in share mode;
select * from table where ? for update;
insert;
update;
delete;
```

### 参考资料

- [Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Database.md#L128)，来源许可：GPL-3.0。

<a id="k91a61cc3f423"></a>

## 什么是三级封锁协议？

- 一级封锁协议：事务在修改数据之前必须先对其加X锁，直到事务结束才释放。可以解决丢失修改问题（两个事务不能同时对一个数据加X锁，避免了修改被覆盖）；
- 二级封锁协议：在一级的基础上，事务在读取数据之前必须先加S锁，读完后释放。可以解决脏读问题（如果已经有事务在修改数据，就意味着已经加了X锁，此时想要读取数据的事务并不能加S锁，也就无法进行读取，避免了读取脏数据）；
- 三级封锁协议：在二级的基础上，事务在读取数据之前必须先加S锁，直到事务结束才能释放。可以解决不可重复读问题（避免了在事务结束前其它事务对数据加X锁进行修改，保证了事务期间数据不会被其它事务更新）

### 参考资料

- [Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Database.md#L107)，来源许可：GPL-3.0。

<a id="k1b5466e3b583"></a>

## 什么是两段锁协议？

事务必须严格分为两个阶段对数据进行**加锁和解锁**的操作，第一阶段加锁，第二阶段解锁。也就是说一个事务中一旦释放了锁，就不能再申请新锁了。

**可串行化调度**是指，通过并发控制，使得并发执行的事务结果与某个串行执行的事务结果相同。事务遵循两段锁协议是保证可串行化调度的充分条件。

### 参考资料

- [Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Database.md#L122)，来源许可：GPL-3.0。

<a id="k3d5bb832e2a3"></a>

## 什么是数据库事务？

大多数情况下，我们在谈论事务的时候，如果没有特指**分布式事务**，往往指的就是**数据库事务**。

数据库事务在我们日常开发中接触的最多了。如果你的项目属于单体架构的话，你接触到的往往就是数据库事务了。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L628)，来源许可：Apache-2.0。

<a id="ke79e9a79adc9"></a>

## 介绍 MVCC

`MVCC` 是一种多版本并发控制机制，在大多数情况下代替行级锁，使用 `MVCC`，能降低其系统开销。`MVCC` 是通过保存数据在某个时间点的快照来实现的.。不同存储引擎的 `MVCC` 实现是不同的，典型的有乐观并发控制和悲观并发控制。`InnoDB` 的 `MVCC` 是通过在每行记录后面保存两个隐藏的列来实现的，这两个列，分别保存了这个行的创建时间，一个保存的是行的删除时间。这里存储的并不是实际的时间值，而是系统版本号(可以理解为事务的 `ID`)，每开始一个新的事务，系统版本号就会自动递增，事务开始时刻的系统版本号会作为事务的 `ID`。`InnoDB` 只会查找版本早于当前事务版本的数据行(也就是行的系统版本号小于或等于事务的系统版本号)，这样可以确保事务读取的行，要么是在事务开始前已经存在的，要么是事务自身插入或者修改过的。

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/02-programming-languages/Java/java-fundamentals.md#L217)，来源许可：GPL-3.0。

<a id="kf621880a801c"></a>

## 何为事务？ 一言蔽之，事务是逻辑上的一组操作，要么都执行，要么都不执行。

事务最经典也经常被拿出来说例子就是转账了。假如小明要给小红转账 1000 元，这个转账会涉及到两个关键操作，这两个操作必须都成功或者都失败。

1. 将小明的余额减少 1000 元
2. 将小红的余额增加 1000 元。

事务会把这两个操作就可以看成逻辑上的一个整体，这个整体包含的操作要么都成功，要么都要失败。这样就不会出现小明余额减少而小红的余额却并没有增加的情况。

![事务示意图](https://oss.javaguide.cn/github/javaguide/mysql/%E4%BA%8B%E5%8A%A1%E7%A4%BA%E6%84%8F%E5%9B%BE.png)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L617)，来源许可：Apache-2.0。

<a id="ka684999f715f"></a>

## 共享锁和排他锁呢？

不论是表级锁还是行级锁，都存在共享锁（Share Lock，S 锁）和排他锁（Exclusive Lock，X 锁）这两类：

排他锁与任何的锁都不兼容，共享锁仅和共享锁兼容。

|      | S 锁   | X 锁 |
| :--- | :----- | :--- |
| S 锁 | 不冲突 | 冲突 |
| X 锁 | 冲突   | 冲突 |

由于 MVCC 的存在，对于一般的 `SELECT` 语句，InnoDB 不会加任何锁。不过， 你可以通过以下语句显式加共享锁或排他锁。

```sql
# 共享锁 可以在 MySQL 5.7 和 MySQL 8.0 中使用
SELECT ... LOCK IN SHARE MODE;
# 共享锁 可以在 MySQL 8.0 中使用
SELECT ... FOR SHARE;
# 排他锁
SELECT ... FOR UPDATE;
```

**相关解释：** [并发事务的控制方式有哪些？](%E4%BA%8B%E5%8A%A1%E3%80%81%E9%94%81%E4%B8%8EMVCC.md#k35bd7af8c907)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L811)，来源许可：Apache-2.0。

<a id="k0d6dd8359468"></a>

## 四种隔离级别的实现原理？

- 未提交读（Read Uncommited）：啥都不做。；
- （一级封锁协议 ----> 解决丢失修改）；
- 提交读（Read Commited）：二级封锁协议 ----> 解决脏读。；
- 可重复读（Repeatable Read）:  三级封锁协议 ----> 解决不可重复读。；
- 可串行化（Serializable）：强制事务串行执行 ----> 解决幻读问题。；
- （其中提交读和可重复读也可以由MVCC实现）；

### 参考资料

- [Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Database.md#L113)，来源许可：GPL-3.0。

<a id="k7682d880b926"></a>

## 在高并发写入场景下，MySQL 的间隙锁可能造成什么问题？

**回答：**

InnoDB 间隙锁作用于索引记录之间的间隙，主要抑制向该区间插入记录。默认可重复读隔离级别下，部分锁定读和写操作会使用 next-key locking，即记录锁与间隙锁的组合，以保护搜索范围。普通一致性快照读通常通过 MVCC 工作，不应笼统说“范围 SELECT 都会加间隙锁”。

例如事务执行 `SELECT ... WHERE tenant_id = 10 AND created_at >= ? FOR UPDATE`，具体锁范围由实际使用的索引、扫描边界和记录分布共同决定，不是 SQL 文本中的逻辑条件自动映射为精确最小锁范围。没有合适索引或扫描范围过大，可能阻塞大量本来希望并发执行的插入。

高并发下主要出现锁等待、事务超时、队列堆积与死锁。不同事务持有的纯间隙锁可以兼容，但插入时申请的插入意向锁仍可能被阻塞；“双方都先锁住空区间，再尝试插入”就可能形成等待环。死锁不是只有更新同一行才会出现。

处理顺序是：查看 `performance_schema.data_locks`、`data_lock_waits` 和死锁记录；把等待映射到 SQL、索引与事务；缩短事务并缩小扫描范围，统一访问顺序，避免在持锁期间调用外部服务。唯一索引上满足条件的完整唯一键等值查找可减少间隙锁使用，但查找不存在的键及部分唯一键条件需要单独分析。

READ COMMITTED 会减少搜索扫描中的间隙锁，但外键和重复键检查等场景仍有例外，且业务可观察语义改变。必须先验证业务不变量。死锁受害事务需要回滚并进行有限、带随机退避的整事务重试，同时保证业务幂等。

<a id="baidu-agent-20260922-r1-q10"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%99%BE%E5%BA%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L886)，来源许可：GPL-3.0。

<a id="ke21cbc489b10"></a>

## 常见的封锁类型？

意向锁是 InnoDB 自动加的， 不需用户干预。
对于 UPDATE、 DELETE 和 INSERT 语句， InnoDB
会自动给涉及数据集加排他锁（X)；
对于普通 SELECT 语句，InnoDB 不会加任何锁；
事务可以通过以下语句显式给记录集加共享锁或排他锁：
共享锁（S）：SELECT * FROM table_name WHERE ... LOCK IN SHARE MODE。 其他 session 仍然可以查询记录，并也可以对该记录加 share mode 的共享锁。但是如果当前事务需要对该记录进行更新操作，则很有可能造成死锁。
排他锁（X)：SELECT * FROM table_name WHERE ... FOR UPDATE。其他 session 可以查询该记录，但是不能对该记录加共享锁或排他锁，而是等待获得锁

- **排它锁**（Exclusive Lock）/ X锁：事务对数据加上X锁时，只允许此事务读取和修改此数据，并且其它事务不能对该数据加任何锁；
- **共享锁**（Shared Lock）/ S锁：加了S锁后，该事务只能对数据进行读取而不能修改，并且其它事务只能加S锁，不能加X锁
- **意向锁**（Intention Locks）：
  - 一个事务在获得某个**数据行**对象的 S 锁之前，必须先获得**整个表**的 IS 锁或更强的锁；
  - 一个事务在获得某个数据行对象的 X 锁之前，必须先获得整个表的 IX 锁；
  - IS/IX 锁之间都是兼容的；
  - 好处：如果一个事务想要对整个表加X锁，就需要先检测是否有其它事务对该表或者该表中的某一行加了锁，这种检测非常耗时。有了意向锁之后，只需要检测整个表是否存在IX/IS/X/S锁就行了

锁的作用：用于管理对共享资源的并发访问，保证数据库的完整性和一致性

封锁粒度的概念

MySQL 中提供了两种封锁粒度：**行级锁**以及**表级锁**。

封锁粒度小：

- 好处：锁定的数据量越少，发生锁争用的可能就越小，系统的**并发程度**就越高；
- 坏处：**系统开销**大（加锁、释放锁、检查锁的状态都需要消耗资源）

MySQL加锁

```
SELECT ... LOCK In SHARE MODE;
SELECT ... FOR UPDATE;
```

### 参考资料

- [Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Database.md#L65)，来源许可：GPL-3.0。

<a id="kf2a4f268eb5f"></a>

## 并发事务带来了哪些问题?

在典型的应用程序中，多个事务并发运行，经常会操作相同的数据来完成各自的任务（多个用户对同一数据进行操作）。并发虽然是必须的，但可能会导致以下的问题。

### 脏读（Dirty read）

一个事务读取数据并且对数据进行了修改，这个修改对其他事务来说是可见的，即使当前事务没有提交。这时另外一个事务读取了这个还未提交的数据，但第一个事务突然回滚，导致数据并没有被提交到数据库，那第二个事务读取到的就是脏数据，这也就是脏读的由来。

例如：事务 1 读取某表中的数据 A=20，事务 1 修改 A=A-1，事务 2 读取到 A = 19,事务 1 回滚导致对 A 的修改并未提交到数据库， A 的值还是 20。

![脏读](https://oss.javaguide.cn/github/javaguide/database/mysql/concurrency-consistency-issues-dirty-reading.png)

### 丢失修改（Lost to modify）

在一个事务读取一个数据时，另外一个事务也访问了该数据，那么在第一个事务中修改了这个数据后，第二个事务也修改了这个数据。这样第一个事务内的修改结果就被丢失，因此称为丢失修改。

例如：事务 1 读取某表中的数据 A=20，事务 2 也读取 A=20，事务 1 先修改 A=A-1，事务 2 后来也修改 A=A-1，最终结果 A=19，事务 1 的修改被丢失。

![丢失修改](https://oss.javaguide.cn/github/javaguide/database/mysql/concurrency-consistency-issues-missing-modifications.png)

### 不可重复读（Unrepeatable read）

指在一个事务内多次读同一数据。在这个事务还没有结束时，另一个事务也访问该数据。那么，在第一个事务中的两次读数据之间，由于第二个事务的修改导致第一个事务两次读取的数据可能不太一样。这就发生了在一个事务内两次读到的数据是不一样的情况，因此称为不可重复读。

例如：事务 1 读取某表中的数据 A=20，事务 2 也读取 A=20，事务 1 修改 A=A-1，事务 2 再次读取 A =19，此时读取的结果和第一次读取的结果不同。

![不可重复读](https://oss.javaguide.cn/github/javaguide/database/mysql/concurrency-consistency-issues-unrepeatable-read.png)

### 幻读（Phantom read）

幻读与不可重复读类似。它发生在一个事务读取了几行数据，接着另一个并发事务插入了一些数据时。在随后的查询中，第一个事务就会发现多了一些原本不存在的记录，就好像发生了幻觉一样，所以称为幻读。

例如：事务 2 读取某个范围的数据，事务 1 在这个范围插入了新的数据，事务 2 再次读取这个范围的数据发现相比于第一次读取的结果多了新的数据。

![幻读](https://oss.javaguide.cn/github/javaguide/database/mysql/concurrency-consistency-issues-phantom-read.png)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L675)，来源许可：Apache-2.0。

<a id="k35bd7af8c907"></a>

## 并发事务的控制方式有哪些？

MySQL 中并发事务的控制方式无非就两种：**锁** 和 **MVCC**。锁可以看作是悲观控制的模式，多版本并发控制（MVCC，Multiversion concurrency control）可以看作是乐观控制的模式。

**锁** 控制方式下会通过锁来显式控制共享资源而不是通过调度手段，MySQL 中主要是通过 **读写锁** 来实现并发控制。

- **共享锁（S 锁）**：又称读锁，事务在读取记录的时候获取共享锁，允许多个事务同时获取（锁兼容）。
- **排他锁（X 锁）**：又称写锁/独占锁，事务在修改记录的时候获取排他锁，不允许多个事务同时获取。如果一个记录已经被加了排他锁，那其他事务不能再对这条记录加任何类型的锁（锁不兼容）。

读写锁可以做到读读并行，但是无法做到写读、写写并行。另外，根据根据锁粒度的不同，又被分为 **表级锁(table-level locking)** 和 **行级锁(row-level locking)** 。InnoDB 不光支持表级锁，还支持行级锁，默认为行级锁。行级锁的粒度更小，仅对相关的记录上锁即可（对一行或者多行记录加锁），所以对于并发写入操作来说， InnoDB 的性能更高。不论是表级锁还是行级锁，都存在共享锁（Share Lock，S 锁）和排他锁（Exclusive Lock，X 锁）这两类。

**MVCC** 是多版本并发控制方法，即对一份数据会存储多个版本，通过事务的可见性来保证事务能看到自己应该看到的版本。通常会有一个全局的版本分配器来为每一行数据设置版本号，版本号是唯一的。

MVCC 在 MySQL 中实现所依赖的手段主要是: **隐藏字段、read view、undo log**。

- undo log : undo log 用于记录某行数据的多个版本的数据。
- read view 和 隐藏字段 : 用来判断当前版本数据的可见性。

关于 InnoDB 对 MVCC 的具体实现可以看这篇文章：[InnoDB 存储引擎对 MVCC 的实现](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/innodb-implementation-of-mvcc.md) 。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L720)，来源许可：Apache-2.0。

<a id="k606184e06b44"></a>

## 意向锁有什么作用？

如果需要用到表锁的话，如何判断表中的记录没有行锁呢，一行一行遍历肯定是不行，性能太差。我们需要用到一个叫做意向锁的东东来快速判断是否可以对某个表使用表锁。

意向锁是表级锁，共有两种：

- **意向共享锁（Intention Shared Lock，IS 锁）**：事务有意向对表中的某些记录加共享锁（S 锁），加共享锁前必须先取得该表的 IS 锁。
- **意向排他锁（Intention Exclusive Lock，IX 锁）**：事务有意向对表中的某些记录加排他锁（X 锁），加排他锁之前必须先取得该表的 IX 锁。

**意向锁是由数据引擎自己维护的，用户无法手动操作意向锁，在为数据行加共享/排他锁之前，InnoDB 会先获取该数据行所在在数据表的对应意向锁。**

意向锁之间是互相兼容的。

|       | IS 锁 | IX 锁 |
| ----- | ----- | ----- |
| IS 锁 | 兼容  | 兼容  |
| IX 锁 | 兼容  | 兼容  |

意向锁和共享锁和排它锁互斥（这里指的是表级别的共享锁和排他锁，意向锁不会与行级的共享锁和排他锁互斥）。

|      | IS 锁 | IX 锁 |
| ---- | ----- | ----- |
| S 锁 | 兼容  | 互斥  |
| X 锁 | 互斥  | 互斥  |

《MySQL 技术内幕 InnoDB 存储引擎》这本书对应的描述应该是笔误了。

![](https://oss.javaguide.cn/github/javaguide/mysql/image-20220511171419081.png)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L836)，来源许可：Apache-2.0。

<a id="kf293cd897f18"></a>

## 数据库中的锁有了解过吗

**回答：**

以 MySQL InnoDB 为例，锁用于协调并发访问与修改；事务隔离还依赖 MVCC，因此普通快照读不一定需要对读到的每行加共享锁。需要区分一致性读、锁定读、写操作及它们在具体隔离级别下的行为。

行级锁主要作用于索引记录，包括记录锁、间隙锁和 Next-Key Lock。Next-Key Lock 结合记录及其前方间隙，在一定的范围锁定读和写场景下帮助防止幻读；间隙锁主要阻止向间隙插入，并非所有类型的间隙锁之间都互斥。意向锁是表级协调机制，用于声明事务计划在表内取得某类行锁，不能把它理解为自动锁住全表数据。

在常见的 Repeatable Read 配置下，范围锁定可能使用 Next-Key Lock；唯一索引的完整等值查找等场景可以更精确地锁定记录。Read Committed 对普通搜索和索引扫描的间隙锁使用更少，但外键检查、重复键检查等仍有例外。锁范围由执行路径、条件和隔离级别共同决定，缺少合适索引可能扩大扫描与锁定范围。

死锁是多个事务互相等待形成环；等待超时则不一定存在环。应统一访问顺序、缩短事务、确保更新条件有合适索引，并通过锁等待与死锁诊断定位。数据库选择事务回滚后，应用按业务语义重试整个事务，配合幂等与重试上限；不能只重新执行最后一条 SQL 就假定一致性仍然成立。

还可以补充乐观锁：通过版本号条件更新检查并发冲突，检查受影响行数并决定重试或提示冲突；它不意味着底层执行更新时完全不使用数据库锁。DDL 还涉及元数据锁，长事务可能阻塞结构变更。回答时始终限定数据库实现，不把 MySQL 的间隙锁规则推广到所有数据库。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L2542)，来源许可：GPL-3.0。

<a id="k0cd05af58822"></a>

## 数据库并发事务会带来哪些问题？

数据库并发会带来脏读、幻读、丢弃更改、不可重复读这四个常见问题，其中：

**脏读**：在第一个修改事务和读取事务进行的时候，读取事务读到的数据为100，这是修改之后的数据，但是之后该事务满足一致性等特性而做了回滚操作，那么读取事务得到的结果就是脏数据了。

**幻读**：一般是T1在某个范围内进行修改操作（增加或者删除），而T2读取该范围导致读到的数据是修改之间的了，强调范围。

**丢弃修改**：两个写事务T1 T2同时对A=0进行递增操作，结果T2覆盖T1，导致最终结果是1 而不是2，事务被覆盖

**不可重复读**：T2 读取一个数据，然后T1 对该数据做了修改。如果 T2 再次读取这个数据，此时读取的结果和第一次读取的结果不同。

### **脏读**

![脏读](https://raw.githubusercontent.com/forthespada/InterviewGuide/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-01-01-MySQL.assets/202205220024781.png)

第一个事务首先读取var变量为50，接着准备更新为100的时，并未提交，第二个事务已经读取var为100，此时第一个事务做了回滚。最终第二个事务读取的var和数据库的var不一样。

### **幻读（幻影读）**

![幻读](https://raw.githubusercontent.com/forthespada/InterviewGuide/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-01-01-MySQL.assets/202205220024132.png)

T1 读取某个范围的数据，T2 在这个范围内插入新的数据，T1 再次读取这个范围的数据，此时读取的结果和和第一次读取的结果不同。

### **丢弃修改**

![丢弃修改](https://raw.githubusercontent.com/forthespada/InterviewGuide/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-01-01-MySQL.assets/202205220024561.png)

T1 和 T2 两个事务都对一个数据进行修改，T1 先修改，T2 随后修改，T2 的修改覆盖了 T1 的修改。例如：事务1读取某表中的数据A=50，事务2也读取A=50，事务1修改A=A+50，事务2也修改A=A+50，最终结果A=100，事务1的修改被丢失。

### **不可重复读**

![不可重复读](https://raw.githubusercontent.com/forthespada/InterviewGuide/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-01-01-MySQL.assets/202205220024930.png)

T2 读取一个数据，T1 对该数据做了修改。如果 T2 再次读取这个数据，此时读取的结果和第一次读取的结果不同。

<p  id="数据库悲观锁和乐观锁的原理和应用场景分别有什么"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-01-01-MySQL.md#L292)，来源许可：Apache-2.0。

<a id="kbd1e27901875"></a>

## 数据库悲观锁和乐观锁的原理和应用场景分别有什么？

悲观锁，先获取锁，再进行业务操作，一般就是利用类似 SELECT … FOR UPDATE 这样的语句，对数据加锁，避免其他事务意外修改数据。
当数据库执行SELECT … FOR UPDATE时会获取被select中的数据行的行锁，select for update获取的行锁会在当前事务结束时自动释放，因此必须在事务中使用。

乐观锁，先进行业务操作，只在最后实际更新数据时进行检查数据是否被更新过。Java 并发包中的 AtomicFieldUpdater 类似，也是利用 CAS 机制，并不会对数据加锁，而是通过对比数据的时间戳或者版本号，来实现乐观锁需要的版本判断。

<p  id="索引主要使用的两种数据结构是什么"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-01-01-MySQL.md#L330)，来源许可：Apache-2.0。

<a id="k80da9f3ae2f2"></a>

## 数据库的四种隔离级别？

- **未提交读**（Read Uncommited）：在一个事务提交之前，它的执行结果对其它事务也是可见的。会导致脏读、不可重复读、幻读；
- **提交读**（Read Commited）：一个事务只能看见已经提交的事务所作的改变。可避免脏读问题；
- **可重复读**（Repeatable Read）：可以确保同一个事务在多次读取同样的数据时得到相同的结果。（MySQL的默认隔离级别）。可避免不可重复读；
- **可串行化**（Serializable）：强制事务串行执行，使之不可能相互冲突，从而解决幻读问题。可能导致大量的超时现象和锁竞争，实际很少使用。

### 参考资料

- [Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Database.md#L51)，来源许可：GPL-3.0。

<a id="k9e43cb41dd52"></a>

## 数据库隔离级别

- **未提交读**，事务中发生了修改，即使没有提交，其他事务也是可见的，比如对于一个数A原来50修改为100，但是我还没有提交修改，另一个事务看到这个修改，而这个时候原事务发生了回滚，这时候A还是50，但是另一个事务看到的A是100.**可能会导致脏读、幻读或不可重复读**
- **提交读**，对于一个事务从开始直到提交之前，所做的任何修改是其他事务不可见的，举例就是对于一个数A原来是50，然后提交修改成100，这个时候另一个事务在A提交修改之前，读取的A是50，刚读取完，A就被修改成100，这个时候另一个事务再进行读取发现A就突然变成100了；**可以阻止脏读，但是幻读或不可重复读仍有可能发生**
- **重复读**，就是对一个记录读取多次的记录是相同的，比如对于一个数A读取的话一直是A，前后两次读取的A是一致的；**可以阻止脏读和不可重复读，但幻读仍有可能发生**
- **可串行化读**，在并发情况下，和串行化的读取的结果是一致的，没有什么不同，比如不会发生脏读和幻读；**该级别可以防止脏读、不可重复读以及幻读**

| 隔离级别                  | 脏读 | 不可重复读 | 幻影读 |
| ------------------------- | ---- | ---------- | ------ |
| READ-UNCOMMITTED 未提交读 | √    | √          | √      |
| READ-COMMITTED 提交读     | ×    | √          | √      |
| REPEATABLE-READ 重复读    | ×    | ×          | √      |
| SERIALIZABLE 可串行化读   | ×    | ×          | ×      |

MySQL InnoDB 存储引擎的默认支持的隔离级别是 **REPEATABLE-READ**（可重读）

**这里需要注意的是**：与 SQL 标准不同的地方在于InnoDB 存储引擎在 REPEATABLE-READ（可重读）事务隔离级别 下使用的是**Next-Key Lock 锁**算法，因此可以避免幻读的产生，这与其他数据库系统(如 SQL Server)是不同的。所以 说InnoDB 存储引擎的默认支持的隔离级别是 REPEATABLE-READ（可重读） 已经可以完全保证事务的隔离性要 求，即达到了 SQL标准的SERIALIZABLE(可串行化)隔离级别。

因为隔离级别越低，事务请求的锁越少，所以大部分数据库系统的隔离级别都是READ-COMMITTED(读取提交内 容):，但是你要知道的是InnoDB 存储引擎默认使用 **REPEATABLE-READ（可重读）并不会有任何性能损失**。

InnoDB 存储引擎在分布式事务 的情况下一般会用到SERIALIZABLE(可串行化)隔离级别。

<P  id="都知道数据库索引采用原因也有很多主要原因是什么"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-01-01-MySQL.md#L192)，来源许可：Apache-2.0。

<a id="ke971d27007b5"></a>

## 是否支持 MVCC

MyISAM 不支持，而 InnoDB 支持。

讲真，这个对比有点废话，毕竟 MyISAM 连行级锁都不支持。MVCC 可以看作是行级锁的一个升级，可以有效减少加锁操作，提高性能。

**6、索引实现不一样。**

虽然 MyISAM 引擎和 InnoDB 引擎都是使用 B+Tree 作为索引结构，但是两者的实现方式不太一样。

InnoDB 引擎中，其数据文件本身就是索引文件。相比 MyISAM，索引文件和数据文件是分离的，其表数据文件本身就是按 B+Tree 组织的一个索引结构，树的叶节点 data 域保存了完整的数据记录。

详细区别，推荐你看看我写的这篇文章：[MySQL 索引详解](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-index.md)。

**7、性能有差别。**

InnoDB 的性能比 MyISAM 更强大，不管是在读写混合模式下还是只读模式下，随着 CPU 核数的增加，InnoDB 的读写能力呈线性增长。MyISAM 因为读写不能并发，它的处理能力跟核数没关系。

![InnoDB 和 MyISAM 性能对比](https://oss.javaguide.cn/github/javaguide/mysql/innodb-myisam-performance-comparison.png)

**8、数据缓存策略和机制实现不同。**

InnoDB 使用缓冲池（Buffer Pool）缓存数据页和索引页，MyISAM 使用键缓存（Key Cache）仅缓存索引页而不缓存数据页。

**总结**：

- InnoDB 支持行级别的锁粒度，MyISAM 不支持，只支持表级别的锁粒度。
- MyISAM 不提供事务支持。InnoDB 提供事务支持，实现了 SQL 标准定义了四个隔离级别。
- MyISAM 不支持外键，而 InnoDB 支持。
- MyISAM 不支持 MVCC，而 InnoDB 支持。
- 虽然 MyISAM 引擎和 InnoDB 引擎都是使用 B+Tree 作为索引结构，但是两者的实现方式不太一样。
- MyISAM 不支持数据库异常崩溃后的安全恢复，而 InnoDB 支持。
- InnoDB 的性能比 MyISAM 更强大。

最后，再分享一张图片给你，这张图片详细对比了常见的几种 MySQL 存储引擎。

![常见的几种 MySQL 存储引擎对比](https://oss.javaguide.cn/github/javaguide/mysql/comparison-of-common-mysql-storage-engines.png)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L354)，来源许可：Apache-2.0。

<a id="k28705e47ed87"></a>

## 是否支持行级锁

MyISAM 只有表级锁(table-level locking)，而 InnoDB 支持行级锁(row-level locking)和表级锁,默认为行级锁。

也就说，MyISAM 一锁就是锁住了整张表，这在并发写的情况下是多么滴憨憨啊！这也是为什么 InnoDB 在并发写的时候，性能更牛皮了！

**2、是否支持事务**

MyISAM 不提供事务支持。

InnoDB 提供事务支持，实现了 SQL 标准定义了四个隔离级别，具有提交(commit)和回滚(rollback)事务的能力。并且，InnoDB 默认使用的 REPEATABLE-READ（可重读）隔离级别是可以解决幻读问题发生的（基于 MVCC 和 Next-Key Lock）。

关于 MySQL 事务的详细介绍，可以看看我写的这篇文章：[MySQL 事务隔离级别详解](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/transaction-isolation-level.md)。

**3、是否支持外键**

MyISAM 不支持，而 InnoDB 支持。

外键对于维护数据一致性非常有帮助，但是对性能有一定的损耗。因此，通常情况下，我们是不建议在实际生产项目中使用外键的，在业务代码中进行约束即可！

阿里的《Java 开发手册》也是明确规定禁止使用外键的。

![](https://oss.javaguide.cn/github/javaguide/mysql/image-20220510090309427.png)

不过，在代码中进行约束的话，对程序员的能力要求更高，具体是否要采用外键还是要根据你的项目实际情况而定。

总结：一般我们也是不建议在数据库层面使用外键的，应用层面可以解决。不过，这样会对数据的一致性造成威胁。具体要不要使用外键还是要根据你的项目来决定。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L320)，来源许可：Apache-2.0。

<a id="kdcbc755db2bb"></a>

## 自增锁有了解吗？

> 不太重要的一个知识点，简单了解即可。

关系型数据库设计表的时候，通常会有一列作为自增主键。InnoDB 中的自增主键会涉及一种比较特殊的表级锁— **自增锁（AUTO-INC Locks）** 。

```sql
CREATE TABLE `sequence_id` (
  `id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
  `stub` CHAR(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  UNIQUE KEY `stub` (`stub`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

更准确点来说，不仅仅是自增主键，`AUTO_INCREMENT`的列都会涉及到自增锁，毕竟非主键也可以设置自增长。

如果一个事务正在插入数据到有自增列的表时，会先获取自增锁，拿不到就可能会被阻塞住。这里的阻塞行为只是自增锁行为的其中一种，可以理解为自增锁就是一个接口，其具体的实现有多种。具体的配置项为 `innodb_autoinc_lock_mode` （MySQL 5.1.22 引入），可以选择的值如下：

| innodb_autoinc_lock_mode | 介绍                           |
| :----------------------- | :----------------------------- |
| 0                        | 传统模式                       |
| 1                        | 连续模式（MySQL 8.0 之前默认） |
| 2                        | 交错模式(MySQL 8.0 之后默认)   |

交错模式下，所有的“INSERT-LIKE”语句（所有的插入语句，包括：`INSERT`、`REPLACE`、`INSERT…SELECT`、`REPLACE…SELECT`、`LOAD DATA`等）都不使用表级锁，使用的是轻量级互斥锁实现，多条插入语句可以并发执行，速度更快，扩展性也更好。

不过，如果你的 MySQL 数据库有主从同步需求并且 Binlog 存储格式为 Statement 的话，不要将 InnoDB 自增锁模式设置为交叉模式，不然会有数据不一致性问题。这是因为并发情况下插入语句的执行顺序就无法得到保障。

> 如果 MySQL 采用的格式为 Statement ，那么 MySQL 的主从同步实际上同步的就是一条一条的 SQL 语句。

最后，再推荐一篇文章：[为什么 MySQL 的自增主键不单调也不连续](https://draveness.me/whys-the-design-mysql-auto-increment/) 。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L906)，来源许可：Apache-2.0。

<a id="k12330241e0b3"></a>

## 行级锁的使用有什么注意事项？

InnoDB 的行锁是针对索引字段加的锁，表级锁是针对非索引字段加的锁。当我们执行 `UPDATE`、`DELETE` 语句时，如果 `WHERE`条件中字段没有命中唯一索引或者索引失效的话，就会导致扫描全表对表中的所有行记录进行加锁。这个在我们日常工作开发中经常会遇到，一定要多多注意！！！

不过，很多时候即使用了索引也有可能会走全表扫描，这是因为 MySQL 优化器的原因。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L795)，来源许可：Apache-2.0。

<a id="ka0caeb87325c"></a>

## 详细说说 MVCC 的实现，ReadView 的生成时机是怎样的？

**回答：**

MVCC 是多版本并发控制，目标是在不加读锁的情况下实现一致性读，提高读写并发。InnoDB 的 MVCC 依赖隐藏字段、undo log 和 ReadView。

InnoDB 每行记录有隐藏字段，重要的是 `trx_id` 和 `roll_pointer`。`trx_id` 表示最后修改这行记录的事务 ID；`roll_pointer` 指向 undo log 中的旧版本。每次更新并不是简单覆盖旧值，而是生成新版本，并通过 undo log 保留旧版本链。

ReadView 是一致性读时生成的快照，里面通常包含：创建 ReadView 时活跃事务 ID 列表 `m_ids`，最小活跃事务 ID `up_limit_id`，下一个将分配的事务 ID `low_limit_id`，以及当前事务 ID。判断某个版本是否可见时，大致规则是：如果版本的 trx_id 小于最小活跃事务 ID，说明在快照前已提交，可见；如果 trx_id 大于等于 low_limit_id，说明是快照后才出现的事务，不可见；如果 trx_id 在活跃事务列表中，说明快照创建时还没提交，不可见；否则可见。

如果当前记录版本不可见，就沿着 undo log 版本链向前找，直到找到对当前 ReadView 可见的版本，或者找不到。

ReadView 的生成时机和隔离级别有关。在读已提交下，每次执行一致性读语句都会生成新的 ReadView，所以同一事务里两次 SELECT 可能看到不同已提交结果。在可重复读下，事务中第一次一致性读生成 ReadView，后续一致性读复用这个 ReadView，因此能保证同一事务内快照稳定。

注意，MVCC 主要针对普通 SELECT 的一致性读。`select ... for update`、`lock in share mode`、update、delete 属于当前读，会读取最新已提交版本并加锁。

<a id="bytedance-ai-agent-hard-20260602-q18"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%AD%97%E8%8A%82%E8%B7%B3%E5%8A%A8%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L648)，来源许可：GPL-3.0。

<a id="kd44a404fbbdc"></a>

## 说一下数据库表锁和行锁吧

**表锁**

不会出现死锁，发生锁冲突几率高，并发低。

MyISAM在执行查询语句（select）前，会自动给涉及的所有表加读锁，在执行增删改操作前，会自动给涉及的表加写锁。

MySQL的表级锁有两种模式：表共享读锁和表独占写锁。

读锁会阻塞写，写锁会阻塞读和写

- 对MyISAM表的读操作，不会阻塞其它进程对同一表的读请求，但会阻塞对同一表的写请求。只有当读锁释放后，才会执行其它进程的写操作。
- 对MyISAM表的写操作，会阻塞其它进程对同一表的读和写操作，只有当写锁释放后，才会执行其它进程的读写操作。

MyISAM不适合做写为主表的引擎，因为写锁后，其它线程不能做任何操作，大量的更新会使查询很难得到锁，从而造成永远阻塞。

**行锁**

会出现死锁，发生锁冲突几率低，并发高。

在MySQL的InnoDB引擎支持行锁，与Oracle不同，MySQL的行锁是通过索引加载的。也就是说，行锁是加在索引响应的行上的，要是对应的SQL语句没有走索引，则会全表扫描，行锁则无法实现，取而代之的是表锁，此时其它事务无法对当前表进行更新或插入操作。

**行锁的实现需要注意：**

- 行锁必须有索引才能实现，否则会自动锁全表，那么就不是行锁了。
- 如果是共享锁，两个事务可以锁同一个索引，排它锁则不能。
- insert，delete，update在事务中都会自动默认加上排它锁。

**行锁的适用场景：**

A用户消费，service层先查询该用户的账户余额，若余额足够，则进行后续的扣款操作；这种情况查询的时候应该对该记录进行加锁。

否则，B用户在A用户查询后消费前先一步将A用户账号上的钱转走，而此时A用户已经进行了用户余额是否足够的判断，则可能会出现余额已经不足但却扣款成功的情况。

为了避免此情况，需要在A用户操作该记录的时候进行for update加锁

<p  id="语法中内连接自连接外连接左右全交叉连接的区别分别是什么"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-01-03-MySQL.md#L86)，来源许可：Apache-2.0。

<a id="k582cb78421e4"></a>

## 那数据库事务有什么作用呢？

简单来说，数据库事务可以保证多个对数据库的操作（也就是 SQL 语句）构成一个逻辑上的整体。构成这个逻辑上的整体的这些数据库操作遵循：**要么全部执行成功,要么全部不执行** 。

```sql
# 开启一个事务
START TRANSACTION;
# 多条 SQL 语句
SQL1,SQL2...
## 提交事务
COMMIT;
```

![数据库事务示意图](https://oss.javaguide.cn/github/javaguide/mysql/%E6%95%B0%E6%8D%AE%E5%BA%93%E4%BA%8B%E5%8A%A1%E7%A4%BA%E6%84%8F%E5%9B%BE.png)

另外，关系型数据库（例如：`MySQL`、`SQL Server`、`Oracle` 等）事务都有 **ACID** 特性：

![ACID](https://oss.javaguide.cn/github/javaguide/mysql/ACID.png)

1. **原子性**（`Atomicity`）：事务是最小的执行单位，不允许分割。事务的原子性确保动作要么全部完成，要么完全不起作用；
2. **一致性**（`Consistency`）：执行事务前后，数据保持一致，例如转账业务中，无论事务是否成功，转账者和收款人的总额应该是不变的；
3. **隔离性**（`Isolation`）：并发访问数据库时，一个用户的事务不被其他事务所干扰，各并发事务之间数据库是独立的；
4. **持久性**（`Durability`）：一个事务被提交之后。它对数据库中数据的改变是持久的，即使数据库发生故障也不应该对其有任何影响。

🌈 这里要额外补充一点：**只有保证了事务的持久性、原子性、隔离性之后，一致性才能得到保障。也就是说 A、I、D 是手段，C 是目的！** 想必大家也和我一样，被 ACID 这个概念被误导了很久! 我也是看周志明老师的公开课[《周志明的软件架构课》](https://time.geekbang.org/opencourse/intro/100064201)才搞清楚的（多看好书！！！）。

![AID->C](https://oss.javaguide.cn/github/javaguide/mysql/AID-%3EC.png)

另外，DDIA 也就是 [《Designing Data-Intensive Application（数据密集型应用系统设计）》](https://book.douban.com/subject/30329536/) 的作者在他的这本书中如是说：

> Atomicity, isolation, and durability are properties of the database, whereas consis‐
> tency (in the ACID sense) is a property of the application. The application may rely
> on the database’s atomicity and isolation properties in order to achieve consistency,
> but it’s not up to the database alone.
>
> 翻译过来的意思是：原子性，隔离性和持久性是数据库的属性，而一致性（在 ACID 意义上）是应用程序的属性。应用可能依赖数据库的原子性和隔离属性来实现一致性，但这并不仅取决于数据库。因此，字母 C 不属于 ACID 。

《Designing Data-Intensive Application（数据密集型应用系统设计）》这本书强推一波，值得读很多遍！豆瓣有接近 90% 的人看了这本书之后给了五星好评。另外，中文翻译版本已经在 GitHub 开源，地址：[https://github.com/Vonng/ddia](https://github.com/Vonng/ddia) 。

![](https://oss.javaguide.cn/github/javaguide/books/ddia.png)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/mysql/mysql-questions-01.md#L634)，来源许可：Apache-2.0。
