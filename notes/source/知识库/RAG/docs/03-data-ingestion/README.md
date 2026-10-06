# 03 数据摄取：把原始资料变成可信输入

数据摄取（data ingestion）位于 RAG 的索引阶段最前面。它接收文件或业务记录，识别
格式，提取文字与结构，清理内容，并补上来源、权限和版本信息。后面的切分、向量化与
检索只能处理它收到的结果；如果摄取阶段丢了表头、页码或访问范围，后续步骤通常无法
凭空恢复。

本部分不把“能读出一段文字”当成完成。一个可追踪的摄取结果至少要回答：内容是什么、
来自哪里、由哪个版本产生、允许谁使用，以及失败时保留了哪些证据。

## 学完后你能做什么

- 用统一的 `Document` 心智模型描述不同来源；
- 区分读取来源的 Loader 与解释格式的 Parser；
- 为 PDF、扫描件、网页和 Office 文件选择有边界的处理路径；
- 在清洗时保留结构、来源和可复现性；
- 设计权限、血缘、版本、增量更新与删除所需的元数据；
- 识别不可信文件、OCR 误差、重复内容和旧版本残留带来的风险。

## 推荐阅读顺序

1. [03-01 文档模型、Loader 与 Parser](01-document-model-loaders-and-parsers.md)
2. [03-02 PDF、OCR、图片与不可信文件](02-pdf-ocr-images-and-untrusted-files.md)
3. [03-03 Markdown、HTML 与 Office 文件](03-markdown-html-and-office.md)
4. [03-04 表格、布局与结构](04-tables-layout-and-structure.md)
5. [03-05 清洗、编码与去重](05-cleaning-encoding-and-deduplication.md)
6. [03-06 元数据、权限与来源血缘](06-metadata-permissions-and-provenance.md)
7. [03-07 版本、增量更新与删除](07-versioning-incremental-update-and-deletion.md)

03-01 是共同入口。03-02 和 03-03 介绍不同格式，03-04 说明为什么不能只保留纯文本；
03-05 至 03-07 再处理清洗、安全和生命周期。阅读完本部分后，再进入 04 文本切分。

## 本批次的诚实边界

本部分提供教学正文和设计检查表。计划中的 `documents.py`、格式适配器、清洗代码、
权限契约、D04/D16/D17 图表及其测试尚未在本批次实现，因此正文不会声称这些代码或
图表已经运行或验证。真实系统仍需用自己的文件样本、权限模型和失败预算做验证。

## 返回

- 前置：[02 RAG 原理](../02-rag-principles/README.md)
- 教程总索引：[文档索引](../README.md)
