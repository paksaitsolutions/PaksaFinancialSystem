import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token') || sessionStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface Vendor {
  id: string;
  code: string;
  name: string;
  email: string;
  phone: string;
  status: string;
  payment_terms: string;
  is_1099: boolean;
}

export interface Bill {
  id: string;
  invoice_number: string;
  vendor: { name: string };
  invoice_date: string;
  due_date: string;
  total_amount: number;
  balance_due: number;
  status: string;
}

export interface Payment {
  id: string;
  payment_number: string;
  vendor: { name: string };
  payment_date: string;
  amount: number;
  payment_method: string;
  status: string;
}

export interface CreditMemo {
  id: string;
  credit_memo_number: string;
  vendor: { name: string };
  credit_date: string;
  amount: number;
  applied_amount: number;
  remaining_amount: number;
  status: string;
}

// Vendors API
export const vendorService = {
  async getVendors(params?: any) {
    const response = await apiClient.get('/api/v1/accounts-payable/vendors', { params });
    return response.data;
  },

  async getVendor(id: string) {
    const response = await apiClient.get(`/api/v1/accounts-payable/vendors/${id}`);
    return response.data;
  },

  async createVendor(vendor: Partial<Vendor>) {
    const response = await apiClient.post('/api/v1/accounts-payable/vendors', vendor);
    return response.data;
  },

  async updateVendor(id: string, vendor: Partial<Vendor>) {
    const response = await apiClient.put(`/api/v1/accounts-payable/vendors/${id}`, vendor);
    return response.data;
  },

  async deleteVendor(id: string) {
    const response = await apiClient.delete(`/api/v1/accounts-payable/vendors/${id}`);
    return response.data;
  }
};

// Bills API
export const billService = {
  async getBills(params?: any) {
    const response = await apiClient.get('/api/v1/accounts-payable/bills', { params });
    return response.data;
  },

  async getBill(id: string) {
    const response = await apiClient.get(`/api/v1/accounts-payable/bills/${id}`);
    return response.data;
  },

  async createBill(bill: Partial<Bill>) {
    const response = await apiClient.post('/api/v1/accounts-payable/bills', bill);
    return response.data;
  },

  async updateBill(id: string, bill: Partial<Bill>) {
    const response = await apiClient.put(`/api/v1/accounts-payable/bills/${id}`, bill);
    return response.data;
  },

  async approveBill(id: string, approvalData: any) {
    const response = await apiClient.post(`/api/v1/accounts-payable/bills/${id}/approve`, approvalData);
    return response.data;
  },

  async rejectBill(id: string, rejectionData: any) {
    const response = await apiClient.post(`/api/v1/accounts-payable/bills/${id}/reject`, rejectionData);
    return response.data;
  }
};

// Payments API
export const paymentService = {
  async getPayments(params?: any) {
    const response = await apiClient.get('/api/v1/accounts-payable/payments', { params });
    return response.data;
  },

  async getPayment(id: string) {
    const response = await apiClient.get(`/api/v1/accounts-payable/payments/${id}`);
    return response.data;
  },

  async createPayment(payment: Partial<Payment>) {
    const response = await apiClient.post('/api/v1/accounts-payable/payments', payment);
    return response.data;
  },

  async updatePayment(id: string, payment: Partial<Payment>) {
    const response = await apiClient.put(`/api/v1/accounts-payable/payments/${id}`, payment);
    return response.data;
  },

  async deletePayment(id: string) {
    const response = await apiClient.delete(`/api/v1/accounts-payable/payments/${id}`);
    return response.data;
  }
};

// Credit Memos API
export const creditMemoService = {
  async getCreditMemos(params?: any) {
    const response = await apiClient.get('/api/v1/accounts-payable/credit-memos', { params });
    return response.data;
  },

  async getCreditMemo(id: string) {
    const response = await apiClient.get(`/api/v1/accounts-payable/credit-memos/${id}`);
    return response.data;
  },

  async createCreditMemo(memo: Partial<CreditMemo>) {
    const response = await apiClient.post('/api/v1/accounts-payable/credit-memos', memo);
    return response.data;
  },

  async applyCreditMemo(id: string, applicationData: any) {
    const response = await apiClient.post(`/api/v1/accounts-payable/credit-memos/${id}/apply`, applicationData);
    return response.data;
  },

  async voidCreditMemo(id: string, reason: string) {
    const response = await apiClient.post(`/api/v1/accounts-payable/credit-memos/${id}/void`, { reason });
    return response.data;
  }
};

// Reports API
export const reportsService = {
  async getAgingReport(params?: any) {
    const response = await apiClient.get('/api/v1/accounts-payable/reports/aging', { params });
    return response.data;
  },

  async getVendorSummary(params?: any) {
    const response = await apiClient.get('/api/v1/accounts-payable/reports/vendor-summary', { params });
    return response.data;
  },

  async getPaymentHistory(params?: any) {
    const response = await apiClient.get('/api/v1/accounts-payable/reports/payment-history', { params });
    return response.data;
  },

  async getCashFlowForecast(params?: any) {
    const response = await apiClient.get('/api/v1/accounts-payable/reports/cash-flow-forecast', { params });
    return response.data;
  }
};

export default {
  vendorService,
  billService,
  paymentService,
  creditMemoService,
  reportsService
};