import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { fileURLToPath, URL } from 'node:url';

export default defineConfig({
  plugins: [vue()],
  
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      'vue': 'vue/dist/vue.esm-bundler.js'
    }
  },
  
  server: {
    port: 3001,
    host: '0.0.0.0',
    strictPort: true,
    open: true
  },
  
  preview: {
    port: 3000,
    host: true,
    strictPort: true
  }
});
