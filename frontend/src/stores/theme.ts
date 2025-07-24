import { defineStore } from 'pinia'
import { useTheme } from 'vuetify'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    isDark: false
  }),

  actions: {
    toggleTheme() {
      this.isDark = !this.isDark
      this.applyTheme()
      this.saveThemePreference()
    },

    setTheme(isDark: boolean) {
      this.isDark = isDark
      this.applyTheme()
      this.saveThemePreference()
    },

    applyTheme() {
      const theme = useTheme()
      theme.global.name.value = this.isDark ? 'dark' : 'light'
      
      // Update data attribute for CSS theming
      document.documentElement.setAttribute('data-theme', this.isDark ? 'dark' : 'light')
      
      // Update CSS custom properties for consistent theming
      const root = document.documentElement
      if (this.isDark) {
        root.style.setProperty('--bg-color', '#121212')
        root.style.setProperty('--surface-color', '#1e1e1e')
        root.style.setProperty('--text-color', '#ffffff')
        root.style.setProperty('--text-secondary', '#b0b0b0')
      } else {
        root.style.setProperty('--bg-color', '#ffffff')
        root.style.setProperty('--surface-color', '#f5f5f5')
        root.style.setProperty('--text-color', '#000000')
        root.style.setProperty('--text-secondary', '#666666')
      }
    },

    loadThemePreference() {
      const saved = localStorage.getItem('theme-preference')
      if (saved) {
        this.isDark = saved === 'dark'
      } else {
        // Check system preference
        this.isDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      }
      this.applyTheme()
    },

    saveThemePreference() {
      localStorage.setItem('theme-preference', this.isDark ? 'dark' : 'light')
    }
  }
})