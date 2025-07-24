import { RouteRecordRaw } from 'vue-router'

const payrollRoutes: RouteRecordRaw[] = [
  {
    path: '/payroll',
    name: 'Payroll',
    component: () => import('../../views/ModuleView.vue'),
    meta: {
      title: 'Payroll',
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
          title: 'Employee Management'
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
        path: 'deductions-benefits',
        name: 'DeductionsBenefits',
        component: () => import('../../modules/payroll/views/PayrollDeductionsBenefitsView.vue'),
        meta: {
          title: 'Deductions & Benefits'
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