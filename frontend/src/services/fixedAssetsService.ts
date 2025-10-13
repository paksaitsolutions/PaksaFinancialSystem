import { api } from '@/utils/api'

export interface FixedAsset {
  id: number
  asset_number: string
  asset_name: string
  description?: string
  asset_category: string
  location?: string
  purchase_date: string
  purchase_cost: number
  salvage_value: number
  useful_life_years: number
  depreciation_method: 'straight_line' | 'declining_balance' | 'units_of_production'
  accumulated_depreciation: number
  current_value: number
  status: 'active' | 'maintenance' | 'disposed' | 'sold'
  vendor_name?: string
  warranty_expiry?: string
  last_maintenance?: string
  next_maintenance?: string
  created_at: string
  updated_at: string
}

export interface AssetStats {
  total_assets: number
  total_cost: number
  total_accumulated_depreciation: number
  total_current_value: number
  monthly_depreciation: number
  maintenance_due: number
}

export interface MaintenanceRecord {
  id: number
  asset_id: number
  asset_name: string
  maintenance_type: 'preventive' | 'corrective' | 'emergency'
  description: string
  scheduled_date: string
  completed_date?: string
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled'
  estimated_cost?: number
  actual_cost?: number
  vendor_name?: string
  notes?: string
  created_by: string
  created_at: string
}

export interface AssetCategory {
  id: number
  name: string
  description?: string
  default_useful_life: number
  default_depreciation_method: string
  default_salvage_rate: number
  asset_count: number
}

export interface DepreciationEntry {
  id: number
  asset_id: number
  period_date: string
  depreciation_amount: number
  accumulated_depreciation: number
  book_value: number
  created_at: string
}

export interface AssetDisposal {
  id: number
  asset_id: number
  disposal_date: string
  disposal_method: 'sale' | 'scrap' | 'donation' | 'trade'
  disposal_amount: number
  disposal_reason: string
  gain_loss: number
  notes?: string
  created_by: string
  created_at: string
}

class FixedAssetsService {
  // Assets
  async getAssets(params?: {
    page?: number
    limit?: number
    search?: string
    category?: string
    status?: string
  }): Promise<{ assets: FixedAsset[], total: number }> {
    const response = await api.get('/api/v1/fixed-assets/assets', { params })
    return response.data
  }

  async getAsset(id: number): Promise<FixedAsset> {
    const response = await api.get(`/api/v1/fixed-assets/assets/${id}`)
    return response.data
  }

  async createAsset(asset: Omit<FixedAsset, 'id' | 'accumulated_depreciation' | 'current_value' | 'created_at' | 'updated_at'>): Promise<FixedAsset> {
    const response = await api.post('/api/v1/fixed-assets/assets', asset)
    return response.data
  }

  async updateAsset(id: number, asset: Partial<FixedAsset>): Promise<FixedAsset> {
    const response = await api.put(`/api/v1/fixed-assets/assets/${id}`, asset)
    return response.data
  }

  async deleteAsset(id: number): Promise<void> {
    await api.delete(`/api/v1/fixed-assets/assets/${id}`)
  }

  // Statistics
  async getAssetStats(): Promise<AssetStats> {
    const response = await api.get('/api/v1/fixed-assets/stats')
    return response.data
  }

  // Categories
  async getCategories(): Promise<{ name: string, value: string }[]> {
    const response = await api.get('/api/v1/fixed-assets/categories')
    return response.data.map((cat: AssetCategory) => ({
      name: cat.name,
      value: cat.name
    }))
  }

  async createCategory(category: Omit<AssetCategory, 'id' | 'asset_count'>): Promise<AssetCategory> {
    const response = await api.post('/api/v1/fixed-assets/categories', category)
    return response.data
  }

  async updateCategory(id: number, category: Partial<AssetCategory>): Promise<AssetCategory> {
    const response = await api.put(`/api/v1/fixed-assets/categories/${id}`, category)
    return response.data
  }

  async deleteCategory(id: number): Promise<void> {
    await api.delete(`/api/v1/fixed-assets/categories/${id}`)
  }

  // Maintenance
  async getMaintenanceRecords(assetId?: number): Promise<MaintenanceRecord[]> {
    const params = assetId ? { asset_id: assetId } : {}
    const response = await api.get('/api/v1/fixed-assets/maintenance', { params })
    return response.data
  }

  async createMaintenanceRecord(maintenance: Omit<MaintenanceRecord, 'id' | 'asset_name' | 'created_by' | 'created_at'>): Promise<MaintenanceRecord> {
    const response = await api.post('/api/v1/fixed-assets/maintenance', maintenance)
    return response.data
  }

  async updateMaintenanceRecord(id: number, maintenance: Partial<MaintenanceRecord>): Promise<MaintenanceRecord> {
    const response = await api.put(`/api/v1/fixed-assets/maintenance/${id}`, maintenance)
    return response.data
  }

  async getUpcomingMaintenance(days: number = 30): Promise<MaintenanceRecord[]> {
    const response = await api.get(`/api/v1/fixed-assets/maintenance/upcoming?days=${days}`)
    return response.data
  }

  // Depreciation
  async getDepreciationSchedule(assetId: number): Promise<DepreciationEntry[]> {
    const response = await api.get(`/fixed-assets/assets/${assetId}/depreciation`)
    return response.data
  }

  async calculateDepreciation(assetId: number, periodDate: string): Promise<DepreciationEntry> {
    const response = await api.post(`/fixed-assets/assets/${assetId}/depreciation`, {
      period_date: periodDate
    })
    return response.data
  }

  async runMonthlyDepreciation(): Promise<{ processed: number, total_amount: number }> {
    const response = await api.post('/fixed-assets/depreciation/run-monthly')
    return response.data
  }

  // Disposal
  async disposeAsset(id: number, disposal: {
    disposal_date: string
    disposal_method: string
    disposal_amount: number
    disposal_reason: string
    notes?: string
  }): Promise<AssetDisposal> {
    const response = await api.post(`/fixed-assets/assets/${id}/dispose`, disposal)
    return response.data
  }

  async getDisposalHistory(): Promise<AssetDisposal[]> {
    const response = await api.get('/fixed-assets/disposals')
    return response.data
  }

  // Reports
  async getAssetValuationReport(): Promise<{
    by_category: { category: string, count: number, cost: number, current_value: number }[]
    by_status: { status: string, count: number, value: number }[]
    total_cost: number
    total_current_value: number
    total_depreciation: number
  }> {
    const response = await api.get('/api/v1/fixed-assets/reports/valuation')
    return response.data
  }

  async getDepreciationReport(year: number): Promise<{
    monthly_depreciation: { month: string, amount: number }[]
    by_category: { category: string, amount: number }[]
    total_annual_depreciation: number
  }> {
    const response = await api.get(`/fixed-assets/reports/depreciation?year=${year}`)
    return response.data
  }

  async getMaintenanceReport(): Promise<{
    upcoming: MaintenanceRecord[]
    overdue: MaintenanceRecord[]
    completed_this_month: MaintenanceRecord[]
    total_maintenance_cost: number
  }> {
    const response = await api.get('/fixed-assets/reports/maintenance')
    return response.data
  }

  // Import/Export
  async importAssets(file: File): Promise<{ success: number, errors: string[] }> {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/fixed-assets/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  }

  async exportAssets(format: 'csv' | 'excel' = 'csv'): Promise<Blob> {
    const response = await api.get(`/fixed-assets/export?format=${format}`, {
      responseType: 'blob'
    })
    return response.data
  }
}

export const fixedAssetsService = new FixedAssetsService()