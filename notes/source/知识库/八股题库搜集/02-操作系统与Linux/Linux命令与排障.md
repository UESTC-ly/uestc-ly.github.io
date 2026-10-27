# Linux命令与排障

<a id="ke2f4bd523573"></a>

## Clash Verge Rev 的本质架构是什么？GUI、mihomo 内核、代理节点分别负责什么？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

### 核心判断

Clash Verge Rev 不是“VPN 协议”本身，也不是一个能够凭空改变网络的按钮。它本质上是一个基于 Tauri 的桌面控制界面，负责配置管理、状态展示、系统集成和生命周期管理；真正处理连接、DNS、规则与出站选择的是其内置的 mihomo 内核；真正把流量转发到目标网络的，通常是远端代理节点。

因此，这类客户端最好拆成三层理解：

1. **控制面**：GUI、订阅、配置合并、策略切换、日志与 REST API。它决定“希望系统怎样工作”。
2. **数据面**：本地 mihomo 内核监听代理端口或虚拟网卡，解析入站连接，执行 DNS 与规则匹配，再建立相应出站连接。它决定“每一个包或连接实际怎样走”。
3. **传输与出口面**：直连互联网，或使用 Shadowsocks、Trojan、VMess、VLESS、Hysteria、TUIC 等协议与远端节点通信。它决定“最终从哪个网络出口到达目标”。

下图把这三层放进同一条因果链。控制面只下发意图，数据面才处理流量；规则结果可以是 `DIRECT`、`REJECT` 或某个代理组，并不是所有请求都会经过同一个远端节点。

![Clash Verge Rev 与 mihomo 本地规则代理架构](https://raw.githubusercontent.com/WeThinkIn/AIGC-Interview-Book/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/imgs/clash-verge-proxy-architecture.png)

### 一条 HTTPS 请求实际经历了什么

以 Git 访问 GitHub 为例，一条典型链路可以抽象为：

```text
Git 进程
  -> 本地 HTTP/SOCKS 代理端口，或被 TUN 虚拟网卡接管
  -> mihomo 获取目标域名、IP、端口、进程等上下文
  -> DNS 与规则引擎决定 DIRECT / REJECT / 代理组
  -> 选择具体远端节点并建立出站连接
  -> 目标 GitHub 服务
  -> 响应沿连接反向返回
```

这里至少存在两条 TCP 连接：应用到本地代理的连接，以及本地内核到目标或远端节点的连接。使用远端节点时，还可能叠加一个代理协议的加密会话。把它错误地看成一条“端到端直连”，就很难解释为什么本地端口、规则、节点和目标站会分别产生不同错误。

### 跨周期价值

Clash Verge 的界面和版本会变化，但“控制面与数据面分离、入站接管、策略决策、出站转发、可观测性”这套框架不会轻易过时。它同样适用于服务网格、API Gateway、零信任访问代理、云网络网关和 Agent 出站沙箱。

**面试中可以用一句话收束：Clash Verge 是控制面，mihomo 是本地数据面，代理节点是远端转发面；代理的本质不是换一个 IP，而是对连接建立、策略选择与出口路径进行重新编排。**

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E4%BB%A3%E7%90%86%E3%80%81%E9%9A%A7%E9%81%93%E4%B8%8EVPN%E6%9C%AC%E8%B4%A8%E5%8E%9F%E7%90%86%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L17)，来源许可：GPL-3.0。

<a id="kdc88c0ea3c93"></a>

## CPU和GPU的区别？

CPU（中央处理单元）和GPU（图形处理单元）是计算机系统中两种非常重要的处理器，它们在设计、功能和使用场景上有明显的区别：

1. **基本功能和设计**：
   - **CPU**：设计为通用处理器，优化用于执行复杂的逻辑和控制任务。CPU通常有较少的核心（通常在4到32核之间），但每个核心的功能强大，能够处理多种类型的计算任务。
   - **GPU**：最初设计用于处理计算机图形和图像处理任务。GPU包含成百上千个小核心，这些核心能够并行处理大量相似的计算任务，非常适合于执行大规模的数值计算，如图形渲染或科学计算。

2. **性能和并行处理**：
   - **CPU**：强调每个核心的性能，更适合执行顺序指令和处理需要复杂决策和数据依赖性的任务。CPU更适合执行需要快速、复杂决策的应用程序，如运行操作系统、办公软件等。
   - **GPU**：设计用于同时执行大量比较简单的计算任务，非常适合于并行处理。因此，GPU在进行视频编辑、3D渲染、深度学习和大规模科学计算等任务时表现出较高的效率。

3. **应用场景**：
   - **CPU**：几乎出现在所有类型的计算设备中，是执行程序的主要硬件。它处理输入输出、系统管理、复杂运算以及与其他设备的通信等任务。
   - **GPU**：虽然最初主要用于图形相关的处理，但现在广泛用于科学计算、机器学习、大数据分析等领域，特别是在需要处理大量数据的并行计算中。

4. **发展趋势**：
   - **CPU**：近年来，CPU也在增加核心数，引入更高级的多任务处理和虚拟化技术，以提高性能和能效。
   - **GPU**：随着AIGC、传统深度学习、自动驾驶的持续发展，GPU的重要性日益增加，GPU制造商也在不断推出针对这些领域优化的产品。

总的来说，CPU更擅长处理需要较高逻辑复杂性和任务多样性的计算任务，而GPU则优于处理可大规模并行化的计算密集型任务。在现代计算系统中，CPU和GPU往往协同工作，提供更高效、更强大的计算能力。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L499)，来源许可：GPL-3.0。

<a id="k732377013d80"></a>

## Linux

linux下非编译器决定栈大小，而是由操作系统环境决定，默认是8192KB（8M）；而在Windows平台下栈的大小是被记录在可执行文件中的（由编译器来设置)，即：windows下可以由编译器决定栈大小，而在Linux下是由系统环境变量来控制栈的大小的。

 在Linux下通过如下命令可查看和设置栈的大小：

```shell
$ ulimit -a            # 显示当前栈的大小 （ulimit为系统命令，非编译器命令）       
$ ulimit -s 32768      # 设置当前栈的大小为32M
```

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/02-03-os.md#L93)，来源许可：Apache-2.0。

<a id="k785392b79c74"></a>

## Linux中修改用户权限的命令有哪些？

在Linux系统中，用户权限是保证系统安全和稳定运行的关键因素。正确理解和使用权限管理命令，可以有效地控制用户对系统资源的访问。通过`chmod`、`chown`、`usermod`等命令，可以精确地控制用户和组对文件、目录的访问权限。理解并正确使用这些命令，有助于维护系统的安全和稳定。

### 一、文件权限概述

在Linux系统中，每个文件和目录都有一组权限，定义了所有者（Owner）、所属组（Group）和其他用户（Others）对该文件或目录的访问权限。这些权限分为：

- **读（r）**：允许查看文件内容或列出目录内容。
- **写（w）**：允许修改文件内容或在目录中创建、删除文件。
- **执行（x）**：允许执行文件或进入目录。

权限可以通过两种方式表示：

- **符号表示法**：使用`r`、`w`、`x`字符表示权限。
- **数字表示法**：使用八进制数字表示权限，例如`7`表示`rwx`。

