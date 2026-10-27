# 并发、Channel与调度

<a id="kd26e143aab4d"></a>

## channel 发送和接收元素的本质是什么

Channel 发送和接收元素的本质是什么？

> All transfer of value on the go channels happens with the copy of value.

就是说 channel 的发送和接收操作本质上都是 “值的拷贝”，无论是从 sender goroutine 的栈到 chan buf，还是从 chan buf 到 receiver goroutine，或者是直接从 sender goroutine 到 receiver goroutine。

举一个例子：

```
type user struct {
	name string
	age int8
}

var u = user{name: "Ankur", age: 25}
var g = &u

func modifyUser(pu *user) {
	fmt.Println("modifyUser Received Vaule", pu)
	pu.name = "Anand"
}

func printUser(u <-chan *user) {
	time.Sleep(2 * time.Second)
	fmt.Println("printUser goRoutine called", <-u)
}

func main() {
	c := make(chan *user, 5)
	c <- g
	fmt.Println(g)
	// modify g
	g = &user{name: "Ankur Anand", age: 100}
	go printUser(c)
	go modifyUser(g)
	time.Sleep(5 * time.Second)
	fmt.Println(g)
}
```

运行结果：

```shell
&{Ankur 25}
modifyUser Received Vaule &{Ankur Anand 100}
printUser goRoutine called &{Ankur 25}
&{Anand 100}
```

这里就是一个很好的 `share memory by communicating` 的例子。

![output](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/channel/assets/12.png)

一开始构造一个结构体 u，地址是 0x56420，图中地址上方就是它的内容。接着把 `&u` 赋值给指针 `g`，g 的地址是 0x565bb0，它的内容就是一个地址，指向 u。

main 程序里，先把 g 发送到 c，根据 `copy value` 的本质，进入到 chan buf 里的就是 `0x56420`，它是指针 g 的值（不是它指向的内容），所以打印从 channel 接收到的元素时，它就是 `&{Ankur 25}`。因此，这里并不是将指针 g “发送” 到了 channel 里，只是拷贝它的值而已。

再强调一次：

> Remember all transfer of value on the go channels happens with the copy of value.

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/channel/9-channel%20%E5%8F%91%E9%80%81%E5%92%8C%E6%8E%A5%E6%94%B6%E5%85%83%E7%B4%A0%E7%9A%84%E6%9C%AC%E8%B4%A8%E6%98%AF%E4%BB%80%E4%B9%88.md#L3)，来源许可：GPL-3.0。

<a id="k1c5bcadcf739"></a>

## channel 底层的数据结构是什么

### 数据结构
底层数据结构需要看源码，版本为 go 1.9.2：

```golang
type hchan struct {
	// chan 里元素数量
	qcount   uint
	// chan 底层循环数组的长度
	dataqsiz uint
	// 指向底层循环数组的指针
	// 只针对有缓冲的 channel
	buf      unsafe.Pointer
	// chan 中元素大小
	elemsize uint16
	// chan 是否被关闭的标志
	closed   uint32
	// chan 中元素类型
	elemtype *_type // element type
	// 已发送元素在循环数组中的索引
	sendx    uint   // send index
	// 已接收元素在循环数组中的索引
	recvx    uint   // receive index
	// 等待接收的 goroutine 队列
	recvq    waitq  // list of recv waiters
	// 等待发送的 goroutine 队列
	sendq    waitq  // list of send waiters

	// 保护 hchan 中所有字段
	lock mutex
}
```

关于字段的含义都写在注释里了，再来重点说几个字段：

`buf` 指向底层循环数组，只有缓冲型的 channel 才有。

`sendx`，`recvx` 均指向底层循环数组，表示当前可以发送和接收的元素位置索引值（相对于底层数组）。

`sendq`，`recvq` 分别表示被阻塞的 goroutine，这些 goroutine 由于尝试读取 channel 或向 channel 发送数据而被阻塞。

`waitq` 是 `sudog` 的一个双向链表，而 `sudog` 实际上是对 goroutine 的一个封装：

```golang
type waitq struct {
	first *sudog
	last  *sudog
}
```

`lock` 用来保证每个读 channel 或写 channel 的操作都是原子的。

例如，创建一个容量为 6 的，元素为 int 型的 channel 数据结构如下 ：

![chan data structure](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/channel/assets/0.png)

### 创建
我们知道，通道有两个方向，发送和接收。理论上来说，我们可以创建一个只发送或只接收的通道，但是这种通道创建出来后，怎么使用呢？一个只能发的通道，怎么接收呢？同样，一个只能收的通道，如何向其发送数据呢？

一般而言，使用 `make` 创建一个能收能发的通道：

```golang
// 无缓冲通道
ch1 := make(chan int)
// 有缓冲通道
ch2 := make(chan int, 10)
```

