import type { RouteRecordRaw } from 'vue-router';
import { defineComponent } from 'vue';

// Helper function for lazy loading with fallback
function lazyLoad(path: string) {
  return () => import(`@/modules/general-ledger/views/${path}.vue`)
    .catch(() => import('@/views/common/UnderConstruction.vue'));
}

// General Ledger Layout
const GeneralLedgerLayout = defineComponent({
  template: '<router-view />'
});

const generalLedgerRoutes: RouteRecordRaw = {
  path: '/gl',
  component: GeneralLedgerLayout,
  meta: { requiresAuth: true },
  children: [
    {
      path: '',
      name: 'GeneralLedger',
      component: () => import('@/modules/general-ledger/views/GLDashboard.vue'),
      meta: { 
        title: 'Dashboard',
        icon: 'pi pi-chart-line',
        permission: 'gl.view_dashboard',
        breadcrumb: ['General Ledger', 'Dashboard']
      }
    },
    {
      path: 'accounts',
      name: 'GLAccounts',
      component: lazyLoad('GLAccounts'),
      meta: { 
        title: 'Chart of Accounts',
        icon: 'pi pi-list',
        permission: 'gl.accounts.view',
        breadcrumb: ['General Ledger', 'Chart of Accounts']
      },
      children: [
        {
          path: 'new',
          name: 'GLNewAccount',
          component: lazyLoad('GLNewAccount'),
          meta: { 
            title: 'New Account',
            icon: 'pi pi-plus',
            permission: 'gl.accounts.create',
            breadcrumb: ['General Ledger', 'Chart of Accounts', 'New Account']
          }
        },
        {
          path: ':id/edit',
          name: 'GLEditAccount',
          component: lazyLoad('GLEditAccount'),
          meta: { 
            title: 'Edit Account',
            icon: 'pi pi-pencil',
            permission: 'gl.accounts.edit',
            breadcrumb: ['General Ledger', 'Chart of Accounts', 'Edit Account']
          },
          props: true
        },
        {
          path: ':id',
          name: 'GLAccountDetails',
          component: lazyLoad('GLAccountDetails'),
          meta: { 
            title: 'Account Details',
            icon: 'pi pi-info-circle',
            permission: 'gl.accounts.view',
            breadcrumb: ['General Ledger', 'Chart of Accounts', 'Details']
          },
          props: true
        }
      ]
    },
    {
      path: 'journal-entries',
      name: 'GLJournalEntries',
      component: lazyLoad('GLJournalEntries'),
      meta: { 
        title: 'Journal Entries',
        icon: 'pi pi-book',
        permission: 'gl.journal_entries.view',
        breadcrumb: ['General Ledger', 'Journal Entries']
      }
    },
    {
      path: 'trial-balance',
      name: 'GLTrialBalance',
      component: lazyLoad('GLTrialBalance'),
      meta: { 
        title: 'Trial Balance',
        icon: 'pi pi-balance-scale',
        permission: 'gl.view_trial_balance',
        breadcrumb: ['General Ledger', 'Trial Balance']
      }
    },
    {
      path: 'financial-statements',
      name: 'GLFinancialStatements',
      component: lazyLoad('GLFinancialStatements'),
      meta: { 
        title: 'Financial Statements',
        icon: 'pi pi-file-pdf',
        breadcrumb: ['General Ledger', 'Financial Statements'],
        permission: 'gl.view_financial_statements'
      },
      children: [
        {
          path: 'balance-sheet',
          name: 'GLBalanceSheet',
          component: lazyLoad('GLBalanceSheet'),
          meta: { 
            title: 'Balance Sheet',
            breadcrumb: ['General Ledger', 'Financial Statements', 'Balance Sheet']
          }
        },
        {
          path: 'income-statement',
          name: 'GLIncomeStatement',
          component: lazyLoad('GLIncomeStatement'),
          meta: { 
            title: 'Income Statement',
            breadcrumb: ['General Ledger', 'Financial Statements', 'Income Statement']
          }
        },
        {
          path: 'cash-flow',
          name: 'GLCashFlow',
          component: lazyLoad('GLCashFlow'),
          meta: { 
            title: 'Cash Flow Statement',
            breadcrumb: ['General Ledger', 'Financial Statements', 'Cash Flow']
          }
        },
        {
          path: 'changes-in-equity',
          name: 'GLChangesInEquity',
          component: lazyLoad('GLChangesInEquity'),
          meta: { 
            title: 'Changes in Equity',
            breadcrumb: ['General Ledger', 'Financial Statements', 'Changes in Equity']
          }
        }
      ]
    },
    {
      path: 'recurring',
      name: 'GLRecurringJournals',
      component: lazyLoad('RecurringJournals'),
      meta: { 
        title: 'Recurring Journals',
        icon: 'pi pi-sync',
        permission: 'gl.manage_recurring_journals',
        breadcrumb: ['General Ledger', 'Recurring Journals']
      }
    },
    {
      path: 'period-close',
      name: 'GLPeriodClose',
      component: lazyLoad('GLPeriodClose'),
      meta: { 
        title: 'Period Close',
        icon: 'pi pi-calendar-times',
        permission: 'gl.manage_period_close',
        breadcrumb: ['General Ledger', 'Period Close']
      }
    },
    {
      path: 'reports',
      name: 'GLReports',
      component: lazyLoad('GLReports'),
      meta: { 
        title: 'Reports',
        icon: 'pi pi-chart-bar',
        breadcrumb: ['General Ledger', 'Reports'],
        permission: 'gl.view_reports'
      }
    }
  ]
};

export default generalLedgerRoutes;
