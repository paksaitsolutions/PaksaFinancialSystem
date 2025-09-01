import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field

from .models import BillStatus, PaymentStatus

# ================================================
#                Vendor Schemas
# ================================================

class VendorBase(BaseModel):
    name: str = Field(..., max_length=255)
    contact_person: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    tax_id: Optional[str] = Field(None, max_length=100)
    default_currency: str = Field('USD', max_length=3)
    is_active: bool = True

class VendorCreate(VendorBase):
    pass

class VendorUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    contact_person: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    tax_id: Optional[str] = Field(None, max_length=100)
    default_currency: Optional[str] = Field(None, max_length=3)
    is_active: Optional[bool] = None

class Vendor(VendorBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# ================================================
#                  Bill Schemas
# ================================================

class BillLineItemBase(BaseModel):
    account_id: uuid.UUID
    description: str
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)

class BillLineItemCreate(BillLineItemBase):
    pass

class BillLineItem(BillLineItemBase):
    id: uuid.UUID
    total_price: Decimal

    class Config:
        orm_mode = True

class BillBase(BaseModel):
    vendor_id: uuid.UUID
    bill_number: str = Field(..., max_length=100)
    issue_date: date
    due_date: date
    currency: str = Field('USD', max_length=3)
    notes: Optional[str] = None

class BillCreate(BillBase):
    line_items: List[BillLineItemCreate]

class BillUpdate(BaseModel):
    bill_number: Optional[str] = Field(None, max_length=100)
    issue_date: Optional[date] = None
    due_date: Optional[date] = None
    notes: Optional[str] = None
    status: Optional[BillStatus] = None

class Bill(BillBase):
    id: uuid.UUID
    total_amount: Decimal
    amount_paid: Decimal
    status: BillStatus
    created_at: datetime
    updated_at: datetime
    line_items: List[BillLineItem]
    vendor: Vendor

    class Config:
        orm_mode = True

# ================================================
#                Payment Schemas
# ================================================

class PaymentAllocationCreate(BaseModel):
    bill_id: uuid.UUID
    amount_allocated: Decimal = Field(..., gt=0)

class PaymentAllocation(PaymentAllocationCreate):
    id: uuid.UUID

    class Config:
        orm_mode = True

class PaymentBase(BaseModel):
    vendor_id: uuid.UUID
    payment_date: date
    amount: Decimal = Field(..., gt=0)
    currency: str = Field('USD', max_length=3)
    payment_method: Optional[str] = Field(None, max_length=100)
    reference_number: Optional[str] = Field(None, max_length=255)

class PaymentCreate(PaymentBase):
    allocations: List[PaymentAllocationCreate]

class PaymentUpdate(BaseModel):
    payment_date: Optional[date] = None
    payment_method: Optional[str] = Field(None, max_length=100)
    reference_number: Optional[str] = Field(None, max_length=255)
    status: Optional[PaymentStatus] = None

class Payment(PaymentBase):
    id: uuid.UUID
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime
    allocations: List[PaymentAllocation]
    vendor: Vendor

    class Config:
        orm_mode = True
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

# Enums
class VendorCategory(str, Enum):
    SUPPLIER = "supplier"
    CONTRACTOR = "contractor"
    SERVICE_PROVIDER = "service_provider"
    CONSULTANT = "consultant"
    UTILITY = "utility"
    GOVERNMENT = "government"
    OTHER = "other"

class VendorStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BLACKLISTED = "blacklisted"
    PENDING_APPROVAL = "pending_approval"

class PaymentTerms(str, Enum):
    NET_15 = "net15"
    NET_30 = "net30"
    NET_45 = "net45"
    NET_60 = "net60"
    NET_90 = "net90"
    DUE_ON_RECEIPT = "due_on_receipt"
    COD = "cod"
    PREPAID = "prepaid"

class VendorRiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"

class PaymentMethod(str, Enum):
    CHECK = "check"
    ACH = "ach"
    WIRE_TRANSFER = "wire_transfer"
    IBFT = "ibft"
    CASH = "cash"
    DEBIT_CARD = "debit_card"
    CREDIT_CARD = "credit_card"
    DIGITAL_WALLET = "digital_wallet"
    CRYPTO = "crypto"
    BANK_TRANSFER = "bank_transfer"
    MOBILE_PAYMENT = "mobile_payment"
    ONLINE_BANKING = "online_banking"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETURNED = "returned"

class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"

