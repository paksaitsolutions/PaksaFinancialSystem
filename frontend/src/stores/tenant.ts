import { defineStore } from 'pinia'
import axios from 'axios'

export interface Company {
  id: number
  tenant_id: string
  name: string
  email: string
  logo?: string
  theme?: {
    primary: string
    secondary: string
    accent: string
  }
  features: string[]
  subscription_plan: string
  status: string
}

export const useTenantStore = defineStore('tenant', {
  state: () => ({
    currentCompany: null as Company | null,
    availableCompanies: [] as Company[],
    loading: false,
    error: null as string | null
  }),

  getters: {
    isLoggedIn: (state) => !!state.currentCompany,
    tenantId: (state) => state.currentCompany?.tenant_id,
    companyName: (state) => state.currentCompany?.name,
    hasFeature: (state) => (feature: string) => 
      state.currentCompany?.features.includes(feature) || false,
    theme: (state) => state.currentCompany?.theme || {
      primary: '#1976D2',
      secondary: '#424242',
      accent: '#82B1FF'
    }
  },

  actions: {
    async fetchAvailableCompanies() {
      try {
        this.loading = true
        const response = await axios.get('/api/v1/companies/available')
        this.availableCompanies = response.data
      } catch (error) {
        this.error = 'Failed to fetch companies'
        throw error
      } finally {
        this.loading = false
      }
    },

    async selectCompany(companyId: number) {
      const company = this.availableCompanies.find(c => c.id === companyId)
      if (!company) throw new Error('Company not found')

      this.currentCompany = company
      
      // Set tenant header for all future requests
      axios.defaults.headers.common['X-Tenant-ID'] = company.tenant_id
      
      // Store in localStorage
      localStorage.setItem('currentCompany', JSON.stringify(company))
      
      // Apply theme
      this.applyTheme(company.theme)
    },

    async switchCompany(companyId: number) {
      await this.selectCompany(companyId)
      // Reload the page to refresh all data
      window.location.reload()
    },

    applyTheme(theme?: { primary: string; secondary: string; accent: string }) {
      if (!theme) return
      
      const root = document.documentElement
      root.style.setProperty('--v-theme-primary', theme.primary)
      root.style.setProperty('--v-theme-secondary', theme.secondary)
      root.style.setProperty('--v-theme-accent', theme.accent)
    },

    loadFromStorage() {
      const stored = localStorage.getItem('currentCompany')
      if (stored) {
        this.currentCompany = JSON.parse(stored)
        if (this.currentCompany) {
          axios.defaults.headers.common['X-Tenant-ID'] = this.currentCompany.tenant_id
          this.applyTheme(this.currentCompany.theme)
        }
      }
    },

    logout() {
      this.currentCompany = null
      this.availableCompanies = []
      localStorage.removeItem('currentCompany')
      delete axios.defaults.headers.common['X-Tenant-ID']
    }
  }
})