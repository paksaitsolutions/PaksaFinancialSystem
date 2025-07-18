import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { lightTheme, darkTheme } from './theme'

export default createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'light',
    themes: {
      light: lightTheme,
      dark: darkTheme
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