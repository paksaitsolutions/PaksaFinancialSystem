// Core Report Types
export interface Report {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: string;
  type: ReportType;
  dataSource: string;
  filters: ReportFilter[];
  columns: ReportColumn[];
  sorting: ReportSorting[];
  settings: ReportSettings;
  lastRun?: string;
  favorite?: boolean;
  tags?: string[];
  created: Date | string;
  modified: Date | string;
  createdBy?: string;
  modifiedBy?: string;
}

export enum ReportType {
  TABLE = 'table',
  CHART = 'chart',
  PIVOT = 'pivot',
  SUMMARY = 'summary',
  MATRIX = 'matrix',
  CROSSTAB = 'crosstab'
}

export interface ReportFilter {
  id: string;
  field: string;
  operator: FilterOperator;
  value: any;
  value2?: any;
  dataType?: 'string' | 'number' | 'date' | 'boolean' | 'list';
  displayName?: string;
}

export interface ReportColumn {
  field: string;
  header?: string;
  width?: number;
  visible?: boolean;
  dataType?: 'string' | 'number' | 'date' | 'currency' | 'boolean' | 'percentage';
  format?: string;
  aggregate?: 'sum' | 'avg' | 'min' | 'max' | 'count';
  style?: Record<string, any>;
  filterable?: boolean;
  sortable?: boolean;
  groupable?: boolean;
}

export interface ReportSorting {
  field: string;
  direction: 'asc' | 'desc';
}

export interface ReportSettings {
  showGridLines: boolean;
  showRowNumbers: boolean;
  allowExport: boolean;
  allowPrint: boolean;
  rowsPerPage: number;
  showFooter?: boolean;
  showHeader?: boolean;
  stripedRows?: boolean;
  compactMode?: boolean;
  showColumnFilters?: boolean;
  showGlobalFilter?: boolean;
  paginatorPosition?: 'top' | 'bottom' | 'both';
  rowSelectionMode?: 'single' | 'multiple' | 'none';
  exportFormats?: ('pdf' | 'excel' | 'csv')[];
  theme?: string;
}

export type FilterOperator = 
  | 'equals' 
  | 'notEquals' 
  | 'contains' 
  | 'notContains' 
  | 'startsWith' 
  | 'endsWith' 
  | 'gt' 
  | 'gte' 
  | 'lt' 
  | 'lte' 
  | 'between' 
  | 'in' 
  | 'notIn' 
  | 'isNull' 
  | 'isNotNull' 
  | 'isEmpty' 
  | 'isNotEmpty';

// Report Category and Data Source
export interface ReportCategory {
  id: string;
  name: string;
  icon?: string;
  description?: string;
  count?: number;
}

export interface ReportDataSource {
  id: string;
  name: string;
  description: string;
  type: 'database' | 'api' | 'file' | 'custom';
  connectionString?: string;
  tables?: string[];
  isActive?: boolean;
}

// Report Execution and Scheduling
export interface ReportExecution {
  id: string;
  reportId: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  startedAt: Date | string;
  completedAt?: Date | string;
  initiatedBy: string;
  parameters: Record<string, any>;
  result?: {
    rowCount: number;
    columns: string[];
    data: any[];
    summary?: Record<string, any>;
  };
  error?: {
    message: string;
    details?: string;
  };
  executionTimeMs?: number;
  fileUrl?: string;
  fileFormat?: 'pdf' | 'excel' | 'csv' | 'json';
}

export interface ReportSchedule {
  id: string;
  reportId: string;
  name: string;
  description?: string;
  frequency: 'once' | 'hourly' | 'daily' | 'weekly' | 'monthly' | 'custom';
  cronExpression?: string;
  startDate: Date | string;
  endDate?: Date | string;
  nextRun?: Date | string;
  lastRun?: Date | string;
  lastRunStatus?: 'success' | 'failed' | 'running';
  isActive: boolean;
  recipients: string[];
  format: 'pdf' | 'excel' | 'csv' | 'json';
  parameters: Record<string, any>;
  created: Date | string;
  modified: Date | string;
  createdBy: string;
  modifiedBy?: string;
}

// Report Subscription and Favorites
export interface ReportSubscription {
  id: string;
  reportId: string;
  userId: string;
  email: string;
  isActive: boolean;
  frequency: 'real-time' | 'daily' | 'weekly' | 'monthly';
  lastNotified?: Date | string;
  created: Date | string;
  modified: Date | string;
}

export interface ReportFavorite {
  id: string;
  reportId: string;
  userId: string;
  created: Date | string;
}

// Report Comments
export interface ReportComment {
  id: string;
  reportId: string;
  userId: string;
  userName: string;
  userAvatar?: string;
  content: string;
  created: Date | string;
  modified?: Date | string;
  replies?: ReportComment[];
}

// Report Export Options
export interface ReportExportOptions {
  format: 'pdf' | 'excel' | 'csv' | 'json';
  orientation?: 'portrait' | 'landscape';
  pageSize?: 'A4' | 'Letter' | 'A3' | 'A5' | 'Legal';
  includeHeader?: boolean;
  includeFooter?: boolean;
  includePageNumbers?: boolean;
  includeCharts?: boolean;
  includeData?: boolean;
  fileName?: string;
  filterCriteria?: Record<string, any>;
  sortCriteria?: ReportSorting[];
  selectedColumns?: string[];
  showGridLines?: boolean;
  showRowNumbers?: boolean;
  theme?: 'light' | 'dark' | 'custom';
  customStyles?: Record<string, any>;
  margins?: {
    top?: number;
    right?: number;
    bottom?: number;
    left?: number;
  };
  metadata?: {
    title?: string;
    author?: string;
    subject?: string;
    keywords?: string[];
  };
}
