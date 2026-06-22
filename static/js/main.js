let isLoading = false;

function toggleSave(id) {
    let saved = JSON.parse(localStorage.getItem('saved_news') || '[]');
    const idx = saved.indexOf(String(id));
    if (idx > -1) {
        saved.splice(idx, 1);
        const btn = document.querySelector('.save-btn');
        if (btn) { btn.innerHTML = '<i class="bi bi-bookmark"></i>'; btn.classList.remove('saved'); }
    } else {
        saved.push(String(id));
        const btn = document.querySelector('.save-btn');
        if (btn) { btn.innerHTML = '<i class="bi bi-bookmark-fill"></i>'; btn.classList.add('saved'); }
    }
    localStorage.setItem('saved_news', JSON.stringify(saved));
}

function isSaved(id) {
    return JSON.parse(localStorage.getItem('saved_news') || '[]').includes(String(id));
}

function getSavedIds() {
    return JSON.parse(localStorage.getItem('saved_news') || '[]');
}

function webShare() {
    if (navigator.share) {
        navigator.share({title: document.title, text: document.querySelector('meta[name="description"]')?.content || '', url: window.location.href}).catch(() => {});
    }
}

function copyLink() {
    navigator.clipboard.writeText(window.location.href).then(() => {
        const btn = event.target.closest('.btn');
        if (btn) { btn.innerHTML = '<i class="bi bi-check"></i>'; setTimeout(() => { btn.innerHTML = '<i class="bi bi-link-45deg"></i>'; }, 2000); }
    });
}

function yorumGonder(newsId) {
    const input = document.getElementById('yorumInput');
    const yorum = input.value.trim();
    if (!yorum) return;
    fetch('/api/yorum-ekle/' + newsId, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({yorum: yorum})
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) { input.value = ''; yorumlariGoster(data.yorumlar); }
        else if (data.error) { alert(data.error); }
    });
}

function yorumlariGoster(list) {
    const div = document.getElementById('yorumlar');
    if (!div) return;
    if (!list || list.length === 0) {
        div.innerHTML = '<p class="text-muted small">Henuz yorum yok.</p>';
        return;
    }
    div.innerHTML = list.map(y =>
        '<div class="card bg-transparent border-secondary mb-2">' +
            '<div class="card-body py-2">' +
                '<div class="d-flex justify-content-between"><strong class="small">' + escapeHtml(y.author || 'Anonim') + '</strong><small class="text-muted">' + (y.date || y.tarih || '') + '</small></div>' +
                '<p class="mb-1 mt-1">' + escapeHtml(y.content || y.yorum || '') + '</p>' +
                '<button class="btn btn-sm btn-outline-danger py-0 px-1" onclick="yorumBegen(' + y.id + ')"><i class="bi bi-heart"></i> <span id="like-' + y.id + '">' + (y.likes || 0) + '</span></button>' +
            '</div>' +
        '</div>'
    ).join('');
}

function yorumBegen(commentId) {
    fetch('/api/yorum-begen/' + commentId, {method: 'POST'}).then(() => {
        const el = document.getElementById('like-' + commentId);
        if (el) el.textContent = parseInt(el.textContent || '0') + 1;
    });
}

function escapeHtml(text) {
    var d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML;
}

function loadMore() {
    if (isLoading) return;
    const btn = document.getElementById('loadMore');
    if (!btn) return;
    isLoading = true;
    const sayfa = parseInt(btn.getAttribute('data-sayfa')) + 1;
    const kategori = btn.getAttribute('data-kategori');
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Yukleniyor...';
    btn.disabled = true;
    fetch('/api/load-more?kategori=' + kategori + '&sayfa=' + sayfa)
        .then(r => r.json())
        .then(data => {
            if (data.html) {
                document.getElementById('newsContainer').insertAdjacentHTML('beforeend', data.html);
                initLazyBg();
                btn.setAttribute('data-sayfa', sayfa);
                if (!data.hasMore) { btn.remove(); }
                else { btn.innerHTML = '<i class="bi bi-arrow-down-circle"></i> Daha Fazla Haber'; btn.disabled = false; }
            }
            isLoading = false;
        })
        .catch(() => { btn.innerHTML = '<i class="bi bi-arrow-down-circle"></i> Daha Fazla Haber'; btn.disabled = false; isLoading = false; });
}

function newsletterAbone() { newsletterAboneOl('newsletter-email', 'newsletter-msg'); }
function sidebarNewsletter() { newsletterAboneOl('sidebar-newsletter', 'sidebar-newsletter-msg'); }

function newsletterAboneOl(inputId, msgId) {
    const input = document.getElementById(inputId);
    const msg = document.getElementById(msgId);
    const email = input.value.trim();
    if (!email || !email.includes('@')) { msg.textContent = 'Gecerli bir e-posta adresi girin.'; msg.style.color = '#e74c3c'; return; }
    fetch('/api/newsletter', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({email: email})})
        .then(r => r.json())
        .then(data => { input.value = ''; msg.textContent = data.message || 'Abone oldunuz!'; msg.style.color = data.success ? '#27ae60' : '#e74c3c'; })
        .catch(() => { msg.textContent = 'Hata.'; msg.style.color = '#e74c3c'; });
}

