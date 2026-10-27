# 文件系统与I-O

<a id="k14920e2227ad"></a>

## AI行业中如何降低计算机I/O开销？

### 2. **减少 I/O 开销的优化策略**

为了减少 AI 任务中的 I/O 开销，通常可以采用以下策略：

### 3. **I/O 开销在 AI 系统设计中的深远影响**

在 AI 系统设计中，I/O 开销对整个系统性能有着重要影响。在处理海量数据的任务（如自然语言处理、图像处理、视频分析）中，I/O 往往会成为系统性能的瓶颈。设计一个高效的 AI 系统时，必须综合考虑 I/O 开销，并通过缓存、并行数据加载、文件格式优化等方式减少这种开销。

随着模型和数据规模的增长，I/O 开销将越来越显著，特别是在大规模分布式系统中，网络 I/O 和存储 I/O 都可能限制系统的扩展性。因此，合理优化 I/O 是 AI 系统性能调优的关键步骤之一。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L1491)，来源许可：GPL-3.0。

<a id="kc8c079b46ca6"></a>

## Linux中有哪些常用的查看文件夹占用空间的命令？

在AIGC、传统深度学习、自动驾驶领域，我们经常需要进行大规模的数据整理与迁移等工作，所以掌握Linux系统中的不同文件夹的占用空间，对我们日常的工作能够降本增效。下面是Linux系统中常用的查看文件夹占用空间的命令：

在 Linux 中，有多种命令可以用来查看文件夹占用的空间。以下是几种常用的方法和工具：

### 1. `du`（Disk Usage）

`du` 是一个非常强大的命令，用于检查文件和目录的磁盘使用情况。它的基本用法和常见选项如下：

### 查看当前目录下的每个文件夹的大小

```bash
du -h --max-depth=1
```
- `-h`：以人类可读的格式显示（例如：K，M，G）。
- `--max-depth=1`：限制显示深度为1层，只显示当前目录下的文件夹大小。

### 查看特定目录下的每个文件夹的大小

```bash
du -h --max-depth=1 /path/to/directory
```

### 只显示总大小

```bash
du -sh /path/to/directory
```
- `-s`：只显示总计。

在 Ubuntu 系统中，你可以使用 `du`（disk usage）命令来查看每个文件夹占用的磁盘空间。以下是一些常见的方法和选项，可以帮助你获取所需的信息。

### 查看当前目录下的每个文件夹的大小

```bash
du -h --max-depth=1
```

- `-h`：以人类可读的格式显示（例如：K，M，G）。
- `--max-depth=1`：仅显示当前目录下的文件夹大小。

### 查看特定目录下的每个文件夹的大小

例如，要查看 `/var` 目录下每个文件夹的大小，可以使用：

```bash
du -h --max-depth=1 /var
```

### 查看所有子目录的大小

如果你想查看所有子目录的详细大小，可以省略 `--max-depth` 选项：

```bash
du -h /var
```

### 只显示总大小

如果你只想查看某个目录的总大小，可以使用 `-s` 选项：

```bash
du -sh /var
```

### 结合 `sort` 命令查看占用空间最大的文件夹

我们可以结合 `sort` 命令查看占用空间最大的文件夹：

```bash
du -h --max-depth=1 /home | sort -hr
```

- `sort -hr`：根据大小进行降序排序。

### 示例解释

假设我们在 `/home` 目录下运行 `du -h --max-depth=1`，输出可能如下所示：

```bash
4.0K    ./WeThinkIn
16K     ./Documents
3.1G    ./Downloads
8.0K    ./Music
24K     ./Pictures
5.2M    ./Videos
3.2G    .
```

这里每一行表示每个子目录的大小，最后一行 `3.2G .` 表示当前目录（即 `/home` 目录）的总大小。

### 2. `ncdu`（NCurses Disk Usage）

`ncdu` 是一个基于文本的磁盘使用分析工具，提供了交互式的界面。

### 安装 `ncdu`

```bash
sudo apt install ncdu  # 对于Debian/Ubuntu
sudo yum install ncdu  # 对于RHEL/CentOS
```

### 使用 `ncdu`

```bash
ncdu /path/to/directory
```

### 3. `df`（Disk Free）

虽然 `df` 主要用于显示文件系统的总的磁盘空间使用情况，但也可以用来查看特定挂载点的使用情况。

### 查看所有文件系统的使用情况

```bash
df -h
```
- `-h`：以人类可读的格式显示。

