# 内存、GC与性能

<a id="k0d9fd7770fbd"></a>

## g0 栈何用户栈如何切换

上一讲讲完了 main goroutine 的诞生，它不是第一个，算上 g0，它要算第二个了。不过，我们要考虑的就是这个 goroutine，它会真正执行用户代码。

`g0` 栈用于执行调度器的代码，执行完之后，要跳转到执行用户代码的地方，如何跳转？这中间涉及到栈和寄存器的切换。要知道，函数调用和返回主要靠的也是 CPU 寄存器的切换。`goroutine` 的切换和此类似。

继续看 `proc1` 函数的代码。中间有一段调整运行空间的代码，计算出的结果一般为 0，也就是一般不会调整 SP 的位置，忽略好了。

```golang
// 确定参数入栈位置
spArg := sp
```

参数的入参位置也是从 SP 处开始，通过：

```golang
// 将参数从执行 newproc 函数的栈拷贝到新 g 的栈
memmove(unsafe.Pointer(spArg), unsafe.Pointer(argp), uintptr(narg))
```

将 fn 的参数从 g0 栈上拷贝到 newg 的栈上，memmove 函数需要传入源地址、目的地址、参数大小。由于 main 函数在这里没有参数需要拷贝，因此这里相当于没做什么。

接着，初始化 newg 的各种字段，而且涉及到最重要的 pc，sp 等字段：

```golang
// 把 newg.sched 结构体成员的所有成员设置为 0
memclrNoHeapPointers(unsafe.Pointer(&newg.sched), unsafe.Sizeof(newg.sched))
// 设置 newg 的 sched 成员，调度器需要依靠这些字段才能把 goroutine 调度到 CPU 上运行
newg.sched.sp = sp
newg.stktopsp = sp
// newg.sched.pc 表示当 newg 被调度起来运行时从这个地址开始执行指令
newg.sched.pc = funcPC(goexit) + sys.PCQuantum // +PCQuantum so that previous instruction is in same function
newg.sched.g = guintptr(unsafe.Pointer(newg))
gostartcallfn(&newg.sched, fn)
newg.gopc = callerpc
// 设置 newg 的 startpc 为 fn.fn，该成员主要用于函数调用栈的 traceback 和栈收缩
// newg 真正从哪里开始执行并不依赖于这个成员，而是 sched.pc
newg.startpc = fn.fn
if _g_.m.curg != nil {
	newg.labels = _g_.m.curg.labels
}
```

首先，`memclrNoHeapPointers` 将 newg.sched 的内存全部清零。接着，设置 sched 的 sp 字段，当 goroutine 被调度到 m 上运行时，需要通过 sp 字段来指示栈顶的位置，这里设置的就是新栈的栈顶位置。

最关键的一行来了：

```golang
// newg.sched.pc 表示当 newg 被调度起来运行时从这个地址开始执行指令
newg.sched.pc = funcPC(goexit) + sys.PCQuantum // +PCQuantum so that previous instruction is in same function
```

设置 `pc` 字段为函数 `goexit` 的地址加 1，也说是 `goexit` 函数的第二条指令，`goexit` 函数是 `goroutine` 退出后的一些清理工作。有点奇怪，这是要干嘛？接着往后看。

```golang
newg.sched.g = guintptr(unsafe.Pointer(newg))
```

设置 `g` 字段为 newg 的地址。插一句，sched 是 g 结构体的一个字段，它本身也是一个结构体，保存调度信息。复习一下：

接下来的这个函数非常重要，可以解释之前为什么要那样设置 `pc` 字段的值。调用 `gostartcallfn`：

```golang
gostartcallfn(&newg.sched, fn) //调整sched成员和newg的栈
```

传入 newg.sched 和 fn。

```golang
func gostartcallfn(gobuf *gobuf, fv *funcval) {
	var fn unsafe.Pointer
	if fv != nil {
		// fn: gorotine 的入口地址，初始化时对应的是 runtime.main
		fn = unsafe.Pointer(fv.fn)
	} else {
		fn = unsafe.Pointer(funcPC(nilfunc))
	}
	gostartcall(gobuf, fn, unsafe.Pointer(fv))
}

func gostartcall(buf *gobuf, fn, ctxt unsafe.Pointer) {
	// newg 的栈顶，目前 newg 栈上只有 fn 函数的参数，sp 指向的是 fn 的第一参数
	sp := buf.sp

	// …………………………

	// 为返回地址预留空间
	sp -= sys.PtrSize
	// 这里填的是 newproc1 函数里设置的 goexit 函数的第二条指令
	// 伪装 fn 是被 goexit 函数调用的，使得 fn 执行完后返回到 goexit 继续执行，从而完成清理工作
	*(*uintptr)(unsafe.Pointer(sp)) = buf.pc
	// 重新设置 buf.sp
	buf.sp = sp
	// 当 goroutine 被调度起来执行时，会从这里的 pc 值开始执行，初始化时就是 runtime.main
	buf.pc = uintptr(fn)
	buf.ctxt = ctxt
}
```

函数 `gostartcallfn` 只是拆解出了包含在 funcval 结构体里的函数指针，转过头就调用 `gostartcall`。将 sp 减小了一个指针的位置，这是给返回地址留空间。果然接着就把 buf.pc 填入了栈顶的位置：

```golang
*(*uintptr)(unsafe.Pointer(sp)) = buf.pc
```

原来 buf.pc 只是做了一个搬运工，搞什么啊。重新设置 buf.sp 为送减掉一个指针位置之后的值，设置 buf.pc 为 fn，指向要执行的函数，这里就是指的 runtime.main 函数。

对嘛，这才是应有的操作。之后，当调度器“光顾”此 goroutine 时，取出 buf.sp 和 buf.pc，恢复 CPU 相应的寄存器，就可以构造出 goroutine 的运行环境。

而 goexit 函数也通过“偷天换日”将自己的地址“强行”放到 newg 的栈顶，达到自己不可告人的目的：每个 goroutine 执行完之后，都要经过我的一些清理工作，才能“放行”。这样一说，goexit 函数还真是无私，默默地做一些“扫尾”的工作。

设置完 newg.sched 这后，我们的图又可以前进一步：

![设置 newg.sched](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/sched/assets/27.png)

上图中，newg 新增了 sched.pc 指向 `runtime.main` 函数，当它被调度起来执行时，就从这里开始；新增了 sched.sp 指向了 newg 栈顶位置，同时，newg 栈顶位置的内容是一个跳转地址，指向 `runtime.goexit` 的第二条指令，当 goroutine 退出时，这条地址会载入 CPU 的 PC 寄存器，跳转到这里执行“扫尾”工作。

之后，将 newg 的状态改为 runnable，设置 goroutine 的 id：

```golang
// 设置 g 的状态为 _Grunnable，可以运行了
casgstatus(newg, _Gdead, _Grunnable)
newg.goid = int64(_p_.goidcache)
```

每个 P 每次会批量（16个）申请 id，每次调用 newproc 函数，新创建一个 goroutine，id 加 1。因此 g0 的 id 是 0，而 main goroutine 的 id 就是 1。

`newg` 的状态变成可执行后（Runnable），就可以将它加入到 P 的本地运行队列里，等待调度。所以，goroutine 何时被执行，用户代码决定不了。来看源码：

```golang
// 将 G 放入 _p_ 的本地待运行队列
runqput(_p_, newg, true)

// runqput 尝试将 g 放到本地可执行队列里。
// 如果 next 为假，runqput 将 g 添加到可运行队列的尾部
// 如果 next 为真，runqput 将 g 添加到 p.runnext 字段
// 如果 run queue 满了，runnext 将 g 放到全局队列里
//
// runnext 成员中的 goroutine 会被优先调度起来运行
func runqput(_p_ *p, gp *g, next bool) {
	// ……………………

	if next {
	retryNext:
		oldnext := _p_.runnext
		if !_p_.runnext.cas(oldnext, guintptr(unsafe.Pointer(gp))) {
			// 有其它线程在操作 runnext 成员，需要重试
			goto retryNext
		}
		// 老的 runnext 为 nil，不用管了
		if oldnext == 0 {
			return
		}
		// 把之前的 runnext 踢到正常的 runq 中
		// 原本存放在 runnext 的 gp 放入 runq 的尾部
		gp = oldnext.ptr()
	}

retry:
	h := atomic.Load(&_p_.runqhead) // load-acquire, synchronize with consumers
	t := _p_.runqtail
	// 如果 P 的本地队列没有满，入队
	if t-h < uint32(len(_p_.runq)) {
		_p_.runq[t%uint32(len(_p_.runq))].set(gp)
		// 原子写入
		atomic.Store(&_p_.runqtail, t+1) // store-release, makes the item available for consumption
		return
	}
	// 可运行队列已经满了，放入全局队列了
	if runqputslow(_p_, gp, h, t) {
		return
	}
	// the queue is not full, now the put above must succeed
	// 没有成功放入全局队列，说明本地队列没满，重试一下
	goto retry
}
```

`runqput` 函数的主要作用就是将新创建的 goroutine 加入到 P 的可运行队列，如果本地队列满了，则加入到全局可运行队列。前两个参数都好理解，最后一个参数 `next` 的作用是，当它为 true 时，会将 newg 加入到 P 的 runnext 字段，具有最高优先级，将先于普通队列中的 goroutine 得到执行。

先将 P 老的 runnext 成员取出，接着用一个原子操作 cas 来试图将 runnext 成员设置成 newg，目的是防止其他线程在同时修改 runnext 字段。

设置成功之后，相当于 newg “挤掉” 了原来老的处于 runnext 的 goroutine，还得给人遣散费，安顿好人家嘛，不然和强盗有何区别？