# Vendor Schemas
class VendorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    legal_name: Optional[str] = Field(None, max_length=255)
    category: VendorCategory
    subcategory: Optional[str] = Field(None, max_length=100)
    
    # Contact Information
    contact_person: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    mobile: Optional[str] = Field(None, max_length=20)
    fax: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = Field(None, max_length=255)
    
    # Address Information
    billing_address: Optional[str] = Field(None, max_length=500)
    shipping_address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    
    # Tax and Legal Information
    tax_id: Optional[str] = Field(None, max_length=50)
    vat_number: Optional[str] = Field(None, max_length=50)
    registration_number: Optional[str] = Field(None, max_length=100)
    business_license: Optional[str] = Field(None, max_length=100)
    
    # Financial Information
    payment_terms: PaymentTerms = PaymentTerms.NET_30
    credit_limit: Decimal = Field(default=Decimal('0.00'), ge=0)
    discount_percentage: Decimal = Field(default=Decimal('0.00'), ge=0, le=100)
    currency_code: str = Field(default='USD', max_length=3)
    
    # Banking Information
    bank_name: Optional[str] = Field(None, max_length=255)
    bank_account_number: Optional[str] = Field(None, max_length=100)
    bank_routing_number: Optional[str] = Field(None, max_length=50)
    swift_code: Optional[str] = Field(None, max_length=20)
    iban: Optional[str] = Field(None, max_length=50)
    
    # Risk and Compliance
    risk_level: VendorRiskLevel = VendorRiskLevel.LOW
    last_audit_date: Optional[date] = None
    next_audit_date: Optional[date] = None
    
    # Status
    status: VendorStatus = VendorStatus.ACTIVE
    
    # Metadata
    tags: Optional[List[str]] = []
    custom_fields: Optional[Dict[str, Any]] = {}
    notes: Optional[str] = None

class VendorCreate(VendorBase):
    pass

class VendorUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    legal_name: Optional[str] = Field(None, max_length=255)
    category: Optional[VendorCategory] = None
    subcategory: Optional[str] = Field(None, max_length=100)
    contact_person: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    mobile: Optional[str] = Field(None, max_length=20)
    billing_address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    tax_id: Optional[str] = Field(None, max_length=50)
    payment_terms: Optional[PaymentTerms] = None
    credit_limit: Optional[Decimal] = Field(None, ge=0)
    status: Optional[VendorStatus] = None
    risk_level: Optional[VendorRiskLevel] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None

class VendorResponse(VendorBase):
    id: int
    vendor_id: str
    outstanding_balance: Decimal = Field(default=Decimal('0.00'))
    total_spent_ytd: Decimal = Field(default=Decimal('0.00'))
    compliance_score: int = Field(default=100)
    ai_risk_score: Optional[Decimal] = None
    payment_behavior_score: Optional[Decimal] = None
    reliability_score: Optional[Decimal] = None
    approval_status: ApprovalStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Vendor Contract Schemas
class VendorContractBase(BaseModel):
    contract_number: str = Field(..., max_length=100)
    contract_type: Optional[str] = Field(None, max_length=50)
    start_date: date
    end_date: Optional[date] = None
    auto_renew: bool = False
    contract_value: Optional[Decimal] = Field(None, ge=0)
    currency_code: str = Field(default='USD', max_length=3)
    terms_and_conditions: Optional[str] = None
    status: str = Field(default='active', max_length=20)

class VendorContractCreate(VendorContractBase):
    vendor_id: int

class VendorContractResponse(VendorContractBase):
    id: int
    vendor_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Vendor Evaluation Schemas
class VendorEvaluationBase(BaseModel):
    evaluation_date: date
    evaluator: str = Field(..., max_length=255)
    quality_score: int = Field(..., ge=1, le=10)
    delivery_score: int = Field(..., ge=1, le=10)
    service_score: int = Field(..., ge=1, le=10)
    price_score: int = Field(..., ge=1, le=10)
    communication_score: int = Field(..., ge=1, le=10)
    comments: Optional[str] = None
    recommendations: Optional[str] = None

class VendorEvaluationCreate(VendorEvaluationBase):
    vendor_id: int

class VendorEvaluationResponse(VendorEvaluationBase):
    id: int
    vendor_id: int
    overall_score: Decimal
    created_at: datetime

    class Config:
        from_attributes = True

# Invoice Line Schemas
class InvoiceLineBase(BaseModel):
    line_number: int = Field(..., ge=1)
    item_code: Optional[str] = Field(None, max_length=100)
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
    account_id: Optional[int] = None
    cost_center: Optional[str] = Field(None, max_length=50)
    project_id: Optional[int] = None

class InvoiceLineCreate(InvoiceLineBase):
    pass

class InvoiceLineUpdate(BaseModel):
    line_number: Optional[int] = Field(None, ge=1)
    item_code: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    category: Optional[str] = Field(None, max_length=100)
    quantity: Optional[Decimal] = Field(None, gt=0)
    unit_price: Optional[Decimal] = Field(None, ge=0)
    discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    tax_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    account_id: Optional[int] = None

class InvoiceLineResponse(InvoiceLineBase):
    id: int
    line_total: Decimal
    ai_category: Optional[str] = None
    ai_confidence: Optional[Decimal] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Invoice Schemas
