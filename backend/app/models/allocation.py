"""
Allocation rules and allocation models.
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, String, Numeric, Date, DateTime, ForeignKey, Enum as SQLEnum, Boolean, Text, Integer
from sqlalchemy.orm import relationship

from .base import BaseModel, GUID


class AllocationMethod(str, Enum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    EQUAL = "equal"
    WEIGHTED = "weighted"
    FORMULA = "formula"


class AllocationStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"


class AllocationRule(BaseModel):
    """
    Defines rules for automatic allocation of transactions.
    """
    __tablename__ = "allocation_rules"
    
    # Rule identification
    rule_name = Column(String(100), nullable=False)
    rule_code = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Rule configuration
    allocation_method = Column(SQLEnum(AllocationMethod), nullable=False)
    status = Column(SQLEnum(AllocationStatus), nullable=False, default=AllocationStatus.ACTIVE)
    
    # Source criteria
    source_account_id = Column(GUID(), ForeignKey("chart_of_accounts.id"), nullable=True)
    source_department_id = Column(GUID(), nullable=True)
    source_cost_center_id = Column(GUID(), nullable=True)
    
    # Effective dates
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    
    # Priority for rule application
    priority = Column(Integer, nullable=False, default=100)
    
    # Relationships
    source_account = relationship("ChartOfAccounts", back_populates="allocation_rules")
    allocation_lines = relationship("AllocationRuleLine", back_populates="allocation_rule", cascade="all, delete-orphan")
    allocations = relationship("Allocation", back_populates="allocation_rule")
    
    def __repr__(self) -> str:
        return f"<AllocationRule(id={self.id}, code='{self.rule_code}', name='{self.rule_name}')>"


class AllocationRuleLine(BaseModel):
    """
    Defines the allocation targets and percentages for an allocation rule.
    """
    __tablename__ = "allocation_rule_lines"
    
    # Parent rule
    allocation_rule_id = Column(GUID(), ForeignKey("allocation_rules.id"), nullable=False)
    
    # Target allocation
    target_account_id = Column(GUID(), ForeignKey("chart_of_accounts.id"), nullable=False)
    target_department_id = Column(GUID(), nullable=True)
    target_cost_center_id = Column(GUID(), nullable=True)
    
    # Allocation parameters
    allocation_percentage = Column(Numeric(5, 2), nullable=True)  # For percentage method
    fixed_amount = Column(Numeric(15, 2), nullable=True)  # For fixed amount method
    weight = Column(Numeric(10, 4), nullable=True)  # For weighted method
    formula = Column(Text, nullable=True)  # For formula method
    
    # Line order
    line_order = Column(Integer, nullable=False, default=1)
    
    # Relationships
    allocation_rule = relationship("AllocationRule", back_populates="allocation_lines")
    target_account = relationship("ChartOfAccounts")
    
    def __repr__(self) -> str:
        return f"<AllocationRuleLine(id={self.id}, rule_id={self.allocation_rule_id}, percentage={self.allocation_percentage})>"


class Allocation(BaseModel):
    """
    Records actual allocations performed based on allocation rules.
    """
    __tablename__ = "allocations"
    
    # Allocation identification
    allocation_number = Column(String(50), unique=True, index=True, nullable=False)
    allocation_date = Column(Date, nullable=False)
    
    # Source transaction
    source_journal_entry_id = Column(GUID(), ForeignKey("journal_entries.id"), nullable=False)
    source_amount = Column(Numeric(15, 2), nullable=False)
    
    # Allocation rule used
    allocation_rule_id = Column(GUID(), ForeignKey("allocation_rules.id"), nullable=False)
    
    # Status
    status = Column(String(20), nullable=False, default="posted")
    
    # Description
    description = Column(Text, nullable=True)
    
    # Relationships
    source_journal_entry = relationship("JournalEntry")
    allocation_rule = relationship("AllocationRule", back_populates="allocations")
    allocation_entries = relationship("AllocationEntry", back_populates="allocation", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Allocation(id={self.id}, number='{self.allocation_number}', amount={self.source_amount})>"


class AllocationEntry(BaseModel):
    """
    Individual allocation entries created from an allocation.
    """
    __tablename__ = "allocation_entries"
    
    # Parent allocation
    allocation_id = Column(GUID(), ForeignKey("allocations.id"), nullable=False)
    
    # Target details
    target_account_id = Column(GUID(), ForeignKey("chart_of_accounts.id"), nullable=False)
    target_department_id = Column(GUID(), nullable=True)
    target_cost_center_id = Column(GUID(), nullable=True)
    
    # Allocation amounts
    allocated_amount = Column(Numeric(15, 2), nullable=False)
    allocation_percentage = Column(Numeric(5, 2), nullable=True)
    
    # Generated journal entry
    journal_entry_id = Column(GUID(), ForeignKey("journal_entries.id"), nullable=True)
    
    # Description
    description = Column(Text, nullable=True)
    
    # Relationships
    allocation = relationship("Allocation", back_populates="allocation_entries")
    target_account = relationship("ChartOfAccounts")
    journal_entry = relationship("JournalEntry")
    
    def __repr__(self) -> str:
        return f"<AllocationEntry(id={self.id}, amount={self.allocated_amount}, percentage={self.allocation_percentage})>"