### 1. 基本用法

`chmod`命令用于改变文件或目录的权限。

```bash
chmod [选项] 模式 文件名
```

### 2. 符号表示法修改权限

使用符号表示法，可以针对所有者、所属组和其他用户分别修改权限。

- **符号说明**：
  - `u`：文件所有者（user）
  - `g`：文件所属组（group）
  - `o`：其他用户（others）
  - `a`：所有用户（all，等同于`ugo`）
- **操作符**：
  - `+`：添加权限
  - `-`：移除权限
  - `=`：设置权限

**示例**：

```bash
# 给文件 owner.txt 的所有者添加执行权限
chmod u+x owner.txt

# 移除文件 group.txt 的所属组的写权限
chmod g-w group.txt

# 设置文件 all.txt 的所有用户权限为读和执行
chmod a=rx all.txt
```

### 3. 数字表示法修改权限

数字表示法使用三位八进制数字，每位数字对应所有者、所属组和其他用户的权限。

- 权限数值对应：
  - `r`：4
  - `w`：2
  - `x`：1

```bash
# 将文件 example.txt 的权限设置为所有者读写，所属组读，其他用户无权限
chmod 640 example.txt

# 将目录 mydir 的权限设置为所有用户可读写执行
chmod 777 mydir
```

### 1. 修改文件所有者：`chown`

`chown`命令用于改变文件或目录的所有者。

```bash
chown [选项] 新所有者 文件名
```

```bash
# 将文件 example.txt 的所有者改为 user1
sudo chown user1 example.txt

# 递归修改目录 mydir 下所有文件的所有者为 user2
sudo chown -R user2 mydir
```

### 2. 修改文件所属组：`chgrp`

`chgrp`命令用于改变文件或目录的所属组。

```bash
chgrp [选项] 新组 文件名
```

```bash
# 将文件 example.txt 的所属组改为 group1
sudo chgrp group1 example.txt

# 递归修改目录 mydir 下所有文件的所属组为 group2
sudo chgrp -R group2 mydir
```

### 3. 同时修改所有者和所属组：`chown` 的组合用法

```bash
chown [新所有者][:新组] 文件名
```

```bash
# 将文件 example.txt 的所有者改为 user1，所属组改为 group1
sudo chown user1:group1 example.txt

# 仅修改所属组
sudo chown :group2 example.txt
```

### 1. 修改用户所属组：`usermod`

`usermod`命令用于修改用户账户属性，包括所属组、登录权限等。

### 添加用户到附加组

```bash
sudo usermod -aG 组名 用户名
```

```bash
# 将用户 user1 添加到组 sudo
sudo usermod -aG sudo user1
```

### 修改用户的主组

```bash
sudo usermod -g 组名 用户名
```

```bash
# 将用户 user1 的主组改为 group1
sudo usermod -g group1 user1
```

### 2. 修改组的信息：`groupmod`

`groupmod`命令用于修改组的属性。

```bash
sudo groupmod [选项] 组名
```

```bash
# 修改组 group1 的名称为 newgroup
sudo groupmod -n newgroup group1
```

### 1. 添加用户：`adduser` 或 `useradd`

```bash
sudo adduser 用户名
```

### 2. 删除用户：`deluser` 或 `userdel`

```bash
sudo deluser 用户名
```

### 3. 添加组：`addgroup` 或 `groupadd`

```bash
sudo addgroup 组名
```

### 4. 删除组：`delgroup` 或 `groupdel`

```bash
sudo delgroup 组名
```

### 1. 为用户赋予sudo权限

```bash
# 将用户 user1 添加到 sudo 组
sudo usermod -aG sudo user1
```

### 2. 限制用户对文件的访问

```bash
# 将文件 secret.txt 的权限设置为只有所有者可读写
chmod 600 secret.txt
```

### 3. 共享目录给特定组

```bash
# 创建组 sharegroup
sudo addgroup sharegroup

# 将用户 user1 和 user2 添加到 sharegroup
sudo usermod -aG sharegroup user1
sudo usermod -aG sharegroup user2

# 修改目录 sharedir 的所属组为 sharegroup
sudo chown :sharegroup sharedir

# 设置目录权限，使组成员可读写执行
chmod 770 sharedir
```

### 七、注意事项

- **谨慎使用`sudo`**：带有`sudo`的命令拥有超级用户权限，操作不当可能导致系统不稳定。
- **备份重要数据**：在修改权限前，备份重要文件以防数据丢失。
- **最小权限原则**：只赋予用户完成任务所需的最低权限，增强系统安全性。
- **定期检查权限**：使用`ls -l`命令查看文件权限，确保符合预期。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L1211)，来源许可：GPL-3.0。

<a id="k4f2326b63d51"></a>

## Linux中可视化GPU使用情况？

nvitop 是一个用于监控和管理 NVIDIA GPU 的命令行工具。它可以帮助用户实时监控 GPU 的使用情况，包括 GPU 的温度、功耗、显存使用率、风扇转速等信息。nvitop 类似于 Linux 下的 `htop` 工具，但专门用于 GPU。

### nvitop 的主要功能包括：

1. **实时监控**：显示当前所有 GPU 的利用率、显存使用情况、温度、风扇转速等。
2. **多 GPU 支持**：可以同时监控多张 GPU 的状态，非常适合使用多 GPU 的用户。
3. **可视化**：使用 ASCII 图形界面以友好的方式展示 GPU 数据，使得信息更加直观。
4. **进程监控**：列出每张 GPU 上运行的进程及其资源占用情况，便于发现和分析问题。
5. **轻量级**：nvitop 是一个轻量级工具，占用资源少，不会对 GPU 性能造成明显影响。

### 安装和使用：

你可以通过 pip 安装 nvitop：

```bash
pip install nvitop
```

安装完成后，直接在命令行输入 `nvitop` 即可启动监控工具。它会自动检测系统中的 NVIDIA GPU 并显示相关信息。

nvitop 非常适合开发者、数据科学家和需要实时了解 GPU 资源利用情况的用户，特别是在深度学习和科学计算等 GPU 密集型任务中非常有用。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L1106)，来源许可：GPL-3.0。

<a id="k6614e4443667"></a>

## Linux中如何创建软连接？

在 Linux 中，创建软连接（符号链接）的方法非常简单，可以通过 `ln` 命令来实现。软连接类似于 Windows 系统中的快捷方式，它指向另一个文件或目录，而不占用实际的存储空间。

### 创建软连接的基本语法

```bash
ln -s [目标文件或目录] [软连接名称]
```

- **`-s`**：表示创建的是软连接（符号链接），如果不加 `-s` 参数，创建的就是硬链接。
- **`目标文件或目录`**：我们想要创建软连接指向的原文件或目录。
- **`软连接名称`**：软连接的名称及路径。

### 具体示例

1. **创建一个文件的软连接**：

   假设我们有一个文件 `/home/user/documents/file.txt`，我们想在 `/home/user/desktop/` 下创建一个指向这个文件的软连接，命令如下：

```bash
   ln -s /home/user/documents/file.txt /home/user/desktop/file_link.txt
```

   这个命令将在 `/home/user/desktop/` 目录下创建一个名为 `file_link.txt` 的软连接，指向 `/home/user/documents/file.txt`。

