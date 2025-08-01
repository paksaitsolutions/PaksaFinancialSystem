import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { setupPrimeVue } from './plugins/primevue'

// PrimeVue Theme and Styles
import './assets/primevue/theme.css'  // Local theme override
import 'primevue/resources/primevue.min.css'  // Core CSS
import 'primeicons/primeicons.css'            // Icons
import 'primeflex/primeflex.css'              // PrimeFlex

const pinia = createPinia()
const app = createApp(App)

// Setup PrimeVue
setupPrimeVue(app)

app.use(pinia)
app.use(router)

app.mount('#app')