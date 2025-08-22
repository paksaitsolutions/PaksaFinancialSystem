import BaseService from '@/shared/api/base.service';
import type { 
  GlAccount, 
  CreateGlAccountDto, 
  UpdateGlAccountDto, 
  GlAccountFilters,
  GlAccountImportDto,
  GlAccountExportDto,
  GlAccountSummary,
  GlAccountType,
  GlAccountBalanceHistory,
  GlAccountTree,
  AccountStatus,
  AccountCategory,
  GlAccountReconcileDto,
  GlAccountMoveDto,
  GlAccountBulkUpdateDto
} from '../types/gl-account';







class GlAccountService extends BaseService {
  constructor() {
    super('gl/accounts');
  }

  /**
   * Fetch all GL accounts with optional filters and pagination
   * @param filters Filter criteria for accounts
   * @param includeInactive Whether to include inactive accounts
   * @param includeSystemAccounts Whether to include system accounts
   * @returns Paginated list of GL accounts
   */
  async fetchAccounts(
    filters?: GlAccountFilters,
    includeInactive = false,
    includeSystemAccounts = false
  ): Promise<{ data: GlAccount[]; total: number }> {
    return this.get<{ data: GlAccount[]; total: number }>('', { 
      params: { 
        ...filters, 
        includeInactive: String(includeInactive),
        includeSystemAccounts: String(includeSystemAccounts)
      } 
    });
  }

  /**
   * Fetch a single GL account by ID
   */
  async fetchAccountById(id: string | number): Promise<GlAccount> {
    return this.get<GlAccount>(`/${id}`);
  }

  /**
   * Create a new GL account
   */
  async createAccount(accountData: CreateGlAccountDto): Promise<GlAccount> {
    return this.post<GlAccount>('', accountData);
  }

  /**
   * Update an existing GL account
   */
  async updateAccount(id: string | number, accountData: UpdateGlAccountDto): Promise<GlAccount> {
    return this.put<GlAccount>(`/${id}`, accountData);
  }

  /**
   * Delete a GL account
   */
  async deleteAccount(id: string | number): Promise<void> {
    return this.delete(`/${id}`);
  }

  /**
   * Import GL accounts from file
   */
  async importAccounts(importData: GlAccountImportDto): Promise<{ success: boolean; message: string }> {
    return this.post<{ success: boolean; message: string }>('/import', importData);
  }

  /**
   * Export GL accounts based on filters
   */
  async exportAccounts(filters?: GlAccountFilters): Promise<GlAccountExportDto[]> {
    return this.get<GlAccountExportDto[]>('/export', { params: filters });
  }

  /**
   * Get GL account summary
   */
  async getAccountSummary(): Promise<GlAccountSummary> {
    return this.get<GlAccountSummary>('/summary');
  }

  /**
   * Get GL accounts by type
   */
  async getAccountsByType(type: GlAccountType): Promise<GlAccount[]> {
    return this.get<GlAccount[]>(`/type/${type}`);
  }

  /**
   * Get complete GL account hierarchy as a tree structure
   * @param includeInactive Whether to include inactive accounts
   * @param includeSystemAccounts Whether to include system accounts
   * @returns Full account hierarchy as a tree
   */
  async getFullAccountHierarchy(
    includeInactive = false,
    includeSystemAccounts = false
  ): Promise<GlAccountTree> {
    return this.get<GlAccountTree>('/hierarchy/full', {
      params: {
        includeInactive: String(includeInactive),
        includeSystemAccounts: String(includeSystemAccounts)
      }
    });
  }

  /**
   * Get GL account hierarchy starting from a specific parent
   * @param parentId Parent account ID (null for root level)
   * @param includeInactive Whether to include inactive accounts
   * @returns Account hierarchy starting from the specified parent
   */
  async getAccountHierarchy(
    parentId?: string | number | null,
    includeInactive = false
  ): Promise<GlAccountTree[]> {
    const url = parentId ? `/hierarchy/${parentId}` : '/hierarchy';
    return this.get<GlAccountTree[]>(url, {
      params: { includeInactive: String(includeInactive) }
    });
  }

