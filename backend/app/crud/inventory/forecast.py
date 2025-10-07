"""
CRUD operations for inventory forecasting.
"""
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import InventoryItem, InventoryTransaction
from app.schemas.inventory.forecast import DemandForecast, StockoutRisk, ForecastSummary

class InventoryForecastCRUD:
    """CRUD operations for inventory forecasting."""
    
    async def get_demand_forecast(
        self, 
        db: AsyncSession,
        *,
        days_history: int = 90,
        category_id: Optional[str] = None
    ) -> List[DemandForecast]:
        """Generate demand forecast for inventory items."""
        # Get items with transaction history
        query = select(InventoryItem).where(InventoryItem.is_tracked == True)
        if category_id:
            query = query.where(InventoryItem.category_id == category_id)
        
        result = await db.execute(query)
        items = result.scalars().all()
        
        forecasts = []
        cutoff_date = datetime.now().date() - timedelta(days=days_history)
        
        for item in items:
            # Calculate historical usage
            usage_query = select(
                func.sum(InventoryTransaction.quantity).label("total_usage")
            ).where(
                and_(
                    InventoryTransaction.item_id == item.id,
                    InventoryTransaction.transaction_type == "issue",
                    InventoryTransaction.transaction_date >= cutoff_date
                )
            )
            
            usage_result = await db.execute(usage_query)
            total_usage = usage_result.scalar() or 0
            
            # Calculate average daily usage
            avg_daily_usage = abs(total_usage) / days_history if total_usage else 0
            
            # Simple linear forecasting
            forecasted_30 = avg_daily_usage * 30
            forecasted_60 = avg_daily_usage * 60
            forecasted_90 = avg_daily_usage * 90
            
            # Calculate days until stockout
            days_until_stockout = None
            if avg_daily_usage > 0:
                days_until_stockout = int(item.quantity_on_hand / avg_daily_usage)
            
            # Calculate recommended order quantity (Economic Order Quantity simplified)
            recommended_qty = max(
                forecasted_30,  # At least 30 days supply
                item.reorder_quantity or 0
            )
            
            forecast = DemandForecast(
                item_id=item.id,
                sku=item.sku,
                name=item.name,
                current_stock=item.quantity_on_hand,
                average_daily_usage=avg_daily_usage,
                forecasted_demand_30_days=forecasted_30,
                forecasted_demand_60_days=forecasted_60,
                forecasted_demand_90_days=forecasted_90,
                days_until_stockout=days_until_stockout,
                recommended_order_quantity=recommended_qty,
                reorder_point=item.reorder_point
            )
            
            forecasts.append(forecast)
        
        return sorted(forecasts, key=lambda x: x.days_until_stockout or 999)
    
    async def get_stockout_risks(
        self, 
        db: AsyncSession,
        *,
        risk_threshold_days: int = 30
    ) -> List[StockoutRisk]:
        """Analyze stockout risks for inventory items."""
        forecasts = await self.get_demand_forecast(db)
        risks = []
        
        for forecast in forecasts:
            if forecast.days_until_stockout is None:
                continue
                
            days_remaining = forecast.days_until_stockout
            
            # Determine risk level
            if days_remaining <= 7:
                risk_level = "critical"
                action = "Order immediately"
            elif days_remaining <= 14:
                risk_level = "high"
                action = "Order within 3 days"
            elif days_remaining <= risk_threshold_days:
                risk_level = "medium"
                action = "Plan to order soon"
            else:
                risk_level = "low"
                action = "Monitor stock levels"
            
            # Only include items with medium or higher risk
            if risk_level in ["medium", "high", "critical"]:
                risk = StockoutRisk(
                    item_id=forecast.item_id,
                    sku=forecast.sku,
                    name=forecast.name,
                    current_stock=forecast.current_stock,
                    daily_usage=forecast.average_daily_usage,
                    days_remaining=days_remaining,
                    risk_level=risk_level,
                    recommended_action=action
                )
                risks.append(risk)
        
        return risks
    
    async def get_forecast_summary(self, db: AsyncSession) -> ForecastSummary:
        """Get forecast summary statistics."""
        forecasts = await self.get_demand_forecast(db)
        risks = await self.get_stockout_risks(db)
        
        items_requiring_reorder = len([
            f for f in forecasts 
            if f.current_stock <= f.reorder_point
        ])
        
        total_order_value = sum(
            f.recommended_order_quantity * Decimal("10")  # Simplified cost estimation
            for f in forecasts
            if f.current_stock <= f.reorder_point
        )
        
        return ForecastSummary(
            total_items_analyzed=len(forecasts),
            items_at_risk=len(risks),
            items_requiring_reorder=items_requiring_reorder,
            total_recommended_order_value=total_order_value,
            forecast_accuracy=0.85  # Placeholder accuracy metric
        )

# Create an instance for dependency injection
inventory_forecast_crud = InventoryForecastCRUD()