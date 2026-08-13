const CACHE = 'wrxm-fc26-v16';

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
  '/Keeyvon-Jenkins-FC26-Manager-Career/history.html',
  '/Keeyvon-Jenkins-FC26-Manager-Career/media/index.html',
  '/Keeyvon-Jenkins-FC26-Manager-Career/assets/style.css',
  '/Keeyvon-Jenkins-FC26-Manager-Career/assets/media_index.js',
  '/Keeyvon-Jenkins-FC26-Manager-Career/assets/pl_table.js',
  '/Keeyvon-Jenkins-FC26-Manager-Career/assets/home_config.js',
  '/Keeyvon-Jenkins-FC26-Manager-Career/assets/home.js',
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

// Network-first for HTML, CSS, and JS (always fresh — roster/fixture data
// lives in submit_data.js and must never go stale behind a service worker
// cache). Stale-while-revalidate for images/fonts/icons: serve the cached
// copy instantly, but always refetch in the background and update the
// cache, so a photo swapped in on the same filename (e.g. a player's
// headshot) is fresh on the *next* load instead of stuck forever behind
// the first cached copy.
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET') return;

  if (url.pathname.endsWith('.html') || url.pathname.endsWith('/') || url.pathname.endsWith('.css') || url.pathname.endsWith('.js')) {
    e.respondWith(
      fetch(e.request)
        .then(res => { caches.open(CACHE).then(c => c.put(e.request, res.clone())); return res; })
        .catch(() => caches.match(e.request))
    );
  } else {
    e.respondWith(
      caches.open(CACHE).then(cache =>
        cache.match(e.request).then(cached => {
          const fetchPromise = fetch(e.request).then(res => {
            cache.put(e.request, res.clone());
            return res;
          }).catch(() => cached);
          return cached || fetchPromise;
        })
      )
    );
  }
});
