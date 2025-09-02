import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export interface TenantCompany {
  id?: number
  name: string
  code: string
  industry?: string
  size?: string
  address?: string
  domain?: string
  subdomain: string
  logo_url?: string
  primary_color?: string
  secondary_color?: string
  plan: string
  max_users: number
  current_users?: number
  storage_limit_gb: number
  api_rate_limit: number
  timezone: string
  language: string
  currency: string
  date_format: string
  enabled_modules?: string[]
  feature_flags?: Record<string, boolean>
  custom_settings?: Record<string, any>
  status?: string
  is_active?: boolean
  trial_ends_at?: string
  subscription_ends_at?: string
  created_at?: string
  updated_at?: string
  users_percentage?: number
}

export interface CompanyRegistration extends TenantCompany {
  admin_name: string
  admin_email: string
  admin_password: string
  admin_phone?: string
  trial_days?: number
}

export interface CompanyStats {
  total_companies: number
  active_companies: number
  trial_companies: number
  suspended_companies: number
  total_users: number
  companies_by_plan: Record<string, number>
  companies_by_status: Record<string, number>
}

export interface CompanyActivationResponse {
  success: boolean
  message: string
  company: TenantCompany
  access_token?: string
}

class TenantService {
  private getAuthHeaders() {
    const token = localStorage.getItem('token') || sessionStorage.getItem('token')
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  }

  async getCompanies(params?: {
    skip?: number
    limit?: number
    status?: string
    plan?: string
    search?: string
  }): Promise<TenantCompany[]> {
    try {
      const queryParams = new URLSearchParams()
      if (params?.skip) queryParams.append('skip', params.skip.toString())
      if (params?.limit) queryParams.append('limit', params.limit.toString())
      if (params?.status) queryParams.append('status', params.status)
      if (params?.plan) queryParams.append('plan', params.plan)
      if (params?.search) queryParams.append('search', params.search)

      const response = await axios.get(
        `${API_BASE_URL}/api/v1/companies?${queryParams.toString()}`,
        { headers: this.getAuthHeaders() }
      )
      return response.data
    } catch (error) {
      console.error('Error fetching companies:', error)
      throw error
    }
  }

