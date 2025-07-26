from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload
from typing import Optional
from datetime import datetime, date, timedelta
from decimal import Decimal
from ..enhanced_models import Budget, BudgetActual, BudgetAlert

class BudgetMonitoringService:
    """Service for budget monitoring and tracking"""
    
    async def get_realtime_budget_tracking(self, db: AsyncSession, budget_id: int):
        """Get real-time budget vs actual tracking"""
        # Get budget with actuals
        query = select(Budget).options(
            selectinload(Budget.actuals),
            selectinload(Budget.line_items)
        ).where(Budget.id == budget_id)
        
        result = await db.execute(query)
        budget = result.scalar_one_or_none()
        
        if not budget:
            return None
        
        # Calculate actual amounts
        total_actual = sum(float(actual.actual_amount) for actual in budget.actuals)
        total_budget = float(budget.total_amount)
        variance = total_budget - total_actual
        variance_percentage = (variance / total_budget) * 100 if total_budget > 0 else 0
        
        # Calculate utilization
        utilization_percentage = (total_actual / total_budget) * 100 if total_budget > 0 else 0
        
        return {
            "budget_id": budget_id,
            "budget_name": budget.name,
            "period": {
                "start_date": budget.start_date.isoformat(),
                "end_date": budget.end_date.isoformat()
            },
            "financial_summary": {
                "total_budget": total_budget,
                "total_actual": total_actual,
                "variance": variance,
                "variance_percentage": variance_percentage,
                "utilization_percentage": utilization_percentage
            },
            "status": "on_track" if abs(variance_percentage) <= 10 else "over_budget" if variance < 0 else "under_budget",
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def create_budget_alert(self, db: AsyncSession, alert_data: dict, user_id: int):
        """Create budget alert with real database persistence"""
        alert = BudgetAlert(
            budget_id=alert_data["budget_id"],
            alert_type=alert_data["alert_type"],
            severity=alert_data.get("severity", "medium"),
            title=alert_data["title"],
            message=alert_data["message"],
            threshold_percentage=Decimal(str(alert_data.get("threshold_percentage", 0))) if alert_data.get("threshold_percentage") else None,
            threshold_amount=Decimal(str(alert_data.get("threshold_amount", 0))) if alert_data.get("threshold_amount") else None,
            current_percentage=Decimal(str(alert_data.get("current_percentage", 0))) if alert_data.get("current_percentage") else None,
            current_amount=Decimal(str(alert_data.get("current_amount", 0))) if alert_data.get("current_amount") else None,
            is_active=True,
            recipients=alert_data.get("recipients", []),
            created_by=user_id
        )
        
        db.add(alert)
        await db.commit()
        await db.refresh(alert)
        
        return {
            "alert_id": alert.id,
            "budget_id": alert.budget_id,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "title": alert.title,
            "created_at": alert.created_at.isoformat()
        }
    
    async def get_budget_alerts(self, db: AsyncSession, budget_id: Optional[int] = None, active_only: bool = True):
        """Get budget alerts"""
        query = select(BudgetAlert).options(
            selectinload(BudgetAlert.budget)
        )
        
        if budget_id:
            query = query.where(BudgetAlert.budget_id == budget_id)
        if active_only:
            query = query.where(BudgetAlert.is_active == True)
        
        query = query.order_by(desc(BudgetAlert.created_at))
        
        result = await db.execute(query)
        alerts = result.scalars().all()
        
        return [
            {
                "alert_id": alert.id,
                "budget_id": alert.budget_id,
                "budget_name": alert.budget.name,
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "title": alert.title,
                "message": alert.message,
                "threshold_percentage": float(alert.threshold_percentage) if alert.threshold_percentage else None,
                "current_percentage": float(alert.current_percentage) if alert.current_percentage else None,
                "is_acknowledged": alert.is_acknowledged,
                "created_at": alert.created_at.isoformat()
            }
            for alert in alerts
        ]
    
    async def calculate_variance_analysis(self, db: AsyncSession, budget_id: int, period: str):
        """Calculate detailed variance analysis"""
        # Get budget with actuals and line items
        query = select(Budget).options(
            selectinload(Budget.actuals),
            selectinload(Budget.line_items)
        ).where(Budget.id == budget_id)
        
        result = await db.execute(query)
        budget = result.scalar_one_or_none()
        
        if not budget:
            return None
        
        # Calculate overall variance
        total_budget = float(budget.total_amount)
        total_actual = sum(float(actual.actual_amount) for actual in budget.actuals)
        total_variance = total_budget - total_actual
        
        # Categorize variances
        favorable_variance = max(0, total_variance)
        unfavorable_variance = abs(min(0, total_variance))
        
        # Calculate category-level variances
        category_variances = []
        category_actuals = {}
        
        # Group actuals by category (simplified - in real implementation would join with GL accounts)
        for actual in budget.actuals:
            category = "General"  # Simplified - would derive from GL account
            if category not in category_actuals:
                category_actuals[category] = 0
            category_actuals[category] += float(actual.actual_amount)
        
        # Compare with budget line items
        for line_item in budget.line_items:
            category = line_item.category
            budget_amount = float(line_item.budgeted_amount)
            actual_amount = category_actuals.get(category, 0)
            variance = budget_amount - actual_amount
            
            category_variances.append({
                "category": category,
                "budget": budget_amount,
                "actual": actual_amount,
                "variance": variance,
                "variance_percentage": (variance / budget_amount) * 100 if budget_amount > 0 else 0,
                "variance_type": "favorable" if variance >= 0 else "unfavorable"
            })
        
        return {
            "budget_id": budget_id,
            "period": period,
            "variance_summary": {
                "total_budget": total_budget,
                "total_actual": total_actual,
                "total_variance": total_variance,
                "favorable_variance": favorable_variance,
                "unfavorable_variance": unfavorable_variance,
                "variance_percentage": (total_variance / total_budget) * 100 if total_budget > 0 else 0
            },
            "category_variances": category_variances,
            "analysis_date": datetime.utcnow().isoformat()
        }
    
    async def create_budget_forecast(self, db: AsyncSession, budget_id: int, forecast_data: dict, user_id: int):
        """Create budget forecast based on current trends"""
        # Get budget with actuals
        query = select(Budget).options(
            selectinload(Budget.actuals)
        ).where(Budget.id == budget_id)
        
        result = await db.execute(query)
        budget = result.scalar_one_or_none()
        
        if not budget:
            return None
        
        # Calculate current run rate
        current_date = date.today()
        days_elapsed = (current_date - budget.start_date).days
        total_days = (budget.end_date - budget.start_date).days
        
        if days_elapsed <= 0:
            return {"error": "Budget period has not started"}
        
        # Calculate actual spend to date
        actual_to_date = sum(float(actual.actual_amount) for actual in budget.actuals)
        
        # Calculate run rate
        daily_run_rate = actual_to_date / days_elapsed if days_elapsed > 0 else 0
        remaining_days = total_days - days_elapsed
        
        # Forecast remaining spend
        forecasted_remaining = daily_run_rate * remaining_days
        total_forecasted = actual_to_date + forecasted_remaining
        
        # Calculate variance from budget
        budget_amount = float(budget.total_amount)
        forecasted_variance = budget_amount - total_forecasted
        
        return {
            "budget_id": budget_id,
            "forecast_date": current_date.isoformat(),
            "period_analysis": {
                "total_days": total_days,
                "days_elapsed": days_elapsed,
                "days_remaining": remaining_days,
                "period_completion_percentage": (days_elapsed / total_days) * 100
            },
            "financial_forecast": {
                "budget_amount": budget_amount,
                "actual_to_date": actual_to_date,
                "daily_run_rate": daily_run_rate,
                "forecasted_remaining": forecasted_remaining,
                "total_forecasted": total_forecasted,
                "forecasted_variance": forecasted_variance,
                "forecasted_variance_percentage": (forecasted_variance / budget_amount) * 100 if budget_amount > 0 else 0
            },
            "forecast_accuracy": "high" if days_elapsed >= 30 else "medium" if days_elapsed >= 14 else "low",
            "created_by": user_id,
            "created_at": datetime.utcnow().isoformat()
        }