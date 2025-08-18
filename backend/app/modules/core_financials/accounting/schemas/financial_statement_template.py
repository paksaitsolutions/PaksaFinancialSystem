"""
Paksa Financial System 
Financial Statement Template Schemas

This module defines the Pydantic schemas for financial statement templates.
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from uuid import UUID

from pydantic import BaseModel, Field, validator, HttpUrl, root_validator


class TemplateType(str, Enum):
    """Types of financial statement templates."""
    BALANCE_SHEET = "balance_sheet"
    INCOME_STATEMENT = "income_statement"
    CASH_FLOW = "cash_flow"
    CUSTOM = "custom"


class LineItemType(str, Enum):
    """Types of line items in a financial statement template."""
    HEADER = "header"
    ACCOUNT = "account"
    FORMULA = "formula"
    SUBTOTAL = "subtotal"
    TOTAL = "total"
    SPACER = "spacer"


class FinancialStatementTemplateBase(BaseModel):
    """Base schema for Financial Statement Templates."""
    name: str = Field(..., max_length=255, description="Name of the template")
    description: Optional[str] = Field(None, description="Description of the template")
    template_type: TemplateType = Field(..., description="Type of financial statement")
    is_default: bool = Field(False, description="Whether this is the default template for its type")
    is_system: bool = Field(False, description="Whether this is a system template")
    version: str = Field("1.0", description="Template version")
    
    class Config:
        orm_mode = True
        use_enum_values = True


class FinancialStatementTemplateCreate(FinancialStatementTemplateBase):
    """Schema for creating a new Financial Statement Template."""
    structure: Dict[str, Any] = Field(
        ..., 
        description="JSON structure defining the template layout"
    )
    
    @validator('structure')
    def validate_structure(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the template structure."""
        if not isinstance(v, dict):
            raise ValueError("Structure must be a JSON object")
            
        if 'sections' not in v:
            raise ValueError("Structure must contain 'sections' key")
            
        if not isinstance(v['sections'], list):
            raise ValueError("'sections' must be a list")
            
        return v


class FinancialStatementTemplateUpdate(BaseModel):
    """Schema for updating an existing Financial Statement Template."""
    name: Optional[str] = Field(None, max_length=255, description="Name of the template")
    description: Optional[str] = Field(None, description="Description of the template")
    is_default: Optional[bool] = Field(None, description="Whether this is the default template for its type")
    version: Optional[str] = Field(None, description="Template version")
    structure: Optional[Dict[str, Any]] = Field(
        None, 
        description="JSON structure defining the template layout"
    )
    
    class Config:
        orm_mode = True
        use_enum_values = True


class FinancialStatementTemplateInDB(FinancialStatementTemplateBase):
    """Schema for Financial Statement Template stored in the database."""
    id: UUID
    company_id: Optional[UUID] = Field(None, description="ID of the company this template belongs to")
    structure: Dict[str, Any] = Field(..., description="JSON structure defining the template layout")
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None


class FinancialStatementTemplate(FinancialStatementTemplateInDB):
    """Schema for returning Financial Statement Template data via API."""
    pass


class FinancialStatementTemplateList(BaseModel):
    """Schema for a list of Financial Statement Templates."""
    items: List[FinancialStatementTemplate]
    total: int
    page: int
    pages: int
    size: int


class LineItemTemplateBase(BaseModel):
    """Base schema for Line Item Templates."""
    name: str = Field(..., max_length=255, description="Name of the line item")
    code: Optional[str] = Field(None, max_length=50, description="Code for the line item")
    line_type: LineItemType = Field(..., description="Type of the line item")
    formula: Optional[str] = Field(None, description="Formula for calculated lines")
    account_code: Optional[str] = Field(None, description="Account code for account-based lines")
    sort_order: int = Field(0, description="Sort order within parent")
    level: int = Field(0, description="Indentation level")
    is_bold: bool = Field(False, description="Whether the text should be bold")
    is_italic: bool = Field(False, description="Whether the text should be italic")
    is_underline: bool = Field(False, description="Whether the text should be underlined")


class LineItemTemplateCreate(LineItemTemplateBase):
    """Schema for creating a new Line Item Template."""
    parent_id: Optional[UUID] = Field(None, description="ID of the parent line item")


class LineItemTemplateUpdate(BaseModel):
    """Schema for updating an existing Line Item Template."""
    name: Optional[str] = Field(None, max_length=255, description="Name of the line item")
    code: Optional[str] = Field(None, max_length=50, description="Code for the line item")
    line_type: Optional[LineItemType] = Field(None, description="Type of the line item")
    formula: Optional[str] = Field(None, description="Formula for calculated lines")
    account_code: Optional[str] = Field(None, description="Account code for account-based lines")
    sort_order: Optional[int] = Field(None, description="Sort order within parent")
    level: Optional[int] = Field(None, description="Indentation level")
    is_bold: Optional[bool] = Field(None, description="Whether the text should be bold")
    is_italic: Optional[bool] = Field(None, description="Whether the text should be italic")
    is_underline: Optional[bool] = Field(None, description="Whether the text should be underlined")
    parent_id: Optional[UUID] = Field(None, description="ID of the parent line item")


class LineItemTemplateInDB(LineItemTemplateBase):
    """Schema for Line Item Template stored in the database."""
    id: UUID
    template_id: UUID
    parent_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime


class LineItemTemplate(LineItemTemplateInDB):
    """Schema for returning Line Item Template data via API."""
    children: List["LineItemTemplate"] = []


# Update forward reference for recursive model
LineItemTemplate.update_forward_refs()


class TemplateStructureSection(BaseModel):
    """Schema for a section in a template structure."""
    id: str
    name: str
    code: Optional[str]
    line_items: List[Dict[str, Any]]
    sort_order: int = 0


class TemplateStructure(BaseModel):
    """Schema for the complete template structure."""
    sections: List[TemplateStructureSection]
    metadata: Dict[str, Any] = {}
    
    @validator('sections')
    def validate_sections(cls, v: List[TemplateStructureSection]) -> List[TemplateStructureSection]:
        """Ensure at least one section exists."""
        if not v:
            raise ValueError("At least one section is required")
        return v
