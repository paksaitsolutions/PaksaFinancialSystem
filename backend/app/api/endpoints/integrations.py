"""
Integration API endpoints.
"""
from typing import Any, Dict
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.core.api_response import success_response, error_response
from app.core.permissions import require_permission, Permission
from app.integrations.banking.bank_api import plaid_client
from app.integrations.payments.payment_gateways import payment_manager
from app.integrations.tax.tax_services import tax_service
from app.services.notifications.notification_service import notification_service
from app.services.workflow.workflow_engine import workflow_engine

router = APIRouter()

MOCK_TENANT_ID = "12345678-1234-5678-9012-123456789012"

# Banking Integration
@router.post("/banking/link-token")
async def create_bank_link_token(
    *,
    user_id: str,
    _: bool = Depends(require_permission(Permission.WRITE))
) -> Any:
    """Create Plaid Link token for bank connection."""
    try:
        link_token = await plaid_client.create_link_token(user_id)
        return success_response(data={"link_token": link_token})
    except Exception as e:
        return error_response(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)

@router.post("/banking/exchange-token")
async def exchange_public_token(
    *,
    public_token: str,
    _: bool = Depends(require_permission(Permission.WRITE))
) -> Any:
    """Exchange public token for access token."""
    try:
        access_token = await plaid_client.exchange_public_token(public_token)
        return success_response(data={"access_token": access_token})
    except Exception as e:
        return error_response(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)

# Payment Integration
@router.post("/payments/create-intent")
async def create_payment_intent(
    *,
    gateway: str,
    amount: float,
    currency: str = "USD",
    _: bool = Depends(require_permission(Permission.WRITE))
) -> Any:
    """Create payment intent."""
    try:
        result = await payment_manager.process_payment(gateway, amount, currency)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)

# Tax Integration
@router.post("/tax/calculate")
async def calculate_tax(
    *,
    amount: float,
    tax_jurisdiction: str,
    item_type: str = "general",
    _: bool = Depends(require_permission(Permission.READ))
) -> Any:
    """Calculate tax using external service."""
    try:
        result = await tax_service.calculate_tax(
            amount, tax_jurisdiction, item_type
        )
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)

# Notification Integration
@router.post("/notifications/send")
async def send_notification(
    *,
    notification_type: str,
    recipient: str,
    subject: str,
    message: str,
    _: bool = Depends(require_permission(Permission.WRITE))
) -> Any:
    """Send notification."""
    try:
        success = await notification_service.send_notification(
            notification_type, recipient, subject, message
        )
        return success_response(data={"sent": success})
    except Exception as e:
        return error_response(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)

# Workflow Integration
@router.post("/workflows/create")
async def create_workflow(
    *,
    template_name: str,
    context: Dict[str, Any] = None,
    _: bool = Depends(require_permission(Permission.WRITE))
) -> Any:
    """Create workflow from template."""
    try:
        workflow_id = await workflow_engine.create_workflow(
            template_name, MOCK_TENANT_ID, context
        )
        return success_response(data={"workflow_id": workflow_id})
    except Exception as e:
        return error_response(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)

@router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(
    *,
    workflow_id: str,
    _: bool = Depends(require_permission(Permission.WRITE))
) -> Any:
    """Execute workflow."""
    try:
        success = await workflow_engine.execute_workflow(workflow_id)
        return success_response(data={"executed": success})
    except Exception as e:
        return error_response(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)

@router.get("/workflows/{workflow_id}/status")
async def get_workflow_status(
    *,
    workflow_id: str,
    _: bool = Depends(require_permission(Permission.READ))
) -> Any:
    """Get workflow status."""
    try:
        status_data = await workflow_engine.get_workflow_status(workflow_id)
        return success_response(data=status_data)
    except Exception as e:
        return error_response(message=str(e), status_code=status.HTTP_404_NOT_FOUND)