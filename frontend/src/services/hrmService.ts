import { api } from '@/utils/api'

// Comprehensive HRM Interfaces
export interface Employee {
  id?: string
  tenant_id?: string
  employee_id: string
  first_name: string
  middle_name?: string
  last_name: string
  full_name?: string
  email: string
  phone_number: string
  date_of_birth?: string
  gender?: string
  marital_status?: string
  national_id?: string
  job_title: string
  department_id?: string
  department?: Department
  manager_id?: string
  manager?: Employee
  hire_date: string
  termination_date?: string
  employment_type: string
  base_salary: number
  currency?: string
  is_active: boolean
  created_at?: string
  updated_at?: string
}

export interface Department {
  id: string
  tenant_id?: string
  name: string
  description?: string
  manager_id?: string
  manager?: Employee
  parent_department_id?: string
  parent_department?: Department
  budget?: number
  employee_count?: number
  is_active: boolean
  created_at?: string
  updated_at?: string
}

export interface LeaveRequest {
  id?: string
  tenant_id?: string
  employee_id: string
  employee?: Employee
  leave_type: string
  start_date: string
  end_date: string
  days_requested: number
  reason?: string
  status: string
  approved_by?: string
  approver?: Employee
  approved_at?: string
  rejection_reason?: string
  created_at?: string
  updated_at?: string
}

export interface AttendanceRecord {
  id?: string
  tenant_id?: string
  employee_id: string
  employee?: Employee
  date: string
  check_in_time?: string
  check_out_time?: string
  break_duration?: number
  total_hours?: number
  overtime_hours?: number
  status: string
  notes?: string
  created_at?: string
  updated_at?: string
}

export interface PerformanceReview {
  id?: string
  tenant_id?: string
  employee_id: string
  employee?: Employee
  reviewer_id: string
  reviewer?: Employee
  review_period_start: string
  review_period_end: string
  review_date: string
  overall_rating: string
  goals_achievement?: number
  strengths?: string
  areas_for_improvement?: string
  development_goals?: string
  manager_comments?: string
  employee_comments?: string
  status: string
  created_at?: string
  updated_at?: string
}

export interface TrainingRecord {
  id?: string
  tenant_id?: string
  employee_id: string
  employee?: Employee
  training_name: string
  training_type: string
  provider?: string
  start_date: string
  end_date?: string
  duration_hours?: number
  cost?: number
  status: string
  completion_date?: string
  certificate_url?: string
  notes?: string
  created_at?: string
  updated_at?: string
}

export interface Policy {
  id?: string
  tenant_id?: string
  title: string
  category: string
  description?: string
  content: string
  version: string
  effective_date: string
  expiry_date?: string
  status: string
  approval_required: boolean
  approved_by?: string
  approver?: Employee
  approved_at?: string
  created_at?: string
  updated_at?: string
  created_by?: string
  updated_by?: string
}

export interface JobOpening {
  id?: string
  tenant_id?: string
  title: string
  department_id?: string
  department?: Department
  description: string
  requirements?: string
  employment_type: string
  salary_min?: number
  salary_max?: number
  location?: string
  remote_allowed: boolean
  status: string
  posted_date: string
  closing_date?: string
  hiring_manager_id?: string
  hiring_manager?: Employee
  created_at?: string
  updated_at?: string
}

export interface Candidate {
  id?: string
  tenant_id?: string
  job_opening_id: string
  job_opening?: JobOpening
  first_name: string
  last_name: string
  email: string
  phone_number?: string
  resume_url?: string
  cover_letter?: string
  status: string
  source?: string
  applied_date: string
  created_at?: string
  updated_at?: string
}

export interface Interview {
  id?: string
  tenant_id?: string
  candidate_id: string
  candidate?: Candidate
  interviewer_id: string
  interviewer?: Employee
  interview_type: string
  scheduled_date: string
  duration_minutes?: number
  location?: string
  meeting_link?: string
  status: string
  feedback?: string
  rating?: number
  recommendation?: string
  created_at?: string
  updated_at?: string
}

export interface HRAnalytics {
  total_employees: number
  active_employees: number
  inactive_employees: number
  pending_leave_requests: number
  department_breakdown: Array<{
    department: string
    count: number
  }>
  recent_hires: Array<{
    name: string
    position: string
    hire_date: string
    department?: string
  }>
  average_tenure_months: number
}

export interface EmployeeDashboard {
  employee: Employee
  pending_leave_requests: LeaveRequest[]
  recent_attendance: AttendanceRecord[]
  upcoming_reviews: PerformanceReview[]
  training_progress: TrainingRecord[]
  team_members: Employee[]
}

