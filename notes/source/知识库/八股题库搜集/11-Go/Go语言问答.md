# Go语言问答

<a id="k6274b40e1b32"></a>

## Go指针和unsafe.Pointer有什么区别

Go 语言的作者之一 Ken Thompson 也是 C 语言的作者。所以，Go 可以看作 C 系语言，它的很多特性都和 C 类似，指针就是其中之一。

然而，Go 语言的指针相比 C 的指针有很多限制。这当然是为了安全考虑，要知道像 Java/Python 这些现代语言，生怕程序员出错，哪有什么指针（这里指的是显式的指针）？更别说像 C/C++ 还需要程序员自己清理“垃圾”。所以对于 Go 来说，有指针已经很不错了，仅管它有很多限制。

相比于 C 语言中指针的灵活，Go 的指针多了一些限制。但这也算是 Go 的成功之处：既可以享受指针带来的便利，又避免了指针的危险性。

限制一：`Go 的指针不能进行数学运算`。

来看一个简单的例子：

```golang
a := 5
p := &a

p++
p = &a + 3
```

上面的代码将不能通过编译，会报编译错误：`invalid operation`，也就是说不能对指针做数学运算。

限制二：`不同类型的指针不能相互转换`。

例如下面这个简短的例子：

```golang
func main() {
	a := int(100)
	var f *float64

	f = &a
}
```

也会报编译错误：

```shell
cannot use &a (type *int) as type *float64 in assignment
```

限制三：`不同类型的指针不能使用 == 或 != 比较`。

只有在两个指针类型相同或者可以相互转换的情况下，才可以对两者进行比较。另外，指针可以通过 `==` 和 `!=` 直接和 `nil` 作比较。

限制四：`不同类型的指针变量不能相互赋值`。

这一点同限制三。

unsafe.Pointer 在 unsafe 包：

```golang
type ArbitraryType int

type Pointer *ArbitraryType
```

从命名来看，`Arbitrary` 是任意的意思，也就是说 Pointer 可以指向任意类型，实际上它类似于 C 语言里的 `void*`。

unsafe 包提供了 2 点重要的能力：

> 1. 任何类型的指针和 unsafe.Pointer 可以相互转换。
> 2. uintptr 类型和 unsafe.Pointer 可以相互转换。

![type pointer uintptr](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/stdlib/unsafe/assets/0.png)

pointer 不能直接进行数学运算，但可以把它转换成 uintptr，对 uintptr 类型进行数学运算，再转换成 pointer 类型。

```golang
// uintptr 是一个整数类型，它足够大，可以存储
type uintptr uintptr
```

还有一点要注意的是，uintptr 并没有指针的语义，意思就是 uintptr 所指向的对象会被 gc 无情地回收。而 unsafe.Pointer 有指针语义，可以保护它所指向的对象在“有用”的时候不会被垃圾回收。

unsafe 包中的几个函数都是在编译期间执行完毕，毕竟，编译器对内存分配这些操作“了然于胸”。在 `/usr/local/go/src/cmd/compile/internal/gc/unsafe.go` 路径下，可以看到编译期间 Go 对 unsafe 包中函数的处理。

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/stdlib/unsafe/1-Go%E6%8C%87%E9%92%88%E5%92%8Cunsafe.Pointer%E6%9C%89%E4%BB%80%E4%B9%88%E5%8C%BA%E5%88%AB.md#L3)，来源许可：GPL-3.0。

<a id="kf5829c4f7b8d"></a>

## M 如何找工作

在 schedule 函数中，我们简单提过找一个 runnable goroutine 的过程，这一讲我们来详细分析源码。

工作线程 M 费尽心机也要找到一个可运行的 goroutine，这是它的工作和职责，不达目的，绝不罢体，这种锲而不舍的精神值得每个人学习。

共经历三个过程：先从本地队列找，定期会从全局队列找，最后实在没办法，就去别的 P 偷。如下图所示：

![M 找工作的过程](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/sched/assets/4.png)

先看第一个：从 P 本地队列找。源码如下：

```golang
// 从本地可运行队列里找到一个 g
// 如果 inheritTime 为真，gp 应该继承这个时间片，否则，新开启一个时间片
func runqget(_p_ *p) (gp *g, inheritTime bool) {
	// If there's a runnext, it's the next G to run.
	// 如果 runnext 不为空，则 runnext 是下一个待运行的 G
	for {
		next := _p_.runnext
		if next == 0 {
			// 为空，则直接跳出循环
			break
		}
		// 再次比较 next 是否没有变化
		if _p_.runnext.cas(next, 0) {
			// 如果没有变化，则返回 next 所指向的 g。且需要继承时间片
			return next.ptr(), true
		}
	}

	for {
		// 获取队列头
		h := atomic.Load(&_p_.runqhead) // load-acquire, synchronize with other consumers
		// 获取队列尾
		t := _p_.runqtail
		if t == h {
			// 头和尾相等，说明本地队列为空，找不到 g
			return nil, false
		}
		// 获取队列头的 g
		gp := _p_.runq[h%uint32(len(_p_.runq))].ptr()
		// 原子操作，防止这中间被其他线程因为偷工作而修改
		if atomic.Cas(&_p_.runqhead, h, h+1) { // cas-release, commits consume
			return gp, false
		}
	}
}
```

整个源码结构比较简单，主要是两个 for 循环。

第一个 for 循环尝试返回 P 的 runnext 成员，因为 runnext 具有最高的运行优先级，因此要首先尝试获取 runnext。当发现 runnext 为空时，直接跳出循环，进入第二个。否则，用原子操作获取 runnext，并将其值修改为 0，也就是空。这里用到原子操作的原因是防止在这个过程中，有其他线程过来“偷工作”，导致并发修改 runnext 成员。

第二个 for 循环则是在尝试获取 runnext 成员失败后，尝试从本地队列中返回队列头的 goroutine。同样，先用原子操作获取队列头，使用原子操作的原因同样是防止其他线程“偷工作”时并发对队列头的并发写操作。之后，直接获取队列尾，因为不担心其他线程同时更改，所以直接获取。注意，“偷工作”时只会修改队列头。

比较队列头和队列尾，如果两者相等，说明 P 本地队列没有可运行的 goroutine，直接返回空。否则，算出队列头指向的 goroutine，再用一个 CAS 原子操作来尝试修改队列头，使用原子操作的原因同上。

从本地队列获取可运行 goroutine 的过程比较简单，我们再来看从全局队列获取 goroutine 的过程。在 schedule 函数中调用 `globrunqget` 的代码：

```golang
// 为了公平，每调用 schedule 函数 61 次就要从全局可运行 goroutine 队列中获取
if _g_.m.p.ptr().schedtick%61 == 0 && sched.runqsize > 0 {
	lock(&sched.lock)
	// 从全局队列最大获取 1 个 goroutine
	gp = globrunqget(_g_.m.p.ptr(), 1)
	unlock(&sched.lock)
}
```

这说明，并不是每次调度都会从全局队列获取可运行的 goroutine。实际情況是调度器每调度 61 次并且全局队列有可运行 goroutine 的情况下才会调用 `globrunqget` 函数尝试从全局获取可运行 goroutine。毕竟，从全局获取需要上锁，这个开销可就大了，能不做就不做。

我们来详细看下 `globrunqget` 的源码：

```golang
// 尝试从全局队列里获取可运行的 goroutine 队列
func globrunqget(_p_ *p, max int32) *g {
	// 如果队列大小为 0
	if sched.runqsize == 0 {
		return nil
	}

	// 根据 p 的数量平分全局运行队列中的 goroutines
	n := sched.runqsize/gomaxprocs + 1
	if n > sched.runqsize {
		n = sched.runqsize // 如果 gomaxprocs 为 1
	}

	// 修正"偷"的数量
	if max > 0 && n > max {
		n = max
	}
	// 最多只能"偷"本地工作队列一半的数量
	if n > int32(len(_p_.runq))/2 {
		n = int32(len(_p_.runq)) / 2
	}

	// 更新全局可运行队列长度
	sched.runqsize -= n
	// 如果都要被"偷"走，修改队列尾
	if sched.runqsize == 0 {
		sched.runqtail = 0
	}

	// 获取队列头指向的 goroutine
	gp := sched.runqhead.ptr()
	// 移动队列头
	sched.runqhead = gp.schedlink
	n--
	for ; n > 0; n-- {
		// 获取当前队列头
		gp1 := sched.runqhead.ptr()
		// 移动队列头
		sched.runqhead = gp1.schedlink
		// 尝试将 gp1 放入 P 本地，使全局队列得到更多的执行机会
		runqput(_p_, gp1, false)
	}
	// 返回最开始获取到的队列头所指向的 goroutine
	return gp
}
```

