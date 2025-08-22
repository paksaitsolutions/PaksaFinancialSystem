import type { RouteRecordRaw } from 'vue-router';

export const taxRoutes: RouteRecordRaw = {
  path: '/tax',
  name: 'Tax',
  redirect: '/tax/dashboard',
  meta: { 
    title: 'Tax', 
    icon: 'mdi-calculator',
    requiresAuth: true 
  },
  children: [
    {
      path: 'dashboard',
      name: 'TaxDashboard',
      component: () => import('@/modules/tax/views/TaxDashboard.vue'),
      meta: { title: 'Tax Dashboard' }
    },
    {
      path: 'compliance',
      name: 'TaxCompliance',
      component: () => import('@/modules/tax/views/TaxCompliance.vue'),
      meta: { title: 'Tax Compliance' }
    },
    {
      path: 'codes',
      name: 'TaxCodes',
      component: () => import('@/modules/tax/views/TaxCodes.vue'),
      meta: { title: 'Tax Codes' }
    },
    {
      path: 'rates',
      name: 'TaxRates',
      component: () => import('@/modules/tax/views/TaxRates.vue'),
      meta: { title: 'Tax Rates' }
    },
    {
      path: 'jurisdictions',
      name: 'TaxJurisdictions',
      component: () => import('@/modules/tax/views/TaxJurisdictions.vue'),
      meta: { title: 'Tax Jurisdictions' }
    },
    {
      path: 'exemptions',
      name: 'TaxExemptions',
      component: () => import('@/modules/tax/views/TaxExemptions.vue'),
      meta: { title: 'Tax Exemptions' }
    },
    {
      path: 'exemption-certificates',
      name: 'TaxExemptionCertificates',
      component: () => import('@/modules/tax/views/TaxExemptionCertificatesView.vue'),
      meta: { title: 'Exemption Certificates' }
    },
    {
      path: 'reports',
      name: 'TaxReports',
      component: () => import('@/modules/tax/views/TaxReports.vue'),
      meta: { title: 'Tax Reports' }
    },
    {
      path: 'liability-report',
      name: 'TaxLiabilityReport',
      component: () => import('@/modules/tax/views/TaxLiabilityReport.vue'),
      meta: { title: 'Tax Liability Report' }
    },
    {
      path: 'policy',
      name: 'TaxPolicy',
      component: () => import('@/modules/tax/views/TaxPolicyView.vue'),
      meta: { title: 'Tax Policy' }
    },
    {
      path: 'compliance-dashboard',
      name: 'TaxComplianceDashboard',
      component: () => import('@/modules/tax/views/TaxComplianceDashboard.vue'),
      meta: { title: 'Compliance Dashboard' }
    },
    {
      path: 'analytics',
      name: 'TaxAnalyticsDashboard',
      component: () => import('@/modules/tax/views/TaxAnalyticsDashboard.vue'),
      meta: { title: 'Analytics Dashboard' }
    },
    {
      path: 'filing-test',
      name: 'TaxFilingTest',
      component: () => import('@/modules/tax/views/TaxFilingTestPage.vue'),
      meta: { 
        title: 'Tax Filing Form Test',
        devOnly: true // This will be hidden in production
      }
    },
    {
      path: 'returns',
      name: 'TaxReturns',
      component: () => import('@/modules/tax/views/TaxReturns.vue'),
      meta: { title: 'Tax Returns' },
      children: [
        {
          path: '',
          name: 'TaxReturnsList',
          component: () => import('@/modules/tax/views/TaxReturnsList.vue'),
          meta: { title: 'All Returns' }
        },
        {
          path: 'new',
          name: 'NewTaxReturn',
          component: () => import('@/modules/tax/views/TaxReturnForm.vue'),
          meta: { title: 'New Tax Return' }
        },
        {
          path: ':id',
          name: 'TaxReturnDetail',
          component: () => import('@/modules/tax/views/TaxReturnDetail.vue'),
          props: true,
          meta: { title: 'Tax Return Details' }
        },
        {
          path: ':id/edit',
          name: 'EditTaxReturn',
          component: () => import('@/modules/tax/views/TaxReturnForm.vue'),
          props: true,
          meta: { title: 'Edit Tax Return' }
        }
      ]
    }
  ]
} as const;
