"""
Unified Core Models for Paksa Financial System
==============================================
Standardized models that eliminate duplicates and provide consistent data structure
across all modules: GL, AP, AR, Payroll, Inventory, Tax, HRM, etc.
"""

from sqlalchemy import Column, String, Integer, Numeric, DateTime, Boolean, Text, ForeignKey, Date, Enum
from app.models.base import GUID
from sqlalchemy.orm import relationship, foreign
from sqlalchemy.sql import func
from app.models.base import Base, BaseModel, AuditMixin
import uuid
from datetime import datetime
from enum import Enum as PyEnum

# Define required enums locally to avoid circular imports
class EmploymentType(str, PyEnum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    TEMPORARY = "temporary"

class LeaveType(str, PyEnum):
    ANNUAL = "annual"
    SICK = "sick"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    PERSONAL = "personal"

class LeaveStatus(str, PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class VendorStatus(str, PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class CreditMemoStatus(str, PyEnum):
    ACTIVE = "active"
    FULLY_APPLIED = "fully_applied"
    VOIDED = "voided"

class CustomerStatus(str, PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class InvoiceStatus(str, PyEnum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class PaymentStatus(str, PyEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class CollectionStatus(str, PyEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class PaymentMethod(str, PyEnum):
    CASH = "cash"
    CHECK = "check"
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    ACH = "ach"

class InventoryStatus(str, PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"

class PurchaseOrderStatus(str, PyEnum):
    DRAFT = "draft"
    SENT = "sent"
    RECEIVED = "received"
    CANCELLED = "cancelled"

class TaxType(str, PyEnum):
    SALES = "sales"
    PURCHASE = "purchase"
    VAT = "vat"
    GST = "gst"

class CompanyStatus(str, PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class ExchangeRateType(str, PyEnum):
    SPOT = "spot"
    FORWARD = "forward"
    HISTORICAL = "historical"

class JournalEntryStatus(str, PyEnum):
    DRAFT = "draft"
    POSTED = "posted"
    REVERSED = "reversed"

# ============================================================================
# CORE FINANCIAL ENTITIES
# ============================================================================

class ChartOfAccounts(Base):
    """Unified Chart of Accounts for all modules"""
    __tablename__ = "chart_of_accounts"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), nullable=False, index=True)
    account_code = Column(String(20), nullable=False, unique=True, index=True)
    account_name = Column(String(255), nullable=False)
    account_type = Column(String(50), nullable=False)  # Asset, Liability, Equity, Revenue, Expense
    balance = Column(Numeric(15, 2), default=0)
    is_active = Column(Boolean, default=True)

class JournalEntry(Base, AuditMixin):
    """Unified Journal Entry for all modules"""
    __tablename__ = "journal_entries"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), nullable=False, index=True)
    entry_number = Column(String(50), nullable=False, unique=True)
    entry_date = Column(Date, nullable=False, index=True)
    description = Column(Text, nullable=False)
    reference = Column(String(100))
    total_debit = Column(Numeric(15, 2), default=0)
    total_credit = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), default=0)  # Added for main.py compatibility
    status = Column(String(20), default='draft', index=True)  # draft, posted, reversed
    source_module = Column(String(20))  # GL, AP, AR, Payroll, Inventory
    
    # Relationships
    lines = relationship("JournalEntryLine", back_populates="journal_entry", cascade="all, delete-orphan")

class JournalEntryLine(Base):
    """Unified Journal Entry Lines"""
    __tablename__ = "journal_entry_lines"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    journal_entry_id = Column(GUID(), ForeignKey("journal_entries.id"), nullable=False)
    account_id = Column(GUID(), ForeignKey("chart_of_accounts.id"), nullable=False)
    description = Column(String(255))
    debit_amount = Column(Numeric(15, 2), default=0)
    credit_amount = Column(Numeric(15, 2), default=0)
    line_number = Column(Integer, nullable=False)
    
    # Relationships
    journal_entry = relationship("JournalEntry", back_populates="lines")

# ============================================================================
# VENDOR MANAGEMENT (Unified for AP & Procurement)
# ============================================================================

class Vendor(Base, AuditMixin):
    """Unified Vendor for AP and Procurement"""
    __tablename__ = "vendors"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), nullable=False, index=True)
    vendor_code = Column(String(20), nullable=False, unique=True)
    vendor_name = Column(String(255), nullable=False)
    contact_person = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    tax_id = Column(String(50))
    payment_terms = Column(String(50))
    credit_limit = Column(Numeric(15, 2), default=0)
    current_balance = Column(Numeric(15, 2), default=0)
    status = Column(Enum(VendorStatus), default=VendorStatus.ACTIVE)
    
    # Relationships
    invoices = relationship("APInvoice", back_populates="vendor")
    payments = relationship("APPayment", back_populates="vendor")
    purchase_orders = relationship("PurchaseOrder", back_populates="vendor")

class VendorContact(Base):
    """Vendor Contact Information"""
    __tablename__ = "vendor_contacts"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    vendor_id = Column(GUID(), ForeignKey("vendors.id"), nullable=False)
    contact_name = Column(String(255), nullable=False)
    title = Column(String(100))
    email = Column(String(255))
    phone = Column(String(50))
    is_primary = Column(Boolean, default=False)

# ============================================================================
# CUSTOMER MANAGEMENT (Unified for AR & Sales)
# ============================================================================


class VendorPortalAccess(Base, AuditMixin):
    """Vendor portal access invitation and status tracking."""
    __tablename__ = "vendor_portal_access"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    vendor_id = Column(GUID(), ForeignKey("vendors.id"), nullable=False, index=True)
    portal_email = Column(String(255), nullable=False)
    access_token = Column(String(128), nullable=False, unique=True)
    status = Column(String(20), default="invited")
    invited_at = Column(DateTime, default=datetime.utcnow)
    activated_at = Column(DateTime)

    vendor = relationship("Vendor")


class VendorPaymentInstruction(Base, AuditMixin):
    """Vendor ACH/Wire payment instruction profile."""
    __tablename__ = "vendor_payment_instructions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    vendor_id = Column(GUID(), ForeignKey("vendors.id"), nullable=False, index=True)
    payment_method = Column(String(20), nullable=False)  # ach|wire
    account_name = Column(String(255), nullable=False)
    account_number_last4 = Column(String(4), nullable=False)
    routing_number = Column(String(50))
    bank_name = Column(String(255))
    swift_code = Column(String(50))
    is_active = Column(Boolean, default=True)

    vendor = relationship("Vendor")

class Customer(Base, AuditMixin):
    """Unified Customer for AR and Sales"""
    __tablename__ = "customers"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), nullable=False, index=True)
    customer_code = Column(String(20), nullable=False, unique=True)
    customer_name = Column(String(255), nullable=False)
    contact_person = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    tax_id = Column(String(50))
    payment_terms = Column(String(50))
    credit_limit = Column(Numeric(15, 2), default=0)
    current_balance = Column(Numeric(15, 2), default=0)
    status = Column(Enum(CustomerStatus), default=CustomerStatus.ACTIVE)
    
    # Relationships
    invoices = relationship("ARInvoice", back_populates="customer")
    payments = relationship("ARPayment", back_populates="customer")

