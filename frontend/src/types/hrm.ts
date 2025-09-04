// Base interface for all HRM entities
export interface BaseEntity {
  id: string;
  createdAt?: string;
  updatedAt?: string;
  createdBy?: string;
  updatedBy?: string;
}

// Employee related types
export interface Employee extends BaseEntity {
  employeeId: string;
  firstName: string;
  middleName?: string;
  lastName: string;
  email: string;
  phoneNumber?: string;
  dateOfBirth?: string;
  gender?: 'male' | 'female' | 'other' | 'prefer-not-to-say';
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  postalCode?: string;
  departmentId?: string;
  positionId?: string;
  hireDate?: string;
  employmentType: 'full-time' | 'part-time' | 'contract' | 'temporary' | 'internship';
  employmentStatus: 'active' | 'on-leave' | 'terminated' | 'retired';
  salary?: number;
  salaryCurrency?: string;
  photoUrl?: string;
  emergencyContactName?: string;
  emergencyContactPhone?: string;
  emergencyContactRelation?: string;
  skills?: string[];
  qualifications?: Qualification[];
  documents?: EmployeeDocument[];
  department?: Department;
  position?: Position;
  leaveBalances?: LeaveBalance[];
}

export interface Qualification extends BaseEntity {
  degree: string;
  fieldOfStudy: string;
  institution: string;
  startDate: string;
  endDate?: string;
  isCompleted: boolean;
  description?: string;
}

export interface EmployeeDocument extends BaseEntity {
  name: string;
  type: string;
  fileUrl: string;
  issueDate?: string;
  expiryDate?: string;
  status: 'valid' | 'expired' | 'expiring-soon';
  notes?: string;
}

// Department related types
export interface Department extends BaseEntity {
  name: string;
  code: string;
  description?: string;
  managerId?: string;
  parentDepartmentId?: string;
  status: 'active' | 'inactive';
  employeeCount?: number;
  manager?: Employee;
  parentDepartment?: Department;
  subDepartments?: Department[];
}

// Position related types
export interface Position extends BaseEntity {
  title: string;
  code: string;
  description?: string;
  departmentId: string;
  isManagerial: boolean;
  isActive: boolean;
  jobDescription?: string;
  requirements?: string;
  minSalary?: number;
  maxSalary?: number;
  department?: Department;
  employeeCount?: number;
}

// Leave related types
export interface LeaveRequest extends BaseEntity {
  employeeId: string;
  leaveTypeId: string;
  startDate: string;
  endDate: string;
  reason: string;
  status: 'pending' | 'approved' | 'rejected' | 'cancelled';
  approverId?: string;
  approverNotes?: string;
  employee?: Employee;
  leaveType?: LeaveType;
  approver?: Employee;
  daysRequested: number;
  isHalfDay?: boolean;
  halfDayType?: 'morning' | 'afternoon';
}

export interface LeaveType extends BaseEntity {
  name: string;
  code: string;
  description?: string;
  defaultDays: number;
  isPaid: boolean;
  isActive: boolean;
  requiresApproval: boolean;
  carryForward: boolean;
  maxCarryForwardDays?: number;
  genderSpecific?: 'male' | 'female' | null;
}

export interface LeaveBalance extends BaseEntity {
  employeeId: string;
  leaveTypeId: string;
  year: number;
  totalDays: number;
  usedDays: number;
  pendingDays: number;
  carriedOverDays: number;
  employee?: Employee;
  leaveType?: LeaveType;
}

// Payroll related types
export interface PayrollRun extends BaseEntity {
  name: string;
  description?: string;
  startDate: string;
  endDate: string;
  paymentDate: string;
  status: 'draft' | 'processing' | 'completed' | 'cancelled';
  totalAmount: number;
  currency: string;
  paymentMethod: 'bank' | 'cash' | 'check' | 'other';
  notes?: string;
  entries: PayrollEntry[];
}

export interface PayrollEntry extends BaseEntity {
  payrollRunId: string;
  employeeId: string;
  basicSalary: number;
  allowances: PayrollAllowance[];
  deductions: PayrollDeduction[];
  overtimePay: number;
  bonus: number;
  tax: number;
  otherDeductions: number;
  netPay: number;
  paymentStatus: 'pending' | 'paid' | 'failed';
  paymentReference?: string;
  notes?: string;
  employee?: Employee;
}

export interface PayrollAllowance {
  name: string;
  amount: number;
  isTaxable: boolean;
  description?: string;
}

export interface PayrollDeduction {
  name: string;
  amount: number;
  isTaxDeductible: boolean;
  description?: string;
}

// Email Template types
export interface EmailTemplate extends BaseEntity {
  name: string;
  subject: string;
  body: string;
  description?: string;
  isActive: boolean;
  category: 'onboarding' | 'offboarding' | 'leave' | 'payroll' | 'announcement' | 'other';
  variables: string[];
  lastUsedAt?: string;
  usedCount: number;
}

// Analytics types
export interface PayrollAnalytics {
  summary: {
    totalEmployees: number;
    totalPayroll: number;
    averageSalary: number;
    averageOvertime: number;
    totalTax: number;
    totalDeductions: number;
    netPay: number;
  };
  byDepartment: Array<{
    departmentId: string;
    departmentName: string;
    totalPayroll: number;
    employeeCount: number;
    averageSalary: number;
  }>;
  byPosition: Array<{
    positionId: string;
    positionTitle: string;
    totalPayroll: number;
    employeeCount: number;
    averageSalary: number;
  }>;
  monthlyTrends: Array<{
    month: string;
    totalPayroll: number;
    employeeCount: number;
    averageSalary: number;
  }>;
  topEarners: Array<{
    employeeId: string;
    employeeName: string;
    position: string;
    department: string;
    salary: number;
    totalEarnings: number;
  }>;
  expenseCategories: Array<{
    category: string;
    amount: number;
    percentage: number;
  }>;
}

// API Response types
export interface PaginatedResponse<T> {
  data: T[];
  meta: {
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  };
}

export interface ApiError {
  message: string;
  code?: string;
  statusCode?: number;
  errors?: Record<string, string[]>;
}

// Form types
export interface EmployeeFormData extends Omit<Employee, 'id' | 'createdAt' | 'updatedAt' | 'createdBy' | 'updatedBy' | 'department' | 'position' | 'qualifications' | 'documents' | 'leaveBalances'> {
  departmentId?: string;
  positionId?: string;
  photoFile?: File | null;
}

export interface DepartmentFormData extends Omit<Department, 'id' | 'createdAt' | 'updatedAt' | 'createdBy' | 'updatedBy' | 'manager' | 'parentDepartment' | 'subDepartments' | 'employeeCount'> {
  managerId?: string;
  parentDepartmentId?: string;
}

export interface PositionFormData extends Omit<Position, 'id' | 'createdAt' | 'updatedAt' | 'createdBy' | 'updatedBy' | 'department' | 'employeeCount'> {
  departmentId: string;
}

export interface EmailTemplateFormData extends Omit<EmailTemplate, 'id' | 'createdAt' | 'updatedAt' | 'createdBy' | 'updatedBy' | 'lastUsedAt' | 'usedCount'> {}

// Filter types
export interface EmployeeFilter {
  search?: string;
  departmentId?: string;
  positionId?: string;
  employmentType?: string[];
  employmentStatus?: string[];
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface PayrollFilter {
  startDate?: string;
  endDate?: string;
  departmentId?: string;
  positionId?: string;
  paymentStatus?: string[];
  page?: number;
  limit?: number;
}
