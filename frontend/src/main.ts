import { createApp } from 'vue'
import { createVuetify } from 'vuetify'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'

// Vuetify
import 'vuetify/styles'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import '@mdi/font/css/materialdesignicons.css'

const vuetify = createVuetify({
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#1976d2',
          secondary: '#424242',
          accent: '#82b1ff',
          error: '#ff5252',
          info: '#2196f3',
          success: '#4caf50',
          warning: '#ffc107'
        }
      }
    }
  }
})

const pinia = createPinia()

// Router with auth guard
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/auth/login',
      name: 'Login',
      component: () => import('./views/auth/Login.vue')
    },
    {
      path: '/auth/register',
      name: 'Register',
      component: () => import('./views/auth/Register.vue')
    },
    {
      path: '/auth/forgot-password',
      name: 'ForgotPassword',
      component: () => import('./views/auth/ForgotPassword.vue')
    },
    {
      path: '/',
      name: 'Home',
      component: () => import('./views/Home.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('./views/Home.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/ap',
      name: 'AccountsPayable',
      component: () => import('./views/accounts-payable/VendorsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/ar',
      name: 'AccountsReceivable',
      component: () => import('./views/accounts-receivable/CustomersView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/gl',
      name: 'GeneralLedger',
      component: () => import('./views/accounting/GeneralLedgerView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/gl/chart-of-accounts',
      name: 'ChartOfAccounts',
      component: () => import('./views/accounting/ChartOfAccountsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/gl/journal-entries',
      name: 'JournalEntries',
      component: () => import('./views/accounting/JournalEntryView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/gl/trial-balance',
      name: 'TrialBalance',
      component: () => import('./views/accounting/TrialBalanceView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/gl/financial-statements',
      name: 'FinancialStatements',
      component: () => import('./views/accounting/FinancialStatementsView.vue'),
      meta: { requiresAuth: true }
    }
    {
      path: '/reports',
      name: 'Reports',
      component: () => import('./views/reports/SimpleReportsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/main-dashboard',
      name: 'MainDashboard',
      component: () => import('./views/Dashboard.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin',
      name: 'SuperAdmin',
      component: () => import('./views/admin/SuperAdminView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/settings',
      name: 'Settings',
      component: () => import('./views/settings/CompanySettingsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/settings/currency',
      name: 'CurrencySettings',
      component: () => import('./views/settings/CurrencyManagementView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/rbac',
      name: 'RoleManagement',
      component: () => import('./views/rbac/RoleManagementView.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

// Auth guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth && !token) {
    next('/auth/login')
  } else if (to.path === '/auth/login' && token) {
    next('/')
  } else {
    next()
  }
})

const app = createApp(App)

app.use(vuetify)
app.use(pinia)
app.use(router)

app.mount('#app')