通过[汇编](https://mp.weixin.qq.com/s/obnnVkO2EiFnuXk_AIDHWw)分析，我们知道，最终创建 chan 的函数是 `makechan`：

```golang
func makechan(t *chantype, size int64) *hchan
```

从函数原型来看，创建的 chan 是一个指针。所以我们能在函数间直接传递 channel，而不用传递 channel 的指针。

具体来看下代码：

```golang
const hchanSize = unsafe.Sizeof(hchan{}) + uintptr(-int(unsafe.Sizeof(hchan{}))&(maxAlign-1))

func makechan(t *chantype, size int64) *hchan {
	elem := t.elem

	// 省略了检查 channel size，align 的代码
	// ……

	var c *hchan
	// 如果元素类型不含指针 或者 size 大小为 0（无缓冲类型）
	// 只进行一次内存分配
	if elem.kind&kindNoPointers != 0 || size == 0 {
		// 如果 hchan 结构体中不含指针，GC 就不会扫描 chan 中的元素
		// 只分配 "hchan 结构体大小 + 元素大小*个数" 的内存
		c = (*hchan)(mallocgc(hchanSize+uintptr(size)*elem.size, nil, true))
		// 如果是缓冲型 channel 且元素大小不等于 0（大小等于 0的元素类型：struct{}）
		if size > 0 && elem.size != 0 {
			c.buf = add(unsafe.Pointer(c), hchanSize)
		} else {
			// race detector uses this location for synchronization
			// Also prevents us from pointing beyond the allocation (see issue 9401).
			// 1. 非缓冲型的，buf 没用，直接指向 chan 起始地址处
			// 2. 缓冲型的，能进入到这里，说明元素无指针且元素类型为 struct{}，也无影响
			// 因为只会用到接收和发送游标，不会真正拷贝东西到 c.buf 处（这会覆盖 chan的内容）
			c.buf = unsafe.Pointer(c)
		}
	} else {
		// 进行两次内存分配操作
		c = new(hchan)
		c.buf = newarray(elem, int(size))
	}
	c.elemsize = uint16(elem.size)
	c.elemtype = elem
	// 循环数组长度
	c.dataqsiz = uint(size)

	// 返回 hchan 指针
	return c
}
```

新建一个 chan 后，内存在堆上分配，大概长这样：

![make chan](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/channel/assets/1.png)

### 参考资料

【Kavya在Gopher Con 上关于 channel 的设计，非常好】https://speakerd.s3.amazonaws.com/presentations/10ac0b1d76a6463aa98ad6a9dec917a7/GopherCon_v10.0.pdf

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/channel/2-channel%20%E5%BA%95%E5%B1%82%E7%9A%84%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84%E6%98%AF%E4%BB%80%E4%B9%88.md#L3)，来源许可：GPL-3.0。

<a id="ka51021db9508"></a>

## context 如何被取消

context 包的代码并不长，`context.go` 文件总共不到 500 行，其中还有很多大段的注释，代码可能也就 200 行左右的样子，是一个非常值得研究的代码库。

先看一张整体的图：

![structure](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/stdlib/context/assets/3.png)

|类型|名称|作用|
|---|---|---|
|Context| 接口 | 定义了 Context 接口的四个方法 |
|emptyCtx| 结构体 | 实现了 Context 接口，它其实是个空的 context|
|CancelFunc| 函数 | 取消函数 |
|canceler| 接口 | context 取消接口，定义了两个方法 |
|cancelCtx| 结构体 | 可以被取消 |
|timerCtx| 结构体 | 超时会被取消 |
|valueCtx| 结构体 | 可以存储 k-v 对 |
|Background| 函数 | 返回一个空的 context，常作为根 context |
|TODO| 函数 | 返回一个空的 context，常用于重构时期，没有合适的 context 可用 |
|WithCancel| 函数 | 基于父 context，生成一个可以取消的 context |
|newCancelCtx| 函数 | 创建一个可取消的 context |
|propagateCancel| 函数 | 向下传递 context 节点间的取消关系 |
|parentCancelCtx| 函数 | 找到第一个可取消的父节点 |
|removeChild| 函数 |去掉父节点的孩子节点|
|init| 函数 | 包初始化 |
|WithDeadline| 函数 | 创建一个有 deadline 的 context |
|WithTimeout| 函数 | 创建一个有 timeout 的 context|
|WithValue| 函数 | 创建一个存储 k-v 对的 context |

上面这张表展示了 context 的所有函数、接口、结构体，可以纵览全局，可以在读完文章后，再回头细看。

整体类图如下：

![classes](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/stdlib/context/assets/4.png)

### 接口
### Context
现在可以直接看源码：

```golang
type Context interface {
	// 当 context 被取消或者到了 deadline，返回一个被关闭的 channel
	Done() <-chan struct{}

	// 在 channel Done 关闭后，返回 context 取消原因
	Err() error

	// 返回 context 是否会被取消以及自动取消时间（即 deadline）
	Deadline() (deadline time.Time, ok bool)

	// 获取 key 对应的 value
	Value(key interface{}) interface{}
}
```

`Context` 是一个接口，定义了 4 个方法，它们都是`幂等`的。也就是说连续多次调用同一个方法，得到的结果都是相同的。

`Done()` 返回一个 channel，可以表示 context 被取消的信号：当这个 channel 被关闭时，说明 context 被取消了。注意，这是一个只读的channel。 我们又知道，读一个关闭的 channel 会读出相应类型的零值。并且源码里没有地方会向这个 channel 里面塞入值。换句话说，这是一个 `receive-only` 的 channel。因此在子协程里读这个 channel，除非被关闭，否则读不出来任何东西。也正是利用了这一点，子协程从 channel 里读出了值（零值）后，就可以做一些收尾工作，尽快退出。

`Err()` 返回一个错误，表示 channel 被关闭的原因。例如是被取消，还是超时。

`Deadline()` 返回 context 的截止时间，通过此时间，函数就可以决定是否进行接下来的操作，如果时间太短，就可以不往下做了，否则浪费系统资源。当然，也可以用这个 deadline 来设置一个 I/O 操作的超时时间。

`Value()` 获取之前设置的 key 对应的 value。

### canceler
再来看另外一个接口：

```golang
type canceler interface {
	cancel(removeFromParent bool, err error)
	Done() <-chan struct{}
}
```

实现了上面定义的两个方法的 Context，就表明该 Context 是可取消的。源码中有两个类型实现了 canceler 接口：`*cancelCtx` 和 `*timerCtx`。注意是加了 `*` 号的，是这两个结构体的指针实现了 canceler 接口。

Context 接口设计成这个样子的原因：

- “取消”操作应该是建议性，而非强制性

caller 不应该去关心、干涉 callee 的情况，决定如何以及何时 return 是 callee 的责任。caller 只需发送“取消”信息，callee 根据收到的信息来做进一步的决策，因此接口并没有定义 cancel 方法。

-  “取消”操作应该可传递

“取消”某个函数时，和它相关联的其他函数也应该“取消”。因此，`Done()` 方法返回一个只读的 channel，所有相关函数监听此 channel。一旦 channel 关闭，通过 channel 的“广播机制”，所有监听者都能收到。

### 结构体
### emptyCtx
源码中定义了 `Context` 接口后，并且给出了一个实现：

```golang
type emptyCtx int

func (*emptyCtx) Deadline() (deadline time.Time, ok bool) {
	return
}

func (*emptyCtx) Done() <-chan struct{} {
	return nil
}

func (*emptyCtx) Err() error {
	return nil
}

func (*emptyCtx) Value(key interface{}) interface{} {
	return nil
}
```

看这段源码，非常 happy。因为每个函数都实现的异常简单，要么是直接返回，要么是返回 nil。

所以，这实际上是一个空的 context，永远不会被 cancel，没有存储值，也没有 deadline。

它被包装成：

```golang
var (
	background = new(emptyCtx)
	todo       = new(emptyCtx)
)
```

通过下面两个导出的函数（首字母大写）对外公开：

```golang
func Background() Context {
	return background
}

func TODO() Context {
	return todo
}
```

background 通常用在 main 函数中，作为所有 context 的根节点。

todo 通常用在并不知道传递什么 context的情形。例如，调用一个需要传递 context 参数的函数，你手头并没有其他 context 可以传递，这时就可以传递 todo。这常常发生在重构进行中，给一些函数添加了一个 Context 参数，但不知道要传什么，就用 todo “占个位子”，最终要换成其他 context。

### cancelCtx
再来看一个重要的 context：

```golang
type cancelCtx struct {
	Context

	// 保护之后的字段
	mu       sync.Mutex
	done     chan struct{}
	children map[canceler]struct{}
	err      error
}
```

这是一个可以取消的 Context，实现了 canceler 接口。它直接将接口 Context 作为它的一个匿名字段，这样，它就可以被看成一个 Context。

先来看 `Done()` 方法的实现：

```golang
func (c *cancelCtx) Done() <-chan struct{} {
	c.mu.Lock()
	if c.done == nil {
		c.done = make(chan struct{})
	}
	d := c.done
	c.mu.Unlock()
	return d
}
```

c.done 是“懒汉式”创建，只有调用了 Done() 方法的时候才会被创建。再次说明，函数返回的是一个只读的 channel，而且没有地方向这个 channel 里面写数据。所以，直接调用读这个 channel，协程会被 block 住。一般通过搭配 select 来使用。一旦关闭，就会立即读出零值。

`Err()` 和 `String()` 方法比较简单，不多说。推荐看源码，非常简单。

接下来，我们重点关注 `cancel()` 方法的实现：

```golang
func (c *cancelCtx) cancel(removeFromParent bool, err error) {
    // 必须要传 err
	if err == nil {
		panic("context: internal error: missing cancel error")
	}
	c.mu.Lock()
	if c.err != nil {
		c.mu.Unlock()
		return // 已经被其他协程取消
	}
	// 给 err 字段赋值
	c.err = err
	// 关闭 channel，通知其他协程
	if c.done == nil {
		c.done = closedchan
	} else {
		close(c.done)
	}

	// 遍历它的所有子节点
	for child := range c.children {
	    // 递归地取消所有子节点
		child.cancel(false, err)
	}
	// 将子节点置空
	c.children = nil
	c.mu.Unlock()

	if removeFromParent {
	    // 从父节点中移除自己 
		removeChild(c.Context, c)
	}
}
```

总体来看，`cancel()` 方法的功能就是关闭 channel：c.done；递归地取消它的所有子节点；从父节点从删除自己。达到的效果是通过关闭 channel，将取消信号传递给了它的所有子节点。goroutine 接收到取消信号的方式就是 select 语句中的`读 c.done` 被选中。

我们再来看创建一个可取消的 Context 的方法：

```golang
func WithCancel(parent Context) (ctx Context, cancel CancelFunc) {
	c := newCancelCtx(parent)
	propagateCancel(parent, &c)
	return &c, func() { c.cancel(true, Canceled) }
}

func newCancelCtx(parent Context) cancelCtx {
	return cancelCtx{Context: parent}
}
```

这是一个暴露给用户的方法，传入一个父 Context（这通常是一个 `background`，作为根节点），返回新建的 context，新 context 的 done channel 是新建的（前文讲过）。

当 WithCancel 函数返回的 CancelFunc 被调用或者是父节点的 done channel 被关闭（父节点的 CancelFunc 被调用），此 context（子节点） 的 done channel 也会被关闭。

注意传给 WithCancel 方法的参数，前者是 true，也就是说取消的时候，需要将自己从父节点里删除。第二个参数则是一个固定的取消错误类型：

```golang
var Canceled = errors.New("context canceled")
```

还注意到一点，调用子节点 cancel 方法的时候，传入的第一个参数 `removeFromParent` 是 false。

两个问题需要回答：1. 什么时候会传 true？2. 为什么有时传 true，有时传 false？

当 `removeFromParent` 为 true 时，会将当前节点的 context 从父节点 context 中删除：

```golang
func removeChild(parent Context, child canceler) {
	p, ok := parentCancelCtx(parent)
	if !ok {
		return
	}
	p.mu.Lock()
	if p.children != nil {
		delete(p.children, child)
	}
	p.mu.Unlock()
}
```

最关键的一行：

```golang
delete(p.children, child)
```

什么时候会传 true 呢？答案是调用 `WithCancel()` 方法的时候，也就是新创建一个可取消的 context 节点时，返回的 cancelFunc 函数会传入 true。这样做的结果是：当调用返回的 cancelFunc 时，会将这个 context 从它的父节点里“除名”，因为父节点可能有很多子节点，你自己取消了，所以我要和你断绝关系，对其他人没影响。

在取消函数内部，我知道，我所有的子节点都会因为我的一：`c.children = nil` 而化为灰烬。我自然就没有必要再多做这一步，最后我所有的子节点都会和我断绝关系，没必要一个个做。另外，如果遍历子节点的时候，调用 child.cancel 函数传了 true，还会造成同时遍历和删除一个 map 的境地，会有问题的。

![context cancel](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/stdlib/context/assets/5.png)

如上左图，代表一棵 context 树。当调用左图中标红 context 的 cancel 方法后，该 context 从它的父 context 中去除掉了：实线箭头变成了虚线。且虚线圈框出来的 context 都被取消了，圈内的 context 间的父子关系都荡然无存了。

重点看 `propagateCancel()`：

```golang
func propagateCancel(parent Context, child canceler) {
	// 父节点是个空节点
	if parent.Done() == nil {
		return // parent is never canceled
	}
	// 找到可以取消的父 context
	if p, ok := parentCancelCtx(parent); ok {
		p.mu.Lock()
		if p.err != nil {
			// 父节点已经被取消了，本节点（子节点）也要取消
			child.cancel(false, p.err)
		} else {
			// 父节点未取消
			if p.children == nil {
				p.children = make(map[canceler]struct{})
			}
			// "挂到"父节点上
			p.children[child] = struct{}{}
		}
		p.mu.Unlock()
	} else {
		// 如果没有找到可取消的父 context。新启动一个协程监控父节点或子节点取消信号
		go func() {
			select {
			case <-parent.Done():
				child.cancel(false, parent.Err())
			case <-child.Done():
			}
		}()
	}
}
```

这个方法的作用就是向上寻找可以“挂靠”的“可取消”的 context，并且“挂靠”上去。这样，调用上层 cancel 方法的时候，就可以层层传递，将那些挂靠的子 context 同时“取消”。

这里着重解释下为什么会有 else 描述的情况发生。`else` 是指当前节点 context 没有向上找到可以取消的父节点，那么就要再启动一个协程监控父节点或者子节点的取消动作。

这里就有疑问了，既然没找到可以取消的父节点，那 `case <-parent.Done()` 这个 case 就永远不会发生，所以可以忽略这个 case；而 `case <-child.Done()` 这个 case 又啥事不干。那这个 `else` 不就多余了吗？

其实不然。我们来看 `parentCancelCtx` 的代码：

```golang
func parentCancelCtx(parent Context) (*cancelCtx, bool) {
	for {
		switch c := parent.(type) {
		case *cancelCtx:
			return c, true
		case *timerCtx:
			return &c.cancelCtx, true
		case *valueCtx:
			parent = c.Context
		default:
			return nil, false
		}
	}
}
```

这里只会识别三种 Context 类型：*cancelCtx，*timerCtx，*valueCtx。若是把 Context 内嵌到一个类型里，就识别不出来了。

由于 context 包的代码并不多，所以我直接把它 copy 出来了，然后在 else 语句里加上了几条打印语句，来验证上面的说法：

```golang
type MyContext struct {
    // 这里的 Context 是我 copy 出来的，所以前面不用加 context.
	Context
}

func main() {
	childCancel := true

	parentCtx, parentFunc := WithCancel(Background())
	mctx := MyContext{parentCtx}

	childCtx, childFun := WithCancel(mctx)

	if childCancel {
		childFun()
	} else {
		parentFunc()
	}

	fmt.Println(parentCtx)
	fmt.Println(mctx)
	fmt.Println(childCtx)

    // 防止主协程退出太快，子协程来不及打印 
	time.Sleep(10 * time.Second)
}
```

我自已在 else 里添加的打印语句我就不贴出来了，感兴趣的可以自己动手实验下。我们看下三个 context 的打印结果：

```shell
context.Background.WithCancel
{context.Background.WithCancel}
{context.Background.WithCancel}.WithCancel
```

果然，mctx，childCtx 和正常的 parentCtx 不一样，因为它是一个自定义的结构体类型。

`else` 这段代码说明，如果把 ctx 强行塞进一个结构体，并用它作为父节点，调用 WithCancel 函数构建子节点 context 的时候，Go 会新启动一个协程来监控取消信号，明显有点浪费嘛。

再来说一下，select 语句里的两个 case 其实都不能删。

```golang
select {
	case <-parent.Done():
		child.cancel(false, parent.Err())
	case <-child.Done():
}
```

第一个 case 说明当父节点取消，则取消子节点。如果去掉这个 case，那么父节点取消的信号就不能传递到子节点。

第二个 case 是说如果子节点自己取消了，那就退出这个 select，父节点的取消信号就不用管了。如果去掉这个 case，那么很可能父节点一直不取消，这个 goroutine 就泄漏了。当然，如果父节点取消了，就会重复让子节点取消，不过，这也没什么影响嘛。

### timerCtx
timerCtx 基于 cancelCtx，只是多了一个 time.Timer 和一个 deadline。Timer 会在 deadline 到来时，自动取消 context。

```golang
type timerCtx struct {
	cancelCtx
	timer *time.Timer // Under cancelCtx.mu.

	deadline time.Time
}
```

timerCtx 首先是一个 cancelCtx，所以它能取消。看下 cancel() 方法：

```golang
func (c *timerCtx) cancel(removeFromParent bool, err error) {
	// 直接调用 cancelCtx 的取消方法
	c.cancelCtx.cancel(false, err)
	if removeFromParent {
		// 从父节点中删除子节点
		removeChild(c.cancelCtx.Context, c)
	}
	c.mu.Lock()
	if c.timer != nil {
		// 关掉定时器，这样，在deadline 到来时，不会再次取消
		c.timer.Stop()
		c.timer = nil
	}
	c.mu.Unlock()
}
```

创建 timerCtx 的方法：

```golang
func WithTimeout(parent Context, timeout time.Duration) (Context, CancelFunc) {
	return WithDeadline(parent, time.Now().Add(timeout))
}
```

`WithTimeout` 函数直接调用了 `WithDeadline`，传入的 deadline 是当前时间加上 timeout 的时间，也就是从现在开始再经过 timeout 时间就算超时。也就是说，`WithDeadline` 需要用的是绝对时间。重点来看它：

```golang
func WithDeadline(parent Context, deadline time.Time) (Context, CancelFunc) {
	if cur, ok := parent.Deadline(); ok && cur.Before(deadline) {
		// 如果父节点 context 的 deadline 早于指定时间。直接构建一个可取消的 context。
		// 原因是一旦父节点超时，自动调用 cancel 函数，子节点也会随之取消。
		// 所以不用单独处理子节点的计时器时间到了之后，自动调用 cancel 函数
		return WithCancel(parent)
	}

	// 构建 timerCtx
	c := &timerCtx{
		cancelCtx: newCancelCtx(parent),
		deadline:  deadline,
	}
	// 挂靠到父节点上
	propagateCancel(parent, c)

	// 计算当前距离 deadline 的时间
	d := time.Until(deadline)
	if d <= 0 {
		// 直接取消
		c.cancel(true, DeadlineExceeded) // deadline has already passed
		return c, func() { c.cancel(true, Canceled) }
	}
	c.mu.Lock()
	defer c.mu.Unlock()
	if c.err == nil {
		// d 时间后，timer 会自动调用 cancel 函数。自动取消
		c.timer = time.AfterFunc(d, func() {
			c.cancel(true, DeadlineExceeded)
		})
	}
	return c, func() { c.cancel(true, Canceled) }
}
```

也就是说仍然要把子节点挂靠到父节点，一旦父节点取消了，会把取消信号向下传递到子节点，子节点随之取消。

有一个特殊情况是，如果要创建的这个子节点的 deadline 比父节点要晚，也就是说如果父节点是时间到自动取消，那么一定会取消这个子节点，导致子节点的 deadline 根本不起作用，因为子节点在 deadline 到来之前就已经被父节点取消了。

这个函数的最核心的一句是：

```golang
c.timer = time.AfterFunc(d, func() {
	c.cancel(true, DeadlineExceeded)
})
```

c.timer 会在 d 时间间隔后，自动调用 cancel 函数，并且传入的错误就是 `DeadlineExceeded`：

```golang
var DeadlineExceeded error = deadlineExceededError{}

type deadlineExceededError struct{}

func (deadlineExceededError) Error() string   { return "context deadline exceeded" }
```

也就是超时错误。

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/stdlib/context/4-context%20%E5%A6%82%E4%BD%95%E8%A2%AB%E5%8F%96%E6%B6%88.md#L3)，来源许可：GPL-3.0。

<a id="k718d348f7012"></a>

## Go Channel

**回答：**

Channel 是 Go 中有类型的通信机制，可在 goroutine 之间传递值并建立同步关系。`make(chan T)` 创建无缓冲 channel，发送需要与接收配对；`make(chan T, n)` 创建容量为 `n` 的缓冲 channel，未满时发送可继续，非空时接收可继续。

| 状态 | 发送 | 接收 | 关闭 |
| --- | --- | --- | --- |
| nil channel | 一直阻塞 | 一直阻塞 | panic |
| 已关闭 channel | panic | 先读完缓冲值，再立即返回零值与 `ok=false` | 再关闭会 panic |
| 打开的无缓冲 channel | 等待接收配对 | 等待发送配对 | 唤醒等待接收；等待发送会 panic |
| 打开的有缓冲 channel | 满时阻塞 | 空时阻塞 | 不丢弃已缓冲的数据 |

两值接收 `v, ok := <-ch` 中，只有 channel 已关闭且缓冲耗尽时，`ok` 才为 false。`for v := range ch` 会持续接收直到该条件成立；若发送方忘记关闭，消费者可能永久等待。

通常由明确负责发送生命周期的一方关闭 channel。多发送者场景应由协调者等待所有发送结束后关闭，接收者不应随意关闭仍有人发送的通道。关闭用于表达“不会再有新值”，不是释放 channel 的必要动作。

`select` 在可执行的通信分支中选择一个；有多个就绪分支时不能依赖源码顺序作为优先级。nil channel 对应分支不会就绪，已关闭且耗尽的 channel 接收则持续就绪，若在循环中不退出或禁用该分支，可能形成忙循环。带 `default` 的循环也可能空转。

Channel 通信具有 Go 内存模型定义的同步语义，但传递指针不会自动保护被指向对象的后续并发修改。工程中仍需明确所有权，利用 `context`、超时和有界队列处理取消与背压，并避免 goroutine 因永久等待而泄漏。

补充一个容易混淆的同步边界：发送方在发送前写入的数据，通过匹配的接收可以建立 Go 内存模型规定的可见性关系；但发送指针后继续修改对象，仍可能与接收者读取发生数据竞争。无缓冲 channel 也不意味着“接收方整个业务处理完成后，发送方才继续”，它只保证通信配对所要求的同步，需要业务完成确认时应增加明确的 ack 或其他同步机制。

多生产者场景通常由协调者等待所有生产者退出后关闭结果 channel；生产者的阻塞发送和消费者的阻塞接收都应考虑取消路径。即使 `select` 同时包含 `ctx.Done()`，取消与发送都就绪时也不能保证取消分支优先。已经发生的外部写入不会因 context 取消而自动回滚。

<a id="baidu-aigc-multimodal-agent-20260922-20260924-r2-q15"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%99%BE%E5%BA%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L2152)，来源许可：GPL-3.0。

