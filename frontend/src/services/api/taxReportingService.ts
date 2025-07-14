import { TaxPolicy, TaxRate, TaxExemption, TaxCalculationRequest, TaxCalculationResponse } from '@/types/tax';
import { apiClient } from '@/utils/apiClient';

class TaxReportingService {
  private baseUrl = '/api/v1/tax';

  async getCurrentPolicy(): Promise<TaxPolicy> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/policy/current`);
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch tax policy');
    }
  }

  async updatePolicy(policy: Partial<TaxPolicy>): Promise<TaxPolicy> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/policy`, policy);
      return response.data;
    } catch (error) {
      throw new Error('Failed to update tax policy');
    }
  }

  async addTaxRate(rate: TaxRate): Promise<TaxRate> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/rates`, rate);
      return response.data;
    } catch (error) {
      throw new Error('Failed to add tax rate');
    }
  }

  async updateTaxRate(rateId: string, updates: Partial<TaxRate>): Promise<TaxRate> {
    try {
      const response = await apiClient.put(`${this.baseUrl}/rates/${rateId}`, updates);
      return response.data;
    } catch (error) {
      throw new Error('Failed to update tax rate');
    }
  }

  async removeTaxRate(rateId: string): Promise<void> {
    try {
      await apiClient.delete(`${this.baseUrl}/rates/${rateId}`);
    } catch (error) {
      throw new Error('Failed to remove tax rate');
    }
  }

  async addTaxExemption(exemption: TaxExemption): Promise<TaxExemption> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/exemptions`, exemption);
      return response.data;
    } catch (error) {
      throw new Error('Failed to add tax exemption');
    }
  }

  async updateTaxExemption(exemptionId: string, updates: Partial<TaxExemption>): Promise<TaxExemption> {
    try {
      const response = await apiClient.put(`${this.baseUrl}/exemptions/${exemptionId}`, updates);
      return response.data;
    } catch (error) {
      throw new Error('Failed to update tax exemption');
    }
  }

  async removeTaxExemption(exemptionId: string): Promise<void> {
    try {
      await apiClient.delete(`${this.baseUrl}/exemptions/${exemptionId}`);
    } catch (error) {
      throw new Error('Failed to remove tax exemption');
    }
  }

  async calculateTaxes(request: TaxCalculationRequest): Promise<TaxCalculationResponse> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/calculate`, request);
      return response.data;
    } catch (error) {
      throw new Error('Failed to calculate taxes');
    }
  }
}

export const taxReportingService = new TaxReportingService();