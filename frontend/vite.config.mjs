/* vite.config.mjs */

import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import vuetify from 'vite-plugin-vuetify';
import path from 'path';

export default defineConfig({
  plugins: [
    vue(),
    vuetify({
      autoImport: true,
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  optimizeDeps: {
    include: ['vue', 'vue-router', 'pinia', 'vuetify'], // Removed '@mdi/font' from here
  },
  build: {
    target: 'esnext',
    minify: 'terser', // remove 'minify: esbuild'
    sourcemap: true, // keep one 'sourcemap' key only
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
    rollupOptions: {
      output: {
        manualChunks: {
          vuetify: ['vuetify', 'vuetify/styles'],
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
        },
        chunkFileNames: 'assets/js/[name].[hash].js',
        entryFileNames: 'assets/js/[name].[hash].js',
      },
    },
  },
});
