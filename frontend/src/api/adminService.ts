import { apiClient } from '@/utils/apiClient';

export interface PlatformAnalytics {
  total_companies: number;
  active_companies: number;
  pending_companies: number;
  suspended_companies: number;
  total_users: number;
  total_storage_gb: number;
  monthly_revenue: number;
  subscription_breakdown: Record<string, number>;
}

export interface SystemHealth {
  status: string;
  uptime: string;
  response_time_ms: number;
  error_rate: number;
  active_connections: number;
  memory_usage: number;
  cpu_usage: number;
  disk_usage: number;
}

export const adminService = {
  async getPlatformAnalytics(): Promise<PlatformAnalytics> {
    const response = await apiClient.get('/api/v1/super-admin/analytics');
    return response.data;
  },

  async getSystemHealth(): Promise<SystemHealth> {
    const response = await apiClient.get('/api/v1/super-admin/system-health');
    return response.data;
  }
};