import axios from 'axios';

const API_BASE_URL = '/api/employees'; // Update with your actual API base URL

export interface Employee {
  id?: number;
  employeeId: string;
  name: string;
  email: string;
  phone: string;
  department: string;
  departmentId: number;
  position: string;
  hireDate: string;
  status: string;
  address: string;
  city: string;
  state: string;
  zipCode: string;
}

export const employeeService = {
  async getEmployees(): Promise<Employee[]> {
    const response = await axios.get(API_BASE_URL);
    return response.data;
  },

  async getEmployee(id: number): Promise<Employee> {
    const response = await axios.get(`${API_BASE_URL}/${id}`);
    return response.data;
  },

  async createEmployee(employee: Omit<Employee, 'id'>): Promise<Employee> {
    const response = await axios.post(API_BASE_URL, employee);
    return response.data;
  },

  async updateEmployee(id: number, employee: Partial<Employee>): Promise<Employee> {
    const response = await axios.put(`${API_BASE_URL}/${id}`, employee);
    return response.data;
  },

  async deleteEmployee(id: number): Promise<void> {
    await axios.delete(`${API_BASE_URL}/${id}`);
  }
};

export default employeeService;
