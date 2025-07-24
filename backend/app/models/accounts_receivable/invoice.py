"""
Invoice model for accounts receivable.
"""
import uuid
from datetime import date
from sqlalchemy import Column, String, ForeignKey, Date, Numeric, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base

class Invoice(Base):
    """Invoice model."""
    
    __tablename__ = "invoice"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customer.id"), nullable=False)
    
    invoice_date = Column(Date, nullable=False, default=date.today)
    due_date = Column(Date, nullable=False)
    amount = Column(Numeric(precision=18, scale=2), nullable=False)
    status = Column(String(20), default="draft", index=True)  # draft, sent, paid, overdue
    
    # Relationships
    customer = relationship("Customer", back_populates="invoices")
    
    def __repr__(self):
        return f"<Invoice {self.invoice_number}: {self.amount}>"