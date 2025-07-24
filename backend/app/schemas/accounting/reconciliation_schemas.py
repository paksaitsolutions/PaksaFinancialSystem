"""
Reconciliation Schemas

This module contains Pydantic models for account reconciliation functionality.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, validator, root_validator

from ..models.reconciliation_models import ReconciliationStatus, ReconciliationMatchType


class ReconciliationBase(BaseModel):
    """Base schema for reconciliation operations."""
    account_id: UUID = Field(..., description="ID of the account being reconciled")
    start_date: datetime = Field(..., description="Start date of the reconciliation period")
    end_date: datetime = Field(..., description="End date of the reconciliation period")
    statement_balance: float = Field(..., description="Ending balance from the bank statement")
    statement_date: datetime = Field(..., description="Date of the bank statement")
    notes: Optional[str] = Field(None, description="Additional notes about the reconciliation")

    @root_validator
    def validate_dates(cls, values):
        """Validate that start_date is before end_date."""
        start_date = values.get('start_date')
        end_date = values.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise ValueError("start_date must be before end_date")
            
        return values


class ReconciliationCreate(ReconciliationBase):
    """Schema for creating a new reconciliation."""
    pass


class ReconciliationUpdate(BaseModel):
    """Schema for updating an existing reconciliation."""
    status: Optional[ReconciliationStatus] = Field(None, description="Updated status of the reconciliation")
    statement_balance: Optional[float] = Field(None, description="Updated statement balance")
    statement_date: Optional[datetime] = Field(None, description="Updated statement date")
    cleared_balance: Optional[float] = Field(None, description="Updated cleared balance")
    difference: Optional[float] = Field(None, description="Updated difference amount")
    notes: Optional[str] = Field(None, description="Updated notes")


class Reconciliation(ReconciliationBase):
    """Schema for returning a reconciliation."""
    id: UUID = Field(..., description="Unique identifier for the reconciliation")
    status: ReconciliationStatus = Field(..., description="Current status of the reconciliation")
    cleared_balance: Optional[float] = Field(None, description="Calculated balance of cleared transactions")
    difference: Optional[float] = Field(None, description="Difference between statement balance and cleared balance")
    created_at: datetime = Field(..., description="When the reconciliation was created")
    updated_at: datetime = Field(..., description="When the reconciliation was last updated")
    created_by: UUID = Field(..., description="ID of the user who created the reconciliation")
    updated_by: UUID = Field(..., description="ID of the user who last updated the reconciliation")
    completed_at: Optional[datetime] = Field(None, description="When the reconciliation was completed")
    completed_by: Optional[UUID] = Field(None, description="ID of the user who completed the reconciliation")
    
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class ReconciliationDetail(Reconciliation):
    """Schema for returning a reconciliation with additional details."""
    items: List["ReconciliationItem"] = Field(default_factory=list, description="Items in this reconciliation")
    
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class ReconciliationItemBase(BaseModel):
    """Base schema for reconciliation items."""
    transaction_date: datetime = Field(..., description="Date of the transaction")
    description: str = Field(..., description="Description of the item")
    reference: Optional[str] = Field(None, description="Reference number or identifier")
    amount: float = Field(..., description="Amount of the transaction (positive for deposits, negative for withdrawals)")
    is_cleared: bool = Field(False, description="Whether this item has been cleared in the bank statement")
    cleared_date: Optional[datetime] = Field(None, description="Date when this item was cleared")
    is_matched: bool = Field(False, description="Whether this item has been matched to a bank transaction")
    match_type: Optional[ReconciliationMatchType] = Field(None, description="How this item was matched")
    match_confidence: Optional[float] = Field(None, ge=0, le=1, description="Confidence score for automatic matches (0-1)")
    notes: Optional[str] = Field(None, description="Additional notes about this item")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the reconciliation item")


class ReconciliationItemCreate(ReconciliationItemBase):
    """Schema for creating a new reconciliation item."""
    journal_entry_id: Optional[UUID] = Field(None, description="ID of the journal entry this item represents, if any")


class ReconciliationItemUpdate(BaseModel):
    """Schema for updating an existing reconciliation item."""
    is_cleared: Optional[bool] = Field(None, description="Updated cleared status")
    cleared_date: Optional[datetime] = Field(None, description="Updated cleared date")
    is_matched: Optional[bool] = Field(None, description="Updated matched status")
    match_type: Optional[ReconciliationMatchType] = Field(None, description="Updated match type")
    match_confidence: Optional[float] = Field(None, ge=0, le=1, description="Updated match confidence score")
    notes: Optional[str] = Field(None, description="Updated notes")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")


class ReconciliationItem(ReconciliationItemBase):
    """Schema for returning a reconciliation item."""
    id: UUID = Field(..., description="Unique identifier for the reconciliation item")
    reconciliation_id: UUID = Field(..., description="ID of the reconciliation this item belongs to")
    journal_entry_id: Optional[UUID] = Field(None, description="ID of the journal entry this item represents, if any")
    created_at: datetime = Field(..., description="When the item was created")
    updated_at: datetime = Field(..., description="When the item was last updated")
    created_by: UUID = Field(..., description="ID of the user who created the item")
    updated_by: UUID = Field(..., description="ID of the user who last updated the item")
    
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class UnreconciledTransaction(BaseModel):
    """Schema for unreconciled transactions."""
    id: UUID = Field(..., description="Unique identifier for the transaction")
    transaction_date: datetime = Field(..., description="Date of the transaction")
    reference: Optional[str] = Field(None, description="Reference number or identifier")
    description: str = Field(..., description="Description of the transaction")
    amount: float = Field(..., description="Amount of the transaction (positive for deposits, negative for withdrawals)")
    type: str = Field(..., description="Type of transaction (debit or credit)")
    source_type: str = Field(..., description="Source of the transaction (e.g., journal_entry, bank_statement)")
    source_id: Optional[UUID] = Field(None, description="ID of the source document")
    
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class ReconciliationAuditLog(BaseModel):
    """Schema for reconciliation audit logs."""
    id: UUID = Field(..., description="Unique identifier for the audit log entry")
    reconciliation_id: UUID = Field(..., description="ID of the reconciliation this log entry is for")
    user_id: UUID = Field(..., description="ID of the user who performed the action")
    action: str = Field(..., description="Type of action performed")
    details: Dict[str, Any] = Field(..., description="Detailed information about the action")
    created_at: datetime = Field(..., description="When the log entry was created")
    ip_address: Optional[str] = Field(None, description="IP address of the user who performed the action")
    user_agent: Optional[str] = Field(None, description="User agent string of the client used")
    
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


# Update forward references
ReconciliationDetail.update_forward_refs()
