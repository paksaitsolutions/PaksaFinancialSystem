from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from decimal import Decimal
from enum import Enum

class TaxTypeEnum(str, Enum):
    INCOME = "income"
    SALES = "sales"
    VAT = "vat"
    GST = "gst"
    PAYROLL = "payroll"
    PROPERTY = "property"
    EXCISE = "excise"

class JurisdictionLevel(str, Enum):
    COUNTRY = "country"
    STATE = "state"
    COUNTY = "county"
    CITY = "city"

class TaxJurisdictionBase(BaseModel):
    code: str = Field(..., max_length=10)
    name: str = Field(..., max_length=100)
    level: JurisdictionLevel
    parent_id: Optional[int] = None

class TaxJurisdictionCreate(TaxJurisdictionBase):
    pass

class TaxJurisdiction(TaxJurisdictionBase):
    id: int
    is_active: bool = True
    
    class Config:
        from_attributes = True

class TaxRateBase(BaseModel):
    name: str = Field(..., max_length=100)
    rate: Decimal = Field(..., ge=0, le=1)
    tax_type: TaxTypeEnum
    jurisdiction_id: int
    effective_date: date
    expiry_date: Optional[date] = None

class TaxRateCreate(TaxRateBase):
    pass

class TaxRate(TaxRateBase):
    id: int
    is_active: bool = True
    
    class Config:
        from_attributes = True

class TaxTransactionComponentBase(BaseModel):
    tax_component: str = Field(..., max_length=50)
    component_rate: Decimal = Field(..., ge=0)
    component_amount: Decimal = Field(..., ge=0)

class TaxTransactionComponentCreate(TaxTransactionComponentBase):
    pass

class TaxTransactionComponent(TaxTransactionComponentBase):
    id: int
    transaction_id: int
    
    class Config:
        from_attributes = True

class TaxTransactionBase(BaseModel):
    transaction_date: date
    document_number: str = Field(..., max_length=50)
    reference_number: Optional[str] = Field(None, max_length=50)
    tax_rate_id: int
    taxable_amount: Decimal = Field(..., ge=0)
    tax_amount: Decimal = Field(..., ge=0)
    total_amount: Decimal = Field(..., ge=0)
    status: str = Field(default="draft", max_length=20)

class TaxTransactionCreate(TaxTransactionBase):
    components: List[TaxTransactionComponentCreate] = []

class TaxTransaction(TaxTransactionBase):
    id: int
    components: List[TaxTransactionComponent] = []
    tax_rate: Optional[TaxRate] = None
    
    class Config:
        from_attributes = True

class TaxExemptionBase(BaseModel):
    exemption_type: str = Field(..., max_length=50)
    reason: str
    certificate_number: Optional[str] = Field(None, max_length=50)
    effective_date: date
    expiry_date: Optional[date] = None
    jurisdiction_id: Optional[int] = None

class TaxExemptionCreate(TaxExemptionBase):
    pass

class TaxExemption(TaxExemptionBase):
    id: int
    is_active: bool = True
    
    class Config:
        from_attributes = True

class TaxReturnBase(BaseModel):
    return_number: str = Field(..., max_length=50)
    tax_type: TaxTypeEnum
    period_start: date
    period_end: date
    filing_date: Optional[date] = None
    due_date: date
    status: str = Field(default="draft", max_length=20)
    total_tax_due: Decimal = Field(default=0, ge=0)

class TaxReturnCreate(TaxReturnBase):
    pass

class TaxReturn(TaxReturnBase):
    id: int
    is_active: bool = True
    
    class Config:
        from_attributes = True