<a id="kdd05eb7315be"></a>

## goroutine 如何退出

上一讲说到调度器将 main goroutine 推上舞台，为它铺好了道路，开始执行 `runtime.main` 函数。这一讲，我们探索 main goroutine 以及普通 goroutine 从执行到退出的整个过程。

```golang
// The main goroutine.
func main() {
    // g = main goroutine，不再是 g0 了
    g := getg()

    // ……………………

    if sys.PtrSize == 8 {
        maxstacksize = 1000000000
    } else {
        maxstacksize = 250000000
    }

    // Allow newproc to start new Ms.
    mainStarted = true

    systemstack(func() {
        // 创建监控线程，该线程独立于调度器，不需要跟 p 关联即可运行
        newm(sysmon, nil)
    })

    lockOSThread()

    if g.m != &m0 {
        throw("runtime.main not on m0")
    }

    // 调用 runtime 包的初始化函数，由编译器实现
    runtime_init() // must be before defer
    if nanotime() == 0 {
        throw("nanotime returning zero")
    }

    // Defer unlock so that runtime.Goexit during init does the unlock too.
    needUnlock := true
    defer func() {
        if needUnlock {
            unlockOSThread()
        }
    }()

    // Record when the world started. Must be after runtime_init
    // because nanotime on some platforms depends on startNano.
    runtimeInitTime = nanotime()

    // 开启垃圾回收器
    gcenable()

    main_init_done = make(chan bool)

    // ……………………

    // main 包的初始化，递归的调用我们 import 进来的包的初始化函数
    fn := main_init
    fn()
    close(main_init_done)

    needUnlock = false
    unlockOSThread()

    // ……………………

    // 调用 main.main 函数
    fn = main_main
    fn()
    if raceenabled {
        racefini()
    }

    // ……………………

    // 进入系统调用，退出进程，可以看出 main goroutine 并未返回，而是直接进入系统调用退出进程了
    exit(0)
    // 保护性代码，如果 exit 意外返回，下面的代码会让该进程 crash 死掉
    for {
        var x *int32
        *x = 0
    }
}
```

`main` 函数执行流程如下图：

![runtime.main 启动流程](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/sched/assets/2.png)

从流程图可知，main goroutine 执行完之后就直接调用 `exit(0)` 退出了，这会导致整个进程退出，太粗暴了。

不过，main goroutine 实际上就是代表用户的 main 函数，它都执行完了，肯定是用户的任务都执行完了，直接退出就可以了，就算有其他的 goroutine 没执行完，同样会直接退出。

```golang
package main

import "fmt"

func main() {
	 go func() {fmt.Println("hello qcrao.com")}()
}
```

在这个例子中，main goroutine 退出时，还来不及执行 `go 出去` 的函数，整个进程就直接退出了，打印语句不会执行。因此，main goroutine 不会等待其他 goroutine 执行完再退出，知道这个有时能解释一些现象，比如上面那个例子。

这时，心中可能会跳出疑问，我们在新创建 goroutine 的时候，不是整出了个“偷天换日”，风风火火地设置了 goroutine 退出时应该跳到 `runtime.goexit` 函数吗，怎么这会不用了，闲得慌？

回顾一下上一讲的内容，跳转到 main 函数的两行代码：

```asm
// 把 sched.pc 值放入 BX 寄存器
MOVQ	gobuf_pc(BX), BX
// JMP 把 BX 寄存器的包含的地址值放入 CPU 的 IP 寄存器，于是，CPU 跳转到该地址继续执行指令
JMP	BX
```

直接使用了一个跳转，并没有使用 `CALL` 指令，而 runtime.main 函数中确实也没有 `RET` 返回的指令。所以，main goroutine 执行完后，直接调用 exit(0) 退出整个进程。

那之前整地“偷天换日”还有用吗？有的！这是针对非 main goroutine 起作用。

参考资料【阿波张 非 goroutine 的退出】中用调试工具验证了非 main goroutine 的退出，感兴趣的可以去跟着实践一遍。

我们继续探索非 main goroutine （后文我们就称 gp 好了）的退出流程。

`gp` 执行完后，RET 指令弹出 `goexit` 函数地址（实际上是 funcPC(goexit)+1），CPU 跳转到 `goexit` 的第二条指令继续执行：

```golang
// src/runtime/asm_amd64.s

// The top-most function running on a goroutine
// returns to goexit+PCQuantum.
TEXT runtime·goexit(SB),NOSPLIT,$0-0
	BYTE	$0x90	// NOP
	CALL	runtime·goexit1(SB)	// does not return
	// traceback from goexit1 must hit code range of goexit
	BYTE	$0x90	// NOP
```

直接调用 `runtime·goexit1`：

```golang
// src/runtime/proc.go
// Finishes execution of the current goroutine.
func goexit1() {
    // …………………… 
	mcall(goexit0)
}
```

调用 `mcall` 函数：

```golang
// 切换到 g0 栈，执行 fn(g)
// Fn 不能返回
TEXT runtime·mcall(SB), NOSPLIT, $0-8
    // 取出参数的值放入 DI 寄存器，它是 funcval 对象的指针，此场景中 fn.fn 是 goexit0 的地址
    MOVQ    fn+0(FP), DI

    get_tls(CX)
    // AX = g
    MOVQ    g(CX), AX   // save state in g->sched
    // mcall 返回地址放入 BX
    MOVQ    0(SP), BX   // caller's PC
    // g.sched.pc = BX，保存 g 的 PC
    MOVQ    BX, (g_sched+gobuf_pc)(AX)
    LEAQ    fn+0(FP), BX    // caller's SP
    // 保存 g 的 SP
    MOVQ    BX, (g_sched+gobuf_sp)(AX)
    MOVQ    AX, (g_sched+gobuf_g)(AX)
    MOVQ    BP, (g_sched+gobuf_bp)(AX)

    // switch to m->g0 & its stack, call fn
    MOVQ    g(CX), BX
    MOVQ    g_m(BX), BX
    // SI = g0
    MOVQ    m_g0(BX), SI
    CMPQ    SI, AX  // if g == m->g0 call badmcall
    JNE 3(PC)
    MOVQ    $runtime·badmcall(SB), AX
    JMP AX
    // 把 g0 的地址设置到线程本地存储中
    MOVQ    SI, g(CX)   // g = m->g0
    // 从 g 的栈切换到了 g0 的栈D
    MOVQ    (g_sched+gobuf_sp)(SI), SP  // sp = m->g0->sched.sp
    // AX = g，参数入栈
    PUSHQ   AX
    MOVQ    DI, DX
    // DI 是结构体 funcval 实例对象的指针，它的第一个成员才是 goexit0 的地址
    // 读取第一个成员到 DI 寄存器
    MOVQ    0(DI), DI
    // 调用 goexit0(g)
    CALL    DI
    POPQ    AX
    MOVQ    $runtime·badmcall2(SB), AX
    JMP AX
    RET
```

函数参数是：

```golang
type funcval struct {
	fn uintptr
	// variable-size, fn-specific data here
}
```

字段 fn 就表示 goexit0 函数的地址。

L5 将函数参数保存到 DI 寄存器，这里 fn.fn 就是 goexit0 的地址。

L7 将 tls 保存到 CX 寄存器，L9 将 当前线程指向的 goroutine （非 main goroutine，称为 gp）保存到 AX 寄存器，L11 将调用者（调用 mcall 函数）的栈顶，这里就是 mcall 完成后的返回地址，存入 BX 寄存器。

