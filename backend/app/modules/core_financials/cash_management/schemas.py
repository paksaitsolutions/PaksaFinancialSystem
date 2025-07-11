"""
Cash Management Module - Pydantic Schemas
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Dict, Any, Union
from uuid import UUID

from pydantic import BaseModel, Field, validator, HttpUrl, EmailStr

from app.schemas.base import BaseSchema, PaginatedResponse


# Enums (redefined here for OpenAPI documentation)
class BankAccountType(str, Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
    MONEY_MARKET = "money_market"
    CREDIT_CARD = "credit_card"
    LINE_OF_CREDIT = "line_of_credit"
    PAYMENT_PROCESSOR = "payment_processor"
    OTHER = "other"


class BankAccountStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    CLOSED = "closed"
    PENDING = "pending"
    SUSPENDED = "suspended"


class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"
    FEE = "fee"
    INTEREST = "interest"
    PAYMENT = "payment"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"
    OTHER = "other"


class TransactionStatus(str, Enum):
    PENDING = "pending"
    POSTED = "posted"
    CLEARED = "cleared"
    VOID = "void"
    RECONCILED = "reconciled"
    FAILED = "failed"


class ReconciliationStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ADJUSTED = "adjusted"
    CANCELLED = "cancelled"


# Base Schemas
class BankAccountBase(BaseSchema):
    """Base schema for bank accounts."""
    name: str = Field(..., max_length=255, description="Name of the bank account")
    account_number: str = Field(..., max_length=100, description="Account number")
    account_type: BankAccountType = Field(..., description="Type of bank account")
    status: BankAccountStatus = Field(default=BankAccountStatus.ACTIVE, description="Account status")
    currency: str = Field(default="USD", max_length=3, description="Currency code (ISO 4217)")
    
    # Bank Information
    bank_name: str = Field(..., max_length=255, description="Name of the bank")
    bank_code: Optional[str] = Field(None, max_length=50, description="Bank code/identifier")
    routing_number: Optional[str] = Field(None, max_length=50, description="Routing number (US)")
    iban: Optional[str] = Field(None, max_length=50, description="IBAN (International)")
    swift_code: Optional[str] = Field(None, max_length=50, description="SWIFT/BIC code")
    
    # GL Integration
    gl_account_id: Optional[UUID] = Field(None, description="Associated GL Account ID")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class BankAccountCreate(BankAccountBase):
    """Schema for creating a new bank account."""
    pass


class BankAccountUpdate(BaseModel):
    """Schema for updating a bank account."""
    name: Optional[str] = Field(None, max_length=255)
    status: Optional[BankAccountStatus] = None
    currency: Optional[str] = Field(None, max_length=3)
    bank_name: Optional[str] = Field(None, max_length=255)
    bank_code: Optional[str] = Field(None, max_length=50)
    routing_number: Optional[str] = Field(None, max_length=50)
    iban: Optional[str] = Field(None, max_length=50)
    swift_code: Optional[str] = Field(None, max_length=50)
    gl_account_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = None


class BankAccountResponse(BankAccountBase):
    """Schema for bank account responses."""
    id: UUID
    current_balance: Decimal = Field(..., description="Current balance")
    available_balance: Decimal = Field(..., description="Available balance")
    last_synced_balance: Optional[Decimal] = None
    last_synced_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by_id: UUID
    updated_by_id: UUID
    
    class Config:
        orm_mode = True


class BankTransactionBase(BaseSchema):
    """Base schema for bank transactions."""
    account_id: UUID = Field(..., description="Bank account ID")
    transaction_date: date = Field(..., description="Date the transaction occurred")
    posted_date: Optional[date] = Field(None, description="Date the transaction was posted")
    transaction_type: TransactionType = Field(..., description="Type of transaction")
    status: TransactionStatus = Field(default=TransactionStatus.PENDING, description="Transaction status")
    
    # Amounts
    amount: Decimal = Field(..., gt=0, description="Transaction amount (always positive)")
    
    # Transaction Details
    reference_number: Optional[str] = Field(None, max_length=100, description="Bank reference number")
    check_number: Optional[str] = Field(None, max_length=50, description="Check number (if applicable)")
    memo: Optional[str] = Field(None, description="Transaction memo")
    notes: Optional[str] = Field(None, description="Internal notes")
    
    # Categorization
    category_id: Optional[UUID] = Field(None, description="Transaction category ID")
    payment_method: Optional[str] = Field(None, max_length=100, description="Payment method used")
    payee: Optional[str] = Field(None, max_length=255, description="Payee/payer name")
    
    # GL Integration
    gl_entry_id: Optional[UUID] = Field(None, description="Associated GL Journal Entry ID")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('amount')
    def validate_amount(cls, v):
        """Ensure amount is positive and has proper precision."""
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v.quantize(Decimal('0.01'))


class BankTransactionCreate(BankTransactionBase):
    """Schema for creating a new bank transaction."""
    pass


class BankTransactionUpdate(BaseModel):
    """Schema for updating a bank transaction."""
    transaction_date: Optional[date] = None
    posted_date: Optional[date] = None
    status: Optional[TransactionStatus] = None
    memo: Optional[str] = None
    notes: Optional[str] = None
    category_id: Optional[UUID] = None
    payment_method: Optional[str] = None
    payee: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BankTransactionResponse(BankTransactionBase):
    """Schema for bank transaction responses."""
    id: UUID
    running_balance: Optional[Decimal] = None
    is_reconciled: bool = False
    created_at: datetime
    updated_at: datetime
    created_by_id: UUID
    updated_by_id: UUID
    
    class Config:
        orm_mode = True


class BankReconciliationBase(BaseSchema):
    """Base schema for bank reconciliations."""
    account_id: UUID = Field(..., description="Bank account ID")
    statement_date: date = Field(..., description="Statement date")
    statement_ending_balance: Decimal = Field(..., description="Ending balance per statement")
    reconciliation_date: date = Field(default_factory=date.today, description="Date of reconciliation")
    status: ReconciliationStatus = Field(default=ReconciliationStatus.DRAFT, description="Reconciliation status")
    notes: Optional[str] = Field(None, description="Reconciliation notes")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class BankReconciliationCreate(BankReconciliationBase):
    """Schema for creating a new bank reconciliation."""
    transaction_ids: List[UUID] = Field(default_factory=list, description="List of transaction IDs to reconcile")


class BankReconciliationUpdate(BaseModel):
    """Schema for updating a bank reconciliation."""
    status: Optional[ReconciliationStatus] = None
    notes: Optional[str] = None
    transaction_ids: Optional[List[UUID]] = None
    metadata: Optional[Dict[str, Any]] = None


class BankReconciliationResponse(BankReconciliationBase):
    """Schema for bank reconciliation responses."""
    id: UUID
    cleared_balance: Optional[Decimal] = None
    difference: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime
    created_by_id: UUID
    updated_by_id: UUID
    
    class Config:
        orm_mode = True


class TransactionCategoryBase(BaseSchema):
    """Base schema for transaction categories."""
    name: str = Field(..., max_length=100, description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    parent_id: Optional[UUID] = Field(None, description="Parent category ID (for hierarchical categories)")
    gl_account_id: Optional[UUID] = Field(None, description="Default GL Account ID for this category")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TransactionCategoryCreate(TransactionCategoryBase):
    """Schema for creating a new transaction category."""
    pass


class TransactionCategoryUpdate(BaseModel):
    """Schema for updating a transaction category."""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    gl_account_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = None


class TransactionCategoryResponse(TransactionCategoryBase):
    """Schema for transaction category responses."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by_id: UUID
    updated_by_id: UUID
    
    class Config:
        orm_mode = True