class CustomerContact(Base):
    """Customer Contact Information"""
    __tablename__ = "customer_contacts"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    customer_id = Column(GUID(), ForeignKey("customers.id"), nullable=False)
    contact_name = Column(String(255), nullable=False)
    title = Column(String(100))
    email = Column(String(255))
    phone = Column(String(50))
    is_primary = Column(Boolean, default=False)

# ============================================================================
# ACCOUNTS PAYABLE
# ============================================================================

class APInvoice(Base, AuditMixin):
    """Unified AP Invoice"""
    __tablename__ = "ap_invoices"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), nullable=False, index=True)
    vendor_id = Column(GUID(), ForeignKey("vendors.id"), nullable=False)
    invoice_number = Column(String(50), nullable=False, unique=True)
    invoice_date = Column(Date, nullable=False, index=True)
    due_date = Column(Date, nullable=False, index=True)
    subtotal = Column(Numeric(15, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), nullable=False)
    paid_amount = Column(Numeric(15, 2), default=0)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    
    # Relationships
    vendor = relationship("Vendor", back_populates="invoices")
    line_items = relationship("APInvoiceLineItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("APPayment", secondary="ap_invoice_payments", back_populates="invoices")

class APInvoiceLineItem(Base):
    """AP Invoice Line Items"""
    __tablename__ = "ap_invoice_line_items"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(GUID(), ForeignKey("ap_invoices.id"), nullable=False)
    account_id = Column(GUID(), ForeignKey("chart_of_accounts.id"), nullable=False)
    description = Column(String(255), nullable=False)
    quantity = Column(Numeric(10, 2), default=1)
    unit_price = Column(Numeric(15, 2), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    
    # Relationships
    invoice = relationship("APInvoice", back_populates="line_items")
    account = relationship("ChartOfAccounts")

class APPayment(Base, AuditMixin):
    """Unified AP Payment"""
    __tablename__ = "ap_payments"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), nullable=False, index=True)
    vendor_id = Column(GUID(), ForeignKey("vendors.id"), nullable=False)
    payment_number = Column(String(50), nullable=False, unique=True)
    payment_date = Column(Date, nullable=False, index=True)
    amount = Column(Numeric(15, 2), nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    reference = Column(String(100))
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Relationships
    vendor = relationship("Vendor", back_populates="payments")
    invoices = relationship("APInvoice", secondary="ap_invoice_payments", back_populates="payments")

class APInvoicePayment(Base):
    """AP Invoice Payment Association"""
    __tablename__ = "ap_invoice_payments"
    
    invoice_id = Column(GUID(), ForeignKey("ap_invoices.id"), primary_key=True)
    payment_id = Column(GUID(), ForeignKey("ap_payments.id"), primary_key=True)
    amount = Column(Numeric(15, 2), nullable=False)

class APCreditMemo(Base, AuditMixin):
    """AP Credit Memo"""
    __tablename__ = "ap_credit_memos"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), nullable=False, index=True)
    vendor_id = Column(GUID(), ForeignKey("vendors.id"), nullable=False)
    credit_memo_number = Column(String(50), nullable=False, unique=True)
    credit_date = Column(Date, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    applied_amount = Column(Numeric(15, 2), default=0)
    remaining_amount = Column(Numeric(15, 2), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="active")
    
    # Relationships
    vendor = relationship("Vendor")
    applications = relationship("APCreditApplication", back_populates="credit_memo", cascade="all, delete-orphan")

class APCreditApplication(Base):
    """AP Credit Memo Application"""
    __tablename__ = "ap_credit_applications"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    credit_memo_id = Column(GUID(), ForeignKey("ap_credit_memos.id"), nullable=False)
    invoice_id = Column(GUID(), ForeignKey("ap_invoices.id"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    notes = Column(Text)
    
    # Relationships
    credit_memo = relationship("APCreditMemo", back_populates="applications")
    invoice = relationship("APInvoice")

class Form1099(Base, AuditMixin):
    """Form 1099 for Tax Reporting"""
    __tablename__ = "form_1099s"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), nullable=False, index=True)
    vendor_id = Column(GUID(), ForeignKey("vendors.id"), nullable=False)
    tax_year = Column(Integer, nullable=False)
    form_type = Column(String(10), default="1099-NEC")
    box_1_rents = Column(Numeric(15, 2), default=0)
    box_2_royalties = Column(Numeric(15, 2), default=0)
    box_3_other_income = Column(Numeric(15, 2), default=0)
    box_5_fishing_boat_proceeds = Column(Numeric(15, 2), default=0)
    box_6_medical_health_payments = Column(Numeric(15, 2), default=0)
    box_7_nonemployee_compensation = Column(Numeric(15, 2), default=0)
    box_8_substitute_payments = Column(Numeric(15, 2), default=0)
    box_9_payer_direct_sales = Column(Numeric(15, 2), default=0)
    box_10_crop_insurance = Column(Numeric(15, 2), default=0)
    box_13_state_income = Column(Numeric(15, 2), default=0)
    box_14_gross_proceeds = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), nullable=False)
    status = Column(String(20), default="draft")
    filed_date = Column(Date)
    void = Column(Boolean, default=False)
    notes = Column(Text)
    
    # Relationships
    vendor = relationship("Vendor")
    transactions = relationship("Form1099Transaction", back_populates="form_1099", cascade="all, delete-orphan")

