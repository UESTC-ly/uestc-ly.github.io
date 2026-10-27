# Redis实践问答

<a id="k190ad5d23257"></a>

## Lua 脚本

Lua 脚本同样支持批量操作多条命令。一段 Lua 脚本可以视作一条命令执行，可以看作是 **原子操作**。也就是说，一段 Lua 脚本执行过程中不会有其他脚本或 Redis 命令同时执行，保证了操作不会被其他指令插入或打扰，这是 pipeline 所不具备的。

并且，Lua 脚本中支持一些简单的逻辑处理比如使用命令读取值并在 Lua 脚本中进行处理，这同样是 pipeline 所不具备的。

不过， Lua 脚本依然存在下面这些缺陷：

- 如果 Lua 脚本运行时出错并中途结束，之后的操作不会进行，但是之前已经发生的写操作不会撤销，所以即使使用了 Lua 脚本，也不能实现类似数据库回滚的原子性。
- Redis Cluster 下 Lua 脚本的原子操作也无法保证了，原因同样是无法保证所有的 key 都在同一个 **hash slot（哈希槽）** 上。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-02.md#L255)，来源许可：Apache-2.0。

<a id="k816be1736c26"></a>

## Memcached与Redis的区别都有哪些？

1、存储方式

- Memecache把数据全部存在内存之中，断电后会挂掉，没有持久化功能，数据不能超过内存大小。
- Redis有部份存在硬盘上，这样能保证数据的持久性。

2、数据支持类型

- Memcache对数据类型支持相对简单,只有String这一种类型
- Redis有复杂的数据类型。Redis不仅仅支持简单的k/v类型的数据，同时还提供 list，set，zset，hash等数据结构的存储。

3、使用底层模型不同

- 它们之间底层实现方式 以及与客户端之间通信的应用协议不一样。
- Redis直接自己构建了VM 机制 ，因为一般的系统调用系统函数的话，会浪费一定的时间去移动和请求。

4、集群模式：Memcached没有原生的集群模式，需要依靠客户端来实现往集群中分片写入数据；但是 Redis 目前 是原生支持 cluster 模式的.

5、Memcached是多线程，非阻塞IO复用的网络模型；Redis使用单线程的多路 IO 复用模型。

6、Value 值大小不同：Redis 最大可以达到 512MB；Memcached 只有 1MB。

<p id = "比的优势在哪里"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-02-01-Redis.md#L361)，来源许可：Apache-2.0。

<a id="k5765670c987b"></a>

## pipeline

对于不支持批量操作的命令，我们可以利用 **pipeline（流水线）** 将一批 Redis 命令封装成一组，这些 Redis 命令会被一次性提交到 Redis 服务器，只需要一次网络传输。不过，需要注意控制一次批量操作的 **元素个数**（例如 500 以内，实际也和元素字节数有关），避免网络传输的数据量过大。

与 `MGET`、`MSET` 等原生批量操作命令一样，pipeline 同样在 Redis Cluster 上使用会存在一些小问题。原因类似，无法保证所有的 key 都在同一个 **hash slot（哈希槽）** 上。如果想要使用的话，客户端需要自己维护 key 与 slot 的关系。

原生批量操作命令和 pipeline 的是有区别的，使用的时候需要注意：

- 原生批量操作命令是原子操作，pipeline 是非原子操作。
- pipeline 可以打包不同的命令，原生批量操作命令不可以。
- 原生批量操作命令是 Redis 服务端支持实现的，而 pipeline 需要服务端和客户端的共同实现。

顺带补充一下 pipeline 和 Redis 事务的对比：

- 事务是原子操作，pipeline 是非原子操作。两个不同的事务不会同时运行，而 pipeline 可以同时以交错方式执行。
- Redis 事务中每个命令都需要发送到服务端，而 Pipeline 只需要发送一次，请求次数更少。

> 事务可以看作是一个原子操作，但其实并不满足原子性。当我们提到 Redis 中的原子操作时，主要指的是这个操作（比如事务、Lua 脚本）不会被其他操作（比如其他事务、Lua 脚本）打扰，并不能完全保证这个操作中的所有写命令要么都执行要么都不执行。这主要也是因为 Redis 是不支持回滚操作。