### 查看特定目录的文件系统使用情况

```bash
df -h /path/to/directory
```

### 4. `duf`（Disk Usage/Free Utility）

`duf` 是一个现代的磁盘使用情况查看工具，具有彩色输出和交互式界面。

### 安装 `duf`

```bash
sudo apt install duf  # 对于Debian/Ubuntu
sudo yum install duf  # 对于RHEL/CentOS
```

### 使用 `duf`

```bash
duf
```

### 5. `ls` 和 `find` 配合使用

通过组合 `ls` 和 `find` 命令，可以获取每个文件夹和文件的大小。

### 查看当前目录下所有文件和文件夹的大小

```bash
find . -type f -exec ls -lh {} + | awk '{print $9 ": " $5}'
```

### 6. `tree` 命令

`tree` 可以以树状结构显示目录内容，并提供每个文件和目录的大小。

### 安装 `tree`

```bash
sudo apt install tree  # 对于Debian/Ubuntu
sudo yum install tree  # 对于RHEL/CentOS
```

### 使用 `tree`

```bash
tree -h /path/to/directory
```
- `-h`：以人类可读的格式显示大小。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L596)，来源许可：GPL-3.0。

<a id="k5a9afb1c1efa"></a>

## open 一个文件时发生了什么？

`open()` 不会把整个文件读进内存，它主要做路径解析和打开对象创建。

![路径到文件描述符](https://oss.javaguide.cn/github/javaguide/cs-basics/operating-system/file-path-to-fd.webp)

大致流程是：

1. 从根目录或当前目录开始解析路径，逐级查目录项和 dentry 缓存。
2. 找到目标 inode 后，检查权限、打开标志和文件类型。
3. 创建内核里的打开文件对象，记录当前文件偏移量、打开状态、读写标志等。
4. 在当前进程的文件描述符表里分配一个最小可用的非负整数，也就是 fd。

fd 是进程文件描述符表里的索引，不是 inode。`dup()`、`fork()` 之后，多个 fd 可能引用同一个打开文件对象，所以它们共享文件偏移量；两个进程分别 `open()` 同一个文件，通常会得到不同的打开文件对象，各自维护偏移量。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/operating-system/operating-system-basic-questions-02.md#L547)，来源许可：Apache-2.0。

<a id="k190c7cc185a5"></a>

## Reactor、Proactor、epoll LT/ET在高并发AI服务中如何理解？

Reactor和Proactor都是高并发网络服务模型，区别在于“谁负责真正执行IO”。

| 模型 | 核心思想 | 典型理解 |
| --- | --- | --- |
| Reactor | 内核通知“可以读/写”，应用自己执行读写 | 同步非阻塞IO + 事件分发 |
| Proactor | 应用提交异步IO，内核完成后通知结果 | 真正异步IO + 完成事件 |

Reactor常见流程：

1. 服务端把socket注册到事件循环。
2. `epoll_wait` 等待连接、读、写事件。
3. 有事件后分发给handler。
4. handler执行读写、解析请求、投递任务到线程池。

Proactor常见流程：

1. 应用提交异步读写请求。
2. 内核或运行时完成IO。
3. 应用收到完成通知并处理结果。

`epoll` 的 LT/ET 是两个触发模式：

| 模式 | 含义 | 特点 |
| --- | --- | --- |
| LT | Level Trigger，水平触发 | 只要fd仍可读/可写，就会反复通知，编程更稳 |
| ET | Edge Trigger，边缘触发 | 状态变化时通知一次，效率高，但必须一次读到 `EAGAIN` |

AI服务中的实践建议：

1. 普通HTTP服务和管理接口，LT模式更稳。
2. 高并发长连接、流式token返回，可以使用ET模式提升效率，但必须配合非阻塞fd和完整读写循环。
3. 网络线程不要执行耗时推理，应把请求投递到调度队列，由GPU worker处理。
4. 流式输出要处理客户端慢读和断开连接，否则会堆积缓冲并浪费GPU计算。

面试金句：Reactor解决的是“连接多但多数在等待”的问题，GPU推理解决的是“计算重”的问题。高并发AI服务要把IO事件循环、CPU线程池和GPU worker边界拆清楚。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L3179)，来源许可：GPL-3.0。

<a id="k64d80842ecf9"></a>

## select、poll、epoll和io_uring有什么区别？

这些都是Linux下处理高并发IO的重要机制：