L13 将 mcall 的返回地址保存到 gp 的 g.sched.pc 字段，L14 将 gp 的栈顶，也就是 SP 保存到 BX 寄存器，L16 将 SP 保存到 gp 的 g.sched.sp 字段，L17 将 g 保存到 gp 的 g.sched.g 字段，L18 将 BP 保存 到 gp 的 g.sched.bp 字段。这一段主要是保存 gp 的调度信息。

L21 将当前指向的 g 保存到 BX 寄存器，L22 将 g.m 字段保存到 BX 寄存器，L23 将 g.m.g0 字段保存到 SI，g.m.g0 就是当前工作线程的 g0。

现在，SI = g0， AX = gp，L25 判断 gp 是否是 g0，如果 gp == g0 说明有问题，执行 runtime·badmcall。正常情况下，PC 值加 3，跳过下面的两条指令，直接到达 L30。

L30 将 g0 的地址设置到线程本地存储中，L32 将 g0.SP 设置到 CPU 的 SP 寄存器，这也就意味着我们从 gp 栈切换到了 g0 的栈，要变天了！

L34 将参数 gp 入栈，为调用 goexit0 构造参数。L35 将 DI 寄存器的内容设置到 DX 寄存器，DI 是结构体 funcval 实例对象的指针，它的第一个成员才是 goexit0 的地址。L36 读取 DI 第一成员，也就是 goexit0 函数的地址。

L40 调用 goexit0 函数，这已经是在 g0 栈上执行了，函数参数就是 gp。

到这里，就会去执行 goexit0 函数，注意，这里永远都不会返回。所以，在 CALL 指令后面，如果返回了，又会去调用 `runtime.badmcall2` 函数去处理意外情况。

来继续看 goexit0：

```golang
// goexit continuation on g0.
// 在 g0 上执行
func goexit0(gp *g) {
	// g0
	_g_ := getg()

	casgstatus(gp, _Grunning, _Gdead)
	if isSystemGoroutine(gp) {
		atomic.Xadd(&sched.ngsys, -1)
	}

	// 清空 gp 的一些字段
	gp.m = nil
	gp.lockedm = nil
	_g_.m.lockedg = nil
	gp.paniconfault = false
	gp._defer = nil // should be true already but just in case.
	gp._panic = nil // non-nil for Goexit during panic. points at stack-allocated data.
	gp.writebuf = nil
	gp.waitreason = ""
	gp.param = nil
	gp.labels = nil
	gp.timer = nil

	// Note that gp's stack scan is now "valid" because it has no
	// stack.
	gp.gcscanvalid = true
	// 解除 g 与 m 的关系
	dropg()

	if _g_.m.locked&^_LockExternal != 0 {
		print("invalid m->locked = ", _g_.m.locked, "\n")
		throw("internal lockOSThread error")
	}
	_g_.m.locked = 0
	// 将 g 放入 free 队列缓存起来
	gfput(_g_.m.p.ptr(), gp)
	schedule()
}
```

它主要完成最后的清理工作：

> 1. 把 g 的状态从 `_Grunning` 更新为 `_Gdead`；

> 2. 清空 g 的一些字段；

> 3. 调用 dropg 函数解除 g 和 m 之间的关系，其实就是设置 g->m = nil, m->currg = nil；

> 4. 把 g 放入 p 的 freeg 队列缓存起来供下次创建 g 时快速获取而不用从内存分配。freeg 就是 g 的一个对象池；

> 5. 调用 schedule 函数再次进行调度。

到这里，gp 就完成了它的历史使命，功成身退，进入了 goroutine 缓存池，待下次有任务再重新启用。

而工作线程，又继续调用 schedule 函数进行新一轮的调度，整个过程形成了一个循环。

总结一下，main goroutine 和普通 goroutine 的退出过程：

对于 main goroutine，在执行完用户定义的 main 函数的所有代码后，直接调用 exit(0) 退出整个进程，非常霸道。

对于普通 goroutine 则没这么“舒服”，需要经历一系列的过程。先是跳转到提前设置好的 goexit 函数的第二条指令，然后调用 runtime.goexit1，接着调用 `mcall(goexit0)`，而 mcall 函数会切换到 g0 栈，运行 goexit0 函数，清理 goroutine 的一些字段，并将其添加到 goroutine 缓存池里，然后进入 schedule 调度循环。到这里，普通 goroutine 才算完成使命。

### 参考资料

【阿波张 非 main goroutine 的退出及调度循环】https://mp.weixin.qq.com/s/XttP9q7-PO7VXhskaBzGqA

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/sched/11-goroutine%20%E5%A6%82%E4%BD%95%E9%80%80%E5%87%BA.md#L3)，来源许可：GPL-3.0。

<a id="ke4d69790eafc"></a>

## GPM 是什么

G、P、M 是 Go 调度器的三个核心组件，各司其职。在它们精密地配合下，Go 调度器得以高效运转，这也是 Go 天然支持高并发的内在动力。今天这篇文章我们来深入理解 GPM 模型。

先看 G，取 goroutine 的首字母，主要保存 goroutine 的一些状态信息以及 CPU 的一些寄存器的值，例如 IP 寄存器，以便在轮到本 goroutine 执行时，CPU 知道要从哪一条指令处开始执行。

> 当 goroutine 被调离 CPU 时，调度器负责把 CPU 寄存器的值保存在 g 对象的成员变量之中。

>当 goroutine 被调度起来运行时，调度器又负责把 g 对象的成员变量所保存的寄存器值恢复到 CPU 的寄存器。

本系列使用的代码版本是 1.9.2，来看一下 g 的源码：

```golang
type g struct {

	// goroutine 使用的栈
	stack       stack   // offset known to runtime/cgo
	// 用于栈的扩张和收缩检查，抢占标志
	stackguard0 uintptr // offset known to liblink
	stackguard1 uintptr // offset known to liblink

	_panic         *_panic // innermost panic - offset known to liblink
	_defer         *_defer // innermost defer
	// 当前与 g 绑定的 m
	m              *m      // current m; offset known to arm liblink
	// goroutine 的运行现场
	sched          gobuf
	syscallsp      uintptr        // if status==Gsyscall, syscallsp = sched.sp to use during gc
	syscallpc      uintptr        // if status==Gsyscall, syscallpc = sched.pc to use during gc
	stktopsp       uintptr        // expected sp at top of stack, to check in traceback
	// wakeup 时传入的参数
	param          unsafe.Pointer // passed parameter on wakeup
	atomicstatus   uint32
	stackLock      uint32 // sigprof/scang lock; TODO: fold in to atomicstatus
	goid           int64
	// g 被阻塞之后的近似时间
	waitsince      int64  // approx time when the g become blocked
	// g 被阻塞的原因
	waitreason     string // if status==Gwaiting
	// 指向全局队列里下一个 g
	schedlink      guintptr
	// 抢占调度标志。这个为 true 时，stackguard0 等于 stackpreempt
	preempt        bool     // preemption signal, duplicates stackguard0 = stackpreempt
	paniconfault   bool     // panic (instead of crash) on unexpected fault address
	preemptscan    bool     // preempted g does scan for gc
	gcscandone     bool     // g has scanned stack; protected by _Gscan bit in status
	gcscanvalid    bool     // false at start of gc cycle, true if G has not run since last scan; TODO: remove?
	throwsplit     bool     // must not split stack
	raceignore     int8     // ignore race detection events
	sysblocktraced bool     // StartTrace has emitted EvGoInSyscall about this goroutine
	// syscall 返回之后的 cputicks，用来做 tracing
	sysexitticks   int64    // cputicks when syscall has returned (for tracing)
	traceseq       uint64   // trace event sequencer
	tracelastp     puintptr // last P emitted an event for this goroutine
	// 如果调用了 LockOsThread，那么这个 g 会绑定到某个 m 上
	lockedm        *m
	sig            uint32
	writebuf       []byte
	sigcode0       uintptr
	sigcode1       uintptr
	sigpc          uintptr
	// 创建该 goroutine 的语句的指令地址
	gopc           uintptr // pc of go statement that created this goroutine
	// goroutine 函数的指令地址
	startpc        uintptr // pc of goroutine function
	racectx        uintptr
	waiting        *sudog         // sudog structures this g is waiting on (that have a valid elem ptr); in lock order
	cgoCtxt        []uintptr      // cgo traceback context
	labels         unsafe.Pointer // profiler labels
	// time.Sleep 缓存的定时器
	timer          *timer         // cached timer for time.Sleep

	gcAssistBytes int64
}
```

源码中，比较重要的字段我已经作了注释，其他未作注释的与调度关系不大或者我暂时也没有理解的。

`g` 结构体关联了两个比较简单的结构体，stack 表示 goroutine 运行时的栈：

```golang
// 描述栈的数据结构，栈的范围：[lo, hi)
type stack struct {
    // 栈顶，低地址
	lo uintptr
	// 栈低，高地址
	hi uintptr
}
```

Goroutine 运行时，光有栈还不行，至少还得包括 PC，SP 等寄存器，gobuf 就保存了这些值：

```golang
type gobuf struct {
	// 存储 rsp 寄存器的值
	sp   uintptr
	// 存储 rip 寄存器的值
	pc   uintptr
	// 指向 goroutine
	g    guintptr
	ctxt unsafe.Pointer // this has to be a pointer so that gc scans it
	// 保存系统调用的返回值
	ret  sys.Uintreg
	lr   uintptr
	bp   uintptr // for GOEXPERIMENT=framepointer
}
```

再来看 M，取 machine 的首字母，它代表一个工作线程，或者说系统线程。G 需要调度到 M 上才能运行，M 是真正工作的人。结构体 m 就是我们常说的 M，它保存了 M 自身使用的栈信息、当前正在 M 上执行的 G 信息、与之绑定的 P 信息……

当 M 没有工作可做的时候，在它休眠前，会“自旋”地来找工作：检查全局队列，查看 network poller，试图执行 gc 任务，或者“偷”工作。

结构体 m 的源码如下：

```golang
// m 代表工作线程，保存了自身使用的栈信息
type m struct {
	// 记录工作线程（也就是内核线程）使用的栈信息。在执行调度代码时需要使用
	// 执行用户 goroutine 代码时，使用用户 goroutine 自己的栈，因此调度时会发生栈的切换
	g0      *g     // goroutine with scheduling stack/
	morebuf gobuf  // gobuf arg to morestack
	divmod  uint32 // div/mod denominator for arm - known to liblink

	// Fields not known to debuggers.
	procid        uint64     // for debuggers, but offset not hard-coded
	gsignal       *g         // signal-handling g
	sigmask       sigset     // storage for saved signal mask
	// 通过 tls 结构体实现 m 与工作线程的绑定
	// 这里是线程本地存储
	tls           [6]uintptr // thread-local storage (for x86 extern register)
	mstartfn      func()
	// 指向正在运行的 goroutine 对象
	curg          *g       // current running goroutine
	caughtsig     guintptr // goroutine running during fatal signal
	// 当前工作线程绑定的 p
	p             puintptr // attached p for executing go code (nil if not executing go code)
	nextp         puintptr
	id            int32
	mallocing     int32
	throwing      int32
	// 该字段不等于空字符串的话，要保持 curg 始终在这个 m 上运行
	preemptoff    string // if != "", keep curg running on this m
	locks         int32
	softfloat     int32
	dying         int32
	profilehz     int32
	helpgc        int32
	// 为 true 时表示当前 m 处于自旋状态，正在从其他线程偷工作
	spinning      bool // m is out of work and is actively looking for work
	// m 正阻塞在 note 上
	blocked       bool // m is blocked on a note
	// m 正在执行 write barrier
	inwb          bool // m is executing a write barrier
	newSigstack   bool // minit on C thread called sigaltstack
	printlock     int8
	// 正在执行 cgo 调用
	incgo         bool // m is executing a cgo call
	fastrand      uint32
	// cgo 调用总计数
	ncgocall      uint64      // number of cgo calls in total
	ncgo          int32       // number of cgo calls currently in progress
	cgoCallersUse uint32      // if non-zero, cgoCallers in use temporarily
	cgoCallers    *cgoCallers // cgo traceback if crashing in cgo call
	// 没有 goroutine 需要运行时，工作线程睡眠在这个 park 成员上，
	// 其它线程通过这个 park 唤醒该工作线程
	park          note
	// 记录所有工作线程的链表
	alllink       *m // on allm
	schedlink     muintptr
	mcache        *mcache
	lockedg       *g
	createstack   [32]uintptr // stack that created this thread.
	freglo        [16]uint32  // d[i] lsb and f[i]
	freghi        [16]uint32  // d[i] msb and f[i+16]
	fflag         uint32      // floating point compare flags
	locked        uint32      // tracking for lockosthread
	// 正在等待锁的下一个 m
	nextwaitm     uintptr     // next m waiting for lock
	needextram    bool
	traceback     uint8
	waitunlockf   unsafe.Pointer // todo go func(*g, unsafe.pointer) bool
	waitlock      unsafe.Pointer
	waittraceev   byte
	waittraceskip int
	startingtrace bool
	syscalltick   uint32
	// 工作线程 id
	thread        uintptr // thread handle

	// these are here because they are too large to be on the stack
	// of low-level NOSPLIT functions.
	libcall   libcall
	libcallpc uintptr // for cpu profiler
	libcallsp uintptr
	libcallg  guintptr
	syscall   libcall // stores syscall parameters on windows

	mOS
}
```

