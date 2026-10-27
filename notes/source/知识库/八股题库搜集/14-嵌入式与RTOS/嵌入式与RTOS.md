# 嵌入式与RTOS

<a id="m7a25e824b9bc"></a>

## 嵌入式volatile与同步边界

常见问法：寄存器为什么常用volatile；volatile能保证中断共享变量原子吗。

volatile 让编译器按相应的可观察访问规则处理对象，常用于内存映射寄存器或会被常规控制流之外改变的状态。它不自动提供读改写原子性、线程间同步或任意硬件访存顺序，具体设备访问还依赖体系结构、内存属性与屏障规则。

例如主程序和中断都修改一个计数器，即使变量声明 volatile，读取、增加和写回仍可能被交错打断。应根据处理器支持使用适当的临界区、原子操作或单写者协议，同时限制关中断时间。不能把“编译器每次都读内存”当成并发正确性的完整证明。

参考资料：[Amir7698/embedded-interview-prep：Volatile遗漏与共享访问错误案例](https://github.com/Amir7698/embedded-interview-prep/blob/c01be80b93c9c3401e01a3321d23a5634af61dac/13_Interview_QA/02_bug_hunt_collection.md#L9)。

<a id="m9e49204f117d"></a>

## 中断服务程序与延后处理

常见问法：ISR中为什么不应做长时间工作；中断怎样通知任务处理数据。

中断服务程序优先完成必须及时进行的硬件确认、状态采集和最小搬运，再把较耗时工作交给任务或其他延后执行机制。这样缩短高优先级上下文占用，减少其他中断与任务的响应延迟。

ISR 不应随意调用可能阻塞、分配不确定或非重入的接口。与 RTOS 交互时必须使用允许在对应中断上下文调用的接口，并遵循端口和优先级限制。若用环形缓冲区传递数据，要说明读写者、索引可见性、满空判断与溢出策略；“中断里置一个标志”也可能丢掉多次发生的事件。

参考资料：[Sering-Hong/embedded-interview：STM32 的中断优先级如何工作？](https://github.com/Sering-Hong/embedded-interview/blob/6d08312bbbd86d28e792c49664450a251f972786/stm32/peripherals.md#L3)；[Amir7698/embedded-interview-prep：Why can't you give a mutex from ISR?](https://github.com/Amir7698/embedded-interview-prep/blob/c01be80b93c9c3401e01a3321d23a5634af61dac/13_Interview_QA/answers/01_rapid_fire_100_answers.md#L268)。

<a id="m4ebff61cc255"></a>

## 中断优先级与RTOS临界区

常见问法：抢占优先级和子优先级有什么区别；高优先级中断能否调用内核API。

以常见 Cortex-M/NVIC 场景为例，抢占优先级决定能否打断正在执行的中断，子优先级参与同时待处理事件的选择。具体有效位数、分组与数值编码必须查处理器和芯片配置；常见的“数值越小优先级越高”也应放在该体系结构语境中。

FreeRTOS 某些端口用优先级阈值保护内核临界区，高于该阈值的中断不能随意调用内核接口，否则可能在内核状态暂不一致时进入。不能把示例中的 0—4、5—15 等数值当成所有芯片统一配置；移植时要核对优先级位数、配置宏和使用的 FromISR 接口。

参考资料：[规范或原始文档校核](https://www.freertos.org/media/2018/161204_Mastering_the_FreeRTOS_Real_Time_Kernel-A_Hands-On_Tutorial_Guide.pdf)。

<a id="m27a3e7c4d074"></a>

## DMA、双缓冲与缓存一致性

常见问法：DMA是否完全不需要CPU参与；DMA收到的数据为什么CPU看到旧值。

DMA 让控制器在存储和外设之间搬运数据，减少 CPU 逐字节执行搬运的工作，但 CPU 仍需配置、管理缓冲与处理完成或错误。双缓冲允许设备处理一块区域时，软件处理另一块区域，前提是交换时机与所有权明确。

具备数据缓存的处理器上，CPU 与 DMA 可能看到不同的副本；需要根据内存区域与平台规则维护缓存、屏障和对齐，或采用合适的不可缓存区域。还要确认 DMA 能访问的总线和内存范围。不能把“声明 volatile”当成通用缓存一致性解决方案，也不能在 DMA 尚未完成时复用其缓冲区。

参考资料：[Sering-Hong/embedded-interview：DMA 的工作原理？](https://github.com/Sering-Hong/embedded-interview/blob/6d08312bbbd86d28e792c49664450a251f972786/stm32/peripherals.md#L19)。

<a id="m9b45ea29f2a6"></a>

## RTOS任务状态与实时性

常见问法：RTOS有哪些任务状态；实时系统是不是执行速度越快越好。

任务可处于运行、就绪、阻塞或显式挂起等状态。就绪表示具备运行条件但尚未得到执行资源，阻塞表示等待事件或超时条件；挂起与带超时的事件等待不同，恢复条件由相应接口决定。

实时性的目标是满足可预期的时间约束，而不只是平均速度快。任务优先级、最坏执行时间、中断占用和共享资源等待都影响响应。单核系统某一瞬间只能执行一个任务，多核或 SMP 配置则不能照搬这一限制。周期任务还应区分相对延时与按固定时间基准等待，避免处理时间累积成周期漂移。

参考资料：[Sering-Hong/embedded-interview：FreeRTOS 的任务状态有哪些？](https://github.com/Sering-Hong/embedded-interview/blob/6d08312bbbd86d28e792c49664450a251f972786/freertos/basics.md#L3)；[规范或原始文档校核](https://www.freertos.org/media/2018/161204_Mastering_the_FreeRTOS_Real_Time_Kernel-A_Hands-On_Tutorial_Guide.pdf)。

<a id="me62e9c00f0ce"></a>

## 优先级反转与优先级继承

常见问法：高优先级任务为何等低优先级任务；优先级继承能否解决全部死锁。

高优先级任务等待低优先级任务持有的锁，而中优先级任务持续抢占低优先级任务，会放大高优先级任务的等待时间，这就是典型的无界优先级反转。优先级继承让锁持有者暂时获得相关等待者的较高优先级，尽快完成临界区并释放锁。

继承不是消除全部资源问题的万能机制：锁嵌套、链式等待和具体内核实现限制仍需分析，它也不自动解决循环等待死锁。应缩短临界区、明确锁顺序并限制资源占用；用于互斥的内核对象与纯事件信号量具有不同语义，不能随意替换。

参考资料：[Sering-Hong/embedded-interview：什么是优先级反转？如何解决？](https://github.com/Sering-Hong/embedded-interview/blob/6d08312bbbd86d28e792c49664450a251f972786/freertos/basics.md#L37)；[规范或原始文档校核](https://www.freertos.org/media/2018/161204_Mastering_the_FreeRTOS_Real_Time_Kernel-A_Hands-On_Tutorial_Guide.pdf)。

<a id="m64509c593c81"></a>

## 队列、信号量与任务通知

常见问法：队列和信号量怎样选择；队列发送一个指针是否复制整个对象。

队列传递固定配置大小的队列项，信号量表达事件或资源数量，任务通知可用于更轻量的定向通知与状态传递。选择取决于是否需要携带数据、保留多少次事件、是否需要多个等待者及具体内核能力。

FreeRTOS 队列通常按队列项复制字节；若项本身是指针，复制的是指针值，不是自动深拷贝其指向的全部对象。发送者和接收者必须约定对象所有权与有效期，不能把指向临时栈数据的地址交出后立即离开作用域。队列满、发送超时和通知合并时是否丢事件，也必须由业务协议定义。

参考资料：[规范或原始文档校核](https://www.freertos.org/media/2018/161204_Mastering_the_FreeRTOS_Real_Time_Kernel-A_Hands-On_Tutorial_Guide.pdf)。

<a id="m036aa594ee80"></a>

## 任务栈、动态内存与碎片

常见问法：任务栈一定从堆里分配吗；嵌入式系统为什么谨慎使用malloc。

每个任务需要相应的执行栈，但栈内存可以由动态创建路径分配，也可以由静态创建方式提供，不能统一说“任务栈都来自内核堆”。容量要覆盖最坏调用深度、局部数组、上下文保存和中断使用方式，并结合平台实际栈组织分析。

动态分配带来失败、执行时延和碎片化等约束；固定大小内存池可提高可预测性，但也会增加容量规划与浪费取舍。栈水位只能说明已观测负载，不能证明所有异常路径都不会溢出。任务长期不结束或忘记释放消息对象，垃圾收集不存在时尤其需要明确生命周期责任。

参考资料：[Sering-Hong/embedded-interview：嵌入式中什么时候用 malloc？](https://github.com/Sering-Hong/embedded-interview/blob/6d08312bbbd86d28e792c49664450a251f972786/c-language/memory.md#L77)；[Amir7698/embedded-interview-prep：Why avoid malloc in embedded production?](https://github.com/Amir7698/embedded-interview-prep/blob/c01be80b93c9c3401e01a3321d23a5634af61dac/13_Interview_QA/answers/01_rapid_fire_100_answers.md#L47)。

<a id="m7ae46d2fc75b"></a>

## UART、SPI与I2C的接口取舍

常见问法：UART和SPI以及I2C有什么区别；通信协议为什么还需要帧格式和校验。

UART 通常以异步串行字节通信，双方约定波特率和帧参数；SPI 使用时钟与片选等信号，常用于短距离高吞吐外设；I2C 以地址组织共享总线，并具有相应的应答与仲裁机制。实际速率、线数与拓扑限制应查具体标准和器件能力。

硬件接口能传递字节，并不自动提供完整业务消息。应用协议仍需长度或分隔、命令、校验、超时和重同步规则；CRC 可以发现特定错误，但不提供身份认证或防恶意篡改。调试先核对电气层、电平与时序，再看帧边界和业务语义。

参考资料：[Sering-Hong/embedded-interview：UART、I2C、SPI 对比](https://github.com/Sering-Hong/embedded-interview/blob/6d08312bbbd86d28e792c49664450a251f972786/communication/protocols.md#L3)。

<a id="mef8e04ece7ab"></a>

## 看门狗与系统恢复

常见问法：看门狗为什么不能只在定时器里喂；独立和窗口看门狗各约束什么。

看门狗在系统未按约定进度反馈时触发恢复，用于从部分死锁或失控状态中退出。独立时钟源可减少主时钟故障带来的影响；窗口式机制还约束过早或过晚的反馈，具体行为取决于硬件。

如果无论业务是否正常都由定时中断无条件喂狗，主任务已经卡死也可能被掩盖。更合理的设计是汇总关键任务的进度与健康状态，再决定是否喂狗。恢复还应记录故障原因并保证关键数据和输出安全，避免设备在同一错误上无限重启却无法诊断。

参考资料：[Sering-Hong/embedded-interview：看门狗的作用？](https://github.com/Sering-Hong/embedded-interview/blob/6d08312bbbd86d28e792c49664450a251f972786/stm32/peripherals.md#L53)。

<a id="md156766e0643"></a>

## PID、离散实现与抗积分饱和

常见问法：PID三项分别解决什么问题；增量式PID是否天然不会积分饱和。

比例项根据当前误差响应，积分项积累误差以改善符合条件下的稳态偏差，微分项根据变化趋势提供阻尼但对噪声敏感。离散实现要把采样周期纳入参数与状态更新，不能忽略时间单位直接照抄连续公式。

执行器输出达到限幅后，控制器内部积分仍可能继续积累，使恢复时间很长。条件积分、积分限幅或回算等抗饱和策略应与执行器约束共同设计；增量式写法本身不能保证天然消除积分饱和。位置式与增量式描述输出计算形式，不应被当成独立于状态和限幅的正确性保证。

参考资料：[Sering-Hong/embedded-interview：什么是积分饱和？如何解决？](https://github.com/Sering-Hong/embedded-interview/blob/6d08312bbbd86d28e792c49664450a251f972786/pid/theory.md#L34)；[规范或原始文档校核](https://www.mathworks.com/help/simulink/slref/anti-windup-control-using-a-pid-controller.html)。

<a id="m42a1dbb028a6"></a>

## Bootloader、OTA与断电恢复

常见问法：OTA升级怎样避免变砖；为什么校验固件仍不等于可信升级。

Bootloader 负责在启动时选择并验证可执行固件，再完成必要的硬件与运行状态交接。可靠 OTA 通常把下载、校验、标记待启动、试运行和确认成功分成明确阶段，使任一步骤断电后仍能找到可恢复状态。

A/B 分区或保留恢复镜像可以降低更新中途失败的风险，但需设计元数据原子更新、版本与回滚策略。校验和只能检测某些传输或存储错误，可信升级还需真实性验证与密钥管理。跳转前还要按平台要求处理向量表、栈、外设和中断状态，不能只把函数指针改到新地址。

参考资料：[Amir7698/embedded-interview-prep：Bootloader架构、OTA与安全问题](https://github.com/Amir7698/embedded-interview-prep/blob/c01be80b93c9c3401e01a3321d23a5634af61dac/12_System_Design/01_bootloader_design.md#L3)。

## 专题阅读

- [嵌入式实践](%E5%B5%8C%E5%85%A5%E5%BC%8F%E5%AE%9E%E8%B7%B5.md)
