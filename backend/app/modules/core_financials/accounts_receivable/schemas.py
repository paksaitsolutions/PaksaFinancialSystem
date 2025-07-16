from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

# Enums
class CustomerCategory(str, Enum):
    INDIVIDUAL = "individual"
    BUSINESS = "business"
    GOVERNMENT = "government"
    NON_PROFIT = "non_profit"
    RESELLER = "reseller"
    DISTRIBUTOR = "distributor"
    ONLINE = "online"
    RETAIL = "retail"

class CustomerStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BLACKLISTED = "blacklisted"
    PENDING_APPROVAL = "pending_approval"
    VIP = "vip"

class PaymentTerms(str, Enum):
    NET_15 = "net15"
    NET_30 = "net30"
    NET_45 = "net45"
    NET_60 = "net60"
    NET_90 = "net90"
    DUE_ON_RECEIPT = "due_on_receipt"
    COD = "cod"
    PREPAID = "prepaid"
    CREDIT_CARD = "credit_card"

class CreditRating(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    NO_RATING = "no_rating"

class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    PARTIAL_PAYMENT = "partial_payment"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    DISPUTED = "disputed"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    DISPUTED = "disputed"

class CollectionStatus(str, Enum):
    CURRENT = "current"
    FIRST_NOTICE = "first_notice"
    SECOND_NOTICE = "second_notice"
    FINAL_NOTICE = "final_notice"
    COLLECTION_AGENCY = "collection_agency"
    LEGAL_ACTION = "legal_action"
    WRITE_OFF = "write_off"

# Customer Schemas
class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    legal_name: Optional[str] = Field(None, max_length=255)
    category: CustomerCategory
    
    # Contact Information
    contact_person: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    mobile: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = Field(None, max_length=255)
    
    # Address Information
    billing_address: Optional[str] = Field(None, max_length=500)
    shipping_address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    
    # Financial Information
    credit_limit: Decimal = Field(default=Decimal('0.00'), ge=0)
    payment_terms: PaymentTerms = PaymentTerms.NET_30
    currency_code: str = Field(default='USD', max_length=3)
    tax_exempt: bool = False
    tax_id: Optional[str] = Field(None, max_length=50)
    
    # Credit Information
    credit_rating: CreditRating = CreditRating.NO_RATING
    credit_score: Optional[int] = Field(None, ge=300, le=850)
    last_credit_check: Optional[date] = None
    
    # Status
    status: CustomerStatus = CustomerStatus.ACTIVE
    
    # E-commerce Integration
    shopify_customer_id: Optional[str] = Field(None, max_length=50)
    amazon_customer_id: Optional[str] = Field(None, max_length=50)
    marketplace_data: Optional[Dict[str, Any]] = {}
    
    # Metadata
    tags: Optional[List[str]] = []
    custom_fields: Optional[Dict[str, Any]] = {}
    notes: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    legal_name: Optional[str] = Field(None, max_length=255)
    category: Optional[CustomerCategory] = None
    contact_person: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    billing_address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    credit_limit: Optional[Decimal] = Field(None, ge=0)
    payment_terms: Optional[PaymentTerms] = None
    status: Optional[CustomerStatus] = None
    credit_rating: Optional[CreditRating] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None

class CustomerResponse(CustomerBase):
    id: int
    customer_id: str
    outstanding_balance: Decimal = Field(default=Decimal('0.00'))
    total_sales_ytd: Decimal = Field(default=Decimal('0.00'))
    payment_behavior_score: Optional[Decimal] = None
    churn_risk_score: Optional[Decimal] = None
    lifetime_value: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Invoice Line Schemas
class ARInvoiceLineBase(BaseModel):
    line_number: int = Field(..., ge=1)
    product_code: Optional[str] = Field(None, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    category: Optional[str] = Field(None, max_length=100)
    quantity: Decimal = Field(..., gt=0)
    unit_of_measure: Optional[str] = Field(None, max_length=20)
    unit_price: Decimal = Field(..., ge=0)
    discount_percentage: Decimal = Field(default=Decimal('0.00'), ge=0, le=100)
    discount_amount: Decimal = Field(default=Decimal('0.00'), ge=0)
    tax_code: Optional[str] = Field(None, max_length=20)
    tax_rate: Decimal = Field(default=Decimal('0.00'), ge=0, le=100)
    tax_amount: Decimal = Field(default=Decimal('0.00'), ge=0)
    revenue_account_id: Optional[int] = None

class ARInvoiceLineCreate(ARInvoiceLineBase):
    pass

class ARInvoiceLineResponse(ARInvoiceLineBase):
    id: int
    line_total: Decimal
    created_at: datetime

    class Config:
        from_attributes = True

# Invoice Schemas
class ARInvoiceBase(BaseModel):
    customer_id: int
    invoice_number: str = Field(..., min_length=1, max_length=100)
    invoice_date: date
    due_date: date
    description: Optional[str] = Field(None, max_length=1000)
    so_number: Optional[str] = Field(None, max_length=100)
    po_number: Optional[str] = Field(None, max_length=100)
    
    # Financial Information
    tax_amount: Decimal = Field(default=Decimal('0.00'), ge=0)
    discount_amount: Decimal = Field(default=Decimal('0.00'), ge=0)
    shipping_amount: Decimal = Field(default=Decimal('0.00'), ge=0)
    
    # Currency
    currency_code: str = Field(default='USD', max_length=3)
    exchange_rate: Decimal = Field(default=Decimal('1.0'), gt=0)
    
    # Status
    status: InvoiceStatus = InvoiceStatus.DRAFT
    
    # E-commerce Integration
    order_source: Optional[str] = Field(None, max_length=50)
    marketplace_order_id: Optional[str] = Field(None, max_length=100)
    
    # Metadata
    tags: Optional[List[str]] = []
    custom_fields: Optional[Dict[str, Any]] = {}

class ARInvoiceCreate(ARInvoiceBase):
    lines: List[ARInvoiceLineCreate] = Field(..., min_items=1)

class ARInvoiceUpdate(BaseModel):
    customer_id: Optional[int] = None
    invoice_number: Optional[str] = Field(None, min_length=1, max_length=100)
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    description: Optional[str] = Field(None, max_length=1000)
    po_number: Optional[str] = Field(None, max_length=100)
    tax_amount: Optional[Decimal] = Field(None, ge=0)
    discount_amount: Optional[Decimal] = Field(None, ge=0)
    shipping_amount: Optional[Decimal] = Field(None, ge=0)
    status: Optional[InvoiceStatus] = None
    lines: Optional[List[ARInvoiceLineCreate]] = None
    tags: Optional[List[str]] = None

class ARInvoiceResponse(ARInvoiceBase):
    id: int
    subtotal: Decimal
    total_amount: Decimal
    paid_amount: Decimal = Field(default=Decimal('0.00'))
    balance_due: Decimal
    customer_name: str
    days_overdue: int = 0
    is_overdue: bool = False
    collection_status: CollectionStatus
    last_reminder_date: Optional[date] = None
    next_followup_date: Optional[date] = None
    
    # AI/ML Fields
    payment_prediction_score: Optional[Decimal] = None
    collection_difficulty_score: Optional[Decimal] = None
    
    lines: List[ARInvoiceLineResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Payment Schemas
class ARPaymentBase(BaseModel):
    customer_id: int
    payment_date: date
    amount: Decimal = Field(..., gt=0)
    payment_method: str = Field(..., max_length=50)
    reference_number: Optional[str] = Field(None, max_length=100)
    bank_account_id: Optional[int] = None
    transaction_id: Optional[str] = Field(None, max_length=100)
    
    # Currency
    currency_code: str = Field(default='USD', max_length=3)
    exchange_rate: Decimal = Field(default=Decimal('1.0'), gt=0)
    
    # E-commerce Integration
    gateway_transaction_id: Optional[str] = Field(None, max_length=100)
    gateway_name: Optional[str] = Field(None, max_length=50)
    
    # Metadata
    notes: Optional[str] = None
    tags: Optional[List[str]] = []

class ARPaymentCreate(ARPaymentBase):
    invoice_ids: List[int] = Field(..., min_items=1)
    amounts_applied: Optional[List[Decimal]] = None

class ARPaymentUpdate(BaseModel):
    payment_date: Optional[date] = None
    payment_method: Optional[str] = Field(None, max_length=50)
    reference_number: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    status: Optional[PaymentStatus] = None
    tags: Optional[List[str]] = None

class ARPaymentResponse(ARPaymentBase):
    id: int
    payment_number: str
    status: PaymentStatus
    customer_name: str
    processed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Credit Memo Schemas
class CreditMemoBase(BaseModel):
    customer_id: int
    credit_memo_number: str = Field(..., max_length=100)
    original_invoice_id: Optional[int] = None
    credit_date: date
    reason: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    subtotal: Decimal = Field(..., ge=0)
    tax_amount: Decimal = Field(default=Decimal('0.00'), ge=0)
    total_amount: Decimal = Field(..., ge=0)

class CreditMemoCreate(CreditMemoBase):
    pass

class CreditMemoResponse(CreditMemoBase):
    id: int
    applied_amount: Decimal = Field(default=Decimal('0.00'))
    balance: Decimal
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Analytics and BI Schemas
class ARSummaryResponse(BaseModel):
    total_outstanding: Decimal
    overdue_amount: Decimal
    this_month_sales: Decimal
    avg_collection_days: Optional[Decimal] = None
    total_customers: int
    active_customers: int
    payment_success_rate: Optional[Decimal] = None
    top_customers_by_sales: List[Dict[str, Any]] = []

class CustomerSummaryResponse(BaseModel):
    customer_id: int
    customer_name: str
    total_invoices: int
    outstanding_balance: Decimal
    total_sales_ytd: Decimal
    last_payment_date: Optional[date]
    payment_terms: PaymentTerms
    avg_payment_days: Optional[Decimal] = None
    credit_rating: CreditRating
    payment_behavior_score: Optional[Decimal] = None

class ARAgingReportItem(BaseModel):
    customer_id: int
    customer_name: str
    current: Decimal = Field(default=Decimal('0.00'))
    days_1_30: Decimal = Field(default=Decimal('0.00'))
    days_31_60: Decimal = Field(default=Decimal('0.00'))
    days_61_90: Decimal = Field(default=Decimal('0.00'))
    over_90_days: Decimal = Field(default=Decimal('0.00'))
    total_outstanding: Decimal

class ARAgingReportResponse(BaseModel):
    report_date: date
    items: List[ARAgingReportItem]
    totals: ARAgingReportItem

class CollectionForecastResponse(BaseModel):
    forecast_date: date
    period_days: int
    predicted_collections: List[Dict[str, Any]]
    total_predicted_amount: Decimal
    confidence_score: Decimal
    risk_factors: List[str] = []

class CustomerPerformanceResponse(BaseModel):
    customer_id: int
    customer_name: str
    period_start: date
    period_end: date
    total_invoices: int
    total_sales: Decimal
    avg_invoice_amount: Decimal
    avg_payment_days: Optional[Decimal] = None
    payment_success_rate: Optional[Decimal] = None
    overdue_amount: Decimal
    collection_efficiency: Optional[Decimal] = None
    loyalty_score: Optional[Decimal] = None
    recommendations: List[str] = []

# AI/ML Schemas
class ChurnPredictionResponse(BaseModel):
    customer_id: int
    churn_probability: Decimal
    risk_level: str
    risk_factors: List[str]
    recommendations: List[str]

class PaymentPredictionResponse(BaseModel):
    invoice_id: int
    payment_probability: Decimal
    predicted_payment_date: Optional[date]
    confidence_score: Decimal
    factors: List[str]

class CustomerSegmentationResponse(BaseModel):
    customer_id: int
    segment: str
    characteristics: List[str]
    lifetime_value: Decimal
    recommendations: List[str]

# Bulk Operations
class BulkInvoiceCreate(BaseModel):
    invoices: List[ARInvoiceCreate] = Field(..., min_items=1)
    send_immediately: bool = False

class BulkPaymentApplication(BaseModel):
    payment_applications: List[Dict[str, Any]] = Field(..., min_items=1)
    batch_reference: Optional[str] = None

class BulkCollectionAction(BaseModel):
    invoice_ids: List[int] = Field(..., min_items=1)
    action: CollectionStatus
    notes: Optional[str] = None
    next_followup_date: Optional[date] = None

# Advanced Search and Filter Schemas
class CustomerSearchRequest(BaseModel):
    search_term: Optional[str] = None
    categories: Optional[List[CustomerCategory]] = None
    statuses: Optional[List[CustomerStatus]] = None
    credit_ratings: Optional[List[CreditRating]] = None
    payment_terms: Optional[List[PaymentTerms]] = None
    min_credit_limit: Optional[Decimal] = None
    max_credit_limit: Optional[Decimal] = None
    countries: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    created_after: Optional[date] = None
    created_before: Optional[date] = None

class ARInvoiceSearchRequest(BaseModel):
    search_term: Optional[str] = None
    customer_ids: Optional[List[int]] = None
    statuses: Optional[List[InvoiceStatus]] = None
    collection_statuses: Optional[List[CollectionStatus]] = None
    invoice_date_from: Optional[date] = None
    invoice_date_to: Optional[date] = None
    due_date_from: Optional[date] = None
    due_date_to: Optional[date] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    overdue_only: bool = False
    tags: Optional[List[str]] = None

class ARPaymentSearchRequest(BaseModel):
    search_term: Optional[str] = None
    customer_ids: Optional[List[int]] = None
    statuses: Optional[List[PaymentStatus]] = None
    payment_methods: Optional[List[str]] = None
    payment_date_from: Optional[date] = None
    payment_date_to: Optional[date] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    gateway_names: Optional[List[str]] = None
    tags: Optional[List[str]] = None