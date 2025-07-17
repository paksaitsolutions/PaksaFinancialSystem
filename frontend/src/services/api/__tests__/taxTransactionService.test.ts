import { describe, it, expect, vi, beforeEach, beforeAll } from 'vitest';
import { TaxTransactionService } from '../taxTransactionService';
import { apiClient } from '@/utils/apiClient';
import { 
  createMockTaxTransaction,
  createMockTaxTransactionComponent,
  createMockApiResponse,
  createMockErrorResponse 
} from '@/test-utils/tax-test-utils';

import { 
  TaxTransactionType,
  TaxTransactionStatus
} from '@/types/tax';

import type { 
  TaxTransaction, 
  TaxTransactionCreate, 
  TaxTransactionComponent,
  TaxTransactionUpdate
} from '@/types/tax';

import type { ApiResponse } from '@/types/common';

declare module 'vitest' {
  interface Assertion<T = any> {
    toBeValidTaxTransaction(): void;
    toBeValidTaxComponent(transactionId: string): void;
  }
}

// Mock the apiClient
vi.mock('@/utils/apiClient', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    defaults: {}
  }
}));

const mockApiClient = vi.mocked(apiClient);

// Create test data
let mockTransaction: TaxTransaction;
let mockComponents: TaxTransactionComponent[];
let mockTaxRateId: string;
let mockCompanyId: string;

beforeAll(() => {
  // Generate consistent IDs for testing
  mockCompanyId = '550e8400-e29b-41d4-a716-446655440000';
  mockTaxRateId = '550e8400-e29b-41d4-a716-446655440001';
  
  // Initialize test data with consistent IDs and required fields
  mockTransaction = createMockTaxTransaction({
    id: '550e8400-e29b-41d4-a716-446655440002',
    document_number: 'TX-001',
    reference_number: 'REF-001',
    company_id: mockCompanyId,
    tax_rate_id: mockTaxRateId,
    status: TaxTransactionStatus.DRAFT,
    transaction_type: TaxTransactionType.SALE,
    tax_type: 'VAT',
    taxable_amount: 1000,
    tax_amount: 150,
    total_amount: 1150,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z',
    created_by: '550e8400-e29b-41d4-a716-446655440003',
    tax_jurisdiction_id: '550e8400-e29b-41d4-a716-446655440004',
    jurisdiction_code: 'US-CA',
    source_document_type: 'invoice',
    source_document_id: '550e8400-e29b-41d4-a716-446655440005'
  });
  
  // Create consistent mock components
  mockComponents = [
    createMockTaxTransactionComponent({ 
      id: '550e8400-e29b-41d4-a716-446655440006',
      transaction_id: mockTransaction.id,
      tax_component: 'VAT',
      tax_rate: 0.15,
      taxable_amount: 1000,
      tax_amount: 150,
      tax_jurisdiction_id: '550e8400-e29b-41d4-a716-446655440004',
      jurisdiction_code: 'US-CA',
      jurisdiction_level: 'state',
      jurisdiction_name: 'California',
      tax_type: 'VAT',
      tax_category: 'Standard',
      created_at: '2023-01-01T00:00:00Z',
      updated_at: '2023-01-01T00:00:00Z'
    })
  ];
  
  // Add components to the mock transaction
  mockTransaction.components = [...mockComponents];
});

// Add custom matcher for validating TaxTransactionComponent
declare global {
  namespace jest {
    interface Matchers<R> {
      toBeValidTaxTransaction(): R;
      toBeValidTaxComponent(transactionId: string): R;
    }
  }
}

