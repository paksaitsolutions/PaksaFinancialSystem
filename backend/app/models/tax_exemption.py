from sqlalchemy import Column, String, Boolean, Date, JSON, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.db.base import Base
import uuid
from datetime import date
from typing import List, Optional, Dict, Any

class TaxExemption(Base):
    """
    Tax Exemption model for storing tax exemption information.
    """
    __tablename__ = "tax_exemptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exemption_code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    certificate_required = Column(Boolean, default=False)
    valid_from = Column(Date, nullable=False, default=date.today)
    valid_to = Column(Date, nullable=True)
    tax_types = Column(JSON, nullable=False)  # List of tax types this exemption applies to
    jurisdictions = Column(JSON, nullable=False)  # List of jurisdictions where this exemption is valid
    metadata = Column(JSON, default=dict)
    
    # Relationships
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<TaxExemption {self.exemption_code}>"
    
    @property
    def is_active(self) -> bool:
        """Check if the exemption is currently active."""
        today = date.today()
        return (self.valid_from <= today and 
                (self.valid_to is None or self.valid_to >= today))
