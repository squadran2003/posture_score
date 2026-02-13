import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

const sharedColors = {
  primary: '#4CAF50',
  secondary: '#2196F3',
  accent: '#FF9800',
  error: '#F44336',
  warning: '#FF9800',
  info: '#2196F3',
  success: '#4CAF50',
}

export default createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          ...sharedColors,
          background: '#F5F5F5',
        },
      },
      dark: {
        dark: true,
        colors: {
          ...sharedColors,
          background: '#121212',
          surface: '#1E1E1E',
        },
      },
    },
  },
})
