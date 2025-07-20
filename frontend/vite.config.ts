import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import path from 'path'

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
      'vue': 'vue/dist/vue.esm-bundler.js',
      '~bootstrap': path.resolve(__dirname, 'node_modules/bootstrap'),
      '~vuetify': path.resolve(__dirname, 'node_modules/vuetify')
    }
  },
  
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `
          @import "@/scss/variables";
          @import "@/scss/settings";
        `
      }
    }
  },
  
  server: {
    port: 3003,
    host: '0.0.0.0',
    strictPort: true,
    hmr: {
      host: 'localhost',
      port: 3003
    },
    watch: {
      usePolling: true
    }
  },
  
  preview: {
    port: 3003,
    host: true,
    strictPort: true
  },
  
  optimizeDeps: {
    include: ['vue', 'vue-router', 'pinia', 'primevue']
  },
  
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: true
  }
})
