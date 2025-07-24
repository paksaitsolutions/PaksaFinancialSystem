import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current directory.
  // Set the third parameter to '' to load all env regardless of the `VITE_` prefix.
  const env = loadEnv(mode, process.cwd(), '')
  
  // API URL from environment or default
  const apiBaseUrl = env.VITE_API_BASE_URL || 'http://localhost:8000'
  
  return {
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
      open: true,
      proxy: {
        '/api': {
          target: apiBaseUrl,
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/api/, '')
        }
      },
      headers: {
        'Content-Security-Policy': `default-src 'self' 'unsafe-inline' 'unsafe-eval' ${apiBaseUrl}; connect-src 'self' ${apiBaseUrl} ws://localhost:3003;`
      },
      hmr: {
        host: 'localhost',
        port: 3003,
        protocol: 'ws',
        overlay: true
      },
      watch: {
        usePolling: true,
        ignored: ['**/node_modules/**', '**/.git/**']
      },
      fs: {
        strict: true,
        allow: ['..']
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
  }
})