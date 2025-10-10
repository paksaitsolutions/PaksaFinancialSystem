import { api } from '@/utils/api'

export interface APStats {
  totalPayable: string
  overdueBills: number
  activeVendors: number
  monthlyPayments: string
}

export interface RecentBill {
  vendor: string
  billNumber: string
  dueDate: string
  amount: string
  status: string
}

export const apService = {
  async getDashboardStats(): Promise<APStats> {
    const response = await api.get('/ap/dashboard/stats')
    return response.data
  },

  async getRecentBills(): Promise<RecentBill[]> {
    const response = await api.get('/ap/dashboard/recent-bills')
    return response.data
  }
}