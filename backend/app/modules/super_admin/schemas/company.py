from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum
from uuid import UUID

class CompanyStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"
    CANCELLED = "cancelled"

class SubscriptionTier(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class Company(BaseModel):
    id: UUID
    name: str
    email: str
    status: CompanyStatus
    subscription_tier: SubscriptionTier
    user_count: int
    storage_used: float  # GB
    created_at: datetime
    last_active: datetime
    monthly_revenue: float
    
    class Config:
        from_attributes = True

class CompanyUsage(BaseModel):
    company_id: UUID
    api_calls: int
    storage_gb: float
    active_users: int
    transactions_count: int
    last_updated: datetime