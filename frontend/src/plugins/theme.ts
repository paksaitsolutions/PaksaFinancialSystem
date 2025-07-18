import { ThemeDefinition } from 'vuetify'

// Light theme
export const lightTheme: ThemeDefinition = {
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
    background: '#F5F7FA',
    'surface-variant': '#FFFFFF',
  }
}

// Dark theme
export const darkTheme: ThemeDefinition = {
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
    background: '#121212',
    'surface-variant': '#1E1E1E',
  }
}