import { apiClient } from '@/utils/apiClient'

export interface Employee {
  id?: string
  employeeId: string
  name: string
  email: string
  phone?: string
  department?: string
  position?: string
  status: string
  hireDate?: string
  salary?: number
}

export interface LeaveRequest {
  id?: string
  employeeId: string
  employeeName: string
  leaveType: string
  startDate: string
  endDate: string
  days: number
  reason: string
  status: string
  submittedDate?: string
}

export interface AttendanceRecord {
  id?: string
  employeeId: string
  employeeName: string
  date: string
  checkIn?: string
  checkOut?: string
  hoursWorked?: string
  status: string
}

export interface Department {
  id: string
  name: string
  description?: string
  manager?: string
  employeeCount: number
}

export interface HRAnalytics {
  totalEmployees: number
  activeEmployees: number
  pendingLeaveRequests: number
  averageAttendance: number
  departmentBreakdown: Array<{
    department: string
    count: number
  }>
  recentHires: Array<{
    name: string
    position: string
    hire_date: string
  }>
}

class HRMService {
  private baseUrl = '/api/v1/hrm'

  // Employee Management
  async getEmployees(params?: {
    skip?: number
    limit?: number
    department?: string
    status?: string
  }): Promise<Employee[]> {
    const response = await apiClient.get(`${this.baseUrl}/employees`, { params })
    return response.data
  }

  async createEmployee(employee: Omit<Employee, 'id'>): Promise<Employee> {
    const response = await apiClient.post(`${this.baseUrl}/employees`, employee)
    return response.data
  }

  async updateEmployee(id: string, employee: Partial<Employee>): Promise<Employee> {
    const response = await apiClient.put(`${this.baseUrl}/employees/${id}`, employee)
    return response.data
  }

  async deleteEmployee(id: string): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/employees/${id}`)
  }

  async getEmployee(id: string): Promise<Employee> {
    const response = await apiClient.get(`${this.baseUrl}/employees/${id}`)
    return response.data
  }

  // Leave Management
  async getLeaveRequests(params?: {
    employeeId?: string
    status?: string
  }): Promise<LeaveRequest[]> {
    const response = await apiClient.get(`${this.baseUrl}/leave-requests`, { params })
    return response.data
  }

  async createLeaveRequest(request: Omit<LeaveRequest, 'id' | 'employeeName' | 'submittedDate'>): Promise<LeaveRequest> {
    const response = await apiClient.post(`${this.baseUrl}/leave-requests`, request)
    return response.data
  }

  async approveLeaveRequest(id: string): Promise<void> {
    await apiClient.put(`${this.baseUrl}/leave-requests/${id}/approve`)
  }

  async rejectLeaveRequest(id: string, reason: string): Promise<void> {
    await apiClient.put(`${this.baseUrl}/leave-requests/${id}/reject`, { reason })
  }

  // Attendance Management
  async getAttendanceRecords(params?: {
    employeeId?: string
    startDate?: string
    endDate?: string
  }): Promise<AttendanceRecord[]> {
    const response = await apiClient.get(`${this.baseUrl}/attendance`, { params })
    return response.data
  }

  async recordAttendance(record: Omit<AttendanceRecord, 'id' | 'employeeName'>): Promise<AttendanceRecord> {
    const response = await apiClient.post(`${this.baseUrl}/attendance`, record)
    return response.data
  }

  // Departments
  async getDepartments(): Promise<Department[]> {
    const response = await apiClient.get(`${this.baseUrl}/departments`)
    return response.data
  }

  // Analytics
  async getHRAnalytics(): Promise<HRAnalytics> {
    const response = await apiClient.get(`${this.baseUrl}/analytics`)
    return response.data
  }

  // Employee Self-Service
  async getEmployeeDashboard(employeeId: string): Promise<any> {
    const response = await apiClient.get(`${this.baseUrl}/employees/${employeeId}/dashboard`)
    return response.data
  }
}

export const hrmService = new HRMService()