再来看 P，取 processor 的首字母，为 M 的执行提供“上下文”，保存 M 执行 G 时的一些资源，例如本地可运行 G 队列，memeory cache 等。

一个 M 只有绑定 P 才能执行 goroutine，当 M 被阻塞时，整个 P 会被传递给其他 M ，或者说整个 P 被接管。

```golang
// p 保存 go 运行时所必须的资源
type p struct {
	lock mutex

	// 在 allp 中的索引
	id          int32
	status      uint32 // one of pidle/prunning/...
	link        puintptr
	// 每次调用 schedule 时会加一
	schedtick   uint32
	// 每次系统调用时加一
	syscalltick uint32
	// 用于 sysmon 线程记录被监控 p 的系统调用时间和运行时间
	sysmontick  sysmontick // last tick observed by sysmon
	// 指向绑定的 m，如果 p 是 idle 的话，那这个指针是 nil
	m           muintptr   // back-link to associated m (nil if idle)
	mcache      *mcache
	racectx     uintptr

	deferpool    [5][]*_defer // pool of available defer structs of different sizes (see panic.go)
	deferpoolbuf [5][32]*_defer

	// Cache of goroutine ids, amortizes accesses to runtime·sched.goidgen.
	goidcache    uint64
	goidcacheend uint64

	// Queue of runnable goroutines. Accessed without lock.
	// 本地可运行的队列，不用通过锁即可访问
	runqhead uint32 // 队列头
	runqtail uint32 // 队列尾
	// 使用数组实现的循环队列
	runq     [256]guintptr

	// runnext 非空时，代表的是一个 runnable 状态的 G，
	// 这个 G 被 当前 G 修改为 ready 状态，相比 runq 中的 G 有更高的优先级。
	// 如果当前 G 还有剩余的可用时间，那么就应该运行这个 G
	// 运行之后，该 G 会继承当前 G 的剩余时间
	runnext guintptr

	// Available G's (status == Gdead)
	// 空闲的 g
	gfree    *g
	gfreecnt int32

	sudogcache []*sudog
	sudogbuf   [128]*sudog

	tracebuf traceBufPtr
	traceSwept, traceReclaimed uintptr

	palloc persistentAlloc // per-P to avoid mutex

	// Per-P GC state
	gcAssistTime     int64 // Nanoseconds in assistAlloc
	gcBgMarkWorker   guintptr
	gcMarkWorkerMode gcMarkWorkerMode
	runSafePointFn uint32 // if 1, run sched.safePointFn at next safe point

	pad [sys.CacheLineSize]byte
}
```

GPM 三足鼎力，共同成就 Go scheduler。G 需要在 M 上才能运行，M 依赖 P 提供的资源，P 则持有待运行的 G。你中有我，我中有你。

描述三者的关系：

![曹大 golang notes GPM 三者关系](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/sched/assets/14.png)

M 会从与它绑定的 P 的本地队列获取可运行的 G，也会从 network poller 里获取可运行的 G，还会从其他 P 偷 G。

最后我们从宏观上总结一下 GPM，这篇文章尝试从它们的状态流转角度总结。

首先是 G 的状态流转：

![G 的状态流转图](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/sched/assets/15.png)

说明一下，上图省略了一些垃圾回收的状态。

接着是 P 的状态流转：

![P 的状态流转图](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/sched/assets/16.png)

> 通常情况下（在程序运行时不调整 P 的个数），P 只会在上图中的四种状态下进行切换。 当程序刚开始运行进行初始化时，所有的 P 都处于 `_Pgcstop` 状态， 随着 P 的初始化（`runtime.procresize`），会被置于 `_Pidle`。

> 当 M 需要运行时，会 `runtime.acquirep` 来使 P 变成 `Prunning` 状态，并通过 `runtime.releasep` 来释放。 

> 当 G 执行时需要进入系统调用，P 会被设置为 `_Psyscall`， 如果这个时候被系统监控抢夺（`runtime.retake`），则 P 会被重新修改为 `_Pidle`。 

> 如果在程序运行中发生 `GC`，则 P 会被设置为 `_Pgcstop`， 并在 `runtime.startTheWorld` 时重新调整为 `_Prunning`。

最后，我们来看 M 的状态变化：

![M 的状态流转图](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/sched/assets/17.png)

M 只有自旋和非自旋两种状态。自旋的时候，会努力找工作；找不到的时候会进入非自旋状态，之后会休眠，直到有工作需要处理时，被其他工作线程唤醒，又进入自旋状态。

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/sched/6-GPM%20%E6%98%AF%E4%BB%80%E4%B9%88.md#L3)，来源许可：GPL-3.0。

<a id="ke816989d149f"></a>

## Provider、Model、Agent Runtime、Channel 如何解耦？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

这四个概念经常被混在一起，但工程上必须拆开：

| 概念 | 含义 | 例子 |
| --- | --- | --- |
| Provider | 模型或 Agent 能力的供应方 | OpenAI、Anthropic、本地模型服务、企业私有网关 |
| Model | 具体推理模型 | GPT、Claude、Gemini、Qwen、Llama 等具体版本 |
| Agent Runtime | 负责模型循环和工具执行的运行时 | 编码 Agent runtime、浏览器 Agent runtime、多模态 Agent runtime |
| Channel | 用户或事件进入 Agent 的通道 | CLI、IDE、Slack、Discord、Web、Webhook、Cron |

解耦的好处：

- 同一个 channel 可以切换不同 runtime。
- 同一个 runtime 可以接多个 provider/model。
- 同一个模型可以服务编码、浏览器、客服、数据分析等不同 Agent。
- 企业可以通过配置控制模型供应商，而不改业务入口。
- 运行时可以独立处理上下文压缩、工具协议、权限和 tracing。

运行时选择通常需要回答几个问题：

- 谁拥有模型 loop？
- 谁保存 canonical thread history？
- 工具调用是模型原生支持，还是运行时模拟？
- 动态工具、MCP、hooks、subagent 是否可用？
- 上下文压缩和 session 恢复由谁负责？
- 当指定 runtime 不可用时，是降级、排队还是失败？

面试中可以说：Provider / Model 解决“用什么脑”，Runtime 解决“怎么思考和行动”，Channel 解决“从哪里接活”。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/02_%E7%BC%96%E7%A0%81Agent%E4%B8%8EAgentOS%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L896)，来源许可：GPL-3.0。

<a id="kd7c47ef3c674"></a>

## 主 goroutine 如何创建

上一讲我们讲完了 Go scheduler 的初始化，现在调度器一切就绪，就差被调度的实体了。本文就来讲述 main goroutine 是如何诞生，并且被调度的。

继续看代码，前面我们完成了 `schedinit` 函数，这是 runtime·rt0_go 函数里的一步，接着往后看：

```asm
// 创建一个新的 goroutine 来启动程序
MOVQ	$runtime·mainPC(SB), AX		// entry
// newproc 的第二个参数入栈，也就是新的 goroutine 需要执行的函数
// AX = &funcval{runtime·main},
PUSHQ	AX
// newproc 的第一个参数入栈，该参数表示 runtime.main 函数需要的参数大小，
// 因为 runtime.main 没有参数，所以这里是 0
PUSHQ	$0			// arg size
// 创建 main goroutine
CALL	runtime·newproc(SB)
POPQ	AX
POPQ	AX

// start this M
// 主线程进入调度循环，运行刚刚创建的 goroutine
CALL	runtime·mstart(SB)

// 永远不会返回，万一返回了，crash 掉
MOVL	$0xf1, 0xf1  // crash
RET
```

代码前面几行是在为调用 newproc 函数构“造栈”，执行完 `runtime·newproc(SB)` 后，就会以一个新的 goroutine 来执行 mainPC 也就是 `runtime.main()` 函数。`runtime.main()` 函数最终会执行到我们写的 main 函数，舞台交给我们。

重点来看 `newproc` 函数：

```golang
// src/runtime/proc.go
// 创建一个新的 g，运行 fn 函数，需要 siz byte 的参数
// 将其放至 G 队列等待运行
// 编译器会将 go 关键字的语句转化成此函数

//go:nosplit
func newproc(siz int32, fn *funcval)
```

从这里开始要进入 hard 模式了，打起精神！当我们随手一句：

```golang
go func() {
    // 要做的事
}()
```

就启动了一个 goroutine 的时候，一定要知道，在 Go 编译器的作用下，这条语句最终会转化成 newproc 函数。

因此，`newproc` 函数需要两个参数：一个是新创建的 goroutine 需要执行的任务，也就是 fn，它代表一个函数 func；还有一个是 fn 的参数大小。

再回过头看，构造 newproc 函数调用栈的时候，第一个参数是 0，因为 runtime.main 函数没有参数：

```golang
// src/runtime/proc.go

func main()
```

第二个参数则是 runtime.main 函数的地址。

可能会感到奇怪，为什么要给 `newproc` 传一个表示 fn 的参数大小的参数呢？

我们知道，goroutine 和线程一样，都有自己的栈，不同的是 goroutine 的初始栈比较小，只有 2K，而且是可伸缩的，这也是创建 goroutine 的代价比创建线程代价小的原因。

换句话说，每个 goroutine 都有自己的栈空间，newproc 函数会新创建一个新的 goroutine 来执行 fn 函数，在新 goroutine 上执行指令，就要用新 goroutine 的栈。而执行函数需要参数，这个参数又是在老的 goroutine 上，所以需要将其拷贝到新 goroutine 的栈上。拷贝的起始位置就是栈顶，这好办，那拷贝多少数据呢？由 siz 来确定。

继续看代码，newproc 函数的第二个参数：

```golang
type funcval struct {
	fn uintptr
	// variable-size, fn-specific data here
}
```

它是一个变长结构，第一个字段是一个指针 fn，内存中，紧挨着 fn 的是函数的参数。

参考资料【欧神 关键字 go】有一个例子：

```golang
package main

func hello(msg string) {
	println(msg)
}

func main() {
	go hello("hello world")
}
```

栈布局是这样的：

![fn 与函数参数](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/sched/assets/25.png)

栈顶是 siz，再往上是函数的地址，再往上就是传给 hello 函数的参数，string 在这里是一个地址。因此前面代码里先 push 参数的地址，再 push 参数大小。

```golang
// src/runtime/proc.go

//go:nosplit
func newproc(siz int32, fn *funcval) {
	// 获取第一个参数地址
	argp := add(unsafe.Pointer(&fn), sys.PtrSize)
	// 获取调用者的指令地址，也就是调用 newproc 时由 call 指令压栈的函数返回地址
	pc := getcallerpc(unsafe.Pointer(&siz))
	// systemstack 的作用是切换到 g0 栈执行作为参数的函数
	// 用 g0 系统栈创建 goroutine 对象
    // 传递的参数包括 fn 函数入口地址，argp 参数起始地址，siz 参数长度，调用方 pc（goroutine）

	systemstack(func() {
		newproc1(fn, (*uint8)(argp), siz, 0, pc)
	})
}
```

