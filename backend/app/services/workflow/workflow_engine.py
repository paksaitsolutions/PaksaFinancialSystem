"""
Workflow engine for business process automation.
"""
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from datetime import datetime
import asyncio
import uuid

from app.core.logging import logger
from app.services.notifications.notification_service import notification_service

class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WorkflowStep:
    """Individual workflow step."""
    
    def __init__(
        self,
        name: str,
        action: Callable,
        condition: Optional[Callable] = None,
        retry_count: int = 3
    ):
        self.name = name
        self.action = action
        self.condition = condition
        self.retry_count = retry_count
        self.status = WorkflowStatus.PENDING
        self.result = None
        self.error = None
    
    async def execute(self, context: Dict[str, Any]) -> bool:
        """Execute workflow step."""
        if self.condition and not await self.condition(context):
            logger.info(f"Skipping step {self.name} - condition not met")
            self.status = WorkflowStatus.COMPLETED
            return True
        
        self.status = WorkflowStatus.RUNNING
        
        for attempt in range(self.retry_count):
            try:
                self.result = await self.action(context)
                self.status = WorkflowStatus.COMPLETED
                logger.info(f"Step {self.name} completed successfully")
                return True
                
            except Exception as e:
                self.error = str(e)
                logger.error(f"Step {self.name} failed (attempt {attempt + 1}): {str(e)}")
                
                if attempt == self.retry_count - 1:
                    self.status = WorkflowStatus.FAILED
                    return False
                
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return False

class Workflow:
    """Workflow definition and execution."""
    
    def __init__(self, name: str, tenant_id: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.tenant_id = tenant_id
        self.steps: List[WorkflowStep] = []
        self.status = WorkflowStatus.PENDING
        self.context: Dict[str, Any] = {}
        self.created_at = datetime.utcnow()
        self.started_at = None
        self.completed_at = None
    
    def add_step(self, step: WorkflowStep):
        """Add step to workflow."""
        self.steps.append(step)
    
    async def execute(self, initial_context: Dict[str, Any] = None) -> bool:
        """Execute workflow."""
        if initial_context:
            self.context.update(initial_context)
        
        self.status = WorkflowStatus.RUNNING
        self.started_at = datetime.utcnow()
        
        logger.info(f"Starting workflow {self.name} ({self.id})")
        
        try:
            for step in self.steps:
                success = await step.execute(self.context)
                if not success:
                    self.status = WorkflowStatus.FAILED
                    logger.error(f"Workflow {self.name} failed at step {step.name}")
                    return False
                
                # Update context with step result
                if step.result:
                    self.context[f"{step.name}_result"] = step.result
            
            self.status = WorkflowStatus.COMPLETED
            self.completed_at = datetime.utcnow()
            logger.info(f"Workflow {self.name} completed successfully")
            return True
            
        except Exception as e:
            self.status = WorkflowStatus.FAILED
            logger.error(f"Workflow {self.name} failed: {str(e)}")
            return False

class WorkflowEngine:
    """Workflow engine for managing business processes."""
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.workflow_templates: Dict[str, Callable] = {}
        self._register_default_workflows()
    
    def register_workflow_template(self, name: str, template_func: Callable):
        """Register workflow template."""
        self.workflow_templates[name] = template_func
    
    async def create_workflow(
        self, 
        template_name: str, 
        tenant_id: str,
        context: Dict[str, Any] = None
    ) -> str:
        """Create workflow from template."""
        if template_name not in self.workflow_templates:
            raise ValueError(f"Unknown workflow template: {template_name}")
        
        workflow = self.workflow_templates[template_name](tenant_id, context or {})
        self.workflows[workflow.id] = workflow
        
        logger.info(f"Created workflow {workflow.name} ({workflow.id})")
        return workflow.id
    
    async def execute_workflow(self, workflow_id: str) -> bool:
        """Execute workflow by ID."""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        workflow = self.workflows[workflow_id]
        return await workflow.execute()
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow status."""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        workflow = self.workflows[workflow_id]
        return {
            "id": workflow.id,
            "name": workflow.name,
            "status": workflow.status.value,
            "created_at": workflow.created_at.isoformat(),
            "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
            "steps": [
                {
                    "name": step.name,
                    "status": step.status.value,
                    "error": step.error
                }
                for step in workflow.steps
            ]
        }
    
    def _register_default_workflows(self):
        """Register default workflow templates."""
        
        def invoice_approval_workflow(tenant_id: str, context: Dict[str, Any]) -> Workflow:
            """Invoice approval workflow."""
            workflow = Workflow("Invoice Approval", tenant_id)
            
            async def validate_invoice(ctx):
                # Validate invoice data
                return ctx.get("invoice_id") is not None
            
            async def send_approval_request(ctx):
                # Send approval notification
                await notification_service.send_notification(
                    "invoice_approval_request",
                    ctx.get("approver_email"),
                    {"invoice_number": ctx.get("invoice_number")}
                )
                return True
            
            async def check_approval_status(ctx):
                # Check if approved (mock implementation)
                return True
            
            async def finalize_invoice(ctx):
                # Finalize invoice
                return {"status": "approved"}
            
            workflow.add_step(WorkflowStep("validate", validate_invoice))
            workflow.add_step(WorkflowStep("request_approval", send_approval_request))
            workflow.add_step(WorkflowStep("check_approval", check_approval_status))
            workflow.add_step(WorkflowStep("finalize", finalize_invoice))
            
            return workflow
        
        def expense_approval_workflow(tenant_id: str, context: Dict[str, Any]) -> Workflow:
            """Expense approval workflow."""
            workflow = Workflow("Expense Approval", tenant_id)
            
            async def validate_expense(ctx):
                return ctx.get("expense_id") is not None
            
            async def check_amount_threshold(ctx):
                amount = ctx.get("amount", 0)
                return amount > 1000  # Require approval for amounts > $1000
            
            async def send_approval_request(ctx):
                await notification_service.send_notification(
                    "expense_approval_request",
                    ctx.get("manager_email"),
                    {"expense_id": ctx.get("expense_id"), "amount": ctx.get("amount")}
                )
                return True
            
            workflow.add_step(WorkflowStep("validate", validate_expense))
            workflow.add_step(WorkflowStep("request_approval", send_approval_request, check_amount_threshold))
            
            return workflow
        
        self.register_workflow_template("invoice_approval", invoice_approval_workflow)
        self.register_workflow_template("expense_approval", expense_approval_workflow)

# Global workflow engine instance
workflow_engine = WorkflowEngine()