2. **创建一个目录的软连接**：

   如果我们想要创建一个目录的软连接，比如将 `/home/user/documents/` 目录链接到 `/home/user/desktop/docs_link`，命令如下：

```bash
   ln -s /home/user/documents/ /home/user/desktop/docs_link
```

   这个命令将在 `/home/user/desktop/` 目录下创建一个名为 `docs_link` 的软连接，指向 `/home/user/documents/` 目录。

### 查看软连接

创建软连接后，可以使用 `ls -l` 命令查看链接的信息。软连接的文件类型在 `ls -l` 输出中会显示为 `l`，并且会显示链接指向的目标路径：

```bash
ls -l /home/user/desktop/
```

输出示例：

```bash
lrwxrwxrwx 1 user user 20 Jan  1 00:00 file_link.txt -> /home/user/documents/file.txt
lrwxrwxrwx 1 user user 25 Jan  1 00:00 docs_link -> /home/user/documents/
```

### 删除软连接

删除软连接与删除普通文件相同，使用 `rm` 命令即可：

```bash
rm /home/user/desktop/file_link.txt
```

注意：删除软连接并不会删除它指向的目标文件或目录。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L1025)，来源许可：GPL-3.0。

<a id="k7a0180382e8e"></a>

## Linux中如何查看CPU的使用率？

在 Linux 中，有多种方法可以查看 CPU 的使用率：

1. 使用 `top` 命令
2. 使用 `htop` 命令
3. 使用 `mpstat` 命令
4. 使用 `sar` 命令
5. 使用 `vmstat` 命令
6. 使用 `iostat` 命令
7. 使用 `dstat` 命令
8. 使用 `cat /proc/stat`

- **`top` 和 `htop`**：适用于实时监控系统资源使用情况，提供了详细的进程信息和使用率。
- **`mpstat`、`sar`、`vmstat` 和 `iostat`**：适合进行更细粒度的系统性能分析，可以定期收集和报告系统的 CPU 使用情况。
- **`dstat`**：是一个功能强大的多合一工具，适用于全面的系统资源监控。
- **`/proc/stat`**：提供了最底层的 CPU 使用信息，适合编写自定义脚本进行监控和分析。
- 

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L1087)，来源许可：GPL-3.0。

<a id="k4d1762edbcef"></a>

## Linux中异常和中断的区别

### **中断**

大家都知道，当我们在敲击键盘的同时就会产生中断，当硬盘读写完数据之后也会产生中断，所以，我们需要知道，中断大多数是由硬件设备产生的，而它们从物理上说就是电信号。

之后，它们通过中断控制器发送给CPU，接着CPU判断收到的中断来自于哪个硬件设备（这定义在内核中）。

最后，由CPU发送给内核，有内核处理中断。下面这张图显示了中断处理的流程：

