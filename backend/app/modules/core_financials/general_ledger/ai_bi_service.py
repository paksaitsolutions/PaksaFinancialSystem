"""AI/BI data preparation service for GL module"""
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from datetime import datetime, timedelta
from app.modules.core_financials.general_ledger.models import Account, JournalEntry, JournalEntryLine

class GLAIBIService:
    """Service for AI/BI data preparation and analytics"""
    
    @staticmethod
    async def get_cash_flow_data(db: AsyncSession, tenant_id: str, months: int = 12) -> Dict:
        """Get cash flow data for predictive analysis"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)
        
        # Get cash accounts
        cash_accounts = await db.execute(
            select(Account).where(
                and_(
                    Account.tenant_id == tenant_id,
                    Account.account_type == 'asset',
                    Account.name.ilike('%cash%')
                )
            )
        )
        cash_account_ids = [acc.id for acc in cash_accounts.scalars().all()]
        
        # Get monthly cash flow
        monthly_flows = await db.execute(
            select(
                func.date_trunc('month', JournalEntry.entry_date).label('month'),
                func.sum(JournalEntryLine.debit_amount - JournalEntryLine.credit_amount).label('net_flow')
            )
            .join(JournalEntryLine)
            .where(
                and_(
                    JournalEntry.tenant_id == tenant_id,
                    JournalEntry.entry_date >= start_date,
                    JournalEntryLine.account_id.in_(cash_account_ids),
                    JournalEntry.status == 'posted'
                )
            )
            .group_by(func.date_trunc('month', JournalEntry.entry_date))
            .order_by(func.date_trunc('month', JournalEntry.entry_date))
        )
        
        return {
            "historical_data": [
                {"month": row.month.strftime("%Y-%m"), "net_flow": float(row.net_flow)}
                for row in monthly_flows
            ],
            "prediction_ready": True
        }
    
    @staticmethod
    async def detect_journal_anomalies(db: AsyncSession, tenant_id: str) -> List[Dict]:
        """Detect anomalies in journal entries"""
        # Get recent entries for analysis
        recent_entries = await db.execute(
            select(JournalEntry)
            .where(
                and_(
                    JournalEntry.tenant_id == tenant_id,
                    JournalEntry.entry_date >= datetime.now() - timedelta(days=30),
                    JournalEntry.status == 'posted'
                )
            )
            .order_by(desc(JournalEntry.entry_date))
        )
        
        anomalies = []
        for entry in recent_entries.scalars().all():
            # Simple anomaly detection rules
            if entry.total_debit > 100000:  # Large amount threshold
                anomalies.append({
                    "entry_id": entry.id,
                    "entry_number": entry.entry_number,
                    "anomaly_type": "large_amount",
                    "amount": float(entry.total_debit),
                    "severity": "high" if entry.total_debit > 500000 else "medium",
                    "description": f"Unusually large journal entry: ${entry.total_debit:,.2f}"
                })
            
            # Check for weekend posting
            if entry.entry_date.weekday() >= 5:  # Saturday or Sunday
                anomalies.append({
                    "entry_id": entry.id,
                    "entry_number": entry.entry_number,
                    "anomaly_type": "weekend_posting",
                    "severity": "low",
                    "description": "Journal entry posted on weekend"
                })
        
        return anomalies
    
    @staticmethod
    async def get_real_time_kpis(db: AsyncSession, tenant_id: str) -> Dict:
        """Generate real-time KPIs for dashboards"""
        # Get account balances by type
        account_balances = await db.execute(
            select(
                Account.account_type,
                func.sum(Account.balance).label('total_balance')
            )
            .where(
                and_(
                    Account.tenant_id == tenant_id,
                    Account.is_active == True
                )
            )
            .group_by(Account.account_type)
        )
        
        balances = {row.account_type: float(row.total_balance) for row in account_balances}
        
        # Calculate key ratios
        total_assets = balances.get('asset', 0)
        total_liabilities = balances.get('liability', 0)
        total_equity = balances.get('equity', 0)
        
        return {
            "total_assets": total_assets,
            "total_liabilities": total_liabilities,
            "total_equity": total_equity,
            "debt_to_equity_ratio": total_liabilities / total_equity if total_equity > 0 else 0,
            "current_ratio": total_assets / total_liabilities if total_liabilities > 0 else 0,
            "last_updated": datetime.now().isoformat()
        }
    
    @staticmethod
    async def get_financial_trends(db: AsyncSession, tenant_id: str, periods: int = 12) -> Dict:
        """Analyze financial trends over time"""
        # Get monthly revenue and expense trends
        monthly_trends = await db.execute(
            select(
                func.date_trunc('month', JournalEntry.entry_date).label('month'),
                Account.account_type,
                func.sum(JournalEntryLine.credit_amount - JournalEntryLine.debit_amount).label('net_amount')
            )
            .join(JournalEntryLine)
            .join(Account, JournalEntryLine.account_id == Account.id)
            .where(
                and_(
                    JournalEntry.tenant_id == tenant_id,
                    JournalEntry.entry_date >= datetime.now() - timedelta(days=periods * 30),
                    Account.account_type.in_(['revenue', 'expense']),
                    JournalEntry.status == 'posted'
                )
            )
            .group_by(
                func.date_trunc('month', JournalEntry.entry_date),
                Account.account_type
            )
            .order_by(func.date_trunc('month', JournalEntry.entry_date))
        )
        
        trends = {}
        for row in monthly_trends:
            month = row.month.strftime("%Y-%m")
            if month not in trends:
                trends[month] = {}
            trends[month][row.account_type] = float(row.net_amount)
        
        return {
            "monthly_trends": trends,
            "trend_analysis": "ready_for_ml"
        }

class GLBIEndpointService:
    """Service for BI tool integration endpoints"""
    
    @staticmethod
    async def get_tableau_data(db: AsyncSession, tenant_id: str, data_type: str) -> Dict:
        """Prepare data for Tableau integration"""
        if data_type == "trial_balance":
            accounts = await db.execute(
                select(Account).where(
                    and_(
                        Account.tenant_id == tenant_id,
                        Account.is_active == True
                    )
                )
            )
            
            return {
                "data": [
                    {
                        "account_code": acc.account_code,
                        "account_name": acc.account_name,
                        "account_type": acc.account_type.value,
                        "balance": float(acc.balance),
                        "is_debit_balance": acc.account_type.value in ['asset', 'expense']
                    }
                    for acc in accounts.scalars().all()
                ],
                "metadata": {
                    "tenant_id": tenant_id,
                    "generated_at": datetime.now().isoformat(),
                    "data_type": "trial_balance"
                }
            }
        
        return {"error": "Unsupported data type"}
    
    @staticmethod
    async def get_powerbi_data(db: AsyncSession, tenant_id: str, report_type: str) -> Dict:
        """Prepare data for PowerBI integration"""
        if report_type == "financial_summary":
            kpis = await GLAIBIService.get_real_time_kpis(db, tenant_id)
            return {
                "financial_summary": kpis,
                "format": "powerbi_compatible"
            }
        
        return {"error": "Unsupported report type"}
    
    @staticmethod
    async def get_metabase_data(db: AsyncSession, tenant_id: str, query_type: str) -> Dict:
        """Prepare data for Metabase integration"""
        if query_type == "journal_entries":
            entries = await db.execute(
                select(JournalEntry)
                .where(
                    and_(
                        JournalEntry.tenant_id == tenant_id,
                        JournalEntry.entry_date >= datetime.now() - timedelta(days=90)
                    )
                )
                .limit(1000)
            )
            
            return {
                "journal_entries": [
                    {
                        "entry_id": entry.id,
                        "entry_number": entry.entry_number,
                        "entry_date": entry.entry_date.isoformat(),
                        "description": entry.description,
                        "total_debit": float(entry.total_debit),
                        "total_credit": float(entry.total_credit),
                        "status": entry.status
                    }
                    for entry in entries.scalars().all()
                ]
            }
        
        return {"error": "Unsupported query type"}