class Form1099Transaction(Base):
    """Form 1099 Transaction Details"""
    __tablename__ = "form_1099_transactions"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    form_1099_id = Column(GUID(), ForeignKey("form_1099s.id"), nullable=False)
    payment_id = Column(GUID(), ForeignKey("ap_payments.id"))
    amount = Column(Numeric(15, 2), nullable=False)
    box_number = Column(Integer, nullable=False)
    description = Column(String(255))
    
    # Relationships
    form_1099 = relationship("Form1099", back_populates="transactions")
    payment = relationship("APPayment")

# ============================================================================
# ACCOUNTS RECEIVABLE
# ============================================================================

class ARInvoice(Base, AuditMixin):
    """Unified AR Invoice"""
    __tablename__ = "ar_invoices"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), nullable=False, index=True)
    customer_id = Column(GUID(), ForeignKey("customers.id"), nullable=False)
    invoice_number = Column(String(50), nullable=False, unique=True)
    invoice_date = Column(Date, nullable=False, index=True)
    due_date = Column(Date, nullable=False, index=True)
    subtotal = Column(Numeric(15, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), nullable=False)
    paid_amount = Column(Numeric(15, 2), default=0)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    
    # Relationships
    customer = relationship("Customer", back_populates="invoices")
    line_items = relationship("ARInvoiceLineItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("ARPayment", secondary="ar_invoice_payments", back_populates="invoices")

class ARInvoiceLineItem(Base):
    """AR Invoice Line Items"""
    __tablename__ = "ar_invoice_line_items"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(GUID(), ForeignKey("ar_invoices.id"), nullable=False)
    account_id = Column(GUID(), ForeignKey("chart_of_accounts.id"), nullable=False)
    description = Column(String(255), nullable=False)
    quantity = Column(Numeric(10, 2), default=1)
    unit_price = Column(Numeric(15, 2), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    
    # Relationships
    invoice = relationship("ARInvoice", back_populates="line_items")
    account = relationship("ChartOfAccounts")

class ARPayment(Base, AuditMixin):
    """Unified AR Payment"""
    __tablename__ = "ar_payments"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), nullable=False, index=True)
    customer_id = Column(GUID(), ForeignKey("customers.id"), nullable=False)
    payment_number = Column(String(50), nullable=False, unique=True)
    payment_date = Column(Date, nullable=False, index=True)
    amount = Column(Numeric(15, 2), nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    reference = Column(String(100))
    status = Column(Enum(PaymentStatus), default=PaymentStatus.COMPLETED)
    
    # Relationships
    customer = relationship("Customer", back_populates="payments")
    invoices = relationship("ARInvoice", secondary="ar_invoice_payments", back_populates="payments")

class ARInvoicePayment(Base):
    """AR Invoice Payment Association"""
    __tablename__ = "ar_invoice_payments"
    
    invoice_id = Column(GUID(), ForeignKey("ar_invoices.id"), primary_key=True)
    payment_id = Column(GUID(), ForeignKey("ar_payments.id"), primary_key=True)
    amount = Column(Numeric(15, 2), nullable=False)

class Collection(Base, AuditMixin):
    """AR Collections Management"""
    __tablename__ = "ar_collections"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), nullable=False, index=True)
    customer_id = Column(GUID(), ForeignKey("customers.id"), nullable=False)
    invoice_id = Column(GUID(), ForeignKey("ar_invoices.id"))
    amount_due = Column(Numeric(15, 2), nullable=False)
    days_overdue = Column(Integer, default=0)
    status = Column(String(20), default="open")
    priority = Column(String(20), default="medium")
    assigned_to = Column(String(255))
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    customer = relationship("Customer")
    invoice = relationship("ARInvoice")

