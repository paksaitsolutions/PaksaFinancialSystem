import { format, subDays, startOfMonth, endOfMonth, startOfYear, endOfYear, subMonths } from 'date-fns';

export interface DateRange {
  startDate: Date;
  endDate: Date;
  label?: string;
}

export interface ReportFilter {
  id: string;
  label: string;
  type: 'text' | 'number' | 'date' | 'select' | 'multiselect' | 'boolean' | 'daterange';
  options?: Array<{ label: string; value: any }>;
  defaultValue?: any;
  required?: boolean;
  placeholder?: string;
  disabled?: boolean;
  hidden?: boolean;
  group?: string;
  dependsOn?: string;
  dependsValue?: any;
}

export interface ReportColumn {
  field: string;
  header: string;
  type?: 'text' | 'number' | 'currency' | 'percentage' | 'date' | 'boolean' | 'action' | 'badge';
  sortable?: boolean;
  filterable?: boolean;
  visible?: boolean;
  width?: string | number;
  align?: 'left' | 'center' | 'right';
  format?: (value: any) => string;
  style?: Record<string, string>;
  className?: string;
}

export interface ReportOptions {
  title: string;
  description?: string;
  exportFormats?: Array<'csv' | 'excel' | 'pdf' | 'print'>;
  defaultSortField?: string;
  defaultSortOrder?: 'asc' | 'desc' | null;
  pageSize?: number;
  showGridLines?: boolean;
  stripedRows?: boolean;
  showCurrentPageReport?: boolean;
  rowHover?: boolean;
  scrollable?: boolean;
  resizableColumns?: boolean;
  reorderableColumns?: boolean;
  showColumnSelector?: boolean;
  showSettings?: boolean;
  showSummaryRow?: boolean;
  showGrouping?: boolean;
  expandableRows?: boolean;
  selectionMode?: 'single' | 'multiple' | null;
}

export interface ReportState {
  loading: boolean;
  error: boolean;
  errorMessage: string;
  data: any[];
  totalRecords: number;
  filters: Record<string, any>;
  sortField: string;
  sortOrder: number;
  first: number;
  rows: number;
  exportLoading: boolean;
  exportFormat: 'csv' | 'excel' | 'pdf' | 'print';
  columns: ReportColumn[];
  visibleColumns: string[];
  selectedRows: any[];
  currentPage: number;
  pageCount: number;
  pageSize: number;
}

// Common date ranges for reports
export const dateRanges: Record<string, () => DateRange> = {
  today: () => {
    const today = new Date();
    return {
      startDate: today,
      endDate: today,
      label: 'Today'
    };
  },
  yesterday: () => {
    const yesterday = subDays(new Date(), 1);
    return {
      startDate: yesterday,
      endDate: yesterday,
      label: 'Yesterday'
    };
  },
  thisWeek: () => {
    const today = new Date();
    const start = subDays(today, today.getDay());
    return {
      startDate: start,
      endDate: today,
      label: 'This Week'
    };
  },
  lastWeek: () => {
    const today = new Date();
    const end = subDays(today, today.getDay() + 1);
    const start = subDays(end, 6);
    return {
      startDate: start,
      endDate: end,
      label: 'Last Week'
    };
  },
  thisMonth: () => ({
    startDate: startOfMonth(new Date()),
    endDate: new Date(),
    label: 'This Month'
  }),
  lastMonth: () => {
    const today = new Date();
    const start = startOfMonth(subMonths(today, 1));
    const end = endOfMonth(start);
    return {
      startDate: start,
      endDate: end,
      label: 'Last Month'
    };
  },
  thisYear: () => ({
    startDate: startOfYear(new Date()),
    endDate: new Date(),
    label: 'This Year'
  }),
  lastYear: () => {
    const today = new Date();
    const start = new Date(today.getFullYear() - 1, 0, 1);
    const end = new Date(today.getFullYear() - 1, 11, 31);
    return {
      startDate: start,
      endDate: end,
      label: 'Last Year'
    };
  }
};

// Format currency values
export const formatCurrency = (value: number, currency = 'USD'): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value);
};

// Format percentage values
export const formatPercentage = (value: number, decimals = 2): string => {
  return `${value.toFixed(decimals)}%`;
};

// Format date values
export const formatDate = (date: Date | string, formatStr = 'MMM d, yyyy'): string => {
  if (!date) return '';
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return format(dateObj, formatStr);
};

// Initialize report state
export const useReportState = (initialState: Partial<ReportState> = {}): ReportState => {
  return {
    loading: false,
    error: false,
    errorMessage: '',
    data: [],
    totalRecords: 0,
    filters: {},
    sortField: '',
    sortOrder: 1,
    first: 0,
    rows: 25,
    exportLoading: false,
    exportFormat: 'excel',
    columns: [],
    visibleColumns: [],
    selectedRows: [],
    currentPage: 1,
    pageCount: 1,
    pageSize: 25,
    ...initialState
  };
};

// Common report filters
export const commonFilters: ReportFilter[] = [
  {
    id: 'dateRange',
    label: 'Date Range',
    type: 'daterange',
    required: true,
    defaultValue: dateRanges.thisMonth()
  },
  {
    id: 'status',
    label: 'Status',
    type: 'select',
    options: [
      { label: 'All', value: 'all' },
      { label: 'Active', value: 'active' },
      { label: 'Inactive', value: 'inactive' },
      { label: 'Pending', value: 'pending' },
      { label: 'Completed', value: 'completed' },
      { label: 'Cancelled', value: 'cancelled' }
    ],
    defaultValue: 'all'
  }
];

// Common report columns
export const commonColumns: ReportColumn[] = [
  {
    field: 'id',
    header: 'ID',
    type: 'text',
    sortable: true,
    width: '80px'
  },
  {
    field: 'name',
    header: 'Name',
    type: 'text',
    sortable: true,
    width: '200px'
  },
  {
    field: 'date',
    header: 'Date',
    type: 'date',
    sortable: true,
    width: '120px',
    format: (value) => formatDate(value, 'MMM d, yyyy')
  },
  {
    field: 'amount',
    header: 'Amount',
    type: 'currency',
    sortable: true,
    width: '120px',
    align: 'right',
    format: (value) => formatCurrency(value)
  },
  {
    field: 'status',
    header: 'Status',
    type: 'badge',
    sortable: true,
    width: '120px'
  },
  {
    field: 'actions',
    header: 'Actions',
    type: 'action',
    sortable: false,
    width: '150px',
    align: 'center'
  }
];

// Export report data to different formats
export const exportReport = (data: any[], format: 'csv' | 'excel' | 'pdf' | 'print', filename: string) => {
  // TODO: Implement export functionality
  console.log(`Exporting ${data.length} rows to ${format} as ${filename}`);
  
  switch (format) {
    case 'csv':
      // Export to CSV
      break;
    case 'excel':
      // Export to Excel
      break;
    case 'pdf':
      // Export to PDF
      break;
    case 'print':
      // Print report
      window.print();
      break;
  }
};

// Generate a unique ID for report components
export const generateReportId = (prefix = 'report'): string => {
  return `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
};

// Format report title with date range
export const formatReportTitle = (title: string, dateRange: DateRange): string => {
  if (!dateRange) return title;
  const start = formatDate(dateRange.startDate, 'MMM d, yyyy');
  const end = formatDate(dateRange.endDate, 'MMM d, yyyy');
  return `${title} (${start} - ${end})`;
};

// Create a download link for exported files
export const createDownloadLink = (data: Blob | string, filename: string): void => {
  const blob = typeof data === 'string' ? new Blob([data], { type: 'text/plain' }) : data;
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
};