![](https://oss.javaguide.cn/github/javaguide/database/redis/redis-pipeline-vs-transaction.png)

另外，pipeline 不适用于执行顺序有依赖关系的一批命令。就比如说，你需要将前一个命令的结果给后续的命令使用，pipeline 就没办法满足你的需求了。对于这种需求，我们可以使用 **Lua 脚本**。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-02.md#L232)，来源许可：Apache-2.0。

<a id="k2b77e8085737"></a>

## Redis replication 的核心机制

-   Redis 采用**异步方式**复制数据到 slave 节点，不过 Redis2.8 开始，slave node 会周期性地确认自己每次复制的数据量；
-   一个 master node 是可以配置多个 slave node 的；
-   slave node 也可以连接其他的 slave node；
-   slave node 做复制的时候，不会 block master node 的正常工作；
-   slave node 在做复制的时候，也不会 block 对自己的查询操作，它会用旧的数据集来提供服务；但是复制完成的时候，需要删除旧数据集，加载新数据集，这个时候就会暂停对外服务了；
-   slave node 主要用来进行横向扩容，做读写分离，扩容的 slave node 可以提高读的吞吐量。

注意，如果采用了主从架构，那么建议必须**开启** master node 的[持久化](https://github.com/doocs/advanced-java/blob/80b89fb9496d7ea3213e402c8c3853399e00c363/docs/high-concurrency/redis-persistence.md)，不建议用 slave node 作为 master node 的数据热备，因为那样的话，如果你关掉 master 的持久化，可能在 master 宕机重启的时候数据是空的，然后可能一经过复制， slave node 的数据也丢了。

另外，master 的各种备份方案，也需要做。万一本地的所有文件丢失了，从备份中挑选一份 rdb 去恢复 master，这样才能**确保启动的时候，是有数据的**，即使采用了后续讲解的[高可用机制](https://github.com/doocs/advanced-java/blob/80b89fb9496d7ea3213e402c8c3853399e00c363/docs/high-concurrency/redis-sentinel.md)，slave node 可以自动接管 master node，但也可能 sentinel 还没检测到 master failure，master node 就自动重启了，还是可能导致上面所有的 slave node 数据被清空。

### 参考资料

- [Advanced Java](https://github.com/doocs/advanced-java/blob/80b89fb9496d7ea3213e402c8c3853399e00c363/docs/high-concurrency/redis-master-slave.md#L9)，来源许可：CC-BY-SA-4.0。

<a id="k88784b33697b"></a>

## Redis 为什么是单线程的而不采用多线程方案？

这主要是基于一种客观原因来考虑的。因为Redis是基于内存的操作，CPU不是Redis的瓶颈，Redis的瓶颈最有可能是机器内存的大小或者网络带宽。

既然单线程容易实现，而且CPU不会成为瓶颈，那就顺理成章地采用单线程的方案了（毕竟采用多线程会有很多麻烦！）

<p  id="单线程的为什么这么快"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-02-01-Redis.md#L411)，来源许可：Apache-2.0。

<a id="kfe223861042c"></a>

## Redis 为什么这么快？

Redis 内部做了非常多的性能优化，比较重要的有下面 4 点：

1. **纯内存操作 (Memory-Based Storage)** ：这是最主要的原因。Redis 数据读写操作都发生在内存中，访问速度是纳秒级别，而传统数据库频繁读写磁盘的速度是毫秒级别，两者相差数个数量级。
2. **高效的 I/O 模型 (I/O Multiplexing & Single-Threaded Event Loop)** ：Redis 使用单线程事件循环配合 I/O 多路复用技术，让单个线程可以同时处理多个网络连接上的 I/O 事件（如读写），避免了多线程模型中的上下文切换和锁竞争问题。虽然是单线程，但结合内存操作的高效性和 I/O 多路复用，使得 Redis 能轻松处理大量并发请求（Redis 线程模型会在后文中详细介绍到）。
3. **优化的内部数据结构 (Optimized Data Structures)** ：Redis 提供多种数据类型（如 String, List, Hash, Set, Sorted Set 等），其内部实现采用高度优化的编码方式（如 ziplist, quicklist, skiplist, hashtable 等）。Redis 会根据数据大小和类型动态选择最合适的内部编码，以在性能和空间效率之间取得最佳平衡。
4. **简洁高效的通信协议 (Simple Protocol - RESP)** ：Redis 使用的是自己设计的 RESP (REdis Serialization Protocol) 协议。这个协议实现简单、解析性能好，并且是二进制安全的。客户端和服务端之间通信的序列化/反序列化开销很小，有助于提升整体的交互速度。

> 下面这张图片总结的挺不错的，分享一下，出自 [Why is Redis so fast?](https://twitter.com/alexxubyte/status/1498703822528544770)。

![why-redis-so-fast](https://oss.javaguide.cn/github/javaguide/database/redis/why-redis-so-fast.png)

那既然都这么快了，为什么不直接用 Redis 当主数据库呢？主要是因为内存成本太高，并且 Redis 提供的数据持久化仍然有数据丢失的风险。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-01.md#L31)，来源许可：Apache-2.0。

<a id="kdccfe2bfc6e1"></a>

## Redis 事务：如何解决 Redis 事务的缺陷？

Redis 从 2.6 版本开始支持执行 Lua 脚本，它的功能和事务非常类似。我们可以利用 Lua 脚本来批量执行多条 Redis 命令，这些 Redis 命令会被提交到 Redis 服务器一次性执行完成，大幅减小了网络开销。

一段 Lua 脚本可以视作一条命令执行，一段 Lua 脚本执行过程中不会有其他脚本或 Redis 命令同时执行，保证了操作不会被其他指令插入或打扰。

不过，如果 Lua 脚本运行时出错并中途结束，出错之后的命令是不会被执行的。并且，出错之前执行的命令是无法被撤销的，无法实现类似关系型数据库执行失败可以回滚的那种原子性效果。因此，**严格来说的话，通过 Lua 脚本来批量执行 Redis 命令实际也是不完全满足原子性的。**

如果想要让 Lua 脚本中的命令全部执行，必须保证语句语法和命令都是对的。

另外，Redis 7.0 新增了 [Redis functions](https://redis.io/docs/latest/develop/programmability/functions-intro/) 特性，你可以将 Redis functions 看作是比 Lua 更强大的脚本。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-02.md#L175)，来源许可：Apache-2.0。

<a id="ke808ace41e88"></a>

## Redis 使用规范

实际使用 Redis 的过程中，我们尽量要准守一些常见的规范，比如：

1. 使用连接池：避免频繁创建关闭客户端连接。
2. 尽量不使用 O(n) 指令，使用 O(n) 命令时要关注 n 的数量：像 `KEYS *`、`HGETALL`、`LRANGE`、`SMEMBERS`、`SINTER`/`SUNION`/`SDIFF` 等 O(n) 命令并非不能使用，但是需要明确 n 的值。另外，有遍历的需求可以使用 `HSCAN`、`SSCAN`、`ZSCAN` 代替。
3. 使用批量操作减少网络传输：原生批量操作命令（比如 `MGET`、`MSET` 等等）、pipeline、Lua 脚本。
4. 尽量不使用 Redis 事务：Redis 事务实现的功能比较鸡肋，可以使用 Lua 脚本代替。
5. 禁止长时间开启 monitor：对性能影响比较大。
6. 控制 key 的生命周期：避免 Redis 中存放了太多不经常被访问的数据。
7. ……

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-02.md#L828)，来源许可：Apache-2.0。

<a id="k39cea3e18edb"></a>

## Redis 后台线程了解吗？

我们虽然经常说 Redis 是单线程模型（主要逻辑是单线程完成的），但实际还有一些后台线程用于执行一些比较耗时的操作：

- 通过 `bio_close_file` 后台线程来释放 AOF / RDB 等过程中产生的临时文件资源。
- 通过 `bio_aof_fsync` 后台线程调用 `fsync` 函数将系统内核缓冲区还未同步到到磁盘的数据强制刷到磁盘（AOF 文件）。
- 通过 `bio_lazy_free` 后台线程释放大对象（已删除）占用的内存空间.

在`bio.h` 文件中有定义（Redis 6.0 版本，源码地址：<https://github.com/redis/redis/blob/6.0/src/bio.h>）：

```java
#ifndef __BIO_H
#define __BIO_H

/* Exported API */
void bioInit(void);
void bioCreateBackgroundJob(int type, void *arg1, void *arg2, void *arg3);
unsigned long long bioPendingJobsOfType(int type);
unsigned long long bioWaitStepOfType(int type);
time_t bioOlderJobOfType(int type);
void bioKillThreads(void);

/* Background job opcodes */
#define BIO_CLOSE_FILE    0 /* Deferred close(2) syscall. */
#define BIO_AOF_FSYNC     1 /* Deferred AOF fsync. */
#define BIO_LAZY_FREE     2 /* Deferred objects freeing. */
#define BIO_NUM_OPS       3

#endif
```

关于 Redis 后台线程的详细介绍可以查看 [Redis 6.0 后台线程有哪些？](https://juejin.cn/post/7102780434739626014) 这篇就文章。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-01.md#L556)，来源许可：Apache-2.0。

<a id="k49466b20ca96"></a>

## Redis 和 Memcached 有啥区别？

### Redis 支持复杂的数据结构

Redis 相比 Memcached 来说，拥有[更多的数据结构](https://github.com/doocs/advanced-java/blob/80b89fb9496d7ea3213e402c8c3853399e00c363/docs/high-concurrency/redis-data-types.md)，能支持更丰富的数据操作。如果需要缓存能够支持更复杂的结构和操作， Redis 会是不错的选择。

### Redis 原生支持集群模式

在 Redis3.x 版本中，便能支持 cluster 模式，而 Memcached 没有原生的集群模式，需要依靠客户端来实现往集群中分片写入数据。

### 性能对比

由于 Redis 只使用**单核**，而 Memcached 可以使用**多核**，所以平均每一个核上 Redis 在存储小数据时比 Memcached 性能更高。而在 100k 以上的数据中，Memcached 性能要高于 Redis。虽然 Redis 最近也在存储大数据的性能上进行优化，但是比起 Memcached，还是稍有逊色。

### 参考资料

- [Advanced Java](https://github.com/doocs/advanced-java/blob/80b89fb9496d7ea3213e402c8c3853399e00c363/docs/high-concurrency/redis-single-thread-model.md#L15)，来源许可：CC-BY-SA-4.0。

<a id="k912cb10a993e"></a>

## Redis 和 Memcached 的区别

**常见问法：** Redis 和 Memcached 的区别：面试官心理分析

### 面试题

Redis 和 Memcached 有什么区别？Redis 的线程模型是什么？为什么 Redis 单线程却能支撑高并发？

### 面试官心理分析

这个是问 Redis 的时候，最基本的问题吧，Redis 最基本的一个内部原理和特点，就是 Redis 实际上是个**单线程工作模型**，你要是这个都不知道，那后面玩儿 Redis 的时候，出了问题岂不是什么都不知道？

还有可能面试官会问问你 Redis 和 Memcached 的区别，但是 Memcached 是早些年各大互联网公司常用的缓存方案，但是现在近几年基本都是 Redis，没什么公司用 Memcached 了。

### 参考资料

- [Advanced Java](https://github.com/doocs/advanced-java/blob/80b89fb9496d7ea3213e402c8c3853399e00c363/docs/high-concurrency/redis-single-thread-model.md#L1)，来源许可：CC-BY-SA-4.0。
- [Advanced Java](https://github.com/doocs/advanced-java/blob/80b89fb9496d7ea3213e402c8c3853399e00c363/docs/high-concurrency/redis-single-thread-model.md#L7)，来源许可：CC-BY-SA-4.0。

<a id="kdb5dd95e4324"></a>

## Redis 如何才能做到高可用

**常见问法：** Redis 如何才能做到高可用？

如果系统在 365 天内，有 99.99% 的时间，都是可以哗哗对外提供服务的，那么就说系统是高可用的。

一个 slave 挂掉了，是不会影响可用性的，还有其它的 slave 在提供相同数据下的相同的对外的查询服务。

但是，如果 master node 死掉了，会怎么样？没法写数据了，写缓存的时候，全部失效了。slave node 还有什么用呢，没有 master 给它们复制数据了，系统相当于不可用了。

Redis 的高可用架构，叫做 `failover` **故障转移**，也可以叫做主备切换。

master node 在故障时，自动检测，并且将某个 slave node 自动切换为 master node 的过程，叫做主备切换。这个过程，实现了 Redis 的主从架构下的高可用。

后面会详细说明 Redis [基于哨兵的高可用性](https://github.com/doocs/advanced-java/blob/80b89fb9496d7ea3213e402c8c3853399e00c363/docs/high-concurrency/redis-sentinel.md)。

### 参考资料

- [Advanced Java](https://github.com/doocs/advanced-java/blob/80b89fb9496d7ea3213e402c8c3853399e00c363/docs/high-concurrency/redis-master-slave.md#L91)，来源许可：CC-BY-SA-4.0。
- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-02-02-Redis.md#L287)，来源许可：Apache-2.0。

<a id="k71cea4ecd59f"></a>

## redis 是单线程的吗，为什么这么快

**单线程**

- 没有了多线程上下文切换的性能损耗
- 没有了访问共享资源加锁的性能损耗
- 开发和调试非常友好，可维护性高

**纯内存操作**

`redis`是一个内存数据库，它的数据都存储在内存中，这意味着我们读写数据都是在内存中完成，这个速度是非常快的。`redis`是一个KV内存数据库，它内部构建了一个哈希表，根据指定的`KEY`访问时，只需要`O(1)`的时间复杂度就可以找到对应的数据。同时，`redis`提供了丰富的数据类型，并使用高效的操作方式进行操作，这些操作都在内存中进行，并不会大量消耗`CPU`资源，所以速度极快

**IO 多路复用技术**

`redis` 服务采用 `Reactor` 的方式来实现文件事件处理器（每一个网络连接其实都对应一个文件描述符）。文件事件处理器使用 I/O 多路复用模块同时监听多个 FD，当 `accept`、`read`、`write` 和 `close` 文件事件产生时，文件事件处理器就会回调 FD 绑定的事件处理器。虽然整个文件事件处理器是在单线程上运行的，但是通过 I/O 多路复用模块的引入，实现了同时对多个 FD 读写的监控，提高了网络通信模型的性能，同时也可以保证整个 `redis` 服务实现的简单

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/02-programming-languages/Java/java-fundamentals.md#L588)，来源许可：GPL-3.0。

<a id="k9cb2495083d5"></a>

## Redis 生产部署方案：面试官心理分析

看看你了解不了解你们公司的 Redis 生产集群的部署架构，如果你不了解，那么确实你就很失职了，你的 Redis 是主从架构？集群架构？用了哪种集群方案？有没有做高可用保证？有没有开启持久化机制确保可以进行数据恢复？线上 Redis 给几个 G 的内存？设置了哪些参数？压测后你们 Redis 集群承载多少 QPS？

兄弟，这些你必须是门儿清的，否则你确实是没好好思考过。

### 参考资料

- [Advanced Java](https://github.com/doocs/advanced-java/blob/80b89fb9496d7ea3213e402c8c3853399e00c363/docs/high-concurrency/redis-production-environment.md#L7)，来源许可：CC-BY-SA-4.0。

<a id="kcc470acb0899"></a>

## Redis 的 RedLock 锁

为了解决 Redis 单点的问题。 Redis 的作者提出了 RedLock 的解决方案。方案非常的巧妙和简洁。 RedLock 的核心思想就是，**同时使用多个 Redis Master 来冗余，且这些节点都是完全的独立的，也不需要对这些节点之间的数据进行同步**。

假设我们有N个Redis节点，N应该是一个大于2的奇数。RedLock的实现步骤:

1. 取得当前时间
2. 使用单节点获取锁的方式，依次获取 N 个节点的 Redis 锁。
3. 如果获取到的锁的数量大于 N/2+1*N*/2+1 个，且获取的时间小于锁的有效时间(lock validity time)就认为获取到了一个有效的锁，锁自动释放时间就是最初的锁释放时间减去之前获取锁所消耗的时间。
4. 如果获取锁的数量小于 N/2+1*N*/2+1 ，或者在锁的有效时间(lock validity time)内没有获取到足够的锁，就认为获取锁失败，这个时候需要向所有节点发送释放锁的消息。

对于释放锁的实现就很简单了，向所有的 Redis 节点发起释放的操作，无论之前是否获取锁成功。

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/05-01-02-distribution.md#L90)，来源许可：Apache-2.0。

<a id="k003f39f37ef3"></a>

## Redis 的并发竞争问题是什么？如何解决这个问题？了解 Redis 事务的 CAS 方案吗？

这个也是线上非常常见的一个问题，就是**多客户端同时并发写**一个 key，可能本来应该先到的数据后到了，导致数据版本错了；或者是多客户端同时获取一个 key，修改值之后再写回去，只要顺序错了，数据就错了。

而且 Redis 自己就有天然解决这个问题的 CAS 类的乐观锁方案。

某个时刻，多个系统实例都去更新某个 key。可以基于 zookeeper 实现分布式锁。每个系统通过 zookeeper 获取分布式锁，确保同一时间，只能有一个系统实例在操作某个 key，别人都不允许读和写。

![zookeeper-distributed-lock](https://raw.githubusercontent.com/forthespada/InterviewGuide/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-02-02-Redis.assets/202208092301751.png)

你要写入缓存的数据，都是从 mysql 里查出来的，都得写入 mysql 中，写入 mysql 中的时候必须保存一个时间戳，从 mysql 查出来的时候，时间戳也查出来。

每次要**写之前，先判断**一下当前这个 value 的时间戳是否比缓存里的 value 的时间戳要新。如果是的话，那么可以写，否则，就不能用旧的数据覆盖新的数据。

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-02-02-Redis.md#L710)，来源许可：Apache-2.0。

<a id="k314b509aa1b8"></a>

## Redis 的并发竞争问题：面试官心理分析

这个也是线上非常常见的一个问题，就是**多客户端同时并发写**一个 key，可能本来应该先到的数据后到了，导致数据版本错了；或者是多客户端同时获取一个 key，修改值之后再写回去，只要顺序错了，数据就错了。

而且 Redis 自己就有天然解决这个问题的 CAS 类的乐观锁方案。

### 参考资料

- [Advanced Java](https://github.com/doocs/advanced-java/blob/80b89fb9496d7ea3213e402c8c3853399e00c363/docs/high-concurrency/redis-cas.md#L7)，来源许可：CC-BY-SA-4.0。

<a id="ka4deacb9bebd"></a>

## Redis 采用的是那种删除策略呢？

Redis 采用的是 **定期删除+惰性/懒汉式删除** 结合的策略，这也是大部分缓存框架的选择。定期删除对内存更加友好，惰性删除对 CPU 更加友好。两者各有千秋，结合起来使用既能兼顾 CPU 友好，又能兼顾内存友好。

下面是我们详细介绍一下 Redis 中的定期删除具体是如何做的。

Redis 的定期删除过程是随机的（周期性地随机从设置了过期时间的 key 中抽查一批），所以并不保证所有过期键都会被立即删除。这也就解释了为什么有的 key 过期了，并没有被删除。并且，Redis 底层会通过限制删除操作执行的时长和频率来减少删除操作对 CPU 时间的影响。

另外，定期删除还会受到执行时间和过期 key 的比例的影响：

- 执行时间已经超过了阈值，那么就中断这一次定期删除循环，以避免使用过多的 CPU 时间。
- 如果这一批过期的 key 比例超过一个比例，就会重复执行此删除流程，以更积极地清理过期 key。相应地，如果过期的 key 比例低于这个比例，就会中断这一次定期删除循环，避免做过多的工作而获得很少的内存回收。

Redis 7.2 版本的执行时间阈值是 **25ms**，过期 key 比例设定值是 **10%**。

```c
#define ACTIVE_EXPIRE_CYCLE_FAST_DURATION 1000 /* Microseconds. */
#define ACTIVE_EXPIRE_CYCLE_SLOW_TIME_PERC 25 /* Max % of CPU to use. */
#define ACTIVE_EXPIRE_CYCLE_ACCEPTABLE_STALE 10 /* % of stale keys after which
                                                   we do extra efforts. */
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-01.md#L647)，来源许可：Apache-2.0。

<a id="k6f2258feefc6"></a>

## Redis6.0 之前为什么不使用多线程？

虽然说 Redis 是单线程模型，但实际上，**Redis 在 4.0 之后的版本中就已经加入了对多线程的支持。**

不过，Redis 4.0 增加的多线程主要是针对一些大键值对的删除操作的命令，使用这些命令就会使用主线程之外的其他线程来“异步处理”，从而减少对主线程的影响。

为此，Redis 4.0 之后新增了几个异步命令：

- `UNLINK`：可以看作是 `DEL` 命令的异步版本。
- `FLUSHALL ASYNC`：用于清空所有数据库的所有键，不限于当前 `SELECT` 的数据库。
- `FLUSHDB ASYNC`：用于清空当前 `SELECT` 数据库中的所有键。

![redis4.0 more thread](https://oss.javaguide.cn/github/javaguide/database/redis/redis4.0-more-thread.png)

总的来说，直到 Redis 6.0 之前，Redis 的主要操作仍然是单线程处理的。

**那 Redis6.0 之前为什么不使用多线程？** 我觉得主要原因有 3 点：

- 单线程编程容易并且更容易维护；
- Redis 的性能瓶颈不在 CPU，主要在内存和网络；
- 多线程就会存在死锁、线程上下文切换等问题，甚至会影响性能。

相关阅读：[为什么 Redis 选择单线程模型？](https://draveness.me/whys-the-design-redis-single-thread/)。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-01.md#L502)，来源许可：Apache-2.0。

<a id="k2508e713f32b"></a>

## Redis6.0 之后为何引入了多线程？

**Redis6.0 引入多线程主要是为了提高网络 IO 读写性能**，因为这个算是 Redis 中的一个性能瓶颈（Redis 的瓶颈主要受限于内存和网络）。

虽然，Redis6.0 引入了多线程，但是 Redis 的多线程只是在网络数据的读写这类耗时操作上使用了，执行命令仍然是单线程顺序执行。因此，你也不需要担心线程安全问题。

Redis6.0 的多线程默认是禁用的，只使用主线程。如需开启需要设置 IO 线程数 > 1，需要修改 redis 配置文件 `redis.conf`：

```bash
io-threads 4 #设置1的话只会开启主线程，官网建议4核的机器建议设置为2或3个线程，8核的建议设置为6个线程
```

另外：

- io-threads 的个数一旦设置，不能通过 config 动态设置。
- 当设置 ssl 后，io-threads 将不工作。

开启多线程后，默认只会使用多线程进行 IO 写入 writes，即发送数据给客户端，如果需要开启多线程 IO 读取 reads，同样需要修改 redis 配置文件 `redis.conf`：

```bash
io-threads-do-reads yes
```

但是官网描述开启多线程读并不能有太大提升，因此一般情况下并不建议开启。

相关阅读：

- [Redis 6.0 新特性-多线程连环 13 问！](https://mp.weixin.qq.com/s/FZu3acwK6zrCBZQ_3HoUgw)
- [Redis 多线程网络模型全面揭秘](https://segmentfault.com/a/1190000039223696)（推荐）

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-01.md#L526)，来源许可：Apache-2.0。

<a id="k719dad6cc5d8"></a>

## Redis在Java开发中的作用、适用场景，底层原理考量？

**回答：**

Redis 是独立的数据服务，在 Java 项目中常通过客户端或 Spring Data Redis 接入。需要从数据结构、并发语义、过期和故障行为解释选择，不能只说“放内存所以快”。

| 场景 | 常用方式 | 关键边界 |
| --- | --- | --- |
| 热点缓存 | String/Hash、TTL、cache-aside | 数据库与缓存通常非强一致，要定义失效窗口 |
| 会话与验证码 | 有时效的键、原子计数 | 访问保护、一次性消费、过期与重放 |
| 计数和限流 | INCR、Lua、Sorted Set | 多步需原子化，脚本不能长时间阻塞 |
| 排行榜 | Sorted Set | 分值更新、并列规则、热点与容量 |
| 任务协作 | Streams、消费组 | 待确认消息、重投和消费者幂等 |
| 互斥协调 | 带租约的锁 | 过期、暂停与故障切换会影响互斥假设 |

常见部署中的命令执行以串行路径为核心，网络 IO 和后台任务可涉及其他线程；不能把整个 Redis 说成只有一个线程。性能来自内存访问、数据结构与事件驱动等共同作用，长命令、大 key、热点 key 和网络往返仍可能成为瓶颈。

缓存层要区分穿透、击穿和雪崩：可结合空值短缓存、适用时的布隆过滤器、并发请求合并、TTL 打散、限流降级处理。数据库提交后删除缓存是常见策略，但并发读写、删除失败和旧值回填仍会造成窗口，重要场景可用版本校验和可靠失效事件收敛。

锁可用 `SET key token NX PX ttl` 获取，用原子比较 token 后删除的方式释放，避免误删别人的锁。租约过期后旧持有者仍可能继续执行，续租也不能消除所有故障；高风险写入应使用底层资源支持的 fencing token、数据库约束或合适的一致性服务。

RDB 是周期快照，AOF 记录写操作，持久化策略影响恢复时间与可能的数据丢失窗口；复制、集群分片和持久化分别解决不同问题。Redis Cluster 的多 key 原子操作通常受同一 hash slot 约束。Java 端还要关注连接池、超时、序列化、客户端重试及重复副作用。

**锁失效后为什么还可能写坏数据？** 假设 worker A 获得 30 秒租约后暂停，租约到期，worker B 获得新锁并完成写入；A 恢复后仍然可能继续访问数据库。比较随机 token 后删除只能防止 A 误删 B 的锁，无法阻止 A 的过期业务写入。

Fencing token 的思路是每次获得执行资格时取得单调递增序号，底层资源记录已接受的序号，并在原子写入时拒绝较旧序号。只有下游真正执行了这个检查，它才有效；单纯在日志或 HTTP 头里附加一个数字没有保护作用。序号生成本身也需具备所需的单调与故障语义，不能把任意 Redis 计数器在故障切换后都视为可靠的 fencing 服务。

对订单等关键业务，唯一约束、条件更新和业务幂等通常应直接落在最终数据存储中。Redis 锁可以减少并发争用，却不应成为账本正确性的唯一依据。

<a id="meituan-agent-20261012-18fa4134-q25"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%BE%8E%E5%9B%A2%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1197)，来源许可：GPL-3.0。

<a id="k8e10472f11a7"></a>

## Redis对于大量的请求，是怎样处理的？

1、Redis是一个单线程程序，也就说同一时刻它只能处理一个客户端请求；

2、Redis是通过IO多路复用（select，epoll，kqueue，依据不同的平台，采取不同的实现）来处理多个客户端请求。

<p  id="缓存雪崩缓存穿透缓存预热缓存更新缓存击穿缓存降级全搞定"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-02-01-Redis.md#L532)，来源许可：Apache-2.0。

<a id="ke48cae84f5ea"></a>

## Redis：如何解决Redis的并发竞争Key问题

所谓 Redis 的并发竞争 Key 的问题也就是多个系统同时对一个 key 进行操作，但是最后执行的顺序和我们期望的顺序不同，这样也就导致了结果的不同！

推荐一种方案：分布式锁（zookeeper 和 Redis 都可以实现分布式锁）。（如果不存在 Redis 的并发竞争 Key 问 题，不要使用分布式锁，这样会影响性能）

基于zookeeper临时有序节点可以实现的分布式锁。大致思想为：每个客户端对某个方法加锁时，在zookeeper上的 与该方法对应的指定节点的目录下，生成一个唯一的瞬时有序节点。 

判断是否获取锁的方式很简单，只需要判断有 序节点中序号最小的一个。 当释放锁的时候，只需将这个瞬时节点删除即可。

同时，其可以避免服务宕机导致的锁 无法释放，而产生的死锁问题。完成业务流程后，删除对应的子节点释放锁。

在实践中，当然是从以可靠性为主。所以首推Zookeeper。

<p  id="如何保证缓存与数据库双写时的数据一致性"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-02-02-Redis.md#L45)，来源许可：Apache-2.0。

<a id="k7fbe7c48d1e0"></a>

## RedLock 算法

这个场景是假设有一个 Redis cluster，有 5 个 Redis master 实例。然后执行如下步骤获取一把锁：

1. 获取当前时间戳，单位是毫秒；
2. 跟上面类似，轮流尝试在每个 master 节点上创建锁，超时时间较短，一般就几十毫秒（客户端为了获取锁而使用的超时时间比自动释放锁的总时间要小。例如，如果自动释放时间是 10 秒，那么超时时间可能在 `5~50` 毫秒范围内）；
3. 尝试在**大多数节点**上建立一个锁，比如 5 个节点就要求是 3 个节点 `n / 2 + 1` ；
4. 客户端计算建立好锁的时间，如果建立锁的时间小于超时时间，就算建立成功了；
5. 要是锁建立失败了，那么就依次之前建立过的锁删除；
6. 只要别人建立了一把分布式锁，你就得**不断轮询去尝试获取锁**。

![redis-redlock](https://raw.githubusercontent.com/doocs/advanced-java/80b89fb9496d7ea3213e402c8c3853399e00c363/docs/distributed-system/images/redis-redlock.png)

[Redis 官方](https://redis.io/)给出了以上两种基于 Redis 实现分布式锁的方法，详细说明可以查看：https://redis.io/topics/distlock 。

### 参考资料

- [Advanced Java](https://github.com/doocs/advanced-java/blob/80b89fb9496d7ea3213e402c8c3853399e00c363/docs/distributed-system/distributed-lock-redis-vs-zookeeper.md#L52)，来源许可：CC-BY-SA-4.0。

<a id="k6071c83965f9"></a>

## String 的应用场景有哪些？

String 是 Redis 中最简单同时也是最常用的一个数据类型。它是一种二进制安全的数据类型，可以用来存储任何类型的数据比如字符串、整数、浮点数、图片（图片的 base64 编码或者解码或者图片的路径）、序列化后的对象。

String 的常见应用场景如下：

- 常规数据（比如 Session、Token、序列化后的对象、图片的路径）的缓存；
- 计数比如用户单位时间的请求数（简单限流可以用到）、页面单位时间的访问数；
- 分布式锁（利用 `SETNX key value` 命令可以实现一个最简易的分布式锁）；
- ……

关于 String 的详细介绍请看这篇文章：[Redis 5 种基本数据类型详解](https://javaguide.cn/database/redis/redis-data-structures-01.html)。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-01.md#L210)，来源许可：Apache-2.0。

<a id="k2a17fc040817"></a>

## String 的底层实现是什么？

Redis 是基于 C 语言编写的，但 Redis 的 String 类型的底层实现并不是 C 语言中的字符串（即以空字符 `\0` 结尾的字符数组），而是自己编写了 [SDS](https://github.com/antirez/sds)（Simple Dynamic String，简单动态字符串）来作为底层实现。

SDS 最早是 Redis 作者为日常 C 语言开发而设计的 C 字符串，后来被应用到了 Redis 上，并经过了大量的修改完善以适合高性能操作。

Redis7.0 的 SDS 的部分源码如下（<https://github.com/redis/redis/blob/7.0/src/sds.h>）：

```c
/* Note: sdshdr5 is never used, we just access the flags byte directly.
 * However is here to document the layout of type 5 SDS strings. */
struct __attribute__ ((__packed__)) sdshdr5 {
    unsigned char flags; /* 3 lsb of type, and 5 msb of string length */
    char buf[];
};
struct __attribute__ ((__packed__)) sdshdr8 {
    uint8_t len; /* used */
    uint8_t alloc; /* excluding the header and null terminator */
    unsigned char flags; /* 3 lsb of type, 5 unused bits */
    char buf[];
};
struct __attribute__ ((__packed__)) sdshdr16 {
    uint16_t len; /* used */
    uint16_t alloc; /* excluding the header and null terminator */
    unsigned char flags; /* 3 lsb of type, 5 unused bits */
    char buf[];
};
struct __attribute__ ((__packed__)) sdshdr32 {
    uint32_t len; /* used */
    uint32_t alloc; /* excluding the header and null terminator */
    unsigned char flags; /* 3 lsb of type, 5 unused bits */
    char buf[];
};
struct __attribute__ ((__packed__)) sdshdr64 {
    uint64_t len; /* used */
    uint64_t alloc; /* excluding the header and null terminator */
    unsigned char flags; /* 3 lsb of type, 5 unused bits */
    char buf[];
};
```

通过源码可以看出，SDS 共有五种实现方式：SDS_TYPE_5（并未用到）、SDS_TYPE_8、SDS_TYPE_16、SDS_TYPE_32、SDS_TYPE_64，其中只有后四种实际用到。Redis 会根据初始化的长度决定使用哪种类型，从而减少内存的使用。

| 类型     | 字节 | 位  |
| -------- | ---- | --- |
| sdshdr5  | < 1  | <8  |
| sdshdr8  | 1    | 8   |
| sdshdr16 | 2    | 16  |
| sdshdr32 | 4    | 32  |
| sdshdr64 | 8    | 64  |

对于后四种实现都包含了下面这 4 个属性：

- `len`：字符串的长度也就是已经使用的字节数。
- `alloc`：总共可用的字符空间大小，alloc-len 就是 SDS 剩余的空间大小。
- `buf[]`：实际存储字符串的数组。
- `flags`：低三位保存类型标志。

SDS 相比于 C 语言中的字符串有如下提升：

1. **可以避免缓冲区溢出**：C 语言中的字符串被修改（比如拼接）时，一旦没有分配足够长度的内存空间，就会造成缓冲区溢出。SDS 被修改时，会先根据 len 属性检查空间大小是否满足要求，如果不满足，则先扩展至所需大小再进行修改操作。
2. **获取字符串长度的复杂度较低**：C 语言中的字符串的长度通常是经过遍历计数来实现的，时间复杂度为 O(n)。SDS 的长度获取直接读取 len 属性即可，时间复杂度为 O(1)。
3. **减少内存分配次数**：为了避免修改（增加/减少）字符串时，每次都需要重新分配内存（C 语言的字符串是这样的），SDS 实现了空间预分配和惰性空间释放两种优化策略。当 SDS 需要增加字符串时，Redis 会为 SDS 分配好内存，并且根据特定的算法分配多余的内存，这样可以减少连续执行字符串增长操作所需的内存重分配次数。当 SDS 需要减少字符串时，这部分内存不会立即被回收，会被记录下来，等待后续使用（支持手动释放，有对应的 API）。
4. **二进制安全**：C 语言中的字符串以空字符 `\0` 作为字符串结束的标识，这存在一些问题，像一些二进制文件（比如图片、视频、音频）就可能包括空字符，C 字符串无法正确保存。SDS 使用 len 属性判断字符串是否结束，不存在这个问题。

🤐 多提一嘴，很多文章里 SDS 的定义是下面这样的：

```c
struct sdshdr {
    unsigned int len;
    unsigned int free;
    char buf[];
};
```

这个也没错，Redis 3.2 之前就是这样定义的。后来，由于这种方式的定义存在问题，`len` 和 `free` 的定义用了 4 个字节，造成了浪费。Redis 3.2 之后，Redis 改进了 SDS 的定义，将其划分为了现在的 5 种类型。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-01.md#L237)，来源许可：Apache-2.0。

<a id="k97fc75c252b0"></a>

## 为啥 Redis 单线程模型也能效率这么高？

-   纯内存操作。
-   核心是基于非阻塞的 IO 多路复用机制。
-   C 语言实现，一般来说，C 语言实现的程序“距离”操作系统更近，执行速度相对会更快。
-   单线程反而避免了多线程的频繁上下文切换问题，预防了多线程可能产生的竞争问题。

### 参考资料

- [Advanced Java](https://github.com/doocs/advanced-java/blob/80b89fb9496d7ea3213e402c8c3853399e00c363/docs/high-concurrency/redis-single-thread-model.md#L58)，来源许可：CC-BY-SA-4.0。

<a id="k000fa7df1453"></a>

## 了解Redis的线程模型吗？可以大致说说吗？

如果你打开看过 Redis 的源码就会发现Redis 内部使用文件事件处理器 file event handler，这个文件事件处理器是单线程的，所以 Redis 才叫做单线程的模型。

它采用 IO 多路复用机制同时监听多个 socket，根据 socket 上的事件来选择对应的事件处理器进行处理。

![](https://raw.githubusercontent.com/forthespada/InterviewGuide/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-02-01-Redis.assets/202205220024968.png)

文件事件处理器的结构包含 4 个部分：

- 多个 socket
- IO多路复用程序
- 文件事件分派器
- 事件处理器（连接应答处理器、命令请求处理器、命令回复处理器）

使用 I/O 多路复用程序来同时监听多个套接字， 并根据套接字目前执行的任务来为套接字关联不同的事件处理器。

当被监听的套接字准备好执行连接应答（accept）、读取（read）、写入（write）、关闭（close）等操作时， 与操作相对应的文件事件就会产生， 这时文件事件处理器就会调用套接字之前关联好的事件处理器来处理这些事件。

多个 socket 可能会并发产生不同的操作，每个操作对应不同的文件事件，但是 IO 多路复用程序会监听多个 socket，会将 socket 产生的事件放入队列中排队，事件分派器每次从队列中取出一个事件，把该事件交给对应的事件处理器进行处理。

**一句话总结**：“I/O 多路复用程序负责监听多个套接字， 并向文件事件分派器传送那些产生了事件的套接字。”

<p  id="设置过期时间的两种方案是什么"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-02-01-Redis.md#L433)，来源许可：Apache-2.0。

<a id="k5a50fe6aed80"></a>

## 什么是 Redis Module？有什么用？

Redis 从 4.0 版本开始，支持通过 Module 来扩展其功能以满足特殊的需求。这些 Module 以动态链接库（so 文件）的形式被加载到 Redis 中，这是一种非常灵活的动态扩展功能的实现方式，值得借鉴学习！

我们每个人都可以基于 Redis 去定制化开发自己的 Module，比如实现搜索引擎功能、自定义分布式锁和分布式限流。

目前，被 Redis 官方推荐的 Module 有：

- [RediSearch](https://github.com/RediSearch/RediSearch)：用于实现搜索引擎的模块。
- [RedisJSON](https://github.com/RedisJSON/RedisJSON)：用于处理 JSON 数据的模块。
- [RedisGraph](https://github.com/RedisGraph/RedisGraph)：用于实现图形数据库的模块。
- [RedisTimeSeries](https://github.com/RedisTimeSeries/RedisTimeSeries)：用于处理时间序列数据的模块。
- [RedisBloom](https://github.com/RedisBloom/RedisBloom)：用于实现布隆过滤器的模块。
- [RedisAI](https://github.com/RedisAI/RedisAI)：用于执行深度学习/机器学习模型并管理其数据的模块。
- [RedisCell](https://github.com/brandur/redis-cell)：用于实现分布式限流的模块。
- ……

关于 Redis 模块的详细介绍，可以查看官方文档：<https://redis.io/modules>。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-01.md#L129)，来源许可：Apache-2.0。

<a id="k98d0ba491b46"></a>

## 什么是 Redis？

[Redis](https://redis.io/) （**RE**mote **DI**ctionary **S**erver）是一个基于 C 语言开发的开源 NoSQL 数据库（BSD 许可）。与传统数据库不同的是，Redis 的数据是保存在内存中的（内存数据库，支持持久化），因此读写速度非常快，被广泛应用于分布式缓存方向。并且，Redis 存储的是 KV 键值对数据。

为了满足不同的业务场景，Redis 内置了多种数据类型实现（比如 String、Hash、Sorted Set、Bitmap、HyperLogLog、GEO）。并且，Redis 还支持事务、持久化、Lua 脚本、发布订阅模型、多种开箱即用的集群方案（Redis Sentinel、Redis Cluster）。

![Redis 数据类型概览](https://oss.javaguide.cn/github/javaguide/database/redis/redis-overview-of-data-types-2023-09-28.jpg)

Redis 没有外部依赖，Linux 和 OS X 是 Redis 开发和测试最多的两个操作系统，官方推荐生产环境使用 Linux 部署 Redis。

个人学习的话，你可以自己本机安装 Redis 或者通过 Redis 官网提供的[在线 Redis 环境](https://try.redis.io/)（少部分命令无法使用）来实际体验 Redis。

![try-redis](https://oss.javaguide.cn/github/javaguide/database/redis/try.redis.io.png)

全世界有非常多的网站使用到了 Redis，[techstacks.io](https://techstacks.io/) 专门维护了一个[使用 Redis 的热门站点列表](https://techstacks.io/tech/redis)，感兴趣的话可以看看。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-01.md#L15)，来源许可：Apache-2.0。

<a id="k017163c7cf29"></a>

## 使用 Redis 实现一个排行榜怎么做？

Redis 中有一个叫做 `Sorted Set`（有序集合）的数据类型经常被用在各种排行榜的场景，比如直播间送礼物的排行榜、朋友圈的微信步数排行榜、王者荣耀中的段位排行榜、话题热度排行榜等等。

相关的一些 Redis 命令：`ZRANGE`（从小到大排序）、`ZREVRANGE`（从大到小排序）、`ZREVRANK`（指定元素排名）。

![](https://oss.javaguide.cn/github/javaguide/database/redis/2021060714195385.png)

[《Java 面试指北》](https://javaguide.cn/zhuanlan/java-mian-shi-zhi-bei.html) 的「技术面试题篇」就有一篇文章详细介绍如何使用 Sorted Set 来设计制作一个排行榜，感兴趣的小伙伴可以看看。

![](https://oss.javaguide.cn/github/javaguide/database/redis/image-20220719071115140.png)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-01.md#L333)，来源许可：Apache-2.0。

<a id="ka05ebbba38a6"></a>

## 使用Redis的好处有哪些？

1、访问速度快，因为数据存在内存中，类似于Java中的HashMap或者C++中的哈希表（如unordered_map/unordered_set），这两者的优势就是查找和操作的时间复杂度都是O(1)

2、数据类型丰富，支持String，list，set，sorted set，hash这五种数据结构

3、支持事务，Redis中的操作都是原子性，换句话说就是对数据的更改要么全部执行，要么全部不执行，这就是原子性的定义

4、特性丰富：Redis可用于缓存，消息，按key设置过期时间，过期后将会自动删除。

<p  id="与的区别都有哪些"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-02-01-Redis.md#L348)，来源许可：Apache-2.0。

<a id="kfce330267b77"></a>

## 压缩列表

> 压缩列表(ziplist)是列表键和哈希键的底层实现之一。当一个列表键只包含少量列表项，并且每个列表项要么就是小整数值，要么就是长度比较短的字符串，那么Redis就会使用压缩列表来做列表键的底层实现。

**特性**

看他的名字就能看出来，是为了节省内存造的列表结构。

<p  id="常见数据结构以及使用场景分别是什么"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-02-01-Redis.md#L256)，来源许可：Apache-2.0。

<a id="k3b9b8be9cf20"></a>

## 听说过Redis吗？它是什么？

Redis是一个**数据库**，不过与传统数据库不同的是Redis的数据库是存在**内存**中，所以**读写速度非常快**，因此 Redis被广泛应用于**缓存**方向。

除此之外，Redis也经常用来做分布式锁，Redis提供了多种数据类型来支持不同的业务场景。除此之外，Redis 支持事务持久化、LUA脚本、LRU驱动事件、多种集群方案。

<p  id="五种数据结构整理"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-02-01-Redis.md#L47)，来源许可：Apache-2.0。

<a id="k81d2259d4fa6"></a>

## 如何使用 Redis 事务？

Redis 可以通过 **`MULTI`、`EXEC`、`DISCARD` 和 `WATCH`** 等命令来实现事务（Transaction）功能。

```bash
> MULTI
OK
> SET PROJECT "JavaGuide"
QUEUED
> GET PROJECT
QUEUED
> EXEC
1) OK
2) "JavaGuide"
```

[`MULTI`](https://redis.io/commands/multi) 命令后可以输入多个命令，Redis 不会立即执行这些命令，而是将它们放到队列，当调用了 [`EXEC`](https://redis.io/commands/exec) 命令后，再执行所有的命令。

这个过程是这样的：

1. 开始事务（`MULTI`）；
2. 命令入队（批量操作 Redis 的命令，先进先出（FIFO）的顺序执行）；
3. 执行事务（`EXEC`）。

你也可以通过 [`DISCARD`](https://redis.io/commands/discard) 命令取消一个事务，它会清空事务队列中保存的所有命令。

```bash
> MULTI
OK
> SET PROJECT "JavaGuide"
QUEUED
> GET PROJECT
QUEUED
> DISCARD
OK
```

你可以通过[`WATCH`](https://redis.io/commands/watch) 命令监听指定的 Key，当调用 `EXEC` 命令执行事务时，如果一个被 `WATCH` 命令监视的 Key 被 **其他客户端/Session** 修改的话，整个事务都不会被执行。

```bash
# 客户端 1
> SET PROJECT "RustGuide"
OK
> WATCH PROJECT
OK
> MULTI
OK
> SET PROJECT "JavaGuide"
QUEUED

# 客户端 2
# 在客户端 1 执行 EXEC 命令提交事务之前修改 PROJECT 的值
> SET PROJECT "GoGuide"

# 客户端 1
# 修改失败，因为 PROJECT 的值被客户端2修改了
> EXEC
(nil)
> GET PROJECT
"GoGuide"
```

不过，如果 **WATCH** 与 **事务** 在同一个 Session 里，并且被 **WATCH** 监视的 Key 被修改的操作发生在事务内部，这个事务是可以被执行成功的（相关 issue：[WATCH 命令碰到 MULTI 命令时的不同效果](https://github.com/Snailclimb/JavaGuide/issues/1714)）。

事务内部修改 WATCH 监视的 Key：

```bash
> SET PROJECT "JavaGuide"
OK
> WATCH PROJECT
OK
> MULTI
OK
> SET PROJECT "JavaGuide1"
QUEUED
> SET PROJECT "JavaGuide2"
QUEUED
> SET PROJECT "JavaGuide3"
QUEUED
> EXEC
1) OK
2) OK
3) OK
127.0.0.1:6379> GET PROJECT
"JavaGuide3"
```

事务外部修改 WATCH 监视的 Key：

```bash
> SET PROJECT "JavaGuide"
OK
> WATCH PROJECT
OK
> SET PROJECT "JavaGuide2"
OK
> MULTI
OK
> GET USER
QUEUED
> EXEC
(nil)
```

Redis 官网相关介绍 [https://redis.io/topics/transactions](https://redis.io/topics/transactions) 如下：

![Redis 事务](https://oss.javaguide.cn/github/javaguide/database/redis/redis-transactions.png)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-02.md#L27)，来源许可：Apache-2.0。

<a id="kfcd476a3f64c"></a>

## 如何基于 Redis 实现延时任务？

> 类似的问题：
>
> - 订单在 10 分钟后未支付就失效，如何用 Redis 实现？
> - 红包 24 小时未被查收自动退还，如何用 Redis 实现？

基于 Redis 实现延时任务的功能无非就下面两种方案：

1. Redis 过期事件监听。
2. Redisson 内置的延时队列。

Redis 过期事件监听存在时效性较差、丢消息、多服务实例下消息重复消费等问题，不被推荐使用。

Redisson 内置的延时队列具备下面这些优势：

1. **减少了丢消息的可能**：DelayedQueue 中的消息会被持久化，即使 Redis 宕机了，根据持久化机制，也只可能丢失一点消息，影响不大。当然了，你也可以使用扫描数据库的方法作为补偿机制。
2. **消息不存在重复消费问题**：每个客户端都是从同一个目标队列中获取任务的，不存在重复消费的问题。

关于 Redis 实现延时任务的详细介绍，可以看我写的这篇文章：[如何基于 Redis 实现延时任务？](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-delayed-task.md)。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-01.md#L173)，来源许可：Apache-2.0。

<a id="kc49439d54afb"></a>

## 如何控制定期删除的执行频率？

在 Redis 中，定期删除的频率是由 **hz** 参数控制的。hz 默认为 10，代表每秒执行 10 次，也就是每秒钟进行 10 次尝试来查找并删除过期的 key。

hz 的取值范围为 1~500。增大 hz 参数的值会提升定期删除的频率。如果你想要更频繁地执行定期删除任务，可以适当增加 hz 的值，但这会增加 CPU 的使用率。根据 Redis 官方建议，hz 的值不建议超过 100，对于大部分用户使用默认的 10 就足够了。

下面是 hz 参数的官方注释，我翻译了其中的重要信息（Redis 7.2 版本）。

![redis.conf 对于 hz 的注释](https://oss.javaguide.cn/github/javaguide/database/redis/redis.conf-hz.png)

类似的参数还有一个 **dynamic-hz**，这个参数开启之后 Redis 就会在 hz 的基础上动态计算一个值。Redis 提供并默认启用了使用自适应 hz 值的能力，

这两个参数都在 Redis 配置文件 `redis.conf` 中：

```properties
# 默认为 10
hz 10
# 默认开启
dynamic-hz yes
```

多提一嘴，除了定期删除过期 key 这个定期任务之外，还有一些其他定期任务例如关闭超时的客户端连接、更新统计信息，这些定期任务的执行频率也是通过 hz 参数决定。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-01.md#L677)，来源许可：Apache-2.0。

<a id="k6eb6bf9f02cb"></a>

## 定期和惰性一定能保证删除数据吗？如果不能，Redis会有什么应对措施？

并不能保证一定删除，Redsi有一个Redis 内存淘汰机制来确保数据一定会被删除。

首先介一下定期删除和惰性删除的工作流程：

1、定期删除，Redis默认每个100ms检查，是否有过期的key,有过期key则删除。需要说明的是，Redis不是每个100ms将所有的key检查一次，而是随机抽取进行检查(如果每隔100ms,全部key进行检查，Redis岂不是卡死)。因此，如果只采用定期删除策略，会导致很多key到时间没有删除。

2、于是，惰性删除派上用场。也就是说在你获取某个key的时候，Redis会检查一下，这个key如果设置了过期时间那么是否过期了？如果过期了此时就会删除。

3、采用定期删除+惰性删除就没其他问题了么?
不是的，如果定期删除没删除key。然后你也没即时去请求key，也就是说惰性删除也没生效。这样，Redis

4、内存会越来越高。那么就应该采用内存淘汰机制。

在Redis.conf中有一行配置:maxmemory-policy volatile-lru

该配置就是配内存淘汰策略的，主要有以下六种方案：

1、**volatile-lru**：从已设置过期时间的数据集（server.db[i].expires）中挑选最近最少使用的数据淘汰

2、**volatile-ttl**：从已设置过期时间的数据集（server.db[i].expires）中挑选将要过期的数据淘汰

3、**volatile-random**：从已设置过期时间的数据集（server.db[i].expires）中任意选择数据淘汰

4、**allkeys-lru**：从数据集（server.db[i].dict）中挑选最近最少使用的数据淘汰

5、**allkeys-random**：从数据集（server.db[i].dict）中任意选择数据淘汰

6、**no-enviction**（驱逐）：禁止驱逐数据，新写入操作会报错

ps：如果没有设置 expire 的key, 不满足先决条件(prerequisites); 那么 volatile-lru, volatile-random 和 volatile-ttl 策略的行为, 和 noeviction(不删除) 基本上一致。

<p   id="对于大量的请求是怎样处理的"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-02-01-Redis.md#L494)，来源许可：Apache-2.0。

<a id="k361a1b481400"></a>

## 常见的数据优化方案你了解吗？

![](https://raw.githubusercontent.com/forthespada/InterviewGuide/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-02-02-Redis.assets/202205220023822.png)

**一、缓存双淘汰法**

1. 先淘汰缓存
2. 再写数据库
3. 往消息总线esb发送一个淘汰消息，发送立即返回。写请求的处理时间几乎没有增加，这个方法淘汰了缓存两次。因此被称为“缓存双淘汰法“，而在消息总线下游，有一个异步淘汰缓存的消费者，在拿到淘汰消息在1s后淘汰缓存，这样，即使在一秒内有脏数据入缓存，也能够被淘汰掉。

**二、异步淘汰缓存**

上述的步骤，都是在业务线里面执行，新增一个线下的读取binlog异步淘汰缓存模块，读取binlog总的数据，然后进行异步淘汰。

![](https://raw.githubusercontent.com/forthespada/InterviewGuide/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-02-02-Redis.assets/202205220023992.png)

这里简单提供一个思路

1.思路：

MySQL binlog增量发布订阅消费+消息队列+增量数据更新到Redis

1）读请求走Redis：热数据基本都在Redis

2）写请求走MySQL: 增删改都操作MySQL

3）更新Redis数据：MySQ的数据操作binlog，来更新到Redis

2.Redis更新

1）数据操作主要分为两块：

- 一个是全量(将全部数据一次写入到Redis)
- 一个是增量（实时更新）

这里说的是增量,指的是mysql的update、insert、delate变更数据。这样一旦MySQL中产生了新的写入、更新、删除等操作，就可以把binlog相关的消息推送至Redis，Redis再根据binlog中的记录，对Redis进行更新，就无需在从业务线去操作缓存内容。

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-02-02-Redis.md#L134)，来源许可：Apache-2.0。

<a id="ka6021167e51d"></a>

## 数据为什么会出现不一致的情况？

这样的问题主要是在并发读写访问的时候，缓存和数据相互交叉执行。

### **一、单库情况下**

同一时刻发生了并发读写请求，**例如为A(写) B (读)2个请求**

![](https://raw.githubusercontent.com/forthespada/InterviewGuide/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-02-02-Redis.assets/202205220023694.png)

1. A请求发送一个写操作到服务端，第一步会淘汰cache，然后因为各种原因卡主了，不在执行后面业务(例：大量的业务操作、调用其他服务处理消耗了1s）。

2. B请求发送一个读操作，读cache，因为cache淘汰，所以为空

3. B请求继续读DB，读出一个脏数据，并写入cache

4. A请求终于执行完全，在写入数据到DB

总结：因最后才把写操作数据入DB，并没同步。cache里面一直保持脏数据

脏数据是指源系统中的数据不在给定的范围内或对于实际业务毫无意义，或是数据格式非法，以及在源系统中存在不规范的编码和含糊的业务逻辑。

### **二、主从同步，读写分离的情况下，读从库而产生脏数据**

![](https://raw.githubusercontent.com/forthespada/InterviewGuide/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-02-02-Redis.assets/202205220023284.png)

1. A请求发送一个写操作到服务端，第一步会淘汰cache

2. A请求写主数据库，写了最新的数据。

3. B请求发送一个读操作，读cache，因为cache淘汰，所以为空

4. B请求继续读DB，读的是从库，此时主从同步还没同步成功。读出脏数据，然后脏数据入cache

5. 最后数据库主从同步完成

总结：这种情况下请求A和请求B操作时序没问题，是主从同步的时延问题(假设1s)，导致读请求读取从库读到脏数据导致的数据不一致

**根本原因:**

单库下，逻辑处理中消耗1s，可能读到旧数据入缓存

主从+读写分离，在1s的主从同步时延中，到从库的旧数据入缓存

<p  id="常见的数据优化方案你了解吗"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-02-02-Redis.md#L84)，来源许可：Apache-2.0。

<a id="ka031dba3dbc3"></a>

## 既然是单线程，那怎么监听大量的客户端连接呢？

Redis 通过 **IO 多路复用程序** 来监听来自客户端的大量连接（或者说是监听多个 socket），它会将感兴趣的事件及类型（读、写）注册到内核中并监听每个事件是否发生。

这样的好处非常明显：**I/O 多路复用技术的使用让 Redis 不需要额外创建多余的线程来监听客户端的大量连接，降低了资源的消耗**（和 NIO 中的 `Selector` 组件很像）。

文件事件处理器（file event handler）主要是包含 4 个部分：

- 多个 socket（客户端连接）
- IO 多路复用程序（支持多个客户端连接的关键）
- 文件事件分派器（将 socket 关联到相应的事件处理器）
- 事件处理器（连接应答处理器、命令请求处理器、命令回复处理器）

![文件事件处理器（file event handler）](https://oss.javaguide.cn/github/javaguide/database/redis/redis-event-handler.png)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-01.md#L487)，来源许可：Apache-2.0。

<a id="k2b66044221ce"></a>

## 有MySQL不就够用了吗？为什么要用Redis这种新的数据库？

主要是因为 Redis 具备高性能和高并发两种特性。

1、**高性能**

假如用户第一次访问数据库中的某些数据。这个过程会比较慢，因为是从硬盘上读取的。将该用户访问的数据存在缓存中，这样下一次再访问这些数据的时候就可以直接从缓存中获取了。

操作缓存就是直接操作内存，所以速度相当快。如果数据库中的对应数据改变的之后，同步改变缓存中相应的数据即可！

2、**高并发**

直接操作缓存能够承受的请求是远远大于直接访问数据库的，所以我们可以考虑把数据库中的部分数据转移到缓存中去，这样用户的一部分请求会直接到缓存这里而不用经过数据库。

<p  id="也是一种缓存型数据结构为什么不用而选择做缓存"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-02-01-Redis.md#L318)，来源许可：Apache-2.0。

<a id="k29afc2025b7f"></a>

## 每次随机抽查数量是多少？

`expire.c` 中定义了每次随机抽查的数量，Redis 7.2 版本为 20，也就是说每次会随机选择 20 个设置了过期时间的 key 判断是否过期。

```c
#define ACTIVE_EXPIRE_CYCLE_KEYS_PER_LOOP 20 /* Keys for each DB loop. */
```

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-01.md#L669)，来源许可：Apache-2.0。

<a id="kd12ce1bca76f"></a>

## 生产环境中的 Redis 是怎么部署的？

这个问题主要是想看看你了解不了解你们公司的 Redis 生产集群的部署架构。

如果你不了解，那么确实你就很失职了，你的 Redis 是主从架构？集群架构？用了哪种集群方案？有没有做高可用保证？有没有开启持久化机制确保可以进行数据恢复？线上 Redis 给几个 G 的内存？设置了哪些参数？压测后你们 Redis 集群承载多少 QPS？

Redis cluster，10 台机器，5 台机器部署了 Redis 主实例，另外 5 台机器部署了 Redis 的从实例，每个主实例挂了一个从实例，5 个节点对外提供读写服务，每个节点的读写高峰 QPS 可能可以达到每秒 5 万，5 台机器最多是 25 万读写请求每秒。

机器是什么配置？32G 内存+ 8 核 CPU + 1T 磁盘，但是分配给 Redis 进程的是 10g 内存，一般线上生产环境，Redis 的内存尽量不要超过 10g，超过 10g 可能会有问题。

5 台机器对外提供读写，一共有 50g 内存。

因为每个主实例都挂了一个从实例，所以是高可用的，任何一个主实例宕机，都会自动故障迁移，Redis 从实例会自动变成主实例继续提供读写服务。

你往内存里写的是什么数据？每条数据的大小是多少？商品数据，每条数据是 10kb。100 条数据是 1mb，10 万条数据是 1g。常驻内存的是 200 万条商品数据，占用内存是 20g，仅仅不到总内存的 50%。目前高峰期每秒就是 3500 左右的请求量。

其实大型的公司，会有基础架构的 team 负责缓存集群的运维。

<p id="reference"> </p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-02-02-Redis.md#L724)，来源许可：Apache-2.0。

<a id="ka257b10b4b01"></a>

## 简单动态字符串(Simple Dynamic String，SDS)

Redis没有直接使用C语言传统的字符串，而是自己构建了一种名为简单动态字符串（Simple dynamic string，SDS）的抽象类型，并将SDS用作Redis的默认字符串表示。

其实SDS等同于C语言中的char * ，但它可以存储任意二进制数据，不能像C语言字符串那样以字符’\0’来标识字符串的结 束，因此它必然有个长度字段。

**定义**

```c
struct sdshdr {
    // 记录buf数组中已使用字节的数量
    // 等于sds所保存字符串的长度
    int len;

    // 记录buf数组中未使用字节的数量
    int free;

    // 字节数组，用于保存字符串
    char buf[];
}
```

**优点**

- 获取字符串长度的复杂度为O(1)。
- 杜绝缓冲区溢出。
- 减少修改字符串长度时所需要的内存重分配次数。
- 二进制安全。
- 兼容部分C字符串函数。

它具有很常规的 set/get 操作，value 可以是String也可以是数字，一般做一些复杂的计数功能的缓存。

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/04-02-01-Redis.md#L58)，来源许可：Apache-2.0。

<a id="kd42dbbdb515b"></a>

## 说一下 Redis 和 Memcached 的区别和共同点

现在公司一般都是用 Redis 来实现缓存，而且 Redis 自身也越来越强大了！不过，了解 Redis 和 Memcached 的区别和共同点，有助于我们在做相应的技术选型的时候，能够做到有理有据！

**共同点**：

1. 都是基于内存的数据库，一般都用来当做缓存使用。
2. 都有过期策略。
3. 两者的性能都非常高。

**区别**：

1. **数据类型**：Redis 支持更丰富的数据类型（支持更复杂的应用场景）。Redis 不仅仅支持简单的 k/v 类型的数据，同时还提供 list、set、zset、hash 等数据结构的存储；而 Memcached 只支持最简单的 k/v 数据类型。
2. **数据持久化**：Redis 支持数据的持久化，可以将内存中的数据保持在磁盘中，重启的时候可以再次加载进行使用；而 Memcached 把数据全部存在内存之中。也就是说，Redis 有灾难恢复机制，而 Memcached 没有。
3. **集群模式支持**：Memcached 没有原生的集群模式，需要依靠客户端来实现往集群中分片写入数据；而 Redis 自 3.0 版本起是原生支持集群模式的。
4. **线程模型**：Memcached 是多线程、非阻塞 IO 复用的网络模型；而 Redis 使用单线程的多路 IO 复用模型（Redis 6.0 针对网络数据的读写引入了多线程）。
5. **特性支持**：Redis 支持发布订阅模型、Lua 脚本、事务等功能，而 Memcached 不支持。并且，Redis 支持更多的编程语言。
6. **过期数据删除**：Memcached 过期数据的删除策略只用了惰性删除，而 Redis 同时使用了惰性删除与定期删除。

相信看了上面的对比之后，我们已经没有什么理由可以选择使用 Memcached 来作为自己项目的分布式缓存了。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-01.md#L74)，来源许可：Apache-2.0。

<a id="k459a9843286d"></a>

## 面试追问：为什么选择 MongoDB、PostgreSQL、Redis 这样的存储组合？各自保存什么数据？

这类组合是一种工程选择，不是 Agent 项目的标配。MongoDB 可保存灵活结构的会话事件与工具记录；PostgreSQL 适合事务业务、明确字段、版本约束，也可承载 pgvector 与全文检索；Redis 适合短期缓存、限流、临时会话和有明确恢复语义的协调数据。

会话记录描述发生过什么，任务状态描述执行到哪里，记忆保存可复用信息，知识库保存外部业务证据，预约表保存权威业务结果。应明确每类数据的唯一权威写入点，避免同一事实在三个库里都可修改。

缓存失效、跨库一致性、删除传播、备份与故障恢复会增加成本。早期系统可先使用 PostgreSQL 加必要缓存，只有查询模式、规模或组织能力支持时才拆库。Redis 中的临时确认与锁不能替代持久化预约事务或可靠的幂等记录。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/07_%E4%BC%81%E4%B8%9A%E7%BA%A7Agent%E5%B9%B3%E5%8F%B0%E4%B8%8E%E4%BA%A7%E5%93%81%E8%90%BD%E5%9C%B0%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L294)，来源许可：GPL-3.0。