![](https://raw.githubusercontent.com/forthespada/InterviewGuide/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/02-02-os.assets/202205212344538.png)

**软件中断与软中断**
除了硬件中断，还存在部分由软件产生的中断，称之为软件中断（Software Interrupt），最常见的有引发系统调用的Int 0x80。

同时，软件中断又区别于软中断（SoftIRQ），软中断主要用于中断处理的下半程（Bottom Halves），非关键逻辑的部分，来提高中断处理的效率与实时性，最常用于I/O相关的中断处理。

处理中断下半程的方法除了软中断，还有tasklet，二者存在一定的区别与联系：

* 二者都可以被注册用于中断处理下半程的延时任务；
* 同一种类型的tasklet只能串行执行，而同类型的软中断可以多个CPU并发执行，不同类型的软中断和tasklet均可并发执行；
* tasklet底层是基于两种软中断来实现的，分别是HI_SOFTIRQ和TASKLET_SOFTIRQ；

### **异常**

我们在学习《计算机组成原理》的时候会知道两个概念，CPU处理程序的时候一旦程序不在内存中，会产生缺页异常；当运行除法程序时，当除数为0时，又会产生除0异常。

所以，大家也需要记住的是，**异常是由CPU产生的，同时，它会发送给内核，要求内核处理这些异常**，下面这张图显示了异常处理的流程：

![](https://raw.githubusercontent.com/forthespada/InterviewGuide/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/02-02-os.assets/202205212344494.png)

### **相同点**

- 最后都是由CPU发送给内核，由内核去处理

- 处理程序的流程设计上是相似的

### **不同点**

- 产生源不相同，异常是由CPU产生的，而中断主要是由硬件设备产生的
- 内核需要根据是异常还是中断调用不同的处理程序
- 中断不是时钟同步的，这意味着中断可能随时到来；异常由于是CPU产生的，所以它是时钟同步的
- 当处理中断时，处于中断上下文中；处理异常时，处于进程上下文中

<p  id="瘟都死和里牛客死环境下内存分布情况"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/02-02-os.md#L514)，来源许可：Apache-2.0。

<a id="kdced8e3bf0a2"></a>

## Linux工具链在AI工程中的高频排查命令有哪些？

AI工程师需要具备基础系统排障能力。常用命令可以按问题分类：

```bash
# 进程与资源
ps aux | grep <name>
top
htop
kill -15 <PID>
kill -9 <PID>

# GPU
nvidia-smi
nvidia-smi pmon
nvidia-smi dmon

# 磁盘
df -h
df -i
du -sh *
find . -type f -size +1G

# 网络
ping <host>
curl -v <url>
ss -tulnp
lsof -i :<port>

# 日志
tail -f app.log
journalctl -u <service> -f
grep -n "ERROR" app.log

# 动态库
ldd ./app
readelf -d ./app
echo $LD_LIBRARY_PATH

# 容器
docker ps
docker logs -f <container>
docker exec -it <container> bash
docker stats
```

实际排障建议：

1. 服务起不来：先看日志、端口、环境变量、动态库、模型路径。
2. 推理慢：看GPU利用率、CPU占用、队列等待、数据加载、网络延迟。
3. 显存爆：看模型副本数、batch、KV Cache、是否有未释放请求。
4. 请求失败：看网关日志、服务日志、下游工具日志和request_id链路。
5. 磁盘满：看日志滚动、临时文件、生成结果、Docker镜像和已删除但未释放文件。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%B7%A5%E7%A8%8B%E5%9F%BA%E7%A1%80%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L2363)，来源许可：GPL-3.0。

<a id="k703921d5237f"></a>

## Linux系统中静态链接与动态链接的优缺点有哪些？

在AI算法岗面试中，回答静态链接与动态链接的优缺点需深入理解其机制及对AI系统的影响。以下是Rocky总结的结构化内容讲解：

### 一、核心概念对比
| **特性**         | **静态链接**                              | **动态链接**                              |
|------------------|------------------------------------------|------------------------------------------|
| **链接时机**     | 编译时完成，代码**直接嵌入**可执行文件     | 运行时加载，代码存放于**独立共享库**（.so） |
| **文件体积**     | 大（包含所有依赖库）                      | 小（仅存引用）                           |
| **内存占用**     | 高（每个进程独占库代码）                  | 低（多进程共享物理内存中的库）            |
| **依赖管理**     | 无需外部库（部署简单）                    | 需目标环境存在兼容的共享库（依赖复杂）     |
| **更新维护**     | 需重新编译整个程序                        | 仅替换共享库文件即可升级                 |
| **加载速度**     | 快（无运行时加载开销）                    | 慢（需解析符号地址）                     |
| **兼容性风险**   | 无（库版本固定）                          | 可能因库版本冲突崩溃（“DLL Hell”问题）    |

> 💡 **本质差异**：静态链接是“自带干粮”，动态链接是“共享食堂”。

### 二、通俗案例：AI推理服务部署
### 场景：部署图像分类模型至10台服务器
- **静态链接方案**  
```bash
  g++ -static main.cpp libmodel.a -o classifier # 编译生成100MB可执行文件
```
  - ✅ **优点**：直接复制文件到任意服务器即可运行（无依赖）  
  - ❌ **缺点**：10台服务器共占用 **100MB × 10 = 1GB** 存储（重复库代码）  

- **动态链接方案**  
```bash
  g++ main.cpp -L./ -lmodel -o classifier  # 生成5MB可执行文件+95MB libmodel.so
```
  - ✅ **优点**：10台服务器总占用 **5MB×10 + 95MB = 145MB**（共享库仅存1份）  
  - ❌ **缺点**：需确保每台服务器都有完全兼容的`libmodel.so`，版本升级需同步所有机器  

**结论**：  
- 服务器集群选择**动态链接** → 节省存储，热更新模型库  
- 边缘设备（无网络）选择**静态链接** → 避免依赖问题  

### 1. **AIGC（生成式AI）**
| **静态链接适用场景**        | **动态链接适用场景**              |
|----------------------------|----------------------------------|
| - 移动端Stable Diffusion部署（避免依赖）<br>- 模型加密分发（代码不可拆分） | - 云服务推理引擎（多模型共享CUDA库）<br>- 插件化架构（如Diffusers动态加载LoRA模块） |

**案例**：  
- **静态链接**：将Stable Diffusion模型与推理引擎编译为单一ARM可执行文件，部署至手机端（如[Draw Things](https://drawthings.ai/)）  
- **动态链接**：AI绘画云服务使用`libtorch.so`，多个容器共享同一份PyTorch库，减少内存冗余  

### 2. **传统深度学习（CV/NLP）**
| **静态链接适用场景**        | **动态链接适用场景**              |
|----------------------------|----------------------------------|
| - 嵌入式设备模型推理（如树莓派）<br>- 比赛提交代码（避免环境问题） | - 训练框架开发（动态加载算子）<br>- 研究实验（快速切换CUDA/cuDNN版本） |

**案例**：  
- **静态链接**：将YOLOv5模型+OpenCV静态编译，部署至安防摄像头（无外部依赖）  
- **动态链接**：PyTorch使用`libc10_cuda.so`动态加载CUDA后端，同一服务器支持多版本GPU驱动  

### 3. **自动驾驶**
| **静态链接适用场景**        | **动态链接适用场景**              |
|----------------------------|----------------------------------|
| - 车载ECU固件（确定性要求高）<br>- 实时控制模块（无延迟风险） | - 仿真测试环境（动态替换感知模型）<br>- 开发调试（热更新算法模块） |

**案例**：  
- **静态链接**：毫米波雷达信号处理代码静态编译，烧录至车规级芯片（ISO 26262要求无运行时依赖）  
- **动态链接**：自动驾驶仿真平台动态加载`libplanning.so`，测试不同规划算法无需重启系统  

### 四、工程实践中的混合策略
1. **关键模块静态化**  
```cmake
   # CMake示例：部分静态链接
   target_link_libraries(main
       -Wl,-Bstatic -lcritical_model  # 静态链接核心模型
       -Wl,-Bdynamic -lcudart         # 动态链接CUDA运行时
   )
```
   - 感知算法静态编译（确保安全），CUDA库动态链接（节省内存）

2. **版本隔离技术**  
```bash
   # 为不同版本库创建独立路径
   export LD_LIBRARY_PATH=/opt/cuda-11.8/lib64:$LD_LIBRARY_PATH
```
   - 解决动态库冲突（如同时需CUDA 11.3和11.8）

3. **容器化部署**  
```Dockerfile
   FROM nvcr.io/nvidia/pytorch:22.08  # 基础镜像含动态库
   COPY libmodel.so /usr/lib/        # 添加业务动态库
   COPY static_app /app/             # 静态链接的可执行文件
```
  - 基础镜像提供标准动态库，业务模块按需选择链接方式

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L2977)，来源许可：GPL-3.0。

<a id="kae9f453206c3"></a>

## Linux系统和Windows系统的区别？

- Linux系统更稳定且有效率。
- Linux系统是免费（或少许费用），而Windows系统是商业化主导。
- Linux系统漏洞少且快速修补。
- Linux系统支持多用户同时使用计算机。
- Linux系统有更加安全的用户与文件权限策略。
- Linux系统可以访问源代码并根据用户的需要修改代码，而Windows系统不能访问源代码。
- Linux系统更能支持多种深度学习配套软件，但是windows系统能支持大量的视频游戏软件。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L259)，来源许可：GPL-3.0。

<a id="k858d9242d81e"></a>

## Linux系统种类

- 红帽企业版Linux：RedHat是全世界内使用最广泛的Linux系统。它具有极强的性能与稳定性，是众多生成环境中使用的（收费的）系统。
- Fedora：由红帽公司发布的桌面版系统套件，用户可以免费体验到最新的技术或工具，这些技术或工具在成熟后会被加入到RedHat系统中，因此Fedora也成为RedHat系统的试验版本。
- CentOS：通过把RedHat系统重新编译并发布给用户免费使用的Linux系统，具有广泛的使用人群。
- Deepin：在中国发行，对优秀的开源成品进行集成和配置。
- Debian：稳定性、安全性强，提供了免费的基础支持，在国外拥有很高的认可度和使用率。
- Ubuntu：是一款派生自Debian的操作系统，<font color=DeepSkyBlue>对新款硬件具有极强的兼容能力。Ubuntu与Fedora都是极其出色的Linux桌面系统，而且Ubuntu也可用于服务器领域</font>。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L249)，来源许可：GPL-3.0。

<a id="kf7fc8cf90871"></a>

## Linux资源排查在AIGC服务中怎么做？

AIGC服务常见问题包括：请求变慢、GPU利用率低、显存爆掉、磁盘满、端口占用、文件句柄耗尽、网络连接异常。排查应按“现象 -> 资源 -> 进程 -> 日志 -> 最近变更”的顺序。

高频命令：

```bash
# CPU/内存/进程
top
htop
ps aux | grep python

# GPU
nvidia-smi
nvidia-smi dmon

# 磁盘与inode
df -h
df -i
du -sh *

# IO
iostat -x 1
pidstat -d 1

# 网络与端口
ss -tulnp
ss -tan | awk '{print $1}' | sort | uniq -c
lsof -i :8000

# 文件句柄
ulimit -n
lsof -p <PID> | wc -l
```

AI场景里的典型判断：

