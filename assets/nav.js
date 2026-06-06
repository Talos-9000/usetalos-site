/* Tal.OS — Mobile Hamburger Nav (M2 + M8 per Claude Boss spec) */
(function () {
  var toggle = document.getElementById('navToggle');
  var nav = document.getElementById('primaryNav');
  var backdrop = document.getElementById('navBackdrop');
  if (!toggle || !nav) { return; }

  function isOpen() { return nav.getAttribute('data-open') === 'true'; }

  function openMenu() {
    nav.setAttribute('data-open', 'true');
    toggle.setAttribute('aria-expanded', 'true');
    toggle.setAttribute('aria-label', 'Close menu');
    if (backdrop) { backdrop.hidden = false; }
    document.body.style.overflow = 'hidden';
    var first = nav.querySelector('a');
    if (first) { first.focus(); }
  }

  function closeMenu() {
    nav.setAttribute('data-open', 'false');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'Open menu');
    if (backdrop) { backdrop.hidden = true; }
    document.body.style.overflow = '';
  }

  toggle.addEventListener('click', function () {
    if (isOpen()) { closeMenu(); } else { openMenu(); }
  });

  if (backdrop) { backdrop.addEventListener('click', closeMenu); }

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && isOpen()) { closeMenu(); toggle.focus(); }
  });

  nav.addEventListener('click', function (e) {
    if (e.target.closest('a')) { closeMenu(); }
  });

  var mq = window.matchMedia('(min-width: 64em)');
  function onChange(ev) { if (ev.matches) { closeMenu(); } }
  if (mq.addEventListener) { mq.addEventListener('change', onChange); }
  else { mq.addListener(onChange); }

  /* M8: Device-aware hints */
  var root = document.documentElement;
  var coarse = window.matchMedia('(pointer: coarse)').matches;
  var narrow = window.matchMedia('(max-width: 64em)').matches;
  root.classList.toggle('is-touch', coarse);
  root.classList.toggle('is-mobile-layout', narrow);
})();
