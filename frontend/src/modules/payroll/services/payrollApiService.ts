import axios, { AxiosRequestConfig } from 'axios';
import { API_BASE_URL } from '@/config';
import { useToast } from 'primevue/usetoast';

export interface Employee {
  id: number;
  employee_id: string;
  first_name: string;
  last_name: string;
  email?: string;
  department?: string;
  position?: string;
  hire_date: string;
  salary: number;
  pay_frequency: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PayrollRecord {
  id: number;
  employee_id: number;
  pay_period_start: string;
  pay_period_end: string;
  pay_date: string;
  gross_pay: number;
  total_deductions: number;
  net_pay: number;
  status: 'draft' | 'processing' | 'completed' | 'paid' | 'cancelled';
  created_at: string;
  updated_at: string;
  employee?: Employee;
}

export interface DeductionBenefit {
  id: number;
  type: 'deduction' | 'benefit' | 'garnishment' | 'loan' | 'other';
  name: string;
  description?: string;
  amount_type: 'fixed' | 'percentage';
  amount: number;
  taxable: boolean;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PayrollDeduction {
  id: number;
  payroll_record_id: number;
  deduction_benefit_id: number;
  deduction_type: string;
  amount: number;
  description?: string;
  taxable: boolean;
  created_at: string;
  updated_at: string;
  deduction_benefit?: DeductionBenefit;
}

export interface DeductionBenefitFormData {
  type: string;
  name: string;
  description?: string;
  amount_type: 'fixed' | 'percentage';
  amount: number;
  taxable: boolean;
  active: boolean;
}

interface ApiResponse<T> {
  success: boolean;
  message?: string;
  data?: T;
}

const api = axios.create({
  baseURL: `${API_BASE_URL}/payroll`,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Request interceptor to add auth token if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle common errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - redirect to login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

const handleResponse = <T>(response: { data: ApiResponse<T> }): T => {
  if (!response.data.success) {
    throw new Error(response.data.message || 'Request failed');
  }
  return response.data.data!;
};

const handleError = (error: any, defaultMessage: string): never => {
  const message = error.response?.data?.message || error.message || defaultMessage;
  console.error('Payroll API Error:', error);
  throw new Error(message);
};

// Helper function to handle API errors
const handleApiError = (error: any, defaultMessage: string) => {
  const toast = useToast();
  const message = error.response?.data?.message || error.message || defaultMessage;
  
  toast.add({
    severity: 'error',
    summary: 'Error',
    detail: message,
    life: 5000
  });
  
  throw new Error(message);
};

export const payrollApiService = {
  // Employee endpoints
  async getEmployees(params: {
    skip?: number;
    limit?: number;
    active_only?: boolean;
  } = {}): Promise<Employee[]> {
    try {
      const response = await api.get<ApiResponse<Employee[]>>('/employees', { params });
      return handleResponse(response);
    } catch (error) {
      return handleError(error, 'Failed to fetch employees');
    }
  },

  async getEmployee(id: number): Promise<Employee> {
    try {
      const response = await api.get<ApiResponse<Employee>>(`/employees/${id}`);
      return handleResponse(response);
    } catch (error) {
      return handleError(error, `Failed to fetch employee ${id}`);
    }
  },

  async createEmployee(employee: Omit<Employee, 'id' | 'created_at' | 'updated_at'>): Promise<Employee> {
    try {
      const response = await api.post<ApiResponse<Employee>>('/employees', employee);
      return handleResponse(response);
    } catch (error) {
      return handleError(error, 'Failed to create employee');
    }
  },

  async updateEmployee(id: number, updates: Partial<Employee>): Promise<Employee> {
    try {
      const response = await api.put<ApiResponse<Employee>>(`/employees/${id}`, updates);
      return handleResponse(response);
    } catch (error) {
      return handleError(error, `Failed to update employee ${id}`);
    }
  },

  // Payroll Record endpoints
  async getPayrollRecords(params: {
    skip?: number;
    limit?: number;
    status?: string;
    employee_id?: number;
    start_date?: string;
    end_date?: string;
  } = {}): Promise<PayrollRecord[]> {
    try {
      const response = await api.get<ApiResponse<PayrollRecord[]>>('/records', { params });
      return handleResponse(response);
    } catch (error) {
      return handleError(error, 'Failed to fetch payroll records');
    }
  },

  async getPayrollRecord(id: number): Promise<PayrollRecord> {
    try {
      const response = await api.get<ApiResponse<PayrollRecord>>(`/records/${id}`);
      return handleResponse(response);
    } catch (error) {
      return handleError(error, `Failed to fetch payroll record ${id}`);
    }
  },

  async createPayrollRecord(record: Omit<PayrollRecord, 'id' | 'created_at' | 'updated_at'>): Promise<PayrollRecord> {
    try {
      const response = await api.post<ApiResponse<PayrollRecord>>('/records', record);
      return handleResponse(response);
    } catch (error) {
      return handleError(error, 'Failed to create payroll record');
    }
  },

  async updatePayrollRecord(id: number, updates: Partial<PayrollRecord>): Promise<PayrollRecord> {
    try {
      const response = await api.put<ApiResponse<PayrollRecord>>(`/records/${id}`, updates);
      return handleResponse(response);
    } catch (error) {
      return handleError(error, `Failed to update payroll record ${id}`);
    }
  },

  async processPayrollRecord(id: number): Promise<PayrollRecord> {
    try {
      const response = await api.post<ApiResponse<PayrollRecord>>(`/records/${id}/process`);
      return handleResponse(response);
    } catch (error) {
      return handleError(error, `Failed to process payroll record ${id}`);
    }
  },

  // Payroll Deduction endpoints
  async getPayrollDeductions(payrollRecordId: number): Promise<PayrollDeduction[]> {
    try {
      const response = await api.get<ApiResponse<PayrollDeduction[]>>(`/records/${payrollRecordId}/deductions`);
      return handleResponse(response);
    } catch (error) {
      return handleError(error, 'Failed to fetch payroll deductions');
    }
  },

  async addPayrollDeduction(deduction: Omit<PayrollDeduction, 'id' | 'created_at' | 'updated_at'>): Promise<PayrollDeduction> {
    try {
      const response = await api.post<ApiResponse<PayrollDeduction>>('/deductions', deduction);
      return handleResponse(response);
    } catch (error) {
      return handleError(error, 'Failed to add payroll deduction');
    }
  },

  async updatePayrollDeduction(id: number, updates: Partial<PayrollDeduction>): Promise<PayrollDeduction> {
    try {
      const response = await api.put<ApiResponse<PayrollDeduction>>(`/deductions/${id}`, updates);
      return handleResponse(response);
    } catch (error) {
      return handleError(error, `Failed to update payroll deduction ${id}`);
    }
  },

  async deletePayrollDeduction: async (id: number): Promise<void> => {
    try {
      await api.delete(`/deductions/${id}`);
    } catch (error) {
      return handleError(error, `Failed to delete payroll deduction ${id}`);
    }
  },

  // Deductions & Benefits Management
  getDeductionsBenefits: async (params: {
    active_only?: boolean;
    type?: string;
  } = {}): Promise<DeductionBenefit[]> => {
    try {
      const response = await api.get<ApiResponse<DeductionBenefit[]>>('/deductions-benefits', { params });
      return handleResponse(response);
    } catch (error) {
      return handleError(error, 'Failed to fetch deductions and benefits');
    }
  },

  getDeductionBenefit: async (id: number): Promise<DeductionBenefit> => {
    try {
      const response = await api.get<ApiResponse<DeductionBenefit>>(`/deductions-benefits/${id}`);
      return handleResponse(response);
    } catch (error) {
      return handleError(error, `Failed to fetch deduction/benefit ${id}`);
    }
  },

  createDeductionBenefit: async (data: DeductionBenefitFormData): Promise<DeductionBenefit> => {
    try {
      const response = await api.post<ApiResponse<DeductionBenefit>>('/deductions-benefits', data);
      return handleResponse(response);
    } catch (error) {
      return handleError(error, 'Failed to create deduction/benefit');
    }
  },

  updateDeductionBenefit: async (id: number, updates: Partial<DeductionBenefitFormData>): Promise<DeductionBenefit> => {
    try {
      const response = await api.put<ApiResponse<DeductionBenefit>>(`/deductions-benefits/${id}`, updates);
      return handleResponse(response);
    } catch (error) {
      return handleError(error, `Failed to update deduction/benefit ${id}`);
    }
  },

  deleteDeductionBenefit: async (id: number): Promise<void> => {
    try {
      await api.delete(`/deductions-benefits/${id}`);
    } catch (error) {
      return handleError(error, `Failed to delete deduction/benefit ${id}`);
    }
  },

  // Export functionality
  exportDeductionsBenefits: async (format: string, options: any = {}): Promise<{ url: string }> => {
    try {
      const response = await api.post<ApiResponse<{ url: string }>>('/export/deductions-benefits', {
        format,
        options
      });
      return handleResponse(response);
    } catch (error) {
      return handleError(error, 'Failed to export deductions and benefits');
    }
  },

  // Tax calculation endpoint
  async calculatePayrollTaxes(grossPay: number, employeeId: number): Promise<{
    federal_tax: number;
    state_tax: number;
    local_tax: number;
    fica: number;
    medicare: number;
    total_taxes: number;
  }> {
    try {
      const response = await api.get<ApiResponse<any>>('/calculate-taxes', {
        params: { gross_pay: grossPay, employee_id: employeeId }
      });
      return handleResponse(response);
    } catch (error) {
      return handleError(error, 'Failed to calculate payroll taxes');
    }
  }
};

export default payrollApiService;
