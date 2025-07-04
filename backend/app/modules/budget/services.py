"""
Budget Module - Services
"""
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID, uuid4

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, text, update

from app.modules.budget import models, schemas
from app.modules.accounting.models import GLAccount
from app.core.exceptions import NotFoundError, ValidationError
from app.core.database import Base

class BudgetService:
    """Service class for budget operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Budget Methods
    def create_budget(self, budget: schemas.BudgetCreate, user_id: UUID) -> models.Budget:
        """Create a new budget."""
        # Check if budget with same name already exists
        existing = self.db.query(models.Budget).filter(
            models.Budget.name == budget.name
        ).first()
        
        if existing:
            raise ValidationError(f"Budget with name '{budget.name}' already exists")
        
        # Create new budget
        db_budget = models.Budget(
            **budget.dict(exclude={"metadata"}),
            id=uuid4(),
            status=models.BudgetStatus.DRAFT,
            total_amount=0.0,
            actual_amount=0.0,
            variance=0.0,
            created_by=user_id,
            updated_by=user_id,
            metadata=budget.metadata or {}
        )
        
        self.db.add(db_budget)
        self.db.commit()
        self.db.refresh(db_budget)
        return db_budget
    
    def get_budget(self, budget_id: UUID) -> models.Budget:
        """Get a budget by ID."""
        budget = self.db.query(models.Budget).get(budget_id)
        if not budget:
            raise NotFoundError(f"Budget with ID {budget_id} not found")
        return budget
    
    def list_budgets(
        self,
        status: Optional[models.BudgetStatus] = None,
        budget_type: Optional[models.BudgetType] = None,
        department_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[models.Budget], int]:
        """List budgets with optional filtering."""
        query = self.db.query(models.Budget)
        
        if status is not None:
            query = query.filter(models.Budget.status == status)
        if budget_type is not None:
            query = query.filter(models.Budget.budget_type == budget_type)
        if department_id is not None:
            query = query.filter(models.Budget.department_id == department_id)
        if project_id is not None:
            query = query.filter(models.Budget.project_id == project_id)
        if start_date:
            query = query.filter(models.Budget.start_date >= start_date)
        if end_date:
            query = query.filter(models.Budget.end_date <= end_date)
        
        total = query.count()
        budgets = query.order_by(desc(models.Budget.start_date)).offset(skip).limit(limit).all()
        
        return budgets, total
    
    def update_budget(
        self, budget_id: UUID, budget_update: schemas.BudgetUpdate, user_id: UUID
    ) -> models.Budget:
        """Update a budget."""
        db_budget = self.get_budget(budget_id)
        
        # Check if budget is locked (approved or archived)
        if db_budget.status in [models.BudgetStatus.APPROVED, models.BudgetStatus.ARCHIVED]:
            raise ValidationError("Cannot modify an approved or archived budget")
        
        # Update fields
        update_data = budget_update.dict(exclude_unset=True)
        
        # Handle status changes
        if "status" in update_data and update_data["status"] != db_budget.status:
            new_status = update_data["status"]
            
            # Validate status transition
            valid_transitions = {
                models.BudgetStatus.DRAFT: [models.BudgetStatus.PENDING_APPROVAL],
                models.BudgetStatus.PENDING_APPROVAL: [
                    models.BudgetStatus.APPROVED,
                    models.BudgetStatus.REJECTED
                ],
                models.BudgetStatus.REJECTED: [models.BudgetStatus.DRAFT],
                models.BudgetStatus.APPROVED: [models.BudgetStatus.ARCHIVED]
            }
            
            current_status = db_budget.status
            if new_status not in valid_transitions.get(current_status, []):
                raise ValidationError(
                    f"Invalid status transition from {current_status} to {new_status}"
                )
            
            # Handle approval
            if new_status == models.BudgetStatus.APPROVED:
                update_data["approved_by"] = user_id
                update_data["approved_at"] = datetime.utcnow()
        
        # Update the budget
        for field, value in update_data.items():
            setattr(db_budget, field, value)
        
        db_budget.updated_by = user_id
        db_budget.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_budget)
        return db_budget
    
    def delete_budget(self, budget_id: UUID) -> None:
        """Delete a budget."""
        db_budget = self.get_budget(budget_id)
        
        # Check if budget is locked
        if db_budget.status in [models.BudgetStatus.APPROVED, models.BudgetStatus.ARCHIVED]:
            raise ValidationError("Cannot delete an approved or archived budget")
        
        # Check for existing transactions
        item_count = self.db.query(models.BudgetItem).filter(
            models.BudgetItem.budget_id == budget_id
        ).count()
        
        if item_count > 0:
            raise ValidationError(
                f"Cannot delete budget with {item_count} items. "
                "Remove all items before deleting the budget."
            )
        
        self.db.delete(db_budget)
        self.db.commit()
    
    # Budget Item Methods
    def add_budget_item(
        self, budget_id: UUID, item: schemas.BudgetItemCreate, user_id: UUID
    ) -> models.BudgetItem:
        """Add an item to a budget."""
        budget = self.get_budget(budget_id)
        
        # Check if budget is locked
        if budget.status in [models.BudgetStatus.APPROVED, models.BudgetStatus.ARCHIVED]:
            raise ValidationError("Cannot modify an approved or archived budget")
        
        # Check if GL account exists
        gl_account = self.db.query(GLAccount).get(item.gl_account_id)
        if not gl_account:
            raise NotFoundError(f"GL account with ID {item.gl_account_id} not found")
        
        # Check for duplicate GL account in budget
        existing = self.db.query(models.BudgetItem).filter(
            models.BudgetItem.budget_id == budget_id,
            models.BudgetItem.gl_account_id == item.gl_account_id
        ).first()
        
        if existing:
            raise ValidationError(
                f"GL account '{gl_account.name}' already exists in this budget"
            )
        
        # Create new budget item
        db_item = models.BudgetItem(
            id=uuid4(),
            budget_id=budget_id,
            gl_account_id=item.gl_account_id,
            amount=item.amount,
            actual_amount=0.0,
            variance=item.amount,  # Initially variance = budgeted amount (since actual is 0)
            notes=item.notes
        )
        
        # Update budget totals
        budget.total_amount += Decimal(str(item.amount))
        budget.variance = budget.total_amount - budget.actual_amount
        budget.updated_by = user_id
        budget.updated_at = datetime.utcnow()
        
        self.db.add(db_item)
        self.db.add(budget)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item
    
    def update_budget_item(
        self, item_id: UUID, item_update: schemas.BudgetItemUpdate, user_id: UUID
    ) -> models.BudgetItem:
        """Update a budget item."""
        db_item = self.db.query(models.BudgetItem).get(item_id)
        if not db_item:
            raise NotFoundError(f"Budget item with ID {item_id} not found")
        
        # Get the parent budget
        budget = self.get_budget(db_item.budget_id)
        
        # Check if budget is locked
        if budget.status in [models.BudgetStatus.APPROVED, models.BudgetStatus.ARCHIVED]:
            raise ValidationError("Cannot modify an approved or archived budget")
        
        # Update amount if provided
        if item_update.amount is not None:
            amount_diff = Decimal(str(item_update.amount)) - db_item.amount
            
            # Update budget totals
            budget.total_amount += amount_diff
            budget.variance = budget.total_amount - budget.actual_amount
            budget.updated_by = user_id
            budget.updated_at = datetime.utcnow()
            
            # Update item
            db_item.amount = item_update.amount
            db_item.variance = db_item.amount - db_item.actual_amount
        
        # Update notes if provided
        if item_update.notes is not None:
            db_item.notes = item_update.notes
        
        self.db.add_all([db_item, budget])
        self.db.commit()
        self.db.refresh(db_item)
        return db_item
    
    def delete_budget_item(self, item_id: UUID, user_id: UUID) -> None:
        """Delete a budget item."""
        db_item = self.db.query(models.BudgetItem).get(item_id)
        if not db_item:
            raise NotFoundError(f"Budget item with ID {item_id} not found")
        
        # Get the parent budget
        budget = self.get_budget(db_item.budget_id)
        
        # Check if budget is locked
        if budget.status in [models.BudgetStatus.APPROVED, models.BudgetStatus.ARCHIVED]:
            raise ValidationError("Cannot modify an approved or archived budget")
        
        # Update budget totals
        budget.total_amount -= db_item.amount
        budget.variance = budget.total_amount - budget.actual_amount
        budget.updated_by = user_id
        budget.updated_at = datetime.utcnow()
        
        # Delete the item
        self.db.delete(db_item)
        self.db.add(budget)
        self.db.commit()
    
    # Budget Adjustment Methods
    def adjust_budget(
        self, budget_id: UUID, adjustment: schemas.BudgetAdjustmentCreate, user_id: UUID
    ) -> models.BudgetAdjustment:
        """Adjust a budget amount."""
        budget = self.get_budget(budget_id)
        
        # Check if budget is approved
        if budget.status != models.BudgetStatus.APPROVED:
            raise ValidationError("Can only adjust an approved budget")
        
        # Create adjustment record
        db_adjustment = models.BudgetAdjustment(
            id=uuid4(),
            budget_id=budget_id,
            adjustment_date=adjustment.adjustment_date or date.today(),
            previous_amount=budget.total_amount,
            amount=adjustment.amount,
            reason=adjustment.reason,
            adjusted_by=user_id
        )
        
        # Update budget
        budget.total_amount = adjustment.amount
        budget.variance = budget.total_amount - budget.actual_amount
        budget.updated_by = user_id
        budget.updated_at = datetime.utcnow()
        
        self.db.add_all([db_adjustment, budget])
        self.db.commit()
        self.db.refresh(db_adjustment)
        return db_adjustment
    
    # Budget Transaction Methods
    def record_transaction(
        self, transaction: schemas.BudgetTransactionCreate, user_id: UUID
    ) -> models.BudgetTransaction:
        """Record a transaction against a budget item."""
        # Get the budget item
        item = self.db.query(models.BudgetItem).get(transaction.budget_item_id)
        if not item:
            raise NotFoundError(
                f"Budget item with ID {transaction.budget_item_id} not found"
            )
        
        # Get the parent budget
        budget = self.get_budget(item.budget_id)
        
        # Check if budget is approved
        if budget.status != models.BudgetStatus.APPROVED:
            raise ValidationError("Can only record transactions against an approved budget")
        
        # Create transaction
        db_transaction = models.BudgetTransaction(
            id=uuid4(),
            budget_item_id=item.id,
            transaction_date=transaction.transaction_date or date.today(),
            amount=transaction.amount,
            reference_type=transaction.reference_type,
            reference_id=transaction.reference_id,
            description=transaction.description
        )
        
        # Update item and budget totals
        item.actual_amount += transaction.amount
        item.variance = item.amount - item.actual_amount
        
        budget.actual_amount += transaction.amount
        budget.variance = budget.total_amount - budget.actual_amount
        budget.updated_by = user_id
        budget.updated_at = datetime.utcnow()
        
        self.db.add_all([db_transaction, item, budget])
        self.db.commit()
        self.db.refresh(db_transaction)
        return db_transaction
    
    # Reporting Methods
    def get_budget_summary(self, budget_id: UUID) -> Dict[str, Any]:
        """Get a summary of budget vs. actuals."""
        budget = self.get_budget(budget_id)
        
        # Get all items with their transactions
        items = self.db.query(models.BudgetItem).filter(
            models.BudgetItem.budget_id == budget_id
        ).options(
            joinedload(models.BudgetItem.transactions)
        ).all()
        
        # Calculate category totals
        categories = {}
        for item in items:
            category = item.gl_account.category
            if category not in categories:
                categories[category] = {
                    'budgeted': Decimal('0.0'),
                    'actual': Decimal('0.0'),
                    'variance': Decimal('0.0')
                }
            
            categories[category]['budgeted'] += item.amount
            categories[category]['actual'] += item.actual_amount
            categories[category]['variance'] += item.variance
        
        # Prepare response
        return {
            'budget': {
                'id': budget.id,
                'name': budget.name,
                'status': budget.status,
                'start_date': budget.start_date,
                'end_date': budget.end_date,
                'total_budget': budget.total_amount,
                'total_actual': budget.actual_amount,
                'total_variance': budget.variance,
                'utilization_percent': (
                    (budget.actual_amount / budget.total_amount * 100) 
                    if budget.total_amount > 0 else 0
                )
            },
            'categories': [
                {
                    'name': category,
                    'budgeted': float(data['budgeted']),
                    'actual': float(data['actual']),
                    'variance': float(data['variance']),
                    'utilization_percent': (
                        (data['actual'] / data['budgeted'] * 100) 
                        if data['budgeted'] > 0 else 0
                    )
                }
                for category, data in categories.items()
            ],
            'items': [
                {
                    'id': item.id,
                    'gl_account': {
                        'id': item.gl_account_id,
                        'code': item.gl_account.code,
                        'name': item.gl_account.name
                    },
                    'budgeted': float(item.amount),
                    'actual': float(item.actual_amount),
                    'variance': float(item.variance),
                    'utilization_percent': (
                        (item.actual_amount / item.amount * 100) 
                        if item.amount > 0 else 0
                    )
                }
                for item in items
            ]
        }
    
    def generate_budget_report(
        self, 
        start_date: date, 
        end_date: date,
        budget_type: Optional[models.BudgetType] = None,
        department_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Generate a budget vs. actual report for the given period."""
        # Base query for budgets that overlap with the report period
        query = self.db.query(models.Budget).filter(
            or_(
                and_(
                    models.Budget.start_date <= end_date,
                    models.Budget.end_date >= start_date
                ),
                and_(
                    models.Budget.start_date >= start_date,
                    models.Budget.end_date <= end_date
                )
            ),
            models.Budget.status == models.BudgetStatus.APPROVED
        )
        
        # Apply filters
        if budget_type:
            query = query.filter(models.Budget.budget_type == budget_type)
        if department_id:
            query = query.filter(models.Budget.department_id == department_id)
        
        budgets = query.all()
        
        # Calculate totals
        total_budget = sum(b.total_amount for b in budgets)
        total_actual = sum(b.actual_amount for b in budgets)
        total_variance = total_budget - total_actual
        
        return {
            'report_period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'filters': {
                'budget_type': budget_type,
                'department_id': department_id
            },
            'summary': {
                'total_budgets': len(budgets),
                'total_budget': float(total_budget),
                'total_actual': float(total_actual),
                'total_variance': float(total_variance),
                'utilization_percent': (
                    (total_actual / total_budget * 100) 
                    if total_budget > 0 else 0
                )
            },
            'budgets': [
                {
                    'id': b.id,
                    'name': b.name,
                    'type': b.budget_type,
                    'start_date': b.start_date,
                    'end_date': b.end_date,
                    'budgeted': float(b.total_amount),
                    'actual': float(b.actual_amount),
                    'variance': float(b.variance),
                    'utilization_percent': (
                        (b.actual_amount / b.total_amount * 100) 
                        if b.total_amount > 0 else 0
                    )
                }
                for b in budgets
            ]
        }
