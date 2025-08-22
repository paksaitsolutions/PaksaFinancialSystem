<<<<<<< HEAD
# -*- coding: utf-8 -*-
"""
Paksa Financial System
----------------------
Version: 1.0
Author: Paksa IT Solutions
Copyright © 2023 Paksa IT Solutions

This file is part of the Paksa Financial System.
It is subject to the terms and conditions defined in
file 'LICENSE', which is part of this source code package.
"""

"""
Budget Module - Services
"""
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional, Dict, Any, Tuple
from datetime import date

from . import models, schemas
from .exceptions import BudgetNotFound, BudgetItemNotFound

class BudgetService:
    def __init__(self, db: Session):
        self.db = db

    def paksa_create_budget(self, budget: schemas.BudgetCreate, user_id: UUID) -> models.Budget:
        db_budget = models.Budget(**budget.dict(), created_by=user_id)
        self.db.add(db_budget)
        self.db.commit()
        self.db.refresh(db_budget)
        return db_budget

    def paksa_get_budget(self, budget_id: UUID) -> models.Budget:
        budget = self.db.query(models.Budget).filter(models.Budget.id == budget_id).first()
        if not budget:
            raise BudgetNotFound(f"Budget with id {budget_id} not found")
        return budget

    def paksa_list_budgets(self, skip: int = 0, limit: int = 100, **kwargs) -> Tuple[List[models.Budget], int]:
        query = self.db.query(models.Budget)
        if 'status' in kwargs and kwargs['status']:
            query = query.filter(models.Budget.status == kwargs['status'])
        if 'budget_type' in kwargs and kwargs['budget_type']:
            query = query.filter(models.Budget.budget_type == kwargs['budget_type'])
        if 'q' in kwargs and kwargs['q']:
            query = query.filter(models.Budget.name.ilike(f"%{kwargs['q']}%"))
        total = query.count()
        budgets = query.offset(skip).limit(limit).all()
        return budgets, total

    def paksa_update_budget(self, budget_id: UUID, budget_update: schemas.BudgetUpdate, user_id: UUID) -> models.Budget:
        db_budget = self.paksa_get_budget(budget_id)
        update_data = budget_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_budget, key, value)
        self.db.commit()
        self.db.refresh(db_budget)
        return db_budget

    def paksa_delete_budget(self, budget_id: UUID, user_id: UUID):
        db_budget = self.paksa_get_budget(budget_id)
        self.db.delete(db_budget)
        self.db.commit()

    def paksa_add_budget_item(self, budget_id: UUID, item: schemas.BudgetItemCreate, user_id: UUID) -> models.BudgetItem:
        self.paksa_get_budget(budget_id) # check if budget exists
        db_item = models.BudgetItem(**item.dict(), budget_id=budget_id)
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def paksa_get_budget_item(self, item_id: UUID) -> models.BudgetItem:
        item = self.db.query(models.BudgetItem).filter(models.BudgetItem.id == item_id).first()
        if not item:
            raise BudgetItemNotFound(f"Budget item with id {item_id} not found")
        return item

    def paksa_update_budget_item(self, item_id: UUID, item_update: schemas.BudgetItemUpdate, user_id: UUID) -> models.BudgetItem:
        db_item = self.paksa_get_budget_item(item_id)
        update_data = item_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_item, key, value)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def paksa_delete_budget_item(self, item_id: UUID, user_id: UUID):
        db_item = self.paksa_get_budget_item(item_id)
        self.db.delete(db_item)
        self.db.commit()

    def paksa_create_budget_adjustment(self, budget_id: UUID, adjustment: schemas.BudgetAdjustmentCreate, user_id: UUID) -> models.BudgetAdjustment:
        self.paksa_get_budget(budget_id)
        db_adjustment = models.BudgetAdjustment(**adjustment.dict(), budget_id=budget_id, created_by=user_id)
        self.db.add(db_adjustment)
        self.db.commit()
        self.db.refresh(db_adjustment)
        return db_adjustment

    def paksa_list_budget_adjustments(self, budget_id: UUID) -> List[models.BudgetAdjustment]:
        return self.db.query(models.BudgetAdjustment).filter(models.BudgetAdjustment.budget_id == budget_id).all()

    def paksa_record_transaction(self, transaction: schemas.BudgetTransactionCreate, user_id: UUID) -> models.BudgetTransaction:
        self.paksa_get_budget_item(transaction.item_id)
        db_transaction = models.BudgetTransaction(**transaction.dict())
        self.db.add(db_transaction)
        self.db.commit()
        self.db.refresh(db_transaction)
        return db_transaction

    def paksa_get_budget_summary(self, budget_id: UUID) -> Dict[str, Any]:
        return {"message": "Budget summary placeholder"}

    def paksa_generate_budget_vs_actual_report(self, **kwargs) -> List[Dict[str, Any]]:
        return [{"message": "Budget vs actual report placeholder"}]

    def paksa_generate_forecast_report(self, forecast_date: date, confidence_level: float, budget_id: Optional[UUID]) -> Dict[str, Any]:
        return {"message": "Forecast report placeholder"}

    def paksa_get_budget_overview_dashboard(self, time_frame: str) -> Dict[str, Any]:
        return {"message": "Overview dashboard placeholder"}

    def paksa_get_department_budget_dashboard(self, department_id: Optional[UUID], time_frame: str) -> Dict[str, Any]:
        return {"message": "Department dashboard placeholder"}

    def paksa_export_budget(self, budget_id: UUID, format: str, include_items: bool, include_transactions: bool) -> Any:
        return {"message": f"Exporting budget {budget_id} to {format}"}

    def paksa_bulk_create_budgets(self, budgets: List[schemas.BudgetCreate], user_id: UUID) -> Dict[str, Any]:
        return {"message": "Bulk create placeholder", "job_id": "temp_job_id"}

    def paksa_get_bulk_operation_status(self, job_id: str) -> Dict[str, Any]:
        return {"message": f"Status for job {job_id} placeholder"}

    def paksa_get_budget_audit_logs(self, budget_id: UUID, **kwargs) -> List[Dict[str, Any]]:
        return [{"message": "Audit logs placeholder"}]

    def paksa_validate_budget(self, budget_id: UUID) -> Dict[str, Any]:
        return {"message": f"Validation for budget {budget_id} placeholder"}

    def paksa_import_data(self, source: str, data: Dict[str, Any], user_id: UUID) -> Dict[str, Any]:
        return {"message": "Import data placeholder"}

    def paksa_export_for_integration(self, target_system: str, **kwargs) -> Dict[str, Any]:
        return {"message": "Export for integration placeholder"}

    def paksa_handle_webhook(self, webhook_id: str, payload: Dict[str, Any]):
        print(f"Webhook {webhook_id} received with payload: {payload}")

    def paksa_health_check(self) -> Dict[str, Any]:
        return {"status": "ok"}
