const CACHE_NAME = 'opencontroller-v3';
const ASSETS = [
    '/',
    '/static/manifest.json',
    '/static/css/style.css',
    '/static/js/controller.js',
    '/static/images/icon-192.png'
];

// Install Event: Cache core assets
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
    );
    self.skipWaiting();
});

// Activate Event: Clean old caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.filter(name => name !== CACHE_NAME)
                    .map(name => caches.delete(name))
            );
        })
    );
});

// Fetch Event: Stale-While-Revalidate (fast + updates)
self.addEventListener('fetch', event => {
    // Skip socket.io requests - they need real-time
    if (event.request.url.includes('socket.io')) {
        return;
    }

    event.respondWith(
        caches.match(event.request).then(cachedResponse => {
            const networkFetch = fetch(event.request).then(response => {
                // Update cache with new data
                if (response.ok) {
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME).then(cache => {
                        cache.put(event.request, responseClone);
                    });
                }
                return response;
            }).catch(() => cachedResponse);

            // Return cached response immediately if available, otherwise wait for network
            return cachedResponse || networkFetch;
        })
    );
});
