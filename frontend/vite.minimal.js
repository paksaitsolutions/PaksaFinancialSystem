import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { resolve } from 'path'

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
      'vue': 'vue/dist/vue.esm-bundler.js',
      '~': resolve(__dirname, './src')
    },
    extensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json', '.vue']
  },
  
  server: {
    port: 3002,
    host: '0.0.0.0',
    strictPort: true,
    open: true,
    hmr: {
      host: 'localhost',
      port: 3002,
      protocol: 'ws',
      overlay: true
    },
    fs: {
      strict: false,
      allow: ['..']
    },
    cors: true
  },
  
  preview: {
    port: 3002,
    host: true,
    strictPort: true
  },
  
  optimizeDeps: {
    include: [
      'vue',
      'vue-router',
      'pinia',
      'primevue',
      '@mdi/font',
      'vuetify',
      'vuelidate',
      'vuelidate/validators'
    ],
    esbuildOptions: {
      target: 'esnext',
      supported: { 
        bigint: true 
      },
    },
  },
  
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: true,
    minify: 'esbuild',
    chunkSizeWarningLimit: 2000,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html')
      },
      output: {
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash][ext]',
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router', 'pinia', 'vue-i18n'],
          'vuetify-vendor': ['vuetify', 'vuetify/styles'],
          'primevue-vendor': ['primevue', 'primeicons', 'primeflex']
        }
      }
    },
    commonjsOptions: {
      include: [/node_modules/],
      transformMixedEsModules: true
    }
  },
  
  logLevel: 'info',
  clearScreen: false,
  define: {
    __VUE_I18N_FULL_INSTALL__: true,
    __VUE_I18N_LEGACY_API__: false,
    __VUE_PROD_DEVTOOLS__: true,
    __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: false,
    'process.env': {}
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `
          @use 'sass:math';
          @import "@/assets/styles/variables";
          @import "@/assets/styles/mixins";
        `
      }
    }
  }
})
