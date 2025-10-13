import { api } from '@/utils/api'

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

class InventoryService {
  // Dashboard
  async getDashboardKPIs(): Promise<InventoryKPIs> {
    const response = await api.get('/api/v1/inventory/dashboard/kpis')
    return response.data
  }

  async getStockMovements(days: number = 30): Promise<StockMovement[]> {
    const response = await api.get(`/api/v1/inventory/dashboard/movements?days=${days}`)
    return response.data
  }

  async getRecentTransactions(limit: number = 10): Promise<InventoryTransaction[]> {
    const response = await api.get(`/api/v1/inventory/transactions/recent?limit=${limit}`)
    return response.data
  }

  async getStockAlerts(acknowledged: boolean = false): Promise<StockAlert[]> {
    const response = await api.get(`/api/v1/inventory/alerts?acknowledged=${acknowledged}`)
    return response.data
  }

  // Items Management
  async getItems(params?: {
    page?: number
    limit?: number
    search?: string
    category_id?: number
    location_id?: number
    status?: string
  }): Promise<{ items: InventoryItem[], total: number }> {
    const response = await api.get('/api/v1/inventory/items', { params })
    return response.data
  }

  async getItem(id: number): Promise<InventoryItem> {
    const response = await api.get(`/api/v1/inventory/items/${id}`)
    return response.data
  }

  async createItem(item: Omit<InventoryItem, 'id' | 'total_value' | 'last_updated' | 'status'>): Promise<InventoryItem> {
    const response = await api.post('/api/v1/inventory/items', item)
    return response.data
  }

  async updateItem(id: number, item: Partial<InventoryItem>): Promise<InventoryItem> {
    const response = await api.put(`/api/v1/inventory/items/${id}`, item)
    return response.data
  }

  async deleteItem(id: number): Promise<void> {
    await api.delete(`/api/v1/inventory/items/${id}`)
  }

  // Stock Adjustments
  async adjustStock(adjustments: {
    item_id: number
    quantity: number
    type: 'increase' | 'decrease' | 'set'
    reason: string
    notes?: string
  }[]): Promise<InventoryTransaction[]> {
    const response = await api.post('/inventory/adjustments', { adjustments })
    return response.data
  }

  async transferStock(transfer: {
    item_id: number
    quantity: number
    from_location_id: number
    to_location_id: number
    notes?: string
  }): Promise<InventoryTransaction> {
    const response = await api.post('/inventory/transfers', transfer)
    return response.data
  }

  // Categories
  async getCategories(): Promise<InventoryCategory[]> {
    const response = await api.get('/api/v1/inventory/categories')
    return response.data
  }

  async createCategory(category: Omit<InventoryCategory, 'id' | 'item_count' | 'total_value'>): Promise<InventoryCategory> {
    const response = await api.post('/api/v1/inventory/categories', category)
    return response.data
  }

  async updateCategory(id: number, category: Partial<InventoryCategory>): Promise<InventoryCategory> {
    const response = await api.put(`/api/v1/inventory/categories/${id}`, category)
    return response.data
  }

  async deleteCategory(id: number): Promise<void> {
    await api.delete(`/api/v1/inventory/categories/${id}`)
  }

  // Locations
  async getLocations(): Promise<InventoryLocation[]> {
    const response = await api.get('/api/v1/inventory/locations')
    return response.data
  }

  async createLocation(location: Omit<InventoryLocation, 'id' | 'item_count' | 'total_value'>): Promise<InventoryLocation> {
    const response = await api.post('/api/v1/inventory/locations', location)
    return response.data
  }

  async updateLocation(id: number, location: Partial<InventoryLocation>): Promise<InventoryLocation> {
    const response = await api.put(`/api/v1/inventory/locations/${id}`, location)
    return response.data
  }

  async deleteLocation(id: number): Promise<void> {
    await api.delete(`/api/v1/inventory/locations/${id}`)
  }

  // Transactions
  async getTransactions(params?: {
    page?: number
    limit?: number
    item_id?: number
    type?: string
    date_from?: string
    date_to?: string
  }): Promise<{ transactions: InventoryTransaction[], total: number }> {
    const response = await api.get('/inventory/transactions', { params })
    return response.data
  }

  // Alerts
  async acknowledgeAlert(id: number): Promise<void> {
    await api.put(`/inventory/alerts/${id}/acknowledge`)
  }

  async acknowledgeAlerts(ids: number[]): Promise<void> {
    await api.put('/inventory/alerts/acknowledge', { alert_ids: ids })
  }

  // Reports & Analytics
  async getInventoryValuation(): Promise<{
    by_category: { category: string, value: number, percentage: number }[]
    by_location: { location: string, value: number, percentage: number }[]
    total_value: number
  }> {
    const response = await api.get('/api/v1/inventory/reports/valuation')
    return response.data
  }

  async getStockLevelsReport(): Promise<{
    in_stock: number
    low_stock: number
    out_of_stock: number
    overstock: number
    items: InventoryItem[]
  }> {
    const response = await api.get('/api/v1/inventory/reports/stock-levels')
    return response.data
  }

  async getInventoryForecast(days: number = 30): Promise<InventoryForecast[]> {
    const response = await api.get(`/inventory/reports/forecast?days=${days}`)
    return response.data
  }

  // Barcode Operations
  async searchByBarcode(barcode: string): Promise<InventoryItem | null> {
    try {
      const response = await api.get(`/inventory/items/barcode/${barcode}`)
      return response.data
    } catch (error) {
      if (error.response?.status === 404) {
        return null
      }
      throw error
    }
  }

  // Import/Export
  async importItems(file: File): Promise<{ success: number, errors: string[] }> {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/inventory/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  }

  async exportItems(format: 'csv' | 'excel' = 'csv'): Promise<Blob> {
    const response = await api.get(`/inventory/export?format=${format}`, {
      responseType: 'blob'
    })
    return response.data
  }
}

export const inventoryService = new InventoryService()