import { createApp } from 'vue'
import pinia from './stores'
import App from './App.vue'
import router from './router'
import debug from './debug'

// Import Vuetify styles first
import 'vuetify/styles'

// Then import our custom styles
import './assets/styles/reset.css'
import './assets/styles/main.css'
import vuetify from './plugins/vuetify'

const app = createApp(App)

app.use(pinia)
app.use(router)
app.use(vuetify)

// Initialize debug
debug.init();

app.mount('#app')