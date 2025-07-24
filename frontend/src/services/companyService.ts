import { api } from '@/utils/api';

export interface Company {
  id: string;
  company_name: string;
  company_code: string;
  email: string;
  phone?: string;
  website?: string;
  industry?: string;
  business_type?: string;
  tax_id?: string;
  registration_number?: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  logo_url?: string;
  primary_color?: string;
  secondary_color?: string;
  default_currency: string;
  default_language: string;
  timezone: string;
  date_format: string;
  fiscal_year_start: string;
  tax_settings?: Record<string, any>;
  enabled_modules?: Record<string, boolean>;
  numbering_formats?: Record<string, string>;
  subscription_tier: string;
  status: string;
  trial_ends_at?: string;
  database_schema?: string;
  created_at: string;
  updated_at: string;
}

export interface CompanyRegistrationRequest {
  company_name: string;
  email: string;
  phone?: string;
  website?: string;
  industry?: string;
  business_type?: string;
  tax_id?: string;
  registration_number?: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  default_currency?: string;
  default_language?: string;
  timezone?: string;
  fiscal_year_start?: string;
}

export interface CompanyUser {
  id: string;
  company_id: string;
  user_id: string;
  role: string;
  is_admin: boolean;
  is_active: boolean;
  permissions?: Record<string, any>;
  created_at: string;
}