因此，argp 跳过 fn，向上跳一个指针的长度，拿到 fn 参数的地址。

接着通过 getcallerpc 获取调用者的指令地址，也就是调用 newproc 时由 call 指令压栈的函数返回地址，也就是 `runtime·rt0_go` 函数里 `CALL runtime·newproc(SB)` 指令后面的 `POPQ AX` 这条指令的地址。

最后，调用 systemstack 函数在 g0 栈执行 fn 函数。由于本文讲述的是初始化过程中，由 `runtime·rt0_go` 函数调用，本身是在 g0 栈执行，因此会直接执行 fn 函数。而如果是我们在程序中写的 `go xxx` 代码，在执行时，就会先切换到 g0 栈执行，然后再切回来。

一鼓作气，继续看 `newproc1` 函数，为了连贯性，我先将整个函数的代码贴出来，并且加上了注释。当然，这篇文章不会涉及到所有的代码，只会讲部分内容。放在这里，方便阅读后面的文章时对照：

```golang
// 创建一个新的 g 来跑 fn
func newproc1(fn *funcval, argp *uint8, narg int32, nret int32, callerpc uintptr) *g {
	// 当前 goroutine 的指针
	// 因为已经切换到 g0 栈，所以无论什么场景都是 _g_ = g0
	// g0 是指当前工作线程的 g0
	_g_ := getg()

	if fn == nil {
		_g_.m.throwing = -1 // do not dump full stacks
		throw("go of nil func value")
	}
	_g_.m.locks++ // disable preemption because it can be holding p in a local var

	// 参数加返回值所需要的空间（经过内存对齐）
	siz := narg + nret
	siz = (siz + 7) &^ 7

	// …………………………

	// 当前工作线程所绑定的 p
	// 初始化时 _p_ = g0.m.p，也就是 _p_ = allp[0]
	_p_ := _g_.m.p.ptr()
	// 从 p 的本地缓冲里获取一个没有使用的 g，初始化时为空，返回 nil
	newg := gfget(_p_)
	if newg == nil {
		// new 一个 g 结构体对象，然后从堆上为其分配栈，并设置 g 的 stack 成员和两个 stackgard 成员
		newg = malg(_StackMin)
		// 初始化 g 的状态为 _Gdead
		casgstatus(newg, _Gidle, _Gdead)
		// 放入全局变量 allgs 切片中
		allgadd(newg) // publishes with a g->status of Gdead so GC scanner doesn't look at uninitialized stack.
	}
	if newg.stack.hi == 0 {
		throw("newproc1: newg missing stack")
	}

	if readgstatus(newg) != _Gdead {
		throw("newproc1: new g is not Gdead")
	}

	// 计算运行空间大小，对齐
	totalSize := 4*sys.RegSize + uintptr(siz) + sys.MinFrameSize // extra space in case of reads slightly beyond frame
	totalSize += -totalSize & (sys.SpAlign - 1)                  // align to spAlign
	// 确定 sp 位置
	sp := newg.stack.hi - totalSize
	// 确定参数入栈位置
	spArg := sp

	// …………………………

	if narg > 0 {
		// 将参数从执行 newproc 函数的栈拷贝到新 g 的栈
		memmove(unsafe.Pointer(spArg), unsafe.Pointer(argp), uintptr(narg))

		// …………………………
	}

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
	if isSystemGoroutine(newg) {
		atomic.Xadd(&sched.ngsys, +1)
	}
	newg.gcscanvalid = false
	// 设置 g 的状态为 _Grunnable，可以运行了
	casgstatus(newg, _Gdead, _Grunnable)

	if _p_.goidcache == _p_.goidcacheend {
		_p_.goidcache = atomic.Xadd64(&sched.goidgen, _GoidCacheBatch)
		_p_.goidcache -= _GoidCacheBatch - 1
		_p_.goidcacheend = _p_.goidcache + _GoidCacheBatch
	}
	// 设置 goid
	newg.goid = int64(_p_.goidcache)
	_p_.goidcache++

	// ……………………

	// 将 G 放入 _p_ 的本地待运行队列
	runqput(_p_, newg, true)

	if atomic.Load(&sched.npidle) != 0 && atomic.Load(&sched.nmspinning) == 0 && mainStarted {
		wakep()
	}
	_g_.m.locks--
	if _g_.m.locks == 0 && _g_.preempt {
		_g_.stackguard0 = stackPreempt
	}
	return newg
}
```

当前代码在 g0 栈上执行，因此执行完 `_g_ := getg()` 之后，无论是在什么情况下都可以得到 `_g_ = g0`。之后通过 g0 找到其绑定的 P，也就是 p0。

接着，尝试从 p0 上找一个空闲的 G：

```golang
// 从 p 的本地缓冲里获取一个没有使用的 g，初始化时为空，返回 nil
newg := gfget(_p_)
```

如果拿不到，则会在堆上创建一个新的 G，为其分配 2KB 大小的栈，并设置好新 goroutine 的 stack 成员，设置其状态为 _Gdead，并将其添加到全局变量 allgs 中。创建完成之后，我们就在堆上有了一个 2K 大小的栈。于是，我们的图再次丰富：

![创建了新的 goroutine](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/sched/assets/26.png)

这样，main goroutine 就诞生了。

### 参考资料

【欧神 关键字 go】https://github.com/changkun/go-under-the-hood/blob/master/book/zh-cn/part3compile/ch11keyword/go.md

【欧神 Go scheduler】https://github.com/changkun/go-under-the-hood/blob/master/book/zh-cn/part2runtime/ch06sched/init.md

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/sched/8-main%20goroutine%20%E5%A6%82%E4%BD%95%E5%88%9B%E5%BB%BA.md#L3)，来源许可：GPL-3.0。

<a id="k3b89060ac225"></a>

## 什么是 CSP

> Do not communicate by sharing memory; instead, share memory by communicating.

不要通过共享内存来通信，而要通过通信来实现内存共享。

这就是 Go 的并发哲学，它依赖 CSP 模型，基于 channel 实现。

CSP 经常被认为是 Go 在并发编程上成功的关键因素。CSP 全称是 “Communicating Sequential Processes”，这也是 Tony Hoare 在 1978 年发表在 ACM 的一篇论文。论文里指出一门编程语言应该重视 input 和 output 的原语，尤其是并发编程的代码。

在那篇文章发表的时代，人们正在研究模块化编程的思想，该不该用 goto 语句在当时是最激烈的议题。彼时，面向对象编程的思想正在崛起，几乎没什么人关心并发编程。

在文章中，CSP 也是一门自定义的编程语言，作者定义了输入输出语句，用于 processes 间的通信（communication）。processes 被认为是需要输入驱动，并且产生输出，供其他 processes 消费，processes 可以是进程、线程、甚至是代码块。输入命令是：!，用来向 processes 写入；输出是：?，用来从 processes 读出。这篇文章要讲的 channel 正是借鉴了这一设计。

Hoare 还提出了一个 -> 命令，如果 -> 左边的语句返回 false，那它右边的语句就不会执行。

通过这些输入输出命令，Hoare 证明了如果一门编程语言中把 processes 间的通信看得第一等重要，那么并发编程的问题就会变得简单。

Go 是第一个将 CSP 的这些思想引入，并且发扬光大的语言。仅管内存同步访问控制（原文是 memory access synchronization）在某些情况下大有用处，Go 里也有相应的 sync 包支持，但是这在大型程序很容易出错。

Go 一开始就把 CSP 的思想融入到语言的核心里，所以并发编程成为 Go 的一个独特的优势，而且很容易理解。

大多数的编程语言的并发编程模型是基于线程和内存同步访问控制，Go 的并发编程的模型则用 goroutine 和 channel 来替代。Goroutine 和线程类似，channel 和 mutex (用于内存同步访问控制)类似。

Goroutine 解放了程序员，让我们更能贴近业务去思考问题。而不用考虑各种像线程库、线程开销、线程调度等等这些繁琐的底层问题，goroutine 天生替你解决好了。

Channel 则天生就可以和其他 channel 组合。我们可以把收集各种子系统结果的 channel 输入到同一个 channel。Channel 还可以和 select, cancel, timeout 结合起来。而 mutex 就没有这些功能。

Go 的并发原则非常优秀，目标就是简单：尽量使用 channel；把 goroutine 当作免费的资源，随便用。

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/channel/1-%E4%BB%80%E4%B9%88%E6%98%AF%20CSP.md#L3)，来源许可：GPL-3.0。

<a id="kd6f642cd8909"></a>

## 传递共享的数据

对于 Web 服务端开发，往往希望将一个请求处理的整个过程串起来，这就非常依赖于 Thread Local（对于 Go 可理解为单个协程所独有） 的变量，而在 Go 语言中并没有这个概念，因此需要在函数调用的时候传递 context。

```golang
package main

import (
	"context"
	"fmt"
)

func main() {
	ctx := context.Background()
	process(ctx)

	ctx = context.WithValue(ctx, "traceId", "qcrao-2019")
	process(ctx)
}

func process(ctx context.Context) {
	traceId, ok := ctx.Value("traceId").(string)
	if ok {
		fmt.Printf("process over. trace_id=%s\n", traceId)
	} else {
		fmt.Printf("process over. no trace_id\n")
	}
}
```

运行结果：

```shell
process over. no trace_id
process over. trace_id=qcrao-2019
```

第一次调用 process 函数时，ctx 是一个空的 context，自然取不出来 traceId。第二次，通过 `WithValue` 函数创建了一个 context，并赋上了 `traceId` 这个 key，自然就能取出来传入的 value 值。

当然，现实场景中可能是从一个 HTTP 请求中获取到的 Request-ID。所以，下面这个样例可能更适合：

```golang
const requestIDKey int = 0

func WithRequestID(next http.Handler) http.Handler {
	return http.HandlerFunc(
		func(rw http.ResponseWriter, req *http.Request) {
			// 从 header 中提取 request-id
			reqID := req.Header.Get("X-Request-ID")
			// 创建 valueCtx。使用自定义的类型，不容易冲突
			ctx := context.WithValue(
				req.Context(), requestIDKey, reqID)

			// 创建新的请求
			req = req.WithContext(ctx)

			// 调用 HTTP 处理函数
			next.ServeHTTP(rw, req)
		}
	)
}

// 获取 request-id
func GetRequestID(ctx context.Context) string {
	return ctx.Value(requestIDKey).(string)
}

func Handle(rw http.ResponseWriter, req *http.Request) {
	// 拿到 reqId，后面可以记录日志等等
	reqID := GetRequestID(req.Context())
	...
}

func main() {
	handler := WithRequestID(http.HandlerFunc(Handle))
	http.ListenAndServe("/", handler)
}
```

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/stdlib/context/2-context%20%E6%9C%89%E4%BB%80%E4%B9%88%E4%BD%9C%E7%94%A8.md#L62)，来源许可：GPL-3.0。

<a id="k34b60078e550"></a>

## 关于 channel 的 happened-before 有哪些

维基百科上给的定义：

> In computer science, the happened-before relation (denoted: ->) is a relation between the result of two events, such that if one event should happen before another event, the result must reflect that, even if those events are in reality executed out of order (usually to optimize program flow).

简单来说就是如果事件 a 和事件 b 存在 happened-before 关系，即 a -> b，那么 a，b 完成后的结果一定要体现这种关系。由于现代编译器、CPU 会做各种优化，包括编译器重排、内存重排等等，在并发代码里，happened-before 限制就非常重要了。

根据晃岳攀老师在 Gopher China 2019 上的并发编程分享，关于 channel 的发送（send）、发送完成（send finished）、接收（receive）、接收完成（receive finished）的 happened-before 关系如下：

