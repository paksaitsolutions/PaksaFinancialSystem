"""
Paksa Financial System 
Financial Statement Template Model

This module defines the FinancialStatementTemplate model for defining financial statement layouts.
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

from sqlalchemy import (
    Column, String, Boolean, ForeignKey, 
    DateTime, Enum as SQLEnum, Text, JSON, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship, validates

from app.db.base_class import Base


class TemplateType(str, Enum):
    """Types of financial statement templates."""
    BALANCE_SHEET = "balance_sheet"
    INCOME_STATEMENT = "income_statement"
    CASH_FLOW = "cash_flow"
    CUSTOM = "custom"


class LineItemType(str, Enum):
    """Types of line items in a financial statement template."""
    HEADER = "header"
    ACCOUNT = "account"
    FORMULA = "formula"
    SUBTOTAL = "subtotal"
    TOTAL = "total"
    SPACER = "spacer"


class FinancialStatementTemplate(Base):
    """
    Defines the structure and layout of financial statements.
    """
    __tablename__ = "financial_statement_templates"
    __table_args__ = (
        UniqueConstraint('name', 'company_id', name='uq_fs_template_name_company'),
        {"schema": "accounting"}
    )

    id = Column(PG_UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    template_type = Column(SQLEnum(TemplateType), nullable=False, index=True)
    is_default = Column(Boolean, default=False, nullable=False)
    is_system = Column(Boolean, default=False, nullable=False)
    
    # Company this template belongs to (null for system templates)
    company_id = Column(PG_UUID(as_uuid=True), ForeignKey("core.companies.id"), nullable=True, index=True)
    
    # Structure definition
    structure = Column(JSONB, nullable=False, default=dict)
    
    # Versioning
    version = Column(String(50), nullable=False, default="1.0")
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(PG_UUID(as_uuid=True), nullable=True)
    updated_by = Column(PG_UUID(as_uuid=True), nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="financial_statement_templates")
    
    # Indexes
    __table_args__ = (
        Index("idx_fs_template_type_company", "template_type", "company_id"),
        Index("idx_fs_template_default", "is_default", "company_id"),
        {"schema": "accounting"}
    )
    
    @validates('structure')
    def validate_structure(self, key, structure: Dict) -> Dict:
        """Validate the structure JSON to ensure it's properly formatted."""
        if not isinstance(structure, dict):
            raise ValueError("Structure must be a JSON object")
            
        required_sections = ["sections"]
        for section in required_sections:
            if section not in structure:
                raise ValueError(f"Missing required section: {section}")
                
        return structure
    
    def __repr__(self) -> str:
        return f"<FinancialStatementTemplate {self.name} ({self.template_type})>"


class FinancialStatementLineTemplate(Base):
    """
    Defines a line item in a financial statement template.
    """
    __tablename__ = "financial_statement_line_templates"
    __table_args__ = (
        {"schema": "accounting"}
    )
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    template_id = Column(PG_UUID(as_uuid=True), ForeignKey("accounting.financial_statement_templates.id"), nullable=False)
    
    # Line item properties
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=True, index=True)
    line_type = Column(SQLEnum(LineItemType), nullable=False, default=LineItemType.ACCOUNT)
    
    # For formula lines
    formula = Column(Text, nullable=True)
    
    # For account-based lines
    account_code = Column(String(50), nullable=True, index=True)
    
    # For section headers and organization
    parent_id = Column(PG_UUID(as_uuid=True), ForeignKey("accounting.financial_statement_line_templates.id"), nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=0, nullable=False)
    
    # Formatting
    is_bold = Column(Boolean, default=False)
    is_italic = Column(Boolean, default=False)
    is_underline = Column(Boolean, default=False)
    
    # Relationships
    template = relationship("FinancialStatementTemplate", back_populates="line_items")
    parent = relationship("FinancialStatementLineTemplate", remote_side=[id], back_populates="children")
    children = relationship("FinancialStatementLineTemplate", back_populates="parent")
    
    # Indexes
    __table_args__ = (
        Index("idx_fs_line_template", "template_id", "code", unique=True),
        Index("idx_fs_line_parent", "parent_id"),
        Index("idx_fs_line_sort", "template_id", "sort_order"),
        {"schema": "accounting"}
    )
    
    def __repr__(self) -> str:
        return f"<FinancialStatementLineTemplate {self.name} ({self.line_type})>"
