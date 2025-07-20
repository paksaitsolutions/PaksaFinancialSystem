import { RouteRecordRaw } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

// Import layout components
const PayrollLayout = () => import('@/layouts/MainLayout.vue');

// Import payroll module components using the new module-based structure
const PayrollView = () => import('@/modules/payroll/views/PayrollView.vue');
const AnalyticsDashboard = () => import('@/modules/payroll/views/AnalyticsDashboard.vue');
const PayRunView = () => import('@/modules/payroll/views/PayRunView.vue');
const PayRunCreateView = () => import('@/modules/payroll/views/PayRunCreateView.vue');
const PayRunProcessView = () => import('@/modules/payroll/views/PayRunProcessView.vue');
const PayRunApproveView = () => import('@/modules/payroll/views/PayRunApproveView.vue');
const PayslipsView = () => import('@/modules/payroll/views/PayslipsView.vue');
const PayslipDetailView = () => import('@/modules/payroll/views/PayslipDetailView.vue');
const EmployeePayrollView = () => import('@/modules/payroll/views/EmployeePayrollView.vue');
const PayrollSettingsView = () => import('@/modules/payroll/views/PayrollSettingsView.vue');
const PayrollReportsView = () => import('@/modules/payroll/views/PayrollReportsView.vue');
const PayrollTaxesView = () => import('@/modules/payroll/views/PayrollTaxesView.vue');

const routes: RouteRecordRaw[] = [
  {
    path: '/payroll',
    component: PayrollLayout,
    meta: {
      title: 'Payroll',
      icon: 'mdi-cash-multiple',
      requiresAuth: true,
      permissions: ['view_payroll'],
      breadcrumb: 'Payroll',
    },
    children: [
      {
        path: '',
        name: 'payroll-dashboard',
        component: PayrollView,
        meta: {
          title: 'Payroll Dashboard',
          icon: 'mdi-view-dashboard',
          requiresAuth: true,
          permissions: ['view_payroll'],
          breadcrumb: 'Dashboard',
        },
      },
      {
        path: 'analytics',
        name: 'payroll-analytics',
        component: AnalyticsDashboard,
        meta: {
          title: 'Payroll Analytics',
          icon: 'mdi-chart-box',
          requiresAuth: true,
          permissions: ['view_payroll_analytics'],
          breadcrumb: 'Analytics',
        },
      },
      {
        path: 'runs',
        name: 'payroll-runs',
        component: () => import('@/views/payroll/PayRunListView.vue'),
        meta: {
          title: 'Pay Runs',
          icon: 'mdi-calendar-check',
          requiresAuth: true,
          permissions: ['view_payruns'],
          breadcrumb: 'Pay Runs',
        },
      },
      {
        path: 'runs/create',
        name: 'payroll-run-create',
        component: PayRunCreateView,
        meta: {
          title: 'Create Pay Run',
          requiresAuth: true,
          permissions: ['create_payruns'],
          breadcrumb: 'Create Pay Run',
        },
      },
      {
        path: 'runs/:id',
        name: 'payroll-run-detail',
        component: PayRunView,
        props: true,
        meta: {
          title: 'Pay Run Details',
          requiresAuth: true,
          permissions: ['view_payruns'],
          breadcrumb: 'Pay Run Details',
        },
      },
      {
        path: 'runs/:id/process',
        name: 'payroll-run-process',
        component: PayRunProcessView,
        props: true,
        meta: {
          title: 'Process Pay Run',
          requiresAuth: true,
          permissions: ['process_payruns'],
          breadcrumb: 'Process Pay Run',
        },
      },
      {
        path: 'runs/:id/approve',
        name: 'payroll-run-approve',
        component: PayRunApproveView,
        props: true,
        meta: {
          title: 'Approve Pay Run',
          requiresAuth: true,
          permissions: ['approve_payruns'],
          breadcrumb: 'Approve Pay Run',
        },
      },
      {
        path: 'payslips',
        name: 'payslips',
        component: PayslipsView,
        meta: {
          title: 'Payslips',
          icon: 'mdi-file-document-multiple',
          requiresAuth: true,
          permissions: ['view_payslips'],
          breadcrumb: 'Payslips',
        },
      },
      {
        path: 'payslips/:id',
        name: 'payslip-detail',
        component: PayslipDetailView,
        props: true,
        meta: {
          title: 'Payslip Details',
          requiresAuth: true,
          permissions: ['view_payslips'],
          breadcrumb: 'Payslip Details',
        },
      },
      {
        path: 'employees',
        name: 'payroll-employees',
        component: () => import('@/views/payroll/EmployeePayrollListView.vue'),
        meta: {
          title: 'Employee Payroll',
          icon: 'mdi-account-group',
          requiresAuth: true,
          permissions: ['view_employee_payroll'],
          breadcrumb: 'Employee Payroll',
        },
      },
      {
        path: 'employees/:id',
        name: 'employee-payroll-detail',
        component: EmployeePayrollView,
        props: true,
        meta: {
          title: 'Employee Payroll Details',
          requiresAuth: true,
          permissions: ['view_employee_payroll'],
          breadcrumb: 'Employee Details',
        },
      },
      {
        path: 'taxes',
        name: 'payroll-taxes',
        component: PayrollTaxesView,
        meta: {
          title: 'Tax Management',
          icon: 'mdi-calculator',
          requiresAuth: true,
          permissions: ['manage_payroll_taxes'],
          breadcrumb: 'Tax Management',
        },
      },
      {
        path: 'reports',
        name: 'payroll-reports',
        component: PayrollReportsView,
        meta: {
          title: 'Payroll Reports',
          icon: 'mdi-chart-bar',
          requiresAuth: true,
          permissions: ['view_payroll_reports'],
          breadcrumb: 'Reports',
        },
      },
      {
        path: 'settings',
        name: 'payroll-settings',
        component: PayrollSettingsView,
        meta: {
          title: 'Payroll Settings',
          icon: 'mdi-cog',
          requiresAuth: true,
          permissions: ['manage_payroll_settings'],
          breadcrumb: 'Settings',
        },
      },
    ],
  },
];

export default routes;

// This function can be used to check if the user has permission to access a route
// It can be used in route guards
// Example usage in router.beforeEach:
// if (to.meta.permissions) {
//   const hasPermission = checkPermissions(to.meta.permissions);
//   if (!hasPermission) {
//     return { name: 'unauthorized' };
//   }
// }
// 
// function checkPermissions(requiredPermissions: string[]): boolean {
//   const authStore = useAuthStore();
//   if (!authStore.user) return false;
//   
//   // If user has 'admin' role, they have all permissions
//   if (authStore.user.roles?.includes('admin')) return true;
//   
//   // Check if user has all required permissions
//   return requiredPermissions.every(permission => 
//     authStore.user?.permissions?.includes(permission)
//   );
// }