expect.extend({
  toBeValidTaxTransaction(received: TaxTransaction) {
    const requiredFields: (keyof TaxTransaction)[] = [
      'id', 'transaction_type', 'tax_type', 'tax_rate', 'taxable_amount', 'tax_amount', 'total_amount'
    ];

    const missingFields = requiredFields.filter(
      field => !(field in received)
    );

    if (missingFields.length > 0) {
      return {
        message: () =>
          `Expected a valid TaxTransaction but is missing required fields: ${missingFields.join(', ')}`,
        pass: false,
      };
    }

    return {
      message: () => 'Expected a valid TaxTransaction',
      pass: true,
    };
  },
  
  toBeValidTaxComponent(received: TaxTransactionComponent, transactionId: string) {
    const requiredFields: (keyof TaxTransactionComponent)[] = [
      'id', 'transaction_id', 'tax_rate', 'taxable_amount', 'tax_amount'
    ];

    const missingFields = requiredFields.filter(
      field => !(field in received)
    );

    if (missingFields.length > 0) {
      return {
        message: () =>
          `Expected a valid TaxTransactionComponent but is missing required fields: ${missingFields.join(', ')}`,
        pass: false,
      };
    }

    if (received.transaction_id !== transactionId) {
      return {
        message: () => `Expected component to belong to transaction ${transactionId}, got ${received.transaction_id}`,
        pass: false,
      };
    }

    return {
      message: () => 'Expected a valid TaxTransactionComponent',
      pass: true,
    };
  }
});

