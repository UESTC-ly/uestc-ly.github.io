# 06-应用层基础：DNS、HTTP、HTTPS、WebSocket

> 应用层协议直接面向应用程序，规定了通信双方如何表示数据、发起请求、返回结果以及维护会话。
>
> 本章围绕 Web 场景中最常见的几类协议展开：DNS 负责“根据域名找到服务地址”，HTTP 负责“以请求—响应方式交换资源”，HTTPS 负责“在 HTTP 之下增加身份认证、机密性和完整性保护”，WebSocket 则负责“在连接建立后进行持续的双向通信”。

---

## 1. 从输入 URL 到页面展示：一条完整请求链路

用户在浏览器地址栏输入：

```text
https://www.example.com:443/api/users?id=10#profile
```

浏览器大致会经历以下过程：

1. **解析 URL**：识别协议、主机名、端口、路径、查询参数和片段标识符。
2. **检查本地缓存**：查询浏览器缓存、操作系统 DNS 缓存以及 hosts 文件。
3. **DNS 解析**：把 `www.example.com` 解析为一个或多个 IP 地址。
4. **建立传输连接**：通常是 TCP 连接；如果使用 HTTP/3，则通过 QUIC 建立连接。
5. **建立 TLS 会话**：HTTPS 场景下验证证书并协商加密参数。
6. **发送 HTTP 请求**：携带请求方法、路径、请求头和可选请求体。
7. **服务端处理请求**：可能经过 CDN、反向代理、网关、负载均衡、应用服务和数据库。
8. **返回 HTTP 响应**：包括状态码、响应头和响应体。
9. **浏览器处理响应**：解析 HTML、CSS、JavaScript 和图片等资源，并可能继续发起更多请求。
10. **复用连接与缓存**：后续请求可能复用已有连接，也可能直接命中浏览器或 CDN 缓存。

可以用下面的链路概括：

```text
URL
  → DNS：域名对应哪个 IP？
  → TCP/QUIC：如何建立传输通道？
  → TLS：如何认证和加密？
  → HTTP：请求什么资源、返回什么结果？
  → 浏览器：如何解析、缓存和渲染？
```

需要区分几个层次：

| 问题 | 主要由什么解决 |
|---|---|
| 域名对应哪个 IP | DNS |
| 如何把字节可靠地送到对端 | TCP，或 QUIC |
| 如何防止窃听和篡改、确认服务端身份 | TLS |
| 请求方法、路径、状态码、缓存语义 | HTTP |
| 页面如何渲染、接口如何调用 | 浏览器和应用层代码 |

---

## 2. URL、URI 与资源定位

### 2.1 URL 的基本结构

URL（Uniform Resource Locator，统一资源定位符）通常可以表示为：

```text
scheme://userinfo@host:port/path?query#fragment
```

例如：

```text
https://user:password@example.com:8443/a/b?key=value&page=2#section
```

各部分含义如下：

| 部分 | 示例 | 作用 |
|---|---|---|
| scheme | `https` | 指示访问资源所使用的协议 |
| userinfo | `user:password` | 用户信息，现代 Web 中通常不建议放密码 |
| host | `example.com` | 域名或 IP 地址 |
| port | `8443` | 端口；省略时使用协议默认端口 |
| path | `/a/b` | 服务器上的资源路径或路由 |
| query | `key=value&page=2` | 查询参数，不同参数用 `&` 分隔 |
| fragment | `section` | 页面内片段，只由客户端处理，通常不会发送给服务器 |

默认端口通常是：

- HTTP：80；
- HTTPS：443；
- WebSocket：80；
- WebSocket over TLS（`wss`）：443。

### 2.2 URI、URL 与 URN

- **URI** 是统一资源标识符的总称，用于标识某个资源。
- **URL** 不仅标识资源，还描述如何定位和访问它。
- **URN** 通过名称标识资源，但不强调访问位置。

日常 Web 开发中经常把 URL、URI 混用，但严格来说 URL 是 URI 的一种。

### 2.3 Path、Query 和 Fragment 的区别

```text
https://example.com/products/10?sort=price#comments
                              │             │
                              │             └─ Fragment：浏览器本地定位
                              └─ Query：通常发送给服务器
```

- Path 常用于表示资源层级或 API 路由。
- Query 常用于筛选、分页、排序和搜索等条件。
- Fragment 通常不会出现在发送给服务器的 HTTP 请求中。浏览器收到响应后，才根据 fragment 定位页面位置；前端路由也可以利用它实现客户端路由。

### 2.4 URL 编码

URL 中有些字符具有特殊含义，例如 `/`、`?`、`#`、`&` 和 `=`。如果参数值本身包含这些字符，就需要进行百分号编码：

```text
空格       → %20 或 +（取决于编码场景）
中文       → 按 UTF-8 编码后进行百分号编码
?          → %3F
#          → %23
```

查询字符串中的 `+` 是否代表空格，取决于是否使用 `application/x-www-form-urlencoded` 规则；不能在所有 URL 场景中简单认为 `+` 就是空格。

---

# 3. DNS：把域名解析为地址

## 3.1 DNS 解决什么问题

DNS（Domain Name System，域名系统）把便于人记忆的域名映射为网络地址及其他服务信息：

```text
www.example.com  →  93.184.216.34
                 →  2606:2800:220:1:248:1893:25c8:1946
```

域名比直接使用 IP 更适合应用，原因包括：

- IP 地址可能发生变化，域名可以保持不变；
- 一个域名可以对应多个 IP，实现容灾、负载分担或就近接入；
- 可以通过 CNAME 把服务交给 CDN 或云厂商；
- MX、SRV 等记录可以描述邮件和特定服务的位置。

DNS 本质上是一个**分布式、层次化、带缓存的命名系统**，不是一个简单的单机字典。

## 3.2 域名层次结构

以 `www.example.com.` 为例：

```text
.                 根域
└── com            顶级域 TLD
    └── example    注册域或权威管理域
        └── www    主机名或子域名
```

末尾的点表示根域，完整形式称为绝对域名（FQDN）。日常书写中通常省略最后的点。

DNS 查询涉及几类服务器：

- **根域名服务器**：告诉查询方某个顶级域由哪些 TLD 服务器负责。
- **TLD 服务器**：例如 `.com` 服务器，告诉查询方某个域名由哪些权威 DNS 服务器负责。
- **权威 DNS 服务器**：保存具体域名区域的真实记录，例如 `example.com` 的 A、AAAA、MX 记录。
- **递归解析器**：通常由运营商、企业、公共 DNS 服务或本地网络提供。它代替客户端向根、TLD 和权威服务器查询，并缓存结果。

客户端一般不会自己逐级询问所有服务器，而是把请求发送给配置好的递归解析器。

## 3.3 一次递归 DNS 查询

假设本地没有 `www.example.com` 的缓存，递归解析器可能执行：

```text
客户端 → 递归解析器：查询 www.example.com
递归解析器 → 根服务器：com 由哪些服务器负责？
根服务器 → 递归解析器：返回 .com TLD 服务器地址
递归解析器 → TLD 服务器：example.com 由哪些权威服务器负责？
TLD 服务器 → 递归解析器：返回权威服务器地址
递归解析器 → 权威服务器：www.example.com 的 A/AAAA 是什么？
权威服务器 → 递归解析器：返回记录和 TTL
递归解析器 → 客户端：返回最终地址
```

这里要区分：

- **递归查询**：客户端要求 DNS 服务器直接给出最终答案。
- **迭代查询**：DNS 服务器只返回“下一步应该询问谁”的线索，查询方继续询问。

## 3.4 常见 DNS 记录

| 记录 | 含义 | 示例 |
|---|---|---|
| A | 域名映射到 IPv4 地址 | `example.com. A 192.0.2.1` |
| AAAA | 域名映射到 IPv6 地址 | `example.com. AAAA 2001:db8::1` |
| CNAME | 一个域名的别名指向另一个域名 | `www.example.com. CNAME web.example.net.` |
| NS | 指定某个区域的权威 DNS 服务器 | `example.com. NS ns1.example.net.` |
| MX | 指定邮件服务器及优先级 | `example.com. MX 10 mail.example.com.` |
| TXT | 保存文本信息，可用于 SPF、DKIM、域名验证等 | `example.com. TXT "..."` |
| PTR | 反向解析，IP 映射到域名 | `1.2.0.192.in-addr.arpa. PTR ...` |
| SOA | 区域起始授权信息，包括主服务器、序列号和计时参数 | 区域管理信息 |
| SRV | 描述特定服务的位置和端口 | `_sip._tcp.example.com.` |

