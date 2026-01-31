import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVuePlugin from './plugins/primevue'
import UnifiedSystemPlugin from './plugins/unified-system'

import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import { registerServiceWorker } from './utils/service-worker'

// Import PrimeVue compatible styles
import './assets/styles/primevue-theme.css'

// Lazy load PrimeVue theme
import('primevue/resources/themes/lara-light-blue/theme.css')
import('primevue/resources/primevue.min.css')
import('primeicons/primeicons.css')
import('primeflex/primeflex.css')

// Performance optimizations
import { ImageOptimizer } from './utils/imageOptimization'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(PrimeVuePlugin)
app.use(UnifiedSystemPlugin)

// Initialize auth store
const authStore = useAuthStore()
console.log('Auth store initialized:', { isAuthenticated: authStore.isAuthenticated, token: !!authStore.token })

// Initialize performance optimizations
document.addEventListener('DOMContentLoaded', () => {
  // Lazy load images
  ImageOptimizer.lazyLoadImages()
  
  // Preload critical routes
  if ('requestIdleCallback' in window) {
    requestIdleCallback(() => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      ;(router as any).prefetch?.(['/gl', '/ap', '/ar'])
    })
  }
})

// Register service worker for offline caching
registerServiceWorker()

app.mount('#app')