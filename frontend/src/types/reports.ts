export interface Report {
  id: string
  name: string
  description: string
  route: string
  icon: string
  category: string
  categoryId?: string
  lastRun?: string
  favorite?: boolean
  is_favorite?: boolean
  tags?: string[]
}

export type ReportType = 'table' | 'chart' | 'pivot' | 'financial'

export interface ReportParameter {
  name: string
  type: 'string' | 'number' | 'date' | 'boolean'
  label: string
  required: boolean
  defaultValue?: any
}

export interface ReportDisplayOptions {
  showHeader: boolean
  showFooter: boolean
  pageSize: number
  exportFormats: string[]
}