class CollectionActivity(Base):
    """Collection Activity Log"""
    __tablename__ = "collection_activities"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    collection_id = Column(GUID(), ForeignKey("ar_collections.id"), nullable=False)
    activity_type = Column(String(50), nullable=False)
    activity_date = Column(DateTime, default=func.now())
    description = Column(Text)
    outcome = Column(String(100))
    next_action = Column(String(255))
    
    # Relationships
    collection = relationship("Collection")

# ============================================================================
# EMPLOYEE & HRM (Unified)
# ============================================================================

class Employee(Base, AuditMixin):
    """Unified Employee for HRM and Payroll"""
    __tablename__ = "employees"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), nullable=False, index=True)
    employee_code = Column(String(20), nullable=False, unique=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True)
    phone = Column(String(50))
    hire_date = Column(Date, nullable=False)
    termination_date = Column(Date)
    department_id = Column(GUID(), ForeignKey("departments.id"))
    department = Column(String(100))  # For compatibility
    position = Column(String(100))
    salary = Column(Numeric(15, 2))
    employment_type = Column(Enum(EmploymentType), default=EmploymentType.FULL_TIME)
    status = Column(String(20), default='active')
    
    # Relationships
    department_rel = relationship("Department", back_populates="employees", foreign_keys=[department_id])
    payroll_entries = relationship("PayrollEntry", back_populates="employee")
    leave_requests = relationship("LeaveRequest", back_populates="employee")

class Department(Base, AuditMixin):
    """Unified Department"""
    __tablename__ = "departments"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), nullable=False, index=True)
    department_code = Column(String(20), nullable=False, unique=True)
    department_name = Column(String(255), nullable=False)
    manager_id = Column(GUID(), ForeignKey("employees.id"))
    employee_count = Column(Integer, default=0)  # For compatibility
    cost_center = Column(String(50))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    employees = relationship("Employee", back_populates="department_rel", foreign_keys="Employee.department_id")
    manager = relationship("Employee", foreign_keys=[manager_id])

# ============================================================================
# PAYROLL (Unified)
# ============================================================================

