from sqlalchemy import Column, String, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel
import uuid

class GLAccount(BaseModel):
    __tablename__ = "gl_accounts"
    
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True, default=uuid.uuid4)
    account_code = Column(String(20), nullable=False, index=True)
    account_name = Column(String(200), nullable=False)
    account_type = Column(String(50), nullable=False)  # Asset, Liability, Equity, Revenue, Expense
    parent_account_id = Column(UUID(as_uuid=True), ForeignKey('gl_accounts.id'), nullable=True)
    balance = Column(Numeric(15, 2), default=0)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    parent = relationship("GLAccount", remote_side="GLAccount.id")
    children = relationship("GLAccount", back_populates="parent")
    journal_entries = relationship("JournalEntryLine", back_populates="account")