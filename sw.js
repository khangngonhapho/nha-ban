const CACHE_NAME = 'bds-khangngo-pwa-v3';
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
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  
  // Only intercept GET requests
  if (e.request.method !== 'GET') return;
  
  // Bypass cache for dynamic API requests and remote images (R2, CloudFront, etc.)
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
