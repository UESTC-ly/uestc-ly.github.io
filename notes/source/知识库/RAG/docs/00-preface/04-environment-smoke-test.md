# 00-04 环境冒烟测试

| 项目 | 内容 |
|---|---|
| chapter-id | `00-04` |
| 难度 | 入门 |
| 预计用时 | 25 分钟 |
| 必须已会 | 完成 00-03，能打开终端并识别当前目录 |
| 联网与费用 | 不联网，不安装第三方包，不产生费用 |
| 离线替代 | 本章所有命令只使用 Python 标准库和本地临时文件 |

完成本章后，你应该能够：

- 确认实际运行的 Python 版本为 3.11 或更高兼容版本；
- 创建一个独立虚拟环境，并直接调用其中的解释器；
- 验证 Python 能写入、读取并清理 UTF-8 中文文件；
- 记录操作系统、解释器路径、命令、输出和失败信息。

## 冒烟测试只回答一个小问题

冒烟测试（smoke test）不是完整测试。它只快速判断“最基本的路径能否工作”。本章不
安装 RAG 框架，不连接模型 API，也不测试向量数据库。这样做是为了把问题缩小：如果
连 Python 版本、虚拟环境或本地文件读写都失败，先解决这些问题比继续安装十个依赖更
有效。

规划中的 `scripts/run-smoke-tests.py` 和环境流程图尚未在本批次交付。下面的手动命令
就是当前可用检查；本章不会把计划中的脚本写成已经运行。

## 开始前先确认位置

打开终端并进入仓库根目录，也就是能够看到 `README.md`、`docs/` 和 `examples/` 的目录。
不要仅凭终端窗口标题猜测当前位置。

在 macOS 或 Linux 的 bash、zsh 等 shell 中，可以运行：

```bash
pwd
ls
```

在 Windows PowerShell 中，可以运行：

```powershell
Get-Location
Get-ChildItem
```

如果列表里没有本仓库的 `README.md`，先进入正确目录，再继续后续命令。

## 路线 A：macOS 或 Linux

以下命令适用于常见的 bash/zsh 环境。本批次在当前 macOS 环境进行了实际检查；Linux
语法相同，但没有在本批次声称逐发行版运行通过。

先查看默认的 Python 3：

```bash
python3 --version
python3 -c 'import sys; assert sys.version_info >= (3, 11), sys.version; print(sys.executable)'
```

第一条输出版本。第二条同时检查版本下限并打印真实解释器路径。如果版本低于 3.11，
断言会失败并显示当前版本；不要通过删除断言来假装满足要求。

接着创建虚拟环境，并直接调用其中的 Python：

```bash
python3 -m venv .venv
.venv/bin/python -c 'import sys; print(sys.executable)'
```

这里不强制执行 `source .venv/bin/activate`。直接写解释器路径虽然稍长，却能清楚表明
正在使用哪个环境，也能减少“终端提示符看似激活、实际解释器仍不对”的困惑。

最后验证 UTF-8 中文文件读写。命令会创建一个临时文件，读回内容后立即删除：

```bash
.venv/bin/python -c 'from pathlib import Path; p=Path("rag_smoke_test.txt"); p.write_text("RAG 环境正常\n", encoding="utf-8"); print(p.read_text(encoding="utf-8").strip()); p.unlink()'
```

预期看到：

```text
RAG 环境正常
```

如果命令中途失败，临时文件可能仍然存在。确认它不含敏感信息后可以手动删除。

## 路线 B：Windows PowerShell

Windows 常用 Python Launcher 的 `py -3` 选择已安装的 Python 3。以下命令经过语法审阅，
但当前批次没有 Windows 执行环境，因此不能声称已经在 Windows 实机运行。

```powershell
py -3 --version
py -3 -c "import sys; assert sys.version_info >= (3, 11), sys.version; print(sys.executable)"
```

