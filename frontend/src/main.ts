import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { setupPrimeVue } from './plugins/primevue'

// PrimeVue Theme and Styles
import './assets/primevue/theme.css'
import 'primevue/resources/primevue.min.css'
import 'primeicons/primeicons.css'
import 'primeflex/primeflex.css'

const pinia = createPinia()
const app = createApp(App)

// Setup PrimeVue
setupPrimeVue(app)

app.use(pinia)
app.use(router)

app.mount('#app')