  async getCompany(companyId: number): Promise<TenantCompany> {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/v1/companies/${companyId}`,
        { headers: this.getAuthHeaders() }
      )
      return response.data
    } catch (error) {
      console.error('Error fetching company:', error)
      throw error
    }
  }

  async registerCompany(companyData: CompanyRegistration): Promise<TenantCompany> {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/v1/companies`,
        companyData,
        { headers: this.getAuthHeaders() }
      )
      return response.data
    } catch (error) {
      console.error('Error registering company:', error)
      throw error
    }
  }

  async updateCompany(companyId: number, companyData: Partial<TenantCompany>): Promise<TenantCompany> {
    try {
      const response = await axios.put(
        `${API_BASE_URL}/api/v1/companies/${companyId}`,
        companyData,
        { headers: this.getAuthHeaders() }
      )
      return response.data
    } catch (error) {
      console.error('Error updating company:', error)
      throw error
    }
  }

  async activateCompany(companyId: number): Promise<CompanyActivationResponse> {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/v1/companies/${companyId}/activate`,
        {},
        { headers: this.getAuthHeaders() }
      )
      
      // Update token if provided
      if (response.data.access_token) {
        const currentStorage = localStorage.getItem('token') ? localStorage : sessionStorage
        currentStorage.setItem('token', response.data.access_token)
      }
      
      return response.data
    } catch (error) {
      console.error('Error activating company:', error)
      throw error
    }
  }

  async deleteCompany(companyId: number): Promise<void> {
    try {
      await axios.delete(
        `${API_BASE_URL}/api/v1/companies/${companyId}`,
        { headers: this.getAuthHeaders() }
      )
    } catch (error) {
      console.error('Error deleting company:', error)
      throw error
    }
  }

  async getCompanyStats(): Promise<CompanyStats> {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/v1/companies/stats`,
        { headers: this.getAuthHeaders() }
      )
      return response.data
    } catch (error) {
      console.error('Error fetching company stats:', error)
      throw error
    }
  }

  async uploadCompanyLogo(companyId: number, file: File): Promise<{ message: string; logo_url: string }> {
    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await axios.post(
        `${API_BASE_URL}/api/v1/companies/${companyId}/logo`,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token') || sessionStorage.getItem('token')}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      )
      return response.data
    } catch (error) {
      console.error('Error uploading logo:', error)
      throw error
    }
  }

  async getCompanyModules(companyId: number): Promise<any[]> {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/v1/companies/${companyId}/modules`,
        { headers: this.getAuthHeaders() }
      )
      return response.data
    } catch (error) {
      console.error('Error fetching company modules:', error)
      throw error
    }
  }

  // Validation helpers
  validateCompanyRegistration(data: CompanyRegistration): string[] {
    const errors: string[] = []

    if (!data.name || data.name.trim().length === 0) {
      errors.push('Company name is required')
    }

    if (!data.code || data.code.trim().length === 0) {
      errors.push('Company code is required')
    }

    if (!data.subdomain || data.subdomain.trim().length === 0) {
      errors.push('Subdomain is required')
    }

    if (!data.plan) {
      errors.push('Subscription plan is required')
    }

    if (!data.admin_name || data.admin_name.trim().length === 0) {
      errors.push('Administrator name is required')
    }

    if (!data.admin_email || data.admin_email.trim().length === 0) {
      errors.push('Administrator email is required')
    }

    if (!data.admin_password || data.admin_password.length < 8) {
      errors.push('Administrator password must be at least 8 characters')
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (data.admin_email && !emailRegex.test(data.admin_email)) {
      errors.push('Invalid email format')
    }

    // Validate subdomain format
    const subdomainRegex = /^[a-z0-9-]+$/
    if (data.subdomain && !subdomainRegex.test(data.subdomain)) {
      errors.push('Subdomain can only contain lowercase letters, numbers, and hyphens')
    }

    // Validate company code format
    const codeRegex = /^[A-Z0-9_-]+$/
    if (data.code && !codeRegex.test(data.code.toUpperCase())) {
      errors.push('Company code can only contain uppercase letters, numbers, underscores, and hyphens')
    }

    return errors
  }

  // Utility methods
  generateSubdomain(companyName: string): string {
    return companyName
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '')
      .substring(0, 20)
  }

  generateCompanyCode(companyName: string): string {
    const words = companyName.toUpperCase().split(/\s+/)
    if (words.length === 1) {
      return words[0].substring(0, 6) + '001'
    }
    
    const initials = words.map(word => word.charAt(0)).join('')
    return initials.substring(0, 4) + '001'
  }

  getPlanFeatures(plan: string): string[] {
    const features: Record<string, string[]> = {
      'Basic': [
        'Up to 10 users',
        '5GB storage',
        'Basic modules (GL, AP, AR)',
        'Email support',
        'Standard reports'
      ],
      'Professional': [
        'Up to 50 users',
        '25GB storage',
        'All basic modules + Payroll, Inventory',
        'Priority support',
        'Advanced reports',
        'API access'
      ],
      'Enterprise': [
        'Up to 200 users',
        '100GB storage',
        'All modules included',
        '24/7 phone support',
        'Custom reports',
        'Advanced API access',
        'Custom integrations'
      ],
      'Custom': [
        'Unlimited users',
        'Custom storage',
        'All modules + custom development',
        'Dedicated support',
        'White-label options',
        'On-premise deployment'
      ]
    }

    return features[plan] || []
  }

  getPlanPrice(plan: string): { monthly: number; yearly: number } {
    const prices: Record<string, { monthly: number; yearly: number }> = {
      'Basic': { monthly: 29, yearly: 290 },
      'Professional': { monthly: 79, yearly: 790 },
      'Enterprise': { monthly: 199, yearly: 1990 },
      'Custom': { monthly: 0, yearly: 0 } // Contact sales
    }

    return prices[plan] || { monthly: 0, yearly: 0 }
  }

  // Company branding helpers
  applyCompanyBranding(company: TenantCompany): void {
    // Apply primary color to CSS variables
    if (company.primary_color) {
      document.documentElement.style.setProperty('--primary-color', company.primary_color)
    }

    // Update page title
    document.title = `${company.name} - Financial System`

    // Update favicon if company has logo
    if (company.logo_url) {
      const favicon = document.querySelector('link[rel="icon"]') as HTMLLinkElement
      if (favicon) {
        favicon.href = company.logo_url
      }
    }

    // Store company context in localStorage for persistence
    localStorage.setItem('activeCompany', JSON.stringify({
      id: company.id,
      name: company.name,
      code: company.code,
      logo_url: company.logo_url,
      primary_color: company.primary_color,
      secondary_color: company.secondary_color
    }))
  }

  getStoredCompanyContext(): Partial<TenantCompany> | null {
    try {
      const stored = localStorage.getItem('activeCompany')
      return stored ? JSON.parse(stored) : null
    } catch {
      return null
    }
  }

  clearCompanyContext(): void {
    localStorage.removeItem('activeCompany')
    
    // Reset to default branding
    document.documentElement.style.setProperty('--primary-color', '#1976D2')
    document.title = 'Paksa Financial System'
  }
}

export const tenantService = new TenantService()
export default tenantService