### A 与 AAAA

A 记录面向 IPv4，AAAA 记录面向 IPv6。一个域名可以同时拥有两类记录。客户端可能根据网络环境、地址选择算法和连接结果选择 IPv4 或 IPv6。

### CNAME 的注意点

CNAME 表示“别名”，目标仍然是另一个域名，解析器还需要继续查询目标域名，最终得到 A 或 AAAA 等记录。它不是直接存储 IP 地址的记录。

DNS 规范中，CNAME 通常不能与同一名称下的其他数据记录并存，因此根域名或某些需要同时配置 MX、TXT 的位置不能简单使用传统 CNAME；云 DNS 提供商可能通过 ALIAS、ANAME 或 CNAME flattening 等方式提供类似能力。

### MX 与 Web 请求

MX 记录用于邮件投递，不用于普通 HTTP 访问。访问 `https://example.com` 时通常查询 A/AAAA，而不是 MX。

## 3.5 DNS 缓存与 TTL

DNS 记录带有 TTL（Time To Live），表示缓存服务器在多长时间内可以直接使用该记录而不必重新向上游查询。

缓存可能存在于：

- 浏览器；
- 操作系统；
- 本地路由器或企业 DNS；
- 运营商递归解析器；
- 公共递归 DNS；
- CDN 或其他中间系统。

TTL 越长，查询压力越小、解析延迟越低，但地址变化传播得越慢。修改 DNS 记录后并不能保证所有客户端立即看到新地址，因为不同缓存的剩余 TTL 不同。

DNS 还可能缓存否定答案。例如某个域名不存在时，解析器可以根据 SOA 中的相关参数缓存 NXDOMAIN 一段时间。因此“刚创建域名但仍然解析不到”或“删除记录后仍然返回旧结果”都可能与缓存有关。

## 3.6 DNS 传输方式

传统 DNS 通常使用 UDP 53 端口，因为请求和响应较短、开销小。但以下情况可能使用 TCP 53：

- UDP 响应过大，需要截断后通过 TCP 重试；
- DNS 区域传送；
- 某些 DNS 实现直接使用 TCP。

现代 DNS 还常见：

- **DoT（DNS over TLS）**：DNS 报文通过 TLS 传输，通常使用 TCP 853 端口。
- **DoH（DNS over HTTPS）**：DNS 请求封装在 HTTPS 中，通常使用 TCP/TLS 或 HTTP/2、HTTP/3。

DoT 和 DoH 主要保护客户端到解析服务之间的 DNS 查询内容，不能自动保证整个互联网中的所有 DNS 路径都安全，也不能替代 HTTPS 对业务数据的保护。

## 3.7 DNS 安全与常见问题

传统 DNS 本身缺少端到端的机密性和完整性保护，攻击者可能进行：

- DNS 查询窃听；
- DNS 响应篡改；
- DNS 缓存投毒；
- 域名劫持；
- DDoS 攻击。

DNSSEC 可以为 DNS 数据提供数字签名验证，帮助验证“返回的数据确实来自权威来源且未被篡改”，但 DNSSEC 不等同于加密，也不会隐藏查询内容。

排查 DNS 问题时可以按顺序确认：

1. 本机 hosts 文件是否覆盖了正常解析；
2. 本地是否有 DNS 缓存；
3. 递归解析器是否能访问外部 DNS；
4. 权威服务器是否配置正确；
5. A 和 AAAA 是否存在不一致；
6. 是否因为 TTL 或否定缓存仍未生效；
7. 是否是 DNS 解析正常但后续 TCP、TLS 或 HTTP 阶段失败。

---

# 4. HTTP：Web 世界的请求—响应协议

## 4.1 HTTP 的定位

HTTP（HyperText Transfer Protocol，超文本传输协议）是一种应用层协议，最初主要用于传输超文本，现在已经广泛用于：

- 网页、样式表、脚本和图片等静态资源；
- REST、RPC、GraphQL 等 API；
- 文件上传和下载；
- CDN、反向代理和缓存通信；
- WebSocket 握手以及其他协议升级场景。

HTTP 的核心模型是：

```text
客户端发送 Request  →  服务端处理  →  服务端返回 Response
```

HTTP 规定的是消息格式和语义，不规定服务端必须使用什么编程语言、数据库或业务框架。

## 4.2 HTTP 的基本特点

1. **请求—响应模型**：客户端先发起请求，服务器返回响应。
2. **无状态协议语义**：单个 HTTP 请求默认不依赖之前的请求；需要连续会话时，通常使用 Cookie、Token 或应用层会话。
3. **可扩展**：可以通过请求头、响应头、方法、状态码和媒体类型扩展能力。
4. **资源导向**：通过 URI 标识资源，并使用方法表达对资源的操作意图。
5. **可缓存**：浏览器、代理和 CDN 可以根据缓存语义复用响应。
6. **可协商**：客户端可以通过请求头告诉服务器自己能接受的媒体类型、压缩格式和语言。
7. **与传输层解耦**：HTTP/1.1 常运行在 TCP 上，HTTP/2 运行在 TLS over TCP 上，HTTP/3 运行在 QUIC 上。

“HTTP 无状态”不等于“HTTP 不能有状态”。它表示协议本身不会自动记住请求之间的业务上下文；应用可以借助 Cookie、Session、Token 或数据库建立状态。

## 4.3 HTTP 请求报文

典型的 HTTP/1.1 请求如下：

```http
POST /api/orders?page=1 HTTP/1.1
Host: api.example.com
Content-Type: application/json
Accept: application/json
Authorization: Bearer <token>
Content-Length: 42

{"productId":123,"quantity":2}
```

HTTP/1.x 请求通常由四部分组成：

```text
请求行
请求头字段
空行
请求体（可选）
```

### 请求行

请求行格式：

```text
方法 SP 请求目标 SP HTTP版本 CRLF
```

例如：

```text
GET /index.html HTTP/1.1
```

- 方法表示希望执行的操作；
- 请求目标通常是路径和查询字符串；
- HTTP/1.1 中一般要求 `Host` 请求头标识目标主机。

HTTP/2 和 HTTP/3 不再使用 HTTP/1.x 的文本请求行，而是使用伪首部表示类似信息：

```text
:method: GET
:scheme: https
:authority: www.example.com
:path: /index.html
```

### 请求头

请求头用于传递元数据，例如：

- 客户端可接受的响应类型；
- 请求体格式；
- 身份凭证；
- Cookie；
- 缓存条件；
- 压缩能力；
- 来源和浏览器上下文。

请求头本身不是业务数据。业务数据通常放在请求体中，或经过编码后放在 URL 查询参数中。

### 请求体

请求体可用于传输表单、JSON、文件或其他二进制数据。是否允许请求体、如何解释请求体，取决于方法和 `Content-Type`。

常见请求体格式：

```http
Content-Type: application/json

{"name":"Alice","age":18}
```

```http
Content-Type: application/x-www-form-urlencoded

name=Alice&age=18
```

```http
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary...

------WebKitFormBoundary...
Content-Disposition: form-data; name="file"; filename="a.txt"
Content-Type: text/plain

file content
------WebKitFormBoundary...--
```

## 4.4 HTTP 响应报文

典型响应如下：

```http
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Content-Length: 27
Cache-Control: no-store

{"id":123,"name":"book"}
```

HTTP/1.x 响应由以下部分组成：

```text
状态行
响应头字段
空行
响应体（可选）
```

状态行格式：

```text
HTTP版本 SP 状态码 SP 原因短语 CRLF
```

HTTP/2 和 HTTP/3 仍然保留状态码语义，但不再传输传统文本状态行，状态码通过 `:status` 伪首部表达。

## 4.5 HTTP 消息的边界与长度

接收方必须知道请求体或响应体在哪里结束。HTTP/1.1 中常见的确定方式包括：

### Content-Length

```http
Content-Length: 1024
```

表示消息体有 1024 字节。对于需要精确读取请求体的服务器，正确处理 `Content-Length` 非常重要。

### Transfer-Encoding: chunked