=======
from typing import Optional
from decimal import Decimal
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.crud.base import CRUDBase
from .models import Budget, BudgetLineItem
from .schemas import BudgetCreate, BudgetUpdate, BudgetVsActual

class BudgetService(CRUDBase[Budget, BudgetCreate, BudgetUpdate]):
    def __init__(self):
        super().__init__(Budget)
    
    async def approve_budget(self, db: AsyncSession, budget_id: int, notes: str = None) -> Optional[Budget]:
        budget = await self.get(db, budget_id)
        if not budget:
            return None
        
        budget.status = "APPROVED"
        budget.approved_at = datetime.utcnow()
        budget.approval_notes = notes
        
        db.add(budget)
        await db.commit()
        await db.refresh(budget)
        return budget
    
    async def reject_budget(self, db: AsyncSession, budget_id: int, reason: str) -> Optional[Budget]:
        budget = await self.get(db, budget_id)
        if not budget:
            return None
        
        budget.status = "REJECTED"
        budget.rejected_at = datetime.utcnow()
        budget.rejection_reason = reason
        
        db.add(budget)
        await db.commit()
        await db.refresh(budget)
        return budget
    
    async def submit_for_approval(self, db: AsyncSession, budget_id: int) -> Optional[Budget]:
        budget = await self.get(db, budget_id)
        if not budget:
            return None
        
        budget.status = "PENDING_APPROVAL"
        budget.submitted_at = datetime.utcnow()
        
        db.add(budget)
        await db.commit()
        await db.refresh(budget)
        return budget
    
    async def get_budget_vs_actual(self, db: AsyncSession, budget_id: int, period: str) -> BudgetVsActual:
        budget = await self.get(db, budget_id)
        if not budget:
            raise ValueError("Budget not found")
        
        # Mock actual amounts - in real implementation, this would query actual transactions
        actual_amount = budget.amount * Decimal('0.85')  # 85% of budget
        variance = budget.amount - actual_amount
        variance_percent = (variance / budget.amount) * 100 if budget.amount > 0 else 0
        
        line_items = []
        for line_item in budget.line_items:
            actual_line_amount = line_item.amount * Decimal('0.85')
            line_variance = line_item.amount - actual_line_amount
            
            line_items.append({
                "category": line_item.category,
                "budgetAmount": float(line_item.amount),
                "actualAmount": float(actual_line_amount),
                "variance": float(line_variance)
            })
        
        return BudgetVsActual(
            budgetId=str(budget_id),
            period=period,
            budgetAmount=float(budget.amount),
            actualAmount=float(actual_amount),
            variance=float(variance),
            variancePercent=float(variance_percent),
            lineItems=line_items
        )
    
    async def create_version(self, db: AsyncSession, budget_id: int, version_data: dict, user_id: int):
        """Create a new budget version"""
        return {
            "version_id": 1,
            "budget_id": budget_id,
            "version_number": "v2.0",
            "created_by": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "changes": version_data.get("changes", [])
        }
    
    async def get_versions(self, db: AsyncSession, budget_id: int):
        """Get all versions of a budget"""
        return [
            {
                "version_id": 1,
                "version_number": "v1.0",
                "created_at": "2024-01-01T00:00:00",
                "status": "approved"
            },
            {
                "version_id": 2,
                "version_number": "v2.0",
                "created_at": "2024-01-15T00:00:00",
                "status": "draft"
            }
        ]
    
    async def consolidate_budgets(self, db: AsyncSession, budget_ids: list, consolidation_data: dict, user_id: int):
        """Consolidate multiple budgets"""
        return {
            "consolidated_budget_id": 1,
            "source_budgets": budget_ids,
            "total_amount": 500000.00,
            "created_by": user_id,
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def get_realtime_monitoring(self, db: AsyncSession, company_id: int):
        """Get real-time budget monitoring data"""
        return {
            "total_budgets": 15,
            "total_budget_amount": 2500000.00,
            "total_actual_amount": 1875000.00,
            "overall_variance": 625000.00,
            "variance_percentage": 25.0,
            "alerts_count": 3,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def get_budget_alerts(self, db: AsyncSession, company_id: int):
        """Get budget alerts"""
        return [
            {
                "alert_id": 1,
                "budget_id": 1,
                "type": "overspend",
                "message": "Budget exceeded by 15%",
                "severity": "high",
                "created_at": datetime.utcnow().isoformat()
            }
        ]
    
    async def create_alert(self, db: AsyncSession, alert_data: dict, user_id: int):
        """Create budget alert"""
        return {
            "alert_id": 1,
            "type": alert_data.get("type"),
            "threshold": alert_data.get("threshold"),
            "created_by": user_id,
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def get_variance_analysis(self, db: AsyncSession, budget_id: int, period: str, company_id: int):
        """Get detailed variance analysis"""
        return {
            "budget_id": budget_id,
            "period": period,
            "variance_summary": {
                "favorable_variance": 25000.00,
                "unfavorable_variance": 15000.00,
                "net_variance": 10000.00
            },
            "category_variances": [
                {
                    "category": "Marketing",
                    "budget": 50000.00,
                    "actual": 45000.00,
                    "variance": 5000.00,
                    "variance_type": "favorable"
                }
            ]
        }
>>>>>>> e96df7278ce4216131b6c65d411c0723f4de7f91
