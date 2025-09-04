import { apiClient } from '@/utils/apiClient'

export interface Account {
  id: number
  account_code: string
  account_name: string
  account_type: string
  balance: number
  is_active: boolean
}

export interface JournalEntryLine {
  account_id: number
  description: string
  debit_amount: number
  credit_amount: number
}

export interface JournalEntry {
  entry_date: string
  description: string
  reference?: string
  lines: JournalEntryLine[]
}

export interface Vendor {
  id?: number
  vendor_code: string
  vendor_name: string
  contact_person?: string
  email?: string
  phone?: string
  address?: string
}

export interface Customer {
  id?: number
  customer_code: string
  customer_name: string
  contact_person?: string
  email?: string
  phone?: string
  address?: string
  credit_limit: number
}

export interface Bill {
  id?: number
  vendor_id: number
  bill_date: string
  due_date: string
  total_amount: number
}

export interface Invoice {
  id?: number
  customer_id: number
  invoice_date: string
  due_date: string
  total_amount: number
}

class AccountingService {
  private readonly baseUrl = '/api/v1/accounting'

  // Chart of Accounts
  async getAccounts(): Promise<Account[]> {
    return await apiClient.get<Account[]>(`${this.baseUrl}/accounts`)
  }

  async createAccount(account: Omit<Account, 'id' | 'balance' | 'is_active'>): Promise<Account> {
    return await apiClient.post<Account>(`${this.baseUrl}/accounts`, account)
  }

  // Journal Entries
  async createJournalEntry(entry: JournalEntry): Promise<any> {
    return await apiClient.post(`${this.baseUrl}/journal-entries`, entry)
  }

  // Vendors
  async getVendors(): Promise<Vendor[]> {
    return await apiClient.get<Vendor[]>(`${this.baseUrl}/vendors`)
  }

  async createVendor(vendor: Omit<Vendor, 'id'>): Promise<Vendor> {
    return await apiClient.post<Vendor>(`${this.baseUrl}/vendors`, vendor)
  }

  // Customers
  async getCustomers(): Promise<Customer[]> {
    return await apiClient.get<Customer[]>(`${this.baseUrl}/customers`)
  }

  async createCustomer(customer: Omit<Customer, 'id'>): Promise<Customer> {
    return await apiClient.post<Customer>(`${this.baseUrl}/customers`, customer)
  }

  // Bills
  async getBills(): Promise<Bill[]> {
    return await apiClient.get<Bill[]>(`${this.baseUrl}/bills`)
  }

  async createBill(bill: Omit<Bill, 'id'>): Promise<Bill> {
    return await apiClient.post<Bill>(`${this.baseUrl}/bills`, bill)
  }

  // Invoices
  async getInvoices(): Promise<Invoice[]> {
    return await apiClient.get<Invoice[]>(`${this.baseUrl}/invoices`)
  }

  async createInvoice(invoice: Omit<Invoice, 'id'>): Promise<Invoice> {
    return await apiClient.post<Invoice>(`${this.baseUrl}/invoices`, invoice)
  }

  // Trial Balance
  async getTrialBalance(): Promise<any> {
    return await apiClient.get(`${this.baseUrl}/trial-balance`)
  }
}

export const accountingService = new AccountingService()
export default accountingService