代码比较简单。首先根据全局队列的可运行 goroutine 长度和 P 的总数，来计算一个数值，表示每个 P 可平均分到的 goroutine 数量。

然后根据函数参数中的 max 以及 P 本地队列的长度来决定把多少全局队列中的 goroutine 转移到 P 本地。

最后，for 循环挨个把全局队列中 n-1 个 goroutine 转移到本地，并且返回最开始获取到的队列头所指向的 goroutine，毕竟它最需要得到运行的机会。

把全局队列中的可运行 goroutine 转移到本地队列，给了全局队列中可运行 goroutine 运行的机会，不然全局队列中的 goroutine 一直得不到运行。

最后，我们继续看第三个过程，从其他 P “偷工作”：
```golang
// 从本地运行队列和全局运行队列都没有找到需要运行的 goroutine，
// 调用 findrunnable 函数从其它工作线程的运行队列中偷取，如果偷不到，则当前工作线程进入睡眠
// 直到获取到 runnable goroutine 之后 findrunnable 函数才会返回。
if gp == nil {
	gp, inheritTime = findrunnable() // blocks until work is available
}
```

这是整个找工作过程最复杂的部分：

```golang
// 从其他地方找 goroutine 来执行
func findrunnable() (gp *g, inheritTime bool) {
    _g_ := getg()

top:
    _p_ := _g_.m.p.ptr()

    // ……………………

    // local runq
    // 从本地队列获取
    if gp, inheritTime := runqget(_p_); gp != nil {
        return gp, inheritTime
    }

    // global runq
    // 从全局队列获取
    if sched.runqsize != 0 {
        lock(&sched.lock)
        gp := globrunqget(_p_, 0)
        unlock(&sched.lock)
        if gp != nil {
            return gp, false
        }
    }

    // ……………………

    // Steal work from other P's.

    // 如果其他的 P 都处于空闲状态，那肯定没有其他工作要做
    procs := uint32(gomaxprocs)
    if atomic.Load(&sched.npidle) == procs-1 {
        goto stop
    }

    // 如果有很多工作线程在找工作，那我就停下休息。避免消耗太多 CPU
    if !_g_.m.spinning && 2*atomic.Load(&sched.nmspinning) >= procs-atomic.Load(&sched.npidle) {
        goto stop
    }

    if !_g_.m.spinning {
        // 设置自旋状态为 true
        _g_.m.spinning = true
        // 自旋状态数加 1
        atomic.Xadd(&sched.nmspinning, 1)
    }
    // 从其它 p 的本地运行队列盗取 goroutine
    for i := 0; i < 4; i++ {
        for enum := stealOrder.start(fastrand()); !enum.done(); enum.next() {
            // ……………………
            stealRunNextG := i > 2 // first look for ready queues with more than 1 g
            if gp := runqsteal(_p_, allp[enum.position()], stealRunNextG); gp != nil {
                return gp, false
            }
        }
    }

stop:

    // ……………………

    // return P and block
    lock(&sched.lock)
    if sched.gcwaiting != 0 || _p_.runSafePointFn != 0 {
        unlock(&sched.lock)
        goto top
    }
    if sched.runqsize != 0 {
        gp := globrunqget(_p_, 0)
        unlock(&sched.lock)
        return gp, false
    }
    // 当前工作线程解除与 p 之间的绑定，准备去休眠
    if releasep() != _p_ {
        throw("findrunnable: wrong p")
    }
    // 把 p 放入空闲队列
    pidleput(_p_)
    unlock(&sched.lock)

    wasSpinning := _g_.m.spinning
    if _g_.m.spinning {
        // m 即将睡眠，不再处于自旋
        _g_.m.spinning = false
        if int32(atomic.Xadd(&sched.nmspinning, -1)) < 0 {
            throw("findrunnable: negative nmspinning")
        }
    }

    // check all runqueues once again
    // 休眠之前再检查一下所有的 p，看一下是否有工作要做
    for i := 0; i < int(gomaxprocs); i++ {
        _p_ := allp[i]
        if _p_ != nil && !runqempty(_p_) {
            lock(&sched.lock)
            _p_ = pidleget()
            unlock(&sched.lock)
            if _p_ != nil {
                acquirep(_p_)
                if wasSpinning {
                    _g_.m.spinning = true
                    atomic.Xadd(&sched.nmspinning, 1)
                }
                goto top
            }
            break
        }
    }

    // ……………………

    // 休眠
    stopm()
    goto top
}
```

这部分也是最能说明 M 找工作的锲而不舍精神：尽力去各个运行队列中寻找 goroutine，如果实在找不到则进入睡眠状态，等待有工作时，被其他 M 唤醒。

先获取当前指向的 g，也就是 g0，然后拿到其绑定的 p，即 `_p_`。

首先再次尝试从 `_p_` 本地队列获取 goroutine，如果没有获取到，则尝试从全局队列获取。如果还没有获取到就会尝试去“偷”了，这也是没有办法的事。

不过，在偷之前，先看大的局势。如果其他所有的 P 都处于空闲状态，就说明其他 P 肯定没有工作可做，就没必要再去偷了，毕竟“地主家也没有余粮了”，跳到 stop 部分。接着再看下当前正在“偷工作”的线程数量“太多了”，就没必要扎堆了，这么多人，竞争肯定大，工作肯定不好找，也不好偷。

在真正的“偷”工作之前，把自己的自旋状态设置为 true，全局自旋数量加 1。

终于到了“偷工作”的部分了，好紧张！整个过程由两层 for 循环组成，外层控制尝试偷的次数，内层控制“偷”的顺序，并真正的去“偷”。实际上，内层会遍历所有的 P，因此，整体看来，会尝试 4 次扫遍所有的 P，并去“偷工作”，是不是非常有毅力！

第二层的循环并不是每次都按一个固定的顺序去遍历所有的 P，这样不太科学，而是使用了一些方法，“随机”地遍历。具体是使用了下面这个变量：

```golang
var stealOrder randomOrder

type randomOrder struct {
	count    uint32
	coprimes []uint32
}
```

初始化的时候会给 count 赋一个值，例如 8，根据 count 计算出 coprimes，里面的元素是小于 count 的值，且和 8 互质，算出来是：[1, 3, 5, 7]。

第二层循环，开始随机给一个值，例如 2，则第一个访问的 P 就是 P2；从 coprimes 里取出索引为 2 的值为 5，那么，第二个访问的 P 索引就是 2+5=7；依此类推，第三个就是 7+5=12，和 count 做一个取余操作，即 12%8=4……

在最后一次遍历所有的 P 的过程中，连人家的 runnext 也要尝试偷过来，毕竟前三次的失败经验证明，工作太不好“偷”了，民不聊生啊，只能做得绝一点了，`stealRunNextG` 控制是否要打 runnext 的主意：

```golang
stealRunNextG := i > 2
```

确定好准备偷的对象 `allp[enum.position()` 之后，调用 `runqsteal(_p_, allp[enum.position()], stealRunNextG)` 函数执行。

```golang
// 从 p2 偷走一半的工作放到 _p_ 的本地
func runqsteal(_p_, p2 *p, stealRunNextG bool) *g {
    // 队尾
    t := _p_.runqtail
    // 从 p2 偷取工作，放到 _p_.runq 的队尾
    n := runqgrab(p2, &_p_.runq, t, stealRunNextG)
    if n == 0 {
        return nil
    }
    n--
    // 找到最后一个 g，准备返回
    gp := _p_.runq[(t+n)%uint32(len(_p_.runq))].ptr()
    if n == 0 {
        // 说明只偷了一个 g
        return gp
    }
    // 队列头
    h := atomic.Load(&_p_.runqhead) // load-acquire, synchronize with consumers
    // 判断是否偷太多了
    if t-h+n >= uint32(len(_p_.runq)) {
        throw("runqsteal: runq overflow")
    }
    // 更新队尾，将偷来的工作加入队列
    atomic.Store(&_p_.runqtail, t+n) // store-release, makes the item available for consumption
    return gp
}
```

调用 `runqgrab` 从 p2 偷走它一半的工作放到 `_p_` 本地：

```golang
n := runqgrab(p2, &_p_.runq, t, stealRunNextG)
```