class PayrollRun(Base, AuditMixin):
    """Unified Payroll Run"""
    __tablename__ = "payroll_runs"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), nullable=False, index=True)
    run_number = Column(String(50), nullable=False, unique=True)
    pay_period = Column(String(50))  # For compatibility
    pay_period_start = Column(Date, nullable=False)
    pay_period_end = Column(Date, nullable=False)
    pay_date = Column(Date, nullable=False)
    status = Column(String(20), default='draft')
    total_gross_pay = Column(Numeric(15, 2), default=0)  # For compatibility
    total_gross = Column(Numeric(15, 2), default=0)
    total_deductions = Column(Numeric(15, 2), default=0)
    total_net_pay = Column(Numeric(15, 2), default=0)  # For compatibility
    total_net = Column(Numeric(15, 2), default=0)
    employee_count = Column(Integer, default=0)
    
    # Relationships
    entries = relationship("PayrollEntry", back_populates="payroll_run", cascade="all, delete-orphan")

class PayrollEntry(Base):
    """Unified Payroll Entry"""
    __tablename__ = "payroll_entries"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    payroll_run_id = Column(GUID(), ForeignKey("payroll_runs.id"), nullable=False)
    employee_id = Column(GUID(), ForeignKey("employees.id"), nullable=False)
    gross_pay = Column(Numeric(15, 2), default=0)
    total_deductions = Column(Numeric(15, 2), default=0)
    net_pay = Column(Numeric(15, 2), default=0)
    
    # Relationships
    payroll_run = relationship("PayrollRun", back_populates="entries")
    employee = relationship("Employee", back_populates="payroll_entries")

class Payslip(Base, AuditMixin):
    """Payslip for individual employee"""
    __tablename__ = "payslips"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    payroll_run_id = Column(GUID(), ForeignKey("payroll_runs.id"), nullable=False)
    employee_id = Column(GUID(), ForeignKey("employees.id"), nullable=False)
    pay_period = Column(String(50))
    pay_period_start = Column(Date)
    pay_period_end = Column(Date)
    pay_date = Column(Date)
    gross_pay = Column(Numeric(15, 2), default=0)
    total_deductions = Column(Numeric(15, 2), default=0)
    net_pay = Column(Numeric(15, 2), default=0)
    
    # Relationships
    payroll_run = relationship("PayrollRun")
    employee = relationship("Employee")

class LeaveRequest(Base, AuditMixin):
    """Unified Leave Request"""
    __tablename__ = "leave_requests"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    employee_id = Column(GUID(), ForeignKey("employees.id"), nullable=False)
    leave_type = Column(Enum(LeaveType), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    days_requested = Column(Integer, nullable=False)
    reason = Column(Text)
    status = Column(Enum(LeaveStatus), default=LeaveStatus.PENDING)
    
    # Relationships
    employee = relationship("Employee", back_populates="leave_requests")

# ============================================================================
# INVENTORY & PROCUREMENT (Unified)
# ============================================================================

class InventoryItem(Base, AuditMixin):
    """Unified Inventory Item"""
    __tablename__ = "inventory_items"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), nullable=False, index=True)
    item_code = Column(String(50), nullable=False, unique=True)
    item_name = Column(String(255), nullable=False)
    description = Column(Text)
    category_id = Column(GUID(), ForeignKey("inventory_categories.id"))
    unit_of_measure = Column(String(20))
    unit_cost = Column(Numeric(15, 2), default=0)
    selling_price = Column(Numeric(15, 2), default=0)
    quantity_on_hand = Column(Numeric(10, 2), default=0)
    reorder_level = Column(Numeric(10, 2), default=0)
    status = Column(Enum(InventoryStatus), default=InventoryStatus.ACTIVE)
    
    # Relationships
    category = relationship("InventoryCategory", back_populates="items")

class InventoryCategory(Base, AuditMixin):
    """Inventory Category"""
    __tablename__ = "inventory_categories"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), nullable=False, index=True)
    category_code = Column(String(20), nullable=False, unique=True)
    category_name = Column(String(255), nullable=False)
    parent_category_id = Column(GUID(), ForeignKey("inventory_categories.id"))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    items = relationship("InventoryItem", back_populates="category")
    parent_category = relationship("InventoryCategory", remote_side="InventoryCategory.id")

class InventoryLocation(Base, AuditMixin):
    """Inventory Location"""
    __tablename__ = "inventory_locations"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), nullable=False, index=True)
    location_code = Column(String(20), nullable=False, unique=True)
    location_name = Column(String(255), nullable=False)
    address = Column(Text)
    capacity = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

