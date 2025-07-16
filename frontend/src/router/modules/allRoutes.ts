import type { RouteRecordRaw } from 'vue-router';

// Import all view components
import UnderConstruction from '@/views/UnderConstruction.vue';

// Helper function to lazy load components with fallback
const lazyLoad = (path: string) => {
  return () => import(`@/views/${path}.vue`).catch(() => ({
    template: '<UnderConstruction />',
    components: { UnderConstruction },
  }));
};

// Root route
export const rootRoute: RouteRecordRaw = {
  path: '/',
  name: 'Home',
  component: () => import('@/views/Home.vue'),
  meta: { title: 'Home' },
};

// Dashboard route
export const dashboardRoutes: RouteRecordRaw = {
  path: '/dashboard',
  name: 'Dashboard',
  component: () => import('@/views/Dashboard.vue'),
  meta: { title: 'Dashboard' },
};

export const glRoutes: RouteRecordRaw = {
  path: '/gl',
  name: 'GL',
  component: { template: '<router-view />' },
  redirect: '/gl/dashboard',
  children: [
    {
      path: 'dashboard',
      name: 'GLDashboard',
      component: lazyLoad('gl/Dashboard'),
      meta: { title: 'GL Dashboard' },
    },
    {
      path: 'accounts',
      name: 'ChartOfAccounts',
      component: lazyLoad('gl/ChartOfAccounts'),
      meta: { title: 'Chart of Accounts' },
    },
    {
      path: 'journal-entries',
      name: 'JournalEntries',
      component: lazyLoad('gl/JournalEntries'),
      meta: { title: 'Journal Entries' },
    },
    {
      path: 'trial-balance',
      name: 'TrialBalance',
      component: lazyLoad('gl/TrialBalance'),
      meta: { title: 'Trial Balance' },
    },
    {
      path: 'financial-statements',
      name: 'FinancialStatements',
      component: UnderConstruction,
      meta: { title: 'Financial Statements' },
    },
    {
      path: 'recurring-journals',
      name: 'RecurringJournals',
      component: UnderConstruction,
      meta: { title: 'Recurring Journals' },
    },
    {
      path: 'allocation-rules',
      name: 'AllocationRules',
      component: UnderConstruction,
      meta: { title: 'Allocation Rules' },
    },
    {
      path: 'period-close',
      name: 'PeriodClose',
      component: UnderConstruction,
      meta: { title: 'Period Close' },
    },
    {
      path: 'advanced',
      name: 'AdvancedGL',
      component: lazyLoad('gl/AdvancedGL'),
      meta: { title: 'Advanced GL' },
    },
  ],
};

// Export all routes as an array
export const allRoutes: RouteRecordRaw[] = [
  rootRoute,
  dashboardRoutes,
  glRoutes,
  // Add other route modules here as they're created
];

export default allRoutes;
