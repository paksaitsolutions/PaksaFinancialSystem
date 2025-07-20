import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import debug from './debug'
import { useAuthStore } from './modules/auth/store'

// Import Vuetify styles first
import 'vuetify/styles'

// Import PrimeVue styles
import 'primeflex/primeflex.css' // PrimeFlex CSS utilities

// Then import our custom styles
import './assets/styles/reset.css'
import './assets/styles/main.css'

// Import plugins
import vuetify from './plugins/vuetify'
import primevue from './plugins/primevue'

// Create app instance
const app = createApp(App)
const pinia = createPinia()

// Use plugins with proper initialization order
app.use(pinia)
app.use(router)
app.use(vuetify)
app.use(primevue)

// Initialize debug
debug.init()

// Initialize auth state before mounting
const initializeApp = async () => {
  const authStore = useAuthStore()
  
  try {
    await authStore.initialize()
  } catch (error) {
    console.error('Failed to initialize auth state:', error)
  } finally {
    // Mount the app regardless of auth initialization result
    app.mount('#app')
  }
}

// Start the application
initializeApp()