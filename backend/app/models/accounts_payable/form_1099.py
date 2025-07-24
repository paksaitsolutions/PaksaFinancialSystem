"""
1099 reporting model for Accounts Payable module.
"""
import uuid
from datetime import date
from sqlalchemy import Column, String, Boolean, ForeignKey, Text, Date, Enum, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.enums import Form1099Status, Form1099Type

class Form1099(Base):
    """1099 form model for tax reporting."""
    
    __tablename__ = "form_1099"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendor.id"), nullable=False, index=True)
    
    # Tax year and form details
    tax_year = Column(Integer, nullable=False, index=True)
    form_type = Column(Enum(Form1099Type), default=Form1099Type.MISC, nullable=False)
    status = Column(Enum(Form1099Status), default=Form1099Status.DRAFT, nullable=False, index=True)
    
    # Payment amounts by box
    box_1_rents = Column(Numeric(precision=18, scale=2), default=0)
    box_2_royalties = Column(Numeric(precision=18, scale=2), default=0)
    box_3_other_income = Column(Numeric(precision=18, scale=2), default=0)
    box_4_federal_tax_withheld = Column(Numeric(precision=18, scale=2), default=0)
    box_5_fishing_boat_proceeds = Column(Numeric(precision=18, scale=2), default=0)
    box_6_medical_health_payments = Column(Numeric(precision=18, scale=2), default=0)
    box_7_nonemployee_compensation = Column(Numeric(precision=18, scale=2), default=0)
    box_8_substitute_payments = Column(Numeric(precision=18, scale=2), default=0)
    box_9_payer_direct_sales = Column(Numeric(precision=18, scale=2), default=0)
    box_10_crop_insurance = Column(Numeric(precision=18, scale=2), default=0)
    box_11_state_tax_withheld = Column(Numeric(precision=18, scale=2), default=0)
    box_12_state_payer_number = Column(String(50))
    box_13_state_income = Column(Numeric(precision=18, scale=2), default=0)
    box_14_gross_proceeds = Column(Numeric(precision=18, scale=2), default=0)
    
    # Total reportable amount
    total_amount = Column(Numeric(precision=18, scale=2), nullable=False, default=0)
    
    # Filing information
    filed_date = Column(Date)
    correction = Column(Boolean, default=False)
    void = Column(Boolean, default=False)
    
    # Notes
    notes = Column(Text)
    
    # Relationships
    vendor = relationship("Vendor")
    transactions = relationship("Form1099Transaction", back_populates="form_1099", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Form1099 {self.vendor.name} {self.tax_year}: {self.total_amount}>"


class Form1099Transaction(Base):
    """Transaction details for 1099 reporting."""
    
    __tablename__ = "form_1099_transaction"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form_1099_id = Column(UUID(as_uuid=True), ForeignKey("form_1099.id"), nullable=False)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("ap_payment.id"), nullable=False)
    
    # Transaction details
    amount = Column(Numeric(precision=18, scale=2), nullable=False)
    box_number = Column(Integer, nullable=False)
    description = Column(String(255))
    
    # Relationships
    form_1099 = relationship("Form1099", back_populates="transactions")
    payment = relationship("APPayment")
    
    def __repr__(self):
        return f"<Form1099Transaction Box {self.box_number}: {self.amount}>"