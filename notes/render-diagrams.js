import mermaid from './vendor/mermaid/mermaid.esm.min.mjs';
mermaid.initialize({startOnLoad:false,securityLevel:'strict',theme:'base',themeVariables:{primaryColor:'#e5ebe1',primaryTextColor:'#1f2926',primaryBorderColor:'#9caf97',lineColor:'#64705e',fontFamily:'sans-serif'}});
const observer = new IntersectionObserver(async entries => {
  for (const entry of entries) {
    if (!entry.isIntersecting) continue;
    observer.unobserve(entry.target);
    const source = entry.target.textContent;
    try { await mermaid.run({nodes:[entry.target],suppressErrors:false}); }
    catch { entry.target.textContent = source; entry.target.removeAttribute('data-processed'); }
  }
}, {rootMargin:'600px'});
document.querySelectorAll('pre.mermaid').forEach(node => observer.observe(node));
