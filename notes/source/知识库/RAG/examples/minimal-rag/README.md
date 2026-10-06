# 纯 Python 最小 RAG

这个示例用 Python 标准库展示一个可观察的最小 RAG 流程。它完全离线、无需 API Key、
不访问网络，也不会产生费用。同样的输入会得到同样的输出。

> 教学边界：这里用词频稀疏向量和抽取式回答帮助初学者看清数据流，不代表所有 RAG
> 技术，也不保证回答永远正确。真实系统仍需要更严格的检索、生成、评估与安全设计。

## 你会看到什么

`minimal_rag.py` 把每个阶段都放在可定位的函数或数据对象里：

| 阶段            | 代码位置                              |
| ------------- | --------------------------------- |
| 语料（Corpus）    | `DEFAULT_CORPUS` 与 `Document`     |
| 切分（Chunk）     | `chunk_corpus()` 与 `Chunk`        |
| 确定性 Embedding | `embed()`                         |
| 相似度           | `cosine_similarity()`             |
| Top-K 检索      | `retrieve()`                      |
| 上下文           | `build_context()`                 |
| Prompt        | `build_prompt()`                  |
| 回答            | `generate_answer()`               |
| 引用位置          | `Citation.start` / `Citation.end` |
| 完整结果          | `run_rag()` 返回的 `RAGResult`       |

引用位置使用 Python 字符串的半开区间 `[start, end)`；因此可以用
`document.text[start:end]` 还原被引用的原文。

## 运行

要求 Python 3.11 或更高版本。无需安装运行依赖。

macOS / Linux 在仓库根目录运行：

```bash
python3 examples/minimal-rag/minimal_rag.py --query "RAG 如何回答问题？" --top-k 2
```

Windows PowerShell 运行：

```powershell
py -3.11 examples/minimal-rag/minimal_rag.py --query "RAG 如何回答问题？" --top-k 2
```

查看便于程序读取的所有中间结果：

```bash
python3 examples/minimal-rag/minimal_rag.py --query "什么是 Chunk？" --top-k 3 --json
```

文本输出会依次显示查询、语料数、Chunk 数、查询 Embedding、Top-K 结果、上下文、
Prompt、回答和引用位置。若查询只能得到零向量或没有正相关 Chunk，程序会明确拒答，
而不是编造答案。

## 测试

测试依赖仓库作者环境中已有的 `pytest`，不属于示例运行依赖：

```bash
python3 -m pytest tests/unit/test_minimal_rag.py tests/smoke/test_minimal_rag_cli.py -q
```

覆盖正常检索、空语料、空查询、Top-K 越界、零向量/无答案和 CLI 成功/拒答路径。

## 常见错误

- `query 不能为空`：`--query` 不能是空字符串或只有空白。
- `top_k 必须是正整数`：`--top-k` 必须大于零。
- “未找到足够相关的资料”：当前语料没有正相关 Chunk；这是一条正常的拒答路径。

验证状态：`unit-passed` 仅在仓库测试真实通过后由项目报告记录；本 README 不替代测试证据。
