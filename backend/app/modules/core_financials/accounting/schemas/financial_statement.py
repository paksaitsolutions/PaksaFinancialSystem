from datetime import date, datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator
from uuid import UUID


class FinancialStatementType(str, Enum):
    """Types of financial statements."""
    BALANCE_SHEET = "balance_sheet"
    INCOME_STATEMENT = "income_statement"
    CASH_FLOW = "cash_flow"


class FinancialStatementPeriod(BaseModel):
    """Represents a financial period for statements."""
    id: Optional[str] = Field(None, description="Unique identifier for the period")
    name: str = Field(..., description="Name of the period")
    start_date: date = Field(..., description="Start date of the period")
    end_date: date = Field(..., description="End date of the period")
    fiscal_year: int = Field(..., description="Fiscal year this period belongs to")
    is_closed: bool = Field(False, description="Whether the period is closed")


class FinancialStatementLineItem(BaseModel):
    """A single line item in a financial statement."""
    name: str = Field(..., description="Name of the line item")
    amount: Union[str, float, int] = Field(..., description="Amount for the line item")
    amount_prev: Optional[Union[str, float, int]] = Field(
        None, 
        description="Amount for the line item from the previous period (if applicable)"
    )
    code: Optional[str] = Field(None, description="Account or item code")
    is_header: bool = Field(False, description="Whether this is a header/section title")
    is_subtotal: bool = Field(False, description="Whether this is a subtotal line")
    is_total: bool = Field(False, description="Whether this is a total line")
    metadata: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional metadata for the line item"
    )


class FinancialStatementSection(BaseModel):
    """A section in a financial statement (e.g., Assets, Liabilities, Revenue, Expenses)."""
    name: str = Field(..., description="Name of the section")
    lines: List[FinancialStatementLineItem] = Field(
        default_factory=list,
        description="Line items in this section"
    )
    total: Union[str, float, int] = Field(
        ...,
        description="Total amount for this section"
    )
    total_prev: Optional[Union[str, float, int]] = Field(
        None,
        description="Total amount for this section from the previous period (if applicable)"
    )
    is_operating: bool = Field(
        False,
        description="Whether this is an operating activities section (for cash flow statements)"
    )
    is_investing: bool = Field(
        False,
        description="Whether this is an investing activities section (for cash flow statements)"
    )
    is_financing: bool = Field(
        False,
        description="Whether this is a financing activities section (for cash flow statements)"
    )
    show_subtotals: bool = Field(
        False,
        description="Whether to show subtotals in this section"
    )
    show_totals: bool = Field(
        False,
        description="Whether to show the total for this section"
    )


class FinancialStatementResponse(BaseModel):
    """Base response model for financial statements."""
    type: str = Field(..., description="Type of financial statement")
    start_date: Optional[date] = Field(None, description="Start date of the reporting period")
    end_date: Optional[date] = Field(None, description="End date of the reporting period")
    as_of_date: Optional[date] = Field(
        None, 
        description="As of date (for balance sheets)"
    )
    currency: str = Field("USD", description="Reporting currency")
    period: Optional[FinancialStatementPeriod] = Field(
        None,
        description="Financial period information"
    )
    sections: List[FinancialStatementSection] = Field(
        default_factory=list,
        description="Sections of the financial statement"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the financial statement"
    )


class BalanceSheetResponse(FinancialStatementResponse):
    """Response model for balance sheet requests."""
    type: str = Field(
        FinancialStatementType.BALANCE_SHEET.value,
        description="Type of financial statement"
    )
    as_of_date: date = Field(..., description="Date the balance sheet is generated for")
    total_assets: Union[str, float, int] = Field(
        ...,
        description="Total assets"
    )
    total_liabilities: Union[str, float, int] = Field(
        ...,
        description="Total liabilities"
    )
    total_equity: Union[str, float, int] = Field(
        ...,
        description="Total equity"
    )
    total_liabilities_and_equity: Union[str, float, int] = Field(
        ...,
        description="Total liabilities and equity (should equal total assets)"
    )


class IncomeStatementResponse(FinancialStatementResponse):
    """Response model for income statement requests."""
    type: str = Field(
        FinancialStatementType.INCOME_STATEMENT.value,
        description="Type of financial statement"
    )
    gross_profit: Dict[str, Union[str, float, int]] = Field(
        ...,
        description="Gross profit information"
    )
    operating_income: Dict[str, Union[str, float, int]] = Field(
        ...,
        description="Operating income information"
    )
    net_income: Dict[str, Union[str, float, int]] = Field(
        ...,
        description="Net income information"
    )
    ebitda: Optional[Dict[str, Union[str, float, int]]] = Field(
        None,
        description="Earnings before interest, taxes, depreciation, and amortization"
    )


class CashFlowStatementResponse(FinancialStatementResponse):
    """Response model for cash flow statement requests."""
    type: str = Field(
        FinancialStatementType.CASH_FLOW.value,
        description="Type of financial statement"
    )
    net_cash_operating: Union[str, float, int] = Field(
        ...,
        description="Net cash provided by (used in) operating activities"
    )
    net_cash_investing: Union[str, float, int] = Field(
        ...,
        description="Net cash provided by (used in) investing activities"
    )
    net_cash_financing: Union[str, float, int] = Field(
        ...,
        description="Net cash provided by (used in) financing activities"
    )
    net_increase_decrease: Union[str, float, int] = Field(
        ...,
        description="Net increase (decrease) in cash and cash equivalents"
    )
    beginning_cash: Union[str, float, int] = Field(
        ...,
        description="Cash and cash equivalents at beginning of period"
    )
    ending_cash: Union[str, float, int] = Field(
        ...,
        description="Cash and cash equivalents at end of period"
    )


class FinancialStatementRequest(BaseModel):
    """Base request model for financial statement generation."""
    start_date: Optional[date] = Field(
        None,
        description="Start date of the reporting period"
    )
    end_date: Optional[date] = Field(
        None,
        description="End date of the reporting period"
    )
    as_of_date: Optional[date] = Field(
        None,
        description="As of date (for balance sheets)"
    )
    currency: str = Field("USD", description="Reporting currency")
    include_comparative: bool = Field(
        False,
        description="Whether to include comparative figures from the previous period"
    )
    format_currency: bool = Field(
        True,
        description="Whether to format amounts as currency strings"
    )
    include_metadata: bool = Field(
        True,
        description="Whether to include metadata in the response"
    )
