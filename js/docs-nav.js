(function () {
    if (!document.querySelector('.doc-toc')) return;

    var links = document.querySelectorAll('.doc-toc a[href^="#"]');
    var sections = [];
    links.forEach(function (link) {
        var id = link.getAttribute('href').slice(1);
        var el = document.getElementById(id);
        if (el) sections.push({ link: link, el: el });
    });

    function setActive(id) {
        links.forEach(function (link) {
            var match = link.getAttribute('href') === '#' + id;
            link.classList.toggle('is-active', match);
        });
    }

    function onScroll() {
        var y = window.scrollY + 120;
        var current = sections[0];
        sections.forEach(function (item) {
            if (item.el.offsetTop <= y) current = item;
        });
        if (current) setActive(current.el.id);
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    links.forEach(function (link) {
        link.addEventListener('click', function (e) {
            var id = link.getAttribute('href').slice(1);
            var target = document.getElementById(id);
            if (!target) return;
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            history.replaceState(null, '', '#' + id);
            setActive(id);
        });
    });
})();
