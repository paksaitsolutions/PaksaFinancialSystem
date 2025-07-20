// GL Account Types and Categories
export const ACCOUNT_TYPES = {
  ASSET: 'asset',
  LIABILITY: 'liability',
  EQUITY: 'equity',
  REVENUE: 'revenue',
  EXPENSE: 'expense',
  GAIN: 'gain',
  LOSS: 'loss',
} as const;

export type AccountType = typeof ACCOUNT_TYPES[keyof typeof ACCOUNT_TYPES];

// Account Categories with validation rules
export const ACCOUNT_CATEGORIES = {
  // Assets
  CURRENT_ASSET: 'current_asset',
  FIXED_ASSET: 'fixed_asset',
  INTANGIBLE_ASSET: 'intangible_asset',
  INVESTMENT: 'investment',
  PREPAID_EXPENSE: 'prepaid_expense',
  RECEIVABLE: 'receivable',
  INVENTORY: 'inventory',
  
  // Liabilities
  CURRENT_LIABILITY: 'current_liability',
  LONG_TERM_LIABILITY: 'long_term_liability',
  PAYABLE: 'payable',
  ACCRUED_LIABILITY: 'accrued_liability',
  
  // Equity
  COMMON_STOCK: 'common_stock',
  PREFERRED_STOCK: 'preferred_stock',
  RETAINED_EARNINGS: 'retained_earnings',
  
  // Revenue
  OPERATING_REVENUE: 'operating_revenue',
  OTHER_REVENUE: 'other_revenue',
  
  // Expenses
  COST_OF_GOODS_SOLD: 'cost_of_goods_sold',
  OPERATING_EXPENSE: 'operating_expense',
  DEPRECIATION: 'depreciation',
  AMORTIZATION: 'amortization',
  INTEREST_EXPENSE: 'interest_expense',
  TAX_EXPENSE: 'tax_expense',
  
  // Other
  GAIN: 'gain',
  LOSS: 'loss',
  BANK: 'bank',
  CASH: 'cash'
} as const;

export type AccountCategory = typeof ACCOUNT_CATEGORIES[keyof typeof ACCOUNT_CATEGORIES];

// Account statuses
export const ACCOUNT_STATUS = {
  ACTIVE: 'active',
  INACTIVE: 'inactive',
  CLOSED: 'closed',
  PENDING_APPROVAL: 'pending_approval'
} as const;

export type AccountStatus = typeof ACCOUNT_STATUS[keyof typeof ACCOUNT_STATUS];

// Account number validation rules
export const ACCOUNT_NUMBER_RULES = {
  MIN_LENGTH: 3,
  MAX_LENGTH: 20,
  ALLOWED_CHARS: /^[A-Z0-9\-\.]+$/,
  SEGMENT_SEPARATOR: '.',
  MAX_DEPTH: 5,
  SEGMENT_LENGTH: 3
};

export interface GlAccountBase {
  // Core identification
  id: string;
  accountNumber: string;
  name: string;
  description?: string;
  
  // Account classification
  accountType: AccountType;
  accountCategory: AccountCategory;
  accountSubType?: string;
  
  // Hierarchy
  parentAccountId?: string | null;
  level: number;
  isDetailAccount: boolean; // If false, this is a header/summary account
  sortOrder: number;
  
  // Status and control
  status: AccountStatus;
  isSystemAccount: boolean;
  isLocked: boolean;
  
  // Financial data
  currency: string;
  openingBalance: number;
  currentBalance: number;
  yearToDateBalance: number;
  budgetAmount?: number;
  budgetVariance?: number;
  
  // Accounting details
  taxCode?: string;
  costCenter?: string;
  departmentId?: string;
  projectCode?: string;
  
  // Tracking
  lastReconciledDate?: string;
  lastTransactionDate?: string;
  
  // Metadata
  notes?: string;
  tags?: string[];
  customFields?: Record<string, any>;
  
  // Audit
  createdAt: string;
  updatedAt: string;
  createdBy: string;
  updatedBy?: string;
  
  // Soft delete
  isDeleted: boolean;
  deletedAt?: string;
  deletedBy?: string;
}

