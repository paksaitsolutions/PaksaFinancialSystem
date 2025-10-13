"""
Unified Cross-Module Workflow Engine
Orchestrates workflows across different modules
"""
from typing import Dict, Any, Optional, List, Callable
from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey, Boolean, Integer
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseModel, AuditMixin
from datetime import datetime
from enum import Enum

class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WorkflowStepStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class UnifiedWorkflow(BaseModel, AuditMixin):
    """Cross-module workflow definition"""
    __tablename__ = "unified_workflows"
    
    workflow_name = Column(String(200), nullable=False)
    workflow_type = Column(String(50), nullable=False, index=True)  # approval, automation, integration
    description = Column(Text)
    
    # Trigger configuration
    trigger_module = Column(String(50), nullable=False)
    trigger_event = Column(String(100), nullable=False)  # invoice_created, payment_approved, etc.
    trigger_conditions = Column(JSON)  # Conditions that must be met to trigger
    
    # Workflow configuration
    is_active = Column(Boolean, default=True)
    is_system_workflow = Column(Boolean, default=False)
    priority = Column(Integer, default=1)
    timeout_minutes = Column(Integer, default=1440)  # 24 hours default
    
    # Relationships
    steps = relationship("UnifiedWorkflowStep", back_populates="workflow", cascade="all, delete-orphan")
    instances = relationship("UnifiedWorkflowInstance", back_populates="workflow")
    
    __table_args__ = (
        {"extend_existing": True},
    )

class UnifiedWorkflowStep(BaseModel, AuditMixin):
    """Individual steps in a workflow"""
    __tablename__ = "unified_workflow_steps"
    
    workflow_id = Column(String, ForeignKey("unified_workflows.id"), nullable=False)
    step_name = Column(String(200), nullable=False)
    step_order = Column(Integer, nullable=False)
    
    # Step configuration
    step_type = Column(String(50), nullable=False)  # approval, notification, automation, integration
    target_module = Column(String(50), nullable=False)
    action_type = Column(String(100), nullable=False)
    
    # Execution configuration
    action_config = Column(JSON)  # Configuration for the action
    conditions = Column(JSON)  # Conditions for step execution
    timeout_minutes = Column(Integer, default=60)
    
    # Approval configuration (if step_type = approval)
    approver_role = Column(String(100))
    approver_user_id = Column(String, ForeignKey("users.id"))
    require_all_approvers = Column(Boolean, default=False)
    
    # Relationships
    workflow = relationship("UnifiedWorkflow", back_populates="steps")
    approver = relationship("User", viewonly=True)
    
    __table_args__ = (
        {"extend_existing": True},
    )

class UnifiedWorkflowInstance(BaseModel, AuditMixin):
    """Running instance of a workflow"""
    __tablename__ = "unified_workflow_instances"
    
    workflow_id = Column(String, ForeignKey("unified_workflows.id"), nullable=False)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    
    # Instance details
    instance_name = Column(String(200))
    status = Column(String(20), default=WorkflowStatus.ACTIVE)
    
    # Trigger context
    trigger_data = Column(JSON)  # Data that triggered the workflow
    trigger_resource_type = Column(String(100))
    trigger_resource_id = Column(String)
    
    # Execution tracking
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    current_step_id = Column(String, ForeignKey("unified_workflow_steps.id"))
    
    # Error handling
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Relationships
    workflow = relationship("UnifiedWorkflow", back_populates="instances")
    company = relationship("Company", viewonly=True)
    current_step = relationship("UnifiedWorkflowStep", viewonly=True)
    step_instances = relationship("UnifiedWorkflowStepInstance", back_populates="workflow_instance")
    
    __table_args__ = (
        {"extend_existing": True},
    )

