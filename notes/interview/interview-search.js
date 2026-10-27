// The question index loads only when readers search. All chapter links are static.
(() => {
  const section = document.querySelector('[data-question-index]');
  if (!section) return;
  const input = document.getElementById('question-query');
  const category = document.getElementById('question-category');
  const status = document.getElementById('question-status');
  const results = document.getElementById('question-results');
  const clear = document.getElementById('question-clear');
  const more = document.getElementById('question-more');
  const normalize = text => text.normalize('NFKC').toLocaleLowerCase();
  let records, loading, matches = [], displayed = 0, revision = 0, timer;
  const loadIndex = () => {
    if (!loading) loading = fetch(section.dataset.questionIndex).then(response => {
      if (!response.ok) throw new Error('index unavailable');
      return response.json();
    }).then(data => {
      records = data.questions.map(([chapterId, anchor, title, excerpt]) => {
        const [file, chapter, group] = data.chapters[chapterId];
        return { title, excerpt, chapter, group, url: `${file}#${encodeURIComponent(anchor)}`,
          titleSearch: normalize(title), searchable: normalize(`${title} ${chapter} ${group} ${excerpt}`) };
      });
      return records;
    }).catch(error => { loading = null; throw error; });
    return loading;
  };
  const appendResults = () => {
    const fragment = document.createDocumentFragment();
    for (const item of matches.slice(displayed, displayed + 20)) {
      const link = document.createElement('a');
      link.className = 'question-result';
      link.href = item.url;
      const title = document.createElement('strong');
      title.textContent = item.title;
      const context = document.createElement('small');
      context.textContent = `${item.group.replace(/^\d+-/, '')} / ${item.chapter}`;
      const excerpt = document.createElement('p');
      excerpt.textContent = item.excerpt;
      link.append(title, context, excerpt);
      fragment.append(link);
    }
    results.append(fragment);
    displayed = Math.min(displayed + 20, matches.length);
    more.hidden = displayed >= matches.length;
    status.textContent = matches.length ? `找到 ${matches.length} 个知识条目，已显示 ${displayed} 条。` : '没有找到匹配的知识点，试试更短的关键词或其他方向。';
  };
  const updateUrl = () => {
    const url = new URL(location.href);
    if (input.value.trim()) url.searchParams.set('q', input.value.trim()); else url.searchParams.delete('q');
    if (category.value) url.searchParams.set('category', category.value); else url.searchParams.delete('category');
    history.replaceState(null, '', url);
  };
  const search = async () => {
    const ownRevision = ++revision;
    const query = input.value.trim();
    const selected = category.value;
    clear.hidden = !query && !selected;
    results.replaceChildren();
    more.hidden = true;
    updateUrl();
    if (!query && !selected) {
      status.textContent = '输入关键词开始检索，也可以直接浏览下方分类。';
      return;
    }
    status.textContent = '正在加载题目索引…';
    try {
      const index = records || await loadIndex();
      if (ownRevision !== revision) return;
      const normalized = normalize(query);
      const terms = normalized.split(/\s+/).filter(Boolean);
      matches = index.filter(item => (!selected || item.group === selected) && terms.every(term => item.searchable.includes(term)));
      if (query) matches.sort((a, b) => Number(b.titleSearch.includes(normalized)) - Number(a.titleSearch.includes(normalized)));
      displayed = 0;
      appendResults();
    } catch {
      if (ownRevision === revision) status.textContent = '索引暂时无法加载。请重新输入以重试，或通过下方分类目录阅读。';
    }
  };
  input.addEventListener('input', () => {
    revision++;
    clearTimeout(timer);
    timer = setTimeout(search, 160);
  });
  category.addEventListener('change', () => { clearTimeout(timer); search(); });
  clear.addEventListener('click', () => {
    clearTimeout(timer);
    input.value = '';
    category.value = '';
    search();
    input.focus();
  });
  more.addEventListener('click', () => {
    const previousLast = results.lastElementChild;
    appendResults();
    previousLast?.nextElementSibling?.focus();
  });
  const params = new URL(location.href).searchParams;
  input.value = params.get('q') || '';
  if ([...category.options].some(option => option.value === params.get('category'))) category.value = params.get('category');
  if (input.value || category.value) search();
})();
