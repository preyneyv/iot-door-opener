const cacheName = 'lockbot-v1.0.1';
const appShellFiles = [
    '/',
    '/index.html',
    '/manifest.json',
    '/favicon.ico',
    '/script.js',
    '/style.css',
    '/images/logo.png',
    '/images/offline.png',
];

self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.filter(cn => cn !== cacheName)
            .map(function(cacheName) {
          return caches.delete(cacheName);
        })
      );
    })
  );
});

self.addEventListener('install', (e) => {
  console.log('[Service Worker] Install');
  e.waitUntil((async () => {
    const cache = await caches.open(cacheName);
    console.log('[Service Worker] Caching app files');
    await cache.addAll(appShellFiles);
  })());
});

self.addEventListener('fetch', (e) => {
  e.respondWith((async () => {
    // const r = await caches.match(e.request);
    // console.log(`[Service Worker] Fetching resource: ${e.request.url}`);
    // if (r) { return r; }

    const response = await fetch(e.request);
    if (/fonts.(googleapis|gstatic).com/.test(e.request.url)) {
        const cache = await caches.open(cacheName);
        console.log(`[Service Worker] Caching Google Font: ${e.request.url}`);
        void cache.put(e.request, response.clone());
    }

    return response;
  })());
});