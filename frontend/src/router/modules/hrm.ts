import type { RouteRecordWithMeta } from '../types';

const hrmRoutes: RouteRecordWithMeta = {
  path: 'hrm',
  meta: { 
    title: 'Human Resources',
    icon: 'pi pi-users',
    requiresAuth: true,
    module: 'hrm',
    breadcrumb: true
  },
  children: [
    // Dashboard
    {
      path: '',
      name: 'HrmDashboard',
      component: () => import('@/views/hrm/HrmDashboard.vue'),
      meta: { title: 'HRM Dashboard' }
    },
    // Employee Management
    {
      path: 'employees',
      name: 'HrmEmployees',
      component: () => import('@/views/hrm/EmployeesView.vue'),
      meta: { 
        title: 'Employee Management', 
        roles: ['hrm:read', 'hrm:write'],
        layout: 'app' // Explicitly use app layout
      }
    },
    {
      path: 'employees/:id',
      name: 'HrmEmployeeDetails',
      component: () => import('@/views/hrm/EmployeesView.vue'),
      meta: { 
        title: 'Employee Details', 
        roles: ['hrm:read'],
        layout: 'app' // Explicitly use app layout
      },
      props: true
    },
    // Departments
    {
      path: 'departments',
      name: 'HrmDepartments',
      component: () => import('@/views/hrm/DepartmentsView.vue'),
      meta: { title: 'Department Management', roles: ['hrm:admin'] }
    },
    // Positions
    {
      path: 'positions',
      name: 'HrmPositions',
      component: () => import('@/views/hrm/HrmPositions.vue'),
      meta: { title: 'Position Management', roles: ['hrm:admin'] }
    },
    // Email Templates
    {
      path: 'email-templates',
      name: 'HrmEmailTemplates',
      component: () => import('@/views/hrm/HrmEmailTemplates.vue'),
      meta: { title: 'Email Templates', roles: ['hrm:admin'] }
    },
    // Attendance
    {
      path: 'attendance',
      name: 'HrmAttendance',
      component: () => import('@/views/hrm/HrmAttendance.vue'),
      meta: { title: 'Attendance', roles: ['hrm:read'] }
    },
    // Leave Management
    {
      path: 'leave',
      component: { template: '<router-view />' },
      meta: { title: 'Leave Management' },
      children: [
        {
          path: '',
          name: 'HrmLeaveList',
          component: () => import('@/views/hrm/HrmLeaveRequests.vue'),
          meta: { title: 'Leave Requests' }
        },
        {
          path: 'types',
          name: 'HrmLeaveTypes',
          component: () => import('@/views/hrm/HrmLeaveTypes.vue'),
          meta: { title: 'Leave Types', roles: ['hrm:admin'] }
        },
        {
          path: 'balance',
          name: 'HrmLeaveBalance',
          component: () => import('@/views/hrm/HrmLeaveBalance.vue'),
          meta: { title: 'Leave Balance' }
        },
        {
          path: 'calendar',
          name: 'HrmLeaveCalendar',
          component: () => import('@/views/hrm/HrmLeaveCalendar.vue'),
          meta: { title: 'Leave Calendar' }
        },
        {
          path: 'policies',
          name: 'HrmPolicies',
          component: () => import('@/views/hrm/HrmPolicies.vue'),
          meta: { title: 'Leave Policies', roles: ['hrm:admin'] }
        }
      ]
    },
    // Payroll
    {
      path: 'payroll',
      component: { template: '<router-view />' },
      meta: { title: 'Payroll', roles: ['payroll:read'] },
      children: [
        {
          path: '',
          name: 'HrmPayrollDashboard',
          component: () => import('@/views/hrm/HrmPayroll.vue'),
          meta: { title: 'Payroll Dashboard' }
        },
        {
          path: 'runs',
          name: 'HrmPayrollRuns',
          component: () => import('@/views/hrm/HrmPayroll.vue'),
          meta: { title: 'Payroll Runs', roles: ['payroll:write'], tab: 'runs' }
        },
        {
          path: 'analytics',
          name: 'HrmPayrollAnalytics',
          component: () => import('@/views/hrm/HrmPayroll.vue'),
          meta: { title: 'Payroll Analytics', roles: ['payroll:read'], tab: 'analytics' }
        }
      ]
    },
    // Reports
    {
      path: 'reports',
      name: 'HrmReports',
      component: () => import('@/views/hrm/HrmReports.vue'),
      meta: { title: 'HR Reports', roles: ['hrm:read'] },
      children: [
        {
          path: 'attendance',
          name: 'HrmReportAttendance',
          component: () => import('@/views/hrm/HrmReportAttendance.vue'),
          meta: { title: 'Attendance Reports' }
        },
        {
          path: 'directory',
          name: 'HrmReportDirectory',
          component: () => import('@/views/hrm/HrmReportDirectory.vue'),
          meta: { title: 'Employee Directory' }
        },
        {
          path: 'leave',
          name: 'HrmReportLeave',
          component: () => import('@/views/hrm/HrmReportLeave.vue'),
          meta: { title: 'Leave Reports' }
        },
        {
          path: 'turnover',
          name: 'HrmReportTurnover',
          component: () => import('@/views/hrm/HrmReportTurnover.vue'),
          meta: { title: 'Turnover Reports' }
        }
      ]
    }
  ]
};

export default hrmRoutes;
