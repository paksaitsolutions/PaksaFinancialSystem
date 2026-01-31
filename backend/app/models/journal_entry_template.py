"""
Journal Entry Templates for automated entry creation.
"""
from sqlalchemy import Column, String, Text, Boolean, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, GUID


class JournalEntryTemplate(BaseModel):
    """Template for creating recurring or standard journal entries."""
    __tablename__ = "journal_entry_templates"
    
    template_name = Column(String(100), nullable=False)
    template_code = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    category = Column(String(50), nullable=True)
    
    template_lines = relationship("JournalEntryTemplateLine", back_populates="template", cascade="all, delete-orphan")


class JournalEntryTemplateLine(BaseModel):
    """Template line for journal entry."""
    __tablename__ = "journal_entry_template_lines"
    
    template_id = Column(GUID(), ForeignKey("journal_entry_templates.id"), nullable=False)
    account_id = Column(GUID(), ForeignKey("chart_of_accounts.id"), nullable=False)
    description = Column(Text, nullable=True)
    is_debit = Column(Boolean, nullable=False)
    amount_formula = Column(String(255), nullable=True)
    line_order = Column(Integer, default=1, nullable=False)
    
    template = relationship("JournalEntryTemplate", back_populates="template_lines")
    account = relationship("GLChartOfAccounts")
