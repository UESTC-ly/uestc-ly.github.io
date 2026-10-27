# JVM、类加载与垃圾回收

<a id="k3069b6d6eae6"></a>

## JVM 中对象从创建到回收大致经历了哪些阶段？

**回答：**

以 HotSpot 中普通 `new` 对象为例，可以沿着“类的准备、分配、初始化、使用、可达性变化、回收”理解。类加载与解析并非每创建一个对象都重新执行；`new` 涉及的类在需要时完成加载、链接，并在首次主动使用前完成类初始化。类初始化执行静态初始化逻辑，与每个对象的构造方法不同。

1. **分配内存。** 常见路径先尝试线程本地分配缓冲区 TLAB，减少共享堆分配竞争；大对象、TLAB 不足或不同收集器会进入其他分配路径。具体使用指针碰撞还是空闲空间管理，取决于堆组织方式。
2. **建立初始状态。** 实例字段先获得零值，运行时设置对象头等信息；随后执行实例初始化和构造逻辑。零值初始化不等于执行了业务构造方法。
3. **使用与发布。** 对象被线程、集合或其他对象引用。跨线程传递仍需安全发布，不能认为“构造完了”就天然对另一线程可见。避免在构造函数中让 `this` 提前逸出。
4. **判断存活。** GC 从线程栈、静态字段等根集合出发分析可达性，并处理强、软、弱、虚引用等不同语义。循环引用本身不会阻止可达性分析回收。
5. **回收或移动。** 收集器释放不可达对象占据的空间，可能伴随复制、整理和引用更新。对象何时回收没有应用层的及时性保证。

并非所有对象都实际完成一次堆分配：JIT 的逃逸分析和标量替换可能消除分配，但这不意味着“所有不逃逸对象都直接放到栈上”。晋升老年代也不是所有对象必经的阶段，具体取决于收集器和存活情况。

`finalize()` 已被弃用并标记为待移除，不能用于可靠释放资源。文件、连接、锁应采用 `try-with-resources`、显式关闭或 `finally` 等确定性路径；Cleaner 也只是兜底，不能承诺及时执行。

<a id="baidu-agent-20260922-r1-q3"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%99%BE%E5%BA%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L736)，来源许可：GPL-3.0。

<a id="k8774a0e702ce"></a>

## JVM 参数与诊断工具

参数题考察的是配置依据。堆大小、年轻代比例、收集器和日志参数要跟部署内存、对象分配速率、延迟目标及 JDK 版本一起讨论。尤其是 G1，通常不建议照搬以固定年轻代大小为中心的旧配置。

相关内容：

- [JVM 常用参数总结](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/jvm/jvm-parameters-intro.md)
- [JDK 监控和故障处理工具总结](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/jvm/jdk-monitoring-and-troubleshooting-tools.md)

常见面试题：

- `-Xms`、`-Xmx`、`-Xmn` 和 `-Xss` 分别控制什么？
- 为什么服务端应用常把 `-Xms` 和 `-Xmx` 设为相同值？
- `-XX:MetaspaceSize` 和 `-XX:MaxMetaspaceSize` 有什么区别？
- 怎样为应用选择垃圾收集器？切换收集器前要收集哪些数据？
- JDK 8 和 JDK 9 及之后怎样配置 GC 日志？
- 发生 OOM 时怎样自动生成 Heap Dump？为什么要提前确认存储空间？
- `jps`、`jstat`、`jinfo`、`jmap`、`jstack` 和 `jcmd` 分别适合查什么？
- 怎样用 `jstat` 观察 GC 频率、各区域容量和对象晋升情况？
- 线程长时间阻塞、死锁或 CPU 飙高时，线程转储能提供什么信息？
- Heap Dump 和线程转储有什么区别？`kill -3` 生成的是哪一种？
- MAT 分析 Heap Dump 时，Dominator Tree 和到 GC Roots 的引用链分别有什么用？
- JFR、JMC、VisualVM 适合观察哪些运行时信息？在线采集时要考虑什么开销？

生成 Heap Dump、类直方图或高频采样都有可能增加线上负载，Dump 文件也可能包含业务数据。执行诊断命令前要确认影响范围、磁盘空间和文件保存位置；紧急重启前，至少保留告警时间、关键指标、线程栈和必要的 GC 信息。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/jvm/jvm-interview-questions.md#L109)，来源许可：Apache-2.0。

