"""
Approval Workflows API for financial transactions
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from typing import List, Dict, Any
from pydantic import BaseModel

router = APIRouter()

class ApprovalRequest(BaseModel):
    transaction_id: str
    transaction_type: str  # 'journal_entry', 'invoice', 'payment', 'budget'
    amount: float
    description: str
    requested_by: str

class ApprovalAction(BaseModel):
    action: str  # 'approve', 'reject', 'request_changes'
    comments: str = ""

@router.get("/pending")
async def get_pending_approvals(db: Session = Depends(get_db), user = Depends(get_current_user)):
    """Get all pending approval requests"""
    return [
        {
            "id": 1,
            "transaction_id": "JE-001",
            "transaction_type": "journal_entry",
            "amount": 5000.00,
            "description": "Monthly depreciation entry",
            "requested_by": "john.doe@company.com",
            "requested_date": "2024-01-15T10:30:00Z",
            "status": "pending",
            "priority": "normal"
        },
        {
            "id": 2,
            "transaction_id": "INV-001",
            "transaction_type": "invoice",
            "amount": 15000.00,
            "description": "Office supplies purchase",
            "requested_by": "jane.smith@company.com",
            "requested_date": "2024-01-15T09:15:00Z",
            "status": "pending",
            "priority": "high"
        }
    ]

@router.post("/request")
async def request_approval(request: ApprovalRequest, db: Session = Depends(get_db), user = Depends(get_current_user)):
    """Submit a new approval request"""
    return {
        "id": 3,
        "status": "submitted",
        "message": "Approval request submitted successfully",
        "approval_id": f"APR-{request.transaction_id}"
    }

@router.post("/{approval_id}/action")
async def process_approval(approval_id: int, action: ApprovalAction, db: Session = Depends(get_db), user = Depends(get_current_user)):
    """Process an approval request (approve/reject)"""
    return {
        "success": True,
        "action": action.action,
        "message": f"Approval {action.action}d successfully",
        "processed_by": user.get("email", "admin@paksa.com"),
        "processed_date": "2024-01-15T11:00:00Z"
    }

@router.get("/history")
async def get_approval_history(db: Session = Depends(get_db), user = Depends(get_current_user)):
    """Get approval history"""
    return [
        {
            "id": 1,
            "transaction_id": "JE-001",
            "action": "approved",
            "processed_by": "manager@company.com",
            "processed_date": "2024-01-14T15:30:00Z",
            "comments": "Approved - standard monthly entry"
        },
        {
            "id": 2,
            "transaction_id": "PAY-001",
            "action": "rejected",
            "processed_by": "cfo@company.com",
            "processed_date": "2024-01-13T11:20:00Z",
            "comments": "Rejected - insufficient documentation"
        }
    ]

@router.get("/settings")
async def get_approval_settings(db: Session = Depends(get_db), user = Depends(get_current_user)):
    """Get approval workflow settings"""
    return {
        "approval_limits": {
            "journal_entry": 10000,
            "invoice": 5000,
            "payment": 2500,
            "budget": 50000
        },
        "approvers": [
            {"role": "manager", "limit": 10000},
            {"role": "director", "limit": 50000},
            {"role": "cfo", "limit": 100000}
        ],
        "auto_approve_below": 1000,
        "require_dual_approval_above": 25000
    }