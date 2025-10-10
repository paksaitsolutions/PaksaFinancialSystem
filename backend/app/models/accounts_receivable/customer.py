"""
Customer model for Accounts Receivable module.
"""
import uuid
from typing import Optional, List
from sqlalchemy import Column, String, Boolean, ForeignKey, Text, Date, Enum, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.enums import CustomerStatus, PaymentTerms

class Customer(Base):
    """Customer model for managing customer information."""
    
    __tablename__ = "customer"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    legal_name = Column(String(150))
    tax_id = Column(String(50), index=True)
    status = Column(Enum(CustomerStatus), default=CustomerStatus.ACTIVE, nullable=False, index=True)
    
    # Contact information
    email = Column(String(100))
    phone = Column(String(30))
    website = Column(String(255))
    
    # Address
    address_line1 = Column(String(100))
    address_line2 = Column(String(100))
    city = Column(String(50))
    state = Column(String(50))
    postal_code = Column(String(20))
    country = Column(String(50))
    
    # Payment information
    payment_terms = Column(Enum(PaymentTerms), default=PaymentTerms.NET_30)
    credit_limit = Column(Numeric(precision=18, scale=2), default=0)
    currency_id = Column(UUID(as_uuid=True), ForeignKey("currencies.id"))
    
    # Notes
    notes = Column(Text)
    
    # Relationships
    currency = relationship("Currency")
    contacts = relationship("CustomerContact", back_populates="customer", cascade="all, delete-orphan")
    invoices = relationship("ARInvoice", back_populates="customer")
    
    def __repr__(self):
        return f"<Customer {self.code}: {self.name}>"


class CustomerContact(Base):
    """Contact person for a customer."""
    
    __tablename__ = "customer_contact"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customer.id"), nullable=False)
    name = Column(String(100), nullable=False)
    position = Column(String(100))
    email = Column(String(100))
    phone = Column(String(30))
    is_primary = Column(Boolean, default=False)
    
    # Relationships
    customer = relationship("Customer", back_populates="contacts")
    
    def __repr__(self):
        return f"<CustomerContact {self.name} for {self.customer.name}>"