HTTP/1.1 可以使用分块传输，让服务端在不知道完整长度时边生成边发送：

```http
HTTP/1.1 200 OK
Transfer-Encoding: chunked

7
chunked
6
 data!
0


```

每个块先给出十六进制长度，再给出内容；长度为 0 表示结束。分块传输解决的是传输时不知道最终长度的问题，不等于压缩，也不等于流式业务协议。

HTTP/2 和 HTTP/3 使用帧来表达消息，不使用 HTTP/1.1 的 `Transfer-Encoding: chunked`；在这些版本中发送该头字段通常是不允许的。应用仍然可以通过 DATA 帧逐步发送数据。

### 由连接关闭表示结束

HTTP/1.0 或某些 HTTP/1.1 场景下，服务器可能通过关闭连接表示响应体结束。但这样会损失连接复用能力，通常不如明确的 `Content-Length` 或分块传输。

### 没有消息体的情况

以下情况通常不能按普通响应体处理：

- `HEAD` 请求的响应不携带消息体，但响应头应与对应 GET 类似；
- `1xx` 信息响应；
- `204 No Content`；
- `304 Not Modified`；
- 某些 `CONNECT` 成功后的响应会切换到隧道模式。

## 4.6 HTTP 方法与语义

### GET：获取资源

```http
GET /users/123 HTTP/1.1
Host: api.example.com
```

特点：

- 用于获取资源的当前表示；
- 通常不应产生业务副作用；
- 请求体不是常规传参方式，兼容性和语义都不如查询参数；
- 结果可以被缓存，但是否实际缓存还取决于响应头和缓存策略。

### HEAD：只获取响应头

HEAD 与 GET 的目标资源相同，但服务器不应返回消息体。它适合：

- 检查资源是否存在；
- 获取文件大小、类型和修改时间；
- 判断缓存或下载前的元数据。

### POST：提交数据或触发处理

POST 常用于：

- 创建子资源；
- 提交表单；
- 上传文件；
- 触发不能简单映射为资源替换的业务操作。

POST 通常不是幂等的。网络超时后自动重试 POST 可能导致重复创建订单或重复扣款，因此需要根据业务使用幂等键、请求唯一号或服务端去重。

### PUT：整体创建或替换

PUT 通常表示“把请求体作为目标资源的新表示”。同一个 PUT 请求重复执行，目标资源最终状态通常相同，因此其语义是幂等的。

幂等不代表请求只执行一次，也不代表响应完全相同；它表示多次执行后的预期资源状态与执行一次相同。

### PATCH：部分修改

PATCH 用于对资源进行部分更新，例如只修改用户昵称。PATCH 是否幂等取决于具体补丁语义：

- `name = "Alice"` 多次执行通常幂等；
- `balance += 10` 多次执行通常不幂等。

### DELETE：删除资源

DELETE 请求资源删除。第一次删除可能返回 200 或 204，之后再次删除可能返回 404，也可能仍返回成功，这并不改变 DELETE 通常具有幂等语义的事实：资源最终处于“被删除”状态。

### OPTIONS：询问通信能力

OPTIONS 可以询问服务器支持的方法、跨域策略或其他通信能力。浏览器的 CORS 预检请求就常使用 OPTIONS。

### TRACE：诊断请求链路

TRACE 用于回显请求，实际生产服务中通常会关闭，以减少跨站脚本追踪等安全风险。

### CONNECT：建立隧道

CONNECT 通常用于代理场景，要求代理与目标建立字节隧道。HTTPS 通过 HTTP 代理时，客户端经常先发送：

```http
CONNECT example.com:443 HTTP/1.1
Host: example.com:443
```

代理返回成功后，客户端再在这条隧道中进行 TLS 握手。

## 4.7 安全、幂等与缓存性

HTTP 方法常用的语义属性：

| 方法 | Safe（安全） | Idempotent（幂等） | 常见缓存情况 |
|---|---:|---:|---|
| GET | 是 | 是 | 常见 |
| HEAD | 是 | 是 | 常见 |
| OPTIONS | 是 | 是 | 较少 |
| POST | 否 | 通常否 | 技术上可以，实际较少 |
| PUT | 否 | 是 | 较少 |
| DELETE | 否 | 是 | 通常不缓存 |
| PATCH | 否 | 不一定 | 通常不缓存 |
| CONNECT | 否 | 否 | 不适用 |

- **安全（safe）**表示客户端请求意图不应产生资源修改，不表示完全没有日志、计费或统计副作用。
- **幂等（idempotent）**表示重复执行的最终预期效果与执行一次相同。
- **可缓存**表示规范允许缓存，并不表示所有浏览器、代理都会缓存。

这些属性会影响浏览器、代理、重试组件和 API 网关的行为。

---

# 5. HTTP 状态码

## 5.1 状态码分类

| 类别 | 范围 | 含义 |
|---|---:|---|
| 1xx | 100–199 | 信息性响应，请继续处理 |
| 2xx | 200–299 | 请求成功 |
| 3xx | 300–399 | 重定向或缓存相关处理 |
| 4xx | 400–499 | 请求本身存在问题，通常由客户端负责修正 |
| 5xx | 500–599 | 服务端处理失败 |

状态码描述的是 HTTP 层结果，不一定等于业务成功。例如接口可能返回 `200 OK`，但 JSON 中 `code` 表示业务失败；也可能正确使用 `409` 表示业务资源冲突。API 设计应尽量让 HTTP 状态码和业务语义保持一致。

## 5.2 常见 2xx

### 200 OK

请求成功，响应体通常包含资源或处理结果。

### 201 Created

请求成功创建资源。服务端常通过 `Location` 返回新资源地址：

```http
HTTP/1.1 201 Created
Location: /users/123
```

### 202 Accepted

请求已接受，但处理尚未完成，适合异步任务。它不代表最终业务一定成功，客户端可能需要轮询任务状态或等待回调。

### 204 No Content

请求成功，但没有响应体。常用于删除成功或更新成功且不需要返回内容。

## 5.3 常见 3xx

### 301、308：永久重定向

- `301 Moved Permanently`：资源永久移动。历史上客户端可能改变 POST 为 GET，因此对于需要严格保持方法和请求体的重定向，常考虑 308。
- `308 Permanent Redirect`：永久重定向，并要求保持请求方法和请求体。

### 302、307：临时重定向

- `302 Found`：历史兼容行为复杂，部分客户端可能把 POST 改成 GET。
- `307 Temporary Redirect`：临时重定向，保持原请求方法和请求体。

### 304 Not Modified

条件请求命中缓存时返回。它表示资源未变化，客户端继续使用本地缓存内容，响应通常不携带消息体。

## 5.4 常见 4xx

### 400 Bad Request

请求语法错误、参数格式不正确或无法解析。

### 401 Unauthorized

请求缺少有效身份认证凭证，或凭证无效、已过期。它通常应配合 `WWW-Authenticate` 告诉客户端需要哪种认证方式。

名称中虽然有 Unauthorized，但实际更接近“未通过认证”，不是“没有权限”。

### 403 Forbidden

服务器理解请求，但拒绝执行。常见原因是已认证用户没有权限、来源被禁止或策略不允许访问。

### 404 Not Found

服务器找不到目标资源。出于安全考虑，某些服务会对“资源不存在”和“用户无权看到资源”都返回 404，以避免泄露资源是否存在。

### 405 Method Not Allowed

资源存在，但不支持当前方法，通常通过 `Allow` 响应头列出允许的方法。

### 406 Not Acceptable

服务端无法根据客户端的内容协商要求返回可接受的表示。

### 408 Request Timeout

服务端等待客户端请求超时。

### 409 Conflict

请求与资源当前状态冲突，例如版本冲突、重复创建或状态机不允许当前操作。

### 413 Content Too Large

请求体超过服务器允许的大小。旧规范和部分实现中可能称为 `413 Payload Too Large`。

### 415 Unsupported Media Type

请求体的媒体类型不受支持，例如接口只接受 JSON，却发送了不支持的格式。

### 422 Unprocessable Content

请求语法正确，但语义校验失败，例如字段格式正确但不满足业务规则。

### 429 Too Many Requests

请求频率超过限制，通常可以通过 `Retry-After` 告诉客户端何时再试。

## 5.5 常见 5xx

### 500 Internal Server Error

服务端遇到未能明确处理的内部错误。

