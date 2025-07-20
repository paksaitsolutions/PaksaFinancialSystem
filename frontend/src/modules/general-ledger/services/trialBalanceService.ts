import axios from 'axios';
import { TrialBalance, TrialBalanceParams } from '@/types/gl/trialBalance';
import { format } from 'date-fns';

const API_BASE_URL = '/api/v1/gl';

export const TrialBalanceService = {
  /**
   * Get trial balance data
   */
  async getTrialBalance(params: Omit<TrialBalanceParams, 'format'>): Promise<TrialBalance> {
    try {
      const response = await axios.get(`${API_BASE_URL}/reports/trial-balance`, {
        params: {
          start_date: format(new Date(params.startDate), 'yyyy-MM-dd'),
          end_date: format(new Date(params.endDate), 'yyyy-MM-dd'),
          include_zeros: params.includeZeros,
          format: 'json'
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching trial balance:', error);
      throw error;
    }
  },

  /**
   * Export trial balance to the specified format
   */
  async exportTrialBalance(params: TrialBalanceParams): Promise<void> {
    try {
      const response = await axios({
        url: `${API_BASE_URL}/reports/trial-balance`,
        method: 'GET',
        params: {
          start_date: format(new Date(params.startDate), 'yyyy-MM-dd'),
          end_date: format(new Date(params.endDate), 'yyyy-MM-dd'),
          include_zeros: params.includeZeros,
          format: params.format || 'excel'
        },
        responseType: 'blob',
      });

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      const fileName = `trial_balance_${params.startDate}_to_${params.endDate}.${params.format || 'xlsx'}`;
      
      link.href = url;
      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      
      // Clean up
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error exporting trial balance:', error);
      throw error;
    }
  }
};

export default TrialBalanceService;