`runqgrab` 函数将从 p2 偷来的工作放到以 t 为地址的数组里，数组就是 `_p_.runq`。 我们知道，`t` 是 `_p_.runq` 的队尾，因此这行代码表达的真正意思是将从 p2 偷来的工作，神不知，鬼不觉地放到 `_p_.runq` 的队尾，之后，再悄悄改一下 ``_p_.runqtail` 就把这些偷来的工作据为己有了。

接着往下看，返回的 n 表示偷到的工作数量。先将 n 自减 1，目的是把第 n 个工作（也就是 g）直接返回，如果这时候 n 变成 0 了，说明就只偷到了一个 g，那就直接返回。否则，将队尾往后移动 n，把偷来的工作合法化，简直完美！

我们接着往下看 `runqgrab` 函数的实现：

```golang
// 从 _p_ 批量获取可运行 goroutine，放到 batch 数组里
// batch 是一个环，起始于 batchHead
// 返回偷的数量，返回的 goroutine 可被任何 P 执行
func runqgrab(_p_ *p, batch *[256]guintptr, batchHead uint32, stealRunNextG bool) uint32 {
    for {
        // 队列头
        h := atomic.Load(&_p_.runqhead) // load-acquire, synchronize with other consumers
        // 队列尾
        t := atomic.Load(&_p_.runqtail) // load-acquire, synchronize with the producer
        // g 的数量
        n := t - h
        // 取一半
        n = n - n/2
        if n == 0 {
            if stealRunNextG {
                // 连 runnext 都要偷，没有人性
                // Try to steal from _p_.runnext.
                if next := _p_.runnext; next != 0 {
                    // 这里是为了防止 _p_ 执行当前 g，并且马上就要阻塞，所以会马上执行 runnext，
                    // 这个时候偷就没必要了，因为让 g 在 P 之间"游走"不太划算，
                    // 就不偷了，给他们一个机会。
                    // channel 一次同步的的接收发送需要 50ns 左右，因此 3us 差不多给了他们 50 次机会了，做得还是不错的
                    if GOOS != "windows" {
                        usleep(3)
                    } else {
                        osyield()
                    }
                    if !_p_.runnext.cas(next, 0) {
                        continue
                    }
                    // 真的偷走了 next
                    batch[batchHead%uint32(len(batch))] = next
                    // 返回偷的数量，只有 1 个
                    return 1
                }
            }
            // 没偷到
            return 0
        }
        // 如果 n 这时变得太大了，重新来一遍了，不能偷的太多，做得太过分了
        if n > uint32(len(_p_.runq)/2) { // read inconsistent h and t
            continue
        }
        // 将 g 放置到 bacth 中
        for i := uint32(0); i < n; i++ {
            g := _p_.runq[(h+i)%uint32(len(_p_.runq))]
            batch[(batchHead+i)%uint32(len(batch))] = g
        }
        // 工作被偷走了，更新一下队列头指针
        if atomic.Cas(&_p_.runqhead, h, h+n) { // cas-release, commits consume
            return n
        }
    }
}
```

外层直接就是一个无限循环，先用原子操作取出 p 的队列头和队列尾，算出一半的 g 的数量，如果 n == 0，说明地主家也没有余粮，这时看 `stealRunNextG` 的值。如果为假，说明不偷 runnext，那就直接返回 0，啥也没偷到；如果为真，则要尝试偷一下 runnext。

先判断 runnext 不为空，那就真的准备偷了。不过在这之前，要先休眠 3 us。这是为了防止 p 正在执行当前的 g，马上就要阻塞（可能是向一个非缓冲的 channel 发送数据，没有接收者），之后会马上执行 runnext。这个时候偷就没必要了，因为 runnext 马上就要执行了，偷走它还不是要去执行，那何必要偷呢？大家的愿望就是提高效率，这样让 g 在 P 之间"游走"不太划算，索性先不偷了，给他们一个机会。`channel` 一次同步的的接收或发送需要 50ns 左右，因此休眠 3us 差不多给了他们 50 次机会了，做得还是挺厚道的。

继续看，再次判断 n 是否小于等于 p.runq 长度的一半，因为这个时候很可能 p 也被其他线程偷了，它的 p.runq 就没那么多工作了，这个时候就不能偷这么多了，要重新再走一次循环。

最后一个 for 循环，将 p.runq 里的 g 放到 batch 数组里。使用原子操作更新 p 的队列头指针，往后移动 n 个位置，这些都是被偷走的，伤心！

回到 `findrunnable` 函数，经过上述三个层面的“偷窃”过程，我们仍然没有找到工作，真惨！于是就走到了 `stop` 这个代码块。

先上锁，因为要将 P 放到全局空闲 P 链表里去。在这之前还不死心，再瞧一下全局队列里是否有工作，如果有，再去尝试偷全局。

如果没有，就先解除当前工作线程和当前 P 的绑定关系：

```golang
// 解除 p 与 m 的关联
func releasep() *p {
	_g_ := getg()

	// ……………………

	_p_ := _g_.m.p.ptr()

	// ……………………

	// 清空一些字段
	_g_.m.p = 0
	_g_.m.mcache = nil
	_p_.m = 0
	_p_.status = _Pidle
	return _p_
}
```

主要的工作就是将 p 的 m 字段清空，并将 p 的状态修改为 `_Pidle`。

这之后，将其放入全局空闲 P 列表：

```golang
// 将 p 放到 _Pidle 列表里
//go:nowritebarrierrec
func pidleput(_p_ *p) {
	if !runqempty(_p_) {
		throw("pidleput: P has non-empty run queue")
	}
	_p_.link = sched.pidle
	sched.pidle.set(_p_)
	// 增加全局空闲 P 的数量
	atomic.Xadd(&sched.npidle, 1) // TODO: fast atomic
}
```

构造链表的过程其实比较简单，先将 p.link 指向原来的 sched.pidle 所指向的 p，也就是原空闲链表的最后一个 P，最后，再更新 sched.pidle，使其指向当前 p，这样，新的链表就构造完成。

接下来就要真正地准备休眠了，但是仍然不死心！还要再查看一次所有的 P 是否有工作，如果发现任何一个 P 有工作的话（判断 P 的本地队列不空），就先从全局空闲 P 链表里先拿到一个 P：

```golang
// 试图从 _Pidle 列表里获取 p
//go:nowritebarrierrec
func pidleget() *p {
	_p_ := sched.pidle.ptr()
	if _p_ != nil {
		sched.pidle = _p_.link
		atomic.Xadd(&sched.npidle, -1) // TODO: fast atomic
	}
	return _p_
}
```

比较简单，获取链表最后一个，再更新 sched.pidle，使其指向前一个 P。调用 `acquirep(_p_)` 绑定获取到的 p 和 m，主要的动作就是设置 p 的 m 字段，更改 p 的工作状态为 `_Prunning`，并且设置 m 的 p 字段。做完这些之后，再次进入 top 代码段，再走一遍之前找工作的过程。

```golang
// 休眠，停止执行工作，直到有新的工作需要做为止
func stopm() {
	// 当前 goroutine，g0
	_g_ := getg()

	// ……………………
retry:
	lock(&sched.lock)
	// 将 m 放到全局空闲链表里去
	mput(_g_.m)
	unlock(&sched.lock)
	// 进入睡眠状态
	notesleep(&_g_.m.park)
	// 这里被其他工作线程唤醒
	noteclear(&_g_.m.park)

	// ……………………

	acquirep(_g_.m.nextp.ptr())
	_g_.m.nextp = 0
}
```

先将 m 放入全局空闲链表里，注意涉及到全局变量的修改，要上锁。接着，调用 `notesleep(&_g_.m.park)` 使得当前工作线程进入休眠状态。其他工作线程在检测到“当前有很多工作要做”，会调用 `noteclear(&_g_.m.park)` 将其唤醒。注意，这两个函数传入的参数都是一样的：`&_g_.m.park`，它的类型是：

```golang
type note struct {
	key uintptr
}
```

很简单，只有一个 key 字段。

> note 的底层实现机制跟操作系统相关，不同系统使用不同的机制，比如 linux 下使用的 futex 系统调用，而 mac 下则是使用的 pthread_cond_t 条件变量，note 对这些底层机制做了一个抽象和封装。

> 这种封装给扩展性带来了很大的好处，比如当睡眠和唤醒功能需要支持新平台时，只需要在 note 层增加对特定平台的支持即可，不需要修改上层的任何代码。

上面这一段来自阿波张的系列教程。我们接着来看下 notesleep 的实现：

```golang
// runtime/lock_futex.go
func notesleep(n *note) {
	// g0
	gp := getg()
	if gp != gp.m.g0 {
		throw("notesleep not on g0")
	}
	// -1 表示无限期休眠
	ns := int64(-1)

	// ……………………

	// 这里之所以需要用一个循环，是因为 futexsleep 有可能意外从睡眠中返回，
	// 所以 futexsleep 函数返回后还需要检查 note.key 是否还是 0，
	// 如果是 0 则表示并不是其它工作线程唤醒了我们，
	// 只是 futexsleep 意外返回了，需要再次调用 futexsleep 进入睡眠
	for atomic.Load(key32(&n.key)) == 0 {
		// 表示 m 被阻塞
		gp.m.blocked = true
		futexsleep(key32(&n.key), 0, ns)

		// ……………………

		// 被唤醒，更新标志
		gp.m.blocked = false
	}
}
```

继续往下追：

```golang
// runtime/os_linux.go
func futexsleep(addr *uint32, val uint32, ns int64) {
	var ts timespec

	if ns < 0 {
		futex(unsafe.Pointer(addr), _FUTEX_WAIT, val, nil, nil, 0)
		return
	}

	// ……………………
}
```

当 *addr 和 val 相等的时候，休眠。`futex` 由汇编语言实现：

```asm
TEXT runtime·futex(SB),NOSPLIT,$0
    // 为系统调用准备参数
	MOVQ	addr+0(FP), DI
	MOVL	op+8(FP), SI
	MOVL	val+12(FP), DX
	MOVQ	ts+16(FP), R10
	MOVQ	addr2+24(FP), R8
	MOVL	val3+32(FP), R9
	// 系统调用编号
	MOVL	$202, AX
	// 执行 futex 系统调用进入休眠，被唤醒后接着执行下一条 MOVL 指令
	SYSCALL
	// 保存系统调用的返回值
	MOVL	AX, ret+40(FP)
	RET