1. GPU利用率低但CPU高：可能是预处理、数据加载或tokenization成为瓶颈。
2. GPU显存满：检查batch、KV Cache、模型副本数、未释放请求。
3. 磁盘满但 `du` 看不出来：可能是文件已删除但仍被进程占用，用 `lsof | grep deleted`。
4. 连接很多但吞吐低：检查TIME_WAIT、客户端读慢、背压和worker数量。
5. 延迟突然升高：对比最近部署、模型版本、流量、数据库慢查询和下游工具延迟。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L3119)，来源许可：GPL-3.0。

<a id="k831e2ea809ee"></a>

## ps aux | grep xxx命令

如果直接用ps命令，会显示所有进程的状态，通常结合grep命令查看某进程的状态。

grep （global search regular expression(RE) and print out the line,全面搜索正则表达式并把行打印出来）是一种强大的文本搜索工具，它能使用正则表达式搜索文本，并把匹配的行打印出来。

例如我想要查看Python 的所有进程，可以在终端输入如下命令：

```bash
ps aux | grep python
```

便可以把Python相关的进程全部都打印到终端供我们查看。相关参数和之前的ps aux | more一致。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L191)，来源许可：GPL-3.0。

<a id="k0d1da1098f6f"></a>

## ps aux | more 指令

这个指令可以显示进程详细的状态。

参数解释：

- USER：进程的所有者。
- PID：进程的ID。
- PPID：父进程。
- %CPU：进程占用的CPU百分比。
- %MEM：进程占用的内存百分比。
- NI：进程的NICE值，数值越大，表示占用的CPU时间越少。
- VSZ：该进程使用的虚拟内存量（KB）。
- RSS：该进程占用的固定内存量（KB）。
- TTY：该进程在哪个终端上运行，若与终端无关，则显示？。若为pts/0等，则表示由网络连接主机进程。
- WCHAN：查看当前进程是否在运行，若为-表示正在运行。
- START：该进程被触发启动时间。
- TIME：该进程实际使用CPU运行的时间。
- COMMAND：命令的名称和参数。
- STAT状态位常见的状态字符：
D 无法中断的休眠状态（通常 IO 的进程）；
R 正在运行可中在队列中可过行的；
S 处于休眠状态；
T 停止或被追踪；
W 进入内存交换  （从内核2.6开始无效）；
X 死掉的进程   （基本很少見）；
Z 僵尸进程；
< 优先级高的进程
N 优先级较低的进程
L 有些页被锁进内存；
s 进程的领导者（在它之下有子进程）；
l 多进程的（使用 CLONE_THREAD, 类似 NPTL pthreads）；+ 位于后台的进程组；

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L158)，来源许可：GPL-3.0。

<a id="k12685dfbd06b"></a>

## 一、什么是内核优化？

内核优化中的“内核”通常指底层计算kernel，例如CUDA kernel、CPU SIMD kernel或NPU专用算子实现。

它关注的是：对于同一个算子，如何让底层实现更快。

例如同样是矩阵乘法，不同kernel实现的性能可能差很多。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E6%A8%A1%E5%9E%8B%E9%83%A8%E7%BD%B2%E5%9F%BA%E7%A1%80%EF%BC%88%E7%B2%BE%E5%8D%8E%E7%89%88%EF%BC%89/6.1%E6%8E%A8%E7%90%86%E9%83%A8%E7%BD%B2%E7%BB%BC%E8%BF%B0.md#L1319)，来源许可：GPL-3.0。

<a id="kb644f98c7dba"></a>

## 为什么要分用户态和内核态？


（我自己的见解：）

- 安全性：防止用户程序恶意或者不小心破坏系统/内存/硬件资源；
- 封装性：用户程序不需要实现更加底层的代码；
- 利于调度：如果多个用户程序都在等待键盘输入，这时就需要进行调度；统一交给操作系统调度更加方便。

### 参考资料

- [Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Operating%20Systems.md#L428)，来源许可：GPL-3.0。

<a id="kc19d8811e9cd"></a>

## 为什么要有用户态和内核态？只有一个内核态不行么？

这样设计主要是为了**安全**和**稳定**。

- **限制特权操作**：修改页表、控制中断、访问特定设备寄存器等操作会影响整个系统，只能由内核执行。
- **隔离故障和权限**：如果应用都能以内核权限运行，一个越界写或恶意程序就可能破坏其他进程和内核数据，进程隔离也就失去了基础。

这套特权级机制把普通应用限制在受控环境中，硬件和系统资源则统一交给内核管理。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/operating-system/operating-system-basic-questions-01.md#L103)，来源许可：Apache-2.0。

<a id="k2723c31c31bf"></a>

## 什么是Shell

Shell是用户与Linux操作系统之间的命令解释器，它可以执行命令、脚本和其他操作。常见的shell包括：
- **Bourne Shell (sh)**: /bin/sh
- **Bourne Again Shell (bash)**: /bin/bash
- **C Shell (csh)**: /bin/csh
- **Korn Shell (ksh)**: /bin/ksh
- **Z Shell (zsh)**: /bin/zsh

在AI领域中，主要使用/bin/sh和/bin/bash两种命令解释器。Rocky再讲一下两者的区别，以便大家更好的理解：
1. Bash是sh的超集，这意味着Bash包含了sh的所有功能，并且向后兼容sh脚本。使用sh编写的脚本几乎可以在Bash中不做修改地运行。
2. Bash提供了许多增强的交互功能，如命令行编辑（使用Emacs和Vi模式）、命令历史记录、Tab补全等。sh提供的交互功能较少，更适合编写简单的脚本而不是交互式使用。
3. Bash支持一系列高级编程特性，如数组、命令替换、进程替换、改进的变量替换、字符串操作等。sh提供的编程功能较为基本，主要用于简单的脚本和系统级任务。
4. sh通常比bash更轻量级，因为它的功能较少。因此，sh可能在一些简单的脚本中表现更快。bash提供了更多功能和灵活性，适用于更复杂的脚本和交互式使用，但在某些情况下可能比sh略慢。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L776)，来源许可：GPL-3.0。

<a id="k90f896ea90e7"></a>

## 介绍一下Linux中“No space left on device”问题的解决方案

### **1. 问题诊断：确认磁盘使用情况**
- **核心命令**：
```bash
  df -h          # 查看所有挂载点的空间使用情况
  du -sh /*      # 分析根目录下各子目录的占用空间
```
- **作用**：快速定位空间不足的分区或目录。例如，若发现`/var`占用过高，可能是日志或缓存堆积。

**实际案例**：
- **AIGC**：生成式模型（如Stable Diffusion）训练时，若未设置自动清理，临时生成的图像样本和模型检查点可能占满`/tmp`或用户目录。
- **传统深度学习**：TensorFlow/PyTorch的数据预处理阶段，未清理的中间文件（如未压缩的数据集缓存）可能导致`/home`空间耗尽。
- **自动驾驶**：自动驾驶车辆的路测数据（如激光雷达点云、摄像头视频）若直接存储在根目录下，可能迅速占满存储。

### **2. 清理临时文件与缓存**
- **关键操作**：
```bash
  # 清理APT缓存（释放/var/cache/apt/archives）
  sudo apt-get clean
  sudo apt-get autoremove

  # 清理Docker资源（释放/var/lib/docker）
  docker system prune -a -f

  # 清理日志（释放/var/log）
  sudo journalctl --vacuum-time=7d  # 仅保留7天日志
  sudo truncate -s 0 /var/log/*.log
```

