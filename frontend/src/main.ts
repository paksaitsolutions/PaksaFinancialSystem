import { createApp } from 'vue'
import { createVuetify } from 'vuetify'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Vuetify
import 'vuetify/styles'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import '@mdi/font/css/materialdesignicons.css'

const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#1976d2',
          secondary: '#424242',
          accent: '#82b1ff',
          error: '#ff5252',
          info: '#2196f3',
          success: '#4caf50',
          warning: '#ffc107'
        }
      }
    }
  }
})

const pinia = createPinia()
const app = createApp(App)

app.use(vuetify)
app.use(pinia)
app.use(router)

app.mount('#app')