# -*- coding: utf-8 -*-
"""
Paksa Financial System - Budget Services
---------------------------------------
Version: 1.0
Author: Paksa IT Solutions
Copyright © 2023 Paksa IT Solutions
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, date
from decimal import Decimal

from . import models, schemas


class BudgetService:
    def __init__(self, db: Session):
        self.db = db

    def create_budget(self, budget: schemas.BudgetCreate, user_id: int) -> models.Budget:
        """Create a new budget with line items."""
        db_budget = models.Budget(
            name=budget.name,
            amount=budget.amount,
            type=budget.type,
            status=budget.status,
            start_date=budget.start_date,
            end_date=budget.end_date,
            description=budget.description,
            created_by=user_id
        )
        
        self.db.add(db_budget)
        self.db.flush()  # Get the ID without committing
        
        # Add line items if provided
        if budget.line_items:
            for line_item_data in budget.line_items:
                line_item = models.BudgetLineItem(
                    budget_id=db_budget.id,
                    category=line_item_data.category,
                    description=line_item_data.description,
                    amount=line_item_data.amount
                )
                self.db.add(line_item)
        
        self.db.commit()
        self.db.refresh(db_budget)
        return db_budget

    def get_budget(self, budget_id: int) -> Optional[models.Budget]:
        """Get a budget by ID."""
        return self.db.query(models.Budget).filter(models.Budget.id == budget_id).first()

    def list_budgets(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,
        budget_type: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[models.Budget], int]:
        """List budgets with filtering and pagination."""
        query = self.db.query(models.Budget)
        
        # Apply filters
        if status:
            query = query.filter(models.Budget.status == status)
        
        if budget_type:
            query = query.filter(models.Budget.type == budget_type)
        
        if search:
            search_filter = or_(
                models.Budget.name.ilike(f"%{search}%"),
                models.Budget.description.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        budgets = query.order_by(models.Budget.created_at.desc()).offset(skip).limit(limit).all()
        
        return budgets, total

    def update_budget(
        self, 
        budget_id: int, 
        budget_update: schemas.BudgetUpdate, 
        user_id: int
    ) -> Optional[models.Budget]:
        """Update an existing budget."""
        db_budget = self.get_budget(budget_id)
        if not db_budget:
            return None
        
        # Update budget fields
        update_data = budget_update.dict(exclude_unset=True)
        line_items_data = update_data.pop('line_items', None)
        
        for field, value in update_data.items():
            setattr(db_budget, field, value)
        
        # Update line items if provided
        if line_items_data is not None:
            # Remove existing line items
            self.db.query(models.BudgetLineItem).filter(
                models.BudgetLineItem.budget_id == budget_id
            ).delete()
            
            # Add new line items
            for line_item_data in line_items_data:
                line_item = models.BudgetLineItem(
                    budget_id=budget_id,
                    category=line_item_data['category'],
                    description=line_item_data['description'],
                    amount=line_item_data['amount']
                )
                self.db.add(line_item)
        
        self.db.commit()
        self.db.refresh(db_budget)
        return db_budget

    def delete_budget(self, budget_id: int, user_id: int) -> bool:
        """Delete a budget."""
        db_budget = self.get_budget(budget_id)
        if not db_budget:
            return False
        
        self.db.delete(db_budget)
        self.db.commit()
        return True

    def submit_for_approval(self, budget_id: int, user_id: int) -> Optional[models.Budget]:
        """Submit a budget for approval."""
        db_budget = self.get_budget(budget_id)
        if not db_budget or db_budget.status != 'DRAFT':
            return None
        
        db_budget.status = 'PENDING_APPROVAL'
        db_budget.submitted_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_budget)
        return db_budget

    def approve_budget(
        self, 
        budget_id: int, 
        user_id: int, 
        notes: Optional[str] = None
    ) -> Optional[models.Budget]:
        """Approve a budget."""
        db_budget = self.get_budget(budget_id)
        if not db_budget or db_budget.status != 'PENDING_APPROVAL':
            return None
        
        db_budget.status = 'APPROVED'
        db_budget.approved_at = datetime.utcnow()
        db_budget.approval_notes = notes
        
        self.db.commit()
        self.db.refresh(db_budget)
        return db_budget

    def reject_budget(
        self, 
        budget_id: int, 
        user_id: int, 
        reason: str
    ) -> Optional[models.Budget]:
        """Reject a budget."""
        db_budget = self.get_budget(budget_id)
        if not db_budget or db_budget.status != 'PENDING_APPROVAL':
            return None
        
        db_budget.status = 'REJECTED'
        db_budget.rejected_at = datetime.utcnow()
        db_budget.rejection_reason = reason
        
        self.db.commit()
        self.db.refresh(db_budget)
        return db_budget

    def add_line_item(
        self, 
        budget_id: int, 
        line_item: schemas.BudgetLineItemCreate
    ) -> Optional[models.BudgetLineItem]:
        """Add a line item to a budget."""
        db_budget = self.get_budget(budget_id)
        if not db_budget:
            return None
        
        db_line_item = models.BudgetLineItem(
            budget_id=budget_id,
            category=line_item.category,
            description=line_item.description,
            amount=line_item.amount
        )
        
        self.db.add(db_line_item)
        self.db.commit()
        self.db.refresh(db_line_item)
        return db_line_item

    def update_line_item(
        self, 
        line_item_id: int, 
        line_item_update: schemas.BudgetLineItemCreate
    ) -> Optional[models.BudgetLineItem]:
        """Update a budget line item."""
        db_line_item = self.db.query(models.BudgetLineItem).filter(
            models.BudgetLineItem.id == line_item_id
        ).first()
        
        if not db_line_item:
            return None
        
        db_line_item.category = line_item_update.category
        db_line_item.description = line_item_update.description
        db_line_item.amount = line_item_update.amount
        
        self.db.commit()
        self.db.refresh(db_line_item)
        return db_line_item

    def delete_line_item(self, line_item_id: int) -> bool:
        """Delete a budget line item."""
        db_line_item = self.db.query(models.BudgetLineItem).filter(
            models.BudgetLineItem.id == line_item_id
        ).first()
        
        if not db_line_item:
            return False
        
        self.db.delete(db_line_item)
        self.db.commit()
        return True

    def get_budget_vs_actual(
        self, 
        budget_id: int, 
        period: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get budget vs actual comparison."""
        db_budget = self.get_budget(budget_id)
        if not db_budget:
            return None
        
        # This is a simplified implementation
        # In a real system, you would query actual spending data from GL or other modules
        line_items = []
        total_budget = 0
        total_actual = 0
        
        for line_item in db_budget.line_items:
            budget_amount = float(line_item.amount)
            # Simulate actual spending (in real implementation, query from GL)
            actual_amount = budget_amount * 0.75  # 75% spent as example
            variance = budget_amount - actual_amount
            
            line_items.append({
                "category": line_item.category,
                "budgetAmount": budget_amount,
                "actualAmount": actual_amount,
                "variance": variance
            })
            
            total_budget += budget_amount
            total_actual += actual_amount
        
        total_variance = total_budget - total_actual
        variance_percent = (total_variance / total_budget * 100) if total_budget > 0 else 0
        
        return {
            "budgetId": str(budget_id),
            "period": period or "current",
            "budgetAmount": total_budget,
            "actualAmount": total_actual,
            "variance": total_variance,
            "variancePercent": variance_percent,
            "lineItems": line_items
        }

    def get_budget_summary(self) -> Dict[str, Any]:
        """Get budget summary statistics."""
        total_budgets = self.db.query(models.Budget).count()
        
        # Get totals by status
        status_counts = {}
        for status in ['DRAFT', 'PENDING_APPROVAL', 'APPROVED', 'REJECTED', 'ARCHIVED']:
            count = self.db.query(models.Budget).filter(models.Budget.status == status).count()
            status_counts[status] = count
        
        # Get totals by type
        type_counts = {}
        for budget_type in ['OPERATIONAL', 'CAPITAL', 'PROJECT', 'DEPARTMENT']:
            count = self.db.query(models.Budget).filter(models.Budget.type == budget_type).count()
            type_counts[budget_type] = count
        
        # Calculate total amounts
        total_amount = self.db.query(models.Budget).with_entities(
            self.db.func.sum(models.Budget.amount)
        ).scalar() or 0
        
        return {
            "totalBudgets": total_budgets,
            "totalAmount": float(total_amount),
            "totalSpent": 0,  # Would come from actual spending data
            "totalRemaining": float(total_amount),
            "byStatus": status_counts,
            "byType": type_counts
        }