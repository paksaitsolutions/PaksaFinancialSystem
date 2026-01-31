"""
Paksa Financial System
Financial Statement Generator

This module provides a comprehensive service for generating all types of financial statements.
"""
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Any, Union, Tuple

from ...models import (
from ..gl.period_service import PeriodService
from .financial_statement_service import FinancialStatementService
from decimal import Decimal
from sqlalchemy import and_, or_, func, case, text, select
from sqlalchemy.orm import Session, joinedload
from uuid import UUID



    Account,
    AccountType,
    GLPeriod,
    JournalEntry,
    JournalEntryLine,
    JournalEntryStatus,
    FinancialStatement,
    FinancialStatementType,
    FinancialStatementSection,
    FinancialStatementLine
)


class FinancialStatementGenerator:
    """
    Service for generating comprehensive financial statements.
    """
    
    def __init__(self, db: Session):
        """  Init  ."""
        """Initialize the generator with a database session."""
        self.db = db
        self.fs_service = FinancialStatementService(db)
        self.period_service = PeriodService(db)
    
    def generate_all_statements(
        self,
        company_id: UUID,
        as_of_date: date,
        include_comparative: bool = True,
        include_ytd: bool = True,
        currency: str = 'USD',
        format_currency: bool = True,
        created_by: UUID = None
    ) -> Dict[str, Any]:
        """Generate All Statements."""
        """
        Generate all financial statements (balance sheet, income statement, cash flow)
        for a specific date.
        
        Args:
            company_id: The company ID
            as_of_date: The date to generate statements for
            include_comparative: Whether to include comparative figures
            include_ytd: Whether to include year-to-date figures
            currency: The reporting currency
            format_currency: Whether to format numbers as currency strings
            created_by: User ID who initiated the generation
            
        Returns:
            Dictionary containing all financial statements
        """
        # Get the period for the as_of_date
        period = self.period_service.get_period_for_date(as_of_date)
        if not period:
            raise ValueError(f"No accounting period found for date: {as_of_date}")
        
        # Get the start date of the period
        start_date = period.start_date
        
        # Get the previous period for comparison if requested
        prev_period = None
        if include_comparative:
            prev_period = self._get_previous_period(period)
        
        # Generate balance sheet
        balance_sheet = self.fs_service.generate_balance_sheet(
            as_of_date=as_of_date,
            currency=currency,
            include_comparative=include_comparative,
            format_currency=format_currency
        )
        
        # Generate income statement
        income_statement = self.fs_service.generate_income_statement(
            start_date=start_date,
            end_date=as_of_date,
            currency=currency,
            include_comparative=include_comparative,
            include_ytd=include_ytd,
            format_currency=format_currency
        )
        
        # Generate cash flow statement
        cash_flow = self.fs_service.generate_cash_flow_statement(
            start_date=start_date,
            end_date=as_of_date,
            currency=currency,
            include_comparative=include_comparative,
            format_currency=format_currency
        )
        
        # Save the generated statements to the database
        saved_statements = self._save_statements(
            company_id=company_id,
            balance_sheet=balance_sheet,
            income_statement=income_statement,
            cash_flow=cash_flow,
            period_id=period.id,
            created_by=created_by
        )
        
        return {
            "balance_sheet": balance_sheet,
            "income_statement": income_statement,
            "cash_flow": cash_flow,
            "saved_statements": saved_statements,
            "metadata": {
                "company_id": str(company_id),
                "as_of_date": as_of_date.isoformat(),
                "period_id": str(period.id),
                "period_name": period.name,
                "generated_at": datetime.utcnow().isoformat(),
                "include_comparative": include_comparative,
                "include_ytd": include_ytd,
                "currency": currency
            }
        }
    
    def _get_previous_period(self, period: GLPeriod) -> Optional[GLPeriod]:
        """ Get Previous Period."""
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
    
    def _save_statements(
        self,
        company_id: UUID,
        balance_sheet: Dict[str, Any],
        income_statement: Dict[str, Any],
        cash_flow: Dict[str, Any],
        period_id: UUID,
        created_by: UUID = None
    ) -> Dict[str, UUID]:
        """ Save Statements."""
        """
        Save the generated financial statements to the database.
        
        Args:
            company_id: The company ID
            balance_sheet: The generated balance sheet data
            income_statement: The generated income statement data
            cash_flow: The generated cash flow statement data
            period_id: The accounting period ID
            created_by: User ID who initiated the generation
            
        Returns:
            Dictionary mapping statement types to their IDs
        """
        # Create balance sheet record
        bs_record = FinancialStatement(
            company_id=company_id,
            statement_type=FinancialStatementType.BALANCE_SHEET,
            name=f"Balance Sheet as of {balance_sheet['as_of_date']}",
            start_date=None,  # Balance sheet doesn't have a start date
            end_date=datetime.fromisoformat(balance_sheet['as_of_date']).date(),
            period_id=period_id,
            is_final=False,
            statement_data=balance_sheet,
            generated_at=datetime.utcnow(),
            generated_by=created_by,
            created_by=created_by,
            updated_by=created_by
        )
        self.db.add(bs_record)
        
        # Create income statement record
        is_record = FinancialStatement(
            company_id=company_id,
            statement_type=FinancialStatementType.INCOME_STATEMENT,
            name=f"Income Statement for {income_statement['start_date']} to {income_statement['end_date']}",
            start_date=datetime.fromisoformat(income_statement['start_date']).date(),
            end_date=datetime.fromisoformat(income_statement['end_date']).date(),
            period_id=period_id,
            is_final=False,
            statement_data=income_statement,
            generated_at=datetime.utcnow(),
            generated_by=created_by,
            created_by=created_by,
            updated_by=created_by
        )
        self.db.add(is_record)
        
        # Create cash flow statement record
        cf_record = FinancialStatement(
            company_id=company_id,
            statement_type=FinancialStatementType.CASH_FLOW,
            name=f"Cash Flow Statement for {cash_flow['start_date']} to {cash_flow['end_date']}",
            start_date=datetime.fromisoformat(cash_flow['start_date']).date(),
            end_date=datetime.fromisoformat(cash_flow['end_date']).date(),
            period_id=period_id,
            is_final=False,
            statement_data=cash_flow,
            generated_at=datetime.utcnow(),
            generated_by=created_by,
            created_by=created_by,
            updated_by=created_by
        )
        self.db.add(cf_record)
        
        # Commit the changes
        self.db.flush()
        
        # Save sections and lines for each statement
        self._save_statement_structure(bs_record, created_by)
        self._save_statement_structure(is_record, created_by)
        self._save_statement_structure(cf_record, created_by)
        
        self.db.commit()
        
        return {
            "balance_sheet_id": bs_record.id,
            "income_statement_id": is_record.id,
            "cash_flow_id": cf_record.id
        }
    
    def _save_statement_structure(
        self,
        statement: FinancialStatement,
        created_by: UUID
    ) -> None:
        """ Save Statement Structure."""
        """
        Save the financial statement structure (sections and lines) to the database.
        
        Args:
            statement: The financial statement record
            created_by: User ID who created the statement
        """
        statement_data = statement.statement_data
        
        # Process each section
        for section_idx, section_data in enumerate(statement_data.get('sections', []), 1):
            # Create section record
            section = FinancialStatementSection(
                financial_statement_id=statement.id,
                name=section_data['name'],
                display_order=section_idx,
                created_by=created_by,
                updated_by=created_by
            )
            self.db.add(section)
            self.db.flush()  # Get the section ID
            
            # Process each line in the section
            for line_idx, line_data in enumerate(section_data.get('lines', []), 1):
                # Create line record
                line = FinancialStatementLine(
                    section_id=section.id,
                    account_id=line_data.get('account_id'),
                    account_code=line_data.get('account_code'),
                    description=line_data.get('account_name', line_data.get('name', '')),
                    amount=Decimal(str(line_data.get('amount', 0))),
                    display_order=line_idx,
                    is_total=line_data.get('is_total', False),
                    is_subtotal=line_data.get('is_subtotal', False),
                    is_header=line_data.get('is_header', False),
                    metadata={
                        k: v for k, v in line_data.items()
                        if k not in ['account_id', 'account_code', 'account_name', 'name',
                                   'amount', 'is_total', 'is_subtotal', 'is_header']
                    },
                    created_by=created_by,
                    updated_by=created_by
                )
                self.db.add(line)