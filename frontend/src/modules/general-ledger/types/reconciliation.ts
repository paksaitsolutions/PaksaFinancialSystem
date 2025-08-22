/**
 * Reconciliation Module Types
 * 
 * This file contains TypeScript interfaces and types for the General Ledger Reconciliation feature.
 */

/** Status of a reconciliation */
export enum ReconciliationStatus {
  DRAFT = 'draft',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  CANCELLED = 'cancelled'
}

/** Status of an account within a reconciliation */
export enum AccountReconciliationStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  RECONCILED = 'reconciled',
  DISPUTED = 'disputed'
}

/** Reconciliation account details */
export interface ReconciliationAccount {
  /** Unique identifier for the reconciliation account entry */
  id: string;
  
  /** Reference to the GL account ID */
  accountId: string;
  
  /** GL account code */
  accountCode: string;
  
  /** GL account name */
  accountName: string;
  
  /** Opening balance as per the system */
  openingBalance: number;
  
  /** Reconciled balance as per the bank/statement */
  reconciledBalance: number | null;
  
  /** Difference between system and reconciled balance */
  difference: number;
  
  /** Status of this account's reconciliation */
  status: AccountReconciliationStatus;
  
  /** Date when the account was reconciled */
  reconciledAt: string | null;
  
  /** ID of the user who reconciled this account */
  reconciledBy: string | null;
  
  /** Notes or comments about the reconciliation */
  notes: string | null;
  
  /** Timestamp when the record was created */
  createdAt: string;
  
  /** Timestamp when the record was last updated */
  updatedAt: string;
}

/** Reconciliation document */
export interface Reconciliation {
  /** Unique identifier for the reconciliation */
  id: string;
  
  /** Reference number for the reconciliation */
  referenceNumber: string;
  
  /** Description of the reconciliation */
  description: string;
  
  /** Status of the reconciliation */
  status: ReconciliationStatus;
  
  /** Start date of the reconciliation period */
  startDate: string;
  
  /** End date of the reconciliation period */
  endDate: string;
  
  /** Date when the reconciliation was performed */
  reconciliationDate: string;
  
  /** ID of the user who created the reconciliation */
  createdBy: string;
  
  /** Name of the user who created the reconciliation */
  createdByName: string;
  
  /** ID of the user who last updated the reconciliation */
  updatedBy: string;
  
  /** Name of the user who last updated the reconciliation */
  updatedByName: string;
  
  /** Date when the reconciliation was completed */
  completedAt: string | null;
  
  /** ID of the user who completed the reconciliation */
  completedBy: string | null;
  
  /** Date when the reconciliation was approved */
  approvedAt: string | null;
  
  /** ID of the user who approved the reconciliation */
  approvedBy: string | null;
  
  /** Rejection reason if the reconciliation was rejected */
  rejectionReason: string | null;
  
  /** ID of the user who rejected the reconciliation */
  rejectedBy: string | null;
  
  /** Date when the reconciliation was rejected */
  rejectedAt: string | null;
  
  /** Notes or comments about the reconciliation */
  notes: string | null;
  
  /** List of accounts included in this reconciliation */
  accounts: ReconciliationAccount[];
  
  /** Total number of accounts in the reconciliation */
  totalAccounts: number;
  
  /** Number of reconciled accounts */
  reconciledAccounts: number;
  
  /** Number of pending accounts */
  pendingAccounts: number;
  
  /** Total difference amount across all accounts */
  totalDifference: number;
  
  /** Timestamp when the record was created */
  createdAt: string;
  
  /** Timestamp when the record was last updated */
  updatedAt: string;
}

/** Reconciliation transaction details */
export interface ReconciliationTransaction {
  /** Unique identifier for the transaction */
  id: string;
  
  /** Reference to the reconciliation ID */
  reconciliationId: string;
  
  /** Reference to the account ID */
  accountId: string;
  
  /** Transaction date */
  transactionDate: string;
  
  /** Transaction reference number */
  referenceNumber: string;
  
  /** Transaction description */
  description: string;
  
  /** Transaction amount */
  amount: number;
  
  /** Transaction type (debit/credit) */
  type: 'debit' | 'credit';
  
  /** Whether the transaction is reconciled */
  isReconciled: boolean;
  
  /** Date when the transaction was reconciled */
  reconciledAt: string | null;
  
  /** ID of the user who reconciled the transaction */
  reconciledBy: string | null;
  
  /** Notes or comments about the transaction */
  notes: string | null;
  
  /** Timestamp when the record was created */
  createdAt: string;
  
