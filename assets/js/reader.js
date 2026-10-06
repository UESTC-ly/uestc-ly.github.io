// Independent enhancements for a static document site; links work without JS.
(() => {
  const root = document.documentElement;
  const sidebar = document.getElementById('docs-sidebar');
  const sidebarToggle = document.querySelector('.sidebar-toggle');
  const sidebarClose = document.querySelector('.sidebar-close');
  const backdrop = document.querySelector('.sidebar-backdrop');
  const mobile = matchMedia('(max-width: 960px)');
  const background = [...document.querySelectorAll('.site-header-bar, .docs-main, .docs-outline')];
  const save = (key, value) => { try { localStorage.setItem(key, value); } catch {} };
  let previousOverflow = '';
  let drawerOpen = false;
  let returnFocus = null;
  if (sidebar && sidebarToggle) {
    const scrollToCurrent = () => {
      const tree = sidebar.querySelector('.sidebar-tree');
      const selected = tree.querySelector('a[aria-current=page]');
      if (selected) tree.scrollTop = Math.max(0, selected.offsetTop - tree.clientHeight / 3);
    };
    root.classList.add('docs-enhanced');
    try { root.classList.toggle('sidebar-collapsed', localStorage.getItem('notes-sidebar') === 'closed'); } catch {}
    sidebarToggle.hidden = false;
    sidebarClose.hidden = false;
    const closeDrawer = (restore = true) => {
      if (!drawerOpen) return;
      drawerOpen = false;
      root.classList.remove('sidebar-open');
      sidebar.removeAttribute('role');
      sidebar.removeAttribute('aria-modal');
      sidebar.inert = mobile.matches;
      backdrop.hidden = true;
      background.forEach(el => { el.inert = false; });
      document.body.style.overflow = previousOverflow;
      sidebarToggle.setAttribute('aria-expanded', 'false');
      if (restore) returnFocus?.focus();
    };
    const sync = () => {
      closeDrawer(false);
      const visible = !mobile.matches && !root.classList.contains('sidebar-collapsed');
      sidebar.inert = !visible;
      sidebarClose.hidden = !mobile.matches;
      sidebarToggle.setAttribute('aria-expanded', String(visible));
      sidebarToggle.setAttribute('aria-label', visible ? '收起专题目录' : '展开专题目录');
    };
    sidebarToggle.addEventListener('click', () => {
      if (mobile.matches) {
        if (drawerOpen) { closeDrawer(); return; }
        returnFocus = document.activeElement;
        previousOverflow = document.body.style.overflow;
        drawerOpen = true;
        root.classList.add('sidebar-open');
        sidebar.inert = false;
        sidebar.setAttribute('role', 'dialog');
        sidebar.setAttribute('aria-modal', 'true');
        background.forEach(el => { el.inert = true; });
        backdrop.hidden = false;
        document.body.style.overflow = 'hidden';
        sidebarToggle.setAttribute('aria-expanded', 'true');
        sidebarClose.focus();
        scrollToCurrent();
      } else {
        root.classList.toggle('sidebar-collapsed');
        save('notes-sidebar', root.classList.contains('sidebar-collapsed') ? 'closed' : 'open');
        sync();
      }
    });
    sidebarClose.addEventListener('click', () => closeDrawer());
    backdrop.addEventListener('click', () => closeDrawer());
    sidebar.addEventListener('click', event => {
      if (event.target.closest('a')) closeDrawer(false);
    });
    sidebar.addEventListener('keydown', event => {
      if (!drawerOpen) return;
      if (event.key === 'Escape') { event.preventDefault(); closeDrawer(); }
      if (event.key === 'Tab') {
        const focusables = [...sidebar.querySelectorAll('a, button, summary')].filter(el => el.getClientRects().length);
        const first = focusables[0], last = focusables.at(-1);
        if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
        if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
      }
    });
    mobile.addEventListener('change', sync);
    sync();
    if (!mobile.matches) scrollToCurrent();
  }

  const themeButtons = [...document.querySelectorAll('.theme-toggle')];
  const applyTheme = theme => {
    root.dataset.theme = theme;
    root.classList.toggle('dark', theme === 'dark');
    themeButtons.forEach(button => {
      const label = theme === 'dark' ? '浅色模式' : '深色模式';
      button.hidden = false;
      button.querySelector('span').textContent = label;
      button.setAttribute('aria-label', `切换到${label}`);
    });
  };
  themeButtons.forEach(button => button.addEventListener('click', () => {
    const theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    save('notes-theme', theme);
    applyTheme(theme);
  }));
  applyTheme(root.dataset.theme || 'light');

  const outlineLinks = [...document.querySelectorAll('.outline-nav a')];
  const headings = outlineLinks.map(link => document.getElementById(decodeURIComponent(link.hash.slice(1)))).filter(Boolean);
  if (headings.length && 'IntersectionObserver' in window) {
    const mark = id => outlineLinks.forEach(link => {
      if (decodeURIComponent(link.hash.slice(1)) === id) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
    const observer = new IntersectionObserver(entries => {
      const visible = entries.filter(entry => entry.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
      if (visible.length) mark(visible[0].target.id);
    }, { rootMargin: '-88px 0px -60% 0px' });
    headings.forEach(heading => observer.observe(heading));
    mark(headings[0].id);
    outlineLinks.forEach(link => link.addEventListener('click', () => mark(decodeURIComponent(link.hash.slice(1)))));
  }

  const trigger = document.querySelector('.site-search-trigger');
  const dialog = document.getElementById('search-dialog');
  const input = document.getElementById('global-search-input');
  const results = document.getElementById('global-search-results');
  const status = document.getElementById('global-search-status');
  if (!trigger || !dialog?.showModal || !input) return;
  let records = null;
  let loading = null;
  let searchTimer;
  const normalize = value => value.normalize('NFKC').toLocaleLowerCase();
  const loadIndex = () => {
    if (records) return Promise.resolve(records);
    if (!loading) loading = fetch(trigger.dataset.index).then(response => {
      if (!response.ok) throw new Error('index unavailable');
      return response.json();
    }).then(data => {
      records = data.map(item => ({ ...item, searchable: normalize(item.title + ' ' + item.group) }));
      return records;
    }).catch(error => { loading = null; throw error; });
    return loading;
  };
  const search = async () => {
    const query = input.value.trim();
    results.replaceChildren();
    if (!query) { status.textContent = '输入关键词，搜索全部专题中的笔记。'; return; }
    status.textContent = '正在搜索…';
    try {
      const index = await loadIndex();
      if (query !== input.value.trim()) return;
      const terms = normalize(query).split(/\s+/);
      const matches = index.filter(item => terms.every(term => item.searchable.includes(term)))
        .sort((a, b) => Number(normalize(b.title).includes(normalize(query))) - Number(normalize(a.title).includes(normalize(query))));
      status.textContent = matches.length ? `找到 ${matches.length} 篇笔记${matches.length > 20 ? '，显示前 20 篇' : ''}` : '没有找到匹配的笔记，请尝试其他关键词。';
      for (const item of matches.slice(0, 20)) {
        const link = document.createElement('a');
        link.className = 'search-result';
        link.href = item.url;
        const title = document.createElement('strong');
        title.textContent = item.title;
        const group = document.createElement('small');
        group.textContent = item.group;
        link.append(title, group);
        results.append(link);
      }
    } catch {
      if (query === input.value.trim()) status.textContent = '搜索索引暂时无法加载，请重试或通过专题目录浏览。';
    }
  };
  const openSearch = () => {
    if (dialog.open) return;
    document.querySelector('.menu-toggle')?.setAttribute('aria-expanded', 'false');
    dialog.showModal();
    input.focus();
    search();
  };
  trigger.setAttribute('aria-haspopup', 'dialog');
  trigger.setAttribute('aria-controls', 'search-dialog');
  trigger.addEventListener('click', event => { event.preventDefault(); openSearch(); });
  input.addEventListener('input', () => { clearTimeout(searchTimer); searchTimer = setTimeout(search, 120); });
  input.addEventListener('keydown', event => {
    if (event.isComposing) return;
    if (event.key === 'ArrowDown') { event.preventDefault(); results.querySelector('a')?.focus(); }
    if (event.key === 'Enter') { event.preventDefault(); results.querySelector('a')?.click(); }
  });
  dialog.addEventListener('keydown', event => {
    if (event.key === 'Escape') { event.preventDefault(); dialog.close(); }
  });
  dialog.addEventListener('click', event => { if (event.target === dialog) {
    const box = dialog.getBoundingClientRect();
    if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
  } });
  document.addEventListener('keydown', event => {
    if (event.isComposing || event.target.closest('input, textarea, select, [contenteditable=true]') || drawerOpen) return;
    if (event.key === '/' || ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k')) {
      event.preventDefault(); openSearch();
    }
  });
})();
