"""
Reconciliation Schemas

This module contains Pydantic models for account reconciliation data validation and serialization.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, validator, condecimal

from .base import BaseSchema


class ReconciliationStatus(str, Enum):
    """Status of a reconciliation."""
    DRAFT = 'draft'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    VOIDED = 'voided'


class ReconciliationMatchType(str, Enum):
    """Type of reconciliation match."""
    AUTO = 'auto'
    MANUAL = 'manual'
    SUGGESTED = 'suggested'


# Shared properties
class ReconciliationBase(BaseModel):
    """Base schema for reconciliation data."""
    account_id: UUID = Field(..., description="ID of the account being reconciled")
    reference: str = Field(..., max_length=100, description="Reference number/identifier for the reconciliation")
    start_date: datetime = Field(..., description="Start date of the reconciliation period")
    end_date: datetime = Field(..., description="End date of the reconciliation period")
    statement_balance: condecimal(max_digits=19, decimal_places=4) = Field(..., description="Ending balance from the external statement")
    statement_currency: str = Field(default="USD", max_length=3, description="Currency of the statement balance")
    statement_reference: Optional[str] = Field(None, max_length=100, description="Reference number from the statement")
    statement_date: datetime = Field(..., description="Date of the statement")
    notes: Optional[str] = Field(None, description="Additional notes or comments")

    @validator('end_date')
    def validate_date_range(cls, v, values, **kwargs):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


# Properties to receive on reconciliation creation
class ReconciliationCreate(ReconciliationBase):
    """Schema for creating a new reconciliation."""
    pass


# Properties to receive on reconciliation update
class ReconciliationUpdate(BaseModel):
    """Schema for updating an existing reconciliation."""
    status: Optional[ReconciliationStatus] = Field(None, description="New status of the reconciliation")
    notes: Optional[str] = Field(None, description="Additional notes or comments")


# Properties shared by models stored in DB
class ReconciliationInDBBase(ReconciliationBase):
    """Base schema for reconciliation data stored in the database."""
    id: UUID
    status: ReconciliationStatus = Field(..., description="Current status of the reconciliation")
    calculated_balance: condecimal(max_digits=19, decimal_places=4) = Field(..., description="Calculated balance from the system")
    difference: condecimal(max_digits=19, decimal_places=4) = Field(..., description="Difference between statement and calculated balance")
    created_by: UUID = Field(..., description="ID of the user who created the reconciliation")
    created_at: datetime = Field(..., description="When the reconciliation was created")
    updated_at: datetime = Field(..., description="When the reconciliation was last updated")
    approved_by: Optional[UUID] = Field(None, description="ID of the user who approved the reconciliation")
    approved_at: Optional[datetime] = Field(None, description="When the reconciliation was approved")

    class Config:
        orm_mode = True


# Properties to return to client
class Reconciliation(ReconciliationInDBBase):
    """Schema for returning reconciliation data to the client."""
    pass


# Shared properties for reconciliation items
class ReconciliationItemBase(BaseModel):
    """Base schema for reconciliation items."""
    reconciliation_id: UUID = Field(..., description="ID of the parent reconciliation")
    journal_entry_id: Optional[UUID] = Field(None, description="ID of the journal entry (if applicable)")
    journal_entry_line_id: Optional[UUID] = Field(None, description="ID of the journal entry line (if applicable)")
    statement_line_ref: Optional[str] = Field(None, max_length=100, description="Reference from the statement")
    statement_line_date: Optional[datetime] = Field(None, description="Date from the statement line")
    statement_line_description: Optional[str] = Field(None, description="Description from the statement")
    statement_line_amount: Optional[condecimal(max_digits=19, decimal_places=4)] = Field(None, description="Amount from the statement")
    match_type: ReconciliationMatchType = Field(ReconciliationMatchType.MANUAL, description="How this item was matched")
    is_matched: bool = Field(False, description="Whether this item has been matched")
    matched_with: Optional[UUID] = Field(None, description="ID of the item this was matched with")
    notes: Optional[str] = Field(None, description="Additional notes about this item")


# Properties to receive on item creation
class ReconciliationItemCreate(ReconciliationItemBase):
    """Schema for creating a new reconciliation item."""
    pass


# Properties to receive on item update
class ReconciliationItemUpdate(BaseModel):
    """Schema for updating an existing reconciliation item."""
    is_matched: Optional[bool] = Field(None, description="Whether this item has been matched")
    matched_with: Optional[UUID] = Field(None, description="ID of the item this was matched with")
    notes: Optional[str] = Field(None, description="Additional notes about this item")


# Properties shared by item models stored in DB
class ReconciliationItemInDBBase(ReconciliationItemBase):
    """Base schema for reconciliation item data stored in the database."""
    id: UUID
    created_at: datetime = Field(..., description="When the item was created")
    updated_at: datetime = Field(..., description="When the item was last updated")

    class Config:
        orm_mode = True


# Properties to return to client
class ReconciliationItem(ReconciliationItemInDBBase):
    """Schema for returning reconciliation item data to the client."""
    pass


# Shared properties for reconciliation rules
class ReconciliationRuleBase(BaseModel):
    """Base schema for reconciliation rules."""
    account_id: UUID = Field(..., description="ID of the account this rule applies to")
    name: str = Field(..., max_length=100, description="Name of the rule")
    description: Optional[str] = Field(None, description="Description of the rule")
    is_active: bool = Field(True, description="Whether the rule is active")
    priority: int = Field(0, description="Priority of the rule (higher = evaluated first)")
    reference_pattern: Optional[str] = Field(None, max_length=200, description="Pattern to match against transaction references")
    description_pattern: Optional[str] = Field(None, max_length=500, description="Pattern to match against transaction descriptions")
    amount_min: Optional[float] = Field(None, description="Minimum amount to match")
    amount_max: Optional[float] = Field(None, description="Maximum amount to match")
    auto_approve: bool = Field(False, description="Whether to automatically approve matches")
    category_id: Optional[UUID] = Field(None, description="Category to assign to matched transactions")


# Properties to receive on rule creation
class ReconciliationRuleCreate(ReconciliationRuleBase):
    """Schema for creating a new reconciliation rule."""
    created_by: UUID = Field(..., description="ID of the user creating the rule")


# Properties to receive on rule update
class ReconciliationRuleUpdate(BaseModel):
    """Schema for updating an existing reconciliation rule."""
    name: Optional[str] = Field(None, max_length=100, description="Name of the rule")
    description: Optional[str] = Field(None, description="Description of the rule")
    is_active: Optional[bool] = Field(None, description="Whether the rule is active")
    priority: Optional[int] = Field(None, description="Priority of the rule (higher = evaluated first)")
    reference_pattern: Optional[str] = Field(None, max_length=200, description="Pattern to match against transaction references")
    description_pattern: Optional[str] = Field(None, max_length=500, description="Pattern to match against transaction descriptions")
    amount_min: Optional[float] = Field(None, description="Minimum amount to match")
    amount_max: Optional[float] = Field(None, description="Maximum amount to match")
    auto_approve: Optional[bool] = Field(None, description="Whether to automatically approve matches")
    category_id: Optional[UUID] = Field(None, description="Category to assign to matched transactions")


# Properties shared by rule models stored in DB
class ReconciliationRuleInDBBase(ReconciliationRuleBase):
    """Base schema for reconciliation rule data stored in the database."""
    id: UUID
    created_by: UUID = Field(..., description="ID of the user who created the rule")
    created_at: datetime = Field(..., description="When the rule was created")
    updated_at: datetime = Field(..., description="When the rule was last updated")

    class Config:
        orm_mode = True


# Properties to return to client
class ReconciliationRule(ReconciliationRuleInDBBase):
    """Schema for returning reconciliation rule data to the client."""
    pass


# Properties for reconciliation audit log
class ReconciliationAuditLogBase(BaseModel):
    """Base schema for reconciliation audit logs."""
    reconciliation_id: UUID = Field(..., description="ID of the reconciliation")
    action: str = Field(..., max_length=100, description="Action that was performed")
    details: Optional[dict] = Field(None, description="Additional details about the action")
    user_id: UUID = Field(..., description="ID of the user who performed the action")


class ReconciliationAuditLogCreate(ReconciliationAuditLogBase):
    """Schema for creating a new reconciliation audit log entry."""
    pass


class ReconciliationAuditLog(ReconciliationAuditLogBase):
    """Schema for returning reconciliation audit log data to the client."""
    id: UUID
    created_at: datetime = Field(..., description="When the log entry was created")

    class Config:
        orm_mode = True


# Response models
class ReconciliationWithItems(Reconciliation):
    """Reconciliation with its items included."""
    items: List[ReconciliationItem] = Field(default_factory=list, description="Items in this reconciliation")


class ReconciliationWithDetails(ReconciliationWithItems):
    """Reconciliation with items and audit log."""
    audit_log: List[ReconciliationAuditLog] = Field(default_factory=list, description="Audit log for this reconciliation")
