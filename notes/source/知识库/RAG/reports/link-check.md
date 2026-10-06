# 链接检查报告

状态：`static-pass-current-files`。

核查日期：2026-07-17。

- Markdown 链接扫描：当前 37 个受 Git 管理的交付 Markdown 文件包含 34 个相对链接；
  排除代码块、行内代码、`.omx/`、`.pytest_cache/` 和运行时 `AGENTS.md` 后，目标缺失为 0。
- 试点导航覆盖根 README -> 02-01 -> minimal-rag -> unit/smoke，以及 D01 和各级索引。
- Manifest 路径检查：试点新增文件已登记；最终以 `./scripts/verify-planning.sh` 输出为准。
- planned 的后续章节路径不作为当前链接通过证据。

本结果只覆盖当前文件，不外推到试点或最终仓库。

可复现入口：`./scripts/verify-planning.sh` 与报告中记录的相对链接扫描。链接脚本只验证
路径存在，不验证未来锚点语义或外部 URL 可用性。
