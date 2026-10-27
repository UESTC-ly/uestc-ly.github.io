# HTTP与Web通信

<a id="k062a5a6c3125"></a>

## Feign(HTTP)

Spring Cloud Netflix 的微服务都是以 HTTP 接口的形式暴露的，所以可以用 Apache 的 HttpClient 或 Spring 的 RestTemplate 去调用，而 Feign 是一个使用起来更加方便的 HTTP 客戶端，使用起来就像是调用自身工程的方法，而感觉不到是调用远程方法。

### 参考资料

- [Advanced Java](https://github.com/doocs/advanced-java/blob/80b89fb9496d7ea3213e402c8c3853399e00c363/docs/micro-services/micro-services-technology-stack.md#L103)，来源许可：CC-BY-SA-4.0。

<a id="k61ee623d57ae"></a>

## How to use https instead of http in create-react-app?

    You just need to use `HTTPS=true` configuration. You can edit your `package.json` scripts section:

```json
    "scripts": {
      "start": "set HTTPS=true && react-scripts start"
    }
```

    or just run `set HTTPS=true && npm start`

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L11491)，来源许可：MIT。

<a id="k0f55bd2881ce"></a>

## HTTP Header 中常见的字段有哪些？

| 请求头字段名        | 说明                                                                                                                                                                          | 示例                                                                             |
| :------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------- |
| Accept              | 能够接受的回应内容类型（Content-Types）。                                                                                                                                     | Accept: text/plain                                                               |
| Accept-Charset      | 能够接受的字符集                                                                                                                                                              | Accept-Charset: utf-8                                                            |
| Accept-Datetime     | 能够接受的按照时间来表示的版本                                                                                                                                                | Accept-Datetime: Thu, 31 May 2007 20:35:00 GMT                                   |
| Accept-Encoding     | 能够接受的编码方式列表。参考 HTTP 压缩。                                                                                                                                      | Accept-Encoding: gzip, deflate                                                   |
| Accept-Language     | 能够接受的回应内容的自然语言列表。                                                                                                                                            | Accept-Language: en-US                                                           |
| Authorization       | 用于超文本传输协议的认证的认证信息                                                                                                                                            | Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==                                |
| Cache-Control       | 用来指定在这次的请求/响应链中的所有缓存机制 都必须 遵守的指令                                                                                                                 | Cache-Control: no-cache                                                          |
| Connection          | 该浏览器想要优先使用的连接类型                                                                                                                                                | Connection: keep-alive                                                           |
| Content-Length      | 以八位字节数组（8 位的字节）表示的请求体的长度                                                                                                                                | Content-Length: 348                                                              |
| Content-MD5         | 请求体的内容的二进制 MD5 散列值，以 Base64 编码的结果                                                                                                                         | Content-MD5: Q2hlY2sgSW50ZWdyaXR5IQ==                                            |
| Content-Type        | 请求体的多媒体类型（用于 POST 和 PUT 请求中）                                                                                                                                 | Content-Type: application/x-www-form-urlencoded                                  |
| Cookie              | 之前由服务器通过 Set-Cookie（下文详述）发送的一个超文本传输协议 Cookie                                                                                                        | Cookie: $Version=1; Skin=new;                                                    |
| Date                | 发送该消息的日期和时间（按照 RFC 7231 中定义的“超文本传输协议日期”格式来发送）                                                                                                | Date: Tue, 15 Nov 1994 08:12:31 GMT                                              |
| Expect              | 表明客户端要求服务器做出特定的行为                                                                                                                                            | Expect: 100-continue                                                             |
| From                | 发起此请求的用户的邮件地址                                                                                                                                                    | From: `user@example.com`                                                         |
| Host                | 服务器的域名（用于虚拟主机），以及服务器所监听的传输控制协议端口号。如果所请求的端口是对应的服务的标准端口，则端口号可被省略。                                                | Host: en.wikipedia.org                                                           |
| If-Match            | 仅当客户端提供的实体与服务器上对应的实体相匹配时，才进行对应的操作。主要作用是用于像 PUT 这样的方法中，仅当从用户上次更新某个资源以来，该资源未被修改的情况下，才更新该资源。 | If-Match: "737060cd8c284d8af7ad3082f209582d"                                     |
| If-Modified-Since   | 允许服务器在请求的资源自指定的日期以来未被修改的情况下返回 `304 Not Modified` 状态码                                                                                          | If-Modified-Since: Sat, 29 Oct 1994 19:43:31 GMT                                 |
| If-None-Match       | 允许服务器在请求的资源的 ETag 未发生变化的情况下返回 `304 Not Modified` 状态码                                                                                                | If-None-Match: "737060cd8c284d8af7ad3082f209582d"                                |
| If-Range            | 如果该实体未被修改过，则向我发送我所缺少的那一个或多个部分；否则，发送整个新的实体                                                                                            | If-Range: "737060cd8c284d8af7ad3082f209582d"                                     |
| If-Unmodified-Since | 仅当该实体自某个特定时间以来未被修改的情况下，才发送回应。                                                                                                                    | If-Unmodified-Since: Sat, 29 Oct 1994 19:43:31 GMT                               |
| Max-Forwards        | 限制该消息可被代理及网关转发的次数。                                                                                                                                          | Max-Forwards: 10                                                                 |
| Origin              | 发起一个针对跨来源资源共享的请求。                                                                                                                                            | `Origin: http://www.example-social-network.com`                                  |
| Pragma              | 与具体的实现相关，这些字段可能在请求/回应链中的任何时候产生多种效果。                                                                                                         | Pragma: no-cache                                                                 |
| Proxy-Authorization | 用来向代理进行认证的认证信息。                                                                                                                                                | Proxy-Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==                          |
| Range               | 仅请求某个实体的一部分。字节偏移以 0 开始。参见字节服务。                                                                                                                     | Range: bytes=500-999                                                             |
| Referer             | 表示浏览器所访问的前一个页面，正是那个页面上的某个链接将浏览器带到了当前所请求的这个页面。                                                                                    | `Referer: http://en.wikipedia.org/wiki/Main_Page`                                |
| TE                  | 浏览器预期接受的传输编码方式：可使用回应协议头 Transfer-Encoding 字段中的值；                                                                                                 | TE: trailers, deflate                                                            |
| Upgrade             | 要求服务器升级到另一个协议。                                                                                                                                                  | Upgrade: HTTP/2.0, SHTTP/1.3, IRC/6.9, RTA/x11                                   |
| User-Agent          | 浏览器的浏览器身份标识字符串                                                                                                                                                  | User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/21.0 |
| Via                 | 向服务器告知，这个请求是由哪些代理发出的。                                                                                                                                    | Via: 1.0 fred, 1.1 example.com (Apache/1.1)                                      |
| Warning             | 一个一般性的警告，告知，在实体内容体中可能存在错误。                                                                                                                          | Warning: 199 Miscellaneous warning                                               |

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions.md#L140)，来源许可：Apache-2.0。

<a id="kef555c28de0e"></a>

## HTTP 代理、HTTPS 代理、HTTP CONNECT 与 SOCKS5 如何转发请求？TLS 在哪里终止？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐⭐ (5/5)**

### HTTP 与 HTTPS 代理最容易被误解的地方

配置中的 `HTTPS_PROXY=http://127.0.0.1:7897` 并不矛盾。左侧的 `HTTPS_PROXY` 表示“用于 HTTPS 目标请求的代理设置”，右侧的 `http://` 表示“客户端如何与代理端口对话”。访问 HTTPS 目标时，客户端通常先向 HTTP 代理发送：

```http
CONNECT github.com:443 HTTP/1.1
Host: github.com:443
```

代理建立到目标的 TCP 连接并返回成功后，这条连接切换为双向字节隧道。随后客户端才在隧道内与 `github.com` 进行 TLS 握手。按照 HTTP 语义规范，`CONNECT` 的成功响应会把连接切换到 tunnel mode；普通转发代理若不主动做 TLS 中间人解密，就看不到加密后的 HTTP 路径、请求体和响应体。

因此需要区分两个概念：

- **HTTPS over HTTP proxy**：应用到代理使用 HTTP `CONNECT`，TLS 仍在应用与目标站之间终止。
- **HTTPS proxy**：应用到代理本身也使用 TLS，再在其中请求建立隧道。这保护的是“客户端到代理”这一跳，但部署更少见。

### SOCKS5 是更通用的传输层中间层

RFC 1928 把 SOCKS5 定义为位于应用层与传输层之间的 shim layer。客户端先协商认证方式，再发送 `CONNECT`、`BIND` 或 `UDP ASSOCIATE` 请求，并可携带 IPv4、IPv6 或域名目标。SOCKS5 不理解 HTTP 业务语义，因此能为 SSH、数据库连接及其他 TCP 应用提供通用转发。

