// MES Cable — Service Worker
// Cache shell tĩnh để dùng offline; dữ liệu thực luôn lấy realtime từ Firebase.
const CACHE_NAME = 'mes-cable-cache-v1';
const CORE_ASSETS = [
  './',
  './index.html',
  './manifest.json',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(CORE_ASSETS)).catch(() => {})
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  // Không cache Firebase / API calls — luôn lấy trực tiếp từ mạng.
  if (req.url.includes('firebaseio.com') || req.url.includes('googleapis.com') || req.url.includes('gstatic.com')) {
    return;
  }

  // version.json luôn lấy mới từ mạng để banner cập nhật hoạt động chính xác.
  if (req.url.includes('version.json')) {
    event.respondWith(fetch(req).catch(() => caches.match(req)));
    return;
  }

  event.respondWith(
    caches.match(req).then((cached) => {
      const fetchPromise = fetch(req)
        .then((res) => {
          if (res && res.status === 200) {
            const resClone = res.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(req, resClone));
          }
          return res;
        })
        .catch(() => cached);
      return cached || fetchPromise;
    })
  );
});
