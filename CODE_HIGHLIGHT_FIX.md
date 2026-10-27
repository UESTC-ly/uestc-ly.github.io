# 🔧 代码高亮修复

## 问题描述

原版代码高亮脚本在处理包含 `<`、`>`、`&` 等特殊字符的代码时，会产生嵌套 `<span>` 标签混乱，导致渲染错误。

**症状**：
```html
<!-- 错误的渲染结果 -->
<span <span <span <span class="keyword">class</span> = "keyword">class</span>
```

## 根本原因

1. 原逻辑先转义 HTML 字符（`< → &lt;`）
2. 然后用正则替换应用高亮（会匹配到已转义的字符）
3. 导致生成的 `<span>` 标签与转义字符混合，造成 HTML 结构破坏

## 修复方案

**新的高亮逻辑**（`assets/js/code-highlight.js`）：

1. **保护阶段**：先提取注释和字符串，用占位符替换
   ```javascript
   // 保护注释
   text = text.replace(/(\/\*[\s\S]*?\*\/|\/\/[^\n]*|#[^\n]*)/g, (match) => {
     protected[i] = `<span class="comment">${escapeHtml(match)}</span>`;
     return `___PROTECTED_${i}___`;
   });
   ```

2. **转义阶段**：统一转义剩余的 HTML 特殊字符
   ```javascript
   text = escapeHtml(text);  // 一次性转义所有 <, >, &, ", '
   ```

3. **高亮阶段**：在已转义的纯文本上应用语法高亮
   ```javascript
   // 高亮关键字
   keywords.forEach(kw => {
     text = text.replace(/\b(keyword)\b/gi, '<span class="keyword">$1</span>');
   });
   ```

4. **还原阶段**：将占位符替换回已高亮的注释和字符串
   ```javascript
   text = text.replace(/___PROTECTED_\d+___/g, (match) => protected[i]);
   ```

## 核心改进

| 方面 | 旧逻辑 | 新逻辑 |
|------|--------|--------|
| 转义时机 | 先转义，后正则替换（会匹配转义字符） | 先保护，再转义，避免冲突 |
| 注释/字符串 | 与代码混合处理 | 单独保护，避免内容被误高亮 |
| HTML安全 | 手动转义 `<`、`>` | 完整转义所有特殊字符 |
| 嵌套问题 | 会产生嵌套 `<span>` | 用占位符隔离，不会嵌套 |

## 部署方式

**好消息**：不需要修改任何 HTML 文件！

1. 修改后的 `code-highlight.js` 会在页面加载时自动应用
2. 浏览器会重新执行新的高亮逻辑
3. 所有 892 个笔记页面会自动修复

**推送修复**：
```bash
cd "/Users/li/Library/Application Support/Claude-3p/local-agent-mode-sessions/23103d5c/00000000/local_f3ae9b9b-a608-4fcd-a9a6-c0b7950e4c1b/outputs/uestc-ly.github.io"

git add assets/js/code-highlight.js
git commit -m "修复代码高亮嵌套标签问题

- 重构高亮逻辑：保护 → 转义 → 高亮 → 还原
- 避免注释和字符串内容被误高亮
- 修复包含 <, >, & 的代码渲染错误"

git push origin main
```

## 测试验证

推送后访问包含特殊字符的代码页面（如 C++ 模板代码），检查：

- [ ] `map<string, int>` 正确显示（不会变成 `<span>` 嵌套混乱）
- [ ] `cout &lt;&lt;` 正确转义为 `cout <<`
- [ ] 注释中的 `<tag>` 不会被当作HTML标签
- [ ] 字符串中的 `"Hello <World>"` 正确高亮
- [ ] 关键字、函数名、类名颜色正确
- [ ] 复制按钮功能正常

## 技术细节

### 占位符机制
使用唯一占位符 `___PROTECTED_N___` 标记受保护的片段：
- 保证不会与实际代码内容冲突
- 按顺序编号，还原时不会错位
- 在最后阶段才替换回来，避免被正则匹配

### 转义函数
```javascript
function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')   // 必须最先转义
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
```

---

**修复完成时间**：2026-10-27  
**影响范围**：所有 892 个笔记页面  
**用户影响**：无需重新加载缓存，浏览器会自动执行新脚本
