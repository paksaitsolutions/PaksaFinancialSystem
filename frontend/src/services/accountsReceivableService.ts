import apiClient from '@/services/api';
import type { InvoiceCreate, PaymentCreate, CreditNoteCreate } from '@/types/accounts-receivable';

export const fetchInvoices = (params = {}) => apiClient.get('/accounts-receivable/invoices', { params });
export const getInvoice = (id: string) => apiClient.get(`/accounts-receivable/invoices/${id}`);
export const createInvoice = (data: InvoiceCreate) => apiClient.post('/accounts-receivable/invoices', data);
export const updateInvoice = (id: string, data: Partial<InvoiceCreate>) => apiClient.put(`/accounts-receivable/invoices/${id}`, data);
export const deleteInvoice = (id: string) => apiClient.delete(`/accounts-receivable/invoices/${id}`);

export const fetchPayments = (params = {}) => apiClient.get('/accounts-receivable/payments', { params });
export const getPayment = (id: string) => apiClient.get(`/accounts-receivable/payments/${id}`);
export const recordPayment = (data: PaymentCreate) => apiClient.post('/accounts-receivable/payments', data);

export const fetchCreditNotes = (params = {}) => apiClient.get('/accounts-receivable/credit-notes', { params });
export const getCreditNote = (id: string) => apiClient.get(`/accounts-receivable/credit-notes/${id}`);
export const createCreditNote = (data: CreditNoteCreate) => apiClient.post('/accounts-receivable/credit-notes', data);

export const fetchAgingReport = (params = {}) => apiClient.get('/accounts-receivable/reports/accounts-aging', { params });
export const fetchPaymentsSummary = (params = {}) => apiClient.get('/accounts-receivable/reports/payments-summary', { params });
