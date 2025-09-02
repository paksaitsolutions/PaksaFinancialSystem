// Reports Module Exports
export { default as ReportsView } from './views/ReportsView.vue'
export { default as FinancialReportsView } from './views/FinancialReportsView.vue'
export { default as OperationalReportsView } from './views/OperationalReportsView.vue'
export { default as ComplianceReportsView } from './views/ComplianceReportsView.vue'
export { default as CustomReportsView } from './views/CustomReportsView.vue'

// Types
export interface Report {
  id: string
  name: string
  category?: string
  description: string
  icon: string
  color: string
  status: 'Active' | 'Draft' | 'Archived' | 'Pending'
  frequency: string
  lastRun?: string
  running: boolean
}

export interface ReportModule {
  id: string
  name: string
  icon: string
  color: string
  reports: Report[]
}

// Constants
export const REPORT_STATUSES = {
  ACTIVE: 'Active',
  DRAFT: 'Draft',
  ARCHIVED: 'Archived',
  PENDING: 'Pending'
} as const

export const REPORT_FREQUENCIES = {
  DAILY: 'Daily',
  WEEKLY: 'Weekly',
  MONTHLY: 'Monthly',
  QUARTERLY: 'Quarterly',
  YEARLY: 'Yearly',
  MANUAL: 'Manual'
} as const