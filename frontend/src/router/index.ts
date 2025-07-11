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
// Accounts Receivable
const InvoicesView = () => import('@/views/accounts-receivable/InvoicesView.vue');
const InvoiceForm = () => import('@/views/accounts-receivable/InvoiceForm.vue');
const ARDashboard = () => import('@/views/accounts-receivable/ARDashboard.vue');
const InvoiceDetailView = () => import('@/views/accounts-receivable/InvoiceDetailView.vue');
// Accounts Payable
const BillsView = () => import('@/views/accounts-payable/BillsView.vue');
const BillForm = () => import('@/views/accounts-payable/BillForm.vue');
const APDashboard = () => import('@/views/accounts-payable/APDashboard.vue');
const BillDetailView = () => import('@/views/accounts-payable/BillDetailView.vue');

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
  // Accounts Receivable Routes
  {
    path: '/accounts-receivable/invoices',
    name: 'Invoices',
    component: InvoicesView,
    meta: { requiresAuth: true, title: 'Invoices' },
  },
  {
    path: '/accounts-receivable/dashboard',
    name: 'ARDashboard',
    component: ARDashboard,
    meta: { requiresAuth: true, title: 'AR Dashboard' },
  },
  {
    path: '/accounts-receivable/invoices/:id',
    name: 'InvoiceDetail',
    component: InvoiceDetailView,
    meta: { requiresAuth: true, title: 'Invoice Detail' },
    props: true,
  },
  // Accounts Payable Routes
  {
    path: '/accounts-payable/bills',
    name: 'Bills',
    component: BillsView,
    meta: { requiresAuth: true, title: 'Bills' },
  },
  {
    path: '/accounts-payable/dashboard',
    name: 'APDashboard',
    component: APDashboard,
    meta: { requiresAuth: true, title: 'AP Dashboard' },
  },
  {
    path: '/accounts-payable/bills/:id',
    name: 'BillDetail',
    component: BillDetailView,
    meta: { requiresAuth: true, title: 'Bill Detail' },
    props: true,
  },
  // BI Dashboard Route
  {
    path: '/bi-dashboard',
    name: 'BIDashboard',
    component: () => import('@/views/accounting/bi/BIDashboardView.vue'),
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
