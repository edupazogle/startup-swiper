// Removed: Service worker disabled intentionally
if (false) {
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
    const url = new URL(event.request.url);
    
    // Skip service worker entirely for API requests
    // This allows CORS headers to work properly
    if (url.port === '8000' || 
        url.hostname.includes('localhost') && url.port === '8000' ||
        event.request.url.includes('/api/') || 
        event.request.url.includes(':8000') ||
        event.request.url.includes('/feedback/') ||
        event.request.url.includes('/insights/')) {
      // Don't intercept - let browser handle it normally
      return;
    }
    
    // Only cache non-API requests (static assets, pages, etc.)
    event.respondWith(
      caches.match(event.request)
        .then((response) => {
          // Cache hit - return response
          if (response) {
            return response;
          }
          return fetch(event.request);
        })
        .catch((error) => {
          console.error('Service worker fetch error:', error);
          // Fallback to network on error
          return fetch(event.request);
        })
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