```

这样，找不到工作的 m 就休眠了。当其他线程发现有工作要做时，就会先找到空闲的 m，再通过 m.park 字段来唤醒本线程。唤醒之后，回到 `findrunnable` 函数，继续寻找 goroutine，找到后返回 schedule 函数，然后就会去运行找到的 goroutine。

这就是 m 找工作的整个过程，历尽千辛万苦，终于修成正果。

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/sched/13-M%20%E5%A6%82%E4%BD%95%E6%89%BE%E5%B7%A5%E4%BD%9C.md#L3)，来源许可：GPL-3.0。

<a id="k5dab091d9dd6"></a>

## schedule 循环如何启动

上一讲新创建了一个 goroutine，设置好了 sched 成员的 sp 和 pc 字段，并且将其添加到了 p0 的本地可运行队列，坐等调度器的调度。

我们继续看代码。搞了半天，我们其实还在 `runtime·rt0_go` 函数里，执行完 `runtime·newproc(SB)` 后，两条 POP 指令将之前为调用它构建的参数弹出栈。好消息是，最后就只剩下一个函数了：

```golang
// start this M
// 主线程进入调度循环，运行刚刚创建的 goroutine
CALL	runtime·mstart(SB)
```

这到达了本系列的核心区，前面铺垫了半天，调度器终于要开始运转了。

`mstart` 函数设置了 stackguard0 和 stackguard1 字段后，就直接调用 mstart1() 函数：

```golang
func mstart1() {
    // 启动过程时 _g_ = m0.g0
    _g_ := getg()

    if _g_ != _g_.m.g0 {
        throw("bad runtime·mstart")
    }

    // Record top of stack for use by mcall.
    // Once we call schedule we're never coming back,
    // so other calls can reuse this stack space.
    // 
    // 一旦调用 schedule() 函数，永不返回
    // 所以栈帧可以被复用
    gosave(&_g_.m.g0.sched)
    _g_.m.g0.sched.pc = ^uintptr(0) // make sure it is never used
    asminit()
    minit()

    // ……………………

    // 执行启动函数。初始化过程中，fn == nil
    if fn := _g_.m.mstartfn; fn != nil {
        fn()
    }

    if _g_.m.helpgc != 0 {
        _g_.m.helpgc = 0
        stopm()
    } else if _g_.m != &m0 {
        acquirep(_g_.m.nextp.ptr())
        _g_.m.nextp = 0
    }

    // 进入调度循环。永不返回
    schedule()
}
```

调用 `gosave` 函数来保存调度信息到 `g0.sched` 结构体，来看源码：

```golang
// void gosave(Gobuf*)
// save state in Gobuf; setjmp
TEXT runtime·gosave(SB), NOSPLIT, $0-8
    // 将 gobuf 赋值给 AX
    MOVQ    buf+0(FP), AX       // gobuf
    // 取参数地址，也就是 caller 的 SP
    LEAQ    buf+0(FP), BX       // caller's SP
    // 保存 caller's SP，再次运行时的栈顶
    MOVQ    BX, gobuf_sp(AX)
    MOVQ    0(SP), BX       // caller's PC
    // 保存 caller's PC，再次运行时的指令地址
    MOVQ    BX, gobuf_pc(AX)
    MOVQ    $0, gobuf_ret(AX)
    MOVQ    BP, gobuf_bp(AX)
    // Assert ctxt is zero. See func save.
    MOVQ    gobuf_ctxt(AX), BX
    TESTQ   BX, BX
    JZ  2(PC)
    CALL    runtime·badctxt(SB)
    // 获取 tls
    get_tls(CX)
    // 将 g 的地址存入 BX
    MOVQ    g(CX), BX
    // 保存 g 的地址
    MOVQ    BX, gobuf_g(AX)
    RET
```

主要是设置了 g0.sched.sp 和 g0.sched.pc，前者指向 mstart1 函数栈上参数的位置，后者则指向 gosave 函数返回后的下一条指令。如下图：

![调用 gosave 函数后](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/sched/assets/0.png)

图中 sched.pc 并不直接指向返回地址，所以图中的虚线并没有箭头。

接下来，进入 schedule 函数，永不返回。

```golang
// 执行一轮调度器的工作：找到一个 runnable 的 goroutine，并且执行它
// 永不返回
func schedule() {
    // _g_ = 每个工作线程 m 对应的 g0，初始化时是 m0 的 g0
    _g_ := getg()

    // ……………………

top:
    // ……………………

    var gp *g
    var inheritTime bool

    // ……………………

    if gp == nil {
        // Check the global runnable queue once in a while to ensure fairness.
        // Otherwise two goroutines can completely occupy the local runqueue
        // by constantly respawning each other.
        // 为了公平，每调用 schedule 函数 61 次就要从全局可运行 goroutine 队列中获取
        if _g_.m.p.ptr().schedtick%61 == 0 && sched.runqsize > 0 {
            lock(&sched.lock)
            // 从全局队列最大获取 1 个 goroutine
            gp = globrunqget(_g_.m.p.ptr(), 1)
            unlock(&sched.lock)
        }
    }

    // 从 P 本地获取 G 任务
    if gp == nil {
        gp, inheritTime = runqget(_g_.m.p.ptr())
        if gp != nil && _g_.m.spinning {
            throw("schedule: spinning with local work")
        }
    }

    if gp == nil {
        // 从本地运行队列和全局运行队列都没有找到需要运行的 goroutine，
        // 调用 findrunnable 函数从其它工作线程的运行队列中偷取，如果偷不到，则当前工作线程进入睡眠
        // 直到获取到 runnable goroutine 之后 findrunnable 函数才会返回。
        gp, inheritTime = findrunnable() // blocks until work is available
    }

    // This thread is going to run a goroutine and is not spinning anymore,
    // so if it was marked as spinning we need to reset it now and potentially
    // start a new spinning M.
    if _g_.m.spinning {
        resetspinning()
    }

    if gp.lockedm != nil {
        // Hands off own p to the locked m,
        // then blocks waiting for a new p.
        startlockedm(gp)
        goto top
    }

    // 执行 goroutine 任务函数
    // 当前运行的是 runtime 的代码，函数调用栈使用的是 g0 的栈空间
    // 调用 execute 切换到 gp 的代码和栈空间去运行
    execute(gp, inheritTime)
}
```

调用 `runqget`，从 P 本地可运行队列先选出一个可运行的 goroutine；为了公平，调度器每调度 61 次的时候，都会尝试从全局队列里取出待运行的 goroutine 来运行，调用 `globrunqget`；如果还没找到，就要去其他 P 里面去偷一些 goroutine 来执行，调用 `findrunnable` 函数。

经过千辛万苦，终于找到了可以运行的 goroutine，调用 `execute(gp, inheritTime)` 切换到选出的 goroutine 栈执行，调度器的调度次数会在这里更新，源码如下：

```golang
// 调度 gp 在当前 M 上运行
// 如果 inheritTime 为真，gp 执行当前的时间片
// 否则，开启一个新的时间片
// 
//go:yeswritebarrierrec 
func execute(gp *g, inheritTime bool) {
    // g0
    _g_ := getg()

    // 将 gp 的状态改为 running
    casgstatus(gp, _Grunnable, _Grunning)
    gp.waitsince = 0
    gp.preempt = false
    gp.stackguard0 = gp.stack.lo + _StackGuard
    if !inheritTime {
        // 调度器调度次数增加 1
        _g_.m.p.ptr().schedtick++
    }

    // 将 gp 和 m 关联起来
    _g_.m.curg = gp
    gp.m = _g_.m

    // …………………………

    // gogo 完成从 g0 到 gp 真正的切换
    // CPU 执行权的转让以及栈的切换
    // 执行流的切换从本质上来说就是 CPU 寄存器以及函数调用栈的切换，
    // 然而不管是 go 还是 c 这种高级语言都无法精确控制 CPU 寄存器的修改，
    // 因而高级语言在这里也就无能为力了，只能依靠汇编指令来达成目的
    gogo(&gp.sched)
}
```

将 gp 的状态改为 `_Grunning`，将 m 和 gp 相互关联起来。最后，调用 `gogo` 完成从 g0 到 gp 的切换，CPU 的执行权将从 g0 转让到 gp。 `gogo` 函数用汇编语言写成，原因如下：

> `gogo` 函数也是通过汇编语言编写的，这里之所以需要使用汇编，是因为 goroutine 的调度涉及不同执行流之间的切换。

> 前面我们在讨论操作系统切换线程时已经看到过，执行流的切换从本质上来说就是 CPU 寄存器以及函数调用栈的切换，然而不管是 go 还是 c 这种高级语言都无法精确控制 CPU 寄存器，因而高级语言在这里也就无能为力了，只能依靠汇编指令来达成目的。

继续看 `gogo` 函数的实现，传入 `&gp.sched` 参数，源码如下：

```golang
TEXT runtime·gogo(SB), NOSPLIT, $16-8
    // 0(FP) 表示第一个参数，即 buf = &gp.sched
    MOVQ    buf+0(FP), BX       // gobuf

    // ……………………

    MOVQ    buf+0(FP), BX