class PurchaseOrder(Base, AuditMixin):
    """Unified Purchase Order"""
    __tablename__ = "purchase_orders"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), nullable=False, index=True)
    vendor_id = Column(GUID(), ForeignKey("vendors.id"), nullable=False)
    po_number = Column(String(50), nullable=False, unique=True)
    po_date = Column(Date, nullable=False)
    expected_date = Column(Date)
    total_amount = Column(Numeric(15, 2), default=0)
    status = Column(Enum(PurchaseOrderStatus), default=PurchaseOrderStatus.DRAFT)
    
    # Relationships
    vendor = relationship("Vendor", back_populates="purchase_orders")
    line_items = relationship("PurchaseOrderLineItem", back_populates="purchase_order", cascade="all, delete-orphan")

class PurchaseOrderLineItem(Base):
    """Purchase Order Line Items"""
    __tablename__ = "purchase_order_line_items"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    purchase_order_id = Column(GUID(), ForeignKey("purchase_orders.id"), nullable=False)
    inventory_item_id = Column(GUID(), ForeignKey("inventory_items.id"))
    description = Column(String(255), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(15, 2), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="line_items")
    inventory_item = relationship("InventoryItem")

# ============================================================================
# TAX MANAGEMENT (Unified)
# ============================================================================

class TaxRate(Base, AuditMixin):
    """Unified Tax Rate"""
    __tablename__ = "tax_rates"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), nullable=False, index=True)
    tax_code = Column(String(20), nullable=False, unique=True)
    tax_name = Column(String(255), nullable=False)
    rate = Column(Numeric(5, 4), nullable=False)  # For compatibility
    rate_percentage = Column(Numeric(5, 4), nullable=False)
    tax_type = Column(Enum(TaxType), nullable=False)
    jurisdiction = Column(String(100))
    effective_date = Column(Date, nullable=False)
    expiry_date = Column(Date)
    is_active = Column(Boolean, default=True)

class TaxReturn(Base, AuditMixin):
    """Tax Return"""
    __tablename__ = "tax_returns"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), nullable=False, index=True)
    return_type = Column(String(50), nullable=False)
    tax_period = Column(String(50), nullable=False)
    jurisdiction = Column(String(100))
    due_date = Column(Date, nullable=False)
    amount_due = Column(Numeric(15, 2), default=0)
    status = Column(String(20), default="draft")
    filed_date = Column(Date)
    
class TaxTransaction(Base, AuditMixin):
    """Tax Transaction"""
    __tablename__ = "tax_transactions"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), nullable=False, index=True)
    entity_type = Column(String(20), nullable=False)
    entity_id = Column(GUID(), nullable=False)
    entity_name = Column(String(255), nullable=False)
    transaction_date = Column(Date, nullable=False)
    taxable_amount = Column(Numeric(15, 2), nullable=False)
    tax_amount = Column(Numeric(15, 2), nullable=False)
    total_amount = Column(Numeric(15, 2), nullable=False)
    tax_rate = Column(Numeric(5, 4), nullable=False)
    jurisdiction_name = Column(String(100))
    reference_number = Column(String(100))
    description = Column(Text)

# CashTransaction model exists in reconciliation_core.py - removed duplicate

# ============================================================================
# FINANCIAL PERIODS & REPORTING
# ============================================================================

class FinancialPeriod(Base, AuditMixin):
    """Unified Financial Period"""
    __tablename__ = "financial_periods"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), nullable=False, index=True)
    period_name = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    period_type = Column(String(20), nullable=False)  # monthly, quarterly, yearly
    is_current = Column(Boolean, default=False)
    is_closed = Column(Boolean, default=False)
    closed_at = Column(DateTime)

class Budget(Base, AuditMixin):
    """Unified Budget"""
    __tablename__ = "budgets"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), nullable=False, index=True)
    budget_name = Column(String(255), nullable=False)
    budget_year = Column(Integer, nullable=False)
    account_id = Column(GUID(), ForeignKey("chart_of_accounts.id"))
    total_amount = Column(Numeric(15, 2), default=0)  # For compatibility
    budgeted_amount = Column(Numeric(15, 2), nullable=False)
    actual_amount = Column(Numeric(15, 2), default=0)
    variance = Column(Numeric(15, 2), default=0)
    status = Column(String(20), default='draft')
    
    # Relationships
    account = relationship("ChartOfAccounts")
    line_items = relationship("BudgetLineItem", back_populates="budget", cascade="all, delete-orphan")

