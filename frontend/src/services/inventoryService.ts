import { apiClient } from '@/utils/apiClient'

export interface InventoryItem {
  id?: string
  item_code: string
  item_name: string
  description?: string
  category_id?: string
  unit_of_measure?: string
  cost_price?: number
  selling_price?: number
  reorder_level?: number
  maximum_level?: number
  barcode?: string
  quantity_on_hand?: number
  is_active?: boolean
  created_at?: string
  updated_at?: string
}

export interface InventoryCategory {
  id?: string
  code: string
  name: string
  description?: string
  parent_id?: string
  is_active?: boolean
  created_at?: string
  updated_at?: string
}

export interface InventoryLocation {
  id?: string
  location_code: string
  location_name: string
  address?: string
  location_type?: string
  is_active?: boolean
  created_at?: string
}

export interface InventoryTransaction {
  id?: string
  item_id: string
  location_id: string
  transaction_type: 'in' | 'out' | 'adjustment'
  quantity: number
  unit_cost?: number
  total_value?: number
  reference?: string
  notes?: string
  transaction_date?: string
  created_by?: string
}

export interface InventoryAdjustment {
  id?: string
  adjustment_number: string
  adjustment_date: string
  reason?: string
  total_adjustment_value?: number
  status?: string
  created_by?: string
  approved_by?: string
  created_at?: string
}

export interface ItemsListParams {
  skip?: number
  limit?: number
  search?: string
  category_id?: string
  status?: string
}

class InventoryService {
  private baseUrl = '/api/v1/inventory'

  // Items
  async getItems(params: ItemsListParams = {}) {
    const response = await apiClient.get(`${this.baseUrl}/items`, { params })
    return response.data
  }

  async getItem(id: string) {
    const response = await apiClient.get(`${this.baseUrl}/items/${id}`)
    return response.data
  }

  async createItem(item: Omit<InventoryItem, 'id' | 'created_at' | 'updated_at'>) {
    const response = await apiClient.post(`${this.baseUrl}/items`, item)
    return response.data
  }

  async updateItem(id: string, item: Partial<InventoryItem>) {
    const response = await apiClient.put(`${this.baseUrl}/items/${id}`, item)
    return response.data
  }

  async deleteItem(id: string) {
    const response = await apiClient.delete(`${this.baseUrl}/items/${id}`)
    return response.data
  }

  // Categories
  async getCategories() {
    const response = await apiClient.get(`${this.baseUrl}/categories`)
    return response.data
  }

  async createCategory(category: Omit<InventoryCategory, 'id' | 'created_at' | 'updated_at'>) {
    const response = await apiClient.post(`${this.baseUrl}/categories`, category)
    return response.data
  }

  // Locations
  async getLocations() {
    const response = await apiClient.get(`${this.baseUrl}/locations`)
    return response.data
  }

  async createLocation(location: Omit<InventoryLocation, 'id' | 'created_at'>) {
    const response = await apiClient.post(`${this.baseUrl}/locations`, location)
    return response.data
  }

  // Transactions
  async getTransactions(params: { item_id?: string; skip?: number; limit?: number } = {}) {
    const response = await apiClient.get(`${this.baseUrl}/transactions`, { params })
    return response.data
  }

  async createTransaction(transaction: Omit<InventoryTransaction, 'id' | 'created_by'>) {
    const response = await apiClient.post(`${this.baseUrl}/transactions`, transaction)
    return response.data
  }

  // Adjustments
  async getAdjustments(params: { skip?: number; limit?: number } = {}) {
    const response = await apiClient.get(`${this.baseUrl}/adjustments`, { params })
    return response.data
  }

  async createAdjustment(adjustment: Omit<InventoryAdjustment, 'id' | 'created_by' | 'created_at'>) {
    const response = await apiClient.post(`${this.baseUrl}/adjustments`, adjustment)
    return response.data
  }

  // Barcode lookup
  async lookupByBarcode(code: string) {
    const response = await apiClient.get(`${this.baseUrl}/barcode/lookup`, {
      params: { code }
    })
    return response.data
  }
}

export const inventoryService = new InventoryService()
export default inventoryService