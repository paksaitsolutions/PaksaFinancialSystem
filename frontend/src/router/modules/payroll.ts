import { RouteRecordRaw } from 'vue-router'

const payrollRoutes: RouteRecordRaw[] = [
  {
    path: '/payroll',
    name: 'Payroll',
    component: () => import('../../views/ModuleView.vue'),
    meta: {
      title: 'Payroll',
      breadcrumb: 'Payroll',
      requiresAuth: true
    },
    children: [
      {
        path: '',
        name: 'PayrollDashboard',
        component: () => import('../../modules/payroll/views/PayrollView.vue'),
        meta: {
          title: 'Payroll Dashboard'
        }
      },
      {
        path: 'employees',
        name: 'EmployeeManagement',
        component: () => import('../../modules/payroll/views/EmployeeManagementView.vue'),
        meta: {
          title: 'Employee Management',
          breadcrumb: 'Employees'
        }
      },
      {
        path: 'employees/:id',
        name: 'EmployeeDetail',
        component: () => import('../../modules/payroll/components/employee/EmployeeDetail.vue'),
        props: true,
        meta: {
          title: 'Employee Details'
        }
      },
      {
        path: 'processing',
        name: 'PayrollProcessing',
        component: () => import('../../modules/payroll/components/PayrollProcessing.vue'),
        meta: {
          title: 'Payroll Processing',
          breadcrumb: 'Processing'
        }
      },
      {
        path: 'payrun',
        name: 'PayrollRun',
        component: () => import('../../modules/payroll/views/PayrollRunView.vue'),
        meta: {
          title: 'Payroll Run'
        }
      },
      {
        path: 'payslips',
        name: 'Payslips',
        component: () => import('../../modules/payroll/views/PayslipsView.vue'),
        meta: {
          title: 'Payslips'
        }
      },
      {
        path: 'benefits',
        name: 'BenefitsManagement',
        component: () => import('../../modules/payroll/components/BenefitsManagement.vue'),
        meta: {
          title: 'Benefits Management',
          breadcrumb: 'Benefits'
        }
      },
      {
        path: 'deductions-benefits',
        name: 'DeductionsBenefits',
        component: () => import('../../modules/payroll/views/PayrollDeductionsBenefitsView.vue'),
        meta: {
          title: 'Deductions & Benefits'
        }
      },
      {
        path: 'tax-calculator',
        name: 'TaxCalculator',
        component: () => import('../../modules/payroll/components/TaxCalculator.vue'),
        meta: {
          title: 'Tax Calculator'
        }
      },
      {
        path: 'taxes',
        name: 'PayrollTaxes',
        component: () => import('../../modules/payroll/views/PayrollTaxesView.vue'),
        meta: {
          title: 'Payroll Taxes'
        }
      },
      {
        path: 'reporting',
        name: 'PayrollReporting',
        component: () => import('../../modules/payroll/components/PayrollReporting.vue'),
        meta: {
          title: 'Payroll Reporting'
        }
      },
      {
        path: 'reports',
        name: 'PayrollReports',
        component: () => import('../../modules/payroll/views/PayrollReportsView.vue'),
        meta: {
          title: 'Payroll Reports'
        }
      },
      {
        path: 'settings',
        name: 'PayrollSettings',
        component: () => import('../../modules/payroll/views/PayrollSettingsView.vue'),
        meta: {
          title: 'Payroll Settings'
        }
      }
    ]
  }
]

export default payrollRoutes