### 502 Bad Gateway

网关或代理从上游服务收到无效响应，或无法正确处理上游响应。

### 503 Service Unavailable

服务暂时无法处理请求，可能是过载、维护或依赖不可用。可以配合 `Retry-After` 表示重试时间。

### 504 Gateway Timeout

网关等待上游服务响应超时。

排查 502、503、504 时要区分：

- 客户端到网关是否成功；
- 网关到上游是否成功；
- 上游是否收到请求；
- 上游是否处理超时；
- 是否是连接池、DNS、TLS、限流或负载均衡问题。

---

# 6. HTTP 请求头与响应头

## 6.1 Host 与虚拟主机

同一个 IP 地址上可以部署多个域名。HTTP/1.1 通过 `Host` 区分访问的主机：

```http
Host: api.example.com
```

HTTPS 建立 TLS 连接时，还常通过 SNI 告诉服务器客户端希望访问的域名。SNI 主要用于选择证书和虚拟站点，HTTP 请求中的 `Host` 则用于 HTTP 层路由；二者通常应保持一致。

HTTP/2 和 HTTP/3 使用 `:authority` 表示类似 Host 的信息。

## 6.2 Content-Type、Accept 与 Content-Encoding

这三个字段经常被混淆：

### Content-Type：当前消息体是什么格式

```http
Content-Type: application/json; charset=utf-8
```

它可以描述请求体，也可以描述响应体。

### Accept：客户端能接受什么响应格式

```http
Accept: application/json, text/plain;q=0.9, */*;q=0.8
```

这是内容协商的一部分，不是对请求体格式的声明。

### Content-Encoding：消息体经过什么编码

```http
Content-Encoding: gzip
```

它描述压缩或其他内容编码。客户端通常通过：

```http
Accept-Encoding: gzip, br
```

告诉服务端自己支持哪些编码。解压之后的数据格式仍由 `Content-Type` 描述。

可以这样记：

```text
Content-Type    → 内容本身是什么
Content-Encoding→ 内容被怎样压缩/编码
Accept          → 我希望收到什么内容格式
Accept-Encoding → 我能解压什么编码
```

## 6.3 Content-Disposition

常用于文件下载或 multipart 表单：

```http
Content-Disposition: attachment; filename="report.pdf"
```

- `inline`：倾向于让浏览器直接展示；
- `attachment`：提示下载；
- `filename`：建议保存的文件名。

服务端不能盲目信任用户提供的文件名，应防止路径穿越、响应头注入和危险扩展名问题。

## 6.4 Authorization 与 WWW-Authenticate

常见认证形式：

```http
Authorization: Basic <base64-credentials>
Authorization: Bearer <access-token>
```

Basic 只是编码，不是加密，必须在 HTTPS 中使用。Bearer Token 的含义是“持有令牌者可以使用它”，因此令牌泄露会造成冒用风险。

`401` 通常配合：

```http
WWW-Authenticate: Bearer realm="api"
```

`403` 则通常表示身份可能已识别，但访问被授权策略拒绝。

## 6.5 User-Agent、Referer 和 Origin

- `User-Agent`：描述客户端软件，内容可被伪造，不能作为可靠身份认证。
- `Referer`：表示请求通常从哪个页面跳转或发起，拼写沿用了历史标准；可能受 `Referrer-Policy` 限制。
- `Origin`：表示请求的来源，包含 scheme、host 和 port，浏览器会在跨域请求、POST 或 WebSocket 握手等场景中发送。服务端可以用它执行来源校验。

`Origin` 与 `Referer` 都不能单独替代 CSRF 防护、身份认证和权限校验。

---

# 7. HTTP 缓存

## 7.1 为什么需要缓存

缓存可以减少：

- 重复的网络传输；
- 服务端计算压力；
- 数据库查询压力；
- 用户等待时间；
- CDN 与源站之间的带宽消耗。

缓存可能位于浏览器、代理、CDN、网关或应用内部。缓存的核心问题是：

```text
这个响应能否复用？可以复用多久？过期后如何确认它是否变化？
```

## 7.2 Cache-Control

### max-age

```http
Cache-Control: max-age=3600
```

表示响应在 3600 秒内通常可以视为新鲜，不必访问源站重新验证。

### no-cache

`no-cache` 不是“不允许缓存”，而是“可以存储，但使用前必须向服务器重新验证”。

### no-store

表示不要存储响应，常用于敏感数据，但它不能替代应用层的访问控制和传输加密。

### public 与 private

- `public`：允许共享缓存保存；
- `private`：只允许浏览器等私有缓存保存，不应由共享缓存保存个性化响应。

### must-revalidate

响应过期后必须重新验证，不能在无法联系源站时随意使用旧内容。

### s-maxage

主要控制共享缓存（例如 CDN）的新鲜时间，可覆盖共享缓存对 `max-age` 的使用。

### 其他常见指令

- `immutable`：提示资源在新鲜期内不会变化，减少不必要的重新验证；
- `stale-while-revalidate`：允许短时间返回旧响应，同时后台重新验证；
- `stale-if-error`：源站出错时允许使用旧响应一段时间。

## 7.3 强缓存与协商缓存

### 强缓存

浏览器认为响应还在新鲜期内，直接使用本地副本，不向服务器发请求。常见依据：

```http
Cache-Control: max-age=3600
Expires: Wed, 21 Oct 2015 07:28:00 GMT
```

`Expires` 是较早的绝对时间字段，现代系统通常优先使用 `Cache-Control`。

### 协商缓存

缓存过期或要求验证时，客户端携带缓存验证器请求服务器：

```http
If-None-Match: "abc123"
```

如果资源没变，服务器返回：

```http
HTTP/1.1 304 Not Modified
ETag: "abc123"
```

浏览器继续使用本地内容，不必重新下载响应体。

常见验证器：

- `ETag` / `If-None-Match`：基于实体标签，更精确，推荐优先使用；
- `Last-Modified` / `If-Modified-Since`：基于修改时间，精度和可靠性相对有限。

### ETag 的强弱

```http
ETag: "abc"
ETag: W/"abc"
```

弱 ETag 只表示语义上等价，不一定逐字节完全相同。强 ETag 更适合需要精确字节一致性的场景，例如范围请求或并发控制。

## 7.4 缓存与用户个性化数据

带有 Cookie、Authorization 或用户身份的响应不能简单地放入共享缓存。否则可能发生：

```text
用户 A 的响应被 CDN 缓存
→ 用户 B 请求相同 URL
→ 用户 B 得到用户 A 的内容
```

针对个性化响应，常见做法包括：

- 使用 `Cache-Control: private` 或 `no-store`；
- 让缓存键包含必要的区分因素；
- 正确设置 `Vary`；
- 不把敏感信息放到可共享 URL 中。

`Vary` 表示响应内容会随指定请求头变化：

```http
Vary: Accept-Encoding, Accept-Language
```

缓存必须在缓存键中考虑这些字段，否则可能把一种协商结果错误地提供给另一类客户端。

## 7.5 条件更新与并发控制

缓存验证器还可以防止“后写覆盖先写”。例如客户端读取资源得到：

```http
ETag: "version-7"
```

客户端更新时发送：

```http
If-Match: "version-7"
```

如果服务器上的版本已经变成 `version-8`，就返回 `412 Precondition Failed`，要求客户端先重新读取，避免覆盖其他用户的更新。

这是一种基于 HTTP 条件请求的乐观并发控制。

## 7.6 Range 断点续传

客户端可以请求资源的一部分：

```http
Range: bytes=1000-1999
```

服务器支持时返回：

```http
HTTP/1.1 206 Partial Content
Accept-Ranges: bytes
Content-Range: bytes 1000-1999/10000
Content-Length: 1000
```

- `206 Partial Content`：部分内容成功返回；
- `416 Range Not Satisfiable`：范围无效；
- `Accept-Ranges: bytes`：表示服务器支持按字节范围请求。

大文件下载、视频拖动和断点续传常用此能力。若资源在下载期间发生变化，应结合 ETag 或 Last-Modified 进行一致性验证。

---

# 8. Cookie、Session 与 Token

## 8.1 HTTP 无状态与会话

HTTP 的单个请求默认相互独立：服务器不会仅凭 TCP 连接自动知道当前请求属于哪个用户。为了建立会话，服务端需要给客户端分配某种凭证。

