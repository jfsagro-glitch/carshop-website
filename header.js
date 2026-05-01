/**
 * EXPO MIR — Shared header utilities
 * Handles: active nav, scroll-to-top, WhatsApp button, cart pulse,
 *          sticky header, modal Escape/backdrop close, mobile menu,
 *          mobile bottom nav, lazy images, section animations
 */
(function () {
  'use strict';

  /* ── Active navigation link ──────────────────────────────── */
  function setActiveNav() {
    var page = location.pathname.split('/').pop() || 'index.html';
    var map = {
      'index.html':         'nav_georgia',
      '':                   'nav_georgia',
      'georgia-stock.html': 'nav_georgia',
      'usa-orders.html':    'nav_usa',
      'korea-orders.html':  'nav_korea',
      'china-orders.html':  'nav_china',
      'europe-orders.html': 'nav_europe',
      'parts-orders.html':  null,
    };
    var i18nKey = map[page];
    document.querySelectorAll('.nav a').forEach(function (a) {
      a.classList.remove('active');
      if (i18nKey && a.getAttribute('data-i18n') === i18nKey) {
        a.classList.add('active');
      }
      if (!i18nKey && page === 'parts-orders.html' && a.href.includes('parts-orders.html')) {
        a.classList.add('active');
      }
    });
  }

  /* ── Sticky header shadow on scroll ─────────────────────── */
  function initStickyHeader() {
    // Skip: script.js setupEventListeners() already handles .header--scrolled
    if (typeof setupEventListeners === 'function') return;
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
    // Skip: index.html already has #backToTop handled by script.js
    if (document.getElementById('backToTop')) return;
    var btn = document.createElement('button');
    btn.id = 'scrollTopBtn';
    btn.setAttribute('aria-label', 'Вернуться наверх');
    btn.innerHTML = '<i class="fas fa-chevron-up"></i>';
    document.body.appendChild(btn);

    window.addEventListener('scroll', function () {
      btn.classList.toggle('visible', window.scrollY > 400);
    }, { passive: true });

    btn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* ── WhatsApp floating button ────────────────────────────── */
  function initWhatsAppButton() {
    // Skip: index.html already has #floatingWhatsApp
    if (document.getElementById('floatingWhatsApp')) return;
    if (document.getElementById('whatsappFloatBtn')) return;
    var btn = document.createElement('a');
    btn.id = 'whatsappFloatBtn';
    btn.href = 'https://wa.me/996755666805';
    btn.target = '_blank';
    btn.rel = 'noopener noreferrer';
    btn.setAttribute('aria-label', 'Написать в WhatsApp');
    btn.innerHTML = '<i class="fab fa-whatsapp"></i><span class="wa-tooltip">Написать в WhatsApp</span>';
    document.body.appendChild(btn);
  }

  /* ── Cart badge pulse on add ─────────────────────────────── */
  function initCartBadgePulse() {
    var countEl = document.getElementById('cartCount');
    if (!countEl) return;
    var lastVal = countEl.textContent;
    var observer = new MutationObserver(function () {
      var newVal = countEl.textContent;
      if (newVal !== lastVal && parseInt(newVal, 10) > parseInt(lastVal, 10)) {
        var btn = document.getElementById('cartBtn');
        if (btn) {
          btn.classList.remove('cart-pulse');
          void btn.offsetWidth;
          btn.classList.add('cart-pulse');
        }
      }
      lastVal = newVal;
    });
    observer.observe(countEl, { childList: true, characterData: true, subtree: true });
  }

  /* ── Modal close on Escape + backdrop click ──────────────── */
  function initModalClose() {
    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape') return;
      document.querySelectorAll('.modal').forEach(function (m) {
        if (m.style.display !== 'none' && m.style.display !== '') {
          var closeBtn = m.querySelector('.close');
          if (closeBtn) closeBtn.click();
          else m.style.display = 'none';
        }
      });
      var cartModal = document.getElementById('cartModal');
      if (cartModal && cartModal.classList.contains('active')) {
        if (typeof closeCart === 'function') closeCart();
      }
    });

    document.querySelectorAll('.modal').forEach(function (m) {
      m.addEventListener('click', function (e) {
        if (e.target === m) {
          var closeBtn = m.querySelector('.close');
          if (closeBtn) closeBtn.click();
          else m.style.display = 'none';
        }
      });
    });
  }

  /* ── Mobile menu hamburger ───────────────────────────────── */
  function initMobileMenu() {
    var headerContainer = document.querySelector('.header-content');
    if (!headerContainer) return;
    if (document.getElementById('mobileMenuToggle')) return;

    var toggle = document.createElement('button');
    toggle.id = 'mobileMenuToggle';
    toggle.setAttribute('aria-label', 'Меню');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.innerHTML = '<span></span><span></span><span></span>';
    headerContainer.appendChild(toggle);

    var nav = document.querySelector('.nav');
    if (!nav) return;

    function closeNav() {
      nav.classList.remove('nav--open');
      toggle.classList.remove('active');
      toggle.setAttribute('aria-expanded', 'false');
      document.body.classList.remove('nav-open');
    }

    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('nav--open');
      toggle.classList.toggle('active', open);
      toggle.setAttribute('aria-expanded', String(open));
      document.body.classList.toggle('nav-open', open);
    });

    // Close when any nav link is clicked (e.g. after navigating to anchor)
    nav.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', closeNav);
    });

    document.addEventListener('click', function (e) {
      if (!toggle.contains(e.target) && !nav.contains(e.target)) {
        closeNav();
      }
    });
  }

  /* ── Mobile bottom navigation bar ───────────────────────── */
  function initMobileBottomNav() {
    if (document.getElementById('mobileBottomNav')) return;
    var nav = document.createElement('nav');
    nav.id = 'mobileBottomNav';
    nav.setAttribute('aria-label', 'Мобильная навигация');
    nav.innerHTML = [
      '<a href="georgia-catalog.html" class="mbn-item" data-page="georgia-catalog.html">',
      '  <i class="fas fa-car"></i><span>Каталог</span>',
      '</a>',
      '<a href="https://wa.me/996755666805" target="_blank" rel="noopener noreferrer" class="mbn-item mbn-item--wa">',
      '  <i class="fab fa-whatsapp"></i><span>WhatsApp</span>',
      '</a>',
      '<a href="javascript:void(0)" class="mbn-item mbn-item--cta" onclick="typeof openRequestModal!==\'undefined\'&&openRequestModal()">',
      '  <i class="fas fa-search"></i><span>Заявка</span>',
      '</a>',
      '<a href="https://t.me/expo_mir" target="_blank" rel="noopener noreferrer" class="mbn-item">',
      '  <i class="fab fa-telegram"></i><span>Telegram</span>',
      '</a>',
      '<a href="tel:+996755666805" class="mbn-item">',
      '  <i class="fas fa-phone"></i><span>Звонок</span>',
      '</a>',
    ].join('');
    document.body.appendChild(nav);

    var page = location.pathname.split('/').pop() || 'index.html';
    nav.querySelectorAll('[data-page]').forEach(function (a) {
      if (a.dataset.page === page) a.classList.add('mbn-active');
    });
  }

  /* ── Lazy-load images via IntersectionObserver ───────────── */
  function initLazyImages() {
    if (!('IntersectionObserver' in window)) return;
    var imgs = document.querySelectorAll('img[data-src]');
    if (!imgs.length) return;
    var io = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var img = entry.target;
        img.src = img.dataset.src;
        img.removeAttribute('data-src');
        obs.unobserve(img);
      });
    }, { rootMargin: '200px' });
    imgs.forEach(function (img) { io.observe(img); });
  }

  /* ── Section scroll-reveal animations ───────────────────── */
  function initScrollReveal() {
    // Skip: script.js setupScrollReveal() handles this with CSS classes
    if (typeof setupScrollReveal === 'function') return;
    if (!('IntersectionObserver' in window)) return;
    var els = document.querySelectorAll('.why-card, .testimonial-card, .contact-item');
    if (!els.length) return;
    els.forEach(function (el, i) {
      el.style.opacity = '0';
      el.style.transform = 'translateY(24px)';
      el.style.transition = 'opacity 0.5s ease ' + (i % 3 * 0.1) + 's, transform 0.5s ease ' + (i % 3 * 0.1) + 's';
    });
    var io = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        obs.unobserve(entry.target);
      });
    }, { threshold: 0.12 });
    els.forEach(function (el) { io.observe(el); });
  }

  /* ── Testimonials touch-swipe on mobile ──────────────────── */
  function initTestimonialsCarousel() {
    var grid = document.querySelector('.testimonials-grid');
    if (!grid) return;
    var startX = null;
    grid.addEventListener('touchstart', function (e) {
      startX = e.touches[0].clientX;
    }, { passive: true });
    grid.addEventListener('touchend', function (e) {
      if (startX === null) return;
      var diff = startX - e.changedTouches[0].clientX;
      if (Math.abs(diff) > 50) {
        grid.scrollBy({ left: diff > 0 ? 280 : -280, behavior: 'smooth' });
      }
      startX = null;
    }, { passive: true });
  }

  /* ── Animated counter for [data-count] elements ──────────── */
  function initCounterAnimation() {
    // Skip: script.js animateCounters() handles this
    if (typeof animateCounters === 'function') return;
    if (!('IntersectionObserver' in window)) return;
    var counters = document.querySelectorAll('[data-count]');
    if (!counters.length) return;
    var io = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        var target = parseInt(el.getAttribute('data-count'), 10);
        var suffix = el.getAttribute('data-suffix') || '';
        var duration = 1400;
        var startTime = null;
        function tick(now) {
          if (!startTime) startTime = now;
          var progress = Math.min((now - startTime) / duration, 1);
          // Ease-out cubic
          var eased = 1 - Math.pow(1 - progress, 3);
          el.textContent = Math.round(eased * target) + suffix;
          if (progress < 1) {
            requestAnimationFrame(tick);
          } else {
            el.textContent = target + suffix;
          }
        }
        requestAnimationFrame(tick);
        obs.unobserve(el);
      });
    }, { threshold: 0.5 });
    counters.forEach(function (el) { io.observe(el); });
  }

  /* ── Modal focus management ──────────────────────────────── */
  function initModalFocusManagement() {
    if (!('MutationObserver' in window)) return;
    var FOCUSABLE = 'input:not([disabled]):not([type="hidden"]), select:not([disabled]), textarea:not([disabled]), button:not([disabled]), a[href], [tabindex]:not([tabindex="-1"])';

    document.querySelectorAll('.modal').forEach(function (modal) {
      var prevFocused = null;
      var trapHandler = null;

      new MutationObserver(function () {
        var visible = modal.style.display === 'block';

        if (visible && !modal._focusMgr) {
          modal._focusMgr = true;
          prevFocused = document.activeElement;

          setTimeout(function () {
            var focusables = Array.prototype.slice.call(modal.querySelectorAll(FOCUSABLE));
            if (!focusables.length) return;

            var first = focusables[0];
            var last  = focusables[focusables.length - 1];

            // Set initial focus on first field (skip close button if possible)
            var preferredFirst = modal.querySelector('input:not([disabled]):not([type="hidden"]), select:not([disabled])') || first;
            preferredFirst.focus();

            // Tab / Shift+Tab trap
            trapHandler = function (e) {
              if (e.key !== 'Tab') return;
              // Refresh focusables in case DOM changed (e.g. skeleton replaced)
              var els = Array.prototype.slice.call(modal.querySelectorAll(FOCUSABLE));
              if (!els.length) return;
              var f = els[0], l = els[els.length - 1];
              if (e.shiftKey) {
                if (document.activeElement === f) { e.preventDefault(); l.focus(); }
              } else {
                if (document.activeElement === l) { e.preventDefault(); f.focus(); }
              }
            };
            modal.addEventListener('keydown', trapHandler);
          }, 60);

        } else if (!visible && modal._focusMgr) {
          modal._focusMgr = false;
          if (trapHandler) {
            modal.removeEventListener('keydown', trapHandler);
            trapHandler = null;
          }
          // Return focus to the element that opened the modal
          if (prevFocused && typeof prevFocused.focus === 'function') {
            try { prevFocused.focus(); } catch (_) {}
          }
        }
      }).observe(modal, { attributes: true, attributeFilter: ['style'] });
    });
  }

  /* ── Init all ────────────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', function () {
    setActiveNav();
    initStickyHeader();
    initScrollToTop();
    initWhatsAppButton();
    initCartBadgePulse();
    initModalClose();
    initMobileMenu();
    initMobileBottomNav();
    initLazyImages();
    initScrollReveal();
    initTestimonialsCarousel();
    initCounterAnimation();
    initModalFocusManagement();
  });
})();