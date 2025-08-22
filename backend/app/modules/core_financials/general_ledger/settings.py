"""GL module-specific settings and configuration"""
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from app.core.database.base import Base
import uuid
from datetime import datetime

class GLSettings(Base):
    """GL module settings per tenant"""
    __tablename__ = "gl_settings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Posting rules
    allow_future_posting = Column(Boolean, default=False)
    require_balanced_entries = Column(Boolean, default=True)
    auto_post_entries = Column(Boolean, default=False)
    
    # Currency settings
    base_currency = Column(String(3), default='USD')
    allow_multi_currency = Column(Boolean, default=False)
    
    # Fiscal year settings
    fiscal_year_start_month = Column(Integer, default=1)  # January
    fiscal_year_end_month = Column(Integer, default=12)   # December
    
    # Approval settings
    require_journal_approval = Column(Boolean, default=True)
    require_period_close_approval = Column(Boolean, default=True)
    require_reversal_approval = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class GLRole(Base):
    """GL-specific roles and permissions"""
    __tablename__ = "gl_roles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    description = Column(Text)
    
    # Permissions
    can_create_accounts = Column(Boolean, default=False)
    can_edit_accounts = Column(Boolean, default=False)
    can_delete_accounts = Column(Boolean, default=False)
    
    can_create_journal_entries = Column(Boolean, default=False)
    can_edit_journal_entries = Column(Boolean, default=False)
    can_post_journal_entries = Column(Boolean, default=False)
    can_unpost_journal_entries = Column(Boolean, default=False)
    can_reverse_journal_entries = Column(Boolean, default=False)
    
    can_close_periods = Column(Boolean, default=False)
    can_reopen_periods = Column(Boolean, default=False)
    
    can_approve_entries = Column(Boolean, default=False)
    can_view_all_entries = Column(Boolean, default=False)
    can_generate_reports = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class GLApprovalWorkflow(Base):
    """GL approval workflow configuration"""
    __tablename__ = "gl_approval_workflows"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    workflow_type = Column(String(50), nullable=False)  # journal_entry, period_close, reversal
    
    # Workflow settings
    approval_required = Column(Boolean, default=True)
    approval_levels = Column(Integer, default=1)
    auto_approve_threshold = Column(Integer, default=0)  # Amount threshold for auto-approval
    
    # Approver roles
    approver_roles = Column(Text)  # JSON array of role IDs
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Default role configurations
DEFAULT_GL_ROLES = [
    {
        "name": "GL_ACCOUNTANT",
        "description": "General Ledger Accountant - Can create and edit entries",
        "permissions": {
            "can_create_accounts": True,
            "can_edit_accounts": True,
            "can_create_journal_entries": True,
            "can_edit_journal_entries": True,
            "can_view_all_entries": True,
            "can_generate_reports": True
        }
    },
    {
        "name": "GL_REVIEWER",
        "description": "GL Reviewer - Can post and approve entries",
        "permissions": {
            "can_post_journal_entries": True,
            "can_unpost_journal_entries": True,
            "can_approve_entries": True,
            "can_view_all_entries": True,
            "can_generate_reports": True
        }
    },
    {
        "name": "GL_AUDITOR",
        "description": "GL Auditor - Read-only access with reporting",
        "permissions": {
            "can_view_all_entries": True,
            "can_generate_reports": True
        }
    }
]