常见方案：

```text
Cookie + Session ID：浏览器自动携带短标识，状态保存在服务端
Cookie + 签名信息：客户端携带数据，但服务端验证签名
Authorization Bearer Token：客户端显式携带访问令牌
```

## 8.2 Cookie 的工作过程

服务端响应：

```http
Set-Cookie: session_id=abc123; Path=/; Secure; HttpOnly; SameSite=Lax
```

后续请求：

```http
Cookie: session_id=abc123
```

Cookie 一般由浏览器根据域名、路径、安全属性和过期时间自动决定是否发送。

## 8.3 Cookie 属性

| 属性 | 作用 |
|---|---|
| Expires | 指定绝对过期时间 |
| Max-Age | 指定从当前时间起的存活秒数 |
| Domain | 指定可发送到哪些域名；省略时通常是 host-only Cookie |
| Path | 限制可发送的路径范围 |
| Secure | 只通过 HTTPS 发送 |
| HttpOnly | 禁止 JavaScript 通过 `document.cookie` 读取 |
| SameSite | 限制跨站请求是否携带 Cookie |
| Partitioned | 在支持的浏览器中将跨站 Cookie 按顶级站点分区 |

### Secure 不等于加密 Cookie

`Secure` 只要求浏览器通过 HTTPS 发送 Cookie，不能防止服务器端日志泄露、XSS 读取非 HttpOnly 数据或应用自身错误。

### HttpOnly 的边界

`HttpOnly` 能降低 Cookie 被 XSS 直接读取的风险，但不能阻止 XSS 代码以受害者身份发起请求，因为浏览器仍可能自动携带 HttpOnly Cookie。因此仍需要输出编码、CSP、CSRF 防护等措施。

### SameSite

- `Strict`：跨站场景限制最严格；
- `Lax`：对部分顶级导航较宽松，现代浏览器常见默认策略；
- `None`：允许跨站发送，但通常必须同时设置 `Secure`。

“跨站（site）”与“跨源（origin）”不是同一概念。源由 scheme、host、port 共同决定；站点判断还涉及注册域等规则。CORS 讨论的是跨源读取，SameSite 主要影响跨站 Cookie 发送。

## 8.4 Session 与 Token 的取舍

### 服务端 Session

优点：

- 服务端可以主动失效会话；
- 客户端只保存随机标识，不保存完整权限数据；
- 便于集中控制。

代价：

- 多实例部署需要共享 Session 存储或会话粘滞；
- 需要处理过期、续期和并发登录。

### Token

优点：

- 服务端可以较少依赖集中式 Session 存储；
- 适合 API、移动端和服务间调用。

代价：

- 一旦签发，撤销和主动失效更复杂；
- Token 过大可能增加请求开销；
- 签名只能保证未被篡改，不代表内容加密；
- 必须严格校验签名算法、签发方、受众、过期时间和权限范围。

无论使用哪种方案，身份认证不等于权限校验：

```text
Authentication：你是谁？
Authorization：你能做什么？
```

---

# 9. CORS、同源策略与跨域

## 9.1 同源策略

浏览器同源策略把以下三项都相同的页面视为同源：

```text
scheme + host + port
```

例如：

```text
https://a.example.com:443
https://a.example.com:8443   → 端口不同，跨源
http://a.example.com:443     → scheme 不同，跨源
https://b.example.com:443    → host 不同，跨源
```

同源策略主要限制一个源的脚本读取另一个源的响应，目的是降低恶意网站窃取用户数据的风险。它不是简单地禁止所有跨域网络请求，浏览器允许某些请求发出，但会限制脚本读取响应。

## 9.2 CORS 的基本过程

CORS（Cross-Origin Resource Sharing，跨源资源共享）通过 HTTP 头让服务器声明允许哪些跨源访问。

简单请求可能直接发送，并根据响应中的 `Access-Control-Allow-Origin` 决定脚本是否可以读取结果：

```http
Origin: https://frontend.example.com
```

服务器：

```http
Access-Control-Allow-Origin: https://frontend.example.com
```

## 9.3 预检请求

如果请求使用了非简单方法、非简单请求头或某些非简单媒体类型，浏览器通常先发送 OPTIONS 预检：

```http
OPTIONS /api/users HTTP/1.1
Origin: https://frontend.example.com
Access-Control-Request-Method: DELETE
Access-Control-Request-Headers: Authorization, Content-Type
```

服务器可以返回：

```http
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://frontend.example.com
Access-Control-Allow-Methods: GET, POST, DELETE
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Max-Age: 600
```

预检通过后，浏览器才发送真正的请求。

## 9.4 携带凭证

跨源请求如果需要携带 Cookie，前端需要显式允许凭证，服务端需要返回：

```http
Access-Control-Allow-Credentials: true
```

此时 `Access-Control-Allow-Origin` 不能使用 `*`，必须明确指定允许的源。服务端还需要正确配置 Cookie 的 `SameSite`、`Secure` 等属性。

CORS 是浏览器的读取控制机制，不能替代服务端身份认证和权限校验。非浏览器客户端通常不会自动遵守 CORS。

## 9.5 CORS 与 CSRF

- **CORS**：控制跨源脚本能否读取响应。
- **CSRF**：攻击者诱导浏览器携带已有 Cookie 发起有害请求。

即使服务端配置了 CORS，也不代表自动解决 CSRF。使用 Cookie 认证的修改操作仍应考虑 SameSite、CSRF Token、Origin/Referer 校验和合理的请求方法设计。

---

# 10. HTTP 连接管理与版本演进

## 10.1 HTTP/1.0

早期 HTTP/1.0 通常一个请求对应一个 TCP 连接。每获取一个资源都重新建立连接，会产生较多 TCP 和 TLS 握手开销。

## 10.2 HTTP/1.1 持久连接

HTTP/1.1 默认支持持久连接：

```http
Connection: keep-alive
```

多个请求可以复用同一条 TCP 连接。连接关闭可以通过：

```http
Connection: close
```

HTTP/1.1 仍然存在以下问题：

- 同一连接上的请求通常按顺序处理；
- 队头请求迟迟不完成时，后面的响应可能被阻塞，这称为应用层队头阻塞（HOL blocking）；
- 浏览器通常通过建立多个并行 TCP 连接缓解问题，但连接数量增加会带来握手和资源开销。

HTTP/1.1 的请求管线化（pipelining）理论上可以连续发送多个请求，但由于中间设备和服务端兼容性问题，实际使用很少。

## 10.3 HTTP/1.1 分块与流式响应

服务端不必等到全部内容生成后才响应，可以：

- 使用 `Transfer-Encoding: chunked` 分块发送；
- 使用长连接持续发送事件或数据；
- 通过 `Content-Length` 已知长度的文件直接发送。

“分块传输”是 HTTP/1.1 的消息分帧方式；“流式响应”是应用逐步产生和消费数据的行为，二者相关但不是同义词。

## 10.4 HTTP/2

HTTP/2 保留 HTTP 的方法、状态码、URI 和大部分语义，但改变了传输表示：

1. 使用二进制帧，不再使用纯文本报文行；
2. 一个 TCP 连接上可以复用多个并发 Stream；
3. 每个请求和响应属于一个 Stream；
4. 使用 HPACK 压缩头部；
5. 支持连接级和流级流量控制；
6. 可以交错发送不同 Stream 的帧；
7. 支持服务器推送，但浏览器和生态中的实际支持与使用情况有限。

### HTTP/2 多路复用

HTTP/2 的多个请求可以在一条连接上交错传输：

```text
TCP 连接
├── Stream 1：HTML
├── Stream 3：CSS
├── Stream 5：JavaScript
└── Stream 7：图片
```

这样通常不需要 HTTP/1.1 那样建立很多并行连接。

但 HTTP/2 运行在 TCP 之上。如果 TCP 层丢失一个报文，TCP 需要按序恢复字节流，可能让多个 HTTP/2 Stream 暂时一起等待。因此 HTTP/2 消除了 HTTP 请求队列层面的部分队头阻塞，但没有消除 TCP 层的队头阻塞。

### HPACK 与请求头压缩

HTTP/2 不只是简单地对每个请求头做 gzip，而是通过静态表、动态表和索引减少重复字段传输。连接中的两端维护动态表，因此动态表状态必须保持同步。

## 10.5 HTTP/3

