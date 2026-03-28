document.addEventListener('DOMContentLoaded', function() {
    var toggle = document.querySelector('.theme-toggle');

    var saved = localStorage.getItem('theme');
    if (saved) {
        document.documentElement.setAttribute('data-theme', saved);
    }

    toggle.addEventListener('click', function() {
        var current = document.documentElement.getAttribute('data-theme');
        var next;

        if (current) {
            next = current === 'dark' ? 'light' : 'dark';
        } else {
            next = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'light' : 'dark';
        }

        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
    });
});