nilctxt:
    // DX = gp.sched.g
    MOVQ    gobuf_g(BX), DX
    MOVQ    0(DX), CX       // make sure g != nil
    get_tls(CX)
    // 将 g 放入到 tls[0]
    // 把要运行的 g 的指针放入线程本地存储，这样后面的代码就可以通过线程本地存储
    // 获取到当前正在执行的 goroutine 的 g 结构体对象，从而找到与之关联的 m 和 p
    // 运行这条指令之前，线程本地存储存放的是 g0 的地址
    MOVQ    DX, g(CX)
    // 把 CPU 的 SP 寄存器设置为 sched.sp，完成了栈的切换
    MOVQ    gobuf_sp(BX), SP    // restore SP
    // 恢复调度上下文到CPU相关寄存器
    MOVQ    gobuf_ret(BX), AX
    MOVQ    gobuf_ctxt(BX), DX
    MOVQ    gobuf_bp(BX), BP
    // 清空 sched 的值，因为我们已把相关值放入 CPU 对应的寄存器了，不再需要，这样做可以少 GC 的工作量
    MOVQ    $0, gobuf_sp(BX)    // clear to help garbage collector
    MOVQ    $0, gobuf_ret(BX)
    MOVQ    $0, gobuf_ctxt(BX)
    MOVQ    $0, gobuf_bp(BX)
    // 把 sched.pc 值放入 BX 寄存器
    MOVQ    gobuf_pc(BX), BX
    // JMP 把 BX 寄存器的包含的地址值放入 CPU 的 IP 寄存器，于是，CPU 跳转到该地址继续执行指令
    JMP BX
