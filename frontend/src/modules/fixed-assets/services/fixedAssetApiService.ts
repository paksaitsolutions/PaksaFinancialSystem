import axios from 'axios'

const API_BASE = '/api/v1/fixed-assets'

export interface FixedAsset {
  id: number
  asset_number: string
  name: string
  description?: string
  category: string
  location?: string
  purchase_date: string
  purchase_cost: number
  salvage_value: number
  useful_life_years: number
  depreciation_method: string
  accumulated_depreciation: number
  status: string
  vendor_name?: string
  warranty_expiry?: string
}

export interface MaintenanceRecord {
  id: number
  asset_id: number
  maintenance_type: string
  description: string
  scheduled_date: string
  completed_date?: string
  status: string
  estimated_cost?: number
  actual_cost?: number
  vendor_name?: string
  notes?: string
}

export interface AssetCategory {
  id: number
  name: string
  description?: string
  default_useful_life?: number
  default_depreciation_method: string
  default_salvage_rate: number
}

class FixedAssetApiService {
  // Asset methods
  async getAssets(): Promise<FixedAsset[]> {
    const response = await axios.get(`${API_BASE}/assets/`)
    return response.data
  }

  async getAsset(id: number): Promise<FixedAsset> {
    const response = await axios.get(`${API_BASE}/assets/${id}`)
    return response.data
  }

  async createAsset(asset: Omit<FixedAsset, 'id' | 'accumulated_depreciation' | 'status'>): Promise<FixedAsset> {
    const response = await axios.post(`${API_BASE}/assets/`, asset)
    return response.data
  }

  async updateAsset(id: number, asset: Partial<FixedAsset>): Promise<FixedAsset> {
    const response = await axios.put(`${API_BASE}/assets/${id}`, asset)
    return response.data
  }

  async deleteAsset(id: number): Promise<void> {
    await axios.delete(`${API_BASE}/assets/${id}`)
  }

  async disposeAsset(id: number, disposalData: {
    disposal_date: string
    disposal_amount: number
    disposal_reason: string
  }): Promise<FixedAsset> {
    const response = await axios.post(`${API_BASE}/assets/${id}/dispose`, disposalData)
    return response.data
  }

  async createDepreciationEntry(assetId: number, periodDate: string): Promise<any> {
    const response = await axios.post(`${API_BASE}/assets/${assetId}/depreciation`, {
      period_date: periodDate
    })
    return response.data
  }

  // Maintenance methods
  async getMaintenanceRecords(assetId?: number): Promise<MaintenanceRecord[]> {
    const params = assetId ? { asset_id: assetId } : {}
    const response = await axios.get(`${API_BASE}/maintenance/`, { params })
    return response.data
  }

  async createMaintenanceRecord(maintenance: Omit<MaintenanceRecord, 'id'>): Promise<MaintenanceRecord> {
    const response = await axios.post(`${API_BASE}/maintenance/`, maintenance)
    return response.data
  }

  async updateMaintenanceRecord(id: number, maintenance: Partial<MaintenanceRecord>): Promise<MaintenanceRecord> {
    const response = await axios.put(`${API_BASE}/maintenance/${id}`, maintenance)
    return response.data
  }

  async getUpcomingMaintenance(days: number = 30): Promise<MaintenanceRecord[]> {
    const response = await axios.get(`${API_BASE}/maintenance/`, {
      params: { upcoming_days: days }
    })
    return response.data
  }

  // Category methods
  async getCategories(): Promise<AssetCategory[]> {
    const response = await axios.get(`${API_BASE}/categories/`)
    return response.data
  }

  async createCategory(category: Omit<AssetCategory, 'id'>): Promise<AssetCategory> {
    const response = await axios.post(`${API_BASE}/categories/`, category)
    return response.data
  }

  // Reports
  async getAssetReport(): Promise<any> {
    const response = await axios.get(`${API_BASE}/reports/summary`)
    return response.data
  }
}

export const fixedAssetApiService = new FixedAssetApiService()