`socks5://` 与 `socks5h://` 的差别常出现在命令行工具中：前者一般由本地应用先解析域名再把 IP 交给代理，后者把域名交给 SOCKS 代理侧解析。后者有助于保持域名规则上下文并减少本地 DNS 泄漏，但具体行为仍取决于客户端实现。

### TLS 与代理协议的加密不是同一层

一次代理访问可能同时存在两种加密：

1. 应用与目标站之间的 TLS，保护 HTTPS 内容与目标身份验证。
2. 本地内核与远端代理节点之间的代理协议加密或 TLS 封装，保护这一段传输并隐藏原始流量形态的一部分。

两者不能互相替代。如果最终访问的是明文 HTTP，即使代理节点链路加密，远端节点到目标站之间仍可能是明文；如果客户端安装并信任了中间人 CA，代理也可能终止 TLS 并检查内容。判断安全性时必须问清楚：哪一段被加密、证书由谁验证、TLS 在哪里终止。

**面试中可以用一句话收束：HTTP CONNECT 建立的是字节隧道，SOCKS5提供的是通用目标转发，而 TLS 保护哪一段连接取决于其真正的终止点。**

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E4%BB%A3%E7%90%86%E3%80%81%E9%9A%A7%E9%81%93%E4%B8%8EVPN%E6%9C%AC%E8%B4%A8%E5%8E%9F%E7%90%86%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L96)，来源许可：GPL-3.0。

<a id="k479c8683b4df"></a>

## HTTP 和 HTTPS 有什么区别？（重要）

