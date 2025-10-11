from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from app.models import JournalEntry, JournalEntryLine, ChartOfAccounts
from typing import Dict, List
from datetime import date
from decimal import Decimal

class CashFlowService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def generate_cash_flow_statement(self, company_id: str, start_date: date, end_date: date) -> Dict:
        """Generate cash flow statement from GL journal entries"""
        
        # Get cash accounts
        cash_accounts = await self._get_cash_accounts(company_id)
        cash_account_ids = [str(acc.id) for acc in cash_accounts]
        
        # Operating Activities
        operating_flows = await self._get_operating_cash_flows(company_id, start_date, end_date, cash_account_ids)
        
        # Investing Activities  
        investing_flows = await self._get_investing_cash_flows(company_id, start_date, end_date, cash_account_ids)
        
        # Financing Activities
        financing_flows = await self._get_financing_cash_flows(company_id, start_date, end_date, cash_account_ids)
        
        # Calculate totals
        total_operating = sum(item['amount'] for item in operating_flows)
        total_investing = sum(item['amount'] for item in investing_flows)  
        total_financing = sum(item['amount'] for item in financing_flows)
        net_cash_flow = total_operating + total_investing + total_financing
        
        return {
            "period": {"start_date": start_date, "end_date": end_date},
            "operating_activities": {
                "items": operating_flows,
                "total": float(total_operating)
            },
            "investing_activities": {
                "items": investing_flows,
                "total": float(total_investing)
            },
            "financing_activities": {
                "items": financing_flows,
                "total": float(total_financing)
            },
            "net_cash_flow": float(net_cash_flow)
        }
    
    async def _get_cash_accounts(self, company_id: str) -> List[ChartOfAccounts]:
        """Get all cash and cash equivalent accounts"""
        result = await self.db.execute(
            select(ChartOfAccounts).where(
                and_(
                    ChartOfAccounts.company_id == company_id,
                    ChartOfAccounts.account_type == 'Asset',
                    ChartOfAccounts.account_subtype.in_(['Cash', 'Bank', 'Cash Equivalents']),
                    ChartOfAccounts.is_active == True
                )
            )
        )
        return result.scalars().all()
    
    async def _get_operating_cash_flows(self, company_id: str, start_date: date, end_date: date, cash_account_ids: List[str]) -> List[Dict]:
        """Get operating cash flows from GL entries"""
        result = await self.db.execute(
            select(
                JournalEntryLine.description,
                func.sum(JournalEntryLine.debit_amount - JournalEntryLine.credit_amount).label('amount'),
                JournalEntry.source_module
            ).select_from(
                JournalEntryLine.join(JournalEntry)
            ).where(
                and_(
                    JournalEntry.company_id == company_id,
                    JournalEntry.entry_date.between(start_date, end_date),
                    JournalEntry.status == 'posted',
                    JournalEntryLine.account_id.in_(cash_account_ids),
                    JournalEntry.source_module.in_(['AR', 'AP', 'PAYROLL'])
                )
            ).group_by(JournalEntryLine.description, JournalEntry.source_module)
        )
        
        flows = []
        for row in result:
            flows.append({
                "description": row.description,
                "amount": float(row.amount),
                "source": row.source_module
            })
        return flows
    
    async def _get_investing_cash_flows(self, company_id: str, start_date: date, end_date: date, cash_account_ids: List[str]) -> List[Dict]:
        """Get investing cash flows from GL entries"""
        result = await self.db.execute(
            select(
                JournalEntryLine.description,
                func.sum(JournalEntryLine.debit_amount - JournalEntryLine.credit_amount).label('amount')
            ).select_from(
                JournalEntryLine.join(JournalEntry).join(ChartOfAccounts, JournalEntryLine.account_id == ChartOfAccounts.id)
            ).where(
                and_(
                    JournalEntry.company_id == company_id,
                    JournalEntry.entry_date.between(start_date, end_date),
                    JournalEntry.status == 'posted',
                    JournalEntryLine.account_id.in_(cash_account_ids),
                    ChartOfAccounts.account_subtype.in_(['Fixed Assets', 'Investments', 'Equipment'])
                )
            ).group_by(JournalEntryLine.description)
        )
        
        flows = []
        for row in result:
            flows.append({
                "description": row.description,
                "amount": float(row.amount),
                "source": "INVESTING"
            })
        return flows
    
    async def _get_financing_cash_flows(self, company_id: str, start_date: date, end_date: date, cash_account_ids: List[str]) -> List[Dict]:
        """Get financing cash flows from GL entries"""
        result = await self.db.execute(
            select(
                JournalEntryLine.description,
                func.sum(JournalEntryLine.debit_amount - JournalEntryLine.credit_amount).label('amount')
            ).select_from(
                JournalEntryLine.join(JournalEntry).join(ChartOfAccounts, JournalEntryLine.account_id == ChartOfAccounts.id)
            ).where(
                and_(
                    JournalEntry.company_id == company_id,
                    JournalEntry.entry_date.between(start_date, end_date),
                    JournalEntry.status == 'posted',
                    JournalEntryLine.account_id.in_(cash_account_ids),
                    ChartOfAccounts.account_type.in_(['Liability', 'Equity'])
                )
            ).group_by(JournalEntryLine.description)
        )
        
        flows = []
        for row in result:
            flows.append({
                "description": row.description,
                "amount": float(row.amount),
                "source": "FINANCING"
            })
        return flows