class InvoiceBase(BaseModel):
    vendor_id: int
    invoice_number: str = Field(..., min_length=1, max_length=100)
    invoice_date: date
    due_date: date
    received_date: Optional[date] = None
    description: Optional[str] = Field(None, max_length=1000)
    po_number: Optional[str] = Field(None, max_length=100)
    po_id: Optional[int] = None
    
    # Financial Information
    tax_amount: Decimal = Field(default=Decimal('0.00'), ge=0)
    discount_amount: Decimal = Field(default=Decimal('0.00'), ge=0)
    shipping_amount: Decimal = Field(default=Decimal('0.00'), ge=0)
    other_charges: Decimal = Field(default=Decimal('0.00'), ge=0)
    
    # Currency
    currency_code: str = Field(default='USD', max_length=3)
    exchange_rate: Decimal = Field(default=Decimal('1.0'), gt=0)
    
    # Status
    status: InvoiceStatus = InvoiceStatus.DRAFT
    
    # Metadata
    tags: Optional[List[str]] = []
    custom_fields: Optional[Dict[str, Any]] = {}

class InvoiceCreate(InvoiceBase):
    lines: List[InvoiceLineCreate] = Field(..., min_items=1)

class InvoiceUpdate(BaseModel):
    vendor_id: Optional[int] = None
    invoice_number: Optional[str] = Field(None, min_length=1, max_length=100)
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    received_date: Optional[date] = None
    description: Optional[str] = Field(None, max_length=1000)
    po_number: Optional[str] = Field(None, max_length=100)
    tax_amount: Optional[Decimal] = Field(None, ge=0)
    discount_amount: Optional[Decimal] = Field(None, ge=0)
    shipping_amount: Optional[Decimal] = Field(None, ge=0)
    status: Optional[InvoiceStatus] = None
    lines: Optional[List[InvoiceLineCreate]] = None
    tags: Optional[List[str]] = None

