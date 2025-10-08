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

export interface Customer {
  id: string;
  code: string;
  name: string;
  email: string;
  phone: string;
  status: string;
  payment_terms: string;
  credit_limit: number;
}

export interface ARInvoice {
  id: string;
  invoice_number: string;
  customer: { name: string };
  invoice_date: string;
  due_date: string;
  total_amount: number;
  balance_due: number;
  status: string;
}

export interface ARPayment {
  id: string;
  payment_number: string;
  customer: { name: string };
  payment_date: string;
  amount: number;
  payment_method: string;
  status: string;
}

export interface AnalyticsDashboard {
  kpis: {
    total_outstanding: number;
    overdue_amount: number;
    current_month_collections: number;
    dso: number;
    total_customers: number;
    active_customers: number;
  };
  aging_buckets: Array<{
    range: string;
    amount: number;
    percentage: number;
    invoice_count: number;
    risk: string;
  }>;
  collection_metrics: Array<{
    name: string;
    value: string;
    percentage: number;
    status: string;
  }>;
  payment_forecasts: Array<{
    period: string;
    amount: number;
    confidence: number;
    risk_level: string;
  }>;
  risk_analysis: {
    high_risk_customers: number;
    medium_risk_customers: number;
    low_risk_customers: number;
    total_at_risk_amount: number;
  };
}

// Customers API
export const customerService = {
  async getCustomers(params?: any) {
    const response = await apiClient.get('/api/v1/accounts-receivable/customers', { params });
    return response.data;
  },

  async getCustomer(id: string) {
    const response = await apiClient.get(`/api/v1/accounts-receivable/customers/${id}`);
    return response.data;
  },

  async createCustomer(customer: Partial<Customer>) {
    const response = await apiClient.post('/api/v1/accounts-receivable/customers', customer);
    return response.data;
  },

  async updateCustomer(id: string, customer: Partial<Customer>) {
    const response = await apiClient.put(`/api/v1/accounts-receivable/customers/${id}`, customer);
    return response.data;
  }
};

// Invoices API
export const invoiceService = {
  async getInvoices(params?: any) {
    const response = await apiClient.get('/api/v1/accounts-receivable/invoices', { params });
    return response.data;
  },

  async getInvoice(id: string) {
    const response = await apiClient.get(`/api/v1/accounts-receivable/invoices/${id}`);
    return response.data;
  },

  async createInvoice(invoice: Partial<ARInvoice>) {
    const response = await apiClient.post('/api/v1/accounts-receivable/invoices', invoice);
    return response.data;
  },

  async updateInvoice(id: string, invoice: Partial<ARInvoice>) {
    const response = await apiClient.put(`/api/v1/accounts-receivable/invoices/${id}`, invoice);
    return response.data;
  }
};

// Payments API
export const paymentService = {
  async getPayments(params?: any) {
    const response = await apiClient.get('/api/v1/accounts-receivable/payments', { params });
    return response.data;
  },

  async getPayment(id: string) {
    const response = await apiClient.get(`/api/v1/accounts-receivable/payments/${id}`);
    return response.data;
  },

  async createPayment(payment: Partial<ARPayment>) {
    const response = await apiClient.post('/api/v1/accounts-receivable/payments', payment);
    return response.data;
  }
};

// Analytics API
export const analyticsService = {
  async getDashboardAnalytics(): Promise<AnalyticsDashboard> {
    const response = await apiClient.get('/api/v1/accounts-receivable/analytics/dashboard');
    return response.data;
  },

  async getAgingReport(params?: any) {
    const response = await apiClient.get('/api/v1/accounts-receivable/analytics/aging-report', { params });
    return response.data;
  },

  async getCollectionForecast(days: number = 90) {
    const response = await apiClient.get(`/api/v1/accounts-receivable/analytics/collection-forecast?days=${days}`);
    return response.data;
  },

  async getCustomerSegmentation() {
    const response = await apiClient.get('/api/v1/accounts-receivable/analytics/customer-segmentation');
    return response.data;
  }
};

export default {
  customerService,
  invoiceService,
  paymentService,
  analyticsService
};