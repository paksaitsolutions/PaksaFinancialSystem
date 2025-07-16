from sqlalchemy import Column, Integer, String, Text, Decimal, DateTime, Date, Boolean, ForeignKey, Enum as SQLEnum, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models.base import Base
import enum
import uuid

class VendorCategory(enum.Enum):
    SUPPLIER = "supplier"
    CONTRACTOR = "contractor"
    SERVICE_PROVIDER = "service_provider"
    CONSULTANT = "consultant"
    UTILITY = "utility"
    GOVERNMENT = "government"
    OTHER = "other"

class VendorStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BLACKLISTED = "blacklisted"
    PENDING_APPROVAL = "pending_approval"

class PaymentTerms(enum.Enum):
    NET_15 = "net15"
    NET_30 = "net30"
    NET_45 = "net45"
    NET_60 = "net60"
    NET_90 = "net90"
    DUE_ON_RECEIPT = "due_on_receipt"
    COD = "cod"
    PREPAID = "prepaid"

class VendorRiskLevel(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class InvoiceStatus(enum.Enum):
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

class PaymentMethod(enum.Enum):
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

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETURNED = "returned"

class ApprovalStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"

class Vendor(Base):
    __tablename__ = "ap_vendors"
    
    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    legal_name = Column(String(255))
    category = Column(SQLEnum(VendorCategory), nullable=False)
    subcategory = Column(String(100))
    
    # Contact Information
    contact_person = Column(String(255))
    email = Column(String(255), index=True)
    phone = Column(String(20))
    mobile = Column(String(20))
    fax = Column(String(20))
    website = Column(String(255))
    
    # Address Information
    billing_address = Column(Text)
    shipping_address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    
    # Tax and Legal Information
    tax_id = Column(String(50), index=True)
    vat_number = Column(String(50))
    registration_number = Column(String(100))
    business_license = Column(String(100))
    
    # Financial Information
    payment_terms = Column(SQLEnum(PaymentTerms), default=PaymentTerms.NET_30)
    credit_limit = Column(Decimal(15, 2), default=0)
    discount_percentage = Column(Decimal(5, 2), default=0)
    currency_code = Column(String(3), default='USD')
    
    # Banking Information
    bank_name = Column(String(255))
    bank_account_number = Column(String(100))
    bank_routing_number = Column(String(50))
    swift_code = Column(String(20))
    iban = Column(String(50))
    
    # Risk and Compliance
    risk_level = Column(SQLEnum(VendorRiskLevel), default=VendorRiskLevel.LOW)
    compliance_score = Column(Integer, default=100)
    last_audit_date = Column(Date)
    next_audit_date = Column(Date)
    
    # Status and Workflow
    status = Column(SQLEnum(VendorStatus), default=VendorStatus.ACTIVE)
    approval_status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING)
    approved_by = Column(String(255))
    approved_at = Column(DateTime(timezone=True))
    
    # AI/ML Fields
    ai_risk_score = Column(Decimal(5, 2))
    payment_behavior_score = Column(Decimal(5, 2))
    reliability_score = Column(Decimal(5, 2))
    
    # Metadata
    tags = Column(JSONB)
    custom_fields = Column(JSONB)
    notes = Column(Text)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    invoices = relationship("Invoice", back_populates="vendor")
    payments = relationship("Payment", back_populates="vendor")
    contracts = relationship("VendorContract", back_populates="vendor")
    evaluations = relationship("VendorEvaluation", back_populates="vendor")
    
    # Indexes
    __table_args__ = (
        Index('idx_vendor_name_category', 'name', 'category'),
        Index('idx_vendor_status_risk', 'status', 'risk_level'),
    )
    
    @property
    def outstanding_balance(self):
        return sum(invoice.balance_due for invoice in self.invoices if invoice.balance_due > 0)
    
    @property
    def total_spent_ytd(self):
        from datetime import datetime
        current_year = datetime.now().year
        return sum(
            invoice.total_amount for invoice in self.invoices 
            if invoice.invoice_date.year == current_year and invoice.status == InvoiceStatus.PAID
        )

class VendorContract(Base):
    __tablename__ = "ap_vendor_contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("ap_vendors.id"), nullable=False)
    contract_number = Column(String(100), unique=True, nullable=False)
    contract_type = Column(String(50))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    auto_renew = Column(Boolean, default=False)
    contract_value = Column(Decimal(15, 2))
    currency_code = Column(String(3), default='USD')
    terms_and_conditions = Column(Text)
    status = Column(String(20), default='active')
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    vendor = relationship("Vendor", back_populates="contracts")