export interface CompanySettings {
  id: string;
  company_id: string;
  chart_of_accounts_template?: string;
  approval_workflows?: Record<string, any>;
  integrations?: Record<string, any>;
  custom_fields?: Record<string, any>;
  notification_settings?: Record<string, any>;
  security_settings?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

/**
 * Company Service
 * Provides methods to interact with the company management API endpoints
 */
export default {
  /**
   * Register a new company
   * @param companyData - Company registration data
   * @returns Promise with the registered company
   */
  async registerCompany(companyData: CompanyRegistrationRequest) {
    return api.post('/company/register', companyData);
  },

  /**
   * Get company by ID
   * @param companyId - Company ID
   * @returns Promise with company details
   */
  async getCompany(companyId: string) {
    return api.get(`/company/${companyId}`);
  },

  /**
   * Update company information
   * @param companyId - Company ID
   * @param companyData - Updated company data
   * @returns Promise with updated company
   */
  async updateCompany(companyId: string, companyData: Partial<Company>) {
    return api.put(`/company/${companyId}`, companyData);
  },

  /**
   * List companies
   * @param status - Optional status filter
   * @param limit - Maximum number of records
   * @returns Promise with list of companies
   */
  async listCompanies(status?: string, limit: number = 100) {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    params.append('limit', limit.toString());

    return api.get(`/company/?${params.toString()}`);
  },

  /**
   * Add user to company
   * @param companyId - Company ID
   * @param userData - User data
   * @returns Promise with company user
   */
  async addUserToCompany(companyId: string, userData: {
    user_id: string;
    role?: string;
    is_admin?: boolean;
    permissions?: Record<string, any>;
  }) {
    return api.post(`/company/${companyId}/users`, userData);
  },

  /**
   * Get company users
   * @param companyId - Company ID
   * @param activeOnly - Show only active users
   * @returns Promise with list of company users
   */
  async getCompanyUsers(companyId: string, activeOnly: boolean = true) {
    return api.get(`/company/${companyId}/users?active_only=${activeOnly}`);
  },

  /**
   * Get user companies
   * @param userId - User ID
   * @param activeOnly - Show only active companies
   * @returns Promise with list of user companies
   */
  async getUserCompanies(userId: string, activeOnly: boolean = true) {
    return api.get(`/company/user/${userId}/companies?active_only=${activeOnly}`);
  },

  /**
   * Update company settings
   * @param companyId - Company ID
   * @param settings - Settings data
   * @returns Promise with updated settings
   */
  async updateCompanySettings(companyId: string, settings: Partial<CompanySettings>) {
    return api.put(`/company/${companyId}/settings`, settings);
  },

  /**
   * Get company settings
   * @param companyId - Company ID
   * @returns Promise with company settings
   */
  async getCompanySettings(companyId: string) {
    return api.get(`/company/${companyId}/settings`);
  },

  /**
   * Utility functions for company operations
   */
  utils: {
    /**
     * Format company status for display
     */
    formatStatus(status: string): string {
      const statusMap: Record<string, string> = {
        'active': 'Active',
        'inactive': 'Inactive',
        'suspended': 'Suspended',
        'trial': 'Trial'
      };
      
      return statusMap[status] || status.charAt(0).toUpperCase() + status.slice(1);
    },

    /**
     * Get status color for UI
     */
    getStatusColor(status: string): string {
      const colorMap: Record<string, string> = {
        'active': 'success',
        'inactive': 'warning',
        'suspended': 'error',
        'trial': 'info'
      };
      
      return colorMap[status] || 'grey';
    },

    /**
     * Format subscription tier
     */
    formatSubscriptionTier(tier: string): string {
      const tierMap: Record<string, string> = {
        'basic': 'Basic',
        'professional': 'Professional',
        'enterprise': 'Enterprise'
      };
      
      return tierMap[tier] || tier.charAt(0).toUpperCase() + tier.slice(1);
    },

    /**
     * Get available industries
     */
    getIndustries(): string[] {
      return [
        'Technology',
        'Healthcare',
        'Finance',
        'Manufacturing',
        'Retail',
        'Education',
        'Real Estate',
        'Construction',
        'Transportation',
        'Hospitality',
        'Professional Services',
        'Non-profit',
        'Government',
        'Other'
      ];
    },

    /**
     * Get available business types
     */
    getBusinessTypes(): string[] {
      return [
        'Corporation',
        'LLC',
        'Partnership',
        'Sole Proprietorship',
        'Non-profit',
        'Government',
        'Other'
      ];
    },

    /**
     * Get available currencies
     */
    getCurrencies(): Array<{ code: string; name: string; symbol: string }> {
      return [
        { code: 'USD', name: 'US Dollar', symbol: '$' },
        { code: 'EUR', name: 'Euro', symbol: '€' },
        { code: 'GBP', name: 'British Pound', symbol: '£' },
        { code: 'CAD', name: 'Canadian Dollar', symbol: 'C$' },
        { code: 'AUD', name: 'Australian Dollar', symbol: 'A$' },
        { code: 'JPY', name: 'Japanese Yen', symbol: '¥' },
        { code: 'CHF', name: 'Swiss Franc', symbol: 'CHF' },
        { code: 'CNY', name: 'Chinese Yuan', symbol: '¥' }
      ];
    },

    /**
     * Get available timezones
     */
    getTimezones(): Array<{ value: string; label: string }> {
      return [
        { value: 'UTC', label: 'UTC' },
        { value: 'America/New_York', label: 'Eastern Time (US)' },
        { value: 'America/Chicago', label: 'Central Time (US)' },
        { value: 'America/Denver', label: 'Mountain Time (US)' },
        { value: 'America/Los_Angeles', label: 'Pacific Time (US)' },
        { value: 'Europe/London', label: 'London' },
        { value: 'Europe/Paris', label: 'Paris' },
        { value: 'Europe/Berlin', label: 'Berlin' },
        { value: 'Asia/Tokyo', label: 'Tokyo' },
        { value: 'Asia/Shanghai', label: 'Shanghai' },
        { value: 'Australia/Sydney', label: 'Sydney' }
      ];
    },

    /**
     * Get available languages
     */
    getLanguages(): Array<{ code: string; name: string }> {
      return [
        { code: 'en-US', name: 'English (US)' },
        { code: 'en-GB', name: 'English (UK)' },
        { code: 'es-ES', name: 'Spanish' },
        { code: 'fr-FR', name: 'French' },
        { code: 'de-DE', name: 'German' },
        { code: 'it-IT', name: 'Italian' },
        { code: 'pt-BR', name: 'Portuguese (Brazil)' },
        { code: 'ja-JP', name: 'Japanese' },
        { code: 'zh-CN', name: 'Chinese (Simplified)' }
      ];
    },

    /**
     * Validate company code format
     */
    validateCompanyCode(code: string): { valid: boolean; message?: string } {
      if (!code) {
        return { valid: false, message: 'Company code is required' };
      }
      
      if (code.length < 3 || code.length > 10) {
        return { valid: false, message: 'Company code must be 3-10 characters' };
      }
      
      if (!/^[A-Z0-9]+$/.test(code)) {
        return { valid: false, message: 'Company code must contain only uppercase letters and numbers' };
      }
      
      return { valid: true };
    },

    /**
     * Check if company is in trial
     */
    isTrialCompany(company: Company): boolean {
      return company.status === 'trial';
    },

    /**
     * Get trial days remaining
     */
    getTrialDaysRemaining(company: Company): number {
      if (!company.trial_ends_at) return 0;
      
      const trialEnd = new Date(company.trial_ends_at);
      const now = new Date();
      const diffTime = trialEnd.getTime() - now.getTime();
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      return Math.max(0, diffDays);
    },

    /**
     * Format address
     */
    formatAddress(company: Company): string {
      const parts = [
        company.address_line1,
        company.address_line2,
        company.city,
        company.state,
        company.postal_code,
        company.country
      ].filter(Boolean);
      
      return parts.join(', ');
    }
  }
};