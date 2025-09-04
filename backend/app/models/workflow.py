"""
Workflow Models - Approval Workflows, Steps, Approvals, Delegations
"""
from sqlalchemy import Column, String, Integer, Numeric, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, AuditMixin
from datetime import datetime

class WorkflowInstance(BaseModel, AuditMixin):
    __tablename__ = "workflow_instances"
    
    workflow_type = Column(String(50), nullable=False)  # journal_entry, vendor_payment, etc.
    entity_id = Column(String(36), nullable=False)  # ID of the entity being approved
    entity_type = Column(String(50), nullable=False)  # JournalEntry, VendorPayment, etc.
    status = Column(String(20), default='pending')  # pending, approved, rejected, cancelled
    current_step = Column(Integer, default=1)
    total_steps = Column(Integer, nullable=False)
    amount = Column(Numeric(15, 2))
    priority = Column(String(10), default='normal')  # low, normal, high, urgent
    workflow_data = Column(Text)  # JSON workflow definition
    completed_at = Column(DateTime)
    
    # Relationships
    steps = relationship("WorkflowStep", back_populates="workflow", cascade="all, delete-orphan")
    approvals = relationship("WorkflowApproval", back_populates="workflow", cascade="all, delete-orphan")
    delegations = relationship("WorkflowDelegation", back_populates="workflow", cascade="all, delete-orphan")

class WorkflowStep(BaseModel):
    __tablename__ = "workflow_steps"
    
    workflow_id = Column(String(36), ForeignKey("workflow_instances.id"), nullable=False)
    step_number = Column(Integer, nullable=False)
    step_name = Column(String(100), nullable=False)
    approver_role = Column(String(50))  # Role-based approval
    approver_user = Column(String(36))  # Direct user assignment
    delegated_to = Column(String(36))  # Delegated approver
    required_approvals = Column(Integer, default=1)  # Number of approvals needed
    status = Column(String(20), default='waiting')  # waiting, pending, approved, rejected
    due_date = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    workflow = relationship("WorkflowInstance", back_populates="steps")
    approvals = relationship("WorkflowApproval", back_populates="step", cascade="all, delete-orphan")

class WorkflowApproval(BaseModel):
    __tablename__ = "workflow_approvals"
    
    workflow_id = Column(String(36), ForeignKey("workflow_instances.id"), nullable=False)
    step_id = Column(String(36), ForeignKey("workflow_steps.id"), nullable=False)
    approver_id = Column(String(36), nullable=False)
    action = Column(String(20), nullable=False)  # approved, rejected
    comments = Column(Text)
    approved_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Relationships
    workflow = relationship("WorkflowInstance", back_populates="approvals")
    step = relationship("WorkflowStep", back_populates="approvals")

class WorkflowDelegation(BaseModel):
    __tablename__ = "workflow_delegations"
    
    workflow_id = Column(String(36), ForeignKey("workflow_instances.id"), nullable=False)
    step_id = Column(String(36), ForeignKey("workflow_steps.id"), nullable=False)
    from_user = Column(String(36), nullable=False)
    to_user = Column(String(36), nullable=False)
    reason = Column(Text)
    delegated_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    workflow = relationship("WorkflowInstance", back_populates="delegations")

class WorkflowTemplate(BaseModel, AuditMixin):
    __tablename__ = "workflow_templates"
    
    template_name = Column(String(100), nullable=False)
    workflow_type = Column(String(50), nullable=False)
    description = Column(Text)
    template_data = Column(Text)  # JSON template definition
    is_default = Column(Boolean, default=False)
    min_amount = Column(Numeric(15, 2))
    max_amount = Column(Numeric(15, 2))

class ApprovalRule(BaseModel, AuditMixin):
    __tablename__ = "approval_rules"
    
    rule_name = Column(String(100), nullable=False)
    workflow_type = Column(String(50), nullable=False)
    condition_field = Column(String(50))  # amount, department, etc.
    condition_operator = Column(String(10))  # >, <, =, >=, <=
    condition_value = Column(String(100))
    approver_role = Column(String(50))
    approver_user = Column(String(36))
    step_order = Column(Integer, default=1)
    required_approvals = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)

class WorkflowNotification(BaseModel):
    __tablename__ = "workflow_notifications"
    
    workflow_id = Column(String(36), ForeignKey("workflow_instances.id"), nullable=False)
    recipient_id = Column(String(36), nullable=False)
    notification_type = Column(String(50), nullable=False)  # email, sms, push
    subject = Column(String(255))
    message = Column(Text)
    sent_at = Column(DateTime)
    status = Column(String(20), default='pending')  # pending, sent, failed
    retry_count = Column(Integer, default=0)
    
    # Relationships
    workflow = relationship("WorkflowInstance")

class WorkflowComment(BaseModel):
    __tablename__ = "workflow_comments"
    
    workflow_id = Column(String(36), ForeignKey("workflow_instances.id"), nullable=False)
    user_id = Column(String(36), nullable=False)
    comment = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)  # Internal vs external comments
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    workflow = relationship("WorkflowInstance")

class WorkflowAttachment(BaseModel):
    __tablename__ = "workflow_attachments"
    
    workflow_id = Column(String(36), ForeignKey("workflow_instances.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    uploaded_by = Column(String(36), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    workflow = relationship("WorkflowInstance")