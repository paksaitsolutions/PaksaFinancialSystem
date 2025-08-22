declare module '../api/BankAccountService' {
  import { AxiosResponse } from 'axios';

  interface BankAccount {
    id?: string;
    name: string;
    accountNumber: string;
    bankName: string;
    accountType: string;
    currency: string;
    balance: number;
    isActive: boolean;
    description?: string;
    routingNumber?: string;
    iban?: string;
    swiftCode?: string;
    openingBalance?: number;
    openingDate?: string;
  }

  interface Transaction {
    id?: string;
    bankAccountId: string;
    date: string;
    amount: number;
    type: 'deposit' | 'withdrawal' | 'transfer' | 'fee' | 'interest' | 'other';
    category?: string;
    description: string;
    referenceNumber?: string;
    status: 'pending' | 'completed' | 'cancelled' | 'reconciled';
    notes?: string;
    createdBy?: string;
    createdAt?: string;
    updatedAt?: string;
  }

  interface Reconciliation {
    id?: string;
    bankAccountId: string;
    statementDate: string;
    endingBalance: number;
    status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
    notes?: string;
    reconciledBy?: string;
    reconciledAt?: string;
    createdAt?: string;
    updatedAt?: string;
    transactions?: any[];
  }

  interface ApiResponse<T> {
    data: T;
    message?: string;
    success: boolean;
  }

  const BankAccountService: {
    // Bank Account methods
    getBankAccounts(): Promise<AxiosResponse<ApiResponse<BankAccount[]>>>;
    getBankAccount(id: string): Promise<AxiosResponse<ApiResponse<BankAccount>>>;
    createBankAccount(account: Omit<BankAccount, 'id'>): Promise<AxiosResponse<ApiResponse<BankAccount>>>;
    updateBankAccount(id: string, account: Partial<BankAccount>): Promise<AxiosResponse<ApiResponse<BankAccount>>>;
    deleteBankAccount(id: string): Promise<AxiosResponse<ApiResponse<void>>>;
    
    // Transaction methods
    getTransactions(bankAccountId: string): Promise<AxiosResponse<ApiResponse<Transaction[]>>>;
    getTransaction(id: string): Promise<AxiosResponse<ApiResponse<Transaction>>>;
    createTransaction(transaction: Omit<Transaction, 'id'>): Promise<AxiosResponse<ApiResponse<Transaction>>>;
    updateTransaction(id: string, transaction: Partial<Transaction>): Promise<AxiosResponse<ApiResponse<Transaction>>>;
    deleteTransaction(id: string): Promise<AxiosResponse<ApiResponse<void>>>;
    
    // Reconciliation methods
    getReconciliations(bankAccountId: string): Promise<AxiosResponse<ApiResponse<Reconciliation[]>>>;
    getReconciliation(id: string): Promise<AxiosResponse<ApiResponse<Reconciliation>>>;
    startReconciliation(data: Omit<Reconciliation, 'id' | 'createdAt' | 'updatedAt'>): Promise<AxiosResponse<ApiResponse<Reconciliation>>>;
    updateReconciliation(id: string, data: Partial<Reconciliation>): Promise<AxiosResponse<ApiResponse<Reconciliation>>>;
    deleteReconciliation(id: string): Promise<AxiosResponse<ApiResponse<void>>>;
  };

  export default BankAccountService;
}
