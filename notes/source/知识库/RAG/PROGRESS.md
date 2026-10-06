# 项目进度

更新时间：2026-07-17（Asia/Shanghai）

## 总体状态

| 阶段 | 状态 | 当前证据 | 进入下一阶段条件 |
|---|---|---|---|
| 能力与约束检查 | verified | reports/capability-audit.md、reports/runtime-evidence.md、最终三 lane PASS | 已满足 |
| 课程设计 | verified | PROJECT_PLAN.md、四轮独立审查与修复记录 | 已满足 |
| 共享规范 | verified | 指定规范文件、扩展证据文件、结构脚本与最终三 lane PASS | 已满足 |
| 试点 | reviewing | README、02-01、minimal-rag、D01、12 项 unit/smoke PASS | 四类独立审查全部 PASS |
| 正式章节批次 | reviewing | 00-08 共 54 章正文与 54 份摘要 | 持续写作；独立审查后再升级 |
| 两个综合项目 | pending | 无 | 相关基础、评估、安全和生产模块完成 |
| 全局集成 | pending | 无 | 所有内容批次 terminal |
| 最终交付 | pending | 无 | AC01-AC22 全部有验收证据 |

## 本批次完成内容

- 已有文件：00 前言 5 章、01 基础 6 章、02 原理 5 章，以及对应 16 份章节摘要。
- 本轮新增：03 数据摄取 7 章、04 文本切分 6 章、05 嵌入向量 6 章、06 索引 6 章、07 检索 8 章、08 重排 5 章，以及对应 38 份章节摘要和 6 个部分索引。
- 更新文件：根/文档/摘要导航、Manifest、Progress；试点代码与报告保持原有证据。
- 已写章节：54，全部为 reviewing；作者侧轻量静态检查不等于独立技术、代码、初学者或编辑审查。
- 新增代码：1 个标准库离线示例；新增测试 2 个文件、12 个测试用例。
- 新增图表：D01 已创建并 static-checked；未渲染。D02-D20 仍为 planned。

## 验证结果

- 技术审查：第二轮 FAIL 和第三轮定向 FAIL 均已修复；最终对 commit `710d644` 的独立 re-review PASS。
- 初学者/编辑审查：Manifest schema、依赖、试点顺序、摘要和来源路径回归项在最终 re-review 中 PASS。
- 证据审查：`./scripts/verify-planning.sh` 连续执行 PASS，计数为 `delivery=30 markdown=29 ids=156 AC=22 BASIC=7 CAP=2 D=20 roles=15 specification_lines=1618`。
- 试点结构回归：新增文件登记后 verifier PASS，计数为 `delivery=42 markdown=37 ids=156 AC=22 BASIC=7 CAP=2 D=20 roles=15 specification_lines=1618`。
- 代码验证：集成树执行 unit + smoke 共 12 项 PASS；确定性 CLI 重放 PASS。
- Mermaid 检查：D01 静态规则和人工阅读 PASS；`mmdc` 不存在，不声称渲染通过。
- 链接检查：试点当前相对链接目标检查 PASS；planned 路径不计作通过。
- 03-08 写作批次：作者侧文件数、单一 H1、尾随空白和 lane-local 链接检查 PASS；未据此升级独立审查状态。

## 当前进度

- 已完成教学草稿：00 至 08 共 54 章，形成从准备度、RAG 原理到摄取、切分、嵌入、索引、检索和重排的连续主线。
- 已验证：最终最小 re-review 的三项任务均为 completed/PASS，团队随后正常 shutdown，三个 worktree 均无差异。
- 审查中：现有正文与试点仍保持 reviewing；精细审查延后补齐，不阻塞下一批写作。
- 下一写作入口：09 上下文构建与生成。

## 下一批次

- 计划处理：继续撰写 09 上下文构建与生成；现有 03-08 后续补代码、图表和独立审查证据。
- 所需依赖：默认只使用 Python 标准库和 pytest；不新增教程依赖。
- 主要风险：Responses 传输不稳定、Mermaid 无真实渲染器、未来框架 API 版本变化。
