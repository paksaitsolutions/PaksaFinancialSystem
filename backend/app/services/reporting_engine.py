"""
Reporting Engine - PDF/Excel Generation, Financial Statements, Scheduling
"""
from datetime import datetime, date
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from typing import Dict, List, Any
import json
import os

from decimal import Decimal
from sqlalchemy import text, func
from sqlalchemy.orm import Session
import pandas as pd
import uuid

from app.models.financial_core import *


class ReportGenerator:
    """Core report generation engine"""
    
    @staticmethod
    def generate_trial_balance(db: Session, as_of_date: date = None) -> Dict:
        """Generate Trial Balance."""
        """Generate trial balance report"""
        if not as_of_date:
            as_of_date = date.today()
        
        accounts = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.is_active == True
        ).order_by(ChartOfAccounts.account_code).all()
        
        trial_balance = []
        total_debits = Decimal('0')
        total_credits = Decimal('0')
        
        for account in accounts:
            if account.current_balance != 0:
                if account.normal_balance == 'Debit':
                    debit_balance = account.current_balance if account.current_balance > 0 else Decimal('0')
                    credit_balance = -account.current_balance if account.current_balance < 0 else Decimal('0')
                else:
                    credit_balance = account.current_balance if account.current_balance > 0 else Decimal('0')
                    debit_balance = -account.current_balance if account.current_balance < 0 else Decimal('0')
                
                trial_balance.append({
                    "account_code": account.account_code,
                    "account_name": account.account_name,
                    "debit_balance": float(debit_balance),
                    "credit_balance": float(credit_balance)
                })
                
                total_debits += debit_balance
                total_credits += credit_balance
        
        return {
            "report_type": "trial_balance",
            "as_of_date": as_of_date.isoformat(),
            "accounts": trial_balance,
            "total_debits": float(total_debits),
            "total_credits": float(total_credits),
            "is_balanced": abs(total_debits - total_credits) <= Decimal('0.01')
        }
    
    @staticmethod
    def generate_balance_sheet(db: Session, as_of_date: date = None) -> Dict:
        """Generate Balance Sheet."""
        """Generate balance sheet"""
        if not as_of_date:
            as_of_date = date.today()
        
        # Assets
        assets = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.account_type == 'Asset',
            ChartOfAccounts.is_active == True
        ).order_by(ChartOfAccounts.account_code).all()
        
        # Liabilities
        liabilities = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.account_type == 'Liability',
            ChartOfAccounts.is_active == True
        ).order_by(ChartOfAccounts.account_code).all()
        
        # Equity
        equity = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.account_type == 'Equity',
            ChartOfAccounts.is_active == True
        ).order_by(ChartOfAccounts.account_code).all()
        
        def format_accounts(accounts):
            """Format Accounts."""
            return [{
                "account_code": acc.account_code,
                "account_name": acc.account_name,
                "balance": float(acc.current_balance)
            } for acc in accounts if acc.current_balance != 0]
        
        total_assets = sum(acc.current_balance for acc in assets)
        total_liabilities = sum(acc.current_balance for acc in liabilities)
        total_equity = sum(acc.current_balance for acc in equity)
        
        return {
            "report_type": "balance_sheet",
            "as_of_date": as_of_date.isoformat(),
            "assets": {
                "accounts": format_accounts(assets),
                "total": float(total_assets)
            },
            "liabilities": {
                "accounts": format_accounts(liabilities),
                "total": float(total_liabilities)
            },
            "equity": {
                "accounts": format_accounts(equity),
                "total": float(total_equity)
            },
            "total_liabilities_equity": float(total_liabilities + total_equity)
        }
    
    @staticmethod
    def generate_income_statement(db: Session, start_date: date, end_date: date) -> Dict:
        """Generate Income Statement."""
        """Generate profit & loss statement"""
        # Revenue
        revenue = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.account_type == 'Revenue',
            ChartOfAccounts.is_active == True
        ).order_by(ChartOfAccounts.account_code).all()
        
        # Expenses
        expenses = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.account_type == 'Expense',
            ChartOfAccounts.is_active == True
        ).order_by(ChartOfAccounts.account_code).all()
        
        def format_accounts(accounts):
            """Format Accounts."""
            return [{
                "account_code": acc.account_code,
                "account_name": acc.account_name,
                "balance": float(acc.current_balance)
            } for acc in accounts if acc.current_balance != 0]
        
        total_revenue = sum(acc.current_balance for acc in revenue)
        total_expenses = sum(acc.current_balance for acc in expenses)
        net_income = total_revenue - total_expenses
        
        return {
            "report_type": "income_statement",
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "revenue": {
                "accounts": format_accounts(revenue),
                "total": float(total_revenue)
            },
            "expenses": {
                "accounts": format_accounts(expenses),
                "total": float(total_expenses)
            },
            "net_income": float(net_income)
        }
    
    @staticmethod
    def generate_cash_flow(db: Session, start_date: date, end_date: date) -> Dict:
        """Generate Cash Flow."""
        """Generate cash flow statement"""
        # Get cash accounts
        cash_accounts = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.account_code.like('1000%'),
            ChartOfAccounts.is_active == True
        ).all()
        
        # Operating activities (simplified)
        net_income_query = db.query(func.sum(ChartOfAccounts.current_balance)).filter(
            ChartOfAccounts.account_type == 'Revenue'
        ).scalar() or Decimal('0')
        
        expenses_query = db.query(func.sum(ChartOfAccounts.current_balance)).filter(
            ChartOfAccounts.account_type == 'Expense'
        ).scalar() or Decimal('0')
        
        net_income = net_income_query - expenses_query
        
        # Cash from operations (simplified)
        ar_change = db.query(func.sum(ChartOfAccounts.current_balance)).filter(
            ChartOfAccounts.account_code.like('1200%')
        ).scalar() or Decimal('0')
        
        ap_change = db.query(func.sum(ChartOfAccounts.current_balance)).filter(
            ChartOfAccounts.account_code.like('2000%')
        ).scalar() or Decimal('0')
        
        operating_cash_flow = net_income - ar_change + ap_change
        
        # Beginning and ending cash
        total_cash = sum(acc.current_balance for acc in cash_accounts)
        
        return {
            "report_type": "cash_flow_statement",
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "operating_activities": {
                "net_income": float(net_income),
                "ar_change": float(-ar_change),
                "ap_change": float(ap_change),
                "net_operating_cash": float(operating_cash_flow)
            },
            "investing_activities": {
                "net_investing_cash": 0.0
            },
            "financing_activities": {
                "net_financing_cash": 0.0
            },
            "net_change_in_cash": float(operating_cash_flow),
            "ending_cash_balance": float(total_cash)
        }

