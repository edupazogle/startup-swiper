// Self-unregistering service worker
// This replaces the old service worker and immediately unregisters itself

self.addEventListener('install', function(event) {
  console.log('Service worker installing - will immediately unregister');
  self.skipWaiting();
});

self.addEventListener('activate', function(event) {
  console.log('Service worker activating - unregistering now');
  
  event.waitUntil(
    // Delete all caches
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          console.log('Deleting cache:', cacheName);
          return caches.delete(cacheName);
        })
      );
    }).then(function() {
      // Unregister this service worker
      return self.registration.unregister();
    }).then(function() {
      console.log('Service worker unregistered successfully');
      // Force reload all clients
      return self.clients.matchAll();
    }).then(function(clients) {
      clients.forEach(function(client) {
        client.postMessage({
          type: 'SW_UNREGISTERED',
          message: 'Service worker has been removed. Please reload the page.'
        });
      });
    })
  );
});

// Don't cache anything
self.addEventListener('fetch', function(event) {
  // Just pass through to network
  return;
});

console.log('Self-unregistering service worker loaded');
