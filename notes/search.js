const search = document.getElementById('note-search');
if (search) {
  const entries = [...document.querySelectorAll('[data-search]')];
  search.addEventListener('input', () => {
    const query = search.value.trim().toLocaleLowerCase();
    let count = 0;
    for (const entry of entries) {
      entry.hidden = !entry.dataset.search.toLocaleLowerCase().includes(query);
      if (!entry.hidden) count++;
    }
    for (const group of document.querySelectorAll('[data-group]')) {
      group.hidden = !group.querySelector('[data-search]:not([hidden])');
    }
    document.getElementById('search-count').textContent = `${count} 篇笔记`;
    document.getElementById('no-results').hidden = count !== 0;
  });
}
