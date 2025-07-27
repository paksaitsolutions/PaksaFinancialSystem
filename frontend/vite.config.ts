import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'
import { resolve } from 'path'

export default defineConfig({
  plugins: [
    vue(),
vuetify({
      autoImport: true,
      styles: {
        configFile: 'src/scss/settings.scss'
      }
    })
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3000,
    host: true,
    headers: {
      // Security headers for development
      'X-Frame-Options': 'SAMEORIGIN',
      'X-Content-Type-Options': 'nosniff',
      'Referrer-Policy': 'strict-origin-when-cross-origin'
    }
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'pinia'],
          vuetify: ['vuetify'],
          'general-ledger': ['./src/modules/general-ledger'],
          'accounts-payable': ['./src/modules/accounts-payable'],
          'budget': ['./src/modules/budget'],
          'reports': ['./src/views/reports'],
          'admin': ['./src/views/admin', './src/views/rbac', './src/views/settings']
        }
      }
    },
    chunkSizeWarningLimit: 1000
  }
})