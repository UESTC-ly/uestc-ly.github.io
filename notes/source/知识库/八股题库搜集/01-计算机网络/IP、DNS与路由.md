# IP、DNS与路由

<a id="kef133edef642"></a>

## ARP 协议解决了什么问题？

ARP 协议，全称 **地址解析协议（Address Resolution Protocol）**，它解决的是网络层地址和链路层地址之间的转换问题。因为一个 IP 数据报在物理上传输的过程中，总是需要知道下一跳（物理上的下一个目的地）该去往何处，但 IP 地址属于逻辑地址，而 MAC 地址才是物理地址，ARP 协议解决了 IP 地址转 MAC 地址的一些问题。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions2.md#L344)，来源许可：Apache-2.0。

<a id="k29034907e7a4"></a>

## ARP协议的工作原理和流程，路由器是如何转发的？(路由表的工作原理)

**工作流程**

* 当主机A欲向本局域网上的某个主机 B 发送 IP 数据报时，就先在其 ARP高速缓存中查看有无主机B的IP地址；
  * 如有，就可查出其对应的硬件地址，再将此硬件地址写入MAC帧，然后通过局域网将该MAC帧发往此硬件地址；
  * 如没有，ARP进程在本局域网上广播发送一个ARP请求分组。收到ARP响应分组后，将得到的IP地址到硬件地址的映射写入ARP高速缓存。

**路由器工作原理**

1. 一个帧到达路由器后，首先检查帧中目标MAC地址是否是本接口的MAC，如不是则丢弃，如是则解封装并将IP包移动到路由器内部；
2. 将IP包中目标IP与路由表进行匹配，如匹配路由表不成功，则丢弃，返回ICMP（互联网控制消息协议）错误消息；若成功，则将数据路由到相应的出口，再封装帧头帧尾；
3. 检查ARP缓存中是否有下一跳的MAC，如有则重新封装出去；如没有，则发送ARP请求广播报文获取下一跳的MAC，并记录到ARP缓存表中，再重新封装数据帧发送出去。

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/03-computer-basics/computer-network/network-protocols.md#L242)，来源许可：GPL-3.0。

<a id="k429c68d416d5"></a>

## Clash 类规则代理如何处理 DNS？fake-IP、DNS 泄漏和污染分别是什么？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

### DNS 不是代理之外的附属步骤，而是策略输入

域名请求在真正建立连接前通常要变成 IP。若应用先使用本地系统 DNS 得到 IP，代理内核可能只看到一个地址，丢失域名规则所需的上下文；若 DNS 返回了被污染、错误地区或不可达的地址，即使代理节点正常，连接也可能失败。

Clash 类内核通常内置 DNS 服务，可选择普通 UDP/TCP DNS、DoT 或 DoH 上游。RFC 8484 定义的 DoH 把 DNS 查询响应映射到 HTTPS 交换，主要收益是防止路径上的明文窥探与篡改，但它不会自动证明解析结果适合当前业务，也不会消除 DoH 服务商的可见性。

### redir-host 与 fake-IP 的思路

- **redir-host 类思路**：先得到真实 IP，再用域名与 IP 映射辅助规则和转发。语义直观，但域名恢复、缓存和多 IP 场景可能复杂。
- **fake-IP 类思路**：内核先给应用返回一个保留地址池中的“占位 IP”，同时保存 `域名 <-> fake-IP` 映射。应用随后连接这个占位地址时，内核可以恢复原始域名，再按域名规则选择出站并在合适一侧完成真实解析。

fake-IP 的本质不是伪造公网身份，而是延迟真实解析并保留域名语义。它可能与局域网域名、硬编码 IP 校验、某些游戏或局域网发现协议冲突，因此需要旁路域名清单或针对性回退。

### 三类高频问题要分开

1. **DNS 污染或劫持**：查询响应被路径中间设备伪造、篡改或错误重定向，得到错误地址。
2. **DNS 泄漏**：本应由受控路径解析的域名却交给了本地 ISP、企业 DNS 或其他非预期解析器，暴露访问意图或产生分流错误。
3. **DNS 回环依赖**：代理访问 DoH 上游本身又需要先通过同一套未建立的 DNS 或代理路径解析，形成启动死锁。工程上需要 bootstrap DNS、IP 直连或明确的解析器依赖顺序。