class BudgetLineItem(Base, AuditMixin):
    """Unified Budget Line Item"""
    __tablename__ = "budget_line_items"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    budget_id = Column(GUID(), ForeignKey("budgets.id"), nullable=False)
    account_id = Column(GUID(), ForeignKey("chart_of_accounts.id"), nullable=False)
    period = Column(String(20), nullable=False)  # monthly, quarterly
    budgeted_amount = Column(Numeric(15, 2), nullable=False)
    actual_amount = Column(Numeric(15, 2), default=0)
    variance = Column(Numeric(15, 2), default=0)
    
    # Relationships
    budget = relationship("Budget", back_populates="line_items")
    account = relationship("ChartOfAccounts")

# ============================================================================
# FIXED ASSETS (Unified)
# ============================================================================

class AssetCategory(Base, AuditMixin):
    """Asset Category"""
    __tablename__ = "asset_categories"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    default_useful_life = Column(Integer, default=5)
    default_depreciation_method = Column(String(50), default="straight_line")
    default_salvage_rate = Column(Numeric(5, 4), default=0.1)
    is_active = Column(Boolean, default=True)

class FixedAsset(Base, AuditMixin):
    """Unified Fixed Asset"""
    __tablename__ = "fixed_assets"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), nullable=False, index=True)
    asset_number = Column(String(50), unique=True, nullable=False)
    asset_name = Column(String(255), nullable=False)
    description = Column(Text)
    category_id = Column(GUID(), ForeignKey("asset_categories.id"))
    location = Column(String(255))
    purchase_date = Column(Date, nullable=False)
    purchase_cost = Column(Numeric(15, 2), nullable=False)
    salvage_value = Column(Numeric(15, 2), default=0)
    useful_life_years = Column(Integer, nullable=False)
    depreciation_method = Column(String(50), default="straight_line")
    accumulated_depreciation = Column(Numeric(15, 2), default=0)
    current_value = Column(Numeric(15, 2))
    status = Column(String(20), default="active")
    vendor_name = Column(String(200))
    warranty_expiry = Column(Date)
    serial_number = Column(String(100))
    model_number = Column(String(100))
    
    # Relationships
    category = relationship("AssetCategory", backref="assets")
    maintenance_records = relationship("MaintenanceRecord", back_populates="asset")

class MaintenanceRecord(Base, AuditMixin):
    """Asset Maintenance Records"""
    __tablename__ = "maintenance_records"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    asset_id = Column(GUID(), ForeignKey("fixed_assets.id"), nullable=False)
    maintenance_type = Column(String(50), nullable=False)  # preventive, corrective, emergency
    description = Column(Text, nullable=False)
    scheduled_date = Column(Date, nullable=False)
    completed_date = Column(Date)
    status = Column(String(20), default="scheduled")  # scheduled, in_progress, completed, cancelled
    estimated_cost = Column(Numeric(15, 2))
    actual_cost = Column(Numeric(15, 2))
    vendor_name = Column(String(200))
    technician_name = Column(String(200))
    notes = Column(Text)
    created_by = Column(String(200))
    
    # Relationships
    asset = relationship("FixedAsset", back_populates="maintenance_records")

class AssetDepreciation(Base):
    """Asset Depreciation Records"""
    __tablename__ = "asset_depreciation"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    asset_id = Column(GUID(), ForeignKey("fixed_assets.id"), nullable=False)
    depreciation_date = Column(Date, nullable=False)
    depreciation_amount = Column(Numeric(15, 2), nullable=False)
    accumulated_depreciation = Column(Numeric(15, 2), nullable=False)
    book_value = Column(Numeric(15, 2), nullable=False)
    notes = Column(Text)
    
    # Relationships
    asset = relationship("FixedAsset")

# ============================================================================
# SYSTEM & CONFIGURATION
# ============================================================================

class Company(Base, AuditMixin):
    """Unified Company"""
    __tablename__ = "companies"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_code = Column(String(20), nullable=False, unique=True)
    company_name = Column(String(255), nullable=False)
    legal_name = Column(String(255))
    tax_id = Column(String(50))
    address = Column(Text)
    phone = Column(String(50))
    email = Column(String(255))
    website = Column(String(255))
    base_currency = Column(String(3), default='USD')
    fiscal_year_end = Column(String(5), default='12-31')
    status = Column(Enum(CompanyStatus), default=CompanyStatus.ACTIVE)

class Currency(Base, AuditMixin):
    """Unified Currency"""
    __tablename__ = "currencies"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    currency_code = Column(String(3), nullable=False, unique=True)
    currency_name = Column(String(100), nullable=False)
    symbol = Column(String(10))
    decimal_places = Column(Integer, default=2)
    is_active = Column(Boolean, default=True)

class ExchangeRate(Base):
    """Unified Exchange Rate"""
    __tablename__ = "exchange_rates"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    from_currency = Column(String(3), nullable=False)
    to_currency = Column(String(3), nullable=False)
    rate = Column(Numeric(15, 6), nullable=False)
    rate_date = Column(Date, nullable=False)
    rate_type = Column(Enum(ExchangeRateType), default=ExchangeRateType.SPOT)

