import { api } from '@/utils/api';

export interface Vendor {
  id: string;
  code: string;
  name: string;
  email?: string;
  phone?: string;
  status: string;
  is_1099: boolean;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  tax_id?: string;
  payment_terms?: string;
  company_id: string;
  created_at: string;
  updated_at: string;
}

export interface VendorCreate {
  code: string;
  name: string;
  email?: string;
  phone?: string;
  status?: string;
  is_1099?: boolean;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  tax_id?: string;
  payment_terms?: string;
}

export default {
  async getVendors(companyId: string, params?: any) {
    const queryParams = new URLSearchParams({ company_id: companyId, ...params });
    return api.get(`/accounts-payable/vendors?${queryParams.toString()}`);
  },

  async getVendor(vendorId: string) {
    return api.get(`/accounts-payable/vendors/${vendorId}`);
  },

  async createVendor(companyId: string, vendorData: VendorCreate) {
    return api.post('/accounts-payable/vendors', { ...vendorData, company_id: companyId });
  },

  async updateVendor(vendorId: string, vendorData: Partial<VendorCreate>) {
    return api.put(`/accounts-payable/vendors/${vendorId}`, vendorData);
  },

  async deleteVendor(vendorId: string) {
    return api.delete(`/accounts-payable/vendors/${vendorId}`);
  }
};