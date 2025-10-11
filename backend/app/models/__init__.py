"""
Paksa Financial System - Unified Models
=======================================
Import all standardized models from core_models to eliminate duplicates
and ensure consistent data structure across all modules.
"""

# Import all unified core models
from .core_models import (
    # Core Financial
    ChartOfAccounts,
    JournalEntry,
    JournalEntryLine,
    
    # Vendor Management
    Vendor,
    VendorContact,
    
    # Customer Management  
    Customer,
    CustomerContact,
    
    # Accounts Payable
    APInvoice,
    APInvoiceLineItem,
    APPayment,
    APInvoicePayment,
    APCreditMemo,
    APCreditApplication,
    Form1099,
    Form1099Transaction,
    
    # Accounts Receivable
    ARInvoice,
    ARInvoiceLineItem,
    ARPayment,
    ARInvoicePayment,
    Collection,
    CollectionActivity,
    
    # Employee & HRM
    Employee,
    Department,
    
    # Payroll
    PayrollRun,
    PayrollEntry,
    LeaveRequest,
    
    # Inventory & Procurement
    InventoryItem,
    InventoryCategory,
    PurchaseOrder,
    PurchaseOrderLineItem,
    
    # Tax Management
    TaxRate,
    
    # Financial Periods & Reporting
    FinancialPeriod,
    Budget,
    BudgetLineItem,
    BudgetLineItem,
    
    # System & Configuration
    Company,
    Currency,
    ExchangeRate,
)

# Import enums
from .enums import *

# Import base classes
from .base import Base, BaseModel, AuditMixin

# Import specialized models that don't have duplicates
from .ai_bi_models import (
    AIInsight,
    AIRecommendation,
    AIAnomaly,
    AIPrediction,
    AIModelMetrics,
    AIAnalyticsReport,
)

# Import Cash Management models
from .cash_management import (
    BankAccount,
    BankTransaction,
    CashFlowCategory,
    BankReconciliation,
    ReconciliationItem,
)

# Import Notification models
from .notification import (
    Notification,
    NotificationType,
    NotificationPriority,
)

# Import GL-specific models (using unified ChartOfAccounts)
from .gl_models import (
    AccountingPeriod,
    LedgerBalance,
    TrialBalance,
    TrialBalanceAccount,
    FinancialStatement,
    FinancialStatementLine,
    FinancialStatementSection,
    FinancialStatementType,
    BudgetEntry,
    AccountType,
    AccountSubType,
    AccountStatus,
    JournalEntryStatus,
)

# Add aliases for GL models that should use unified models
GLChartOfAccounts = ChartOfAccounts
GLJournalEntry = JournalEntry
GLJournalEntryLine = JournalEntryLine

from .user import User
from .role import Role, Permission, RolePermission, UserPermission

# Export all models for easy importing
__all__ = [
    # Core Financial
    'ChartOfAccounts',
    'JournalEntry', 
    'JournalEntryLine',
    
    # Vendor Management
    'Vendor',
    'VendorContact',
    
    # Customer Management
    'Customer',
    'CustomerContact',
    
    # Accounts Payable
    'APInvoice',
    'APInvoiceLineItem', 
    'APPayment',
    'APInvoicePayment',
    'APCreditMemo',
    'APCreditApplication',
    'Form1099',
    'Form1099Transaction',
    
    # Accounts Receivable
    'ARInvoice',
    'ARInvoiceLineItem',
    'ARPayment', 
    'ARInvoicePayment',
    'Collection',
    'CollectionActivity',
    
    # Employee & HRM
    'Employee',
    'Department',
    
    # Payroll
    'PayrollRun',
    'PayrollEntry',
    'LeaveRequest',
    
    # Inventory & Procurement
    'InventoryItem',
    'InventoryCategory',
    'PurchaseOrder',
    'PurchaseOrderLineItem',
    
    # Tax Management
    'TaxRate',
    
    # Financial Periods & Reporting
    'FinancialPeriod',
    'Budget',
    'BudgetLineItem',
    'BudgetLineItem',
    
    # System & Configuration
    'Company',
    'Currency',
    'ExchangeRate',
    
    # AI/BI
    'AIInsight',
    'AIRecommendation',
    'AIAnomaly',
    'AIPrediction',
    'AIModelMetrics',
    'AIAnalyticsReport',
    
    # User Management
    'User',
    'Role',
    'Permission',
    'RolePermission',
    'UserPermission',
    
    # GL-specific models
    'GLChartOfAccounts',
    'GLJournalEntry', 
    'GLJournalEntryLine',
    'AccountingPeriod',
    'LedgerBalance',
    'TrialBalance',
    'TrialBalanceAccount',
    'FinancialStatement',
    'FinancialStatementLine',
    'FinancialStatementSection',
    'FinancialStatementType',
    'BudgetEntry',
    'AccountType',
    'AccountSubType',
    'AccountStatus',
    'JournalEntryStatus',
    
    # Cash Management models
    'BankAccount',
    'BankTransaction',
    'CashFlowCategory',
    'BankReconciliation',
    'ReconciliationItem',
    
    # Notification models
    'Notification',
    'NotificationType',
    'NotificationPriority',
    
    # Base Classes
    'Base',
    'BaseModel',
    'AuditMixin',
]