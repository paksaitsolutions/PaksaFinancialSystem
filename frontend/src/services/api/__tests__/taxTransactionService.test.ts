import { describe, it, expect, vi, beforeEach } from 'vitest';
import { taxTransactionService } from '../taxTransactionService';

describe('TaxTransactionService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should create tax transaction', async () => {
    const mockTransaction = {
      id: '1',
      amount: 100,
      taxRate: 0.1,
      taxAmount: 10
    };

    const result = await taxTransactionService.create(mockTransaction);
    expect(result).toBeDefined();
  });

  it('should get tax transactions', async () => {
    const result = await taxTransactionService.getAll();
    expect(Array.isArray(result)).toBe(true);
  });

  it('should update tax transaction', async () => {
    const mockTransaction = {
      id: '1',
      amount: 200,
      taxRate: 0.15,
      taxAmount: 30
    };

    const result = await taxTransactionService.update('1', mockTransaction);
    expect(result).toBeDefined();
  });

  it('should delete tax transaction', async () => {
    const result = await taxTransactionService.delete('1');
    expect(result).toBe(true);
  });
});