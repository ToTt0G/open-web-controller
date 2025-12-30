const CACHE_NAME = 'opencontroller-v4';
const ASSETS = [
    '/',
    '/static/manifest.json',
    '/static/css/style.css',
    '/static/js/controller.js',
    '/static/images/icon-192.png',
    '/static/images/icon-512.png',
    '/static/images/apple-touch-icon.png',
    '/offline'
];

// Install Event: Cache core assets
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(ASSETS))
            .then(() => self.skipWaiting())
    );
});

// Activate Event: Clean old caches and take control immediately
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames
                        .filter(name => name.startsWith('opencontroller-') && name !== CACHE_NAME)
                        .map(name => caches.delete(name))
                );
            })
            .then(() => self.clients.claim()) // Take control of all clients immediately
    );
});

// Fetch Event: Network-first for navigation, Stale-While-Revalidate for assets
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip socket.io requests - they need real-time
    if (url.pathname.includes('socket.io')) {
        return;
    }

    // Skip cross-origin requests (like CDN resources)
    if (url.origin !== location.origin) {
        return;
    }

    // Navigation requests: Network-first with offline fallback
    if (request.mode === 'navigate') {
        event.respondWith(
            fetch(request)
                .catch(() => caches.match('/offline'))
        );
        return;
    }

    // Assets: Stale-While-Revalidate
    event.respondWith(
        caches.match(request).then(cachedResponse => {
            const networkFetch = fetch(request)
                .then(response => {
                    // Update cache with new data
                    if (response.ok) {
                        const responseClone = response.clone();
                        caches.open(CACHE_NAME).then(cache => {
                            cache.put(request, responseClone);
                        });
                    }
                    return response;
                })
                .catch(() => cachedResponse);

            // Return cached response immediately if available, otherwise wait for network
            return cachedResponse || networkFetch;
        })
    );
});

// Handle messages from clients
self.addEventListener('message', event => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});
