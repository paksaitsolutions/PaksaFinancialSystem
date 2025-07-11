import apiClient from '@/services/api';
import type { BillCreate, PaymentCreate, VendorCreate } from '@/types/accounts-payable';

export const fetchBills = (params = {}) => apiClient.get('/accounts-payable/bills', { params });
export const getBill = (id: string) => apiClient.get(`/accounts-payable/bills/${id}`);
export const createBill = (data: BillCreate) => apiClient.post('/accounts-payable/bills', data);
export const updateBill = (id: string, data: Partial<BillCreate>) => apiClient.put(`/accounts-payable/bills/${id}`, data);
export const deleteBill = (id: string) => apiClient.delete(`/accounts-payable/bills/${id}`);

export const fetchPayments = (params = {}) => apiClient.get('/accounts-payable/payments', { params });
export const getPayment = (id: string) => apiClient.get(`/accounts-payable/payments/${id}`);
export const recordPayment = (data: PaymentCreate) => apiClient.post('/accounts-payable/payments', data);

export const fetchVendors = (params = {}) => apiClient.get('/accounts-payable/vendors', { params });
export const getVendor = (id: string) => apiClient.get(`/accounts-payable/vendors/${id}`);
export const createVendor = (data: VendorCreate) => apiClient.post('/accounts-payable/vendors', data);

export const fetchAgingReport = (params = {}) => apiClient.get('/accounts-payable/reports/accounts-aging', { params });
export const fetchPaymentsSummary = (params = {}) => apiClient.get('/accounts-payable/reports/payments-summary', { params });