DNS 诊断不能只看 `ping`。应分别验证系统解析器、代理内置解析器、规则命中的域名、最终连接使用的 IP，以及 DNS 请求究竟走直连还是代理。

**面试中可以用一句话收束：DNS 决定的不只是“域名对应哪个 IP”，还决定代理规则有没有足够上下文；fake-IP 的核心价值是保留域名语义并把真实解析延迟到策略决策之后。**

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E4%BB%A3%E7%90%86%E3%80%81%E9%9A%A7%E9%81%93%E4%B8%8EVPN%E6%9C%AC%E8%B4%A8%E5%8E%9F%E7%90%86%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L133)，来源许可：GPL-3.0。

<a id="k996e6024e44a"></a>

## Disadvantage(s): DNS

* Accessing a DNS server introduces a slight delay, although mitigated by caching described above.
* DNS server management could be complex and is generally managed by [governments, ISPs, and large companies](http://superuser.com/questions/472695/who-controls-the-dns-servers/472729).
* DNS services have recently come under [DDoS attack](http://dyn.com/blog/dyn-analysis-summary-of-friday-october-21-attack/), preventing users from accessing websites such as Twitter without knowing Twitter's IP address(es).

### 参考资料

- [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer/blob/ae9bbd7b02d90b9866215de185217d33f39ab733/README.md#L607)，来源许可：CC-BY-4.0。

<a id="k66c87577f370"></a>

## DNS 劫持了解吗？如何应对？

DNS 劫持是一种网络攻击，它通过修改 DNS 服务器的解析结果，使用户访问的域名指向错误的 IP 地址，从而导致用户无法访问正常的网站，或者被引导到恶意的网站。DNS 劫持有时也被称为 DNS 重定向、DNS 欺骗或 DNS 污染。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions.md#L589)，来源许可：Apache-2.0。

<a id="kf5882ffc1449"></a>

## DNS 服务器有哪些？根服务器有多少个？

DNS 可以从两个维度描述。权威层次包括根、顶级域和具体区域的权威服务器；查询侧则包括存根解析器、递归解析器和转发器等角色。同一套软件或同一台服务器也可能承担多个角色，因此这些类别不是互斥且穷尽的“服务器类型”。

- 根 DNS 服务器向查询方提供顶级域服务器的转介信息。
- 顶级域 DNS 服务器通常返回目标域权威服务器的转介信息。
- 权威 DNS 服务器保存一个或多个区域的数据，并对这些区域内的查询给出权威回答。
- 递归解析器接收客户端查询，先检查缓存，必要时再向根、TLD 和权威服务器逐级查询。它属于查询侧角色，不是权威 DNS 层次的一层。

根服务器系统逻辑上有 13 个命名的根服务器标识，从 `a.root-servers.net` 到 `m.root-servers.net`，由 12 个独立运营组织负责。每个标识背后可以通过 Anycast 部署多个物理实例，实例数量和地点会持续变化，应以 [Root-Servers.org](https://root-servers.org/) 的实时数据为准。不能把 13 个逻辑标识理解为全球只有 13 台物理服务器。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions.md#L574)，来源许可：Apache-2.0。

<a id="k18f88dd9f835"></a>

## DNS、CDN、负载均衡和API Gateway对AI服务稳定性有什么作用？

AI服务上线后，稳定性不只取决于模型，还取决于入口流量治理：

| 组件 | 作用 | AI服务价值 |
| --- | --- | --- |
| DNS | 域名到IP解析 | 故障切换、就近访问 |
| CDN | 静态资源缓存和加速 | 图片、视频、模型demo页面、生成结果下载 |
| 负载均衡 | 分发请求到多个实例 | 扩容、故障摘除、灰度发布 |
| API Gateway | 统一鉴权、限流、路由、审计 | 多模型API、Agent工具API、租户隔离 |

对AIGC服务而言，API Gateway通常承担统一入口角色：检查API key、限制QPS和token预算、记录请求日志、路由到不同模型、做灰度发布和熔断降级。负载均衡则要理解模型服务的特殊性：不是所有实例都等价，不同实例可能绑定不同GPU、加载不同模型、拥有不同显存余量。

面试回答时可以补充：长连接和流式请求会影响负载均衡策略，不能只按请求数平均分配，还要考虑连接时长、GPU队列长度、KV Cache占用和实例健康状态。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L1417)，来源许可：GPL-3.0。

<a id="k2cd87ada1916"></a>

## DNS查询方式有哪些？

### 递归解析

当局部DNS服务器自己不能回答客户机的DNS查询时，它就需要向其他DNS服务器进行查询。此时有两种方式。

**局部DNS服务器自己负责向其他DNS服务器进行查询，一般是先向该域名的根域服务器查询，再由根域名服务器一级级向下查询**。最后得到的查询结果返回给局部DNS服务器，再由局部DNS服务器返回给客户端。

### 迭代解析

当局部DNS服务器自己不能回答客户机的DNS查询时，也可以通过迭代查询的方式进行解析。

局部DNS服务器不是自己向其他DNS服务器进行查询，**而是把能解析该域名的其他DNS服务器的IP地址返回给客户端DNS程序**，客户端DNS程序再继续向这些DNS服务器进行查询，直到得到查询结果为止。

也就是说，迭代解析只是帮你找到相关的服务器而已，而不会亲自帮你去查。

举个例子，比如说："baidu.com的服务器ip地址在192.168.4.5这里，你自己去查吧，本人比较忙，只能帮你到这里了。"差不多就是这个意思了

<p  id="中缓存的私有和共有字段知道吗"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-02-net.md#L258)，来源许可：Apache-2.0。

<a id="ke801bb3d2354"></a>

## DNS的具体过程

1. 检查浏览器缓存中是否缓存过该域名对应的IP地址；
2. 如果在浏览器缓存中没有找到IP，那么将继续查找本机系统是否缓存过IP；
3. 向本地域名解析服务系统发起域名解析的请求；
4. 向根域名解析服务器发起域名解析请求；
5. 根域名服务器返回gTLD（通用顶级域名）域名解析服务器地址；
6. 向gTLD服务器发起解析请求；
7. gTLD服务器接收请求并返回Name Server服务器；
8. Name Server服务器返回IP地址给本地服务器；
9. 本地域名服务器缓存解析结果；
10. 返回解析结果给用户。

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/03-computer-basics/computer-network/network-protocols.md#L229)，来源许可：GPL-3.0。

<a id="k53ec7ba35504"></a>

## IP 协议的作用是什么？

**IP（Internet Protocol，网际协议）** 是 TCP/IP 协议中最重要的协议之一，属于网络层的协议，主要作用是定义数据包的格式、对数据包进行路由和寻址，以便它们可以跨网络传播并到达正确的目的地。

目前 IP 协议主要分为两种，一种是过去的 IPv4，另一种是较新的 IPv6，目前这两种协议都在使用，但后者已经被提议来取代前者。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions2.md#L257)，来源许可：Apache-2.0。

<a id="k4dfce8b239b4"></a>

## IPv4 和 IPv6 有什么区别？

**常见问法：** IPv4和IPv6的区别

**IPv4（Internet Protocol version 4）** 是目前广泛使用的 IP 地址版本，其格式是四组由点分隔的数字，例如：123.89.46.72。IPv4 使用 32 位地址作为其 Internet 地址，这意味着共有约 42 亿（2^32）个可用 IP 地址。

![IPv4 地址使用点分十进制格式表示 32 位地址](https://oss.javaguide.cn/github/javaguide/cs-basics/network/Figure-1-IPv4Addressformatwithdotteddecimalnotation-29c824f6a451d48d8c27759799f0c995.png)

这么少当然不够用啦！为了解决 IP 地址耗尽的问题，最根本的办法是采用具有更大地址空间的新版本 IP 协议 - **IPv6（Internet Protocol version 6）**。IPv6 地址使用更复杂的格式，该格式使用由单或双冒号分隔的一组数字和字母，例如：2001:0db8:85a3:0000:0000:8a2e:0370:7334。IPv6 使用 128 位互联网地址，这意味着越有 2^128（3 开头的 39 位数字，恐怖如斯）个可用 IP 地址。

![IPv6 地址使用十六进制冒号分隔格式表示 128 位地址](https://oss.javaguide.cn/github/javaguide/cs-basics/network/Figure-2-IPv6Addressformatwithhexadecimalnotation-7da3a419bd81627a9b2cef3b0efb4940.png)

除了更大的地址空间之外，IPv6 的优势还包括：

- **无状态地址自动配置（Stateless Address Autoconfiguration，简称 SLAAC）**：主机可以根据路由器通告的前缀和接口标识生成 IPv6 地址，不必依赖 DHCPv6 分配地址。地址使用前通常会执行重复地址检测（DAD），但 DAD 检查的是本链路内是否存在重复，而且检测并非完全可靠，不能据此声称地址得到“全球唯一”保证。
- **NAT（Network Address Translation，网络地址转换）成为可选项**：IPv6 地址资源充足，可以给全球每个设备一个独立的地址。
- **对标头结构进行了改进**：IPv6 基本头部简化了常见转发路径上的部分处理，但实际性能仍取决于硬件、扩展头、网络策略和具体实现，不能只凭头部结构保证整体性能一定提高。
- **可选的扩展头**：允许在 IPv6 标头中添加不同的扩展头（Extension Headers），用于实现不同类型的功能和选项。
- **ICMPv6（Internet Control Message Protocol for IPv6）**：IPv6 中的 ICMPv6 相较于 IPv4 中的 ICMP 有了一些改进，如邻居发现、路径 MTU 发现等功能的改进，从而提升了网络的可靠性和性能。
- ……

### 补充说明

* IPv4协议具有32位（4字节）地址长度；IPv6协议具有128位（16字节）地址长度；
* IPv4地址是以小数表示的二进制数。 IPv6地址是以十六进制表示的二进制数；
* IPv4协议的数据包需要576个字节，碎片可选 ；IPv6协议的数据包需要1280个字节，不会碎片；
* IPv4根据提供的 IP 选项，有 20-60 个字节的可变长度；IPv6有40 个字节的固定长度。没有 IP 报头选项。通常，IPv6 报头比 IPv4 报头简单。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions2.md#L281)，来源许可：Apache-2.0。
- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/03-computer-basics/computer-network/network-protocols.md#L256)，来源许可：GPL-3.0。

<a id="k70c0f5a7ebcd"></a>

## 什么叫划分子网？

从主机号host-id借用若干个比特作为子网号subnet-id；子网掩码：网络号和子网号都为1，主机号为0；数据报仍然先按照网络号找到目的网络，发送到路由器，路由器再按照网络号和子网号找到目的子网：将子网掩码与目标地址逐比特与操作，若结果为某个子网的网络地址，则送到该子网。

### 参考资料

- [Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Computer%20Network.md#L395)，来源许可：GPL-3.0。

<a id="kd69fc5efabf1"></a>

## 什么是 IP 地址过滤？

**IP 地址过滤（IP Address Filtering）** 简单来说就是限制或阻止特定 IP 地址或 IP 地址范围的访问。例如，你有一个图片服务突然被某一个 IP 地址攻击，那我们就可以禁止这个 IP 地址访问图片服务。

IP 地址过滤是一种简单的网络安全措施，实际应用中一般会结合其他网络安全措施，如认证、授权、加密等一起使用。单独使用 IP 地址过滤并不能完全保证网络的安全。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions2.md#L275)，来源许可：Apache-2.0。

<a id="kcaaa99b2094f"></a>

## 什么是 IP 地址？IP 寻址如何工作？

IP 地址通常分配给网络接口，用于在特定作用域和路由上下文中标识通信端点。一个接口可以有多个地址，地址也可能动态变化；私有地址可以在不同网络中重复使用，Anycast 地址还可以分配给多个接口。IPv4 地址示例为 `192.168.1.1`，IPv6 地址示例为 `2001:0db8:85a3:0000:0000:8a2e:0370:7334`。

当网络设备发送 IP 数据包时，数据包中包含 **源 IP 地址** 和 **目的 IP 地址**。它们标识本次通信使用的源接口地址和目标地址，而不是设备永久不变的身份。

网络设备根据目的 IP 地址来判断数据包的目的地，并将数据包转发到正确的目的地网络或子网络，从而实现了设备间的通信。

这种基于 IP 地址的寻址方式是互联网通信的基础，它允许数据包在不同网络之间传递。地址是否唯一、能否全局路由取决于地址类型和作用域，不能笼统地把 IP 地址描述为每台设备全球唯一的身份证。

![IP 地址使数据包到达其目的地](https://oss.javaguide.cn/github/javaguide/cs-basics/network/internet_protocol_ip_address_diagram.png)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions2.md#L263)，来源许可：Apache-2.0。

<a id="k97e8d2ff1052"></a>

## 什么是RIP (Routing Information Protocol, 距离矢量路由协议)? 算法是什么？

每个路由器维护一张表，记录该路由器到其它网络的”跳数“，路由器到与其直接连接的网络的跳数是1，每多经过一个路由器跳数就加1；更新该表时和相邻路由器交换路由信息；路由器允许一个路径最多包含15个路由器，如果跳数为16，则不可达。交付数据报时优先选取距离最短的路径。

（PS：RIP是应用层协议：[https://www.zhihu.com/question/19645407](https://www.zhihu.com/question/19645407)）

优缺点

- 实现简单，开销小
- 随着网络规模扩大开销也会增大；
- 最大距离为15，限制了网络的规模；
- 当网络出现故障时，要经过较长的时间才能将此信息传递到所有路由器

### 参考资料

- [Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Computer%20Network.md#L352)，来源许可：GPL-3.0。

<a id="kf98ac3c3848f"></a>

## 介绍一下计算机中DNS（Domain Name System）的概念

DNS（Domain Name System，域名系统）是互联网中的一项基础技术，其作用是将易读的域名（如 `www.WeThinkIn.com`）转换为计算机可以识别的 IP 地址（如 `192.168.1.1` 或 `2606:2800:220:1:248:1893:25c8:1946`），以便用户能够进行网站访问、邮件服务和其他网络通信等功能。它具有分布式设计、缓存机制和容错性，同时也面临安全和隐私挑战。通过合理配置和使用 DNS 技术，在AIGC、传统深度学习以及自动驾驶领域都非常重要，可以提高AI网络服务的可靠性和性能。

### **1. DNS 的作用**
在计算机网络中，主机之间通过 IP 地址通信。然而，IP 地址（尤其是 IPv6 地址）不易记忆，因此 DNS 提供了以下功能：
1. **域名到 IP 地址的映射**：解析用户输入的域名为对应的 IP 地址。
2. **IP 地址到域名的映射**：支持反向解析，将 IP 地址解析为域名。
3. **分布式的名称管理**：通过层次化的系统分布管理域名，提供高效、可靠的域名解析服务。

例如：
- 用户访问 `https://www.WeThinkIn.com`，DNS 将其解析为 `142.250.72.36`。
- 浏览器使用这个 IP 地址建立连接，并加载网页内容。

### **2. DNS 的层次结构**
DNS 采用分层的树状结构，由多个域组成，每个域由点号（`.`）分隔：
1. **根域（Root Domain）**：
   - 是 DNS 层次结构的顶层，表示为一个隐式的点号（`.`）。
   - 例如：`www.WeThinkIn.com.` 实际包含根域的点号。
   - 根域由 13 组根服务器（Root Servers）管理，负责引导域名解析。

2. **顶级域（Top-Level Domain, TLD）**：
   - 位于根域下方，例如：
     - 通用顶级域：`.com`, `.org`, `.net`, `.edu`
     - 国家/地区代码顶级域：`.cn`, `.uk`, `.us`
   - TLD 由 ICANN（互联网名称与数字地址分配机构）授权的机构管理。

3. **二级域（Second-Level Domain, SLD）**：
   - TLD 之下的域名，例如 `WeThinkIn.com` 中的 `WeThinkIn` 是二级域。
   - 这些域名通常由企业或个人注册。

4. **子域（Subdomain）**：
   - 二级域名下可以划分子域，例如 `www.WeThinkIn.com` 中的 `www` 是子域。
   - 子域可以有多层级，例如 `mail.server.WeThinkIn.com`。

### **3.1 域名解析过程**
当用户在浏览器中输入域名（如 `www.WeThinkIn.com`），系统通过 DNS 将其解析为 IP 地址，具体步骤如下：

1. **本地缓存查询**：
   - 系统先查询本地 DNS 缓存，看是否已经解析过该域名。如果缓存命中，直接返回结果。
   - 否则，进入下一步。

2. **本地 DNS 服务器查询**：
   - 本地 DNS 服务器（通常由 ISP 提供）接收到解析请求。如果有结果，会返回。
   - 如果本地 DNS 服务器未命中，则向更高层的 DNS 服务器发起查询。

3. **递归查询**：
   - 本地 DNS 服务器向根域服务器发起请求，根域服务器返回对应顶级域（如 `.com`）的权威服务器地址。
   - 本地 DNS 服务器继续向顶级域权威服务器发起请求，获取二级域的权威服务器地址。
   - 依次类推，直到返回目标域名的 IP 地址。

4. **返回结果**：
   - 本地 DNS 服务器将最终结果返回给用户设备，并缓存结果以便后续快速查询。

### **3.2 查询方式**
DNS 查询有两种主要方式：
1. **递归查询**：
   - 查询由本地 DNS 服务器完成，用户只需等待最终结果。
   - 本地 DNS 服务器依次查询根服务器、TLD 服务器等，直到获取目标 IP。

2. **迭代查询**：
   - 用户设备接收到中间服务器的地址后，自行向这些服务器发起进一步查询。
   - 这种方式较少使用，大多数情况下由本地 DNS 服务器负责递归查询。

### **4. DNS 的记录类型**
DNS 系统中，每个域名包含多个记录类型，不同类型提供不同的信息：

| **记录类型** | **描述**                                                   |
|--------------|-----------------------------------------------------------|
| **A 记录**   | 将域名映射到 IPv4 地址。                                   |
| **AAAA 记录**| 将域名映射到 IPv6 地址。                                   |
| **CNAME 记录**| 将一个域名映射到另一个域名，常用于别名解析。                |
| **MX 记录**  | 定义邮件服务器地址，用于电子邮件系统。                       |
| **NS 记录**  | 定义域名服务器的地址，指向该域名的权威 DNS 服务器。          |
| **PTR 记录** | 用于反向解析，将 IP 地址映射回域名。                        |
| **TXT 记录** | 存储任意文本信息，常用于身份验证（如 SPF、DKIM）。           |
| **SRV 记录** | 服务定位记录，用于指定特定服务的地址（如 SIP、XMPP）。        |

### **6. 常见 DNS 工具和命令**

1. **`nslookup`**：查询 DNS 记录。
```bash
   nslookup www.WeThinkIn.com
```

2. **`dig`**：详细查询 DNS 信息。
```bash
   dig www.WeThinkIn.com
```

3. **`ping`**：验证域名解析是否正常。
```bash
   ping www.WeThinkIn.com
```

4. **`host`**：快速查询 DNS 记录。
```bash
   host www.WeThinkIn.com
```

### **7. DNS 的应用场景**

1. **互联网访问**：为用户提供人类可读的域名，方便访问网站。
2. **负载均衡**：通过多 A 记录或 CNAME 指向不同的服务器，分散流量。
3. **邮件服务**：通过 MX 记录指定邮件服务器地址。
4. **内容分发网络（CDN）**：结合地理位置优化用户请求的分配。

### **8. DNS 的挑战与解决方案**

1. **DNS 缓存中毒**：
   - 攻击者伪造 DNS 响应，将用户引导到恶意网站。
   - 解决：启用 DNSSEC（DNS Security Extensions），验证响应的真实性。

2. **隐私问题**：
   - DNS 查询通常是明文传输，可能泄露用户访问记录。
   - 解决：使用 DoH（DNS over HTTPS）或 DoT（DNS over TLS）加密查询。

3. **高延迟**：
   - 多次查询可能导致解析延迟。
   - 解决：使用 DNS 缓存和本地 DNS 服务优化性能。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L679)，来源许可：GPL-3.0。

<a id="kbe402ada6048"></a>

## 你知道DNS是什么？

**官方解释**：DNS（Domain Name System，域名系统），因特网上作为**域名和IP地址相互映射**的一个**分布式数据库**，能够使用户更方便的访问互联网，而不用去记住能够被机器直接读取的IP数串。

通过主机名，最终得到该主机名对应的IP地址的过程叫做域名解析（或主机名解析）。

**通俗的讲**，我们更习惯于记住一个网站的名字，比如www.baidu.com,而不是记住它的ip地址，比如：167.23.10.2。

<p  id="第嗯斯的工作原理"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-01-net.md#L100)，来源许可：Apache-2.0。

<a id="k58b5ab188973"></a>

## 如何获取客户端真实 IP？

获取客户端真实 IP 的方法有多种，主要分为应用层方法、传输层方法和网络层方法。

**应用层方法**：

`X-Forwarded-For` 是 HTTP 代理生态中广泛使用但未标准化的请求头；IETF 标准化的对应机制是 HTTP `Forwarded` 头。它们都属于 HTTP，不能直接套用于 SMTP 等其他应用层协议。业务服务也不能无条件信任客户端传入的 `X-Forwarded-For`：可信反向代理应覆盖或规范化外部传入值，服务端只解析由已知代理追加的部分。

**传输层方法**：

利用 TCP Options 字段承载真实源 IP 信息。这种方法适用于任何基于 TCP 的协议，不受应用层的限制。不过，这并非是 TCP 标准所支持的，所以需要通信双方都进行改造。也就是：对于发送方来说，需要有能力把真实源 IP 插入到 TCP Options 里面。对于接收方来说，需要有能力把 TCP Options 里面的 IP 地址读取出来。

也可以通过 Proxy Protocol 协议来传递客户端 IP 和 Port 信息。这种方法可以利用 Nginx 或者其他支持该协议的反向代理服务器来获取真实 IP 或者在业务服务器解析真实 IP。

**网络层方法**：

隧道 + DSR 模式。这种方法可以适用于任何协议，就是实施起来会比较麻烦，也存在一定限制，实际应用中一般不会使用这种方法。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions2.md#L300)，来源许可：Apache-2.0。

<a id="kc790431090a6"></a>

## 谈谈DNS解析过程，具体一点

![](https://raw.githubusercontent.com/forthespada/InterviewGuide/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-01-net.assets/202205220036692.png)

- 请求一旦发起，若是chrome浏览器，先在浏览器找之前**有没有缓存过的域名所对应的ip地址**，有的话，直接跳过dns解析了，若是没有，就会**找硬盘的hosts文件**，看看有没有，有的话，直接找到hosts文件里面的ip
- 如果本地的hosts文件没有能得到对应的ip地址，浏览器会发出一个**dns请求到本地dns服务器**，**本地dns服务器一般都是你的网络接入服务器商提供**，比如中国电信，中国移动等。
- 查询你输入的网址的DNS请求到达本地DNS服务器之后，**本地DNS服务器会首先查询它的缓存记录**，如果缓存中有此条记录，就可以直接返回结果，此过程是**递归的方式进行查询**。如果没有，本地DNS服务器还要向**DNS根服务器**进行查询。
- 本地DNS服务器继续向域服务器发出请求，在这个例子中，请求的对象是.com域服务器。.com域服务器收到请求之后，也不会直接返回域名和IP地址的对应关系，而是告诉本地DNS服务器，你的域名的解析服务器的地址。
- 最后，本地DNS服务器向**域名的解析服务器**发出请求，这时就能收到一个域名和IP地址对应关系，本地DNS服务器不仅要把IP地址返回给用户电脑，还要把这个对应关系保存在缓存中，以备下次别的用户查询时，可以直接返回结果，加快网络访问。

<p  id="负载均衡是什么策略"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-01-net.md#L351)，来源许可：Apache-2.0。
