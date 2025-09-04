"""
Complete Database Setup for Paksa Financial System - ALL MODULES
"""
from sqlalchemy import create_engine, Column, String, Integer, Numeric, DateTime, Boolean, Text, ForeignKey, Index
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid
import os

def generate_uuid():
    return str(uuid.uuid4())

# Database setup
DB_PATH = 'paksa_complete.db'
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

engine = create_engine(f'sqlite:///{DB_PATH}', echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# ===== CORE MODELS =====
class User(Base):
    __tablename__ = 'users'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Role(Base):
    __tablename__ = 'roles'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)

class Permission(Base):
    __tablename__ = 'permissions'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False)
    resource = Column(String(100), nullable=False)
    action = Column(String(50), nullable=False)

# ===== CHART OF ACCOUNTS =====
class ChartOfAccounts(Base):
    __tablename__ = 'chart_of_accounts'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    account_code = Column(String(20), unique=True, nullable=False)
    account_name = Column(String(255), nullable=False)
    account_type = Column(String(50), nullable=False)  # Asset, Liability, Equity, Revenue, Expense
    parent_id = Column(String(36), ForeignKey('chart_of_accounts.id'))
    normal_balance = Column(String(10), nullable=False)  # Debit, Credit
    current_balance = Column(Numeric(15, 2), default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# ===== GENERAL LEDGER =====
class JournalEntry(Base):
    __tablename__ = 'journal_entries'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    entry_number = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    reference = Column(String(100))
    entry_date = Column(DateTime, nullable=False)
    status = Column(String(20), default='draft')
    total_debit = Column(Numeric(15, 2), default=0)
    total_credit = Column(Numeric(15, 2), default=0)
    created_by = Column(String(36))
    created_at = Column(DateTime, default=datetime.utcnow)

class JournalEntryLine(Base):
    __tablename__ = 'journal_entry_lines'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    journal_entry_id = Column(String(36), ForeignKey('journal_entries.id'), nullable=False)
    account_id = Column(String(36), ForeignKey('chart_of_accounts.id'), nullable=False)
    description = Column(String(255))
    debit_amount = Column(Numeric(15, 2), default=0)
    credit_amount = Column(Numeric(15, 2), default=0)
    line_number = Column(Integer, nullable=False)

# ===== ACCOUNTS PAYABLE =====
class Vendor(Base):
    __tablename__ = 'vendors'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    vendor_code = Column(String(20), unique=True, nullable=False)
    vendor_name = Column(String(255), nullable=False)
    contact_person = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    tax_id = Column(String(50))
    payment_terms = Column(String(50))
    credit_limit = Column(Numeric(15, 2), default=0)
    current_balance = Column(Numeric(15, 2), default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Bill(Base):
    __tablename__ = 'bills'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    bill_number = Column(String(50), unique=True, nullable=False)
    vendor_id = Column(String(36), ForeignKey('vendors.id'), nullable=False)
    bill_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    total_amount = Column(Numeric(15, 2), nullable=False)
    paid_amount = Column(Numeric(15, 2), default=0)
    status = Column(String(20), default='pending')
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class VendorPayment(Base):
    __tablename__ = 'vendor_payments'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    payment_number = Column(String(50), unique=True, nullable=False)
    vendor_id = Column(String(36), ForeignKey('vendors.id'), nullable=False)
    bill_id = Column(String(36), ForeignKey('bills.id'))
    payment_date = Column(DateTime, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    payment_method = Column(String(50))
    reference = Column(String(100))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# ===== ACCOUNTS RECEIVABLE =====
class Customer(Base):
    __tablename__ = 'customers'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    customer_code = Column(String(20), unique=True, nullable=False)
    customer_name = Column(String(255), nullable=False)
    contact_person = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    tax_id = Column(String(50))
    payment_terms = Column(String(50))
    credit_limit = Column(Numeric(15, 2), default=0)
    current_balance = Column(Numeric(15, 2), default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Invoice(Base):
    __tablename__ = 'invoices'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    invoice_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(String(36), ForeignKey('customers.id'), nullable=False)
    invoice_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    total_amount = Column(Numeric(15, 2), nullable=False)
    paid_amount = Column(Numeric(15, 2), default=0)
    status = Column(String(20), default='pending')
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class CustomerPayment(Base):
    __tablename__ = 'customer_payments'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    payment_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(String(36), ForeignKey('customers.id'), nullable=False)
    invoice_id = Column(String(36), ForeignKey('invoices.id'))
    payment_date = Column(DateTime, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    payment_method = Column(String(50))
    reference = Column(String(100))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# ===== BANKING & CASH =====
class BankAccount(Base):
    __tablename__ = 'bank_accounts'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    account_name = Column(String(255), nullable=False)
    account_number = Column(String(50), nullable=False)
    bank_name = Column(String(255), nullable=False)
    routing_number = Column(String(20))
    account_type = Column(String(50))  # checking, savings, credit
    current_balance = Column(Numeric(15, 2), default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class BankTransaction(Base):
    __tablename__ = 'bank_transactions'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    bank_account_id = Column(String(36), ForeignKey('bank_accounts.id'), nullable=False)
    transaction_date = Column(DateTime, nullable=False)
    description = Column(String(255), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    transaction_type = Column(String(20))  # debit, credit
    reference = Column(String(100))
    reconciled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class BankReconciliation(Base):
    __tablename__ = 'bank_reconciliations'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    bank_account_id = Column(String(36), ForeignKey('bank_accounts.id'), nullable=False)
    statement_date = Column(DateTime, nullable=False)
    statement_balance = Column(Numeric(15, 2), nullable=False)
    book_balance = Column(Numeric(15, 2), nullable=False)
    reconciliation_difference = Column(Numeric(15, 2), default=0)
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)

# ===== BUDGETING =====
class Budget(Base):
    __tablename__ = 'budgets'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    budget_name = Column(String(255), nullable=False)
    budget_year = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String(20), default='draft')
    total_budget = Column(Numeric(15, 2), default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class BudgetLine(Base):
    __tablename__ = 'budget_lines'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    budget_id = Column(String(36), ForeignKey('budgets.id'), nullable=False)
    account_id = Column(String(36), ForeignKey('chart_of_accounts.id'), nullable=False)
    period = Column(String(20), nullable=False)  # monthly, quarterly, yearly
    budgeted_amount = Column(Numeric(15, 2), nullable=False)
    actual_amount = Column(Numeric(15, 2), default=0)
    variance = Column(Numeric(15, 2), default=0)

# ===== INVENTORY =====
class InventoryItem(Base):
    __tablename__ = 'inventory_items'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    item_code = Column(String(50), unique=True, nullable=False)
    item_name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    unit_of_measure = Column(String(20))
    unit_cost = Column(Numeric(15, 2), default=0)
    selling_price = Column(Numeric(15, 2), default=0)
    quantity_on_hand = Column(Numeric(15, 4), default=0)
    reorder_level = Column(Numeric(15, 4), default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class InventoryTransaction(Base):
    __tablename__ = 'inventory_transactions'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    item_id = Column(String(36), ForeignKey('inventory_items.id'), nullable=False)
    transaction_type = Column(String(20), nullable=False)  # purchase, sale, adjustment
    quantity = Column(Numeric(15, 4), nullable=False)
    unit_cost = Column(Numeric(15, 2), nullable=False)
    total_cost = Column(Numeric(15, 2), nullable=False)
    reference = Column(String(100))
    transaction_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# ===== FIXED ASSETS =====
class FixedAsset(Base):
    __tablename__ = 'fixed_assets'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    asset_code = Column(String(50), unique=True, nullable=False)
    asset_name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    purchase_date = Column(DateTime, nullable=False)
    purchase_cost = Column(Numeric(15, 2), nullable=False)
    salvage_value = Column(Numeric(15, 2), default=0)
    useful_life_years = Column(Integer, nullable=False)
    depreciation_method = Column(String(50), default='straight_line')
    accumulated_depreciation = Column(Numeric(15, 2), default=0)
    book_value = Column(Numeric(15, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Depreciation(Base):
    __tablename__ = 'depreciations'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    asset_id = Column(String(36), ForeignKey('fixed_assets.id'), nullable=False)
    depreciation_date = Column(DateTime, nullable=False)
    depreciation_amount = Column(Numeric(15, 2), nullable=False)
    accumulated_depreciation = Column(Numeric(15, 2), nullable=False)
    book_value = Column(Numeric(15, 2), nullable=False)
    journal_entry_id = Column(String(36), ForeignKey('journal_entries.id'))
    created_at = Column(DateTime, default=datetime.utcnow)

# ===== PAYROLL =====
class Employee(Base):
    __tablename__ = 'employees'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    employee_code = Column(String(20), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(50))
    hire_date = Column(DateTime, nullable=False)
    job_title = Column(String(100), nullable=False)
    department = Column(String(100))
    salary = Column(Numeric(15, 2), nullable=False)
    pay_frequency = Column(String(20), default='monthly')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class PayrollRun(Base):
    __tablename__ = 'payroll_runs'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    run_name = Column(String(100), nullable=False)
    pay_period_start = Column(DateTime, nullable=False)
    pay_period_end = Column(DateTime, nullable=False)
    pay_date = Column(DateTime, nullable=False)
    status = Column(String(20), default='draft')
    total_gross = Column(Numeric(15, 2), default=0)
    total_deductions = Column(Numeric(15, 2), default=0)
    total_net = Column(Numeric(15, 2), default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class PayrollItem(Base):
    __tablename__ = 'payroll_items'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    payroll_run_id = Column(String(36), ForeignKey('payroll_runs.id'), nullable=False)
    employee_id = Column(String(36), ForeignKey('employees.id'), nullable=False)
    gross_pay = Column(Numeric(15, 2), nullable=False)
    federal_tax = Column(Numeric(15, 2), default=0)
    state_tax = Column(Numeric(15, 2), default=0)
    social_security = Column(Numeric(15, 2), default=0)
    medicare = Column(Numeric(15, 2), default=0)
    other_deductions = Column(Numeric(15, 2), default=0)
    net_pay = Column(Numeric(15, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# ===== TAX MANAGEMENT =====
class TaxRate(Base):
    __tablename__ = 'tax_rates'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    tax_code = Column(String(20), unique=True, nullable=False)
    tax_name = Column(String(100), nullable=False)
    rate_percentage = Column(Numeric(5, 4), nullable=False)
    tax_type = Column(String(50), nullable=False)
    jurisdiction = Column(String(100))
    effective_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class TaxReturn(Base):
    __tablename__ = 'tax_returns'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    return_type = Column(String(50), nullable=False)
    tax_year = Column(Integer, nullable=False)
    filing_status = Column(String(20), default='draft')
    due_date = Column(DateTime, nullable=False)
    filed_date = Column(DateTime)
    total_tax_due = Column(Numeric(15, 2), default=0)
    total_payments = Column(Numeric(15, 2), default=0)
    refund_amount = Column(Numeric(15, 2), default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

# ===== MULTI-CURRENCY =====
class Currency(Base):
    __tablename__ = 'currencies'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    currency_code = Column(String(3), unique=True, nullable=False)
    currency_name = Column(String(100), nullable=False)
    symbol = Column(String(10))
    is_base_currency = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ExchangeRate(Base):
    __tablename__ = 'exchange_rates'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    from_currency = Column(String(3), nullable=False)
    to_currency = Column(String(3), nullable=False)
    rate = Column(Numeric(15, 6), nullable=False)
    rate_date = Column(DateTime, nullable=False)
    source = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

# ===== FINANCIAL REPORTS =====
class ReportTemplate(Base):
    __tablename__ = 'report_templates'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    report_name = Column(String(255), nullable=False)
    report_type = Column(String(100), nullable=False)
    template_data = Column(Text)  # JSON configuration
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ReportRun(Base):
    __tablename__ = 'report_runs'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    template_id = Column(String(36), ForeignKey('report_templates.id'), nullable=False)
    run_date = Column(DateTime, nullable=False)
    parameters = Column(Text)  # JSON parameters
    status = Column(String(20), default='pending')
    file_path = Column(String(500))
    created_by = Column(String(36))
    created_at = Column(DateTime, default=datetime.utcnow)

# ===== PERIOD CLOSING =====
class PeriodClose(Base):
    __tablename__ = 'period_closes'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    period_name = Column(String(50), nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    status = Column(String(20), default='open')
    closed_by = Column(String(36))
    closed_at = Column(DateTime)
    net_income = Column(Numeric(15, 2))
    total_revenue = Column(Numeric(15, 2))
    total_expenses = Column(Numeric(15, 2))
    closing_entries = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# ===== WORKFLOW SYSTEM =====
class WorkflowInstance(Base):
    __tablename__ = 'workflow_instances'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    workflow_type = Column(String(50), nullable=False)
    entity_id = Column(String(36), nullable=False)
    entity_type = Column(String(50), nullable=False)
    status = Column(String(20), default='pending')
    current_step = Column(Integer, default=1)
    total_steps = Column(Integer, nullable=False)
    amount = Column(Numeric(15, 2))
    priority = Column(String(10), default='normal')
    workflow_data = Column(Text)
    created_by = Column(String(36))
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class WorkflowStep(Base):
    __tablename__ = 'workflow_steps'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    workflow_id = Column(String(36), ForeignKey('workflow_instances.id'), nullable=False)
    step_number = Column(Integer, nullable=False)
    step_name = Column(String(100), nullable=False)
    approver_role = Column(String(50))
    approver_user = Column(String(36))
    delegated_to = Column(String(36))
    required_approvals = Column(Integer, default=1)
    status = Column(String(20), default='waiting')
    due_date = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class WorkflowApproval(Base):
    __tablename__ = 'workflow_approvals'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    workflow_id = Column(String(36), ForeignKey('workflow_instances.id'), nullable=False)
    step_id = Column(String(36), ForeignKey('workflow_steps.id'), nullable=False)
    approver_id = Column(String(36), nullable=False)
    action = Column(String(20), nullable=False)
    comments = Column(Text)
    approved_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45))
    user_agent = Column(String(500))

class WorkflowDelegation(Base):
    __tablename__ = 'workflow_delegations'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    workflow_id = Column(String(36), ForeignKey('workflow_instances.id'), nullable=False)
    step_id = Column(String(36), ForeignKey('workflow_steps.id'), nullable=False)
    from_user = Column(String(36), nullable=False)
    to_user = Column(String(36), nullable=False)
    reason = Column(Text)
    delegated_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)

class WorkflowTemplate(Base):
    __tablename__ = 'workflow_templates'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    template_name = Column(String(100), nullable=False)
    workflow_type = Column(String(50), nullable=False)
    description = Column(Text)
    template_data = Column(Text)
    is_default = Column(Boolean, default=False)
    min_amount = Column(Numeric(15, 2))
    max_amount = Column(Numeric(15, 2))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# ===== AUDIT TRAIL =====
class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(36))
    old_values = Column(Text)
    new_values = Column(Text)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

def create_complete_database():
    """Create complete database with all modules"""
    try:
        # Create all tables
        Base.metadata.create_all(engine)
        print(f"Database created: {os.path.abspath(DB_PATH)}")
        
        session = Session()
        
        # Create sample data
        with session.begin():
            # Create base currency
            usd = Currency(currency_code='USD', currency_name='US Dollar', symbol='$', is_base_currency=True)
            session.add(usd)
            
            # Create sample chart of accounts
            accounts = [
                ChartOfAccounts(account_code='1000', account_name='Cash', account_type='Asset', normal_balance='Debit'),
                ChartOfAccounts(account_code='1200', account_name='Accounts Receivable', account_type='Asset', normal_balance='Debit'),
                ChartOfAccounts(account_code='1500', account_name='Inventory', account_type='Asset', normal_balance='Debit'),
                ChartOfAccounts(account_code='2000', account_name='Accounts Payable', account_type='Liability', normal_balance='Credit'),
                ChartOfAccounts(account_code='3000', account_name='Retained Earnings', account_type='Equity', normal_balance='Credit'),
                ChartOfAccounts(account_code='4000', account_name='Sales Revenue', account_type='Revenue', normal_balance='Credit'),
                ChartOfAccounts(account_code='5000', account_name='Cost of Goods Sold', account_type='Expense', normal_balance='Debit'),
            ]
            session.add_all(accounts)
            
            # Create admin user
            admin = User(
                email='admin@paksa.com',
                hashed_password='$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',  # admin123
                first_name='System',
                last_name='Administrator',
                is_superuser=True
            )
            session.add(admin)
            
            session.commit()
        
        print("Sample data created")
        
        # Print table count
        tables = Base.metadata.tables.keys()
        print(f"Created {len(tables)} tables:")
        for table in sorted(tables):
            print(f"   - {table}")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("=== Creating Complete Paksa Financial Database ===")
    if create_complete_database():
        print("\nComplete database setup successful!")
    else:
        print("\nDatabase setup failed!")