import { ExportAnalyticsRequest, ExportAnalyticsResponse } from '@/types/tax';
import { taxAnalyticsApi } from '@/api/tax/analytics';
import { useNotification } from '@/composables/useNotification';

export class TaxAnalyticsExportService {
  private api = taxAnalyticsApi;
  private notification = useNotification();

  async exportAnalytics(request: ExportAnalyticsRequest): Promise<void> {
    try {
      const exportResponse = await this.api.exportAnalytics(request);
      
      if (exportResponse.status === 'completed') {
        await this.downloadExport(exportResponse);
      } else {
        // Monitor export status
        await this.monitorExportStatus(exportResponse);
      }
    } catch (error) {
      console.error('Error exporting tax analytics:', error);
      this.notification.error('Failed to export tax analytics');
      throw error;
    }
  }

  private async monitorExportStatus(exportResponse: ExportAnalyticsResponse): Promise<void> {
    const checkInterval = 5000; // 5 seconds
    let isCompleted = false;

    while (!isCompleted) {
      try {
        const status = await this.api.getExportStatus(exportResponse.id);
        
        if (status.status === 'completed') {
          await this.downloadExport(status);
          isCompleted = true;
        } else if (status.status === 'failed') {
          throw new Error(status.error || 'Export failed');
        }
      } catch (error) {
        console.error('Error checking export status:', error);
        throw error;
      }

      await new Promise(resolve => setTimeout(resolve, checkInterval));
    }
  }

  private async downloadExport(exportResponse: ExportAnalyticsResponse): Promise<void> {
    try {
      const blob = await this.api.downloadExport(exportResponse.id);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = exportResponse.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      this.notification.success(`Successfully downloaded ${exportResponse.filename}`);
    } catch (error) {
      console.error('Error downloading export:', error);
      this.notification.error('Failed to download export');
      throw error;
    }
  }
}

export const taxAnalyticsExportService = new TaxAnalyticsExportService();