**实际案例**：
- **AIGC**：在训练大型语言模型（如GPT-3）时，Docker容器生成的中间层镜像可能占用数百GB，需定期清理。
- **传统深度学习**：使用Jupyter Notebook时，内核崩溃生成的`core.*`文件可能堆积在`/var/crash`，需手动删除。
- **自动驾驶**：车载系统的高频传感器日志（如每秒10GB的雷达数据）需配置日志轮转（`logrotate`），限制单个日志文件大小。

### **3. 删除无用的大文件**
- **操作步骤**：
```bash
  # 查找大文件（按大小排序）
  sudo find / -type f -size +1G -exec ls -lh {} \;

  # 删除特定文件或目录
  rm -rf /path/to/large_files
```

**实际案例**：
- **AIGC**：训练生成的中间模型检查点（如每epoch保存的`model_ckpt_*.pt`）可仅保留最优模型，其余删除。
- **传统深度学习**：ImageNet预处理后的数据集缓存（如未压缩的TFRecords）在训练结束后可删除。
- **自动驾驶**：冗余的旧版本地图数据（如高精度地图的`.pcd`文件）可通过版本管理工具清理。

### **4. 扩展存储空间**
- **物理扩展**：添加新硬盘并挂载到空闲目录（如`/data`）。
- **逻辑卷扩展（LVM）**：
```bash
  sudo lvextend -L +100G /dev/vg0/root  # 扩展逻辑卷
  sudo resize2fs /dev/vg0/root          # 调整文件系统
```
- **符号链接迁移**：
```bash
  mv /root/large_data /new_disk/
  ln -s /new_disk/large_data /root/large_data  # 创建软链接
```

**实际案例**：
- **AIGC**：扩展存储用于存放扩散模型的高分辨率训练数据集（如LAION-5B）。
- **传统深度学习**：挂载NAS存储，存放分布式训练中的共享数据集。
- **自动驾驶**：使用SAN存储阵列存放PB级路测数据，通过NFS挂载到训练服务器。

### **5. 处理进程占用已删除文件**
- **命令**：
```bash
  # 查找被删除但仍被进程占用的文件
  sudo lsof +L1 | grep deleted

  # 重启相关进程或服务释放空间
  sudo systemctl restart apache2
```

**实际案例**：
- **AIGC**：训练脚本异常退出后，模型文件被删除但GPU进程仍占用，需`kill`进程或重启服务。
- **自动驾驶**：车载数据采集服务崩溃后，未正确关闭的进程占用传感器日志文件，需重启服务。

### **6. 预防措施**
- **自动化清理脚本**：
```bash
  # 每周清理Docker和APT缓存
  echo "0 3 * * 0 docker system prune -af && apt-get clean" | sudo tee /etc/cron.weekly/cleanup
```
- **监控工具**：
  - 使用`ncdu`可视化磁盘占用。
  - 部署Prometheus + Grafana监控存储使用率。

**实际案例**：
- **AIGC**：在Kubernetes集群中配置Pod的存储卷自动清理策略，避免模型训练任务占满持久化存储。
- **自动驾驶**：车载边缘计算设备配置InfluxDB监控，实时预警存储使用率超过90%。
- **传统深度学习**：Slurm作业调度系统中设置任务结束后的自动清理脚本，删除临时文件。

### 总结

“No space left on device”的解决方案本质是**空间诊断→清理释放→扩展容量→预防监控**的闭环。在AI各领域中，需结合领域特性优化：
- **AIGC**：关注模型训练生命周期管理，利用云原生存储弹性扩展。
- **传统深度学习**：优化数据流水线，减少中间文件产生。
- **自动驾驶**：强化边缘设备的存储可靠性，设计高吞吐日志系统。  
通过技术组合与自动化策略，可系统性解决存储瓶颈，支撑AI领域应用的规模化落地。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L1938)，来源许可：GPL-3.0。

<a id="k764cf7768ecb"></a>

## 介绍一下Linux中下载命令的使用大全

在Linux系统中，文件下载是日常高频操作，无论是从服务器拉取数据、抓取网页资源，还是通过命令行高效管理下载任务，都需要掌握核心工具。**以下从基础到进阶，详解 `wget`、`curl`、`aria2`、`axel` 四大神器的用法，附场景化案例和避坑指南**。

### **高频用法**
1. **基础下载**  
```bash
   wget http://example.com/file.zip  # 下载到当前目录
   wget -O custom_name.zip http://example.com/file.zip  # 指定保存文件名
```

2. **断点续传 & 后台下载**  
```bash
   wget -c http://example.com/large_file.iso  # 断点续传（-c）
   wget -b http://example.com/file.zip        # 后台下载（日志写入wget-log）
```

3. **递归抓取整站**  
```bash
   wget -r -np -k -p http://example.com/  # -r递归 -np不爬上级目录 -k转换链接为本地 -p下载所有依赖
```

4. **限速下载（防带宽占满）**  
```bash
   wget --limit-rate=200k http://example.com/large_file.iso  # 限速200KB/s
```

### **高频用法**
1. **直接下载文件**  
```bash
   curl -O http://example.com/file.zip        # -O 保留远程文件名
   curl -o custom_name.zip http://example.com/file.zip  # -o 自定义文件名
```

2. **调试API & 显示详细过程**  
```bash
   curl -X POST -H "Content-Type: application/json" -d '{"key":"value"}' http://api.example.com/data
   curl -v http://example.com  # -v显示详细请求/响应头
```

3. **上传文件 & 认证**  
```bash
   curl -u username:password -T local_file.txt ftp://ftp.example.com/  # FTP上传
   curl -F "file=@/path/to/file" http://example.com/upload  # HTTP表单上传
```

4. **跟随重定向 & 代理设置**  
```bash
   curl -L http://example.com  # -L自动跟随301/302跳转
   curl -x http://proxy:8080 http://example.com  # 通过代理下载
```

### **高频用法**
1. **多线程下载**  
```bash
   aria2c -s 16 http://example.com/large_file.iso  # -s指定16线程
```

2. **批量下载（多链接/多文件）**  
```bash
   aria2c -i urls.txt  # urls.txt每行一个下载链接
   aria2c -Z http://file1.zip http://file2.zip  # 同时下载多个文件
```

3. **BT下载 & 限速**  
```bash
   aria2c --seed-time=0 --max-upload-limit=50K "magnet:?xt=urn:..."  # BT下载不限做种时间，上传限速50KB
```

4. **断点续传 & 日志管理**  
```bash
   aria2c -c --log=download.log --save-session=session.txt  # 记录日志和会话
```

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L2400)，来源许可：GPL-3.0。

<a id="k3b81d4d98839"></a>

## 介绍一下Linux系统中的Shell脚本

**在Linux系统中，Shell脚本是一种非常强大的工具，在AIGC、传统深度学习、自动驾驶领域中主要用于自动化任务、管理系统和处理日常操作**。直观上看，**Shell脚本是一系列shell命令的集合，以脚本文件的形式存储，并通过shell解释器来执行**。下面是Rocky对Linux系统中shell脚本的详细讲解，包括基础知识、编写示例和一些高级用法：

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L770)，来源许可：GPL-3.0。

