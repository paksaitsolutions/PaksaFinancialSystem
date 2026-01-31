"""
Reporting Engine Service

This service provides a flexible reporting system that can generate various types
of financial reports with custom parameters and formats.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import json

from enum import Enum
from io import BytesIO
from sqlalchemy import select, func, and_, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from uuid import UUID, uuid4
import pandas as pd

from app.models.accounts_payable import Vendor, Invoice as APInvoice, Payment
from app.models.accounts_receivable import Customer, Invoice as ARInvoice, Receipt
from app.models.general_ledger import Transaction, Account, JournalEntry
from app.models.payroll import Employee, Payroll, PayrollItem





class ReportType(str, Enum):
    INCOME_STATEMENT = "income_statement"
    BALANCE_SHEET = "balance_sheet"
    CASH_FLOW = "cash_flow"
    TRIAL_BALANCE = "trial_balance"
    AGING_REPORT = "aging_report"
    CUSTOM = "custom"


class ReportFormat(str, Enum):
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"
    PDF = "pdf"


class ReportingEngine:
    """Service for generating financial reports."""

    def __init__(self, db: AsyncSession, company_id: UUID):
        """  Init  ."""
        self.db = db
        self.company_id = company_id

    async def generate_report(
        self,
        report_type: ReportType,
        parameters: Dict[str, Any],
        format: ReportFormat = ReportFormat.JSON
    ) -> Dict[str, Any]:
        """Generate Report."""
        """Generate a report based on type and parameters."""
        
        report_id = str(uuid4())
        start_time = datetime.now()
        
        try:
            if report_type == ReportType.INCOME_STATEMENT:
                data = await self._generate_income_statement(parameters)
            elif report_type == ReportType.BALANCE_SHEET:
                data = await self._generate_balance_sheet(parameters)
            elif report_type == ReportType.CASH_FLOW:
                data = await self._generate_cash_flow_statement(parameters)
            elif report_type == ReportType.TRIAL_BALANCE:
                data = await self._generate_trial_balance(parameters)
            elif report_type == ReportType.AGING_REPORT:
                data = await self._generate_aging_report(parameters)
            elif report_type == ReportType.CUSTOM:
                data = await self._generate_custom_report(parameters)
            else:
                raise ValueError(f"Unsupported report type: {report_type}")

            # Format the output
            formatted_data = await self._format_report(data, format)
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()

            return {
                'report_id': report_id,
                'report_type': report_type,
                'format': format,
                'data': formatted_data,
                'metadata': {
                    'generated_at': end_time.isoformat(),
                    'execution_time_seconds': execution_time,
                    'parameters': parameters,
                    'company_id': str(self.company_id)
                }
            }
            
        except Exception as e:
            return {
                'report_id': report_id,
                'error': str(e),
                'generated_at': datetime.now().isoformat()
            }

    async def _generate_income_statement(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Income Statement."""
        """Generate income statement."""
        start_date = datetime.fromisoformat(parameters.get('start_date', (datetime.now() - timedelta(days=365)).isoformat()))
        end_date = datetime.fromisoformat(parameters.get('end_date', datetime.now().isoformat()))

        # Revenue accounts
        revenue_query = select(
            Account.account_name,
            Account.account_code,
            func.sum(Transaction.amount).label('total')
        ).join(Transaction).where(
            and_(
                Account.company_id == self.company_id,
                Account.account_type == 'revenue',
                Transaction.transaction_date.between(start_date, end_date)
            )
        ).group_by(Account.id, Account.account_name, Account.account_code)

        # Expense accounts
        expense_query = select(
            Account.account_name,
            Account.account_code,
            func.sum(Transaction.amount).label('total')
        ).join(Transaction).where(
            and_(
                Account.company_id == self.company_id,
                Account.account_type == 'expense',
                Transaction.transaction_date.between(start_date, end_date)
            )
        ).group_by(Account.id, Account.account_name, Account.account_code)

        revenue_result = await self.db.execute(revenue_query)
        expense_result = await self.db.execute(expense_query)

        revenue_accounts = [
            {
                'account_name': row.account_name,
                'account_code': row.account_code,
                'amount': float(row.total or 0)
            }
            for row in revenue_result.fetchall()
        ]

        expense_accounts = [
            {
                'account_name': row.account_name,
                'account_code': row.account_code,
                'amount': float(row.total or 0)
            }
            for row in expense_result.fetchall()
        ]

        total_revenue = sum(acc['amount'] for acc in revenue_accounts)
        total_expenses = sum(acc['amount'] for acc in expense_accounts)
        net_income = total_revenue - total_expenses

        return {
            'report_name': 'Income Statement',
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'revenue': {
                'accounts': revenue_accounts,
                'total': total_revenue
            },
            'expenses': {
                'accounts': expense_accounts,
                'total': total_expenses
            },
            'net_income': net_income
        }

    async def _generate_balance_sheet(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Balance Sheet."""
        """Generate balance sheet."""
        as_of_date = datetime.fromisoformat(parameters.get('as_of_date', datetime.now().isoformat()))

        # Assets
        assets_query = select(
            Account.account_name,
            Account.account_code,
            Account.account_subtype,
            func.sum(Transaction.amount).label('balance')
        ).join(Transaction).where(
            and_(
                Account.company_id == self.company_id,
                Account.account_type == 'asset',
                Transaction.transaction_date <= as_of_date
            )
        ).group_by(Account.id, Account.account_name, Account.account_code, Account.account_subtype)

        # Liabilities
        liabilities_query = select(
            Account.account_name,
            Account.account_code,
            Account.account_subtype,
            func.sum(Transaction.amount).label('balance')
        ).join(Transaction).where(
            and_(
                Account.company_id == self.company_id,
                Account.account_type == 'liability',
                Transaction.transaction_date <= as_of_date
            )
        ).group_by(Account.id, Account.account_name, Account.account_code, Account.account_subtype)

        # Equity
        equity_query = select(
            Account.account_name,
            Account.account_code,
            Account.account_subtype,
            func.sum(Transaction.amount).label('balance')
        ).join(Transaction).where(
            and_(
                Account.company_id == self.company_id,
                Account.account_type == 'equity',
                Transaction.transaction_date <= as_of_date
            )
        ).group_by(Account.id, Account.account_name, Account.account_code, Account.account_subtype)

        assets_result = await self.db.execute(assets_query)
        liabilities_result = await self.db.execute(liabilities_query)
        equity_result = await self.db.execute(equity_query)

        assets = self._group_by_subtype(assets_result.fetchall())
        liabilities = self._group_by_subtype(liabilities_result.fetchall())
        equity = self._group_by_subtype(equity_result.fetchall())

        total_assets = sum(
            sum(acc['balance'] for acc in subtype['accounts'])
            for subtype in assets.values()
        )
        total_liabilities = sum(
            sum(acc['balance'] for acc in subtype['accounts'])
            for subtype in liabilities.values()
        )
        total_equity = sum(
            sum(acc['balance'] for acc in subtype['accounts'])
            for subtype in equity.values()
        )

        return {
            'report_name': 'Balance Sheet',
            'as_of_date': as_of_date.isoformat(),
            'assets': {
                'subtypes': assets,
                'total': total_assets
            },
            'liabilities': {
                'subtypes': liabilities,
                'total': total_liabilities
            },
            'equity': {
                'subtypes': equity,
                'total': total_equity
            },
            'total_liabilities_and_equity': total_liabilities + total_equity
        }

    async def _generate_cash_flow_statement(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Cash Flow Statement."""
        """Generate cash flow statement."""
        start_date = datetime.fromisoformat(parameters.get('start_date', (datetime.now() - timedelta(days=365)).isoformat()))
        end_date = datetime.fromisoformat(parameters.get('end_date', datetime.now().isoformat()))

        # Operating activities (receipts and payments)
        receipts_query = select(func.sum(Receipt.amount)).where(
            and_(
                Receipt.company_id == self.company_id,
                Receipt.receipt_date.between(start_date, end_date)
            )
        )

        payments_query = select(func.sum(Payment.amount)).where(
            and_(
                Payment.company_id == self.company_id,
                Payment.payment_date.between(start_date, end_date)
            )
        )

        receipts_result = await self.db.execute(receipts_query)
        payments_result = await self.db.execute(payments_query)

        total_receipts = float(receipts_result.scalar() or 0)
        total_payments = float(payments_result.scalar() or 0)
        net_operating_cash_flow = total_receipts - total_payments

        return {
            'report_name': 'Cash Flow Statement',
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'operating_activities': {
                'cash_receipts': total_receipts,
                'cash_payments': total_payments,
                'net_cash_flow': net_operating_cash_flow
            },
            'investing_activities': {
                'net_cash_flow': 0  # Placeholder
            },
            'financing_activities': {
                'net_cash_flow': 0  # Placeholder
            },
            'net_change_in_cash': net_operating_cash_flow
        }

    async def _generate_aging_report(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Aging Report."""
        """Generate aging report for AR or AP."""
        report_type = parameters.get('type', 'ar')  # 'ar' or 'ap'
        as_of_date = datetime.fromisoformat(parameters.get('as_of_date', datetime.now().isoformat()))

        if report_type == 'ar':
            return await self._generate_ar_aging(as_of_date)
        else:
            return await self._generate_ap_aging(as_of_date)

    async def _generate_ar_aging(self, as_of_date: datetime) -> Dict[str, Any]:
        """Generate Ar Aging."""
        """Generate AR aging report."""
        query = select(
            Customer.name,
            ARInvoice.invoice_number,
            ARInvoice.invoice_date,
            ARInvoice.due_date,
            ARInvoice.total_amount,
            ARInvoice.paid_amount,
            (ARInvoice.total_amount - ARInvoice.paid_amount).label('outstanding')
        ).join(Customer).where(
            and_(
                ARInvoice.company_id == self.company_id,
                ARInvoice.total_amount > ARInvoice.paid_amount,
                ARInvoice.invoice_date <= as_of_date
            )
        )

        result = await self.db.execute(query)
        invoices = result.fetchall()

        aging_buckets = {
            'current': [],
            '1_30_days': [],
            '31_60_days': [],
            '61_90_days': [],
            'over_90_days': []
        }

        for invoice in invoices:
            days_overdue = (as_of_date - invoice.due_date).days
            outstanding = float(invoice.outstanding)
            
            invoice_data = {
                'customer_name': invoice.name,
                'invoice_number': invoice.invoice_number,
                'invoice_date': invoice.invoice_date.isoformat(),
                'due_date': invoice.due_date.isoformat(),
                'total_amount': float(invoice.total_amount),
                'paid_amount': float(invoice.paid_amount),
                'outstanding': outstanding,
                'days_overdue': days_overdue
            }

            if days_overdue <= 0:
                aging_buckets['current'].append(invoice_data)
            elif days_overdue <= 30:
                aging_buckets['1_30_days'].append(invoice_data)
            elif days_overdue <= 60:
                aging_buckets['31_60_days'].append(invoice_data)
            elif days_overdue <= 90:
                aging_buckets['61_90_days'].append(invoice_data)
            else:
                aging_buckets['over_90_days'].append(invoice_data)

        # Calculate totals
        totals = {}
        for bucket, invoices in aging_buckets.items():
            totals[bucket] = sum(inv['outstanding'] for inv in invoices)

        return {
            'report_name': 'Accounts Receivable Aging Report',
            'as_of_date': as_of_date.isoformat(),
            'aging_buckets': aging_buckets,
            'totals': totals,
            'grand_total': sum(totals.values())
        }

    async def _generate_custom_report(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Custom Report."""
        """Generate custom report based on SQL query."""
        query_text = parameters.get('query')
        if not query_text:
            raise ValueError("Custom report requires 'query' parameter")

        # Security: Only allow SELECT statements
        if not query_text.strip().upper().startswith('SELECT'):
            raise ValueError("Only SELECT queries are allowed")

        try:
            result = await self.db.execute(text(query_text))
            rows = result.fetchall()
            columns = result.keys()

            data = [
                {col: row[i] for i, col in enumerate(columns)}
                for row in rows
            ]

            return {
                'report_name': parameters.get('name', 'Custom Report'),
                'columns': list(columns),
                'data': data,
                'row_count': len(data)
            }
        except Exception as e:
            raise ValueError(f"Query execution failed: {str(e)}")

    def _group_by_subtype(self, rows) -> Dict[str, Any]:
        """ Group By Subtype."""
        """Group account rows by subtype."""
        grouped = {}
        for row in rows:
            subtype = row.account_subtype or 'Other'
            if subtype not in grouped:
                grouped[subtype] = {
                    'subtype_name': subtype,
                    'accounts': [],
                    'total': 0
                }
            
            account_data = {
                'account_name': row.account_name,
                'account_code': row.account_code,
                'balance': float(row.balance or 0)
            }
            
            grouped[subtype]['accounts'].append(account_data)
            grouped[subtype]['total'] += account_data['balance']

        return grouped

    async def _format_report(self, data: Dict[str, Any], format: ReportFormat) -> Any:
        """Format Report."""
        """Format report data according to specified format."""
        if format == ReportFormat.JSON:
            return data
        elif format == ReportFormat.CSV:
            return self._to_csv(data)
        elif format == ReportFormat.EXCEL:
            return self._to_excel(data)
        elif format == ReportFormat.PDF:
            return self._to_pdf(data)
        else:
            return data

    def _to_csv(self, data: Dict[str, Any]) -> str:
        """ To Csv."""
        """Convert report data to CSV format."""
        # This is a simplified implementation
        # In practice, you'd want more sophisticated CSV generation
        if 'data' in data and isinstance(data['data'], list):
            df = pd.DataFrame(data['data'])
            return df.to_csv(index=False)
        return ""

    def _to_excel(self, data: Dict[str, Any]) -> bytes:
        """ To Excel."""
        """Convert report data to Excel format."""
        output = BytesIO()
        if 'data' in data and isinstance(data['data'], list):
            df = pd.DataFrame(data['data'])
            df.to_excel(output, index=False)
        return output.getvalue()

    def _to_pdf(self, data: Dict[str, Any]) -> bytes:
        """ To Pdf."""
        """Convert report data to PDF format."""
        # This would require a PDF library like reportlab
        # For now, return placeholder
        return b"PDF generation not implemented"