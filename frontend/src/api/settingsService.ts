import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api/v1'

export interface CompanySettings {
  id?: number
  company_name: string
  company_code?: string
  tax_id?: string
  registration_number?: string
  company_address?: string
  base_currency: string
  fiscal_year_start: string
  decimal_places: number
  rounding_method: string
  multi_currency_enabled: boolean
  timezone: string
  language: string
  date_format: string
  time_format: string
  number_format: string
  week_start: string
  invoice_prefix: string
  invoice_start_number: number
  bill_prefix: string
  payment_prefix: string
  auto_numbering_enabled: boolean
  session_timeout: number
  default_page_size: number
  default_theme: string
  backup_frequency: string
  audit_trail_enabled: boolean
  email_notifications_enabled: boolean
  two_factor_auth_required: boolean
  auto_save_enabled: boolean
  api_rate_limit: number
  webhook_timeout: number
  api_logging_enabled: boolean
  webhook_retry_enabled: boolean
  created_at?: string
  updated_at?: string
}

export interface UserSetting {
  id?: number
  user_id: string
  setting_key: string
  setting_value?: string
  created_at?: string
  updated_at?: string
}

export interface SystemSetting {
  id?: number
  setting_key: string
  setting_value?: string
  description?: string
  is_encrypted: boolean
  created_at?: string
  updated_at?: string
}

class SettingsService {
  // Company Settings
  async getCompanySettings(companyId: number): Promise<CompanySettings> {
    const response = await axios.get(`${API_BASE_URL}/settings/company/${companyId}`)
    return response.data
  }

  async updateCompanySettings(companyId: number, settings: Partial<CompanySettings>): Promise<CompanySettings> {
    const response = await axios.put(`${API_BASE_URL}/settings/company/${companyId}`, settings)
    return response.data
  }

  async createCompanySettings(settings: Omit<CompanySettings, 'id' | 'created_at' | 'updated_at'>): Promise<CompanySettings> {
    const response = await axios.post(`${API_BASE_URL}/settings/company`, settings)
    return response.data
  }

  // User Settings
  async getUserSettings(userId: string): Promise<UserSetting[]> {
    const response = await axios.get(`${API_BASE_URL}/settings/user/${userId}`)
    return response.data
  }

  async getUserSetting(userId: string, settingKey: string): Promise<UserSetting> {
    const response = await axios.get(`${API_BASE_URL}/settings/user/${userId}/${settingKey}`)
    return response.data
  }

  async updateUserSetting(userId: string, settingKey: string, settingValue: string): Promise<UserSetting> {
    const response = await axios.put(`${API_BASE_URL}/settings/user/${userId}/${settingKey}`, null, {
      params: { setting_value: settingValue }
    })
    return response.data
  }

  async deleteUserSetting(userId: string, settingKey: string): Promise<void> {
    await axios.delete(`${API_BASE_URL}/settings/user/${userId}/${settingKey}`)
  }

  // System Settings
  async getSystemSettings(): Promise<SystemSetting[]> {
    const response = await axios.get(`${API_BASE_URL}/settings/system`)
    return response.data
  }

  async getSystemSetting(settingKey: string): Promise<SystemSetting> {
    const response = await axios.get(`${API_BASE_URL}/settings/system/${settingKey}`)
    return response.data
  }

  async updateSystemSetting(settingKey: string, settingValue: string, description?: string): Promise<SystemSetting> {
    const response = await axios.put(`${API_BASE_URL}/settings/system/${settingKey}`, null, {
      params: { setting_value: settingValue, description }
    })
    return response.data
  }

  async deleteSystemSetting(settingKey: string): Promise<void> {
    await axios.delete(`${API_BASE_URL}/settings/system/${settingKey}`)
  }

  // Validation
  async validateSettings(settings: Record<string, any>): Promise<{ valid: boolean; errors: string[] }> {
    const response = await axios.post(`${API_BASE_URL}/settings/validate`, settings)
    return response.data
  }

  // Client-side validation helper
  validateSettings(settings: Record<string, any>): string[] {
    const errors: string[] = []

    if ('company_name' in settings && !settings.company_name) {
      errors.push('Company name is required')
    }

    if ('base_currency' in settings && !settings.base_currency) {
      errors.push('Base currency is required')
    }

    if ('decimal_places' in settings) {
      const decimalPlaces = settings.decimal_places
      if (typeof decimalPlaces !== 'number' || decimalPlaces < 0 || decimalPlaces > 6) {
        errors.push('Decimal places must be between 0 and 6')
      }
    }

    if ('session_timeout' in settings) {
      const sessionTimeout = settings.session_timeout
      if (typeof sessionTimeout !== 'number' || sessionTimeout < 5 || sessionTimeout > 480) {
        errors.push('Session timeout must be between 5 and 480 minutes')
      }
    }

    if ('default_page_size' in settings) {
      const pageSize = settings.default_page_size
      if (typeof pageSize !== 'number' || pageSize < 1 || pageSize > 1000) {
        errors.push('Default page size must be between 1 and 1000')
      }
    }

    if ('api_rate_limit' in settings) {
      const rateLimit = settings.api_rate_limit
      if (typeof rateLimit !== 'number' || rateLimit < 10 || rateLimit > 10000) {
        errors.push('API rate limit must be between 10 and 10000')
      }
    }

    if ('webhook_timeout' in settings) {
      const timeout = settings.webhook_timeout
      if (typeof timeout !== 'number' || timeout < 5 || timeout > 300) {
        errors.push('Webhook timeout must be between 5 and 300 seconds')
      }
    }

    return errors
  }
}

export default new SettingsService()