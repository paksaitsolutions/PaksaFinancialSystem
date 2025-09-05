import { api } from '@/utils/api';

export interface InventoryLocation {
  id: string;
  code: string;
  name: string;
  description?: string;
  is_active: boolean;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  company_id: string;
  created_at: string;
  updated_at: string;
}

export interface InventoryLocationCreate {
  code: string;
  name: string;
  description?: string;
  is_active?: boolean;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
}

export default {
  async getLocations(companyId: string, params?: any) {
    const queryParams = new URLSearchParams({ company_id: companyId, ...params });
    return api.get(`/inventory/locations?${queryParams.toString()}`);
  },

  async getLocation(locationId: string) {
    return api.get(`/inventory/locations/${locationId}`);
  },

  async createLocation(companyId: string, locationData: InventoryLocationCreate) {
    return api.post('/inventory/locations', { ...locationData, company_id: companyId });
  },

  async updateLocation(locationId: string, locationData: Partial<InventoryLocationCreate>) {
    return api.put(`/inventory/locations/${locationId}`, locationData);
  },

  async deleteLocation(locationId: string) {
    return api.delete(`/inventory/locations/${locationId}`);
  }
};