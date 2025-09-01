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
    // TODO: Replace with actual API call when backend is ready
    // const response = await axios.get(`${API_BASE}/assets/`)
    // return response.data
    return [
      {
        id: 1,
        asset_number: 'FA-001',
        name: 'Office Computer',
        category: 'IT Equipment',
        purchase_cost: 1500,
        accumulated_depreciation: 300,
        status: 'active',
        purchase_date: '2023-01-15',
        salvage_value: 100,
        useful_life_years: 5,
        depreciation_method: 'straight_line'
      }
    ]
  }

  async getAsset(id: number): Promise<FixedAsset> {
    // TODO: Replace with actual API call when backend is ready
    // const response = await axios.get(`${API_BASE}/assets/${id}`)
    // return response.data
    return {
      id,
      asset_number: 'FA-001',
      name: 'Office Computer',
      category: 'IT Equipment',
      purchase_cost: 1500,
      accumulated_depreciation: 300,
      status: 'active',
      purchase_date: '2023-01-15',
      salvage_value: 100,
      useful_life_years: 5,
      depreciation_method: 'straight_line'
    }
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

  // Reports
  async getAssetReport(): Promise<any> {
    // TODO: Replace with actual API call when backend is ready
    // const response = await axios.get(`${API_BASE}/reports/`)
    // return response.data
    
    // Mock data for now
    return {
      total_assets: 25,
      total_cost: 125000,
      total_accumulated_depreciation: 45000,
      total_book_value: 80000,
      assets_by_category: [
        { category: 'IT Equipment', count: 10, total_cost: 70000 },
        { category: 'Office Furniture', count: 8, total_cost: 30000 },
        { category: 'Vehicles', count: 5, total_cost: 20000 },
        { category: 'Machinery', count: 2, total_cost: 5000 }
      ],
      assets_by_status: [
        { status: 'active', count: 22 },
        { status: 'under_maintenance', count: 2 },
        { status: 'disposed', count: 1 }
      ]
    }
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
    // TODO: Replace with actual API call when backend is ready
    // const params = assetId ? { asset_id: assetId } : {}
    // const response = await axios.get(`${API_BASE}/maintenance/`, { params })
    // return response.data
    return [
      {
        id: 1,
        asset_id: assetId || 1, // Use provided assetId or default to 1
        maintenance_type: 'Preventive',
        description: 'Regular system maintenance',
        scheduled_date: '2024-02-15',
        status: 'scheduled',
        estimated_cost: 150,
        actual_cost: 0 // Changed from null to 0 to match number type
      }
    ]
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

}

export const fixedAssetApiService = new FixedAssetApiService()