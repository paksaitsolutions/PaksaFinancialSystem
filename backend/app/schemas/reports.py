from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, date

class ReportResponse(BaseModel):
    id: str
    name: str
    description: str
    category: str
    status: str
    last_run: Optional[datetime] = None
    
class ReportRunRequest(BaseModel):
    report_id: str
    parameters: Optional[Dict[str, Any]] = {}

class FinancialStatementResponse(BaseModel):
    period_start: date
    period_end: date
    generated_at: datetime = datetime.now()

class BalanceSheetResponse(BaseModel):
    as_of_date: date
    assets: Dict[str, Any]
    liabilities: Dict[str, Any]
    equity: Dict[str, Any]
    generated_at: datetime = datetime.now()

class IncomeStatementResponse(BaseModel):
    period_start: date
    period_end: date
    revenue: Dict[str, float]
    cost_of_goods_sold: Dict[str, float]
    gross_profit: float
    operating_expenses: Dict[str, float]
    operating_income: float
    other_income: float
    other_expenses: float
    net_income: float
    generated_at: datetime = datetime.now()

class CashFlowResponse(BaseModel):
    period_start: date
    period_end: date
    operating_activities: Dict[str, float]
    investing_activities: Dict[str, float]
    financing_activities: Dict[str, float]
    net_cash_change: float
    beginning_cash: float
    ending_cash: float
    generated_at: datetime = datetime.now()

class TrialBalanceResponse(BaseModel):
    as_of_date: date
    accounts: List[Dict[str, Any]]
    total_debits: float
    total_credits: float
    is_balanced: bool
    generated_at: datetime = datetime.now()

class AgingReportResponse(BaseModel):
    report_type: str  # "accounts_receivable" or "accounts_payable"
    as_of_date: date
    aging_buckets: List[Dict[str, Any]]
    totals: Dict[str, float]
    generated_at: datetime = datetime.now()