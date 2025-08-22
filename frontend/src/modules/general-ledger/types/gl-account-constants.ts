import type { AccountType, AccountCategory, AccountStatus } from './gl-account';

// Account Types
export const ACCOUNT_TYPES = {
  ASSET: 'asset',
  LIABILITY: 'liability',
  EQUITY: 'equity',
  REVENUE: 'revenue',
  EXPENSE: 'expense',
  GAIN: 'gain',
  LOSS: 'loss'
} as const satisfies Record<string, AccountType>;

// Account Categories
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
} as const satisfies Record<string, AccountCategory>;

// Account Statuses
export const ACCOUNT_STATUS = {
  ACTIVE: 'active',
  INACTIVE: 'inactive',
  CLOSED: 'closed',
  PENDING_APPROVAL: 'pending_approval'
} as const satisfies Record<string, AccountStatus>;

// Account number validation rules
export const ACCOUNT_NUMBER_RULES = {
  MIN_LENGTH: 3,
  MAX_LENGTH: 20,
  ALLOWED_CHARS: /^[A-Z0-9\-\.]+$/,
  SEGMENT_SEPARATOR: '.',
  MAX_DEPTH: 5,
  SEGMENT_LENGTH: 3
} as const;

// Account Type to Category Mapping
export const ACCOUNT_TYPE_CATEGORIES: Record<string, AccountCategory[]> = {
  [ACCOUNT_TYPES.ASSET]: [
    ACCOUNT_CATEGORIES.CURRENT_ASSET,
    ACCOUNT_CATEGORIES.FIXED_ASSET,
    ACCOUNT_CATEGORIES.INTANGIBLE_ASSET,
    ACCOUNT_CATEGORIES.INVESTMENT,
    ACCOUNT_CATEGORIES.PREPAID_EXPENSE,
    ACCOUNT_CATEGORIES.RECEIVABLE,
    ACCOUNT_CATEGORIES.INVENTORY,
    ACCOUNT_CATEGORIES.BANK,
    ACCOUNT_CATEGORIES.CASH
  ],
  [ACCOUNT_TYPES.LIABILITY]: [
    ACCOUNT_CATEGORIES.CURRENT_LIABILITY,
    ACCOUNT_CATEGORIES.LONG_TERM_LIABILITY,
    ACCOUNT_CATEGORIES.PAYABLE,
    ACCOUNT_CATEGORIES.ACCRUED_LIABILITY
  ],
  [ACCOUNT_TYPES.EQUITY]: [
    ACCOUNT_CATEGORIES.COMMON_STOCK,
    ACCOUNT_CATEGORIES.PREFERRED_STOCK,
    ACCOUNT_CATEGORIES.RETAINED_EARNINGS
  ],
  [ACCOUNT_TYPES.REVENUE]: [
    ACCOUNT_CATEGORIES.OPERATING_REVENUE,
    ACCOUNT_CATEGORIES.OTHER_REVENUE
  ],
  [ACCOUNT_TYPES.EXPENSE]: [
    ACCOUNT_CATEGORIES.COST_OF_GOODS_SOLD,
    ACCOUNT_CATEGORIES.OPERATING_EXPENSE,
    ACCOUNT_CATEGORIES.DEPRECIATION,
    ACCOUNT_CATEGORIES.AMORTIZATION,
    ACCOUNT_CATEGORIES.INTEREST_EXPENSE,
    ACCOUNT_CATEGORIES.TAX_EXPENSE
  ],
  [ACCOUNT_TYPES.GAIN]: [ACCOUNT_CATEGORIES.GAIN],
  [ACCOUNT_TYPES.LOSS]: [ACCOUNT_CATEGORIES.LOSS]
} as const;

// Default form values
export const DEFAULT_GL_ACCOUNT: CreateGlAccountDto = {
  accountNumber: '',
  name: '',
  accountType: ACCOUNT_TYPES.ASSET,
  accountCategory: ACCOUNT_CATEGORIES.CURRENT_ASSET,
  currency: 'PKR',
  description: '',
  status: ACCOUNT_STATUS.ACTIVE,
  isDetailAccount: true,
  sortOrder: 0,
  openingBalance: 0,
  isLocked: false
};

// Validation messages
export const VALIDATION_MESSAGES = {
  ACCOUNT_NUMBER_REQUIRED: 'Account number is required',
  ACCOUNT_NUMBER_INVALID: 'Account number must be alphanumeric with dots or hyphens only',
  ACCOUNT_NUMBER_LENGTH: `Account number must be between ${ACCOUNT_NUMBER_RULES.MIN_LENGTH} and ${ACCOUNT_NUMBER_RULES.MAX_LENGTH} characters`,
  ACCOUNT_NUMBER_FORMAT: 'Account number must follow the format XXXX.XXX.XX (e.g., 1000.100.00)',
  NAME_REQUIRED: 'Account name is required',
  NAME_LENGTH: 'Account name must be less than 100 characters',
  ACCOUNT_TYPE_REQUIRED: 'Account type is required',
  ACCOUNT_CATEGORY_REQUIRED: 'Account category is required',
  CURRENCY_REQUIRED: 'Currency is required',
  PARENT_ACCOUNT_INVALID: 'Invalid parent account selection',
  OPENING_BALANCE_INVALID: 'Opening balance must be a valid number'
} as const;