| 机制 | 特点 | 局限 |
| --- | --- | --- |
| `select` | 跨平台、接口简单 | fd数量受限，需要每次复制和扫描集合 |
| `poll` | 无固定fd上限 | 仍需线性扫描，连接很多时效率低 |
| `epoll` | 事件驱动，适合大量连接 | 主要处理网络IO就绪通知 |
| `io_uring` | 异步提交/完成队列，减少系统调用开销 | 编程复杂，对内核版本和场景有要求 |

在AIGC服务中，`epoll`适合大量HTTP/WebSocket/SSE连接，例如流式token返回；`io_uring`更适合高性能文件和网络异步IO，例如大规模数据加载、日志写入或代理转发。

面试中可以这样总结：`select/poll`是早期多路复用，`epoll`是高并发网络服务主力，`io_uring`进一步把异步IO做成提交队列和完成队列，减少阻塞和系统调用成本。但是否使用 `io_uring` 要看团队复杂度承受能力，不是所有服务都值得引入。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L3103)，来源许可：GPL-3.0。

<a id="kcc132827f94e"></a>

## 什么是 I/O 多路复用？

I/O 多路复用解决的不是“单次读写更快”，而是**一个线程如何同时等待多个文件描述符（fd）的就绪事件**。

一次网络读取通常分成两个阶段：先等数据从网卡到达并进入内核缓冲区，再把数据从内核缓冲区拷贝到用户缓冲区。阻塞 I/O 的问题在第一阶段：一个线程调用 `recv` 后，如果这个连接没数据，线程就只能卡在那里等。

![网络读取中的两个阶段：先等待网卡数据进入内核缓冲区，再通过 copy_to_user 拷贝到用户缓冲区](https://oss.javaguide.cn/github/javaguide/cs-basics/operating-system/io-multiplexing-io-two-phases.png)

I/O 多路复用把一批 fd 交给内核，让线程阻塞在 `select`、`poll` 或 `epoll` 这类系统调用上。只要其中任意 fd 就绪，调用就返回，应用再去处理对应的连接。这样一个线程就能管理成千上万个连接，特别适合大量连接空闲、少量连接活跃的场景，比如 Redis、Nginx、Netty 这类高性能网络程序。

需要注意：I/O 多路复用仍然属于**同步 I/O**。内核只是通知“可以读/可以写了”，真正的 `read`/`recv` 还得应用自己调用，数据从内核缓冲区拷到用户缓冲区这一步并没有被省掉。

详细介绍：[I/O 多路复用详解：select、poll、epoll 原理与区别](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/operating-system/io-multiplexing.md)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/operating-system/operating-system-basic-questions-02.md#L449)，来源许可：Apache-2.0。

<a id="kc96c8023d037"></a>

## 什么是 I/O 开销？

在计算机科学中，**I/O 开销**（Input/Output Overhead）指的是在执行数据传输时，系统为**输入（Input）**和**输出（Output）**操作所消耗的资源和时间。I/O 操作包括**从存储设备读取数据**（如硬盘、SSD）或**将数据写入存储设备**，以及与其他外部设备（如网络、显卡、外部硬件）之间的通信。在AI行业中，I/O开销主要涉及在AI模型的训练和推理时，从磁盘读取数据、从内存到GPU的传输，以及将结果输出到存储设备或网络。

**由于 I/O 操作通常比内存操作或 CPU、GPU 上的计算速度慢得多，因此 I/O 开销往往成为系统的性能瓶颈**，尤其在需要处理大量数据的任务中，例如AI模型的训练和推理。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L1454)，来源许可：GPL-3.0。

<a id="k7358185ec52a"></a>

## 介绍一下Linux中修改文件权限的命令

### **一、Linux 文件权限修改命令详解**
### **1. 核心命令**
- **`chmod`**（修改权限）  
  - **符号模式**：`u/g/o/a`（用户/组/其他/全部） + `+/-/=`（添加/移除/设置） + `r/w/x`（读/写/执行）  
    示例：`chmod u+x script.sh`（赋予所有者执行权限）  
  - **数字模式**：三位八进制数（如 `755`），分别代表 **所有者、组、其他用户** 的权限组合（r=4, w=2, x=1）。  
    示例：`chmod 755 model.pth` → 所有者 `rwx`，组和其他用户 `r-x`。

- **`chown`**（修改所有者/组）  
  示例：`chown alice:ai_team model.log`（将文件所有者和组改为 `alice` 和 `ai_team`）。

