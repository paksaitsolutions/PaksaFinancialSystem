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
    // Code splitting and optimization
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunks
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'primevue-vendor': ['primevue/config', 'primevue/button', 'primevue/inputtext'],
          'chart-vendor': ['chart.js', 'primevue/chart'],
          
          // Module chunks
          'gl-module': [
            './src/modules/general-ledger/views/Dashboard.vue',
            './src/modules/general-ledger/views/ChartOfAccounts.vue'
          ],
          'ap-module': [
            './src/modules/accounts-payable/views/APDashboard.vue'
          ],
          'ar-module': [
            './src/modules/accounts-receivable/views/AccountsReceivableView.vue'
          ],
          'hrm-module': [
            './src/modules/hrm/views/HRMDashboard.vue'
          ],
          'payroll-module': [
            './src/modules/payroll/views/AnalyticsDashboard.vue'
          ],
          'tax-module': [
            './src/modules/tax/views/TaxDashboard.vue'
          ]
        }
      }
    },
    // Asset optimization
    assetsInlineLimit: 4096, // 4kb
    cssCodeSplit: true,
    sourcemap: false, // Disable in production
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    },
    // Chunk size warnings
    chunkSizeWarningLimit: 1000
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