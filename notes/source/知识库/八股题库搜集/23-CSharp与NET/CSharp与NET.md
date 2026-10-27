# CSharp与NET

<a id="me5ac8a8b83cd"></a>

## NET托管执行、CLR与JIT

常见问法：托管代码是什么意思；C#代码怎样变成机器指令。

.NET 的托管执行由运行时参与代码加载、类型系统、内存管理和异常等服务。常见路径先把源代码编译为中间表示与元数据，再由运行时按需编译成机器代码；预先编译等部署方式会改变具体阶段，不能把一种 JIT 流程说成所有 .NET 程序的唯一方式。

托管不等于永远没有底层资源或原生调用。与非托管代码交互仍需处理数据布局、调用约定、寿命和资源释放。面试中先区分语言、运行时和框架：C# 是语言，CLR 等执行系统提供运行时能力，库与应用框架建立在这些能力之上。

参考资料：[StefanTheCode/dotnet_interview_questions：What is .NET?](https://github.com/StefanTheCode/dotnet_interview_questions/blob/8283459bca159be9b72fca50d7fa03021d5c1f7c/Interview%20Questions/README.md#L98)；[规范或原始文档校核](https://learn.microsoft.com/en-us/dotnet/standard/managed-code)。

<a id="m8c78bfe19906"></a>

## CSharp值类型、引用类型与装箱

常见问法：值类型一定在栈上吗；装箱为什么可能带来额外成本。

值类型变量包含该类型的值，引用类型变量包含对对象的引用；默认赋值复制变量的值，因此值类型通常复制内容，引用类型则复制引用。值类型也可以包含引用字段，复制结构体并不自动深拷贝这些字段指向的全部对象。

存放在栈还是堆取决于包含关系和实现等因素，不能用“值类型都在栈、引用类型都在堆”定义类型语义。装箱把值放入可通过对象或相应接口引用的包装形式，可能带来分配与复制；泛型集合可在许多场景避免不必要的装箱。

参考资料：[StefanTheCode/dotnet_interview_questions：What are Value Types and Reference Types in C#?](https://github.com/StefanTheCode/dotnet_interview_questions/blob/8283459bca159be9b72fca50d7fa03021d5c1f7c/Interview%20Questions/README.md#L134)；[规范或原始文档校核](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/value-types)。

<a id="m1bed973bea77"></a>

## NET垃圾回收与确定性资源释放

常见问法：GC为什么不能代替Dispose；using和终结器有什么区别。

GC 管理不再可达的托管对象存储，回收时机不由一次变量离开作用域直接决定。文件、套接字和其他外部资源却可能需要及时释放，因此可用 IDisposable 与 using 等明确消费协议组织清理；异步释放另有 IAsyncDisposable 等机制。

终结器不适合承担精确的业务释放时机，存在调度与执行条件限制。Dispose 也不等于手动把对象内存立即交还系统，而是执行类型定义的释放动作。所有权清楚时，应由拥有资源的层负责释放，借用方不能随意提前关闭其他代码仍在使用的资源。

参考资料：[StefanTheCode/dotnet_interview_questions：How Garbage Collection Works:](https://github.com/StefanTheCode/dotnet_interview_questions/blob/8283459bca159be9b72fca50d7fa03021d5c1f7c/Interview%20Questions/README.md#L1049)；[规范或原始文档校核](https://learn.microsoft.com/en-us/dotnet/api/system.idisposable)。

<a id="m344daa10268b"></a>

## CSharp的async、await与Task

常见问法：await是否一定创建新线程；同步等待异步任务为什么有风险。

Task 表达正在进行或已经完成的操作；async/await 让编译器组织异步状态推进，使代码按接近顺序的形式编写。遇到尚未完成的 await 时，方法可以挂起并在完成后继续，这不等于每个 await 都创建一个新线程。

I/O 异步主要减少等待期间占用线程，CPU 密集工作仍需要实际执行资源。同步阻塞等待异步结果可能造成线程池压力，或与特定同步上下文形成死锁；取消也需要底层操作配合。接口设计应明确任务的完成、异常和取消路径，而不是把所有函数机械加上 async。

参考资料：[StefanTheCode/dotnet_interview_questions：What is async/await and how does it work?](https://github.com/StefanTheCode/dotnet_interview_questions/blob/8283459bca159be9b72fca50d7fa03021d5c1f7c/Interview%20Questions/README.md#L568)；[规范或原始文档校核](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/)。

<a id="m19a77ddfe03f"></a>

## LINQ的延迟执行与查询边界

常见问法：定义LINQ查询时就执行了吗；IEnumerable和IQueryable有什么区别。

许多 LINQ 操作在枚举时才执行，因此创建查询并不总意味着立即读取和计算全部数据。重复枚举可能重复执行工作，也可能观察到已经变化的数据；转成列表等物化操作可以固定一次结果，但会带来内存和时机上的取舍。

IEnumerable 常表达在本地对象序列上枚举，IQueryable 可以把表达式交给提供程序翻译与执行。能否翻译、何时远程访问和哪些操作回到本地，取决于查询提供程序，不能仅看 C# 代码相似就认为数据库执行代价相同。

参考资料：[StefanTheCode/dotnet_interview_questions：Describe what LINQ is and give an example of where it might be used.](https://github.com/StefanTheCode/dotnet_interview_questions/blob/8283459bca159be9b72fca50d7fa03021d5c1f7c/Interview%20Questions/README.md#L363)；[规范或原始文档校核](https://learn.microsoft.com/en-us/dotnet/standard/linq/deferred-execution-lazy-evaluation)。

<a id="m0df98eaa35c5"></a>

## CSharp委托、事件与订阅寿命

常见问法：委托和事件有什么区别；事件订阅为什么可能保留对象。

委托以类型安全的方式表示可调用的方法引用，事件在发布订阅关系上增加访问约束，使外部代码通常只能订阅或退订，而不能随意替发布者触发事件。它们适合将通知与具体处理者解耦。

发布者持有订阅者相关引用时，可能让本应结束的订阅者继续保持可达，尤其发布者寿命更长时。订阅管理应随对象生命周期解除，或选择适合的弱引用机制。把回调挂上去之后忘记它的引用关系，即使有 GC，也可能形成业务意义上的内存保留。

参考资料：[StefanTheCode/dotnet_interview_questions：What are delegates and how are they used in C#?](https://github.com/StefanTheCode/dotnet_interview_questions/blob/8283459bca159be9b72fca50d7fa03021d5c1f7c/Interview%20Questions/README.md#L319)；[规范或原始文档校核](https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/delegates/)。
