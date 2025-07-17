import { faker } from '@faker-js/faker';
import type { AxiosResponse } from 'axios';
import { 
  TaxTransaction, 
  TaxTransactionComponent, 
  TaxRate, 
  TaxJurisdiction,
  TaxTransactionCreate,
  TaxTransactionUpdate,
  TaxTransactionFilter
} from '@/types/tax';

// Import enums as values
import { 
  TaxTransactionStatus,
  TaxTransactionType
} from '@/types/tax';

type ApiResponse<T = any> = AxiosResponse<T>;

// Generate a random UUID
const generateId = (): string => faker.string.uuid();

// Create a mock tax rate
export const createMockTaxRate = (overrides: Partial<TaxRate> = {}): TaxRate => ({
  id: generateId(),
  name: faker.finance.transactionType(),
  rate: faker.number.float({ min: 1, max: 20, fractionDigits: 2 }),
  type: faker.helpers.arrayElement(['percentage', 'fixed']),
  category: faker.commerce.department(),
  effective_date: faker.date.past().toISOString(),
  expiry_date: faker.date.future().toISOString(),
  is_active: true,
  jurisdiction_code: faker.location.countryCode(),
  created_at: faker.date.past().toISOString(),
  updated_at: faker.date.recent().toISOString(),
  ...overrides
});

// Create a mock tax jurisdiction
export const createMockTaxJurisdiction = (overrides: Partial<TaxJurisdiction> = {}): TaxJurisdiction => ({
  id: generateId(),
  code: faker.location.countryCode(),
  name: faker.location.country(),
  level: faker.helpers.arrayElement(['country', 'state', 'county', 'city', 'special']),
  is_active: true,
  created_at: faker.date.past().toISOString(),
  updated_at: faker.date.recent().toISOString(),
  ...overrides
});

// Create a mock tax transaction component
export const createMockTaxTransactionComponent = (
  overrides: Partial<TaxTransactionComponent> = {}
): TaxTransactionComponent => {
  const taxAmount = overrides.tax_amount ?? faker.number.float({ min: 1, max: 1000, fractionDigits: 2 });
  const taxableAmount = overrides.taxable_amount ?? faker.number.float({ min: 100, max: 10000, fractionDigits: 2 });
  
  return {
    id: generateId(),
    transaction_id: generateId(),
    tax_component: faker.finance.transactionType(),
    tax_rate: faker.number.float({ min: 1, max: 20, fractionDigits: 2 }),
    taxable_amount: taxableAmount,
    tax_amount: taxAmount,
    jurisdiction_level: faker.helpers.arrayElement(['country', 'state', 'county', 'city']),
    jurisdiction_name: faker.location.country(),
    jurisdiction_code: faker.location.countryCode(),
    tax_type: faker.finance.transactionType(),
    tax_category: faker.commerce.department(),
    is_tax_inclusive: false,
    created_at: faker.date.past().toISOString(),
    updated_at: faker.date.recent().toISOString(),
    ...overrides
  };
};

// Create a mock tax transaction
export const createMockTaxTransaction = (overrides: Partial<TaxTransaction> = {}): TaxTransaction => {
  const transactionDate = overrides.transaction_date ? new Date(overrides.transaction_date) : faker.date.past();
  const components = overrides.components || [createMockTaxTransactionComponent()];
  
  // Calculate totals if not provided
  let taxableAmount = overrides.taxable_amount;
  let taxAmount = overrides.tax_amount;
  
  if (!taxableAmount || !taxAmount) {
    taxableAmount = components.reduce((sum, comp) => sum + (comp.taxable_amount || 0), 0);
    taxAmount = components.reduce((sum, comp) => sum + (comp.tax_amount || 0), 0);
  }
  
  const totalAmount = overrides.total_amount ?? (taxableAmount + taxAmount);
  
  return {
    id: generateId(),
    transaction_date: transactionDate.toISOString(),
    posting_date: faker.date.recent().toISOString(),
    document_number: `TX-${faker.finance.accountNumber(6)}`,
    reference_number: `REF-${faker.finance.accountNumber(4)}`,
    company_id: generateId(),
    tax_type: faker.finance.transactionType(),
    tax_rate_id: generateId(),
    taxable_amount: taxableAmount,
    tax_amount: taxAmount,
    total_amount: totalAmount,
    status: faker.helpers.arrayElement([
      TaxTransactionStatus.DRAFT,
      TaxTransactionStatus.POSTED,
      TaxTransactionStatus.VOIDED,
      TaxTransactionStatus.ADJUSTED
    ] as const),
    transaction_type: faker.helpers.arrayElement([
      TaxTransactionType.SALE,
      TaxTransactionType.PURCHASE,
      TaxTransactionType.USE,
      TaxTransactionType.IMPORT,
      TaxTransactionType.EXPORT,
      TaxTransactionType.TAX_ADJUSTMENT
    ] as const),
    source_document_type: faker.helpers.arrayElement(['invoice', 'receipt', 'credit_note', 'debit_note']),
    source_document_id: generateId(),
    notes: faker.lorem.sentence(),
    created_at: faker.date.past().toISOString(),
    updated_at: faker.date.recent().toISOString(),
    created_by: generateId(),
    components,
    ...overrides
  };
};

