from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey, Text, Enum, Numeric, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db.base import BaseModel
import enum

class TaxType(enum.Enum):
    INCOME = "income"
    SALES = "sales"
    VAT = "vat"
    GST = "gst"
    PAYROLL = "payroll"
    PROPERTY = "property"
    EXCISE = "excise"

class TaxJurisdiction(BaseModel):
    __tablename__ = 'tax_jurisdictions'
    
    code = Column(String(10), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    level = Column(Enum('country', 'state', 'county', 'city', name='jurisdiction_level'), nullable=False)
    parent_id = Column(Integer, ForeignKey('tax_jurisdictions.id'))
    
    parent = relationship("TaxJurisdiction", remote_side=[id])
    children = relationship("TaxJurisdiction")
    tax_rates = relationship("TaxRate", back_populates="jurisdiction")

class TaxRate(BaseModel):
    __tablename__ = 'tax_rates'
    
    name = Column(String(100), nullable=False)
    rate = Column(Numeric(5, 4), nullable=False)
    tax_type = Column(Enum(TaxType), nullable=False)
    jurisdiction_id = Column(Integer, ForeignKey('tax_jurisdictions.id'), nullable=False)
    effective_date = Column(Date, nullable=False)
    expiry_date = Column(Date)
    
    jurisdiction = relationship("TaxJurisdiction", back_populates="tax_rates")
    transactions = relationship("TaxTransaction", back_populates="tax_rate")

class TaxTransaction(BaseModel):
    __tablename__ = 'tax_transactions'
    
    transaction_date = Column(Date, nullable=False)
    document_number = Column(String(50), nullable=False)
    reference_number = Column(String(50))
    tax_rate_id = Column(Integer, ForeignKey('tax_rates.id'), nullable=False)
    taxable_amount = Column(Numeric(15, 2), nullable=False)
    tax_amount = Column(Numeric(15, 2), nullable=False)
    total_amount = Column(Numeric(15, 2), nullable=False)
    status = Column(String(20), default='draft')
    
    tax_rate = relationship("TaxRate", back_populates="transactions")
    components = relationship("TaxTransactionComponent", back_populates="transaction")

class TaxTransactionComponent(BaseModel):
    __tablename__ = 'tax_transaction_components'
    
    transaction_id = Column(Integer, ForeignKey('tax_transactions.id'), nullable=False)
    tax_component = Column(String(50), nullable=False)
    component_rate = Column(Numeric(5, 4), nullable=False)
    component_amount = Column(Numeric(15, 2), nullable=False)
    
    transaction = relationship("TaxTransaction", back_populates="components")

class TaxExemption(BaseModel):
    __tablename__ = 'tax_exemptions'
    
    exemption_type = Column(String(50), nullable=False)
    reason = Column(Text, nullable=False)
    certificate_number = Column(String(50))
    effective_date = Column(Date, nullable=False)
    expiry_date = Column(Date)
    jurisdiction_id = Column(Integer, ForeignKey('tax_jurisdictions.id'))
    
    jurisdiction = relationship("TaxJurisdiction")

class TaxReturn(BaseModel):
    __tablename__ = 'tax_returns'
    
    return_number = Column(String(50), unique=True, nullable=False)
    tax_type = Column(Enum(TaxType), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    filing_date = Column(Date)
    due_date = Column(Date, nullable=False)
    status = Column(String(20), default='draft')
    total_tax_due = Column(Numeric(15, 2), default=0)
    
    line_items = relationship("TaxReturnLineItem", back_populates="tax_return")