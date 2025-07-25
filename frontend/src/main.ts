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
    defaultTheme: 'paksaLight',
    themes: {
      paksaLight: {
        dark: false,
        colors: {
          primary: '#1565C0',
          secondary: '#37474F',
          accent: '#3F51B5',
          error: '#D32F2F',
          warning: '#F57C00',
          info: '#1976D2',
          success: '#388E3C',
          background: '#F8FAFC',
          surface: '#FFFFFF',
          'surface-variant': '#F1F5F9',
          'on-primary': '#FFFFFF',
          'on-secondary': '#FFFFFF',
          'on-surface': '#1E293B',
          'on-background': '#1E293B'
        }
      },
      paksaDark: {
        dark: true,
        colors: {
          primary: '#42A5F5',
          secondary: '#78909C',
          accent: '#7986CB',
          error: '#EF5350',
          warning: '#FF9800',
          info: '#29B6F6',
          success: '#66BB6A',
          background: '#0F172A',
          surface: '#1E293B',
          'surface-variant': '#334155',
          'on-primary': '#FFFFFF',
          'on-secondary': '#FFFFFF',
          'on-surface': '#F1F5F9',
          'on-background': '#F1F5F9'
        }
      }
    }
  },
  defaults: {
    VCard: {
      elevation: 2,
      rounded: 'lg'
    },
    VBtn: {
      rounded: 'lg',
      style: 'text-transform: none; font-weight: 500;'
    },
    VTextField: {
      variant: 'outlined',
      density: 'comfortable'
    },
    VSelect: {
      variant: 'outlined',
      density: 'comfortable'
    },
    VTextarea: {
      variant: 'outlined'
    },
    VChip: {
      rounded: 'lg'
    }
  }
})

const pinia = createPinia()
const app = createApp(App)

// Global styles
import './assets/styles/global.css'

app.use(vuetify)
app.use(pinia)
app.use(router)

app.mount('#app')