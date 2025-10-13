"""
Data retention policy models.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, JSON
from sqlalchemy.orm import relationship

from .base import BaseModel, GUID


class RetentionAction(str, Enum):
    DELETE = "delete"
    ARCHIVE = "archive"
    ANONYMIZE = "anonymize"


class RetentionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class DataRetentionPolicy(BaseModel):
    """
    Data retention policy configuration.
    """
    __tablename__ = "data_retention_policies"
    
    # Policy identification
    policy_name = Column(String(200), nullable=False)
    policy_code = Column(String(50), unique=True, nullable=False)
    
    # Target data
    table_name = Column(String(100), nullable=False)
    data_category = Column(String(100), nullable=False)
    
    # Retention settings
    retention_period_days = Column(Integer, nullable=False)
    retention_action = Column(String(20), nullable=False, default=RetentionAction.DELETE)
    
    # Policy details
    description = Column(Text, nullable=True)
    legal_basis = Column(String(200), nullable=True)
    conditions = Column(JSON, nullable=True)
    
    # Status
    status = Column(String(20), nullable=False, default=RetentionStatus.ACTIVE)
    last_executed = Column(DateTime, nullable=True)
    next_execution = Column(DateTime, nullable=True)
    
    def __repr__(self) -> str:
        return f"<DataRetentionPolicy(code='{self.policy_code}', table='{self.table_name}')>"


class RetentionExecution(BaseModel):
    """
    Data retention execution log.
    """
    __tablename__ = "retention_executions"
    
    # Execution details
    policy_id = Column(GUID(), nullable=False)
    execution_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Results
    records_processed = Column(Integer, nullable=False, default=0)
    records_deleted = Column(Integer, nullable=False, default=0)
    records_archived = Column(Integer, nullable=False, default=0)
    records_anonymized = Column(Integer, nullable=False, default=0)
    
    # Status
    status = Column(String(20), nullable=False)
    error_message = Column(Text, nullable=True)
    execution_time_seconds = Column(Integer, nullable=True)
    
    def __repr__(self) -> str:
        return f"<RetentionExecution(policy_id={self.policy_id}, date={self.execution_date})>"