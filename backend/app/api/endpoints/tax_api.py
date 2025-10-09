"""
Tax API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.tax_models import TaxRate, TaxTransaction, TaxExemption, TaxReturn
from app.services.tax_service import TaxService

router = APIRouter(prefix="/api/tax", tags=["tax"])

# Pydantic models
class TaxCalculationRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    tax_type: str
    jurisdiction: str
    country_code: str
    state_code: Optional[str] = None
    city: Optional[str] = None
    exemption_id: Optional[str] = None

class TaxCalculationResponse(BaseModel):
    taxable_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    tax_rate: Decimal
    tax_rate_id: Optional[str] = None
    tax_rate_name: Optional[str] = None
    exemption_applied: bool = False
    exemption_certificate: Optional[str] = None
    error: Optional[str] = None

class TaxRateCreate(BaseModel):
    name: str
    code: str
    rate: Decimal = Field(..., ge=0, le=100)
    tax_type: str
    jurisdiction: str
    country_code: str
    state_code: Optional[str] = None
    city: Optional[str] = None
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    description: Optional[str] = None

class TaxRateResponse(BaseModel):
    id: str
    name: str
    code: str
    rate: Decimal
    tax_type: str
    jurisdiction: str
    country_code: str
    state_code: Optional[str] = None
    city: Optional[str] = None
    effective_date: date
    expiry_date: Optional[date] = None
    status: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TaxTransactionResponse(BaseModel):
    id: str
    transaction_id: str
    entity_type: str
    entity_id: str
    taxable_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    transaction_date: date
    description: Optional[str] = None
    reference: Optional[str] = None
    tax_rate: TaxRateResponse
    created_at: datetime

    class Config:
        from_attributes = True

class TaxExemptionCreate(BaseModel):
    certificate_number: str
    entity_type: str
    entity_id: str
    exemption_type: str
    tax_types: List[str]
    jurisdiction: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    issuing_authority: Optional[str] = None
    notes: Optional[str] = None

class TaxExemptionResponse(BaseModel):
    id: str
    certificate_number: str
    entity_type: str
    entity_id: str
    exemption_type: str
    tax_types: List[str]
    jurisdiction: Optional[str] = None
    issue_date: date
    expiry_date: Optional[date] = None
    status: str
    issuing_authority: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# API Endpoints
@router.post("/calculate", response_model=TaxCalculationResponse)
async def calculate_tax(
    request: TaxCalculationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Calculate tax for a given amount and jurisdiction."""
    
    tax_service = TaxService(db)
    
    result = tax_service.calculate_tax(
        amount=request.amount,
        tax_type=request.tax_type,
        jurisdiction=request.jurisdiction,
        country_code=request.country_code,
        state_code=request.state_code,
        city=request.city,
        exemption_id=request.exemption_id
    )
    
    return TaxCalculationResponse(**result)

