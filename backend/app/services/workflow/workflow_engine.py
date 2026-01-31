"""
Workflow engine for business process automation.
"""
from datetime import datetime
from typing import Dict, Any, Optional, List

from uuid import uuid4

from app.core.logging import logger



class WorkflowEngine:
    """Simple workflow engine for business processes."""
    
    def __init__(self):
        self.workflows = {}
        self.templates = {
            "invoice_approval": {
                "steps": ["review", "approve", "process"],
                "description": "Invoice approval workflow"
            },
            "expense_approval": {
                "steps": ["submit", "manager_review", "finance_review", "approve"],
                "description": "Expense approval workflow"
            }
        }
    
    async def create_workflow(
        self, 
        template_name: str, 
        tenant_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create Workflow."""
        """Create workflow from template."""
        if template_name not in self.templates:
            raise ValueError(f"Unknown template: {template_name}")
        
        workflow_id = str(uuid4())
        template = self.templates[template_name]
        
        workflow = {
            "id": workflow_id,
            "template": template_name,
            "tenant_id": tenant_id,
            "status": "created",
            "current_step": 0,
            "steps": template["steps"],
            "context": context or {},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        self.workflows[workflow_id] = workflow
        logger.info(f"Created workflow {workflow_id} from template {template_name}")
        
        return workflow_id
    
    async def execute_workflow(self, workflow_id: str) -> bool:
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        workflow = self.workflows[workflow_id]
        
        if workflow["status"] == "completed":
            return True
        
        current_step = workflow["current_step"]
        steps = workflow["steps"]
        
        if current_step < len(steps):
            step_name = steps[current_step]
            logger.info(f"Executing step {step_name} for workflow {workflow_id}")
            
            # Simulate step execution
            workflow["current_step"] += 1
            workflow["updated_at"] = datetime.utcnow().isoformat()
            
            if workflow["current_step"] >= len(steps):
                workflow["status"] = "completed"
            else:
                workflow["status"] = "in_progress"
            
            return True
        
        return False
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        return self.workflows[workflow_id]
    
    async def list_workflows(self, tenant_id: str) -> List[Dict[str, Any]]:
        return [
            workflow for workflow in self.workflows.values()
            if workflow["tenant_id"] == tenant_id
        ]

workflow_engine = WorkflowEngine()