function cookieKabul() { localStorage.setItem('cookie_consent', 'true'); document.getElementById('cookie-consent').classList.remove('visible'); }
function cookieReddet() { localStorage.setItem('cookie_consent', 'false'); document.getElementById('cookie-consent').classList.remove('visible'); }

function initLazyBg() {
    const els = document.querySelectorAll('.lazy-bg:not(.loaded)');
    if (!els.length) return;
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const el = entry.target;
                    const src = el.getAttribute('data-src');
                    if (src) { el.style.backgroundImage = 'url(' + src + ')'; el.classList.add('loaded'); }
                    observer.unobserve(el);
                }
            });
        }, {rootMargin: '200px'});
        els.forEach(el => observer.observe(el));
    } else {
        els.forEach(el => { const src = el.getAttribute('data-src'); if (src) { el.style.backgroundImage = 'url(' + src + ')'; el.classList.add('loaded'); } });
    }
}

if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/sw.js').catch(() => {});
}

function initInfiniteScroll() {
    const btn = document.getElementById('loadMore');
    if (!btn) return;
    const s = document.createElement('div');
    s.id = 'scroll-sentinel'; s.style.height = '1px';
    btn.parentNode.insertBefore(s, btn);
    if ('IntersectionObserver' in window) {
        new IntersectionObserver((entries) => { if (entries[0].isIntersecting && !isLoading) loadMore(); }, {rootMargin: '200px'}).observe(s);
    }
}

// Push Notification
function subscribePush() {
    if (!('Notification' in window)) return;
    if (Notification.permission === 'granted') {
        document.getElementById('pushSubscribe').style.display = 'none';
        return;
    }
    Notification.requestPermission().then(perm => {
        if (perm === 'granted') {
            document.getElementById('pushSubscribe').style.display = 'none';
            if ('serviceWorker' in navigator && 'PushManager' in window) {
                navigator.serviceWorker.ready.then(reg => {
                    reg.pushManager.subscribe({userVisibleOnly: true, applicationServerKey: urlBase64ToUint8Array('BPP7y8wKqPxQvYQgKmOe0vYVxG8Xx7Z0K0VqJ3w5d0s')}).then(sub => {
                        fetch('/api/push-subscribe', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(sub.toJSON())});
                    });
                });
            }
        }
    });
}

function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/\-/g, '+').replace(/_/g, '/');
    const rawData = window.atob(base64);
    return Uint8Array.from([...rawData].map(char => char.charCodeAt(0)));
}

// Auto-init push button visibility
if ('Notification' in window && Notification.permission === 'default') {
    document.addEventListener('DOMContentLoaded', () => {
        const btn = document.getElementById('pushSubscribe');
        if (btn) btn.style.display = 'flex';
    });
}

document.addEventListener('DOMContentLoaded', function() {
    var path = window.location.pathname;

    if (path.startsWith('/haber/')) {
        var id = path.split('/')[2];
        if (id) {
            fetch('/api/yorumlar/' + id).then(r => r.json()).then(d => yorumlariGoster(d));
            if (isSaved(id)) {
                var btn = document.querySelector('.save-btn');
                if (btn) { btn.innerHTML = '<i class="bi bi-bookmark-fill"></i>'; btn.classList.add('saved'); }
            }
        }
    }

    initLazyBg();

    const toggle = document.getElementById('themeToggle');
    const html = document.documentElement;
    if (toggle) {
        const saved = localStorage.getItem('theme');
        if (saved) { html.setAttribute('data-bs-theme', saved); toggle.innerHTML = saved === 'dark' ? '<i class="bi bi-sun-fill"></i>' : '<i class="bi bi-moon-fill"></i>'; }
        toggle.addEventListener('click', function() {
            const cur = html.getAttribute('data-bs-theme');
            const next = cur === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-bs-theme', next);
            localStorage.setItem('theme', next);
            toggle.innerHTML = next === 'dark' ? '<i class="bi bi-sun-fill"></i>' : '<i class="bi bi-moon-fill"></i>';
        });
    }

    const cookieEl = document.getElementById('cookie-consent');
    if (cookieEl && !localStorage.getItem('cookie_consent')) { setTimeout(() => cookieEl.classList.add('visible'), 500); }

    const backBtn = document.getElementById('back-to-top');
    if (backBtn) {
        window.addEventListener('scroll', () => backBtn.classList.toggle('visible', window.scrollY > 400));
        backBtn.addEventListener('click', () => window.scrollTo({top: 0, behavior: 'smooth'}));
    }

    const progressBar = document.getElementById('reading-progress');
    if (progressBar && path.startsWith('/haber/')) {
        window.addEventListener('scroll', function() {
            const s = window.scrollY, h = document.documentElement.scrollHeight - window.innerHeight;
            progressBar.style.width = (h > 0 ? (s / h) * 100 : 0) + '%';
        });
    }

    initInfiniteScroll();
});