- **`chgrp`**（仅修改组）  
  示例：`chgrp researchers data/`（将目录所属组设为 `researchers`）。

### **2. 实际案例：团队协作中的权限管理**
**场景**：  
某 AI 团队需要共享训练脚本和数据集，但需确保：  
- **脚本**（如 `train.py`）：仅所有者可修改，其他成员可读可执行。  
- **数据集**（如 `dataset/`）：组成员可读写，其他用户无权限。  
- **日志**（如 `logs/`）：所有成员可读，但仅运维组可删除。

**操作**：  
```bash
# 1. 脚本权限：rwxr-xr-x（所有者可执行，其他用户只读和执行）
chmod 755 train.py

# 2. 数据集目录：组可读写，其他用户无权限（rwxrwx---）
chmod 770 dataset/
chgrp ai_team dataset/

# 3. 日志目录：组成员可读写，其他用户只读，并设置 Sticky Bit（仅所有者可删除文件）
chmod 1774 logs/
```

### **二、在 AI 领域中的实际应用**
### **1. AIGC（生成式 AI）场景**
- **应用背景**：  
  多团队协作开发扩散模型（如 Stable Diffusion），需隔离不同角色的权限：  
  - **算法工程师**：可修改模型训练脚本（`chmod 750 train.py`）。  
  - **数据工程师**：仅能读写训练数据目录（`chgrp data_team /data/images`）。  
  - **运维人员**：管理推理服务日志（`chmod 640 inference.log`）。

- **意义**：  
  防止误删或篡改关键模型文件，保障生成结果的一致性（如保护预训练权重文件权限为 `600`）。

### **2. 传统深度学习场景**
- **应用背景**：  
  分布式训练集群中，权限管理用于：  
  - **训练脚本**：确保仅调度节点可执行（`chmod +x distributed_train.sh`）。  
  - **共享存储**：组内成员可读写中间结果（`chmod 775 /shared_results`）。  
  - **敏感数据**：限制非授权用户访问标注数据（`chmod 600 labels.txt`）。

- **意义**：  
  避免训练任务因权限冲突中断（如权限错误导致数据加载失败），同时保护标注数据隐私。

### **3. 自动驾驶场景**
- **应用背景**：  
  车端-云端协同系统中，权限控制用于：  
  - **传感器数据**：仅车载系统用户可读写（`chown caros:caros /sensor_data`）。  
  - **实时日志**：设置 Sticky Bit 防止日志被非特权进程删除（`chmod +t /var/log/autodrive`）。  
  - **OTA 更新包**：仅校验通过后赋予执行权限（`chmod 744 update.bin`）。

- **意义**：  
  确保行车关键数据的安全性（如防止恶意篡改高精地图权限），同时满足车规级系统的实时性要求。

### **三、面试回答技巧**
1. **强调系统思维**：  
   “权限管理是 AI 工程化的基础设施，直接影响团队协作效率和系统安全性。例如在自动驾驶中，权限错误可能导致传感器数据泄漏或 OTA 升级失败。”

2. **结合调试经验**：  
   “我曾遇到因 `Permission Denied` 导致训练任务卡死的问题，最终通过 `chmod` 修复数据集目录权限，并添加 `set -e` 和错误日志监控。”

3. **延伸扩展**：  
   - **特殊权限**：如 `SUID` 用于部署工具链（如 Docker 容器内的权限继承）。  
   - **ACL 高级控制**：复杂场景下使用 `setfacl` 精细化授权。  
   - **安全合规**：符合 GDPR/ISO 27001 的数据访问权限设计。

通过将 Linux 权限命令与 AI 行业场景结合，既能展示技术深度，又能体现工程化思维，这正是算法岗面试中脱颖而出的关键！

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L2044)，来源许可：GPL-3.0。

<a id="k0ae453d3bd1d"></a>

## 多文件查看

- **查看多个文件的尾部**：可以同时查看多个文件的尾部，`tail` 会在输出中显示文件名作为标识。
```bash
  tail -n 20 /path/to/your/file1 /path/to/your/file2
```

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L554)，来源许可：GPL-3.0。

<a id="k47fa7ed22681"></a>

## 如何消除碎片文件

对于外部碎片，通过**紧凑技术**消除，就是操作系统不时地对进程进行移动和整理。但是这需要动态重定位寄存器地支持，且相对费时。紧凑地过程实际上类似于Windows系统中地磁盘整理程序，只不过后者是对外存空间地紧凑

