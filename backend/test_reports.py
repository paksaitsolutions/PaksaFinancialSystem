"""
Test script for reporting system
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.services.reporting_engine import *
from datetime import date, datetime
import json

# Connect to database
engine = create_engine('sqlite:///paksa_complete.db')
Session = sessionmaker(bind=engine)
db = Session()

def test_reports():
    """Test all report generation functions"""
    print("=== Testing Reporting System ===\n")
    
    # Test Trial Balance
    print("1. Testing Trial Balance...")
    try:
        trial_balance = ReportGenerator.generate_trial_balance(db)
        print(f"   ✓ Generated trial balance with {len(trial_balance['accounts'])} accounts")
        print(f"   ✓ Total Debits: ${trial_balance['total_debits']:,.2f}")
        print(f"   ✓ Total Credits: ${trial_balance['total_credits']:,.2f}")
        print(f"   ✓ Balanced: {trial_balance['is_balanced']}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test Balance Sheet
    print("\n2. Testing Balance Sheet...")
    try:
        balance_sheet = ReportGenerator.generate_balance_sheet(db)
        print(f"   ✓ Generated balance sheet")
        print(f"   ✓ Total Assets: ${balance_sheet['assets']['total']:,.2f}")
        print(f"   ✓ Total Liabilities: ${balance_sheet['liabilities']['total']:,.2f}")
        print(f"   ✓ Total Equity: ${balance_sheet['equity']['total']:,.2f}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test Income Statement
    print("\n3. Testing Income Statement...")
    try:
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        income_statement = ReportGenerator.generate_income_statement(db, start_date, end_date)
        print(f"   ✓ Generated income statement")
        print(f"   ✓ Total Revenue: ${income_statement['revenue']['total']:,.2f}")
        print(f"   ✓ Total Expenses: ${income_statement['expenses']['total']:,.2f}")
        print(f"   ✓ Net Income: ${income_statement['net_income']:,.2f}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test Cash Flow
    print("\n4. Testing Cash Flow Statement...")
    try:
        cash_flow = ReportGenerator.generate_cash_flow(db, start_date, end_date)
        print(f"   ✓ Generated cash flow statement")
        print(f"   ✓ Operating Cash Flow: ${cash_flow['operating_activities']['net_operating_cash']:,.2f}")
        print(f"   ✓ Ending Cash Balance: ${cash_flow['ending_cash_balance']:,.2f}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test PDF Generation
    print("\n5. Testing PDF Generation...")
    try:
        os.makedirs('reports', exist_ok=True)
        pdf_path = PDFReportGenerator.create_pdf_report(trial_balance, 'reports/test_trial_balance.pdf')
        print(f"   ✓ Generated PDF report: {pdf_path}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test Excel Generation
    print("\n6. Testing Excel Generation...")
    try:
        excel_path = ExcelReportGenerator.create_excel_report(trial_balance, 'reports/test_trial_balance.xlsx')
        print(f"   ✓ Generated Excel report: {excel_path}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test Custom Report Builder
    print("\n7. Testing Custom Report Builder...")
    try:
        fields = CustomReportBuilder.get_available_fields()
        print(f"   ✓ Available fields loaded: {len(fields)} tables")
        
        # Create sample template
        template_config = {
            "name": "Test Custom Report",
            "fields": [
                {"table": "chart_of_accounts", "column": "account_code", "alias": "code", "label": "Account Code"},
                {"table": "chart_of_accounts", "column": "account_name", "alias": "name", "label": "Account Name"},
                {"table": "chart_of_accounts", "column": "current_balance", "alias": "balance", "label": "Balance"}
            ],
            "filters": [
                {"field": "account_type", "operator": "=", "value": "Asset"}
            ]
        }
        
        template_id = CustomReportBuilder.create_custom_report_template(db, template_config, "test_user")
        print(f"   ✓ Created custom template: {template_id}")
        
        # Generate custom report
        custom_report = CustomReportBuilder.generate_custom_report(db, template_id)
        print(f"   ✓ Generated custom report with {len(custom_report['data'])} rows")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test Report Scheduling
    print("\n8. Testing Report Scheduling...")
    try:
        schedule_config = {
            "format": "pdf",
            "frequency": "monthly",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }
        
        run_id = ReportScheduler.schedule_report(db, template_id, schedule_config, "test_user")
        print(f"   ✓ Scheduled report: {run_id}")
        
        # Execute scheduled reports
        executed = ReportScheduler.execute_scheduled_reports(db)
        print(f"   ✓ Executed {len(executed)} scheduled reports")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n=== Reporting System Test Complete ===")

if __name__ == "__main__":
    test_reports()
    db.close()