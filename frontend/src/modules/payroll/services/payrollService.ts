import axios, { AxiosRequestConfig } from 'axios';
import {
  PayRun,
  PayPeriod,
  Payslip,
  EmployeePayrollInfo,
  PayrollSettings,
  ReportTemplate,
  PayrollApiResponse,
  PayRunWithDetails,
  PayslipWithDetails,
  PayRunCreatePayload,
  PayPeriodCreateData,
  YearToDateSummary
} from './types';

const API_BASE_URL = '/api/payroll';

// API Response Handler
const handleResponse = <T>(response: { data: PayrollApiResponse<T> }): T => {
  if (!response.data.success) {
    throw new Error(response.data.message || 'Request failed');
  }
  return response.data.data!;
};

// Error Handler
const handleError = (error: any, defaultMessage: string): never => {
  const message = error.response?.data?.message || error.message || defaultMessage;
  console.error('Payroll API Error:', error);
  throw new Error(message);
};

// Date formatting utilities have been moved to a shared date utility module

// Convert params object to query string
const getQueryString = (params: Record<string, any>): string => {
  const queryParams = new URLSearchParams();
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined) {
      if (Array.isArray(value)) {
        value.forEach(item => queryParams.append(key, String(item)));
      } else {
        queryParams.append(key, String(value));
      }
    }
  });
  
  return queryParams.toString();
};

// Alias for handleResponse for better readability
const getData = handleResponse;

/**
 * API client configuration
 * Handles all HTTP requests and responses with consistent error handling
 */
const api = {
  /**
   * Send a GET request to the specified URL
   * @template T Expected response data type
   * @param url The URL to send the request to
   * @param config Optional Axios request configuration
   * @returns Promise with the response data
   */
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<{ data: T }> {
    const response = await axios.get<PayrollApiResponse<T>>(url, { ...config });
    if (!response.data.success) {
      throw new Error(response.data.message || 'Request failed');
    }
    return { data: response.data.data! }; // Non-null assertion as we've checked success
  },

  /**
   * Send a POST request to the specified URL
   * @template T Expected response data type
   * @param url The URL to send the request to
   * @param data The data to send in the request body
   * @param config Optional Axios request configuration
   * @returns Promise with the response data
   */
  async post<T>(
    url: string, 
    data?: any, 
    config?: AxiosRequestConfig
  ): Promise<{ data: T }> {
    const response = await axios.post<PayrollApiResponse<T>>(url, data, config);
    if (!response.data.success) {
      throw new Error(response.data.message || 'Request failed');
    }
    return { data: response.data.data! }; // Non-null assertion as we've checked success
  },

  /**
   * Send a PUT request to the specified URL
   * @template T Expected response data type
   * @param url The URL to send the request to
   * @param data The data to send in the request body
   * @param config Optional Axios request configuration
   * @returns Promise with the response data
   */
  async put<T>(
    url: string, 
    data?: any, 
    config?: AxiosRequestConfig
  ): Promise<{ data: T }> {
    const response = await axios.put<PayrollApiResponse<T>>(url, data, config);
    if (!response.data.success) {
      throw new Error(response.data.message || 'Request failed');
    }
    return { data: response.data.data! }; // Non-null assertion as we've checked success
  },

  /**
   * Send a DELETE request to the specified URL
   * @param url The URL to send the request to
   * @param config Optional Axios request configuration
   * @returns Promise that resolves when the request is complete
   */
  async delete(url: string, config?: AxiosRequestConfig): Promise<void> {
    const response = await axios.delete<PayrollApiResponse<void>>(url, config);
    if (!response.data.success) {
      throw new Error(response.data.message || 'Request failed');
    }
  }
};

// ==============================================
// Payroll Service
// ==============================================

// ==============================================
// Pay Run Operations
// ==============================================

/**
 * Fetch all pay runs with optional filtering
 * @param params Query parameters for filtering and pagination
 * @returns Promise with an array of pay runs with details
 */
export const getPayRuns = async (params: Record<string, any> = {}): Promise<PayRunWithDetails[]> => {
  try {
    const query = getQueryString(params);
    const response = await api.get<PayrollApiResponse<PayRunWithDetails[]>>(
      `${API_BASE_URL}/pay-runs${query ? `?${query}` : ''}`
    );
    return handleResponse(response);
  } catch (error) {
    return handleError(error, 'Failed to fetch pay runs');
  }
};

/**
 * Get pay run by ID
 * @param id - Pay run ID
 * @returns Promise resolving to pay run details
 * @throws {Error} If pay run cannot be fetched
 */
export const getPayRun = async (id: string): Promise<PayRunWithDetails> => {
  try {
    const response = await api.get<PayrollApiResponse<PayRunWithDetails>>(
      `${API_BASE_URL}/pay-runs/${id}`
    );
    return handleResponse(response);
  } catch (error) {
    return handleError(error, `Failed to fetch pay run ${id}`);
  }
};

