import { TaxAnalyticsRequest, TaxAnalyticsResponse, ExportAnalyticsRequest, ExportAnalyticsResponse } from '@/types/tax';
import { useApi } from '@/composables/useApi';

export class TaxAnalyticsApi {
  private api = useApi();

  async getTaxAnalytics(request: TaxAnalyticsRequest): Promise<TaxAnalyticsResponse> {
    try {
      const response = await this.api.post<TaxAnalyticsResponse>(
        '/api/tax/analytics',
        request
      );
      return response;
    } catch (error) {
      console.error('Error fetching tax analytics:', error);
      throw error;
    }
  }

  async exportAnalytics(request: ExportAnalyticsRequest): Promise<ExportAnalyticsResponse> {
    try {
      const response = await this.api.get<ExportAnalyticsResponse>(
        `/api/tax/analytics/export?period=${request.period}&format=${request.format}`
      );
      return response;
    } catch (error) {
      console.error('Error exporting tax analytics:', error);
      throw error;
    }
  }

  async getExportStatus(exportId: string): Promise<ExportAnalyticsResponse> {
    try {
      const response = await this.api.get<ExportAnalyticsResponse>(
        `/api/tax/analytics/export/status/${exportId}`
      );
      return response;
    } catch (error) {
      console.error('Error fetching export status:', error);
      throw error;
    }
  }

  async downloadExport(exportId: string): Promise<Blob> {
    try {
      const response = await this.api.get<Blob>(
        `/api/tax/analytics/export/download/${exportId}`,
        { responseType: 'blob' }
      );
      return response;
    } catch (error) {
      console.error('Error downloading export:', error);
      throw error;
    }
  }
}

export const taxAnalyticsApi = new TaxAnalyticsApi();
