import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { md3 } from 'vuetify/blueprints'
import { aliases, mdi } from 'vuetify/iconsets/mdi-svg'

// Import the styles you want to use
import 'vuetify/styles'

export default createVuetify({
  components,
  directives,
  blueprint: md3, // Enable Material Design 3
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
        dark: false,
        colors: {
          primary: '#1976D2',
          secondary: '#424242',
          accent: '#82B1FF',
          error: '#FF5252',
          info: '#2196F3',
          success: '#4CAF50',
          warning: '#FFC107',
        }
      },
      dark: {
        dark: true,
        colors: {
          primary: '#2196F3',
          secondary: '#424242',
          accent: '#FF4081',
          error: '#FF5252',
          info: '#2196F3',
          success: '#4CAF50',
          warning: '#FFC107',
        }
      }
    }
  },
  defaults: {
    global: {
      ripple: true,
    },
    VBtn: {
      variant: 'flat',
      rounded: 'md',
    },
    VCard: {
      elevation: 2,
      rounded: 'lg',
    },
    VTextField: {
      variant: 'outlined',
      density: 'comfortable',
    },
    VAlert: {
      variant: 'tonal',
      border: 'start',
      borderColor: 'primary',
    }
  }
})