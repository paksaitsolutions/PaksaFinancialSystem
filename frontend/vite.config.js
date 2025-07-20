import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import vuetify from 'vite-plugin-vuetify';
import { fileURLToPath, URL } from 'node:url';
import { createHash } from 'crypto';

// Generate a nonce for the current build
const nonce = createHash('sha256')
  .update(Math.random().toString())
  .digest('base64');

// Base configuration
const baseConfig = {
  base: '/',
  plugins: [
    vue({
      template: {
        compilerOptions: {
          isCustomElement: (tag) => tag.startsWith('v-')
        },
        // Add nonce to all script and style tags
        transformAssetUrls: {
          'v-img': ['src', 'lazy-src']
        }
      },
      // Enable reactivity transform for better performance
      reactivityTransform: true
    }),
    vuetify({
      autoImport: true,
      styles: {
        configFile: 'src/scss/settings.scss',
        includeStyles: true
      }
    })
  ],
  // CSS configuration moved to the end of the file
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      'vue': 'vue/dist/vue.esm-bundler.js'
    },
    extensions: [
      '.js',
      '.json',
      '.jsx',
      '.mjs',
      '.ts',
      '.tsx',
      '.vue',
    ],
  },
  server: {
    port: 3003,
    host: '0.0.0.0',
    strictPort: true,
    open: true,
    cors: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        ws: true
      }
    },
    hmr: {
      host: 'localhost',
      port: 3003,
      protocol: 'ws',
      overlay: true
    },
    fs: {
      strict: false,
      allow: ['..']
    }
  },
  build: {
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'vuetify': ['vuetify', 'vuetify/styles'],
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'mdi': ['@mdi/font/css/materialdesignicons.min.css']
        },
        assetFileNames: (assetInfo) => {
          const ext = assetInfo.name.split('.').pop();
          if (['png', 'jpg', 'jpeg', 'gif', 'svg'].includes(ext)) {
            return 'assets/images/[name].[hash][extname]';
          }
          if (['woff', 'woff2', 'eot', 'ttf', 'otf'].includes(ext)) {
            return 'assets/fonts/[name].[hash][extname]';
          }
          return 'assets/[name].[hash][extname]';
        },
        chunkFileNames: 'assets/js/[name].[hash].js',
        entryFileNames: 'assets/js/[name].[hash].js'
      }
    },
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    },
    cssCodeSplit: true,
    manifest: true,
    chunkSizeWarningLimit: 2000,
    emptyOutDir: true
  },
  
  optimizeDeps: {
    include: [
      'vue',
      'vue-router',
      'pinia',
      'vuetify',
      '@mdi/font/css/materialdesignicons.min.css',
      'material-design-icons-iconfont/dist/material-design-icons.css',
      '@vuelidate/validators',
      '@vuelidate/core'
    ],
    exclude: ['vue-demi']
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `
          @use "sass:math";
          @use "sass:map";
          @import "@/scss/variables";
          @import "@/styles/variables";
        `
      }
    }
  }
};

export default defineConfig(({ mode }) => ({
  ...baseConfig,
  define: {
    'process.env': {},
    __VUE_PROD_DEVTOOLS__: mode !== 'production',
    __VUE_OPTIONS_API__: true,
    __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: mode !== 'production',
    __NONCE__: JSON.stringify(nonce)
  },
  server: {
    ...baseConfig.server,
    headers: {
      'Content-Security-Policy': [
        "default-src 'self'",
        `script-src 'self' 'unsafe-inline' 'unsafe-eval' 'nonce-${nonce}'`,
        "style-src 'self' 'unsafe-inline' https: http:",
        "img-src 'self' data: blob: https: http:",
        "font-src 'self' data: https: http:",
        "connect-src 'self' ws: wss: http: https:",
        "frame-src 'self' https:",
        "object-src 'none'",
        "base-uri 'self'",
        "form-action 'self'",
        "frame-ancestors 'none'"
      ].join('; ')
    }
  },
  build: {
    ...baseConfig.build,
    minify: mode === 'production' ? 'terser' : false,
    sourcemap: mode !== 'production',
    emptyOutDir: mode === 'production',
    terserOptions: {
      compress: {
        drop_console: mode === 'production',
        drop_debugger: mode === 'production',
        keep_classnames: mode !== 'production',
        keep_fnames: mode !== 'production'
      },
      format: {
        comments: mode !== 'production'
      },
      mangle: mode === 'production',
      sourceMap: mode !== 'production'
    }
  }
}));
