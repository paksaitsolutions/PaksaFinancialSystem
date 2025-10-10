export interface InventoryItem {
  id: number
  sku: string
  name: string
  description?: string
  category_id: number
  category_name: string
  location_id: number
  location_name: string
  quantity: number
  unit_price: number
  total_value: number
  reorder_point: number
  max_stock: number
  unit_of_measure: string
  barcode?: string
  supplier_id?: number
  supplier_name?: string
  last_updated: string
  status: 'in_stock' | 'low_stock' | 'out_of_stock'
}

export interface InventoryTransaction {
  id: number
  item_id: number
  item_name: string
  item_sku: string
  type: 'stock_in' | 'stock_out' | 'adjustment' | 'transfer'
  quantity: number
  unit_price?: number
  total_value?: number
  reference_number?: string
  notes?: string
  location_from?: string
  location_to?: string
  created_by: string
  created_at: string
}

export interface StockAlert {
  id: number
  item_id: number
  item_name: string
  item_sku: string
  alert_type: 'low_stock' | 'out_of_stock' | 'overstock' | 'expiring'
  severity: 'low' | 'medium' | 'high' | 'critical'
  message: string
  current_quantity: number
  threshold_quantity?: number
  created_at: string
  acknowledged: boolean
}

export interface InventoryKPIs {
  total_items: number
  total_items_change: number
  low_stock_count: number
  out_of_stock_count: number
  total_value: number
  total_value_change: number
  turnover_ratio: number
  avg_days_to_sell: number
}

export interface InventoryCategory {
  id: number
  name: string
  description?: string
  parent_id?: number
  item_count: number
  total_value: number
}

export interface InventoryLocation {
  id: number
  name: string
  code: string
  type: 'warehouse' | 'store' | 'office' | 'other'
  address?: string
  manager?: string
  capacity?: number
  item_count: number
  total_value: number
}

export interface StockMovement {
  date: string
  stock_in: number
  stock_out: number
  adjustments: number
  net_change: number
}

export interface InventoryForecast {
  item_id: number
  item_name: string
  current_stock: number
  predicted_demand: number
  suggested_reorder: number
  days_until_stockout: number
  confidence_score: number
}

export interface StockAdjustment {
  item_id: number
  quantity: number
  type: 'increase' | 'decrease' | 'set'
  reason: string
  notes?: string
}

export interface StockTransfer {
  item_id: number
  quantity: number
  from_location_id: number
  to_location_id: number
  notes?: string
}

export interface InventoryReport {
  id: string
  name: string
  type: 'valuation' | 'stock_levels' | 'movements' | 'forecast'
  generated_at: string
  parameters: Record<string, any>
  data: any
}

export interface BarcodeSearchResult {
  found: boolean
  item?: InventoryItem
  suggestions?: InventoryItem[]
}

export interface ImportResult {
  success: number
  errors: string[]
  warnings?: string[]
  imported_items?: InventoryItem[]
}