class VendorEvaluation(Base):
    __tablename__ = "ap_vendor_evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("ap_vendors.id"), nullable=False)
    evaluation_date = Column(Date, nullable=False)
    evaluator = Column(String(255))
    
    # Evaluation Scores (1-10)
    quality_score = Column(Integer)
    delivery_score = Column(Integer)
    service_score = Column(Integer)
    price_score = Column(Integer)
    communication_score = Column(Integer)
    overall_score = Column(Decimal(3, 1))
    
    comments = Column(Text)
    recommendations = Column(Text)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    vendor = relationship("Vendor", back_populates="evaluations")

class Invoice(Base):
    __tablename__ = "ap_invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(100), unique=True, nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("ap_vendors.id"), nullable=False)
    
    # Invoice Details
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    received_date = Column(Date)
    description = Column(Text)
    
    # Purchase Order Reference
    po_number = Column(String(100), index=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"))
    
    # Financial Information
    subtotal = Column(Decimal(15, 2), nullable=False, default=0)
    tax_amount = Column(Decimal(15, 2), default=0)
    discount_amount = Column(Decimal(15, 2), default=0)
    shipping_amount = Column(Decimal(15, 2), default=0)
    other_charges = Column(Decimal(15, 2), default=0)
    total_amount = Column(Decimal(15, 2), nullable=False)
    paid_amount = Column(Decimal(15, 2), default=0)
    balance_due = Column(Decimal(15, 2), nullable=False)
    
    # Currency and Exchange
    currency_code = Column(String(3), default='USD')
    exchange_rate = Column(Decimal(10, 6), default=1.0)
    base_currency_amount = Column(Decimal(15, 2))
    
    # Status and Workflow
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    approval_status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING)
    
    # Approval Workflow
    approved_by = Column(String(255))
    approved_at = Column(DateTime(timezone=True))
    approval_notes = Column(Text)
    rejection_reason = Column(Text)
    
    # AI/ML Fields
    fraud_risk_score = Column(Decimal(5, 2))
    duplicate_risk_score = Column(Decimal(5, 2))
    ai_category_prediction = Column(String(100))
    ai_confidence_score = Column(Decimal(5, 2))
    
    # Document Management
    document_path = Column(String(500))
    ocr_extracted_data = Column(JSONB)
    
    # Metadata
    tags = Column(JSONB)
    custom_fields = Column(JSONB)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    vendor = relationship("Vendor", back_populates="invoices")
    lines = relationship("InvoiceLine", back_populates="invoice", cascade="all, delete-orphan")
    payment_applications = relationship("PaymentInvoice", back_populates="invoice")
    approvals = relationship("InvoiceApproval", back_populates="invoice")
    
    # Indexes
    __table_args__ = (
        Index('idx_invoice_vendor_date', 'vendor_id', 'invoice_date'),
        Index('idx_invoice_status_due', 'status', 'due_date'),
        Index('idx_invoice_po_number', 'po_number'),
    )
    
    @property
    def vendor_name(self):
        return self.vendor.name if self.vendor else ""
    
    @property
    def days_overdue(self):
        from datetime import date
        if self.due_date < date.today() and self.balance_due > 0:
            return (date.today() - self.due_date).days
        return 0
    
    @property
    def is_overdue(self):
        return self.days_overdue > 0

class InvoiceLine(Base):
    __tablename__ = "ap_invoice_lines"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("ap_invoices.id"), nullable=False)
    line_number = Column(Integer, nullable=False)
    
    # Item Information
    item_code = Column(String(100))
    description = Column(String(500), nullable=False)
    category = Column(String(100))
    
    # Quantity and Pricing
    quantity = Column(Decimal(10, 4), nullable=False, default=1)
    unit_of_measure = Column(String(20))
    unit_price = Column(Decimal(15, 2), nullable=False)
    discount_percentage = Column(Decimal(5, 2), default=0)
    discount_amount = Column(Decimal(15, 2), default=0)
    line_total = Column(Decimal(15, 2), nullable=False)
    
    # Tax Information
    tax_code = Column(String(20))
    tax_rate = Column(Decimal(5, 2), default=0)
    tax_amount = Column(Decimal(15, 2), default=0)
    
    # GL Account
    account_id = Column(Integer, ForeignKey("gl_accounts.id"))
    cost_center = Column(String(50))
    project_id = Column(Integer, ForeignKey("projects.id"))
    
    # AI/ML Fields
    ai_category = Column(String(100))
    ai_confidence = Column(Decimal(5, 2))
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    invoice = relationship("Invoice", back_populates="lines")