describe('TaxTransactionService', () => {
  let service: TaxTransactionService;

  beforeEach(() => {
    vi.clearAllMocks();
    service = new TaxTransactionService();
  });

  describe('createTransaction', () => {
    it('should create a new tax transaction with minimal required fields', async () => {
      // Arrange
      const transactionData: TaxTransactionCreate = {
        transaction_date: '2023-01-01',
        tax_rate: 0.1, // Changed from tax_rate_id to tax_rate
        taxable_amount: 1000,
        tax_amount: 100,
        total_amount: 1100,
        document_number: 'TX-001',
        tax_type: 'VAT',
        transaction_type: TaxTransactionType.SALE,
        status: TaxTransactionStatus.DRAFT,
        company_id: mockCompanyId,
        // Removed currency as it's not part of TaxTransactionCreate
        components: [
          {
            tax_component: 'VAT',
            tax_rate: 0.1,
            taxable_amount: 1000,
            tax_amount: 100,
            tax_type: 'VAT',
            tax_category: 'STANDARD',
            tax_authority: 'FEDERAL_TAX_AUTHORITY',
            tax_authority_id: 'AUTH-123',
            tax_registration_number: 'REG-123',
            is_tax_inclusive: false,
            jurisdiction_level: 'FEDERAL',
            jurisdiction_name: 'Federal',
            jurisdiction_code: 'FED',
            tax_jurisdiction_id: 'JUR-123',
            tax_exemption_reason: 'NON_PROFIT',
            tax_exemption_certificate_number: 'EXEMPT-123',
            tax_exemption_certificate_expiry_date: '2025-12-31',
            notes: 'Standard VAT component',
            custom_fields: {}
          }
        ]
      };

      mockApiClient.post.mockResolvedValueOnce(
        createMockApiResponse(
          { transaction: mockTransaction },
          201,
          'Created'
        )
      );

      // Act
      const result = await service.createTransaction(transactionData);

      // Assert
      expect(result).toBeValidTaxTransaction();
      expect(result).toMatchObject({
        id: expect.any(String),
        document_number: 'TX-001',
        tax_type: 'VAT',
        transaction_type: TaxTransactionType.SALE,
        status: TaxTransactionStatus.DRAFT
      });
      expect(mockApiClient.post).toHaveBeenCalledWith(
        '/api/v1/tax/transactions',
        expect.objectContaining({
          document_number: 'TX-001',
          tax_type: 'VAT',
          transaction_type: TaxTransactionType.SALE
        })
      );
    });

    it('should handle validation errors', async () => {
      // Arrange
      const createData: Partial<TaxTransactionCreate> = {
        // Missing required fields
        transaction_date: '2023-01-01',
        document_number: 'TX-001'
      } as unknown as TaxTransactionCreate;

      const error = createMockErrorResponse(400, 'Validation failed', {
        errors: {
          company_id: ['This field is required'],
          tax_type: ['This field is required'],
          tax_rate_id: ['This field is required'],
          tax_jurisdiction_id: ['This field is required'],
          transaction_type: ['This field is required']
        }
      });

      mockApiClient.post.mockRejectedValueOnce(error);

      // Act & Assert
      await expect(service.createTransaction({
        ...createData,
        transaction_date: '2023-01-01'
      } as TaxTransactionCreate))
      .rejects
      .toMatchObject({
        response: {
          status: 400,
          data: {
            message: 'Validation failed',
            errors: {
              transaction_type: ['This field is required']
            }
          }
        }
      });
    });

    it('should handle network errors', async () => {
      // Arrange
      const transactionData: TaxTransactionCreate = {
        transaction_type: TaxTransactionType.SALE,
        tax_type: 'VAT',
        taxable_amount: 1000,
        tax_amount: 150,
        total_amount: 1150,
        tax_rate_id: mockTaxRateId,
        tax_jurisdiction_id: '550e8400-e29b-41d4-a716-446655440004',
        jurisdiction_code: 'US-CA',
        source_document_type: 'invoice',
        source_document_id: 'doc-12345',
        transaction_date: new Date().toISOString(),
        currency: 'USD'
      };

      const networkError = new Error('Network Error');
      mockApiClient.post.mockRejectedValueOnce(networkError);

      // Act & Assert
      await expect(service.createTransaction(transactionData))
        .rejects
        .toThrow('Network Error');
    });

    it('should handle invalid response data', async () => {
      // Arrange
      const transactionData: TaxTransactionCreate = {
        transaction_type: TaxTransactionType.SALE,
        tax_type: 'VAT',
        taxable_amount: 1000,
        tax_amount: 150,
        total_amount: 1150,
        tax_rate_id: mockTaxRateId,
        tax_jurisdiction_id: '550e8400-e29b-41d4-a716-446655440004',
        jurisdiction_code: 'US-CA',
        source_document_type: 'invoice',
        source_document_id: 'doc-12345',
        transaction_date: new Date().toISOString(),
        currency: 'USD'
      };

      // Mock a response with invalid data structure
      mockApiClient.post.mockResolvedValueOnce({
        data: {
          // Missing required transaction field
          status: 'success'
        },
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {}
      });

      // Act & Assert
      await expect(service.createTransaction(transactionData))
        .rejects
        .toThrow('Invalid transaction data received from server');
    });

    it('should handle concurrent transaction creation', async () => {
      // Arrange
      const transactionData: TaxTransactionCreate = {
        transaction_type: TaxTransactionType.SALE,
        tax_type: 'VAT',
        taxable_amount: 1000,
        tax_amount: 150,
        total_amount: 1150,
        tax_rate_id: mockTaxRateId,
        tax_jurisdiction_id: '550e8400-e29b-41d4-a716-446655440004',
        jurisdiction_code: 'US-CA',
        source_document_type: 'invoice',
        source_document_id: 'doc-12345',
        transaction_date: new Date().toISOString(),
        currency: 'USD'
      };

      // Mock two different responses for concurrent requests
      const mockResponse1 = createMockApiResponse(
        { 
          transaction: { 
            ...mockTransaction, 
            id: 'tx-001',
            document_number: 'TX-001' 
          } 
        },
        201,
        'Created'
      );

      const mockResponse2 = createMockApiResponse(
        { 
          transaction: { 
            ...mockTransaction, 
            id: 'tx-002',
            document_number: 'TX-002' 
          } 
        },
        201,
        'Created'
      );

      mockApiClient.post
        .mockResolvedValueOnce(mockResponse1)
        .mockResolvedValueOnce(mockResponse2);

      // Act
      const [result1, result2] = await Promise.all([
        service.createTransaction(transactionData),
        service.createTransaction(transactionData)
      ]);

      // Assert
      expect(result1.document_number).toBe('TX-001');
      expect(result2.document_number).toBe('TX-002');
      expect(mockApiClient.post).toHaveBeenCalledTimes(2);
    });

    it('should create a transaction with components', async () => {
      // Arrange
      const transactionData: TaxTransactionCreate = {
        transaction_type: TaxTransactionType.SALE,
        transaction_date: new Date().toISOString(),
        tax_type: 'sales',
        tax_rate_id: mockTaxRateId,
        tax_jurisdiction_id: '550e8400-e29b-41d4-a716-446655440004',
        jurisdiction_code: 'US-CA',
        source_document_type: 'invoice',
        source_document_id: 'doc-12345',
        taxable_amount: 2000,
        tax_amount: 400,
        total_amount: 2400,
        components: [
          {
            tax_rate_id: mockTaxRateId,
            tax_amount: 200,
            taxable_amount: 1000,
            tax_rate: 0.2,
            tax_type: 'VAT-STANDARD',
            tax_code: 'STANDARD',
            tax_name: 'Standard VAT',
            tax_jurisdiction_id: '550e8400-e29b-41d4-a716-446655440004',
            jurisdiction_code: 'US-CA',
            is_tax_inclusive: false,
            description: 'Standard VAT component'
          },
          {
            tax_rate_id: '550e8400-e29b-41d4-a716-446655440006',
            tax_amount: 200,
            taxable_amount: 1000,
            tax_rate: 0.2,
            tax_type: 'VAT-REDUCED',
            tax_code: 'REDUCED',
            tax_name: 'Reduced VAT',
            tax_jurisdiction_id: '550e8400-e29b-41d4-a716-446655440004',
            jurisdiction_code: 'US-CA',
            is_tax_inclusive: false,
            description: 'Reduced VAT component'
          }
        ]
      };

      const mockResponse = {
        data: { 
          transaction: {
            ...mockTransaction,
            components: transactionData.components?.map(comp => ({
              ...comp,
              id: 'comp-123',
              transaction_id: mockTransaction.id,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
              created_by: 'user-123',
              updated_by: 'user-123'
            })) || []
          }
        },
        status: 201,
        statusText: 'Created',
        headers: {},
        config: {}
      };

      mockApiClient.post.mockResolvedValueOnce(mockResponse);

      // Act
      const result = await service.createTransaction(transactionData);

      // Assert
      expect(result.components).toHaveLength(2);
      expect(result.components[0].tax_type).toBe('VAT-STANDARD');
      expect(result.components[1].tax_type).toBe('VAT-REDUCED');
      expect(mockApiClient.post).toHaveBeenCalledWith(
        '/api/v1/tax/transactions',
        expect.objectContaining({
          components: expect.arrayContaining([
            expect.objectContaining({ tax_type: 'VAT-STANDARD' }),
            expect.objectContaining({ tax_type: 'VAT-REDUCED' })
          ])
        })
      );
    });

    it('should create a transaction with metadata', async () => {
      // Arrange
      const transactionData: TaxTransactionCreate = {
        transaction_type: TaxTransactionType.PURCHASE,
        transaction_date: new Date().toISOString(),
        tax_type: 'purchase',
        tax_rate: 10,
        total_amount: 1150,
        tax_rate_id: mockTaxRateId,
        tax_jurisdiction_id: '550e8400-e29b-41d4-a716-446655440004',
        jurisdiction_code: 'US-CA',
        source_document_type: 'invoice',
        source_document_id: 'doc-12345',
        currency: 'USD',
        custom_fields: {
          custom1: 'value1',
          custom2: 123,
          custom3: true
        },
        metadata: {
          internal_reference: 'INT-001',
          department: 'SALES'
        },
        tags: ['ecommerce', 'high-value']
      };

      const mockResponse = {
        data: { 
          transaction: {
            ...mockTransaction,
            custom_fields: transactionData.custom_fields,
            metadata: transactionData.metadata,
            tags: transactionData.tags
          }
        },
        status: 201,
        statusText: 'Created',
        headers: {},
        config: {}
      };

      mockApiClient.post.mockResolvedValueOnce(mockResponse);

      // Act
      const result = await service.createTransaction(transactionData);

      // Assert
      expect(result.custom_fields).toEqual({
        custom1: 'value1',
        custom2: 123,
        custom3: true
      });
      expect(result.metadata).toEqual({
        internal_reference: 'INT-001',
        department: 'SALES'
      });
      expect(result.tags).toEqual(['ecommerce', 'high-value']);
    });

    it('should create a transaction with different tax rate', async () => {
      // Arrange
      const transactionData: TaxTransactionCreate = {
        transaction_type: TaxTransactionType.SALE,
        transaction_date: new Date().toISOString(),
        tax_type: 'sales',
        tax_rate: 17,
        taxable_amount: 1000,
        tax_amount: 170,
        total_amount: 1170,
        tax_rate_id: mockTaxRateId,
        tax_jurisdiction_id: '550e8400-e29b-41d4-a716-446655440004',
        jurisdiction_code: 'US-CA',
        source_document_type: 'invoice',
        source_document_id: 'doc-12345'
      };

      const mockResponse = {
        data: { 
          transaction: {
            ...mockTransaction,
            ...transactionData
          }
        },
        status: 201,
        statusText: 'Created',
        headers: {},
        config: {}
      };

      mockApiClient.post.mockResolvedValueOnce(mockResponse);

      // Act
      const result = await service.createTransaction(transactionData);

      // Assert
      expect(result.tax_rate).toBe(17);
      expect(mockApiClient.post).toHaveBeenCalledWith(
        '/api/v1/tax/transactions',
        expect.objectContaining({
          tax_rate: 17,
          tax_amount: 170,
          total_amount: 1170
        })
      );
    });
  });

  describe('getTransaction', () => {
    it('should retrieve a tax transaction by ID', async () => {
      // Arrange
      const transactionId = '550e8400-e29b-41d4-a716-446655440002';
      
      mockApiClient.get.mockResolvedValueOnce({
        data: { transaction: mockTransaction },
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {}
      });

      // Act
      const result = await service.getTransaction(transactionId);

      // Assert
      expect(result).toBeValidTaxTransaction();
      expect(mockApiClient.get).toHaveBeenCalledWith(
        `/api/v1/tax/transactions/${transactionId}`
      );
    });

    it('should handle transaction not found', async () => {
      // Arrange
      const transactionId = 'non-existent-id';
      const error = createMockErrorResponse(404, 'Transaction not found');
      mockApiClient.get.mockRejectedValueOnce(error);

      // Act & Assert
      await expect(service.getTransaction(transactionId))
        .rejects
        .toMatchObject({
          response: {
            status: 404,
            data: {
              message: 'Transaction not found'
            }
          }
        });
    });
  });

  describe('updateTransaction', () => {
    it('should update an existing transaction', async () => {
      // Arrange
      const transactionId = '550e8400-e29b-41d4-a716-446655440002';
      const updateData: TaxTransactionUpdate = {
        notes: 'Updated notes',
        metadata: {
          updated_by: 'user123',
          update_reason: 'Customer requested changes'
        }
      };

      const updatedTransaction = {
        ...mockTransaction,
        ...updateData,
        updated_at: new Date().toISOString()
      };

      mockApiClient.put.mockResolvedValueOnce({
        data: { transaction: updatedTransaction },
        status: 200,
        statusText: 'OK',
      expect(mockApiClient.put).toHaveBeenCalledWith(
        `/api/v1/tax/transactions/${transactionId}`,
        updateData
      );
    });
  });

  describe('deleteTransaction', () => {
    it('should delete a transaction', async () => {
      // Arrange
      const transactionId = '550e8400-e29b-41d4-a716-446655440002';
      
      mockApiClient.delete.mockResolvedValueOnce({
        data: { success: true },
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {}
      });

      // Act
      await service.deleteTransaction(transactionId);

      // Assert
      expect(mockApiClient.delete).toHaveBeenCalledWith(
        `/api/v1/tax/transactions/${transactionId}`
      );
    });
  });

  describe('getTransactionComponents', () => {
    it('should fetch transaction components', async () => {
      // Arrange
      const transactionId = mockTransaction.id;
      
      const mockResponse: ApiResponse<{ components: TaxTransactionComponent[] }> = {
        data: { components: mockComponents },
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {}
      };
      
      mockApiClient.get.mockResolvedValueOnce(
        createMockApiResponse({ components: mockComponents })
      );

      // Act
      const result = await service.getTransactionComponents(transactionId);

      // Assert
      expect(Array.isArray(result)).toBe(true);
      result.forEach(component => {
        expect(component).toBeValidTaxComponent(transactionId);
      });
      expect(mockApiClient.get).toHaveBeenCalledWith(
        `/api/v1/tax/transactions/${transactionId}/components`
      );
    });

    it('should return empty array for transaction with no components', async () => {
      // Arrange
      const transactionId = mockTransaction.id;
      
      mockApiClient.get.mockResolvedValueOnce(
        createMockApiResponse({ components: [] })
      );

      // Act
      const result = await service.getTransactionComponents(transactionId);

      // Assert
      expect(result).toEqual([]);
    });
  });

  describe('voidTransaction', () => {
    it('should void a transaction', async () => {
      // Test data
      const transactionId = 'txn_123';
      const voidReason = 'Test void reason';
      const mockTransaction = {
        ...createMockTaxTransaction(),
        status: 'voided' as const,
        void_reason: voidReason
      };

      // Mock API response
      (mockApiClient.post as any).mockResolvedValueOnce({
        data: { transaction: mockTransaction }
      });

      // Act
      const result = await service.voidTransaction(transactionId, voidReason);

      // Assert
      expect(result).toBeValidTaxTransaction();
      expect(result.status).toBe('voided');
      expect((result as any).void_reason).toBe(voidReason);
      expect(mockApiClient.post).toHaveBeenCalledWith(
        `/api/v1/tax/transactions/${transactionId}/void`,
        { reason: voidReason }
      );
    });

    it('should require a void reason', async () => {
      // Arrange
      const transactionId = mockTransaction.id;
      const error = createMockErrorResponse(400, 'Void reason is required');
      mockApiClient.post.mockRejectedValueOnce(error);

      // Act & Assert
      await expect(service.voidTransaction(transactionId, ''))
        .rejects
        .toThrow('Void reason is required');
    });
  });

  describe('exportTransactions', () => {
    it('should export transactions in the specified format', async () => {
      // Arrange
      const mockBlob = new Blob(['test'], { type: 'text/csv' });
      const params = {
        format: 'csv' as const,
        start_date: '2023-01-01',
        end_date: '2023-12-31',
        status: TaxTransactionStatus.POSTED as const
      };

      mockApiClient.get.mockResolvedValueOnce(mockBlob);

      // Act
      const result = await service.exportTransactions(params);

      // Assert
      expect(result).toBeInstanceOf(Blob);
      expect(mockApiClient.get).toHaveBeenCalledWith(
        '/api/v1/tax/transactions/export/csv',
        {
          params: {
            start_date: expect.any(String),
            end_date: expect.any(String),
            status: 'posted'
          },
          responseType: 'blob',
        }
      );
    });

    it('should handle export errors', async () => {
      // Arrange
      const params = {
        format: 'csv' as const,
        start_date: '2023-01-01',
        end_date: '2023-12-31',
        status: undefined
      };

      const error = createMockErrorResponse(500, 'Export failed');
      mockApiClient.get.mockRejectedValueOnce(error);

      // Act & Assert
      await expect(service.exportTransactions(params))
        .rejects
        .toThrow('Export failed');
    });
  });

  describe('error handling', () => {
    it('should handle network errors', async () => {
      // Arrange
      const error = new Error('Network error');
      mockApiClient.get.mockRejectedValueOnce(error);

      // Act & Assert
      await expect(service.getTransaction('test-id' as UUID))
        .rejects
        .toThrow('Network error');
    });

    it('should handle API error responses with validation errors', async () => {
      // Arrange
      const error = createMockErrorResponse(422, 'Validation failed', {
        start_date: ['Must be a valid date'],
        end_date: ['Must be after start date']
      });
      
      mockApiClient.get.mockRejectedValueOnce(error);

      // Act & Assert
      await expect(service.listTransactions({
        start_date: 'invalid-date',
        end_date: '2022-01-01'
      })).rejects.toThrow('Validation failed');
    });

    it('should handle unauthorized access', async () => {
      // Arrange
      const error = createMockErrorResponse(401, 'Unauthorized');
      mockApiClient.get.mockRejectedValueOnce(error);

      // Act & Assert
      await expect(service.getTransaction('test-id' as UUID))
        .rejects
        .toThrow('Unauthorized');
    });
  });

  describe('edge cases', () => {
    it('should handle concurrent updates', async () => {
      // This would test optimistic concurrency control if implemented
      // For now, we'll just test that we can make concurrent requests
      const transactionId = mockTransaction.id;
      const updates = [
        { description: 'Update 1' },
        { description: 'Update 2' }
      ];

      mockApiClient.put
        .mockResolvedValueOnce(createMockApiResponse({ 
          transaction: { ...mockTransaction, description: 'Update 1' } 
        }))
        .mockResolvedValueOnce(createMockApiResponse({ 
          transaction: { ...mockTransaction, description: 'Update 2' } 
        }));

      // Execute concurrent updates
      const [result1, result2] = await Promise.all([
        service.updateTransaction(transactionId, { description: 'Update 1' }),
        service.updateTransaction(transactionId, { description: 'Update 2' })
      ]);

      expect(result1.description).toBe('Update 1');
      expect(result2.description).toBe('Update 2');
      expect(mockApiClient.put).toHaveBeenCalledTimes(2);
    });
  });
});