HTTP/3 使用 QUIC 作为传输基础，QUIC 通常运行在 UDP 之上，但提供可靠、有序的流、加密、连接迁移和拥塞控制等能力。

HTTP/3 的特点：

- 使用 QUIC Stream；
- 使用 QPACK 压缩头部；
- 不再依赖 TCP；
- 不同 Stream 的丢包恢复相互独立，减少 TCP 层队头阻塞；
- TLS 1.3 与 QUIC 紧密结合；
- 网络切换时可以使用连接 ID 支持连接迁移。

HTTP/3 并不是“UDP 不可靠所以 HTTP 不可靠”。QUIC 在 UDP 之上实现了可靠传输、拥塞控制和加密等能力。

## 10.6 HTTP 版本对比

| 对比项 | HTTP/1.1 | HTTP/2 | HTTP/3 |
|---|---|---|---|
| 典型传输 | TCP | TCP + TLS | QUIC over UDP |
| 报文表示 | 文本 | 二进制帧 | 二进制帧 |
| 多路复用 | 有限，常靠多连接 | 一个 TCP 连接多个 Stream | 一个 QUIC 连接多个 Stream |
| 头部压缩 | 无统一动态压缩 | HPACK | QPACK |
| TCP 队头阻塞 | 有 | 仍有 | 不依赖 TCP，显著缓解 |
| TLS | 可选，HTTPS 时使用 | 实际部署通常使用 TLS | 与 QUIC/TLS 1.3 紧密结合 |
| 连接迁移 | 一般不支持 | 一般不支持 | QUIC 原生支持 |

使用 HTTP/2 或 HTTP/3 后，HTTP 方法和状态码等应用语义并没有被替换；变化主要在于连接、帧、流和头部压缩的传输方式。

---

# 11. HTTPS 与 TLS

## 11.1 HTTPS 是什么

HTTPS 可以理解为：

```text
HTTP over TLS
```

TLS 为 HTTP 提供：

1. **机密性**：中间人难以读取明文内容；
2. **完整性**：检测传输内容是否被篡改；
3. **服务端身份认证**：通过证书和信任链验证服务端域名身份。

HTTPS 不能保证：

- 服务端业务逻辑一定正确；
- 网站一定没有恶意代码；
- 用户输入一定安全；
- 服务器不会记录数据；
- IP 地址、连接时间和流量大小完全隐藏；
- 所有 DNS 查询都已加密。

## 11.2 TLS 证书

服务端证书通常包含：

- 公钥；
- 证书主体和域名；
- 有效期；
- 签发者；
- 签名算法和签名；
- Subject Alternative Name（SAN）等扩展。

浏览器验证证书时通常会检查：

1. 当前时间是否在有效期内；
2. 访问域名是否匹配 SAN；
3. 证书是否由受信任的 CA 链签发；
4. 证书链签名是否有效；
5. 证书是否被吊销或受到其他策略限制；
6. 协商的 TLS 版本和密码套件是否满足安全策略。

证书中的公钥不是用来直接加密所有 HTTP 数据的主要工具。现代 TLS 通常使用非对称密码完成身份认证和密钥协商，再使用对称密码高效加密应用数据。

## 11.3 TLS 1.3 握手的抽象过程

可以简化为：

```text
客户端                                      服务端
  | -------- ClientHello ---------------> |
  |   支持版本、密码套件、SNI、ALPN、密钥材料 |
  | <------- ServerHello ---------------- |
  |   选择参数、返回证书、证明私钥、密钥材料   |
  | <------ 加密握手消息 ---------------- |
  | -------- 加密 Finished ------------> |
  | <------- 加密 Finished -------------- |
  | ======== 开始传输 HTTP 数据 ========= |
```

TLS 1.3 通过临时密钥交换建立会话密钥，通常可提供前向保密：即使将来服务端长期私钥泄露，也不能轻易解密过去已经捕获的会话流量。

### ALPN

ALPN（Application-Layer Protocol Negotiation）用于在 TLS 握手期间协商应用层协议，例如：

```text
h2    → HTTP/2
http/1.1 → HTTP/1.1
h3    → 通常通过 QUIC 参数协商
```

### SNI

SNI（Server Name Indication）允许客户端在 TLS 握手时提供目标域名，使同一 IP 的服务器选择正确证书和虚拟主机配置。传统 SNI 的域名可能暴露给路径上的观察者；ECH 是用于进一步保护这类信息的演进机制，但实际支持取决于客户端、服务器和网络环境。

## 11.4 TLS 会话复用与 0-RTT

TLS 会话恢复可以减少再次连接时的握手成本。TLS 1.3 还支持 0-RTT 数据，但早期数据可能被重放，因此不应把具有不可重复副作用的操作（例如扣款、创建订单）直接放在没有额外幂等保护的 0-RTT 请求中。

## 11.5 HSTS

HSTS（HTTP Strict Transport Security）通过响应头告诉浏览器：