# Paginated Responses
class PaginatedBankAccounts(PaginatedResponse):
    """Paginated response for bank accounts."""
    items: List[BankAccountResponse]


class PaginatedTransactions(PaginatedResponse):
    """Paginated response for transactions."""
    items: List[BankTransactionResponse]


class PaginatedReconciliations(PaginatedResponse):
    """Paginated response for reconciliations."""
    items: List[BankReconciliationResponse]


class PaginatedTransactionCategories(PaginatedResponse):
    """Paginated response for transaction categories."""
    items: List[TransactionCategoryResponse]


# Specialized Request/Response Models
class BankAccountBalanceUpdate(BaseModel):
    """Schema for updating bank account balance."""
    balance_date: date = Field(..., description="Date of the balance")
    balance: Decimal = Field(..., gt=0, description="New balance amount")
    notes: Optional[str] = Field(None, description="Notes about the balance update")


class TransactionImportRequest(BaseModel):
    """Schema for importing transactions."""
    account_id: UUID = Field(..., description="Bank account ID")
    transactions: List[Dict[str, Any]] = Field(..., description="List of transactions to import")
    format: str = Field(..., description="Import format (e.g., 'csv', 'ofx', 'qif')")
    options: Dict[str, Any] = Field(default_factory=dict, description="Import options")


