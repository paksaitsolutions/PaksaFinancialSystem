"""
Tax Analytics Service

This module provides services for tax analytics, including:
- Tax compliance analysis
- Tax optimization recommendations
- Risk assessment
- Report generation
"""
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, case

from app.core.config import settings
from app.modules.cross_cutting.bi_ai.services.ai_service import AIService
from app.modules.tax.models import TaxTransaction, TaxExemption, TaxPolicy
from app.modules.tax.schemas import TaxAnalyticsRequest, TaxAnalyticsResponse


class TaxAnalyticsService:
    """Service for tax analytics and reporting."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_service = AIService(db)

    async def get_tax_analytics(self, request: TaxAnalyticsRequest) -> TaxAnalyticsResponse:
        """Get comprehensive tax analytics based on the request parameters."""
        try:
            # Get date range based on period
            start_date, end_date = self._get_date_range(request.period)

            # Calculate basic metrics
            metrics = await self._calculate_metrics(start_date, end_date)

            # Generate AI insights
            insights = await self._generate_insights(metrics)

            return TaxAnalyticsResponse(
                metrics=metrics,
                insights=insights,
                period={
                    "start_date": start_date,
                    "end_date": end_date
                }
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def _calculate_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate tax metrics for the specified period."""
        # Get total tax amount
        total_tax = await self._get_total_tax(start_date, end_date)

        # Get average tax per employee
        avg_tax_per_employee = await self._get_avg_tax_per_employee(start_date, end_date)

        # Get compliance rate
        compliance_rate = await self._get_compliance_rate(start_date, end_date)

        # Get exemption usage
        exemption_usage = await self._get_exemption_usage(start_date, end_date)

        # Get jurisdictional breakdown
        jurisdictional_breakdown = await self._get_jurisdictional_breakdown(start_date, end_date)

        return {
            "total_tax": total_tax,
            "avg_tax_per_employee": avg_tax_per_employee,
            "compliance_rate": compliance_rate,
            "exemption_usage": exemption_usage,
            "jurisdictional_breakdown": jurisdictional_breakdown
        }

    async def _generate_insights(self, metrics: Dict[str, Any]) -> Dict[str, str]:
        """Generate AI-powered insights based on the calculated metrics."""
        try:
            return await self.ai_service.generate_insights({
                "metrics": metrics,
                "context": {
                    "period": metrics.get("period", {}),
                    "company": settings.COMPANY_NAME,
                    "industry": settings.COMPANY_INDUSTRY
                }
            })
        except Exception as e:
            return {
                "compliance": f"Unable to generate compliance insights: {str(e)}",
                "optimization": f"Unable to generate optimization insights: {str(e)}",
                "risk": f"Unable to generate risk insights: {str(e)}"
            }

    def _get_date_range(self, period: str) -> tuple[datetime, datetime]:
        """Get date range based on the period type."""
        now = datetime.utcnow()
        
        if period == "current_month":
            start_date = now.replace(day=1)
            end_date = start_date.replace(day=1, month=start_date.month + 1) - timedelta(days=1)
        elif period == "current_quarter":
            month = now.month - (now.month % 3)
            start_date = now.replace(month=month, day=1)
            end_date = start_date + relativedelta(months=3) - timedelta(days=1)
        elif period == "current_year":
            start_date = now.replace(month=1, day=1)
            end_date = now.replace(month=12, day=31)
        else:  # custom range
            start_date = now - timedelta(days=30)
            end_date = now

        return start_date, end_date

    async def _get_total_tax(self, start_date: datetime, end_date: datetime) -> float:
        """Calculate total tax amount for the period."""
        query = (
            select(func.sum(TaxTransaction.amount))
            .where(
                and_(
                    TaxTransaction.date >= start_date,
                    TaxTransaction.date <= end_date
                )
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or 0.0

    async def _get_avg_tax_per_employee(self, start_date: datetime, end_date: datetime) -> float:
        """Calculate average tax per employee for the period."""
        query = (
            select(
                func.sum(TaxTransaction.amount).label("total_tax"),
                func.count(func.distinct(TaxTransaction.employee_id)).label("employee_count")
            )
            .where(
                and_(
                    TaxTransaction.date >= start_date,
                    TaxTransaction.date <= end_date
                )
            )
        )
        result = await self.db.execute(query)
        row = result.first()
        if not row or row.employee_count == 0:
            return 0.0
        return row.total_tax / row.employee_count

    async def _get_compliance_rate(self, start_date: datetime, end_date: datetime) -> float:
        """Calculate tax compliance rate for the period."""
        query = (
            select(
                func.count(
                    case(
                        [(TaxTransaction.is_compliant == True, 1)],
                        else_=0
                    )
                ).label("compliant_count"),
                func.count(TaxTransaction.id).label("total_count")
            )
            .where(
                and_(
                    TaxTransaction.date >= start_date,
                    TaxTransaction.date <= end_date
                )
            )
        )
        result = await self.db.execute(query)
        row = result.first()
        if not row or row.total_count == 0:
            return 0.0
        return (row.compliant_count / row.total_count) * 100

    async def _get_exemption_usage(self, start_date: datetime, end_date: datetime) -> Dict[str, float]:
        """Calculate exemption usage by type for the period."""
        query = (
            select(
                TaxExemption.type,
                func.sum(TaxExemption.amount).label("total_amount")
            )
            .where(
                and_(
                    TaxExemption.date >= start_date,
                    TaxExemption.date <= end_date
                )
            )
            .group_by(TaxExemption.type)
        )
        result = await self.db.execute(query)
        return {row.type: row.total_amount for row in result.all()}

    async def _get_jurisdictional_breakdown(self, start_date: datetime, end_date: datetime) -> Dict[str, float]:
        """Calculate tax breakdown by jurisdiction for the period."""
        query = (
            select(
                TaxTransaction.jurisdiction,
                func.sum(TaxTransaction.amount).label("total_amount")
            )
            .where(
                and_(
                    TaxTransaction.date >= start_date,
                    TaxTransaction.date <= end_date
                )
            )
            .group_by(TaxTransaction.jurisdiction)
        )
        result = await self.db.execute(query)
        return {row.jurisdiction: row.total_amount for row in result.all()}
