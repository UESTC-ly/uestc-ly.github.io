# 作者侧验证脚本

这些脚本验证教程仓库本身，不是读者运行 RAG 所需的依赖。

- `verify-planning.sh`：检查当前规划文件、Manifest 覆盖、requirement-id、硬性数量、
  Agent 角色、Markdown 一级标题、行尾空白和 Git whitespace。

运行：

```bash
./scripts/verify-planning.sh
```

需要仓库作者环境提供 Bash、Git 和 ripgrep (`rg`)。该要求不会进入教程运行依赖。
