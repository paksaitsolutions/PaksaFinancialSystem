"""
Paksa Financial System 
Financial Statement Template Service

This module provides services for managing financial statement templates.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

"""
Financial statement template service placeholder.
"""
from app.db.session import SessionLocal
=======
from app.core.db.session import SessionLocal
>>>>>>> e96df7278ce4216131b6c65d411c0723f4de7f91:backend/app/services/accounting/financial_statement_template_service.py
from app.exceptions import NotFoundException, ValidationException
from ..models.financial_statement_template import (
    FinancialStatementTemplate as TemplateModel,
    FinancialStatementLineTemplate as LineTemplateModel,
    TemplateType
)
from ..schemas.financial_statement_template import (
    FinancialStatementTemplateCreate,
    FinancialStatementTemplateUpdate,
    FinancialStatementTemplate,
    LineItemTemplateCreate,
    LineItemTemplate,
    TemplateStructure
)


class FinancialStatementTemplateService:
    """Service for managing financial statement templates."""
    
    def __init__(self, db: Session):
        """Initialize the service with a database session."""
        self.db = db
    
    def get_template(self, template_id: UUID) -> TemplateModel:
        """Retrieve a template by ID."""
        template = self.db.query(TemplateModel).get(template_id)
        if not template:
            raise NotFoundException(
                detail=f"Template with ID {template_id} not found"
            )
        return template
    
    def get_template_by_name(self, name: str, company_id: Optional[UUID] = None) -> Optional[TemplateModel]:
        """Retrieve a template by name and optionally company ID."""
        query = self.db.query(TemplateModel).filter(TemplateModel.name == name)
        
        if company_id:
            query = query.filter(TemplateModel.company_id == company_id)
        else:
            query = query.filter(TemplateModel.company_id.is_(None))
            
        return query.first()
    
    def list_templates(
        self, 
        skip: int = 0, 
        limit: int = 100,
        template_type: Optional[TemplateType] = None,
        company_id: Optional[UUID] = None,
        include_system: bool = False
    ) -> tuple[List[TemplateModel], int]:
        """List templates with optional filtering."""
        query = self.db.query(TemplateModel)
        
        if template_type:
            query = query.filter(TemplateModel.template_type == template_type)
            
        if company_id is not None:
            query = query.filter(TemplateModel.company_id == company_id)
            
        if not include_system:
            query = query.filter(TemplateModel.is_system.is_(False))
            
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        
        return items, total
    
    def create_template(self, template_data: FinancialStatementTemplateCreate, user_id: UUID) -> TemplateModel:
        """Create a new template."""
        # Check for duplicate name
        existing = self.get_template_by_name(template_data.name, template_data.company_id)
        if existing:
            raise ValidationException(
                detail=f"A template with name '{template_data.name}' already exists for this company"
            )
            
        # Create the template
        db_template = TemplateModel(
            **template_data.dict(exclude={"structure"}),
            created_by=user_id,
            updated_by=user_id
        )
        
        # Set structure
        db_template.structure = template_data.structure
        
        self.db.add(db_template)
        self.db.commit()
        self.db.refresh(db_template)
        
        return db_template
    
    def update_template(
        self, 
        template_id: UUID, 
        template_data: FinancialStatementTemplateUpdate,
        user_id: UUID
    ) -> TemplateModel:
        """Update an existing template."""
        db_template = self.get_template(template_id)
        
        # Check for duplicate name if name is being updated
        if template_data.name and template_data.name != db_template.name:
            existing = self.get_template_by_name(template_data.name, db_template.company_id)
            if existing and existing.id != template_id:
                raise ValidationException(
                    detail=f"A template with name '{template_data.name}' already exists for this company"
                )
        
        # Update fields
        update_data = template_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field != 'structure':
                setattr(db_template, field, value)
        
        # Update structure if provided
        if 'structure' in update_data:
            db_template.structure = update_data['structure']
        
        db_template.updated_by = user_id
        db_template.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_template)
        
        return db_template
    
    def delete_template(self, template_id: UUID) -> bool:
        """Delete a template."""
        db_template = self.get_template(template_id)
        
        if db_template.is_system:
            raise ValidationException(
                detail="System templates cannot be deleted"
            )
            
        # Check if template is in use
        # TODO: Add checks for template usage before allowing deletion
        
        self.db.delete(db_template)
        self.db.commit()
        return True
    
    def set_default_template(
        self, 
        template_id: UUID, 
        template_type: Optional[TemplateType] = None,
        company_id: Optional[UUID] = None
    ) -> TemplateModel:
        """Set a template as the default for its type and company."""
        # Get the template to be set as default
        db_template = self.get_template(template_id)
        
        # If template_type is not provided, use the template's type
        template_type = template_type or db_template.template_type
        
        # Reset existing default for this type and company
        self.db.query(TemplateModel).filter(
            TemplateModel.template_type == template_type,
            TemplateModel.company_id == company_id,
            TemplateModel.is_default.is_(True)
        ).update({"is_default": False})
        
        # Set new default
        db_template.is_default = True
        db_template.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_template)
        
        return db_template
    
    def get_default_template(
        self, 
        template_type: TemplateType,
        company_id: Optional[UUID] = None
    ) -> Optional[TemplateModel]:
        """Get the default template for a given type and company."""
        query = self.db.query(TemplateModel).filter(
            TemplateModel.template_type == template_type,
            TemplateModel.company_id == (company_id if company_id else None),
            TemplateModel.is_default.is_(True)
        )
        
        return query.first()
    
    def clone_template(
        self, 
        template_id: UUID, 
        new_name: str,
        user_id: UUID,
        company_id: Optional[UUID] = None
    ) -> TemplateModel:
        """Create a copy of an existing template."""
        source_template = self.get_template(template_id)
        
        # Check if new name is available
        if self.get_template_by_name(new_name, company_id):
            raise ValidationException(
                detail=f"A template with name '{new_name}' already exists for this company"
            )
        
        # Create a copy of the template
        template_data = {
            "name": new_name,
            "description": f"Copy of {source_template.name}",
            "template_type": source_template.template_type,
            "is_default": False,
            "is_system": False,
            "version": source_template.version,
            "structure": source_template.structure,
            "company_id": company_id or source_template.company_id,
            "created_by": user_id,
            "updated_by": user_id
        }
        
        db_template = TemplateModel(**template_data)
        self.db.add(db_template)
        self.db.commit()
        self.db.refresh(db_template)
        
        return db_template
    
    def validate_template_structure(self, structure: Dict[str, Any]) -> bool:
        """Validate a template structure."""
        # TODO: Implement comprehensive structure validation
        if not isinstance(structure, dict):
            raise ValidationException(detail="Template structure must be a JSON object")
            
        if 'sections' not in structure:
            raise ValidationException(detail="Template structure must contain 'sections' key")
            
        if not isinstance(structure['sections'], list):
            raise ValidationException(detail="'sections' must be a list")
            
        return True


def get_financial_statement_template_service():
    """Dependency function to get a FinancialStatementTemplateService instance."""
    db = SessionLocal()
    try:
        yield FinancialStatementTemplateService(db)
    finally:
        db.close()