“安顿”的动作在 retry 代码段中执行。先通过 `head`，`tail`，`len(_p_.runq)` 来判断队列是否已满，如果没满，则直接写到队列尾部，同时修改队列尾部的指针。

```golang
// store-release, makes it available for consumption
atomic.Store(&_p_.runqtail, t+1)
```

这里使用原子操作写入 runtail，防止编译器和 CPU 指令重排，保证上一行代码对 runq 的修改发生在修改 runqtail 之前，并且保证当前线程对队列的修改对其它线程立即可见。

如果本地队列满了，那就只能试图将 newg 添加到全局可运行队列中了。调用 `runqputslow(_p_, gp, h, t)` 完成。

```golang
// 将 g 和 _p_ 本地队列的一半 goroutine 放入全局队列。
// 因为要获取锁，所以会慢
func runqputslow(_p_ *p, gp *g, h, t uint32) bool {
	var batch [len(_p_.runq)/2 + 1]*g

	// First, grab a batch from local queue.
	n := t - h
	n = n / 2
	if n != uint32(len(_p_.runq)/2) {
		throw("runqputslow: queue is not full")
	}
	for i := uint32(0); i < n; i++ {
		batch[i] = _p_.runq[(h+i)%uint32(len(_p_.runq))].ptr()
	}
	// 如果 cas 操作失败，说明本地队列不满了，直接返回
	if !atomic.Cas(&_p_.runqhead, h, h+n) { // cas-release, commits consume
		return false
	}
	batch[n] = gp

    // …………………………

	// Link the goroutines.
	// 全局运行队列是一个链表，这里首先把所有需要放入全局运行队列的 g 链接起来，
	// 减小锁粒度，从而降低锁冲突，提升性能
	for i := uint32(0); i < n; i++ {
		batch[i].schedlink.set(batch[i+1])
	}

	// Now put the batch on global queue.
	lock(&sched.lock)
	globrunqputbatch(batch[0], batch[n], int32(n+1))
	unlock(&sched.lock)
	return true
}
```

先将 P 本地队列里所有的 goroutine 加入到一个数组中，数组长度为 `len(_p_.runq)/2 + 1`，也就是 runq 的一半加上 newg。

接着，将从 runq 的头部开始的前一半 goroutine 存入 bacth 数组。然后，使用原子操作尝试修改 P 的队列头，因为出队了一半 goroutine，所以 head 要向后移动 1/2 的长度。如果修改失败，说明 runq 的本地队列被其他线程修改了，因此后面的操作就不进行了，直接返回 false，表示 newg 没被添加进来。

```golang
batch[n] = gp
```

将 newg 本身添加到数组。

通过循环将 batch 数组里的所有 g 串成链表：

```golang
for i := uint32(0); i < n; i++ {
	batch[i].schedlink.set(batch[i+1])
}
```

![批量 goroutine 连接成链表](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/sched/assets/28.png)

最后，将链表添加到全局队列中。由于操作的是全局队列，因此需要获取锁，因为存在竞争，所以代价较高。这也是本地可运行队列存在的原因。调用 `globrunqputbatch(batch[0], batch[n], int32(n+1))`：

```golang
// Put a batch of runnable goroutines on the global runnable queue.
// Sched must be locked.
func globrunqputbatch(ghead *g, gtail *g, n int32) {
	gtail.schedlink = 0
	if sched.runqtail != 0 {
		sched.runqtail.ptr().schedlink.set(ghead)
	} else {
		sched.runqhead.set(ghead)
	}
	sched.runqtail.set(gtail)
	sched.runqsize += n
}
```

如果全局的队列尾 `sched.runqtail` 不为空，则直接将其和前面生成的链表头相接，否则说明全局的可运行列队为空，那就直接将前面生成的链表头设置到 sched.runqhead。

最后，再设置好队列尾，增加 runqsize。

设置完成之后：

![放到全局可运行队列](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/sched/assets/29.png)

再回到 `runqput` 函数，如果将 newg 添加到全局队列失败了，说明本地队列在此过程中发生了变化，又有了位置可以添加 newg，因此重试 retry 代码段。我们也可以发现，P 的本地可运行队列的长度为 256，它是一个循环队列，因此最多只能放下 256 个 goroutine。

因为本文还是处于初始化的场景，所以 newg 被成功放入 p0 的本地可运行队列，等待被调度。

将我们的图再完善一下：

![newg 添加到本地 runq](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/sched/assets/30.png)

