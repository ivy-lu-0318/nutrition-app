const CACHE_NAME = 'nutrition-app-v4';
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
  // tfnd.json 不快取，讓瀏覽器直接從網路拿，避免 iOS Safari 快取大檔出錯
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS).catch(() => {}))
  );
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => {
      // 通知所有開著的分頁：有新版本，自動重新載入
      return self.clients.matchAll({ type: 'window' }).then(clients =>
        clients.forEach(client => client.postMessage({ type: 'SW_UPDATED' }))
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  // tfnd.json 永遠從網路取，不走快取
  if (e.request.url.includes('tfnd.json')) {
    e.respondWith(fetch(e.request));
    return;
  }
  e.respondWith(
    caches.match(e.request).then(cached => cached || fetch(e.request))
  );
});
