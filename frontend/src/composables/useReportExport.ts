import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useToast } from 'primevue/usetoast';
import { useExport } from '@/core/utils/export';

/**
 * Composable for handling report exports with a consistent UI/UX
 */
export function useReportExport() {
  const { t } = useI18n();
  const toast = useToast();
  const exportDialogRef = ref();
  const { isExporting, exportProgress, exportData, prepareExportData } = useExport();

  /**
   * Open the export dialog
   * @param options Initial export options
   */
  const openExportDialog = (options = {}) => {
    if (exportDialogRef.value) {
      exportDialogRef.value.open(options);
    }
  };

  /**
   * Handle export with the given options
   * @param data The data to export (if not using API)
   * @param options Export options
   * @param apiEndpoint Optional API endpoint to fetch data from
   */
  const handleExport = async (data: any[] | null, options: any, apiEndpoint?: string) => {
    try {
      if (apiEndpoint) {
        // Export from API
        return await exportData({
          endpoint: apiEndpoint,
          format: options.format,
          filters: options.filters || {},
          exportAll: options.scope === 'all',
          page: options.page || 1,
          pageSize: options.pageSize || 25,
          sortField: options.sortField,
          sortOrder: options.sortOrder,
        });
      } else if (data) {
        // Export directly from provided data
        return await exportData({
          data,
          format: options.format,
          columns: options.columns,
          fileName: options.fileName,
        });
      } else {
        throw new Error('No data or API endpoint provided for export');
      }
    } catch (error) {
      console.error('Export failed:', error);
      toast.add({
        severity: 'error',
        summary: t('export.error.title'),
        detail: t('export.error.message'),
        life: 5000,
      });
      throw error;
    }
  };

  /**
   * Handle successful export
   * @param format The export format
   */
  const onExportSuccess = (format: string) => {
    toast.add({
      severity: 'success',
      summary: t('export.success.title'),
      detail: t('export.success.message', { format: format.toUpperCase() }),
      life: 3000,
    });
  };

  /**
   * Handle export error
   * @param error The error that occurred
   */
  const onExportError = (error: any) => {
    console.error('Export error:', error);
    toast.add({
      severity: 'error',
      summary: t('export.error.title'),
      detail: error.message || t('export.error.message'),
      life: 5000,
    });
  };

  return {
    // Refs
    exportDialogRef,
    isExporting,
    exportProgress,
    
    // Methods
    openExportDialog,
    handleExport,
    onExportSuccess,
    onExportError,
    prepareExportData,
  };
}

export default useReportExport;
