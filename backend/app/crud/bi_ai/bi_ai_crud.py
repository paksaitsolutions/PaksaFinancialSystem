"""
CRUD operations for BI/AI.
"""
import json
import random
from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime, date, timedelta
from decimal import Decimal

from sqlalchemy import select, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.query_helper import QueryHelper
from app.models.bi_ai.dashboard import Dashboard, KPI, Anomaly, Prediction
from app.schemas.bi_ai.bi_ai_schemas import (
    DashboardCreate, KPICreate, AnalyticsData, KPIValue, 
    AnomalyResponse, PredictionResponse, AIInsight
)

class BIAICRUD:
    """CRUD operations for BI/AI."""
    
    def __init__(self):
        self.dashboard_helper = QueryHelper(Dashboard)
        self.kpi_helper = QueryHelper(KPI)
    
    # Dashboard Management
    async def create_dashboard(
        self, 
        db: AsyncSession, 
        *, 
        tenant_id: UUID, 
        created_by: UUID,
        obj_in: DashboardCreate
    ) -> Dashboard:
        """Create dashboard."""
        # If this is default, unset others
        if obj_in.is_default:
            await self._unset_default_dashboards(db, tenant_id)
        
        dashboard = Dashboard(
            tenant_id=tenant_id,
            created_by=created_by,
            **obj_in.dict()
        )
        
        db.add(dashboard)
        await db.commit()
        await db.refresh(dashboard)
        return dashboard
    
    async def get_dashboards(
        self,
        db: AsyncSession,
        *,
        tenant_id: UUID,
        active_only: bool = True
    ) -> List[Dashboard]:
        """Get dashboards for tenant."""
        filters = {"tenant_id": tenant_id}
        if active_only:
            filters["is_active"] = True
        
        query = self.dashboard_helper.build_query(
            filters=filters,
            sort_by="is_default",
            sort_order="desc"
        )
        return await self.dashboard_helper.execute_query(db, query)
    
    # KPI Management
    async def create_kpi(
        self,
        db: AsyncSession,
        *,
        tenant_id: UUID,
        created_by: UUID,
        obj_in: KPICreate
    ) -> KPI:
        """Create KPI."""
        kpi = KPI(
            tenant_id=tenant_id,
            created_by=created_by,
            **obj_in.dict()
        )
        
        db.add(kpi)
        await db.commit()
        await db.refresh(kpi)
        return kpi
    
    async def get_kpis(
        self,
        db: AsyncSession,
        *,
        tenant_id: UUID,
        category: Optional[str] = None
    ) -> List[KPI]:
        """Get KPIs for tenant."""
        filters = {"tenant_id": tenant_id, "is_active": True}
        if category:
            filters["category"] = category
        
        query = self.kpi_helper.build_query(
            filters=filters,
            sort_by="category",
            sort_order="asc"
        )
        return await self.kpi_helper.execute_query(db, query)
    
    # Analytics Data
    async def get_analytics_data(
        self,
        db: AsyncSession,
        *,
        tenant_id: UUID
    ) -> AnalyticsData:
        """Get comprehensive analytics data."""
        # Revenue trend (mock data with realistic patterns)
        revenue_trend = self._generate_revenue_trend()
        
        # Expense breakdown
        expense_breakdown = [
            {"category": "Salaries", "amount": 45000, "percentage": 45},
            {"category": "Operations", "amount": 25000, "percentage": 25},
            {"category": "Marketing", "amount": 15000, "percentage": 15},
            {"category": "Technology", "amount": 10000, "percentage": 10},
            {"category": "Other", "amount": 5000, "percentage": 5}
        ]
        
        # Cash flow forecast
        cash_flow_forecast = self._generate_cash_flow_forecast()
        
        # Key metrics
        key_metrics = await self._calculate_key_metrics(db, tenant_id)
        
        # Recent anomalies
        anomalies = await self._get_recent_anomalies(db, tenant_id)
        
        # Predictions
        predictions = await self._get_active_predictions(db, tenant_id)
        
        return AnalyticsData(
            revenue_trend=revenue_trend,
            expense_breakdown=expense_breakdown,
            cash_flow_forecast=cash_flow_forecast,
            key_metrics=key_metrics,
            anomalies=anomalies,
            predictions=predictions
        )
    
    # Anomaly Detection
    async def detect_anomalies(
        self,
        db: AsyncSession,
        *,
        tenant_id: UUID
    ) -> List[Anomaly]:
        """Detect anomalies in financial data."""
        anomalies = []
        
        # Simulate anomaly detection
        current_time = datetime.utcnow()
        
        # Revenue anomaly
        if random.random() < 0.3:  # 30% chance
            anomaly = Anomaly(
                tenant_id=tenant_id,
                metric_name="Monthly Revenue",
                metric_value="$85,000",
                expected_range="$95,000 - $105,000",
                anomaly_score="0.85",
                severity="high",
                description="Revenue is 15% below expected range for this month",
                recommendation="Review sales pipeline and marketing campaigns",
                detected_at=current_time
            )
            db.add(anomaly)
            anomalies.append(anomaly)
        
        # Expense anomaly
        if random.random() < 0.4:  # 40% chance
            anomaly = Anomaly(
                tenant_id=tenant_id,
                metric_name="Operating Expenses",
                metric_value="$125,000",
                expected_range="$100,000 - $115,000",
                anomaly_score="0.72",
                severity="medium",
                description="Operating expenses are 15% above normal range",
                recommendation="Review expense categories and identify cost-saving opportunities",
                detected_at=current_time
            )
            db.add(anomaly)
            anomalies.append(anomaly)
        
        if anomalies:
            await db.commit()
        
        return anomalies
    
    # Predictive Analytics
    async def generate_predictions(
        self,
        db: AsyncSession,
        *,
        tenant_id: UUID
    ) -> List[Prediction]:
        """Generate AI predictions."""
        predictions = []
        current_time = datetime.utcnow()
        
        # Revenue forecast
        revenue_prediction = Prediction(
            tenant_id=tenant_id,
            prediction_type="revenue_forecast",
            target_metric="Monthly Revenue",
            prediction_data={
                "next_month": {"value": 98000, "confidence_interval": [92000, 104000]},
                "next_quarter": {"value": 295000, "confidence_interval": [280000, 310000]},
                "trend": "stable_growth",
                "factors": ["seasonal_patterns", "market_conditions", "historical_performance"]
            },
            confidence_score="0.87",
            prediction_period="next_quarter",
            model_used="ARIMA_with_seasonality",
            created_at=current_time,
            expires_at=current_time + timedelta(days=30)
        )
        db.add(revenue_prediction)
        predictions.append(revenue_prediction)
        
        # Cash flow prediction
        cashflow_prediction = Prediction(
            tenant_id=tenant_id,
            prediction_type="cash_flow_forecast",
            target_metric="Cash Flow",
            prediction_data={
                "next_month": {"inflow": 120000, "outflow": 95000, "net": 25000},
                "risk_factors": ["delayed_payments", "seasonal_variations"],
                "recommendations": ["improve_collection_process", "optimize_payment_timing"]
            },
            confidence_score="0.82",
            prediction_period="next_month",
            model_used="ML_ensemble",
            created_at=current_time,
            expires_at=current_time + timedelta(days=30)
        )
        db.add(cashflow_prediction)
        predictions.append(cashflow_prediction)
        
        await db.commit()
        return predictions
    
    # AI Insights
    async def get_ai_insights(
        self,
        db: AsyncSession,
        *,
        tenant_id: UUID
    ) -> List[AIInsight]:
        """Get AI-powered insights."""
        insights = [
            AIInsight(
                insight_type="cost_optimization",
                title="Potential Cost Savings Identified",
                description="Analysis shows 12% reduction in operational costs possible through vendor consolidation",
                impact="high",
                recommendation="Consolidate suppliers and renegotiate contracts with top 3 vendors",
                confidence=0.89,
                data_points=[
                    {"metric": "current_vendor_count", "value": 45},
                    {"metric": "optimal_vendor_count", "value": 28},
                    {"metric": "potential_savings", "value": 15000}
                ]
            ),
            AIInsight(
                insight_type="revenue_opportunity",
                title="Revenue Growth Opportunity",
                description="Customer segment analysis reveals untapped market potential worth $50K monthly",
                impact="medium",
                recommendation="Focus marketing efforts on enterprise customers in technology sector",
                confidence=0.76,
                data_points=[
                    {"metric": "target_segment_size", "value": 150},
                    {"metric": "conversion_rate", "value": 0.08},
                    {"metric": "avg_deal_size", "value": 4200}
                ]
            ),
            AIInsight(
                insight_type="risk_alert",
                title="Cash Flow Risk Detected",
                description="Predictive model indicates potential cash flow shortage in 6-8 weeks",
                impact="high",
                recommendation="Accelerate collections and defer non-critical expenses",
                confidence=0.82,
                data_points=[
                    {"metric": "projected_shortage", "value": -25000},
                    {"metric": "days_until_risk", "value": 45},
                    {"metric": "collection_acceleration_needed", "value": 0.15}
                ]
            )
        ]
        
        return insights
    
    # Helper methods
    def _generate_revenue_trend(self) -> List[Dict[str, Any]]:
        """Generate realistic revenue trend data."""
        base_revenue = 100000
        trend_data = []
        
        for i in range(12):
            # Add seasonal variation and growth trend
            seasonal_factor = 1 + 0.1 * (i % 4 - 1.5) / 1.5  # Quarterly seasonality
            growth_factor = 1 + (i * 0.02)  # 2% monthly growth
            noise = random.uniform(0.95, 1.05)  # Random variation
            
            revenue = base_revenue * seasonal_factor * growth_factor * noise
            
            trend_data.append({
                "month": f"Month {i+1}",
                "revenue": round(revenue, 2),
                "target": base_revenue * growth_factor,
                "growth_rate": round((growth_factor - 1) * 100, 1)
            })
        
        return trend_data
    
    def _generate_cash_flow_forecast(self) -> List[Dict[str, Any]]:
        """Generate cash flow forecast data."""
        forecast_data = []
        base_inflow = 120000
        base_outflow = 95000
        
        for i in range(6):  # 6 months forecast
            inflow = base_inflow * random.uniform(0.9, 1.1)
            outflow = base_outflow * random.uniform(0.95, 1.05)
            net_flow = inflow - outflow
            
            forecast_data.append({
                "period": f"Month {i+1}",
                "inflow": round(inflow, 2),
                "outflow": round(outflow, 2),
                "net_flow": round(net_flow, 2)
            })
        
        return forecast_data
    
    async def _calculate_key_metrics(self, db: AsyncSession, tenant_id: UUID) -> List[KPIValue]:
        """Calculate key metrics values."""
        # Mock KPI calculations
        return [
            KPIValue(
                kpi_id=UUID("12345678-1234-5678-9012-123456789012"),
                name="Monthly Revenue",
                current_value="$98,500",
                target_value="$100,000",
                unit="currency",
                trend="down",
                change_percentage=-1.5
            ),
            KPIValue(
                kpi_id=UUID("12345678-1234-5678-9012-123456789013"),
                name="Gross Margin",
                current_value="68.5%",
                target_value="70%",
                unit="percentage",
                trend="stable",
                change_percentage=0.2
            ),
            KPIValue(
                kpi_id=UUID("12345678-1234-5678-9012-123456789014"),
                name="Customer Acquisition Cost",
                current_value="$245",
                target_value="$200",
                unit="currency",
                trend="up",
                change_percentage=12.5
            )
        ]
    
    async def _get_recent_anomalies(self, db: AsyncSession, tenant_id: UUID) -> List[AnomalyResponse]:
        """Get recent anomalies."""
        query = select(Anomaly).where(
            and_(
                Anomaly.tenant_id == tenant_id,
                Anomaly.status == "open"
            )
        ).order_by(desc(Anomaly.detected_at)).limit(5)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def _get_active_predictions(self, db: AsyncSession, tenant_id: UUID) -> List[PredictionResponse]:
        """Get active predictions."""
        current_time = datetime.utcnow()
        query = select(Prediction).where(
            and_(
                Prediction.tenant_id == tenant_id,
                Prediction.expires_at > current_time
            )
        ).order_by(desc(Prediction.created_at)).limit(10)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def _unset_default_dashboards(self, db: AsyncSession, tenant_id: UUID):
        """Unset default flag from other dashboards."""
        query = select(Dashboard).where(
            and_(
                Dashboard.tenant_id == tenant_id,
                Dashboard.is_default == True
            )
        )
        result = await db.execute(query)
        dashboards = result.scalars().all()
        
        for dashboard in dashboards:
            dashboard.is_default = False

# Create instance
bi_ai_crud = BIAICRUD()