```

注释地比较详细了。核心的地方是：

```golang
MOVQ    gobuf_g(BX), DX
// ……
get_tls(CX)
MOVQ    DX, g(CX)
```

第一行，将 gp.sched.g 保存到 DX 寄存器；第二行，我们见得已经比较多了，`get_tls` 将 tls 保存到 CX 寄存器，再将 gp.sched.g 放到 tls[0] 处。这样，当下次再调用 `get_tls` 时，取出的就是 gp，而不再是 g0，这一行完成从 g0 栈切换到 gp。

可能需要提一下的是，Go plan9 汇编中的一些奇怪的符号：

```golang
MOVQ    buf+0(FP), BX  # &gp.sched --> BX
```

`FP` 是个伪奇存器，前面加 0 表示是第一个寄存器，表示参数的位置，最前面的 buf 表示一个符号。关于 Go 汇编语言的一些知识，可以参考曹大在夜读上的分享和《Go 语言高级编程》的相关章节，地址见参考资料。

接下来，将 gp.sched 的相关成员恢复到 CPU 对应的寄存器。最重要的是 sched.sp 和 sched.pc，前者被恢复到了 SP 寄存器，后者被保存到 BX 寄存器，最后一条跳转指令跳转到新的地址开始执行。通过之前的文章，我们知道，这里保存的就是 `runtime.main` 函数的地址。

最终，调度器完成了这个值得铭记的时刻，从 g0 转到 gp，开始执行 `runtime.main` 函数。

用一张流程图总结一下从 g0 切换到 main goroutine 的过程：

![从 g0 到 gp](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/sched/assets/1.png)

### 参考资料
【欧神 调度循环】https://github.com/changkun/go-under-the-hood/blob/master/book/zh-cn/part2runtime/ch06sched/exec.md

【go 语言核心编程技术 调度器系列】https://mp.weixin.qq.com/s/8eJm5hjwKXya85VnT4y8Cw

【曹大 Go plan9 汇编】https://github.com/cch123/asmshare/blob/master/layout.md

【Go 语言高级编程】https://chai2010.cn/advanced-go-programming-book/ch3-asm/readme.html

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/sched/10-schedule%20%E5%BE%AA%E7%8E%AF%E5%A6%82%E4%BD%95%E5%90%AF%E5%8A%A8.md#L3)，来源许可：GPL-3.0。

<a id="k642c237f9eb9"></a>

## schedule 循环如何运转

上一节，我们讲完 main goroutine 以及普通 goroutine 的退出过程。main goroutine 退出后直接调用 exit(0) 使得整个进程退出，而普通 goroutine 退出后，则进行了一系列的调用，最终又切到 g0 栈，执行 schedule 函数。

从前面的文章我们知道，普通 goroutine（gp）就是在 schedule 函数中被选中，然后才有机会执行。而现在，gp 执行完之后，再次进入 schedule 函数，形成一个循环。这个循环太长了，我们有必要再重新梳理一下。

![调度循环](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/sched/assets/3.png)

如图所示，rt0_go 负责 Go 程序启动的所有初始化，中间进行了很多初始化工作，调用 mstart 之前，已经切换到了 g0 栈，图中不同色块表示使用不同的栈空间。

接着调用 gogo 函数，完成从 g0 栈到用户 goroutine 栈的切换，包括 main goroutine 和普通 goroutine。

之后，执行 main 函数或者用户自定义的 goroutine 任务。

执行完成后，main goroutine 直接调用 eixt(0) 退出，普通 goroutine 则调用 goexit -> goexit1 -> mcall，完成普通 goroutine 退出后的清理工作，然后切换到 g0 栈，调用 goexit0 函数，将普通 goroutine 添加到缓存池中，再调用 schedule 函数进行新一轮的调度。

```shell
schedule() -> execute() -> gogo() -> goroutine 任务 -> goexit() -> goexit1() -> mcall() -> goexit0() -> schedule()
```

> 可以看出，一轮调度从调用 schedule 函数开始，经过一系列过程再次调用 schedule 函数来进行新一轮的调度，从一轮调度到新一轮调度的过程称之为一个调度循环。

> 这里说的调度循环是指某一个工作线程的调度循环，而同一个Go 程序中存在多个工作线程，每个工作线程都在进行着自己的调度循环。

> 从前面的代码分析可以得知，上面调度循环中的每一个函数调用都没有返回，虽然 `goroutine 任务-> goexit() -> goexit1() -> mcall()` 是在 g2 的栈空间执行的，但剩下的函数都是在 g0 的栈空间执行的。

> 那么问题就来了，在一个复杂的程序中，调度可能会进行无数次循环，也就是说会进行无数次没有返回的函数调用，大家都知道，每调用一次函数都会消耗一定的栈空间，而如果一直这样无返回的调用下去无论 g0 有多少栈空间终究是会耗尽的，那么这里是不是有问题？其实没有问题！关键点就在于，每次执行 mcall 切换到 g0 栈时都是切换到 g0.sched.sp 所指的固定位置，这之所以行得通，正是因为从 schedule 函数开始之后的一系列函数永远都不会返回，所以重用这些函数上一轮调度时所使用过的栈内存是没有问题的。

我再解释一下：栈空间在调用函数时会自动“增大”，而函数返回时，会自动“减小”，这里的增大和减小是指栈顶指针 SP 的变化。上述这些函数都没有返回，说明调用者不需要用到被调用者的返回值，有点像“尾递归”。

因为 g0 一直没有动过，所有它之前保存的 sp 还能继续使用。每一次调度循环都会覆盖上一次调度循环的栈数据，完美！

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/sched/12-schedule%20%E5%BE%AA%E7%8E%AF%E5%A6%82%E4%BD%95%E8%BF%90%E8%BD%AC.md#L3)，来源许可：GPL-3.0。

<a id="kbe876544a369"></a>

## 为什么要 scheduler

Go scheduler 可以说是 Go 运行时的一个最重要的部分了。Runtime 维护所有的 goroutines，并通过 scheduler 来进行调度。Goroutines 和 threads 是独立的，但是 goroutines 要依赖 threads 才能执行。

Go 程序执行的高效和 scheduler 的调度是分不开的。

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/sched/2-%E4%BB%80%E4%B9%88%E6%98%AF%20go%20scheduler.md#L14)，来源许可：GPL-3.0。

<a id="k0657791a1d7f"></a>

## 交流和勘误

我们在这里维护了一份已出版内容的[勘误表](https://golang.design/go-questions/errata/)，以帮助并消除读者在阅读过程中出现的困惑。
读者还可以本书的 [GitHub 仓库](https://github.com/golang-design/go-questions)
里讨论关于本书内容的问题，或报告并提交本书存在的错误。

我们欢迎你在 GitHub 仓库上发起 [Issues](https://github.com/golang-design/go-questions/issues/new/choose) 或提交 [Pull Request](https://github.com/golang-design/go-questions/compare)。

我们也欢迎你关注 “码农桃花源” 的公众号，和更多的人一起学习：

<img src="content/assets/qrcode.jpg" alt="logo" height="350" style="margin: 5px; margin-bottom: 20px;" />

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/README.md#L39)，来源许可：GPL-3.0。

<a id="k5f77c7fcc995"></a>

## 什么是 scheduler

Go 程序的执行由两层组成：Go Program，Runtime，即用户程序和运行时。它们之间通过函数调用来实现内存管理、channel 通信、goroutines 创建等功能。用户程序进行的系统调用都会被 Runtime 拦截，以此来帮助它进行调度以及垃圾回收相关的工作。

一个展现了全景式的关系如下图：

![runtime overall](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/sched/assets/5.png)

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/sched/2-%E4%BB%80%E4%B9%88%E6%98%AF%20go%20scheduler.md#L7)，来源许可：GPL-3.0。

<a id="k9d9fec070bcd"></a>

## 什么是M:N模型

我们都知道，Go runtime 会负责 goroutine 的生老病死，从创建到销毁，都一手包办。Runtime 会在程序启动的时候，创建 M 个线程（CPU 执行调度的单位），之后创建的 N 个 goroutine 都会依附在这 M 个线程上执行。这就是 M:N 模型：

![M:N scheduling](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/sched/assets/11.png)

在同一时刻，一个线程上只能跑一个 goroutine。当 goroutine 发生阻塞（例如上篇文章提到的向一个 channel 发送数据，被阻塞）时，runtime 会把当前 goroutine 调度走，让其他 goroutine 来执行。目的就是不让一个线程闲着，榨干 CPU 的每一滴油水。

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/sched/4-%E4%BB%80%E4%B9%88%E6%98%AFM%3AN%E6%A8%A1%E5%9E%8B.md#L3)，来源许可：GPL-3.0。

<a id="k600c617b15d0"></a>

## 什么是工作窃取

Go scheduler 的职责就是将所有处于 runnable 的 goroutines 均匀分布到在 P 上运行的 M。

当一个 P 发现自己的 LRQ 已经没有 G 时，会从其他 P “偷” 一些 G 来运行。看看这是什么精神！自己的工作做完了，为了全局的利益，主动为别人分担。这被称为 `Work-stealing`，Go 从 1.1 开始实现。

Go scheduler 使用 M:N 模型，在任一时刻，M 个 goroutines（G） 要分配到 N 个内核线程（M），这些 M 跑在个数最多为 GOMAXPROCS 的逻辑处理器（P）上。每个 M 必须依附于一个 P，每个 P 在同一时刻只能运行一个 M。如果 P 上的 M 阻塞了，那它就需要其他的 M 来运行 P 的 LRQ 里的 goroutines。

![GPM relatioship](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/sched/assets/12.png)

个人感觉，上面这张图比常见的那些用三角形表示 M，圆形表示 G，矩形表示 P 的那些图更生动形象。

实际上，Go scheduler 每一轮调度要做的工作就是找到处于 runnable 的 goroutines，并执行它。找的顺序如下：

```golang
runtime.schedule() {
    // only 1/61 of the time, check the global runnable queue for a G.
    // if not found, check the local queue.
    // if not found,
    //     try to steal from other Ps.
    //     if not, check the global runnable queue.
    //     if not found, poll network.
}
```

找到一个可执行的 goroutine 后，就会一直执行下去，直到被阻塞。

当 P2 上的一个 G 执行结束，它就会去 LRQ 获取下一个 G 来执行。如果 LRQ 已经空了，就是说本地可运行队列已经没有 G 需要执行，并且这时 GRQ 也没有 G 了。这时，P2 会随机选择一个 P（称为 P1），P2 会从 P1 的 LRQ “偷”过来一半的 G。

![Work Stealing](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/sched/assets/13.png)

这样做的好处是，有更多的 P 可以一起工作，加速执行完所有的 G。

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/sched/5-%E4%BB%80%E4%B9%88%E6%98%AFworkstealing.md#L3)，来源许可：GPL-3.0。

<a id="ke0dfb203b636"></a>

## 初始化 allp

跳过一些其他的初始化代码，继续往后看：

```golang
procs := ncpu
if n, ok := atoi32(gogetenv("GOMAXPROCS")); ok && n > 0 {
	procs = n
}
if procs > _MaxGomaxprocs {
	procs = _MaxGomaxprocs
}
```

这里就是设置 procs，它决定创建 P 的数量。ncpu 这里已经被赋上了系统的核心数，因此代码里不设置 GOMAXPROCS 也是没问题的。这里还限制了 procs 的最大值，为 1024。

来看最后一个核心的函数：

```golang
// src/runtime/proc.go