class InvoiceApproval(Base):
    __tablename__ = "ap_invoice_approvals"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("ap_invoices.id"), nullable=False)
    approval_level = Column(Integer, nullable=False)
    approver_id = Column(Integer, ForeignKey("users.id"))
    approver_name = Column(String(255))
    
    status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING)
    approved_at = Column(DateTime(timezone=True))
    comments = Column(Text)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    invoice = relationship("Invoice", back_populates="approvals")

class Payment(Base):
    __tablename__ = "ap_payments"
    
    id = Column(Integer, primary_key=True, index=True)
    payment_number = Column(String(100), unique=True, nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("ap_vendors.id"), nullable=False)
    
    # Payment Details
    payment_date = Column(Date, nullable=False)
    amount = Column(Decimal(15, 2), nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    reference_number = Column(String(100))
    check_number = Column(String(50))
    
    # Banking Information
    bank_account_id = Column(Integer, ForeignKey("bank_accounts.id"))
    transaction_id = Column(String(100))
    
    # Currency and Exchange
    currency_code = Column(String(3), default='USD')
    exchange_rate = Column(Decimal(10, 6), default=1.0)
    base_currency_amount = Column(Decimal(15, 2))
    
    # Status and Processing
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    processed_at = Column(DateTime(timezone=True))
    processed_by = Column(String(255))
    
    # Approval
    approval_status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING)
    approved_by = Column(String(255))
    approved_at = Column(DateTime(timezone=True))
    
    # AI/ML Fields
    fraud_risk_score = Column(Decimal(5, 2))
    anomaly_score = Column(Decimal(5, 2))
    
    # Metadata
    notes = Column(Text)
    tags = Column(JSONB)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    vendor = relationship("Vendor", back_populates="payments")
    invoice_applications = relationship("PaymentInvoice", back_populates="payment")
    
    # Indexes
    __table_args__ = (
        Index('idx_payment_vendor_date', 'vendor_id', 'payment_date'),
        Index('idx_payment_status_method', 'status', 'payment_method'),
    )
    
    @property
    def vendor_name(self):
        return self.vendor.name if self.vendor else ""
    
    @property
    def invoice_numbers(self):
        return [app.invoice.invoice_number for app in self.invoice_applications if app.invoice]

class PaymentInvoice(Base):
    __tablename__ = "ap_payment_invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("ap_payments.id"), nullable=False)
    invoice_id = Column(Integer, ForeignKey("ap_invoices.id"), nullable=False)
    amount_applied = Column(Decimal(15, 2), nullable=False)
    discount_taken = Column(Decimal(15, 2), default=0)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    payment = relationship("Payment", back_populates="invoice_applications")
    invoice = relationship("Invoice", back_populates="payment_applications")

# AI/BI Analytics Tables
class APAnalytics(Base):
    __tablename__ = "ap_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    vendor_id = Column(Integer, ForeignKey("ap_vendors.id"))
    
    # Metrics
    total_invoices = Column(Integer, default=0)
    total_amount = Column(Decimal(15, 2), default=0)
    avg_payment_days = Column(Decimal(5, 1))
    on_time_payment_rate = Column(Decimal(5, 2))
    
    # AI Predictions
    predicted_cash_flow = Column(Decimal(15, 2))
    risk_score = Column(Decimal(5, 2))
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class VendorPerformanceMetrics(Base):
    __tablename__ = "ap_vendor_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("ap_vendors.id"), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    
    # Performance Metrics
    total_invoices = Column(Integer, default=0)
    total_amount = Column(Decimal(15, 2), default=0)
    avg_invoice_amount = Column(Decimal(15, 2))
    on_time_delivery_rate = Column(Decimal(5, 2))
    quality_score = Column(Decimal(3, 1))
    
    # Payment Metrics
    avg_payment_days = Column(Decimal(5, 1))
    early_payment_discount_taken = Column(Decimal(15, 2), default=0)
    
    # AI Scores
    reliability_score = Column(Decimal(5, 2))
    risk_score = Column(Decimal(5, 2))
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())