创建虚拟环境，并直接调用其中的解释器：

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -c "import sys; print(sys.executable)"
```

验证 UTF-8 中文文件读写：

```powershell
.\.venv\Scripts\python.exe -c "from pathlib import Path; p=Path('rag_smoke_test.txt'); p.write_text('RAG 环境正常\n', encoding='utf-8'); print(p.read_text(encoding='utf-8').strip()); p.unlink()"
```

预期输出同样是 `RAG 环境正常`。直接调用 `.venv` 中的解释器不依赖 PowerShell 的脚本
激活策略；不要为了激活虚拟环境而随意降低整台电脑的执行策略。

如果系统没有 `py` 命令，但 `python --version` 显示 3.11 或更高，可以把上述 `py -3`
替换为 `python`。替换后仍要运行版本断言，不能只根据安装程序名称判断版本。

## 怎样判断通过

四项都满足才算完成本章的最小环境检查：

| 检查 | 通过证据 | 失败时先看什么 |
|---|---|---|
| 仓库位置 | 文件列表包含仓库入口和目录 | 当前目录、路径是否含空格、是否进入了错误副本 |
| Python 版本 | 版本断言无错误，版本至少为 3.11 | 实际解释器路径、系统是否同时安装多个 Python |
| 虚拟环境 | 打印路径位于当前仓库的 `.venv` 内 | 创建权限、磁盘空间、调用路径 |
| UTF-8 文件 | 输出 `RAG 环境正常`，临时文件被清理 | 当前目录写权限、编码、命令引号 |

把实际输出保存到自己的学习记录中，不要把机器用户名、家庭目录、访问令牌或公司内部
路径公开提交到仓库。

## 常见失败和最小处理

### 找不到 `python3` 或 `py`

这表示命令入口不存在或不在 PATH 中，不代表“RAG 代码有问题”。先确认 Python 是否
安装、安装位置和操作系统推荐的启动方式。安装时优先使用 Python 官方渠道或组织批准
的软件源，不要从不明下载站获取解释器。

### 版本低于 3.11

保留旧环境，不要直接删除正在被其他项目使用的 Python。安装一个兼容版本，为本教程
单独创建 `.venv`，再通过打印 `sys.executable` 确认使用的是新环境。

### 虚拟环境创建失败

检查完整错误的第一处原因，常见类别包括权限不足、磁盘空间不足、Python 安装缺少 venv
组件或安全软件阻止写入。不要因为看到最后一行“失败”就猜测需要重装所有依赖。

### 中文输出乱码

先区分“文件内容编码错误”和“终端显示错误”。本章显式使用 UTF-8 写入和读取；如果
Python 读回内容正确但终端显示异常，问题更可能在终端字体或编码配置。

### 网络、代理或证书报错

本章不访问网络。如果执行上述标准库命令却出现网络问题，说明你运行的可能不是本章
命令，或环境中存在额外启动脚本。先回到最小命令，不要在这一步配置模型 API。

## 记录模板

```text
操作系统：
终端：
Python 版本：
解释器路径：
虚拟环境路径：
UTF-8 输出：
第一条失败信息（如有）：
处理动作：
```

记录事实，不要把“我的电脑应该没问题”当作证据。

## 自测

1. 为什么冒烟测试不安装 RAG 框架？
2. `python3 --version` 与打印 `sys.executable` 分别告诉你什么？
3. 为什么直接调用 `.venv` 中的 Python 有助于排错？
4. 当前批次可以声称 Windows 命令已经实机验证吗？为什么？
5. 中文显示异常时，怎样区分文件编码和终端显示问题？

## 本章状态与导航

- 文本状态：`static-checked`；独立技术、初学者和编辑审查待后续门禁。
- macOS/bash-zsh 路线：本批次已运行最小命令；完整输出见本次任务验证记录。
- Linux 路线：语法适用性检查，未在本批次逐发行版运行。
- Windows PowerShell 路线：语法审阅，未在本批次实机运行。
- 统一冒烟脚本和环境流程图：计划中，未在本章声称已交付。
- 本章摘要：[summaries/chapters/00-04.md](../../summaries/chapters/00-04.md)

- 上一站：[00-03 学习准备度检查](03-readiness-check.md)
- 下一站：[00-05 安全基线](05-security-baseline.md)
- 返回：[00 前言索引](知识库/RAG/docs/00-preface/README.md)｜[文档总索引](../README.md)
