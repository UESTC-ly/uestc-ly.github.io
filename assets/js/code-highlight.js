/**
 * 代码语法高亮增强脚本
 * 自动检测代码语言并添加语法高亮
 */

(function() {
  'use strict';

  // 代码语言检测规则
  const languagePatterns = {
    python: /\b(def|class|import|from|if|elif|else|for|while|return|print|self)\b/,
    javascript: /\b(const|let|var|function|=>|console\.log|async|await)\b/,
    cpp: /\b(#include|int|void|class|namespace|std::)\b|iostream/,
    c: /\b(#include|int|void|struct|printf|scanf)\b|stdio\.h/,
    java: /\b(public|private|class|static|void|System\.out)\b/,
    bash: /^\$|^#\s|\becho\b|\bcd\b|\bls\b/m,
    sql: /\b(SELECT|FROM|WHERE|INSERT|UPDATE|DELETE|CREATE|TABLE)\b/i,
    json: /^\{[\s\S]*\}$|^\[[\s\S]*\]$/,
    html: /<[a-z][\s\S]*>/i,
    css: /\{[\s\S]*:[^:]+;/
  };

  // 检测代码语言
  function detectLanguage(code) {
    // 优先从class属性检测
    const codeBlock = code.parentElement;
    if (codeBlock && codeBlock.className) {
      const match = codeBlock.className.match(/language-(\w+)/);
      if (match) return match[1];
    }

    // 自动检测
    const text = code.textContent;
    for (const [lang, pattern] of Object.entries(languagePatterns)) {
      if (pattern.test(text)) {
        return lang;
      }
    }
    return 'text';
  }

  // 应用语法高亮
  function applySyntaxHighlight(code) {
    // 获取原始文本（可能已包含HTML实体）
    let text = code.textContent;

    // 如果文本为空，跳过
    if (!text.trim()) return;

    // 存储需要保护的片段（注释和字符串）
    const protected = [];
    let protectedIndex = 0;

    // 1. 保护注释（避免注释内容被高亮）
    text = text.replace(/(\/\*[\s\S]*?\*\/|\/\/[^\n]*|#[^\n]*)/g, (match) => {
      const placeholder = `___PROTECTED_${protectedIndex}___`;
      protected[protectedIndex] = `<span class="comment">${escapeHtml(match)}</span>`;
      protectedIndex++;
      return placeholder;
    });

    // 2. 保护字符串
    text = text.replace(/("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|`(?:[^`\\]|\\.)*`)/g, (match) => {
      const placeholder = `___PROTECTED_${protectedIndex}___`;
      protected[protectedIndex] = `<span class="string">${escapeHtml(match)}</span>`;
      protectedIndex++;
      return placeholder;
    });

    // 3. 转义剩余的HTML字符
    text = escapeHtml(text);

    // 4. 高亮关键字（在非保护区域）
    const keywords = [
      // Python
      'def', 'class', 'import', 'from', 'if', 'elif', 'else', 'for', 'while', 'return', 'in', 'and', 'or', 'not', 'try', 'except', 'finally', 'with', 'as', 'lambda', 'yield', 'async', 'await',
      // JavaScript
      'const', 'let', 'var', 'function', 'return', 'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break', 'continue', 'new', 'this', 'extends', 'export',
      // C/C++
      'int', 'float', 'double', 'char', 'void', 'bool', 'string', 'auto', 'const', 'static', 'public', 'private', 'protected', 'struct', 'namespace', 'using', 'template', 'typename',
      // SQL
      'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'TABLE', 'INDEX', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'ON', 'AND', 'OR', 'NOT', 'NULL', 'IS', 'IN'
    ];

    keywords.forEach(kw => {
      const regex = new RegExp(`\\b(${kw})\\b`, 'gi');
      text = text.replace(regex, '<span class="keyword">$1</span>');
    });

    // 5. 高亮数字
    text = text.replace(/\b(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?\b/g, '<span class="number">$1$2</span>');

    // 6. 高亮函数名（word后跟左括号）
    text = text.replace(/\b([a-zA-Z_]\w*)\s*(?=\()/g, '<span class="function">$1</span>');

    // 7. 高亮类名（大写开头的单词）
    text = text.replace(/\b([A-Z][a-zA-Z0-9_]*)\b/g, '<span class="class-name">$1</span>');

    // 8. 还原保护的片段
    for (let i = 0; i < protected.length; i++) {
      text = text.replace(`___PROTECTED_${i}___`, protected[i]);
    }

    code.innerHTML = text;
  }

  // HTML转义辅助函数
  function escapeHtml(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // 添加复制按钮
  function addCopyButton(pre) {
    const button = document.createElement('button');
    button.className = 'copy-button';
    button.textContent = '复制';
    button.setAttribute('aria-label', '复制代码');

    button.addEventListener('click', async () => {
      const code = pre.querySelector('code');
      const text = code.textContent;

      try {
        await navigator.clipboard.writeText(text);
        button.textContent = '已复制';
        button.classList.add('copied');

        setTimeout(() => {
          button.textContent = '复制';
          button.classList.remove('copied');
        }, 2000);
      } catch (err) {
        console.error('复制失败:', err);
        button.textContent = '失败';
        setTimeout(() => {
          button.textContent = '复制';
        }, 2000);
      }
    });

    pre.appendChild(button);
  }

  // 处理所有代码块
  function highlightAllCode() {
    const codeBlocks = document.querySelectorAll('.note-content pre code');

    codeBlocks.forEach(code => {
      const pre = code.parentElement;

      // 跳过已经处理过的
      if (pre.classList.contains('highlighted')) return;

      // 检测语言
      const lang = detectLanguage(code);

      // 添加语言类
      if (lang !== 'text') {
        pre.classList.add(`language-${lang}`);
        pre.setAttribute('data-lang', lang.toUpperCase());
      }

      // 应用语法高亮
      applySyntaxHighlight(code);

      // 添加复制按钮
      addCopyButton(pre);

      // 标记为已处理
      pre.classList.add('highlighted');
    });
  }

  // DOM加载完成后执行
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', highlightAllCode);
  } else {
    highlightAllCode();
  }

  // 监听动态内容变化
  if (typeof MutationObserver !== 'undefined') {
    const observer = new MutationObserver((mutations) => {
      let shouldHighlight = false;
      mutations.forEach(mutation => {
        if (mutation.addedNodes.length > 0) {
          mutation.addedNodes.forEach(node => {
            if (node.nodeType === 1 && (node.tagName === 'PRE' || node.querySelector('pre'))) {
              shouldHighlight = true;
            }
          });
        }
      });
      if (shouldHighlight) {
        highlightAllCode();
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }
})();
