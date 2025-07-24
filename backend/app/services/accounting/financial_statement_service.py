"""
Paksa Financial System 
Financial Statement Service

This module provides services for generating financial statements from the general ledger.
"""
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Optional, Tuple, Union, Any, TypedDict, Literal
from uuid import UUID

from dateutil.relativedelta import relativedelta
from sqlalchemy import and_, or_, func, case, text, select, literal_column
from sqlalchemy.orm import Session, joinedload, aliased

from ...base.service import BaseService
from ..exceptions import (
    FinancialStatementException,
    PeriodNotFoundException,
    InvalidPeriodException
)
from ..models import (
    Account,
    AccountType,
    AccountBalance,
    GLPeriod,
    JournalEntry,
    JournalEntryLine,
    FinancialStatement,
    FinancialStatementType,
    FinancialStatementLine,
    FinancialStatementLineType
)
from .gl_period_service import GLPeriodService


class FinancialStatementService(BaseService):
    """
    Service for generating and managing financial statements.
    """
    
    def __init__(self, db: Session):
        """Initialize the service with a database session."""
        super().__init__(db)
        self.period_service = GLPeriodService(db)
    
    def generate_balance_sheet(
        self,
        as_of_date: date,
        currency: str = 'USD',
        include_comparative: bool = False,
        include_notes: bool = True,
        format_currency: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a balance sheet as of a specific date.
        
        Args:
            as_of_date: The date to generate the balance sheet for
            currency: The reporting currency
            include_comparative: Whether to include prior period comparison
            include_notes: Whether to include notes and disclosures
            format_currency: Whether to format numbers as currency strings
            
        Returns:
            Dictionary containing the balance sheet data
        """
        # Get the period for the as_of_date
        period = self.period_service.get_period_for_date(as_of_date)
        if not period:
            raise PeriodNotFoundException(f"No open period found for date: {as_of_date}")
        
        # Get the previous period for comparison if requested
        prev_period = None
        if include_comparative:
            prev_period = self._get_previous_period(period)
        
        # Get account balances
        current_balances = self._get_account_balances_for_period(period.id)
        prev_balances = self._get_account_balances_for_period(prev_period.id) if prev_period else {}
        
        # Prepare the balance sheet structure
        balance_sheet = {
            'type': FinancialStatementType.BALANCE_SHEET.value,
            'as_of_date': as_of_date.isoformat(),
            'currency': currency,
            'period': {
                'id': str(period.id),
                'name': period.name,
                'start_date': period.start_date.isoformat(),
                'end_date': period.end_date.isoformat(),
                'fiscal_year': period.fiscal_year
            },
            'sections': [],
            'metadata': {
                'generated_at': datetime.utcnow().isoformat(),
                'include_comparative': include_comparative,
                'include_notes': include_notes
            }
        }
        
        # Define balance sheet sections
        sections = [
            {
                'name': 'Assets',
                'account_types': [
                    AccountType.ASSET_CURRENT.value,
                    AccountType.ASSET_FIXED.value,
                    AccountType.ASSET_INTANGIBLE.value,
                    AccountType.ASSET_NON_CURRENT.value,
                    AccountType.ASSET_PREPAYMENT.value
                ],
                'is_debit_positive': True
            },
            {
                'name': 'Liabilities',
                'account_types': [
                    AccountType.LIABILITY_CURRENT.value,
                    AccountType.LIABILITY_LONG_TERM.value,
                    AccountType.LIABILITY_PROVISION.value
                ],
                'is_debit_positive': False
            },
            {
                'name': 'Equity',
                'account_types': [
                    AccountType.EQUITY.value,
                    AccountType.RETAINED_EARNINGS.value
                ],
                'is_debit_positive': False
            }
        ]
        
        # Process each section
        for section in sections:
            section_data = {
                'name': section['name'],
                'total': Decimal('0'),
                'lines': [],
                'subtotals': {}
            }
            
            if include_comparative and prev_balances:
                section_data['total_prev'] = Decimal('0')
            
            # Process each account type in the section
            for account_type in section['account_types']:
                accounts = self._get_accounts_by_type(account_type)
                type_total = Decimal('0')
                type_prev_total = Decimal('0')
                
                for account in accounts:
                    # Get current period balance
                    balance = current_balances.get(account.id, {
                        'account_id': account.id,
                        'account_code': account.code,
                        'account_name': account.name,
                        'balance': Decimal('0')
                    })
                    
                    # Get previous period balance if available
                    prev_balance = prev_balances.get(account.id, {
                        'balance': Decimal('0')
                    }) if include_comparative and prev_balances else None
                    
                    # Calculate the balance based on account type
                    if section['is_debit_positive']:
                        current_balance = balance['balance']
                        prev_balance_val = prev_balance['balance'] if prev_balance else Decimal('0')
                    else:
                        current_balance = -balance['balance']
                        prev_balance_val = -prev_balance['balance'] if prev_balance else Decimal('0')
                    
                    # Add to type total
                    type_total += current_balance
                    if include_comparative and prev_balances:
                        type_prev_total += prev_balance_val
                    
                    # Add account line
                    line = {
                        'account_id': str(account.id),
                        'account_code': account.code,
                        'account_name': account.name,
                        'amount': self._format_amount(current_balance, format_currency, currency),
                        'is_header': False
                    }
                    
                    if include_comparative and prev_balances:
                        line['amount_prev'] = self._format_amount(prev_balance_val, format_currency, currency)
                    
                    section_data['lines'].append(line)
                
                # Add account type subtotal
                if accounts:
                    subtotal = {
                        'name': f"Total {account_type.replace('_', ' ').title()}",
                        'amount': self._format_amount(type_total, format_currency, currency),
                        'is_subtotal': True
                    }
                    
                    if include_comparative and prev_balances:
                        subtotal['amount_prev'] = self._format_amount(type_prev_total, format_currency, currency)
                    
                    section_data['lines'].append(subtotal)
                    section_data['subtotals'][account_type] = {
                        'current': type_total,
                        'previous': type_prev_total if include_comparative and prev_balances else None
                    }
                    
                    section_data['total'] += type_total
                    if include_comparative and prev_balances:
                        section_data['total_prev'] += type_prev_total
            
            # Format section total
            section_data['total'] = self._format_amount(section_data['total'], format_currency, currency)
            if include_comparative and prev_balances:
                section_data['total_prev'] = self._format_amount(section_data['total_prev'], format_currency, currency)
            
            balance_sheet['sections'].append(section_data)
        
        # Calculate total equity (assets - liabilities)
        assets_section = next((s for s in balance_sheet['sections'] if s['name'] == 'Assets'), None)
        liabilities_section = next((s for s in balance_sheet['sections'] if s['name'] == 'Liabilities'), None)
        equity_section = next((s for s in balance_sheet['sections'] if s['name'] == 'Equity'), None)
        
        if assets_section and liabilities_section and equity_section:
            # Calculate total assets and liabilities
            total_assets = self._parse_amount(assets_section['total'])
            total_liabilities = self._parse_amount(liabilities_section['total'])
            
            # Calculate total equity (assets - liabilities)
            calculated_equity = total_assets - total_liabilities
            
            # Add calculated equity line
            equity_line = {
                'name': 'Calculated Equity (Assets - Liabilities)',
                'amount': self._format_amount(calculated_equity, format_currency, currency),
                'is_calculated': True,
                'is_header': True
            }
            
            if include_comparative and prev_balances:
                total_assets_prev = self._parse_amount(assets_section['total_prev'])
                total_liabilities_prev = self._parse_amount(liabilities_section['total_prev'])
                calculated_equity_prev = total_assets_prev - total_liabilities_prev
                equity_line['amount_prev'] = self._format_amount(calculated_equity_prev, format_currency, currency)
            
            # Add the calculated equity line to the equity section
            equity_section['lines'].insert(0, equity_line)
        
        return balance_sheet
    
    def _get_account_balances_for_period(self, period_id: UUID) -> Dict[UUID, Dict[str, Any]]:
        """
        Get account balances for a specific period.
        
        Args:
            period_id: The ID of the period
            
        Returns:
            Dictionary mapping account IDs to balance information
        """
        from sqlalchemy import func, case
        from decimal import Decimal
        from ..models import Account, JournalEntry, JournalEntryLine
        
        # Get the period to ensure it exists
        period = self.db.query(GLPeriod).filter(GLPeriod.id == period_id).first()
        if not period:
            raise PeriodNotFoundException(f"Period with ID {period_id} not found")
        
        # Query to get all account balances for the period
        query = (
            self.db.query(
                Account.id,
                Account.code,
                Account.name,
                Account.type,
                func.sum(
                    case(
                        [
                            (JournalEntryLine.is_debit == True, JournalEntryLine.amount),
                            (JournalEntryLine.is_debit == False, -JournalEntryLine.amount)
                        ],
                        else_=0
                    )
                ).label('balance')
            )
            .join(JournalEntryLine, Account.id == JournalEntryLine.account_id)
            .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
            .filter(
                JournalEntry.period_id == period_id,
                JournalEntry.status == 'posted'
            )
            .group_by(Account.id, Account.code, Account.name, Account.type)
        )
        
        # Execute the query and build the result dictionary
        balances = {}
        for account_id, code, name, acc_type, balance in query.all():
            if balance is None:
                balance = Decimal('0')
                
            balances[account_id] = {
                'account_id': account_id,
                'account_code': code,
                'account_name': name,
                'account_type': acc_type,
                'balance': balance
            }
            
        return balances
    
    def _get_accounts_by_type(self, account_type: str) -> List[Account]:
        """
        Get all accounts of a specific type.
        
        Args:
            account_type: The account type to filter by
            
        Returns:
            List of Account objects
        """
        return (
            self.db.query(Account)
            .filter(Account.type == account_type, Account.is_active == True)
            .order_by(Account.code)
            .all()
        )
    
    def _get_previous_period(self, period: GLPeriod) -> Optional[GLPeriod]:
        """
        Get the previous period for a given period.
        
        Args:
            period: The current period
            
        Returns:
            The previous GLPeriod, or None if not found
        """
        return (
            self.db.query(GLPeriod)
            .filter(
                GLPeriod.end_date < period.start_date,
                GLPeriod.fiscal_year == period.fiscal_year
            )
            .order_by(GLPeriod.end_date.desc())
            .first()
        )
    
    def _format_amount(self, amount: Decimal, format_currency: bool, currency: str) -> Union[str, Decimal]:
        """
        Format an amount as a currency string if requested.
        
        Args:
            amount: The amount to format
            format_currency: Whether to format as currency
            currency: The currency code
            
        Returns:
            The formatted amount as a string or Decimal
        """
        if not format_currency:
            return amount
        
        # This is a simplified version - in a real app, you'd use a proper currency formatter
        return f"{currency} {amount:,.2f}"
    
    def _parse_amount(self, amount: Union[str, Decimal]) -> Decimal:
        """
        Parse an amount from a formatted currency string or return as is.
        
        Args:
            amount: The amount to parse
            
        Returns:
            The parsed Decimal amount
        """
        if isinstance(amount, Decimal):
            return amount
        
        # This is a simplified version - in a real app, you'd handle various formats
        try:
            # Remove currency symbols and thousands separators
            clean_amount = ''.join(c for c in amount if c.isdigit() or c in '.-')
            return Decimal(clean_amount)
        except:
            return Decimal('0')
    
    def generate_income_statement(
        self,
        start_date: date,
        end_date: date,
        currency: str = 'USD',
        include_comparative: bool = False,
        include_ytd: bool = False,
        format_currency: bool = True
    ) -> Dict[str, Any]:
        """
        Generate an income statement for a date range.
        
        Args:
            start_date: Start date of the period
            end_date: End date of the period
            currency: The reporting currency
            include_comparative: Whether to include prior period comparison
            include_ytd: Whether to include year-to-date figures
            format_currency: Whether to format numbers as currency strings
            
        Returns:
            Dictionary containing the income statement data
        """
        # Get the periods for the date range
        start_period = self.period_service.get_period_for_date(start_date)
        end_period = self.period_service.get_period_for_date(end_date)
        
        if not start_period or not end_period:
            raise PeriodNotFoundException(
                f"Could not find periods for the date range {start_date} to {end_date}"
            )
        
        # Get the previous period for comparison if requested
        prev_start_period = None
        prev_end_period = None
        
        if include_comparative:
            prev_start_period = self._get_previous_period(start_period)
            prev_end_period = self._get_previous_period(end_period)
        
        # Get YTD periods if requested
        ytd_start_period = None
        ytd_end_period = None
        
        if include_ytd:
            fiscal_year = start_period.fiscal_year
            ytd_start_period = self._get_first_period_of_fiscal_year(fiscal_year)
            ytd_end_period = end_period
        
        # Get account balances for all required periods
        current_balances = self._get_account_balances_for_date_range(start_date, end_date)
        
        prev_balances = {}
        if include_comparative and prev_start_period and prev_end_period:
            prev_start_date = prev_start_period.start_date
            prev_end_date = prev_end_period.end_date
            prev_balances = self._get_account_balances_for_date_range(prev_start_date, prev_end_date)
        
        ytd_balances = {}
        if include_ytd and ytd_start_period and ytd_end_period:
            ytd_start_date = ytd_start_period.start_date
            ytd_balances = self._get_account_balances_for_date_range(ytd_start_date, end_date)
        
        # Prepare the income statement structure
        income_statement = {
            'type': FinancialStatementType.INCOME_STATEMENT.value,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'currency': currency,
            'period': {
                'id': str(start_period.id) if start_period.id == end_period.id else None,
                'name': start_period.name if start_period.id == end_period.id else f"{start_period.name} to {end_period.name}",
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'fiscal_year': start_period.fiscal_year
            },
            'sections': [],
            'metadata': {
                'generated_at': datetime.utcnow().isoformat(),
                'include_comparative': include_comparative,
                'include_ytd': include_ytd
            }
        }
        
        # Define income statement sections
        sections = [
            {
                'name': 'Revenue',
                'account_types': [AccountType.REVENUE.value],
                'is_debit_positive': False,
                'show_subtotals': True
            },
            {
                'name': 'Cost of Goods Sold',
                'account_types': [AccountType.COST_OF_GOODS_SOLD.value],
                'is_debit_positive': True,
                'show_subtotals': True
            },
            {
                'name': 'Operating Expenses',
                'account_types': [
                    AccountType.EXPENSE_OPERATING.value,
                    AccountType.EXPENSE_DEPRECIATION.value,
                    AccountType.EXPENSE_AMORTIZATION.value
                ],
                'is_debit_positive': True,
                'show_subtotals': True
            },
            {
                'name': 'Other Income/Expense',
                'account_types': [
                    AccountType.REVENUE_OTHER.value,
                    AccountType.EXPENSE_OTHER.value,
                    AccountType.EXPENSE_INTEREST.value,
                    AccountType.EXPENSE_TAX.value
                ],
                'is_debit_positive': True,
                'show_subtotals': True
            }
        ]
        
        # Process each section
        for section in sections:
            section_data = {
                'name': section['name'],
                'total': Decimal('0'),
                'lines': [],
                'subtotals': {},
                'show_subtotals': section.get('show_subtotals', False)
            }
            
            if include_comparative and prev_balances:
                section_data['total_prev'] = Decimal('0')
            
            if include_ytd and ytd_balances:
                section_data['total_ytd'] = Decimal('0')
            
            # Process each account type in the section
            for account_type in section['account_types']:
                accounts = self._get_accounts_by_type(account_type)
                type_total = Decimal('0')
                type_prev_total = Decimal('0')
                type_ytd_total = Decimal('0')
                
                for account in accounts:
                    # Get current period balance
                    balance = current_balances.get(account.id, {
                        'account_id': account.id,
                        'account_code': account.code,
                        'account_name': account.name,
                        'balance': Decimal('0')
                    })
                    
                    # Get previous period balance if available
                    prev_balance = prev_balances.get(account.id, {
                        'balance': Decimal('0')
                    }) if include_comparative and prev_balances else None
                    
                    # Get YTD balance if available
                    ytd_balance = ytd_balances.get(account.id, {
                        'balance': Decimal('0')
                    }) if include_ytd and ytd_balances else None
                    
                    # Calculate the balance based on account type
                    if section['is_debit_positive']:
                        current_balance = balance['balance']
                        prev_balance_val = prev_balance['balance'] if prev_balance else Decimal('0')
                        ytd_balance_val = ytd_balance['balance'] if ytd_balance else Decimal('0')
                    else:
                        current_balance = -balance['balance']
                        prev_balance_val = -prev_balance['balance'] if prev_balance else Decimal('0')
                        ytd_balance_val = -ytd_balance['balance'] if ytd_balance else Decimal('0')
                    
                    # Add to type total
                    type_total += current_balance
                    if include_comparative and prev_balances:
                        type_prev_total += prev_balance_val
                    if include_ytd and ytd_balances:
                        type_ytd_total += ytd_balance_val
                    
                    # Add account line if balance is not zero
                    if current_balance != 0 or (include_comparative and prev_balance_val != 0) or (include_ytd and ytd_balance_val != 0):
                        line = {
                            'account_id': str(account.id),
                            'account_code': account.code,
                            'account_name': account.name,
                            'amount': self._format_amount(current_balance, format_currency, currency),
                            'is_header': False
                        }
                        
                        if include_comparative and prev_balances:
                            line['amount_prev'] = self._format_amount(prev_balance_val, format_currency, currency)
                        
                        if include_ytd and ytd_balances:
                            line['amount_ytd'] = self._format_amount(ytd_balance_val, format_currency, currency)
                        
                        section_data['lines'].append(line)
                
                # Add account type subtotal if there are accounts
                if accounts and section['show_subtotals']:
                    subtotal = {
                        'name': f"Total {account_type.replace('_', ' ').title()}",
                        'amount': self._format_amount(type_total, format_currency, currency),
                        'is_subtotal': True
                    }
                    
                    if include_comparative and prev_balances:
                        subtotal['amount_prev'] = self._format_amount(type_prev_total, format_currency, currency)
                    
                    if include_ytd and ytd_balances:
                        subtotal['amount_ytd'] = self._format_amount(type_ytd_total, format_currency, currency)
                    
                    section_data['lines'].append(subtotal)
                    
                    section_data['total'] += type_total
                    if include_comparative and prev_balances:
                        section_data['total_prev'] += type_prev_total
                    if include_ytd and ytd_balances:
                        section_data['total_ytd'] += type_ytd_total
                    
                    section_data['subtotals'][account_type] = {
                        'current': type_total,
                        'previous': type_prev_total if include_comparative and prev_balances else None,
                        'ytd': type_ytd_total if include_ytd and ytd_balances else None
                    }
            
            # Only add the section if it has lines or we want to show empty sections
            if section_data['lines'] or section.get('show_empty', False):
                # Format section total
                section_data['total'] = self._format_amount(section_data['total'], format_currency, currency)
                if include_comparative and prev_balances:
                    section_data['total_prev'] = self._format_amount(section_data['total_prev'], format_currency, currency)
                if include_ytd and ytd_balances:
                    section_data['total_ytd'] = self._format_amount(section_data['total_ytd'], format_currency, currency)
                
                income_statement['sections'].append(section_data)
        
        # Calculate gross profit, operating profit, and net profit
        self._calculate_income_statement_totals(income_statement, format_currency, currency)
        
        return income_statement
    
    def _get_first_period_of_fiscal_year(self, fiscal_year: str) -> Optional[GLPeriod]:
        """
        Get the first period of a fiscal year.
        
        Args:
            fiscal_year: The fiscal year (e.g., 'FY2023')
            
        Returns:
            The first GLPeriod of the fiscal year, or None if not found
        """
        return (
            self.db.query(GLPeriod)
            .filter(GLPeriod.fiscal_year == fiscal_year)
            .order_by(GLPeriod.start_date.asc())
            .first()
        )
    
    def _get_account_balances_for_date_range(
        self, 
        start_date: date, 
        end_date: date,
        account_ids: Optional[List[UUID]] = None
    ) -> Dict[UUID, Dict[str, Any]]:
        """
        Get account balances for a date range by aggregating journal entries.
        
        Args:
            start_date: Start date of the period
            end_date: End date of the period
            account_ids: Optional list of account IDs to filter by
            
        Returns:
            Dictionary mapping account IDs to balance information
        """
        # Start with a query to get all relevant journal entry lines
        query = (
            self.db.query(
                JournalEntryLine.account_id,
                func.sum(
                    case(
                        [(JournalEntryLine.is_debit == True, JournalEntryLine.amount)],
                        else_=JournalEntryLine.amount * -1
                    )
                ).label('balance')
            )
            .join(JournalEntry, JournalEntry.id == JournalEntryLine.journal_entry_id)
            .filter(
                JournalEntry.entry_date >= start_date,
                JournalEntry.entry_date <= end_date,
                JournalEntry.status == JournalEntryStatus.POSTED
            )
            .group_by(JournalEntryLine.account_id)
        )
        
        # Filter by account IDs if provided
        if account_ids:
            query = query.filter(JournalEntryLine.account_id.in_(account_ids))
        
        # Execute the query
        results = query.all()
        
        # Get account details for the balances
        account_ids = [r[0] for r in results]
        accounts = {a.id: a for a in self.db.query(Account).filter(Account.id.in_(account_ids)).all()}
        
        # Prepare the result dictionary
        balances = {}
        for account_id, balance in results:
            account = accounts.get(account_id)
            if account:
                balances[account_id] = {
                    'account_id': account_id,
                    'account_code': account.code,
                    'account_name': account.name,
                    'balance': balance or Decimal('0')
                }
        
        return balances
    
    def _calculate_income_statement_totals(
        self, 
        income_statement: Dict[str, Any],
        format_currency: bool,
        currency: str
    ) -> None:
        """
        Calculate and add summary totals to the income statement.
        
        Args:
            income_statement: The income statement data
            format_currency: Whether to format numbers as currency strings
            currency: The currency code
        """
        # Get section totals
        revenue_section = next((s for s in income_statement['sections'] if s['name'] == 'Revenue'), None)
        cogs_section = next((s for s in income_statement['sections'] if s['name'] == 'Cost of Goods Sold'), None)
        op_expenses_section = next((s for s in income_statement['sections'] if s['name'] == 'Operating Expenses'), None)
        other_section = next((s for s in income_statement['sections'] if s['name'] == 'Other Income/Expense'), None)
        
        # Calculate totals
        if revenue_section and cogs_section:
            # Gross Profit
            total_revenue = self._parse_amount(revenue_section['total'])
            total_cogs = self._parse_amount(cogs_section['total'])
            gross_profit = total_revenue - total_cogs
            
            income_statement['gross_profit'] = {
                'name': 'Gross Profit',
                'amount': self._format_amount(gross_profit, format_currency, currency)
            }
            
            # Operating Income
            total_op_expenses = self._parse_amount(op_expenses_section['total']) if op_expenses_section else Decimal('0')
            operating_income = gross_profit - total_op_expenses
            
            income_statement['operating_income'] = {
                'name': 'Operating Income',
                'amount': self._format_amount(operating_income, format_currency, currency)
            }
            
            # Net Income
            total_other = self._parse_amount(other_section['total']) if other_section else Decimal('0')
            net_income = operating_income - total_other
            
            income_statement['net_income'] = {
                'name': 'Net Income',
                'amount': self._format_amount(net_income, format_currency, currency)
            }
            
            # Add comparative figures if available
            if 'total_prev' in revenue_section:
                total_revenue_prev = self._parse_amount(revenue_section['total_prev'])
                total_cogs_prev = self._parse_amount(cogs_section['total_prev'])
                gross_profit_prev = total_revenue_prev - total_cogs_prev
                
                income_statement['gross_profit']['amount_prev'] = self._format_amount(
                    gross_profit_prev, format_currency, currency
                )
                
                total_op_expenses_prev = (
                    self._parse_amount(op_expenses_section['total_prev']) 
                    if op_expenses_section and 'total_prev' in op_expenses_section 
                    else Decimal('0')
                )
                operating_income_prev = gross_profit_prev - total_op_expenses_prev
                
                income_statement['operating_income']['amount_prev'] = self._format_amount(
                    operating_income_prev, format_currency, currency
                )
                
                total_other_prev = (
                    self._parse_amount(other_section['total_prev']) 
                    if other_section and 'total_prev' in other_section 
                    else Decimal('0')
                )
                net_income_prev = operating_income_prev - total_other_prev
                
                income_statement['net_income']['amount_prev'] = self._format_amount(
                    net_income_prev, format_currency, currency
                )
            
            # Add YTD figures if available
            if 'total_ytd' in revenue_section:
                total_revenue_ytd = self._parse_amount(revenue_section['total_ytd'])
                total_cogs_ytd = self._parse_amount(cogs_section['total_ytd'])
                gross_profit_ytd = total_revenue_ytd - total_cogs_ytd
                
                income_statement['gross_profit']['amount_ytd'] = self._format_amount(
                    gross_profit_ytd, format_currency, currency
                )
                
                total_op_expenses_ytd = (
                    self._parse_amount(op_expenses_section['total_ytd']) 
                    if op_expenses_section and 'total_ytd' in op_expenses_section 
                    else Decimal('0')
                )
                operating_income_ytd = gross_profit_ytd - total_op_expenses_ytd
                
                income_statement['operating_income']['amount_ytd'] = self._format_amount(
                    operating_income_ytd, format_currency, currency
                )
                
                total_other_ytd = (
                    self._parse_amount(other_section['total_ytd']) 
                    if other_section and 'total_ytd' in other_section 
                    else Decimal('0')
                )
                net_income_ytd = operating_income_ytd - total_other_ytd
                
                income_statement['net_income']['amount_ytd'] = self._format_amount(
                    net_income_ytd, format_currency, currency
                )
    
    def generate_balance_sheet(
        self,
        as_of_date: date,
        currency: str = 'USD',
        include_comparative: bool = False,
        format_currency: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a balance sheet as of a specific date.
        
        Args:
            as_of_date: The date to generate the balance sheet for
            currency: The reporting currency
            include_comparative: Whether to include prior period comparison
            format_currency: Whether to format numbers as currency strings
            
        Returns:
            Dictionary containing the balance sheet data
        """
        # Get the period for the as_of_date
        period = self.period_service.get_period_for_date(as_of_date)
        if not period:
            raise PeriodNotFoundException(
                f"Could not find period for date {as_of_date}"
            )
        
        # Get the previous period for comparison if requested
        prev_period = None
        if include_comparative:
            prev_period = self._get_previous_period(period)
        
        # Get the start date of the fiscal year for YTD calculations
        fiscal_year_start = self._get_first_period_of_fiscal_year(period.fiscal_year)
        fiscal_year_start_date = fiscal_year_start.start_date if fiscal_year_start else period.start_date
        
        # Get balances for assets, liabilities, and equity
        current_balances = self._get_account_balances_as_of_date(as_of_date)
        
        # Get previous period balances if needed
        prev_balances = {}
        if include_comparative and prev_period:
            prev_balances = self._get_account_balances_as_of_date(prev_period.end_date)
        
        # Get YTD income/loss for the fiscal year
        ytd_income_loss = Decimal('0')
        ytd_balances = self._get_account_balances_for_date_range(
            fiscal_year_start_date,
            as_of_date
        )
        
        # Calculate YTD income/loss (revenue - expenses)
        for account_id, balance in ytd_balances.items():
            account = self.db.query(Account).get(account_id)
            if not account:
                continue
                
            # Revenue accounts (credit balance is positive)
            if account.account_type in [
                AccountType.REVENUE.value,
                AccountType.REVENUE_OTHER.value
            ]:
                ytd_income_loss += balance['balance']
            # Expense accounts (debit balance is positive)
            elif account.account_type in [
                AccountType.EXPENSE_OPERATING.value,
                AccountType.EXPENSE_DEPRECIATION.value,
                AccountType.EXPENSE_AMORTIZATION.value,
                AccountType.EXPENSE_OTHER.value,
                AccountType.EXPENSE_INTEREST.value,
                AccountType.EXPENSE_TAX.value,
                AccountType.COST_OF_GOODS_SOLD.value
            ]:
                ytd_income_loss -= balance['balance']
        
        # Prepare the balance sheet structure
        balance_sheet = {
            'type': FinancialStatementType.BALANCE_SHEET.value,
            'as_of_date': as_of_date.isoformat(),
            'currency': currency,
            'period': {
                'id': str(period.id),
                'name': period.name,
                'start_date': period.start_date.isoformat(),
                'end_date': period.end_date.isoformat(),
                'fiscal_year': period.fiscal_year
            },
            'sections': [],
            'metadata': {
                'generated_at': datetime.utcnow().isoformat(),
                'include_comparative': include_comparative
            }
        }
        
        # Define balance sheet sections
        sections = [
            {
                'name': 'Assets',
                'account_types': [
                    AccountType.ASSET_CURRENT.value,
                    AccountType.ASSET_FIXED.value,
                    AccountType.ASSET_ACCUMULATED_DEPRECIATION.value,
                    AccountType.ASSET_INTANGIBLE.value,
                    AccountType.ASSET_ACCUMULATED_AMORTIZATION.value,
                    AccountType.ASSET_OTHER.value
                ],
                'is_debit_positive': True,
                'show_subtotals': True,
                'show_totals': True
            },
            {
                'name': 'Liabilities',
                'account_types': [
                    AccountType.LIABILITY_CURRENT.value,
                    AccountType.LIABILITY_LONG_TERM.value,
                    AccountType.LIABILITY_OTHER.value
                ],
                'is_debit_positive': False,
                'show_subtotals': True,
                'show_totals': True
            },
            {
                'name': 'Equity',
                'account_types': [
                    AccountType.EQUITY.value,
                    AccountType.EQUITY_RETAINED_EARNINGS.value,
                    AccountType.EQUITY_DIVIDENDS.value
                ],
                'is_debit_positive': False,
                'show_subtotals': True,
                'show_totals': True,
                'include_ytd_income': True
            }
        ]
        
        # Process each section
        for section in sections:
            section_data = {
                'name': section['name'],
                'total': Decimal('0'),
                'lines': [],
                'subtotals': {},
                'show_subtotals': section.get('show_subtotals', False),
                'show_totals': section.get('show_totals', False)
            }
            
            if include_comparative and prev_balances:
                section_data['total_prev'] = Decimal('0')
            
            # Process each account type in the section
            for account_type in section['account_types']:
                accounts = self._get_accounts_by_type(account_type)
                type_total = Decimal('0')
                type_prev_total = Decimal('0')
                
                for account in accounts:
                    # Get current period balance
                    balance = current_balances.get(account.id, {
                        'account_id': account.id,
                        'account_code': account.code,
                        'account_name': account.name,
                        'balance': Decimal('0')
                    })
                    
                    # Get previous period balance if available
                    prev_balance = prev_balances.get(account.id, {
                        'balance': Decimal('0')
                    }) if include_comparative and prev_balances else None
                    
                    # Calculate the balance based on account type
                    if section['is_debit_positive']:
                        current_balance = balance['balance']
                        prev_balance_val = prev_balance['balance'] if prev_balance else Decimal('0')
                    else:
                        current_balance = -balance['balance']
                        prev_balance_val = -prev_balance['balance'] if prev_balance else Decimal('0')
                    
                    # Add to type total
                    type_total += current_balance
                    if include_comparative and prev_balances:
                        type_prev_total += prev_balance_val
                    
                    # Add account line if balance is not zero
                    if current_balance != 0 or (include_comparative and prev_balance_val != 0):
                        line = {
                            'account_id': str(account.id),
                            'account_code': account.code,
                            'account_name': account.name,
                            'amount': self._format_amount(current_balance, format_currency, currency),
                            'is_header': False
                        }
                        
                        if include_comparative and prev_balances:
                            line['amount_prev'] = self._format_amount(prev_balance_val, format_currency, currency)
                        
                        section_data['lines'].append(line)
                
                # Add account type subtotal if there are accounts
                if accounts and section['show_subtotals']:
                    subtotal = {
                        'name': f"Total {account_type.replace('_', ' ').title()}",
                        'amount': self._format_amount(type_total, format_currency, currency),
                        'is_subtotal': True
                    }
                    
                    if include_comparative and prev_balances:
                        subtotal['amount_prev'] = self._format_amount(type_prev_total, format_currency, currency)
                    
                    section_data['lines'].append(subtotal)
                    
                    section_data['total'] += type_total
                    if include_comparative and prev_balances:
                        section_data['total_prev'] += type_prev_total
                    
                    section_data['subtotals'][account_type] = {
                        'current': type_total,
                        'previous': type_prev_total if include_comparative and prev_balances else None
                    }
            
            # Add YTD income/loss to equity section
            if section['name'] == 'Equity' and section.get('include_ytd_income', False):
                # Add a line for current year earnings/loss
                ytd_line = {
                    'name': 'Current Year Earnings/Loss',
                    'amount': self._format_amount(ytd_income_loss, format_currency, currency),
                    'is_header': False,
                    'is_ytd_income': True
                }
                
                # Add to the section total
                section_data['total'] += ytd_income_loss
                
                # Add the line to the section
                section_data['lines'].append(ytd_line)
                
                # Add a subtotal after YTD income/loss
                subtotal = {
                    'name': 'Total Equity',
                    'amount': self._format_amount(section_data['total'], format_currency, currency),
                    'is_subtotal': True
                }
                
                if include_comparative and prev_balances:
                    subtotal['amount_prev'] = self._format_amount(
                        section_data.get('total_prev', Decimal('0')), 
                        format_currency, 
                        currency
                    )
                
                section_data['lines'].append(subtotal)
            
            # Only add the section if it has lines or we want to show empty sections
            if section_data['lines'] or section.get('show_empty', False):
                # Format section total
                if section_data.get('show_totals', False):
                    section_data['total'] = self._format_amount(section_data['total'], format_currency, currency)
                    if include_comparative and prev_balances and 'total_prev' in section_data:
                        section_data['total_prev'] = self._format_amount(
                            section_data['total_prev'], 
                            format_currency, 
                            currency
                        )
                
                balance_sheet['sections'].append(section_data)
        
        # Calculate total assets, liabilities, and equity
        self._calculate_balance_sheet_totals(balance_sheet, format_currency, currency)
        
        return balance_sheet
    
    def _get_account_balances_as_of_date(
        self, 
        as_of_date: date,
        account_ids: Optional[List[UUID]] = None
    ) -> Dict[UUID, Dict[str, Any]]:
        """
        Get account balances as of a specific date by aggregating journal entries.
        
        Args:
            as_of_date: The date to get balances as of
            account_ids: Optional list of account IDs to filter by
            
        Returns:
            Dictionary mapping account IDs to balance information
        """
        # Start with a query to get all relevant journal entry lines
        query = (
            self.db.query(
                JournalEntryLine.account_id,
                func.sum(
                    case(
                        [(JournalEntryLine.is_debit == True, JournalEntryLine.amount)],
                        else_=JournalEntryLine.amount * -1
                    )
                ).label('balance')
            )
            .join(JournalEntry, JournalEntry.id == JournalEntryLine.journal_entry_id)
            .filter(
                JournalEntry.entry_date <= as_of_date,
                JournalEntry.status == JournalEntryStatus.POSTED
            )
            .group_by(JournalEntryLine.account_id)
        )
        
        # Filter by account IDs if provided
        if account_ids:
            query = query.filter(JournalEntryLine.account_id.in_(account_ids))
        
        # Execute the query
        results = query.all()
        
        # Get account details for the balances
        account_ids = [r[0] for r in results] if results else []
        accounts = {}
        if account_ids:
            accounts = {a.id: a for a in self.db.query(Account).filter(Account.id.in_(account_ids)).all()}
        
        # Prepare the result dictionary
        balances = {}
        for account_id, balance in results:
            account = accounts.get(account_id)
            if account:
                balances[account_id] = {
                    'account_id': account_id,
                    'account_code': account.code,
                    'account_name': account.name,
                    'balance': balance or Decimal('0')
                }
        
        return balances
    
    def _calculate_balance_sheet_totals(
        self, 
        balance_sheet: Dict[str, Any],
        format_currency: bool,
        currency: str
    ) -> None:
        """
        Calculate and add summary totals to the balance sheet.
        
        Args:
            balance_sheet: The balance sheet data
            format_currency: Whether to format numbers as currency strings
            currency: The currency code
        """
        # Get section totals
        assets_section = next((s for s in balance_sheet['sections'] if s['name'] == 'Assets'), None)
        liabilities_section = next((s for s in balance_sheet['sections'] if s['name'] == 'Liabilities'), None)
        equity_section = next((s for s in balance_sheet['sections'] if s['name'] == 'Equity'), None)
        
        # Calculate totals if all sections exist
        if assets_section and liabilities_section and equity_section:
            # Total Assets
            total_assets = self._parse_amount(assets_section['total'])
            
            # Total Liabilities
            total_liabilities = self._parse_amount(liabilities_section['total'])
            
            # Total Equity
            total_equity = self._parse_amount(equity_section['total'])
            
            # Total Liabilities and Equity
            total_liab_equity = total_liabilities + total_equity
            
            # Add to balance sheet
            balance_sheet['total_assets'] = {
                'name': 'Total Assets',
                'amount': self._format_amount(total_assets, format_currency, currency)
            }
            
            balance_sheet['total_liabilities'] = {
                'name': 'Total Liabilities',
                'amount': self._format_amount(total_liabilities, format_currency, currency)
            }
            
            balance_sheet['total_equity'] = {
                'name': 'Total Equity',
                'amount': self._format_amount(total_equity, format_currency, currency)
            }
            
            balance_sheet['total_liabilities_equity'] = {
                'name': 'Total Liabilities and Equity',
                'amount': self._format_amount(total_liab_equity, format_currency, currency)
            }
            
            # Check if assets equal liabilities + equity (should balance)
            balance_sheet['is_balanced'] = abs(total_assets - total_liab_equity) < Decimal('0.01')
            
            # Add comparative figures if available
            if 'total_prev' in assets_section:
                total_assets_prev = self._parse_amount(assets_section['total_prev'])
                total_liabilities_prev = self._parse_amount(liabilities_section['total_prev'])
                total_equity_prev = self._parse_amount(equity_section['total_prev'])
                total_liab_equity_prev = total_liabilities_prev + total_equity_prev
                
                balance_sheet['total_assets']['amount_prev'] = self._format_amount(
                    total_assets_prev, format_currency, currency
                )
                
                balance_sheet['total_liabilities']['amount_prev'] = self._format_amount(
                    total_liabilities_prev, format_currency, currency
                )
                
                balance_sheet['total_equity']['amount_prev'] = self._format_amount(
                    total_equity_prev, format_currency, currency
                )
                
                balance_sheet['total_liabilities_equity']['amount_prev'] = self._format_amount(
                    total_liab_equity_prev, format_currency, currency
                )
                
                balance_sheet['is_balanced_prev'] = abs(total_assets_prev - total_liab_equity_prev) < Decimal('0.01')
    
    def _get_accounts_by_type(self, account_type: str) -> List[Account]:
        """
        Get all accounts of a specific type.
        
        Args:
            account_type: The account type to filter by
            
        Returns:
            List of Account objects
        """
        return (
            self.db.query(Account)
            .filter(Account.account_type == account_type)
            .order_by(Account.code)
            .all()
        )
    
    def generate_cash_flow_statement(
        self,
        start_date: date,
        end_date: date,
        currency: str = 'USD',
        include_comparative: bool = False,
        format_currency: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a cash flow statement for a date range using the indirect method.
        
        Args:
            start_date: Start date of the period
            end_date: End date of the period
            currency: The reporting currency
            include_comparative: Whether to include prior period comparison
            format_currency: Whether to format numbers as currency strings
            
        Returns:
            Dictionary containing the cash flow statement data
        """
        # Get the periods for the date range
        start_period = self.period_service.get_period_for_date(start_date)
        end_period = self.period_service.get_period_for_date(end_date)
        
        if not start_period or not end_period:
            raise PeriodNotFoundException(
                f"Could not find periods for the date range {start_date} to {end_date}"
            )
        
        # Get the previous period for comparison if requested
        prev_start_period = None
        prev_end_period = None
        
        if include_comparative:
            prev_start_period = self._get_previous_period(start_period)
            prev_end_period = self._get_previous_period(end_period)
        
        # Get the start date of the fiscal year for YTD calculations
        fiscal_year_start = self._get_first_period_of_fiscal_year(start_period.fiscal_year)
        fiscal_year_start_date = fiscal_year_start.start_date if fiscal_year_start else start_period.start_date
        
        # Get balances for the current and previous periods
        current_balances = self._get_account_balances_as_of_date(end_date)
        beginning_balances = self._get_account_balances_as_of_date(start_date - timedelta(days=1))
        
        # Get previous period balances if needed
        prev_balances = {}
        prev_beginning_balances = {}
        if include_comparative and prev_start_period and prev_end_period:
            prev_balances = self._get_account_balances_as_of_date(prev_end_period.end_date)
            prev_beginning_balances = self._get_account_balances_as_of_date(prev_start_period.start_date - timedelta(days=1))
        
        # Get all journal entries for the period
        journal_entries = self._get_journal_entries_for_date_range(start_date, end_date)
        
        # Get all accounts for categorization
        all_accounts = {a.id: a for a in self.db.query(Account).all()}
        
        # Categorize accounts
        cash_accounts = [
            a for a in all_accounts.values() 
            if a.account_type == AccountType.ASSET_CURRENT.value 
            and 'cash' in a.name.lower()
        ]
        
        if not cash_accounts:
            raise ValueError("No cash accounts found. Please ensure you have at least one cash account configured.")
        
        # Prepare the cash flow statement structure
        cash_flow = {
            'type': FinancialStatementType.CASH_FLOW.value,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'currency': currency,
            'period': {
                'id': str(start_period.id) if start_period.id == end_period.id else None,
                'name': start_period.name if start_period.id == end_period.id else f"{start_period.name} to {end_period.name}",
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'fiscal_year': start_period.fiscal_year
            },
            'sections': [],
            'metadata': {
                'generated_at': datetime.utcnow().isoformat(),
                'include_comparative': include_comparative,
                'method': 'indirect'
            }
        }
        
        # Define cash flow sections
        sections = [
            {
                'name': 'Cash Flows from Operating Activities',
                'is_operating': True,
                'is_financing': False,
                'is_investing': False,
                'show_subtotals': True,
                'show_totals': True
            },
            {
                'name': 'Cash Flows from Investing Activities',
                'is_operating': False,
                'is_financing': False,
                'is_investing': True,
                'show_subtotals': True,
                'show_totals': True
            },
            {
                'name': 'Cash Flows from Financing Activities',
                'is_operating': False,
                'is_financing': True,
                'is_investing': False,
                'show_subtotals': True,
                'show_totals': True
            },
            {
                'name': 'Net Increase (Decrease) in Cash and Cash Equivalents',
                'is_operating': False,
                'is_financing': False,
                'is_investing': False,
                'show_subtotals': False,
                'show_totals': True
            }
        ]
        
        # Initialize section data
        section_data = {}
        for section in sections:
            section_data[section['name']] = {
                'name': section['name'],
                'total': Decimal('0'),
                'lines': [],
                'subtotals': {},
                'show_subtotals': section.get('show_subtotals', False),
                'show_totals': section.get('show_totals', False)
            }
            
            if include_comparative:
                section_data[section['name']]['total_prev'] = Decimal('0')
        
        # 1. Start with net income from the income statement
        income_statement = self.generate_income_statement(
            start_date, 
            end_date, 
            currency=currency, 
            include_comparative=include_comparative,
            format_currency=format_currency
        )
        
        net_income = self._parse_amount(income_statement['net_income']['amount'])
        
        # Add net income to operating activities
        section_data['Cash Flows from Operating Activities']['lines'].append({
            'name': 'Net Income',
            'amount': self._format_amount(net_income, format_currency, currency),
            'is_header': False,
            'is_net_income': True
        })
        
        section_data['Cash Flows from Operating Activities']['total'] += net_income
        
        # Add comparative net income if needed
        if include_comparative and 'net_income' in income_statement and 'amount_prev' in income_statement['net_income']:
            net_income_prev = self._parse_amount(income_statement['net_income']['amount_prev'])
            section_data['Cash Flows from Operating Activities']['lines'][-1]['amount_prev'] = \
                self._format_amount(net_income_prev, format_currency, currency)
            section_data['Cash Flows from Operating Activities']['total_prev'] += net_income_prev
        
        # 2. Add adjustments for non-cash items and changes in working capital
        # This is a simplified version - in a real app, you'd have more sophisticated logic
        
        # Depreciation and amortization
        deprec_amort = self._calculate_depreciation_amortization(start_date, end_date)
        if deprec_amort != 0:
            section_data['Cash Flows from Operating Activities']['lines'].append({
                'name': 'Depreciation and Amortization',
                'amount': self._format_amount(deprec_amort, format_currency, currency),
                'is_header': False,
                'is_adjustment': True
            })
            section_data['Cash Flows from Operating Activities']['total'] += deprec_amort
        
        # Changes in working capital accounts
        working_capital_changes = self._calculate_working_capital_changes(
            beginning_balances,
            current_balances,
            all_accounts
        )
        
        for change in working_capital_changes:
            section_data['Cash Flows from Operating Activities']['lines'].append({
                'name': change['name'],
                'amount': self._format_amount(change['amount'], format_currency, currency),
                'is_header': False,
                'is_working_capital': True
            })
            section_data['Cash Flows from Operating Activities']['total'] += change['amount']
        
        # 3. Calculate cash flows from investing activities
        investing_activities = self._calculate_investing_activities(
            journal_entries, 
            all_accounts
        )
        
        for activity in investing_activities:
            section_data['Cash Flows from Investing Activities']['lines'].append({
                'name': activity['name'],
                'amount': self._format_amount(activity['amount'], format_currency, currency),
                'is_header': False
            })
            section_data['Cash Flows from Investing Activities']['total'] += activity['amount']
        
        # 4. Calculate cash flows from financing activities
        financing_activities = self._calculate_financing_activities(
            journal_entries, 
            all_accounts
        )
        
        for activity in financing_activities:
            section_data['Cash Flows from Financing Activities']['lines'].append({
                'name': activity['name'],
                'amount': self._format_amount(activity['amount'], format_currency, currency),
                'is_header': False
            })
            section_data['Cash Flows from Financing Activities']['total'] += activity['amount']
        
        # 5. Calculate net increase (decrease) in cash
        operating_cash_flow = section_data['Cash Flows from Operating Activities']['total']
        investing_cash_flow = section_data['Cash Flows from Investing Activities']['total']
        financing_cash_flow = section_data['Cash Flows from Financing Activities']['total']
        
        net_cash_flow = operating_cash_flow + investing_cash_flow + financing_cash_flow
        
        # Add net increase (decrease) in cash
        section_data['Net Increase (Decrease) in Cash and Cash Equivalents']['lines'].append({
            'name': 'Net Increase (Decrease) in Cash and Cash Equivalents',
            'amount': self._format_amount(net_cash_flow, format_currency, currency),
            'is_header': False,
            'is_net_change': True
        })
        section_data['Net Increase (Decrease) in Cash and Cash Equivalents']['total'] = net_cash_flow
        
        # Add beginning and ending cash balances
        beginning_cash = sum(beginning_balances.get(a.id, {'balance': Decimal('0')})['balance'] for a in cash_accounts)
        ending_cash = sum(current_balances.get(a.id, {'balance': Decimal('0')})['balance'] for a in cash_accounts)
        
        section_data['Net Increase (Decrease) in Cash and Cash Equivalents']['lines'].extend([
            {
                'name': 'Cash and Cash Equivalents at Beginning of Period',
                'amount': self._format_amount(beginning_cash, format_currency, currency),
                'is_header': False,
                'is_balance': True
            },
            {
                'name': 'Cash and Cash Equivalents at End of Period',
                'amount': self._format_amount(ending_cash, format_currency, currency),
                'is_header': False,
                'is_balance': True,
                'is_ending_balance': True
            }
        ])
        
        # Add comparative data if needed
        if include_comparative and prev_balances and prev_beginning_balances:
            # Calculate previous period cash flows
            prev_operating = section_data['Cash Flows from Operating Activities']['total_prev']
            prev_investing = section_data['Cash Flows from Investing Activities']['total_prev']
            prev_financing = section_data['Cash Flows from Financing Activities']['total_prev']
            prev_net_cash_flow = prev_operating + prev_investing + prev_financing
            
            # Add to net change in cash
            section_data['Net Increase (Decrease) in Cash and Cash Equivalents']['lines'][0]['amount_prev'] = \
                self._format_amount(prev_net_cash_flow, format_currency, currency)
            
            # Add beginning and ending balances for previous period
            prev_beginning_cash = sum(
                prev_beginning_balances.get(a.id, {'balance': Decimal('0')})['balance'] 
                for a in cash_accounts
            )
            prev_ending_cash = sum(
                prev_balances.get(a.id, {'balance': Decimal('0')})['balance'] 
                for a in cash_accounts
            )
            
            section_data['Net Increase (Decrease) in Cash and Cash Equivalents']['lines'][1]['amount_prev'] = \
                self._format_amount(prev_beginning_cash, format_currency, currency)
            section_data['Net Increase (Decrease) in Cash and Cash Equivalents']['lines'][2]['amount_prev'] = \
                self._format_amount(prev_ending_cash, format_currency, currency)
        
        # Add all sections to the cash flow statement
        for section in sections:
            section_name = section['name']
            if section_name in section_data and (
                section_data[section_name]['lines'] or 
                section.get('show_empty', False)
            ):
                # Format section total if needed
                if section_data[section_name].get('show_totals', False):
                    section_data[section_name]['total'] = self._format_amount(
                        section_data[section_name]['total'], 
                        format_currency, 
                        currency
                    )
                    
                    if include_comparative and 'total_prev' in section_data[section_name]:
                        section_data[section_name]['total_prev'] = self._format_amount(
                            section_data[section_name]['total_prev'],
                            format_currency,
                            currency
                        )
                
                cash_flow['sections'].append(section_data[section_name])
        
        return cash_flow
    
    def _calculate_depreciation_amortization(
        self, 
        start_date: date, 
        end_date: date
    ) -> Decimal:
        """
        Calculate total depreciation and amortization for a date range.
        
        Args:
            start_date: Start date of the period
            end_date: End date of the period
            
        Returns:
            Total depreciation and amortization as a Decimal
        """
        # Get all depreciation and amortization journal entries
        deprec_amort_entries = (
            self.db.query(JournalEntryLine)
            .join(Account, JournalEntryLine.account_id == Account.id)
            .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
            .filter(
                JournalEntry.entry_date >= start_date,
                JournalEntry.entry_date <= end_date,
                JournalEntry.status == JournalEntryStatus.POSTED,
                or_(
                    Account.account_type == AccountType.EXPENSE_DEPRECIATION.value,
                    Account.account_type == AccountType.EXPENSE_AMORTIZATION.value
                )
            )
            .all()
        )
        
        # Sum up all depreciation and amortization amounts
        total = Decimal('0')
        for entry in deprec_amort_entries:
            if entry.is_debit:
                total += entry.amount
            else:
                total -= entry.amount
        
        return total
    
    def _calculate_working_capital_changes(
        self,
        beginning_balances: Dict[UUID, Dict[str, Any]],
        ending_balances: Dict[UUID, Dict[str, Any]],
        all_accounts: Dict[UUID, Account]
    ) -> List[Dict[str, Any]]:
        """
        Calculate changes in working capital accounts.
        
        Args:
            beginning_balances: Account balances at the beginning of the period
            ending_balances: Account balances at the end of the period
            all_accounts: Dictionary of all accounts by ID
            
        Returns:
            List of working capital changes
        """
        changes = []
        
        # Define working capital account types
        working_capital_types = [
            AccountType.ASSET_CURRENT.value,
            AccountType.LIABILITY_CURRENT.value
        ]
        
        # Process each account
        for account_id, account in all_accounts.items():
            if account.account_type not in working_capital_types:
                continue
            
            # Skip cash accounts as they're handled separately
            if account.account_type == AccountType.ASSET_CURRENT.value and 'cash' in account.name.lower():
                continue
            
            # Get beginning and ending balances
            begin_balance = beginning_balances.get(account_id, {'balance': Decimal('0')})['balance']
            end_balance = ending_balances.get(account_id, {'balance': Decimal('0')})['balance']
            
            # Calculate change
            change = end_balance - begin_balance
            
            # For asset accounts, a positive change is a use of cash (negative adjustment)
            # For liability accounts, a positive change is a source of cash (positive adjustment)
            if account.account_type == AccountType.ASSET_CURRENT.value:
                change = -change
            
            # Only include if there's a change
            if change != 0:
                changes.append({
                    'name': f"Changes in {account.name}",
                    'amount': change,
                    'account_id': account_id,
                    'account_code': account.code,
                    'account_name': account.name
                })
        
        return changes
    
    def _calculate_investing_activities(
        self,
        journal_entries: List[JournalEntry],
        all_accounts: Dict[UUID, Account]
    ) -> List[Dict[str, Any]]:
        """
        Calculate cash flows from investing activities.
        
        Args:
            journal_entries: List of journal entries for the period
            all_accounts: Dictionary of all accounts by ID
            
        Returns:
            List of investing activities
        """
        activities = []
        
        # Define investing account types
        investing_types = [
            AccountType.ASSET_FIXED.value,
            AccountType.ASSET_INTANGIBLE.value,
            AccountType.INVESTMENT_SECURITIES.value,
            AccountType.INVESTMENT_EQUITY.value,
            AccountType.INVESTMENT_DEBT.value
        ]
        
        # Process each journal entry
        for entry in journal_entries:
            for line in entry.lines:
                account = all_accounts.get(line.account_id)
                if not account or account.account_type not in investing_types:
                    continue
                
                # Only consider cash transactions
                cash_line = next((l for l in entry.lines if 
                                all_accounts.get(l.account_id, Account()).account_type == AccountType.ASSET_CURRENT.value and 
                                'cash' in all_accounts.get(l.account_id, Account()).name.lower()), None)
                
                if not cash_line:
                    continue
                
                # Determine if this is an inflow or outflow of cash
                is_inflow = (cash_line.is_debit and line.is_credit) or (not cash_line.is_debit and not line.is_credit)
                amount = line.amount if is_inflow else -line.amount
                
                # Add to activities
                activity_name = f"{'Purchase' if amount < 0 else 'Proceeds from sale'} of {account.name}"
                activities.append({
                    'name': activity_name,
                    'amount': amount,
                    'account_id': account.id,
                    'account_code': account.code,
                    'account_name': account.name,
                    'journal_entry_id': str(entry.id),
                    'date': entry.entry_date.isoformat()
                })
        
        return activities
    
    def _calculate_financing_activities(
        self,
        journal_entries: List[JournalEntry],
        all_accounts: Dict[UUID, Account]
    ) -> List[Dict[str, Any]]:
        """
        Calculate cash flows from financing activities.
        
        Args:
            journal_entries: List of journal entries for the period
            all_accounts: Dictionary of all accounts by ID
            
        Returns:
            List of financing activities
        """
        activities = []
        
        # Define financing account types
        financing_types = [
            AccountType.LIABILITY_LONG_TERM.value,
            AccountType.EQUITY.value,
            AccountType.EQUITY_RETAINED_EARNINGS.value,
            AccountType.EQUITY_DIVIDENDS.value
        ]
        
        # Process each journal entry
        for entry in journal_entries:
            for line in entry.lines:
                account = all_accounts.get(line.account_id)
                if not account or account.account_type not in financing_types:
                    continue
                
                # Only consider cash transactions
                cash_line = next((l for l in entry.lines if 
                                all_accounts.get(l.account_id, Account()).account_type == AccountType.ASSET_CURRENT.value and 
                                'cash' in all_accounts.get(l.account_id, Account()).name.lower()), None)
                
                if not cash_line:
                    continue
                
                # Determine if this is an inflow or outflow of cash
                is_inflow = (cash_line.is_debit and line.is_credit) or (not cash_line.is_debit and not line.is_credit)
                amount = line.amount if is_inflow else -line.amount
                
                # Special handling for dividends (always an outflow)
                if account.account_type == AccountType.EQUITY_DIVIDENDS.value:
                    amount = -abs(amount)
                
                # Add to activities
                activity_name = account.name
                if 'loan' in account.name.lower() or 'debt' in account.name.lower():
                    activity_name = f"{'Repayment' if amount < 0 else 'Proceeds from'} {account.name}"
                elif 'dividend' in account.name.lower():
                    activity_name = f"Dividends paid"
                elif 'equity' in account.name.lower() and 'retained' not in account.name.lower():
                    activity_name = f"{'Repurchase' if amount < 0 else 'Proceeds from issuance of'} {account.name}"
                
                activities.append({
                    'name': activity_name,
                    'amount': amount,
                    'account_id': account.id,
                    'account_code': account.code,
                    'account_name': account.name,
                    'journal_entry_id': str(entry.id),
                    'date': entry.entry_date.isoformat()
                })
        
        return activities
    
    def _get_journal_entries_for_date_range(
        self,
        start_date: date,
        end_date: date
    ) -> List[JournalEntry]:
        """
        Get all journal entries for a date range.
        
        Args:
            start_date: Start date of the period
            end_date: End date of the period
            
        Returns:
            List of JournalEntry objects
        """
        return (
            self.db.query(JournalEntry)
            .options(joinedload(JournalEntry.lines))
            .filter(
                JournalEntry.entry_date >= start_date,
                JournalEntry.entry_date <= end_date,
                JournalEntry.status == JournalEntryStatus.POSTED
            )
            .order_by(JournalEntry.entry_date, JournalEntry.created_at)
            .all()
        )
