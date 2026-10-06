const header = document.querySelector('.site-header');
const toggle = header?.querySelector('.menu-toggle');
const navigation = header?.querySelector('#site-navigation');
if (toggle && navigation) {
  header.classList.add('enhanced');
  toggle.hidden = false;
  const close = () => toggle.setAttribute('aria-expanded', 'false');
  toggle.addEventListener('click', () => {
    toggle.setAttribute('aria-expanded', String(toggle.getAttribute('aria-expanded') !== 'true'));
  });
  navigation.addEventListener('click', event => {
    if (event.target.closest('a')) close();
  });
  document.addEventListener('click', event => {
    if (!header.contains(event.target)) close();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
      close();
      toggle.focus();
    }
  });
  matchMedia('(min-width: 761px)').addEventListener('change', event => {
    if (event.matches) close();
  });
}