  /** Timestamp when the record was last updated */
  updatedAt: string;
}

/** Reconciliation summary statistics */
export interface ReconciliationStats {
  /** Total number of reconciliations */
  totalReconciliations: number;
  
  /** Number of draft reconciliations */
  draftCount: number;
  
  /** Number of in-progress reconciliations */
  inProgressCount: number;
  
  /** Number of completed reconciliations */
  completedCount: number;
  
  /** Number of approved reconciliations */
  approvedCount: number;
  
  /** Number of rejected reconciliations */
  rejectedCount: number;
  
  /** Number of cancelled reconciliations */
  cancelledCount: number;
  
  /** Total number of accounts reconciled */
  totalAccountsReconciled: number;
  
  /** Total number of transactions processed */
  totalTransactionsProcessed: number;
  
  /** Total value of reconciled transactions */
  totalValueReconciled: number;
  
  /** Average time to complete reconciliation (in hours) */
  averageCompletionTime: number;
  
  /** Reconciliation completion rate (percentage) */
  completionRate: number;
}

/** Reconciliation filter criteria */
export interface ReconciliationFilter {
  /** Filter by status */
  status?: ReconciliationStatus | '';
  
  /** Filter by start date (YYYY-MM-DD) */
  startDate?: string;
  
  /** Filter by end date (YYYY-MM-DD) */
  endDate?: string;
  
  /** Filter by account ID */
  accountId?: string;
  
  /** Filter by created by user ID */
  createdBy?: string;
  
  /** Search query (searches in reference number and description) */
  searchQuery?: string;
  
  /** Page number for pagination */
  page?: number;
  
  /** Number of items per page */
  limit?: number;
  
  /** Sort field */
  sortBy?: string;
  
  /** Sort direction (asc/desc) */
  sortDirection?: 'asc' | 'desc';
}

/** Reconciliation creation data */
export interface CreateReconciliationData {
  /** Description of the reconciliation */
  description: string;
  
  /** Start date of the reconciliation period (YYYY-MM-DD) */
  startDate: string;
  
  /** End date of the reconciliation period (YYYY-MM-DD) */
  endDate: string;
  
  /** Array of account IDs to include in the reconciliation */
  accountIds: string[];
  
  /** Optional notes */
  notes?: string;
}

/** Reconciliation update data */
export interface UpdateReconciliationData {
  /** Updated description */
  description?: string;
  
  /** Updated status */
  status?: ReconciliationStatus;
  
  /** Updated notes */
  notes?: string | null;
  
  /** Rejection reason (if status is being updated to REJECTED) */
  rejectionReason?: string | null;
}

/** Reconciliation account update data */
export interface UpdateReconciliationAccountData {
  /** Reconciled balance */
  reconciledBalance: number | null;
  
  /** Reconciliation status */
  status: AccountReconciliationStatus;
  
  /** Notes or comments */
  notes?: string | null;
}

/** Reconciliation report data */
export interface ReconciliationReportData {
  /** Reconciliation ID */
  reconciliationId: string;
  
  /** Report title */
  title: string;
  
  /** Report date */
  reportDate: string;
  
  /** Generated by user */
  generatedBy: string;
  
  /** Summary statistics */
  summary: {
    /** Total number of accounts */
    totalAccounts: number;
    
    /** Number of reconciled accounts */
    reconciledAccounts: number;
    
    /** Number of pending accounts */
    pendingAccounts: number;
    
    /** Total difference amount */
    totalDifference: number;
  };
  
  /** Account reconciliation details */
  accounts: Array<{
    /** Account ID */
    accountId: string;
    
    /** Account code */
    accountCode: string;
    
    /** Account name */
    accountName: string;
    
    /** Opening balance */
    openingBalance: number;
    
    /** Reconciled balance */
    reconciledBalance: number | null;
    
    /** Difference amount */
    difference: number;
    
    /** Reconciliation status */
    status: AccountReconciliationStatus;
    
    /** Reconciliation date */
    reconciledAt: string | null;
    
    /** Reconciled by user */
    reconciledBy: string | null;
  }>;
  
  /** Reconciliation transactions */
  transactions: Array<{
    /** Transaction ID */
    id: string;
    
    /** Transaction date */
    date: string;
    
    /** Reference number */
    reference: string;
    
    /** Description */
    description: string;
    
    /** Debit amount */
    debit: number;
    
    /** Credit amount */
    credit: number;
    
    /** Balance */
    balance: number;
    
    /** Whether the transaction is reconciled */
    isReconciled: boolean;
  }>;
}
