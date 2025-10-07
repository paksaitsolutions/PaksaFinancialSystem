from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Integer
from sqlalchemy.types import DECIMAL as Decimal
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class TaxRate(Base):
    __tablename__ = "tax_rates"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    tax_name = Column(String(255), nullable=False)
    tax_code = Column(String(20), unique=True, nullable=False)
    rate_percentage = Column(Decimal(5, 4), nullable=False)
    tax_type = Column(String(50))  # sales, income, property, etc.
    jurisdiction = Column(String(100))
    effective_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    policies = relationship("TaxPolicy", back_populates="tax_rate")

class TaxJurisdiction(Base):
    __tablename__ = "tax_jurisdictions"
    
    id = Column(String, primary_key=True)
    jurisdiction_name = Column(String(255), nullable=False)
    jurisdiction_code = Column(String(20), unique=True, nullable=False)
    jurisdiction_type = Column(String(50))  # federal, state, local
    country = Column(String(100))
    state_province = Column(String(100))
    city = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class TaxExemption(Base):
    __tablename__ = "tax_exemptions"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    exemption_name = Column(String(255), nullable=False)
    exemption_code = Column(String(50))
    tax_type = Column(String(50))
    exemption_percentage = Column(Decimal(5, 2), default=100.0)
    effective_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime)
    certificate_number = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class TaxReturn(Base):
    __tablename__ = "tax_returns"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    return_type = Column(String(50), nullable=False)
    tax_period = Column(String(50))
    filing_date = Column(DateTime)
    due_date = Column(DateTime, nullable=False)
    total_tax_due = Column(Decimal(15, 2), default=0)
    tax_paid = Column(Decimal(15, 2), default=0)
    status = Column(String(20), default="draft")
    filed_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class TaxPolicy(Base):
    __tablename__ = "tax_policies"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    policy_name = Column(String(255), nullable=False)
    policy_type = Column(String(50), nullable=False)
    tax_rate_id = Column(String, ForeignKey("tax_rates.id"))
    priority = Column(Integer, default=1)
    conditions = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    tax_rate = relationship("TaxRate", back_populates="policies")

class TaxCompliance(Base):
    __tablename__ = "tax_compliance"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    compliance_type = Column(String(100), nullable=False)
    requirement_description = Column(Text)
    due_date = Column(DateTime, nullable=False)
    completion_date = Column(DateTime)
    status = Column(String(20), default="pending")
    assigned_to = Column(String, ForeignKey("users.id"))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)