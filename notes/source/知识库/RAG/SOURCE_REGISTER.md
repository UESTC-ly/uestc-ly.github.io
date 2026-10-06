# 版本与来源登记

可变事实必须先登记再写入正文。章节内仍需就近引用；本表不能替代读者可见来源。

## 证据等级

1. 官方文档或规范。
2. 原始论文。
3. 官方代码仓库或发布记录。
4. 官方技术博客。
5. 权威研究机构资料。
6. 可靠二手资料，仅用于补充，不作为关键可变事实的唯一来源。

## 登记字段

| claim-id | chapter path | claim scope | product/paper | applicable version | checked-at | official source | evidence type | recheck-before-release | status |
|---|---|---|---|---|---|---|---|---|---|
| SRC-PENDING-001 | docs/11-frameworks/02-langchain-case-study.md | 框架 API 与最低支持版本 | 待写作批次核查 | 待定 | 未核查 | 待定 | official docs/repo | yes | planned |
| SRC-PENDING-002 | docs/11-frameworks/03-llamaindex-case-study.md | 框架 API 与最低支持版本 | 待写作批次核查 | 待定 | 未核查 | 待定 | official docs/repo | yes | planned |
| SRC-PENDING-003 | docs/15-production/01-api-sync-async-and-streaming.md | API 框架接口与兼容版本 | 待写作批次核查 | 待定 | 未核查 | 待定 | official docs/repo | yes | planned |

## 规则

- `checked-at` 使用 ISO 日期，记录实际访问日期，不用当前日期代填未查事实。
- 性能、价格和产品限制必须说明地区、配置、数据和时间；无法稳定复核时避免精确数值。
- 论文术语要记录原始语境，不能把后续产品实现等同于论文唯一含义。
- 发布前对 `recheck-before-release=yes` 的行重新核查。