func procresize(nprocs int32) *p {
	old := gomaxprocs
	if old < 0 || old > _MaxGomaxprocs || nprocs <= 0 || nprocs > _MaxGomaxprocs {
		throw("procresize: invalid arg")
	}

	// ……………………

	// update statistics
	// 更新数据
	now := nanotime()
	if sched.procresizetime != 0 {
		sched.totaltime += int64(old) * (now - sched.procresizetime)
	}
	sched.procresizetime = now

	// 初始化所有的 P
	for i := int32(0); i < nprocs; i++ {
		pp := allp[i]
		if pp == nil {
			// 申请新对象
			pp = new(p)
			pp.id = i
			// pp 的初始状态为 stop
			pp.status = _Pgcstop
			pp.sudogcache = pp.sudogbuf[:0]
			for i := range pp.deferpool {
				pp.deferpool[i] = pp.deferpoolbuf[i][:0]
			}
			// 将 pp 存放到 allp 处
			atomicstorep(unsafe.Pointer(&allp[i]), unsafe.Pointer(pp))
		}

		// ……………………

	}

	// 释放多余的 P。由于减少了旧的 procs 的数量，因此需要释放
	// ……………………

	// 获取当前正在运行的 g 指针，初始化时 _g_ = g0
	_g_ := getg()
	if _g_.m.p != 0 && _g_.m.p.ptr().id < nprocs {
		// continue to use the current P
		// 继续使用当前 P
		_g_.m.p.ptr().status = _Prunning
	} else {
		// 初始化时执行这个分支

		// ……………………

		_g_.m.p = 0
		_g_.m.mcache = nil
		// 取出第 0 号 p
		p := allp[0]
		p.m = 0
		p.status = _Pidle
		// 将 p0 和 m0 关联起来
		acquirep(p)
		if trace.enabled {
			traceGoStart()
		}
	}
	var runnablePs *p
	// 下面这个 for 循环把所有空闲的 p 放入空闲链表
	for i := nprocs - 1; i >= 0; i-- {
		p := allp[i]
		// allp[0] 跟 m0 关联了，不会进行之后的“放入空闲链表”
		if _g_.m.p.ptr() == p {
			continue
		}

		// 状态转为 idle
		p.status = _Pidle
		// p 的 LRQ 里没有 G
		if runqempty(p) {
			// 放入全局空闲链表
			pidleput(p)
		} else {
			p.m.set(mget())
			p.link.set(runnablePs)
			runnablePs = p
		}
	}
	stealOrder.reset(uint32(nprocs))
	var int32p *int32 = &gomaxprocs // make compiler check that gomaxprocs is an int32
	atomic.Store((*uint32)(unsafe.Pointer(int32p)), uint32(nprocs))
	// 返回有本地任务的 P 链表
	return runnablePs
}

```

代码比较长，这个函数不仅是初始化的时候会执行到，在中途改变 procs 的值的时候，仍然会调用它。所有存在很多一般不用关心的代码，因为一般不会在中途重新设置 procs 的值。我把初始化无关的代码删掉了，这样会更清晰一些。

函数先是从堆上创建了 nproc 个 P，并且把 P 的状态设置为 `_Pgcstop`，现在全局变量 allp 里就维护了所有的 P。

接着，调用函数 `acquirep` 将 p0 和 m0 关联起来。我们来详细看一下：

```golang
func acquirep(_p_ *p) {
	// Do the part that isn't allowed to have write barriers.
	acquirep1(_p_)

	// have p; write barriers now allowed
	_g_ := getg()
	_g_.m.mcache = _p_.mcache

	// ……………………
}
```

先调用 `acquirep1` 函数真正地进行关联，之后，将 p0 的 mcache 资源赋给 m0。再来看 `acquirep1`：

```golang
func acquirep1(_p_ *p) {
	_g_ := getg()

	// ……………………

	_g_.m.p.set(_p_)
	_p_.m.set(_g_.m)
	_p_.status = _Prunning
}
```

可以看到就是一些字段相互设置，执行完成后：

```golang
g0.m.p = p0
p0.m = m0
```

并且，p0 的状态变成了 `_Prunning`。

接下来是一个循环，它将除了 p0 的所有非空闲的 P，放入 P 链表 runnablePs，并返回给 procresize 函数的调用者，并由调用者来“调度”这些 P。

函数 `runqempty` 用来判断一个 P 是否是空闲，依据是 P 的本地 run queue 队列里有没有 runnable 的 G，如果没有，那 P 就是空闲的。

```golang
// src/runtime/proc.go

// 如果 _p_ 的本地队列里没有待运行的 G，则返回 true
func runqempty(_p_ *p) bool {
	// 这里涉及到一些数据竞争，并不是简单地判断 runqhead == runqtail 并且 runqnext == nil 就可以
	//
	for {
		head := atomic.Load(&_p_.runqhead)
		tail := atomic.Load(&_p_.runqtail)
		runnext := atomic.Loaduintptr((*uintptr)(unsafe.Pointer(&_p_.runnext)))
		if tail == atomic.Load(&_p_.runqtail) {
			return head == tail && runnext == 0
		}
	}
}
```

并不是简单地判断 head == tail 并且 runnext == nil 为真，就可以说明 runq 是空的。因为涉及到一些数据竞争，例如在比较 head == tail 时为真，但此时 runnext 上其实有一个 G，之后再去比较 runnext == nil 的时候，这个 G 又通过 runqput跑到了 runq 里去了或者通过 runqget 拿走了，runnext 也为真，于是函数就判断这个 P 是空闲的，这就会形成误判。

因此 runqempty 函数先是通过原子操作取出了 head，tail，runnext，然后再次确认 tail 没有发生变化，最后再比较 head == tail 以及 runnext == nil，保证了在观察三者都是在“同时”观察到的，因此，返回的结果就是正确的。

说明一下，runnext 上有时会绑定一个 G，这个 G 是被当前 G 唤醒的，相比其他 G 有更高的执行优先级，因此把它单独拿出来。 

函数的最后，初始化了一个“随机分配器”：

```golang
stealOrder.reset(uint32(nprocs))
```

将来有些 m 去偷工作的时候，会遍历所有的 P，这时为了偷地随机一些，就会用到 stealOrder 来返回一个随机选择的 P，后面的文章会再讲。

这样，整个 procresize 函数就讲完了，这也意味着，调度器的初始化工作已经完成了。

还是引用阿波张公号文章里的总结，写得太好了，很简洁，很难再优化了：

> 1. 使用 make([]*p, nprocs) 初始化全局变量 allp，即 allp = make([]*p, nprocs)

> 2. 循环创建并初始化 nprocs 个 p 结构体对象并依次保存在 allp 切片之中

> 3. 把 m0 和 allp[0] 绑定在一起，即 m0.p = allp[0]，allp[0].m = m0

> 4. 把除了 allp[0] 之外的所有 p 放入到全局变量 sched 的 pidle 空闲队列之中

说明一下，最后一步，代码里是将所有空闲的 P 放入到调度器的全局空闲队列；对于非空闲的 P（本地队列里有 G 待执行），则是生成一个 P 链表，返回给 procresize 函数的调用者。

最后我们将 allp 和 allm 都添加到图上：

![g0-p0-m0](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/sched/assets/24.png)

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/sched/7-%E6%8F%8F%E8%BF%B0%20scheduler%20%E7%9A%84%E5%88%9D%E5%A7%8B%E5%8C%96%E8%BF%87%E7%A8%8B.md#L649)，来源许可：GPL-3.0。

<a id="k5593758cbf03"></a>

## 初始化 m0

```golang
MOVL	16(SP), AX		// copy argc
MOVL	AX, 0(SP)
MOVQ	24(SP), AX		// copy argv
MOVQ	AX, 8(SP)
CALL	runtime·args(SB)
// 初始化系统核心数
CALL	runtime·osinit(SB)
// 调度器初始化
CALL	runtime·schedinit(SB)
```

L1-L2 将 16(SP) 处的内容移动到 0(SP)，也就是栈顶，通过前面的图，16(SP) 处的内容为 argc；L3-L4 将 argv 存入 8(SP)，接下来调用 `runtime·args` 函数，处理命令行参数。

接着，连续调用了两个 runtime 函数。osinit 函数初始化系统核心数，将全局变量 ncpu 初始化的核心数，schedinit 则是本文的核心：调度器的初始化。

下面，我们来重点看 schedinit 函数：

```golang
// src/runtime/proc.go

