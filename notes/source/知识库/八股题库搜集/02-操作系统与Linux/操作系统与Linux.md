# 操作系统与Linux

<a id="m747201b0bc89"></a>

## 进程、线程与协程的边界

常见问法：进程和线程有什么区别；协程为什么切换成本较低。

进程主要提供资源与地址空间的组织和隔离，线程提供可独立调度的执行现场。同一进程的线程通常共享虚拟地址空间和打开的资源，但各有寄存器现场、栈和线程本地状态。线程栈在用途上属于各线程，并不表示其他同进程线程在硬件上绝对不能通过指针访问它。

协程把执行暂停与恢复交给语言运行时或用户态库，可以降低频繁切换的开销并组织大量等待任务；它不自动等于多核并行。协程是否分布在多个系统线程上、阻塞调用是否阻塞调度线程，都取决于运行时。选择时先看隔离需求、任务并行度与 I/O 等待，而不只比较创建速度。

参考资料：[wolverinn/Waking-Up：进程与线程的区别？](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Operating%20Systems.md#L29)；[Snailclimb/JavaGuide：进程和线程的区别是什么？](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/operating-system/operating-system-basic-questions-01.md#L172)。

<a id="m0bb21ea5849d"></a>

## 用户态、内核态与系统调用

常见问法：用户态和内核态有什么区别；系统调用为什么有开销。

用户态限制普通程序直接执行敏感操作，内核态允许操作系统管理页表、设备和全局资源。系统调用是程序请求内核服务的受控入口：参数经过检查后，由内核完成相关操作，再把结果返回用户态。切换涉及保存恢复现场与权限边界，系统调用本身也可能等待资源。

中断通常来自外部设备，异常由当前指令执行触发；缺页是同步异常，不能简单叫作外设中断。进入内核不必然切换到另一个进程，进程切换也不是每一次系统调用都会发生。性能分析应区分权限切换、调度切换以及实际执行的工作。

参考资料：[wolverinn/Waking-Up：什么是用户态和内核态？](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Operating%20Systems.md#L419)；[Snailclimb/JavaGuide：什么是用户态和内核态？](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/operating-system/operating-system-basic-questions-01.md#L92)。

<a id="m95ac982a5fb2"></a>

## 上下文切换与调度

常见问法：进程切换需要保存什么；线程切换一定比进程切换快吗。

上下文切换要保存当前执行现场并恢复另一执行现场，例如寄存器、程序计数器和栈位置。切换进程还可能改变地址空间相关状态，使缓存与地址翻译的工作集受到影响；同进程线程通常减少这部分成本，但仍存在调度、缓存和同步开销。

调度策略在响应时间、吞吐、公平性与截止期限之间取舍。短任务偏好、时间片轮转和优先级调度具有不同目标；高优先级任务也可能受锁持有者影响。不能仅用“切换次数多”证明性能差，需同时观察任务是否在有效工作、是否频繁等待及缓存命中情况。

参考资料：[wolverinn/Waking-Up：进程调度策略有哪些？](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Operating%20Systems.md#L235)；[Snailclimb/JavaGuide：什么是上下文切换？](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/operating-system/operating-system-basic-questions-01.md#L303)。

<a id="ma74c49055805"></a>

## fork、exec与wait的分工

常见问法：fork和exec有什么区别；子进程退出为什么需要wait。

fork 创建子进程，子进程获得独立的进程身份和地址空间视图，Linux 通常用写时复制减少立即复制全部内存的成本。exec 用一个新程序映像替换当前进程的程序内容，成功后不返回原调用位置，因此它本身不是再创建一个新进程。

父进程用 wait 系列取得子进程退出状态并回收残留的内核记账信息。fork 后的文件描述符可能引用相同的打开文件描述，因此偏移等状态也可能共享。多线程进程 fork 后，子进程只保留调用线程；继承的用户态锁可能处于不一致状态，成功 exec 前须遵守相应的异步信号安全限制。

参考资料：[Snailclimb/JavaGuide：fork、exec、wait 分别做什么？](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/operating-system/operating-system-basic-questions-01.md#L291)；[规范或原始文档校核](https://man7.org/linux/man-pages/man2/fork.2.html)。

<a id="mf8a05d1352dc"></a>

## 进程间通信的选择

常见问法：Linux有哪些IPC方式；共享内存为何仍需要同步。

管道适合有明确生产消费关系的字节流，消息队列强调消息边界，Socket 可用于本机或跨主机通信；共享内存让多个进程映射同一片物理内存，减少通过内核反复搬运大量数据的需要。信号通常用于事件通知，不能替代通用的大数据传输通道。

共享内存只解决“看见同一份存储”，不保证复合操作原子，也不规定记录何时完整可读。还需进程共享的互斥量、信号量或正确的原子协议，处理生命周期、异常退出和权限。选择应比较数据量、消息边界、通信拓扑和恢复要求，而不是只背一种方式最快。

参考资料：[wolverinn/Waking-Up：进程间通信有哪些方式？](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Operating%20Systems.md#L63)；[forthespada/InterviewGuide：Linux下进程间通信方式？](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/02-01-os.md#L342)。

<a id="m2ecda1343be5"></a>

## 互斥锁、信号量与条件变量

常见问法：互斥锁和信号量有什么区别；条件变量为什么要在循环中等待。

互斥锁保护共享状态的临界区，强调互斥所有权；信号量用计数表达可用资源或事件数量。条件变量用于等待某个由共享状态表达的条件，不是用来保存业务条件本身。等待操作需要与互斥锁配合，原子地释放锁并进入等待，醒来后再重新持有锁检查条件。

条件变量通常在循环中检查谓词，因为可能发生虚假唤醒，也可能有其他线程先消费了状态。通知本身不等于条件仍然成立。临界区短且竞争可控时自旋可能有价值，等待较长或线程可能被抢占时，持续忙等会浪费 CPU；锁类型选择需要结合调度与任务规模。

| 工具 | 主要表达 | 配套约束 |
| --- | --- | --- |
| 互斥锁 | 同一时刻谁可进入临界区 | 保护共享状态不变量，遵守解锁责任 |
| 信号量 | 可用资源或事件的计数 | 明确每次增减代表什么 |
| 条件变量 | 等待共享状态达到某条件 | 与互斥锁、谓词循环配合 |


参考资料：[wolverinn/Waking-Up：同步与互斥的概念？](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Operating%20Systems.md#L205)。

<a id="m9001ac2a0db0"></a>

## 死锁条件、预防与避免

常见问法：死锁的四个必要条件是什么；如何预防死锁和定位死锁。

经典资源死锁要求互斥、占有并等待、不可抢占和循环等待同时存在。固定全局加锁顺序可以破坏循环等待，一次申请所需资源可以减少占有并等待；但这些策略可能增加等待、降低并发或浪费资源，并非没有代价。

预防从结构上破坏必要条件，避免则根据未来需求和当前分配判断是否仍处于安全状态；银行家算法属于后者。实际排障要获取线程栈与锁依赖，确认谁持有哪些锁、又在等谁。超时能帮助失败退出与恢复，但如果超时后状态和资源没有正确清理，不能认为就解决了死锁或一致性问题。

参考资料：[wolverinn/Waking-Up：死锁产生的必要条件？](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Operating%20Systems.md#L452)；[Snailclimb/JavaGuide：如何检测死锁？](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/concurrent/java-concurrent-questions-01.md#L327)。

<a id="m960ff9294554"></a>

## 虚拟内存与地址空间

常见问法：虚拟内存的作用是什么；虚拟内存等于交换空间吗。

虚拟内存为进程提供地址空间，由硬件地址翻译与操作系统映射管理把虚拟页关联到物理页或其他后备对象。它支持隔离、按需分配、共享映射和统一地址布局，并不只是“拿磁盘扩大内存”。某个虚拟地址可被保留却尚无物理页，也可能根本没有合法映射。

访问内存时先受地址映射和权限约束，应用看到的连续虚拟区间不要求物理页连续。交换空间是部分系统把匿名页移出的后备机制，既不是虚拟内存的全部，也不能消除物理内存、提交资源和性能上的限制。

参考资料：[wolverinn/Waking-Up：什么是虚拟内存？](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Operating%20Systems.md#L569)；[forthespada/InterviewGuide：虚拟内存的目的是什么？](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/02-01-os.md#L973)。

<a id="m1431d3ec83a7"></a>

## 页表、多级页表与TLB

常见问法：虚拟地址如何转换为物理地址；TLB未命中和缺页有什么区别。

分页把地址划成虚拟页号和页内偏移。页表记录映射和权限，硬件或相关软件机制查得物理页框后，保留页内偏移组成物理地址。多级页表按需建立部分层级，避免为稀疏地址空间一次分配完整线性表。

TLB 缓存近期地址翻译，命中可减少页表遍历。TLB 未命中只表示缓存没有该翻译，页表仍可能有有效映射；缺页异常则表示当前访问无法直接完成，例如页未驻留或权限需要内核处理。页表更新还涉及翻译缓存一致性，因此修改映射也有跨核同步成本。

参考资料：[Snailclimb/JavaGuide：页表有什么用？地址翻译过程是怎样的？](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/operating-system/operating-system-basic-questions-02.md#L212)。

<a id="mb0898fcb8f82"></a>

## 缺页异常与按需分配

常见问法：缺页异常是否一定出错；主缺页和次缺页有什么区别。

缺页异常是访存指令触发的同步异常。内核先检查地址所属的合法映射和访问权限：可以通过分配页、调入文件页或处理写时复制修复时，更新映射后重试指令；非法访问则通常以信号等方式交给进程处理。

主缺页需要从存储设备读取页面，次缺页不需要这种读取，二者性能影响不同。越界访问也不保证立即崩溃：如果越界位置仍落在可访问页面中，硬件未必知道语言层面的对象边界，程序可能先破坏数据。用缺页统计定位性能问题时，应同时观察 I/O、工作集和内存压力。

参考资料：[Snailclimb/JavaGuide：什么是缺页异常（Page Fault）？](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/operating-system/operating-system-basic-questions-02.md#L286)。

<a id="m3144cd43df9a"></a>

## 写时复制与共享页

常见问法：写时复制怎样减少fork成本；fork后父子进程如何修改内存。

写时复制先让多个地址空间共享原有页面，并把相应写入路径置于受控状态。某一方第一次写入时触发异常，内核在需要时复制页面，更新该方映射，使修改与其他地址空间隔离。因此“fork 把内存完整复制一遍”和“fork 后永远共享修改”都不准确。

复制粒度通常是页，少量写入也可能引发整页复制；如果子进程很快 exec，很多原页就无需复制。COW 仍有页表、引用计数、异常和实际复制成本。共享内存映射的修改可见性由映射类型决定，不能把匿名私有映射的 COW 结论套到所有共享映射。

参考资料：[Snailclimb/JavaGuide：mmap、COW 和共享内存有什么关系？](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/operating-system/operating-system-basic-questions-02.md#L368)；[规范或原始文档校核](https://man7.org/linux/man-pages/man2/fork.2.html)。

<a id="m54890cf58ff9"></a>

## mmap与共享映射的持久化

常见问法：mmap比read少了什么；修改mmap内容什么时候落盘。

mmap 把文件或其他对象映射到进程虚拟地址区间，应用以普通内存访问操作映射内容，缺页和页缓存由内核参与管理。它可以避免某些反复 read 与用户缓冲区复制，也方便随机访问与进程共享，但会引入缺页、映射管理和并发访问约束。

MAP_SHARED 与 MAP_PRIVATE 对修改传播的语义不同：私有映射的写时复制通常不会改写原文件；共享映射的脏页回写又不等于每次赋值立即持久化。需要崩溃后数据保证时，应使用适合的同步与持久化协议，并考虑文件截断、映射长度和错误处理。

参考资料：[Snailclimb/JavaGuide：mmap、COW 和共享内存有什么关系？](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/operating-system/operating-system-basic-questions-02.md#L368)；[规范或原始文档校核](https://man7.org/linux/man-pages/man2/mmap.2.html)。

<a id="m7bb21637698a"></a>

## 页缓存、缓冲I/O与写回

常见问法：为什么重复读文件会变快；write返回后数据一定落盘了吗。

页缓存保存文件数据的内存副本，让重复读与相邻读减少存储访问。普通缓冲写通常先把数据复制到内核缓存并标记为脏页，随后再回写存储。因此 write 成功通常表示数据被系统接受，不应直接等同于已经经受住断电或系统崩溃。

需要持久化时要理解文件系统与设备的保证，并按需求使用同步接口；写数据和持久化目录项是不同事项。缓存占用也不应全部解释成应用内存泄漏：一部分缓存可在压力下回收，但脏页、固定页和活跃工作集具有不同回收条件。

参考资料：[规范或原始文档校核](https://man7.org/linux/man-pages/man2/fsync.2.html)。

<a id="m0856754a27e7"></a>

## 页面置换、局部性与抖动

常见问法：LRU和FIFO有什么区别；为什么内存不足时会抖动。

页面置换在内存压力下选择可回收的页面。FIFO 只看进入顺序，可能淘汰仍频繁使用的页；LRU 利用最近访问反映局部性，精确实现成本较高，实际系统常使用近似或更复杂的冷热识别策略。理论最优算法依赖未来访问，只能作为比较基准。

当活跃工作集超过可用内存，刚被换出的页很快又要读回，系统会在缺页和 I/O 上消耗大量时间，这就是抖动。改策略不一定能解决容量不足，还应减少并发工作集、修正访问模式或增加资源。缓存算法与系统页回收有关联，但不能把应用 LRU 链表实现当成现代内核全部行为。

参考资料：[Snailclimb/JavaGuide：FIFO 页面置换算法性能为何不好？](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/operating-system/operating-system-basic-questions-02.md#L326)；[wolverinn/Waking-Up：有哪些页面置换算法？](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Operating%20Systems.md#L583)。

<a id="mc0bb120f860c"></a>

## 文件描述符、打开文件描述与inode

常见问法：文件描述符和inode有什么区别；dup和fork为什么可能共享文件偏移。

文件描述符是进程用于引用打开资源的整数句柄；它通常指向内核的打开文件描述，后者保存文件偏移与状态标志等；inode 则保存文件对象的元数据和数据映射信息。目录把名称关联到文件对象，文件名通常不直接保存在 inode 中。

dup 或 fork 得到的描述符可能指向同一个打开文件描述，所以共享文件偏移；独立 open 同一文件则通常产生不同的打开状态。close 释放一个引用，并不必然马上销毁文件内容。回答时分清“名称”“文件对象”“一次打开状态”和“进程句柄”，许多共享与释放问题就能直接推导。

参考资料：[wolverinn/Waking-Up：什么是文件描述符？](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Operating%20Systems.md#L392)；[Snailclimb/JavaGuide：文件、目录、inode、dentry 有什么关系？](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/operating-system/operating-system-basic-questions-02.md#L526)。

<a id="md4de8298285b"></a>

## 硬链接、软链接与删除语义

常见问法：硬链接和软链接有什么区别；删除正在打开的文件会怎样。

硬链接是同一文件系统中指向同一文件对象的另一个目录项，多个名字共享内容和 inode；符号链接保存一个路径，路径解析时再寻找目标，因此可以跨文件系统，也可能成为悬空链接。

unlink 删除的是名称关联，文件对象何时真正释放还取决于链接计数与打开引用。程序仍持有已删除文件的描述符时，可能继续读写该文件，空间也未必立刻回收。这是日志已删除但磁盘占用没有下降的常见分析方向；清理前应确认哪个进程仍引用该文件，而不是重复执行路径删除。

参考资料：[Snailclimb/JavaGuide：硬链接和软链接有什么区别？](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/operating-system/operating-system-basic-questions-02.md#L574)。

<a id="mec1d8c2bba7a"></a>

## 阻塞、非阻塞与同步异步I/O

常见问法：非阻塞I/O等于异步I/O吗；同步I/O为什么也可以非阻塞。

阻塞与非阻塞主要描述调用在暂时无法完成时如何返回：阻塞调用可能让执行线程等待，非阻塞调用则及时报告当前无法推进。同步与异步主要区分操作完成过程如何组织，异步接口通常把请求提交与完成通知分开。

非阻塞 read 返回 EAGAIN 并不表示数据已经在后台读完，它只是要求调用方稍后再尝试；事件通知又通常表示“现在可能可以进行 I/O”，不是业务消息已经完整。讨论某个 API 时要明确是否就绪通知、完成通知，以及缓冲区在完成前是否允许复用。

参考资料：[规范或原始文档校核](https://man7.org/linux/man-pages/man2/read.2.html)。

<a id="m54e5accb6ad1"></a>

## select、poll与epoll的机制

常见问法：epoll为什么适合大量连接；epoll是不是所有操作都是O1。

select 和 poll 每次传入或描述待检查集合，内核检查就绪状态后，应用还需找出可以处理的对象。epoll 把关注集合保存在内核中，通过控制接口增删兴趣项，再取得就绪事件，减少在大量空闲连接上反复传递与扫描集合的工作。

epoll 的优势与连接数量、活跃比例、事件模式和程序组织有关，不能笼统保证所有操作 O(1) 或任何场景都更快。就绪不保证后续操作不会遇到变化，实际服务常配合非阻塞 I/O。它也不是把同步业务代码自动变成异步模型，事件循环仍需避免耗时任务阻塞整个处理链。

参考资料：[wolverinn/Waking-Up：select/poll/epoll三者的区别？](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Operating%20Systems.md#L372)；[Snailclimb/JavaGuide：select/poll/epoll三者的区别？](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/operating-system/operating-system-basic-questions-02.md#L463)；[规范或原始文档校核](https://man7.org/linux/man-pages/man7/epoll.7.html)。

<a id="m1c35b540210e"></a>

## epoll水平触发与边缘触发

常见问法：LT和ET有什么区别；ET为什么通常要读到EAGAIN。

水平触发在就绪条件仍满足时可以继续通知；边缘触发重点通知状态变化。如果采用 ET，收到事件后只处理少量数据就返回，缓冲中仍有未处理内容而没有新变化时，可能长期得不到新的通知。因此常用非阻塞模式持续处理，直到返回 EAGAIN，或采用经过正确设计的重新通知策略。

事件循环还应考虑公平性：一个连接持续繁忙，不能无限占用处理线程。LT 相对容易正确实现，ET 可以减少某些重复通知，但复杂度更高；选型应结合吞吐、调度与代码正确性，而不把 ET 视为天然更高级。

参考资料：[wolverinn/Waking-Up：什么是水平触发？什么是边缘触发？](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Operating%20Systems.md#L399)；[规范或原始文档校核](https://man7.org/linux/man-pages/man7/epoll.7.html)。

<a id="mac854631fbc7"></a>

## 零拷贝与sendfile的边界

常见问法：零拷贝到底减少什么拷贝；mmap和sendfile有什么区别。

零拷贝通常指避免数据在用户缓冲区和内核缓冲区之间的部分重复搬运，或减少 CPU 参与的数据复制，并不保证整个路径完全没有复制。sendfile 让内核在文件与输出描述符之间传输，适合文件发送；mmap 则建立可由应用访问的映射，二者接口与目标不同。

收益取决于文件系统、设备、内核支持及应用是否需要修改或加密内容。使用相关接口仍须处理短传输、错误和输出背压，并保持被发送的数据在必要期间有效。若应用必须逐字节变换正文，不能只靠换一个系统调用就保留全部原有零拷贝收益。

参考资料：[Snailclimb/JavaGuide：什么是零拷贝？](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/operating-system/operating-system-basic-questions-02.md#L479)；[规范或原始文档校核](https://man7.org/linux/man-pages/man2/sendfile.2.html)。

<a id="m7fb8bd3d3205"></a>

## CPU、Load与内存排障的观察顺序

常见问法：CPU低而Load高说明什么；内存增长怎样区分泄漏和缓存。

CPU 使用率描述处理器忙于哪些工作的比例；Linux 的 load average 反映一段时间内可运行任务及部分不可中断等待任务的平均数量，二者不等价。CPU 不高而 Load 高时，要检查任务状态、存储等待和资源阻塞，而不能只增加工作线程。

内存分析应区分虚拟地址大小、驻留物理页、共享页、页缓存与进程实际保留对象。先确认资源限制和增长趋势，再定位到进程、线程或分配位置，最后用堆、映射、调用栈或性能事件验证假设。单张 top 截图或一次 RSS 数值不足以证明泄漏，容器的限制与宿主机总量也应分开看。

参考资料：[Snailclimb/JavaGuide：load average 和 CPU 使用率有什么区别？](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/operating-system/operating-system-basic-questions-01.md#L357)。

<a id="mbb08ee7d8155"></a>

## 僵尸、孤儿与进程回收

常见问法：僵尸进程如何产生；孤儿进程和僵尸进程有什么区别。

子进程已经结束执行，但父进程尚未读取退出状态时，内核保留少量退出记账信息，形成僵尸进程；它不再正常执行代码，因此重复发送终止信号无法像杀运行进程一样清理它。父进程正确调用 wait 系列才是回收路径。

孤儿进程是原父进程先退出而子进程还存在，之后被适当的收养者接管，可能继续运行，也可能随后退出。不能把“父进程退出”直接说成“子进程一定变成僵尸”。服务应设计子进程管理与异常退出处理，长期大量僵尸通常反映回收逻辑缺失。

参考资料：[wolverinn/Waking-Up：什么是僵尸进程？](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Operating%20Systems.md#L305)；[forthespada/InterviewGuide：如何避免僵尸进程？](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/02-02-os.md#L402)。

<a id="m1921c47395c6"></a>

## 信号处理与异步信号安全

常见问法：为什么信号处理函数里不能随便printf；信号和普通回调有什么区别。

信号处理函数可能打断线程正在执行的普通代码，再在该上下文中运行。如果处理函数再次调用被打断代码正在使用的非重入库函数或获取同一把锁，就可能破坏内部状态或死锁，因此不能把它当成普通业务回调。

通常让处理函数只执行规定安全的最小操作，例如设置合适的标志或通过安全通道通知正常执行流，再由普通代码完成日志、释放和业务逻辑。volatile sig_atomic_t 的特定用途也不能推广为一般多线程原子变量；线程同步仍应遵循相应语言与系统的内存模型。

参考资料：[规范或原始文档校核](https://man7.org/linux/man-pages/man7/signal-safety.7.html)。

## 专题阅读

- [Linux命令与排障](Linux%E5%91%BD%E4%BB%A4%E4%B8%8E%E6%8E%92%E9%9A%9C.md)
- [内存管理](%E5%86%85%E5%AD%98%E7%AE%A1%E7%90%86.md)
- [文件系统与I-O](%E6%96%87%E4%BB%B6%E7%B3%BB%E7%BB%9F%E4%B8%8EI-O.md)
- [系统机制与实践](%E7%B3%BB%E7%BB%9F%E6%9C%BA%E5%88%B6%E4%B8%8E%E5%AE%9E%E8%B7%B5.md)
- [进程、线程与同步（1）](%E8%BF%9B%E7%A8%8B%E3%80%81%E7%BA%BF%E7%A8%8B%E4%B8%8E%E5%90%8C%E6%AD%A5-01.md)
- [进程、线程与同步（2）](%E8%BF%9B%E7%A8%8B%E3%80%81%E7%BA%BF%E7%A8%8B%E4%B8%8E%E5%90%8C%E6%AD%A5-02.md)
- [进程、线程与同步（3）](%E8%BF%9B%E7%A8%8B%E3%80%81%E7%BA%BF%E7%A8%8B%E4%B8%8E%E5%90%8C%E6%AD%A5-03.md)
