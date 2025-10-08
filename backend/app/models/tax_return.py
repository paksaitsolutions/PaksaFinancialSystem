from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.core.database import Base

class TaxReturn(Base):
    __tablename__ = "tax_returns"

    id = Column(Integer, primary_key=True, index=True)
    return_id = Column(String(50), unique=True, index=True, nullable=False)
    tax_year = Column(String(4), nullable=False)
    return_type = Column(String(50), nullable=False)  # income_tax, sales_tax, withholding_tax, corporate_tax, wealth_statement
    ntn = Column(String(20))
    cnic = Column(String(20))
    gross_income = Column(Numeric(15, 2), default=0)
    taxable_income = Column(Numeric(15, 2), default=0)
    tax_liability = Column(Numeric(15, 2), default=0)
    advance_tax_paid = Column(Numeric(15, 2), default=0)
    due_date = Column(Date, nullable=False)
    filed_date = Column(Date)
    status = Column(String(20), default="draft")  # draft, filed, accepted, rejected, amended, overdue
    remarks = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())