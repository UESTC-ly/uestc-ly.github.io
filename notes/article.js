if (window.renderMathInElement) {
  document.querySelectorAll('.arithmatex').forEach(element => {
    renderMathInElement(element, {
      delimiters: [{left:'\\(',right:'\\)',display:false},{left:'\\[',right:'\\]',display:true}],
      throwOnError:false, strict:'ignore', trust:false
    });
  });
}