  /**
   * Get a flattened list of accounts in hierarchical order
   * @param includeInactive Whether to include inactive accounts
   * @returns Flattened list of accounts with proper indentation
   */
  async getFlattenedHierarchy(includeInactive = false): Promise<GlAccount[]> {
    return this.get<GlAccount[]>('/hierarchy/flattened', {
      params: { includeInactive: String(includeInactive) }
    });
  }

  /**
   * Generate account number based on account type
   */
  async generateAccountNumber(accountType: string): Promise<{ accountNumber: string }> {
    return this.get<{ accountNumber: string }>('/generate-account-number', { 
      params: { accountType } 
    });
  }

  /**
   * Check if account number is available
   */
  async checkAccountNumberAvailability(accountNumber: string): Promise<{ available: boolean }> {
    return this.get<{ available: boolean }>('/check-account-number', { 
      params: { accountNumber } 
    });
  }

  /**
   * Get account balance history with optional filters
   */
  async getAccountBalanceHistory(
    accountId: string | number, 
    options?: { 
      startDate?: string; 
      endDate?: string;
      includeChildAccounts?: boolean;
      groupBy?: 'day' | 'week' | 'month' | 'quarter' | 'year';
    }
  ): Promise<GlAccountBalanceHistory[]> {
    return this.get<GlAccountBalanceHistory[]>(`/${accountId}/balance-history`, { 
      params: {
        includeChildAccounts: options?.includeChildAccounts ? 'true' : 'false',
        groupBy: options?.groupBy || 'day',
        ...(options?.startDate && { startDate: options.startDate }),
        ...(options?.endDate && { endDate: options.endDate })
      }
    });
  }

  /**
   * Move an account to a new parent or position in the hierarchy
   */
  async moveAccount(moveData: GlAccountMoveDto): Promise<GlAccount> {
    return this.post<GlAccount>('/move', moveData);
  }

  /**
   * Bulk update accounts
   */
  async bulkUpdate(updateData: GlAccountBulkUpdateDto): Promise<{ updated: number }> {
    return this.patch<{ updated: number }>('/bulk-update', updateData);
  }

  /**
   * Reconcile an account
   */
  async reconcileAccount(reconcileData: GlAccountReconcileDto): Promise<GlAccount> {
    return this.post<GlAccount>(`/${reconcileData.accountId}/reconcile`, reconcileData);
  }

  /**
   * Get reconciliation history for an account
   */
  async getReconciliationHistory(accountId: string | number): Promise<Array<{
    id: string;
    statementDate: string;
    statementBalance: number;
    systemBalance: number;
    difference: number;
    reconciledBy: string;
    reconciledAt: string;
    notes?: string;
  }>> {
    return this.get(`/${accountId}/reconciliation-history`);
  }

  /**
   * Lock or unlock an account
   */
  async setAccountLock(accountId: string | number, locked: boolean): Promise<GlAccount> {
    return this.patch<GlAccount>(`/${accountId}/lock`, { isLocked: locked });
  }

  /**
   * Get account activity log
   */
  async getAccountActivity(
    accountId: string | number,
    options?: { 
      startDate?: string; 
      endDate?: string;
      limit?: number;
      offset?: number;
    }
  ): Promise<{
    items: Array<{
      id: string;
      action: 'created' | 'updated' | 'deleted' | 'reconciled' | 'locked' | 'unlocked';
      timestamp: string;
      userId: string;
      userName: string;
      changes?: Record<string, { oldValue: any; newValue: any }>;
      ipAddress?: string;
    }>;
    total: number;
  }> {
    return this.get(`/${accountId}/activity`, { params: options });
  }
}

// Error handling is implemented in BaseService, a global error handling service
export const glAccountService = new GlAccountService();
