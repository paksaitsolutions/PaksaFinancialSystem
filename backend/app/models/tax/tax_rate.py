"""
Tax rate and policy models.
"""
import uuid
from datetime import date
from sqlalchemy import Column, String, Boolean, ForeignKey, Date, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base

# TaxRate moved to core_models.py for unified definition

class TaxExemption(Base):
    """Tax exemption certificate model."""
    
    __tablename__ = "tax_exemption"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    certificate_number = Column(String(50), unique=True, nullable=False, index=True)
    entity_type = Column(String(20), nullable=False)  # customer, vendor
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    exemption_type = Column(String(50), nullable=False)  # resale, nonprofit, government
    tax_type = Column(String(50), nullable=False)  # sales, vat, gst
    jurisdiction = Column(String(100))
    issue_date = Column(Date, nullable=False, default=date.today)
    expiry_date = Column(Date)
    is_active = Column(Boolean, default=True)
    notes = Column(Text)
    
    def __repr__(self):
        return f"<TaxExemption {self.certificate_number}>"

class TaxPolicy(Base):
    """Tax policy configuration model."""
    
    __tablename__ = "tax_policy"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, index=True)
    policy_type = Column(String(50), nullable=False)  # product, service, location
    tax_rate_id = Column(UUID(as_uuid=True), ForeignKey("tax_rate.id"), nullable=False)
    conditions = Column(Text)  # JSON conditions for applying this policy
    priority = Column(Numeric(precision=3, scale=0), default=1)
    is_active = Column(Boolean, default=True)
    
    # Relationship with unified TaxRate from core_models
    tax_rate = relationship("TaxRate", viewonly=True)
    
    def __repr__(self):
        return f"<TaxPolicy {self.name}>"