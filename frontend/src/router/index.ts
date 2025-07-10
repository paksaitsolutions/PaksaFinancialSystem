import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';
import DashboardView from '@/views/compliance/DashboardView.vue';
import EventsView from '@/views/compliance/security/EventsView.vue';
import PoliciesView from '@/views/compliance/security/PoliciesView.vue';
import EncryptionView from '@/views/compliance/security/EncryptionView.vue';
import EncryptionKeysView from '@/views/compliance/security/EncryptionKeysView.vue';
import SettingsView from '@/views/compliance/SettingsView.vue';

// Financial Statements
const FinancialStatementsView = () => import('@/views/accounting/gl/financial-statements/FinancialStatementsView.vue');
const FinancialStatementTemplatesView = () => import('@/views/accounting/gl/financial-statement-templates/FinancialStatementTemplatesView.vue');

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/accounting/financial-statements',
  },
  // Accounting Routes
  {
    path: '/accounting',
    redirect: '/accounting/financial-statements',
    meta: { requiresAuth: true },
  },
  {
    path: '/accounting/financial-statements',
    name: 'FinancialStatements',
    component: FinancialStatementsView,
    meta: { requiresAuth: true, title: 'Financial Statements' },
  },
  {
    path: '/accounting/financial-statement-templates',
    name: 'FinancialStatementTemplates',
    component: FinancialStatementTemplatesView,
    meta: { requiresAuth: true, title: 'Financial Statement Templates' },
  },
  // Compliance Routes
  {
    path: '/compliance/dashboard',
    name: 'ComplianceDashboard',
    component: DashboardView,
    meta: { requiresAuth: true, title: 'Compliance Dashboard' },
  },
  {
    path: '/compliance/security/events',
    name: 'SecurityEvents',
    component: EventsView,
    meta: { requiresAuth: true, title: 'Security Events' },
  },
  {
    path: '/compliance/security/policies',
    name: 'SecurityPolicies',
    component: PoliciesView,
    meta: { requiresAuth: true, title: 'Security Policies' },
  },
  {
    path: '/compliance/security/encryption',
    name: 'SecurityEncryption',
    component: EncryptionView,
    meta: { requiresAuth: true, title: 'Encryption' },
  },
  {
    path: '/compliance/security/encryption-keys',
    name: 'SecurityEncryptionKeys',
    component: EncryptionKeysView,
    meta: { requiresAuth: true, title: 'Encryption Keys' },
  },
  {
    path: '/compliance/settings',
    name: 'ComplianceSettings',
    component: SettingsView,
    meta: { requiresAuth: true, title: 'Compliance Settings' },
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // Always scroll to top when navigating to a new route
    return { top: 0, behavior: 'smooth' };
  },
});

// Update page title based on route meta
router.beforeEach((to, from, next) => {
  const appName = 'Paksa Financial System';
  document.title = to.meta.title ? `${to.meta.title} | ${appName}` : appName;
  next();
});

export default router;