class ReconciliationSummary(BaseModel):
    """Summary of a bank reconciliation."""
    reconciliation_id: UUID
    account_id: UUID
    account_name: str
    statement_date: date
    statement_balance: Decimal
    cleared_balance: Decimal
    difference: Decimal
    status: ReconciliationStatus
    transaction_count: int


class CashFlowSummary(BaseModel):
    """Cash flow summary for a period."""
    start_date: date
    end_date: date
    opening_balance: Decimal
    closing_balance: Decimal
    total_inflows: Decimal
    total_outflows: Decimal
    net_cash_flow: Decimal
    by_category: Dict[str, Decimal]
    by_payment_method: Dict[str, Decimal]


# Bank Integration Schemas
class BankIntegrationBase(BaseSchema):
    """Base schema for bank integrations."""
    name: str = Field(..., max_length=100, description="Integration name")
    provider: str = Field(..., max_length=100, description="Integration provider")
    is_active: bool = Field(default=True, description="Whether the integration is active")
    config: Dict[str, Any] = Field(default_factory=dict, description="Integration configuration")
    sync_interval_minutes: int = Field(default=1440, description="Sync interval in minutes")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class BankIntegrationCreate(BankIntegrationBase):
    """Schema for creating a new bank integration."""
    api_key: Optional[str] = Field(None, description="API key (will be encrypted)")
    client_id: Optional[str] = Field(None, description="Client ID (will be encrypted)")
    secret: Optional[str] = Field(None, description="Secret (will be encrypted)")


class BankIntegrationUpdate(BaseModel):
    """Schema for updating a bank integration."""
    name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None
    sync_interval_minutes: Optional[int] = None
    api_key: Optional[str] = Field(None, description="API key (will be encrypted)")
    client_id: Optional[str] = Field(None, description="Client ID (will be encrypted)")
    secret: Optional[str] = Field(None, description="Secret (will be encrypted)")
    metadata: Optional[Dict[str, Any]] = None


class BankIntegrationResponse(BankIntegrationBase):
    """Schema for bank integration responses."""
    id: UUID
    last_sync: Optional[datetime] = None
    sync_status: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by_id: UUID
    updated_by_id: UUID
    
    class Config:
        orm_mode = True


class BankAccountStatementResponse(BaseModel):
    """Schema for bank account statement responses."""
    id: UUID
    account_id: UUID
    statement_date: date
    start_date: date
    end_date: date
    opening_balance: Decimal
    closing_balance: Decimal
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    file_url: Optional[str] = None
    is_processed: bool
    processed_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by_id: UUID
    updated_by_id: UUID
    
    class Config:
        orm_mode = True


class CashForecast(BaseModel):
    forecast: list


class EnhancedReconciliationReport(BaseModel):
    details: list
