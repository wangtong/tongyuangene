(function () {
    'use strict';

    var STORAGE_THEME = 'ty-theme';

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem(STORAGE_THEME, theme);
        var btn = document.getElementById('theme-toggle');
        if (btn) {
            btn.setAttribute('aria-label', theme === 'dark' ? '切换到明亮模式' : '切换到暗色模式');
            btn.setAttribute('title', theme === 'dark' ? '明亮模式' : '暗色模式');
        }
    }

    function toggleTheme() {
        var current = document.documentElement.getAttribute('data-theme') || 'light';
        applyTheme(current === 'dark' ? 'light' : 'dark');
    }

    function initToolbar() {
        var themeBtn = document.getElementById('theme-toggle');
        if (themeBtn) themeBtn.addEventListener('click', toggleTheme);
    }

    function initNav() {
        var toggle = document.querySelector('.nav-toggle');
        var menu = document.querySelector('.nav-menu');
        if (toggle && menu) {
            toggle.addEventListener('click', function () {
                menu.classList.toggle('open');
            });
        }
        var current = location.pathname.split('/').pop() || 'index.html';
        document.querySelectorAll('.nav-menu a').forEach(function (link) {
            if (link.getAttribute('href') === current) {
                document.querySelectorAll('.nav-menu a.active').forEach(function (a) {
                    a.classList.remove('active');
                });
                link.classList.add('active');
            }
        });
    }

    function initScrollAnimations() {
        if (!('IntersectionObserver' in window)) return;
        var observer = new IntersectionObserver(
            function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('fade-up');
                        observer.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.1 }
        );
        document.querySelectorAll('.card, .article-card, .feature-block, .stat-item, .contact-card, .price-card, .storage-highlight').forEach(function (el) {
            observer.observe(el);
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        applyTheme(localStorage.getItem(STORAGE_THEME) || 'light');
        initToolbar();
        initNav();
        initScrollAnimations();
    });
})();