class PDFReportGenerator:
    """PDF report generation"""
    
    @staticmethod
    def create_pdf_report(report_data: Dict, output_path: str) -> str:
        """Create Pdf Report."""
        """Generate PDF report from data"""
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center
        )
        
        report_type = report_data.get('report_type', 'Financial Report').replace('_', ' ').title()
        story.append(Paragraph(report_type, title_style))
        
        # Date info
        if 'as_of_date' in report_data:
            story.append(Paragraph(f"As of: {report_data['as_of_date']}", styles['Normal']))
        elif 'period_start' in report_data:
            story.append(Paragraph(f"Period: {report_data['period_start']} to {report_data['period_end']}", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Generate table based on report type
        if report_data['report_type'] == 'trial_balance':
            PDFReportGenerator._create_trial_balance_table(story, report_data, styles)
        elif report_data['report_type'] == 'balance_sheet':
            PDFReportGenerator._create_balance_sheet_table(story, report_data, styles)
        elif report_data['report_type'] == 'income_statement':
            PDFReportGenerator._create_income_statement_table(story, report_data, styles)
        elif report_data['report_type'] == 'cash_flow_statement':
            PDFReportGenerator._create_cash_flow_table(story, report_data, styles)
        
        doc.build(story)
        return output_path
    
    @staticmethod
    def _create_trial_balance_table(story, data, styles):
        """ Create Trial Balance Table."""
        """Create trial balance table"""
        table_data = [['Account Code', 'Account Name', 'Debit', 'Credit']]
        
        for account in data['accounts']:
            table_data.append([
                account['account_code'],
                account['account_name'],
                f"${account['debit_balance']:,.2f}" if account['debit_balance'] else '',
                f"${account['credit_balance']:,.2f}" if account['credit_balance'] else ''
            ])
        
        # Totals
        table_data.append(['', 'TOTALS', f"${data['total_debits']:,.2f}", f"${data['total_credits']:,.2f}"])
        
        table = Table(table_data, colWidths=[1*inch, 3*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
    
    @staticmethod
    def _create_balance_sheet_table(story, data, styles):
        """ Create Balance Sheet Table."""
        """Create balance sheet table"""
        # Assets
        story.append(Paragraph("ASSETS", styles['Heading2']))
        assets_data = [['Account', 'Amount']]
        for account in data['assets']['accounts']:
            assets_data.append([account['account_name'], f"${account['balance']:,.2f}"])
        assets_data.append(['Total Assets', f"${data['assets']['total']:,.2f}"])
        
        assets_table = Table(assets_data, colWidths=[4*inch, 2*inch])
        assets_table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('LINEBELOW', (0, -2), (-1, -2), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(assets_table)
        story.append(Spacer(1, 20))
        
        # Liabilities & Equity
        story.append(Paragraph("LIABILITIES & EQUITY", styles['Heading2']))
        liab_equity_data = [['Account', 'Amount']]
        
        for account in data['liabilities']['accounts']:
            liab_equity_data.append([account['account_name'], f"${account['balance']:,.2f}"])
        liab_equity_data.append(['Total Liabilities', f"${data['liabilities']['total']:,.2f}"])
        
        for account in data['equity']['accounts']:
            liab_equity_data.append([account['account_name'], f"${account['balance']:,.2f}"])
        liab_equity_data.append(['Total Equity', f"${data['equity']['total']:,.2f}"])
        liab_equity_data.append(['Total Liabilities & Equity', f"${data['total_liabilities_equity']:,.2f}"])
        
        liab_table = Table(liab_equity_data, colWidths=[4*inch, 2*inch])
        liab_table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('LINEBELOW', (0, -2), (-1, -2), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(liab_table)
    
    @staticmethod
    def _create_income_statement_table(story, data, styles):
        """ Create Income Statement Table."""
        """Create income statement table"""
        # Revenue
        story.append(Paragraph("REVENUE", styles['Heading2']))
        revenue_data = [['Account', 'Amount']]
        for account in data['revenue']['accounts']:
            revenue_data.append([account['account_name'], f"${account['balance']:,.2f}"])
        revenue_data.append(['Total Revenue', f"${data['revenue']['total']:,.2f}"])
        
        revenue_table = Table(revenue_data, colWidths=[4*inch, 2*inch])
        revenue_table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(revenue_table)
        story.append(Spacer(1, 20))
        
        # Expenses
        story.append(Paragraph("EXPENSES", styles['Heading2']))
        expense_data = [['Account', 'Amount']]
        for account in data['expenses']['accounts']:
            expense_data.append([account['account_name'], f"${account['balance']:,.2f}"])
        expense_data.append(['Total Expenses', f"${data['expenses']['total']:,.2f}"])
        
        expense_table = Table(expense_data, colWidths=[4*inch, 2*inch])
        expense_table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(expense_table)
        story.append(Spacer(1, 20))
        
        # Net Income
        net_income_data = [['Net Income', f"${data['net_income']:,.2f}"]]
        net_table = Table(net_income_data, colWidths=[4*inch, 2*inch])
        net_table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 2, colors.black)
        ]))
        story.append(net_table)
    
    @staticmethod
    def _create_cash_flow_table(story, data, styles):
        """ Create Cash Flow Table."""
        """Create cash flow statement table"""
        cash_flow_data = [['Cash Flow Item', 'Amount']]
        
        # Operating Activities
        cash_flow_data.append(['OPERATING ACTIVITIES', ''])
        cash_flow_data.append(['Net Income', f"${data['operating_activities']['net_income']:,.2f}"])
        cash_flow_data.append(['Change in A/R', f"${data['operating_activities']['ar_change']:,.2f}"])
        cash_flow_data.append(['Change in A/P', f"${data['operating_activities']['ap_change']:,.2f}"])
        cash_flow_data.append(['Net Operating Cash Flow', f"${data['operating_activities']['net_operating_cash']:,.2f}"])
        
        # Net Change
        cash_flow_data.append(['', ''])
        cash_flow_data.append(['Net Change in Cash', f"${data['net_change_in_cash']:,.2f}"])
        cash_flow_data.append(['Ending Cash Balance', f"${data['ending_cash_balance']:,.2f}"])
        
        cash_table = Table(cash_flow_data, colWidths=[4*inch, 2*inch])
        cash_table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -2), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(cash_table)

class ExcelReportGenerator:
    """Excel report generation"""
    
    @staticmethod
    def create_excel_report(report_data: Dict, output_path: str) -> str:
        """Create Excel Report."""
        """Generate Excel report from data"""
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            if report_data['report_type'] == 'trial_balance':
                ExcelReportGenerator._create_trial_balance_excel(report_data, writer)
            elif report_data['report_type'] == 'balance_sheet':
                ExcelReportGenerator._create_balance_sheet_excel(report_data, writer)
            elif report_data['report_type'] == 'income_statement':
                ExcelReportGenerator._create_income_statement_excel(report_data, writer)
            elif report_data['report_type'] == 'cash_flow_statement':
                ExcelReportGenerator._create_cash_flow_excel(report_data, writer)
        
        return output_path
    
    @staticmethod
    def _create_trial_balance_excel(data, writer):
        """ Create Trial Balance Excel."""
        """Create trial balance Excel sheet"""
        df_data = []
        for account in data['accounts']:
            df_data.append({
                'Account Code': account['account_code'],
                'Account Name': account['account_name'],
                'Debit': account['debit_balance'] if account['debit_balance'] else 0,
                'Credit': account['credit_balance'] if account['credit_balance'] else 0
            })
        
        # Add totals
        df_data.append({
            'Account Code': '',
            'Account Name': 'TOTALS',
            'Debit': data['total_debits'],
            'Credit': data['total_credits']
        })
        
        df = pd.DataFrame(df_data)
        df.to_excel(writer, sheet_name='Trial Balance', index=False)
    
    @staticmethod
    def _create_balance_sheet_excel(data, writer):
        """ Create Balance Sheet Excel."""
        """Create balance sheet Excel sheet"""
        # Assets
        assets_data = []
        for account in data['assets']['accounts']:
            assets_data.append({'Account': account['account_name'], 'Amount': account['balance']})
        assets_data.append({'Account': 'Total Assets', 'Amount': data['assets']['total']})
        
        # Liabilities & Equity
        liab_equity_data = []
        for account in data['liabilities']['accounts']:
            liab_equity_data.append({'Account': account['account_name'], 'Amount': account['balance']})
        liab_equity_data.append({'Account': 'Total Liabilities', 'Amount': data['liabilities']['total']})
        
        for account in data['equity']['accounts']:
            liab_equity_data.append({'Account': account['account_name'], 'Amount': account['balance']})
        liab_equity_data.append({'Account': 'Total Equity', 'Amount': data['equity']['total']})
        
        pd.DataFrame(assets_data).to_excel(writer, sheet_name='Assets', index=False)
        pd.DataFrame(liab_equity_data).to_excel(writer, sheet_name='Liabilities & Equity', index=False)
    
    @staticmethod
    def _create_income_statement_excel(data, writer):
        """ Create Income Statement Excel."""
        """Create income statement Excel sheet"""
        income_data = []
        
        # Revenue
        for account in data['revenue']['accounts']:
            income_data.append({'Item': account['account_name'], 'Amount': account['balance'], 'Type': 'Revenue'})
        income_data.append({'Item': 'Total Revenue', 'Amount': data['revenue']['total'], 'Type': 'Revenue Total'})
        
        # Expenses
        for account in data['expenses']['accounts']:
            income_data.append({'Item': account['account_name'], 'Amount': account['balance'], 'Type': 'Expense'})
        income_data.append({'Item': 'Total Expenses', 'Amount': data['expenses']['total'], 'Type': 'Expense Total'})
        
        # Net Income
        income_data.append({'Item': 'Net Income', 'Amount': data['net_income'], 'Type': 'Net Income'})
        
        pd.DataFrame(income_data).to_excel(writer, sheet_name='Income Statement', index=False)
    
    @staticmethod
    def _create_cash_flow_excel(data, writer):
        """ Create Cash Flow Excel."""
        """Create cash flow Excel sheet"""
        cash_flow_data = []
        
        # Operating Activities
        cash_flow_data.append({'Item': 'Net Income', 'Amount': data['operating_activities']['net_income'], 'Category': 'Operating'})
        cash_flow_data.append({'Item': 'Change in A/R', 'Amount': data['operating_activities']['ar_change'], 'Category': 'Operating'})
        cash_flow_data.append({'Item': 'Change in A/P', 'Amount': data['operating_activities']['ap_change'], 'Category': 'Operating'})
        cash_flow_data.append({'Item': 'Net Operating Cash Flow', 'Amount': data['operating_activities']['net_operating_cash'], 'Category': 'Operating Total'})
        
        # Summary
        cash_flow_data.append({'Item': 'Net Change in Cash', 'Amount': data['net_change_in_cash'], 'Category': 'Summary'})
        cash_flow_data.append({'Item': 'Ending Cash Balance', 'Amount': data['ending_cash_balance'], 'Category': 'Summary'})
        
        pd.DataFrame(cash_flow_data).to_excel(writer, sheet_name='Cash Flow', index=False)

class ReportScheduler:
    """Report scheduling system"""
    
    @staticmethod
    def schedule_report(db: Session, template_id: str, schedule_config: Dict, user_id: str) -> str:
        """Schedule Report."""
        """Schedule a report for automatic generation"""
        from app.models.financial_core import ReportRun
        
        scheduled_run = ReportRun(
            template_id=template_id,
            run_date=datetime.now(),
            parameters=json.dumps(schedule_config),
            status='scheduled',
            created_by=user_id
        )
        
        db.add(scheduled_run)
        db.commit()
        
        return scheduled_run.id
    
    @staticmethod
    def execute_scheduled_reports(db: Session) -> List[str]:
        """Execute Scheduled Reports."""
        """Execute all pending scheduled reports"""
        from app.models.financial_core import ReportRun, ReportTemplate
        
        pending_reports = db.query(ReportRun).filter(
            ReportRun.status == 'scheduled',
            ReportRun.run_date <= datetime.now()
        ).all()
        
        executed_reports = []
        
        for report_run in pending_reports:
            try:
                template = db.query(ReportTemplate).filter(
                    ReportTemplate.id == report_run.template_id
                ).first()
                
                if template:
                    # Generate report based on template
                    parameters = json.loads(report_run.parameters) if report_run.parameters else {}
                    
                    # Execute report generation
                    output_path = ReportScheduler._generate_scheduled_report(db, template, parameters)
                    
                    # Update report run
                    report_run.status = 'completed'
                    report_run.file_path = output_path
                    
                    executed_reports.append(report_run.id)
                
            except Exception as e:
                report_run.status = 'failed'
                print(f"Failed to execute report {report_run.id}: {e}")
        
        db.commit()
        return executed_reports
    
    @staticmethod
    def _generate_scheduled_report(db: Session, template: Any, parameters: Dict) -> str:
        """ Generate Scheduled Report."""
        """Generate report from template and parameters"""
        report_type = template.report_type
        
        if report_type == 'trial_balance':
            data = ReportGenerator.generate_trial_balance(db)
        elif report_type == 'balance_sheet':
            data = ReportGenerator.generate_balance_sheet(db)
        elif report_type == 'income_statement':
            start_date = datetime.fromisoformat(parameters.get('start_date', '2024-01-01')).date()
            end_date = datetime.fromisoformat(parameters.get('end_date', '2024-12-31')).date()
            data = ReportGenerator.generate_income_statement(db, start_date, end_date)
        else:
            raise ValueError(f"Unsupported report type: {report_type}")
        
        # Generate output file
        output_format = parameters.get('format', 'pdf')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if output_format == 'pdf':
            output_path = f"reports/{report_type}_{timestamp}.pdf"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            PDFReportGenerator.create_pdf_report(data, output_path)
        else:
            output_path = f"reports/{report_type}_{timestamp}.xlsx"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            ExcelReportGenerator.create_excel_report(data, output_path)
        
        return output_path

class CustomReportBuilder:
    """Drag-drop custom report builder"""
    
    @staticmethod
    def create_custom_report_template(db: Session, template_config: Dict, user_id: str) -> str:
        """Create Custom Report Template."""
        """Create custom report template"""
        from app.models.financial_core import ReportTemplate
        
        template = ReportTemplate(
            report_name=template_config['name'],
            report_type='custom',
            template_data=json.dumps(template_config),
            created_by=user_id
        )
        
        db.add(template)
        db.commit()
        
        return template.id
    
    @staticmethod
    def generate_custom_report(db: Session, template_id: str, parameters: Dict = None) -> Dict:
        """Generate Custom Report."""
        """Generate report from custom template"""
        from app.models.financial_core import ReportTemplate
        
        template = db.query(ReportTemplate).filter(
            ReportTemplate.id == template_id
        ).first()
        
        if not template:
            raise ValueError("Template not found")
        
        config = json.loads(template.template_data)
        
        # Build dynamic query based on template configuration
        query_parts = []
        joins = []
        
        for field in config.get('fields', []):
            if field['table'] == 'chart_of_accounts':
                query_parts.append(f"coa.{field['column']} as {field['alias']}")
                if 'chart_of_accounts' not in joins:
                    joins.append('chart_of_accounts coa')
            elif field['table'] == 'journal_entries':
                query_parts.append(f"je.{field['column']} as {field['alias']}")
                if 'journal_entries' not in joins:
                    joins.append('journal_entries je')
        
        # Build WHERE clause
        where_conditions = []
        for condition in config.get('filters', []):
            where_conditions.append(f"{condition['field']} {condition['operator']} '{condition['value']}'")
        
        # Construct SQL
        select_clause = "SELECT " + ", ".join(query_parts)
        from_clause = "FROM " + " JOIN ".join(joins) if joins else "FROM chart_of_accounts coa"
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        sql = f"{select_clause} {from_clause} {where_clause}"
        
        # Execute query
        result = db.execute(text(sql))
        rows = result.fetchall()
        
        # Format results
        columns = [field['alias'] for field in config.get('fields', [])]
        data = []
        for row in rows:
            data.append(dict(zip(columns, row)))
        
        return {
            "report_type": "custom",
            "template_name": template.report_name,
            "columns": columns,
            "data": data,
            "generated_at": datetime.now().isoformat()
        }
    
    @staticmethod
    def get_available_fields() -> Dict:
        """Get Available Fields."""
        """Get available fields for report builder"""
        return {
            "chart_of_accounts": [
                {"column": "account_code", "label": "Account Code", "type": "string"},
                {"column": "account_name", "label": "Account Name", "type": "string"},
                {"column": "account_type", "label": "Account Type", "type": "string"},
                {"column": "current_balance", "label": "Current Balance", "type": "decimal"},
                {"column": "normal_balance", "label": "Normal Balance", "type": "string"}
            ],
            "journal_entries": [
                {"column": "entry_number", "label": "Entry Number", "type": "string"},
                {"column": "description", "label": "Description", "type": "string"},
                {"column": "entry_date", "label": "Entry Date", "type": "date"},
                {"column": "total_debit", "label": "Total Debit", "type": "decimal"},
                {"column": "total_credit", "label": "Total Credit", "type": "decimal"}
            ],
            "vendors": [
                {"column": "vendor_code", "label": "Vendor Code", "type": "string"},
                {"column": "vendor_name", "label": "Vendor Name", "type": "string"},
                {"column": "current_balance", "label": "Balance", "type": "decimal"}
            ],
            "customers": [
                {"column": "customer_code", "label": "Customer Code", "type": "string"},
                {"column": "customer_name", "label": "Customer Name", "type": "string"},
                {"column": "current_balance", "label": "Balance", "type": "decimal"}
            ]
        }