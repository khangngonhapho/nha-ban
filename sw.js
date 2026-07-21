const CACHE_NAME = 'bds-khangngo-pwa-v19';
const ASSETS = [
  '/view-images',
  '/static/img/icon-192.png',
  '/static/img/icon-512.png'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS);
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    (async () => {
      if (self.registration.navigationPreload) {
        try { await self.registration.navigationPreload.enable(); } catch (err) {}
      }
      const keys = await caches.keys();
      await Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
      await self.clients.claim();
    })()
  );
});

self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  
  // Only intercept GET requests
  if (e.request.method !== 'GET') return;

  // 1. Navigation and iframe preview requests: fetch string URL directly to eliminate 30s SW deadlock
  if (e.request.mode === 'navigate' || url.searchParams.has('preview') || url.searchParams.has('s')) {
    e.respondWith(
      (async () => {
        try {
          if (e.preloadResponse) {
            const preloaded = await e.preloadResponse;
            if (preloaded) return preloaded;
          }
          return await fetch(e.request.url, { cache: 'no-cache' });
        } catch (err) {
          return await fetch(e.request.url);
        }
      })()
    );
    return;
  }
  
  // 2. Bypass API and remote assets
  if (
    url.pathname.startsWith('/api/') || 
    url.hostname.includes('googleapis') || 
    url.hostname.includes('cloudinary') || 
    url.hostname.includes('r2.dev') ||
    url.hostname.includes('cloudfront.net')
  ) {
    return;
  }

  e.respondWith(
    caches.match(e.request).then((cachedResponse) => {
      if (cachedResponse) {
        // Fetch in background to update cache for next time
        fetch(e.request).then((networkResponse) => {
          if (networkResponse.status === 200) {
            caches.open(CACHE_NAME).then((cache) => cache.put(e.request, networkResponse));
          }
        }).catch(() => {});
        return cachedResponse;
      }
      return fetch(e.request);
    })
  );
});