<a id="kcd52963c6873"></a>

## JVM 线上问题排查

线上排查通常没有“一个命令直接定位”的答案。收到告警后先核对时间、影响范围、最近变更和系统资源，再决定采集线程栈、GC 日志还是堆转储。若服务已经影响用户，止血和留证需要同时安排，不能为了抓全量证据让故障继续扩大。

相关内容：[Java 后端线上问题排查](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/jvm/jvm-in-action.md)

常见面试题：

- CPU 飙高时，怎样从进程定位到线程和具体代码栈？
- CPU 不高但 Load 很高，应该检查哪些线程状态和系统指标？
- 接口响应很慢但 CPU 使用率正常，怎样区分锁等待、I/O、连接池和下游延迟？
- 内存持续上涨时，怎样判断是业务缓存增长、对象分配过快还是内存泄漏？
- Java 进程 OOM 后，怎样判断问题发生在堆、元空间、直接内存还是本地内存？
- Young GC 很频繁，但每次回收很快，应该重点检查什么？
- Full GC 频繁时，怎样观察老年代增长、对象晋升和回收效果？
- Heap Dump 应该在什么时候生成？生产环境直接执行 `jmap -dump` 有什么风险？
- 线程池队列堆积与 CPU 使用率、线程状态之间有什么关系？
- 修复 JVM 问题后，应该对比哪些指标来确认改动有效？
- 面试中怎样讲一次没有亲历过的 JVM 故障排查题？

排查结果要能形成证据链。例如 CPU 飙高时，先找到高 CPU 的 Java 进程和线程，把线程 ID 转成线程转储使用的格式，再核对多次线程栈是否持续落在同一段代码。内存问题则要结合 GC 日志、对象直方图、Heap Dump 和本机内存，单看 JVM 堆使用率无法覆盖所有 OOM。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/jvm/jvm-interview-questions.md#L135)，来源许可：Apache-2.0。

<a id="k4a32a74df4ab"></a>

## JVM加载一个class文件的完整过程是什么？

**回答：**

JVM 对类的生命周期通常描述为：**加载（Loading）-> 链接（Linking：验证、准备、解析）-> 初始化（Initialization）-> 使用 -> 卸载**。其中解析在规范允许的范围内可以延迟执行，所以不要把所有实现细节说成绝对同步顺序。

1. **加载：** 类加载器根据二进制名定位字节流，JVM 解析 class 文件并在方法区/元空间建立运行时表示，同时创建对应的 `java.lang.Class` 对象。来源可以是文件、JAR、网络或运行时生成的字节码。
2. **验证：** 检查文件格式、元数据、字节码和符号引用是否合法，保证类型安全与控制流约束。验证通过不代表业务代码安全。
3. **准备：** 为类的 `static` 字段分配存储并设置 JVM 规定的默认值；带 `ConstantValue` 属性的编译期常量可在该阶段赋值。普通静态赋值语句不是在这里执行。
4. **解析：** 将运行时常量池中的符号引用转换为直接引用，涉及类/接口、字段、方法、方法句柄等；可以采用惰性解析。
5. **初始化：** 执行类初始化方法 `<clinit>`，其内容由静态字段赋值和静态代码块按源码顺序合并。JVM 保证同一个类加载器定义的类只初始化一次，并进行同步；初始化子类前先初始化父类，但接口初始化规则不同。

主动使用通常包括 `new`、访问非编译期常量静态字段、调用静态方法、反射和初始化子类等；仅引用编译期常量或创建该类型数组通常不会触发初始化。

类身份由“二进制类名 + 定义它的类加载器”共同决定。常见父级委派用于避免核心类被重复定义，但模块化、插件、容器会使用更复杂的委派策略。类卸载通常要求其定义类加载器不可达且相关类对象不再可达，实际何时回收由 JVM 决定。

<a id="insta360-agent-20260809-q18"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%BD%B1%E7%9F%B3%E5%88%9B%E6%96%B0%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L354)，来源许可：GPL-3.0。

<a id="kb149972cb0e5"></a>

## 什么是字节码？采用字节码的好处是什么？

