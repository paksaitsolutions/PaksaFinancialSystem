import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export interface CompanySettings {
  id?: number
  company_id?: number
  
  // Company Information
  company_name: string
  company_code?: string
  tax_id?: string
  registration_number?: string
  company_address?: string
  
  // Financial Settings
  base_currency: string
  fiscal_year_start: string
  decimal_places: number
  rounding_method: string
  multi_currency_enabled: boolean
  
  // Regional Settings
  timezone: string
  language: string
  date_format: string
  time_format: string
  number_format: string
  week_start: string
  
  // Document Settings
  invoice_prefix?: string
  invoice_start_number: number
  bill_prefix?: string
  payment_prefix?: string
  auto_numbering_enabled: boolean
  
  // System Preferences
  session_timeout: number
  default_page_size: number
  default_theme: string
  backup_frequency: string
  audit_trail_enabled: boolean
  email_notifications_enabled: boolean
  two_factor_auth_required: boolean
  auto_save_enabled: boolean
  
  // Integration Settings
  api_rate_limit: number
  webhook_timeout: number
  api_logging_enabled: boolean
  webhook_retry_enabled: boolean
}

export interface SettingsDefaults {
  currencies: Array<{ label: string; value: string }>
  timezones: Array<{ label: string; value: string }>
  languages: Array<{ label: string; value: string }>
  dateFormats: Array<{ label: string; value: string }>
  themes: Array<{ label: string; value: string }>
}

class SettingsService {
  private getAuthHeaders() {
    const token = localStorage.getItem('token') || sessionStorage.getItem('token')
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  }

  async getCompanySettings(companyId: number): Promise<CompanySettings> {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/v1/company/${companyId}/settings`,
        { headers: this.getAuthHeaders() }
      )
      return response.data
    } catch (error) {
      console.error('Error fetching company settings:', error)
      throw error
    }
  }

  async createCompanySettings(companyId: number, settings: Partial<CompanySettings>): Promise<CompanySettings> {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/v1/company/${companyId}/settings`,
        { ...settings, company_id: companyId },
        { headers: this.getAuthHeaders() }
      )
      return response.data
    } catch (error) {
      console.error('Error creating company settings:', error)
      throw error
    }
  }

  async updateCompanySettings(companyId: number, settings: Partial<CompanySettings>): Promise<CompanySettings> {
    try {
      const response = await axios.put(
        `${API_BASE_URL}/api/v1/company/${companyId}/settings`,
        settings,
        { headers: this.getAuthHeaders() }
      )
      return response.data
    } catch (error) {
      console.error('Error updating company settings:', error)
      throw error
    }
  }

  async deleteCompanySettings(companyId: number): Promise<void> {
    try {
      await axios.delete(
        `${API_BASE_URL}/api/v1/company/${companyId}/settings`,
        { headers: this.getAuthHeaders() }
      )
    } catch (error) {
      console.error('Error deleting company settings:', error)
      throw error
    }
  }

  async getSettingsDefaults(): Promise<SettingsDefaults> {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/v1/settings/defaults`,
        { headers: this.getAuthHeaders() }
      )
      return response.data
    } catch (error) {
      console.error('Error fetching settings defaults:', error)
      throw error
    }
  }

  // Validation helpers
  validateSettings(settings: Partial<CompanySettings>): string[] {
    const errors: string[] = []

    if (!settings.company_name || settings.company_name.trim().length === 0) {
      errors.push('Company name is required')
    }

    if (settings.company_name && settings.company_name.length > 255) {
      errors.push('Company name must be less than 255 characters')
    }

    if (settings.base_currency && !/^[A-Z]{3}$/.test(settings.base_currency)) {
      errors.push('Base currency must be a valid 3-letter currency code')
    }

    if (settings.decimal_places !== undefined && (settings.decimal_places < 0 || settings.decimal_places > 6)) {
      errors.push('Decimal places must be between 0 and 6')
    }

    if (settings.session_timeout !== undefined && (settings.session_timeout < 5 || settings.session_timeout > 480)) {
      errors.push('Session timeout must be between 5 and 480 minutes')
    }

    if (settings.default_page_size !== undefined && (settings.default_page_size < 10 || settings.default_page_size > 100)) {
      errors.push('Default page size must be between 10 and 100')
    }

    if (settings.api_rate_limit !== undefined && (settings.api_rate_limit < 10 || settings.api_rate_limit > 10000)) {
      errors.push('API rate limit must be between 10 and 10000 requests per minute')
    }

    if (settings.webhook_timeout !== undefined && (settings.webhook_timeout < 5 || settings.webhook_timeout > 300)) {
      errors.push('Webhook timeout must be between 5 and 300 seconds')
    }

    return errors
  }

  // Default settings factory
  getDefaultSettings(): CompanySettings {
    return {
      company_name: 'Paksa Financial System',
      company_code: 'PAKSA001',
      tax_id: '',
      registration_number: '',
      company_address: '',
      base_currency: 'USD',
      fiscal_year_start: 'January',
      decimal_places: 2,
      rounding_method: 'round',
      multi_currency_enabled: false,
      timezone: 'UTC',
      language: 'en',
      date_format: 'MM/DD/YYYY',
      time_format: '12',
      number_format: 'US',
      week_start: 'Sunday',
      invoice_prefix: 'INV-',
      invoice_start_number: 1000,
      bill_prefix: 'BILL-',
      payment_prefix: 'PAY-',
      auto_numbering_enabled: true,
      session_timeout: 60,
      default_page_size: 25,
      default_theme: 'light',
      backup_frequency: 'daily',
      audit_trail_enabled: true,
      email_notifications_enabled: true,
      two_factor_auth_required: false,
      auto_save_enabled: true,
      api_rate_limit: 1000,
      webhook_timeout: 30,
      api_logging_enabled: true,
      webhook_retry_enabled: true
    }
  }
}

export const settingsService = new SettingsService()
export default settingsService