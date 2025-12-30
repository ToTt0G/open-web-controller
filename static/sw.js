/**
 * OpenController Service Worker
 * Enables offline functionality and PWA installation
 */

const CACHE_NAME = 'opencontroller-v2';
const urlsToCache = [
    '/',
    '/static/css/style.css',
    '/static/js/controller.js',
    '/static/icons/icon.svg',
    '/manifest.json'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(urlsToCache))
    );
    self.skipWaiting();
});

self.addEventListener('fetch', event => {
    // Don't cache socket.io requests
    if (event.request.url.includes('socket.io')) {
        return;
    }

    event.respondWith(
        caches.match(event.request)
            .then(response => response || fetch(event.request))
    );
});

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
