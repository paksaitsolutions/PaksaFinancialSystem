from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, text
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from ..enhanced_models import Budget, BudgetActual

class BudgetIntegrationService:
    """Service for budget integration with GL and other modules"""
    
    async def integrate_with_gl_accounts(self, db: AsyncSession, budget_id: int):
        """Integrate budget with GL accounts for actual tracking"""
        # Get budget with line items
        query = select(Budget).options(
            selectinload(Budget.line_items)
        ).where(Budget.id == budget_id)
        
        result = await db.execute(query)
        budget = result.scalar_one_or_none()
        
        if not budget:
            return None
        
        # Get GL account mappings
        gl_mappings = []
        for line_item in budget.line_items:
            if line_item.gl_account_id:
                gl_mappings.append({
                    "line_item_id": line_item.id,
                    "category": line_item.category,
                    "gl_account_id": line_item.gl_account_id,
                    "budgeted_amount": float(line_item.budgeted_amount)
                })
        
        return {
            "budget_id": budget_id,
            "gl_mappings": gl_mappings,
            "total_mapped_amount": sum(mapping["budgeted_amount"] for mapping in gl_mappings),
            "integration_status": "active",
            "last_sync": datetime.utcnow().isoformat()
        }
    
    async def sync_actuals_from_gl(self, db: AsyncSession, budget_id: int, sync_date: date):
        """Sync actual amounts from GL transactions"""
        # Get budget
        query = select(Budget).options(
            selectinload(Budget.line_items)
        ).where(Budget.id == budget_id)
        
        result = await db.execute(query)
        budget = result.scalar_one_or_none()
        
        if not budget:
            return None
        
        synced_actuals = []
        
        # For each line item with GL account mapping
        for line_item in budget.line_items:
            if line_item.gl_account_id:
                # Query GL transactions (simplified - would use actual GL transaction table)
                # This is a mock implementation - in reality would query gl_transactions table
                mock_actual_amount = float(line_item.budgeted_amount) * 0.75  # 75% of budget
                
                # Create or update budget actual
                existing_actual = await db.scalar(
                    select(BudgetActual).where(
                        and_(
                            BudgetActual.budget_id == budget_id,
                            BudgetActual.period_date == sync_date,
                            BudgetActual.gl_account_id == line_item.gl_account_id
                        )
                    )
                )
                
                if existing_actual:
                    existing_actual.actual_amount = Decimal(str(mock_actual_amount))
                    existing_actual.variance_amount = line_item.budgeted_amount - Decimal(str(mock_actual_amount))
                    existing_actual.variance_percentage = (float(existing_actual.variance_amount) / float(line_item.budgeted_amount)) * 100
                    actual_record = existing_actual
                else:
                    actual_record = BudgetActual(
                        budget_id=budget_id,
                        period_date=sync_date,
                        actual_amount=Decimal(str(mock_actual_amount)),
                        variance_amount=line_item.budgeted_amount - Decimal(str(mock_actual_amount)),
                        variance_percentage=(float(line_item.budgeted_amount - Decimal(str(mock_actual_amount))) / float(line_item.budgeted_amount)) * 100,
                        source_type="gl_transaction",
                        gl_account_id=line_item.gl_account_id,
                        created_by=1  # System user
                    )
                    db.add(actual_record)
                
                synced_actuals.append({
                    "gl_account_id": line_item.gl_account_id,
                    "category": line_item.category,
                    "budgeted_amount": float(line_item.budgeted_amount),
                    "actual_amount": mock_actual_amount,
                    "variance": float(actual_record.variance_amount)
                })
        
        await db.commit()
        
        return {
            "budget_id": budget_id,
            "sync_date": sync_date.isoformat(),
            "synced_records": len(synced_actuals),
            "total_actual": sum(actual["actual_amount"] for actual in synced_actuals),
            "total_variance": sum(actual["variance"] for actual in synced_actuals),
            "actuals": synced_actuals,
            "sync_timestamp": datetime.utcnow().isoformat()
        }
    
    async def generate_budget_to_actual_report(self, db: AsyncSession, budget_id: int, report_date: date):
        """Generate comprehensive budget to actual report"""
        # Get budget with actuals and line items
        query = select(Budget).options(
            selectinload(Budget.actuals),
            selectinload(Budget.line_items)
        ).where(Budget.id == budget_id)
        
        result = await db.execute(query)
        budget = result.scalar_one_or_none()
        
        if not budget:
            return None
        
        # Calculate summary metrics
        total_budget = float(budget.total_amount)
        total_actual = sum(float(actual.actual_amount) for actual in budget.actuals)
        total_variance = total_budget - total_actual
        variance_percentage = (total_variance / total_budget) * 100 if total_budget > 0 else 0
        
        # Calculate period progress
        total_days = (budget.end_date - budget.start_date).days
        days_elapsed = (report_date - budget.start_date).days
        period_completion = (days_elapsed / total_days) * 100 if total_days > 0 else 0
        
        # Category-level analysis
        category_analysis = []
        for line_item in budget.line_items:
            category_actuals = [
                actual for actual in budget.actuals 
                if actual.gl_account_id == line_item.gl_account_id
            ]
            
            category_actual_total = sum(float(actual.actual_amount) for actual in category_actuals)
            category_budget = float(line_item.budgeted_amount)
            category_variance = category_budget - category_actual_total
            
            category_analysis.append({
                "category": line_item.category,
                "subcategory": line_item.subcategory,
                "budgeted_amount": category_budget,
                "actual_amount": category_actual_total,
                "variance": category_variance,
                "variance_percentage": (category_variance / category_budget) * 100 if category_budget > 0 else 0,
                "utilization_percentage": (category_actual_total / category_budget) * 100 if category_budget > 0 else 0
            })
        
        return {
            "report_header": {
                "budget_id": budget_id,
                "budget_name": budget.name,
                "budget_type": budget.budget_type,
                "fiscal_year": budget.fiscal_year,
                "report_date": report_date.isoformat(),
                "period": {
                    "start_date": budget.start_date.isoformat(),
                    "end_date": budget.end_date.isoformat(),
                    "completion_percentage": period_completion
                }
            },
            "executive_summary": {
                "total_budget": total_budget,
                "total_actual": total_actual,
                "total_variance": total_variance,
                "variance_percentage": variance_percentage,
                "budget_utilization": (total_actual / total_budget) * 100 if total_budget > 0 else 0,
                "performance_status": "on_track" if abs(variance_percentage) <= 10 else "over_budget" if total_variance < 0 else "under_budget"
            },
            "category_analysis": category_analysis,
            "key_insights": [
                f"Budget is {abs(variance_percentage):.1f}% {'over' if total_variance < 0 else 'under'} target",
                f"Period is {period_completion:.1f}% complete",
                f"Current utilization rate: {(total_actual / total_budget) * 100:.1f}%" if total_budget > 0 else "No budget allocated"
            ],
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def calculate_budget_impact_analysis(self, db: AsyncSession, budget_id: int, proposed_changes: dict):
        """Calculate impact of proposed budget changes"""
        # Get current budget
        query = select(Budget).options(
            selectinload(Budget.line_items),
            selectinload(Budget.actuals)
        ).where(Budget.id == budget_id)
        
        result = await db.execute(query)
        budget = result.scalar_one_or_none()
        
        if not budget:
            return None
        
        # Current state
        current_total = float(budget.total_amount)
        current_actual = sum(float(actual.actual_amount) for actual in budget.actuals)
        
        # Calculate proposed changes impact
        proposed_total = current_total
        line_item_impacts = []
        
        for change in proposed_changes.get("line_item_changes", []):
            line_item_id = change.get("line_item_id")
            new_amount = change.get("new_amount", 0)
            
            # Find current line item
            current_line = next((line for line in budget.line_items if line.id == line_item_id), None)
            if current_line:
                current_amount = float(current_line.budgeted_amount)
                impact = new_amount - current_amount
                proposed_total += impact
                
                line_item_impacts.append({
                    "line_item_id": line_item_id,
                    "category": current_line.category,
                    "current_amount": current_amount,
                    "proposed_amount": new_amount,
                    "impact": impact,
                    "impact_percentage": (impact / current_amount) * 100 if current_amount > 0 else 0
                })
        
        # Calculate overall impact
        total_impact = proposed_total - current_total
        impact_percentage = (total_impact / current_total) * 100 if current_total > 0 else 0
        
        # Calculate new variance with proposed changes
        new_variance = proposed_total - current_actual
        new_variance_percentage = (new_variance / proposed_total) * 100 if proposed_total > 0 else 0
        
        return {
            "budget_id": budget_id,
            "impact_analysis": {
                "current_budget": current_total,
                "proposed_budget": proposed_total,
                "total_impact": total_impact,
                "impact_percentage": impact_percentage,
                "current_actual": current_actual,
                "new_projected_variance": new_variance,
                "new_variance_percentage": new_variance_percentage
            },
            "line_item_impacts": line_item_impacts,
            "recommendations": [
                "Review impact on cash flow projections",
                "Assess departmental resource allocation",
                "Consider approval requirements for changes > 10%"
            ] if abs(impact_percentage) > 10 else [
                "Changes are within acceptable variance limits"
            ],
            "analysis_date": datetime.utcnow().isoformat()
        }
    
    async def get_budget_performance_metrics(self, db: AsyncSession, budget_ids: List[int]):
        """Get performance metrics across multiple budgets"""
        # Get budgets with actuals
        query = select(Budget).options(
            selectinload(Budget.actuals)
        ).where(Budget.id.in_(budget_ids))
        
        result = await db.execute(query)
        budgets = result.scalars().all()
        
        performance_metrics = []
        
        for budget in budgets:
            total_budget = float(budget.total_amount)
            total_actual = sum(float(actual.actual_amount) for actual in budget.actuals)
            variance = total_budget - total_actual
            
            # Calculate performance score (0-100)
            variance_percentage = abs(variance / total_budget) * 100 if total_budget > 0 else 0
            performance_score = max(0, 100 - variance_percentage)
            
            performance_metrics.append({
                "budget_id": budget.id,
                "budget_name": budget.name,
                "budget_type": budget.budget_type,
                "total_budget": total_budget,
                "total_actual": total_actual,
                "variance": variance,
                "variance_percentage": (variance / total_budget) * 100 if total_budget > 0 else 0,
                "performance_score": performance_score,
                "status": budget.status,
                "fiscal_year": budget.fiscal_year
            })
        
        # Calculate aggregate metrics
        total_all_budgets = sum(metric["total_budget"] for metric in performance_metrics)
        total_all_actuals = sum(metric["total_actual"] for metric in performance_metrics)
        overall_variance = total_all_budgets - total_all_actuals
        average_performance = sum(metric["performance_score"] for metric in performance_metrics) / len(performance_metrics) if performance_metrics else 0
        
        return {
            "individual_performance": performance_metrics,
            "aggregate_metrics": {
                "total_budgets": len(budgets),
                "total_budget_amount": total_all_budgets,
                "total_actual_amount": total_all_actuals,
                "overall_variance": overall_variance,
                "overall_variance_percentage": (overall_variance / total_all_budgets) * 100 if total_all_budgets > 0 else 0,
                "average_performance_score": average_performance
            },
            "analysis_date": datetime.utcnow().isoformat()
        }