```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

作用包括：

- 后续自动把 HTTP 导航升级为 HTTPS；
- 不允许用户轻易忽略证书错误；
- 降低 SSL stripping 等降级攻击风险。

只有在确认整个域名及其子域都能稳定支持 HTTPS 时，才应谨慎使用 `includeSubDomains`。HSTS 需要先通过一次安全的 HTTPS 响应被浏览器记住，首次访问仍存在“第一次连接”问题；预加载机制可以在浏览器内置列表中提前记录域名，但也需要满足严格条件。

## 11.6 HTTPS 请求失败的分层排查

```text
DNS 失败       → 域名解析不到地址
TCP/QUIC 失败  → 端口不可达、网络策略或服务未监听
TLS 失败       → 证书、SNI、版本、密码套件、时间问题
HTTP 失败      → 状态码、路由、认证、权限或业务逻辑问题
应用失败       → JSON、字段校验或前端处理问题
```

看到“HTTPS 访问失败”时，不要直接归因于 HTTP。应先确定失败发生在哪一层。

---

# 12. WebSocket：建立长连接后的双向通信

## 12.1 WebSocket 解决什么问题

传统 HTTP 主要是客户端请求、服务端响应。如果服务端需要主动通知客户端，常见做法是：

- 客户端轮询；
- 长轮询；
- Server-Sent Events（SSE）；
- WebSocket。

WebSocket 允许客户端和服务器建立一条持久连接，之后双方都可以主动发送消息，适合：

- 在线聊天；
- 实时协作；
- 行情和竞价推送；
- 在线游戏；
- 实时监控；
- 需要低延迟双向消息的控制面。

WebSocket 通常使用 TCP，因此连接内的数据可靠、有序，但它本身不替应用定义业务消息、重连、离线消息和最终一致性。

## 12.2 WebSocket URI

```text
ws://example.com/chat
wss://example.com/chat
```

- `ws` 通常对应明文 TCP；
- `wss` 表示 WebSocket over TLS，通常使用 443 端口。

生产环境通常使用 `wss`，避免消息被窃听和篡改。

## 12.3 HTTP/1.1 Upgrade 握手

客户端发起类似请求：

```http
GET /chat HTTP/1.1
Host: example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
Origin: https://www.example.com
```

服务端接受后返回：

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

`Sec-WebSocket-Accept` 的计算思路是：

```text
Base64(SHA-1(Sec-WebSocket-Key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"))
```

这个值主要用于确认服务端确实理解 WebSocket 握手，不是身份认证，也不能替代 TLS。

返回 `101 Switching Protocols` 后，通信不再按照普通 HTTP 请求—响应方式解析，而是进入 WebSocket 帧通信阶段。

## 12.4 WebSocket 帧

WebSocket 的消息会被编码为帧。重要概念包括：

- 文本帧：通常要求内容是有效 UTF-8；
- 二进制帧：传输任意二进制数据；
- Ping/Pong：心跳和存活探测；
- Close：关闭握手；
- FIN：标记消息是否结束；
- Fragmentation：一个较大消息可以拆成多个帧。

客户端发送到服务端的帧必须使用掩码（masking），服务端发送给客户端的帧通常不要求掩码。掩码主要用于避免某些代理将客户端数据误识别为缓存或控制内容，并不是加密机制。

WebSocket 帧格式中包含长度、掩码和操作码等字段。控制帧通常不能无限大，Ping、Pong 和 Close 需要及时处理，不能因为业务消息处理繁忙而完全忽略心跳和关闭事件。

## 12.5 WebSocket 连接生命周期

```text
CONNECTING → OPEN → CLOSING → CLOSED
```

实际应用还需要处理：

1. 握手失败；
2. 认证失败或权限变更；
3. 连接空闲超时；
4. 网络切换导致断连；
5. 代理或负载均衡关闭连接；
6. 服务端重启；
7. 消息发送速度超过接收方处理速度；
8. 客户端重连时的重复订阅和重复消息。

常见工程措施：

- 定期 Ping/Pong 或应用层心跳；
- 指数退避重连，并增加随机抖动；
- 重连后重新认证和订阅；
- 为消息设计序列号、确认号或幂等 ID；
- 设置发送队列上限和背压策略；
- 对 Close Code 和异常断开做分类处理；
- 服务端校验 `Origin`、身份凭证和权限；
- 对消息大小、连接数和发送频率做限制。

## 12.6 WebSocket 与 HTTP 的关系

WebSocket 借助 HTTP/1.1 Upgrade 完成初始握手，但升级成功后不再是普通 HTTP 请求。不能认为“WebSocket 就是不断发送 HTTP 请求”。

另外，HTTP/2 和 HTTP/3 中可以使用扩展机制（例如 extended CONNECT）承载 WebSocket，但具体支持取决于客户端、服务器、代理和框架。

## 12.7 WebSocket、SSE、长轮询对比

| 对比项 | 轮询 | 长轮询 | SSE | WebSocket |
|---|---|---|---|---|
| 通信方向 | 客户端发起 | 主要由服务端延迟响应 | 服务端到客户端 | 双向 |
| 连接形式 | 短请求较多 | 请求保持较久 | 长 HTTP 响应 | 持久连接 |
| 数据格式 | 自定义 HTTP 响应 | 自定义 HTTP 响应 | `text/event-stream` | WebSocket 帧 |
| 浏览器重连 | 应用自行实现 | 应用自行实现 | EventSource 常有基础支持 | 应用自行实现 |
| 适合场景 | 更新不频繁 | 兼容性优先的实时通知 | 单向事件推送 | 双向实时交互 |
| 复杂度 | 低 | 中 | 较低 | 较高 |

如果只需要服务端向浏览器推送事件，SSE 往往比 WebSocket 简单；如果客户端和服务端都需要频繁发送消息，WebSocket 更合适。

---

# 13. HTTP 常见安全问题

## 13.1 明文 HTTP 与中间人攻击

明文 HTTP 中，网络路径上的攻击者可能读取、修改或伪造内容。HTTPS 通过 TLS 降低这些风险，但应用仍必须正确验证证书并避免混合内容。

### 混合内容

HTTPS 页面加载 HTTP 脚本、请求或其他主动内容，可能破坏安全边界。浏览器通常会阻止部分混合内容，生产站点应让页面及其依赖全部通过 HTTPS 获取。

## 13.2 XSS

XSS 是攻击者让恶意脚本在受信任页面上下文中执行。防护重点包括：

- 按输出上下文进行 HTML、属性、URL 和 JavaScript 编码；
- 避免把不可信字符串直接拼接进 HTML 或脚本；
- 使用 CSP 限制脚本来源和执行方式；
- 合理设置 Cookie 的 HttpOnly；
- 对富文本使用经过验证的白名单清洗器。

HttpOnly 不能阻止 XSS 发起带 Cookie 的请求，因此不能单独作为 XSS 或 CSRF 的完整防护。

## 13.3 CSRF

CSRF 利用浏览器自动携带 Cookie 的特点，诱导用户向目标站点发起状态修改请求。常见防护：

- CSRF Token；
- SameSite Cookie；
- 校验 `Origin` 或 `Referer`；
- 修改操作不使用 GET；
- 对重要操作要求再次验证或幂等确认。

## 13.4 请求走私（HTTP Request Smuggling）

当前端代理和后端服务器对请求边界的解释不一致时，攻击者可能构造含糊的 `Content-Length` 与 `Transfer-Encoding` 组合，使不同设备解析出不同请求。防护包括：

- 统一并严格遵守消息长度解析规则；
- 拒绝歧义或非法请求；
- 及时更新代理、网关和 Web 服务器；
- 避免在多个设备之间采用不一致的 HTTP 解析策略。

## 13.5 Host Header 攻击

如果服务端信任用户可控的 `Host` 头生成密码重置链接、绝对 URL 或缓存键，攻击者可能诱导生成恶意域名链接或污染缓存。应使用可信的外部主机配置，并对允许的 Host 做白名单校验。

## 13.6 常见安全响应头

```http
Content-Security-Policy: default-src 'self'; object-src 'none'
Strict-Transport-Security: max-age=31536000
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=()
```

- `Content-Security-Policy`：限制脚本、图片、样式等资源来源；
- `Strict-Transport-Security`：强制后续使用 HTTPS；
- `X-Content-Type-Options: nosniff`：减少 MIME 类型嗅探；
- `Referrer-Policy`：控制 Referer 信息泄露；
- `Permissions-Policy`：控制浏览器能力的使用范围。

安全头需要结合站点实际资源、浏览器兼容性和部署方式配置，不能机械复制。

---

# 14. API 设计中的 HTTP 实践

## 14.1 资源、URI 与方法

一种常见 REST 风格是使用名词表示资源，用 HTTP 方法表示操作：

```text
GET    /users/123       获取用户
POST   /users            创建用户
PUT    /users/123       整体替换用户
PATCH  /users/123       部分修改用户
DELETE /users/123       删除用户
```

查询、过滤和分页可以使用 Query：

```text
GET /users?status=active&page=2&pageSize=20&sort=-createdAt
```

URI 不是安全边界。不要因为使用了“隐藏路径”就认为接口安全；认证、授权和输入校验必须在服务端执行。

## 14.2 JSON 接口

建议明确声明媒体类型：

```http
Content-Type: application/json
Accept: application/json
```

服务端应：

- 校验 JSON 是否可解析；
- 校验字段类型、长度、范围和枚举值；
- 忽略或拒绝未允许字段，避免批量赋值漏洞；
- 返回稳定、可文档化的错误结构；
- 不在错误响应中暴露堆栈、SQL 和密钥等内部信息。

## 14.3 错误响应

可以使用统一结构：

```json
{
  "type": "https://api.example.com/errors/invalid-parameter",
  "title": "Invalid parameter",
  "status": 422,
  "detail": "pageSize must be between 1 and 100",
  "instance": "/requests/req_abc123",
  "requestId": "req_abc123"
}
```

错误响应应便于客户端处理和日志关联，同时避免把内部敏感信息直接返回给用户。

## 14.4 重试、超时与幂等

网络超时不一定代表服务端没有执行请求。可能的情况是：

```text
客户端已发送请求
→ 服务端已完成处理
→ 响应在返回途中丢失
→ 客户端看到超时
```

因此：

- GET、HEAD 等幂等请求通常更适合自动重试；
- POST 等非幂等请求不能无脑重试；
- 创建订单、支付、扣库存等操作应使用幂等键；
- 设置连接超时、读取超时、整体截止时间；
- 使用指数退避和抖动，避免重试风暴；
- 对 429、503 等响应结合 `Retry-After` 和服务端策略处理。

幂等键示例：

```http
POST /payments HTTP/1.1
Idempotency-Key: payment-request-20250308-001
```

服务端需要持久化幂等键与处理结果的关联，不能只依赖客户端“保证不重复”。

## 14.5 分页

常见分页方式：

### Offset 分页

```text
GET /items?page=3&pageSize=20
```

简单直观，但数据频繁插入或删除时可能出现重复、遗漏，深分页性能也可能较差。

### Cursor 分页

```text
GET /items?limit=20&after=eyJpZCI6MTAwLCJjcmVhdGVkQXQiOiIuLi4ifQ
```

服务端根据游标继续查询，通常更适合大数据量和持续变化的数据集。游标应避免暴露不必要的内部信息，并考虑过期和排序稳定性。

## 14.6 版本管理

API 版本可以通过：

- URL：`/v1/users`；
- 媒体类型：`Accept: application/vnd.example.user.v2+json`；
- 查询参数或其他协商方式。

无论采用哪种方式，都应明确兼容性策略，避免突然删除客户端依赖的字段或改变字段类型。

---

# 15. HTTP 调试与排查方法

## 15.1 先确认请求是否真的发出

浏览器开发者工具 Network 面板中重点观察：

- Request URL；
- Request Method；
- Status Code；
- Remote Address；
- Protocol（HTTP/1.1、h2 或 h3）；
- Request Headers；
- Response Headers；
- Payload；
- Timing；
- 是否命中内存缓存、磁盘缓存或 Service Worker。

如果没有真正发出请求，问题可能发生在前端代码、Service Worker、浏览器缓存、CORS 预检或浏览器安全策略阶段。

## 15.2 按层排查

### DNS

确认域名是否解析到预期的 A/AAAA，检查不同网络环境是否结果不同。

### 连接

确认目标端口是否监听，是否被防火墙、代理、负载均衡或安全组拦截。

### TLS

确认：

- 证书是否过期；
- SAN 是否包含访问域名；
- 证书链是否完整；
- 系统时间是否正确；
- SNI 和 ALPN 是否正常；
- 客户端与服务端是否有共同 TLS 版本和密码套件。

### HTTP

确认请求方法、路径、Host、Content-Type、Authorization、Cookie、Content-Length 和编码是否符合预期。

### 应用

确认 JSON 字段、参数校验、数据库、依赖服务和业务权限。

## 15.3 常用工具思路

可以使用浏览器开发者工具、应用日志、代理访问日志和抓包工具观察请求链路。命令行环境中常用 HTTP 客户端检查响应头和重定向，例如：

```bash
curl -v https://example.com/
curl -I https://example.com/
curl -X POST https://api.example.com/users \\
  -H 'Content-Type: application/json' \\
  -d '{"name":"Alice"}'
```

这些命令只表示常见调试方式；是否能执行还取决于本机环境和权限。排查线上问题时应注意脱敏，不要把 Cookie、Authorization、Token 或个人数据直接粘贴到公共日志中。

## 15.4 Timing 中的阶段

浏览器常把请求耗时拆成：

```text
排队/阻塞
→ DNS Lookup
→ Initial connection
→ SSL/TLS
→ Request sent
→ Waiting for response（TTFB）
→ Content Download
```

- DNS 慢：关注解析器和缓存；
- Initial connection 慢：关注网络、TCP/QUIC、连接复用；
- SSL 慢：关注 TLS 握手和证书链；
- TTFB 高：关注网关排队、服务端计算、数据库和上游依赖；
- Download 慢：关注响应大小、压缩、带宽和客户端读取速度。

---

# 16. 高频面试问题辨析

## 16.1 HTTP 是无连接的吗？

需要分清不同含义：

- HTTP/1.0 时代常见短连接，每次请求建立并关闭 TCP；
- HTTP/1.1 默认支持持久连接；
- HTTP/2 和 HTTP/3 都强调连接复用；
- HTTP 的“无状态”说的是请求语义默认不保存上下文，不是说底层一定没有连接。

## 16.2 HTTP 和 HTTPS 的区别是什么？

HTTPS 不是另一个完全不同的应用协议，而是 HTTP 通过 TLS 传输。HTTPS 增加机密性、完整性和身份认证，同时带来握手、证书验证和加密计算等成本。现代硬件和连接复用使这些成本通常可以接受。

## 16.3 GET 和 POST 的区别是什么？

不能只回答“GET 放 URL、POST 放请求体”。更完整地说：

- GET 的语义是获取资源，通常安全、幂等、可缓存；
- POST 的语义是提交数据或触发处理，通常不安全、非幂等；
- GET 参数出现在 URL，可能被历史记录、日志和 Referer 记录；
- POST 请求体适合承载较复杂或较大的数据，但不代表天然安全；
- 真正安全性取决于 HTTPS、认证、授权、输入校验和业务设计。

## 16.4 301、302、307、308 有什么区别？

核心区别是永久/临时以及是否严格保持原方法和请求体：

- 301：永久，历史客户端可能改变方法；
- 302：临时，历史客户端可能改变方法；
- 307：临时，保持方法和请求体；
- 308：永久，保持方法和请求体。

## 16.5 401 和 403 有什么区别？

- 401：需要认证或认证失败，通常需要提供或更新凭证；
- 403：服务器拒绝访问，通常表示权限或策略不允许。

## 16.6 304 是成功还是失败？

它属于 3xx，但在条件缓存请求中是一种正常结果：资源没有变化，客户端使用已有缓存。它不是服务端返回完整资源，也不是错误。

## 16.7 200 响应一定表示业务成功吗？

不一定。HTTP 200 只说明 HTTP 层成功返回。应用可以在 JSON 中返回业务失败，但这种设计会让监控、缓存、重试和客户端处理变复杂。更推荐根据错误类型选择合适的 HTTP 状态码，并保持响应结构稳定。

## 16.8 Cookie 和 Session 的关系是什么？

Cookie 是客户端保存并按规则发送的小片段数据；Session 是服务端保存的会话状态。常见模式是 Cookie 只保存 Session ID，服务端根据 ID 查找 Session。Cookie 并不等于 Session，也可以用 Cookie 携带其他数据或用 Authorization Header 携带 Token。

## 16.9 为什么有了 HTTPS 还需要 Cookie 的 Secure 和 HttpOnly？

HTTPS 保护传输过程，`Secure` 防止浏览器通过明文 HTTP 发送 Cookie，`HttpOnly` 限制 JavaScript 读取 Cookie。它们保护的是不同环节，不能相互替代。

## 16.10 HTTP/2 为什么还可能有队头阻塞？

HTTP/2 解决了 HTTP 请求排队层面的部分队头阻塞，但它依赖 TCP。TCP 丢失一个报文时，后续字节通常要等待重传和按序恢复，因此多个 HTTP/2 Stream 可能一起受到影响。HTTP/3 使用 QUIC 的独立 Stream，能进一步减少这种跨流阻塞。

## 16.11 WebSocket 为什么还需要心跳？

TCP 连接长时间空闲时，中间 NAT、代理和负载均衡可能清理状态；某些网络故障也不会立即让一端感知连接已经不可用。心跳可以更快发现失效连接，并及时释放资源或触发重连。

## 16.12 DNS 解析成功但网页仍打不开，为什么？

DNS 只说明域名获得了地址，后续仍可能失败：

```text
DNS 成功
→ 目标端口未监听
→ 防火墙拦截
→ TLS 证书不匹配
→ HTTP 路由不存在
→ 认证失败
→ 服务端 5xx
```

因此不能用“能解析”推导出“服务正常”。

---

# 17. 总结：如何建立应用层知识主线

## 17.1 DNS

```text
域名
  → 递归解析器
  → 根 / TLD / 权威服务器
  → A、AAAA、CNAME 等记录
  → TTL 缓存
  → IP 地址
```

DNS 解决的是名称到地址及服务信息的映射，不负责传输网页内容。

## 17.2 HTTP

```text
URI 定位资源
  → 方法表达意图
  → 请求头传递元数据
  → 请求体承载数据
  → 状态码表达处理结果
  → 响应头控制缓存、编码和会话
  → 响应体返回表示
```

理解 HTTP 最重要的不是背诵字段，而是掌握：

- 请求和响应如何构成；
- 方法的安全性和幂等性；
- 状态码的分层含义；
- 消息体如何确定边界；
- 缓存如何新鲜、验证和失效；
- Cookie、认证和 CORS 如何影响请求；
- HTTP/1.1、HTTP/2、HTTP/3 如何演进连接模型。

## 17.3 HTTPS

```text
HTTP
  → TLS 握手
  → 证书验证
  → 密钥协商
  → 加密、完整性保护和身份认证
```

HTTPS 保护通信通道，但仍需要应用层正确处理认证、授权、输入校验、XSS、CSRF、重放和敏感信息管理。

## 17.4 WebSocket

```text
HTTP Upgrade / extended CONNECT
  → 持久连接
  → WebSocket 帧
  → 文本、二进制、Ping/Pong、Close
  → 应用层消息、重连和背压
```

WebSocket 适合双向实时通信，但不会自动解决身份认证、消息确认、断线重连、离线补偿和业务幂等。

最终可以用四个问题区分本章协议：

```text
DNS：服务在哪里？
HTTP：如何请求和返回资源？
HTTPS：如何安全地传输 HTTP？
WebSocket：如何在连接建立后持续双向通信？
```
