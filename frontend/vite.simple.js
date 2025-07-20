import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { fileURLToPath, URL } from 'node:url';

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
  
  server: {
    port: 3002,
    host: '0.0.0.0',
    strictPort: true,
    open: true,
    hmr: {
      host: 'localhost',
      port: 3002
    }
  },
  
  preview: {
    port: 3002,
    host: true,
    strictPort: true
  },
  
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: true
  }
});
