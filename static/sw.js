const CACHE = 'pusula-v3';
const STATIC = [
    '/static/css/style.css?v=6',
    '/static/js/main.js?v=6',
    '/static/manifest.json',
];

self.addEventListener('install', e => {
    e.waitUntil(caches.open(CACHE).then(cache => cache.addAll(STATIC)));
    self.skipWaiting();
});

self.addEventListener('activate', e => {
    e.waitUntil(
        caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    );
    self.clients.claim();
});

self.addEventListener('fetch', e => {
    const url = new URL(e.request.url);
    if (STATIC.includes(url.pathname + (url.search || ''))) {
        e.respondWith(caches.match(e.request).then(r => r || fetch(e.request)));
    }
});

// Push notification
self.addEventListener('push', e => {
    const data = e.data ? e.data.json() : {};
    const title = data.title || 'Pusula - Son Dakika';
    const options = {
        body: data.body || 'Yeni haberler var!',
        icon: '/static/favicon.ico',
        badge: '/static/favicon.ico',
        data: { url: data.url || '/' }
    };
    e.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', e => {
    e.notification.close();
    const url = e.notification.data?.url || '/';
    e.waitUntil(clients.openWindow(url));
});
