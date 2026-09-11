const button = document.querySelector('[data-menu-button]');
const menu = document.querySelector('[data-menu]');

if (button && menu) {
  button.addEventListener('click', () => {
    const open = button.getAttribute('aria-expanded') === 'true';
    button.setAttribute('aria-expanded', String(!open));
    menu.dataset.open = String(!open);
  });

  menu.addEventListener('click', (event) => {
    if (event.target instanceof HTMLAnchorElement) {
      button.setAttribute('aria-expanded', 'false');
      menu.dataset.open = 'false';
    }
  });
}

document.querySelectorAll('[data-year]').forEach((node) => {
  node.textContent = String(new Date().getFullYear());
});
