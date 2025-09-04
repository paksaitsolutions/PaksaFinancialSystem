import axios from 'axios';
import { useAuthStore } from '@/stores/auth';
import type { EmailTemplate, Employee, Department, Position } from '@/types/hrm';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const hrmApi = axios.create({
  baseURL: `${API_BASE_URL}/hrm`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
hrmApi.interceptors.request.use((config) => {
  const authStore = useAuthStore();
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`;
  }
  return config;
});

// Response interceptor for error handling
hrmApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Handle specific status codes
      switch (error.response.status) {
        case 401:
          // Handle unauthorized
          const authStore = useAuthStore();
          authStore.logout();
          break;
        case 403:
          // Handle forbidden
          console.error('You do not have permission to perform this action');
          break;
        case 404:
          // Handle not found
          console.error('The requested resource was not found');
          break;
        case 500:
          // Handle server error
          console.error('A server error occurred');
          break;
        default:
          console.error('An error occurred:', error.message);
      }
    } else if (error.request) {
      // The request was made but no response was received
      console.error('No response received from server');
    } else {
      // Something happened in setting up the request
      console.error('Error setting up request:', error.message);
    }
    return Promise.reject(error);
  }
);

// Email Templates API
export const emailTemplateApi = {
  /**
   * Get all email templates
   */
  async getAll(): Promise<EmailTemplate[]> {
    try {
      const response = await hrmApi.get('/email-templates');
      return response.data.data;
    } catch (error) {
      console.error('Error fetching email templates:', error);
      throw error;
    }
  },

  /**
   * Get a single email template by ID
   */
  async getById(id: string): Promise<EmailTemplate> {
    try {
      const response = await hrmApi.get(`/email-templates/${id}`);
      return response.data.data;
    } catch (error) {
      console.error(`Error fetching email template with ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Create a new email template
   */
  async create(template: Partial<EmailTemplate>): Promise<EmailTemplate> {
    try {
      const response = await hrmApi.post('/email-templates', template);
      return response.data.data;
    } catch (error) {
      console.error('Error creating email template:', error);
      throw error;
    }
  },

  /**
   * Update an existing email template
   */
  async update(id: string, template: Partial<EmailTemplate>): Promise<EmailTemplate> {
    try {
      const response = await hrmApi.put(`/email-templates/${id}`, template);
      return response.data.data;
    } catch (error) {
      console.error(`Error updating email template with ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Delete an email template
   */
  async delete(id: string): Promise<void> {
    try {
      await hrmApi.delete(`/email-templates/${id}`);
    } catch (error) {
      console.error(`Error deleting email template with ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Send a test email with the template
   */
  async sendTestEmail(id: string, email: string, data: Record<string, any> = {}): Promise<void> {
    try {
      await hrmApi.post(`/email-templates/${id}/test`, { email, data });
    } catch (error) {
      console.error(`Error sending test email for template ${id}:`, error);
      throw error;
    }
  }
};

// Employees API
export const employeeApi = {
  /**
   * Get all employees with optional filtering and pagination
   */
  async getAll(params: {
    page?: number;
    limit?: number;
    departmentId?: string;
    positionId?: string;
    status?: string;
  } = {}): Promise<{ data: Employee[]; total: number }> {
    try {
      const response = await hrmApi.get('/employees', { params });
      return {
        data: response.data.data,
        total: response.data.meta?.total || response.data.data.length
      };
    } catch (error) {
      console.error('Error fetching employees:', error);
      throw error;
    }
  },

  /**
   * Get a single employee by ID
   */
  async getById(id: string): Promise<Employee> {
    try {
      const response = await hrmApi.get(`/employees/${id}`);
      return response.data.data;
    } catch (error) {
      console.error(`Error fetching employee with ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Create a new employee
   */
  async create(employee: Partial<Employee>): Promise<Employee> {
    try {
      const response = await hrmApi.post('/employees', employee);
      return response.data.data;
    } catch (error) {
      console.error('Error creating employee:', error);
      throw error;
    }
  },

  /**
   * Update an existing employee
   */
  async update(id: string, employee: Partial<Employee>): Promise<Employee> {
    try {
      const response = await hrmApi.put(`/employees/${id}`, employee);
      return response.data.data;
    } catch (error) {
      console.error(`Error updating employee with ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Delete an employee
   */
  async delete(id: string): Promise<void> {
    try {
      await hrmApi.delete(`/employees/${id}`);
    } catch (error) {
      console.error(`Error deleting employee with ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Upload employee photo
   */
  async uploadPhoto(id: string, file: File): Promise<string> {
    try {
      const formData = new FormData();
      formData.append('photo', file);
      
      const response = await hrmApi.post(`/employees/${id}/photo`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      return response.data.data.url;
    } catch (error) {
      console.error(`Error uploading photo for employee ${id}:`, error);
      throw error;
    }
  }
};

// Departments API
export const departmentApi = {
  /**
   * Get all departments
   */
  async getAll(): Promise<Department[]> {
    try {
      const response = await hrmApi.get('/departments');
      return response.data.data;
    } catch (error) {
      console.error('Error fetching departments:', error);
      throw error;
    }
  },

  /**
   * Create a new department
   */
  async create(department: Partial<Department>): Promise<Department> {
    try {
      const response = await hrmApi.post('/departments', department);
      return response.data.data;
    } catch (error) {
      console.error('Error creating department:', error);
      throw error;
    }
  },

  /**
   * Update a department
   */
  async update(id: string, department: Partial<Department>): Promise<Department> {
    try {
      const response = await hrmApi.put(`/departments/${id}`, department);
      return response.data.data;
    } catch (error) {
      console.error(`Error updating department with ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Delete a department
   */
  async delete(id: string): Promise<void> {
    try {
      await hrmApi.delete(`/departments/${id}`);
    } catch (error) {
      console.error(`Error deleting department with ID ${id}:`, error);
      throw error;
    }
  }
};

// Positions API
export const positionApi = {
  /**
   * Get all positions
   */
  async getAll(): Promise<Position[]> {
    try {
      const response = await hrmApi.get('/positions');
      return response.data.data;
    } catch (error) {
      console.error('Error fetching positions:', error);
      throw error;
    }
  },

  /**
   * Create a new position
   */
  async create(position: Partial<Position>): Promise<Position> {
    try {
      const response = await hrmApi.post('/positions', position);
      return response.data.data;
    } catch (error) {
      console.error('Error creating position:', error);
      throw error;
    }
  },

  /**
   * Update a position
   */
  async update(id: string, position: Partial<Position>): Promise<Position> {
    try {
      const response = await hrmApi.put(`/positions/${id}`, position);
      return response.data.data;
    } catch (error) {
      console.error(`Error updating position with ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Delete a position
   */
  async delete(id: string): Promise<void> {
    try {
      await hrmApi.delete(`/positions/${id}`);
    } catch (error) {
      console.error(`Error deleting position with ID ${id}:`, error);
      throw error;
    }
  }
};

// Payroll API
export const payrollApi = {
  /**
   * Get payroll analytics data
   */
  async getAnalytics(params: {
    startDate?: string;
    endDate?: string;
    departmentId?: string;
    positionId?: string;
  } = {}): Promise<any> {
    try {
      const response = await hrmApi.get('/payroll/analytics', { params });
      return response.data.data;
    } catch (error) {
      console.error('Error fetching payroll analytics:', error);
      throw error;
    }
  },

  /**
   * Generate payroll report
   */
  async generateReport(params: {
    startDate: string;
    endDate: string;
    format: 'pdf' | 'excel' | 'csv';
    includeDetails: boolean;
  }): Promise<Blob> {
    try {
      const response = await hrmApi.get('/payroll/report', {
        params,
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error('Error generating payroll report:', error);
      throw error;
    }
  }
};

export default {
  emailTemplate: emailTemplateApi,
  employee: employeeApi,
  department: departmentApi,
  position: positionApi,
  payroll: payrollApi
};
