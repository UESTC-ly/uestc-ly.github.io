# Go

<a id="md14576660487"></a>

## 数组、slice与底层存储共享

常见问法：数组和切片有什么区别；append为什么可能影响另一切片。

数组的长度属于其类型，赋值会复制数组值；slice 是对底层数组一段元素的视图，具有长度与容量，复制 slice 不会自动复制全部元素。两个 slice 可能共享底层数组，因此经一个视图修改元素，另一个视图也可能观察到变化。

append 在容量足够时可以复用原数组，容量不足时取得新的底层存储；应使用返回的 slice，不能依赖固定扩容倍率。需要隔离修改时应显式复制元素，或合理限制切片容量。长度控制可索引的范围，容量描述从起点还能扩展的范围，二者不可混用。

参考资料：[golang-design/go-questions：数组与切片有什么异同](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/slice/1-%E6%95%B0%E7%BB%84%E5%92%8C%E5%88%87%E7%89%87%E6%9C%89%E4%BB%80%E4%B9%88%E5%BC%82%E5%90%8C.md#L3)；[规范或原始文档校核](https://go.dev/ref/spec#Slice_types)。

<a id="m69079e2b3fb0"></a>

## map的语义、遍历与并发访问

常见问法：map为什么不能直接并发读写；map遍历顺序是否稳定。

map 根据可比较的键保存映射，查找可以用额外的布尔结果区分“键不存在”与“值恰好为零值”。nil map 可以读取，但不能直接写入。遍历顺序没有稳定顺序保证，业务需要排序时应先收集键或记录再排序。

普通 map 不提供任意并发读写的同步保证，需用锁、所有权划分或适用的并发容器组织访问。运行时可能检测并报错，也可能表现为其他不正确行为，不能把“没有触发报错”当成线程安全证据。具体哈希表布局与增长实现会随 Go 版本演进，不应把某版源码结构当成语言规范。

参考资料：[golang-design/go-questions：什么是 map](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/map/1-map%E7%9A%84%E5%BA%95%E5%B1%82%E5%AE%9E%E7%8E%B0%E5%8E%9F%E7%90%86%E6%98%AF%E4%BB%80%E4%B9%88.md#L7)；[规范或原始文档校核](https://go.dev/ref/spec#Map_types)。

<a id="m5d10b7167bfe"></a>

## interface与typednil

常见问法：interface为什么可能不等于nil；返回nil错误为什么仍进入错误分支。

接口值包含动态类型与相关动态值的信息。只有接口本身没有动态类型和动态值时，才是 nil 接口；把一个值为 nil 的具体指针放入接口后，动态类型仍然存在，因此该接口通常不等于 nil。

这常见于 error 返回路径：若用具体指针类型的变量保存 nil，再把它作为 error 返回，调用方收到的可能是非 nil 接口。应明确返回真正的 nil 接口，或保证具体错误对象确实存在。比较接口值时，还要考虑其动态值是否可比较，不能认为所有接口都能无条件比较。

参考资料：[规范或原始文档校核](https://go.dev/ref/spec#Interface_types)。

<a id="m41e1ba3860ca"></a>

## goroutine与GMP调度模型

常见问法：goroutine和线程有什么区别；GMP分别代表什么。

goroutine 是 Go 运行时调度的执行单元，可以以较低的创建和栈管理成本组织并发。常见运行时实现用 G 表示 goroutine、M 表示操作系统线程、P 表示执行 Go 代码所需的调度资源；可运行任务在这些资源之间分配，但这不是语言规范要求的固定数据布局。

并发数量多不等于 CPU 并行度无限提高。GOMAXPROCS 约束同时执行相应 Go 代码的运行时资源规模，阻塞调用、系统调用和调度抢占还会影响线程使用。性能排查应观察任务是否在运行、等待锁、等待网络或被外部调用阻塞，而不是仅统计 goroutine 总数。

参考资料：[golang-design/go-questions：goroutine 调度时机有哪些](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/sched/3-goroutine%20%E8%B0%83%E5%BA%A6%E6%97%B6%E6%9C%BA%E6%9C%89%E5%93%AA%E4%BA%9B.md#L3)。

<a id="m99020f52b1fb"></a>

## channel、关闭与select

常见问法：读写nil或关闭channel会怎样；如何安全结束生产消费。

channel 用于传递值与协调执行，缓冲通道可以保存有限数量尚未被接收的元素。nil channel 上的发送和接收会等待；关闭后可继续取出已缓冲值，之后接收得到元素零值与 ok=false；向已关闭通道发送会 panic，重复关闭或关闭 nil 通道也不合法。

关闭表达“不会再有新值”，应由能确定发送已结束的一方负责，而不是让每个接收者自行关闭。select 在多个可推进分支间选择，不提供任意业务优先级保证；将某个通道变量设为 nil 可暂时禁用该分支。要同时设计结束、错误和背压，避免仅靠缓冲增大来掩盖处理速度不足。

参考资料：[golang-design/go-questions：channel 有哪些应用](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/channel/12-channel%20%E6%9C%89%E5%93%AA%E4%BA%9B%E5%BA%94%E7%94%A8.md#L3)；[规范或原始文档校核](https://go.dev/ref/spec#Channel_types)。

<a id="m220153fb2a91"></a>

## context取消与goroutine泄漏

常见问法：context取消会杀死goroutine吗；如何避免goroutine一直阻塞。

context 传播取消信号、截止时间和请求范围的信息，取消本身不会强制杀死 goroutine。任务必须在等待或工作边界检查 Done、使用支持 context 的接口，并在退出时释放它拥有的资源，才能形成完整的取消链路。

泄漏常来自永远等不到的通道收发、未设置边界的网络调用、停止条件缺失或任务生命周期脱离请求。应明确谁创建、谁等待结束、谁通知取消；需要时用 select 把通信与退出信号结合。把所有数据都塞进 context 值也不合适，它不应代替明确参数或普通依赖关系。

参考资料：[golang-design/go-questions：context 是什么](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/stdlib/context/1-context%20%E6%98%AF%E4%BB%80%E4%B9%88.md#L3)。

<a id="m93fd9e39db3d"></a>

## defer、panic与recover

常见问法：defer参数何时求值；recover为什么捕获不到其他goroutine的panic。

defer 注册调用，在当前函数返回路径上按后进先出顺序执行；调用参数通常在注册 defer 时已经求值，而闭包中的变量读取可发生在随后执行时。defer 适合把资源清理紧邻成功取得资源的位置，使正常返回和异常路径共享释放逻辑。

panic 会沿当前 goroutine 的调用栈展开相应 defer；recover 需要在同一 goroutine 的适当延迟调用中发挥作用，不能用另一个 goroutine 的恢复器兜住所有任务。恢复以后还需恢复不变量或转换成清楚的错误结果，不能只吞掉 panic 让程序在未知状态下继续。

参考资料：[规范或原始文档校核](https://go.dev/ref/spec#Defer_statements)。

<a id="ma52d2c731d0e"></a>

## 逃逸分析与栈堆分配

常见问法：返回局部变量地址为什么合法；new出来的对象一定在堆上吗。

逃逸分析判断对象的引用是否可能超出当前栈帧等局部生命周期，从而帮助编译器决定存储与优化方式。Go 允许返回局部变量的地址，因为实现会保证返回引用所需的对象寿命，而不是让它指向已经失效的栈存储。

是否写 new、是否取地址，都不能单独决定最终分配位置；编译优化、接口转换、闭包捕获和调用可见性等会影响结果。过度追求“全部在栈上”并非目标，应先观察分配率和 GC 压力，再用编译器分析与性能剖析确定真正热点。实现细节必须与实际 Go 版本对应。

参考资料：[golang-design/go-questions：逃逸分析是怎么进行的](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/compile/1-%E9%80%83%E9%80%B8%E5%88%86%E6%9E%90%E6%98%AF%E6%80%8E%E4%B9%88%E8%BF%9B%E8%A1%8C%E7%9A%84.md#L3)。

<a id="mb523c8912743"></a>

## GC、内存保留与性能权衡

常见问法：Go GC大致怎样工作；为什么对象不用了内存却未立即下降。

垃圾回收追踪仍可达的对象并回收不再需要的存储，降低显式释放的负担，但不能代替资源生命周期设计。常见 Go 实现包含并发标记、写屏障和短暂停顿等机制；具体策略、触发与回收细节应按版本查看运行时资料。

一个小 slice 或引用可能仍然让较大的底层对象保持可达；GC 能管理内存，却不能把仍被引用的内容判为“业务不再需要”。进程 RSS、堆中活对象和已保留给运行时的内存也不同。优化通常从减少不必要的分配与长期引用开始，再依据延迟和内存预算调整，而不是先调 GC 参数。

参考资料：[golang-design/go-questions：如何观察 Go GC？](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/memgc/1-%E5%9E%83%E5%9C%BE%E5%9B%9E%E6%94%B6%E7%9A%84%E8%AE%A4%E8%AF%86.md#L104)。

<a id="m14529c21de12"></a>

## 锁、原子与channel的同步边界

常见问法：channel能够保证哪些可见性；什么时候用锁而不用通道。

Go 内存模型规定特定同步操作之间的先后关系，使普通内存更新能被另一个执行单元可靠观察。channel 通信、互斥锁和原子操作都可用于同步，但各有明确前提，不能只因两个 goroutine 曾访问同一通道就推断任意操作都有顺序。

锁适合保护共享对象的不变量；channel 适合转移数据、组织生命周期或表达通信协议。多个原子字段各自安全，不意味着它们组成的业务状态整体一致。对共享 map、缓存或队列，先明确所有者和临界区，再决定使用通信还是共享内存同步。

参考资料：[规范或原始文档校核](https://go.dev/ref/mem)。

<a id="md01a4f158a47"></a>

## 竞态检测与性能剖析

常见问法：race detector和pprof分别解决什么问题；为什么测试没报竞态仍可能有问题。

竞态检测用于发现运行过程中被覆盖到的非同步并发访问，性能剖析用于定位 CPU、内存、阻塞等成本分布，两者回答不同问题。一次执行没有报告只说明该次路径没有被检测出问题，不能证明所有可能交错都正确。

排查时应复现有代表性的负载，先定位资源异常，再沿热点栈与对象引用验证原因。大量 goroutine 未必是泄漏，热点函数耗时也可能是调用次数过多而非单次实现慢；需要结合时间、分配率、等待关系和生命周期作判断。

性能采样的具体用法可对照 [Go 官方 pprof 介绍](https://go.dev/blog/pprof)；先明确采样类型，再解释热点的业务含义。

参考资料：[规范或原始文档校核](https://go.dev/doc/articles/race_detector)。

## 专题阅读

- [Go语言问答](Go%E8%AF%AD%E8%A8%80%E9%97%AE%E7%AD%94.md)
- [内存、GC与性能](%E5%86%85%E5%AD%98%E3%80%81GC%E4%B8%8E%E6%80%A7%E8%83%BD.md)
- [并发、Channel与调度（1）](%E5%B9%B6%E5%8F%91%E3%80%81Channel%E4%B8%8E%E8%B0%83%E5%BA%A6-01.md)
- [并发、Channel与调度（2）](%E5%B9%B6%E5%8F%91%E3%80%81Channel%E4%B8%8E%E8%B0%83%E5%BA%A6-02.md)
- [集合、接口与语言机制](%E9%9B%86%E5%90%88%E3%80%81%E6%8E%A5%E5%8F%A3%E4%B8%8E%E8%AF%AD%E8%A8%80%E6%9C%BA%E5%88%B6.md)
