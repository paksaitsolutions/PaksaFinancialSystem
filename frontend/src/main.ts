import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { setupPrimeVue } from './plugins/primevue'
import aiAssistant from './plugins/ai-assistant'
import './plugins/axios'

// 0. Critical layout fixes (must be first)
import './assets/styles/critical-layout.css'

// 1. PrimeVue Theme and Base Styles
import 'primevue/resources/themes/saga-blue/theme.css'
import 'primevue/resources/primevue.min.css'
import 'primeicons/primeicons.css'
import 'primeflex/primeflex.css'

// 2. Custom SCSS styles (will override PrimeVue defaults)
import './assets/scss/main.scss'

// 3. Component-specific styles (if any)
import './assets/styles/reset.css'
import './assets/styles/global.css'
import './assets/styles/layout.css'

const pinia = createPinia()
const app = createApp(App)

// Setup PrimeVue
setupPrimeVue(app)

app.use(pinia)
app.use(router)

// Register AI Assistant plugin
app.use(aiAssistant)

app.mount('#app')