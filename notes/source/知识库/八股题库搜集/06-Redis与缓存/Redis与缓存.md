# Redis与缓存

先确定数据的权威来源和允许的不一致窗口，再讨论缓存命中率和吞吐；缓存性能机制不能代替业务一致性协议。

<a id="m11c906b2dc2f"></a>

## 本地缓存、分布式缓存与权威数据

缓存保存可更快获取的数据副本，减少重复计算或慢存储访问。本地缓存访问路径短，但各进程独立，更新、容量和失效难以统一；分布式缓存便于多实例共享，却引入网络、服务依赖和远程故障。两者可分层组合，但层数越多，失效与一致性也越复杂。

使用前先定义缓存丢失后能否重建、数据过期能否容忍，以及数据库与缓存谁是权威来源。若把缓存同时当作唯一数据源，就必须按存储系统设计其持久化、复制和恢复，不能继续沿用“丢了随时重建”的假设。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-01.md#L95)。

<a id="m941d761a2f28"></a>

## 数据类型与访问方式匹配

String 适合独立值与计数；Hash 适合按字段读取和修改对象；List 提供顺序与两端操作；Set 表达去重集合及集合运算；Sorted Set 为成员附加分数，支持有序排名和范围访问。类型的意义在于让服务器直接执行所需操作，避免整段数据来回传输并在客户端重写。

选型要连同生命周期和原子操作考虑。把整个对象序列化为一个 String 便于整体替换，Hash 更适合独立字段变更，但过大的集合会形成大键。排行榜不仅需要排序，还要确定并列规则、更新方式和过期策略。不要因为数据“像对象”就不加分析地全部使用 Hash。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-01.md#L201)；[doocs/advanced-java](https://github.com/doocs/advanced-java/blob/80b89fb9496d7ea3213e402c8c3853399e00c363/docs/high-concurrency/redis-data-types.md#L1)。

<a id="m8ce2c34d664c"></a>

## 线程模型、命令串行与阻塞

Redis 的常见命令执行路径以串行处理共享数据为核心，省去大量细粒度锁竞争；内存访问、高效数据结构与事件驱动网络共同贡献性能。“Redis 单线程”只概括部分执行路径，后台持久化、释放资源及不同版本的 I/O 处理可能使用其他线程。

串行执行也意味着一个高成本命令会拖慢后续请求。巨大集合遍历、复杂脚本、慢存储引起的持久化干扰和网络大包都可能拉高延迟。应限制单次操作规模、使用分批扫描并监测慢命令，不能把所有瓶颈都归结为网络，或认为加入 I/O 线程就能并行执行任意写命令。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-01.md#L474)；[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-02.md#L786)。

<a id="m0977e158dd0b"></a>

## RDB、AOF 与恢复目标

RDB 保存某一时刻的数据快照，恢复时直接装载状态；AOF 记录写入操作，按日志重放恢复。快照适合备份与较快装载，但两次快照之间的变化可能丢失；AOF 的数据丢失窗口、写入成本和文件大小则受到刷盘与重写策略影响。重写根据当前数据生成更紧凑的等效日志，减少重放无用历史操作的成本。实际部署还可能组合快照与日志格式。

选择时先明确可接受丢失多少数据、恢复多久以及能承受怎样的后台开销。后台生成文件不代表完全没有影响：派生进程、写时复制、CPU 和磁盘压力都可能作用于服务延迟。复制也不能独立替代持久化或历史备份，因为误删除与错误写入同样可能被复制。

