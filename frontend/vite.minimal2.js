import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { fileURLToPath, URL } from 'node:url';
import { resolve } from 'path';

export default defineConfig({
  plugins: [
    vue({
      template: {
        compilerOptions: {
          isCustomElement: (tag) => ['v-container', 'v-row', 'v-col', 'v-card', 'v-card-item', 'v-card-title', 'v-card-subtitle', 'v-card-text', 'v-form', 'v-text-field', 'v-btn', 'v-icon', 'v-checkbox', 'v-img', 'v-alert'].includes(tag)
        }
      }
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      '@shared': fileURLToPath(new URL('./src/shared', import.meta.url)),
      'vue': 'vue/dist/vue.esm-bundler.js'
    },
    extensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json', '.vue']
  },
  server: {
    port: 3003,
    host: '0.0.0.0',
    strictPort: true,
    open: true,
    hmr: {
      host: 'localhost',
      port: 3003,
      protocol: 'ws'
    },
    fs: {
      strict: false
    }
  },
  preview: {
    port: 3003,
    host: true,
    strictPort: true
  },
  optimizeDeps: {
    include: ['@vuelidate/validators', '@vuelidate/core']
  },
  logLevel: 'info',
  clearScreen: false
});
