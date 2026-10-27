/**
 * 代码语法高亮 - 使用 Prism.js
 * 轻量、成熟、支持 200+ 语言
 */

(function() {
  'use strict';

  // 等待 Prism.js 加载
  function waitForPrism(callback) {
    if (typeof Prism !== 'undefined') {
      callback();
    } else {
      setTimeout(() => waitForPrism(callback), 50);
    }
  }

  // 语言映射（简化的检测规则 → Prism 语言标识）
  const languageMap = {
    python: 'python',
    javascript: 'javascript',
    js: 'javascript',
    typescript: 'typescript',
    ts: 'typescript',
    cpp: 'cpp',
    'c++': 'cpp',
    c: 'c',
    java: 'java',
    bash: 'bash',
    shell: 'bash',
    sql: 'sql',
    json: 'json',
    html: 'markup',
    xml: 'markup',
    css: 'css',
    go: 'go',
    rust: 'rust',
    ruby: 'ruby',
    php: 'php',
    swift: 'swift',
    kotlin: 'kotlin',
    yaml: 'yaml',
    yml: 'yaml',
    markdown: 'markdown',
    md: 'markdown'
  };

  // 简单的语言检测（基于关键字特征）
  function detectLanguage(text) {
    // Python
    if (/\b(def|class|import|from|elif)\b/.test(text)) return 'python';
    // C/C++
    if (/#include|std::|iostream|namespace/.test(text)) return 'cpp';
    // JavaScript
    if (/\b(const|let|var|function|=>|console\.log)\b/.test(text)) return 'javascript';
    // Java
    if (/\b(public|private|static|void|System\.out)\b/.test(text)) return 'java';
    // SQL
    if (/\b(SELECT|FROM|WHERE|INSERT|UPDATE|CREATE TABLE)\b/i.test(text)) return 'sql';
    // Bash
    if (/^[$#]\s|\becho\b|\bcd\b/.test(text)) return 'bash';
    // JSON
    if (/^\s*[\{\[]/.test(text) && /[\}\]]\s*$/.test(text)) return 'json';

    return 'clike'; // 默认类C语言
  }


  // 添加复制按钮
  function addCopyButton(pre) {
    // 避免重复添加
    if (pre.querySelector('.copy-button')) return;

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

      // 跳过已处理的
      if (pre.classList.contains('highlighted')) return;

      // 获取或检测语言
      let lang = null;

      // 1. 从 class 属性读取（如 language-python）
      if (pre.className) {
        const match = pre.className.match(/language-(\w+)/);
        if (match) {
          lang = languageMap[match[1].toLowerCase()] || match[1];
        }
      }

      // 2. 自动检测
      if (!lang) {
        const detected = detectLanguage(code.textContent);
        lang = languageMap[detected] || detected;
        pre.classList.add(`language-${detected}`);
      }

      // 3. 添加语言标签
      if (lang && lang !== 'text' && lang !== 'clike') {
        pre.setAttribute('data-lang', lang.toUpperCase());
      }

      // 4. 应用 Prism 高亮
      code.className = `language-${lang}`;
      try {
        Prism.highlightElement(code);
      } catch (err) {
        console.warn('Prism 高亮失败:', err);
      }

      // 5. 添加复制按钮
      addCopyButton(pre);

      // 标记为已处理
      pre.classList.add('highlighted');
    });
  }

  // 初始化
  waitForPrism(() => {
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
  });
})();

