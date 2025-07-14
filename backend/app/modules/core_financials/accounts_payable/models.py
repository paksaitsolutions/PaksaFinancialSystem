from sqlalchemy import Column, Integer, String, Text, Decimal, DateTime, Date, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import enum

class VendorCategory(enum.Enum):
    SUPPLIER = "supplier"
    CONTRACTOR = "contractor"
    SERVICE = "service"

class VendorStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class PaymentTerms(enum.Enum):
    NET_15 = "net15"
    NET_30 = "net30"
    NET_60 = "net60"
    DUE_ON_RECEIPT = "due_on_receipt"

class InvoiceStatus(enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class PaymentMethod(enum.Enum):
    CHECK = "check"
    ACH = "ach"
    WIRE = "wire"
    CARD = "card"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    PROCESSED = "processed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Vendor(Base):
    __tablename__ = "ap_vendors"
    
    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    category = Column(SQLEnum(VendorCategory), nullable=False)
    contact_person = Column(String(255))
    email = Column(String(255))
    phone = Column(String(20))
    tax_id = Column(String(50))
    address = Column(Text)
    payment_terms = Column(SQLEnum(PaymentTerms), default=PaymentTerms.NET_30)
    status = Column(SQLEnum(VendorStatus), default=VendorStatus.ACTIVE)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    invoices = relationship("Invoice", back_populates="vendor")
    payments = relationship("Payment", back_populates="vendor")
    
    @property
    def outstanding_balance(self):
        return sum(invoice.balance_due for invoice in self.invoices if invoice.balance_due > 0)

class Invoice(Base):
    __tablename__ = "ap_invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(100), unique=True, nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("ap_vendors.id"), nullable=False)
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    description = Column(Text)
    subtotal = Column(Decimal(15, 2), nullable=False, default=0)
    tax_amount = Column(Decimal(15, 2), default=0)
    total_amount = Column(Decimal(15, 2), nullable=False)
    paid_amount = Column(Decimal(15, 2), default=0)
    balance_due = Column(Decimal(15, 2), nullable=False)
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    
    # Approval fields
    approved_by = Column(String(255))
    approved_at = Column(DateTime(timezone=True))
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    vendor = relationship("Vendor", back_populates="invoices")
    lines = relationship("InvoiceLine", back_populates="invoice", cascade="all, delete-orphan")
    payment_applications = relationship("PaymentInvoice", back_populates="invoice")
    
    @property
    def vendor_name(self):
        return self.vendor.name if self.vendor else ""

class InvoiceLine(Base):
    __tablename__ = "ap_invoice_lines"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("ap_invoices.id"), nullable=False)
    description = Column(String(500), nullable=False)
    quantity = Column(Decimal(10, 4), nullable=False, default=1)
    unit_price = Column(Decimal(15, 2), nullable=False)
    line_total = Column(Decimal(15, 2), nullable=False)
    account_id = Column(Integer, ForeignKey("gl_accounts.id"))
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    invoice = relationship("Invoice", back_populates="lines")

class Payment(Base):
    __tablename__ = "ap_payments"
    
    id = Column(Integer, primary_key=True, index=True)
    payment_number = Column(String(100), unique=True, nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("ap_vendors.id"), nullable=False)
    payment_date = Column(Date, nullable=False)
    amount = Column(Decimal(15, 2), nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    reference_number = Column(String(100))
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    notes = Column(Text)
    
    # Processing fields
    processed_at = Column(DateTime(timezone=True))
    processed_by = Column(String(255))
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    vendor = relationship("Vendor", back_populates="payments")
    invoice_applications = relationship("PaymentInvoice", back_populates="payment")
    
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
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    payment = relationship("Payment", back_populates="invoice_applications")
    invoice = relationship("Invoice", back_populates="payment_applications")