"""
Data Aggregation Service

This service provides comprehensive data aggregation capabilities for analytics,
replacing mock data with real financial data aggregations.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union

from decimal import Decimal
from sqlalchemy import select, func, and_, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.models.accounts_payable import Vendor, Invoice as APInvoice, Payment
from app.models.accounts_receivable import Customer, Invoice as ARInvoice, Receipt
from app.models.general_ledger import Transaction, Account, JournalEntry
from app.models.inventory import InventoryItem, InventoryTransaction
from app.models.payroll import Employee, Payroll, PayrollItem





class DataAggregationService:
    """Service for aggregating financial data for analytics."""

    def __init__(self, db: AsyncSession, company_id: UUID):
        """  Init  ."""
        self.db = db
        self.company_id = company_id

    async def get_financial_summary(self, date_range: Optional[Dict[str, datetime]] = None) -> Dict[str, Any]:
        """Get Financial Summary."""
        """Get comprehensive financial summary."""
        if not date_range:
            date_range = {
                'start': datetime.now() - timedelta(days=30),
                'end': datetime.now()
            }

        # Revenue aggregation
        revenue_query = select(func.sum(Transaction.amount)).where(
            and_(
                Transaction.company_id == self.company_id,
                Transaction.transaction_type == 'credit',
                Transaction.account_id.in_(
                    select(Account.id).where(
                        and_(
                            Account.company_id == self.company_id,
                            Account.account_type == 'revenue'
                        )
                    )
                ),
                Transaction.transaction_date.between(date_range['start'], date_range['end'])
            )
        )
        
        # Expense aggregation
        expense_query = select(func.sum(Transaction.amount)).where(
            and_(
                Transaction.company_id == self.company_id,
                Transaction.transaction_type == 'debit',
                Transaction.account_id.in_(
                    select(Account.id).where(
                        and_(
                            Account.company_id == self.company_id,
                            Account.account_type == 'expense'
                        )
                    )
                ),
                Transaction.transaction_date.between(date_range['start'], date_range['end'])
            )
        )

        # Execute queries
        revenue_result = await self.db.execute(revenue_query)
        expense_result = await self.db.execute(expense_query)
        
        revenue = revenue_result.scalar() or Decimal('0')
        expenses = expense_result.scalar() or Decimal('0')
        profit = revenue - expenses

        # Additional metrics
        cash_flow = await self._get_cash_flow_summary(date_range)
        ar_summary = await self._get_ar_summary()
        ap_summary = await self._get_ap_summary()

        return {
            'revenue': float(revenue),
            'expenses': float(expenses),
            'profit': float(profit),
            'profit_margin': float((profit / revenue * 100) if revenue > 0 else 0),
            'cash_flow': cash_flow,
            'accounts_receivable': ar_summary,
            'accounts_payable': ap_summary,
            'period': {
                'start': date_range['start'].isoformat(),
                'end': date_range['end'].isoformat()
            }
        }

    async def _get_cash_flow_summary(self, date_range: Dict[str, datetime]) -> Dict[str, Any]:
        """Get Cash Flow Summary."""
        """Get cash flow summary."""
        # Cash inflows (receipts)
        inflows_query = select(func.sum(Receipt.amount)).where(
            and_(
                Receipt.company_id == self.company_id,
                Receipt.receipt_date.between(date_range['start'], date_range['end'])
            )
        )
        
        # Cash outflows (payments)
        outflows_query = select(func.sum(Payment.amount)).where(
            and_(
                Payment.company_id == self.company_id,
                Payment.payment_date.between(date_range['start'], date_range['end'])
            )
        )

        inflows_result = await self.db.execute(inflows_query)
        outflows_result = await self.db.execute(outflows_query)
        
        inflows = inflows_result.scalar() or Decimal('0')
        outflows = outflows_result.scalar() or Decimal('0')
        net_cash_flow = inflows - outflows

        return {
            'inflows': float(inflows),
            'outflows': float(outflows),
            'net_cash_flow': float(net_cash_flow)
        }

    async def get_trend_analysis(self, metric: str, period: str = 'monthly', months: int = 12) -> List[Dict[str, Any]]:
        """Get Trend Analysis."""
        """Get trend analysis for specific metrics."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)

        if metric == 'revenue':
            return await self._get_revenue_trend(start_date, end_date, period)
        elif metric == 'expenses':
            return await self._get_expense_trend(start_date, end_date, period)
        elif metric == 'profit':
            return await self._get_profit_trend(start_date, end_date, period)
        elif metric == 'cash_flow':
            return await self._get_cash_flow_trend(start_date, end_date, period)
        else:
            raise ValueError(f"Unsupported metric: {metric}")

    async def _get_revenue_trend(self, start_date: datetime, end_date: datetime, period: str) -> List[Dict[str, Any]]:
        """Get Revenue Trend."""
        """Get revenue trend data."""
        if period == 'monthly':
            date_format = '%Y-%m'
            date_trunc = 'month'
        elif period == 'weekly':
            date_format = '%Y-%W'
            date_trunc = 'week'
        else:
            date_format = '%Y-%m-%d'
            date_trunc = 'day'

        query = select(
            func.date_trunc(date_trunc, Transaction.transaction_date).label('period'),
            func.sum(Transaction.amount).label('total')
        ).where(
            and_(
                Transaction.company_id == self.company_id,
                Transaction.transaction_type == 'credit',
                Transaction.account_id.in_(
                    select(Account.id).where(
                        and_(
                            Account.company_id == self.company_id,
                            Account.account_type == 'revenue'
                        )
                    )
                ),
                Transaction.transaction_date.between(start_date, end_date)
            )
        ).group_by(
            func.date_trunc(date_trunc, Transaction.transaction_date)
        ).order_by('period')

        result = await self.db.execute(query)
        rows = result.fetchall()

        return [
            {
                'period': row.period.strftime(date_format),
                'value': float(row.total or 0),
                'metric': 'revenue'
            }
            for row in rows
        ]

    async def get_kpi_dashboard(self) -> Dict[str, Any]:
        """Get Kpi Dashboard."""
        """Get comprehensive KPI dashboard data."""
        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        current_month_end = datetime.now()
        
        prev_month_end = current_month_start - timedelta(days=1)
        prev_month_start = prev_month_end.replace(day=1)

        current_summary = await self.get_financial_summary({
            'start': current_month_start,
            'end': current_month_end
        })
        
        prev_summary = await self.get_financial_summary({
            'start': prev_month_start,
            'end': prev_month_end
        })

        revenue_growth = self._calculate_growth_rate(
            current_summary['revenue'], 
            prev_summary['revenue']
        )
        
        profit_growth = self._calculate_growth_rate(
            current_summary['profit'], 
            prev_summary['profit']
        )

        customer_count = await self._get_active_customer_count()
        vendor_count = await self._get_active_vendor_count()
        inventory_value = await self._get_inventory_value()

        return {
            'financial_summary': current_summary,
            'growth_metrics': {
                'revenue_growth': revenue_growth,
                'profit_growth': profit_growth
            },
            'operational_metrics': {
                'active_customers': customer_count,
                'active_vendors': vendor_count,
                'inventory_value': inventory_value
            },
            'trends': {
                'revenue': await self.get_trend_analysis('revenue', 'monthly', 6),
                'profit': await self.get_trend_analysis('profit', 'monthly', 6)
            }
        }

    def _calculate_growth_rate(self, current: float, previous: float) -> float:
        """ Calculate Growth Rate."""
        """Calculate growth rate percentage."""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return ((current - previous) / previous) * 100

    async def _get_active_customer_count(self) -> int:
        """Get Active Customer Count."""
        """Get count of active customers."""
        query = select(func.count(Customer.id)).where(
            and_(
                Customer.company_id == self.company_id,
                Customer.status == 'active'
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def _get_active_vendor_count(self) -> int:
        """Get Active Vendor Count."""
        """Get count of active vendors."""
        query = select(func.count(Vendor.id)).where(
            and_(
                Vendor.company_id == self.company_id,
                Vendor.status == 'active'
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def _get_inventory_value(self) -> float:
        """Get Inventory Value."""
        """Get total inventory value."""
        query = select(func.sum(InventoryItem.quantity * InventoryItem.unit_cost)).where(
            and_(
                InventoryItem.company_id == self.company_id,
                InventoryItem.status == 'active'
            )
        )
        result = await self.db.execute(query)
        return float(result.scalar() or 0)