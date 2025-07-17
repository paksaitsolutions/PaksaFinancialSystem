import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Import styles
import './assets/styles/reset.css'
import './assets/styles/main.scss'
import './assets/styles/tailwind.css'
import './assets/styles/vuetify.scss'
import './assets/styles/compatibility.css'

// Vuetify
import 'vuetify/styles'
import vuetify from './plugins/vuetify'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(vuetify)

app.mount('#app')
