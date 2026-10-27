# Java与JVM

API 语义与具体 HotSpot 实现分开说明；涉及实现演变时明确版本，不把旧版本的结构当成全部 JDK 的固定规则。

<a id="m90a28f24b8da"></a>

## 值传递、引用与对象身份

Java 的方法参数始终按值传递。基本类型复制其值，引用类型复制引用值；两个引用可能仍指向同一个对象，所以通过形参修改对象内部状态会被调用方观察到，而把形参重新指向另一对象不会改变调用方变量。这一规则同时解释了“Java 是值传递还是引用传递”“交换两个对象引用为什么不生效”。

判断代码时先画出变量与对象的对应关系，再区分“修改对象”与“修改引用变量”。`==` 比较基本类型的值；用于引用时比较是否指向同一对象。`equals` 是否比较内容取决于类的实现，不能把所有对象的 `equals` 都当作深度比较。

来源：[Oracle：方法参数传递](https://docs.oracle.com/javase/tutorial/java/javaOO/arguments.html)。

<a id="m046b83a7a2c6"></a>

## equals、hashCode 与哈希集合的约定

`equals` 定义逻辑相等，`hashCode` 帮助哈希容器缩小查找范围。相等对象必须具有相同哈希值；哈希值相同的对象仍可能不相等，容器需要继续比较。自定义值对象若只重写 `equals`，两个逻辑相等的对象可能落入不同桶，破坏集合去重和映射查找。

作为键参与相等判断的字段应尽量不可变。对象放入 `HashMap` 后若改变这些字段，新哈希值可能指向另一桶，使用同一对象也可能找不到原记录。面试追问不应停在“必须同时重写”，还要说明哈希定位、碰撞判断与键稳定性的因果链。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/basis/java-basic-questions-02.md#L550)；[Java 21 Object 契约](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Object.html)。

<a id="m02a12a6a3ed6"></a>

## String 不可变与字符串构建

`String` 不可变指一个字符串对象创建后，其对外可观察的字符序列不能通过公开接口改变。关键是封装内部存储、不给外部提供修改路径，并限制子类破坏语义；仅有 `final` 引用不足以保证数组内容不可变。不可变性便于安全共享、缓存哈希值和作为键使用。

重复拼接可使用当前线程私有的 `StringBuilder`；`StringBuffer` 的同步方法并不自动让跨多个调用的业务操作成为原子事务。不要把字符串内部永远描述为 `char[]`：Java 9 引入紧凑字符串后，常见 HotSpot/JDK 实现用 `byte[]` 配合编码标记。一次简单 `+` 连接通常交给编译器和运行时优化，循环构建才需要关注重复创建中间结果的成本。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/basis/java-basic-questions-02.md#L606)。

<a id="mb3b662f99574"></a>

## ArrayList、LinkedList 与集合选择

`ArrayList` 以可扩展数组保存引用，随机访问直接按下标定位，尾部追加通常具有较好的均摊成本；中间插删需要搬移后续元素。`LinkedList` 以节点连接元素，已定位节点后的链接调整便宜，但按下标寻找位置仍要遍历，并额外承担节点内存和指针追踪成本。

因此“频繁插删就选链表”缺少位置条件。若操作主要按下标查找或在尾部追加，数组通常更合适；队列、双端队列还应比较 `ArrayDeque` 等实现。两者都不因实现不同而自动线程安全。集合选择应围绕访问方式、容量变化、迭代局部性和并发需求，而非单看一种操作的理论复杂度。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/collection/java-collection-questions-01.md#L201)。

<a id="m109748dffe40"></a>

## HashMap 的定位、碰撞与扩容

`HashMap` 先对键的哈希值作处理，再定位桶；同桶内继续核对哈希和键相等性。桶数组长度取 2 的幂，使位运算定位方便，扩容时可利用新增的高位把原桶元素分到两个位置。均匀散列时查找接近常数时间，严重碰撞会降低效率。

JDK 8 的常见实现结合数组、链表和红黑树：长链在容量条件满足时才树化，较小数组通常先扩容。阈值是具体实现策略，不是 `Map` 接口契约。`HashMap` 没有并发修改保护，扩容或更新冲突都不能靠“单次 put 很快”规避。预估容量可以减少扩容，但过量预分配同样增加内存与遍历成本。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/collection/java-collection-questions-02.md#L180)。

<a id="md396176bc0ae"></a>

## ConcurrentHashMap 的并发边界

`ConcurrentHashMap` 让多个线程安全地访问映射。JDK 7 的分段设计与 JDK 8 起的桶级更新方案应分别回答，不能把 `Segment` 当作现代实现的固定结构。读取通常不获取更新桶使用的锁；更新会结合原子操作与局部同步协调。

线程安全的方法不等于任意方法组合都原子。例如“先 containsKey，再 put”之间可插入另一个线程的更新。需要按业务使用 `putIfAbsent`、`compute`、`merge` 等复合 API，映射函数也应保持短小并遵守 API 的限制。它不允许空键和空值；并发遍历通常反映变化过程中的状态，`size` 等聚合结果不能在持续修改时当成全表事务快照。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/collection/java-collection-questions-02.md#L493)；[Java 21 ConcurrentHashMap](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ConcurrentHashMap.html)。

<a id="m62ccb2e95430"></a>

## 泛型的类型检查与类型擦除

泛型把类型约束前移到编译期，让容器等代码复用而不丢失静态检查。Java 泛型通常通过擦除实现：编译器检查类型参数，在需要的位置插入转换，运行时并不为每一种类型实参生成一套普通对象类。因此不能简单用 `instanceof List<String>` 检查元素类型，也不能直接创建类型参数的实例。

`? extends T` 适合把元素当作 T 读取，却通常无法安全加入任意 T；`? super T` 允许放入 T，但读取时只能获得更弱的静态类型。这里的限制来自编译器必须保证所有合法实参都安全，不是通配符让容器本身变成只读。反射可能读取声明中的泛型信息，但这不等于运行时对每次写入都有同样的泛型检查。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/basis/java-basic-questions-03.md#L219)。

<a id="mbee97de62506"></a>

## 反射、注解与框架的运行时装配

反射允许程序在运行时检查类型、构造对象、读取属性或调用方法，注解则为类型和成员附加结构化元数据。二者常在依赖注入、对象映射、测试框架和插件装配中配合：框架先发现元数据，再据此完成对象创建或方法调用。

代价包括运行时错误更晚暴露、封装与模块访问限制更复杂，以及某些路径上的额外开销。不能把“反射一定很慢”当成设计结论，也不能默认任何私有成员都能无条件访问。业务代码若在编译时已知道依赖，优先保持清晰的静态接口；确有动态装配需求时再引入反射，并缓存稳定的解析结果。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/basis/java-basic-questions-03.md#L338)。

<a id="m972006108891"></a>

## 异常分类与资源释放

Java 的异常体系以 `Throwable` 为根。受检查异常要求调用点捕获或声明；运行时异常与 `Error` 属于不受检查异常。分类描述的是编译期约束，不直接决定业务能否恢复。捕获异常后应补偿、转换或保留足够上下文，单纯吞掉异常会把失败伪装成成功。

资源管理应优先使用 `try-with-resources` 关闭实现 `AutoCloseable` 的资源。`finally` 适合必须执行的清理逻辑，但在其中返回或抛出新异常可能掩盖原结果；进程被强制终止等情况也不能保证执行。区分“当前线程失败”“整个服务不可用”和“资源必须回收”三个层次，比背诵 `Exception` 与 `Error` 的名称更有用。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/basis/java-basic-questions-03.md#L18)。

<a id="me790d9e573fc"></a>

## JMM、volatile 与安全发布

Java 内存模型规定线程之间对共享数据的可见性与合法执行顺序。`happens-before` 是判断一个动作的结果能否被另一个动作可靠观察到的规则，不是简单按现实时间先后排序。对同一监视器的解锁与后续加锁、线程启动以及 `volatile` 写读等都能建立关系，再通过传递性覆盖相关普通写入。

`volatile` 适合状态发布：先写配置对象，再写完成标志，读取线程观察到对应标志后才能依赖被发布的数据。它不把“读—改—写”合为原子操作，所以 `volatile count++` 仍可能丢更新。共享计数用原子类或锁；多字段不变量通常需要把相关操作放进同一同步协议。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/concurrent/java-concurrent-questions-02.md#L138)。

<a id="mb5cdc703d064"></a>

## synchronized、ReentrantLock 与 AQS

锁既限制临界区并发进入，也建立共享数据的可见性关系。`synchronized` 由语言与 JVM 支持，离开同步区域时自动释放；`ReentrantLock` 通过显式 API 提供可中断获取、尝试获取、超时和多个条件队列等能力，必须在 `finally` 中释放成功获取的锁。

可重入表示同一线程能再次获取自己持有的锁，不能据此推导出“不会死锁”。AQS 是许多同步器使用的状态与排队框架：子类决定怎样修改同步状态，框架负责竞争失败后的排队、阻塞与唤醒。选择锁应从取消需求、条件等待、竞争方式和可维护性出发；不要把旧 HotSpot 的完整锁升级顺序当成所有 JDK 的永久规则。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/concurrent/java-concurrent-questions-02.md#L776)；[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/concurrent/java-concurrent-questions-03.md#L1219)。

<a id="m07c8b0251c14"></a>

## CAS、ABA 与原子类

CAS 在一个不可分割的步骤中比较当前位置是否仍等于预期值，符合才写入新值。它适合小范围状态更新，使调用方能以“读取—计算—尝试提交”的方式处理竞争；失败者通常重试，而不是把操作默默当作成功。

问题在于值可能经历 A→B→A，单看最终相等无法识别中间变化，这就是 ABA。若业务必须识别变化历史，应把版本号与值一起比较。高竞争下反复重试会消耗 CPU，多变量的业务不变量也不能靠几个独立原子字段自动保证。原子类是构建同步协议的工具，是否比锁更合适取决于竞争强度、临界区复杂度和进展要求。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/concurrent/java-concurrent-questions-02.md#L345)。

<a id="mbc0afa0f5fa6"></a>

## ThreadLocal 的隔离与线程池清理

`ThreadLocal` 把变量的不同值放进各线程持有的映射中，解决同一段代码需要使用线程专属上下文的问题。它提供的是线程隔离，不是共享对象的线程安全：若不同线程保存的值仍引用同一可变对象，竞争依然存在。

线程池使工作线程比一次请求活得更久。未移除的上下文既可能占住对象，也可能污染后续任务。内部弱引用键并不能代替业务清理，因为值及线程的生命周期不同。正确做法是在设置后明确作用范围，并在 `finally` 中 `remove`；跨线程或异步链需要显式传递上下文或使用明确的传播机制，而不能假设普通 ThreadLocal 会自动跟随任务。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/concurrent/java-concurrent-questions-03.md#L48)。

<a id="m6956ce28ea50"></a>

## 线程池的执行流程、队列与拒绝

线程池通过复用线程、限制并发与集中管理任务来控制资源。典型 `ThreadPoolExecutor` 在工作线程不足核心数量时创建线程；否则尝试入队，队列满后才尝试扩到最大线程数，仍无法接收时执行拒绝策略。这解释了为什么配置了很大的最大线程数，却在无界队列下看不到扩容。

队列长度决定排队延迟与内存风险，线程数则要结合 CPU 计算、阻塞等待、下游并发上限和延迟目标。拒绝可以显式失败、让调用方执行或丢弃，但每种方式都对应业务后果；`CallerRunsPolicy` 可能把耗时转移到请求线程。应监测活跃线程、队列长度、排队时间、拒绝和任务耗时，基于负载验证配置，而不只套一个线程数公式。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/concurrent/java-concurrent-questions-03.md#L548)；[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/concurrent/java-concurrent-questions-03.md#L865)。

<a id="m70bf2a9f8a6c"></a>

## Future、CompletableFuture 与异步依赖

`Future` 表示一个尚未完成的计算结果，调用 `get` 仍可能阻塞。`CompletableFuture` 在此基础上提供依赖组合：结果转换、多个任务汇合、异常处理和完成回调，使依赖关系从手工等待变成明确的执行图。

异步不等于无限增加并发。阻塞任务若占满共享执行器，彼此等待可能放大尾延迟；应区分计算与阻塞任务，明确使用的线程池、超时与异常传播。任一分支失败后，其他分支是否取消、能否接受部分结果以及最终如何响应，都属于业务设计；取消一个 Future 也不保证底层操作必然立刻停止。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/concurrent/java-concurrent-questions-03.md#L1045)。

<a id="m206e3a41d213"></a>

## JVM 内存区域与 OOM 定位

运行时内存区域用来区分数据的归属和生命周期。堆主要保存对象；线程执行方法时使用栈帧记录局部变量、操作数栈等；方法区是规范中的逻辑区域，HotSpot 的元空间是其中一种实现。直接内存不等同于 Java 堆，调大堆上限不能解决所有内存不足。

出现异常先确认耗尽位置和增长对象：堆、元空间、直接内存、线程本地资源可能对应不同原因。栈深过大与持续保留对象不是同一问题。排查应保留 GC 日志、线程栈、堆转储和系统指标，再定位引用链或资源生命周期；不要把所有 OOM 都回答成“内存泄漏”或直接增加 `-Xmx`。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/jvm/jvm-interview-questions.md#L33)。

<a id="md75e80bc6526"></a>

## 类加载、初始化与类身份

类加载把类的字节表示变成运行时可用的类结构；连接包含验证、准备与解析，初始化执行相应静态初始化逻辑。加载到内存不等于已完成初始化，触发时机要和实际使用方式区分。双亲委派描述常见类加载器的查找协作方式，目的包括减少重复加载与维护核心类型的一致性，不是 JVM 规定所有自定义加载器都必须遵守的唯一算法。

运行时类身份不仅看全限定名，还与定义它的类加载器有关。插件隔离、容器部署或热加载中，即使类名相同也可能不是同一种类型。类加载器仍被引用时，其关联的类型与元数据可能无法卸载，因此元空间增长要同时检查动态生成类和加载器引用，而不只查看业务对象数量。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/jvm/jvm-interview-questions.md#L56)。

<a id="m3d09f8a6c19e"></a>

## 垃圾回收的可达性、算法与停顿

垃圾回收首先判断对象是否仍能从 GC Roots 到达，再由具体收集器组织内存回收。引用计数不能独立解决互相引用但已与根断开的对象；可达性分析也不表示每个对象一失去引用就立刻回收。标记、复制、整理等方法分别权衡额外空间、碎片、移动成本和暂停时间。

收集器选择应服从吞吐、延迟、堆规模与运行版本。并发回收能把部分工作与业务线程重叠，但不等于没有暂停，也不等于回收不消耗 CPU。频繁 GC 需要结合分配速率、存活比例、晋升、堆配置和停顿日志定位。先证明瓶颈，再更换收集器或调整参数；不要把“发生 Full GC”本身当成根因。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/jvm/jvm-interview-questions.md#L81)。

<a id="m2bde99a7ec4d"></a>

## Spring IoC、Bean 生命周期与 AOP

IoC 把对象创建与依赖装配交给容器，依赖注入是实现这种控制反转的方式。容器读取配置或元数据，实例化对象、设置依赖，再执行相应初始化回调；销毁回调的执行还取决于作用域和容器是否正常管理该实例。单例 Bean 表示容器中的实例数量策略，不代表其中的可变字段天然线程安全。

AOP 把事务、监控等横切行为附着到方法调用边界，常见 Spring 场景通过代理实现。必须分清“获取的是代理对象”和“对象内部直接调用自身方法”：后者可能绕过代理，通知不会按预期执行。依赖关系应尽量清晰，循环依赖并非所有构造方式、作用域和配置下都能被容器自动解决。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/system-design/framework/spring/spring-knowledge-and-questions-summary.md#L118)；[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/system-design/framework/spring/spring-knowledge-and-questions-summary.md#L486)。

<a id="mb1813b085861"></a>

## Spring 事务代理、传播与回滚边界

声明式事务通过拦截符合条件的方法调用，在执行前后管理事务边界。事务是否生效取决于调用是否经过代理、事务管理器、方法与代理机制等条件。对象内部自调用可能绕过代理；把耗时远程调用放在数据库事务内，还可能让锁与连接被长时间占用。

传播行为回答“已有事务时怎样参加或另开事务”，隔离级别回答“并发事务之间能观察到什么”，两者不能互相替代。默认回滚规则与显式配置需要分别说明；捕获异常后正常返回，拦截器可能无法按预期判定失败。设计事务时先确定必须一起成功的数据库修改，再选择回滚规则和传播方式，跨服务操作则需要分布式一致性方案。

来源：[Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/system-design/framework/spring/spring-knowledge-and-questions-summary.md#L983)；[Spring 声明式事务](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html)。

## 专题阅读

- [JVM、类加载与垃圾回收](JVM%E3%80%81%E7%B1%BB%E5%8A%A0%E8%BD%BD%E4%B8%8E%E5%9E%83%E5%9C%BE%E5%9B%9E%E6%94%B6.md)
- [Java综合问答（1）](Java%E7%BB%BC%E5%90%88%E9%97%AE%E7%AD%94-01.md)
- [Java综合问答（2）](Java%E7%BB%BC%E5%90%88%E9%97%AE%E7%AD%94-02.md)
- [Java综合问答（3）](Java%E7%BB%BC%E5%90%88%E9%97%AE%E7%AD%94-03.md)
- [Spring与应用框架](Spring%E4%B8%8E%E5%BA%94%E7%94%A8%E6%A1%86%E6%9E%B6.md)
- [并发与线程](%E5%B9%B6%E5%8F%91%E4%B8%8E%E7%BA%BF%E7%A8%8B.md)
- [语言基础与对象](%E8%AF%AD%E8%A8%80%E5%9F%BA%E7%A1%80%E4%B8%8E%E5%AF%B9%E8%B1%A1.md)
- [集合与数据结构（1）](%E9%9B%86%E5%90%88%E4%B8%8E%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84-01.md)
- [集合与数据结构（2）](%E9%9B%86%E5%90%88%E4%B8%8E%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84-02.md)