class UnifiedWorkflowStepInstance(BaseModel, AuditMixin):
    """Instance of a workflow step execution"""
    __tablename__ = "unified_workflow_step_instances"
    
    workflow_instance_id = Column(String, ForeignKey("unified_workflow_instances.id"), nullable=False)
    workflow_step_id = Column(String, ForeignKey("unified_workflow_steps.id"), nullable=False)
    
    # Execution details
    status = Column(String(20), default=WorkflowStepStatus.PENDING)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Approval details (if applicable)
    assigned_to = Column(String, ForeignKey("users.id"))
    approved_by = Column(String, ForeignKey("users.id"))
    approval_notes = Column(Text)
    
    # Execution results
    result_data = Column(JSON)
    error_message = Column(Text)
    
    # Relationships
    workflow_instance = relationship("UnifiedWorkflowInstance", back_populates="step_instances")
    workflow_step = relationship("UnifiedWorkflowStep", viewonly=True)
    assigned_user = relationship("User", foreign_keys=[assigned_to], viewonly=True)
    approver = relationship("User", foreign_keys=[approved_by], viewonly=True)
    
    __table_args__ = (
        {"extend_existing": True},
    )

class UnifiedWorkflowEngine:
    """Cross-module workflow execution engine"""
    
    def __init__(self, db_session):
        self.db = db_session
        self.step_handlers = {}
        self.event_listeners = {}
    
    def register_step_handler(self, step_type: str, handler: Callable):
        """Register a handler for a specific step type"""
        self.step_handlers[step_type] = handler
    
    def register_event_listener(self, event: str, listener: Callable):
        """Register a listener for workflow events"""
        if event not in self.event_listeners:
            self.event_listeners[event] = []
        self.event_listeners[event].append(listener)
    
    async def trigger_workflow(self, module: str, event: str, data: Dict[str, Any], 
                              resource_type: str = None, resource_id: str = None) -> List[UnifiedWorkflowInstance]:
        """Trigger workflows based on an event"""
        
        # Find matching workflows
        workflows = await self.db.query(UnifiedWorkflow).filter(
            UnifiedWorkflow.trigger_module == module,
            UnifiedWorkflow.trigger_event == event,
            UnifiedWorkflow.is_active == True
        ).all()
        
        instances = []
        for workflow in workflows:
            # Check trigger conditions
            if self._check_conditions(workflow.trigger_conditions, data):
                instance = await self._create_workflow_instance(workflow, data, resource_type, resource_id)
                instances.append(instance)
                
                # Start workflow execution
                await self._execute_workflow(instance)
        
        return instances
    
    async def _create_workflow_instance(self, workflow: UnifiedWorkflow, trigger_data: Dict,
                                       resource_type: str, resource_id: str) -> UnifiedWorkflowInstance:
        """Create a new workflow instance"""
        
        instance = UnifiedWorkflowInstance(
            workflow_id=workflow.id,
            company_id=trigger_data.get('company_id'),
            instance_name=f"{workflow.workflow_name} - {datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            trigger_data=trigger_data,
            trigger_resource_type=resource_type,
            trigger_resource_id=resource_id
        )
        
        self.db.add(instance)
        await self.db.commit()
        return instance
    
    async def _execute_workflow(self, instance: UnifiedWorkflowInstance):
        """Execute a workflow instance"""
        
        try:
            # Get workflow steps in order
            steps = await self.db.query(UnifiedWorkflowStep).filter(
                UnifiedWorkflowStep.workflow_id == instance.workflow_id
            ).order_by(UnifiedWorkflowStep.step_order).all()
            
            for step in steps:
                # Check step conditions
                if not self._check_conditions(step.conditions, instance.trigger_data):
                    continue
                
                # Create step instance
                step_instance = UnifiedWorkflowStepInstance(
                    workflow_instance_id=instance.id,
                    workflow_step_id=step.id,
                    started_at=datetime.utcnow()
                )
                self.db.add(step_instance)
                await self.db.commit()
                
                # Execute step
                success = await self._execute_step(step, step_instance, instance)
                
                if not success:
                    instance.status = WorkflowStatus.FAILED
                    break
            
            if instance.status != WorkflowStatus.FAILED:
                instance.status = WorkflowStatus.COMPLETED
                instance.completed_at = datetime.utcnow()
            
            await self.db.commit()
            
        except Exception as e:
            instance.status = WorkflowStatus.FAILED
            instance.error_message = str(e)
            await self.db.commit()
    
    async def _execute_step(self, step: UnifiedWorkflowStep, step_instance: UnifiedWorkflowStepInstance,
                           workflow_instance: UnifiedWorkflowInstance) -> bool:
        """Execute a single workflow step"""
        
        try:
            step_instance.status = WorkflowStepStatus.IN_PROGRESS
            await self.db.commit()
            
            # Get step handler
            handler = self.step_handlers.get(step.step_type)
            if not handler:
                raise Exception(f"No handler registered for step type: {step.step_type}")
            
            # Execute step
            result = await handler(step, step_instance, workflow_instance)
            
            step_instance.status = WorkflowStepStatus.COMPLETED
            step_instance.completed_at = datetime.utcnow()
            step_instance.result_data = result
            
            await self.db.commit()
            return True
            
        except Exception as e:
            step_instance.status = WorkflowStepStatus.FAILED
            step_instance.error_message = str(e)
            await self.db.commit()
            return False
    
    def _check_conditions(self, conditions: Dict, data: Dict) -> bool:
        """Check if conditions are met"""
        if not conditions:
            return True
        
        # Simple condition checking - can be extended
        for key, expected_value in conditions.items():
            if key not in data or data[key] != expected_value:
                return False
        
        return True
    
    async def approve_step(self, step_instance_id: str, user_id: str, approved: bool, notes: str = None):
        """Approve or reject a workflow step"""
        
        step_instance = await self.db.query(UnifiedWorkflowStepInstance).filter(
            UnifiedWorkflowStepInstance.id == step_instance_id
        ).first()
        
        if not step_instance:
            raise Exception("Step instance not found")
        
        step_instance.approved_by = user_id
        step_instance.approval_notes = notes
        step_instance.completed_at = datetime.utcnow()
        
        if approved:
            step_instance.status = WorkflowStepStatus.COMPLETED
            # Continue workflow execution
            await self._continue_workflow(step_instance.workflow_instance_id)
        else:
            step_instance.status = WorkflowStepStatus.FAILED
            # Mark workflow as failed
            workflow_instance = await self.db.query(UnifiedWorkflowInstance).filter(
                UnifiedWorkflowInstance.id == step_instance.workflow_instance_id
            ).first()
            workflow_instance.status = WorkflowStatus.FAILED
        
        await self.db.commit()
    
    async def _continue_workflow(self, workflow_instance_id: str):
        """Continue workflow execution after approval"""
        workflow_instance = await self.db.query(UnifiedWorkflowInstance).filter(
            UnifiedWorkflowInstance.id == workflow_instance_id
        ).first()
        
        if workflow_instance and workflow_instance.status == WorkflowStatus.ACTIVE:
            await self._execute_workflow(workflow_instance)

