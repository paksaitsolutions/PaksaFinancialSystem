from sqlalchemy import Column, Integer, String, Text, Decimal, DateTime, Date, Boolean, ForeignKey, Enum as SQLEnum, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.db.base import Base
import enum
import uuid

class CustomerCategory(enum.Enum):
    INDIVIDUAL = "individual"
    BUSINESS = "business"
    GOVERNMENT = "government"
    NON_PROFIT = "non_profit"
    RESELLER = "reseller"
    DISTRIBUTOR = "distributor"
    ONLINE = "online"
    RETAIL = "retail"

class CustomerStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BLACKLISTED = "blacklisted"
    PENDING_APPROVAL = "pending_approval"
    VIP = "vip"

class PaymentTerms(enum.Enum):
    NET_15 = "net15"
    NET_30 = "net30"
    NET_45 = "net45"
    NET_60 = "net60"
    NET_90 = "net90"
    DUE_ON_RECEIPT = "due_on_receipt"
    COD = "cod"
    PREPAID = "prepaid"
    CREDIT_CARD = "credit_card"

class CreditRating(enum.Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    NO_RATING = "no_rating"

class InvoiceStatus(enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    PARTIAL_PAYMENT = "partial_payment"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    DISPUTED = "disputed"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    DISPUTED = "disputed"

class CollectionStatus(enum.Enum):
    CURRENT = "current"
    FIRST_NOTICE = "first_notice"
    SECOND_NOTICE = "second_notice"
    FINAL_NOTICE = "final_notice"
    COLLECTION_AGENCY = "collection_agency"
    LEGAL_ACTION = "legal_action"
    WRITE_OFF = "write_off"

class Customer(Base):
    __tablename__ = "ar_customers"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    legal_name = Column(String(255))
    category = Column(SQLEnum(CustomerCategory), nullable=False)
    
    # Contact Information
    contact_person = Column(String(255))
    email = Column(String(255), index=True)
    phone = Column(String(20))
    mobile = Column(String(20))
    website = Column(String(255))
    
    # Address Information
    billing_address = Column(Text)
    shipping_address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    
    # Financial Information
    credit_limit = Column(Decimal(15, 2), default=0)
    payment_terms = Column(SQLEnum(PaymentTerms), default=PaymentTerms.NET_30)
    currency_code = Column(String(3), default='USD')
    tax_exempt = Column(Boolean, default=False)
    tax_id = Column(String(50))
    
    # Credit Information
    credit_rating = Column(SQLEnum(CreditRating), default=CreditRating.NO_RATING)
    credit_score = Column(Integer)
    last_credit_check = Column(Date)
    
    # Status and Workflow
    status = Column(SQLEnum(CustomerStatus), default=CustomerStatus.ACTIVE)
    
    # AI/ML Fields
    payment_behavior_score = Column(Decimal(5, 2))
    churn_risk_score = Column(Decimal(5, 2))
    lifetime_value = Column(Decimal(15, 2))
    
    # E-commerce Integration
    shopify_customer_id = Column(String(50))
    amazon_customer_id = Column(String(50))
    marketplace_data = Column(JSONB)
    
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
    invoices = relationship("ARInvoice", back_populates="customer")
    payments = relationship("ARPayment", back_populates="customer")
    credit_memos = relationship("CreditMemo", back_populates="customer")
    
    # Indexes
    __table_args__ = (
        Index('idx_customer_name_category', 'name', 'category'),
        Index('idx_customer_status_rating', 'status', 'credit_rating'),
    )
    
    @property
    def outstanding_balance(self):
        return sum(invoice.balance_due for invoice in self.invoices if invoice.balance_due > 0)
    
    @property
    def total_sales_ytd(self):
        from datetime import datetime
        current_year = datetime.now().year
        return sum(
            invoice.total_amount for invoice in self.invoices 
            if invoice.invoice_date.year == current_year and invoice.status in ['paid', 'partial_payment']
        )

class ARInvoice(Base):
    __tablename__ = "ar_invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(100), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("ar_customers.id"), nullable=False)
    
    # Invoice Details
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    description = Column(Text)
    
    # Sales Order Reference
    so_number = Column(String(100), index=True)
    po_number = Column(String(100))
    
    # Financial Information
    subtotal = Column(Decimal(15, 2), nullable=False, default=0)
    tax_amount = Column(Decimal(15, 2), default=0)
    discount_amount = Column(Decimal(15, 2), default=0)
    shipping_amount = Column(Decimal(15, 2), default=0)
    total_amount = Column(Decimal(15, 2), nullable=False)
    paid_amount = Column(Decimal(15, 2), default=0)
    balance_due = Column(Decimal(15, 2), nullable=False)
    
    # Currency and Exchange
    currency_code = Column(String(3), default='USD')
    exchange_rate = Column(Decimal(10, 6), default=1.0)
    
    # Status and Workflow
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    sent_date = Column(Date)
    viewed_date = Column(Date)
    
    # Collection Information
    collection_status = Column(SQLEnum(CollectionStatus), default=CollectionStatus.CURRENT)
    last_reminder_date = Column(Date)
    next_followup_date = Column(Date)
    
    # AI/ML Fields
    payment_prediction_score = Column(Decimal(5, 2))
    collection_difficulty_score = Column(Decimal(5, 2))
    
    # E-commerce Integration
    order_source = Column(String(50))  # shopify, amazon, website, etc.
    marketplace_order_id = Column(String(100))
    
    # Metadata
    tags = Column(JSONB)
    custom_fields = Column(JSONB)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    customer = relationship("Customer", back_populates="invoices")
    lines = relationship("ARInvoiceLine", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("ARPaymentInvoice", back_populates="invoice")
    
    # Indexes
    __table_args__ = (
        Index('idx_invoice_customer_date', 'customer_id', 'invoice_date'),
        Index('idx_invoice_status_due', 'status', 'due_date'),
        Index('idx_invoice_collection', 'collection_status', 'next_followup_date'),
    )
    
    @property
    def customer_name(self):
        return self.customer.name if self.customer else ""
    
    @property
    def days_overdue(self):
        from datetime import date
        if self.due_date < date.today() and self.balance_due > 0:
            return (date.today() - self.due_date).days
        return 0
    
    @property
    def is_overdue(self):
        return self.days_overdue > 0

class ARInvoiceLine(Base):
    __tablename__ = "ar_invoice_lines"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("ar_invoices.id"), nullable=False)
    line_number = Column(Integer, nullable=False)
    
    # Product Information
    product_code = Column(String(100))
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
    revenue_account_id = Column(Integer, ForeignKey("gl_accounts.id"))
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    invoice = relationship("ARInvoice", back_populates="lines")

class ARPayment(Base):
    __tablename__ = "ar_payments"
    
    id = Column(Integer, primary_key=True, index=True)
    payment_number = Column(String(100), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("ar_customers.id"), nullable=False)
    
    # Payment Details
    payment_date = Column(Date, nullable=False)
    amount = Column(Decimal(15, 2), nullable=False)
    payment_method = Column(String(50), nullable=False)
    reference_number = Column(String(100))
    
    # Banking Information
    bank_account_id = Column(Integer, ForeignKey("bank_accounts.id"))
    transaction_id = Column(String(100))
    
    # Currency and Exchange
    currency_code = Column(String(3), default='USD')
    exchange_rate = Column(Decimal(10, 6), default=1.0)
    
    # Status and Processing
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    processed_at = Column(DateTime(timezone=True))
    
    # E-commerce Integration
    gateway_transaction_id = Column(String(100))
    gateway_name = Column(String(50))
    
    # Metadata
    notes = Column(Text)
    tags = Column(JSONB)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    customer = relationship("Customer", back_populates="payments")
    invoice_applications = relationship("ARPaymentInvoice", back_populates="payment")
    
    @property
    def customer_name(self):
        return self.customer.name if self.customer else ""

class ARPaymentInvoice(Base):
    __tablename__ = "ar_payment_invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("ar_payments.id"), nullable=False)
    invoice_id = Column(Integer, ForeignKey("ar_invoices.id"), nullable=False)
    amount_applied = Column(Decimal(15, 2), nullable=False)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    payment = relationship("ARPayment", back_populates="invoice_applications")
    invoice = relationship("ARInvoice", back_populates="payments")

class CreditMemo(Base):
    __tablename__ = "ar_credit_memos"
    
    id = Column(Integer, primary_key=True, index=True)
    credit_memo_number = Column(String(100), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("ar_customers.id"), nullable=False)
    original_invoice_id = Column(Integer, ForeignKey("ar_invoices.id"))
    
    # Credit Memo Details
    credit_date = Column(Date, nullable=False)
    reason = Column(String(255))
    description = Column(Text)
    
    # Financial Information
    subtotal = Column(Decimal(15, 2), nullable=False)
    tax_amount = Column(Decimal(15, 2), default=0)
    total_amount = Column(Decimal(15, 2), nullable=False)
    applied_amount = Column(Decimal(15, 2), default=0)
    balance = Column(Decimal(15, 2), nullable=False)
    
    # Status
    status = Column(String(20), default='active')
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    customer = relationship("Customer", back_populates="credit_memos")

# Analytics and BI Tables
class ARAnalytics(Base):
    __tablename__ = "ar_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    customer_id = Column(Integer, ForeignKey("ar_customers.id"))
    
    # Metrics
    total_invoices = Column(Integer, default=0)
    total_amount = Column(Decimal(15, 2), default=0)
    avg_collection_days = Column(Decimal(5, 1))
    payment_success_rate = Column(Decimal(5, 2))
    
    # AI Predictions
    predicted_collections = Column(Decimal(15, 2))
    churn_probability = Column(Decimal(5, 2))
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CustomerPerformanceMetrics(Base):
    __tablename__ = "ar_customer_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("ar_customers.id"), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    
    # Performance Metrics
    total_invoices = Column(Integer, default=0)
    total_sales = Column(Decimal(15, 2), default=0)
    avg_invoice_amount = Column(Decimal(15, 2))
    avg_payment_days = Column(Decimal(5, 1))
    payment_success_rate = Column(Decimal(5, 2))
    
    # Collection Metrics
    overdue_amount = Column(Decimal(15, 2), default=0)
    collection_efficiency = Column(Decimal(5, 2))
    
    # AI Scores
    loyalty_score = Column(Decimal(5, 2))
    credit_score = Column(Decimal(5, 2))
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())