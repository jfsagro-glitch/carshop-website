/**
 * EXPO MIR — Shared header utilities
 * Handles: active nav, scroll-to-top, cart badge animation, sticky header shadow
 */
(function () {
  'use strict';

  /* ── Active navigation link ──────────────────────────────── */
  function setActiveNav() {
    const page = location.pathname.split('/').pop() || 'index.html';
    const map = {
      'index.html':         'nav_georgia',
      '':                   'nav_georgia',
      'georgia-stock.html': 'nav_georgia',
      'usa-orders.html':    'nav_usa',
      'korea-orders.html':  'nav_korea',
      'china-orders.html':  'nav_china',
      'europe-orders.html': 'nav_europe',
      'parts-orders.html':  null, // no i18n key for parts
    };
    const i18nKey = map[page];
    document.querySelectorAll('.nav a').forEach(function (a) {
      a.classList.remove('active');
      if (i18nKey && a.getAttribute('data-i18n') === i18nKey) {
        a.classList.add('active');
      }
      // Parts page special case (no data-i18n)
      if (!i18nKey && page === 'parts-orders.html' && a.href.includes('parts-orders.html')) {
        a.classList.add('active');
      }
    });
  }

  /* ── Sticky header shadow on scroll ─────────────────────── */
  function initStickyHeader() {
    var header = document.querySelector('.header');
    if (!header) return;
    var scrolled = false;
    window.addEventListener('scroll', function () {
      if (window.scrollY > 10) {
        if (!scrolled) { header.classList.add('header--scrolled'); scrolled = true; }
      } else {
        if (scrolled) { header.classList.remove('header--scrolled'); scrolled = false; }
      }
    }, { passive: true });
  }

  /* ── Scroll-to-top button ────────────────────────────────── */
  function initScrollToTop() {
    var btn = document.createElement('button');
    btn.id = 'scrollTopBtn';
    btn.setAttribute('aria-label', 'Вернуться наверх');
    btn.innerHTML = '&#8679;';
    document.body.appendChild(btn);

    window.addEventListener('scroll', function () {
      btn.classList.toggle('visible', window.scrollY > 400);
    }, { passive: true });

    btn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* ── Cart badge pulse on add ─────────────────────────────── */
  function initCartBadgePulse() {
    // Observe cart count changes
    var countEl = document.getElementById('cartCount');
    if (!countEl) return;
    var lastVal = countEl.textContent;
    var observer = new MutationObserver(function () {
      var newVal = countEl.textContent;
      if (newVal !== lastVal && parseInt(newVal, 10) > parseInt(lastVal, 10)) {
        var btn = document.getElementById('cartBtn');
        if (btn) {
          btn.classList.remove('cart-pulse');
          // force reflow
          void btn.offsetWidth;
          btn.classList.add('cart-pulse');
        }
      }
      lastVal = newVal;
    });
    observer.observe(countEl, { childList: true, characterData: true, subtree: true });
  }

  /* ── Mobile menu hamburger ───────────────────────────────── */
  function initMobileMenu() {
    var header = document.querySelector('.header .container');
    if (!header) return;
    if (document.getElementById('mobileMenuToggle')) return; // already added

    var toggle = document.createElement('button');
    toggle.id = 'mobileMenuToggle';
    toggle.setAttribute('aria-label', 'Меню');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.innerHTML = '<span></span><span></span><span></span>';
    header.appendChild(toggle);

    var nav = document.querySelector('.nav');
    if (!nav) return;

    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('nav--open');
      toggle.classList.toggle('active', open);
      toggle.setAttribute('aria-expanded', String(open));
    });

    // Close on outside click
    document.addEventListener('click', function (e) {
      if (!toggle.contains(e.target) && !nav.contains(e.target)) {
        nav.classList.remove('nav--open');
        toggle.classList.remove('active');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  /* ── Init all ────────────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', function () {
    setActiveNav();
    initStickyHeader();
    initScrollToTop();
    initCartBadgePulse();
    initMobileMenu();
  });
})();