<a id="kd710333a7b90"></a>

## 在计算机中有哪些常用的读写操作，每个读写操作的性能是什么样的？

在计算机中，**读写操作**是处理数据的基本操作之一，涉及将数据从一个存储介质（如内存、硬盘、缓存等）读取到另一个存储介质，或将数据从一个存储介质写入到另一个存储介质。**在AI行业中，稳健的读写操作往往是AI算法解决方案的关键一环，如果其中的读写操作不恰当，往往会造成AI算法解决方案的性能瓶颈**。下面Rocky带大家详细了解一下计算机中的主要读写操作以及它们的性能。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L1131)，来源许可：GPL-3.0。

<a id="kef8c5edff796"></a>

## 外中断和异常有什么区别？

外中断是指由 CPU 执行指令以外的事件引起，如 I/O 完成中断，表示设备输入/输出处理已经完成，处理器能够发送下一个输入/输出请求。此外还有时钟中断、控制台中断等。

而异常时由 CPU 执行指令的内部事件引起，如非法操作码、地址越界、算术溢出等。

<p  id="进程线程模型你知道多少"></p>

### 参考资料

- [阿秀面试笔记](https://github.com/forthespada/InterviewGuide/blob/25055ccfa146c11f2ccc986402ad36b34471e6c0/docs/notes/03-hunting_job/02-interview/02-01-os.md#L105)，来源许可：Apache-2.0。

<a id="k0c5f6fef869a"></a>

## 如何从用户态切换到内核态？


- 系统调用：比如读取命令行输入。本质上还是通过中断实现
- 用户程序发生异常时：比如缺页异常
- 外围设备的中断：外围设备完成用户请求的操作之后，会向CPU发出中断信号，这时CPU会转去处理对应的中断处理程序

### 参考资料

- [Waking-Up](https://github.com/wolverinn/Waking-Up/blob/cf692b53e1b3d1b740a97dab0e4e71db801daf33/Operating%20Systems.md#L439)，来源许可：GPL-3.0。

<a id="kb4e6f1ab5a05"></a>

## 执行命令

```bash
# 对查找到的每个文件执行 ls -l 命令
find /path/to/start -name "*.txt" -exec ls -l {} \;
# 对查找到的每个文件执行 rm 命令
find /path/to/start -name "*.tmp" -exec rm -f {} \;
```

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L454)，来源许可：GPL-3.0。

<a id="k2a0941051649"></a>

## 深度学习中常用的Linux命令汇总

```
1.man：man command，可以查看某个命令的帮助文档，按q退出帮助文档
2.cd：用于切换目录，cd - 可以在最近两次目录之间来回切换
3.touch：touch file创建文件。
4.ls：ls -lh可以列出当前目录下文件的详细信息。
5.pwd：pwd命令以绝对路径的方式显示用户当前的工作目录
6.cat：cat file显示文件内容。
7.mkdir：mkdir dir可以创建一个目录；mkdir -p dir/xxx/xxx可以递归创建目录。
8.cat：cat file显示文件内容，按q退出。
9.more：more file显示文件内容，按q退出。
10.grep：筛选命令，比如我想查找当前目录下的py文件（ls -lh | grep .py）
11.whereis：可以查找含有制定关键字的文件，如whereis python3
重定向 > 和 >>：Linux 允许将命令执行结果重定向到一个文件，将本应显示在终端上的内容输出／追加到指定文件中。其中>表示输出，会覆盖原有文件；>>表示追加，会将内容追加到已有文件的末尾。
12.cp：cp dst1 dst2复制文件；cp -r dst1 dst2复制文件夹。
13.mv：mv dst1 dst2可以移动文件、目录，也可以给文件或目录重命名。
14.zip：zip file.zip file压缩文件；zip dir.zip -r dir压缩文件夹。
15.unzip：unzip file.zip解压由zip命令压缩的.zip文件。
16.tar：
    tar -cvf file.tar dir打包文件夹
    tar -xvf file.tar解包
    tar -czvf file.tar.gz dir压缩文件夹
    tar -zxvf file.tar.gz解压
17.chmod：chmod -R 777 data将整个data文件夹修改为任何人可读写。
18.ps：ps aux列出所有进程的详细信息。
19.kill：kill PID根据PID杀死进程。
20.df：df -h 查看磁盘空间。
21.du：du -h dir查看文件夹大小。
22.top：实时查看系统的运行状态，如 CPU、内存、进程的信息。
23wget：wget url从指定url下载文件。
24.ln：ln -s dst1 dst2建立文件的软链接，类似于windows的快捷方式；ln dst1 dst2建立文件的硬链接。无论哪种链接，dst1都最好使用绝对路径。
25.top：我们可以使用top命令实时的对系统处理器的状态进行监视。
26.apt-get：用于安装，升级和清理包。
27.vim：对文件内容进行编辑。
28.nvidia-smi：对GPU使用情况进行查看。
29.nohup sh test.sh &：程序后台运行且不挂断。
30.find：这个命令用于查找文件，功能强大。find . -name "*.c"表示查找当前目录及其子目录下所有扩展名是.c的文件。
```

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9F%BA%E7%A1%80/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L49)，来源许可：GPL-3.0。

<a id="ka73122f275cc"></a>

## 用户态和内核态是如何切换的？

