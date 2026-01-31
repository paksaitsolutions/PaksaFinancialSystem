import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import { visualizer } from 'rollup-plugin-visualizer'

export default defineConfig({
  plugins: [
    vue(),
    // Bundle analyzer
    visualizer({
      filename: 'dist/stats.html',
      open: true,
      gzipSize: true
    })
  ],
  css: {
    preprocessorOptions: {
      scss: {
        api: 'modern-compiler'
      }
    }
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          // Vendor chunks
          if (id.includes('node_modules')) {
            if (id.includes('vue') || id.includes('pinia') || id.includes('vue-router')) {
              return 'vue-vendor';
            }
            if (id.includes('primevue')) {
              return 'primevue-vendor';
            }
            if (id.includes('chart.js') || id.includes('echarts')) {
              return 'chart-vendor';
            }
            if (id.includes('axios')) {
              return 'http-vendor';
            }
            return 'vendor';
          }
          
          // Module-based chunks
          if (id.includes('/modules/general-ledger/')) return 'gl-module';
          if (id.includes('/modules/accounts-payable/')) return 'ap-module';
          if (id.includes('/modules/accounts-receivable/')) return 'ar-module';
          if (id.includes('/modules/cash-management/')) return 'cash-module';
          if (id.includes('/modules/fixed-assets/')) return 'assets-module';
          if (id.includes('/modules/payroll/')) return 'payroll-module';
          if (id.includes('/modules/budget/')) return 'budget-module';
          if (id.includes('/modules/tax/')) return 'tax-module';
          if (id.includes('/modules/inventory/')) return 'inventory-module';
          if (id.includes('/modules/hrm/')) return 'hrm-module';
          if (id.includes('/modules/reports/')) return 'reports-module';
          if (id.includes('/modules/settings/')) return 'settings-module';
        },
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    },
    assetsInlineLimit: 4096,
    cssCodeSplit: true,
    sourcemap: false,
    minify: 'esbuild',
    chunkSizeWarningLimit: 500,
    target: 'es2015',
    reportCompressedSize: false
  },
  // Asset optimization
  assetsInclude: ['**/*.woff', '**/*.woff2', '**/*.ttf'],
  
  // Development server
  server: {
    port: 3003,
    host: true,
    cors: true
  },
  
  // Preview server
  preview: {
    port: 3003,
    host: true
  },
  

})