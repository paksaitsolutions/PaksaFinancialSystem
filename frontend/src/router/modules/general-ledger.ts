import type { RouteRecordRaw } from 'vue-router';
import { defineComponent } from 'vue';
import UnderConstruction from '@/views/UnderConstruction.vue';

// Helper function for lazy loading with fallback
const lazyLoad = (path: string) => {
  return () => import(`@/views/${path}.vue`).catch(() => ({
    template: '<UnderConstruction />',
    components: { UnderConstruction },
  }));
};

// General Ledger Layout
const GeneralLedgerLayout = defineComponent({
  template: '<router-view />'
});

// General Ledger Routes
export const generalLedgerRoutes: RouteRecordRaw = {
  path: '/gl',
  component: GeneralLedgerLayout,
  meta: {
    title: 'General Ledger',
    icon: 'pi pi-book',
    permission: 'gl.view_dashboard',
    breadcrumb: ['General Ledger']
  },
  children: [
    {
      path: '',
      name: 'gl-dashboard',
      component: () => import('@/modules/general-ledger/views/Dashboard.vue'),
      meta: { 
        title: 'Dashboard',
        icon: 'pi pi-chart-line',
        permission: 'gl.view_dashboard',
        breadcrumb: ['General Ledger', 'Dashboard']
      }
    },
    // Accounts Management
    {
      path: 'accounts',
      name: 'gl-accounts',
      component: () => import('@/modules/general-ledger/views/accounts/GlAccountListView.vue'),
      meta: { 
        title: 'Chart of Accounts',
        icon: 'pi pi-list',
        permission: 'gl.accounts.view',
        breadcrumb: ['General Ledger', 'Chart of Accounts']
      }
    },
    {
      path: 'accounts/new',
      name: 'gl-account-new',
      component: () => import('@/modules/general-ledger/views/accounts/GlAccountForm.vue'),
      meta: { 
        title: 'New Account',
        icon: 'pi pi-plus',
        permission: 'gl.accounts.create',
        breadcrumb: ['General Ledger', 'Chart of Accounts', 'New Account']
      },
      props: { mode: 'create' }
    },
    {
      path: 'accounts/:id/edit',
      name: 'gl-account-edit',
      component: () => import('@/modules/general-ledger/views/accounts/GlAccountForm.vue'),
      meta: { 
        title: 'Edit Account',
        icon: 'pi pi-pencil',
        permission: 'gl.accounts.edit',
        breadcrumb: ['General Ledger', 'Chart of Accounts', 'Edit Account']
      },
      props: route => ({ 
        mode: 'edit',
        accountId: route.params.id 
      })
    },
    {
      path: 'accounts/:id',
      name: 'gl-account-detail',
      component: () => import('@/modules/general-ledger/views/accounts/GlAccountDetail.vue'),
      meta: { 
        title: 'Account Details',
        icon: 'pi pi-info-circle',
        permission: 'gl.accounts.view',
        breadcrumb: ['General Ledger', 'Chart of Accounts', 'Details']
      },
      props: true
    },
    {
      path: 'journal-entries',
      name: 'journal-entries',
      component: lazyLoad('JournalEntries'),
      meta: { 
        title: 'Journal Entries',
        icon: 'pi pi-book',
        breadcrumb: ['General Ledger', 'Journal Entries'],
        permission: 'gl.view_journal_entries'
      }
    },
    {
      path: 'financial-statements',
      name: 'financial-statements',
      component: () => import('@/modules/general-ledger/views/financial-statements/FinancialStatementsView.vue'),
      meta: { 
        title: 'Financial Statements',
        icon: 'pi pi-file-pdf',
        breadcrumb: ['General Ledger', 'Financial Statements'],
        permission: 'gl.view_financial_statements'
      }
    },
    {
      path: 'trial-balance',
      name: 'trial-balance',
      component: lazyLoad('TrialBalance'),
      meta: { 
        title: 'Trial Balance',
        icon: 'pi pi-balance-scale',
        breadcrumb: ['General Ledger', 'Trial Balance'],
        permission: 'gl.view_trial_balance'
      }
    },
    {
      path: 'reconciliation',
      name: 'gl-reconciliation',
      component: lazyLoad('GLReconciliation'),
      meta: { 
        title: 'Reconciliation',
        icon: 'pi pi-sync',
        breadcrumb: ['General Ledger', 'Reconciliation'],
        permission: 'gl.view_reconciliation'
      }
    },
    {
      path: 'reports',
      name: 'gl-reports',
      component: lazyLoad('GLReports'),
      meta: { 
        title: 'Reports',
        icon: 'pi pi-chart-bar',
        breadcrumb: ['General Ledger', 'Reports'],
        permission: 'gl.view_reports'
      }
    },
    {
      path: 'settings',
      name: 'gl-settings',
      component: lazyLoad('GLSettings'),
      meta: { 
        title: 'Settings',
        icon: 'pi pi-cog',
        breadcrumb: ['General Ledger', 'Settings'],
        permission: 'gl.manage_settings'
      }
    }
  ]
};

export default generalLedgerRoutes;