![用户态切换到内核态的 3 种方式](https://oss.javaguide.cn/github/javaguide/cs-basics/operating-system/the-way-switch-between-user-mode-and-kernel-mode.drawio.png)

让 CPU 从用户态进入内核态的事件主要有三类：

1. **系统调用（Trap）**：应用程序主动执行 `syscall`、`ecall` 等指令，请求内核完成 `read()`、`send()` 等操作。它由当前指令触发，属于同步事件。
2. **硬件中断（Interrupt）**：由定时器、网卡、磁盘等外部硬件触发，与当前正在执行的指令没有直接关系，因此属于异步事件。
3. **同步异常（Exception）**：由当前指令触发，例如除零、非法指令或 Page Fault。异常不一定代表程序出错，懒分配、COW 和从文件调页也会触发可恢复的 Page Fault。

中断、异常和系统调用描述的是 CPU 为什么进入内核；信号则是内核通知进程或线程的一种软件机制。非法内存访问可能先触发 Page Fault，内核判断无法修复后，再向当前线程投递 `SIGSEGV`。

不同体系结构的入口细节不完全相同，但都会根据事件类型转到对应的内核处理入口。完整的概念对比和处理路径可以看：[中断、异常与系统调用详解：从内核入口到缺页异常](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/operating-system/interrupt-exception-syscall.md)。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/cs-basics/operating-system/operating-system-basic-questions-01.md#L112)，来源许可：Apache-2.0。

<a id="k71f0dfaf689b"></a>

## 硬中断和软中断

​	    **硬中断**是由硬件产生的，比如，像磁盘，网卡，键盘，时钟等。每个设备或设备集都有它自己的IRQ（中断请求）。

​	    处理中断的驱动是需要运行在CPU上的，因此，当中断产生的时候，CPU会中断当前正在运行的任务，来处理中断。在有多核心的系统上，一个中断通常只能中断一颗CPU（也有一种特殊的情况，就是在大型主机上是有硬件通道的，它可以在没有主CPU的支持下，可以同时处理多个中断）。

​		**硬中断**可以直接中断CPU。它会引起内核中相关的代码被触发。对于那些需要花费一些时间去处理的进程，中断代码本身也可以被其他的硬中断中断。

​		**软中断**的处理非常像硬中断。然而，它们仅仅是由当前正在运行的进程所产生的。通常，软中断是一些对I/O的请求。这些请求会调用内核中可以调度I/O发生的程序。对于某些设备，I/O请求需要被立即处理，而磁盘I/O请求通常可以排队并且可以稍后处理。根据I/O模型的不同，进程或许会被挂起直到I/O完成，此时内核调度器就会选择另一个进程去运行。I/O可以在进程之间产生并且调度过程通常和磁盘I/O的方式是相同。

​		**软中断**仅与**内核**相联系。而内核主要负责对需要运行的任何其他的进程进行调度。一些内核允许设备驱动的一些部分存在于用户空间，并且当需要的时候内核也会调度这个进程去运行。

​		**软中断**并不会直接中断CPU。也只有当前正在运行的代码（或进程）才会产生软中断。这种中断是一种需要内核为正在运行的进程去做一些事情（通常为I/O）的请求。有一个特殊的软中断是Yield调用，它的作用是请求内核调度器去查看是否有一些其他的进程可以运行。

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/03-computer-basics/operating-system/processes-and-threads.md#L103)，来源许可：GPL-3.0。

<a id="k233c62d5cd56"></a>

## 系统级工具（Nsight Systems、Timeline）与内核级工具（Nsight Compute、Kernel Profiler）如何配合使用？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

### 一、系统级 vs 内核级：两种分析视角

| 维度 | 系统级分析 | 内核级（Kernel）分析 |
|------|-----------|---------------------|
| 分析粒度 | 毫秒~秒级，看全局流程 | 微秒~纳秒级，看单个 Kernel 内部 |
| 主要问题 | "时间花在了哪里？" | "这个 Kernel 为什么慢？" |
| 典型工具 | Nsight Systems、Chrome Trace | Nsight Compute（ncu） |
| 分析对象 | API 调用序列、Kernel 排队、数据传输、同步 | 单 Kernel 的 SM 占用、显存访问、指令流水线 |
| 输出形式 | Timeline 时间轴 | Roofline 图、内存/计算吞吐报告 |

### 二、Nsight Systems（系统级）

Nsight Systems（nsys）是 NVIDIA 官方的系统级性能分析工具：
- **Timeline 视图**：以时间轴展示所有 CUDA API 调用、Kernel 执行、内存拷贝（H2D/D2H）、CUDA Stream 活动
- **可看清**：CPU 线程活动、GPU Kernel 序列、stream 间并行情况、CPU-GPU 同步点、数据传输与计算的 overlap
- **典型发现**：Kernel 之间有大量 Gap（空闲气泡）、CPU 等待 GPU、数据传输和计算没有流水线化

### 三、Nsight Compute（内核级）

Nsight Compute（ncu）是 NVIDIA 官方的 Kernel 性能分析工具：
- **单 Kernel 深度分析**：选定一个 Kernel，分析其 SM 占用率、算术吞吐、内存吞吐、指令混合、寄存器使用
- **Roofline 分析**：将 Kernel 的性能点标在计算能力 vs 计算强度的图上
- **Source Page**：将分析结果映射到 CUDA 源码或 PTX/SASS 汇编行
- **典型发现**：Occupancy 过低、Shared Memory Bank Conflict、Global Memory 访问未合并

### 四、配合使用的标准流程

```
1. nsys（系统级）→ 跑一遍推理，看 Timeline
   → 发现：GPU 在 70% 时间内是空闲的
   → 发现：MatMul Kernel 占用了 80% 的 GPU 活跃时间

2. ncu（内核级）→ 对 MatMul Kernel 做深度分析
   → 发现：Arithmetic Throughput 只达理论峰值的 40%
   → 发现：Occupancy 只有 25%

3. 优化后 → 用 nsys 再跑一遍验证全局效果
```

可以总结为：**系统级工具（Nsight Systems）回答"哪个 Kernel 慢、为什么 GPU 空闲"；内核级工具（Nsight Compute）回答"这个 Kernel 为什么只跑到理论的 X%"。两者配合是经典的"先宏观定位、再微观分析"的二阶段调优流程。**

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E6%A8%A1%E5%9E%8B%E9%83%A8%E7%BD%B2%E5%9F%BA%E7%A1%80%EF%BC%88%E7%B2%BE%E5%8D%8E%E7%89%88%EF%BC%89/6.4%E6%80%A7%E8%83%BD%E5%88%86%E6%9E%90%E4%B8%8E%E8%B0%83%E4%BC%98%E5%B7%A5%E5%85%B7.md#L243)，来源许可：GPL-3.0。

<a id="kc176a81eb439"></a>

## 计算优化中的算子融合与内核优化分别指什么？

> 算子融合关注的是把多个算子合并成更少的执行单元，减少中间数据读写和调度开销；内核优化关注的是把单个算子的底层实现写得更高效，充分利用CPU、GPU或NPU的计算单元、缓存和内存带宽。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E6%A8%A1%E5%9E%8B%E9%83%A8%E7%BD%B2%E5%9F%BA%E7%A1%80%EF%BC%88%E7%B2%BE%E5%8D%8E%E7%89%88%EF%BC%89/6.1%E6%8E%A8%E7%90%86%E9%83%A8%E7%BD%B2%E7%BB%BC%E8%BF%B0.md#L1276)，来源许可：GPL-3.0。

<a id="k91858f6d6960"></a>

## 项目中如何定位问题，有没有使用过Linux或者抓包等工具？

**回答：**

定位问题要体现方法论，而不是只说“看日志”。我一般会按“复现 -> 分层 -> 证据 -> 缩小范围 -> 修复验证”走。

第一步复现问题，明确输入、环境、版本、时间点和期望行为。第二步分层定位：前端交互、网关、后端服务、模型服务、工具服务、数据库、向量库、客户本地网络都要分开看。第三步收集证据：应用日志、trace id、接口状态码、请求耗时、模型输入输出、工具调用参数、数据库慢查询和系统资源。

Linux 工具上，常用 `top/htop` 看 CPU 和内存，`df/du` 看磁盘，`ps/jstack` 看进程和线程，`journalctl` 或服务日志看异常，`curl` 验接口，`netstat/ss/lsof` 看端口，`grep/awk/sed` 快速过滤日志。网络问题可以用 `ping`、`telnet/nc`、`traceroute`、`dig/nslookup`。抓包可以用 `tcpdump` 或 Wireshark，重点看 DNS、TLS 握手、TCP 重传、HTTP 状态码、请求体是否异常。

对 AI 应用还要额外看模型链路：prompt 是否被裁剪、RAG 召回是否为空、rerank 是否误排、工具参数是否被模型生成错、上下文是否超长、供应商 API 是否限流。定位的核心不是工具清单，而是每一步都能用证据排除一层。

<a id="bytedance-ai-fde-20260712-q5"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%AD%97%E8%8A%82%E8%B7%B3%E5%8A%A8%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L804)，来源许可：GPL-3.0。
