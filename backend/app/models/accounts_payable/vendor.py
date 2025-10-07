"""
Vendor model for Accounts Payable module.
"""
import uuid
from typing import Optional, List
from sqlalchemy import Column, String, Boolean, ForeignKey, Text, Date, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.enums import VendorStatus, PaymentTerms

class Vendor(Base):
    """Vendor model for managing supplier information."""
    
    __tablename__ = "vendor"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    legal_name = Column(String(150))
    tax_id = Column(String(50), index=True)
    status = Column(Enum(VendorStatus), default=VendorStatus.ACTIVE, nullable=False, index=True)
    
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
    currency_id = Column(UUID(as_uuid=True), ForeignKey("currency.id"))
    default_account_id = Column(UUID(as_uuid=True), ForeignKey("gl_account.id"))
    
    # 1099 reporting
    is_1099 = Column(Boolean, default=False)
    tax_classification = Column(String(50))
    
    # Notes
    notes = Column(Text)
    
    # Relationships
    currency = relationship("Currency")
    default_account = relationship("GLAccount")
    contacts = relationship("VendorContact", back_populates="vendor", cascade="all, delete-orphan")
    invoices = relationship("APInvoice", back_populates="vendor")
    
    def __repr__(self):
        return f"<Vendor {self.code}: {self.name}>"


class VendorContact(Base):
    """Contact person for a vendor."""
    
    __tablename__ = "vendor_contact"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendor.id"), nullable=False)
    name = Column(String(100), nullable=False)
    position = Column(String(100))
    email = Column(String(100))
    phone = Column(String(30))
    is_primary = Column(Boolean, default=False)
    
    # Relationships
    vendor = relationship("Vendor", back_populates="contacts")
    
    def __repr__(self):
        return f"<VendorContact {self.name} for {self.vendor.name}>"