export interface GlAccount extends GlAccountBase {
  children?: GlAccount[];
  parentAccount?: GlAccount;
  // Override to make required from GlAccountBase
  level: number;
  isDetailAccount: boolean;
  sortOrder: number;
  status: AccountStatus;
  isLocked: boolean;
  openingBalance: number;
  currentBalance: number;
  yearToDateBalance: number;
  isDeleted: boolean;
}

export interface GlAccountTree extends GlAccountBase {
  children: GlAccountTree[];
  parentAccount?: GlAccountBase;
  // Override to make required from GlAccountBase
  level: number;
  isDetailAccount: boolean;
  sortOrder: number;
  status: AccountStatus;
  isLocked: boolean;
  openingBalance: number;
  currentBalance: number;
  yearToDateBalance: number;
  isDeleted: boolean;
}

export interface CreateGlAccountDto {
  // Required fields
  accountNumber: string;
  name: string;
  accountType: AccountType;
  accountCategory: AccountCategory;
  currency: string;
  
  // Optional fields with defaults
  description?: string;
  accountSubType?: string;
  parentAccountId?: string | null;
  status?: AccountStatus;
  isDetailAccount?: boolean;
  sortOrder?: number;
  
  // Financial data
  openingBalance?: number;
  budgetAmount?: number;
  
  // Accounting details
  taxCode?: string;
  costCenter?: string;
  departmentId?: string;
  projectCode?: string;
  
  // Metadata
  notes?: string;
  tags?: string[];
  customFields?: Record<string, any>;
}

export interface UpdateGlAccountDto extends Partial<Omit<CreateGlAccountDto, 'accountNumber' | 'accountType' | 'accountCategory'>> {
  id: string;
  // Additional fields that can be updated separately
  isLocked?: boolean;
  isDeleted?: boolean;
}

export interface GlAccountImportDto extends Omit<CreateGlAccountDto, 'parentAccountId'> {
  parentAccountNumber?: string;
  // Additional fields for import
  importId?: string;
  importStatus?: 'pending' | 'validated' | 'imported' | 'error';
  importErrors?: string[];
}

export interface GlAccountMoveDto {
  accountId: string;
  newParentId: string | null;
  newSortOrder?: number;
}

export interface GlAccountBulkUpdateDto {
  accountIds: string[];
  updates: Partial<UpdateGlAccountDto>;
}

export interface GlAccountReconcileDto {
  accountId: string;
  statementDate: string | Date;
  statementBalance: number;
  reconciliationNotes?: string;
  transactionIds: string[];
}

export interface GlAccountExportDto {
  ids?: string[];
  includeInactive?: boolean;
  includeSystemAccounts?: boolean;
  format?: 'csv' | 'excel' | 'json';
  fields?: (keyof GlAccount)[];
  parentAccountId?: string | null;
}

export interface GlAccountState {
  accounts: GlAccount[];
  accountTree: GlAccountTree[];
  currentAccount: GlAccount | null;
  loading: boolean;
  error: string | null;
}

export interface GlAccountFilters {
  accountType?: AccountType | AccountType[];
  isActive?: boolean;
  searchTerm?: string;
  parentAccountId?: string | null;
  currency?: string;
  page?: number;
  pageSize?: number;
  sortField?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface GlAccountSummary {
  totalAccounts: number;
  activeAccounts: number;
  totalBalance: number;
  byType: Record<AccountType, { count: number; balance: number }>;
}

export interface GlAccountBalanceHistory {
  date: string;
  balance: number;
  change: number;
  transactionCount: number;
  openingBalance: number;
  closingBalance: number;
}

export interface GlAccountImportDto {
  accountNumber: string;
  name: string;
  description?: string;
  accountType: AccountType;
  accountSubType?: string;
  parentAccountNumber?: string;
  isActive: boolean;
  currency: string;
  taxCode?: string;
  costCenter?: string;
  projectCode?: string;
  budgetAmount?: number;
}

export interface GlAccountExportDto extends GlAccountBase {
  parentAccountNumber?: string;
}
