const CACHE = 'wrxm-fc26-v10';

const PRECACHE = [
  '/Keeyvon-Jenkins-FC26-Manager-Career/',
  '/Keeyvon-Jenkins-FC26-Manager-Career/index.html',
  '/Keeyvon-Jenkins-FC26-Manager-Career/journal.html',
  '/Keeyvon-Jenkins-FC26-Manager-Career/roster.html',
  '/Keeyvon-Jenkins-FC26-Manager-Career/season.html',
  '/Keeyvon-Jenkins-FC26-Manager-Career/depth_chart.html',
  '/Keeyvon-Jenkins-FC26-Manager-Career/academy.html',
  '/Keeyvon-Jenkins-FC26-Manager-Career/dossier.html',
  '/Keeyvon-Jenkins-FC26-Manager-Career/submit.html',
  '/Keeyvon-Jenkins-FC26-Manager-Career/assets/style.css',
  '/Keeyvon-Jenkins-FC26-Manager-Career/manifest.json',
  '/Keeyvon-Jenkins-FC26-Manager-Career/manifest-submit.json',
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(PRECACHE)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// Network-first for HTML and CSS (always fresh); cache-first for images/fonts
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET') return;

  if (url.pathname.endsWith('.html') || url.pathname.endsWith('/') || url.pathname.endsWith('.css')) {
    e.respondWith(
      fetch(e.request)
        .then(res => { caches.open(CACHE).then(c => c.put(e.request, res.clone())); return res; })
        .catch(() => caches.match(e.request))
    );
  } else {
    e.respondWith(
      caches.match(e.request).then(cached => cached || fetch(e.request))
    );
  }
});
