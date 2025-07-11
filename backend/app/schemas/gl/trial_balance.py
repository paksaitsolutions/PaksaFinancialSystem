from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field

class TrialBalanceEntry(BaseModel):
    """Represents a single line item in the trial balance"""
    account_code: str = Field(..., description="The account code")
    account_name: str = Field(..., description="The account name")
    account_type: str = Field(..., description="The type of the account")
    opening_balance: float = Field(0.0, description="Opening balance as of the start date")
    period_activity: float = Field(0.0, description="Net activity during the period")
    ending_balance: float = Field(0.0, description="Ending balance as of the end date")
    debit_amount: float = Field(0.0, description="Debit amount for the period")
    credit_amount: float = Field(0.0, description="Credit amount for the period")

class TrialBalance(BaseModel):
    """Represents a complete trial balance report"""
    start_date: date = Field(..., description="Start date of the reporting period")
    end_date: date = Field(..., description="End date of the reporting period")
    entries: List[TrialBalanceEntry] = Field(default_factory=list, description="List of trial balance entries")
    total_debit: float = Field(0.0, description="Total of all debit amounts")
    total_credit: float = Field(0.0, description="Total of all credit amounts")
    difference: float = Field(0.0, description="Difference between total debits and credits (should be 0)")

class TrialBalanceParams(BaseModel):
    """Parameters for generating a trial balance"""
    start_date: date = Field(..., description="Start date of the reporting period")
    end_date: date = Field(..., description="End date of the reporting period")
    include_zeros: bool = Field(False, description="Include accounts with zero balance")
    format: str = Field("json", description="Output format (json, csv, excel)")