解决外部内存碎片的问题就是**内存交换**。

可以把音乐程序占用的那 256MB 内存写到硬盘上，然后再从硬盘上读回来到内存里。不过再读回的时候，我们不能装载回原来的位置，而是紧紧跟着那已经被占用了的 512MB 内存后面。这样就能空缺出连续的 256MB 空间，于是新的 200MB 程序就可以装载进来。

回收内存时要尽可能地将相邻的空闲空间合并。

<p  id="冯诺依曼结构有哪几个模块分别对应现代计算机的哪几个部分百度安全一面"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/02-04-os.md#L72)，来源许可：Apache-2.0。

<a id="k586c6d1f3f1c"></a>

## 实时监控文件（AI行业高价值命令）

- **持续跟踪文件更新**：使用 `-f` 选项，`tail` 会显示文件的最后几行并在文件有新内容追加时，实时显示新增内容。这对于监控实时日志非常有用。
```bash
  tail -f /path/to/your/file
```

- **结合 `-n` 和 `-f`**：可以结合 `-n` 和 `-f` 选项，先显示文件的最后几行并持续跟踪文件更新。
```bash
  tail -n 20 -f /path/to/your/file
```

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L542)，来源许可：GPL-3.0。

<a id="k5799506d5e63"></a>

## 持续监控文件变化并进行高级操作

- **附加模式**：使用 `--follow` 选项的 `name` 参数，可以在文件重命名或旋转（如日志文件轮转）后继续跟踪。
```bash
  tail --follow=name /path/to/your/file
```

- **与其他命令结合使用**：结合管道和其他命令进行更复杂的操作。例如，过滤实时日志输出中的某些关键字：
```bash
  tail -f /path/to/your/file | grep "keyword"
```

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L568)，来源许可：GPL-3.0。

<a id="k8f5c99db1739"></a>

## 按文件名搜索

```bash
# 按名称精确匹配
find /path/to/start -name "filename"
# 按名称模糊匹配（大小写敏感）
find /path/to/start -name "*.txt"
# 按名称模糊匹配（大小写不敏感）
find /path/to/start -iname "*.txt"
```

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L382)，来源许可：GPL-3.0。

<a id="k21d0d4b7185b"></a>

## 按文件大小搜索

```bash
# 查找大于 100MB 的文件
find /path/to/start -size +100M
# 查找小于 10KB 的文件
find /path/to/start -size -10k
# 查找正好 1GB 的文件
find /path/to/start -size 1G
```

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L402)，来源许可：GPL-3.0。

<a id="k11f7e59906b5"></a>

## 按文件时间搜索

```bash
# 查找在最近 7 天内修改的文件
find /path/to/start -mtime -7
# 查找在最近 30 分钟内修改的文件
find /path/to/start -mmin -30
# 查找在最近 7 天内访问的文件
find /path/to/start -atime -7
# 查找在最近 30 分钟内访问的文件
find /path/to/start -amin -30
```

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L412)，来源许可：GPL-3.0。

<a id="k8ab56216f2d5"></a>

## 按文件类型搜索

```bash
# 查找目录
find /path/to/start -type d
# 查找普通文件
find /path/to/start -type f
# 查找符号链接
find /path/to/start -type l
```

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L392)，来源许可：GPL-3.0。

<a id="kbfabbc94e4ff"></a>

## 提高文件系统性能的方式有哪些？

可以从访问模式、缓存、元数据和硬件几方面答：

- **尽量顺序读写**：顺序 I/O 更容易被预读、合并写和 extent 这类连续空间映射利用。
- **利用 Page Cache**：普通文件读写会经过 Page Cache，命中时可以少访问磁盘；但缓存不是越大越好，还要看内存压力和回写压力。
- **减少小文件和元数据操作**：大量小文件会放大 inode、目录项、权限检查、创建删除等元数据成本。
- **控制刷盘频率**：频繁 `fsync()` 会降低吞吐，但完全不刷盘又会扩大掉电丢数据窗口，需要按业务持久性要求取舍。
- **选择合适的文件系统和挂载参数**：ext4、XFS、Btrfs 等实现不同，日志模式、atime、barrier 等参数也会影响性能和可靠性。
- **使用更合适的硬件**：SSD、NVMe、RAID、磁盘缓存策略都会影响读写延迟和吞吐。

排查时常看这些命令：

```bash
df -h
df -i
lsof +L1
iostat -x 1
```

