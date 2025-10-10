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

export interface AssetValuationReport {
  by_category: {
    category: string
    count: number
    cost: number
    current_value: number
  }[]
  by_status: {
    status: string
    count: number
    value: number
  }[]
  total_cost: number
  total_current_value: number
  total_depreciation: number
}

export interface DepreciationReport {
  monthly_depreciation: {
    month: string
    amount: number
  }[]
  by_category: {
    category: string
    amount: number
  }[]
  total_annual_depreciation: number
}

export interface MaintenanceReport {
  upcoming: MaintenanceRecord[]
  overdue: MaintenanceRecord[]
  completed_this_month: MaintenanceRecord[]
  total_maintenance_cost: number
}