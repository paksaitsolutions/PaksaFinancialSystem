# Import unified accounting models to avoid duplicates
from app.models import (
    ChartOfAccounts,
    JournalEntry,
    JournalEntryLine,
    Vendor,
    Customer,
    APInvoice,
    ARInvoice,
    APPayment,
    ARPayment,
    TaxRate
)
from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

# Aliases for backward compatibility
AccountingChartOfAccountsMain = ChartOfAccounts
AccountingVendor = Vendor
AccountingBill = APInvoice
AccountingInvoice = ARInvoice
AccountingPayment = APPayment
TaxCode = TaxRate
Invoice = ARInvoice  # Common alias for AR Invoice
Bill = APInvoice  # Common alias for AP Invoice
Payment = APPayment  # Common alias for Payment

# AccountingRule model (not in unified models yet)
class AccountingRule(Base):
    __tablename__ = 'accounting_rules'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String(255), nullable=False)
    trigger_event = Column(String(100), nullable=False)
    conditions = Column(Text)
    debit_account_id = Column(Integer, ForeignKey('chart_of_accounts.id'))
    credit_account_id = Column(Integer, ForeignKey('chart_of_accounts.id'))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())