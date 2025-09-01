import { defineConfig, loadEnv, type ConfigEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
export default defineConfig(({ mode }: ConfigEnv) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: `
            @import "@/assets/scss/_variables.scss";
            @import "@/assets/scss/_mixins.scss";
          `
        }
      }
    },

    base: env.VITE_APP_BASE_URL || '/',

    define: {
      __APP_VERSION__: JSON.stringify(env.VITE_APP_VERSION || '1.0.0'),
      __APP_ENV__: JSON.stringify(mode)
    },

    resolve: {
      alias: [
        { find: '@', replacement: fileURLToPath(new URL('./src', import.meta.url)) },
        { find: /^~(.+)/, replacement: fileURLToPath(new URL('./node_modules/$1', import.meta.url)) },
        { find: 'vue', replacement: 'vue/dist/vue.esm-bundler.js' },
        { find: '@assets', replacement: fileURLToPath(new URL('./src/assets', import.meta.url)) },
        { find: '@components', replacement: fileURLToPath(new URL('./src/components', import.meta.url)) },
        { find: '@views', replacement: fileURLToPath(new URL('./src/views', import.meta.url)) },
        { find: '@stores', replacement: fileURLToPath(new URL('./src/stores', import.meta.url)) },
        { find: '@utils', replacement: fileURLToPath(new URL('./src/utils', import.meta.url)) },
        { find: '@api', replacement: fileURLToPath(new URL('./src/api', import.meta.url)) },
        { find: '@router', replacement: fileURLToPath(new URL('./src/router', import.meta.url)) }
      ],
      extensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json', '.vue']
    },

    plugins: [
      vue({
        script: { defineModel: true, propsDestructure: true }
      })
    ],

    server: {
      host: '0.0.0.0',
      port: 3000,
      strictPort: true,
      open: true,
      headers: {
        'Content-Security-Policy':
          "default-src 'self'; " +
          "script-src 'self' 'unsafe-inline' 'unsafe-eval' https:; " +
          "style-src 'self' 'unsafe-inline' https:; " +
          "font-src 'self' https: data:; " +
          "img-src 'self' https://images.unsplash.com https: data: blob:; " +
          "connect-src 'self' http://localhost:* https: ws: wss:;"
      },
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
          ws: true
        },
        '/auth': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false
        }
      }
    },

    preview: {
      port: 4173,
      host: '0.0.0.0',
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false
        }
      }
    },

    build: {
      outDir: 'dist',
      assetsDir: 'assets',
      sourcemap: true,
      minify: 'esbuild',
      rollupOptions: {
        output: {
          manualChunks: {
            vue: ['vue', 'vue-router', 'pinia'],
            charts: ['chart.js'],
            vendor: ['axios', 'date-fns']
          }
        }
      }
    },

    optimizeDeps: {
      include: [
        'vue',
        'vue-router',
        'pinia'
      ],
      exclude: ['primevue']
    }
  }
})
