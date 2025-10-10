import { api } from '@/utils/api'

export interface Customer {
  id: string
  name: string
  email: string
  phone: string
  address: string
  creditLimit: number
  balance: number
  paymentTerms: string
  status: 'active' | 'inactive'
}

export interface Invoice {
  id: string
  customer_id: string
  invoice_number: string
  invoice_date: string
  due_date: string
  total_amount: number
  paid_amount: number
  status: 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled'
  customer?: Customer
}

export interface Payment {
  id: string
  invoice_id: string
  amount: number
  payment_date: string
  payment_method: string
  reference: string
}

export interface ARAnalytics {
  total_outstanding: number
  overdue_amount: number
  current_month_collections: number
  active_customers: number
  average_days_to_pay: number
  collection_efficiency: number
}

export const analyticsService = {
  async getDashboardAnalytics(): Promise<ARAnalytics> {
    const response = await api.get('/ar/analytics/dashboard')
    return response.data
  }
}

export const customerService = {
  async getCustomers(params?: { limit?: number }): Promise<{ customers: Customer[] }> {
    const response = await api.get('/ar/customers', { params })
    return response.data
  },

  async createCustomer(customer: Omit<Customer, 'id'>): Promise<Customer> {
    const response = await api.post('/ar/customers', customer)
    return response.data
  },

  async updateCustomer(id: string, customer: Partial<Customer>): Promise<Customer> {
    const response = await api.put(`/ar/customers/${id}`, customer)
    return response.data
  }
}

export const invoiceService = {
  async getInvoices(params?: { limit?: number }): Promise<{ invoices: Invoice[] }> {
    const response = await api.get('/ar/invoices', { params })
    return response.data
  },

  async createInvoice(invoice: Omit<Invoice, 'id' | 'status'>): Promise<Invoice> {
    const response = await api.post('/ar/invoices', invoice)
    return response.data
  },

  async recordPayment(payment: Omit<Payment, 'id'>): Promise<Payment> {
    const response = await api.post('/ar/payments', payment)
    return response.data
  },

  async sendReminders(invoiceIds: string[]): Promise<{ success: boolean }> {
    const response = await api.post('/ar/invoices/send-reminders', { invoice_ids: invoiceIds })
    return response.data
  }
}