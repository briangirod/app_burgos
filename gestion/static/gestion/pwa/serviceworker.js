self.addEventListener('install', function(e) {
  console.log('Service Worker instalado');
  e.waitUntil(
    caches.open('clinica-v1').then(function(cache) {
      return cache.addAll(['/']);
    })
  );
});

self.addEventListener('fetch', function(e) {
  e.respondWith(
    caches.match(e.request).then(function(response) {
      return response || fetch(e.request);
    })
  );
});
