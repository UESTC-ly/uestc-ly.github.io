# TCP与连接管理

<a id="k3e7dc103b250"></a>

## HTTP 基于 TCP 还是 UDP？

~~**HTTP 协议是基于 TCP 协议的**，所以发送 HTTP 请求之前首先要建立 TCP 连接也就是要经历 3 次握手。~~

🐛 修正（参见 [issue#1915](https://github.com/Snailclimb/JavaGuide/issues/1915)）：

HTTP/3.0 之前是基于 TCP 协议的，而 HTTP/3.0 将弃用 TCP，改用 **基于 UDP 的 QUIC 协议**：

- **HTTP/1.x 和 HTTP/2.0**：这两个版本的 HTTP 协议都明确建立在 TCP 之上。TCP 提供了可靠的、面向连接的传输，确保数据按序、无差错地到达，这对于网页内容的正确展示非常重要。发送 HTTP 请求前，需要先通过 TCP 的三次握手建立连接。
- **HTTP/3.0**：这是一个重大的改变。HTTP/3 弃用了 TCP，转而使用 QUIC 协议，而 QUIC 是构建在 UDP 之上的。

**相关解释：** [HTTP/2.0 和 HTTP/3.0 有什么区别？](HTTP%E4%B8%8EWeb%E9%80%9A%E4%BF%A1.md#k252ab7a5cc2a)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions2.md#L77)，来源许可：Apache-2.0。

<a id="k33a436ece9fe"></a>

## HTTPS 握手里的 RSA 和 ECDHE，到底差在哪？（应用层）

RSA 和 ECDHE 的核心区别在于：**会话密钥材料是“传过去的”，还是“协商出来的”**。

在 TLS 1.2 的静态 RSA 握手里，客户端生成 `PreMasterSecret`，用服务器证书里的 RSA 公钥加密后发给服务端，服务端再用 RSA 私钥解密。问题是，如果攻击者保存了当年的握手流量，后来服务器私钥又泄漏，就可能回头解出历史会话密钥，所以它没有前向安全。

ECDHE 不直接传输共享秘密。客户端和服务端各自生成临时密钥对，交换临时公钥后，双方本地算出同一个共享秘密。服务器证书私钥主要用于签名认证，证明临时参数没被中间人替换，而不是用来解密会话密钥。

所以一句话总结：**RSA 是客户端把秘密加密送过去；ECDHE 是双方用临时密钥协商出秘密。ECDHE 支持前向安全，也因此成为现代 HTTPS 的主流方向。**

详细介绍：[HTTPS 握手里的 RSA 和 ECDHE，到底差在哪？（应用层）](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/https-rsa-vs-ecdhe.md)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions.md#L188)，来源许可：Apache-2.0。

<a id="ke99185ab3ca3"></a>

## HTTPS连接的时候，怎么确定收到的包是服务器发来的（中间人攻击）？

1.验证域名、有效期等信息是否正确。证书上都有包含这些信息，比较容易完成验证；

2.判断证书来源是否合法。每份签发证书都可以根据验证链查找到对应的根证书，操作系统、浏览器会在本地存储权威机构的根证书，利用本地根证书可以对对应机构签发证书完成来源验证；

3.判断证书是否被篡改。需要与 CA 服务器进行校验；

4.判断证书是否已吊销。通过CRL（Certificate Revocation List 证书注销列表）和 OCSP（Online Certificate Status Protocol 在线证书状态协议）实现，其中 OCSP 可用于第3步中以减少与 CA 服务器的交互，提高验证效率

### 参考资料

- [Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Computer%20Network.md#L290)，来源许可：GPL-3.0。

<a id="k4937f54c7a4e"></a>

## HTTP可以使用UDP吗？

HTTP不可以使用UDP，HTTP需要基于可靠的传输协议，而UDP不可靠

注：**http 3.0 使用udp实现**
https://zh.wikipedia.org/wiki/HTTP/3

### 参考资料

- [Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Computer%20Network.md#L223)，来源许可：GPL-3.0。

<a id="k06eb01665524"></a>

## POST 方法会产生两个 TCP 数据包？你了解吗？

有些文章中提到，POST 会将 header 和 body 分开发送，先发送 header，服务端返回 100 状态码再发送 body。

HTTP 协议中没有明确说明 POST 会产生两个 TCP 数据包，而且实际测试(Chrome)发现，header 和 body 不会分开发送。

所以，header 和 body 分开发送是部分浏览器或框架的请求方法，不属于 post 必然行为。

<p  id="赛森是什么"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-02-net.md#L331)，来源许可：Apache-2.0。

<a id="k07643685e094"></a>

## Socket 中 TCP 的三次握手建立连接

我们知道 TCP 建立连接要进行 “三次握手”，即交换三个分组。大致流程如下：

1. 客户端向服务器发送一个 SYN J
2. 服务器向客户端响应一个 SYN K，并对 SYN J 进行确认 ACK J+1
3. 客户端再向服务器发一个确认 ACK K+1

这样就完成了三次握手，但是这个三次握手发生在 Socket 的那几个函数中呢？请看下图：

![socket 中发送的 TCP 三次握手](http://images.cnblogs.com/cnblogs_com/skynet/201012/201012122157467258.png)

从图中可以看出：
1. 当客户端调用 connect 时，触发了连接请求，向服务器发送了 SYN J 包，这时 connect 进入阻塞状态；  
2. 服务器监听到连接请求，即收到 SYN J 包，调用 accept 函数接收请求向客户端发送 SYN K ，ACK J+1，这时 accept 进入阻塞状态；  
3. 客户端收到服务器的 SYN K ，ACK J+1 之后，这时 connect 返回，并对 SYN K 进行确认；  
4. 服务器收到 ACK K+1 时，accept 返回，至此三次握手完毕，连接建立。

### 参考资料

- [huihut/interview](https://github.com/huihut/interview/blob/7a7166804a0ffc8f156e906bf4c1a94bb9f6a94b/README.md#L2533)，来源许可：CC-BY-NC-SA-4.0。

<a id="k90065ae72327"></a>

## Socket 中 TCP 的四次挥手释放连接

上面介绍了 socket 中 TCP 的三次握手建立过程，及其涉及的 socket 函数。现在我们介绍 socket 中的四次挥手释放连接的过程，请看下图：

![socket 中发送的 TCP 四次挥手](http://images.cnblogs.com/cnblogs_com/skynet/201012/201012122157487616.png)

图示过程如下：

1. 某个应用进程首先调用 close 主动关闭连接，这时 TCP 发送一个 FIN M；
2. 另一端接收到 FIN M 之后，执行被动关闭，对这个 FIN 进行确认。它的接收也作为文件结束符传递给应用进程，因为 FIN 的接收意味着应用进程在相应的连接上再也接收不到额外数据；
3. 一段时间之后，接收到文件结束符的应用进程调用 close 关闭它的 socket。这导致它的 TCP 也发送一个 FIN N；
4. 接收到这个 FIN 的源发送端 TCP 对它进行确认。

这样每个方向上都有一个 FIN 和 ACK。

<a id="database"></a>

### 参考资料

- [huihut/interview](https://github.com/huihut/interview/blob/7a7166804a0ffc8f156e906bf4c1a94bb9f6a94b/README.md#L2551)，来源许可：CC-BY-NC-SA-4.0。

<a id="ke2323e33c2e1"></a>

## TCP TIME_WAIT 到底在等什么？为什么要等？

**相关面试题**：

1. `TIME_WAIT` 到底在等什么？
2. `TIME_WAIT` 大量堆积会不会真的出问题？
3. `tcp_tw_reuse` 能不能随便开？
4. `TIME_WAIT` 和 `CLOSE_WAIT` 怎么区分？

**参考答案**： [TCP TIME_WAIT 详解：为什么要等、会不会出问题、能不能复用？](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/tcp-time-wait.md)。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions2.md#L206)，来源许可：Apache-2.0。

<a id="k85e5c82cbb65"></a>

## TCP 三次握手和四次挥手（非常重要）

**相关面试题**：

- 为什么要三次握手？
- 第 2 次握手传回了 ACK，为什么还要传回 SYN？
- 为什么要四次挥手？
- 为什么不能把服务器发送的 ACK 和 FIN 合并起来，变成三次挥手？
- 如果第二次挥手时服务器的 ACK 没有送达客户端，会怎样？
- 为什么第四次挥手客户端需要等待 2\*MSL（报文段最长寿命）时间后才进入 CLOSED 状态？

**参考答案**：[TCP 三次握手和四次挥手（传输层）](https://javaguide.cn/cs-basics/network/tcp-connection-and-disconnection.html)。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions2.md#L193)，来源许可：Apache-2.0。

<a id="k3e9a5efc9627"></a>

## TCP 三次握手建立连接

![TCP 三次握手](https://gitee.com/huihut/interview/raw/master/images/TCP三次握手建立连接.png)

【TCP 建立连接全过程解释】

1. 客户端发送 SYN 给服务器，说明客户端请求建立连接；
2. 服务端收到客户端发的 SYN，并回复 SYN+ACK 给客户端（同意建立连接）；
3. 客户端收到服务端的 SYN+ACK 后，回复 ACK 给服务端（表示客户端收到了服务端发的同意报文）；
4. 服务端收到客户端的 ACK，连接已建立，可以数据传输。

### 参考资料

- [huihut/interview](https://github.com/huihut/interview/blob/7a7166804a0ffc8f156e906bf4c1a94bb9f6a94b/README.md#L2356)，来源许可：CC-BY-NC-SA-4.0。

<a id="k7e0c4d99f3da"></a>

## TCP 与 UDP 的区别（重要）

1. **是否面向连接**：
   - TCP 是面向连接的。在传输数据之前，必须先通过“三次握手”建立连接；数据传输完成后，还需要通过“四次挥手”来释放连接。这保证了双方都准备好通信。
   - UDP 是无连接的。发送数据前不需要建立任何连接，直接把数据包（数据报）扔出去。
2. **是否是可靠传输**：
   - TCP 提供可靠的数据传输服务。它通过序列号、确认应答（ACK）、超时重传、流量控制、拥塞控制等一系列机制，来确保数据能够无差错、不丢失、不重复且按顺序地到达目的地。
   - UDP 提供不可靠的传输。它尽最大努力交付（best-effort delivery），但不保证数据一定能到达，也不保证到达的顺序，更不会自动重传。收到报文后，接收方也不会主动发确认。
3. **是否有状态**：
   - TCP 是有状态的。因为要保证可靠性，TCP 需要在连接的两端维护连接状态信息，比如序列号、窗口大小、哪些数据发出去了、哪些收到了确认等。
   - UDP 是无状态的。它不维护连接状态，发送方发出数据后就不再关心它是否到达以及如何到达，因此开销更小（**这很“渣男”！**）。
4. **传输效率**：
   - TCP 因为需要建立连接、发送确认、处理重传等，其开销较大，传输效率相对较低。
   - UDP 结构简单，没有复杂的控制机制，开销小，传输效率更高，速度更快。
5. **传输形式**：
   - TCP 是面向字节流（Byte Stream）的。它将应用程序交付的数据视为一连串无结构的字节流，可能会对数据进行拆分或合并。
   - UDP 是面向报文（Message Oriented）的。应用程序交给 UDP 多大的数据块，UDP 就照样发送，既不拆分也不合并，保留了应用程序消息的边界。
6. **首部开销**：
   - TCP 的头部至少需要 20 字节，如果包含选项字段，最多可达 60 字节。
   - UDP 的头部非常简单，固定只有 8 字节。
7. **是否提供广播或多播服务**：
   - TCP 只支持点对点（Point-to-Point）的单播通信。
   - UDP 支持一对一（单播）、一对多（多播/Multicast）和一对所有（广播/Broadcast）的通信方式。
8. ……

为了更直观地对比，可以看下面这个表格：

| 特性         | TCP                        | UDP                                 |
| ------------ | -------------------------- | ----------------------------------- |
| **连接性**   | 面向连接                   | 无连接                              |
| **可靠性**   | 可靠                       | 不可靠（尽力而为）                  |
| **状态维护** | 有状态                     | 无状态                              |
| **传输效率** | 较低                       | 较高                                |
| **传输形式** | 面向字节流                 | 面向数据报（报文）                  |
| **头部开销** | 20 - 60 字节               | 8 字节                              |
| **通信模式** | 点对点（单播）             | 单播、多播、广播                    |
| **常见应用** | HTTP/HTTPS, FTP, SMTP, SSH | DNS, DHCP, SNMP, TFTP, VoIP, 视频流 |

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions2.md#L19)，来源许可：Apache-2.0。

<a id="k0bade1f37e01"></a>

## TCP 协议如何保证可靠传输？：第二种回答

- 建立连接（标志位）：通信前确认通信实体存在。

- 序号机制（序号、确认号）：确保了数据是按序、完整到达。

- 数据校验（校验和）：CRC校验全部数据。

- 超时重传（定时器）：保证因链路故障未能到达数据能够被多次重发。

- 窗口机制（窗口）：提供流量控制，避免过量发送。

- 拥塞控制：同上。

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-05-net.md#L213)，来源许可：Apache-2.0。

<a id="kc3efde54e881"></a>

## TCP 和 UDP 可以使用同一个端口吗？

结论：**可以**。TCP 和 UDP 的端口绑定命名空间按传输层协议区分，同一个数字端口在不同协议下不冲突。

内核收到 IP 包后，会先看 IP 层的协议标识（TCP 协议号是 `6`，UDP 是 `17`），根据协议号把报文交给对应的 TCP 或 UDP 协议栈，然后再在各自协议栈内按地址和端口分发。所以 `TCP/8080` 和 `UDP/8080` 可以共存，内核压根不会把它们当成同一条通信。

![内核协议分发流程](https://oss.javaguide.cn/github/javaguide/cs-basics/network/can-tcp-and-udp-use-the-same-port-kernel-protocol-dispatching-process.png)

真正容易冲突的是**同一协议**下的重复绑定，比如两个 TCP 服务通常不能同时监听同一个本地 IP 和端口；这时才涉及 `SO_REUSEADDR`、`SO_REUSEPORT` 这类 socket 复用选项。

经典例子：DNS 同时使用 `UDP/53`（日常查询）和 `TCP/53`（响应过大、区域传送）；HTTP/3 常见部署是 `UDP/443`（QUIC），可以和传统 HTTPS 的 `TCP/443` 同时存在。

![DNS 和 HTTP/3 同时使用 TCP 与 UDP 端口的实际案例](https://oss.javaguide.cn/github/javaguide/cs-basics/network/can-tcp-and-udp-use-the-same-port-practical-application-example.png)

详细介绍：[TCP 和 UDP 可以使用同一个端口吗？](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/can-tcp-and-udp-use-the-same-port.md)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions2.md#L221)，来源许可：Apache-2.0。

<a id="ke9de4a91e984"></a>

## TCP 四次挥手释放连接

![TCP 四次挥手](https://gitee.com/huihut/interview/raw/master/images/TCP四次挥手释放连接.png)

【TCP 释放连接全过程解释】

1. 客户端发送 FIN 给服务器，说明客户端不必发送数据给服务器了（请求释放从客户端到服务器的连接）；
2. 服务器接收到客户端发的 FIN，并回复 ACK 给客户端（同意释放从客户端到服务器的连接）；
3. 客户端收到服务端回复的 ACK，此时从客户端到服务器的连接已释放（但服务端到客户端的连接还未释放，并且客户端还可以接收数据）；
4. 服务端继续发送之前没发完的数据给客户端；
5. 服务端发送 FIN+ACK 给客户端，说明服务端发送完了数据（请求释放从服务端到客户端的连接，就算没收到客户端的回复，过段时间也会自动释放）；
6. 客户端收到服务端的 FIN+ACK，并回复 ACK 给服务端（同意释放从服务端到客户端的连接）；
7. 服务端收到客户端的 ACK 后，释放从服务端到客户端的连接。

### 参考资料

- [huihut/interview](https://github.com/huihut/interview/blob/7a7166804a0ffc8f156e906bf4c1a94bb9f6a94b/README.md#L2381)，来源许可：CC-BY-NC-SA-4.0。

<a id="kb5251d57434b"></a>

## TCP/IP 四层模型是什么？每一层的作用是什么？

**TCP/IP 四层模型** 是目前被广泛采用的一种模型，我们可以将 TCP/IP 模型看作是 OSI 七层模型的精简版本，由以下 4 层组成：

1. 应用层
2. 传输层
3. 网络层
4. 网络接口层

需要注意的是，我们并不能将 TCP/IP 四层模型 和 OSI 七层模型完全精确地匹配起来，不过可以简单将两者对应起来，如下图所示：

![TCP/IP 四层模型与 OSI 模型的对应关系](https://oss.javaguide.cn/github/javaguide/cs-basics/network/tcp-ip-4-model.png)

关于每一层作用的详细介绍，请看 [OSI 和 TCP/IP 网络分层模型详解（基础）](https://javaguide.cn/cs-basics/network/osi-and-tcp-ip-model.html) 这篇文章。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions.md#L37)，来源许可：Apache-2.0。

<a id="ke6df3eeb32fe"></a>

## TCP/IP四层模型的相关概念

<font color=DeepSkyBlue>TCP/IP四层模型</font>：

1. 应用层：负责各种不同应用之间的协议，如文件传输协议（FTP），远程登陆协议（Telnet），电子邮件协议（SMTP），网络文件服务协议（NFS），网络管理协议（SNMP）等。

2. 传输层：负责可靠传输的TCP协议、高效传输的UDP协议。

3. 网络层：负责寻址（准确找到对方设备）的IP，ICMP，ARP，RARP等协议。

4. 数据链路层：负责将数字信号在物理通道（网线）中准确传输。

<font color=DeepSkyBlue>四层模型逻辑</font>：

发送端是由上至下，把上层来的数据在头部加上各层协议的数据（部首）再下发给下层。

接受端则由下而上，把从下层接收到的数据进行解密和去掉头部的部首后再发送给上层。

层层加密和解密后，应用层最终拿到了需要的数据。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L31)，来源许可：GPL-3.0。

<a id="kffc861ce571b"></a>

## TCP一定需要四次挥手吗？

**面试官：** TCP为什么有四次挥手？一定需要四次挥手吗？

**回答：**

TCP 是全双工协议，两个方向的字节流可以独立关闭。主动关闭方发送 FIN，只表示“我没有更多数据要发送”，并不表示对方也发送完了。被动关闭方先 ACK 这个 FIN，应用层可能还要继续发送剩余数据；等它也关闭发送方向时，再发自己的 FIN，最后由主动关闭方 ACK。因此逻辑上存在两个独立的半关闭过程：

```text
A -> B: FIN
B -> A: ACK
B -> A: FIN
A -> B: ACK
```

但“四次挥手”描述的是四个逻辑报文动作，不保证线上一定看到四个独立 TCP Segment。如果 B 收到 FIN 后应用立即关闭，并且没有待发送数据，它对第一个 FIN 的 ACK 可以与自己的 FIN 合并在同一个 Segment 中，于是抓包可能表现为三次。关键条件是被动方何时进入关闭发送方向，而不是“开启延迟 ACK 就一定三次”。

其他情况也可能不同：双方同时主动关闭时会发生 Simultaneous Close；连接异常、进程强杀或设置特定 Socket 行为时可能通过 RST 中止，这不是正常的优雅关闭；中间设备和重传也会让抓包数量多于四个。

最后一个 ACK 之后，主动关闭方通常进入 TIME_WAIT，等待 $2\times\mathrm{MSL}$。原因是确保最后 ACK 丢失时还能重发，并让旧连接中的延迟报文在网络中消失，避免污染相同四元组的新连接。TIME_WAIT 不是“无用等待”，但在高并发短连接服务中需要通过连接复用、合理的端口与内核参数治理，而不是粗暴关闭协议保护。

FIN 也占用一个序列号，ACK 确认的是对方 FIN 的下一个序列号。收到 FIN 只关闭接收方向中的“对方继续发送”能力，本端仍可以发送数据，这正是 TCP Half-Close 的语义。

**因此，TCP 关闭需要两个方向分别确认，但四个逻辑动作可以合并成更少的报文段；是否合并取决于应用关闭时机和协议栈行为。**

<a id="alibaba-cloud-agent-algo-20260901-q20"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1731)，来源许可：GPL-3.0。

<a id="k4aa9276dbcf1"></a>

## tcp三次握手、四次挥手

**回答：**

TCP 三次握手的目标是建立可靠连接，并让双方确认彼此的发送和接收能力，同时同步初始序列号。

第一次握手，客户端发送 SYN 报文，带上自己的初始序列号 `seq=x`，进入 SYN_SENT 状态。第二次握手，服务端收到后返回 SYN+ACK，带上自己的初始序列号 `seq=y`，并确认客户端序列号 `ack=x+1`，进入 SYN_RCVD 状态。第三次握手，客户端再发 ACK，确认服务端序列号 `ack=y+1`，双方进入 ESTABLISHED 状态。

为什么不是两次？因为两次只能让客户端确认服务端收到了自己的 SYN，并不能让服务端确认客户端收到了自己的 SYN+ACK。第三次 ACK 能证明双方收发能力都正常，也能避免历史延迟 SYN 导致服务端误建立连接。

TCP 四次挥手的目标是关闭双向字节流。因为 TCP 是全双工，客户端到服务端和服务端到客户端两个方向要分别关闭。

假设客户端主动关闭。第一次，客户端发送 FIN，表示自己不再发送数据，进入 FIN_WAIT_1。第二次，服务端回复 ACK，表示收到了关闭请求，客户端进入 FIN_WAIT_2；此时服务端可能还有数据要发。第三次，服务端数据发送完后发送 FIN，进入 LAST_ACK。第四次，客户端回复 ACK，进入 TIME_WAIT，服务端收到 ACK 后关闭，客户端等待 2MSL 后关闭。

TIME_WAIT 的作用主要有两个：确保最后一个 ACK 如果丢失，客户端还能重发；让网络中旧连接的残留报文自然过期，避免影响后续相同四元组的新连接。常见追问包括 SYN flood、半连接队列、TIME_WAIT 过多、CLOSE_WAIT 过多。CLOSE_WAIT 多通常说明应用程序没有正确 close socket；TIME_WAIT 多一般出现在主动关闭方，需要结合连接复用、keep-alive、端口范围和内核参数分析。

<a id="ant-agent-20260520-q11"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E8%9A%82%E8%9A%81%E9%9B%86%E5%9B%A2%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L224)，来源许可：GPL-3.0。

<a id="k0c34a1ad864e"></a>

## TCP四大拥塞控制算法总结？（极其重要）

### **四大算法**

拥塞控制主要是四个算法：1）慢启动，2）拥塞避免，3）拥塞发生，4）快速恢复。这四个算法不是一天都搞出来的，这个四算法的发展经历了很多时间，到今天都还在优化中。

![](https://raw.githubusercontent.com/forthespada/InterviewGuide/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-04-net.assets/202205220036635.png)

### 慢热启动算法 – Slow Start

 所谓慢启动，也就是TCP连接刚建立，一点一点地提速，试探一下网络的承受能力，以免直接扰乱了网络通道的秩序。

 慢启动算法：

1) 连接建好的开始先初始化拥塞窗口cwnd大小为1，表明可以传一个MSS大小的数据。
2) 每当收到一个ACK，cwnd大小加一，呈线性上升。
3) 每当过了一个往返延迟时间RTT(Round-Trip Time)，cwnd大小直接翻倍，乘以2，呈指数让升。
4) 还有一个ssthresh（slow start threshold），是一个上限，当cwnd >= ssthresh时，就会进入“拥塞避免算法”（后面会说这个算法）

### 拥塞避免算法 – Congestion Avoidance

 如同前边说的，当拥塞窗口大小cwnd大于等于慢启动阈值ssthresh后，就进入拥塞避免算法。算法如下：

1) 收到一个ACK，则cwnd = cwnd + 1 / cwnd
2) 每当过了一个往返延迟时间RTT，cwnd大小加一。

 过了慢启动阈值后，拥塞避免算法可以避免窗口增长过快导致窗口拥塞，而是缓慢的增加调整到网络的最佳值。

### 拥塞发生状态时的算法

一般来说，TCP拥塞控制默认认为网络丢包是由于网络拥塞导致的，所以一般的TCP拥塞控制算法以丢包为网络进入拥塞状态的信号。

对于丢包有两种判定方式，一种是超时重传RTO[Retransmission Timeout]超时，另一个是收到三个重复确认ACK。

超时重传是TCP协议保证数据可靠性的一个重要机制，其原理是在发送一个数据以后就开启一个计时器，在一定时间内如果没有得到发送数据报的ACK报文，那么就重新发送数据，直到发送成功为止。

但是如果发送端接收到3个以上的重复ACK，TCP就意识到数据发生丢失，需要重传。这个机制不需要等到重传定时器超时，所以叫做快速重传，而快速重传后没有使用慢启动算法，而是拥塞避免算法，所以这又叫做快速恢复算法。

超时重传RTO[Retransmission Timeout]超时，TCP会重传数据包。TCP认为这种情况比较糟糕，反应也比较强烈：

- 由于发生丢包，将慢启动阈值ssthresh设置为当前cwnd的一半，即ssthresh = cwnd / 2.
- cwnd重置为1
- 进入慢启动过程

 最为早期的TCP Tahoe算法就只使用上述处理办法，但是由于一丢包就一切重来，导致cwnd又重置为1，十分不利于网络数据的稳定传递。

 所以，TCP Reno算法进行了优化。当收到三个重复确认ACK时，TCP开启快速重传Fast Retransmit算法，而不用等到RTO超时再进行重传：

- cwnd大小缩小为当前的一半
- ssthresh设置为缩小后的cwnd大小
- 然后进入快速恢复算法Fast Recovery。

![](https://raw.githubusercontent.com/forthespada/InterviewGuide/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-04-net.assets/202205220036573.png)

### 快速恢复算法 – Fast Recovery

 TCP Tahoe是早期的算法，所以没有快速恢复算法，而Reno算法有。在进入快速恢复之前，cwnd和ssthresh已经被更改为原有cwnd的一半。快速恢复算法的逻辑如下：

- cwnd = cwnd + 3 *MSS，加3* MSS的原因是因为收到3个重复的ACK。

- 重传DACKs指定的数据包。

- 如果再收到DACKs，那么cwnd大小增加一。

- 如果收到新的ACK，表明重传的包成功了，那么退出快速恢复算法。将cwnd设置为ssthresh，然后进入拥塞避免算法。

  ![](https://raw.githubusercontent.com/forthespada/InterviewGuide/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-04-net.assets/202205220036984.png)

 如图所示，第五个包发生了丢失，所以导致接收方接收到三次重复ACK，也就是ACK5。所以将ssthresh设置当当时cwnd的一半，也就是6/2 = 3，cwnd设置为3 + 3 = 6。

然后重传第五个包。当收到新的ACK时，也就是ACK11，则退出快速恢复阶段，将cwnd重新设置为当前的ssthresh，也就是3，然后进入拥塞避免算法阶段。

<p  id="为何快速重传是选择次"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-04-net.md#L325)，来源许可：Apache-2.0。

<a id="k2e35ac41ac51"></a>

## TCP头部中有哪些信息？

- 序号（32bit）：传输方向上字节流的字节编号。初始时序号会被设置一个随机的初始值（ISN），之后每次发送数据时，序号值 = ISN + 数据在整个字节流中的偏移。假设A -> B且ISN = 1024，第一段数据512字节已经到B，则第二段数据发送时序号为1024 + 512。用于解决网络包乱序问题。

- 确认号（32bit）：接收方对发送方TCP报文段的响应，其值是收到的序号值 + 1。

- 首部长（4bit）：标识首部有多少个4字节 * 首部长，最大为15，即60字节。

- 标志位（6bit）：
  - URG：标志紧急指针是否有效。

  - ACK：标志确认号是否有效（确认报文段）。用于解决丢包问题。

  - PSH：提示接收端立即从缓冲读走数据。

  - RST：表示要求对方重新建立连接（复位报文段）。

  - SYN：表示请求建立一个连接（连接报文段）。

  - FIN：表示关闭连接（断开报文段）。

- 窗口（16bit）：接收窗口。用于告知对方（发送方）本方的缓冲还能接收多少字节数据。用于解决流控。

- 校验和（16bit）：接收端用CRC检验整个报文段有无损坏。

<p  id="常见的连接状态有哪些"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-03-net.md#L149)，来源许可：Apache-2.0。

<a id="k94fb748328e1"></a>

## TCP头部报文字段介绍几个？各自的功能？

source port 和 destination port

> 两者分别为「源端口号」和「目的端口号」。源端口号就是指本地端口，目的端口就是远程端口。

可以这么理解，我们有很多软件，每个软件都对应一个端口，假如，你想和我数据交互，咱们得互相知道你我的端口号。

再来一个很官方的：

> 扩展：应用程序的端口号和应用程序所在主机的 IP 地址统称为 socket（套接字），IP:端口号, 在互联网上 socket 唯一标识每一个应用程序，源端口+源IP+目的端口+目的IP称为”套接字对“，一对套接字就是一个连接，一个客户端与服务器之间的连接。

Sequence Number

> 称为「序列号」。用于 TCP 通信过程中某一传输方向上字节流的每个字节的编号，为了确保数据通信的有序性，避免网络中乱序的问题。接收端根据这个编号进行确认，保证分割的数据段在原始数据包的位置。初始序列号由自己定，而后绪的序列号由对端的 ACK 决定：SN_x = ACK_y (x 的序列号 = y 发给 x 的 ACK)。

说白了，类似于身份证一样，而且还得发送此时此刻的所在的位置，就相当于身份证上的地址一样。

Acknowledge Number

> 称为「确认序列号」。确认序列号是接收确认端所期望收到的下一序列号。确认序号应当是上次已成功收到数据字节序号加1，只有当标志位中的 ACK 标志为 1 时该确认序列号的字段才有效。主要用来解决不丢包的问题。

TCP Flag

`TCP` 首部中有 6 个标志比特，它们中的多个可同时被设置为 `1`，主要是用于操控 `TCP` 的状态机的，依次为`URG，ACK，PSH，RST，SYN，FIN`。

当然只介绍三个：

1. **ACK**：这个标识可以理解为发送端发送数据到接收端，发送的时候 ACK 为 0，标识接收端还未应答，一旦接收端接收数据之后，就将 ACK 置为 1，发送端接收到之后，就知道了接收端已经接收了数据。
2. **SYN**：表示「同步序列号」，是 TCP 握手的发送的第一个数据包。用来建立 TCP 的连接。SYN 标志位和 ACK 标志位搭配使用，当连接请求的时候，SYN=1，ACK=0连接被响应的时候，SYN=1，ACK=1；这个标志的数据包经常被用来进行端口扫描。扫描者发送一个只有 SYN 的数据包，如果对方主机响应了一个数据包回来 ，就表明这台主机存在这个端口。
3. **FIN**：表示发送端已经达到数据末尾，也就是说双方的数据传送完成，没有数据可以传送了，发送FIN标志位的 TCP 数据包后，连接将被断开。这个标志的数据包也经常被用于进行端口扫描。发送端只剩最后的一段数据了，同时要告诉接收端后边没有数据可以接受了，所以用FIN标识一下，接收端看到这个FIN之后，哦！这是接受的最后的数据，接受完就关闭了；**TCP四次分手必然问**。

Window size

> 称为滑动窗口大小。所说的滑动窗口，用来进行流量控制。

<p  id="偶斯哎的七层模型的主要功能"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-03-net.md#L206)，来源许可：Apache-2.0。

<a id="kec021a85c0e0"></a>

## TCP如何保证可靠传输

* 应用数据被分割成 TCP 认为最适合发送的数据块；
* TCP 给发送的每一个包进行编号，接收方对数据包进行排序，把有序数据传送给应用层；
* **校验和：**TCP 将保持它首部和数据的检验和。这是一个端到端的检验和，目的是检测数据在传输过程中的任何变化。如果收到段的检验和有差错，TCP 将丢弃这个报文段和不确认收到此报文段；
* TCP 的接收端会丢弃重复的数据；
* **流量控制：**TCP 连接的每一方都有固定大小的缓冲空间，TCP的接收端只允许发送端发送接收端缓冲区能接纳的数据。当接收方来不及处理发送方的数据，能提示发送方降低发送的速率，防止包丢失。TCP 使用的流量控制协议是可变大小的滑动窗口协议；（TCP 利用滑动窗口实现流量控制）
* **拥塞控制：**当网络拥塞时，减少数据的发送；
* **ARQ协议：**也是为了实现可靠传输的，它的基本原理就是每发完一个分组就停止发送，等待对方确认。在收到确认后再发下一个分组；
* **超时重传：**当 TCP 发出一个段后，它启动一个定时器，等待目的端确认收到这个报文段。如果不能及时收到一个确认，将重发这个报文段。

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/03-computer-basics/computer-network/network-protocols.md#L117)，来源许可：GPL-3.0。

<a id="kba18c6d51168"></a>

## TCP如何最大利用带宽？

TCP速率受到三个因素影响

- 窗口：即滑动窗口大小，见[TCP如何实现流量控制？](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Computer%20Network.md#TCP如何实现流量控制)
- 带宽：这里带宽是指单位时间内从发送端到接收端所能通过的“最高数据率”，是一种硬件限制。TCP发送端和接收端的数据传输数不可能超过两点间的带宽限制。发送端和接收端之间带宽取所通过线路的带宽最小值（如通过互联网连接）。
- RTT：即Round Trip Time，表示从发送端到接收端的一去一回需要的时间，TCP在数据传输过程中会对RTT进行采样（即对发送的数据包及其ACK的时间差进行测量，并根据测量值更新RTT值），TCP根据得到的RTT值更新RTO值，即Retransmission TimeOut，就是重传间隔，发送端对每个发出的数据包进行计时，如果在RTO时间内没有收到所发出的数据包的对应ACK，则任务数据包丢失，将重传数据。一般RTO值都比采样得到的RTT值要大。

带宽时延乘积

带宽时延乘积=带宽*RTT，实际上等于发送端到接收端单向通道的数据容积的两倍，这里单向通道的数据容积可以这样来理解，单向通道看成是一条单行道马路，带宽就是马路的车道数，路上跑的汽车就是数据（不过这里所有汽车的速率都是一样的，且不会有人想超车，大家齐头并进），那么单向通道的数据容积就是这条单行道上摆满车，一共可以摆多少辆。带宽就是马路的车道数，带宽数乘以单向通道的数据容积就是路面上所能容纳的全部数据量。当路面上已经摆满的时候，就不能再往里面放了。

设滑动窗口大小为![](https://latex.codecogs.com/svg.latex?W)， 发送端和接收端的带宽为![](https://latex.codecogs.com/svg.latex?B)， RTT为![](https://latex.codecogs.com/svg.latex?T_r)。

前面已经说过了，TCP发送数据时受滑动窗口的限制，当TCP将滑动窗口中的数据都发出后，在收到第一个ACK之前，滑动窗口大小是0，不能再发送数据了，必须等待ACK包使滑动窗口移动。那么在理想情况下，ACK包应该在什么时候到达呢？显然，就是在数据发出后的RTT时间后，ACK包到达。这也就是说，现在在不考虑丢包和拥塞情况下，TCP在一个RTT时间内能发出的最大数据量为 ![](http://latex.codecogs.com/gif.latex?W) ，所以不考虑带宽限制下，TCP能一个时刻能达到的最大速度是 ![](https://latex.codecogs.com/svg.latex?V=\frac{W}{T_r})。

现在再考虑带宽限制，前面说过当马路上摆满车的时候，就无法再往里放车了，同理，TCP发送端在 ![](https://latex.codecogs.com/svg.latex?\frac{T_r}{2}) 时间内，能往通道上放的最大数据量为 ![](https://latex.codecogs.com/svg.latex?\frac{V*T_r}{2}) ，通过带宽时延乘积得到的容积限制为 ![](https://latex.codecogs.com/svg.latex?\frac{B*T_r}{2})。当 ![](https://latex.codecogs.com/svg.latex?\frac{B*T_r}{2}%20\geq%20\frac{V*T_r}{2}) 时，单向通道容积不构成瓶颈，速率的限制主要来源于窗口大小限制。而当 ![](https://latex.codecogs.com/svg.latex?\frac{V*T_r}{2}%20\geq%20\frac{B*T_r}{2}) 时，则就受到容积限制，即此时速率限制来源于带宽限制。

因此，TCP的最大速率为 ![](https://latex.codecogs.com/svg.latex?V%20=%20\min{(\frac{W}{T_r},%20B)})

在我们平时生活中使用的宽带网络，ADSL等环境下，因为带宽都比较小，从而 ![](https://latex.codecogs.com/svg.latex?B*T_r) 也比较小，再加上网络情况比较复杂，拥塞情况比较常见，所以这些网络环境下，TCP速率的主要限制因素在于带宽，丢包率等。长肥管道一般不太常见，多见于一些单位使用的专线网络，在这些网络中速率的主要限制因素就是窗口大小了，这也是传统TCP在这些网络环境中不能充分利用带宽的原因所在（因为传统TCP的窗口大小是用2字节表示的，所以最大只有65535（不考虑窗口扩大选项）），除了专线网络外，随着网络硬件技术的发展，万兆交换机的出现，局域网中也可能会出现带宽时延乘积较大的情况。

### 参考资料

- [Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Computer%20Network.md#L164)，来源许可：GPL-3.0。

<a id="kb380cf473d01"></a>

## TCP对应的应用层协议

FTP：定义了文件传输协议，使用21端口.
Telnet：它是一种用于远程登陆的端口,23端口
SMTP：定义了简单邮件传送协议，服务器开放的是25号端口。
POP3：它是和SMTP对应，POP3用于接收邮件。

<p  id="有地皮对应的应用层协议"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-05-net.md#L312)，来源许可：Apache-2.0。

<a id="k35c6f47f351c"></a>

## TCP建立连接可以两次握手吗？为什么?


不可以。有两个原因：

首先，可能会出现**已失效的连接请求报文段又传到了服务器端**。

> client 发出的第一个连接请求报文段并没有丢失，而是在某个网络结点长时间的滞留了，以致延误到连接释放以后的某个时间才到达 server。本来这是一个早已失效的报文段。但 server 收到此失效的连接请求报文段后，就误认为是 client 再次发出的一个新的连接请求。于是就向 client 发出确认报文段，同意建立连接。假设不采用 “三次握手”，那么只要 server 发出确认，新的连接就建立了。由于现在 client 并没有发出建立连接的请求，因此不会理睬 server 的确认，也不会向 server 发送数据。但 server 却以为新的运输连接已经建立，并一直等待 client 发来数据。这样，server 的很多资源就白白浪费掉了。采用 “三次握手” 的办法可以防止上述现象发生。例如刚才那种情况，client 不会向 server 的确认发出确认。server 由于收不到确认，就知道 client 并没有要求建立连接。

其次，两次握手无法保证Client正确接收第二次握手的报文（Server无法确认Client是否收到），也无法保证Client和Server之间成功互换初始序列号。

还有就是两次握手会给SYN flood攻击提供机会。
扩展阅读： 什么是SYN攻击？https://zhuanlan.zhihu.com/p/360479307

### 参考资料

- [Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Computer%20Network.md#L39)，来源许可：GPL-3.0。

<a id="ka6285973d2c5"></a>

## TCP拥塞控制

* 慢开始

  * 刚开始发送数据时，先把拥塞窗口cwnd（congestion window）设置为一个最大报文段MSS的数值，每收到一个新的确认报文之后，可以把拥塞窗口增加最多一个 SMSS 的数值。这样每经过一个传输轮次（或者说是每经过一个往返时间RTT），拥塞窗口的大小就会加倍。

    ![](https://i.loli.net/2021/03/12/lpe2o7CVsbJaNj1.png)

* 拥塞避免

  * 当拥塞窗口的大小达到慢开始门限(slow start threshold)时，开始执行拥塞避免算法，让拥塞窗口cwnd缓慢地增大，避免出现拥塞，每经过一个传输轮次，拥塞窗口加一，使其按线性规律缓慢增大。

  ![](https://i.loli.net/2021/03/12/HgaMwBY7y6vskiZ.png)

* 快重传

  * 发送方只要一连收到三个重复确认，就知道接收方确实没有收到报文段，因而应当立即进行重传（即快重传），这样就不会出现超时，发送方也不就会误认为出现了网络拥塞。使用快重传可以使整个网络的吞吐量提高约20%。

  ![](https://i.loli.net/2021/03/12/iOW3JSVly2BaEQt.png)

* 快恢复

  * 当发送端收到连续三个重复的确认时，由于发送方现在认为网络很可能没有发生拥塞，因此现在不执行慢开始算法，而是执行快恢复算法FR (Fast Recovery)算法：

    1.慢开始门限ssthresh=当前拥塞窗口cwnd / 2 ；

    2.新拥塞窗口cwnd=慢开始门限ssthresh；

    3.开始执行拥塞避免算法，使拥塞窗口缓慢地线性增大。

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/03-computer-basics/computer-network/network-protocols.md#L132)，来源许可：GPL-3.0。

<a id="k4088316ff84d"></a>

## TCP流量控制

​		TCP使用滑动窗口协议（连续ARQ协议）实现流量控制。滑动窗口协议既保证了分组无差错、有序接收，也实现了流量控制。主要的方式就是接收方返回的 ACK 中会包含自己的接收窗口的大小，并且利用大小来控制发送方的数据发送。发送窗口的大小不能超过接受窗口的大小，只有当发送方发送并收到确认之后，才能将发送窗口右移。发送窗口的上限为接受窗口和拥塞窗口中的较小值。接受窗口表明了接收方的接收能力，拥塞窗口表明了网络的传送能力。

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/03-computer-basics/computer-network/network-protocols.md#L128)，来源许可：GPL-3.0。

<a id="kc24ab3e1caba"></a>

## TCP粘包、心跳、重连和背压在模型服务中有什么影响？

TCP是字节流协议，没有天然消息边界，所以会出现所谓“粘包/拆包”。解决方式是应用层自定义协议，例如固定长度头、分隔符、长度前缀或使用HTTP/gRPC这类成熟协议。

模型服务中的关键网络问题：

1. 粘包/拆包：自定义socket协议必须设计消息边界，否则请求和响应无法正确解析。
2. 心跳：长连接需要检测对端是否还活着，避免资源被死连接占用。
3. 重连：客户端断线后需要指数退避，避免服务恢复时被瞬时流量打爆。
4. 背压：服务端生成速度快于客户端读取速度时，必须限制缓冲，避免内存暴涨。
5. 超时：工具调用、模型推理、检索都要有超时，不能无限等待。

LLM流式输出中，背压尤其重要。如果客户端网络慢，服务端不能无限缓存token；如果用户取消请求，后端应尽快停止decode，释放KV Cache和GPU资源。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L1402)，来源许可：GPL-3.0。

<a id="k24339f0d3da8"></a>

## TCP粘包问题是什么？你会如何去解决它？

**TCP粘包**是指发送方发送的若干包数据到接收方接收时粘成一包，从接收缓冲区看，后一包数据的头紧接着前一包数据的尾。

- 由TCP**连接复用**造成的粘包问题。
- 因为TCP默认会使用**Nagle算法**，此算法会导致粘包问题。
  - 只有上一个分组得到确认，才会发送下一个分组；
  - 收集多个小分组，在一个确认到来时一起发送。
- **数据包过大**造成的粘包问题。
- 流量控制，**拥塞控制**也可能导致粘包。
- **接收方不及时接收缓冲区的包，造成多个包接收**

**解决**：

1. **Nagle算法**问题导致的，需要结合应用场景适当关闭该算法
2. 尾部标记序列。通过特殊标识符表示数据包的边界，例如\n\r，\t，或者一些隐藏字符。
3. 头部标记分步接收。在TCP报文的头部加上表示数据长度。
4. 应用层发送数据时**定长**发送。

<p  id="七层模型中表示层和会话层功能是什么"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-04-net.md#L152)，来源许可：Apache-2.0。

<a id="k5c563de27c0e"></a>

## Transmission control protocol (TCP)

<p align="center">
  <img src="images/JdAsdvG.jpg">

  <i><a href=http://www.wildbunny.co.uk/blog/2012/10/09/how-to-make-a-multi-player-game-part-1/>Source: How to make a multiplayer game</a></i>
</p>

TCP is a connection-oriented protocol over an [IP network](https://en.wikipedia.org/wiki/Internet_Protocol).  Connection is established and terminated using a [handshake](https://en.wikipedia.org/wiki/Handshaking).  All packets sent are guaranteed to reach the destination in the original order and without corruption through:

* Sequence numbers and [checksum fields](https://en.wikipedia.org/wiki/Transmission_Control_Protocol#Checksum_computation) for each packet
* [Acknowledgement](https://en.wikipedia.org/wiki/Acknowledgement_(data_networks)) packets and automatic retransmission

If the sender does not receive a correct response, it will resend the packets.  If there are multiple timeouts, the connection is dropped.  TCP also implements [flow control](https://en.wikipedia.org/wiki/Flow_control_(data)) and [congestion control](https://en.wikipedia.org/wiki/Network_congestion#Congestion_control).  These guarantees cause delays and generally result in less efficient transmission than UDP.

To ensure high throughput, web servers can keep a large number of TCP connections open, resulting in high memory usage.  It can be expensive to have a large number of open connections between web server threads and say, a [memcached](https://memcached.org/) server.  [Connection pooling](https://en.wikipedia.org/wiki/Connection_pool) can help in addition to switching to UDP where applicable.

TCP is useful for applications that require high reliability but are less time critical.  Some examples include web servers, database info, SMTP, FTP, and SSH.

Use TCP over UDP when:

* You need all of the data to arrive intact
* You want to automatically make a best estimate use of the network throughput

### 参考资料

- [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer/blob/ae9bbd7b02d90b9866215de185217d33f39ab733/README.md#L1402)，来源许可：CC-BY-4.0。

<a id="k96d9fbe7e986"></a>

## UDP的特点有哪些（附赠TCP的特点）？

- UDP是**无连接的**；
- UDP使用**尽最大努力交付**，即不保证可靠交付，因此主机不需要维持复杂的链接状态（这里面有许多参数）；
- UDP是**面向报文**的；
- UDP**没有拥塞控制**，因此网络出现拥塞不会使源主机的发送速率降低（对实时应用很有用，如IP电话，实时视频会议等）；
- UDP**支持一对一、一对多、多对一和多对多**的交互通信；
- UDP的**首部开销小**，只有8个字节，比TCP的20个字节的首部要短。

那么，再说一次TCP的特点：

- **TCP是面向连接的**。（就好像打电话一样，通话前需要先拨号建立连接，通话结束后要挂机释放连接）；
- 每一条TCP连接只能有两个端点，每一条TCP连接只能是点对点的（**一对一**）；
- TCP**提供可靠交付的服务**。通过TCP连接传送的数据，无差错、不丢失、不重复、并且按序到达；
- TCP**提供全双工通信**。TCP允许通信双方的应用进程在任何时候都能发送数据。TCP连接的两端都设有发送缓存和接收缓存，用来临时存放双方通信的数据；
- **面向字节流**。TCP中的“流”（stream）指的是流入进程或从进程流出的字节序列。“面向字节流”的含义是：虽然应用程序和TCP的交互是一次一个数据块（大小不等），但TCP把应用程序交下来的数据仅仅看成是一连串的无结构的字节流。

<p  id="体系屁对应的应用层协议"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-05-net.md#L292)，来源许可：Apache-2.0。

<a id="k5148d6af2cea"></a>

## 一个 TCP 连接中 HTTP 请求发送可以一起发送么（比如一起发三个请求，再三个响应一起接收）？

HTTP/1.1 存在一个问题，单个 TCP 连接在同一时刻只能处理一个请求，意思是说：两个请求的生命周期不能重叠，任意两个 HTTP 请求从开始到结束的时间在同一个 TCP 连接里不能重叠。

在 HTTP/1.1 存在 Pipelining 技术可以完成这个多个请求同时发送，但是由于浏览器默认关闭，所以可以认为这是不可行的。在 HTTP2 中由于 Multiplexing 特点的存在，多个 HTTP 请求可以在同一个 TCP 连接中并行进行。

那么在 HTTP/1.1 时代，浏览器是如何提高页面加载效率的呢？主要有下面两点：

- 维持和服务器已经建立的 TCP 连接，在同一连接上顺序处理多个请求。
- 和服务器建立多个 TCP 连接。

<p  id="浏览器对同一建立连接到的数量有没有限制"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-01-net.md#L256)，来源许可：Apache-2.0。

<a id="k539e992581b3"></a>

## 一台主机上只能保持最多 65535 个 TCP 连接吗？

结论：**不是**。`65535` 是最大端口号，不是连接数上限。

TCP 连接靠四元组区分：源 IP、源端口、目的 IP、目的端口。只要四元组不同，内核就识别为不同连接。服务端监听同一个端口时，只要客户端 IP 或客户端端口不同，连接就可以继续增加。

![TCP 连接靠四元组区分和真正的限制](https://oss.javaguide.cn/github/javaguide/cs-basics/network/maximum-number-of-tcp-connections-per-host-tcp-four-tuple-and-server-connection.png)

真正限制连接数的因素：

- **服务端**：主要受文件描述符、内存、CPU、网卡和应用处理能力限制，而不是端口数。
- **客户端**：连同一个目标时，源 IP 和目的 IP:Port 都固定，只剩源端口可变，更容易撞到临时端口上限（Linux 默认约 2.8 万个）。`TIME_WAIT` 堆积会加剧这个问题。
- **NAT 网关**：大量内网机器共享同一个公网 IP 访问同一个外部目标时，NAT 侧的公网源端口也会成为瓶颈。

生产环境最常见的坑不是端口不够，而是**连接池没配好导致短连接疯狂创建和销毁**，把临时端口耗光。排查时优先看连接池和 keep-alive 是否生效，不要一上来就改内核参数。

详细介绍：[一台主机上只能保持最多 65535 个 TCP 连接吗？](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/maximum-number-of-tcp-connections-per-host.md)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions2.md#L237)，来源许可：Apache-2.0。

<a id="ka8f7a5424759"></a>

## 三次握手四次挥手的变迁图

《TCP/IP详解 卷1:协议》有一张TCP状态变迁图，很具有代表性，有助于大家理解三次握手和四次挥手的状态变化。如下图所示，粗的实线箭头表示正常的客户端状态变迁，粗的虚线箭头表示正常的服务器状态变迁。

![](https://raw.githubusercontent.com/forthespada/InterviewGuide/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-04-net.assets/202205220036408.png)

<p  id="对称密钥加密的优点缺点"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-04-net.md#L182)，来源许可：Apache-2.0。

<a id="kf8b92d90ec29"></a>

## 三次握手相关内容：第一种回答

刚开始客户端处于 Closed 的状态，服务端处于 Listen 状态，进行三次握手：

- 第一次握手：客户端给服务端发一个 SYN 报文，并指明客户端的初始化序列号 ISN(c)。此时客户端处于 `SYN_SEND` 状态。

  首部的同步位SYN=1，初始序号seq=x，SYN=1的报文段不能携带数据，但要消耗掉一个序号。

- 第二次握手：服务器收到客户端的 SYN 报文之后，会以自己的 SYN 报文作为应答，并且也是指定了自己的初始化序列号 ISN(s)。同时会把客户端的 ISN + 1 作为ACK 的值，表示自己已经收到了客户端的 SYN，此时服务器处于 `SYN_RCVD` 的状态。

  在确认报文段中SYN=1，ACK=1，确认号ack=x+1，初始序号seq=y。

- 第三次握手：客户端收到 SYN 报文之后，会发送一个 ACK 报文，当然，也是一样把服务器的 ISN + 1 作为 ACK 的值，表示已经收到了服务端的 SYN 报文，此时客户端处于 `ESTABLISHED` 状态。服务器收到 ACK 报文之后，也处于 `ESTABLISHED` 状态，此时，双方已建立起了连接。

  确认报文段ACK=1，确认号ack=y+1，序号seq=x+1（初始为seq=x，第二个报文段所以要+1），ACK报文段可以携带数据，不携带数据则不消耗序号。

发送第一个SYN的一端将执行主动打开（active open），接收这个SYN并发回下一个SYN的另一端执行被动打开（passive open）。

在socket编程中，客户端执行connect()时，将触发三次握手。

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-03-net.md#L305)，来源许可：Apache-2.0。

<a id="k6b71fe664fce"></a>

## 三次握手相关内容：第二种回答

- **初始状态**：客户端处于 `closed(关闭)`状态，服务器处于 `listen(监听)` 状态。
- **第一次握手**：客户端发送请求报文将 `SYN = 1`同步序列号和初始化序列号`seq = x`发送给服务端，发送完之后客户端处于`SYN_Send`状态。（验证了客户端的发送能力和服务端的接收能力）
- **第二次握手**：服务端受到 `SYN` 请求报文之后，如果同意连接，会以自己的同步序列号`SYN(服务端) = 1`、初始化序列号 `seq = y`和确认序列号（期望下次收到的数据包）`ack = x+ 1` 以及确认号`ACK = 1`报文作为应答，服务器为`SYN_Receive`状态。（问题来了，两次握手之后，站在客户端角度上思考：我发送和接收都ok，服务端的发送和接收也都ok。但是站在服务端的角度思考：哎呀，我服务端接收ok，但是我不清楚我的发送ok不ok呀，而且我还不知道你接受能力如何呢？所以老哥，你需要给我三次握手来传个话告诉我一声。你要是不告诉我，万一我认为你跑了，然后我可能出于安全性的考虑继续给你发一次，看看你回不回我。）
- **第三次握手**： 客户端接收到服务端的 `SYN + ACK`之后，知道可以下次可以发送了下一序列的数据包了，然后发送同步序列号 `ack = y + 1`和数据包的序列号 `seq = x + 1`以及确认号`ACK = 1`确认包作为应答，客户端转为`established`状态。（分别站在双方的角度上思考，各自ok）

<p  id="为什么需要三次握手两次不行吗"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-03-net.md#L327)，来源许可：Apache-2.0。

<a id="kb87850a4a3cb"></a>

## 三次握手过程中可以携带数据吗？

其实第三次握手的时候，是可以携带数据的。但是，**第一次、第二次握手不可以携带数据**

为什么这样呢?大家可以想一个问题，假如第一次握手可以携带数据的话，如果有人要恶意攻击服务器，那他每次都在第一次握手中的 SYN 报文中放入大量的数据。

因为攻击者根本就不理服务器的接收、发送能力是否正常，然后疯狂着重复发 SYN 报文的话，这会让服务器花费很多时间、内存空间来接收这些报文。

也就是说，**第一次握手不可以放数据，其中一个简单的原因就是会让服务器更加容易受到攻击了。而对于第三次的话，此时客户端已经处于 ESTABLISHED 状态。**

**对于客户端来说，他已经建立起连接了，并且也已经知道服务器的接收、发送能力是正常的了，所以能携带数据也没啥毛病。**

<p  id="爱死外嗯攻击是什么"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-03-net.md#L383)，来源许可：Apache-2.0。

<a id="k4cb224db8287"></a>

## 为什么 TCP 是面向字节流，UDP 是面向报文？

![TCP 与 UDP 的消息边界](https://oss.javaguide.cn/github/javaguide/cs-basics/network/tcp-udp-byte-stream-tcp-udp-message-boundary.png)

TCP 是面向字节流的。应用层写入的数据会进入内核缓冲区，TCP 只保证这些字节可靠、有序地到达对端，不保证一次 `send()` 对应一次 `recv()`，也不保留应用层消息边界。因此接收方可能一次读到多条消息，也可能只读到半条消息，这就是常说的粘包、拆包现象。
![TCP 粘包 / 拆包为什么会出现？](https://oss.javaguide.cn/github/javaguide/cs-basics/network/tcp-udp-byte-stream-tcp-sticky-split-causes.png)

UDP 是面向报文的。应用层交给 UDP 的一次数据会作为一个 UDP 数据报发送，接收端也是按数据报读取，所以天然保留消息边界。不过 UDP 不保证可靠到达，也不保证顺序。

解决 TCP 粘包/拆包，本质是应用层协议自己定义消息边界。常见方案有固定长度、分隔符、长度头。工程里更常用长度头，因为它对二进制协议和变长消息更友好，但要处理字节序、最大长度限制、半包缓存和异常连接关闭等问题。

![应用层如何定义消息边界？](https://oss.javaguide.cn/github/javaguide/cs-basics/network/tcp-udp-byte-stream-tcp-message-boundary-solutions.png)

详细介绍：[为什么 TCP 是面向字节流，UDP 是面向报文？](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/tcp-byte-stream-udp-datagram.md)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions2.md#L110)，来源许可：Apache-2.0。

<a id="k08a88de4afb7"></a>

## 为什么区域传送用TCP协议？

因为TCP协议可靠性好啊！

你要从主DNS上复制内容啊，你用不可靠的UDP？ 因为TCP协议传输的内容大啊，你用最大只能传512字节的UDP协议？万一同步的数据大于512字节，你怎么办？所以用TCP协议比较好！

<p  id="长连接和短连接的区别"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-01-net.md#L146)，来源许可：Apache-2.0。

<a id="k78948ab304e4"></a>

## 为什么需要三次握手

> ​		TCP 建立连接时通过三次握手可以有效地避免历史错误连接的建立，减少通信双方不必要的资源消耗，三次握手能够帮助通信双方获取初始化序列号，它们能够保证数据包传输的不重不丢，还能保证它们的传输顺序，不会因为网络传输的问题发生混乱。
>
> * 两次握手：无法避免历史错误连接的初始化，浪费接收方的资源；
> * 四次握手：TCP 协议的设计可以让我们同时传递 `ACK` 和 `SYN` 两个控制信息，减少了通信次数，所以不需要使用更多的通信次数传输相同的信息。

![image-20210226164259010.png](https://i.loli.net/2021/03/10/ZGXRKOaj7Wxzs2p.png)

![](https://i.loli.net/2021/03/10/Woin6Xqkbj259Pf.png)

* 第一次握手

![](https://i.loli.net/2021/03/10/Ln1E65xVDuwcUHS.png)

* 第二次握手

![](https://i.loli.net/2021/03/10/8xhdkOwJaWEBRUu.png)

* 第三次握手

![](https://i.loli.net/2021/03/10/a7jyZsrhOKPiVL3.png)

![](https://i.loli.net/2021/03/10/s62ZLCtQXVgSPHk.png)

![](https://i.loli.net/2021/03/10/F3iblcJvD8YTPQI.png)

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/03-computer-basics/computer-network/network-protocols.md#L46)，来源许可：GPL-3.0。

<a id="k56911c929a75"></a>

## 为什么需要三次握手，两次不行吗？

弄清这个问题，我们需要先弄明白三次握手的目的是什么，能不能只用两次握手来达到同样的目的。

- 第一次握手：客户端发送网络包，服务端收到了。 这样服务端就能得出结论：客户端的发送能力、服务端的接收能力是正常的。
- 第二次握手：服务端发包，客户端收到了。 这样客户端就能得出结论：服务端的接收、发送能力，客户端的接收、发送能力是正常的。不过此时服务器并不能确认客户端的接收能力是否正常。
- 第三次握手：客户端发包，服务端收到了。 这样服务端就能得出结论：客户端的接收、发送能力正常，服务器自己的发送、接收能力也正常。

因此，需要三次握手才能确认双方的接收与发送能力是否正常。

试想如果是用两次握手，则会出现下面这种情况：

> 如客户端发出连接请求，但因连接请求报文丢失而未收到确认，于是客户端再重传一次连接请求。后来收到了确认，建立了连接。
>
> 数据传输完毕后，就释放了连接，客户端共发出了两个连接请求报文段，其中第一个丢失，第二个到达了服务端，但是第一个丢失的报文段只是在**某些网络结点长时间滞留了，延误到连接释放以后的某个时间才到达服务端**。
>
> 此时服务端误认为客户端又发出一次新的连接请求，于是就向客户端发出确认报文段，同意建立连接，不采用三次握手，只要服务端发出确认，就建立新的连接了，此时客户端忽略服务端发来的确认，也不发送数据，则服务端一致等待客户端发送数据，浪费资源。

<p  id="什么是半连接队列"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-03-net.md#L336)，来源许可：Apache-2.0。

<a id="k08498df2d638"></a>

## 为什么需要四次挥手

> ​		因为当服务端收到客户端的SYN连接请求报文后，可以直接发送SYN+ACK报文。其中ACK报文是用来应答的，SYN报文是用来同步的。但是关闭连接时，当服务端收到FIN报文时，很可能并不会立即关闭SOCKET，所以只能先回复一个ACK报文，告诉客户端，"你发的FIN报文我收到了"。只有等到我服务端所有的报文都发送完了，我才能发送FIN报文，因此不能一起发送。故需要四次挥手。

* 第一次挥手

![](https://i.loli.net/2021/03/10/dM1rBt5fqblzHcL.png)

* 第二次挥手

![](https://i.loli.net/2021/03/10/WMlSqjukUtpbZzr.png)

* 第三次挥手

![](https://i.loli.net/2021/03/10/nr6Vv3AeJHRNIGX.png)

* 第四次挥手

![](https://i.loli.net/2021/03/10/m7ht9eKsI4ZzWQT.png)

![](https://i.loli.net/2021/03/10/hDAObXlavYiRPC8.png)

![](https://i.loli.net/2021/03/10/62ceNEwKJf1TsGV.png)

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/03-computer-basics/computer-network/network-protocols.md#L75)，来源许可：GPL-3.0。

<a id="k67cc44213fe1"></a>

## 什么时候选择 TCP，什么时候选 UDP?

**常见问法：** 什么时候选择TCP，什么时候选UDP？

选择 TCP 还是 UDP，主要取决于你的应用**对数据传输的可靠性要求有多高，以及对实时性和效率的要求有多高**。

当**数据准确性和完整性至关重要，一点都不能出错**时，通常选择 TCP。因为 TCP 提供了一整套机制（三次握手、确认应答、重传、流量控制等）来保证数据能够可靠、有序地送达。典型应用场景如下：

- **Web 浏览（HTTP/HTTPS）:** 网页内容、图片、脚本必须完整加载才能正确显示。
- **文件传输（FTP, SCP）:** 文件内容不允许有任何字节丢失或错序。
- **邮件收发（SMTP, POP3, IMAP）:** 邮件内容需要完整无误地送达。
- **远程登录（SSH, Telnet）:** 命令和响应需要准确传输。
- ……

当**实时性、速度和效率优先，并且应用能容忍少量数据丢失或乱序**时，通常选择 UDP。UDP 开销小、传输快，没有建立连接和保证可靠性的复杂过程。典型应用场景如下：

- **实时音视频通信（VoIP, 视频会议，直播）:** 偶尔丢失一两个数据包（可能导致画面或声音短暂卡顿）通常比因为等待重传（TCP 机制）导致长时间延迟更可接受。应用层可能会有自己的补偿机制。
- **在线游戏:** 需要快速传输玩家位置、状态等信息，对实时性要求极高，旧的数据很快就没用了，丢失少量数据影响通常不大。
- **DHCP（动态主机配置协议）:** 客户端在请求 IP 时自身没有 IP 地址，无法满足 TCP 建立连接的前提条件，并且 DHCP 有广播需求、交互模式简单以及自带可靠性机制。
- **物联网（IoT）数据上报:** 某些场景下，传感器定期上报数据，丢失个别数据点可能不影响整体趋势分析。
- ……

### 补充说明

对某些实时性要求比较高的情况，选择UDP，比如游戏，媒体通信，实时视频流（直播），即使出现传输错误也可以容忍；其它大部分情况下，HTTP都是用TCP，因为要求传输的内容可靠，不出现丢失

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions2.md#L57)，来源许可：Apache-2.0。
- [Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Computer%20Network.md#L216)，来源许可：GPL-3.0。

<a id="k457d281cceb2"></a>

## 什么是三次握手 (three-way handshake)？

![image-20221212004219997](https://raw.githubusercontent.com/wolverinn/Waking-Up/cf692b53e1b3d1b740a97dab0e4e71db801daf33/_v_images/image-20221212004219997.png)

- 第一次握手：Client将SYN置1，随机产生一个初始序列号seq发送给Server，进入SYN_SENT状态；
- 第二次握手：Server收到Client的SYN=1之后，知道客户端请求建立连接，将自己的SYN置1，ACK置1，产生一个acknowledge number=sequence number+1，并随机产生一个自己的初始序列号，发送给客户端；进入SYN_RCVD状态；
- 第三次握手：客户端检查acknowledge number是否为序列号+1，ACK是否为1，检查正确之后将自己的ACK置为1，产生一个acknowledge number=服务器发的序列号+1，发送给服务器；进入ESTABLISHED状态；服务器检查ACK为1和acknowledge number为序列号+1之后，也进入ESTABLISHED状态；完成三次握手，连接建立。

### 参考资料

- [Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Computer%20Network.md#L31)，来源许可：GPL-3.0。

<a id="k1d6be9bc4705"></a>

## 你知道哪些基于 TCP/UDP 的协议？

TCP（传输控制协议）和 UDP（用户数据报协议）是互联网传输层的两大核心协议，它们为各种应用层协议提供了基础的通信服务。以下是一些常见的、分别构建在 TCP 和 UDP 之上的应用层协议：

**运行于 TCP 协议之上的协议（强调可靠、有序传输）：**

| 中文全称（缩写）            | 英文全称                           | 主要用途                     | 说明与特性                                                                                                                  |
| --------------------------- | ---------------------------------- | ---------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| 超文本传输协议（HTTP）      | HyperText Transfer Protocol        | 传输网页、超文本、多媒体内容 | **HTTP/1.x 和 HTTP/2 基于 TCP**。早期版本不加密，是 Web 通信的基础。                                                        |
| 安全超文本传输协议（HTTPS） | HyperText Transfer Protocol Secure | 加密的网页传输               | 使用 TLS 保护 HTTP。HTTP/1.1 和 HTTP/2 通常使用 TLS over TCP，HTTP/3 使用集成 TLS 1.3 的 QUIC。                             |
| 文件传输协议（FTP）         | File Transfer Protocol             | 文件传输                     | 传统的 FTP **明文传输**，不安全。推荐使用其安全版本 **SFTP（SSH File Transfer Protocol）** 或 **FTPS (FTP over SSL/TLS)**。 |
| 简单邮件传输协议（SMTP）    | Simple Mail Transfer Protocol      | **发送**电子邮件             | 负责将邮件从客户端发送到服务器，或在邮件服务器之间传递。可通过 **STARTTLS** 升级到加密传输。                                |
| 邮局协议第 3 版（POP3）     | Post Office Protocol version 3     | **接收**电子邮件             | 通常将邮件从服务器**下载到本地设备后删除服务器副本**（可配置保留）。**POP3S** 是其 SSL/TLS 加密版本。                       |
| 互联网消息访问协议（IMAP）  | Internet Message Access Protocol   | **接收和管理**电子邮件       | 邮件保留在服务器，支持多设备同步邮件状态、文件夹管理、在线搜索等。**IMAPS** 是其 SSL/TLS 加密版本。现代邮件服务首选。       |
| 远程终端协议（Telnet）      | Teletype Network                   | 远程终端登录                 | **明文传输**所有数据（包括密码），安全性极差，基本已被 SSH 完全替代。                                                       |
| 安全外壳协议（SSH）         | Secure Shell                       | 安全远程管理、加密数据传输   | 提供了加密的远程登录和命令执行，以及安全的文件传输（SFTP）等功能，是 Telnet 的安全替代品。                                  |

**运行于 UDP 协议之上的协议（强调快速、低开销传输）：**

| 中文全称（缩写）         | 英文全称                              | 主要用途                   | 说明与特性                                                                                                         |
| ------------------------ | ------------------------------------- | -------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| 超文本传输协议（HTTP/3） | HyperText Transfer Protocol version 3 | 新一代网页传输             | 基于 **QUIC** 协议（QUIC 本身构建于 UDP 之上），旨在减少延迟、缓解 TCP 队头阻塞；会话恢复时可使用 0-RTT 早期数据。 |
| 动态主机配置协议（DHCP） | Dynamic Host Configuration Protocol   | 动态分配 IP 地址及网络配置 | 客户端从服务器自动获取 IP 地址、子网掩码、网关、DNS 服务器等信息。                                                 |
| 域名系统（DNS）          | Domain Name System                    | 域名到 IP 地址的解析       | **通常使用 UDP** 进行快速查询。当响应数据包过大或进行区域传送（AXFR）时，会**切换到 TCP** 以保证数据完整性。       |
| 实时传输协议（RTP）      | Real-time Transport Protocol          | 实时音视频数据流传输       | 常用于 VoIP、视频会议、直播等。追求低延迟，允许少量丢包。通常与 RTCP 配合使用。                                    |
| RTP 控制协议（RTCP）     | RTP Control Protocol                  | RTP 流的质量监控和控制信息 | 配合 RTP 工作，提供丢包、延迟、抖动等统计信息，辅助流量控制和拥塞管理。                                            |
| 简单文件传输协议（TFTP） | Trivial File Transfer Protocol        | 简化的文件传输             | 功能简单，常用于局域网内无盘工作站启动、网络设备固件升级等小文件传输场景。                                         |
| 简单网络管理协议（SNMP） | Simple Network Management Protocol    | 网络设备的监控与管理       | 允许网络管理员查询和修改网络设备的状态信息。                                                                       |
| 网络时间协议（NTP）      | Network Time Protocol                 | 同步计算机时钟             | 用于在网络中的计算机之间同步时间，确保时间的一致性。                                                               |

**总结一下：**

- **TCP** 更适合那些对数据**可靠性、完整性和顺序性**要求高的应用，如网页浏览（HTTP/HTTPS）、文件传输（FTP/SFTP）、邮件收发（SMTP/POP3/IMAP）。
- **UDP** 则更适用于那些对**实时性要求高、能容忍少量数据丢失**的应用，如域名解析（DNS）、实时音视频（RTP）、在线游戏、网络管理（SNMP）等。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions2.md#L125)，来源许可：Apache-2.0。

<a id="ke5aafea7820c"></a>

## 可以采用四次握手吗？为什么？


可以。但是会降低传输的效率。

四次握手是指：第二次握手：Server只发送ACK和acknowledge number；而Server的SYN和初始序列号在第三次握手时发送；原来协议中的第三次握手变为第四次握手。出于优化目的，四次握手中的二、三可以合并。

### 参考资料

- [Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Computer%20Network.md#L55)，来源许可：GPL-3.0。

<a id="k32db5ab66ae6"></a>

## 四次挥手相关内容：第一种回答

刚开始双方都处于 ESTABLISHED 状态，假如是客户端先发起关闭请求。四次挥手的过程如下：

- 第一次挥手：客户端发送一个 FIN 报文，报文中会指定一个序列号。此时客户端处于 `FIN_WAIT1` 状态。 即发出**连接释放报文段**（FIN=1，序号seq=u），并停止再发送数据，主动关闭TCP连接，进入FIN_WAIT1（终止等待1）状态，等待服务端的确认。
- 第二次挥手：服务端收到 FIN 之后，会发送 ACK 报文，且把客户端的序列号值 +1 作为 ACK 报文的序列号值，表明已经收到客户端的报文了，此时服务端处于 `CLOSE_WAIT` 状态。 即服务端收到连接释放报文段后即发出**确认报文段**（ACK=1，确认号ack=u+1，序号seq=v），服务端进入CLOSE_WAIT（关闭等待）状态，此时的TCP处于半关闭状态，客户端到服务端的连接释放。客户端收到服务端的确认后，进入FIN_WAIT2（终止等待2）状态，等待服务端发出的连接释放报文段。
- 第三次挥手：如果服务端也想断开连接了，和客户端的第一次挥手一样，发给 FIN 报文，且指定一个序列号。此时服务端处于 `LAST_ACK` 的状态。 即服务端没有要向客户端发出的数据，服务端发出**连接释放报文段**（FIN=1，ACK=1，序号seq=w，确认号ack=u+1），服务端进入LAST_ACK（最后确认）状态，等待客户端的确认。
- 第四次挥手：客户端收到 FIN 之后，一样发送一个 ACK 报文作为应答，且把服务端的序列号值 +1 作为自己 ACK 报文的确认号值，此时客户端处于 `TIME_WAIT` 状态。需要过一阵子以确保服务端收到自己的 ACK 报文之后才会进入 CLOSED 状态，服务端收到 ACK 报文之后，就处于关闭连接了，处于 `CLOSED` 状态。 即客户端收到服务端的连接释放报文段后，对此发出**确认报文段**（ACK=1，seq=u+1，ack=w+1），客户端进入TIME_WAIT（时间等待）状态。此时TCP未释放掉，需要经过时间等待计时器设置的时间2MSL后，客户端才进入CLOSED状态。

收到一个FIN只意味着在这一方向上没有数据流动。**客户端执行主动关闭并进入TIME_WAIT是正常的，服务端通常执行被动关闭，不会进入TIME_WAIT状态。**

在socket编程中，任何一方执行close()操作即可产生挥手操作。 

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-04-net.md#L58)，来源许可：Apache-2.0。

<a id="k183fe5960122"></a>

## 四次挥手相关内容：第二种回答

- **初始化状态**：客户端和服务端都在连接状态，接下来开始进行四次分手断开连接操作。
- **第一次分手**：第一次分手无论是客户端还是服务端都可以发起，因为 TCP 是全双工的。

> 假如客户端发送的数据已经发送完毕，发送FIN = 1 **告诉服务端，客户端所有数据已经全发完了**，**服务端你可以关闭接收了**，但是如果你们服务端有数据要发给客户端，客户端照样可以接收的。此时客户端处于FIN = 1等待服务端确认释放连接状态。

- **第二次分手**：服务端接收到客户端的释放请求连接之后，**知道客户端没有数据要发给自己了**，**然后服务端发送ACK = 1告诉客户端收到你发给我的信息**，此时服务端处于 CLOSE_WAIT 等待关闭状态。（服务端先回应给客户端一声，我知道了，但服务端的发送数据能力即将等待关闭，于是接下来第三次就来了。）
- **第三次分手**：此时服务端向客户端把所有的数据发送完了，然后发送一个FIN = 1，**用于告诉客户端，服务端的所有数据发送完毕**，**客户端你也可以关闭接收数据连接了**。此时服务端状态处于LAST_ACK状态，来等待确认客户端是否收到了自己的请求。（服务端等客户端回复是否收到呢，不收到的话，服务端不知道客户端是不是挂掉了还是咋回事呢，所以服务端不敢关闭自己的接收能力，于是第四次就来了。）
- **第四次分手**：此时如果客户端收到了服务端发送完的信息之后，就发送ACK = 1，告诉服务端，客户端已经收到了你的信息。**有一个 2 MSL 的延迟等待**。

> 感谢网友勘误，https://github.com/forthespada/InterviewGuide/issues/25 - 2022.02.22

<p  id="挥手为什么需要四次"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-04-net.md#L71)，来源许可：Apache-2.0。

<a id="k9982d361125a"></a>

## 如何区分流量控制和拥塞控制？

- 流量控制属于通信双方协商；拥塞控制涉及通信链路全局。

- 流量控制需要通信双方各维护一个发送窗、一个接收窗，对任意一方，接收窗大小由自身决定，发送窗大小由接收方响应的TCP报文段中窗口值确定；拥塞控制的拥塞窗口大小变化由试探性发送一定数据量数据探查网络状况后而自适应调整。

- 实际最终发送窗口 = min{流控发送窗口，拥塞窗口}。

<p  id="常见的爱去提调皮状态码有哪些"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-06-net.md#L48)，来源许可：Apache-2.0。

<a id="k87e3b98acde0"></a>

## 如果已经建立了连接，但客户端出现了故障怎么办？


服务器每收到一次客户端的请求后都会重新复位一个计时器，时间通常是设置为2小时，若两小时还没有收到客户端的任何数据，服务器就会发送一个探测报文段，以后每隔75秒钟发送一次。若一连发送10个探测报文仍然没反应，服务器就认为客户端出了故障，接着就关闭连接。

### 参考资料

- [Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Computer%20Network.md#L77)，来源许可：GPL-3.0。

<a id="k56d00a87848d"></a>

## 常见TCP的连接状态有哪些？

- CLOSED：初始状态。
- LISTEN：服务器处于监听状态。
- SYN_SEND：客户端socket执行CONNECT连接，发送SYN包，进入此状态。
- SYN_RECV：服务端收到SYN包并发送服务端SYN包，进入此状态。
- ESTABLISH：表示连接建立。客户端发送了最后一个ACK包后进入此状态，服务端接收到ACK包后进入此状态。
- FIN_WAIT_1：终止连接的一方（通常是客户机）发送了FIN报文后进入。等待对方FIN。
- CLOSE_WAIT：（假设服务器）接收到客户机FIN包之后等待关闭的阶段。在接收到对方的FIN包之后，自然是需要立即回复ACK包的，表示已经知道断开请求。但是本方是否立即断开连接（发送FIN包）取决于是否还有数据需要发送给客户端，若有，则在发送FIN包之前均为此状态。
- FIN_WAIT_2：此时是半连接状态，即有一方要求关闭连接，等待另一方关闭。客户端接收到服务器的ACK包，但并没有立即接收到服务端的FIN包，进入FIN_WAIT_2状态。
- LAST_ACK：服务端发动最后的FIN包，等待最后的客户端ACK响应，进入此状态。
- TIME_WAIT：客户端收到服务端的FIN包，并立即发出ACK包做最后的确认，在此之后的2MSL时间称为TIME_WAIT状态。

<p  id="网络的七层五层模型主要的协议有哪些"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-03-net.md#L177)，来源许可：Apache-2.0。

<a id="kc407a82e28be"></a>

## 序列化协议对应于 TCP/IP 4 层模型的哪一层？

我们知道网络通信的双方必须要采用和遵守相同的协议。TCP/IP 四层模型是下面这样的，序列化协议属于哪一层呢？

1. 应用层
2. 传输层
3. 网络层
4. 网络接口层

![TCP/IP 四层模型](https://oss.javaguide.cn/github/javaguide/cs-basics/network/tcp-ip-4-model.png)

如上图所示，OSI 七层协议模型中，表示层做的事情主要就是对应用层的用户数据进行处理转换为二进制流。反过来的话，就是将二进制流转换成应用层的用户数据。这不就对应的是序列化和反序列化么？

因为，OSI 七层协议模型中的应用层、表示层和会话层对应的都是 TCP/IP 四层模型中的应用层，所以序列化协议属于 TCP/IP 协议应用层的一部分。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/java/basis/java-basic-questions-03.md#L539)，来源许可：Apache-2.0。

<a id="kfdfa42c10a3f"></a>

## 建立TCP服务器的各个系统调用过程是怎样的？

![](https://raw.githubusercontent.com/forthespada/InterviewGuide/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-05-net.assets/202205220023934.png)

![](https://raw.githubusercontent.com/forthespada/InterviewGuide/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-05-net.assets/202205220023348.png)

- 服务器：

  - 创建socket -> int socket(int domain, int type, int protocol);

    - domain：协议域，决定了socket的地址类型，IPv4为AF_INET。

    - type：指定socket类型，SOCK_STREAM为TCP连接。

    - protocol：指定协议。IPPROTO_TCP表示TCP协议，为0时自动选择type默认协议。

  - 绑定socket和端口号 -> int bind(int sockfd, const struct sockaddr *addr, socklen_t addrlen);

    - sockfd：socket返回的套接字描述符，类似于文件描述符fd。

    - addr：有个sockaddr类型数据的指针，指向的是被绑定结构变量。

```C++
        // IPv4的sockaddr地址结构
        struct sockaddr_in {
            sa_family_t sin_family;    // 协议类型，AF_INET
            in_port_t sin_port;    // 端口号
            struct in_addr sin_addr;    // IP地址
        };
        struct in_addr {
            uint32_t s_addr;
        }
```

    - addrlen：地址长度。

  - 监听端口号 -> int listen(int sockfd, int backlog);

    - sockfd：要监听的sock描述字。

    - backlog：socket可以排队的最大连接数。

  - 接收用户请求 -> int accept(int sockfd, struct sockaddr *addr, socklen_t *addrlen);

    - sockfd：服务器socket描述字。

    - addr：指向地址结构指针。

    - addrlen：协议地址长度。

    - 注：一旦accept某个客户机请求成功将返回一个全新的描述符用于标识具体客户的TCP连接。

  - 从socket中读取字符 -> ssize_t read(int fd, void *buf, size_t count);

    - fd：连接描述字。

    - buf：缓冲区buf。

    - count：缓冲区长度。

    - 注：大于0表示读取的字节数，返回0表示文件读取结束，小于0表示发生错误。

  - 关闭socket -> int close(int fd);

    - fd：accept返回的连接描述字，每个连接有一个，生命周期为连接周期。

    - 注：sockfd是监听描述字，一个服务器只有一个，用于监听是否有连接；fd是连接描述字，用于每个连接的操作。

- 客户机：

  - 连接指定计算机 -> int connect(int sockfd, struct sockaddr* addr, socklen_t addrlen);
    - sockfd客户端的sock描述字。

    - addr：服务器的地址。

    - addrlen：socket地址长度。

  - 向socket写入信息 -> ssize_t write(int fd, const void *buf, size_t count);
    - fd、buf、count：同read中意义。

    - 大于0表示写了部分或全部数据，小于0表示出错。

  - 关闭oscket -> int close(int fd);
    - fd：同服务器端fd。

<p  id="体系屁协议如何保证可靠传输"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-05-net.md#L113)，来源许可：Apache-2.0。

<a id="kb5ca4c13274a"></a>

## 手撕：TCP 与 UDP 主要区别，TCP 滑动窗口机制原理、窗口大小动态调整、双方如何交换窗口信息

**回答：**

TCP 面向连接、可靠、有序、字节流传输，依靠序列号、确认、重传、校验和、滑动窗口、拥塞控制实现；UDP 无连接、无序、不保证到达，报文边界保留，开销和延迟更低，可靠性由应用自行补足。

TCP 接收窗口由接收方在 Window 字段通告，发送方维护未确认数据量；拥塞窗口由发送方根据网络拥塞动态调整，实际发送窗口约为 $\min(rwnd,cwnd)$。滑动窗口通过累计 ACK、选择确认和重传推进。要区分流量控制的 `rwnd` 与拥塞控制的 `cwnd`，双方通过 TCP 首部和 ACK 交换接收窗口，不能说“窗口大小由双方直接协商成一个值”。

<a id="tencent-llm-collection-20260903-q42"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E8%85%BE%E8%AE%AF%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L776)，来源许可：GPL-3.0。

<a id="k5ebe2a82344b"></a>

## 本地代理连接失败时，如何按分层思路定位端口、配置、DNS、规则、节点和目标站问题？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐⭐ (5/5)**

### 先读错误对象，再决定检查哪一层

代理排障最常见的低效方式是不断切换节点。高效方法是先问：错误中的主机和端口是谁？失败发生在 DNS、TCP、代理握手、TLS 还是 HTTP 业务层？

例如：

```text
Failed to connect to 127.0.0.1 port 7890: Connection refused
```

这里失败对象是本机回环地址，不是 GitHub，也不是远端节点。`Connection refused` 通常表示该地址可达，但没有进程监听这个端口，或监听协议/地址不匹配。若当前代理实际监听 `7897`，而 Git 仍保存 `7890`，根因是客户端配置漂移。此时换远端节点没有意义，因为请求根本尚未进入代理内核。

### 七层排查顺序

| 层级 | 要回答的问题 | 只读验证示例 | 典型现象 |
|---|---|---|---|
| 1. 客户端配置 | 应用实际读到哪个代理？ | `git config --show-origin --get-regexp '.*proxy.*'`、检查代理环境变量 | 仍引用旧端口、不同工具行为不一致 |
| 2. 本地监听 | 地址、端口和协议是否有人监听？ | `nc -zv 127.0.0.1 7897`、`lsof -nP -iTCP:7897 -sTCP:LISTEN` | `connection refused` |
| 3. 代理握手 | HTTP/SOCKS 协议是否与端口匹配？ | `curl --proxy http://127.0.0.1:7897 https://example.com` | 握手乱码、认证失败、CONNECT 失败 |
| 4. DNS | 域名在哪里解析，结果是否正确？ | `dig`、代理日志、对比本地与远端解析 | 域名失败、误分流、错误 IP |
| 5. 规则 | 请求命中了 DIRECT、REJECT 还是代理组？ | 查看连接日志中的规则与出站 | 节点正常但请求走了直连或拒绝 |
| 6. 节点 | 到节点的网络和协议握手是否成功？ | 内核日志、健康检查、多个已知目标交叉验证 | 超时、认证或协议握手失败 |
| 7. 目标业务 | 目标站是否可用、鉴权是否正确？ | HTTP 状态码、TLS 证书、API 错误体 | `401`、`403`、`421`、`429`、`5xx` |

### HTTP 状态码不等于网络失败

能收到 `401`、`403`、`404`、`421` 或 `429`，通常说明 DNS、TCP、代理隧道与 TLS 至少已经走到目标服务或其网关。此时应分析路径、Host/SNI、认证、配额和业务语义，而不是笼统宣称“VPN 不可用”。反过来，`connection refused`、连接超时、TLS alert 与 HTTP `5xx` 也不能混为一类。

### 可重复的最小验证矩阵

排查时至少选择三类目标：公网 IP 查询服务、稳定的静态网站、实际业务 API。这样可以分辨“代理整体不可用”“特定域名规则错误”“特定服务拒绝请求”。对于 Git，可用 `git ls-remote --heads origin` 做只读传输检查；它能验证网络和远端读取，但不能证明当前分支一定有推送权限。

任何修改前都应先用 `--show-origin` 或等价手段找到配置来源，因为系统代理、Shell 环境变量、Git 全局配置、仓库配置、应用内配置可能同时存在。修复要对准实际生效层，而不是继续叠加配置。

**面试中可以用一句话收束：先定位失败对象和协议阶段，再沿“客户端配置 -> 本地监听 -> 代理握手 -> DNS -> 规则 -> 节点 -> 目标业务”逐层收敛；错误文本本身就是最短路径。**

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E4%BB%A3%E7%90%86%E3%80%81%E9%9A%A7%E9%81%93%E4%B8%8EVPN%E6%9C%AC%E8%B4%A8%E5%8E%9F%E7%90%86%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L198)，来源许可：GPL-3.0。

<a id="k3b70b162a53a"></a>

## 浏览器在与服务器建立了一个 TCP 连接后是否会在一个 HTTP 请求完成后断开？什么情况下会断开？

在 HTTP/1.0 中，一个服务器在发送完一个 HTTP 响应后，会断开 TCP 链接。但是这样每次请求都会重新建立和断开 TCP 连接，代价过大。所以虽然标准中没有设定，**某些服务器对 Connection: keep-alive 的 Header 进行了支持**。

意思是说，完成这个 HTTP 请求之后，不要断开 HTTP 请求使用的 TCP 连接。这样的好处是连接可以被重新使用，之后发送 HTTP 请求的时候不需要重新建立 TCP 连接，以及如果维持连接，那么 SSL 的开销也可以避免。

**持久连接**：既然维持 TCP 连接好处这么多，HTTP/1.1 就把 Connection 头写进标准，并且默认开启持久连接，除非请求中写明 Connection: close，那么浏览器和服务器之间是会维持一段时间的 TCP 连接，不会一个请求结束就断掉。

默认情况下建立 TCP 连接不会断开，只有在请求报头中声明 Connection: close 才会在请求完成后关闭连接。

<p  id="三次握手相关内容"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-03-net.md#L285)，来源许可：Apache-2.0。

<a id="k1cacdd46aa61"></a>

## 浏览器对同一 Host 建立 TCP 连接到的数量有没有限制？

假设我们还处在 HTTP/1.1 时代，那个时候没有多路传输，当浏览器拿到一个有几十张图片的网页该怎么办呢？

肯定不能只开一个 TCP 连接顺序下载，那样用户肯定等的很难受，但是如果每个图片都开一个 TCP 连接发 HTTP 请求，那电脑或者服务器都可能受不了，要是有 1000 张图片的话总不能开 1000 个TCP 连接吧，你的电脑同意 NAT 也不一定会同意。

**有。Chrome 最多允许对同一个 Host 建立六个 TCP 连接。不同的浏览器有一些区别。**

如果图片都是 HTTPS 连接并且在同一个域名下，那么浏览器在 SSL 握手之后会和服务器商量能不能用 HTTP2，如果能的话就使用 Multiplexing 功能在这个连接上进行多路传输。

不过也未必会所有挂在这个域名的资源都会使用一个 TCP 连接去获取，但是可以确定的是 Multiplexing 很可能会被用到。

如果发现用不了 HTTP2 呢？或者用不了 HTTPS（现实中的 HTTP2 都是在 HTTPS 上实现的，所以也就是只能使用 HTTP/1.1）。

那浏览器就会在一个 HOST 上建立多个 TCP 连接，连接数量的最大限制取决于浏览器设置，这些连接会在空闲的时候被浏览器用来发送新的请求，如果所有的连接都正在发送请求呢？那其他的请求就只能等等了。

>update1：微信好友“卷轴”提出勘误“连接到”-》“连接到的”
>
><p  id="在浏览器中输入地址后显示主页的过程"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-01-net.md#L270)，来源许可：Apache-2.0。

<a id="k58a8125b79f1"></a>

## 第三次握手中，如果客户端的ACK未送达服务器，会怎样？


Server端：  
由于Server没有收到ACK确认，因此会重发之前的SYN+ACK（默认重发五次，之后自动关闭连接进入CLOSED状态），Client收到后会重新传ACK给Server。

Client端，两种情况：  
1. 在Server进行超时重发的过程中，如果Client向服务器发送数据，数据头部的ACK是为1的，所以服务器收到数据之后会读取 ACK number，进入 establish 状态  
2. 在Server进入CLOSED状态之后，如果Client向服务器发送数据，服务器会以RST包应答。

### 参考资料

- [Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Computer%20Network.md#L64)，来源许可：GPL-3.0。

<a id="k1d48ac179e16"></a>

## 能 Ping 通，TCP 就一定能连通吗？

先说结论：**不是**。

Ping 使用 ICMP（网络层），TCP 连接使用 TCP（传输层），两者可能经过同一条网络路径，但中间设备会按协议类型、端口、连接状态和安全策略分别处理。你能 Ping 通，只能说明 ICMP Echo 这条路径能往返，不等于目标 TCP 端口一定可达。

![ICMP与TCP路径差异](https://oss.javaguide.cn/github/javaguide/cs-basics/network/can-ping-but-tcp-may-not-connect-icmp-and-tcp-path-differences.png)

常见原因有这几种：

- **防火墙策略不同**：很多网络设备允许 ICMP（方便运维探测），但 TCP 端口规则收得更紧，可能只开放了 `22`、`80`、`443`，其他端口一律不放。
- **服务没启动或端口没监听**：主机能回 ICMP，但 Nginx 没启动、MySQL 没监听，Ping 通但 TCP 连不上。
- **中间有 NAT / 负载均衡 / 安全设备**：公网 IP 后面可能不是一台真实服务器，ICMP 响应可能来自中间设备，不能直接等同于后端服务可用。
- **HTTPS 还可能卡在 TLS 握手的 SNI**：TCP 三次握手可能成功了，但 `ClientHello` 里的 SNI 被中间设备识别并拦截，导致连接重置或卡住。

反过来也成立：**Ping 不通，不代表 TCP 一定不通**。有些服务器或云安全组直接禁 ICMP，但业务端口正常工作。

排查建议：先看 DNS（域名场景），再用 `ping` 看 ICMP，然后用 `nc` 测端口，最后用 `curl` 或 `openssl s_client` 看 HTTPS / TLS。别用一个命令过早下结论。

![HTTPS连接排查层次](https://oss.javaguide.cn/github/javaguide/cs-basics/network/can-ping-but-tcp-may-not-connect-https-connection-troubleshooting-layers.png)

详细介绍：[能 Ping 通，TCP 就一定能连通吗？](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/can-ping-but-tcp-may-not-connect.md)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions.md#L539)，来源许可：Apache-2.0。

<a id="k989b472d9813"></a>

## 补充题：封包和拆包你听说过吗？它是基于TCP还是UDP的？

封包和拆包都是基于TCP的概念。因为TCP是无边界的流传输，所以需要对TCP进行封包和拆包，确保发送和接收的数据不粘连。

* 封包：封包就是在发送数据报的时候为每个TCP数据包加上一个包头，将数据报分为包头和包体两个部分。包头是一个固定长度的结构体，里面包含该数据包的总长度。
* 拆包：接收方在接收到报文后提取包头中的长度信息进行截取。

<p id="有地皮的特点有哪些附赠体系屁的特点"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-05-net.md#L282)，来源许可：Apache-2.0。

<a id="k67786b21d94b"></a>

## 面向连接和无连接的区别


无连接的网络服务（数据报服务）-- 面向连接的网络服务（虚电路服务）

虚电路服务：首先建立连接，所有的数据包经过相同的路径，服务质量有较好的保证；

数据报服务：每个数据包含目的地址，数据路由相互独立（路径可能变化）；网络尽最大努力交付数据，但不保证不丢失、不保证先后顺序、不保证在时限内交付；网络发生拥塞时，可能会将一些分组丢弃；

![virtual circuit](https://raw.githubusercontent.com/wolverinn/Waking-Up/cf692b53e1b3d1b740a97dab0e4e71db801daf33/_v_images/20191201081919108_30577.png)

### 参考资料

- [Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Computer%20Network.md#L233)，来源许可：GPL-3.0。