class InvoiceResponse(InvoiceBase):
    id: int
    subtotal: Decimal
    total_amount: Decimal
    paid_amount: Decimal = Field(default=Decimal('0.00'))
    balance_due: Decimal
    base_currency_amount: Optional[Decimal] = None
    vendor_name: str
    approval_status: ApprovalStatus
    days_overdue: int = 0
    is_overdue: bool = False
    
    # AI/ML Fields
    fraud_risk_score: Optional[Decimal] = None
    duplicate_risk_score: Optional[Decimal] = None
    ai_category_prediction: Optional[str] = None
    ai_confidence_score: Optional[Decimal] = None
    
    lines: List[InvoiceLineResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Invoice Approval Schemas
class InvoiceApprovalBase(BaseModel):
    approval_level: int = Field(..., ge=1)
    approver_name: str = Field(..., max_length=255)
    status: ApprovalStatus = ApprovalStatus.PENDING
    comments: Optional[str] = None

class InvoiceApprovalCreate(InvoiceApprovalBase):
    invoice_id: int
    approver_id: Optional[int] = None

class InvoiceApprovalResponse(InvoiceApprovalBase):
    id: int
    invoice_id: int
    approver_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Payment Schemas
class PaymentBase(BaseModel):
    vendor_id: int
    payment_date: date
    amount: Decimal = Field(..., gt=0)
    payment_method: PaymentMethod
    reference_number: Optional[str] = Field(None, max_length=100)
    check_number: Optional[str] = Field(None, max_length=50)
    bank_account_id: Optional[int] = None
    transaction_id: Optional[str] = Field(None, max_length=100)
    
    # Currency
    currency_code: str = Field(default='USD', max_length=3)
    exchange_rate: Decimal = Field(default=Decimal('1.0'), gt=0)
    
    # Metadata
    notes: Optional[str] = None
    tags: Optional[List[str]] = []

class PaymentCreate(PaymentBase):
    invoice_ids: List[int] = Field(..., min_items=1)
    amounts_applied: Optional[List[Decimal]] = None

class PaymentUpdate(BaseModel):
    payment_date: Optional[date] = None
    payment_method: Optional[PaymentMethod] = None
    reference_number: Optional[str] = Field(None, max_length=100)
    check_number: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    status: Optional[PaymentStatus] = None
    tags: Optional[List[str]] = None

class PaymentResponse(PaymentBase):
    id: int
    payment_number: str
    status: PaymentStatus
    base_currency_amount: Optional[Decimal] = None
    vendor_name: str
    invoice_numbers: List[str] = []
    approval_status: ApprovalStatus
    processed_at: Optional[datetime] = None
    processed_by: Optional[str] = None
    
    # AI/ML Fields
    fraud_risk_score: Optional[Decimal] = None
    anomaly_score: Optional[Decimal] = None
    
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Analytics and BI Schemas
class APSummaryResponse(BaseModel):
    total_outstanding: Decimal
    overdue_amount: Decimal
    this_month_invoices: Decimal
    pending_approval: Decimal
    total_vendors: int
    active_vendors: int
    avg_payment_days: Optional[Decimal] = None
    on_time_payment_rate: Optional[Decimal] = None
    top_vendors_by_spend: List[Dict[str, Any]] = []

class VendorSummaryResponse(BaseModel):
    vendor_id: int
    vendor_name: str
    total_invoices: int
    outstanding_balance: Decimal
    total_spent_ytd: Decimal
    last_payment_date: Optional[date]
    payment_terms: PaymentTerms
    avg_payment_days: Optional[Decimal] = None
    risk_level: VendorRiskLevel
    compliance_score: int
    performance_score: Optional[Decimal] = None

class AgingReportItem(BaseModel):
    vendor_id: int
    vendor_name: str
    current: Decimal = Field(default=Decimal('0.00'))
    days_1_30: Decimal = Field(default=Decimal('0.00'))
    days_31_60: Decimal = Field(default=Decimal('0.00'))
    days_61_90: Decimal = Field(default=Decimal('0.00'))
    over_90_days: Decimal = Field(default=Decimal('0.00'))
    total_outstanding: Decimal

class AgingReportResponse(BaseModel):
    report_date: date
    items: List[AgingReportItem]
    totals: AgingReportItem

class CashFlowForecastResponse(BaseModel):
    forecast_date: date
    period_days: int
    predicted_payments: List[Dict[str, Any]]
    total_predicted_amount: Decimal
    confidence_score: Decimal
    risk_factors: List[str] = []

class VendorPerformanceResponse(BaseModel):
    vendor_id: int
    vendor_name: str
    period_start: date
    period_end: date
    total_invoices: int
    total_amount: Decimal
    avg_invoice_amount: Decimal
    on_time_delivery_rate: Optional[Decimal] = None
    quality_score: Optional[Decimal] = None
    avg_payment_days: Optional[Decimal] = None
    reliability_score: Optional[Decimal] = None
    risk_score: Optional[Decimal] = None
    recommendations: List[str] = []

# AI/ML Schemas
class FraudDetectionResponse(BaseModel):
    invoice_id: int
    fraud_risk_score: Decimal
    risk_level: str
    risk_factors: List[str]
    recommendations: List[str]

class DuplicateDetectionResponse(BaseModel):
    invoice_id: int
    potential_duplicates: List[Dict[str, Any]]
    confidence_score: Decimal
    matching_criteria: List[str]

class SmartCategorizationResponse(BaseModel):
    line_item_id: int
    predicted_category: str
    confidence_score: Decimal
    suggested_account: Optional[str] = None
    alternative_categories: List[Dict[str, Any]] = []

# Bulk Operations
class BulkApprovalRequest(BaseModel):
    invoice_ids: List[int] = Field(..., min_items=1)
    approved_by: str
    approval_notes: Optional[str] = None

class BulkPaymentRequest(BaseModel):
    payment_requests: List[PaymentCreate] = Field(..., min_items=1)
    batch_reference: Optional[str] = None
    scheduled_date: Optional[date] = None

class BulkVendorUpdateRequest(BaseModel):
    vendor_ids: List[int] = Field(..., min_items=1)
    updates: VendorUpdate

# Advanced Search and Filter Schemas
class VendorSearchRequest(BaseModel):
    search_term: Optional[str] = None
    categories: Optional[List[VendorCategory]] = None
    statuses: Optional[List[VendorStatus]] = None
    risk_levels: Optional[List[VendorRiskLevel]] = None
    payment_terms: Optional[List[PaymentTerms]] = None
    min_credit_limit: Optional[Decimal] = None
    max_credit_limit: Optional[Decimal] = None
    countries: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    created_after: Optional[date] = None
    created_before: Optional[date] = None

class InvoiceSearchRequest(BaseModel):
    search_term: Optional[str] = None
    vendor_ids: Optional[List[int]] = None
    statuses: Optional[List[InvoiceStatus]] = None
    invoice_date_from: Optional[date] = None
    invoice_date_to: Optional[date] = None
    due_date_from: Optional[date] = None
    due_date_to: Optional[date] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    po_numbers: Optional[List[str]] = None
    overdue_only: bool = False
    tags: Optional[List[str]] = None

class PaymentSearchRequest(BaseModel):
    search_term: Optional[str] = None
    vendor_ids: Optional[List[int]] = None
    statuses: Optional[List[PaymentStatus]] = None
    payment_methods: Optional[List[PaymentMethod]] = None
    payment_date_from: Optional[date] = None
    payment_date_to: Optional[date] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    reference_numbers: Optional[List[str]] = None
    tags: Optional[List[str]] = None
>>>>>>> e96df7278ce4216131b6c65d411c0723f4de7f91
