"""
Schemas for data retention operations.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class DataRetentionPolicyRequest(BaseModel):
    """Schema for data retention policy creation request."""
    policy_name: str = Field(..., description="Policy name")
    policy_code: str = Field(..., description="Policy code")
    table_name: str = Field(..., description="Target table name")
    data_category: str = Field(..., description="Data category")
    retention_period_days: int = Field(..., description="Retention period in days")
    retention_action: str = Field("delete", description="Retention action")
    description: Optional[str] = Field(None, description="Policy description")
    legal_basis: Optional[str] = Field(None, description="Legal basis")
    conditions: Optional[Dict[str, Any]] = Field(None, description="Additional conditions")


class DataRetentionPolicyResponse(BaseModel):
    """Schema for data retention policy response."""
    id: UUID = Field(..., description="Policy ID")
    policy_name: str = Field(..., description="Policy name")
    policy_code: str = Field(..., description="Policy code")
    table_name: str = Field(..., description="Target table name")
    data_category: str = Field(..., description="Data category")
    retention_period_days: int = Field(..., description="Retention period in days")
    retention_action: str = Field(..., description="Retention action")
    description: Optional[str] = Field(None, description="Policy description")
    legal_basis: Optional[str] = Field(None, description="Legal basis")
    conditions: Optional[Dict[str, Any]] = Field(None, description="Additional conditions")
    status: str = Field(..., description="Policy status")
    last_executed: Optional[datetime] = Field(None, description="Last execution timestamp")
    next_execution: Optional[datetime] = Field(None, description="Next execution timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        orm_mode = True


class RetentionExecutionResponse(BaseModel):
    """Schema for retention execution response."""
    id: UUID = Field(..., description="Execution ID")
    policy_id: UUID = Field(..., description="Policy ID")
    execution_date: datetime = Field(..., description="Execution date")
    records_processed: int = Field(..., description="Records processed")
    records_deleted: int = Field(..., description="Records deleted")
    records_archived: int = Field(..., description="Records archived")
    records_anonymized: int = Field(..., description="Records anonymized")
    status: str = Field(..., description="Execution status")
    error_message: Optional[str] = Field(None, description="Error message")
    execution_time_seconds: Optional[int] = Field(None, description="Execution time in seconds")

    class Config:
        orm_mode = True


class RetentionDashboardResponse(BaseModel):
    """Schema for retention dashboard data."""
    total_policies: int = Field(..., description="Total number of policies")
    active_policies: int = Field(..., description="Number of active policies")
    policies_due: int = Field(..., description="Number of policies due for execution")
    recent_executions: List[RetentionExecutionResponse] = Field(..., description="Recent executions")
    total_records_processed: int = Field(..., description="Total records processed today")
    storage_saved_mb: float = Field(..., description="Estimated storage saved in MB")