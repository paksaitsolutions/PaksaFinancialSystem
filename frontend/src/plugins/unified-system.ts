import type { App } from 'vue'
import UnifiedTheme from '@/components/ui/UnifiedTheme.vue'
import UnifiedNavigation from '@/components/ui/UnifiedNavigation.vue'
import UnifiedLoading from '@/components/ui/UnifiedLoading.vue'
import UnifiedNotification from '@/components/ui/UnifiedNotification.vue'
import UnifiedForm from '@/components/ui/UnifiedForm.vue'
import UnifiedModal from '@/components/ui/UnifiedModal.vue'
import UnifiedDashboard from '@/components/ui/UnifiedDashboard.vue'
import UnifiedMetrics from '@/components/ui/UnifiedMetrics.vue'
import UnifiedDataTable from '@/components/ui/UnifiedDataTable.vue'
import UnifiedForm from '@/components/ui/UnifiedForm.vue'

// Import unified styles
import '@/styles/unified.scss'

export default {
  install(app: App) {
    // Register global components
    app.component('UnifiedTheme', UnifiedTheme)
    app.component('UnifiedNavigation', UnifiedNavigation)
    app.component('UnifiedLoading', UnifiedLoading)
    app.component('UnifiedNotification', UnifiedNotification)
    app.component('UnifiedForm', UnifiedForm)
    app.component('UnifiedModal', UnifiedModal)
    app.component('UnifiedDashboard', UnifiedDashboard)
    app.component('UnifiedMetrics', UnifiedMetrics)
    app.component('UnifiedDataTable', UnifiedDataTable)
    app.component('UnifiedForm', UnifiedForm)

    // Global properties
    app.config.globalProperties.$unified = {
      version: '1.0.0',
      theme: 'paksa-financial'
    }

    // Global error handler
    app.config.errorHandler = (err, instance, info) => {
      console.error('Global error:', err, info)
      
      // You can integrate with your error tracking service here
      // e.g., Sentry, LogRocket, etc.
    }
  }
}