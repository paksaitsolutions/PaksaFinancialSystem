import type { RouteRecordRaw } from 'vue-router';
import { defineComponent } from 'vue';
import UnderConstruction from '@/views/common/UnderConstruction.vue';

// Helper function for lazy loading with fallback
const lazyLoad = (path: string) => {
  return () => import(`@/views/${path}.vue`).catch(() => ({
    template: '<UnderConstruction />',
    components: { UnderConstruction },
  }));
};

// Cash Management Layout
const CashLayout = defineComponent({
  template: '<router-view />'
});

// Cash Management Routes
export const cashRoutes: RouteRecordRaw = {
  path: '/cash',
  name: 'CashManagement',
  component: CashLayout,
  meta: { 
    title: 'Cash Management',
    requiresAuth: true,
    icon: 'pi pi-wallet',
    permission: 'cash_management.view'
  },
  children: [
    {
      path: '',
      name: 'CashDashboard',
      component: () => import('@/views/cash/Dashboard.vue'),
      meta: { 
        title: 'Cash Dashboard',
        icon: 'pi pi-chart-line',
        breadcrumb: ['Cash Management', 'Dashboard']
      }
    },
    {
      path: 'cash-flow',
      name: 'CashFlow',
      component: () => import('@/views/cash/CashFlowForecast.vue'),
      meta: { 
        title: 'Cash Flow Forecast',
        icon: 'pi pi-chart-line',
        breadcrumb: ['Cash Management', 'Cash Flow Forecast'],
        permission: 'cash_management.view_cash_flow'
      }
    },
    {
      path: 'bank-accounts',
      name: 'BankAccounts',
      component: () => import('@/views/cash/BankAccounts.vue'),
      meta: { 
        title: 'Bank Accounts',
        icon: 'pi pi-credit-card',
        breadcrumb: ['Cash Management', 'Bank Accounts']
      }
    },
    {
      path: 'transactions',
      name: 'Transactions',
      component: () => import('@/views/cash/Transactions.vue'),
      meta: { 
        title: 'Transactions',
        icon: 'pi pi-exchange',
        breadcrumb: ['Cash Management', 'Transactions']
      }
    },
    {
      path: 'reconciliation',
      name: 'Reconciliation',
      component: () => import('@/views/cash/Reconciliation.vue'),
      meta: { 
        title: 'Bank Reconciliation',
        icon: 'pi pi-sync',
        breadcrumb: ['Cash Management', 'Bank Reconciliation']
      }
    },
    {
      path: 'cash-flow',
      name: 'CashFlow',
      component: () => import('@/views/cash/CashFlow.vue').catch(() => ({
        template: '<UnderConstruction />',
        components: { UnderConstruction },
      })),
      meta: { 
        title: 'Cash Flow',
        icon: 'pi pi-chart-pie',
        breadcrumb: ['Cash Management', 'Cash Flow']
      }
    },
    {
      path: 'reports',
      name: 'CashReports',
      component: () => import('@/views/cash/Reports.vue').catch(() => ({
        template: '<UnderConstruction />',
        components: { UnderConstruction },
      })),
      meta: { 
        title: 'Reports',
        icon: 'pi pi-file-pdf',
        breadcrumb: ['Cash Management', 'Reports']
      }
    },
    {
      path: 'settings',
      name: 'CashSettings',
      component: () => import('@/views/cash/Settings.vue').catch(() => ({
        template: '<UnderConstruction />',
        components: { UnderConstruction },
      })),
      meta: { 
        title: 'Settings',
        icon: 'pi pi-cog',
        breadcrumb: ['Cash Management', 'Settings']
      }
    }
  ]
};

export default cashRoutes;