1. 第 n 个 `send` 一定 `happened before` 第 n 个 `receive finished`，无论是缓冲型还是非缓冲型的 channel。
2. 对于容量为 m 的缓冲型 channel，第 n 个 `receive` 一定 `happened before` 第 n+m 个 `send finished`。
3. 对于非缓冲型的 channel，第 n 个 `receive` 一定 `happened before` 第 n 个 `send finished`。
4. channel close 一定 `happened before` receiver 得到通知。

我们来逐条解释一下。

第一条，我们从源码的角度看也是对的，send 不一定是 `happened before` receive，因为有时候是先 receive，然后 goroutine 被挂起，之后被 sender 唤醒，send happened after receive。但不管怎样，要想完成接收，一定是要先有发送。

第二条，缓冲型的 channel，当第 n+m 个 send 发生后，有下面两种情况：

若第 n 个 receive 没发生。这时，channel 被填满了，send 就会被阻塞。那当第 n 个 receive 发生时，sender goroutine 会被唤醒，之后再继续发送过程。这样，第 n 个 `receive` 一定 `happened before` 第 n+m 个 `send finished`。

若第 n 个 receive 已经发生过了，这直接就符合了要求。

第三条，也是比较好理解的。第 n 个 send 如果被阻塞，sender goroutine 挂起，第 n 个 receive 这时到来，先于第 n 个 send finished。如果第 n 个 send 未被阻塞，说明第 n 个 receive 早就在那等着了，它不仅 happened before send finished，它还 happened before send。

第四条，回忆一下源码，先设置完 closed = 1，再唤醒等待的 receiver，并将零值拷贝给 receiver。

参考资料【鸟窝 并发编程分享】这篇博文的评论区有 PPT 的下载链接，这是晁老师在 Gopher 2019 大会上的演讲。

关于 happened before，这里再介绍一个柴大和曹大的新书《Go 语言高级编程》里面提到的一个例子。

书中 1.5 节先讲了顺序一致性的内存模型，这是并发编程的基础。

我们直接来看例子：

```golang
var done = make(chan bool)
var msg string

func aGoroutine() {
	msg = "hello, world"
	done <- true
}

func main() {
	go aGoroutine()
	<-done
	println(msg)
}
```

先定义了一个 done channel 和一个待打印的字符串。在 main 函数里，启动一个 goroutine，等待从 done 里接收到一个值后，执行打印 msg 的操作。如果 main 函数中没有 `<-done` 这行代码，打印出来的 msg 为空，因为 aGoroutine 来不及被调度，还来不及给 msg 赋值，主程序就会退出。而在 Go 语言里，主协程退出时不会等待其他协程。

加了 `<-done` 这行代码后，就会阻塞在此。等 aGoroutine 里向 done 发送了一个值之后，才会被唤醒，继续执行打印 msg 的操作。而这在之前，msg 已经被赋值过了，所以会打印出 `hello, world`。

这里依赖的 happened before 就是前面讲的第一条。第一个 send 一定 happened before 第一个 receive finished，即 `done <- true` 先于 `<-done` 发生，这意味着 main 函数里执行完 `<-done` 后接着执行 `println(msg)` 这一行代码时，msg 已经被赋过值了，所以会打印出想要的结果。

进一步利用前面提到的第 3 条 happened before 规则，修改一下代码：

```golang
var done = make(chan bool)
var msg string

func aGoroutine() {
	msg = "hello, world"
	<-done
}

func main() {
	go aGoroutine()
	done <- true
	println(msg)
}
```

同样可以得到相同的结果，为什么？根据第三条规则，对于非缓冲型的 channel，第一个 receive 一定 happened before 第一个 send finished。也就是说，
在 `done <- true` 完成之前，`<-done` 就已经发生了，也就意味着 msg 已经被赋上值了，最终也会打印出 `hello, world`。

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/channel/11-%E5%85%B3%E4%BA%8E%20channel%20%E7%9A%84%20happened-before%20%E6%9C%89%E5%93%AA%E4%BA%9B.md#L3)，来源许可：GPL-3.0。

<a id="k27de8afcdaa7"></a>

## 取消 goroutine

我们先来设想一个场景：打开外卖的订单页，地图上显示外卖小哥的位置，而且是每秒更新 1 次。app 端向后台发起 websocket 连接（现实中可能是轮询）请求后，后台启动一个协程，每隔 1 秒计算 1 次小哥的位置，并发送给端。如果用户退出此页面，则后台需要“取消”此过程，退出 goroutine，系统回收资源。

后端可能的实现如下：

```golang
func Perform() {
    for {
        calculatePos()
        sendResult()
        time.Sleep(time.Second)
    }
}
```

如果需要实现“取消”功能，并且在不了解 context 功能的前提下，可能会这样做：给函数增加一个指针型的 bool 变量，在 for 语句的开始处判断 bool 变量是发由 true 变为 false，如果改变，则退出循环。

上面给出的简单做法，可以实现想要的效果，没有问题，但是并不优雅，并且一旦协程数量多了之后，并且各种嵌套，就会很麻烦。优雅的做法，自然就要用到 context。

```golang
func Perform(ctx context.Context) {
    for {
        calculatePos()
        sendResult()

        select {
        case <-ctx.Done():
            // 被取消，直接返回
            return
        case <-time.After(time.Second):
            // block 1 秒钟 
        }
    }
}
```

主流程可能是这样的：

```golang
ctx, cancel := context.WithTimeout(context.Background(), time.Hour)
go Perform(ctx)

// ……
// app 端返回页面，调用cancel 函数
cancel()
```

注意一个细节，WithTimeOut 函数返回的 context 和 cancelFun 是分开的。context 本身并没有取消函数，这样做的原因是取消函数只能由外层函数调用，防止子节点 context 调用取消函数，从而严格控制信息的流向：由父节点 context 流向子节点 context。

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/stdlib/context/2-context%20%E6%9C%89%E4%BB%80%E4%B9%88%E4%BD%9C%E7%94%A8.md#L141)，来源许可：GPL-3.0。

<a id="kfc98e442c134"></a>

## 多平台会话如何做 session、user、channel、workspace 隔离？

多平台 Agent 最怕上下文串线。设计 session scope 时应显式包含：

- platform：Telegram、Slack、Discord、Email、CLI。
- account / workspace：企业或组织空间。
- channel：群、频道、私聊、邮件线程。
- user：用户身份。
- agent_id：不同 Agent 或人格。
- task_id：长任务或后台任务。

常见隔离策略：

| Scope | 适用场景 | 风险控制 |
| --- | --- | --- |
| per-user | 私人助理 | 防止不同用户共享上下文 |
| per-channel | 群聊 / 频道 | 防止群聊内容进入私聊 |
| per-thread | Slack / 邮件线程 | 保持任务上下文局部 |
| per-workspace | 企业多租户 | 防止跨组织数据泄露 |
| per-task | 长任务 / cron | 防止后台任务污染主会话 |

关键原则：

- 默认最小共享。
- 私聊和群聊分离。
- 工作区和租户分离。
- 自动任务独立 session。
- reset、resume、archive 有明确规则。
- 每次 trace 记录完整 scope。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/09_%E8%87%AA%E8%BF%9B%E5%8C%96Agent%E4%B8%8E%E5%A4%9A%E5%B9%B3%E5%8F%B0%E8%BF%90%E8%A1%8C%E6%97%B6%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L211)，来源许可：GPL-3.0。

<a id="k0b8579ec9079"></a>

## 如何优雅地关闭 channel

关于 channel 的使用，有几点不方便的地方：

1. 在不改变 channel 自身状态的情况下，无法获知一个 channel 是否关闭。
2. 关闭一个 closed channel 会导致 panic。所以，如果关闭 channel 的一方在不知道 channel 是否处于关闭状态时就去贸然关闭 channel 是很危险的事情。
3. 向一个 closed channel 发送数据会导致 panic。所以，如果向 channel 发送数据的一方不知道 channel 是否处于关闭状态时就去贸然向 channel 发送数据是很危险的事情。

一个比较粗糙的检查 channel 是否关闭的函数：

```golang
func IsClosed(ch <-chan T) bool {
	select {
	case <-ch:
		return true
	default:
	}

	return false
}

func main() {
	c := make(chan T)
	fmt.Println(IsClosed(c)) // false
	close(c)
	fmt.Println(IsClosed(c)) // true
}
```

看一下代码，其实存在很多问题。首先，IsClosed 函数是一个有副作用的函数。每调用一次，都会读出 channel 里的一个元素，改变了 channel 的状态。这不是一个好的函数，干活就干活，还顺手牵羊！

其次，IsClosed 函数返回的结果仅代表调用那个瞬间，并不能保证调用之后会不会有其他 goroutine 对它进行了一些操作，改变了它的这种状态。例如，IsClosed 函数返回 false，但这时有另一个 goroutine 关闭了 channel，而你还拿着这个过时的 “channel 未关闭”的信息，向其发送数据，就会导致 panic 的发生。当然，一个 channel 不会被重复关闭两次，如果 IsClosed 函数返回的结果是 true，说明 channel 是真的关闭了。

有一条广泛流传的关闭 channel 的原则：

> don't close a channel from the receiver side and don't close a channel if the channel has multiple concurrent senders.

不要从一个 receiver 侧关闭 channel，也不要在有多个 sender 时，关闭 channel。

比较好理解，向 channel 发送元素的就是 sender，因此 sender 可以决定何时不发送数据，并且关闭 channel。但是如果有多个 sender，某个 sender 同样没法确定其他 sender 的情况，这时也不能贸然关闭 channel。

但是上面所说的并不是最本质的，最本质的原则就只有一条：

> don't close (or send values to) closed channels.

有两个不那么优雅地关闭 channel 的方法：

1. 使用 defer-recover 机制，放心大胆地关闭 channel 或者向 channel 发送数据。即使发生了 panic，有 defer-recover 在兜底。

2. 使用 sync.Once 来保证只关闭一次。

那到底应该如何优雅地关闭 channel？

根据 sender 和 receiver 的个数，分下面几种情况：

1. 一个 sender，一个 receiver
2. 一个 sender， M 个 receiver
3. N 个 sender，一个 reciver
4. N 个 sender， M 个 receiver

对于 1，2，只有一个 sender 的情况就不用说了，直接从 sender 端关闭就好了，没有问题。重点关注第 3，4 种情况。

第 3 种情形下，优雅关闭 channel 的方法是：the only receiver says "please stop sending more" by closing an additional signal channel。

解决方案就是增加一个传递关闭信号的 channel，receiver 通过信号 channel 下达关闭数据 channel 指令。senders 监听到关闭信号后，停止发送数据。代码如下：

```golang
func main() {
	rand.Seed(time.Now().UnixNano())

	const Max = 100000
	const NumSenders = 1000

	dataCh := make(chan int, 100)
	stopCh := make(chan struct{})

	// senders
	for i := 0; i < NumSenders; i++ {
		go func() {
			for {
				select {
				case <- stopCh:
					return
				case dataCh <- rand.Intn(Max):
				}
			}
		}()
	}

	// the receiver
	go func() {
		for value := range dataCh {
			if value == Max-1 {
				fmt.Println("send stop signal to senders.")
				close(stopCh)
				return
			}

			fmt.Println(value)
		}
	}()

	select {
	case <- time.After(time.Hour):
	}
}
```

这里的 stopCh 就是信号 channel，它本身只有一个 sender，因此可以直接关闭它。senders 收到了关闭信号后，select 分支 “case <- stopCh” 被选中，退出函数，不再发送数据。

需要说明的是，上面的代码并没有明确关闭 dataCh。在 Go 语言中，对于一个 channel，如果最终没有任何 goroutine 引用它，不管 channel 有没有被关闭，最终都会被 gc 回收。所以，在这种情形下，所谓的优雅地关闭 channel 就是不关闭 channel，让 gc 代劳。

最后一种情况，优雅关闭 channel 的方法是：any one of them says "let's end the game" by notifying a moderator to close an additional signal channel。

和第 3 种情况不同，这里有 M 个 receiver，如果直接还是采取第 3 种解决方案，由 receiver 直接关闭 stopCh 的话，就会重复关闭一个 channel，导致 panic。因此需要增加一个中间人，M 个 receiver 都向它发送关闭 dataCh 的“请求”，中间人收到第一个请求后，就会直接下达关闭 dataCh 的指令（通过关闭 stopCh，这时就不会发生重复关闭的情况，因为 stopCh 的发送方只有中间人一个）。另外，这里的 N 个 sender 也可以向中间人发送关闭 dataCh 的请求。

