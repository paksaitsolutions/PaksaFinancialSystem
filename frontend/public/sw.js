// Service Worker for caching API responses and static assets
const CACHE_NAME = 'paksa-financial-v1'
const API_CACHE_NAME = 'paksa-api-v1'

const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json'
]

const API_CACHE_PATTERNS = [
  /\/api\/v1\/gl\/accounts/,
  /\/api\/v1\/ap\/vendors/,
  /\/api\/v1\/ar\/customers/,
  /\/api\/v1\/hrm\/employees/
]

// Install event
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(STATIC_ASSETS))
  )
})

// Fetch event with caching strategy
self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)

  // API caching strategy
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      caches.open(API_CACHE_NAME).then(cache => {
        return cache.match(request).then(response => {
          if (response) {
            // Return cached response and update in background
            fetch(request).then(fetchResponse => {
              if (fetchResponse.ok) {
                cache.put(request, fetchResponse.clone())
              }
            })
            return response
          }
          
          // Fetch and cache
          return fetch(request).then(fetchResponse => {
            if (fetchResponse.ok && request.method === 'GET') {
              cache.put(request, fetchResponse.clone())
            }
            return fetchResponse
          })
        })
      })
    )
    return
  }

  // Static assets caching
  event.respondWith(
    caches.match(request)
      .then(response => response || fetch(request))
  )
})

// Activate event
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME && cacheName !== API_CACHE_NAME) {
            return caches.delete(cacheName)
          }
        })
      )
    })
  )
})