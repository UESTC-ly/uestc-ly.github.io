# 初学者体验审查记录

Reviewer：独立 worker-3，`gpt-5.6-sol xhigh`。范围包括零基础路径、术语门禁、难度、
导航、跨平台复现和实际蓝图 delta。

主要发现：缺少独立准备度/环境冒烟路径，依赖图没有四类能力标签，Advanced RAG
曾被设为统一硬前置，依赖真源不明确，示例数据和跨平台命令没有门禁。

已纳入的修复：

- 00 增加 readiness、environment smoke 和 security baseline。
- `DEPENDENCY_MATRIX.md` 使用四类依赖并移除 Advanced RAG 的统一硬前置。
- 试点和 10-01 明确为“直觉试跑/完整回访”。
- `pyproject.toml` 被指定为依赖真源。
- Manifest 增加难度、用时、费用、术语、摘要和导航字段。
- 增加 `DATA_LICENSES.md` 与跨平台 requirement-id。

阶段结论：共享规范需要结构与链接复核，试点保持 pending。

## 第二轮共享规范审查

commit `18d6606` 的 Beginner Experience + Managing Editor 返回 FAIL：Manifest 扩展
字段未落表、10-07/15 形成 Streaming 回指、B1/B2 顺序违反准备度依赖、摘要与来源
路径漂移。当前工作树已建立独立扩展表、移除回指、把最低准备度纳入 B1 并统一
路径。

## 最终 B0 初学者结论

第四轮对 commit `710d644` 的独立复核确认上述回归项全部 PASS：扩展 Manifest 字段已
落表、BASIC-07 不再形成生产模块回指、Advanced RAG 明确为选修、B1/B2 顺序符合
readiness -> 原理直觉 -> pilot，摘要与来源路径一致。B0 初学者门禁为 `verified`；
试点内容本身仍为 pending，必须另做真实首次运行与导航走查。
