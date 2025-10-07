"""
Customer model for accounts receivable.
"""
import uuid
from sqlalchemy import Column, String, Boolean, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base

class Customer(Base):
    """Customer model."""
    
    __tablename__ = "customer"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False, index=True)
    email = Column(String(100), index=True)
    phone = Column(String(20))
    address = Column(Text)
    credit_limit = Column(Numeric(precision=18, scale=2), default=0)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    invoices = relationship("Invoice", back_populates="customer")
    
    def __repr__(self):
        return f"<Customer {self.name}>"