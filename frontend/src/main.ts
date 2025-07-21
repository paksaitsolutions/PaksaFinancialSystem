import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import App from './App.vue'
import router from './router'
import debug from './debug'
import { useAuthStore } from './modules/auth/store'
import { useMenuStore } from './store/menu'
import AppSnackbar from '@/components/AppSnackbar.vue'
import snackbar from '@/shared/composables/useSnackbar'

// Import Vuetify styles
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'

// Import our custom styles
import './assets/styles/reset.css'
import './assets/styles/main.scss'

// Import plugins
import vuetify from './plugins/vuetify'

// Create app instance
const app = createApp(App)
const pinia = createPinia()

// Add pinia plugins
pinia.use(piniaPluginPersistedstate)

// Use plugins with proper initialization order
app.use(pinia)
app.use(router)
app.use(vuetify)
app.use(snackbar)

// Register global components
app.component('AppSnackbar', AppSnackbar)

// Global error handler
app.config.errorHandler = (err, instance, info) => {
  console.error('Vue error:', err)
  console.error('Error in component:', instance)
  console.error('Error info:', info)
  
  // Show error in snackbar if available
  const snackbar = app.config.globalProperties.$snackbar
  if (snackbar && snackbar.showError) {
    const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred'
    snackbar.showError(errorMessage)
  }
}

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

// Initialize menu store when app starts
const initializeMenuStore = () => {
  const menuStore = useMenuStore()
  menuStore.init()
}

// Start the application
initializeApp().then(() => {
  initializeMenuStore()
})