@router.get("/rates", response_model=List[TaxRateResponse])
async def get_tax_rates(
    tax_type: Optional[str] = None,
    jurisdiction: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get tax rates with optional filtering."""
    
    tax_service = TaxService(db)
    rates = tax_service.get_tax_rates(tax_type, jurisdiction, active_only)
    
    return [TaxRateResponse.from_orm(rate) for rate in rates]

@router.post("/rates", response_model=TaxRateResponse)
async def create_tax_rate(
    request: TaxRateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new tax rate."""
    
    # Check if code already exists
    existing = db.query(TaxRate).filter(TaxRate.code == request.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tax rate code already exists")
    
    tax_service = TaxService(db)
    
    rate = tax_service.create_tax_rate(
        name=request.name,
        code=request.code,
        rate=request.rate,
        tax_type=request.tax_type,
        jurisdiction=request.jurisdiction,
        country_code=request.country_code,
        state_code=request.state_code,
        city=request.city,
        effective_date=request.effective_date,
        expiry_date=request.expiry_date,
        description=request.description
    )
    
    return TaxRateResponse.from_orm(rate)

@router.get("/rates/{rate_id}", response_model=TaxRateResponse)
async def get_tax_rate(
    rate_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific tax rate."""
    
    rate = db.query(TaxRate).filter(TaxRate.id == rate_id).first()
    if not rate:
        raise HTTPException(status_code=404, detail="Tax rate not found")
    
    return TaxRateResponse.from_orm(rate)

@router.put("/rates/{rate_id}", response_model=TaxRateResponse)
async def update_tax_rate(
    rate_id: str,
    request: TaxRateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a tax rate."""
    
    rate = db.query(TaxRate).filter(TaxRate.id == rate_id).first()
    if not rate:
        raise HTTPException(status_code=404, detail="Tax rate not found")
    
    # Check if new code conflicts with existing
    if request.code != rate.code:
        existing = db.query(TaxRate).filter(TaxRate.code == request.code).first()
        if existing:
            raise HTTPException(status_code=400, detail="Tax rate code already exists")
    
    # Update fields
    rate.name = request.name
    rate.code = request.code
    rate.rate = request.rate
    rate.tax_type = request.tax_type
    rate.jurisdiction = request.jurisdiction
    rate.country_code = request.country_code
    rate.state_code = request.state_code
    rate.city = request.city
    rate.effective_date = request.effective_date or rate.effective_date
    rate.expiry_date = request.expiry_date
    rate.description = request.description
    rate.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(rate)
    
    return TaxRateResponse.from_orm(rate)

@router.delete("/rates/{rate_id}")
async def delete_tax_rate(
    rate_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a tax rate."""
    
    rate = db.query(TaxRate).filter(TaxRate.id == rate_id).first()
    if not rate:
        raise HTTPException(status_code=404, detail="Tax rate not found")
    
    # Check if rate is used in transactions
    transaction_count = db.query(TaxTransaction).filter(TaxTransaction.tax_rate_id == rate_id).count()
    if transaction_count > 0:
        # Soft delete - mark as inactive
        rate.status = "inactive"
        rate.updated_at = datetime.utcnow()
        db.commit()
        return {"message": "Tax rate deactivated (has associated transactions)"}
    else:
        # Hard delete
        db.delete(rate)
        db.commit()
        return {"message": "Tax rate deleted"}

@router.get("/transactions", response_model=List[TaxTransactionResponse])
async def get_tax_transactions(
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get tax transactions with optional filtering."""
    
    tax_service = TaxService(db)
    transactions = tax_service.get_tax_transactions(entity_type, entity_id, start_date, end_date)
    
    # Apply limit
    transactions = transactions[:limit]
    
    return [TaxTransactionResponse.from_orm(t) for t in transactions]

@router.post("/exemptions", response_model=TaxExemptionResponse)
async def create_tax_exemption(
    request: TaxExemptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a tax exemption certificate."""
    
    # Check if certificate number already exists
    existing = db.query(TaxExemption).filter(TaxExemption.certificate_number == request.certificate_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Certificate number already exists")
    
    tax_service = TaxService(db)
    
    exemption = tax_service.create_tax_exemption(
        certificate_number=request.certificate_number,
        entity_type=request.entity_type,
        entity_id=request.entity_id,
        exemption_type=request.exemption_type,
        tax_types=request.tax_types,
        jurisdiction=request.jurisdiction,
        issue_date=request.issue_date,
        expiry_date=request.expiry_date,
        issuing_authority=request.issuing_authority,
        notes=request.notes
    )
    
    return TaxExemptionResponse.from_orm(exemption)

@router.get("/exemptions", response_model=List[TaxExemptionResponse])
async def get_tax_exemptions(
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get tax exemptions with optional filtering."""
    
    query = db.query(TaxExemption)
    
    if entity_type:
        query = query.filter(TaxExemption.entity_type == entity_type)
    if entity_id:
        query = query.filter(TaxExemption.entity_id == entity_id)
    if active_only:
        query = query.filter(TaxExemption.status == "active")
    
    exemptions = query.all()
    
    return [TaxExemptionResponse.from_orm(e) for e in exemptions]

@router.get("/summary")
async def get_tax_summary(
    start_date: date,
    end_date: date,
    tax_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get tax summary for a period."""
    
    tax_service = TaxService(db)
    summary = tax_service.get_tax_summary(start_date, end_date, tax_type)
    
    return summary