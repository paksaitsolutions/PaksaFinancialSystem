import { v4 as uuidv4 } from 'uuid';
import type { 
  TaxTransaction, 
  TaxTransactionCreate, 
  TaxTransactionUpdate, 
  TaxTransactionFilter,
  TaxTransactionComponent,
  TaxTransactionStatus,
  TaxTransactionType
} from '../tax';
import type { UUID } from '../common';

/**
 * Test utility functions for tax module
 */

/**
 * Creates a mock tax transaction for testing
 */
export const createMockTransaction = (overrides: Partial<TaxTransaction> = {}): TaxTransaction => {
  const now = new Date().toISOString();
  const transactionId = uuidv4() as UUID;
  const companyId = uuidv4() as UUID;
  const taxRateId = uuidv4() as UUID;
  
  return {
    id: transactionId,
    transaction_date: now,
    posting_date: now,
    document_number: `DOC-${Date.now()}`,
    reference_number: `REF-${Date.now()}`,
    company_id: companyId,
    tax_type: 'VAT',
    tax_rate_id: taxRateId,
    taxable_amount: 1000,
    tax_amount: 150,
    total_amount: 1150,
    status: 'draft' as TaxTransactionStatus,
    transaction_type: 'sale' as TaxTransactionType,
    source_document_type: 'invoice',
    source_document_id: uuidv4() as UUID,
    notes: 'Test transaction',
    created_at: now,
    updated_at: now,
    created_by: companyId,
    updated_by: companyId,
    ...overrides
  };
};

/**
 * Creates a mock tax transaction component for testing
 */
export const createMockTransactionComponent = (
  transactionId: UUID,
  overrides: Partial<TaxTransactionComponent> = {}
): TaxTransactionComponent => {
  const now = new Date().toISOString();
  
  return {
    id: uuidv4(),
    transaction_id: transactionId,
    tax_component: 'VAT',
    tax_rate: 0.15,
    taxable_amount: 1000,
    tax_amount: 150,
    tax_basis: 1000,
    jurisdiction_level: 'country',
    jurisdiction_name: 'Test Country',
    jurisdiction_code: 'TC',
    tax_type: 'VAT',
    tax_category: 'Standard',
    tax_authority: 'Test Authority',
    tax_authority_id: 'AUTH-001',
    tax_registration_number: 'REG-001',
    is_tax_inclusive: false,
    tax_exemption_reason: '',
    tax_exemption_certificate_number: '',
    tax_exemption_certificate_expiry_date: '',
    created_at: now,
    updated_at: now,
    created_by: uuidv4() as UUID,
    updated_by: uuidv4() as UUID,
    ...overrides
  };
};

/**
 * Creates a mock API response for a single entity
 */
export const createMockApiResponse = <T>(data: T, message: string = 'Success') => ({
  data: { data },
  status: 200,
  statusText: 'OK',
  headers: {},
  config: {},
  message,
  success: true
});

/**
 * Creates a mock paginated API response
 */
export const createMockPaginatedResponse = <T>(
  items: T[],
  total: number = items.length,
  page: number = 1,
  pageSize: number = 10
) => {
  const totalPages = Math.ceil(total / pageSize);
  
  return {
    data: {
      items,
      total,
      page,
      page_size: pageSize,
      total_pages: totalPages
    },
    status: 200,
    statusText: 'OK',
    headers: {},
    config: {},
    message: 'Success',
    success: true
  };
};

/**
 * Creates a mock API error response
 */
export const createMockErrorResponse = (
  status: number,
  message: string = 'An error occurred',
  errors: Record<string, string[]> = {}
) => ({
  response: {
    data: {
      message,
      errors,
      status_code: status
    },
    status,
    statusText: status === 404 ? 'Not Found' : 'Error',
    headers: {},
    config: {}
  },
  isAxiosError: true,
  message: `Request failed with status code ${status}`
});

/**
 * Test data factories for consistent test data generation
 */
export const TestData = {
  transactions: {
    draft: (count: number = 3): TaxTransaction[] => 
      Array.from({ length: count }, (_, i) => 
        createMockTransaction({ 
          status: 'draft',
          document_number: `DRAFT-${i + 1}`
        })
      ),
    
    posted: (count: number = 3): TaxTransaction[] => 
      Array.from({ length: count }, (_, i) => 
        createMockTransaction({ 
          status: 'posted',
          document_number: `POSTED-${i + 1}`,
          posting_date: new Date().toISOString()
        })
      ),
    
    voided: (count: number = 2): TaxTransaction[] => 
      Array.from({ length: count }, (_, i) => 
        createMockTransaction({ 
          status: 'voided',
          document_number: `VOIDED-${i + 1}`,
          void_reason: 'Test void reason'
        })
      )
  },
  
  components: (transactionId: UUID, count: number = 2): TaxTransactionComponent[] => 
    Array.from({ length: count }, (_, i) => 
      createMockTransactionComponent(transactionId, {
        tax_component: `COMPONENT-${i + 1}`,
        tax_rate: 0.1 + (i * 0.05) // 10%, 15%, etc.
      })
    )
};

/**
 * Type assertions for test data
 */
declare global {
  // eslint-disable-next-line @typescript-eslint/no-namespace
  namespace jest {
    interface Matchers<R> {
      toBeValidTaxTransaction(): R;
      toBeValidTaxComponent(transactionId: UUID): R;
    }
  }
}

expect.extend({
  toBeValidTaxTransaction(received: TaxTransaction) {
    const requiredFields: Array<keyof TaxTransaction> = [
      'id', 'transaction_date', 'document_number', 'company_id',
      'tax_type', 'tax_rate_id', 'taxable_amount', 'tax_amount',
      'total_amount', 'status', 'transaction_type', 'created_at', 'updated_at'
    ];
    
    const missingFields = requiredFields.filter(field => !(field in received));
    
    if (missingFields.length > 0) {
      return {
        message: () => 
          `Expected a valid TaxTransaction but missing required fields: ${missingFields.join(', ')}`,
        pass: false
      };
    }
    
    return {
      message: () => 'Expected value to be a valid TaxTransaction',
      pass: true
    };
  },
  
  toBeValidTaxComponent(received: TaxTransactionComponent, transactionId: UUID) {
    const requiredFields: Array<keyof TaxTransactionComponent> = [
      'id', 'transaction_id', 'tax_component', 'tax_rate',
      'taxable_amount', 'tax_amount', 'created_at', 'updated_at'
    ];
    
    const missingFields = requiredFields.filter(field => !(field in received));
    
    if (missingFields.length > 0) {
      return {
        message: () => 
          `Expected a valid TaxTransactionComponent but missing required fields: ${missingFields.join(', ')}`,
        pass: false
      };
    }
    
    if (received.transaction_id !== transactionId) {
      return {
        message: () => 
          `Expected component to belong to transaction ${transactionId} but got ${received.transaction_id}`,
        pass: false
      };
    }
    
    return {
      message: () => 'Expected value to be a valid TaxTransactionComponent',
      pass: true
    };
  }
});
