/**
 * DECEL — Scripts UI globaux
 */
(function () {
  'use strict';

  function getCookie(name) {
    var match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? decodeURIComponent(match[2]) : null;
  }

  window.getCookie = getCookie;

  window.toggleTheme = function () {
    var html = document.documentElement;
    var icon = document.getElementById('theme-icon');
    var next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('decel-theme', next);
    if (icon) {
      icon.className = next === 'dark' ? 'fas fa-sun navbar-action-icon' : 'fas fa-moon navbar-action-icon';
    }
  };

  window.toggleMobileMenu = function () {
    var menu = document.getElementById('mobile-menu');
    var overlay = document.getElementById('mobile-menu-overlay');
    var toggle = document.getElementById('mobile-menu-toggle');
    if (!menu) return;
    menu.classList.toggle('show');
    if (overlay) overlay.classList.toggle('show');
    if (toggle) toggle.classList.toggle('active');
    document.body.style.overflow = menu.classList.contains('show') ? 'hidden' : '';
  };

  document.addEventListener('DOMContentLoaded', function () {
    var saved = localStorage.getItem('decel-theme');
    var icon = document.getElementById('theme-icon');
    if (saved === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark');
      if (icon) icon.className = 'fas fa-sun navbar-action-icon';
    }

    if (document.querySelector('.bottom-nav')) {
      document.body.classList.add('has-bottom-nav');
    }

    var trackUrl = document.body.dataset.trackClick;
    if (trackUrl) {
      document.addEventListener('click', function (event) {
        var el = event.target.closest('a, button, input[type="submit"], [onclick]');
        if (!el) return;
        fetch(trackUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
          },
          body: JSON.stringify({
            page_url: window.location.pathname,
            element_id: el.id || '',
            element_class: el.className || '',
            element_tag: el.tagName.toLowerCase(),
            element_text: (el.textContent || '').trim().substring(0, 255),
            href: el.href || '',
            x: event.clientX,
            y: event.clientY
          })
        }).catch(function () {});
      });
    }

    var sessionEndUrl = document.body.dataset.trackSessionEnd;
    if (sessionEndUrl) {
      window.addEventListener('beforeunload', function () {
        navigator.sendBeacon(sessionEndUrl, JSON.stringify({}));
      });
    }
  });
})();
