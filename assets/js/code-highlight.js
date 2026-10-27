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

  // 语法高亮规则
  const syntaxRules = {
    // 注释
    comment: [
      { pattern: /(#[^\n]*)/g, class: 'comment' }, // Python, Bash注释
      { pattern: /(\/\/[^\n]*)/g, class: 'comment' }, // C++, JS注释
      { pattern: /(\/\*[\s\S]*?\*\/)/g, class: 'comment' } // 多行注释
    ],
    // 字符串
    string: [
      { pattern: /("(?:[^"\\]|\\.)*")/g, class: 'string' },
      { pattern: /('(?:[^'\\]|\\.)*')/g, class: 'string' },
      { pattern: /(`(?:[^`\\]|\\.)*`)/g, class: 'string' }
    ],
    // 关键字
    keyword: [
      { pattern: /\b(def|class|import|from|if|elif|else|for|while|return|in|and|or|not|try|except|finally|with|as|lambda|yield|async|await)\b/g, class: 'keyword' },
      { pattern: /\b(const|let|var|function|return|if|else|for|while|do|switch|case|break|continue|new|this|class|extends|async|await|export|import)\b/g, class: 'keyword' },
      { pattern: /\b(int|float|double|char|void|bool|string|auto|const|static|public|private|protected|class|struct|namespace|using|template|typename)\b/g, class: 'keyword' },
      { pattern: /\b(SELECT|FROM|WHERE|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|TABLE|INDEX|JOIN|LEFT|RIGHT|INNER|OUTER|ON|AND|OR|NOT|NULL|IS|IN)\b/gi, class: 'keyword' }
    ],
    // 数字
    number: [
      { pattern: /\b(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?\b/g, class: 'number' }
    ],
    // 函数名
    function: [
      { pattern: /\b([a-zA-Z_]\w*)\s*(?=\()/g, class: 'function' }
    ],
    // 类名
    className: [
      { pattern: /\b([A-Z][a-zA-Z0-9_]*)\b/g, class: 'class-name' }
    ],
    // 运算符
    operator: [
      { pattern: /([\+\-\*\/\%\=\<\>\!\&\|\^\~])/g, class: 'operator' }
    ]
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
    let html = code.textContent;

    // 转义HTML特殊字符
    html = html
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    // 按顺序应用语法规则
    ['comment', 'string', 'keyword', 'number', 'function', 'className', 'operator'].forEach(type => {
      if (syntaxRules[type]) {
        syntaxRules[type].forEach(rule => {
          html = html.replace(rule.pattern, `<span class="${rule.class}">$1</span>`);
        });
      }
    });

    code.innerHTML = html;
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
