import { TaxPeriod, TaxAnalyticsRequest } from '@/types/tax';
import { useTaxAnalyticsStore } from '@/modules/tax/store/analytics';
import { useNotification } from '@/composables/useNotification';

export class TaxAnalyticsConfigService {
  private store = useTaxAnalyticsStore();
  private notification = useNotification();

  getPeriodOptions(): { text: string; value: TaxPeriod }[] {
    return [
      { text: 'Current Month', value: TaxPeriod.CURRENT_MONTH },
      { text: 'Current Quarter', value: TaxPeriod.CURRENT_QUARTER },
      { text: 'Current Year', value: TaxPeriod.CURRENT_YEAR },
      { text: 'Custom Range', value: TaxPeriod.CUSTOM }
    ];
  }

  async fetchAnalytics(period: TaxPeriod): Promise<void> {
    try {
      this.store.selectedPeriod = period;
      await this.store.fetchAnalytics();
    } catch (error) {
      console.error('Error fetching tax analytics:', error);
      this.notification.error('Failed to fetch tax analytics');
      throw error;
    }
  }

  async refreshData(): Promise<void> {
    try {
      await this.store.refreshData();
      this.notification.success('Tax analytics data refreshed successfully');
    } catch (error) {
      console.error('Error refreshing tax analytics:', error);
      this.notification.error('Failed to refresh tax analytics');
      throw error;
    }
  }

  async exportAnalytics(format: 'csv' | 'excel' | 'pdf'): Promise<void> {
    try {
      const request: TaxAnalyticsRequest = {
        period: this.store.selectedPeriod,
        start_date: this.store.selectedPeriod === TaxPeriod.CUSTOM 
          ? this.store.customStartDate 
          : undefined,
        end_date: this.store.selectedPeriod === TaxPeriod.CUSTOM 
          ? this.store.customEndDate 
          : undefined
      };

      await this.store.exportAnalytics(format);
    } catch (error) {
      console.error('Error exporting tax analytics:', error);
      this.notification.error('Failed to export tax analytics');
      throw error;
    }
  }

  setCustomDateRange(startDate: Date, endDate: Date): void {
    this.store.customStartDate = startDate;
    this.store.customEndDate = endDate;
    this.store.selectedPeriod = TaxPeriod.CUSTOM;
  }

  validateCustomDateRange(startDate: Date, endDate: Date): boolean {
    if (!startDate || !endDate) {
      this.notification.error('Please select both start and end dates');
      return false;
    }

    if (startDate > endDate) {
      this.notification.error('Start date cannot be after end date');
      return false;
    }

    return true;
  }
}

export const taxAnalyticsConfigService = new TaxAnalyticsConfigService();
