"""
Service layer for generating financial statements.
"""
from datetime import date, datetime
from typing import List, Dict, Any, Optional, Tuple

from decimal import Decimal
from sqlalchemy import func, and_, or_, select, text
from sqlalchemy.orm import Session, joinedload
from uuid import UUID

from app.exceptions import (
    NotFoundException,
    ValidationException,
    BusinessRuleException
)
from app.models import (
    GLChartOfAccounts,
    ChartOfAccounts,
    JournalEntryLine,
    JournalEntry,
    TrialBalance,
    TrialBalanceAccount,
    FinancialStatement,
    FinancialStatementLine,
    FinancialStatementSection,
    FinancialStatementType,
    AccountType
)
from app.schemas.gl_schemas import (
    FinancialStatementResponse,
    FinancialStatementType as FSType,
    FinancialStatementCreate,
    FinancialStatementLineCreate,
    FinancialStatementSectionCreate
)
from app.services.base import BaseService


class FinancialStatementService(BaseService):
    """Service for generating and managing financial statements."""
    
    def __init__(self, db: Session):
        """  Init  ."""
        super().__init__(db, FinancialStatement)
    
    def generate_financial_statement(
        self,
        statement_type: FSType,
        company_id: UUID,
        end_date: date,
        start_date: Optional[date] = None,
        period_id: Optional[UUID] = None,
        created_by: Optional[UUID] = None,
        is_final: bool = False,
        name: Optional[str] = None
    ) -> FinancialStatementResponse:
        """Generate Financial Statement."""
        """
        Generate a financial statement of the specified type.
        
        Args:
            statement_type: Type of financial statement to generate
            company_id: Company ID
            end_date: End date for the statement
            start_date: Start date (for income statement, cash flow)
            period_id: Optional period ID
            created_by: User ID creating the statement
            is_final: Whether this is a final statement
            name: Optional custom name for the statement
            
        Returns:
            Generated financial statement
        """
        # Get the most recent trial balance for the end date
        trial_balance = self._get_trial_balance(company_id, end_date, period_id)
        
        # Generate statement data based on type
        if statement_type == FSType.BALANCE_SHEET:
            statement_data = self._generate_balance_sheet(trial_balance, end_date)
            statement_name = name or f"Balance Sheet as of {end_date.strftime('%Y-%m-%d')}"
        elif statement_type == FSType.INCOME_STATEMENT:
            if not start_date:
                raise ValidationException("Start date is required for income statement")
            statement_data = self._generate_income_statement(
                company_id, start_date, end_date, trial_balance
            )
            statement_name = name or f"Income Statement for {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        elif statement_type == FSType.CASH_FLOW:
            if not start_date:
                raise ValidationException("Start date is required for cash flow statement")
            statement_data = self._generate_cash_flow_from_gl(
                company_id, start_date, end_date
            )
            statement_name = name or f"Cash Flow Statement for {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        else:
            raise ValidationException(f"Unsupported statement type: {statement_type}")
        
        # Create the financial statement record
        statement = FinancialStatement(
            name=statement_name,
            statement_type=statement_type,
            start_date=start_date,
            end_date=end_date,
            company_id=company_id,
            period_id=period_id,
            is_final=is_final,
            statement_data=statement_data,
            generated_at=datetime.utcnow(),
            generated_by=created_by,
            created_by=created_by,
            updated_by=created_by
        )
        
        self.db.add(statement)
        self.db.flush()  # Get the statement ID
        
        # Save sections and lines
        self._save_statement_structure(statement.id, statement_data, created_by)
        
        self.db.commit()
        self.db.refresh(statement)
        
        return self._format_statement_response(statement)
    
    def _get_trial_balance(
        self, 
        company_id: UUID, 
        as_of_date: date,
        period_id: Optional[UUID] = None
    ) -> TrialBalance:
        """ Get Trial Balance."""
        """Get or generate a trial balance for the given date."""
        # Try to find an existing trial balance
        query = self.db.query(TrialBalance).filter(
            TrialBalance.company_id == company_id,
            TrialBalance.as_of_date == as_of_date,
            TrialBalance.is_posted == True
        )
        
        if period_id:
            query = query.filter(TrialBalance.period_id == period_id)
        
        trial_balance = query.order_by(TrialBalance.generated_at.desc()).first()
        
        if not trial_balance:
            # Generate a new trial balance if none exists
            from app.services.gl.period_service import PeriodService
            period_service = PeriodService(self.db)
            trial_balance = period_service._generate_trial_balance(
                company_id=company_id,
                as_of_date=as_of_date,
                period_id=period_id,
                created_by=UUID('00000000-0000-0000-0000-000000000000')  # System user
            )
        
        return trial_balance
    
    def _generate_balance_sheet(
        self, 
        trial_balance: TrialBalance,
        as_of_date: date
    ) -> Dict[str, Any]:
        """ Generate Balance Sheet."""
        """Generate balance sheet data consolidating all modules."""
        # Get consolidated account balances from unified GL across all modules
        accounts = self.db.query(
            ChartOfAccounts,
            func.sum(JournalEntryLine.debit_amount).label('total_debits'),
            func.sum(JournalEntryLine.credit_amount).label('total_credits')
        ).join(
            JournalEntryLine, ChartOfAccounts.id == JournalEntryLine.account_id
        ).join(
            JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id
        ).filter(
            JournalEntry.company_id == trial_balance.company_id,
            JournalEntry.entry_date <= as_of_date,
            JournalEntry.status == 'posted',
            ChartOfAccounts.is_active == True
        ).group_by(ChartOfAccounts.id, ChartOfAccounts.account_code, ChartOfAccounts.account_name, ChartOfAccounts.account_type).all()
        
        # Initialize sections
        assets = {
            "name": "Assets",
            "order": 1,
            "lines": []
        }
        
        liabilities = {
            "name": "Liabilities",
            "order": 2,
            "lines": []
        }
        
        equity = {
            "name": "Equity",
            "order": 3,
            "lines": []
        }
        
        # Categorize accounts from all modules (AP, AR, Cash, Payroll, etc.)
        for account, debit_bal, credit_bal in accounts:
            if account.account_type in ['Asset']:
                balance = debit_bal - credit_bal
                section = assets
            elif account.account_type in ['Liability']:
                balance = credit_bal - debit_bal
                section = liabilities
            elif account.account_type in ['Equity', 'Revenue']:
                balance = credit_bal - debit_bal
                section = equity
            else:
                continue
            
            section["lines"].append({
                "account_id": str(account.id),
                "account_code": account.account_code,
                "account_name": account.account_name,
                "amount": float(balance),
                "order": len(section["lines"]) + 1
            })
        
        # Calculate totals
        total_assets = sum(line["amount"] for line in assets["lines"])
        total_liabilities = sum(line["amount"] for line in liabilities["lines"])
        total_equity = sum(line["amount"] for line in equity["lines"])
        
        # Add total lines
        assets["lines"].append({
            "account_id": None,
            "account_code": "TOTAL",
            "account_name": "Total Assets",
            "amount": float(total_assets),
            "is_total": True,
            "order": len(assets["lines"]) + 1
        })
        
        liabilities["lines"].append({
            "account_id": None,
            "account_code": "TOTAL",
            "account_name": "Total Liabilities",
            "amount": float(total_liabilities),
            "is_total": True,
            "order": len(liabilities["lines"]) + 1
        })
        
        equity["lines"].append({
            "account_id": None,
            "account_code": "TOTAL",
            "account_name": "Total Equity",
            "amount": float(total_equity),
            "is_total": True,
            "order": len(equity["lines"]) + 1
        })
        
        # Add total liabilities and equity
        total_liab_equity = total_liabilities + total_equity
        
        return {
            "sections": [assets, liabilities, equity],
            "metadata": {
                "as_of_date": as_of_date.isoformat(),
                "currency": self._get_company_currency(trial_balance.company_id),
                "total_assets": float(total_assets),
                "total_liabilities": float(total_liabilities),
                "total_equity": float(total_equity),
                "total_liabilities_and_equity": float(total_liab_equity),
                "is_balanced": abs(total_assets - total_liab_equity) < 0.01  # Allow for rounding differences
            }
        }
    
    def _generate_income_statement(
        self,
        company_id: UUID,
        start_date: date,
        end_date: date,
        trial_balance: TrialBalance
    ) -> Dict[str, Any]:
        """ Generate Income Statement."""
        """Generate income statement data consolidating all modules."""
        # Get revenue and expense accounts with consolidated balances from all modules
        accounts = self.db.query(
            ChartOfAccounts,
            func.sum(JournalEntryLine.debit_amount).label('total_debits'),
            func.sum(JournalEntryLine.credit_amount).label('total_credits')
        ).join(
            JournalEntryLine, ChartOfAccounts.id == JournalEntryLine.account_id
        ).join(
            JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id
        ).filter(
            JournalEntry.company_id == company_id,
            JournalEntry.entry_date.between(start_date, end_date),
            JournalEntry.status == 'posted',
            ChartOfAccounts.account_type.in_(['Revenue', 'Expense']),
            ChartOfAccounts.is_active == True
        ).group_by(ChartOfAccounts.id, ChartOfAccounts.account_code, ChartOfAccounts.account_name, ChartOfAccounts.account_type).all()
        
        # Initialize sections
        revenue = {
            "name": "Revenue",
            "order": 1,
            "lines": []
        }
        
        expenses = {
            "name": "Expenses",
            "order": 2,
            "lines": []
        }
        
        # Categorize accounts
        total_revenue = Decimal('0')
        total_expenses = Decimal('0')
        
        for account, debit_bal, credit_bal in accounts:
            if account.account_type == 'Revenue':
                amount = credit_bal - debit_bal
                revenue["lines"].append({
                    "account_id": str(account.id),
                    "account_code": account.account_code,
                    "account_name": account.account_name,
                    "amount": float(amount),
                    "order": len(revenue["lines"]) + 1
                })
                total_revenue += amount
            else:  # Expense
                amount = debit_bal - credit_bal
                expenses["lines"].append({
                    "account_id": str(account.id),
                    "account_code": account.account_code,
                    "account_name": account.account_name,
                    "amount": float(amount),
                    "order": len(expenses["lines"]) + 1
                })
                total_expenses += amount
        
        # Calculate net income/loss
        net_income = total_revenue - total_expenses
        
        # Add total lines
        revenue["lines"].append({
            "account_id": None,
            "account_code": "TOTAL",
            "account_name": "Total Revenue",
            "amount": float(total_revenue),
            "is_total": True,
            "order": len(revenue["lines"]) + 1
        })
        
        expenses["lines"].append({
            "account_id": None,
            "account_code": "TOTAL",
            "account_name": "Total Expenses",
            "amount": float(total_expenses),
            "is_total": True,
            "order": len(expenses["lines"]) + 1
        })
        
        # Add net income/loss
        result_section = {
            "name": "Net Income (Loss)",
            "order": 3,
            "lines": [{
                "account_id": None,
                "account_code": "NET",
                "account_name": "Net Income" if net_income >= 0 else "Net Loss",
                "amount": float(abs(net_income)),
                "is_net_income": True,
                "order": 1
            }]
        }
        
        return {
            "sections": [revenue, expenses, result_section],
            "metadata": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "currency": self._get_company_currency(company_id),
                "total_revenue": float(total_revenue),
                "total_expenses": float(total_expenses),
                "net_income": float(net_income),
                "is_profit": net_income >= 0
            }
        }
    
    def _generate_cash_flow_statement(
        self,
        company_id: UUID,
        start_date: date,
        end_date: date,
        trial_balance: TrialBalance
    ) -> Dict[str, Any]:
        """ Generate Cash Flow Statement."""
        """Generate cash flow statement data for the given date range."""
        # This is a simplified implementation
        # In a real system, you'd need to analyze changes in balance sheet accounts
        # and categorize cash flows into operating, investing, and financing activities
        
        # Placeholder implementation
        operating = {
            "name": "Operating Activities",
            "order": 1,
            "lines": [
                {
                    "account_id": None,
                    "account_code": "NET_INC",
                    "account_name": "Net Income",
                    "amount": 0.0,  # Would come from income statement
                    "order": 1
                },
                # More line items would be added here
            ]
        }
        
        investing = {
            "name": "Investing Activities",
            "order": 2,
            "lines": [
                # Placeholder for investing activities
            ]
        }
        
        financing = {
            "name": "Financing Activities",
            "order": 3,
            "lines": [
                # Placeholder for financing activities
            ]
        }
        
        # Calculate net cash flow (simplified)
        net_cash_flow = 0.0
        
        return {
            "sections": [operating, investing, financing],
            "metadata": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "currency": self._get_company_currency(company_id),
                "net_cash_flow": net_cash_flow
            }
        }
    
    def _save_statement_structure(
        self,
        statement_id: UUID,
        statement_data: Dict[str, Any],
        created_by: UUID
    ) -> None:
        """ Save Statement Structure."""
        """Save the financial statement structure to the database."""
        sections = statement_data.get("sections", [])
        
        for section_idx, section_data in enumerate(sections, 1):
            # Create section
            section = FinancialStatementSection(
                financial_statement_id=statement_id,
                name=section_data["name"],
                display_order=section_data.get("order", section_idx),
                created_by=created_by,
                updated_by=created_by
            )
            self.db.add(section)
            self.db.flush()  # Get the section ID
            
            # Add section lines
            for line_idx, line_data in enumerate(section_data.get("lines", []), 1):
                line = FinancialStatementLine(
                    section_id=section.id,
                    account_id=line_data.get("account_id"),
                    account_code=line_data.get("account_code"),
                    description=line_data.get("account_name"),
                    amount=Decimal(str(line_data.get("amount", 0))),
                    display_order=line_data.get("order", line_idx),
                    is_total=line_data.get("is_total", False),
                    is_net_income=line_data.get("is_net_income", False),
                    metadata={
                        k: v for k, v in line_data.items()
                        if k not in ["account_id", "account_code", "account_name", 
                                   "amount", "order", "is_total", "is_net_income"]
                    },
                    created_by=created_by,
                    updated_by=created_by
                )
                self.db.add(line)
    
    def _format_statement_response(
        self, 
        statement: FinancialStatement
    ) -> FinancialStatementResponse:
        """ Format Statement Response."""
        """Format a financial statement for the API response."""
        # Get sections and lines
        sections = self.db.query(FinancialStatementSection).filter(
            FinancialStatementSection.financial_statement_id == statement.id
        ).order_by(FinancialStatementSection.display_order).all()
        
        statement_data = {
            "sections": [],
            "metadata": statement.statement_data.get("metadata", {})
        }
        
        for section in sections:
            section_data = {
                "id": str(section.id),
                "name": section.name,
                "order": section.display_order,
                "lines": []
            }
            
            lines = self.db.query(FinancialStatementLine).filter(
                FinancialStatementLine.section_id == section.id
            ).order_by(FinancialStatementLine.display_order).all()
            
            for line in lines:
                line_data = {
                    "id": str(line.id),
                    "account_id": line.account_id,
                    "account_code": line.account_code,
                    "description": line.description,
                    "amount": float(line.amount),
                    "order": line.display_order,
                    "is_total": line.is_total,
                    "is_net_income": line.is_net_income,
                    **line.metadata
                }
                section_data["lines"].append(line_data)
            
            statement_data["sections"].append(section_data)
        
        return FinancialStatementResponse(
            id=statement.id,
            name=statement.name,
            statement_type=statement.statement_type,
            start_date=statement.start_date,
            end_date=statement.end_date,
            is_final=statement.is_final,
            generated_at=statement.generated_at,
            generated_by=statement.generated_by,
            company_id=statement.company_id,
            statement_data=statement_data,
            created_at=statement.created_at,
            updated_at=statement.updated_at
        )
    
    def _get_company_currency(self, company_id: UUID) -> str:
        """ Get Company Currency."""
        """Get company's default currency from settings."""
        from app.models.company import Company
        company = self.db.query(Company).filter(Company.id == company_id).first()
        return company.default_currency if company else "USD"
    
    def _generate_cash_flow_from_gl(self, company_id: UUID, start_date: date, end_date: date) -> Dict[str, Any]:
        """ Generate Cash Flow From Gl."""
        """Generate cash flow statement consolidating all modules through GL journal entries"""
        # Get cash accounts from unified chart of accounts
        cash_accounts = self.db.query(ChartOfAccounts).filter(
            ChartOfAccounts.company_id == company_id,
            ChartOfAccounts.account_type == 'Asset',
            ChartOfAccounts.account_subtype.in_(['Cash', 'Bank']),
            ChartOfAccounts.is_active == True
        ).all()
        
        cash_account_ids = [acc.id for acc in cash_accounts]
        
        # Operating cash flows from all modules (AR, AP, Payroll, etc.)
        operating_flows = self.db.query(
            JournalEntry.source_module,
            JournalEntryLine.description,
            func.sum(JournalEntryLine.debit_amount - JournalEntryLine.credit_amount).label('amount')
        ).join(JournalEntry).filter(
            JournalEntry.company_id == company_id,
            JournalEntry.entry_date.between(start_date, end_date),
            JournalEntry.status == 'posted',
            JournalEntryLine.account_id.in_(cash_account_ids),
            JournalEntry.source_module.in_(['AR', 'AP', 'PAYROLL', 'CASH'])
        ).group_by(JournalEntry.source_module, JournalEntryLine.description).all()
        
        # Investing cash flows (Fixed Assets, Investments)
        investing_flows = self.db.query(
            JournalEntryLine.description,
            func.sum(JournalEntryLine.debit_amount - JournalEntryLine.credit_amount).label('amount')
        ).join(JournalEntry).join(ChartOfAccounts, JournalEntryLine.account_id == ChartOfAccounts.id).filter(
            JournalEntry.company_id == company_id,
            JournalEntry.entry_date.between(start_date, end_date),
            JournalEntry.status == 'posted',
            or_(
                JournalEntryLine.account_id.in_(cash_account_ids),
                ChartOfAccounts.account_subtype.in_(['Fixed Assets', 'Investments'])
            )
        ).group_by(JournalEntryLine.description).all()
        
        # Financing cash flows (Loans, Equity transactions)
        financing_flows = self.db.query(
            JournalEntryLine.description,
            func.sum(JournalEntryLine.debit_amount - JournalEntryLine.credit_amount).label('amount')
        ).join(JournalEntry).join(ChartOfAccounts, JournalEntryLine.account_id == ChartOfAccounts.id).filter(
            JournalEntry.company_id == company_id,
            JournalEntry.entry_date.between(start_date, end_date),
            JournalEntry.status == 'posted',
            or_(
                JournalEntryLine.account_id.in_(cash_account_ids),
                and_(ChartOfAccounts.account_type.in_(['Liability', 'Equity']),
                     ChartOfAccounts.account_subtype.in_(['Long-term Debt', 'Capital']))
            )
        ).group_by(JournalEntryLine.description).all()
        
        # Build sections with module source information
        operating = {
            "name": "Operating Activities",
            "order": 1,
            "lines": [{
                "description": f"{flow.source_module}: {flow.description}",
                "amount": float(flow.amount),
                "order": i + 1
            } for i, flow in enumerate(operating_flows)]
        }
        
        investing = {
            "name": "Investing Activities", 
            "order": 2,
            "lines": [{
                "description": flow.description,
                "amount": float(flow.amount),
                "order": i + 1
            } for i, flow in enumerate(investing_flows)]
        }
        
        financing = {
            "name": "Financing Activities",
            "order": 3, 
            "lines": [{
                "description": flow.description,
                "amount": float(flow.amount),
                "order": i + 1
            } for i, flow in enumerate(financing_flows)]
        }
        
        # Calculate totals and add total lines
        total_operating = sum(line["amount"] for line in operating["lines"])
        total_investing = sum(line["amount"] for line in investing["lines"])
        total_financing = sum(line["amount"] for line in financing["lines"])
        net_cash_flow = total_operating + total_investing + total_financing
        
        # Add total lines to each section
        operating["lines"].append({
            "description": "Net Cash from Operating Activities",
            "amount": total_operating,
            "is_total": True,
            "order": len(operating["lines"]) + 1
        })
        
        investing["lines"].append({
            "description": "Net Cash from Investing Activities",
            "amount": total_investing,
            "is_total": True,
            "order": len(investing["lines"]) + 1
        })
        
        financing["lines"].append({
            "description": "Net Cash from Financing Activities",
            "amount": total_financing,
            "is_total": True,
            "order": len(financing["lines"]) + 1
        })
        
        return {
            "sections": [operating, investing, financing],
            "metadata": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "currency": self._get_company_currency(company_id),
                "total_operating": total_operating,
                "total_investing": total_investing,
                "total_financing": total_financing,
                "net_cash_flow": net_cash_flow,
                "modules_included": ["AR", "AP", "PAYROLL", "CASH", "GL"]
            }
        }
