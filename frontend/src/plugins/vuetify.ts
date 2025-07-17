import { createVuetify } from 'vuetify'
import 'vuetify/styles'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { md3 } from 'vuetify/blueprints'

export default createVuetify({
  blueprint: md3,
  components,
  directives,
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        dark: false,
        colors: {
          primary: '#1867C0',
          secondary: '#5CBBF6',
          accent: '#82B1FF',
          error: '#FF5252',
          info: '#2196F3',
          success: '#4CAF50',
          warning: '#FFC107',
          'on-primary': '#FFFFFF',
          'on-secondary': '#FFFFFF',
          'on-accent': '#FFFFFF',
          'on-error': '#FFFFFF',
          'on-info': '#FFFFFF',
          'on-success': '#FFFFFF',
          'on-warning': '#000000',
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
          warning: '#FB8C00',
          'on-primary': '#FFFFFF',
          'on-secondary': '#FFFFFF',
          'on-accent': '#FFFFFF',
          'on-error': '#FFFFFF',
          'on-info': '#FFFFFF',
          'on-success': '#FFFFFF',
          'on-warning': '#000000',
        }
      }
    }
  },
  defaults: {
    VBtn: {
      variant: 'flat',
      rounded: 'md',
    },
    VCard: {
      rounded: 'lg',
    },
    VTextField: {
      variant: 'outlined',
      density: 'comfortable',
    },
    VAlert: {
      variant: 'tonal',
      closable: true,
    }
  }
})