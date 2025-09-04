"""
Simple test script for reporting system
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime
import json

# Connect to database
engine = create_engine('sqlite:///paksa_complete.db')
Session = sessionmaker(bind=engine)
db = Session()

def test_basic_reports():
    """Test basic report functionality"""
    print("=== Testing Basic Reporting System ===")
    
    # Test database connection
    print("1. Testing database connection...")
    try:
        result = db.execute(text("SELECT COUNT(*) FROM chart_of_accounts")).scalar()
        print(f"   Found {result} accounts in database")
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    # Test simple query
    print("2. Testing account query...")
    try:
        result = db.execute(text("SELECT account_code, account_name, current_balance FROM chart_of_accounts LIMIT 5")).fetchall()
        print(f"   Retrieved {len(result)} sample accounts")
        for row in result:
            print(f"     {row[0]} - {row[1]}: ${row[2]:,.2f}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test basic report data structure
    print("3. Testing report data structure...")
    try:
        # Simple trial balance calculation
        assets = db.execute(text("SELECT SUM(current_balance) FROM chart_of_accounts WHERE account_type = 'Asset'")).scalar() or 0
        liabilities = db.execute(text("SELECT SUM(current_balance) FROM chart_of_accounts WHERE account_type = 'Liability'")).scalar() or 0
        equity = db.execute(text("SELECT SUM(current_balance) FROM chart_of_accounts WHERE account_type = 'Equity'")).scalar() or 0
        revenue = db.execute(text("SELECT SUM(current_balance) FROM chart_of_accounts WHERE account_type = 'Revenue'")).scalar() or 0
        expenses = db.execute(text("SELECT SUM(current_balance) FROM chart_of_accounts WHERE account_type = 'Expense'")).scalar() or 0
        
        print(f"   Assets: ${assets:,.2f}")
        print(f"   Liabilities: ${liabilities:,.2f}")
        print(f"   Equity: ${equity:,.2f}")
        print(f"   Revenue: ${revenue:,.2f}")
        print(f"   Expenses: ${expenses:,.2f}")
        
        net_income = revenue - expenses
        print(f"   Net Income: ${net_income:,.2f}")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test PDF libraries
    print("4. Testing PDF generation libraries...")
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        
        # Create simple PDF
        os.makedirs('reports', exist_ok=True)
        doc = SimpleDocTemplate('reports/test_simple.pdf', pagesize=letter)
        styles = getSampleStyleSheet()
        story = [Paragraph("Test Report", styles['Title'])]
        doc.build(story)
        print("   PDF generation successful")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test Excel libraries
    print("5. Testing Excel generation libraries...")
    try:
        import pandas as pd
        
        # Create simple Excel
        data = {'Account': ['Cash', 'Accounts Receivable'], 'Balance': [50000, 25000]}
        df = pd.DataFrame(data)
        df.to_excel('reports/test_simple.xlsx', index=False)
        print("   Excel generation successful")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    print("=== Basic Test Complete ===")

if __name__ == "__main__":
    test_basic_reports()
    db.close()