import type { RouteRecordRaw } from 'vue-router';
import { defineComponent } from 'vue';

// Helper function for lazy loading with fallback
function lazyLoad(path: string) {
  return () => import(`@/modules/budget/views/${path}.vue`)
    .catch(() => import('@/views/common/UnderConstruction.vue'));
}

// Budget Layout
const BudgetLayout = defineComponent({
  template: '<router-view />'
});

const budgetRoutes: RouteRecordRaw = {
  path: '/budget',
  component: BudgetLayout,
  meta: { requiresAuth: true },
  children: [
    {
      path: '',
      name: 'Budget',
      component: () => import('@/modules/budget/views/BudgetDashboard.vue'),
      meta: { 
        title: 'Budget Dashboard',
        icon: 'pi pi-chart-pie',
        permission: 'budget.view_dashboard',
        breadcrumb: ['Budget', 'Dashboard']
      }
    },
    {
      path: 'manage',
      name: 'BudgetManage',
      component: () => import('@/modules/budget/views/BudgetingView.vue'),
      meta: { 
        title: 'Budget Management',
        icon: 'pi pi-wallet',
        permission: 'budget.manage',
        breadcrumb: ['Budget', 'Management']
      }
    },
    {
      path: 'planning',
      name: 'BudgetPlanning',
      component: lazyLoad('BudgetPlanningView'),
      meta: { 
        title: 'Budget Planning',
        icon: 'pi pi-calendar',
        permission: 'budget.planning',
        breadcrumb: ['Budget', 'Planning']
      }
    },
    {
      path: 'monitoring',
      name: 'BudgetMonitoring',
      component: lazyLoad('BudgetMonitoringView'),
      meta: { 
        title: 'Budget Monitoring',
        icon: 'pi pi-eye',
        permission: 'budget.monitoring',
        breadcrumb: ['Budget', 'Monitoring']
      }
    },
    {
      path: 'approval',
      name: 'BudgetApproval',
      component: lazyLoad('BudgetApprovalView'),
      meta: { 
        title: 'Budget Approval',
        icon: 'pi pi-check',
        permission: 'budget.approval',
        breadcrumb: ['Budget', 'Approval']
      }
    },
    {
      path: 'scenarios',
      name: 'BudgetScenarios',
      component: lazyLoad('BudgetScenarios'),
      meta: { 
        title: 'Budget Scenarios',
        icon: 'pi pi-sliders-h',
        permission: 'budget.scenarios.view',
        breadcrumb: ['Budget', 'Scenarios']
      }
    },
    {
      path: 'forecasting',
      name: 'BudgetForecasting',
      component: lazyLoad('BudgetForecasting'),
      meta: { 
        title: 'Forecasting',
        icon: 'pi pi-chart-line',
        permission: 'budget.forecasting.view',
        breadcrumb: ['Budget', 'Forecasting']
      }
    },
    {
      path: 'reports',
      name: 'BudgetReports',
      component: lazyLoad('BudgetReportView'),
      meta: { 
        title: 'Budget Reports',
        icon: 'pi pi-file-pdf',
        permission: 'budget.reports.view',
        breadcrumb: ['Budget', 'Reports']
      }
    },
    {
      path: 'settings',
      name: 'BudgetSettings',
      component: lazyLoad('BudgetSettings'),
      meta: { 
        title: 'Settings',
        icon: 'pi pi-cog',
        permission: 'budget.settings.view',
        breadcrumb: ['Budget', 'Settings']
      }
    }
  ]
};

export default budgetRoutes;
