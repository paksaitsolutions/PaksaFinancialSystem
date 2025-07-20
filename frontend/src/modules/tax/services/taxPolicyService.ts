import axios from 'axios';
import { authHeader } from '@/utils/auth';
import { TaxType, type TaxRule, type TaxJurisdiction, type TaxRate, type TaxExemption, type TaxCalculationRequest, type TaxCalculationResult, type TaxValidationRequest, type TaxValidationResponse, type PaginatedResponse } from '@/types/tax';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

class TaxPolicyService {
  private static instance: TaxPolicyService;
  
  private constructor() {}
  
  public static getInstance(): TaxPolicyService {
    if (!TaxPolicyService.instance) {
      TaxPolicyService.instance = new TaxPolicyService();
    }
    return TaxPolicyService.instance;
  }
  
  // Tax Calculation
  async calculateTax(calculationRequest: TaxCalculationRequest): Promise<TaxCalculationResult> {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/tax/calculate`,
        calculationRequest,
        { headers: authHeader() }
      );
      return response.data;
    } catch (error) {
      this.handleError(error, 'Error calculating tax');
      throw error;
    }
  }
  
  // Tax ID Validation
  async validateTaxId(validationRequest: TaxValidationRequest): Promise<TaxValidationResponse> {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/tax/validate`,
        validationRequest,
        { headers: authHeader() }
      );
      return response.data;
    } catch (error) {
      this.handleError(error, 'Error validating tax ID');
      throw error;
    }
  }
  
  // Tax Rules CRUD
  async getTaxRules(
    params: {
      taxType?: TaxType;
      countryCode?: string;
      stateCode?: string;
      city?: string;
      isActive?: boolean;
      category?: string;
      tags?: string[];
      page?: number;
      pageSize?: number;
    } = {}
  ): Promise<PaginatedResponse<TaxRule>> {
    try {
      const response = await axios.get(`${API_BASE_URL}/tax/rules`, {
        params,
        headers: authHeader()
      });
      return response.data;
    } catch (error) {
      this.handleError(error, 'Error fetching tax rules');
      throw error;
    }
  }
  
  async getTaxRule(ruleId: string): Promise<TaxRule> {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/tax/rules/${ruleId}`,
        { headers: authHeader() }
      );
      return response.data;
    } catch (error) {
      this.handleError(error, `Error fetching tax rule ${ruleId}`);
      throw error;
    }
  }
  
  async createTaxRule(ruleData: Omit<TaxRule, 'id' | 'createdAt' | 'updatedAt' | 'createdBy' | 'updatedBy'>): Promise<TaxRule> {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/tax/rules`,
        ruleData,
        { headers: authHeader() }
      );
      return response.data;
    } catch (error) {
      this.handleError(error, 'Error creating tax rule');
      throw error;
    }
  }
  
  async updateTaxRule(ruleId: string, ruleData: Partial<Omit<TaxRule, 'id' | 'createdAt' | 'updatedAt' | 'createdBy' | 'updatedBy'>>): Promise<TaxRule> {
    try {
      const response = await axios.put(
        `${API_BASE_URL}/tax/rules/${ruleId}`,
        ruleData,
        { headers: authHeader() }
      );
      return response.data;
    } catch (error) {
      this.handleError(error, `Error updating tax rule ${ruleId}`);
      throw error;
    }
  }
  
  async deleteTaxRule(ruleId: string): Promise<void> {
    try {
      await axios.delete(
        `${API_BASE_URL}/tax/rules/${ruleId}`,
        { headers: authHeader() }
      );
    } catch (error) {
      this.handleError(error, `Error deleting tax rule ${ruleId}`);
      throw error;
    }
  }
  
  // Tax Exemptions CRUD
  async getTaxExemptions(
    params: {
      search?: string;
      taxTypes?: string[];
      countryCode?: string;
      stateCode?: string;
      isActive?: boolean;
      page?: number;
      pageSize?: number;
      sortBy?: string;
      descending?: boolean;
    } = {}
  ): Promise<PaginatedResponse<TaxExemption>> {
    try {
      const response = await axios.get(`${API_BASE_URL}/tax/exemptions`, {
        params: {
          ...params,
          taxTypes: params.taxTypes?.join(','),
        },
        headers: authHeader()
      });
      return response.data;
    } catch (error) {
      this.handleError(error, 'Error fetching tax exemptions');
      throw error;
    }
  }

  async getTaxExemption(id: string): Promise<TaxExemption> {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/tax/exemptions/${id}`,
        { headers: authHeader() }
      );
      return response.data;
    } catch (error) {
      this.handleError(error, `Error fetching tax exemption ${id}`);
      throw error;
    }
  }

  async createTaxExemption(exemptionData: Omit<TaxExemption, 'id' | 'createdAt' | 'updatedAt' | 'createdBy' | 'updatedBy'>): Promise<TaxExemption> {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/tax/exemptions`,
        exemptionData,
        { headers: authHeader() }
      );
      return response.data;
    } catch (error) {
      this.handleError(error, 'Error creating tax exemption');
      throw error;
    }
  }

  async updateTaxExemption(id: string, exemptionData: Partial<Omit<TaxExemption, 'id' | 'createdAt' | 'updatedAt' | 'createdBy' | 'updatedBy'>>): Promise<TaxExemption> {
    try {
      const response = await axios.put(
        `${API_BASE_URL}/tax/exemptions/${id}`,
        exemptionData,
        { headers: authHeader() }
      );
      return response.data;
    } catch (error) {
      this.handleError(error, `Error updating tax exemption ${id}`);
      throw error;
    }
  }

  async deleteTaxExemption(id: string): Promise<void> {
    try {
      await axios.delete(
        `${API_BASE_URL}/tax/exemptions/${id}`,
        { headers: authHeader() }
      );
    } catch (error) {
      this.handleError(error, `Error deleting tax exemption ${id}`);
      throw error;
    }
  }

  async validateExemptionCode(code: string, id?: string): Promise<boolean> {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/tax/exemptions/validate-code`,
        {
          params: { code, id },
          headers: authHeader()
        }
      );
      return response.data.valid;
    } catch (error) {
      this.handleError(error, 'Error validating exemption code');
      throw error;
    }
  }
  
  // Helper methods
  private handleError(error: any, defaultMessage: string): void {
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.detail || error.message;
      console.error(`${defaultMessage}: ${message}`, error);
      throw new Error(message || defaultMessage);
    }
    console.error(defaultMessage, error);
    throw new Error(defaultMessage);
  }
  
  // Utility methods for tax calculations in the frontend
  calculateTaxAmount(amount: number, rate: number): number {
    return (amount * rate) / 100;
  }
  
  formatTaxRate(rate: number): string {
    return `${rate.toFixed(2)}%`;
  }
  
  // Get standard tax rates for a country/state
  async getStandardTaxRates(countryCode: string, stateCode?: string): Promise<TaxRate[]> {
    try {
      const response = await this.getTaxRules({
        countryCode,
        stateCode,
        isActive: true,
        tags: ['standard']
      });
      
      // Extract and flatten rates from matching rules
      return response.items.flatMap(rule => 
        rule.rates.map(rate => ({
          ...rate,
          ruleCode: rule.code,
          ruleName: rule.name
        }))
      );
    } catch (error) {
      console.error('Error fetching standard tax rates:', error);
      return [];
    }
  }
  
  // Get all available tax jurisdictions
  async getTaxJurisdictions(): Promise<TaxJurisdiction[]> {
    try {
      const response = await this.getTaxRules({ pageSize: 1000 });
      const jurisdictions = new Map<string, TaxJurisdiction>();
      
      // Extract unique jurisdictions
      response.items.forEach(rule => {
        const key = `${rule.jurisdiction.countryCode}-${rule.jurisdiction.stateCode || ''}`.toLowerCase();
        if (!jurisdictions.has(key)) {
          jurisdictions.set(key, rule.jurisdiction);
        }
      });
      
      return Array.from(jurisdictions.values());
    } catch (error) {
      console.error('Error fetching tax jurisdictions:', error);
      return [];
    }
  }
  
  // Get all available tax types
  async getTaxTypes(): Promise<{type: TaxType; name: string}[]> {
    return [
      { type: 'sales', name: 'Sales Tax' },
      { type: 'vat', name: 'VAT' },
      { type: 'gst', name: 'GST' },
      { type: 'income', name: 'Income Tax' },
      { type: 'withholding', name: 'Withholding Tax' },
      { type: 'excise', name: 'Excise Tax' },
      { type: 'custom', name: 'Custom Tax' }
    ];
  }
}

export const taxPolicyService = TaxPolicyService.getInstance();