export const createPayRun = async (data: PayRunCreatePayload): Promise<PayRunWithDetails> => {
  try {
    const response = await api.post<PayrollApiResponse<PayRunWithDetails>>(
      `${API_BASE_URL}/pay-runs`,
      data
    );
    return getData(response);
  } catch (error) {
    return handleError(error, 'Failed to create pay run');
  }
};

/**
 * Update an existing pay run
 * @param id - Pay run ID to update
 * @param data - Partial pay run data to update
 * @returns Promise resolving to the updated pay run
 * @throws {Error} If pay run update fails
 */
export const updatePayRun = async (id: string, data: Partial<PayRun>): Promise<PayRun> => {
  try {
    const response = await api.put<PayrollApiResponse<PayRun>>(
      `${API_BASE_URL}/pay-runs/${id}`,
      data
    );
    return handleResponse(response);
  } catch (error) {
    return handleError(error, `Failed to update pay run ${id}`);
  }
};

export const deletePayRun = async (id: string): Promise<void> => {
  try {
    await api.delete(`${API_BASE_URL}/pay-runs/${id}`);
  } catch (error) {
    return handleError(error, `Failed to delete pay run ${id}`);
  }
};

/**
 * Process a pay run
 * @param id - Pay run ID to process
 * @returns Promise resolving to the processed pay run
 * @throws {Error} If pay run processing fails
 */
export const processPayRun = async (id: string): Promise<PayRun> => {
  try {
    const response = await api.post<PayrollApiResponse<PayRun>>(
      `${API_BASE_URL}/pay-runs/${id}/process`
    );
    return handleResponse(response);
  } catch (error) {
    return handleError(error, `Failed to process pay run ${id}`);
  }
};

// Pay Period Operations
export const getPayPeriods = async (params: Record<string, any> = {}): Promise<PayPeriod[]> => {
  try {
    const query = getQueryString(params);
    const response = await api.get<PayrollApiResponse<PayPeriod[]>>(
      `${API_BASE_URL}/pay-periods${query ? `?${query}` : ''}`
    );
    return handleResponse(response);
  } catch (error) {
    return handleError(error, 'Failed to fetch pay periods');
  }
};

/**
 * Get pay period by ID
 * @param id - Pay period ID to retrieve
 * @returns Promise resolving to the requested pay period
 * @throws {Error} If pay period cannot be fetched
 */
export const getPayPeriod = async (id: string): Promise<PayPeriod> => {
  try {
    const response = await api.get<PayrollApiResponse<PayPeriod>>(
      `${API_BASE_URL}/pay-periods/${id}`
    );
    return handleResponse(response);
  } catch (error) {
    return handleError(error, `Failed to fetch pay period ${id}`);
  }
};

// Alias for backward compatibility
export const getPayPeriodById = getPayPeriod;

export const createPayPeriod = async (data: PayPeriodCreateData): Promise<PayPeriod> => {
  try {
    const response = await api.post<PayrollApiResponse<PayPeriod>>(
      `${API_BASE_URL}/pay-periods`,
      data
    );
    return getData(response);
  } catch (error) {
    return handleError(error, 'Failed to create pay period');
  }
};

/**
 * Update an existing pay period
 * @param id - Pay period ID to update
 * @param data - Partial pay period data to update
 * @returns Promise resolving to the updated pay period
 * @throws {Error} If pay period update fails
 */
export const updatePayPeriod = async (id: string, data: Partial<PayPeriod>): Promise<PayPeriod> => {
  try {
    const response = await api.put<PayrollApiResponse<PayPeriod>>(
      `${API_BASE_URL}/pay-periods/${id}`,
      data
    );
    return handleResponse(response);
  } catch (error) {
    return handleError(error, `Failed to update pay period ${id}`);
  }
};

export const deletePayPeriod = async (id: string): Promise<void> => {
  try {
    await api.delete(`${API_BASE_URL}/pay-periods/${id}`);
  } catch (error) {
    return handleError(error, `Failed to delete pay period ${id}`);
  }
};

// Payslip Operations
export const getPayslips = async (payRunId: string): Promise<Payslip[]> => {
  try {
    const response = await api.get<PayrollApiResponse<Payslip[]>>(
      `${API_BASE_URL}/payslips`,
      { params: { payRunId } }
    );
    return handleResponse(response);
  } catch (error) {
    return handleError(error, 'Failed to fetch payslips');
  }
};

/**
 * Get payslip by ID with full details
 * @param id - Payslip ID to retrieve
 * @returns Promise resolving to the requested payslip with details
 * @throws {Error} If payslip cannot be fetched
 */
export const getPayslip = async (id: string): Promise<PayslipWithDetails> => {
  try {
    const response = await api.get<PayrollApiResponse<PayslipWithDetails>>(
      `${API_BASE_URL}/payslips/${id}`
    );
    return handleResponse(response);
  } catch (error) {
    return handleError(error, `Failed to fetch payslip ${id}`);
  }
};

// Alias for backward compatibility
export const getPayslipById = getPayslip;

export const updatePayslip = async (id: string, data: Partial<Payslip>): Promise<Payslip> => {
  try {
    const response = await api.put<PayrollApiResponse<Payslip>>(
      `${API_BASE_URL}/payslips/${id}`,
      data
    );
    return handleResponse(response);
  } catch (error) {
    return handleError(error, `Failed to update payslip ${id}`);
  }
};