**相关解释：** [GPM 是什么](%E5%B9%B6%E5%8F%91%E3%80%81Channel%E4%B8%8E%E8%B0%83%E5%BA%A6-01.md#ke4d69790eafc)

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/sched/9-g0%20%E6%A0%88%E4%BD%95%E7%94%A8%E6%88%B7%E6%A0%88%E5%A6%82%E4%BD%95%E5%88%87%E6%8D%A2.md#L3)，来源许可：GPL-3.0。

<a id="ka64b84b52e4c"></a>

## GC 关注的指标有哪些？

Go 的 GC 被设计为成比例触发、大部分工作与赋值器并发、不分代、无内存移动且会主动向操作系统归还申请的内存。因此最主要关注的、能够影响赋值器的性能指标有：

- CPU 利用率：回收算法会在多大程度上拖慢程序？有时候，这个是通过回收占用的 CPU 时间与其它 CPU 时间的百分比来描述的。
- GC 停顿时间：回收器会造成多长时间的停顿？目前的 GC 中需要考虑 STW 和 Mark Assist 两个部分可能造成的停顿。
- GC 停顿频率：回收器造成的停顿频率是怎样的？目前的 GC 中需要考虑 STW 和 Mark Assist 两个部分可能造成的停顿。
- GC 可扩展性：当堆内存变大时，垃圾回收器的性能如何？但大部分的程序可能并不一定关心这个问题。

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/memgc/3-%E5%9E%83%E5%9C%BE%E5%9B%9E%E6%94%B6%E7%9A%84%E4%BC%98%E5%8C%96%E9%97%AE%E9%A2%98.md#L9)，来源许可：GPL-3.0。

<a id="kb640d7b7faa7"></a>

## Go GC 在演化过程中还存在哪些其他设计？为什么没有被采用？

### 并发栈重扫

正如我们前面所说，允许灰色赋值器存在的垃圾回收器需要引入重扫过程来保证算法的正确性，除了引入混合屏障来消除重扫这一过程外，有另一种做法可以提高重扫过程的性能，那就是将重扫的过程并发执行。然而这一方案[11]并没有得以实现，原因很简单：实现过程相比引入混合屏障而言十分复杂，而且引入混合屏障能够消除重扫这一过程，将简化垃圾回收的步骤。

### ROC

ROC 的全称是面向请求的回收器（Request Oriented Collector）[12]，它其实也是分代 GC 的一种重新叙述。它提出了一个请求假设（Request Hypothesis）：与一个完整请求、休眠 goroutine 所关联的对象比其他对象更容易死亡。这个假设听起来非常符合直觉，但在实现上，由于垃圾回收器必须确保是否有 goroutine 私有指针被写入公共对象，因此写屏障必须一直打开，这也就产生了该方法的致命缺点：昂贵的写屏障及其带来的缓存未命中，这也是这一设计最终没有被采用的主要原因。

### 传统分代 GC

在发现 ROC 性能不行之后，作为备选方案，Go 团队还尝试了实现传统的分代式 GC [13]。但最终同样发现分代假设并不适用于 Go 的运行栈机制，年轻代对象在栈上就已经死亡，扫描本就该回收的执行栈并没有为由于分代假设带来明显的性能提升。这也是这一设计最终没有被采用的主要原因。

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/memgc/4-%E5%8E%86%E5%8F%B2%E5%8F%8A%E6%BC%94%E8%BF%9B.md#L49)，来源许可：GPL-3.0。

<a id="kfde52b918561"></a>

## Go 历史各个版本在 GC 方面的改进？

- Go 1：串行三色标记清扫

- Go 1.3：并行清扫，标记过程需要 STW，停顿时间在约几百毫秒

- Go 1.5：并发标记清扫，停顿时间在一百毫秒以内

- Go 1.6：使用 bitmap 来记录回收内存的位置，大幅优化垃圾回收器自身消耗的内存，停顿时间在十毫秒以内

- Go 1.7：停顿时间控制在两毫秒以内

- Go 1.8：混合写屏障，停顿时间在半个毫秒左右

- Go 1.9：彻底移除了栈的重扫描过程 

- Go 1.12：整合了两个阶段的 Mark Termination，但引入了一个严重的 GC Bug 至今未修（见问题 20），尚无该 Bug 对 GC 性能影响的报告

- Go 1.13：着手解决向操作系统归还内存的，提出了新的 Scavenger

- Go 1.14：替代了仅存活了一个版本的 scavenger，全新的页分配器，优化分配内存过程的速率与现有的扩展性问题，并引入了异步抢占，解决了由于密集循环导致的 STW 时间过长的问题

可以用下图直观地说明 GC 的演进历史：

![](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/memgc/assets/gc1.png)

在 Go 1 刚发布时的版本中，甚至没有将 Mark-Sweep 的过程并行化，当需要进行垃圾回收时，所有的代码都必须进入 STW 的状态。而到了 Go 1.3 时，官方迅速地将清扫过程进行了并行化的处理，即仅在标记阶段进入 STW。

这一想法很自然，因为并行化导致算法结果不一致的情况仅仅发生在标记阶段，而当时的垃圾回收器没有针对并行结果的一致性进行任何优化，因此才需要在标记阶段进入 STW。对于 Scavenger 而言，早期的版本中会有一个单独的线程来定期将多余的内存归还给操作系统。

![](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/memgc/assets/gc2.png)

而到了 Go 1.5 后，Go 团队花费了相当大的力气，通过引入写屏障的机制来保证算法的一致性，才得以将整个 GC 控制在很小的 STW 内，而到了 1.8 时，由于新的混合屏障的出现，消除了对栈本身的重新扫描，STW 的时间进一步缩减。

从这个时候开始，Scavenger 已经从独立线程中移除，并合并至系统监控这个独立的线程中，并周期性地向操作系统归还内存，但仍然会有内存溢出这种比较极端的情况出现，因为程序可能在短时间内应对突发性的内存申请需求时，内存还没来得及归还操作系统，导致堆不断向操作系统申请内存，从而出现内存溢出。

![](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/memgc/assets/gc3.png)

到了 Go 1.13，定期归还操作系统的问题得以解决，Go 团队开始将周期性的 Scavenger 转化为可被调度的 goroutine，并将其与用户代码并发执行。而到了 Go 1.14，这一向操作系统归还内存的操作时间进一步得到缩减。

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/memgc/4-%E5%8E%86%E5%8F%B2%E5%8F%8A%E6%BC%94%E8%BF%9B.md#L9)，来源许可：GPL-3.0。

<a id="kaf383d80e026"></a>

## Go 的 GC 如何调优？

Go 的 GC 被设计为极致简洁，与较为成熟的 Java GC 的数十个可控参数相比，严格意义上来讲，Go 可供用户调整的参数只有 GOGC 环境变量。当我们谈论 GC 调优时，通常是指减少用户代码对 GC 产生的压力，这一方面包含了减少用户代码分配内存的数量（即对程序的代码行为进行调优），另一方面包含了最小化 Go 的 GC 对 CPU 的使用率（即调整 GOGC）。

GC 的调优是在特定场景下产生的，并非所有程序都需要针对 GC 进行调优。只有那些对执行延迟非常敏感、
当 GC 的开销成为程序性能瓶颈的程序，才需要针对 GC 进行性能调优，几乎不存在于实际开发中 99% 的情况。
除此之外，Go 的 GC 也仍然有一定的可改进的空间，也有部分 GC 造成的问题，目前仍属于 Open Problem。

总的来说，我们可以在现在的开发中处理的有以下几种情况：

1. 对停顿敏感：GC 过程中产生的长时间停顿、或由于需要执行 GC 而没有执行用户代码，导致需要立即执行的用户代码执行滞后。
2. 对资源消耗敏感：对于频繁分配内存的应用而言，频繁分配内存增加 GC 的工作量，原本可以充分利用 CPU 的应用不得不频繁地执行垃圾回收，影响用户代码对 CPU 的利用率，进而影响用户代码的执行效率。

从这两点来看，所谓 GC 调优的核心思想也就是充分的围绕上面的两点来展开：优化内存的申请速度，尽可能的少申请内存，复用已申请的内存。或者简单来说，不外乎这三个关键字：**控制、减少、复用**。

我们将通过三个实际例子介绍如何定位 GC 的存在的问题，并一步一步进行性能调优。当然，在实际情况中问题远比这些例子要复杂，这里也只是讨论调优的核心思想，更多的时候也只能具体问题具体分析。

### 例1：合理化内存分配的速度、提高赋值器的 CPU 利用率

我们来看这样一个例子。在这个例子中，`concat` 函数负责拼接一些长度不确定的字符串。并且为了快速完成任务，出于某种原因，在两个嵌套的 for 循环中一口气创建了 800 个 goroutine。在 main 函数中，启动了一个 goroutine 并在程序结束前不断的触发 GC，并尝试输出 GC 的平均执行时间：

```go
package main

import (
	"fmt"
	"os"
	"runtime"
	"runtime/trace"
	"sync/atomic"
	"time"
)

var (
	stop  int32
	count int64
	sum   time.Duration
)

func concat() {
	for n := 0; n < 100; n++ {
		for i := 0; i < 8; i++ {
			go func() {
				s := "Go GC"
				s += " " + "Hello"
				s += " " + "World"
				_ = s
			}()
		}
	}
}

func main() {
	f, _ := os.Create("trace.out")
	defer f.Close()
	trace.Start(f)
	defer trace.Stop()

	go func() {
		var t time.Time
		for atomic.LoadInt32(&stop) == 0 {
			t = time.Now()
			runtime.GC()
			sum += time.Since(t)
			count++
		}
		fmt.Printf("GC spend avg: %v\n", time.Duration(int64(sum)/count))
	}()

	concat()
	atomic.StoreInt32(&stop, 1)
}
```

这个程序的执行结果是：

```bash
$ go build -o main
$ ./main
GC spend avg: 2.583421ms
```

GC 平均执行一次需要长达 2ms 的时间，我们再进一步观察 trace 的结果：

![](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/memgc/assets/gc-tuning-ex1-1.png)

程序的整个执行过程中仅执行了一次 GC，而且仅 Sweep STW 就耗费了超过 1 ms，非常反常。甚至查看赋值器 mutator 的 CPU 利用率，在整个 trace 尺度下连 40% 都不到：

![](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/memgc/assets/gc-tuning-ex1-2.png)

主要原因是什么呢？我们不妨查看 goroutine 的分析：

![](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/memgc/assets/gc-tuning-ex1-3.png)

在这个榜单中我们不难发现，goroutine 的执行时间占其生命周期总时间非常短的一部分，但大部分时间都花费在调度器的等待上了（蓝色的部分），说明同时创建大量 goroutine 对调度器产生的压力确实不小，我们不妨将这一产生速率减慢，一批一批地创建 goroutine：

```go
func concat() {
	wg := sync.WaitGroup{}
	for n := 0; n < 100; n++ {
		wg.Add(8)
		for i := 0; i < 8; i++ {
			go func() {
				s := "Go GC"
				s += " " + "Hello"
				s += " " + "World"
				_ = s
				wg.Done()
			}()
		}
		wg.Wait()
	}
}
```

这时候我们再来看：

```bash
$ go build -o main
$ ./main
GC spend avg: 328.54µs
```

GC 的平均时间就降到 300 微秒了。这时的赋值器 CPU 使用率也提高到了 60%，相对来说就很可观了：

![](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/memgc/assets/gc-tuning-ex1-4.png)

当然，这个程序仍然有优化空间，例如我们其实没有必要等待很多 goroutine 同时执行完毕才去执行下一组 goroutine。而可以当一个 goroutine 执行完毕时，直接启动一个新的 goroutine，也就是 goroutine 池的使用。
有兴趣的读者可以沿着这个思路进一步优化这个程序中赋值器对 CPU 的使用率。

### 例2：降低并复用已经申请的内存

我们通过一个非常简单的 Web 程序来说明复用内存的重要性。在这个程序中，每当产生一个 `/example2`
的请求时，都会创建一段内存，并用于进行一些后续的工作。

```go
package main

import (
	"fmt"
	"net/http"
	_ "net/http/pprof"
)

func newBuf() []byte {
	return make([]byte, 10<<20)
}

func main() {
	go func() {
		http.ListenAndServe("localhost:6060", nil)
	}()

	http.HandleFunc("/example2", func(w http.ResponseWriter, r *http.Request) {
		b := newBuf()

		// 模拟执行一些工作
		for idx := range b {
			b[idx] = 1
		}

		fmt.Fprintf(w, "done, %v", r.URL.Path[1:])
	})
	http.ListenAndServe(":8080", nil)
}
```

为了进行性能分析，我们还额外创建了一个监听 6060 端口的 goroutine，用于使用 pprof 进行分析。
我们先让服务器跑起来：

```bash
$ go build -o main
$ ./main
```

我们这次使用 pprof 的 trace 来查看 GC 在此服务器中面对大量请求时候的状态，要使用 trace 可以通过访问 `/debug/pprof/trace` 路由来进行，其中 `seconds` 参数设置为 20s，并将 trace 的结果保存为 `trace.out`:

```bash
$ wget http://127.0.0.1:6060/debug/pprof/trace\?seconds\=20 -O trace.out
--2020-01-01 22:13:34--  http://127.0.0.1:6060/debug/pprof/trace?seconds=20
Connecting to 127.0.0.1:6060... connected.
HTTP request sent, awaiting response...
```

这时候我们使用一个压测工具 `ab`，来同时产生 500 个请求
（`-n` 一共 500 个请求，`-c` 一个时刻执行请求的数量，每次 100 个并发请求）：

```bash
$ ab -n 500 -c 100 http://127.0.0.1:8080/example2
This is ApacheBench, Version 2.3 <$Revision: 1843412 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient)
Completed 100 requests
Completed 200 requests
Completed 300 requests
Completed 400 requests
Completed 500 requests
Finished 500 requests


Server Software:        
Server Hostname:        127.0.0.1
Server Port:            8080

Document Path:          /example2
Document Length:        14 bytes

Concurrency Level:      100
Time taken for tests:   0.987 seconds
Complete requests:      500
Failed requests:        0
Total transferred:      65500 bytes
HTML transferred:       7000 bytes
Requests per second:    506.63 [#/sec] (mean)
Time per request:       197.382 [ms] (mean)
Time per request:       1.974 [ms] (mean, across all concurrent requests)
Transfer rate:          64.81 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    1   1.1      0       7
Processing:    13  179  77.5    170     456
Waiting:       10  168  78.8    162     455
Total:         14  180  77.3    171     458

Percentage of the requests served within a certain time (ms)
  50%    171
  66%    203
  75%    222
  80%    239
  90%    281
  95%    335
  98%    365
  99%    400
 100%    458 (longest request)
```

![](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/memgc/assets/gc-tuning-ex2-1.png)

GC 反复被触发，一个显而易见的原因就是内存分配过多。我们可以通过 `go tool pprof` 来查看究竟是谁分配了大量内存（使用 web 指令来使用浏览器打开统计信息的可视化图形）：

```bash
$ go tool pprof http://127.0.0.1:6060/debug/pprof/heap
Fetching profile over HTTP from http://localhost:6060/debug/pprof/heap
Saved profile in /Users/changkun/pprof/pprof.alloc_objects.alloc_space.inuse_o
bjects.inuse_space.003.pb.gz
Type: inuse_space
Time: Jan 1, 2020 at 11:15pm (CET)
Entering interactive mode (type "help" for commands, "o" for options)
(pprof) web
(pprof) 
```

![](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/memgc/assets/gc-tuning-ex2-2.png)

可见 `newBuf` 产生的申请的内存过多，现在我们使用 sync.Pool 来复用 `newBuf` 所产生的对象：

```go
package main

import (
	"fmt"
	"net/http"
	_ "net/http/pprof"
	"sync"
)

// 使用 sync.Pool 复用需要的 buf
var bufPool = sync.Pool{
	New: func() interface{} {
		return make([]byte, 10<<20)
	},
}

func main() {
	go func() {
		http.ListenAndServe("localhost:6060", nil)
	}()
	http.HandleFunc("/example2", func(w http.ResponseWriter, r *http.Request) {
		b := bufPool.Get().([]byte)
		for idx := range b {
			b[idx] = 0
		}
		fmt.Fprintf(w, "done, %v", r.URL.Path[1:])
		bufPool.Put(b)
	})
	http.ListenAndServe(":8080", nil)
}
```

其中 ab 输出的统计结果为：

```bash
$ ab -n 500 -c 100 http://127.0.0.1:8080/example2
This is ApacheBench, Version 2.3 <$Revision: 1843412 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient)
Completed 100 requests
Completed 200 requests
Completed 300 requests
Completed 400 requests
Completed 500 requests
Finished 500 requests


Server Software:        
Server Hostname:        127.0.0.1
Server Port:            8080

Document Path:          /example2
Document Length:        14 bytes

Concurrency Level:      100
Time taken for tests:   0.427 seconds
Complete requests:      500
Failed requests:        0
Total transferred:      65500 bytes
HTML transferred:       7000 bytes
Requests per second:    1171.32 [#/sec] (mean)
Time per request:       85.374 [ms] (mean)
Time per request:       0.854 [ms] (mean, across all concurrent requests)
Transfer rate:          149.85 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    1   1.4      1       9
Processing:     5   75  48.2     66     211
Waiting:        5   72  46.8     63     207
Total:          5   77  48.2     67     211

Percentage of the requests served within a certain time (ms)
  50%     67
  66%     89
  75%    107
  80%    122
  90%    148
  95%    167
  98%    196
  99%    204
 100%    211 (longest request)
```

但从 `Requests per second` 每秒请求数来看，从原来的 506.63 变为 1171.32 得到了近乎一倍的提升。从 trace 的结果来看，GC 也没有频繁的被触发从而长期消耗 CPU 使用率：

![](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/memgc/assets/gc-tuning-ex2-3.png)

sync.Pool 是内存复用的一个最为显著的例子，从语言层面上还有很多类似的例子，例如在例 1 中，`concat` 函数可以预先分配一定长度的缓存，而后再通过 append 的方式将字符串存储到缓存中：

```go
func concat() {
	wg := sync.WaitGroup{}
	for n := 0; n < 100; n++ {
		wg.Add(8)
		for i := 0; i < 8; i++ {
			go func() {
				s := make([]byte, 0, 20)
				s = append(s, "Go GC"...)
				s = append(s, ' ')
				s = append(s, "Hello"...)
				s = append(s, ' ')
				s = append(s, "World"...)
				_ = string(s)
				wg.Done()
			}()
		}
		wg.Wait()
	}
}
```

原因在于 `+` 运算符会随着字符串长度的增加而申请更多的内存，并将内容从原来的内存位置拷贝到新的内存位置，造成大量不必要的内存分配，先提前分配好足够的内存，再慢慢地填充，也是一种减少内存分配、复用内存形式的一种表现。

### 例3：调整 GOGC

我们已经知道了 GC 的触发原则是由步调算法来控制的，其关键在于估计下一次需要触发 GC 时，堆的大小。可想而知，如果我们在遇到海量请求的时，为了避免 GC 频繁触发，是否可以通过将 GOGC 的值设置得更大，让 GC 触发的时间变得更晚，从而减少其触发频率，进而增加用户代码对机器的使用率呢？答案是肯定的。

我们可以非常简单粗暴的将 GOGC 调整为 1000，来执行上一个例子中未复用对象之前的程序：

```bash
$ GOGC=1000 ./main
```

这时我们再重新执行压测：

```bash
$ ab -n 500 -c 100 http://127.0.0.1:8080/example2
This is ApacheBench, Version 2.3 <$Revision: 1843412 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient)
Completed 100 requests
Completed 200 requests
Completed 300 requests
Completed 400 requests
Completed 500 requests
Finished 500 requests


Server Software:        
Server Hostname:        127.0.0.1
Server Port:            8080

Document Path:          /example2
Document Length:        14 bytes

Concurrency Level:      100
Time taken for tests:   0.923 seconds
Complete requests:      500
Failed requests:        0
Total transferred:      65500 bytes
HTML transferred:       7000 bytes
Requests per second:    541.61 [#/sec] (mean)
Time per request:       184.636 [ms] (mean)
Time per request:       1.846 [ms] (mean, across all concurrent requests)
Transfer rate:          69.29 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    1   1.8      0      20
Processing:     9  171 210.4     66     859
Waiting:        5  158 199.6     62     813
Total:          9  173 210.6     68     860

Percentage of the requests served within a certain time (ms)
  50%     68
  66%    133
  75%    198
  80%    292
  90%    566
  95%    696
  98%    723
  99%    743
 100%    860 (longest request)
```

可以看到，压测的结果得到了一定幅度的改善（`Requests per second` 从原来的 506.63 提高为了 541.61），
并且 GC 的执行频率明显降低：

![](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/memgc/assets/gc-tuning-ex3.png)

在实际实践中可表现为需要紧急处理一些由 GC 带来的瓶颈时，人为将 GOGC 调大，加钱加内存，扛过这一段峰值流量时期。

当然，这种做法其实是治标不治本，并没有从根本上解决内存分配过于频繁的问题，极端情况下，反而会由于 GOGC 太大而导致回收不及时而耗费更多的时间来清理产生的垃圾，这对时间不算敏感的应用还好，但对实时性要求较高的程序来说就是致命的打击了。

因此这时更妥当的做法仍然是，定位问题的所在，并从代码层面上进行优化。

### 小结

通过上面的三个例子我们可以看到在 GC 调优过程中 `go tool pprof` 和 `go tool trace` 的强大作用是帮助我们快速定位 GC 导致瓶颈的具体位置，但这些例子中仅仅覆盖了其功能的很小一部分，我们也没有必要完整覆盖所有的功能，因为总是可以通过http pprof 官方文档[7]、runtime pprof官方文档[8]以及 trace 官方文档[9]来举一反三。

现在我们来总结一下前面三个例子中的优化情况：

1. 控制内存分配的速度，限制 goroutine 的数量，从而提高赋值器对 CPU 的利用率。
2. 减少并复用内存，例如使用 sync.Pool 来复用需要频繁创建临时对象，例如提前分配足够的内存来降低多余的拷贝。
3. 需要时，增大 GOGC 的值，降低 GC 的运行频率。

这三种情况几乎涵盖了 GC 调优中的核心思路，虽然从语言上还有很多小技巧可说，但我们并不会在这里事无巨细的进行总结。实际情况也是千变万化，我们更应该着重于培养具体问题具体分析的能力。

当然，我们还应该谨记 **过早优化是万恶之源**这一警语，在没有遇到应用的真正瓶颈时，将宝贵的时间分配在开发中其他优先级更高的任务上。

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/memgc/3-%E5%9E%83%E5%9C%BE%E5%9B%9E%E6%94%B6%E7%9A%84%E4%BC%98%E5%8C%96%E9%97%AE%E9%A2%98.md#L18)，来源许可：GPL-3.0。

<a id="k6d12c471f33a"></a>

## Go 的垃圾回收器有哪些相关的 API？其作用分别是什么？

在 Go 中存在数量极少的与 GC 相关的 API，它们是

- runtime.GC：手动触发 GC
- runtime.ReadMemStats：读取内存相关的统计信息，其中包含部分 GC 相关的统计信息
- debug.FreeOSMemory：手动将内存归还给操作系统
- debug.ReadGCStats：读取关于 GC 的相关统计信息
- debug.SetGCPercent：设置 GOGC 调步变量
- debug.SetMaxHeap（尚未发布[10]）：设置 Go 程序堆的上限值

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/memgc/3-%E5%9E%83%E5%9C%BE%E5%9B%9E%E6%94%B6%E7%9A%84%E4%BC%98%E5%8C%96%E9%97%AE%E9%A2%98.md#L483)，来源许可：GPL-3.0。

<a id="k2321ac0dd355"></a>

## Go 语言中 GC 的流程是什么？

当前版本的 Go 以 STW 为界限，可以将 GC 划分为五个阶段：

|       阶段       |                            说明                            | 赋值器状态 |
| :--------------: | :--------------------------------------------------------: | :--------: |
| SweepTermination | 清扫终止阶段，为下一个阶段的并发标记做准备工作，启动写屏障 |    STW     |
|       Mark       |         扫描标记阶段，与赋值器并发执行，写屏障开启         |    并发    |
| MarkTermination  |    标记终止阶段，保证一个周期内标记任务完成，停止写屏障    |    STW     |
|      GCoff       |    内存清扫阶段，将需要回收的内存归还到堆中，写屏障关闭    |    并发    |
|      GCoff       |    内存归还阶段，将过多的内存归还给操作系统，写屏障关闭    |    并发    |

具体而言，各个阶段的触发函数分别为：

![gc-process](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/memgc/assets/gc-process.png)

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/memgc/2-%E5%9E%83%E5%9C%BE%E5%9B%9E%E6%94%B6%E6%9C%BA%E5%88%B6%E7%9A%84%E5%AE%9E%E7%8E%B0.md#L9)，来源许可：GPL-3.0。

<a id="k5640f18c5dfd"></a>

## STW 是什么意思？

`STW` 可以是 `Stop the World` 的缩写，也可以是 `Start the World` 的缩写。通常意义上指指代从 `Stop the World` 这一动作发生时到 `Start the World` 这一动作发生时这一段时间间隔，即万物静止。STW 在垃圾回收过程中为了保证实现的正确性、防止无止境的内存增长等问题而不可避免的需要停止赋值器进一步操作对象图的一段过程。

在这个过程中整个用户代码被停止或者放缓执行， `STW` 越长，对用户代码造成的影响（例如延迟）就越大，早期 Go 对垃圾回收器的实现中 `STW` 长达几百毫秒，对时间敏感的实时通信等应用程序会造成巨大的影响。我们来看一个例子：

```go
package main

import (
	"runtime"
	"time"
)

func main() {
	go func() {
		for {
		}
	}()

	time.Sleep(time.Millisecond)
	runtime.GC()
	println("OK")
}
```

上面的这个程序在 Go 1.14 以前永远都不会输出 `OK`，其罪魁祸首是进入 STW 这一操作的执行无限制的被延长。

尽管 STW 如今已经优化到了半毫秒级别以下，但这个程序被卡死原因是由于需要进入 STW 导致的。原因在于，GC 在需要进入 STW 时，需要通知并让所有的用户态代码停止，但是 `for {}` 所在的 goroutine 永远都不会被中断，从而始终无法进入 STW 阶段。实际实践中也是如此，当程序的某个 goroutine 长时间得不到停止，强行拖慢进入 STW 的时机，这种情况下造成的影响（卡死）是非常可怕的。好在自 Go 1.14 之后，这类 goroutine 能够被异步地抢占，从而使得进入 STW 的时间不会超过抢占信号触发的周期，程序也不会因为仅仅等待一个 goroutine 的停止而停顿在进入 STW 之前的操作上。

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/memgc/1-%E5%9E%83%E5%9C%BE%E5%9B%9E%E6%94%B6%E7%9A%84%E8%AE%A4%E8%AF%86.md#L74)，来源许可：GPL-3.0。

<a id="k2b6a6b5b0d26"></a>

## 三色标记法是什么？

理解**三色标记法**的关键是理解对象的**三色抽象**以及**波面（wavefront）推进**这两个概念。三色抽象只是一种描述追踪式回收器的方法，在实践中并没有实际含义，它的重要作用在于从逻辑上严密推导标记清理这种垃圾回收方法的正确性。也就是说，当我们谈及三色标记法时，通常指标记清扫的垃圾回收。

从垃圾回收器的视角来看，三色抽象规定了三种不同类型的对象，并用不同的颜色相称：

- 白色对象（可能死亡）：未被回收器访问到的对象。在回收开始阶段，所有对象均为白色，当回收结束后，白色对象均不可达。
- 灰色对象（波面）：已被回收器访问到的对象，但回收器需要对其中的一个或多个指针进行扫描，因为他们可能还指向白色对象。
- 黑色对象（确定存活）：已被回收器访问到的对象，其中所有字段都已被扫描，黑色对象中任何一个指针都不可能直接指向白色对象。

这样三种不变性所定义的回收过程其实是一个**波面**不断前进的过程，这个波面同时也是黑色对象和白色对象的边界，灰色对象就是这个波面。

当垃圾回收开始时，只有白色对象。随着标记过程开始进行时，灰色对象开始出现（着色），这时候波面便开始扩大。当一个对象的所有子节点均完成扫描时，会被着色为黑色。当整个堆遍历完成时，只剩下黑色和白色对象，这时的黑色对象为可达对象，即存活；而白色对象为不可达对象，即死亡。这个过程可以视为以灰色对象为波面，将黑色对象和白色对象分离，使波面不断向前推进，直到所有可达的灰色对象都变为黑色对象为止的过程。如下图所示：

![三色标记法全貌](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/memgc/assets/gc-blueprint.png)

图中展示了根对象、可达对象、不可达对象，黑、灰、白对象以及波面之间的关系。

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/memgc/1-%E5%9E%83%E5%9C%BE%E5%9B%9E%E6%94%B6%E7%9A%84%E8%AE%A4%E8%AF%86.md#L56)，来源许可：GPL-3.0。

<a id="k8da195d02bb2"></a>

## 什么是 GC，有什么作用？

`GC`，全称 `Garbage Collection`，即垃圾回收，是一种自动内存管理的机制。

当程序向操作系统申请的内存不再需要时，垃圾回收主动将其回收并供其他代码进行内存申请时候复用，或者将其归还给操作系统，这种针对内存级别资源的自动回收过程，即为垃圾回收。而负责垃圾回收的程序组件，即为垃圾回收器。

垃圾回收其实一个完美的 “Simplicity is Complicated” 的例子。一方面，程序员受益于 GC，无需操心、也不再需要对内存进行手动的申请和释放操作，GC 在程序运行时自动释放残留的内存。另一方面，GC 对程序员几乎不可见，仅在程序需要进行特殊优化时，通过提供可调控的 API，对 GC 的运行时机、运行开销进行把控的时候才得以现身。

通常，垃圾回收器的执行过程被划分为两个半独立的组件：

- 赋值器（Mutator）：这一名称本质上是在指代用户态的代码。因为对垃圾回收器而言，用户态的代码仅仅只是在修改对象之间的引用关系，也就是在对象图（对象之间引用关系的一个有向图）上进行操作。
- 回收器（Collector）：负责执行垃圾回收的代码。

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/memgc/1-%E5%9E%83%E5%9C%BE%E5%9B%9E%E6%94%B6%E7%9A%84%E8%AE%A4%E8%AF%86.md#L9)，来源许可：GPL-3.0。

<a id="k07f580ce2d2e"></a>

## 什么是写屏障、混合写屏障，如何实现？

要讲清楚写屏障，就需要理解三色标记清除算法中的**强弱不变性**以及**赋值器的颜色**，理解他们需要一定的抽象思维。写屏障是一个在并发垃圾回收器中才会出现的概念，垃圾回收器的正确性体现在：**不应出现对象的丢失，也不应错误的回收还不需要回收的对象。**

可以证明，当以下两个条件同时满足时会破坏垃圾回收器的正确性：

- **条件 1**: 赋值器修改对象图，导致某一黑色对象引用白色对象；
- **条件 2**: 从灰色对象出发，到达白色对象的、未经访问过的路径被赋值器破坏。

只要能够避免其中任何一个条件，则不会出现对象丢失的情况，因为：

- 如果条件 1 被避免，则所有白色对象均被灰色对象引用，没有白色对象会被遗漏；
- 如果条件 2 被避免，即便白色对象的指针被写入到黑色对象中，但从灰色对象出发，总存在一条没有访问过的路径，从而找到到达白色对象的路径，白色对象最终不会被遗漏。

我们不妨将三色不变性所定义的波面根据这两个条件进行削弱：

- 当满足原有的三色不变性定义（或上面的两个条件都不满足时）的情况称为**强三色不变性（strong tricolor invariant）**
- 当赋值器令黑色对象引用白色对象时（满足条件 1 时）的情况称为**弱三色不变性（weak tricolor invariant）**

当赋值器进一步破坏灰色对象到达白色对象的路径时（进一步满足条件 2 时），即打破弱三色不变性，
也就破坏了回收器的正确性；或者说，在破坏强弱三色不变性时必须引入额外的辅助操作。
弱三色不变形的好处在于：**只要存在未访问的能够到达白色对象的路径，就可以将黑色对象指向白色对象。**

如果我们考虑并发的用户态代码，回收器不允许同时停止所有赋值器，就是涉及了存在的多个不同状态的赋值器。为了对概念加以明确，还需要换一个角度，把回收器视为对象，把赋值器视为影响回收器这一对象的实际行为（即影响 GC 周期的长短），从而引入赋值器的颜色：

- 黑色赋值器：已经由回收器扫描过，不会再次对其进行扫描。
- 灰色赋值器：尚未被回收器扫描过，或尽管已经扫描过但仍需要重新扫描。

赋值器的颜色对回收周期的结束产生影响：

- 如果某种并发回收器允许灰色赋值器的存在，则必须在回收结束之前重新扫描对象图。
- 如果重新扫描过程中发现了新的灰色或白色对象，回收器还需要对新发现的对象进行追踪，但是在新追踪的过程中，赋值器仍然可能在其根中插入新的非黑色的引用，如此往复，直到重新扫描过程中没有发现新的白色或灰色对象。

于是，在允许灰色赋值器存在的算法，最坏的情况下，回收器只能将所有赋值器线程停止才能完成其跟对象的完整扫描，也就是我们所说的 STW。

为了确保强弱三色不变性的并发指针更新操作，需要通过赋值器屏障技术来保证指针的读写操作一致。因此我们所说的 Go 中的写屏障、混合写屏障，其实是指赋值器的写屏障，赋值器的写屏障作为一种同步机制，使赋值器在进行指针写操作时，能够“通知”回收器，进而不会破坏弱三色不变性。

有两种非常经典的写屏障：Dijkstra 插入屏障和 Yuasa 删除屏障。

灰色赋值器的 Dijkstra 插入屏障的基本思想是避免满足条件 1：

```go
// 灰色赋值器 Dijkstra 插入屏障
func DijkstraWritePointer(slot *unsafe.Pointer, ptr unsafe.Pointer) {
    shade(ptr)
    *slot = ptr
}
```

为了防止黑色对象指向白色对象，应该假设 `*slot` 可能会变为黑色，为了确保 `ptr` 不会在被赋值到 `*slot` 前变为白色，`shade(ptr)` 会先将指针 `ptr` 标记为灰色，进而避免了条件 1。如图所示：

![](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/memgc/assets/gc-wb-dijkstra.png)

Dijkstra 插入屏障的好处在于可以立刻开始并发标记。但存在两个缺点：

1. 由于 Dijkstra 插入屏障的“保守”，在一次回收过程中可能会残留一部分对象没有回收成功，只有在下一个回收过程中才会被回收；
2. 在标记阶段中，每次进行指针赋值操作时，都需要引入写屏障，这无疑会增加大量性能开销；为了避免造成性能问题，Go 团队在最终实现时，没有为所有栈上的指针写操作，启用写屏障，而是当发生栈上的写操作时，将栈标记为灰色，但此举产生了灰色赋值器，将会需要标记终止阶段 STW 时对这些栈进行重新扫描。

另一种比较经典的写屏障是黑色赋值器的 Yuasa 删除屏障。其基本思想是避免满足条件 2：

```go
// 黑色赋值器 Yuasa 屏障
func YuasaWritePointer(slot *unsafe.Pointer, ptr unsafe.Pointer) {
    shade(*slot)
    *slot = ptr
}
```

为了防止丢失从灰色对象到白色对象的路径，应该假设 `*slot` 可能会变为黑色，为了确保 `ptr` 不会在被赋值到 `*slot` 前变为白色，`shade(*slot)` 会先将 `*slot` 标记为灰色，进而该写操作总是创造了一条灰色到灰色或者灰色到白色对象的路径，进而避免了条件 2。

Yuasa 删除屏障的优势则在于不需要标记结束阶段的重新扫描，结束时候能够准确的回收所有需要回收的白色对象。缺陷是 Yuasa 删除屏障会拦截写操作，进而导致波面的退后，产生“冗余”的扫描：

![](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/memgc/assets/gc-wb-yuasa.png)

Go 在 1.8 的时候为了简化 GC 的流程，同时减少标记终止阶段的重扫成本，将 Dijkstra 插入屏障和 Yuasa 删除屏障进行混合，形成混合写屏障。该屏障提出时的基本思想是：**对正在被覆盖的对象进行着色，且如果当前栈未扫描完成，则同样对指针进行着色。**

但在最终实现时原提案[4]中对 `ptr` 的着色还额外包含对执行栈的着色检查，但由于时间有限，并未完整实现过，所以混合写屏障在目前的实现伪代码是：

```go
// 混合写屏障
func HybridWritePointerSimple(slot *unsafe.Pointer, ptr unsafe.Pointer) {
	shade(*slot)
	shade(ptr)
	*slot = ptr
}
```

在这个实现中，如果无条件对引用双方进行着色，自然结合了 Dijkstra 和 Yuasa 写屏障的优势，但缺点也非常明显，因为着色成本是双倍的，而且编译器需要插入的代码也成倍增加，随之带来的结果就是编译后的二进制文件大小也进一步增加。为了针对写屏障的性能进行优化，Go 1.10 前后，Go 团队随后实现了批量写屏障机制。其基本想法是将需要着色的指针统一写入一个缓存，每当缓存满时统一对缓存中的所有 `ptr` 指针进行着色。

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/memgc/1-%E5%9E%83%E5%9C%BE%E5%9B%9E%E6%94%B6%E7%9A%84%E8%AE%A4%E8%AF%86.md#L434)，来源许可：GPL-3.0。

<a id="kc285dcdff208"></a>

## 初始化 g0 栈

接着往后看，开始初始化 g0 的栈了。g0 栈的作用就是为运行 runtime 代码提供一个“环境”。

```asm
// 把 g0 的地址存入 DI
MOVQ	$runtime·g0(SB), DI
// BX = SP - 64*1024 + 104
LEAQ	(-64*1024+104)(SP), BX
// g0.stackguard0 = SP - 64*1024 + 104
MOVQ	BX, g_stackguard0(DI)
// g0.stackguard1 = SP - 64*1024 + 104
MOVQ	BX, g_stackguard1(DI)
// g0.stack.lo = SP - 64*1024 + 104
MOVQ	BX, (g_stack+stack_lo)(DI)
// g0.stack.hi = SP
MOVQ	SP, (g_stack+stack_hi)(DI)
```

代码 L2 把 g0 的地址存入 DI 寄存器；L4 将 SP 下移 (64K-104)B，并将地址存入 BX 寄存器；L6 将 BX 里存储的地址赋给 g0.stackguard0；L8，L10，L12 分别 将 BX 里存储的地址赋给 g0.stackguard1， g0.stack.lo， g0.stack.hi。

这部分完成之后，g0 栈空间如下图：

![g0 栈空间](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/sched/assets/21.png)

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/sched/7-%E6%8F%8F%E8%BF%B0%20scheduler%20%E7%9A%84%E5%88%9D%E5%A7%8B%E5%8C%96%E8%BF%87%E7%A8%8B.md#L331)，来源许可：GPL-3.0。

<a id="k40e5fed5f4c2"></a>

## 如果内存分配速度超过了标记清除的速度怎么办？

目前的 Go 实现中，当 GC 触发后，会首先进入并发标记的阶段。并发标记会设置一个标志，并在 mallocgc 调用时进行检查。当存在新的内存分配时，会暂停分配内存过快的那些 goroutine，并将其转去执行一些辅助标记（Mark Assist）的工作，从而达到放缓继续分配、辅助 GC 的标记工作的目的。

编译器会分析用户代码，并在需要分配内存的位置，将申请内存的操作翻译为 `mallocgc` 调用，而 `mallocgc` 的实现决定了标记辅助的实现，其伪代码思路如下：

```go
func mallocgc(t typ.Type, size uint64) {
	if enableMarkAssist {
		// 进行标记辅助，此时用户代码没有得到执行
		(...)
	}
	// 执行内存分配
	(...)
}
```

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/memgc/2-%E5%9E%83%E5%9C%BE%E5%9B%9E%E6%94%B6%E6%9C%BA%E5%88%B6%E7%9A%84%E5%AE%9E%E7%8E%B0.md#L181)，来源许可：GPL-3.0。

<a id="ka0171a2d6a43"></a>

## 常见的 GC 实现方式有哪些？Go 语言的 GC 使用的是什么？

所有的 GC 算法其存在形式可以归结为追踪（Tracing）和引用计数（Reference Counting）这两种形式的混合运用。

- 追踪式 GC 

  从根对象出发，根据对象之间的引用信息，一步步推进直到扫描完毕整个堆并确定需要保留的对象，从而回收所有可回收的对象。Go、 Java、V8 对 JavaScript 的实现等均为追踪式 GC。
- 引用计数式 GC

  每个对象自身包含一个被引用的计数器，当计数器归零时自动得到回收。因为此方法缺陷较多，在追求高性能时通常不被应用。Python、Objective-C 等均为引用计数式 GC。

目前比较常见的 GC 实现方式包括：

- 追踪式，分为多种不同类型，例如：
  - 标记清扫：从根对象出发，将确定存活的对象进行标记，并清扫可以回收的对象。
  - 标记整理：为了解决内存碎片问题而提出，在标记过程中，将对象尽可能整理到一块连续的内存上。
  - 增量式：将标记与清扫的过程分批执行，每次执行很小的部分，从而增量的推进垃圾回收，达到近似实时、几乎无停顿的目的。
  - 增量整理：在增量式的基础上，增加对对象的整理过程。
  - 分代式：将对象根据存活时间的长短进行分类，存活时间小于某个值的为年轻代，存活时间大于某个值的为老年代，永远不会参与回收的对象为永久代。并根据分代假设（如果一个对象存活时间不长则倾向于被回收，如果一个对象已经存活很长时间则倾向于存活更长时间）对对象进行回收。
- 引用计数：根据对象自身的引用计数来回收，当引用计数归零时立即回收。

关于各类方法的详细介绍及其实现不在本文中详细讨论。对于 Go 而言，Go 的 GC 目前使用的是无分代（对象没有代际之分）、不整理（回收过程中不对对象进行移动与整理）、并发（与用户代码并发执行）的三色标记清扫算法。原因[1]在于：

1. 对象整理的优势是解决内存碎片问题以及“允许”使用顺序内存分配器。但 Go 运行时的分配算法基于 tcmalloc，基本上没有碎片问题。 并且顺序内存分配器在多线程的场景下并不适用。Go 使用的是基于 tcmalloc 的现代内存分配算法，对对象进行整理不会带来实质性的性能提升。
2. 分代 GC 依赖分代假设，即 GC 将主要的回收目标放在新创建的对象上（存活时间短，更倾向于被回收），而非频繁检查所有对象。但 Go 的编译器会通过**逃逸分析**将大部分新生对象存储在栈上（栈直接被回收），只有那些需要长期存在的对象才会被分配到需要进行垃圾回收的堆中。也就是说，分代 GC 回收的那些存活时间短的对象在 Go 中是直接被分配到栈上，当 goroutine 死亡后栈也会被直接回收，不需要 GC 的参与，进而分代假设并没有带来直接优势。并且 Go 的垃圾回收器与用户代码并发执行，使得 STW 的时间与对象的代际、对象的 size 没有关系。Go 团队更关注于如何更好地让 GC 与用户代码并发执行（使用适当的 CPU 来执行垃圾回收），而非减少停顿时间这一单一目标上。

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/memgc/1-%E5%9E%83%E5%9C%BE%E5%9B%9E%E6%94%B6%E7%9A%84%E8%AE%A4%E8%AF%86.md#L30)，来源许可：GPL-3.0。

<a id="k60792c495afa"></a>

## 有了 GC，为什么还会发生内存泄露？

在一个具有 GC 的语言中，我们常说的内存泄漏，用严谨的话来说应该是：预期的能很快被释放的内存由于附着在了长期存活的内存上、或生命期意外地被延长，导致预计能够立即回收的内存而长时间得不到回收。

在 Go 中，由于 goroutine 的存在，所谓的内存泄漏除了附着在长期对象上之外，还存在多种不同的形式。

### 形式1：预期能被快速释放的内存因被根对象引用而没有得到迅速释放

当有一个全局对象时，可能不经意间将某个变量附着在其上，且忽略的将其进行释放，则该内存永远不会得到释放。例如：

```go
var cache = map[interface{}]interface{}{}

func keepalloc() {
	for i := 0; i < 10000; i++ {
		m := make([]byte, 1<<10)
		cache[i] = m
	}
}
```

### 形式2：goroutine 泄漏

Goroutine 作为一种逻辑上理解的轻量级线程，需要维护执行用户代码的上下文信息。在运行过程中也需要消耗一定的内存来保存这类信息，而这些内存在目前版本的 Go 中是不会被释放的。因此，如果一个程序持续不断地产生新的 goroutine、且不结束已经创建的 goroutine 并复用这部分内存，就会造成内存泄漏的现象，例如：

```go
func keepalloc2() {
	for i := 0; i < 100000; i++ {
		go func() {
			select {}
		}()
	}
}
```

### 验证

我们可以通过如下形式来调用上述两个函数：

```go
package main

import (
	"os"
	"runtime/trace"
)

func main() {
	f, _ := os.Create("trace.out")
	defer f.Close()
	trace.Start(f)
	defer trace.Stop()
	keepalloc()
	keepalloc2()
}
```

运行程序：

```shell
go run main.go
```

会看到程序中生成了 `trace.out` 文件，我们可以使用 `go tool trace trace.out` 命令得到下图：

![](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/memgc/assets/gc-leak1.png)

可以看到，图中的 Heap 在持续增长，没有内存被回收，产生了内存泄漏的现象。

值得一提的是，这种形式的 goroutine 泄漏还可能由 channel 泄漏导致。而 channel 的泄漏本质上与 goroutine 泄漏存在直接联系。Channel 作为一种同步原语，会连接两个不同的 goroutine，如果一个 goroutine 尝试向一个没有接收方的无缓冲 channel 发送消息，则该 goroutine 会被永久的休眠，整个 goroutine 及其执行栈都得不到释放，例如：

```go
var ch = make(chan struct{})

func keepalloc3() {
	for i := 0; i < 100000; i++ {
		// 没有接收方，goroutine 会一直阻塞
		go func() { ch <- struct{}{} }()
	}
}
```

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/memgc/1-%E5%9E%83%E5%9C%BE%E5%9B%9E%E6%94%B6%E7%9A%84%E8%AE%A4%E8%AF%86.md#L328)，来源许可：GPL-3.0。

<a id="k8a3151d76bd5"></a>

## 根对象到底是什么？

根对象在垃圾回收的术语中又叫做根集合，它是垃圾回收器在标记过程时最先检查的对象，包括：

1. 全局变量：程序在编译期就能确定的那些存在于程序整个生命周期的变量。
2. 执行栈：每个 goroutine 都包含自己的执行栈，这些执行栈上包含栈上的变量及指向分配的堆内存区块的指针。
3. 寄存器：寄存器的值可能表示一个指针，参与计算的这些指针可能指向某些赋值器分配的堆内存区块。

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/memgc/1-%E5%9E%83%E5%9C%BE%E5%9B%9E%E6%94%B6%E7%9A%84%E8%AE%A4%E8%AF%86.md#L22)，来源许可：GPL-3.0。

<a id="k3812291605db"></a>

## 目前 Go 语言的 GC 还存在哪些问题？

尽管 Go 团队宣称 STW 停顿时间得以优化到 100 微秒级别，但这本质上是一种取舍。原本的 STW 某种意义上来说其实转移到了可能导致用户代码停顿的几个位置；除此之外，由于运行时调度器的实现方式，同样对 GC 存在一定程度的影响。

目前 Go 中的 GC 仍然存在以下问题：

### 1. Mark Assist 停顿时间过长

```go
package main

import (
	"fmt"
	"os"
	"runtime"
	"runtime/trace"
	"time"
)

const (
	windowSize = 200000
	msgCount   = 1000000
)

var (
	best    time.Duration = time.Second
	bestAt  time.Time
	worst   time.Duration
	worstAt time.Time

	start = time.Now()
)

func main() {
	f, _ := os.Create("trace.out")
	defer f.Close()
	trace.Start(f)
	defer trace.Stop()

	for i := 0; i < 5; i++ {
		measure()
		worst = 0
		best = time.Second
		runtime.GC()
	}
}

func measure() {
	var c channel
	for i := 0; i < msgCount; i++ {
		c.sendMsg(i)
	}
	fmt.Printf("Best send delay %v at %v, worst send delay: %v at %v. Wall clock: %v \n", best, bestAt.Sub(start), worst, worstAt.Sub(start), time.Since(start))
}

type channel [windowSize][]byte

func (c *channel) sendMsg(id int) {
	start := time.Now()

	// 模拟发送
	(*c)[id%windowSize] = newMsg(id)

	end := time.Now()
	elapsed := end.Sub(start)
	if elapsed > worst {
		worst = elapsed
		worstAt = end
	}
	if elapsed < best {
		best = elapsed
		bestAt = end
	}
}

func newMsg(n int) []byte {
	m := make([]byte, 1024)
	for i := range m {
		m[i] = byte(n)
	}
	return m
}
```

运行此程序我们可以得到类似下面的结果：

```
$ go run main.go

Best send delay 330ns at 773.037956ms, worst send delay: 7.127915ms at 579.835487ms. Wall clock: 831.066632ms 
Best send delay 331ns at 873.672966ms, worst send delay: 6.731947ms at 1.023969626s. Wall clock: 1.515295559s 
Best send delay 330ns at 1.812141567s, worst send delay: 5.34028ms at 2.193858359s. Wall clock: 2.199921749s 
Best send delay 338ns at 2.722161771s, worst send delay: 7.479482ms at 2.665355216s. Wall clock: 2.920174197s 
Best send delay 337ns at 3.173649445s, worst send delay: 6.989577ms at 3.361716121s. Wall clock: 3.615079348s 
```
![](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/assets/gc-mark-assist.png)

在这个结果中，第一次的最坏延迟时间高达 7.12 毫秒，发生在程序运行 578 毫秒左右。通过 `go tool trace` 可以发现，这个时间段中，Mark Assist 执行了 7112312ns，约为 7.127915ms；可见，此时最坏情况下，标记辅助拖慢了用户代码的执行，是造成 7 毫秒延迟的原因。

<!-- https://github.com/golang/go/issues/27732 -->
<!-- https://github.com/golang/go/issues/27410 -->

### 2. Sweep 停顿时间过长

同样还是刚才的例子，如果我们仔细观察 Mark Assist 后发生的 Sweep 阶段，竟然对用户代码的影响长达约 30ms，根据调用栈信息可以看到，该 Sweep 过程发生在内存分配阶段：

![](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/memgc/assets/gc-mark-sweep.png)

<!-- https://github.com/golang/go/issues/18155 -->

### 3. 由于 GC 算法的不正确性导致 GC 周期被迫重新执行

此问题很难复现，但是一个已知的问题，根据 Go 团队的描述，能够在 1334 次构建中发生一次 [15]，我们可以计算出其触发概率约为 0.0007496251874。虽然发生概率很低，但一旦发生，GC 需要被重新执行，非常不幸。

<!-- https://github.com/golang/go/issues/27993 -->

### 4. 创建大量 Goroutine 后导致 GC 消耗更多的 CPU

这个问题可以通过以下程序进行验证：

```go
func BenchmarkGCLargeGs(b *testing.B) {
	wg := sync.WaitGroup{}

	for ng := 100; ng <= 1000000; ng *= 10 {
		b.Run(fmt.Sprintf("#g-%d", ng), func(b *testing.B) {
			// 创建大量 goroutine，由于每次创建的 goroutine 会休眠
			// 从而运行时不会复用正在休眠的 goroutine，进而不断创建新的 g
			wg.Add(ng)
			for i := 0; i < ng; i++ {
				go func() {
					time.Sleep(100 * time.Millisecond)
					wg.Done()
				}()
			}
			wg.Wait()

			// 现运行一次 GC 来提供一致的内存环境
			runtime.GC()

			// 记录运行 b.N 次 GC 需要的时间
			b.ResetTimer()
			for i := 0; i < b.N; i++ {
				runtime.GC()
			}
		})

	}
}
```

其结果可以通过如下指令来获得：

```shell
$ go test -bench=BenchmarkGCLargeGs -run=^$ -count=5 -v . | tee 4.txt
$ benchstat 4.txt
name                     time/op
GCLargeGs/#g-100-12       192µs ± 5%
GCLargeGs/#g-1000-12      331µs ± 1%
GCLargeGs/#g-10000-12    1.22ms ± 1%
GCLargeGs/#g-100000-12   10.9ms ± 3%
GCLargeGs/#g-1000000-12  32.5ms ± 4%
```

这种情况通常发生于峰值流量后，大量 goroutine 由于任务等待被休眠，从而运行时不断创建新的 goroutine，
旧的 goroutine 由于休眠未被销毁且得不到复用，导致 GC 需要扫描的执行栈越来越多，进而完成 GC 所需的时间越来越长。
一个解决办法是使用 goroutine 池来限制创建的 goroutine 数量。

<!-- https://github.com/golang/go/issues/34457 -->

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/memgc/4-%E5%8E%86%E5%8F%B2%E5%8F%8A%E6%BC%94%E8%BF%9B.md#L122)，来源许可：GPL-3.0。

<a id="k1b07961213d5"></a>

## 触发 GC 的时机是什么？

Go 语言中对 GC 的触发时机存在两种形式：  

1. **主动触发**，通过调用 runtime.GC 来触发 GC，此调用阻塞式地等待当前 GC 运行完毕。

2. **被动触发**，分为两种方式：

   - 使用系统监控，当超过两分钟没有产生任何 GC 时，强制触发 GC。

   - 使用步调（Pacing）算法，其核心思想是控制内存增长的比例。

通过 `GOGC` 或者 `debug.SetGCPercent` 进行控制（他们控制的是同一个变量，即堆的增长率 $\rho$）。整个算法的设计考虑的是优化问题：如果设上一次 GC 完成时，内存的数量为 $H_m$（heap marked），估计需要触发 GC 时的堆大小 $H_T$（heap trigger），使得完成 GC 时候的目标堆大小 $H_g$（heap goal） 与实际完成时候的堆大小 $H_a$（heap actual）最为接近，即： $\min |H_g - H_a| = \min|(1+\rho)H_m - H_a|$。

![gc-pacing](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/memgc/assets/gc-pacing.png)

除此之外，步调算法还需要考虑 CPU 利用率的问题，显然我们不应该让垃圾回收器占用过多的 CPU，即不应该让每个负责执行用户 goroutine 的线程都在执行标记过程。理想情况下，在用户代码满载的时候，GC 的 CPU 使用率不应该超过 25%，即另一个优化问题：如果设 $u_g$为目标 CPU 使用率（goal utilization），而 $u_a$为实际 CPU 使用率（actual utilization），则 $\min|u_g - u_a|$。

> 求解这两个优化问题的具体数学建模过程我们不在此做深入讨论，有兴趣的读者可以参考两个设计文档：Go 1.5 concurrent garbage collector pacing[5] 和 Separate soft and hard heap size goal[6]。

计算 $H_T$ 的最终结论（从 Go 1.10 时开始 $h_t$ 增加了上界 $0.95 \rho$，从 Go 1.14 开始时 $h_t$ 增加了下界 $0.6 \rho$）是：

- 设第 n 次触发 GC 时 (n > 1)，估计得到的堆增长率为 $h_t^{(n)}$、运行过程中的实际堆增长率为 $h_a^{(n)}$，用户设置的增长率为 $\rho = \text{GOGC}/100$（ $\rho > 0$）则第 $n+1$ 次出触发 GC 时候，估计的堆增长率为：

$$
h_t^{(n+1)} = h_t^{(n)} + 0.5 \left[ \frac{H_g^{(n)} - H_a^{(n)}}{H_a^{(n)}} - h_t^{(n)} - \frac{u_a^{(n)}}{u_g^{(n)}} \left( h_a^{(n)} - h_t^{(n)} \right) \right]
$$

- 特别的，$h_t^{(1)} = 7 / 8$，$u_a^{(1)} = 0.25$，$u_g^{(1)} = 0.3$。第一次触发 GC 时，如果当前的堆小于 $4\rho$ MB，则强制调整到 $4\rho$ MB 时触发 GC

- 特别的，当 $h_t^{(n)}<0.6 \rho$时，将其调整为 $0.6 \rho$，当 $h_t^{(n)} > 0.95 \rho$ 时，将其设置为 $0.95 \rho$（在默认 $\text{GOGC}=100$ 即 $\rho=1$ 时，下界即为 $0.6$）

- 默认情况下，$\rho = 1$（即 GOGC = 100），第一次触发 GC 时强制设置触发第一次 GC 为 4MB，可以写如下程序进行验证：

```go
package main

import (
	"os"
	"runtime"
	"runtime/trace"
	"sync/atomic"
)

var stop uint64

// 通过对象 P 的释放状态，来确定 GC 是否已经完成
func gcfinished() *int {
	p := 1
	runtime.SetFinalizer(&p, func(_ *int) {
		println("gc finished")
		atomic.StoreUint64(&stop, 1) // 通知停止分配
	})
	return &p
}

func allocate() {
	// 每次调用分配 0.25MB
	_ = make([]byte, int((1<<20)*0.25))
}

func main() {
	f, _ := os.Create("trace.out")
	defer f.Close()
	trace.Start(f)
	defer trace.Stop()

	gcfinished()

	// 当完成 GC 时停止分配
	for n := 1; atomic.LoadUint64(&stop) != 1; n++ {
		println("#allocate: ", n)
		allocate()
	}
	println("terminate")
}
```

我们先来验证最简单的一种情况，即第一次触发 GC 时的堆大小：

```
$ go build -o main
$ GODEBUG=gctrace=1 ./main
#allocate:  1
(...)
#allocate:  20
gc finished
gc 1 @0.001s 3%: 0.016+0.23+0.019 ms clock, 0.20+0.11/0.060/0.13+0.22 ms cpu, 4->5->1 MB, 5 MB goal, 12 P
scvg: 8 KB released
scvg: inuse: 1, idle: 62, sys: 63, released: 58, consumed: 5 (MB)
terminate
```

通过这一行数据我们可以看到：

```
gc 1 @0.001s 3%: 0.016+0.23+0.019 ms clock, 0.20+0.11/0.060/0.13+0.22 ms cpu, 4->5->1 MB, 5 MB goal, 12 P
```

1. 程序在完成第一次 GC 后便终止了程序，符合我们的设想
2. 第一次 GC 开始时的堆大小为 4MB，符合我们的设想
3. 当标记终止时，堆大小为 5MB，此后开始执行清扫，这时分配执行到第 20 次，即 20*0.25 = 5MB，符合我们的设想

我们将分配次数调整到 50 次

```go
for n := 1; n < 50; n++ {
	println("#allocate: ", n)
	allocate()
}
```

来验证第二次 GC 触发时是否满足公式所计算得到的值（为 GODEBUG 进一步设置 `gcpacertrace=1`）：

```
$ go build -o main
$ GODEBUG=gctrace=1,gcpacertrace=1 ./main
#allocate:  1
(...)

pacer: H_m_prev=2236962 h_t=+8.750000e-001 H_T=4194304 h_a=+2.387451e+000 H_a=7577600 h_g=+1.442627e+000 H_g=5464064 u_a=+2.652227e-001 u_g=+3.000000e-001 W_a=152832 goalΔ=+5.676271e-001 actualΔ=+1.512451e+000 u_a/u_g=+8.840755e-001
#allocate:  28
gc 1 @0.001s 5%: 0.032+0.32+0.055 ms clock, 0.38+0.068/0.053/0.11+0.67 ms cpu, 4->7->3 MB, 5 MB goal, 12 P

(...)
#allocate:  37
pacer: H_m_prev=3307736 h_t=+6.000000e-001 H_T=5292377 h_a=+7.949171e-001 H_a=5937112 h_g=+1.000000e+000 H_g=6615472 u_a=+2.658428e-001 u_g=+3.000000e-001 W_a=154240 goalΔ=+4.000000e-001 actualΔ=+1.949171e-001 u_a/u_g=+8.861428e-001
#allocate:  38
gc 2 @0.002s 9%: 0.017+0.26+0.16 ms clock, 0.20+0.079/0.058/0.12+1.9 ms cpu, 5->5->0 MB, 6 MB goal, 12 P
```

我们可以得到数据：

- 第一次估计得到的堆增长率为 $h_t^{(1)} = 0.875$
- 第一次的运行过程中的实际堆增长率为 $h_a^{(1)} = 0.2387451$
- 第一次实际的堆大小为 $H_a^{(1)}=7577600$
- 第一次目标的堆大小为 $H_g^{(1)}=5464064$
- 第一次的 CPU 实际使用率为 $u_a^{(1)} = 0.2652227$
- 第一次的 CPU 目标使用率为 $u_g^{(1)} = 0.3$

我们据此计算第二次估计的堆增长率：

$$
h_t^{(2)} = h_t^{(1)} + 0.5 \left[ \frac{H_g^{(1)} - H_a^{(1)}}{H_a^{(1)}} - h_t^{(1)} - \frac{u_a^{(1)}}{u_g^{(1)}} \left( h_a^{(1)} - h_t^{(1)} \right) \right]
$$

$$
= 0.875 + 0.5 \left[ \frac{5464064 - 7577600}{5464064} - 0.875 - \frac{0.2652227}{0.3} \left( 0.2387451 - 0.875 \right) \right]
$$

$$
\approx 0.52534543909
$$

因为 $0.52534543909 < 0.6\rho = 0.6$，因此下一次的触发率为 $h_t^{2} = 0.6$，与我们实际观察到的第二次 GC 的触发率 0.6 吻合。

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/memgc/2-%E5%9E%83%E5%9C%BE%E5%9B%9E%E6%94%B6%E6%9C%BA%E5%88%B6%E7%9A%84%E5%AE%9E%E7%8E%B0.md#L25)，来源许可：GPL-3.0。