`df` 很满但 `du` 找不到大文件时，优先查被删除但仍被进程打开的文件；小文件特别多时，`df -i` 可能比 `df -h` 更早暴露问题。

详细介绍：[操作系统文件系统详解：inode、VFS、Page Cache 与日志机制](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/operating-system/file-system.md)

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/operating-system/operating-system-basic-questions-02.md#L639)，来源许可：Apache-2.0。

<a id="k26a654ac2c8b"></a>

## 文件在磁盘上怎么存放？

文件系统会把一个分区或卷划分成很多块，再用元数据记录文件内容和块之间的关系。教材里常见三种分配方式：

![文件数据块定位方式](https://oss.javaguide.cn/github/javaguide/cs-basics/operating-system/file-block-allocation.webp)

- **连续分配**：文件占用一段连续块，顺序读写和随机访问都快；缺点是文件增长麻烦，容易产生外部碎片。
- **链式分配**：每个块指向下一个块，不要求连续空间；缺点是随机访问差。
- **索引分配**：把数据块地址集中放在索引块中，随机访问更方便；缺点是需要额外索引空间。

经典 ext2/ext3 使用直接块指针、一级间接、二级间接和三级间接块定位文件数据。ext4 通常使用 extent tree，一个 extent 记录一段连续物理块的逻辑起点、物理起点和长度；对连续大文件来说，它比“每个块记录一个地址”更省元数据。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/operating-system/operating-system-basic-questions-02.md#L562)，来源许可：Apache-2.0。

<a id="kbf725a74df4a"></a>

## 文件系统主要做了什么？

文件系统负责把存储设备上的块组织成应用能理解的文件和目录。面试里可以从这 6 件事回答：

![文件系统职责概览](https://oss.javaguide.cn/github/javaguide/cs-basics/operating-system/file-system-responsibilities.webp)

1. **命名**：用路径和文件名找到目标文件，例如 `/var/log/app.log`。
2. **组织**：用目录树管理文件和目录，让不同文件有清晰层次。
3. **定位**：把文件的第 N 个字节映射到底层数据块。
4. **空间管理**：分配、释放和复用磁盘块，记录哪些块空闲、哪些块已使用。
5. **权限保护**：记录所有者、权限、时间戳等元数据，并在访问时做检查。
6. **缓存和恢复**：用 Page Cache 提升读写性能，用日志机制减少崩溃后的文件系统结构损坏。

不是所有文件系统都对应本地磁盘。`tmpfs` 主要以内存作为后端，`procfs` 暴露内核运行状态，NFS 则把远端文件系统接入本地目录树。Linux 通过 VFS 给这些文件系统提供统一接口。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/operating-system/operating-system-basic-questions-02.md#L511)，来源许可：Apache-2.0。

<a id="k7d80907e7962"></a>

## 日志文件系统解决了什么问题？

文件系统一次操作常常要改多处元数据。比如创建文件时，要分配 inode、分配数据块、更新目录项、更新位图。机器在中途断电，文件系统可能停在不一致状态。

日志文件系统会先把即将进行的元数据变更写入日志区域，再更新正式位置。系统恢复时扫描日志，已经完整提交但还没写回正式位置的事务可以重放，没有完整提交的事务会被丢弃。

以 ext4 为例，常见数据模式有三种：

| 模式             | 说明                                                   |
| ---------------- | ------------------------------------------------------ |
| `data=writeback` | 只保证元数据日志，不保证相关数据块先于元数据写入       |
| `data=ordered`   | 默认模式，元数据进日志前，相关数据块会先写到主文件系统 |
| `data=journal`   | 数据和元数据都先写日志，再写最终位置，写放大更明显     |

日志文件系统主要保证文件系统结构一致性，不等于帮应用保证所有业务数据都不丢。事务级持久性仍然要靠应用正确使用 `fsync()`、写入顺序和恢复逻辑。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/operating-system/operating-system-basic-questions-02.md#L623)，来源许可：Apache-2.0。

<a id="ke07ddba2486c"></a>

## 硬链接为什么不能跨文件系统？

硬链接指向的是 inode，而 inode 号只在当前文件系统内有意义。每个文件系统都有自己的 inode 表，另一个文件系统里的同一个 inode 号不代表同一个文件。

软链接保存的是路径字符串，解析时按路径重新查找目标文件，所以可以跨文件系统。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/operating-system/operating-system-basic-questions-02.md#L600)，来源许可：Apache-2.0。
