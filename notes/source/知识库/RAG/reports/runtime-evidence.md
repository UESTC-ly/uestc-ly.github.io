# 运行时与能力原始证据

本文件把 Leader 终端中实际观察到的关键输出持久化。模型启动行来自 OMX 启动命令
的终端输出；团队关闭后不能仅靠仓库重新生成，因此证据等级是“受控终端转录”，
不是可独立重放的服务证明。

## OMX 模型与并行启动

四轮团队分别为：

1. 课程设计 `rag-beginner-tutorial-9ad978cb`；
2. 共享规范审查 `review-the-committed-9ad978cb`；
3. 定向复核 `re-review-only-the-pr-9ad978cb`；
4. 最终最小复核 `final-minimal-b0-re-r-9ad978cb`。

四轮均使用：

```text
OMX_TEAM_WORKER_LAUNCH_ARGS='--model gpt-5.6-sol -c model_reasoning_effort="xhigh"'
```

每轮三个 worker 的启动解析分别输出一次以下模式，共观察到十二次：

```text
actual_model=gpt-5.6-sol thinking_level=xhigh model_source=env reasoning_source=explicit inherited_parent_model=no
```

tmux pane 标题同时显示 `gpt-5.6-sol xhigh`。四轮均有三个独立 worker pane；任务和
mailbox 的原始结论转录在 `reports/review-evidence.md`。

## 试点实现团队

第五轮团队 `implement-the-approve-9ad978cb` 使用相同显式 launch args，两个 worker
启动解析均显示 `actual_model=gpt-5.6-sol` 与 `thinking_level=xhigh`。worker-1 负责
README/02-01/D01，worker-2 负责 minimal-rag 与 unit/smoke tests。

自动分解把原 task 2 owner 错写为 worker-1；Leader 在任何代码写入前关闭该行政重复，
创建 owner=worker-2 的 task 3。最终终态为 `pending=0, in_progress=0, completed=3,
failed=0`，其中真实交付任务为 1 和 3。shutdown 的两个 worktree merge 均没有额外
diff；临时 checkpoint/merge 历史随后整理为语义化 Lore commits。

## B0 作者环境命令（历史捕获）

2026-07-17 执行：

```text
$ python3 --version
Python 3.13.3
$ pytest --version
pytest 9.0.3
$ docker --version
Docker version 28.1.1, build 4eba377327
$ command -v mmdc
mmdc: NOT FOUND
$ git rev-parse HEAD
18d6606ffb9f003acdbc11c74497d4d9d2a83767
```

这些输出只证明 CLI 可调用；不证明 Docker daemon、教程测试、Mermaid 渲染或外部
服务通过。

## 网络证据

2026-07-17 对官方 Python 文档的复核命令：

```text
$ curl -L --max-time 15 -sS -o /dev/null -w 'url=%{url_effective} http_code=%{http_code}' https://docs.python.org/3/
curl: (35) LibreSSL SSL_connect: SSL_ERROR_SYSCALL in connection to docs.python.org:443
url=https://docs.python.org/3/ http_code=000
```

最终最小复核中，worker-3 对同一目标执行同一 curl，命令成功并返回 HTTP 200。两次
结果共同证明访问状态不稳定：不能再写成“当前不可用”，也不能把单次 200 外推为
官方资料持续可访问。后续写作批次仍必须逐项实际检索来源并登记。

## 最终 B0 团队终态

2026-07-17T05:26:22Z，最终团队状态为：

```text
phase=complete pending=0 in_progress=0 completed=3 failed=0 dead_workers=0
```

随后正常 shutdown；三个只读 worktree 均无 diff，leader HEAD 保持
`710d644689d93e2963c1eae15ef9c76f1e8cfeaf`。这证明最终结论来自对同一提交的独立
只读复核，而不是 reviewer 写入后的自审。

## 已知 OMX 限制

- 自动任务分解两次把 worker-2/3 的身份任务错误赋给 worker-1；Leader 创建显式任务
  并把原任务作为行政重复关闭。
- 第一轮长 delta 多次遇到 Responses 传输中断，最终通过小于 2,000 字的 mailbox
  报告恢复。
- 第二轮 worker-1 启动进入 hooks 菜单，worker-3 遇到权限提示；均由 Leader 观察
  后显式恢复，未把未启动 pane 计为有效审查。
