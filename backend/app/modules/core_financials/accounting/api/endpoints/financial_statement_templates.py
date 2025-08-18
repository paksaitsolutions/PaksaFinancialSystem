"""
Paksa Financial System 
Financial Statement Templates API Endpoints

This module defines the API endpoints for managing financial statement templates.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import Message, ResponseModel, ListResponse

from ...services.financial_statement_template_service import (
    FinancialStatementTemplateService,
    get_financial_statement_template_service
)
from ...schemas.financial_statement_template import (
    FinancialStatementTemplateCreate,
    FinancialStatementTemplateUpdate,
    FinancialStatementTemplate,
    TemplateType,
    FinancialStatementTemplateList
)

router = APIRouter()


@router.get(
    "/",
    response_model=ResponseModel[FinancialStatementTemplateList],
    status_code=status.HTTP_200_OK,
    summary="List financial statement templates",
    description="Retrieve a list of financial statement templates with optional filtering."
)
async def list_templates(
    template_type: Optional[TemplateType] = Query(
        None, 
        description="Filter by template type"
    ),
    company_id: Optional[UUID] = Query(
        None,
        description="Filter by company ID"
    ),
    include_system: bool = Query(
        False,
        description="Include system templates in the results"
    ),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    service: FinancialStatementTemplateService = Depends(get_financial_statement_template_service)
):
    """List financial statement templates with optional filtering."""
    templates, total = service.list_templates(
        skip=skip,
        limit=limit,
        template_type=template_type,
        company_id=company_id,
        include_system=include_system
    )
    
    return ResponseModel["list", FinancialStatementTemplateList](
        data=FinancialStatementTemplateList(
            items=templates,
            total=total,
            page=(skip // limit) + 1,
            pages=(total + limit - 1) // limit,
            size=len(templates)
        ),
        message="Templates retrieved successfully"
    )


@router.post(
    "/",
    response_model=ResponseModel[FinancialStatementTemplate],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new financial statement template",
    description="Create a new financial statement template with the provided data."
)
async def create_template(
    template_data: FinancialStatementTemplateCreate,
    current_user: User = Depends(get_current_active_user),
    service: FinancialStatementTemplateService = Depends(get_financial_statement_template_service)
):
    """Create a new financial statement template."""
    # Ensure user has permission to create templates for this company
    # TODO: Add proper permission checks based on company_id
    
    template = service.create_template(
        template_data=template_data,
        user_id=current_user.id
    )
    
    return ResponseModel["create", FinancialStatementTemplate](
        data=template,
        message="Template created successfully"
    )


@router.get(
    "/{template_id}",
    response_model=ResponseModel[FinancialStatementTemplate],
    status_code=status.HTTP_200_OK,
    summary="Get a financial statement template by ID",
    description="Retrieve a financial statement template by its unique identifier."
)
async def get_template(
    template_id: UUID,
    service: FinancialStatementTemplateService = Depends(get_financial_statement_template_service)
):
    """Get a financial statement template by ID."""
    template = service.get_template(template_id)
    return ResponseModel["read", FinancialStatementTemplate](
        data=template,
        message="Template retrieved successfully"
    )


@router.put(
    "/{template_id}",
    response_model=ResponseModel[FinancialStatementTemplate],
    status_code=status.HTTP_200_OK,
    summary="Update a financial statement template",
    description="Update an existing financial statement template with the provided data."
)
async def update_template(
    template_id: UUID,
    template_data: FinancialStatementTemplateUpdate,
    current_user: User = Depends(get_current_active_user),
    service: FinancialStatementTemplateService = Depends(get_financial_statement_template_service)
):
    """Update a financial statement template."""
    # TODO: Add permission checks
    
    template = service.update_template(
        template_id=template_id,
        template_data=template_data,
        user_id=current_user.id
    )
    
    return ResponseModel["update", FinancialStatementTemplate](
        data=template,
        message="Template updated successfully"
    )


@router.delete(
    "/{template_id}",
    response_model=ResponseModel[None],
    status_code=status.HTTP_200_OK,
    summary="Delete a financial statement template",
    description="Delete a financial statement template by its unique identifier."
)
async def delete_template(
    template_id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: FinancialStatementTemplateService = Depends(get_financial_statement_template_service)
):
    """Delete a financial statement template."""
    # TODO: Add permission checks
    
    success = service.delete_template(template_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete template"
        )
    
    return ResponseModel["delete", None](
        message="Template deleted successfully"
    )


@router.post(
    "/{template_id}/set-default",
    response_model=ResponseModel[FinancialStatementTemplate],
    status_code=status.HTTP_200_OK,
    summary="Set as default template",
    description="Set a template as the default for its type and company."
)
async def set_default_template(
    template_id: UUID,
    template_type: Optional[TemplateType] = None,
    company_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_active_user),
    service: FinancialStatementTemplateService = Depends(get_financial_statement_template_service)
):
    """Set a template as the default for its type and company."""
    # TODO: Add permission checks
    
    template = service.set_default_template(
        template_id=template_id,
        template_type=template_type,
        company_id=company_id
    )
    
    return ResponseModel["update", FinancialStatementTemplate](
        data=template,
        message="Default template set successfully"
    )


@router.get(
    "/default/{template_type}",
    response_model=ResponseModel[FinancialStatementTemplate],
    status_code=status.HTTP_200_OK,
    summary="Get default template by type",
    description="Get the default template for a given template type and company."
)
async def get_default_template(
    template_type: TemplateType,
    company_id: Optional[UUID] = None,
    service: FinancialStatementTemplateService = Depends(get_financial_statement_template_service)
):
    """Get the default template for a given type and company."""
    template = service.get_default_template(
        template_type=template_type,
        company_id=company_id
    )
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No default template found for type '{template_type}'"
        )
    
    return ResponseModel["read", FinancialStatementTemplate](
        data=template,
        message="Default template retrieved successfully"
    )


@router.post(
    "/{template_id}/clone",
    response_model=ResponseModel[FinancialStatementTemplate],
    status_code=status.HTTP_201_CREATED,
    summary="Clone a financial statement template",
    description="Create a copy of an existing financial statement template."
)
async def clone_template(
    template_id: UUID,
    new_name: str,
    company_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_active_user),
    service: FinancialStatementTemplateService = Depends(get_financial_statement_template_service)
):
    """Create a copy of an existing financial statement template."""
    # TODO: Add permission checks
    
    new_template = service.clone_template(
        template_id=template_id,
        new_name=new_name,
        user_id=current_user.id,
        company_id=company_id
    )
    
    return ResponseModel["create", FinancialStatementTemplate](
        data=new_template,
        message="Template cloned successfully"
    )