在 Java 中，JVM 可以理解的代码就叫做字节码（即扩展名为 `.class` 的文件），它不面向任何特定的处理器，只面向虚拟机。Java 语言通过字节码的方式，在一定程度上解决了传统解释型语言执行效率低的问题，同时又保留了解释型语言可移植的特点。所以， Java 程序运行时相对来说还是高效的（不过，和 C、 C++，Rust，Go 等语言还是有一定差距的），而且，由于字节码并不针对一种特定的机器，因此，Java 程序无须重新编译便可在多种不同操作系统的计算机上运行。

**Java 程序从源代码到运行的过程如下图所示**：

![Java程序转变为机器代码的过程](https://oss.javaguide.cn/github/javaguide/java/basis/java-code-to-machine-code.png)

我们需要格外注意的是 `.class->机器码` 这一步。以 HotSpot 为例，JVM 加载字节码后可以先解释执行，并识别经常调用的方法和代码块（即热点代码），再由 **JIT（Just in Time Compilation）** 编译器将热点字节码编译为机器码。在当前 JVM 进程后续执行这些代码时，可以直接使用已编译的机器码。这也解释了我们为什么经常会说 **Java 是编译与解释共存的语言**。不过，JVM 规范并不要求具体实现必须包含解释器或 JIT 编译器。

> 🌈 拓展阅读：
>
> - [基本功 | Java 即时编译器原理解析及实践 - 美团技术团队](https://mp.weixin.qq.com/s/7PH8o1tbjLsM4-nOnjbwLw)
> - [基于静态编译构建微服务应用 - 阿里巴巴中间件](https://mp.weixin.qq.com/s/4haTyXUmh8m-dBQaEzwDJw)

![Java程序转变为机器代码的过程](https://oss.javaguide.cn/github/javaguide/java/basis/java-code-to-machine-code-with-jit.png)

> HotSpot 采用了惰性评估(Lazy Evaluation)的做法，根据二八定律，消耗大部分系统资源的只有那一小部分的代码（热点代码），而这也就是 JIT 所需要编译的部分。JVM 会根据代码每次被执行的情况收集信息并相应地做出一些优化，因此执行的次数越多，它的速度就越快。

JDK、JRE、JVM、JIT 这四者的关系如下图所示。

![JDK、JRE、JVM、JIT 这四者的关系](https://oss.javaguide.cn/github/javaguide/java/basis/jdk-jre-jvm-jit.png)

下面这张图是 JVM 的大致结构模型。

![JVM 的大致结构模型](https://oss.javaguide.cn/github/javaguide/java/basis/jvm-rough-structure-model.png)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/basis/java-basic-questions-01.md#L86)，来源许可：Apache-2.0。

<a id="kaed98f55f8c7"></a>

## 介绍一个熟悉的 Java 垃圾回收器

**回答：**

可以介绍 JDK 21 HotSpot 中的 G1。G1 将堆划分为多个大小相同的 Region，逻辑上区分 Eden、Survivor、Old 等角色，通过选择回收收益较高的区域控制停顿。Region 化并不意味着完全取消分代，也不意味着每次回收都遍历整个老年代。

年轻代回收会在 Stop-The-World 阶段将存活对象从回收集复制到其他 Region，更新引用并释放原区域。G1 通过 Remembered Set 和写屏障等机制追踪跨区域引用，减少局部回收时需要扫描的范围。并发标记与应用线程交错执行，仍包含需要停顿的阶段；标记结果帮助后续 Mixed GC 选择部分老年代区域与年轻代一起回收。

G1 使用 SATB 思路支持并发标记，记录标记期间可能影响快照可达性的信息；它不是保证程序执行期间所有垃圾立即被清理。大对象可能成为 Humongous 对象并占用连续 Region，增加分配和空间管理压力。若可用空间不足或复制失败，可能出现更重的回收甚至 Full GC，不能把 G1 描述成“没有长停顿”。

调优先看 GC 日志、分配速率、晋升情况、存活集、停顿分位数、Humongous 分配和应用吞吐。MaxGCPauseMillis 是尽力满足的目标，不是硬实时保证；缩小停顿目标可能增加回收频率、降低吞吐。堆大小、并发标记启动时机和区域选择应结合负载验证，不能只套一组参数。

面试时可以联系 AI 应用的实际对象分配：大量 JSON、文档解析中间对象、日志拼接和长生命周期缓存可能造成不同 GC 压力。先判断是否存在内存泄漏、无限缓存或异常分配，再考虑收集器参数。若比较 ZGC 等方案，须明确 JDK 版本和延迟目标，不能混用不同版本的实现与默认值。

<a id="alibaba-taotian-ai-app-20261020-942091198347345920-q09"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L2497)，来源许可：GPL-3.0。

<a id="k6e4b1dfe5f8b"></a>

## 垃圾回收

垃圾回收题要从对象分配和存活判断讲到具体收集器。吞吐量、停顿时间和内存占用之间存在取舍，选择收集器时还要考虑 JDK 版本、堆大小和业务对延迟的要求，不能只比较算法名称。

相关内容：[JVM 垃圾回收详解](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/jvm/jvm-garbage-collection.md)

常见面试题：

- 新生代和老年代通常怎样划分？对象一般怎样分配和晋升？
- 大对象和长期存活对象会怎样进入老年代？
- 什么是空间分配担保？
- 引用计数法为什么难以解决对象之间的循环引用？
- 可达性分析怎样判断对象是否存活？哪些对象可以作为 GC Roots？
- 强引用、软引用、弱引用和虚引用有什么区别？
- 标记-清除、复制和标记-整理算法各有什么优缺点？
- 分代收集为什么要为新生代和老年代选择不同算法？
- Minor GC、Major GC 和 Full GC 有什么区别？为什么要结合收集器和日志理解这些名称？
- Serial、Parallel、CMS、G1 和 ZGC 的目标和适用场景有什么不同？
- CMS 为什么会产生内存碎片和浮动垃圾？
- G1 怎样通过 Region、回收价值预测和 Mixed GC 控制停顿？
- ZGC 怎样降低长时间停顿？低停顿收集器会付出哪些代价？
- 哪些情况可能触发 Full GC？频繁 Full GC 应该从哪些数据开始查？

GC 日志中的事件名称、内存分区和参数会随 JDK 与收集器变化。面试中可以先说明自己的运行环境，再解释一次回收的触发原因、回收范围、停顿阶段和结果；脱离版本背固定结论，很容易在追问时互相矛盾。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/jvm/jvm-interview-questions.md#L84)，来源许可：Apache-2.0。

<a id="kbee80467528f"></a>

## 复习 JVM 时先抓住哪些问题？

| 模块           | 需要讲清楚的内容                                  | 常见追问方向                                           |
| -------------- | ------------------------------------------------- | ------------------------------------------------------ |
| 内存与对象     | 运行时数据区怎样划分，对象怎样创建、存放和访问    | 堆、栈、方法区、直接内存、对象头、TLAB、OOM            |
| 类文件与类加载 | `.class` 文件如何进入 JVM，类在什么时机完成初始化 | 常量池、加载过程、类加载器、双亲委派、类隔离           |
| 垃圾回收       | 怎样判断对象存活，内存如何回收，停顿从哪里产生    | GC Roots、引用类型、收集算法、CMS、G1、ZGC、Full GC    |
| 参数与工具     | 参数如何跟着 JDK、收集器和运行现象选择            | `-Xms`、`-Xmx`、GC 日志、Heap Dump、jstat、jstack、JFR |
| 线上排查       | 收到告警后怎样保留证据、缩小范围并验证修复        | CPU、Load、OOM、内存泄漏、频繁 GC、线程阻塞            |

大多数对象实例分配在堆中，活跃线程、静态字段等位置可能持有到对象的引用；GC 从 GC Roots 出发判断对象是否可达，再由具体收集器完成回收。应用出现内存上涨或停顿时，还要结合 GC 日志、线程栈、堆转储和系统指标判断原因，不能看到 Full GC 就直接改堆大小。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/jvm/jvm-interview-questions.md#L21)，来源许可：Apache-2.0。

<a id="kd2b6a18488d3"></a>

## 如何避免内存泄漏的发生？

1. 在使用完 `ThreadLocal` 后，务必调用 `remove()` 方法。 这是最安全和最推荐的做法。 `remove()` 方法会从 `ThreadLocalMap` 中显式地移除对应的 entry，彻底解决内存泄漏的风险。 即使将 `ThreadLocal` 定义为 `static final`，也强烈建议在每次使用后调用 `remove()`。
2. 在线程池等线程复用的场景下，使用 `try-finally` 块可以确保即使发生异常，`remove()` 方法也一定会被执行。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/concurrent/java-concurrent-questions-03.md#L158)，来源许可：Apache-2.0。

<a id="kf228487ebe70"></a>

## 按准备时间安排复习

| 剩余时间 | 建议安排                                                                                                                                     | 复习目标                                          |
| -------- | -------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| 1～2 天  | 先过一遍 [JVM 常见面试题总结](https://interview.javaguide.cn/java/java-jvm.html)，优先补内存区域、对象创建、类加载、对象存活判断和主流收集器 | 能回答基础高频题，知道不同结论对应的 JDK 与收集器 |
| 3～7 天  | 补 JVM 参数、GC 日志和 JDK 诊断工具，分别口述一次 CPU 飙高、OOM 与频繁 Full GC 的排查过程                                                    | 能从告警现象选择指标和工具，并说明操作风险        |
| 1 周以上 | 阅读全部 JVM 专题文章，在本地或测试环境分析一次 GC 日志、线程转储或 Heap Dump；结合项目记录实际 JDK、收集器、堆配置和运行指标                | 能把原理、配置、运行现象和验证方法连起来          |

社招和中高级岗位往往会继续追问参数依据与排查证据。没有实际处理过线上 JVM 故障，可以按测试环境观察和专题资料回答，说明自己会先采集什么、怎样缩小范围；不要把学习案例说成亲历的生产事故。

<!-- @include: @article-footer.snippet.md -->

### 补充说明

| 剩余时间 | 建议安排                                                                                                                                                 | 复习目标                           |
| -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| 1～2 天  | 先过一遍[消息队列常见面试题总结](https://interview.javaguide.cn/high-performance/message-queue-interview-questions.html)，优先补可靠性、幂等、顺序和积压 | 能沿消息生命周期回答高频问题       |
| 3～7 天  | 在通用问题之外，重点学习项目实际使用的一种 MQ，再补另外两种产品的定位和主要差异                                                                          | 能回答产品原理、异常处理和选型追问 |
| 1 周以上 | 按本文顺序阅读专题文章，画出生产、存储、复制、消费、确认和补偿链路，并结合项目整理监控与故障恢复过程                                                     | 能从业务要求讲到配置、取舍和运维   |

| 剩余时间 | 建议安排                                                                | 复习目标                                           |
| -------- | ----------------------------------------------------------------------- | -------------------------------------------------- |
| 1～2 天  | 先过本文所有问题，优先补 SQL/索引、读写分离、分库分表和消息可靠性       | 能回答高频问题，并说出每种方案的主要限制           |
| 3～7 天  | 补 CDN、负载均衡、深度分页、冷热分离及一种主流 MQ，再画一条完整请求链路 | 能从瓶颈推导方案，遇到一致性和异常场景可以继续回答 |
| 1 周以上 | 阅读全部专题文章，结合项目整理一次性能问题的发现、定位、优化和验证过程  | 能用真实指标说明选型、收益、代价和后续监控方式     |

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/jvm/jvm-interview-questions.md#L157)，来源许可：Apache-2.0。
- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/high-performance/message-queue/message-queue-interview-questions.md#L160)，来源许可：Apache-2.0。
- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/high-performance/high-performance-system-interview-questions.md#L134)，来源许可：Apache-2.0。

<a id="k5ec0428e1fd5"></a>

## 虚拟机栈和本地方法栈为什么是私有的？

- **虚拟机栈：** 每个 Java 方法在执行之前会创建一个栈帧用于存储局部变量表、操作数栈、常量池引用等信息。从方法调用直至执行完成的过程，就对应着一个栈帧在 Java 虚拟机栈中入栈和出栈的过程。
- **本地方法栈：** 和虚拟机栈所发挥的作用非常相似，区别是：**虚拟机栈为虚拟机执行 Java 方法（也就是字节码）服务，而本地方法栈则为虚拟机使用到的 Native 方法服务。** 在 HotSpot 虚拟机中和 Java 虚拟机栈合二为一。

所以，为了**保证线程中的局部变量不被别的线程访问到**，虚拟机栈和本地方法栈是线程私有的。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/concurrent/java-concurrent-questions-01.md#L108)，来源许可：Apache-2.0。
