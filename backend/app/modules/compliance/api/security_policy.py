"""
Paksa Financial System - Security Policy API Endpoints
Version: 1.0.0
Copyright (c) 2025 Paksa IT Solutions. All rights reserved.

This software is the proprietary information of Paksa IT Solutions.
Use is subject to license terms and restrictions.

API endpoints for managing security policies and configurations.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ....core.security import get_current_active_admin
from ....db.session import get_db
from ....schemas.user import UserInDB
from .. import models, schemas, exceptions
from ..services import SecurityPolicyService, AuditService

# Create router with dependencies
router = APIRouter(
    dependencies=[Depends(get_current_active_admin)],
    responses={404: {"description": "Not found"}},
)

def paksa_get_security_policy_service(db: Session = Depends(get_db)) -> SecurityPolicyService:
    """Dependency to get an instance of SecurityPolicyService."""
    return SecurityPolicyService(db)

def paksa_get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    """Dependency to get an instance of AuditService."""
    return AuditService(db)

@router.get("/policies", response_model=List[schemas.SecurityPolicy])
async def paksa_list_security_policies(
    policy_type: Optional[models.PolicyType] = None,
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    policy_service: SecurityPolicyService = Depends(paksa_get_security_policy_service),
    current_user: UserInDB = Depends(get_current_active_admin)
):
    """
    List all security policies with optional filtering.
    
    Only accessible by administrators.
    """
    try:
        policies = policy_service.list_policies(
            policy_type=policy_type,
            is_active=is_active,
            skip=skip,
            limit=limit
        )
        return policies
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch security policies: {str(e)}"
        )

@router.post("/policies", response_model=schemas.SecurityPolicy, status_code=status.HTTP_201_CREATED)
async def paksa_create_security_policy(
    policy_data: schemas.SecurityPolicyCreate,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_admin)
):
    """
    Create a new security policy.
    
    Only accessible by administrators.
    """
    try:
        policy_service = SecurityPolicyService(db)
        audit_service = AuditService(db)
        
        # Create the policy
        policy = policy_service.create_policy(
            name=policy_data.name,
            description=policy_data.description,
            policy_type=policy_data.policy_type,
            config=policy_data.config,
            is_active=policy_data.is_active,
            created_by=current_user.id
        )
        
        # Log the policy creation
        audit_service.create_audit_log(
            action=models.AuditActionType.CREATE,
            resource_type="SecurityPolicy",
            resource_id=str(policy.id),
            user_id=current_user.id,
            username=current_user.username,
            details={
                "policy_name": policy.name,
                "policy_type": policy.policy_type.value,
                "is_active": policy.is_active
            }
        )
        
        return policy
        
    except exceptions.PolicyValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create security policy: {str(e)}"
        )

@router.get("/policies/{policy_id}", response_model=schemas.SecurityPolicy)
async def paksa_get_security_policy(
    policy_id: UUID,
    policy_service: SecurityPolicyService = Depends(paksa_get_security_policy_service),
    current_user: UserInDB = Depends(get_current_active_admin)
):
    """
    Retrieve a specific security policy by ID.
    
    Only accessible by administrators.
    """
    try:
        policy = policy_service.get_policy(policy_id)
        return policy
    except exceptions.PolicyNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch security policy: {str(e)}"
        )

@router.put("/policies/{policy_id}", response_model=schemas.SecurityPolicy)
async def paksa_update_security_policy(
    policy_id: UUID,
    policy_data: schemas.SecurityPolicyUpdate,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_admin)
):
    """
    Update an existing security policy.
    
    Only accessible by administrators.
    """
    try:
        policy_service = SecurityPolicyService(db)
        audit_service = AuditService(db)
        
        # Get the current policy to track changes
        current_policy = policy_service.get_policy(policy_id)
        
        # Update the policy
        updated_policy = policy_service.update_policy(
            policy_id=policy_id,
            name=policy_data.name,
            description=policy_data.description,
            config=policy_data.config,
            is_active=policy_data.is_active,
            updated_by=current_user.id
        )
        
        # Log the policy update
        changes = {}
        if policy_data.name and policy_data.name != current_policy.name:
            changes["name"] = policy_data.name
        if policy_data.is_active is not None and policy_data.is_active != current_policy.is_active:
            changes["is_active"] = policy_data.is_active
            
        audit_service.create_audit_log(
            action=models.AuditActionType.UPDATE,
            resource_type="SecurityPolicy",
            resource_id=str(policy_id),
            user_id=current_user.id,
            username=current_user.username,
            details={
                "changes": changes,
                "policy_type": current_policy.policy_type.value
            }
        )
        
        return updated_policy
        
    except exceptions.PolicyNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except exceptions.PolicyValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update security policy: {str(e)}"
        )

@router.delete("/policies/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def paksa_delete_security_policy(
    policy_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_admin)
):
    """
    Delete a security policy.
    
    Only accessible by administrators. System default policies cannot be deleted.
    """
    try:
        policy_service = SecurityPolicyService(db)
        audit_service = AuditService(db)
        
        # Get the policy to log details before deletion
        policy = policy_service.get_policy(policy_id)
        
        # Delete the policy
        policy_service.delete_policy(policy_id)
        
        # Log the policy deletion
        audit_service.create_audit_log(
            action=models.AuditActionType.DELETE,
            resource_type="SecurityPolicy",
            resource_id=str(policy_id),
            user_id=current_user.id,
            username=current_user.username,
            details={
                "policy_name": policy.name,
                "policy_type": policy.policy_type.value
            }
        )
        
        return None
        
    except exceptions.PolicyNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except exceptions.PolicyDeletionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete security policy: {str(e)}"
        )

@router.get("/policies/active/{policy_type}", response_model=schemas.SecurityPolicy)
async def paksa_get_active_policy_by_type(
    policy_type: models.PolicyType,
    policy_service: SecurityPolicyService = Depends(paksa_get_security_policy_service),
    current_user: UserInDB = Depends(get_current_active_admin)
):
    """
    Get the currently active policy for a specific policy type.
    
    Only accessible by administrators.
    """
    try:
        policy = policy_service.get_active_policy(policy_type)
        return policy
    except exceptions.PolicyNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch active {policy_type.value} policy: {str(e)}"
        )

@router.post("/policies/{policy_id}/activate", response_model=schemas.SecurityPolicy)
async def paksa_activate_policy(
    policy_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_admin)
):
    """
    Activate a security policy, deactivating any other active policy of the same type.
    
    Only accessible by administrators.
    """
    try:
        policy_service = SecurityPolicyService(db)
        audit_service = AuditService(db)
        
        # Activate the policy
        policy = policy_service.activate_policy(policy_id, current_user.id)
        
        # Log the policy activation
        audit_service.create_audit_log(
            action=models.AuditActionType.UPDATE,
            resource_type="SecurityPolicy",
            resource_id=str(policy_id),
            user_id=current_user.id,
            username=current_user.username,
            details={
                "action": "activated",
                "policy_name": policy.name,
                "policy_type": policy.policy_type.value
            }
        )
        
        return policy
        
    except exceptions.PolicyNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except exceptions.PolicyActivationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate security policy: {str(e)}"
        )

@router.get("/policies/types", response_model=List[Dict[str, Any]])
async def paksa_list_policy_types():
    """
    List all available security policy types with their descriptions.
    
    Accessible by any authenticated user.
    """
    return [
        {
            "type": policy_type.value,
            "name": policy_type.name.replace("_", " ").title(),
            "description": policy_type.get_description()
        }
        for policy_type in models.PolicyType
    ]
