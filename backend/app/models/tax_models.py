# Import unified tax models from core_models to eliminate duplicates
from app.models.core_models import TaxRate

# TaxRate is now unified in core_models.py
# Additional tax models remain here for extended functionality

from app.models.base import Base
from sqlalchemy import Column, String, Boolean, ForeignKey, Date, DateTime, Numeric, Text, Integer, JSON
from app.models.base import GUID
from sqlalchemy.orm import relationship
from enum import Enum
import uuid
from datetime import date, datetime

class TaxStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    EXPIRED = "expired"

# TaxTransaction model exists in core_models.py - removed duplicate

class TaxExemption(Base):
    """Tax exemption certificates."""
    
    __tablename__ = "tax_exemptions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    certificate_number = Column(String(50), unique=True, nullable=False, index=True)
    entity_type = Column(String(20), nullable=False)  # customer, vendor
    entity_id = Column(GUID(), nullable=False, index=True)
    
    # Exemption details
    exemption_type = Column(String(50), nullable=False)
    tax_types = Column(JSON)  # List of tax types this exemption applies to
    jurisdiction = Column(String(100))
    
    # Validity
    issue_date = Column(Date, nullable=False, default=date.today)
    expiry_date = Column(Date)
    status = Column(String(20), default=TaxStatus.ACTIVE)
    
    # Documentation
    issuing_authority = Column(String(100))
    notes = Column(Text)
    attachment_path = Column(String(500))
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<TaxExemption {self.certificate_number}>"

# TaxReturn model exists in core_models.py - removed duplicate

# TaxReturnLineItem removed - TaxReturn in core_models doesn't support line_items

class TaxJurisdiction(Base):
    """Tax jurisdiction configuration."""
    
    __tablename__ = "tax_jurisdictions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    jurisdiction_type = Column(String(20), nullable=False)  # country, state, city
    parent_id = Column(GUID(), ForeignKey("tax_jurisdictions.id"))
    
    # Configuration
    tax_id_required = Column(Boolean, default=False)
    tax_id_format = Column(String(100))
    filing_frequency = Column(String(20))  # monthly, quarterly, annually
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent = relationship("TaxJurisdiction", remote_side="TaxJurisdiction.id", back_populates="children")
    children = relationship("TaxJurisdiction", back_populates="parent", overlaps="parent")
    
    def __repr__(self):
        return f"<TaxJurisdiction {self.code}: {self.name}>"

class ComplianceCheck(Base):
    """Tax compliance check records."""
    
    __tablename__ = "tax_compliance_checks"
    __table_args__ = {'extend_existing': True}
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    check_type = Column(String(50), nullable=False)
    entity_id = Column(GUID(), nullable=False)
    status = Column(String(20), default="pending")
    result = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ComplianceCheck {self.check_type}: {self.status}>"

class ComplianceRule(Base):
    """Tax compliance rules."""
    
    __tablename__ = "tax_compliance_rules"
    __table_args__ = {'extend_existing': True}
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    rule_type = Column(String(50), nullable=False)
    conditions = Column(JSON)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<ComplianceRule {self.name}>"

class ComplianceAlert(Base):
    """Tax compliance alerts."""
    
    __tablename__ = "tax_compliance_alerts"
    __table_args__ = {'extend_existing': True}
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), default="medium")
    message = Column(Text)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ComplianceAlert {self.alert_type}>"

class TaxRateCompliance(Base):
    """Tax rate compliance tracking."""
    
    __tablename__ = "tax_rate_compliance"
    __table_args__ = {'extend_existing': True}
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    tax_rate_id = Column(GUID(), ForeignKey("tax_rates.id"))
    compliance_status = Column(String(20), default="compliant")
    last_checked = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<TaxRateCompliance {self.compliance_status}>"