import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useToast } from 'primevue/usetoast';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import axios from 'axios';

export type ExportFormat = 'excel' | 'csv' | 'pdf';

export interface ExportColumn {
  field: string;
  header: string;
  type?: 'text' | 'number' | 'date' | 'currency' | 'boolean';
  format?: string;
  hidden?: boolean;
  width?: string;
  style?: Record<string, any>;
}

export interface ExportOptions {
  title?: string;
  sheetName?: string;
  columns?: ExportColumn[];
  filters?: Record<string, any>;
  exportAll?: boolean;
  pageSize?: number;
  page?: number;
  sortField?: string;
  sortOrder?: number;
}

/**
 * Composable for handling data exports
 */
export function useExport() {
  const { t } = useI18n();
  const toast = useToast();
  const router = useRouter();
  const authStore = useAuthStore();
  
  const isExporting = ref(false);
  const exportProgress = ref(0);
  
  /**
   * Export data from an API endpoint
   * @param endpoint API endpoint (without base URL)
   * @param format Export format (excel, csv, pdf)
   * @param options Export options
   * @param data Custom data to export (if not using API)
   */
  async function exportData(
    endpoint: string,
    format: ExportFormat = 'excel',
    options: ExportOptions = {},
    data?: any[] | null
  ) {
    try {
      isExporting.value = true;
      exportProgress.value = 0;
      
      // If data is provided directly, use it instead of fetching from API
      if (data) {
        return exportDataDirect(data, format, options);
      }
      
      // Build query parameters
      const params: Record<string, any> = {
        format,
        ...options.filters,
        export: true,
        exportAll: options.exportAll,
      };
      
      // Add pagination if not exporting all
      if (!options.exportAll) {
        params.page = options.page || 1;
        params.perPage = options.pageSize || 25;
      }
      
      // Add sorting
      if (options.sortField) {
        params.sortBy = options.sortField;
        params.sortOrder = options.sortOrder || 1;
      }
      
      // Make the API request
      const response = await axios({
        method: 'GET',
        url: `${import.meta.env.VITE_API_BASE_URL}${endpoint}`,
        params,
        responseType: 'blob',
        onDownloadProgress: (progressEvent) => {
          if (progressEvent.total) {
            exportProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          }
        },
        headers: {
          'Authorization': `Bearer ${authStore.accessToken}`,
          'Accept': getMimeType(format),
        },
      });
      
      // Create a download link and trigger it
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const contentDisposition = response.headers['content-disposition'];
      let filename = `export_${new Date().toISOString().slice(0, 10)}`;
      
      // Extract filename from content disposition if available
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^\n]*)/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '');
        }
      } else {
        // Fallback filename with extension
        filename += `.${format}`;
      }
      
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      // Clean up
      window.URL.revokeObjectURL(url);
      
      toast.add({
        severity: 'success',
        summary: t('export.success.title'),
        detail: t('export.success.message', { format: format.toUpperCase() }),
        life: 3000,
      });
      
      return true;
    } catch (error: any) {
      console.error('Export error:', error);
      
      // Handle unauthorized (401) errors
      if (error.response?.status === 401) {
        toast.add({
          severity: 'error',
          summary: t('export.error.unauthorized.title'),
          detail: t('export.error.unauthorized.message'),
          life: 5000,
        });
        router.push('/auth/login');
        return false;
      }
      
      // Handle other errors
      toast.add({
        severity: 'error',
        summary: t('export.error.generic.title'),
        detail: error.response?.data?.message || t('export.error.generic.message'),
        life: 5000,
      });
      
      return false;
    } finally {
      isExporting.value = false;
      exportProgress.value = 0;
    }
  }
  
  /**
   * Export data directly without an API call
   * @param data Data to export
   * @param format Export format
   * @param options Export options
   */
  async function exportDataDirect(
    data: any[],
    format: ExportFormat = 'excel',
    options: ExportOptions = {}
  ) {
    try {
      isExporting.value = true;
      exportProgress.value = 0;
      
      // Prepare the data for export
      const exportData = prepareExportData(data, options.columns);
      
      // Create a blob with the data
      let blob: Blob;
      let filename = options.title || 'export';
      
      switch (format) {
        case 'csv':
          blob = new Blob([convertToCSV(exportData)], { type: 'text/csv;charset=utf-8;' });
          filename += '.csv';
          break;
          
        case 'excel':
          // For Excel, we need to use a library like xlsx or call our backend
          // For now, we'll convert to CSV as a fallback
          blob = new Blob([convertToCSV(exportData)], { type: 'application/vnd.ms-excel;charset=utf-8;' });
          filename += '.xlsx';
          // TODO: Implement proper Excel export using xlsx library
          break;
          
        case 'pdf':
          // For PDF, we'll use our backend service
          // For now, we'll convert to CSV as a fallback
          blob = new Blob([convertToCSV(exportData)], { type: 'application/pdf' });
          filename += '.pdf';
          // TODO: Implement proper PDF export using backend
          break;
          
        default:
          throw new Error(`Unsupported export format: ${format}`);
      }
      
      // Create a download link and trigger it
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      // Clean up
      window.URL.revokeObjectURL(url);
      
      toast.add({
        severity: 'success',
        summary: t('export.success.title'),
        detail: t('export.success.message', { format: format.toUpperCase() }),
        life: 3000,
      });
      
      return true;
    } catch (error: any) {
      console.error('Export error:', error);
      
      toast.add({
        severity: 'error',
        summary: t('export.error.generic.title'),
        detail: error.message || t('export.error.generic.message'),
        life: 5000,
      });
      
      return false;
    } finally {
      isExporting.value = false;
      exportProgress.value = 0;
    }
  }
  
  /**
   * Prepare data for export based on column definitions
   */
  function prepareExportData(data: any[], columns?: ExportColumn[]) {
    if (!columns || columns.length === 0) {
      return data;
    }
    
    return data.map(item => {
      const result: Record<string, any> = {};
      
      columns.forEach(col => {
        if (col.hidden) return;
        
        // Get the value using the field path (supports nested properties)
        const value = getNestedValue(item, col.field);
        
        // Format the value based on type
        result[col.header] = formatValue(value, col);
      });
      
      return result;
    });
  }
  
  /**
   * Get a nested property from an object using a path string
   */
  function getNestedValue(obj: any, path: string) {
    return path.split('.').reduce((o, p) => (o || {})[p], obj);
  }
  
  /**
   * Format a value based on column definition
   */
  function formatValue(value: any, column: ExportColumn) {
    if (value === null || value === undefined) {
      return '';
    }
    
    switch (column.type) {
      case 'date':
        return formatDate(value, column.format);
        
      case 'number':
        return formatNumber(value, column.format);
        
      case 'currency':
        return formatCurrency(value, column.format);
        
      case 'boolean':
        return value ? t('common.yes') : t('common.no');
        
      default:
        return String(value);
    }
  }
  
  /**
   * Format a date value
   */
  function formatDate(value: string | Date, format?: string) {
    if (!value) return '';
    
    const date = typeof value === 'string' ? new Date(value) : value;
    
    if (!format) {
      return date.toLocaleDateString();
    }
    
    // Simple formatting - in a real app, use a library like date-fns or moment
    const pad = (num: number) => num.toString().padStart(2, '0');
    
    return format
      .replace('yyyy', date.getFullYear().toString())
      .replace('MM', pad(date.getMonth() + 1))
      .replace('dd', pad(date.getDate()))
      .replace('HH', pad(date.getHours()))
      .replace('mm', pad(date.getMinutes()))
      .replace('ss', pad(date.getSeconds()));
  }
  
  /**
   * Format a number value
   */
  function formatNumber(value: number, format?: string) {
    if (format) {
      // Simple number formatting - in a real app, use a library like numeral.js
      const parts = format.split('.');
      const decimals = parts[1] ? parts[1].length : 0;
      return value.toFixed(decimals);
    }
    
    return value.toString();
  }
  
  /**
   * Format a currency value
   */
  function formatCurrency(value: number, format?: string) {
    const currency = format || 'USD';
    return new Intl.NumberFormat(undefined, {
      style: 'currency',
      currency,
    }).format(value);
  }
  
  /**
   * Convert data to CSV format
   */
  function convertToCSV(data: any[]) {
    if (data.length === 0) return '';
    
    // Get headers from the first object
    const headers = Object.keys(data[0]);
    
    // Create CSV header row
    let csv = headers.join(',') + '\n';
    
    // Add data rows
    data.forEach(row => {
      const values = headers.map(header => {
        const value = row[header];
        
        // Escape quotes and wrap in quotes if the value contains commas or quotes
        if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
          return `"${value.replace(/"/g, '""')}"`;
        }
        
        return value || '';
      });
      
      csv += values.join(',') + '\n';
    });
    
    return csv;
  }
  
  /**
   * Get MIME type for a format
   */
  function getMimeType(format: ExportFormat) {
    switch (format) {
      case 'excel':
        return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
      case 'csv':
        return 'text/csv';
      case 'pdf':
        return 'application/pdf';
      default:
        return 'application/octet-stream';
    }
  }
  
  return {
    isExporting,
    exportProgress,
    exportData,
    exportDataDirect,
    prepareExportData,
  };
}