```golang
func main() {
	rand.Seed(time.Now().UnixNano())

	const Max = 100000
	const NumReceivers = 10
	const NumSenders = 1000

	dataCh := make(chan int, 100)
	stopCh := make(chan struct{})

	// It must be a buffered channel.
	toStop := make(chan string, 1)

	var stoppedBy string

	// moderator
	go func() {
		stoppedBy = <-toStop
		close(stopCh)
	}()

	// senders
	for i := 0; i < NumSenders; i++ {
		go func(id string) {
			for {
				value := rand.Intn(Max)
				if value == 0 {
					select {
					case toStop <- "sender#" + id:
					default:
					}
					return
				}

				select {
				case <- stopCh:
					return
				case dataCh <- value:
				}
			}
		}(strconv.Itoa(i))
	}

	// receivers
	for i := 0; i < NumReceivers; i++ {
		go func(id string) {
			for {
				select {
				case <- stopCh:
					return
				case value := <-dataCh:
					if value == Max-1 {
						select {
						case toStop <- "receiver#" + id:
						default:
						}
						return
					}

					fmt.Println(value)
				}
			}
		}(strconv.Itoa(i))
	}

	select {
	case <- time.After(time.Hour):
	}

}
```

代码里 toStop 就是中间人的角色，使用它来接收 senders 和 receivers 发送过来的关闭 dataCh 请求。

这里将 toStop 声明成了一个 缓冲型的 channel。假设 toStop 声明的是一个非缓冲型的 channel，那么第一个发送的关闭 dataCh 请求可能会丢失。因为无论是 sender 还是 receiver 都是通过 select 语句来发送请求，如果中间人所在的 goroutine 没有准备好，那 select 语句就不会选中，直接走 default 选项，什么也不做。这样，第一个关闭 dataCh 的请求就会丢失。

如果，我们把 toStop 的容量声明成 Num(senders) + Num(receivers)，那发送 dataCh 请求的部分可以改成更简洁的形式：

```golang
...
toStop := make(chan string, NumReceivers + NumSenders)
...
			value := rand.Intn(Max)
			if value == 0 {
				toStop <- "sender#" + id
				return
			}
...
				if value == Max-1 {
					toStop <- "receiver#" + id
					return
				}
...
```

直接向 toStop 发送请求，因为 toStop 容量足够大，所以不用担心阻塞，自然也就不用 select 语句再加一个 default case 来避免阻塞。

可以看到，这里同样没有真正关闭 dataCh，原样同第 3 种情况。

以上，就是最基本的一些情形，但已经能覆盖几乎所有的情况及其变种了。只要记住：

以及更本质的原则：

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/channel/8-%E5%A6%82%E4%BD%95%E4%BC%98%E9%9B%85%E5%9C%B0%E5%85%B3%E9%97%AD%20channel.md#L3)，来源许可：GPL-3.0。

<a id="ke38430703e5c"></a>

## 并发标记清除法的难点是什么？

在没有用户态代码并发修改`三色抽象`的情况下，回收可以正常结束。但是并发回收的根本问题在于，用户态代码在回收过程中会并发地更新对象图，从而造成赋值器和回收器可能对对象图的结构产生不同的认知。这时以一个固定的三色波面作为回收过程前进的边界则不再合理。

我们不妨考虑赋值器写操作的例子：

| 时序 | 回收器               | 赋值器             | 说明                                                         |
| ---- | -------------------- | ------------------ | ------------------------------------------------------------ |
| 1    | shade(A, gray)       |                    | 回收器：根对象的子节点着色为灰色对象                         |
| 2    | shade(C, black) |                    | 回收器：当所有子节点着色为灰色后，将节点着为黑色             |
| 3    |                      | C.ref3 = C.ref2.ref1   | 赋值器：并发的修改了 C 的子节点                              |
| 4    |                      | A.ref1 = nil | 赋值器：并发的修改了 A 的子节点                              |
| 5    | shade(A.ref1, gray)  |                    | 回收器：进一步灰色对象的子节点并着色为灰色对象，这时由于 `A.ref1` 为 `nil`，什么事情也没有发生 |
| 6    | shade(A, black)      |                    | 回收器：由于所有子节点均已标记，回收器也不会重新扫描已经被标记为黑色的对象，此时 A 被着色为黑色，`scan(A)` 什么也不会发生，进而 B 在此次回收过程中永远不会被标记为黑色，进而错误地被回收。 |

- 初始状态：假设某个黑色对象 C 指向某个灰色对象 A ，而 A 指向白色对象 B；
- `C.ref3 = C.ref2.ref1`：赋值器并发地将黑色对象 C 指向（ref3）了白色对象 B；
- `A.ref1 = nil`：移除灰色对象 A 对白色对象 B 的引用（ref1）；
- 最终状态：在继续扫描的过程中，白色对象 B 永远不会被标记为黑色对象了（回收器不会重新扫描黑色对象），进而对象 B 被错误地回收。

![gc-mutator](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/memgc/assets/gc-mutator.png)

总而言之，并发标记清除中面临的一个根本问题就是如何保证标记与清除过程的正确性。

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/memgc/1-%E5%9E%83%E5%9C%BE%E5%9B%9E%E6%94%B6%E7%9A%84%E8%AE%A4%E8%AF%86.md#L410)，来源许可：GPL-3.0。

<a id="kaa5dc7847780"></a>

## 案例分析

从 channel 接收和向 channel 发送数据的过程我们均会使用下面这个例子来进行说明：

```golang
func goroutineA(a <-chan int) {
	val := <- a
	fmt.Println("G1 received data: ", val)
	return
}

func goroutineB(b <-chan int) {
	val := <- b
	fmt.Println("G2 received data: ", val)
	return
}

func main() {
	ch := make(chan int)
	go goroutineA(ch)
	go goroutineB(ch)
	ch <- 3
	time.Sleep(time.Second)
}
```

首先创建了一个无缓冲的 channel，接着启动两个 goroutine，并将前面创建的 channel 传递进去。然后，向这个 channel 中发送数据 3，最后 sleep 1 秒后程序退出。

程序第 14 行创建了一个非缓冲型的 channel，我们只看 chan 结构体中的一些重要字段，来从整体层面看一下 chan 的状态，一开始什么都没有：

![unbuffered chan](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/channel/assets/4.png)

接着，第 15、16 行分别创建了一个 goroutine，各自执行了一个接收操作。通过前面的源码分析，我们知道，这两个 goroutine （后面称为 G1 和 G2 好了）都会被阻塞在接收操作。G1 和 G2 会挂在 channel 的 recq 队列中，形成一个双向循环链表。

在程序的 17 行之前，chan 的整体数据结构如下：

![chan struct at the runtime](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/channel/assets/5.png)

`buf` 指向一个长度为 0 的数组，qcount 为 0，表示 channel 中没有元素。重点关注 `recvq` 和 `sendq`，它们是 waitq 结构体，而 waitq 实际上就是一个双向链表，链表的元素是 sudog，里面包含 `g` 字段，`g` 表示一个 goroutine，所以 sudog 可以看成一个 goroutine。recvq 存储那些尝试读取 channel 但被阻塞的 goroutine，sendq 则存储那些尝试写入 channel，但被阻塞的 goroutine。

此时，我们可以看到，recvq 里挂了两个 goroutine，也就是前面启动的 G1 和 G2。因为没有 goroutine 接收，而 channel 又是无缓冲类型，所以 G1 和 G2 被阻塞。sendq 没有被阻塞的 goroutine。

`recvq` 的数据结构如下：

![recvq structure](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/channel/assets/6.png)

再从整体上来看一下 chan 此时的状态：

![chan state](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/channel/assets/7.png)

G1 和 G2 被挂起了，状态是 `WAITING`。关于 goroutine 调度器这块不是今天的重点，当然后面肯定会写相关的文章。这里先简单说下，goroutine 是用户态的协程，由 Go runtime 进行管理，作为对比，内核线程由 OS 进行管理。Goroutine 更轻量，因此我们可以轻松创建数万 goroutine。

一个内核线程可以管理多个 goroutine，当其中一个 goroutine 阻塞时，内核线程可以调度其他的 goroutine 来运行，内核线程本身不会阻塞。这就是通常我们说的 `M:N` 模型：

![M:N scheduling](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/channel/assets/8.png)

`M:N` 模型通常由三部分构成：M、P、G。M 是内核线程，负责运行 goroutine；P 是 context，保存 goroutine 运行所需要的上下文，它还维护了可运行（runnable）的 goroutine 列表；G 则是待运行的 goroutine。M 和 P 是 G 运行的基础。

![MGP](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/channel/assets/9.png)

继续回到例子。假设我们只有一个 M，当 G1（`go goroutineA(ch)`） 运行到 `val := <- a` 时，它由本来的 running 状态变成了 waiting 状态（调用了 gopark 之后的结果）：

![G1 running](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/channel/assets/10.png)

G1 脱离与 M 的关系，但调度器可不会让 M 闲着，所以会接着调度另一个 goroutine 来运行：

![G1 waiting](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/channel/assets/11.png)

G2 也是同样的遭遇。现在 G1 和 G2 都被挂起了，等待着一个 sender 往 channel 里发送数据，才能得到解救。

### 补充说明

好了，看完源码。我们接着来分析例子，代码如下：

```golang
func goroutineA(a <-chan int) {
	val := <- a
	fmt.Println("goroutine A received data: ", val)
	return
}

func goroutineB(b <-chan int) {
	val := <- b
	fmt.Println("goroutine B received data: ", val)
	return
}

func main() {
	ch := make(chan int)
	go goroutineA(ch)
	go goroutineB(ch)
	ch <- 3
	time.Sleep(time.Second)

	ch1 := make(chan struct{})
}
```

在发送小节里我们说到 G1 和 G2 现在被挂起来了，等待 sender 的解救。在第 17 行，主协程向 ch 发送了一个元素 3，来看下接下来会发生什么。

根据前面源码分析的结果，我们知道，sender 发现 ch 的 recvq 里有 receiver 在等待着接收，就会出队一个 sudog，把 recvq 里 first 指针的 sudo “推举”出来了，并将其加入到 P 的可运行 goroutine 队列中。

然后，sender 把发送元素拷贝到 sudog 的 elem 地址处，最后会调用 goready 将 G1 唤醒，状态变为 runnable。

![G1 runnable](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/channel/assets/2.png)

当调度器光顾 G1 时，将 G1 变成 running 状态，执行 goroutineA 接下来的代码。G 表示其他可能有的 goroutine。

这里其实涉及到一个协程写另一个协程栈的操作。有两个 receiver 在 channel 的一边虎视眈眈地等着，这时 channel 另一边来了一个 sender 准备向 channel 发送数据，为了高效，用不着通过 channel 的 buf “中转”一次，直接从源地址把数据 copy 到目的地址就可以了，效率高啊！

![send direct](https://raw.githubusercontent.com/golang-design/go-questions/741cb94826279e6879338565f09b3e71650278f6/content/channel/assets/3.png)

上图是一个示意图，`3` 会被拷贝到 G1 栈上的某个位置，也就是 val 的地址处，保存在 elem 字段。

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/channel/4-%E4%BB%8E%20channel%20%E6%8E%A5%E6%94%B6%E6%95%B0%E6%8D%AE%E7%9A%84%E8%BF%87%E7%A8%8B%E6%98%AF%E6%80%8E%E6%A0%B7%E7%9A%84.md#L291)，来源许可：GPL-3.0。
- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/channel/3-%E5%90%91%20channel%20%E5%8F%91%E9%80%81%E6%95%B0%E6%8D%AE%E7%9A%84%E8%BF%87%E7%A8%8B%E6%98%AF%E6%80%8E%E6%A0%B7%E7%9A%84.md#L247)，来源许可：GPL-3.0。