// Create a mock tax transaction create DTO
export const createMockTaxTransactionCreate = (
  overrides: Partial<TaxTransactionCreate> = {}
): TaxTransactionCreate => {
  const components = overrides.components || [
    createMockTaxTransactionComponent({
      id: undefined,
      transaction_id: undefined,
      created_at: undefined,
      updated_at: undefined
    })
  ];
  
  const taxableAmount = overrides.taxable_amount ?? 
    components.reduce((sum, comp) => sum + (comp.taxable_amount || 0), 0);
  const taxAmount = overrides.tax_amount ?? 
    components.reduce((sum, comp) => sum + (comp.tax_amount || 0), 0);
  
  return {
    transaction_date: faker.date.past().toISOString(),
    document_number: `TX-${faker.finance.accountNumber(6)}`,
    reference_number: `REF-${faker.finance.accountNumber(4)}`,
    company_id: generateId(),
    tax_type: faker.finance.transactionType(),
    tax_rate_id: generateId(),
    taxable_amount: taxableAmount,
    tax_amount: taxAmount,
    total_amount: taxableAmount + taxAmount,
    transaction_type: faker.helpers.arrayElement([
      TaxTransactionType.SALE,
      TaxTransactionType.PURCHASE,
      TaxTransactionType.USE,
      TaxTransactionType.IMPORT,
      TaxTransactionType.EXPORT,
      TaxTransactionType.TAX_ADJUSTMENT
    ]),
    source_document_type: faker.helpers.arrayElement(['invoice', 'receipt', 'credit_note', 'debit_note']),
    source_document_id: generateId(),
    notes: faker.lorem.sentence(),
    is_tax_inclusive: false,
    currency_code: 'USD',
    exchange_rate: 1,
    components: components.map(comp => ({
      tax_component: comp.tax_component,
      tax_rate: comp.tax_rate,
      taxable_amount: comp.taxable_amount,
      tax_amount: comp.tax_amount,
      tax_basis: comp.tax_basis,
      jurisdiction_level: comp.jurisdiction_level,
      jurisdiction_name: comp.jurisdiction_name,
      jurisdiction_code: comp.jurisdiction_code,
      tax_jurisdiction_id: comp.tax_jurisdiction_id,
      tax_type: comp.tax_type,
      tax_category: comp.tax_category,
      tax_authority: comp.tax_authority,
      tax_authority_id: comp.tax_authority_id,
      tax_registration_number: comp.tax_registration_number,
      is_tax_inclusive: comp.is_tax_inclusive,
      tax_exemption_reason: comp.tax_exemption_reason
    })),
    ...overrides
  };
};

// Create a mock tax transaction update DTO
export const createMockTaxTransactionUpdate = (
  overrides: Partial<TaxTransactionUpdate> = {}
): TaxTransactionUpdate => ({
  id: generateId(),
  notes: faker.lorem.sentence(),
  status: faker.helpers.arrayElement([
    TaxTransactionStatus.DRAFT,
    TaxTransactionStatus.POSTED,
    TaxTransactionStatus.VOIDED,
    TaxTransactionStatus.ADJUSTED
  ]),
  ...overrides
});

// Create a mock tax transaction filter
export const createMockTaxTransactionFilter = (
  overrides: Partial<TaxTransactionFilter> = {}
): TaxTransactionFilter => ({
  company_id: generateId(),
  status: faker.helpers.arrayElement([
    TaxTransactionStatus.DRAFT,
    TaxTransactionStatus.POSTED,
    TaxTransactionStatus.VOIDED,
    TaxTransactionStatus.ADJUSTED
  ]),
  transaction_type: faker.helpers.arrayElement([
    TaxTransactionType.SALE,
    TaxTransactionType.PURCHASE,
    TaxTransactionType.USE,
    TaxTransactionType.IMPORT,
    TaxTransactionType.EXPORT,
    TaxTransactionType.TAX_ADJUSTMENT
  ]),
  start_date: faker.date.past().toISOString(),
  end_date: faker.date.recent().toISOString(),
  page: 1,
  page_size: 20,
  ...overrides
});

// Helper to create paginated response
export const createPaginatedResponse = <T>(
  items: T[],
  total: number = items.length,
  page: number = 1,
  pageSize: number = 20
) => ({
  data: items,
  meta: {
    total,
    page,
    page_size: pageSize,
    total_pages: Math.ceil(total / pageSize),
    has_next_page: page * pageSize < total,
    has_previous_page: page > 1
  }
});

// Create a mock API response
export const createMockApiResponse = <T>(
  data: T, 
  status = 200, 
  statusText = 'OK',
  headers: Record<string, string> = {},
  config: any = { headers: {} }
): ApiResponse<T> => ({
  data,
  status,
  statusText,
  headers,
  config: {
    headers: {},
    ...config
  }
});

// Create a mock error response
export const createMockErrorResponse = (status: number, message: string) => ({
  response: {
    status,
    data: { message },
    statusText: 'Error',
    headers: {},
    config: { headers: {} }
  },
  isAxiosError: true,
  toJSON: () => ({}),
  message: `Request failed with status code ${status}`,
  name: 'AxiosError',
  config: { headers: {} }
});
