import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { setupPrimeVue } from './plugins/primevue'
import './plugins/axios'

// 1. PrimeVue Theme and Base Styles (must be first)
import 'primevue/resources/themes/saga-blue/theme.css'  // or your preferred theme
import 'primevue/resources/primevue.min.css'
import 'primeicons/primeicons.css'
import 'primeflex/primeflex.css'

// 2. Custom SCSS styles (will override PrimeVue defaults)
import './assets/scss/main.scss'

// 3. Component-specific styles (if any)
import './assets/styles/reset.css'
import './assets/styles/global.css'

const pinia = createPinia()
const app = createApp(App)

// Setup PrimeVue
setupPrimeVue(app)

app.use(pinia)
app.use(router)

app.mount('#app')