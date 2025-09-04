"""
Workflow API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth_enhanced import get_current_user
from app.services.workflow_engine import *
from app.models.workflow import *
from typing import List, Dict, Optional
from datetime import datetime, date
from pydantic import BaseModel

router = APIRouter(prefix="/api/workflows", tags=["Workflows"])

class WorkflowCreateRequest(BaseModel):
    workflow_type: str
    entity_id: str
    amount: float
    priority: str = "normal"

class ApprovalRequest(BaseModel):
    action: str  # approved, rejected
    comments: Optional[str] = None

class DelegationRequest(BaseModel):
    to_user: str
    reason: str
    expires_at: Optional[datetime] = None

# Workflow Management
@router.post("/create")
async def create_workflow(
    request: WorkflowCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create new workflow instance"""
    try:
        workflow_id = WorkflowEngine.create_workflow(
            db, request.workflow_type, request.entity_id, 
            request.amount, current_user.id
        )
        return {"workflow_id": workflow_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{workflow_id}")
async def get_workflow(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get workflow details"""
    workflow = db.query(WorkflowInstance).filter(
        WorkflowInstance.id == workflow_id
    ).first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Get steps with approvals
    steps = []
    for step in workflow.steps:
        approvals = []
        for approval in step.approvals:
            approvals.append({
                "approver_id": approval.approver_id,
                "action": approval.action,
                "comments": approval.comments,
                "approved_at": approval.approved_at
            })
        
        steps.append({
            "step_number": step.step_number,
            "step_name": step.step_name,
            "status": step.status,
            "approver_role": step.approver_role,
            "approver_user": step.approver_user,
            "delegated_to": step.delegated_to,
            "due_date": step.due_date,
            "completed_at": step.completed_at,
            "approvals": approvals
        })
    
    return {
        "workflow_id": workflow.id,
        "workflow_type": workflow.workflow_type,
        "entity_id": workflow.entity_id,
        "status": workflow.status,
        "current_step": workflow.current_step,
        "total_steps": workflow.total_steps,
        "amount": workflow.amount,
        "created_by": workflow.created_by,
        "created_at": workflow.created_at,
        "completed_at": workflow.completed_at,
        "steps": steps
    }

@router.post("/{workflow_id}/steps/{step_number}/approve")
async def approve_step(
    workflow_id: str,
    step_number: int,
    request: ApprovalRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Approve or reject workflow step"""
    try:
        if request.action == "approved":
            result = WorkflowEngine.approve_step(
                db, workflow_id, step_number, current_user.id, request.comments
            )
        elif request.action == "rejected":
            result = WorkflowEngine.reject_step(
                db, workflow_id, step_number, current_user.id, request.comments
            )
        else:
            raise ValueError("Invalid action. Must be 'approved' or 'rejected'")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{workflow_id}/steps/{step_number}/delegate")
async def delegate_approval(
    workflow_id: str,
    step_number: int,
    request: DelegationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delegate approval to another user"""
    try:
        result = WorkflowEngine.delegate_approval(
            db, workflow_id, step_number, current_user.id, 
            request.to_user, request.reason
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Dashboard and Lists
@router.get("/pending/my-approvals")
async def get_my_pending_approvals(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get pending approvals for current user"""
    try:
        pending = WorkflowDashboard.get_pending_approvals(db, current_user.id)
        return {"pending_approvals": pending}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/my-workflows")
async def get_my_workflow_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get workflow history for current user"""
    try:
        history = WorkflowDashboard.get_workflow_history(db, current_user.id, limit)
        return {"workflow_history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_workflows(
    status: Optional[str] = None,
    workflow_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List workflows with filters"""
    try:
        query = db.query(WorkflowInstance)
        
        if status:
            query = query.filter(WorkflowInstance.status == status)
        
        if workflow_type:
            query = query.filter(WorkflowInstance.workflow_type == workflow_type)
        
        workflows = query.order_by(
            WorkflowInstance.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        result = []
        for workflow in workflows:
            result.append({
                "workflow_id": workflow.id,
                "workflow_type": workflow.workflow_type,
                "status": workflow.status,
                "amount": workflow.amount,
                "current_step": workflow.current_step,
                "total_steps": workflow.total_steps,
                "created_by": workflow.created_by,
                "created_at": workflow.created_at,
                "completed_at": workflow.completed_at
            })
        
        return {"workflows": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Approval Hierarchy
@router.get("/hierarchy/{workflow_type}")
async def get_approval_hierarchy(
    workflow_type: str,
    amount: float,
    department: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get approval hierarchy for workflow type and amount"""
    try:
        chain = ApprovalHierarchy.get_approval_chain(db, workflow_type, amount, department)
        return {"approval_chain": chain}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{workflow_id}/next-approver")
async def get_next_approver(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get next approver in workflow"""
    try:
        next_approver = ApprovalHierarchy.get_next_approver(db, workflow_id)
        return {"next_approver": next_approver}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Workflow Templates
@router.get("/templates")
async def list_workflow_templates(
    workflow_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List workflow templates"""
    try:
        query = db.query(WorkflowTemplate).filter(WorkflowTemplate.is_active == True)
        
        if workflow_type:
            query = query.filter(WorkflowTemplate.workflow_type == workflow_type)
        
        templates = query.all()
        
        result = []
        for template in templates:
            result.append({
                "template_id": template.id,
                "template_name": template.template_name,
                "workflow_type": template.workflow_type,
                "description": template.description,
                "is_default": template.is_default,
                "min_amount": template.min_amount,
                "max_amount": template.max_amount
            })
        
        return {"templates": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Workflow Comments
@router.post("/{workflow_id}/comments")
async def add_workflow_comment(
    workflow_id: str,
    comment: str,
    is_internal: bool = False,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Add comment to workflow"""
    try:
        workflow_comment = WorkflowComment(
            workflow_id=workflow_id,
            user_id=current_user.id,
            comment=comment,
            is_internal=is_internal
        )
        
        db.add(workflow_comment)
        db.commit()
        
        return {"message": "Comment added successfully", "comment_id": workflow_comment.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{workflow_id}/comments")
async def get_workflow_comments(
    workflow_id: str,
    include_internal: bool = False,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get workflow comments"""
    try:
        query = db.query(WorkflowComment).filter(
            WorkflowComment.workflow_id == workflow_id
        )
        
        if not include_internal:
            query = query.filter(WorkflowComment.is_internal == False)
        
        comments = query.order_by(WorkflowComment.created_at.desc()).all()
        
        result = []
        for comment in comments:
            result.append({
                "comment_id": comment.id,
                "user_id": comment.user_id,
                "comment": comment.comment,
                "is_internal": comment.is_internal,
                "created_at": comment.created_at
            })
        
        return {"comments": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Workflow Metrics
@router.get("/metrics/dashboard")
async def get_workflow_metrics(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get workflow metrics for dashboard"""
    try:
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        metrics = WorkflowDashboard.get_workflow_metrics(db, start_datetime, end_datetime)
        return {"metrics": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Bulk Operations
@router.post("/bulk/approve")
async def bulk_approve_workflows(
    workflow_ids: List[str],
    comments: Optional[str] = None,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Bulk approve multiple workflows"""
    try:
        results = []
        
        for workflow_id in workflow_ids:
            try:
                # Get current step
                workflow = db.query(WorkflowInstance).filter(
                    WorkflowInstance.id == workflow_id
                ).first()
                
                if workflow and workflow.status == 'pending':
                    result = WorkflowEngine.approve_step(
                        db, workflow_id, workflow.current_step, 
                        current_user.id, comments
                    )
                    results.append({"workflow_id": workflow_id, "status": "approved"})
                else:
                    results.append({"workflow_id": workflow_id, "status": "skipped", "reason": "not pending"})
            
            except Exception as e:
                results.append({"workflow_id": workflow_id, "status": "error", "error": str(e)})
        
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Workflow Statistics
@router.get("/stats/summary")
async def get_workflow_summary(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get workflow summary statistics"""
    try:
        total_pending = db.query(WorkflowInstance).filter(
            WorkflowInstance.status == 'pending'
        ).count()
        
        my_pending = len(WorkflowDashboard.get_pending_approvals(db, current_user.id))
        
        total_today = db.query(WorkflowInstance).filter(
            WorkflowInstance.created_at >= datetime.now().date()
        ).count()
        
        overdue_steps = db.query(WorkflowStep).filter(
            and_(
                WorkflowStep.status == 'pending',
                WorkflowStep.due_date < datetime.now()
            )
        ).count()
        
        return {
            "total_pending_workflows": total_pending,
            "my_pending_approvals": my_pending,
            "workflows_created_today": total_today,
            "overdue_steps": overdue_steps
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))