/**
 * Generate PDF for a payslip
 * @param id - Payslip ID
 * @returns Promise resolving to a Blob containing the PDF
 * @throws {Error} If PDF generation fails
 */
export const generatePayslipPdf = async (id: string): Promise<Blob> => {
  try {
    const response = await api.get<Blob>(
      `${API_BASE_URL}/payslips/${id}/pdf`,
      { responseType: 'blob' }
    );
    return response.data;
  } catch (error) {
    return handleError(error, `Failed to generate PDF for payslip ${id}`);
  }
};

// Employee Operations
export const getEmployeePayrollInfo = async (employeeId: string): Promise<EmployeePayrollInfo> => {
  try {
    const response = await api.get<PayrollApiResponse<EmployeePayrollInfo>>(
      `${API_BASE_URL}/employees/${employeeId}/payroll-info`
    );
    return handleResponse(response);
  } catch (error) {
    return handleError(error, `Failed to fetch payroll info for employee ${employeeId}`);
  }
};

export const updateEmployeePayrollInfo = async (employeeId: string, data: Partial<EmployeePayrollInfo>): Promise<EmployeePayrollInfo> => {
  try {
    const response = await api.put<PayrollApiResponse<EmployeePayrollInfo>>(
      `${API_BASE_URL}/employees/${employeeId}/info`,
      data
    );
    return handleResponse(response);
  } catch (error) {
    return handleError(error, `Failed to update employee payroll info for employee ${employeeId}`);
  }
};

/**
 * Get year-to-date summary for an employee
 * @param employeeId - Employee ID
 * @returns Promise resolving to the YTD summary
 * @throws {Error} If YTD summary cannot be fetched
 */
export const getEmployeeYearToDateSummary = async (employeeId: string): Promise<YearToDateSummary> => {
  try {
    const response = await api.get<PayrollApiResponse<YearToDateSummary>>(
      `${API_BASE_URL}/employees/${employeeId}/ytd-summary`
    );
    return handleResponse(response);
  } catch (error) {
    return handleError(error, `Failed to fetch YTD summary for employee ${employeeId}`);
  }
};

// Payroll Settings Methods
/**
 * Get payroll system settings
 * @returns Promise resolving to the current payroll settings
 * @throws {Error} If settings cannot be fetched
 */
export const getPayrollSettings = async (): Promise<PayrollSettings> => {
  try {
    const response = await api.get<PayrollApiResponse<PayrollSettings>>(
      `${API_BASE_URL}/settings`
    );
    return handleResponse(response);
  } catch (error) {
    return handleError(error, 'Failed to fetch payroll settings');
  }
};

export const updatePayrollSettings = async (data: Partial<PayrollSettings>): Promise<PayrollSettings> => {
  try {
    const response = await api.put<PayrollApiResponse<PayrollSettings>>(
      `${API_BASE_URL}/settings`,
      data
    );
    return handleResponse(response);
  } catch (error) {
    return handleError(error, 'Failed to update payroll settings');
  }
};

// Report Methods
const generateReport = async (params: {
  type: string;
  format: 'pdf' | 'excel' | 'csv' | 'json';
  startDate?: string;
  endDate?: string;
  payRunId?: string;
  employeeId?: string;
  departmentId?: string;
  includeDetails?: boolean;
}): Promise<{ url: string }> => {
  try {
    const response = await api.get<PayrollApiResponse<{ url: string }>>(
      `${API_BASE_URL}/reports/generate`,
      { params }
    );
    return handleResponse(response);
  } catch (error) {
    return handleError(error, 'Failed to generate report');
  }
};

/**
 * Get available payroll report templates
 * @returns Promise resolving to an array of report templates
 * @throws {Error} If report templates cannot be fetched
 */
export const getReportTemplates = async (): Promise<ReportTemplate[]> => {
  try {
    const response = await api.get<PayrollApiResponse<ReportTemplate[]>>(
      `${API_BASE_URL}/reports/templates`
    );
    return handleResponse(response);
  } catch (error) {
    return handleError(error, 'Failed to fetch report templates');
  }
};

// Export all API functions
export const payrollService = {
  // Pay Run operations
  getPayRuns,
  getPayRun,
  createPayRun,
  updatePayRun,
  deletePayRun,
  processPayRun,
  
  // Pay Period operations
  getPayPeriods,
  getPayPeriodById,
  createPayPeriod,
  updatePayPeriod,
  deletePayPeriod,
  
  // Payslip operations
  getPayslips,
  getPayslipById,
  updatePayslip,
  generatePayslipPdf,
  
  // Employee operations
  getEmployeePayrollInfo,
  updateEmployeePayrollInfo,
  getEmployeeYearToDateSummary,
  
  // Payroll settings
  getPayrollSettings,
  updatePayrollSettings,
  
  // Reports
  generateReport,
  getReportTemplates,
};

// Re-export types from types file
export * from './types';

export default payrollService;
