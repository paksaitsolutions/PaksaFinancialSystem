import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [
    vue({
      template: {
        compilerOptions: {
          isCustomElement: (tag) => tag.includes('-')
        }
      }
    })
  ],
  
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      'vue': 'vue/dist/vue.esm-bundler.js'
    }
  },
  
  server: {
    port: 3000,
    host: true,
    strictPort: true,
    hmr: {
      overlay: false
    }
  },
  
  optimizeDeps: {
    include: ['vue', 'vue-router', 'pinia', 'primevue']
  }
})
