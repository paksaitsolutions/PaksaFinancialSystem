import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { fileURLToPath, URL } from 'node:url';
import { resolve } from 'path';

export default defineConfig({
  plugins: [
    vue({
      template: {
        compilerOptions: {
          isCustomElement: (tag) => tag.includes('-')
        }
      },
      script: {
        defineModel: true,
        propsDestructure: true
      }
    })
  ],
  
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      '~': resolve(__dirname, './src'),
      'vue': 'vue/dist/vue.esm-bundler.js',
      '~bootstrap': resolve(__dirname, 'node_modules/bootstrap'),
      '~vuetify': resolve(__dirname, 'node_modules/vuetify')
    },
    extensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json', '.vue', '.scss', '.css']
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
      usePolling: true,
      interval: 100
    }
  },
  
  optimizeDeps: {
    include: ['vue', 'vue-router', 'pinia', 'vuetify'],
    exclude: ['@mdi/font']
  },
  
  build: {
    target: 'esnext',
    minify: 'esbuild',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'vuetify-vendor': ['vuetify', 'vuetify/styles'],
          'mdi': ['@mdi/font']
        }
      }
    }
  }
});
