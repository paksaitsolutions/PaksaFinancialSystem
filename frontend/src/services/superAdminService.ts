import { apiClient } from '@/utils/apiClient'

export interface SystemOverview {
  total_tenants: number
  active_users: number
  system_health: string
  database_size: string
  uptime: string
  last_backup: string
}

export interface Tenant {
  id: number
  name: string
  status: string
  users: number
  created: string
}

export interface SystemUser {
  id: number
  email: string
  role: string
  status: string
  last_login: string
}

export interface AuditLog {
  id: number
  user: string
  action: string
  timestamp: string
  ip: string
}

export interface GlobalSettings {
  maintenance_mode: boolean
  registration_enabled: boolean
  max_tenants: number
  backup_frequency: string
  session_timeout: number
}

class SuperAdminService {
  private baseUrl = '/api/v1/super-admin'

  async getSystemOverview(): Promise<SystemOverview> {
    const response = await apiClient.get(`${this.baseUrl}/system-overview`)
    return response.data
  }

  async getAllTenants(): Promise<Tenant[]> {
    const response = await apiClient.get(`${this.baseUrl}/tenants`)
    return response.data
  }

  async getAllUsers(): Promise<SystemUser[]> {
    const response = await apiClient.get(`${this.baseUrl}/users`)
    return response.data
  }

  async getAuditLogs(): Promise<AuditLog[]> {
    const response = await apiClient.get(`${this.baseUrl}/audit-logs`)
    return response.data
  }

  async createBackup(): Promise<{ success: boolean; backup_id: string; message: string }> {
    const response = await apiClient.post(`${this.baseUrl}/backup`)
    return response.data
  }

  async getGlobalSettings(): Promise<GlobalSettings> {
    const response = await apiClient.get(`${this.baseUrl}/settings`)
    return response.data
  }

  async updateGlobalSettings(settings: Partial<GlobalSettings>): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.put(`${this.baseUrl}/settings`, settings)
    return response.data
  }
}

export default new SuperAdminService()