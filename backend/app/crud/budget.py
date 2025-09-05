from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.budget import Budget, BudgetLineItem, BudgetApproval
from ..schemas.budget import BudgetCreate, BudgetUpdate, BudgetLineItemCreate
from decimal import Decimal

def get_budget(db: Session, budget_id: int) -> Optional[Budget]:
    return db.query(Budget).filter(Budget.id == budget_id).first()

def get_budgets(db: Session, skip: int = 0, limit: int = 100) -> List[Budget]:
    return db.query(Budget).offset(skip).limit(limit).all()

def create_budget(db: Session, budget: BudgetCreate) -> Budget:
    # Calculate total amount from line items
    total_amount = sum(item.budgeted_amount for item in budget.line_items)
    
    db_budget = Budget(
        name=budget.name,
        description=budget.description,
        fiscal_year=budget.fiscal_year,
        start_date=budget.start_date,
        end_date=budget.end_date,
        total_amount=total_amount
    )
    db.add(db_budget)
    db.flush()  # Get the ID
    
    # Create line items
    for item in budget.line_items:
        db_item = BudgetLineItem(
            budget_id=db_budget.id,
            account_code=item.account_code,
            account_name=item.account_name,
            category=item.category,
            budgeted_amount=item.budgeted_amount
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_budget)
    return db_budget

def update_budget(db: Session, budget_id: int, budget_update: BudgetUpdate) -> Optional[Budget]:
    db_budget = get_budget(db, budget_id)
    if not db_budget:
        return None
    
    update_data = budget_update.dict(exclude_unset=True)
    
    # Handle line items separately
    if "line_items" in update_data:
        line_items = update_data.pop("line_items")
        
        # Delete existing line items
        db.query(BudgetLineItem).filter(BudgetLineItem.budget_id == budget_id).delete()
        
        # Create new line items
        total_amount = Decimal(0)
        for item_data in line_items:
            db_item = BudgetLineItem(
                budget_id=budget_id,
                **item_data
            )
            db.add(db_item)
            total_amount += item_data["budgeted_amount"]
        
        update_data["total_amount"] = total_amount
    
    # Update budget fields
    for field, value in update_data.items():
        setattr(db_budget, field, value)
    
    db.commit()
    db.refresh(db_budget)
    return db_budget

def delete_budget(db: Session, budget_id: int) -> bool:
    db_budget = get_budget(db, budget_id)
    if db_budget:
        db.delete(db_budget)
        db.commit()
        return True
    return False

def get_budget_by_fiscal_year(db: Session, fiscal_year: int) -> List[Budget]:
    return db.query(Budget).filter(Budget.fiscal_year == fiscal_year).all()

def approve_budget(db: Session, budget_id: int, approver_id: int, status: str, comments: str = None) -> BudgetApproval:
    approval = BudgetApproval(
        budget_id=budget_id,
        approver_id=approver_id,
        status=status,
        comments=comments
    )
    db.add(approval)
    
    # Update budget status if approved
    if status == "approved":
        budget = get_budget(db, budget_id)
        if budget:
            budget.status = "active"
    
    db.commit()
    db.refresh(approval)
    return approval