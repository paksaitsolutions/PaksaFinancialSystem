import type { RouteRecordRaw } from 'vue-router';

const hrmRoutes: RouteRecordRaw[] = [
  // Dashboard
  {
    path: 'hrm',
    name: 'HrmDashboard',
    component: () => import('@/views/hrm/HrmDashboard.vue'),
    meta: { title: 'HRM Dashboard' }
  },
  // Employee Management
  {
    path: 'hrm/employees',
    name: 'HrmEmployees',
    component: () => import('@/views/hrm/EmployeesView.vue'),
    meta: { title: 'Employee Management' }
  },
  {
    path: 'hrm/employees/new',
    name: 'HrmEmployeesNew',
    component: () => import('@/views/hrm/EmployeesView.vue'),
    meta: { title: 'Add New Employee' }
  },
  // Departments
  {
    path: 'hrm/departments',
    name: 'HrmDepartments',
    component: () => import('@/views/hrm/DepartmentsView.vue'),
    meta: { title: 'Department Management' }
  },
  // Positions
  {
    path: 'hrm/positions',
    name: 'HrmPositions',
    component: () => import('@/views/hrm/HrmPositions.vue'),
    meta: { title: 'Position Management' }
  },
  // Attendance
  {
    path: 'hrm/attendance',
    name: 'HrmAttendance',
    component: () => import('@/views/hrm/HrmAttendance.vue'),
    meta: { title: 'Attendance' }
  },
  // Leave Management
  {
    path: 'hrm/leave',
    name: 'HrmLeave',
    component: () => import('@/views/hrm/HrmLeave.vue'),
    meta: { title: 'Leave Management' }
  },
  {
    path: 'hrm/leave-requests',
    name: 'HrmLeaveRequests',
    component: () => import('@/views/hrm/HrmLeaveRequests.vue'),
    meta: { title: 'Leave Requests' }
  },
  {
    path: 'hrm/leave-types',
    name: 'HrmLeaveTypes',
    component: () => import('@/views/hrm/HrmLeaveTypes.vue'),
    meta: { title: 'Leave Types' }
  },
  {
    path: 'hrm/leave-balance',
    name: 'HrmLeaveBalance',
    component: () => import('@/views/hrm/HrmLeaveBalance.vue'),
    meta: { title: 'Leave Balance' }
  },
  {
    path: 'hrm/leave-calendar',
    name: 'HrmLeaveCalendar',
    component: () => import('@/views/hrm/HrmLeaveCalendar.vue'),
    meta: { title: 'Leave Calendar' }
  },
  {
    path: 'hrm/policies',
    name: 'HrmPolicies',
    component: () => import('@/views/hrm/HrmPolicies.vue'),
    meta: { title: 'HR Policies' }
  },
  // Payroll
  {
    path: 'hrm/payroll',
    name: 'HrmPayroll',
    component: () => import('@/views/hrm/HrmPayroll.vue'),
    meta: { title: 'Payroll Management' }
  },
  // Training
  {
    path: 'hrm/training',
    name: 'HrmTraining',
    component: () => import('@/views/hrm/HrmTraining.vue'),
    meta: { title: 'Training Management' }
  },
  // Skills
  {
    path: 'hrm/skills',
    name: 'HrmSkills',
    component: () => import('@/views/hrm/HrmSkills.vue'),
    meta: { title: 'Skills Management' }
  },
  // Recruitment
  {
    path: 'hrm/candidates',
    name: 'HrmCandidates',
    component: () => import('@/views/hrm/HrmCandidates.vue'),
    meta: { title: 'Candidate Management' }
  },
  {
    path: 'hrm/job-openings',
    name: 'HrmJobOpenings',
    component: () => import('@/views/hrm/HrmJobOpenings.vue'),
    meta: { title: 'Job Openings' }
  },
  {
    path: 'hrm/interviews',
    name: 'HrmInterviews',
    component: () => import('@/views/hrm/HrmInterviews.vue'),
    meta: { title: 'Interview Management' }
  },
  // Onboarding
  {
    path: 'hrm/onboarding',
    name: 'HrmOnboarding',
    component: () => import('@/views/hrm/HrmOnboarding.vue'),
    meta: { title: 'Employee Onboarding' }
  },
  // Performance
  {
    path: 'hrm/performance',
    name: 'HrmPerformance',
    component: () => import('@/views/hrm/HrmPerformance.vue'),
    meta: { title: 'Performance Management' }
  },
  {
    path: 'hrm/appraisals',
    name: 'HrmAppraisals',
    component: () => import('@/views/hrm/HrmAppraisals.vue'),
    meta: { title: 'Performance Appraisals' }
  },
  {
    path: 'hrm/goals',
    name: 'HrmGoals',
    component: () => import('@/views/hrm/HrmGoals.vue'),
    meta: { title: 'Goals & Objectives' }
  },
  // Email Templates
  {
    path: 'hrm/email-templates',
    name: 'HrmEmailTemplates',
    component: () => import('@/views/hrm/HrmEmailTemplates.vue'),
    meta: { title: 'Email Templates' }
  },
  // Reports
  {
    path: 'hrm/reports',
    name: 'HrmReports',
    component: () => import('@/views/hrm/HrmReports.vue'),
    meta: { title: 'HR Reports' }
  },
  {
    path: 'hrm/reports/attendance',
    name: 'HrmReportAttendance',
    component: () => import('@/views/hrm/HrmReportAttendance.vue'),
    meta: { title: 'Attendance Reports' }
  },
  {
    path: 'hrm/reports/directory',
    name: 'HrmReportDirectory',
    component: () => import('@/views/hrm/HrmReportDirectory.vue'),
    meta: { title: 'Employee Directory' }
  },
  {
    path: 'hrm/reports/leave',
    name: 'HrmReportLeave',
    component: () => import('@/views/hrm/HrmReportLeave.vue'),
    meta: { title: 'Leave Reports' }
  },
  {
    path: 'hrm/reports/turnover',
    name: 'HrmReportTurnover',
    component: () => import('@/views/hrm/HrmReportTurnover.vue'),
    meta: { title: 'Turnover Reports' }
  }
];

export default hrmRoutes;
