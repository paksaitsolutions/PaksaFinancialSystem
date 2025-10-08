from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.crud.tax_return import tax_return_crud
from app.schemas.tax_return import TaxReturn, TaxReturnCreate, TaxReturnUpdate, TaxReturnStats

router = APIRouter()

@router.get("/", response_model=List[TaxReturn])
def read_tax_returns(
    skip: int = 0,
    limit: int = 100,
    tax_year: Optional[str] = None,
    return_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all tax returns with optional filtering"""
    tax_returns = tax_return_crud.get_multi(
        db=db, 
        skip=skip, 
        limit=limit,
        tax_year=tax_year,
        return_type=return_type,
        status=status
    )
    return tax_returns

@router.get("/stats", response_model=TaxReturnStats)
def get_tax_return_stats(db: Session = Depends(get_db)):
    """Get tax return statistics"""
    stats = tax_return_crud.get_stats(db=db)
    return stats

@router.get("/{tax_return_id}", response_model=TaxReturn)
def read_tax_return(tax_return_id: int, db: Session = Depends(get_db)):
    """Get a specific tax return by ID"""
    tax_return = tax_return_crud.get(db=db, id=tax_return_id)
    if not tax_return:
        raise HTTPException(status_code=404, detail="Tax return not found")
    return tax_return

@router.post("/", response_model=TaxReturn)
def create_tax_return(tax_return: TaxReturnCreate, db: Session = Depends(get_db)):
    """Create a new tax return"""
    # Check if return_id already exists
    existing = tax_return_crud.get_by_return_id(db=db, return_id=tax_return.return_id)
    if existing:
        raise HTTPException(status_code=400, detail="Return ID already exists")
    
    return tax_return_crud.create(db=db, obj_in=tax_return)

@router.put("/{tax_return_id}", response_model=TaxReturn)
def update_tax_return(
    tax_return_id: int, 
    tax_return: TaxReturnUpdate, 
    db: Session = Depends(get_db)
):
    """Update a tax return"""
    db_tax_return = tax_return_crud.get(db=db, id=tax_return_id)
    if not db_tax_return:
        raise HTTPException(status_code=404, detail="Tax return not found")
    
    return tax_return_crud.update(db=db, db_obj=db_tax_return, obj_in=tax_return)

@router.delete("/{tax_return_id}", response_model=TaxReturn)
def delete_tax_return(tax_return_id: int, db: Session = Depends(get_db)):
    """Delete a tax return"""
    tax_return = tax_return_crud.get(db=db, id=tax_return_id)
    if not tax_return:
        raise HTTPException(status_code=404, detail="Tax return not found")
    
    return tax_return_crud.remove(db=db, id=tax_return_id)

@router.post("/{tax_return_id}/file", response_model=TaxReturn)
def file_tax_return(tax_return_id: int, db: Session = Depends(get_db)):
    """File a tax return (change status to filed)"""
    db_tax_return = tax_return_crud.get(db=db, id=tax_return_id)
    if not db_tax_return:
        raise HTTPException(status_code=404, detail="Tax return not found")
    
    if db_tax_return.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft returns can be filed")
    
    from datetime import date
    update_data = TaxReturnUpdate(status="filed", filed_date=date.today())
    return tax_return_crud.update(db=db, db_obj=db_tax_return, obj_in=update_data)