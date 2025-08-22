import { ref } from 'vue';
import { useToast } from 'primevue/usetoast';
import { glImportExportService } from '../services/gl-import-export.service';
import type { GlAccountFilters } from '../types/gl-account';

/**
 * Composable for handling GL Account import/export operations
 */
export function useGlImportExport() {
  const toast = useToast();
  const isExporting = ref(false);
  const isImporting = ref(false);
  const importProgress = ref(0);
  const importErrors = ref<string[]>([]);

  /**
   * Export GL accounts to a file
   */
  const exportAccounts = async (format: 'csv' | 'xlsx' | 'pdf', filters?: GlAccountFilters) => {
    isExporting.value = true;
    try {
      const blob = await glImportExportService.exportAccounts(format, filters);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
        .replace('T', '_')
        .split('+')[0];
      
      link.href = url;
      link.download = `gl-accounts-${timestamp}.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      toast.add({
        severity: 'success',
        summary: 'Export Successful',
        detail: `Accounts exported successfully to ${format.toUpperCase()} format.`,
        life: 5000
      });
    } catch (error) {
      console.error('Export failed:', error);
      toast.add({
        severity: 'error',
        summary: 'Export Failed',
        detail: 'Failed to export accounts. Please try again later.',
        life: 5000
      });
    } finally {
      isExporting.value = false;
    }
  };

  /**
   * Import GL accounts from a file
   */
  const importAccounts = async (file: File, updateExisting = false) => {
    isImporting.value = true;
    importProgress.value = 0;
    importErrors.value = [];
    
    try {
      const result = await glImportExportService.importAccounts(
        file,
        {
          updateExisting,
          onProgress: (progress) => {
            importProgress.value = progress;
          }
        }
      );

      if (result.errors.length > 0) {
        importErrors.value = result.errors;
        toast.add({
          severity: 'warn',
          summary: 'Import Completed with Warnings',
          detail: `Imported ${result.imported} accounts, updated ${result.updated} accounts. ${result.errors.length} errors occurred.`,
          life: 8000
        });
      } else {
        toast.add({
          severity: 'success',
          summary: 'Import Successful',
          detail: `Successfully imported ${result.imported} accounts, updated ${result.updated} accounts.`,
          life: 5000
        });
      }

      return result;
    } catch (error) {
      console.error('Import failed:', error);
      toast.add({
        severity: 'error',
        summary: 'Import Failed',
        detail: 'Failed to import accounts. Please check the file format and try again.',
        life: 5000
      });
      throw error;
    } finally {
      isImporting.value = false;
    }
  };

  /**
   * Download a template file for importing GL accounts
   */
  const downloadTemplate = async (format: 'csv' | 'xlsx' = 'xlsx') => {
    try {
      const blob = await glImportExportService.downloadTemplate(format);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      
      link.href = url;
      link.download = `gl-accounts-template.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      toast.add({
        severity: 'success',
        summary: 'Template Downloaded',
        detail: `Template file downloaded successfully in ${format.toUpperCase()} format.`,
        life: 5000
      });
    } catch (error) {
      console.error('Failed to download template:', error);
      toast.add({
        severity: 'error',
        summary: 'Download Failed',
        detail: 'Failed to download template file. Please try again later.',
        life: 5000
      });
    }
  };

  return {
    isExporting,
    isImporting,
    importProgress,
    importErrors,
    exportAccounts,
    importAccounts,
    downloadTemplate
  };
}

export default useGlImportExport;
