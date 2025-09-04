import { RouteRecordRaw } from 'vue-router';
import { defineComponent } from 'vue';

// Helper function for lazy loading with fallback
function lazyLoad(path: string) {
  return () => import(`@/modules/payroll/views/${path}.vue`)
    .catch(() => import('@/views/common/UnderConstruction.vue'));
}

// Payroll Layout
const PayrollLayout = defineComponent({
  template: '<router-view />'
});

const payrollRoutes: RouteRecordRaw = {
  path: '/payroll',
  component: PayrollLayout,
  meta: { 
    title: 'Payroll',
    requiresAuth: true,
    breadcrumb: ['Payroll']
  },
  children: [
    {
      path: '',
      name: 'PayrollDashboard',
      component: () => import('@/modules/payroll/views/PayrollDashboard.vue'),
      meta: { 
        title: 'Dashboard',
        icon: 'pi pi-money-bill',
        permission: 'payroll.view_dashboard',
        breadcrumb: ['Payroll', 'Dashboard']
      }
    },
    {
      path: 'employees',
      name: 'EmployeeManagement',
      component: lazyLoad('EmployeeManagementView'),
meta: {
        title: 'Employee Management',
        icon: 'pi pi-users',
        permission: 'payroll.employees.view',
        breadcrumb: ['Payroll', 'Employees']
      },
      children: [
        {
          path: ':id',
          name: 'EmployeeDetail',
          component: lazyLoad('EmployeeDetail'),
          props: true,
          meta: {
            title: 'Employee Details',
            icon: 'pi pi-user',
            permission: 'payroll.employees.view',
            breadcrumb: ['Payroll', 'Employees', 'Details']
          }
        }
      ]
    },
    {
      path: 'processing',
      name: 'PayrollProcessing',
      component: lazyLoad('PayrollProcessing'),
      meta: {
        title: 'Payroll Processing',
        icon: 'pi pi-cog',
        permission: 'payroll.process',
        breadcrumb: ['Payroll', 'Processing']
      }
    },
    {
      path: 'payrun',
      name: 'PayrollRun',
      component: lazyLoad('PayrollRunView'),
      meta: {
        title: 'Payroll Run',
        icon: 'pi pi-sync',
        permission: 'payroll.run',
        breadcrumb: ['Payroll', 'Pay Run']
      }
    },
    {
      path: 'payslips',
      name: 'Payslips',
      component: lazyLoad('PayslipsView'),
      meta: {
        title: 'Payslips',
        icon: 'pi pi-file-pdf',
        permission: 'payroll.payslips.view',
        breadcrumb: ['Payroll', 'Payslips']
      }
    },
    {
      path: 'benefits',
      name: 'BenefitsManagement',
      component: lazyLoad('BenefitsManagement'),
      meta: {
        title: 'Benefits Management',
        icon: 'pi pi-heart',
        permission: 'payroll.benefits.view',
        breadcrumb: ['Payroll', 'Benefits']
      }
    },
    {
      path: 'deductions-benefits',
      name: 'DeductionsBenefits',
      component: lazyLoad('PayrollDeductionsBenefitsView'),
      meta: {
        title: 'Deductions & Benefits',
        icon: 'pi pi-percentage',
        permission: 'payroll.deductions.view',
        breadcrumb: ['Payroll', 'Deductions & Benefits']
      }
    },
    {
      path: 'tax-calculator',
      name: 'TaxCalculator',
      component: lazyLoad('TaxCalculator'),
      meta: {
        title: 'Tax Calculator',
        icon: 'pi pi-calculator',
        permission: 'payroll.tax.calculate',
        breadcrumb: ['Payroll', 'Tax Calculator']
      }
    },
    {
      path: 'taxes',
      name: 'PayrollTaxes',
      component: lazyLoad('PayrollTaxesView'),
      meta: {
        title: 'Payroll Taxes',
        icon: 'pi pi-file-export',
        permission: 'payroll.taxes.view',
        breadcrumb: ['Payroll', 'Taxes']
      }
    },
    {
      path: 'reporting',
      name: 'PayrollReporting',
      component: lazyLoad('PayrollReportingView'),
      meta: {
        title: 'Payroll Reporting',
        icon: 'pi pi-chart-bar',
        permission: 'payroll.reports.view',
        breadcrumb: ['Payroll', 'Reporting']
      }
    },
    {
      path: 'reports',
      name: 'PayrollReports',
      component: lazyLoad('PayrollReportsView'),
      meta: {
        title: 'Payroll Reports',
        icon: 'pi pi-file-excel',
        permission: 'payroll.reports.view',
        breadcrumb: ['Payroll', 'Reports']
      }
    },
    {
      path: 'settings',
      name: 'PayrollSettings',
      component: lazyLoad('PayrollSettingsView'),
      meta: {
        title: 'Payroll Settings',
        icon: 'pi pi-cog',
        permission: 'payroll.settings.view',
        breadcrumb: ['Payroll', 'Settings']
      }
    }
  ]
};

export default payrollRoutes;