// The bootstrap sequence is:
//
//	call osinit
//	call schedinit
//	make & queue new G
//	call runtime·mstart
//
// The new G calls runtime·main.
func schedinit() {
	// getg 由编译器实现
	// get_tls(CX)
	// MOVQ g(CX), BX; BX存器里面现在放的是当前g结构体对象的地址
	_g_ := getg()
	if raceenabled {
		_g_.racectx, raceprocctx0 = raceinit()
	}

	// 最多启动 10000 个工作线程
	sched.maxmcount = 10000

	tracebackinit()
	moduledataverify()

	// 初始化栈空间复用管理链表
	stackinit()
	mallocinit()

	// 初始化 m0
	mcommoninit(_g_.m)
	alginit()       // maps must not be used before this call
	modulesinit()   // provides activeModules
	typelinksinit() // uses maps, activeModules
	itabsinit()     // uses activeModules

	msigsave(_g_.m)
	initSigmask = _g_.m.sigmask

	goargs()
	goenvs()
	parsedebugvars()
	gcinit()

	sched.lastpoll = uint64(nanotime())

	// 初始化 P 的个数
	// 系统中有多少核，就创建和初始化多少个 p 结构体对象
	procs := ncpu
	if n, ok := atoi32(gogetenv("GOMAXPROCS")); ok && n > 0 {
		procs = n
	}
	if procs > _MaxGomaxprocs {
		procs = _MaxGomaxprocs
	}

	// 初始化所有的 P，正常情况下不会返回有本地任务的 P
	if procresize(procs) != nil {
		throw("unknown runnable goroutine during bootstrap")
	}

	// ……………………
}
```

这个函数开头的注释很贴心地把 Go 程序初始化的过程又说了一遍：

1. call osinit。初始化系统核心数。
2. call schedinit。初始化调度器。
3. make & queue new G。创建新的 goroutine。
4. call runtime·mstart。调用 mstart，启动调度。
5. The new G calls runtime·main。在新的 goroutine 上运行 runtime.main 函数。

函数首先调用 `getg()` 函数获取当前正在运行的 `g`，`getg()` 在 `src/runtime/stubs.go` 中声明，真正的代码由编译器生成。

```golang
// getg returns the pointer to the current g.
// The compiler rewrites calls to this function into instructions
// that fetch the g directly (from TLS or from the dedicated register).
func getg() *g
```

注释里也说了，getg 返回当前正在运行的 goroutine 的指针，它会从 tls 里取出 tls[0]，也就是当前运行的 goroutine 的地址。编译器插入类似下面的代码：

```golang
get_tls(CX) 
MOVQ g(CX), BX; // BX存器里面现在放的是当前g结构体对象的地址
```

继续往下看：

```golang
sched.maxmcount = 10000
```

设置最多只能创建 10000 个工作线程。

然后，调用了一堆 init 函数，初始化各种配置，现在不去深究。只关心本小节的重点，m0 的初始化：

```golang
// 初始化 m
func mcommoninit(mp *m) {
	// 初始化过程中_g_ = g0
	_g_ := getg()

	// g0 stack won't make sense for user (and is not necessary unwindable).
	if _g_ != _g_.m.g0 {
		callers(1, mp.createstack[:])
	}

	// random 初始化
	mp.fastrand = 0x49f6428a + uint32(mp.id) + uint32(cputicks())
	if mp.fastrand == 0 {
		mp.fastrand = 0x49f6428a
	}

	lock(&sched.lock)
	// 设置 m 的 id
	mp.id = sched.mcount
	sched.mcount++
	// 检查已创建系统线程是否超过了数量限制（10000）
	checkmcount()

	// ………………省略了初始化 gsignal

	// Add to allm so garbage collector doesn't free g->m
	// when it is just in a register or thread-local storage.
	mp.alllink = allm

	atomicstorep(unsafe.Pointer(&allm), unsafe.Pointer(mp))
	unlock(&sched.lock)

	// ………………
}
```

因为 sched 是一个全局变量，多个线程同时操作 sched 会有并发问题，因此先要加锁，操作结束之后再解锁。

```golang
mp.id = sched.mcount
sched.mcount++
checkmcount()
```

可以看到，m0 的 id 是 0，并且之后创建的 m 的 id 是递增的。`checkmcount()` 函数检查已创建系统线程是否超过了数量限制（10000）。

```golang
mp.alllink = allm
```

将 m 挂到全局变量 allm 上，allm 是一个指向 m 的的指针。

```golang
atomicstorep(unsafe.Pointer(&allm), unsafe.Pointer(mp))
```

这一行将 allm 变成 m 的地址，这样变成了一个循环链表。之后再新建 m 的时候，新 m 的 alllink 就会指向本次的 m，最后 allm 又会指向新创建的 m。

![m.alllink 形成链表](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/sched/assets/23.png)

上图中，1 将 m0 挂在 allm 上。之后，若新创建 m，则 m1 会和 m0 相连。

完成这些操作后，大功告成！解锁。

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/sched/7-%E6%8F%8F%E8%BF%B0%20scheduler%20%E7%9A%84%E5%88%9D%E5%A7%8B%E5%8C%96%E8%BF%87%E7%A8%8B.md#L464)，来源许可：GPL-3.0。

<a id="k3c890bea288f"></a>

## 如何利用unsafe包修改私有成员

对于一个结构体，通过 offset 函数可以获取结构体成员的偏移量，进而获取成员的地址，读写该地址的内存，就可以达到改变成员值的目的。

这里有一个内存分配相关的事实：结构体会被分配一块连续的内存，结构体的地址也代表了第一个成员的地址。

我们来看一个例子：

```golang
package main

import (
	"fmt"
	"unsafe"
)

type Programmer struct {
	name string
	language string
}

func main() {
	p := Programmer{"stefno", "go"}
	fmt.Println(p)

	name := (*string)(unsafe.Pointer(&p))
	*name = "qcrao"

	lang := (*string)(unsafe.Pointer(uintptr(unsafe.Pointer(&p)) + unsafe.Offsetof(p.language)))
	*lang = "Golang"

	fmt.Println(p)
}
```

运行代码，输出：

```shell
{stefno go}
{qcrao Golang}
```

name 是结构体的第一个成员，因此可以直接将 &p 解析成 *string。这一点，在前面获取 map 的 count 成员时，用的是同样的原理。

对于结构体的私有成员，现在有办法可以通过 unsafe.Pointer 改变它的值了。

我把 Programmer 结构体升级，多加一个字段：

```golang
type Programmer struct {
	name string
	age int
	language string
}
```

并且放在其他包，这样在 main 函数中，它的三个字段都是私有成员变量，不能直接修改。但我通过 unsafe.Sizeof() 函数可以获取成员大小，进而计算出成员的地址，直接修改内存。

```golang
func main() {
	p := Programmer{"stefno", 18, "go"}
	fmt.Println(p)

	lang := (*string)(unsafe.Pointer(uintptr(unsafe.Pointer(&p)) + unsafe.Sizeof(int(0)) + unsafe.Sizeof(string(""))))
	*lang = "Golang"

	fmt.Println(p)
}
```

输出：

```shell
{stefno 18 go}
{stefno 18 Golang}
```

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/stdlib/unsafe/3-%E5%A6%82%E4%BD%95%E5%88%A9%E7%94%A8unsafe%E5%8C%85%E4%BF%AE%E6%94%B9%E7%A7%81%E6%9C%89%E6%88%90%E5%91%98.md#L3)，来源许可：GPL-3.0。

<a id="k9f3ed671dfeb"></a>

## 调整 SP

第一段代码，将 SP 调整到了一个地址是 16 的倍数的位置：

```asm
SUBQ	$(4*8+7), SP		// 2args 2auto
// 调整栈顶寄存器使其按 16 个字节对齐
ANDQ	$~15, SP
```

先是将 SP 减掉 39，也就是向下移动了 39 个 Byte，再进行与运算。

`15` 的二进制低四位是全 1：`1111`，其他位都是 0；取反后，变成了 `0000`，高位则是全 1。这样，与 SP 进行了与运算后，低 4 位变成了全 0，高位则不变。因此 SP 继续向下移动，并且这回是在一个地址值为 16 的倍数的地方，16 字节对齐的地方。

为什么要这么做？画一张图就明白了。不过先得说明一点，前面 `_rt0_amd64_linux` 函数里讲过，DI 里存的是 argc 的值，8 个字节，而 SI 里则存的是 argv 的地址，8 个字节。

![SP 内存对齐](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/sched/assets/19.png)

![SP 内存对齐](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/sched/assets/20.png)

上面两张图中，左侧用箭头标注了 16 字节对齐的位置。第一步表示向下移动 39 B，第二步表示与 `~15` 相与。

存在两种情况，这也是第一步将 SP 下移的时候，多移了 7 个 Byte 的原因。第一张图里，与 `~15` 相与的时候，SP 值减少了 1，第二张图则减少了 9。最后都是移位到了 16 字节对齐的位置。

两张图的共同点是 SP 与 argc 中间多出了 16 个字节的空位。这个后面应该会用到，我们接着探索。

至于为什么进行 16 个字节对齐，就比较好理解了：因为 CPU 有一组 SSE 指令，这些指令中出现的内存地址必须是 16 的倍数。

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/sched/7-%E6%8F%8F%E8%BF%B0%20scheduler%20%E7%9A%84%E5%88%9D%E5%A7%8B%E5%8C%96%E8%BF%87%E7%A8%8B.md#L304)，来源许可：GPL-3.0。
