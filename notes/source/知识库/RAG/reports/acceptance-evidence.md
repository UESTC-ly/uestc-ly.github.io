# 验收证据报告

当前状态：课程设计和共享规范阶段。

`ACCEPTANCE_MATRIX.md` 中的 `planned` 不是完成证据。最终报告将逐项引用文件、测试、
图表、审查和运行结果；任何缺失或间接证据保持未完成。

## 当前结构证据

2026-07-17 的作者侧检查结果：

- 29 个当前交付 Markdown 文件存在且非空；运行时 `AGENTS.md` 不属于教程交付物。
- Manifest 覆盖所有当前非 `.omx` 交付文件。
- requirement-id 无重复。
- AC01-AC22 共 22 项，BASIC 7 项，CAP 2 项，D01-D20 共 20 项。
- `PROJECT_PLAN.md` 登记 15 个职责不同的 Agent 角色。
- 每个当前 Markdown 文件恰好一个一级标题，无行尾空白。

这些结果证明规划结构一致，不证明任何 planned 章节、代码、图或最终 AC 已完成。

第四轮最终最小 re-review 对 commit `710d644` 返回三 lane PASS，因此 B0 共享
`ART-*`、能力约束 `X-CAP-01` 以及已有的 AC15/AC16 状态可以升级为 `verified`。这仍
不是 AC01-AC22 的最终整体通过结论。

## 试点集成证据

当前已创建根 README、02-01、minimal-rag、D01、unit/smoke tests 和试点报告。集成树
pytest 为 12 passed，确定性 CLI 重放 PASS，相对链接目标缺失为 0，D01 只标
`static-checked`/未渲染。因此 BASIC-01、D01 与 X-EARLY-EVAL-01 可进入 reviewing，
但在独立四类审查和 BASIC-01/10-01 完整回访前不能升级为 verified/complete。

试点登记后的结构命令输出：

```text
PASS delivery=42 markdown=37 ids=156 AC=22 BASIC=7 CAP=2 D=20 roles=15 specification_lines=1618
```

## 可复现命令

2026-07-17 修复后的工作树执行：

```text
$ ./scripts/verify-planning.sh
PASS delivery=30 markdown=29 ids=156 AC=22 BASIC=7 CAP=2 D=20 roles=15 specification_lines=1618
```

脚本源在 `scripts/verify-planning.sh`；它动态检查 Manifest 覆盖、ID、硬性数量、角色、
一级标题、行尾空白、规格行数和 `git diff --check`。最终提交后应再次执行并记录新的
commit ID。

故障注入：在仓库根临时创建含两个一级标题的运行时 `AGENTS.md` 后再次执行，仍返回
完全相同的 PASS；文件随后安全移动到 `/tmp`。这证明 verifier 不再把 OMX 控制文件
计入教程交付或 Markdown H1 检查。
