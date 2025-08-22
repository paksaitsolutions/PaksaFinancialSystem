from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional
from datetime import datetime, date, timedelta
from decimal import Decimal
from ..models import CashFlowEntry, BankAccount

class CashFlowService:
    """Service for cash flow forecasting and analysis"""
    
    async def get_cash_flow_forecast(self, db: AsyncSession, start_date: date, end_date: date, 
                                   account_id: Optional[int] = None):
        """Get comprehensive cash flow forecast"""
        # Get opening balance
        if account_id:
            account_query = select(BankAccount).where(BankAccount.id == account_id)
            account_result = await db.execute(account_query)
            account = account_result.scalar_one_or_none()
            opening_balance = float(account.current_balance) if account else 0.0
        else:
            balance_query = select(func.sum(BankAccount.current_balance)).where(BankAccount.status == 'active')
            opening_balance = float(await db.scalar(balance_query) or 0)
        
        # Get forecast entries
        query = select(CashFlowEntry).where(
            and_(
                CashFlowEntry.entry_date >= start_date,
                CashFlowEntry.entry_date <= end_date
            )
        )
        
        if account_id:
            query = query.where(CashFlowEntry.account_id == account_id)
            
        result = await db.execute(query)
        entries = result.scalars().all()
        
        # Calculate totals
        projected_inflows = sum(
            float(entry.amount * entry.confidence_level) 
            for entry in entries if entry.flow_type == 'inflow'
        )
        projected_outflows = sum(
            float(entry.amount * entry.confidence_level) 
            for entry in entries if entry.flow_type == 'outflow'
        )
        closing_balance = opening_balance + projected_inflows - projected_outflows
        
        # Generate daily forecast
        daily_forecast = []
        current_balance = opening_balance
        current_date = start_date
        
        while current_date <= end_date:
            daily_inflow = sum(
                float(entry.amount * entry.confidence_level) 
                for entry in entries 
                if entry.entry_date == current_date and entry.flow_type == 'inflow'
            )
            daily_outflow = sum(
                float(entry.amount * entry.confidence_level) 
                for entry in entries 
                if entry.entry_date == current_date and entry.flow_type == 'outflow'
            )
            current_balance += daily_inflow - daily_outflow
            
            daily_forecast.append({
                "date": current_date.isoformat(),
                "inflow": daily_inflow,
                "outflow": daily_outflow,
                "balance": current_balance
            })
            
            current_date += timedelta(days=1)
        
        return {
            "period": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
            "opening_balance": opening_balance,
            "projected_inflows": projected_inflows,
            "projected_outflows": projected_outflows,
            "closing_balance": closing_balance,
            "daily_forecast": daily_forecast
        }