# Default workflow templates
DEFAULT_WORKFLOWS = {
    "ap_invoice_approval": {
        "workflow_name": "AP Invoice Approval",
        "workflow_type": "approval",
        "trigger_module": "ap",
        "trigger_event": "invoice_created",
        "trigger_conditions": {"amount": {"gt": 1000}},
        "steps": [
            {
                "step_name": "Manager Approval",
                "step_type": "approval",
                "target_module": "ap",
                "action_type": "approve_invoice",
                "approver_role": "AP Manager"
            },
            {
                "step_name": "Post to GL",
                "step_type": "automation",
                "target_module": "gl",
                "action_type": "create_journal_entry"
            }
        ]
    },
    "payroll_processing": {
        "workflow_name": "Payroll Processing",
        "workflow_type": "automation",
        "trigger_module": "payroll",
        "trigger_event": "payroll_run_created",
        "steps": [
            {
                "step_name": "Calculate Payroll",
                "step_type": "automation",
                "target_module": "payroll",
                "action_type": "calculate_payroll"
            },
            {
                "step_name": "Manager Review",
                "step_type": "approval",
                "target_module": "payroll",
                "action_type": "approve_payroll",
                "approver_role": "Payroll Manager"
            },
            {
                "step_name": "Post to GL",
                "step_type": "automation",
                "target_module": "gl",
                "action_type": "create_payroll_entries"
            },
            {
                "step_name": "Generate Paystubs",
                "step_type": "automation",
                "target_module": "payroll",
                "action_type": "generate_paystubs"
            }
        ]
    }
}