class BankAccount(Base, AuditMixin):
    """Bank Account"""
    __tablename__ = "bank_accounts"
    __table_args__ = {'extend_existing': True}
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), nullable=False, index=True)
    account_name = Column(String(255), nullable=False)
    account_number = Column(String(50), nullable=False)
    bank_name = Column(String(255), nullable=False)
    current_balance = Column(Numeric(15, 2), default=0)
    is_active = Column(Boolean, default=True)


class BankFeedConnection(Base, AuditMixin):
    """Automated bank feed integration profile."""
    __tablename__ = "bank_feed_connections"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), nullable=False, index=True)
    account_id = Column(GUID(), ForeignKey("bank_accounts.id"), nullable=False, index=True)
    provider = Column(String(100), nullable=False)
    provider_account_id = Column(String(150), nullable=False)
    status = Column(String(20), default="active")
    last_sync_at = Column(DateTime)


class CashConcentrationRule(Base, AuditMixin):
    """Rules for sweeping balances into a concentration account."""
    __tablename__ = "cash_concentration_rules"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), nullable=False, index=True)
    source_account_id = Column(GUID(), ForeignKey("bank_accounts.id"), nullable=False)
    concentration_account_id = Column(GUID(), ForeignKey("bank_accounts.id"), nullable=False)
    min_source_balance = Column(Numeric(15, 2), default=0)
    transfer_frequency = Column(String(20), default="daily")
    is_active = Column(Boolean, default=True)


class ZeroBalanceAccountConfig(Base, AuditMixin):
    """Configuration for zero balance account (ZBA) operation."""
    __tablename__ = "zero_balance_account_configs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), nullable=False, index=True)
    child_account_id = Column(GUID(), ForeignKey("bank_accounts.id"), nullable=False)
    funding_account_id = Column(GUID(), ForeignKey("bank_accounts.id"), nullable=False)
    target_balance = Column(Numeric(15, 2), default=0)
    is_active = Column(Boolean, default=True)


class InvestmentSweepConfig(Base, AuditMixin):
    """Configuration for investment sweep account behavior."""
    __tablename__ = "investment_sweep_configs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), nullable=False, index=True)
    operating_account_id = Column(GUID(), ForeignKey("bank_accounts.id"), nullable=False)
    investment_account_name = Column(String(255), nullable=False)
    sweep_threshold = Column(Numeric(15, 2), default=0)
    target_operating_balance = Column(Numeric(15, 2), default=0)
    is_active = Column(Boolean, default=True)

# CashTransaction already exists in reconciliation_core.py - removing duplicate

class User(Base, AuditMixin):
    """System User"""
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

class Transaction(Base, AuditMixin):
    """Generic Transaction for analytics"""
    __tablename__ = "transactions"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), nullable=False, index=True)
    transaction_type = Column(String(50), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    description = Column(Text)
    reference_id = Column(GUID())
    reference_type = Column(String(50))

class Notification(Base):
    """System Notifications"""
    __tablename__ = "notifications"
    __table_args__ = {'extend_existing': True}
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), default="info")
    is_read = Column(Boolean, default=False)
    priority = Column(String(20), default="normal")
    action_url = Column(String(500))
    created_at = Column(DateTime, default=func.now(), nullable=False)

class SystemConfiguration(Base, AuditMixin):
    """System Configuration Storage"""
    __tablename__ = "system_configurations"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    module = Column(String(50), nullable=False, index=True)
    config_key = Column(String(100), nullable=False)
    config_value = Column(Text, nullable=False)
    data_type = Column(String(20), default="string")  # string, number, boolean, json
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    __table_args__ = ({'extend_existing': True},)

class SystemSetting(Base, AuditMixin):
    """System Settings Storage"""
    __tablename__ = "system_settings"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    setting_key = Column(String(100), nullable=False, unique=True, index=True)
    setting_value = Column(Text, nullable=False)
    description = Column(Text)
    data_type = Column(String(20), default="string")  # string, number, boolean, json
    is_active = Column(Boolean, default=True)
    
class FeatureFlag(Base, AuditMixin):
    """Feature Flags Management"""
    __tablename__ = "feature_flags"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    module = Column(String(50), nullable=False)
    description = Column(Text)
    enabled = Column(Boolean, default=False)
    rollout_percentage = Column(Integer, default=0)
    target_users = Column(Text)  # JSON array of user IDs
    conditions = Column(Text)  # JSON conditions for enabling
    is_active = Column(Boolean, default=True)