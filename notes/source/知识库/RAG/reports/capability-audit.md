# 能力与约束审计

核查日期：2026-07-16 至 2026-07-17。

| 能力 | 真实结论 | 当前证据 | 限制 |
|---|---|---|---|
| 独立多 Agent | 支持 | B0 四轮 3-worker，加试点一轮 2-worker；`review-evidence.md` 与 pilot report 记录输出 | 自动分解曾错误分配 owner，已记录并人工纠正 |
| 指定模型 | 支持 | B0 十二次加试点两次启动解析显示 `actual_model=gpt-5.6-sol`；pane 显示同一模型 | 原生 subagent 表面不能选择模型，因此未用于内容/审查 |
| xhigh | 支持 | 共十四次启动解析显示 `thinking_level=xhigh` 且 `reasoning_source=explicit`；pane 显示 `xhigh` | worker 内部环境变量本身不是充分证据，以 leader 启动解析和 pane 为准 |
| 并行执行 | 支持 | worker-1/2/3 pane 同时运行并返回独立报告 | Responses 传输多次断开，delta 最终使用紧凑 mailbox 报告恢复 |
| 文件创建和修改 | 支持 | Git 中存在课程蓝图与共享规范 | worktree 需要干净 Git 基线 |
| Python | 支持 | `python3 --version` 为 3.13.3 | 教程兼容目标仍为 3.11+，不能把作者版本当最低要求 |
| 测试 | 支持 | pytest 9.0.3；试点 unit/smoke 12 passed | 只覆盖试点，不代表完整教程测试通过 |
| Docker | CLI 可用 | `docker` 命令存在 | 未验证 daemon、镜像构建或部署环境 |
| Mermaid 校验 | 不支持真实渲染 | `mmdc` 未安装 | 只能做静态规则检查；不得声称渲染通过 |
| 官方资料访问 | 不稳定 | 2026-07-17 早先 curl 返回 SSL_ERROR_SYSCALL/http_code=000，最终复核同一目标返回 HTTP 200 | 单次成功不代表持续可用；后续仍须逐项实际检索 |

命令和捕获输出见 `reports/runtime-evidence.md`。第四轮最终最小复核的独立证据审查
PASS，因此本报告的 B0 状态为 `verified`；这不提升未执行能力的验证等级。

## Agent 分工证据

- worker-1：Curriculum Architect，产出并提交 `PROJECT_PLAN.md` 的课程蓝图来源。
- worker-2：Technical Reviewer，完成需求级审查和实际蓝图技术 delta。
- worker-3：Beginner Experience + Managing Editor，完成需求级审查和实际蓝图教学/编辑 delta。
- Leader：解决 task owner/lease 缺陷，整合审查，不把 worker-1 的错误 reviewer task claim 当成独立审查。

## 不能声称的事项

当前不能声称完整教程代码通过、Mermaid 渲染通过、Docker 部署通过、云环境验证通过、
外部框架 API 已核查或全部章节完成。可以声称的代码证据仅限当前试点 12 项测试。
