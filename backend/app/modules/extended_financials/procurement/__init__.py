"""
Procurement Module

This module handles all procurement-related functionality including:
- Purchase Requisitions
- Purchase Orders
- Vendor Management
- Contract Management
- Spend Analysis
"""

from fastapi import APIRouter
from typing import List, Optional
from pydantic import BaseModel

# Import API router
from .api.router import api_router as procurement_router

# Import models to ensure they're registered with SQLAlchemy
from .models import purchase_requisition

# Import services
from .services import purchase_requisition_service

# Import schemas
from .schemas import purchase_requisition as purchase_requisition_schemas

# Re-export commonly used types for easier imports
PurchaseRequisitionCreate = purchase_requisition_schemas.PurchaseRequisitionCreate
PurchaseRequisitionUpdate = purchase_requisition_schemas.PurchaseRequisitionUpdate
PurchaseRequisitionResponse = purchase_requisition_schemas.PurchaseRequisitionResponse
RequisitionApproval = purchase_requisition_schemas.RequisitionApproval
RequisitionFilter = purchase_requisition_schemas.RequisitionFilter

# Initialize services
def get_purchase_requisition_service(db, current_user):
    """Factory function to get a PurchaseRequisitionService instance."""
    return purchase_requisition_service.PurchaseRequisitionService(db, current_user)

# Module metadata
MODULE_NAME = "procurement"
MODULE_DESCRIPTION = "Handles all procurement and purchasing operations"

# Export the router to be included in the main FastAPI app
router = APIRouter()
router.include_router(procurement_router, prefix="/procurement", tags=["procurement"])

# Export models for Alembic migrations
__all__ = [
    'purchase_requisition',
    'purchase_requisition_service',
    'purchase_requisition_schemas',
    'PurchaseRequisitionCreate',
    'PurchaseRequisitionUpdate',
    'PurchaseRequisitionResponse',
    'RequisitionApproval',
    'RequisitionFilter',
    'get_purchase_requisition_service',
    'router'
]