来源：[doocs/advanced-java](https://github.com/doocs/advanced-java/blob/80b89fb9496d7ea3213e402c8c3853399e00c363/docs/high-concurrency/redis-persistence.md#L1)。

<a id="mb4b8c2ce756f"></a>

## 过期删除与内存淘汰

过期时间决定数据何时不再有效；过期删除负责回收已经超时的键；内存淘汰则在达到内存限制时按策略选择牺牲哪些键。三者解决的问题不同。定期检查与访问时检查可以配合清理过期数据，但不意味着每个键到点就立刻消耗同样的删除动作。

淘汰策略要按数据是否可重建、是否设置 TTL、访问分布和内存上限选择。近似 LRU/LFU 等策略试图在控制开销的同时保留更有价值的数据；不能将它们描述成绝对精确的全局排序。大量键同时过期会把重建压力集中到后端，应错开有效期并限制回源并发。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-01.md#L591)；[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-01.md#L723)。

<a id="m46801c0b7f45"></a>

## 缓存穿透、击穿与雪崩

穿透是请求的数据本来就不存在，使请求长期绕过缓存；击穿是某个高热数据失效或未建立，集中回源；雪崩是大量缓存同时失效或缓存服务整体不可用，后端瞬间承受广泛回源。三者应按触发范围与数据是否存在区分，而不是只看“数据库压力变大”。

穿透可用输入校验、短期空值缓存或适当的存在性过滤降低无效请求；击穿可限制同键重建并发，或使用允许短期旧数据的逻辑过期；雪崩需要错峰过期、预热、容量预留以及限流降级。任何互斥重建方案都必须处理失败与超时，防止请求一直等待或在锁释放后同时再次回源。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-02.md#L626)。

<a id="m281371388a4b"></a>

## Cache Aside 与缓存数据库一致性

旁路缓存通常先读缓存，未命中再读数据库并回填；更新权威数据后使缓存失效，让后续读按需重建。删除而非直接更新，能够避免每次写入都计算昂贵派生值，也减少并发写把旧计算结果覆盖到缓存中的机会。

更新数据库与删除缓存不是一个跨系统原子操作，删除失败和并发旧值回填仍会产生窗口。需要可靠的失效重试、事务消息或变更订阅，并按业务定义 TTL、版本检查或串行重建。延迟双删是在特定时间假设下缩小窗口，不是无条件强一致协议。若业务不能接受旧值，就应让关键读走权威存储或使用更严格的一致性设计。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-02.md#L755)；[doocs/advanced-java](https://github.com/doocs/advanced-java/blob/80b89fb9496d7ea3213e402c8c3853399e00c363/docs/high-concurrency/redis-consistence.md#L1)。

<a id="md4638dcfaa65"></a>

## Redis 锁、过期与安全释放

在单个 Redis 实例上，获取锁常把“不存在才设置”与过期时间放进同一原子命令，并写入本次持有者唯一标识。释放时应原子地核对标识再删除，避免旧持有者删除已由他人重新获得的锁。把设置与过期拆成两步，会留下进程在中途失败后产生无期限锁的窗口。

过期时间防止故障持有者永久占锁，却不能让暂停中的旧进程立即停止执行。旧进程恢复时，新的持有者可能已经开始工作，因此关键资源还需幂等、版本校验或 fencing token。续期、主从切换和网络分区都会改变保证范围，不能把“用了 Lua”视为分布式互斥在所有故障下成立。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/distributed-system/distributed-system-interview-questions.md#L106)；[doocs/advanced-java](https://github.com/doocs/advanced-java/blob/80b89fb9496d7ea3213e402c8c3853399e00c363/docs/distributed-system/distributed-lock-redis-vs-zookeeper.md#L1)；[Redis 官方分布式锁说明](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/)。

<a id="m04646de72a85"></a>

## 事务、WATCH、Lua 与 pipeline

Redis 的事务将一组命令排队后连续执行，其他客户端命令不会在该组执行中任意插入，但执行阶段某条命令报错不意味着此前命令会像关系数据库那样回滚。`WATCH` 可以监视键是否被其他操作改变，并在冲突时放弃执行，调用方需要重新读取和决定是否重试。

Lua 或服务端函数可把判断和修改放在服务器端完成，适合短小的原子业务操作；执行时间过长会阻塞相关命令处理。pipeline 的主要目标是减少往返等待，不把任意一组命令升级成事务。回答三者时应分开网络批处理、并发隔离和失败回滚三个维度。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-02.md#L17)；[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-02.md#L194)。

<a id="m9396e85e9ab8"></a>

## 复制、Sentinel 与 Cluster 的分工

主从复制把主节点状态传播给副本；Sentinel 负责监测、故障判断与主节点切换等高可用协调；Cluster 通过槽划分数据并提供集群路由与故障处理。高可用和分片容量是相关但不同的目标，不能把三者当成同一个组件的不同名称。

异步复制可能留下未传播的已确认写，故障切换后存在丢失风险。Cluster 的多键操作还受键所在槽及命令支持限制，跨槽业务不能假设拥有单实例同样的原子边界。设计时要把客户端路由、重定向、失败重试、热点分布和允许的数据丢失窗口一起考虑。

来源：[doocs/advanced-java](https://github.com/doocs/advanced-java/blob/80b89fb9496d7ea3213e402c8c3853399e00c363/docs/high-concurrency/redis-master-slave.md#L1)；[doocs/advanced-java](https://github.com/doocs/advanced-java/blob/80b89fb9496d7ea3213e402c8c3853399e00c363/docs/high-concurrency/redis-sentinel.md#L1)；[doocs/advanced-java](https://github.com/doocs/advanced-java/blob/80b89fb9496d7ea3213e402c8c3853399e00c363/docs/high-concurrency/redis-cluster.md#L1)。

<a id="mc7cc3b996d65"></a>

## bigkey 与 hotkey 的不同治理

bigkey 指单个键占用过多内存或包含过多元素，影响传输、操作耗时、迁移与删除；hotkey 指访问高度集中，单键或其所在节点承受过多流量。一个键可以同时又大又热，也可以只符合其中之一，所以治理目标应分别确定。

大键常通过拆分数据、限制集合长度、分页读取和渐进删除来控制单次开销；热键则可考虑多级缓存、请求合并、适当复制读取和业务层拆分，但需同时处理失效一致性。仅增加分片不能自动分散单个键的压力；在生产环境发现大键也不应直接执行高成本全量扫描或同步大删除。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-02.md#L279)。

<a id="ma730808b1032"></a>

## Bitmap、HyperLogLog 与 Bloom Filter

这些结构都以特定能力换取空间效率。Bitmap 用位表达二值状态，适合可映射到稳定整数范围的签到或活跃标记；HyperLogLog 用近似统计估计去重数量，适合只关心基数、不需要列出成员的场景；Bloom Filter 判断“肯定不存在或可能存在”，允许误判存在。

因此它们不能替代一般集合的所有能力。使用前必须确认是否需要精确计数、删除元素、枚举成员以及可接受的误差。Bloom Filter 命中不能直接证明记录存在，仍需查询权威数据；普通 Bloom Filter 的删除也需要专门处理，而不是清除一个位就安全完成。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-01.md#L373)。

<a id="mbc1ac88ff612"></a>

## Redis 队列、Stream 与延迟任务

List 可实现简单队列，Stream 提供消息 ID、消费组和待确认管理，Sorted Set 可以按到期时间组织延迟任务。它们的差异在于消费确认、重投、保留、顺序范围和故障恢复能力，而不只是操作命令不同。

将数据取出与完成业务之间仍存在失败窗口。取出后进程崩溃可能导致工作丢失；完成后确认失败则可能重复处理。延迟任务还需要竞争领取、超时恢复与幂等。应按可靠性与规模要求选择方案，不把一个 `LPUSH/RPOP` 或按分数查询就描述成完整的可靠消息系统。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/database/redis/redis-questions-01.md#L164)。

## 专题阅读

- [Redis实践问答](Redis%E5%AE%9E%E8%B7%B5%E9%97%AE%E7%AD%94.md)
- [持久化、复制与集群](%E6%8C%81%E4%B9%85%E5%8C%96%E3%80%81%E5%A4%8D%E5%88%B6%E4%B8%8E%E9%9B%86%E7%BE%A4.md)
- [数据结构与命令](%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84%E4%B8%8E%E5%91%BD%E4%BB%A4.md)
- [缓存一致性与高并发](%E7%BC%93%E5%AD%98%E4%B8%80%E8%87%B4%E6%80%A7%E4%B8%8E%E9%AB%98%E5%B9%B6%E5%8F%91.md)
- [过期、淘汰与内存](%E8%BF%87%E6%9C%9F%E3%80%81%E6%B7%98%E6%B1%B0%E4%B8%8E%E5%86%85%E5%AD%98.md)
