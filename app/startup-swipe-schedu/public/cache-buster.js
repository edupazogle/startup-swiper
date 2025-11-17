// CACHE BUSTER - Runs immediately on page load
(function() {
    console.log('🔥 CACHE BUSTER: Starting aggressive cleanup...');
    
    // 1. Unregister ALL service workers immediately
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.getRegistrations().then(function(registrations) {
            console.log('Found ' + registrations.length + ' service worker(s)');
            for (var registration of registrations) {
                console.log('Unregistering:', registration.scope);
                registration.unregister().then(function(success) {
                    if (success) {
                        console.log('✅ Service worker unregistered');
                    }
                });
            }
        }).catch(function(err) {
            console.log('SW check error:', err);
        });
    }
    
    // 2. Clear all caches
    if ('caches' in window) {
        caches.keys().then(function(names) {
            console.log('Found ' + names.length + ' cache(s)');
            for (var name of names) {
                console.log('Deleting cache:', name);
                caches.delete(name);
            }
        });
    }
    
    // 3. Set flag that we've cleaned up
    try {
        localStorage.setItem('cache_busted', Date.now());
        console.log('✅ Cache bust complete');
    } catch(e) {
        console.log('localStorage not available');
    }
})();
