"""
Schemas for 1099 reporting API endpoints.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field, validator

from app.models.enums import Form1099Status, Form1099Type

class Form1099TransactionBase(BaseModel):
    """Base schema for 1099 transaction."""
    payment_id: UUID
    amount: Decimal = Field(ge=0)
    box_number: int = Field(ge=1, le=14)
    description: Optional[str] = None

class Form1099TransactionResponse(Form1099TransactionBase):
    """Schema for 1099 transaction response."""
    id: UUID
    form_1099_id: UUID

    class Config:
        orm_mode = True

class Form1099Base(BaseModel):
    """Base schema for 1099 form."""
    vendor_id: UUID
    tax_year: int = Field(ge=2000, le=2100)
    form_type: Form1099Type = Form1099Type.MISC
    
    # Box amounts
    box_1_rents: Decimal = Field(default=0, ge=0)
    box_2_royalties: Decimal = Field(default=0, ge=0)
    box_3_other_income: Decimal = Field(default=0, ge=0)
    box_4_federal_tax_withheld: Decimal = Field(default=0, ge=0)
    box_5_fishing_boat_proceeds: Decimal = Field(default=0, ge=0)
    box_6_medical_health_payments: Decimal = Field(default=0, ge=0)
    box_7_nonemployee_compensation: Decimal = Field(default=0, ge=0)
    box_8_substitute_payments: Decimal = Field(default=0, ge=0)
    box_9_payer_direct_sales: Decimal = Field(default=0, ge=0)
    box_10_crop_insurance: Decimal = Field(default=0, ge=0)
    box_11_state_tax_withheld: Decimal = Field(default=0, ge=0)
    box_12_state_payer_number: Optional[str] = None
    box_13_state_income: Decimal = Field(default=0, ge=0)
    box_14_gross_proceeds: Decimal = Field(default=0, ge=0)
    
    correction: bool = False
    void: bool = False
    notes: Optional[str] = None

class Form1099Create(Form1099Base):
    """Schema for creating a 1099 form."""
    pass

class Form1099Update(BaseModel):
    """Schema for updating a 1099 form."""
    form_type: Optional[Form1099Type] = None
    
    # Box amounts
    box_1_rents: Optional[Decimal] = Field(None, ge=0)
    box_2_royalties: Optional[Decimal] = Field(None, ge=0)
    box_3_other_income: Optional[Decimal] = Field(None, ge=0)
    box_4_federal_tax_withheld: Optional[Decimal] = Field(None, ge=0)
    box_5_fishing_boat_proceeds: Optional[Decimal] = Field(None, ge=0)
    box_6_medical_health_payments: Optional[Decimal] = Field(None, ge=0)
    box_7_nonemployee_compensation: Optional[Decimal] = Field(None, ge=0)
    box_8_substitute_payments: Optional[Decimal] = Field(None, ge=0)
    box_9_payer_direct_sales: Optional[Decimal] = Field(None, ge=0)
    box_10_crop_insurance: Optional[Decimal] = Field(None, ge=0)
    box_11_state_tax_withheld: Optional[Decimal] = Field(None, ge=0)
    box_12_state_payer_number: Optional[str] = None
    box_13_state_income: Optional[Decimal] = Field(None, ge=0)
    box_14_gross_proceeds: Optional[Decimal] = Field(None, ge=0)
    
    correction: Optional[bool] = None
    void: Optional[bool] = None
    notes: Optional[str] = None

class Form1099Response(Form1099Base):
    """Schema for 1099 form response."""
    id: UUID
    status: Form1099Status
    total_amount: Decimal
    filed_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    transactions: List[Form1099TransactionResponse] = []

    class Config:
        orm_mode = True

class Form1099ListResponse(BaseModel):
    """Schema for 1099 form list response."""
    items: List[Form1099Response]
    total: int
    page: int
    page_size: int
    pages: int

class Form1099GenerateRequest(BaseModel):
    """Schema for generating 1099 forms."""
    tax_year: int = Field(ge=2000, le=2100)
    vendor_ids: Optional[List[UUID]] = None
    minimum_amount: Decimal = Field(default=600, ge=0)

class Form1099SummaryResponse(BaseModel):
    """Schema for 1099 summary response."""
    tax_year: int
    total_forms: int
    total_amount: Decimal
    forms_by_status: Dict[str, int]
    forms_by_type: Dict[str, int]