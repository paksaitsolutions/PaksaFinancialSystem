import { apiClient } from '@/utils/apiClient'

export interface FixedAsset {
  id?: string
  asset_number: string
  asset_name: string
  asset_category?: string
  purchase_date: string
  purchase_cost: number
  salvage_value?: number
  useful_life_years?: number
  depreciation_method?: string
  location?: string
  status?: string
  accumulated_depreciation?: number
  current_value?: number
  created_at?: string
}

export interface AssetDepreciation {
  id?: string
  asset_id: string
  depreciation_date: string
  depreciation_amount: number
  accumulated_depreciation: number
  book_value: number
  notes?: string
  created_at?: string
}

export interface AssetMaintenance {
  id?: string
  asset_id: string
  maintenance_date: string
  maintenance_type?: string
  description?: string
  cost?: number
  vendor?: string
  next_maintenance_date?: string
  created_by?: string
  created_at?: string
}

export interface AssetStats {
  total_assets: number
  total_cost: number
  total_accumulated_depreciation: number
  total_current_value: number
  monthly_depreciation: number
  maintenance_due: number
}

export interface AssetDisposal {
  disposal_date: string
  disposal_amount: number
  disposal_reason: string
}

export interface AssetsListParams {
  skip?: number
  limit?: number
  category?: string
  status?: string
}

class FixedAssetsService {
  private baseUrl = '/api/v1/fixed-assets'

  // Assets
  async getAssets(params: AssetsListParams = {}) {
    const response = await apiClient.get(`${this.baseUrl}/assets`, { params })
    return response.data
  }

  async getAsset(id: string) {
    const response = await apiClient.get(`${this.baseUrl}/assets/${id}`)
    return response.data
  }

  async createAsset(asset: Omit<FixedAsset, 'id' | 'created_at' | 'current_value'>) {
    const response = await apiClient.post(`${this.baseUrl}/assets`, asset)
    return response.data
  }

  async updateAsset(id: string, asset: Partial<FixedAsset>) {
    const response = await apiClient.put(`${this.baseUrl}/assets/${id}`, asset)
    return response.data
  }

  async deleteAsset(id: string) {
    const response = await apiClient.delete(`${this.baseUrl}/assets/${id}`)
    return response.data
  }

  async disposeAsset(id: string, disposal: AssetDisposal) {
    const response = await apiClient.post(`${this.baseUrl}/assets/${id}/dispose`, disposal)
    return response.data
  }

  // Depreciation
  async getAssetDepreciation(assetId: string) {
    const response = await apiClient.get(`${this.baseUrl}/assets/${assetId}/depreciation`)
    return response.data
  }

  async createDepreciationEntry(assetId: string, depreciation: Omit<AssetDepreciation, 'id' | 'asset_id' | 'created_at'>) {
    const response = await apiClient.post(`${this.baseUrl}/assets/${assetId}/depreciation`, depreciation)
    return response.data
  }

  // Maintenance
  async getMaintenanceRecords(params: { asset_id?: string; upcoming_days?: number; skip?: number; limit?: number } = {}) {
    const response = await apiClient.get(`${this.baseUrl}/maintenance`, { params })
    return response.data
  }

  async createMaintenanceRecord(maintenance: Omit<AssetMaintenance, 'id' | 'created_by' | 'created_at'>) {
    const response = await apiClient.post(`${this.baseUrl}/maintenance`, maintenance)
    return response.data
  }

  async updateMaintenanceRecord(id: string, maintenance: Partial<AssetMaintenance>) {
    const response = await apiClient.put(`${this.baseUrl}/maintenance/${id}`, maintenance)
    return response.data
  }

  // Statistics
  async getAssetStats() {
    const response = await apiClient.get(`${this.baseUrl}/stats`)
    return response.data
  }

  // Categories
  async getCategories() {
    const response = await apiClient.get(`${this.baseUrl}/categories`)
    return response.data
  }
}

export const fixedAssetsService = new FixedAssetsService()
export default fixedAssetsService