class HRMService {
  private baseUrl = '/api/v1/hrm'

  // Employee Management
  async getEmployees(params?: {
    skip?: number
    limit?: number
    department_id?: string
    is_active?: boolean
    search?: string
  }): Promise<{ data: Employee[] }> {
    const response = await api.get('/api/v1/hrm/employees')
    return { data: response.data || [] }
  }

  async createEmployee(employee: any): Promise<Employee> {
    const response = await fetch('/api/v1/hrm/employees', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(employee)
    })
    return response.json()
  }

  async updateEmployee(id: string, employee: Partial<Employee>): Promise<Employee> {
    const response = await api.put(`${this.baseUrl}/employees/${id}`, employee)
    return response.data
  }

  async deleteEmployee(id: string): Promise<void> {
    await api.delete(`${this.baseUrl}/employees/${id}`)
  }

  async getEmployee(id: string): Promise<Employee> {
    const response = await api.get(`${this.baseUrl}/employees/${id}`)
    return response.data
  }

  // Department Management
  async getDepartments(params?: {
    include_inactive?: boolean
  }): Promise<{ data: Department[] }> {
    const response = await api.get('/api/v1/hrm/departments')
    return { data: response.data || [] }
  }

  async createDepartment(department: Omit<Department, 'id' | 'tenant_id' | 'created_at' | 'updated_at'>): Promise<Department> {
    const response = await api.post(`${this.baseUrl}/departments`, department)
    return response.data
  }

  async updateDepartment(id: string, department: Partial<Department>): Promise<Department> {
    const response = await api.put(`${this.baseUrl}/departments/${id}`, department)
    return response.data
  }

  async deleteDepartment(id: string): Promise<void> {
    await api.delete(`${this.baseUrl}/departments/${id}`)
  }

  // Leave Management
  async getLeaveRequests(params?: {
    employee_id?: string
    status?: string
    start_date?: string
    end_date?: string
  }): Promise<{ data: LeaveRequest[] }> {
    const response = await api.get(`${this.baseUrl}/leave-requests`, { params })
    return response
  }

  async createLeaveRequest(employeeId: string, request: Omit<LeaveRequest, 'id' | 'tenant_id' | 'employee_id' | 'employee' | 'days_requested' | 'status' | 'created_at' | 'updated_at'>): Promise<LeaveRequest> {
    const response = await api.post(`${this.baseUrl}/leave-requests?employee_id=${employeeId}`, request)
    return response.data
  }

  async approveLeaveRequest(id: string): Promise<LeaveRequest> {
    const response = await api.post(`${this.baseUrl}/leave-requests/${id}/approve`)
    return response.data
  }

  async rejectLeaveRequest(id: string, reason: string): Promise<LeaveRequest> {
    const response = await api.post(`${this.baseUrl}/leave-requests/${id}/reject`, { reason })
    return response.data
  }

  // Attendance Management
  async getAttendanceRecords(params?: {
    employee_id?: string
    start_date?: string
    end_date?: string
  }): Promise<{ data: AttendanceRecord[] }> {
    const response = await api.get(`${this.baseUrl}/attendance`, { params })
    return response
  }

  async recordAttendance(employeeId: string, record: Omit<AttendanceRecord, 'id' | 'tenant_id' | 'employee_id' | 'employee' | 'total_hours' | 'created_at' | 'updated_at'>): Promise<AttendanceRecord> {
    const response = await api.post(`${this.baseUrl}/attendance?employee_id=${employeeId}`, record)
    return response.data
  }

  // Performance Management
  async getPerformanceReviews(params?: {
    employee_id?: string
    year?: number
  }): Promise<{ data: PerformanceReview[] }> {
    const response = await api.get(`${this.baseUrl}/performance-reviews`, { params })
    return response
  }

  async createPerformanceReview(employeeId: string, reviewerId: string, review: Omit<PerformanceReview, 'id' | 'tenant_id' | 'employee_id' | 'reviewer_id' | 'employee' | 'reviewer' | 'status' | 'created_at' | 'updated_at'>): Promise<PerformanceReview> {
    const response = await api.post(`${this.baseUrl}/performance-reviews?employee_id=${employeeId}&reviewer_id=${reviewerId}`, review)
    return response.data
  }

  async updatePerformanceReview(id: string, review: Partial<PerformanceReview>): Promise<PerformanceReview> {
    const response = await api.put(`${this.baseUrl}/performance-reviews/${id}`, review)
    return response.data
  }

  async deletePerformanceReview(id: string): Promise<void> {
    await api.delete(`${this.baseUrl}/performance-reviews/${id}`)
  }

  // Training Management
  async getTrainingRecords(params?: {
    employee_id?: string
    status?: string
  }): Promise<{ data: TrainingRecord[] }> {
    const response = await api.get(`${this.baseUrl}/training-records`, { params })
    return response
  }

  async createTrainingRecord(employeeId: string, training: Omit<TrainingRecord, 'id' | 'tenant_id' | 'employee_id' | 'employee' | 'created_at' | 'updated_at'>): Promise<TrainingRecord> {
    const response = await api.post(`${this.baseUrl}/training-records?employee_id=${employeeId}`, training)
    return response.data
  }

  async updateTrainingRecord(id: string, training: Partial<TrainingRecord>): Promise<TrainingRecord> {
    const response = await api.put(`${this.baseUrl}/training-records/${id}`, training)
    return response.data
  }

  async deleteTrainingRecord(id: string): Promise<void> {
    await api.delete(`${this.baseUrl}/training-records/${id}`)
  }

  // Policy Management
  async getPolicies(params?: {
    category?: string
    status?: string
  }): Promise<{ data: Policy[] }> {
    const response = await api.get(`${this.baseUrl}/policies`, { params })
    return response
  }

  async createPolicy(policy: Omit<Policy, 'id' | 'tenant_id' | 'version' | 'approved_by' | 'approved_at' | 'created_at' | 'updated_at' | 'created_by' | 'updated_by'>): Promise<Policy> {
    const response = await api.post(`${this.baseUrl}/policies`, policy)
    return response.data
  }

  async updatePolicy(id: string, policy: Partial<Policy>): Promise<Policy> {
    const response = await api.put(`${this.baseUrl}/policies/${id}`, policy)
    return response.data
  }

  async deletePolicy(id: string): Promise<void> {
    await api.delete(`${this.baseUrl}/policies/${id}`)
  }

  // Recruitment Management
  async getJobOpenings(params?: {
    department_id?: string
    status?: string
  }): Promise<{ data: JobOpening[] }> {
    const response = await api.get(`${this.baseUrl}/job-openings`, { params })
    return response
  }

  async createJobOpening(jobOpening: Omit<JobOpening, 'id' | 'tenant_id' | 'created_at' | 'updated_at'>): Promise<JobOpening> {
    const response = await api.post(`${this.baseUrl}/job-openings`, jobOpening)
    return response.data
  }

  async getCandidates(params?: {
    job_opening_id?: string
    status?: string
  }): Promise<{ data: Candidate[] }> {
    const response = await api.get(`${this.baseUrl}/candidates`, { params })
    return response
  }

  async createCandidate(candidate: Omit<Candidate, 'id' | 'tenant_id' | 'created_at' | 'updated_at'>): Promise<Candidate> {
    const response = await api.post(`${this.baseUrl}/candidates`, candidate)
    return response.data
  }

  async getInterviews(params?: {
    candidate_id?: string
    interviewer_id?: string
    status?: string
  }): Promise<{ data: Interview[] }> {
    const response = await api.get(`${this.baseUrl}/interviews`, { params })
    return response
  }

  async createInterview(interview: Omit<Interview, 'id' | 'tenant_id' | 'created_at' | 'updated_at'>): Promise<Interview> {
    const response = await api.post(`${this.baseUrl}/interviews`, interview)
    return response.data
  }

  // Analytics
  async getHRAnalytics(): Promise<{ data: HRAnalytics }> {
    const response = await api.get(`${this.baseUrl}/analytics`)
    return response
  }

  // Employee Self-Service
  async getEmployeeDashboard(employeeId: string): Promise<{ data: EmployeeDashboard }> {
    const response = await api.get(`${this.baseUrl}/employees/${employeeId}/dashboard`)
    return response
  }

  // Utility Methods
  formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString()
  }

  getEmploymentTypeLabel(type: string): string {
    const labels: Record<string, string> = {
      FULL_TIME: 'Full Time',
      PART_TIME: 'Part Time',
      CONTRACT: 'Contract',
      TEMPORARY: 'Temporary',
      INTERN: 'Intern'
    }
    return labels[type] || type
  }

  getStatusColor(status: string): string {
    const colors: Record<string, string> = {
      ACTIVE: 'success',
      INACTIVE: 'secondary',
      PENDING: 'warning',
      APPROVED: 'success',
      REJECTED: 'danger',
      DRAFT: 'info',
      COMPLETED: 'success'
    }
    return colors[status] || 'secondary'
  }
}

export const hrmService = new HRMService()
export default hrmService