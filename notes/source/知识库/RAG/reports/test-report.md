# 测试报告

状态：`pilot-unit-and-smoke-passed-review-pending`。

## 试点测试

2026-07-17 在 Leader 集成树执行：

```text
$ PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -p no:cacheprovider \
    tests/unit/test_minimal_rag.py tests/smoke/test_minimal_rag_cli.py -q
............                                                             [100%]
12 passed in 0.14s
```

覆盖：正常闭环与引用位置、空语料、空查询、Top-K 越界、零向量、空文档、零向量余弦
边界、CLI 确定性、JSON 无答案和 CLI 错误退出。命令不联网、不读取 API Key。

本结果只证明当前试点在 Python 3.13.3 上通过。当前没有 Python 3.11 解释器和 Windows
环境，不能声称已经覆盖全部目标平台。

## 规划 verifier 回归

作者侧规划验证不是教程测试。试点新增文件登记后执行 `./scripts/verify-planning.sh`，
返回 `PASS delivery=42 markdown=37 ids=156 AC=22 BASIC=7 CAP=2 D=20 roles=15
specification_lines=1618`。该结果与本节的 pytest 证据分开记录。

同日 B0 使用临时两-H1 `AGENTS.md` 做故障注入，verifier 仍返回
`delivery=30 markdown=29 ids=156`，确认运行时控制文件排除规则生效。
