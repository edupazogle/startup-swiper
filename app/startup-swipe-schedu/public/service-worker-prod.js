/* eslint-disable no-restricted-globals */
/**
 * Service Worker for Push Notifications
 * Handles background push notifications and deep linking
 * PRODUCTION ONLY - Not used in development
 */

// Only activate in production
if (process.env.NODE_ENV === 'production') {
  const CACHE_NAME = 'slush-2025-v1';
  const urlsToCache = [
    '/',
    '/index.html',
  ];

  // Install event - cache resources
  self.addEventListener('install', (event) => {
    event.waitUntil(
      caches.open(CACHE_NAME)
        .then((cache) => {
          console.log('Opened cache');
          return cache.addAll(urlsToCache);
        })
    );
    self.skipWaiting();
  });

  // Activate event - clean up old caches
  self.addEventListener('activate', (event) => {
    event.waitUntil(
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME) {
              console.log('Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
    );
    self.clients.claim();
  });

  // Fetch event - serve from cache when offline
  self.addEventListener('fetch', (event) => {
    // Skip caching for API requests
    if (event.request.url.includes('/api/') || event.request.url.includes(':8000')) {
      return;
    }
    
    event.respondWith(
      caches.match(event.request)
        .then((response) => {
          // Cache hit - return response
          if (response) {
            return response;
          }
          return fetch(event.request);
        }
      )
    );
  });

  // Push notification event
  self.addEventListener('push', (event) => {
    const options = {
      body: event.data ? event.data.text() : 'New notification',
      icon: '/icon-192.png',
      badge: '/icon-192.png',
      vibrate: [200, 100, 200],
      data: {
        dateOfArrival: Date.now(),
        primaryKey: 1
      },
      actions: [
        {
          action: 'explore',
          title: 'View Details'
        },
        {
          action: 'close',
          title: 'Close'
        }
      ]
    };

    event.waitUntil(
      self.registration.showNotification('Startup Swiper', options)
    );
  });

  // Notification click event
  self.addEventListener('notificationclick', (event) => {
    event.notification.close();

    if (event.action === 'explore') {
      // Open the app
      event.waitUntil(
        clients.openWindow('/')
      );
    }
  });
} else {
  console.log('Service Worker: Development mode - SW disabled');
}