![HTTP 和 HTTPS 对比](https://oss.javaguide.cn/github/javaguide/cs-basics/network/http-vs-https.png)

- **端口号**：HTTP 默认是 80，HTTPS 默认是 443。
- **URL 前缀**：HTTP 的 URL 前缀是 `http://`，HTTPS 的 URL 前缀是 `https://`。
- **安全性和传输方式**：未使用 TLS 的 HTTP 默认不提供机密性、完整性和对端身份认证。HTTPS 使用 TLS 保护 HTTP；HTTP/1.1 和 HTTP/2 通常使用 TLS over TCP，HTTP/3 使用集成 TLS 1.3 的 QUIC。TLS 握手负责认证对端并建立流量密钥，后续数据由对称 AEAD 算法保护。证书主要用于身份认证，不能笼统地说“证书加密了对称密钥”。
- **SEO（搜索引擎优化）**：搜索引擎通常会更青睐使用 HTTPS 协议的网站，因为 HTTPS 能够提供更高的安全性和用户隐私保护。使用 HTTPS 协议的网站在搜索结果中可能会被优先显示，从而对 SEO 产生影响。

关于 HTTP 和 HTTPS 更详细的对比总结，可以看我写的这篇文章：[HTTP vs HTTPS（应用层）](https://javaguide.cn/cs-basics/network/http-vs-https.html)。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions.md#L177)，来源许可：Apache-2.0。

<a id="kaf26bc854246"></a>

## HTTP 是不保存状态的协议，如何保存用户状态？

HTTP 协议本身是 **无状态的（stateless）**。这意味着服务器默认情况下无法区分两个连续的请求是否来自同一个用户，或者同一个用户之前的操作是什么。这就像一个“健忘”的服务员，每次你跟他说话，他都不知道你是谁，也不知道你之前点过什么菜。

但在实际的 Web 应用中，比如网上购物、用户登录等场景，我们显然需要记住用户的状态（例如购物车里的商品、用户的登录信息）。为了解决这个问题，主要有以下几种常用机制：

**方案一：Session（会话）配合 Cookie（主流方式）：**

![Session 配合 Cookie 保存用户登录状态的流程](https://oss.javaguide.cn/github/javaguide/system-design/security/session-cookie-authentication-process.png)

这可以说是最经典也是最常用的方法了。基本流程是这样的：

1. 用户向服务器发送用户名、密码、验证码用于登陆系统。
2. 服务器验证通过后，会为这个用户创建一个专属的 Session 对象（可以理解为服务器上的一块内存，存放该用户的状态数据，如购物车、登录信息等）存储起来，并给这个 Session 分配一个唯一的 `SessionID`。
3. 服务器通过 HTTP 响应头中的 `Set-Cookie` 指令，把这个 `SessionID` 发送给用户的浏览器。
4. 浏览器接收到 `SessionID` 后，会将其以 Cookie 的形式保存在本地。当用户保持登录状态时，每次向该服务器发请求，浏览器都会自动带上这个存有 `SessionID` 的 Cookie。
5. 服务器收到请求后，从 Cookie 中拿出 `SessionID`，就能找到之前保存的那个 Session 对象，从而知道这是哪个用户以及他之前的状态了。

使用 Session 的时候需要注意下面几个点：

- **客户端 Cookie 支持**：依赖 Session 的核心功能要确保用户浏览器开启了 Cookie。
- **Session 过期管理**：合理设置 Session 的过期时间，平衡安全性和用户体验。
- **Session ID 安全**：为包含 `SessionID` 的 Cookie 设置 `HttpOnly` 标志可以防止客户端脚本（如 JavaScript）窃取，设置 Secure 标志可以保证 `SessionID` 只在 HTTPS 连接下传输，增加安全性。

Session 数据本身存储在服务器端。常见的存储方式有：

- **服务器内存**：实现简单，访问速度快，但服务器重启数据会丢失，且不利于多服务器间的负载均衡。这种方式适合简单且用户量不大的业务场景。
- **数据库（如 MySQL, PostgreSQL）**：数据持久化，但读写性能相对较低，一般不会使用这种方式。
- **分布式缓存（如 Redis）**：性能高，支持分布式部署，是目前大规模应用中非常主流的方案。

**方案二：当 Cookie 被禁用时：URL 重写（URL Rewriting）**

如果用户的浏览器禁用了 Cookie，或者某些情况下不便使用 Cookie，还有一种备选方案是 URL 重写。这种方式会将 `SessionID` 直接附加到 URL 的末尾，作为参数传递。例如：<http://www.example.com/page?sessionid=xxxxxx>。服务器端会解析 URL 中的 `sessionid` 参数来获取 `SessionID`，进而找到对应的 Session 数据。

这种方法一般不会使用，存在以下缺点：

- URL 会变长且不美观；
- `SessionID` 暴露在 URL 中，安全性较低（容易被复制、分享或记录在日志中）；
- 对搜索引擎优化（SEO）可能不友好。

**方案三：Token-based 认证（如 JWT - JSON Web Tokens）**

这是一种越来越流行的无状态认证方式，尤其适用于前后端分离的架构和微服务。

![JWT 身份验证示意图](https://oss.javaguide.cn/github/javaguide/system-design/jwt/jwt-authentication%20process.png)

以 JWT 为例（普通 Token 方案也可以），简化后的步骤如下：

1. 用户向服务器发送用户名、密码以及验证码用于登陆系统。
2. 如果用户名、密码以及验证码校验正确的话，服务端会返回已经签名的 Token，也就是 JWT。
3. 客户端收到 Token 后自己保存起来（比如浏览器的 `localStorage`）。
4. 用户以后每次向后端发请求都在 Header 中带上这个 JWT。
5. 服务端检查 JWT 并从中获取用户相关信息。

JWT 详细介绍可以查看这两篇文章：

- [JWT 基础概念详解](https://javaguide.cn/system-design/security/jwt-intro.html)
- [JWT 身份认证优缺点分析](https://javaguide.cn/system-design/security/advantages-and-disadvantages-of-jwt.html)

总结来说，虽然 HTTP 本身是无状态的，但通过 Cookie + Session、URL 重写或 Token 等机制，我们能够有效地在 Web 应用中跟踪和管理用户状态。其中，**Cookie + Session 是最传统也最广泛使用的方式，而 Token-based 认证则在现代 Web 应用中越来越受欢迎。**

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions.md#L299)，来源许可：Apache-2.0。

<a id="k70e50da1ddef"></a>

## HTTP/1.0 和 HTTP/1.1 有什么区别？

![HTTP/1.0 和 HTTP/1.1 对比](https://oss.javaguide.cn/github/javaguide/cs-basics/network/http1.0-vs-http1.1.png)

- **连接方式**：HTTP/1.0 为短连接，HTTP/1.1 支持长连接。HTTP 协议的长连接和短连接，实质上是 TCP 协议的长连接和短连接。
- **状态响应码**：HTTP/1.1 中新加入了大量的状态码，光是错误响应状态码就新增了 24 种。比如说，`100 (Continue)`——允许客户端在发送较大请求体前确认服务器愿意继续接收，`206 (Partial Content)`——范围请求的标识码，`409 (Conflict)`——请求与当前资源的规定冲突，`410 (Gone)`——目标资源已不再可用，这种状态很可能是永久的，并且服务器不知道可用的转发地址。
- **缓存机制**：在 HTTP/1.0 中主要使用 Header 里的 If-Modified-Since,Expires 来做为缓存判断的标准，HTTP/1.1 则引入了更多的缓存控制策略例如 Entity tag，If-Unmodified-Since, If-Match, If-None-Match 等更多可供选择的缓存头来控制缓存策略。
- **带宽**：HTTP/1.0 中，存在一些浪费带宽的现象，例如客户端只是需要某个对象的一部分，而服务器却将整个对象送过来了，并且不支持断点续传功能，HTTP/1.1 则在请求头引入了 range 头域，它允许只请求资源的某个部分，即返回码是 206（Partial Content），这样就方便了开发者自由的选择以便于充分利用带宽和连接。
- **Host 头（Host Header）处理**：HTTP/1.1 引入了 Host 头字段，允许在同一 IP 地址上托管多个域名，从而支持虚拟主机的功能。而 HTTP/1.0 没有 Host 头字段，无法实现虚拟主机。

关于 HTTP/1.0 和 HTTP/1.1 更详细的对比总结，可以看我写的这篇文章：[HTTP/1.0 vs HTTP/1.1（应用层）](https://javaguide.cn/cs-basics/network/http1.0-vs-http1.1.html)。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions.md#L221)，来源许可：Apache-2.0。

<a id="k0dc78ec2b41b"></a>

## HTTP/1.1 和 HTTP/2.0 有什么区别？

![HTTP/1.0 和 HTTP/1.1 对比](https://oss.javaguide.cn/github/javaguide/cs-basics/network/http1.1-vs-http2.0.png)

- **多路复用（Multiplexing）**：HTTP/2.0 在同一连接上可以同时传输多个请求和响应（可以看作是 HTTP/1.1 中长链接的升级版本），互不干扰。HTTP/1.1 则使用串行方式，每个请求和响应都需要独立的连接，而浏览器为了控制资源会有 6-8 个 TCP 连接的限制。这使得 HTTP/2.0 在处理多个请求时更加高效，减少了网络延迟和提高了性能。
- **二进制帧（Binary Frames）**：HTTP/2.0 使用二进制帧进行数据传输，而 HTTP/1.1 则使用文本格式的报文。二进制帧更加紧凑和高效，减少了传输的数据量和带宽消耗。
- **队头阻塞**：HTTP/2 引入了多路复用技术，允许多个请求和响应在单个 TCP 连接上并行交错传输，解决了 HTTP/1.1 应用层的队头阻塞问题，但 HTTP/2 依然受到 TCP 层队头阻塞的影响。
- **头部压缩（Header Compression）**：HTTP/1.1 支持 `Body` 压缩，`Header` 不支持压缩。HTTP/2.0 支持对 `Header` 压缩，使用了专门为 `Header` 压缩而设计的 HPACK 算法，减少了网络开销。
- **服务器推送（Server Push）**：HTTP/2.0 支持服务器推送，可以在客户端请求一个资源时，将其他相关资源一并推送给客户端，从而减少了客户端的请求次数和延迟。而 HTTP/1.1 需要客户端自己发送请求来获取相关资源。

HTTP/2.0 多路复用效果图（图源： [HTTP/2 For Web Developers](https://blog.cloudflare.com/http-2-for-web-developers/)）：

![HTTP/2 在单个 TCP 连接上多路复用多个请求和响应](https://oss.javaguide.cn/github/javaguide/cs-basics/network/http2.0-multiplexing.png)

可以看到，HTTP/2 的多路复用机制允许多个请求和响应共享一个 TCP 连接，从而避免了 HTTP/1.1 在应对并发请求时需要建立多个并行连接的情况，减少了重复连接建立和维护的额外开销。而在 HTTP/1.1 中，尽管支持持久连接，但为了缓解队头阻塞问题，浏览器通常会为同一域名建立多个并行连接。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions.md#L233)，来源许可：Apache-2.0。

<a id="k252ab7a5cc2a"></a>

## HTTP/2.0 和 HTTP/3.0 有什么区别？

![HTTP/2.0 和 HTTP/3.0 对比](https://oss.javaguide.cn/github/javaguide/cs-basics/network/http2.0-vs-http3.0.png)

- **传输协议**：HTTP/2 基于 TCP，HTTP/3 则把 HTTP 语义映射到 QUIC。QUIC 构建在 UDP 之上，在传输层实现可靠交付、拥塞控制、流量控制和 TLS 1.3 安全保护。
- **连接建立**：HTTP/2 的 HTTPS 连接需要先建立 TCP 连接，再完成 TLS 握手；HTTP/3 把传输参数协商和 TLS 1.3 握手结合在 QUIC 建连过程中。新的 QUIC 连接通常使用 1-RTT；0-RTT 只适用于客户端持有先前连接状态的恢复场景，而且早期数据存在重放风险。比较延迟时还要统一采用“何时可发送首个请求”或“何时收到首字节”等同一个指标。
- **头部压缩**：HTTP/2.0 使用 HPACK 算法进行头部压缩，而 HTTP/3.0 使用更高效的 QPACK 头压缩算法。
- **队头阻塞**：HTTP/2 的多个流复用同一个 TCP 连接，TCP 丢包会阻塞这条连接上的所有流。QUIC 在流之间提供独立的可靠有序交付；某个流的数据丢失后，该流会等待缺失数据恢复，但通常不会阻止其他流继续前进。
- **连接迁移**：QUIC 使用独立于 IP/端口四元组的 Connection ID 标识连接。Connection ID 不是固定 64 位：QUIC v1 可以使用零长度到 20 字节的 Connection ID，端点还可以签发和退役多个 Connection ID。网络地址变化后，端点可以验证新路径并维持同一逻辑连接。
- **错误恢复**：HTTP/3.0 具有更好的错误恢复机制，当出现丢包、延迟等网络问题时，可以更快地进行恢复和重传。而 HTTP/2.0 则需要依赖于 TCP 的错误恢复机制。
- **安全性**：HTTP/2 通常使用 TLS 保护 HTTP 头部和数据负载，但 IP、TCP 头以及 TLS 记录层的外部头字段仍然可见。QUIC 使用 TLS 派生的密钥保护报文载荷，并对包号和部分首字节字段做头部保护；IP/UDP 头和部分 QUIC 头字段仍然可见，Version Negotiation 等报文也不具备同样的密码学保护，因此不能说 QUIC 加密了整个数据包的全部报文头。

HTTP/1.0、HTTP/2.0 和 HTTP/3.0 的协议栈比较：

![HTTP/1、HTTP/2 和 HTTP/3 协议栈对比](https://oss.javaguide.cn/github/javaguide/cs-basics/network/http-3-implementation.png)

下图是一个更详细的 HTTP/2.0 和 HTTP/3.0 对比图：

![HTTP/2.0 和 HTTP/3.0 详细对比图](https://oss.javaguide.cn/github/javaguide/cs-basics/network/http2-and-http3-stacks-comparison.png)

从上图可以看出：

- **HTTP/2.0**：使用 TCP 作为传输协议、使用 HPACK 进行头部压缩、依赖 TLS 进行加密。
- **HTTP/3.0**：使用基于 UDP 的 QUIC 协议、使用更高效的 QPACK 进行头部压缩、在 QUIC 中直接集成了 TLS。QUIC 协议具备连接迁移、拥塞控制与避免、流量控制等特性。

关于 HTTP/1.0 -> HTTP/3.0 更详细的演进介绍，推荐阅读[HTTP1 到 HTTP3 的工程优化](https://dbwu.tech/posts/http_evolution/)。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions.md#L249)，来源许可：Apache-2.0。

<a id="k10e46d666774"></a>

## HTTPS和HTTP的区别

1、HTTP协议传输的数据都是未加密的，也就是明文的，因此使用HTTP协议传输隐私信息非常不安全， HTTPS协议是由SSL+HTTP协议构建的可进行加密传输、身份认证的网络协议，要比http协议安全。

2、https协议需要到ca申请证书，一般免费证书较少，因而需要一定费用。
3、http和https使用的是完全不同的连接方式，用的端口也不一样，前者是80，后者是443。

<p  id="什么是艾斯提和提爱斯"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-01-net.md#L373)，来源许可：Apache-2.0。

<a id="k2289fbe14f74"></a>

## HTTP与HTTPS的区别

**常见问法：** HTTP和HTTPS有什么区别？

* HTTP
  * 互联网上应用最为广泛的一种网络协议，是一个客户端和服务器端请求和应答的标准（TCP），用于从WWW服务器传输超文本到本地浏览器的传输协议，它可以使浏览器更加高效，使网络传输减少。
* HTTPS
  * 以安全为目标的HTTP通道，简单讲是HTTP的安全版，即HTTP下加入SSL层，HTTPS的安全基础是SSL，因此加密的详细内容就需要SSL。
  * 工作原理：
    * 客户使用HTTPS的URL访问Web服务器，要求与Web服务器建立SSL连接。
    * Web服务器收到客户端请求后，会将网站的证书信息（证书中包含公钥）传送一份给客户端。
    * 客户端的浏览器与Web服务器开始协商SSL连接的安全等级，也就是信息加密的等级。
    * 客户端的浏览器根据双方同意的安全等级，建立会话密钥，然后利用网站的公钥将会话密钥加密，并传送给网站。
    * Web服务器利用自己的私钥解密出会话密钥。
    * Web服务器利用会话密钥加密与客户端之间的通信。

![](https://i.loli.net/2021/03/12/iDyBOY49orGjt8k.gif)

* 区别：
  * HTTPS协议需要到ca申请证书，一般免费证书较少，因而需要一定费用；
  * HTTP是超文本传输协议，信息是明文传输，HTTPS则是具有安全性的SSL加密传输协议；
  * HTTP和HTTPS使用的是完全不同的连接方式，用的端口也不一样，前者是80，后者是443；
  * HTTP的连接很简单，是无状态的；HTTPS协议是由SSL+HTTP协议构建的可进行加密传输、身份认证的网络协议，比HTTP协议安全。

### 补充说明

1. 端口不同：HTTP使用的是80端口，HTTPS使用443端口；
2. HTTP（超文本传输协议）信息是明文传输，HTTPS运行在SSL(Secure Socket Layer)之上，添加了加密和认证机制，更加安全；
3. HTTPS由于加密解密会带来更大的CPU和内存开销；
4. HTTPS通信需要证书，一般需要向证书颁发机构（CA）购买

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/03-computer-basics/computer-network/network-protocols.md#L205)，来源许可：GPL-3.0。
- [Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Computer%20Network.md#L256)，来源许可：GPL-3.0。

<a id="k44da7d569ab0"></a>

## HTTP各版本

![image-20220528142308368](https://raw.githubusercontent.com/wolverinn/Waking-Up/cf692b53e1b3d1b740a97dab0e4e71db801daf33/_v_images/202205281423439.png)

- HTTP 0.9版本

  - HTTP协议的第一个版本，功能简单，**已弃用**
  - 仅支持纯文本数据的传输，虽然支持HTML，但是不支持图片插入
  - 仅支持GET请求方式，且不支持请求头
  - 无状态，短连接。没有对用户状态的管理；每次请求建立一个TCP连接，响应之后关闭TCP连接。

- HTTP 1.0版本

  - 支持POST、GET、HEAD三种方法
  - **支持长连接keep-alive**（但**默认还是使用短连接**：浏览器每一次请求建立一次TCP连接，请求处理完毕之后断开）。
  - 服务器不跟踪用户的行为也不记录用户过往请求。

- HTTP 1.1版本

  - 新增PUT、DELETE、CONNECT、TRACE、OPTIONS方法，是现今**使用最多**的版本。
  - 支持长连接，在一次TCP连接中可以发送多个请求或响应，且默认使用长连接。
  - 支持宽带优化、断点续传。请求的对象部分数据，可以不必发送整个对象；文件上传下载支持续传。
  - 因为长连接产生的问题：队头阻塞。长连接中，发送请求和响应都是串行化的，前面的消息会造成后面的消息也阻塞。解决方法是创建多个TCP连接，这样就可以基本保证了可用性，浏览器**默认的最大TCP连接数是6个**。

- HTTP 2.0版本

  - 二进制分帧，所有帧都是用二进制编码，节省了空间
  - 多路复用：HTTP 2.0中所有的连接都是持久化的。相比1.1版本可以不用维护更多的TCP连接，在处理并发请求的时候，可以将多个数据流中**互不依赖的帧**可以**乱序发送**，同时还支持**优先级**。接收方接收之后可以根据帧头部信息将帧组合起来。（解决了1.1版本中的队头阻塞问题）
  - 头部压缩：1.1版本每次传输都需要传输一份首部，2.0让双方各自缓存一份首部字段表，达到更快传输的目标。

- HTTP 3.0版本

  - 基于UDP的**QUIC多路复用**：在一个QUIC中可以并发发送多个HTTP请求Stream，且如果各个Stream互不依赖，那么就不会造成**使用TCP带来的队头阻塞问题**。这个问题源头上是因为TCP连接，TCP连接的性质决定了重传会影响队后的数据发送，所以干脆选用UDP来解决这个方案。
  - 0RTT建链：RTT表示Round-Trip Time，3.0可以实现0RTT建链。一般来说HTTPS协议要建立完整链接包括**TCP握手**和**TLS握手**，总计需要至少2-3个RTT，普通的HTTP协议也需要至少1个RTT才可以完成握手。基于UDP的QUIC协议可以在第一次发送包的时候直接发送业务数据。但是由于首次连接需要发送公钥数据，所以首次连接并不使用这一方法。

  ![image-202205281424550.gif](https://raw.githubusercontent.com/wolverinn/Waking-Up/cf692b53e1b3d1b740a97dab0e4e71db801daf33/_v_images/202205281424550.gif)

  > 参考文档：[图解 | 为什么HTTP3.0要弃用TCP协议，而改用UDP协议？_涛哥聊Python-CSDN博客](

### 参考资料

- [Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Computer%20Network.md#L409)，来源许可：GPL-3.0。

<a id="kbd2cffdeb265"></a>

## HTTP报文

HTTP报文有请求报文和响应报文两种，请求报文：从客户向服务器发送请求报文；响应报文：从服务端到客户的回答。HTTP报文都由**开始行、首部行、实体主体**三部分组成。

* **开始行**
  * 请求报文
    * 由 **方法**、**[空格]**、**URL**、**[空格]**、**HTTP版本** 组成。
  * 响应报文
    * 由 **HTTP 版本**、**[空格]**、**状态码**组成。
* **首部行**
  * 是用来说明浏览器、服务器或报文主体的一些信息。
  * 可以有好几行，也可以不使用
  * 每个首部行都是由 **首部字段名**、**[空格]** 和 **值** 组成
  * 每个首部行在结束地方都有 `CRLF`（『回车』和『换行』符）
* **实体主体**
  * 在请求报文中，一般是 post/put 提交的表单信息。与首部行之间有 `CRLF` 即空行。

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/03-computer-basics/computer-network/network-protocols.md#L188)，来源许可：GPL-3.0。

<a id="k08e33e96ec48"></a>

## HTTP状态码

* 2xx状态码：操作成功。200 OK；

* 3xx状态码：重定向。301 永久重定向；302暂时重定向；
* 4xx状态码：客户端错误。400 Bad Request；401 Unauthorized；403 Forbidden；404 Not Found；
* 5xx状态码：服务端错误。500服务器内部错误；501服务不可用；

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/03-computer-basics/computer-network/network-protocols.md#L180)，来源许可：GPL-3.0。

<a id="k1083527b04d3"></a>

## http网络协议和grpc协议有哪些异同？

### HTTP（Hypertext Transfer Protocol）
特点：
1.简单易用：HTTP 使用简单的请求方法和状态码来进行通信，如 GET、POST、200 OK、404 Not Found 等。它易于理解和使用，适合 Web 应用程序的开发。
2.无状态：HTTP 是无状态协议，服务器不会保留与客户端之间的会话状态。每个请求都是独立的，服务器无法识别多个请求是否来自同一客户端。
3.明文传输：HTTP 在传输数据时不对数据进行加密，因此数据在传输过程中可能会被窃听或篡改。为了加强安全性，可以使用 HTTPS（HTTP over TLS）进行加密传输。
4.基于文本：HTTP 使用可读的文本格式进行通信，如使用 JSON、XML 或 HTML 格式进行数据的传输和呈现。这使得数据在传输过程中易于调试和查看。

适用场景：
1.Web 应用程序开发，特别是浏览器和服务器之间的通信。
2.RESTful API 的设计和开发，通过 HTTP 方法和 URL 来实现资源的操作。
3.数据传输不要求低延迟或高吞吐量的场景。

### gRPC（Google Remote Procedure Call）
特点：
1.高性能：gRPC 使用基于二进制的协议，并采用 Protocol Buffers 进行高效的消息序列化和反序列化。它使用 HTTP/2 作为底层传输协议，支持多路复用、头部压缩和流等特性，提供了更低的延迟和更高的吞吐量。
2.跨语言支持：gRPC 提供了多种编程语言的支持，如 C++, Java, Python, Go 等。通过使用 Protocol Buffers 的接口描述语言，可以自动生成客户端和服务端的代码，提供了更好的类型安全性和编译时检查。
3.支持多种消息传输方式：gRPC 不仅支持基于 HTTP/2 的传输方式，还支持原生的 TCP 或 UDP 传输，以及使用 WebSocket 进行双向通信。这使得 gRPC 可以适应不同的应用场景和网络环境。
4.提供多种消息序列化格式：gRPC 默认使用 Protocol Buffers 进行消息的序列化和反序列化，但也支持其他格式，如 JSON。这样可以在不同的数据传输需求之间进行灵活选择。5.支持服务治理：gRPC 提供了丰富的服务治理功能，如负载均衡、服务发现和故障恢复等。它与现代的容器和服务编排平台（如 Kubernetes）集成良好，使得构建和管理大规模分布式系统变得更加容易。

适用场景：
1.分布式系统和微服务架构的开发，特别是需要高性能和跨语言支持的场景。
2.需要低延迟和高吞吐量的数据传输场景。
3.需要复杂的服务治理和负载均衡功能的场景。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L952)，来源许可：GPL-3.0。

<a id="k5d57d409fbe0"></a>

## HTTP请求和响应报文有哪些主要字段？

### 请求报文

简单来说：

- 请求行：Request Line
- 请求头：Request Headers
- 请求体：Request Body

### 响应报文

- 状态行：Status Line
- 响应头：Response Headers
- 响应体：Response Body

<p id="库克是什么"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-02-net.md#L84)，来源许可：Apache-2.0。

<a id="k9ae4e293160a"></a>

## HTTP请求方法你知道多少？

客户端发送的   **请求报文**   第一行为请求行，包含了方法字段。

根据 HTTP 标准，HTTP 请求可以使用多种请求方法。

HTTP1.0 定义了三种请求方法： GET, POST 和 HEAD方法。

HTTP1.1 新增了六种请求方法：OPTIONS、PUT、PATCH、DELETE、TRACE 和 CONNECT 方法。

| 序  号 | 方法    | 描述                                                         |
| :----- | :------ | :----------------------------------------------------------- |
| 1      | GET     | 请求指定的页面信息，并返回实体主体。                         |
| 2      | HEAD    | 类似于 GET 请求，只不过返回的响应中没有具体的内容，用于获取报头 |
| 3      | POST    | 向指定资源提交数据进行处理请求（例如提交表单或者上传文件）。数据被包含在请求体中。POST 请求可能会导致新的资源的建立和/或已有资源的修改。 |
| 4      | PUT     | 从客户端向服务器传送的数据取代指定的文档的内容。             |
| 5      | DELETE  | 请求服务器删除指定的页面。                                   |
| 6      | CONNECT | HTTP/1.1 协议中预留给能够将连接改为管道方式的代理服务器。    |
| 7      | OPTIONS | 允许客户端查看服务器的性能。                                 |
| 8      | TRACE   | 回显服务器收到的请求，主要用于测试或诊断。                   |
| 9      | PATCH   | 是对 PUT 方法的补充，用来对已知资源进行局部更新 。           |

<p  id="和的区别你知道哪些"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-01-net.md#L203)，来源许可：Apache-2.0。

<a id="k0852b6b8663e"></a>

## LLM/AIGC服务为什么需要流式传输？SSE、WebSocket、gRPC怎么选？

LLM生成通常是逐token产生，如果等完整答案生成后一次性返回，用户会感受到很长等待。流式传输可以把首token更快返回，让前端边生成边展示，也便于中途取消、进度展示和超时控制。

| 协议 | 特点 | 适合场景 |
| --- | --- | --- |
| SSE | HTTP单向流，浏览器支持好，实现简单 | 聊天机器人、文本生成、只需要服务端推送 |
| WebSocket | 双向长连接 | 实时语音、多人协作、客户端需要持续发送控制消息 |
| gRPC streaming | 基于HTTP/2，强类型IDL，适合服务间调用 | 模型网关到推理服务、内部微服务流式通信 |

选择建议：

1. Web前端文本生成：优先SSE，简单稳定。
2. 语音对话、实时中断、双向事件：优先WebSocket。
3. 后端服务间高性能调用：优先gRPC streaming。
4. 大文件生成结果：不要直接长期占用流，生成结果落对象存储，再返回URL或任务状态。

面试金句：流式传输解决的是交互延迟和可控性，不是模型计算变快。系统仍然要处理超时、取消、背压、断线重连和日志追踪。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L1365)，来源许可：GPL-3.0。

<a id="k933159537bd8"></a>

## localstorage、sessionstorage 的区别，以及使用场景是什么？

localStorage：生命周期是永久的，关闭页面或浏览器之后 localStorage 中的数据也不会消失。localStorage 除非主动删除数据，否则数据永远不会消失（只会存储 string）。

sessionStorage：生命周期是在仅在当前会话下有效。sessionStorage 引入了一个“浏览器窗口”的概念，sessionStorage 是在同源的窗口中始终存在的数据。只要这个浏览器窗口没有关闭，即使刷新页面或者进入同源另一个页面，数据依然存在。但是 sessionStorage 在关闭了浏览器窗口后就会被销毁。同时独立的打开同一个窗口同一个页面，sessionStorage 也是不一样的。

使用方法：

```javascript
window.localStorage
window.sessionStorage
```

API：

```javascript
setItem(key, value) // 保存数据，以键值对的方式储存信息。
getItem(key) // 获取数据，将键值传入，即可获取到对应的 value 值。
removeItem(key) // 删除单个数据，根据键值移除对应的信息。
clear() // 删除所有的数据
key(index) // 获取某个索引的 key
```

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/03-computer-basics/computer-network/http-protocol.md#L99)，来源许可：GPL-3.0。

<a id="k8f0aab718452"></a>

## MCP 的 stdio 与 Streamable HTTP 如何选择？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

新版 MCP 中，标准传输主要是 `stdio` 和 `Streamable HTTP`。旧的 HTTP+SSE 传输用于兼容历史实现，通常不建议新项目优先选择。

| 传输 | 工作方式 | 适合场景 | 注意事项 |
| --- | --- | --- | --- |
| stdio | Host 启动本地子进程，通过 stdin/stdout 交换 JSON-RPC 消息 | 本地开发工具、CLI、文件系统、低延迟单用户场景 | 权限继承宿主进程，需限制可执行来源 |
| Streamable HTTP | Server 作为 HTTP 服务，支持远程连接和流式响应 | 企业服务、云端工具、多用户部署、跨网络访问 | 必须做认证、授权、TLS、审计和限流 |
| SSE | 旧版 HTTP+Server-Sent Events 路线 | 兼容旧 MCP Server | 新项目优先迁移到 Streamable HTTP |

选择建议：

- 本地私人工具优先 `stdio`。
- 团队共享或云端工具优先 `Streamable HTTP`。
- 远程 MCP Server 不应裸露公网。
- 本地 HTTP Server 应默认绑定 `localhost`。
- 对敏感工具要加 RBAC、审计和参数级权限控制。

需要注意，不能简单说 `stdio` 永远最好。它低延迟、部署简单，但不适合多租户、远程服务和集中治理。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/04_MCP%E4%B8%8EA2A%E5%8D%8F%E8%AE%AE%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L385)，来源许可：GPL-3.0。

<a id="k1d3b32264878"></a>

## MCP 的 stdio、Streamable HTTP、SSE 传输如何选择？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

| 传输 | 特点 | 适合场景 |
| --- | --- | --- |
| stdio | 客户端启动本地子进程，通过 stdin/stdout 通信 | 本地工具、CLI、开发环境、低延迟 |
| Streamable HTTP | 独立 HTTP 服务，可支持多客户端、远程部署和流式响应 | 企业工具服务、云端 MCP、多用户 |
| SSE | 旧版 HTTP+SSE 路线，逐步被 Streamable HTTP 替代 | 兼容旧实现 |

安全注意：

- 本地 Streamable HTTP 应绑定 localhost，避免暴露到公网。
- 远程 MCP 必须有认证、授权和审计。
- 工具返回内容要防 prompt injection。
- 高风险工具要有 approval policy。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/01_AIGC%E6%97%B6%E4%BB%A3AI%20Agent%E5%9F%BA%E7%A1%80%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L358)，来源许可：GPL-3.0。

<a id="k9128cde227fd"></a>

## REST、RPC、gRPC、WebSocket在Agent系统中如何分工？

Agent系统通常包含模型服务、工具服务、检索服务、沙箱服务、状态服务和前端交互。不同通信方式适合不同边界：

| 通信方式 | 优点 | Agent场景 |
| --- | --- | --- |
| REST | 简单、通用、便于调试 | 外部API、管理后台、普通工具调用 |
| RPC | 面向函数调用，内部效率较高 | 内部服务调用、任务调度 |
| gRPC | 强类型、HTTP/2、支持流式 | 模型服务、检索服务、跨语言后端 |
| WebSocket | 双向实时 | 前端实时交互、语音Agent、任务进度推送 |
| SSE | 单向流式输出简单 | LLM token流式返回 |

一个实际Agent链路可能是：前端用SSE接收token；后端用REST调用外部工具；内部用gRPC访问embedding和rerank服务；沙箱执行结果通过消息队列回传；状态写入数据库。

面试中要强调：协议选择要看调用边界、数据量、实时性、类型约束和可运维性。不是所有内部服务都需要gRPC，也不是所有实时体验都必须WebSocket。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L1385)，来源许可：GPL-3.0。

<a id="k215e8844346f"></a>

## Session与Cookie

**Cookie**：

​		Cookie是服务器发送到用户浏览器并保存在本地的一小块数据，它会在浏览器下次向同一服务器再发起请求时被携带并发送到服务器上。通常，它用于告知服务端两个请求是否来自同一浏览器，如保持用户的登录状态。Cookie 使基于无状态的 HTTP 协议记录稳定的状态信息成为了可能。

**Session**：

​		Session 代表着服务器和客户端一次会话的过程。Session 对象存储特定用户会话所需的属性及配置信息。这样，当用户在应用程序的 Web 页之间跳转时，存储在 Session 对象中的变量将不会丢失，而是在整个用户会话中一直存在下去。当客户端关闭会话，或者 Session 超时失效时会话结束。

**区别**：

* 作用范围不同，Cookie 保存在客户端（浏览器），Session 保存在服务器端；
* 存取方式不同，Cookie 只能保存 ASCII，Session 可以存任意数据类型；
* 有效期不同，Cookie 可设置为长时间保持，Session 一般失效时间较短，客户端关闭或者 Session 超时都会失效；
* 隐私策略不同，Cookie 存储在客户端，比较容易遭到不法获取，Session 存储在服务端，安全性相对 Cookie 要好一些；
* 存储大小不同， 单个 Cookie 保存的数据不能超过 4K，Session 可存储数据远高于 Cookie。

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/03-computer-basics/computer-network/network-protocols.md#L162)，来源许可：GPL-3.0。

<a id="kcb19cc51eaf4"></a>

## SSE 与 WebSocket 有什么区别？

SSE（Server-Sent Events）和 WebSocket 都是用来实现服务器向浏览器实时推送消息的技术，让网页内容能自动更新，而不需要用户手动刷新。虽然目标相似，但它们在工作方式和适用场景上有几个关键区别：

1. **通信方式:**
   - **SSE:** **单向通信**。只有服务器能向客户端（浏览器）发送数据。客户端不能通过同一个连接向服务器发送数据（需要发起新的 HTTP 请求）。
   - **WebSocket:** **双向通信（全双工）**。客户端和服务器可以随时互相发送消息，实现真正的实时交互。
2. **底层协议:**
   - **SSE:** 基于**标准的 HTTP/HTTPS 协议**。它本质上是一个“长连接”的 HTTP 请求，服务器保持连接打开并持续发送事件流。不需要特殊的服务器或协议支持，现有的 HTTP 基础设施就能用。
   - **WebSocket:** 使用**独立的 ws:// 或 wss:// 协议**。它需要通过一个特定的 HTTP "Upgrade" 请求来建立连接，并且服务器需要明确支持 WebSocket 协议来处理连接和消息帧。
3. **实现复杂度和成本:**
   - **SSE:** **实现相对简单**，主要在服务器端处理。浏览器端有标准的 EventSource API，使用方便。开发和维护成本较低。
   - **WebSocket:** **稍微复杂一些**。需要服务器端专门处理 WebSocket 连接和协议，客户端也需要使用 WebSocket API。如果需要考虑兼容性、心跳、重连等，开发成本会更高。
4. **断线重连:**
   - **SSE:** **浏览器原生支持**。EventSource API 提供了自动断线重连的机制。
   - **WebSocket:** **需要手动实现**。开发者需要自己编写逻辑来检测断线并进行重连尝试。
5. **数据类型:**
   - **SSE:** **主要设计用来传输文本**（UTF-8 编码）。如果需要传输二进制数据，需要先进行 Base64 等编码转换成文本。
   - **WebSocket:** **原生支持传输文本和二进制数据**，无需额外编码。

为了提供更好的用户体验和利用其简单、高效、基于标准 HTTP 的特性，**Server-Sent Events（SSE）是目前大型语言模型 API（如 OpenAI、DeepSeek 等）实现流式响应的常用甚至可以说是标准的技术选择**。

这里以 DeepSeek 为例，我们发送一个请求并打开浏览器控制台验证一下：

![DeepSeek 响应标头](https://oss.javaguide.cn/github/javaguide/cs-basics/network/deepseek-sse.png)

![DeepSeek SSE 响应使用 text/event-stream 持续传输事件](https://oss.javaguide.cn/github/javaguide/cs-basics/network/deepseek-sse-eventstream.png)

可以看到，响应头里包含了 `text/event-stream`，说明使用的确实是 SSE。并且，响应数据也确实是持续分块传输。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions.md#L463)，来源许可：Apache-2.0。

<a id="ke4c8d01c8996"></a>

## URI 和 URL 的区别是什么？

- URI（Uniform Resource Identifier）是统一资源标志符，可以唯一标识一个资源。
- URL（Uniform Resource Locator）是统一资源定位符，可以提供该资源的路径。它是一种具体的 URI，即 URL 可以用来标识一个资源，而且还指明了如何 locate 这个资源。

URI 的作用像身份证号一样，URL 的作用更像家庭住址一样。URL 是一种具体的 URI，它不仅唯一标识资源，而且还提供了定位该资源的信息。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions.md#L360)，来源许可：Apache-2.0。

<a id="k569abf74c39d"></a>

## WebSocket 和 HTTP 有什么区别？

WebSocket 和 HTTP 两者都是基于 TCP 的应用层协议，都可以在网络中传输数据。

下面是二者的主要区别：

- WebSocket 是一种双向实时通信协议，而 HTTP 是一种单向通信协议。并且，HTTP 协议下的通信只能由客户端发起，服务器无法主动通知客户端。
- WebSocket 使用 ws:// 或 wss://（使用 SSL/TLS 加密后的协议，类似于 HTTP 和 HTTPS 的关系）作为协议前缀，HTTP 使用 http:// 或 https:// 作为协议前缀。
- WebSocket 可以支持扩展，用户可以扩展协议，实现部分自定义的子协议，如支持压缩、加密等。
- WebSocket 通信数据格式比较轻量，用于协议控制的数据包头部相对较小，网络开销小，而 HTTP 通信每次都要携带完整的头部，网络开销较大（HTTP/2.0 使用二进制帧进行数据传输，还支持头部压缩，减少了网络开销）。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions.md#L406)，来源许可：Apache-2.0。

<a id="k861f09dcdaad"></a>

## WebSocket 的工作过程是什么样的？

WebSocket 的工作过程可以分为以下几个步骤：

1. 客户端向服务器发送一个 HTTP 请求，请求头中包含 `Upgrade: websocket` 和 `Sec-WebSocket-Key` 等字段，表示要求升级协议为 WebSocket；
2. 服务器收到这个请求后，会进行升级协议的操作，如果支持 WebSocket，它将回复一个 HTTP 101 状态码，响应头中包含 `Connection: Upgrade` 和 `Sec-WebSocket-Accept: xxx` 等字段，表示成功升级到 WebSocket 协议。
3. 客户端和服务器之间建立了一个 WebSocket 连接，可以进行双向的数据传输。数据以帧（frames）的形式进行传送，WebSocket 的每条消息可能会被切分成多个数据帧（最小单位）。发送端会将消息切割成多个帧发送给接收端，接收端接收消息帧，并将关联的帧重新组装成完整的消息。
4. 客户端或服务器可以主动发送一个关闭帧，表示要断开连接。另一方收到后，也会回复一个关闭帧，然后双方关闭 TCP 连接。

另外，建立 WebSocket 连接之后，通过心跳机制来保持 WebSocket 连接的稳定性和活跃性。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions.md#L417)，来源许可：Apache-2.0。

<a id="k646f1a568d60"></a>

## 为什么 HTTP/3 要做这个改变呢？主要有两大原因：

1. 解决队头阻塞（Head-of-Line Blocking，简写：HOL blocking）问题。
2. 减少连接建立的延迟。

下面我们来详细介绍这两大优化。

在 HTTP/2 中，虽然可以在一个 TCP 连接上并发传输多个请求/响应流（多路复用），但 TCP 本身的特性（保证有序、可靠）意味着如果其中一个流的某个 TCP 报文丢失或延迟，整个 TCP 连接都会被阻塞，等待该报文重传。这会导致所有在这个 TCP 连接上的 HTTP/2 流都受到影响，即使其他流的数据包已经到达。**QUIC（运行在 UDP 上）解决了这个问题**。QUIC 内部实现了自己的多路复用和流控制机制。不同的 HTTP 请求/响应流在 QUIC 层面是真正独立的。如果一个流的数据包丢失，它只会阻塞该流，而不会影响同一 QUIC 连接上的其他流（本质上是多路复用+轮询），大大提高了并发传输的效率。

除了解决队头阻塞问题，HTTP/3.0 还可以减少握手过程的延迟。在 HTTP/2.0 中，如果要建立一个安全的 HTTPS 连接，需要经过 TCP 三次握手和 TLS 握手：

RTT 指报文从一端到对端再返回的往返时间，不是单程传输时间。TCP 握手的延迟必须说明测量终点：客户端在发送 SYN 后约 1 RTT 收到 SYN-ACK，随后可以发送最终 ACK 和应用请求；服务器收到该 ACK 和请求还需要一个单程延迟。比较 HTTP/2 和 HTTP/3 时，应统一采用“客户端何时可以发送首个请求”或“客户端何时收到首字节”等同一个指标。

HTTP/2 的 HTTPS 连接需要先建立 TCP 连接，再完成 TLS 握手。HTTP/3 把传输参数协商和 TLS 1.3 握手结合在 QUIC 建连过程中。新的 QUIC 连接通常使用 1-RTT；0-RTT 只适用于客户端持有先前连接状态的恢复场景，可以在首个报文中携带早期数据，但存在重放风险，只适合可安全重放的请求。

相关证明可以参考下面这两个链接：

- <https://zh.wikipedia.org/zh/HTTP/3>
- <https://datatracker.ietf.org/doc/rfc9114/>

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions2.md#L90)，来源许可：Apache-2.0。

<a id="kd85ac99c8965"></a>

## 什么是 WebSocket?

WebSocket 是一种基于 TCP 连接的全双工通信协议，即客户端和服务器可以同时发送和接收数据。

WebSocket 协议在 2008 年诞生，2011 年成为国际标准，几乎所有主流较新版本的浏览器都支持该协议。不过，WebSocket 不只能在基于浏览器的应用程序中使用，很多编程语言、框架和服务器都提供了 WebSocket 支持。

WebSocket 协议本质上是应用层的协议，用于弥补 HTTP 协议在持久通信能力上的不足。客户端和服务器仅需一次握手，两者之间就直接可以创建持久性的连接，并进行双向数据传输。

![WebSocket 建立持久连接实现双向通信](https://oss.javaguide.cn/github/javaguide/system-design/web-real-time-message-push/1460000042192394.png)

下面是 WebSocket 的常见应用场景：

- 视频弹幕
- 实时消息推送，详见[Web 实时消息推送详解](https://javaguide.cn/system-design/web-real-time-message-push.html)这篇文章
- 实时游戏对战
- 多用户协同编辑
- 社交聊天
- ……

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions.md#L387)，来源许可：Apache-2.0。

<a id="k9c952df9619f"></a>

## 什么是SSL/TLS ？

SSL代表安全套接字层。它是一种用于加密和验证应用程序（如浏览器）和Web服务器之间发送的数据的协议。 身份验证 ， 加密Https的加密机制是一种共享密钥加密和公开密钥加密并用的混合加密机制。

SSL/TLS协议作用：认证用户和服务，加密数据，维护数据的完整性的应用层协议加密和解密需要两个不同的密钥，故被称为非对称加密；加密和解密都使用同一个密钥的

 对称加密：优点在于加密、解密效率通常比较高 ，HTTPS 是基于非对称加密的， 公钥是公开的，

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-01-net.md#L387)，来源许可：Apache-2.0。

<a id="k51149bbcce00"></a>

## 有了 HTTP，为什么还要 RPC？

HTTP 和 RPC 不是谁取代谁的关系，也不是谁更高级的问题。

HTTP 能调服务，RPC 也能调服务。真正的区别在于，你是想把远程调用当成一次“资源访问”，还是当成一次“方法调用”。

如果是对外接口，比如 Web、App、第三方系统接入，HTTP 通常更合适。它通用、好调试、接入成本低，别人拿 Postman、curl 就能测。  
如果是公司内部服务互调，尤其是服务多、调用链长、接口频繁调用，还要考虑服务发现、超时、重试、负载均衡、链路追踪这些问题，RPC 会更顺手一些。它不是单纯为了快，而是把内部服务调用里的很多麻烦事一起处理掉。

所以，别再简单背“HTTP 对外，RPC 对内”了。

这句话可以帮助入门，但真做项目时，还得看你的调用对象、团队基础设施、排查成本、性能要求和后续维护成本。

系统规模不大，用 HTTP 已经跑得很稳，就别为了“看起来更微服务”强上 RPC。

内部调用越来越复杂，HTTP SDK、网关、监控、重试这些东西越补越多，那就可以认真考虑 RPC。

一句话：**HTTP 没那么弱，RPC 也没那么神。选哪个，主要看它能不能用更低成本解决你现在的问题。**

详细介绍：[⭐️有了HTTP，为什么还要RPC？](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/http-vs-rpc.md)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/network/other-network-questions.md#L200)，来源许可：Apache-2.0。

<a id="kb53347c2cb27"></a>

## 浏览器内核中的有哪些线程？

内核主要分成五部分：

![内核](http://www.shadowingszy.top/images/browser.png)

GUI 渲染线程：负责渲染浏览器界面，解析 HTML，CSS，构建渲染树，布局和绘制等。当界面需要重绘或回流时，该线程就会执行。注意，GUI 渲染线程与 JS 引擎线程是互斥的，

JS 引擎线程：解析和执行 javascript。

事件触发线程：归属于浏览器而不是 JS 引擎，用来控制事件循环。

定时器触发线程：setInterval 与 setTimeout 所在线程。浏览器定时计数器并不是由 JavaScript 引擎计数的，因此通过单独线程来计时并触发定时（计时完毕后，添加到事件队列中，等待 JS 引擎空闲后执行）。

异步 http 请求线程：在 XMLHttpRequest 在连接后是通过浏览器新开一个线程请求，将检测到状态变更时，如果设置有回调函数，异步线程就产生状态变更事件，将这个回调再放入事件队列中，再由 JavaScript 引擎执行。

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/03-computer-basics/computer-network/http-protocol.md#L62)，来源许可：GPL-3.0。

<a id="k2eeb3c1c9b5f"></a>

## 计算机中http协议与ssh协议有哪些异同？

HTTP 和 SSH 协议是计算机网络中两种常见的协议，虽然它们有不同的应用场景，但在某些方面也有相似之处。HTTP 更专注于数据传输和信息展示，而 SSH 则强调安全性和远程控制。在实际应用中，选择使用哪种协议需要根据具体AI需求而定。如果追求快速、高效的数据传输，HTTP 是首选；如果需要安全的远程通信或文件传输，SSH 是不二之选。

### 三、HTTP 和 SSH 的相同点
1. **基于 TCP/IP 协议**：
   - 两者都工作在 TCP/IP 协议栈的应用层，依赖于 TCP 进行可靠的数据传输。

2. **跨平台**：
   - HTTP 和 SSH 协议都可以在多种操作系统上使用，并且都是应用广泛的标准协议。

3. **客户端-服务器架构**：
   - 两者都采用客户端与服务器的交互模式，例如：
     - HTTP：浏览器作为客户端向 Web 服务器发送请求。
     - SSH：本地计算机作为客户端远程连接到 SSH 服务器。

4. **扩展性**：
   - 两者都支持功能扩展。例如：
     - HTTP 支持通过 HTTP/2、HTTP/3 和扩展头实现功能增强。
     - SSH 支持多种附加功能，如文件传输（SCP/SFTP）和端口转发。

### 四、HTTP 和 SSH 的不同点

| **特性**          | **HTTP 协议**                                      | **SSH 协议**                                      |
|------------------|--------------------------------------------------|--------------------------------------------------|
| **主要用途**       | 传输超文本数据，主要用于网页浏览和前后端通信                     | 安全远程登录和管理服务器，提供安全的命令执行和数据传输        |
| **安全性**        | HTTP 是明文传输（除非通过 HTTPS 加密）                     | SSH 默认启用加密，确保数据传输的保密性和完整性              |
| **默认端口**       | 80（HTTP）或 443（HTTPS）                       | 22                                              |
| **状态管理**       | 无状态协议，通过外部机制（如 Cookie/Session）实现状态管理  | 基于会话的协议，会在整个会话期间保持连接状态                 |
| **认证机制**       | 一般无需身份认证，依赖于服务器开放的资源访问                    | 需要身份验证（基于密码或公钥的认证机制）                     |
| **通信方式**       | 请求-响应模式，客户端发起请求，服务器返回响应                    | 持续会话模式，客户端和服务器可以双向通信                   |
| **数据内容**       | 主要用于传输网页内容、文本数据和媒体文件                        | 主要用于命令交互、远程文件传输和加密隧道通信                |
| **典型工具**       | 浏览器（如 Chrome、Firefox）                        | SSH 客户端（如 OpenSSH、PuTTY）                   |
| **传输效率**       | 明文传输效率高，HTTPS 的加密可能稍慢，但对静态资源非常高效         | 数据加密增加了开销，但适合需要高安全性的通信场景              |

### 五、应用场景对比

1. **HTTP 应用场景**：
   - 访问网页内容：如浏览器请求网页、获取图片、播放视频等。
   - API 调用：前端与后端的数据通信。
   - 传输静态资源：如 HTML、CSS 和 JavaScript 文件。

2. **SSH 应用场景**：
   - 管理服务器：远程登录到服务器执行管理任务。
   - 传输文件：使用 SCP 或 SFTP 协议上传或下载文件。
   - 构建安全隧道：通过 SSH 隧道代理访问内部网络或加密不安全的通信。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L593)，来源许可：GPL-3.0。

<a id="k9066c7a0743c"></a>

## 说一下一次完整的HTTP请求过程包括哪些内容？

**常见问法：** 说一下一次完整的HTTP请求过程包括哪些内容？：第二种回答

### 第一种回答

- 建立起客户机和服务器连接。
- 建立连接后，客户机发送一个请求给服务器。
- 服务器收到请求给予响应信息。
- 客户端浏览器将返回的内容解析并呈现，断开连接。

### 第二种回答

域名解析 --> 发起TCP的3次握手 --> 建立TCP连接后发起http请求 --> 服务器响应http请求，浏览器得到html代码 --> 浏览器解析html代码，并请求html代码中的资源（如js、css、图片等） --> 浏览器对页面进行渲染呈现给用户。

<p  id="你知道第嗯斯是什么"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-01-net.md#L84)，来源许可：Apache-2.0。
- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/03-01-net.md#L93)，来源许可：Apache-2.0。

<a id="k52c4dcb980ad"></a>

## 请列举一下你知道的浏览器内核的种类？

Trident：IE6、IE7、IE8、IE9、IE10、360 浏览器和猎豹浏览器。
Gecko：firefox 浏览器。
Blink：opera 浏览器。
Webkit：sarfari 和 chrome 浏览器。

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/03-computer-basics/computer-network/http-protocol.md#L55)，来源许可：GPL-3.0。

<a id="kad308060dab1"></a>

## 请简述一下 HTTP 协议中的缓存策略？

HTTP 的缓存策略有两种：强缓存和协商缓存。

强缓存是利用 http 头中的 Expires 和 Cache-Control 两个字段来控制的，用来表示资源的缓存时间。强缓存中，普通刷新会忽略它，但不会清除它，需要强制刷新。

例如：
cache-control: max-age=691200 （HTTP 1.1）
expires: Fri, 14 Apr 2017 10:47:02 GMT （HTTP 1.0）

协商缓存主要涉及到两个 header 字段：E-Tag 和 Last-Modified。每次读取数据时客户单都会跟服务器通信，并且会增加缓存标识。在第一次请求服务器时，服务器会返回资源，并且返回一个资源的缓存标识，一起存到浏览器的缓存数据库。当第二次请求资源时，浏览器会首先将缓存标识发送给服务器，服务器拿到标识后判断标识是否匹配，如果不匹配，表示资源有更新，服务器会将新数据和新的缓存标识一起返回到浏览器；如果缓存标识匹配，表示资源没有更新，并且返回 304，浏览器就读取本地缓存服务器中的数据。

例如：
E-Tag: 123456abcd
Last-Modify: Thu,31 Dec 2037 23:59:59 GMT。

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/03-computer-basics/computer-network/http-protocol.md#L37)，来源许可：GPL-3.0。

<a id="kad17094c6ed2"></a>

## 请简述一下 HTTP 协议，以及 HTTP1.0/1.1/2.0/3.0 的区别？

HTTP 协议：超文本传输协议，使用 TCP/IP 协议传输数据。是一个应用层的协议。

HTTP1.0：HTTP 1.0 规定浏览器与服务器只保持短暂的连接，浏览器的每次请求都需要与服务器建立一个 TCP 连接，服务器完成请求处理后立即断开 TCP 连接，服务器不跟踪每个客户也不记录过去的请求。因此 HTTP 1.0 存在很大的性能缺陷——当访问一个包含有许多资源文件的网页时，每次请求和响应都需要建立一个单独的连接，每次连接只是传输一个文档和图像，请求之间完全分离。即使图像文件都很小，但是客户端和服务器端每次建立和关闭连接却是一个相对比较费时的过程，会严重影响到性能。

HTTP 1.1：支持长连接的 HTTP 协议，在一个 TCP 连接上可以传送多个 HTTP 请求和响应。一个包含有许多图像的网页文件的多个请求和应答可以在一个连接中传输，但每个单独的网页文件的请求和应答仍然需要使用各自的连接。

HTTP2.0：支持多路复用的 HTTP 协议。 HTTP 2.0 允许同时通过单一的 HTTP 2.0 连接发起多重的请求-响应消息。所有通信都在一个连接上完成，这个连接可以承载任意数量的双向数据流。由于 TCP 有慢启动的特点，如果 HTTP 连接很多，就会十分低效。HTTP/2 通过让所有数据流共用同一个连接，可以更有效地使用 TCP 连接。

HTTP3.0：也就是 QUIC (quick udp internet connection)协议，是由 google 提出的使用 udp 进行多路并发传输的协议。通过使用 UDP 协议，省去了 TCP 握手和慢启动的时间，拥有极低的建立连接延时。

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/03-computer-basics/computer-network/http-protocol.md#L5)，来源许可：GPL-3.0。

<a id="ke7061961d34a"></a>

## 请简述一下 HTTPS 协议？

HTTPS 在传输数据之前需要客户端与服务器之间进行一次握手，在握手过程中将确立双方加密传输数据的密码信息。TLS/SSL 协议不仅仅是一套加密传输的协议，TLS/SSL 中使用了非对称加密，对称加密以及 HASH 算法。

握手过程的简单描述如下：
1、客户端将自己支持的加密规则发送给服务器。

2、网站从中选出加密算法和 HASH 算法，将证书发回给浏览器。证书里面包含了网站地址，加密公钥，以及证书的颁发机构等信息。

3、获得证书之后客户端要做以下工作：
a) 验证证书（颁发证书的机构是否合法，证书中包含的网站地址是否与正在访问的地址一致等）。
b) 如果通过验证，浏览器会生成一串随机数的密码，并用证书中提供的公钥加密
c) 计算握手信息的 HASH，然后将握手信息也一并加密，最后将所有信息发送给网站。

4、网站接收浏览器发来的数据之后要做以下的操作：
a) 使用自己的私钥将信息解密取出密码，使用密码解密握手消息，判断 HASH 是否一致。
b) 计算握手的 HASH，并使用密码加密握手消息，发送给浏览器。

5、浏览器解密并计算握手消息的 HASH，如果与服务端发来的 HASH 一致，此时握手过程结束，之后所有的通信数据将由之前浏览器生成的随机密码进行加密。

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/03-computer-basics/computer-network/http-protocol.md#L17)，来源许可：GPL-3.0。

<a id="kf25b0c166b79"></a>

## 请简述一下浏览器的渲染流程？

![渲染流程](http://www.shadowingszy.top/images/render.png)

接收到文档后，渲染引擎会对 HTML 文档进行解析生成 DOM 树、对 CSS 文件进行解析生成布局树；同时执行页面中的 JavaScript 代码；最终根据 DOM 树和布局树，计算样式生成渲染树，渲染树中，只会包含即将显示在页面中的元素及其样式信息（如 head 元素、display 为 hidden 的元素就不会包含在渲染树中）；根据渲染树需要进行布局来计算每个元素在页面上的位置；

接下来渲染引擎开始进行绘制（paint），这一步分为若干阶段：
1、根据渲染树绘制每层的各个元素。
2、栅格化绘制出的图像（将渲染树中的节点转换成屏幕上的实际像素）
3、显示在屏幕上。
每一层的绘制是由浏览器来完成的；最后的合成是由 GPU 来完成；而栅格化过程取决于浏览器的设置，chrome 默认开启 GPU 栅格化，否则由 CPU 进行。

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/03-computer-basics/computer-network/http-protocol.md#L78)，来源许可：GPL-3.0。

<a id="k1af04de6f9b2"></a>

## 输入 www.baidu.com，怎么变成 https://www.baidu.com 的，怎么确定用HTTP还是HTTPS？


[你访问的网站是如何自动切换到 HTTPS 的？](https://www.sohu.com/a/136637876_487516)

一种是原始的302跳转，服务器把所有的HTTp流量跳转到HTTPS。但这样有一个漏洞，就是中间人可能在第一次访问站点的时候就劫持。
解决方法是引入HSTS机制，用户浏览器在访问站点的时候强制使用HTTPS。

### 参考资料

- [Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Computer%20Network.md#L279)，来源许可：GPL-3.0。

<a id="kf8351fe752fe"></a>

## 除了 sse 还知道哪些传输方式（websocket）

**回答：**

SSE 是服务端到客户端的单向长连接，基于 HTTP 文本事件流，浏览器原生支持自动重连，适合模型 Token 流式输出；WebSocket 是全双工长连接，适合双向实时交互，但需要自己处理心跳、重连、鉴权、背压和代理兼容。

其他选择包括普通 HTTP 轮询/长轮询、HTTP/2/gRPC streaming、WebTransport/QUIC，以及内部消息队列。选择要看通信方向、可靠性、代理环境、连接数量和消息语义，不应只按“实时”二字决定。

<a id="tencent-llm-collection-20260903-q57"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E8%85%BE%E8%AE%AF%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L919)，来源许可：GPL-3.0。
