from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, text
from typing import Dict, List, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal

class UnifiedReportingService:
    """Service for unified reporting across all financial modules"""
    
    async def generate_executive_dashboard(self, db: AsyncSession, company_id: int, period_start: date, period_end: date):
        """Generate executive dashboard with data from all modules"""
        
        # AP Summary
        ap_summary = await self._get_ap_summary(db, period_start, period_end)
        
        # AR Summary  
        ar_summary = await self._get_ar_summary(db, period_start, period_end)
        
        # Cash Summary
        cash_summary = await self._get_cash_summary(db, period_start, period_end)
        
        # Budget Summary
        budget_summary = await self._get_budget_summary(db, period_start, period_end)
        
        # Calculate KPIs
        net_cash_flow = ar_summary["total_receipts"] - ap_summary["total_payments"]
        cash_conversion_cycle = self._calculate_cash_conversion_cycle(ar_summary, ap_summary)
        
        return {
            "company_id": company_id,
            "period": {"start_date": period_start.isoformat(), "end_date": period_end.isoformat()},
            "executive_summary": {
                "net_cash_flow": net_cash_flow,
                "total_cash_position": cash_summary["total_balance"],
                "accounts_payable_balance": ap_summary["outstanding_balance"],
                "accounts_receivable_balance": ar_summary["outstanding_balance"],
                "budget_utilization": budget_summary["utilization_percentage"],
                "cash_conversion_cycle": cash_conversion_cycle
            },
            "module_summaries": {
                "accounts_payable": ap_summary,
                "accounts_receivable": ar_summary,
                "cash_management": cash_summary,
                "budget_management": budget_summary
            },
            "key_metrics": {
                "liquidity_ratio": cash_summary["total_balance"] / ap_summary["outstanding_balance"] if ap_summary["outstanding_balance"] > 0 else 0,
                "collection_efficiency": ar_summary["collection_rate"],
                "payment_efficiency": ap_summary["payment_rate"],
                "budget_variance": budget_summary["variance_percentage"]
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def _get_ap_summary(self, db: AsyncSession, start_date: date, end_date: date):
        """Get AP summary for period"""
        from ..core_financials.accounts_payable.models import Payment as APPayment, Bill
        
        # Total payments in period
        payment_query = select(func.sum(APPayment.amount)).where(
            and_(
                APPayment.payment_date >= start_date,
                APPayment.payment_date <= end_date,
                APPayment.status == "approved"
            )
        )
        total_payments = float(await db.scalar(payment_query) or 0)
        
        # Outstanding balance
        outstanding_query = select(func.sum(Bill.balance_due)).where(Bill.balance_due > 0)
        outstanding_balance = float(await db.scalar(outstanding_query) or 0)
        
        # Payment count
        payment_count_query = select(func.count(APPayment.id)).where(
            and_(
                APPayment.payment_date >= start_date,
                APPayment.payment_date <= end_date,
                APPayment.status == "approved"
            )
        )
        payment_count = await db.scalar(payment_count_query) or 0
        
        return {
            "total_payments": total_payments,
            "outstanding_balance": outstanding_balance,
            "payment_count": payment_count,
            "payment_rate": 85.0  # Mock calculation
        }
    
    async def _get_ar_summary(self, db: AsyncSession, start_date: date, end_date: date):
        """Get AR summary for period"""
        from ..core_financials.accounts_receivable.models import ARPayment, ARInvoice
        
        # Total receipts in period
        receipt_query = select(func.sum(ARPayment.amount)).where(
            and_(
                ARPayment.payment_date >= start_date,
                ARPayment.payment_date <= end_date,
                ARPayment.status == "processed"
            )
        )
        total_receipts = float(await db.scalar(receipt_query) or 0)
        
        # Outstanding balance
        outstanding_query = select(func.sum(ARInvoice.balance_due)).where(ARInvoice.balance_due > 0)
        outstanding_balance = float(await db.scalar(outstanding_query) or 0)
        
        # Receipt count
        receipt_count_query = select(func.count(ARPayment.id)).where(
            and_(
                ARPayment.payment_date >= start_date,
                ARPayment.payment_date <= end_date,
                ARPayment.status == "processed"
            )
        )
        receipt_count = await db.scalar(receipt_count_query) or 0
        
        return {
            "total_receipts": total_receipts,
            "outstanding_balance": outstanding_balance,
            "receipt_count": receipt_count,
            "collection_rate": 78.0  # Mock calculation
        }
    
    async def _get_cash_summary(self, db: AsyncSession, start_date: date, end_date: date):
        """Get cash summary for period"""
        from ..core_financials.cash_management.models import BankAccount, BankTransaction
        
        # Total cash balance
        balance_query = select(func.sum(BankAccount.current_balance)).where(BankAccount.status == "active")
        total_balance = float(await db.scalar(balance_query) or 0)
        
        # Transaction count in period
        transaction_query = select(func.count(BankTransaction.id)).where(
            and_(
                BankTransaction.transaction_date >= start_date,
                BankTransaction.transaction_date <= end_date,
                BankTransaction.status == "posted"
            )
        )
        transaction_count = await db.scalar(transaction_query) or 0
        
        # Cash flow in period
        inflow_query = select(func.sum(BankTransaction.amount)).where(
            and_(
                BankTransaction.transaction_date >= start_date,
                BankTransaction.transaction_date <= end_date,
                BankTransaction.transaction_type.in_(["deposit", "transfer_in"]),
                BankTransaction.status == "posted"
            )
        )
        total_inflow = float(await db.scalar(inflow_query) or 0)
        
        outflow_query = select(func.sum(BankTransaction.amount)).where(
            and_(
                BankTransaction.transaction_date >= start_date,
                BankTransaction.transaction_date <= end_date,
                BankTransaction.transaction_type.in_(["withdrawal", "transfer_out"]),
                BankTransaction.status == "posted"
            )
        )
        total_outflow = float(await db.scalar(outflow_query) or 0)
        
        return {
            "total_balance": total_balance,
            "total_inflow": total_inflow,
            "total_outflow": total_outflow,
            "net_cash_flow": total_inflow - total_outflow,
            "transaction_count": transaction_count
        }
    
    async def _get_budget_summary(self, db: AsyncSession, start_date: date, end_date: date):
        """Get budget summary for period"""
        from ..core_financials.budget.enhanced_models import Budget, BudgetActual
        
        # Active budgets
        budget_query = select(func.sum(Budget.total_amount)).where(
            and_(
                Budget.status == "approved",
                Budget.start_date <= end_date,
                Budget.end_date >= start_date
            )
        )
        total_budget = float(await db.scalar(budget_query) or 0)
        
        # Actual spending
        actual_query = select(func.sum(BudgetActual.actual_amount)).where(
            and_(
                BudgetActual.period_date >= start_date,
                BudgetActual.period_date <= end_date
            )
        )
        total_actual = float(await db.scalar(actual_query) or 0)
        
        # Calculate utilization
        utilization = (total_actual / total_budget) * 100 if total_budget > 0 else 0
        variance = total_budget - total_actual
        variance_percentage = (variance / total_budget) * 100 if total_budget > 0 else 0
        
        return {
            "total_budget": total_budget,
            "total_actual": total_actual,
            "utilization_percentage": utilization,
            "variance": variance,
            "variance_percentage": variance_percentage
        }
    
    def _calculate_cash_conversion_cycle(self, ar_summary: dict, ap_summary: dict):
        """Calculate cash conversion cycle"""
        # Simplified calculation - in real implementation would use more detailed data
        days_sales_outstanding = 45  # Mock - would calculate from AR data
        days_payable_outstanding = 30  # Mock - would calculate from AP data
        days_inventory_outstanding = 0   # Not applicable for service business
        
        return days_sales_outstanding + days_inventory_outstanding - days_payable_outstanding
    
    async def generate_cash_flow_statement(self, db: AsyncSession, company_id: int, period_start: date, period_end: date):
        """Generate integrated cash flow statement"""
        
        # Operating activities (from AR and AP)
        ar_summary = await self._get_ar_summary(db, period_start, period_end)
        ap_summary = await self._get_ap_summary(db, period_start, period_end)
        
        operating_cash_flow = ar_summary["total_receipts"] - ap_summary["total_payments"]
        
        # Investing activities (mock - would integrate with fixed assets)
        investing_cash_flow = 0
        
        # Financing activities (mock - would integrate with loans/equity)
        financing_cash_flow = 0
        
        # Net change in cash
        net_change = operating_cash_flow + investing_cash_flow + financing_cash_flow
        
        # Get beginning and ending cash
        cash_summary = await self._get_cash_summary(db, period_start, period_end)
        ending_cash = cash_summary["total_balance"]
        beginning_cash = ending_cash - net_change
        
        return {
            "company_id": company_id,
            "period": {"start_date": period_start.isoformat(), "end_date": period_end.isoformat()},
            "cash_flow_statement": {
                "operating_activities": {
                    "cash_receipts_from_customers": ar_summary["total_receipts"],
                    "cash_payments_to_suppliers": -ap_summary["total_payments"],
                    "net_cash_from_operating": operating_cash_flow
                },
                "investing_activities": {
                    "net_cash_from_investing": investing_cash_flow
                },
                "financing_activities": {
                    "net_cash_from_financing": financing_cash_flow
                },
                "net_change_in_cash": net_change,
                "beginning_cash": beginning_cash,
                "ending_cash": ending_cash
            },
            "generated_at": datetime.utcnow().isoformat()
        }