#!/usr/bin/env python3
"""
Fix Service Connections - Remove Mock Data and Connect to Real Database
This script identifies and fixes all endpoints that return mock data
"""

import os
import re

def find_mock_endpoints():
    """Find all endpoints returning mock data in main.py"""
    main_py_path = "app/main.py"
    
    mock_patterns = [
        r'return \[.*\]',  # Direct array returns
        r'return {.*}',    # Direct dict returns with hardcoded data
        r'# Mock.*',       # Comments indicating mock data
        r'\"id\": \"[0-9]+\"',  # Hardcoded IDs
    ]
    
    issues = []
    
    if os.path.exists(main_py_path):
        with open(main_py_path, 'r') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines, 1):
            for pattern in mock_patterns:
                if re.search(pattern, line) and '@app.' in lines[max(0, i-10):i]:
                    issues.append({
                        'file': main_py_path,
                        'line': i,
                        'content': line.strip(),
                        'type': 'mock_data'
                    })
    
    return issues

def generate_service_fixes():
    """Generate fixes for service connections"""
    fixes = {
        'gl_endpoints': {
            'get_gl_accounts': '''
@app.get("/api/v1/gl/accounts")
async def get_gl_accounts(db: Session = Depends(get_db)):
    try:
        accounts = db.query(ChartOfAccounts).all()
        return {
            "accounts": [
                {
                    "id": str(acc.id),
                    "code": acc.account_code,
                    "name": acc.account_name,
                    "type": acc.account_type,
                    "balance": float(acc.current_balance or 0),
                }
                for acc in accounts
            ]
        }
    except Exception as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database error")
''',
            'create_gl_account': '''
@app.post("/api/v1/gl/accounts")
async def create_gl_account(account_data: dict, db: Session = Depends(get_db)):
    try:
        from app.models.core_models import ChartOfAccounts
        account = ChartOfAccounts(
            company_id=DEFAULT_TENANT_ID,
            account_code=account_data.get("code"),
            account_name=account_data.get("name"),
            account_type=account_data.get("type"),
            normal_balance=account_data.get("normal_balance", "Debit")
        )
        db.add(account)
        db.commit()
        db.refresh(account)
        return {
            "id": str(account.id),
            "code": account.account_code,
            "name": account.account_name,
        }
    except Exception as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create account")
'''
        },
        'ap_endpoints': {
            'get_vendors': '''
@app.get("/api/v1/ap/vendors")
async def get_vendors(db: Session = Depends(get_db)):
    try:
        from app.models.core_models import Vendor
        vendors = db.query(Vendor).all()
        return {
            "vendors": [
                {
                    "id": str(v.id),
                    "code": v.vendor_code,
                    "name": v.vendor_name,
                    "balance": float(v.current_balance or 0)
                }
                for v in vendors
            ]
        }
    except Exception as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database error")
'''
        },
        'hrm_endpoints': {
            'get_employees': '''
@app.get("/api/v1/hrm/employees")
async def get_employees(db: Session = Depends(get_db)):
    try:
        from app.models.core_models import Employee
        employees = db.query(Employee).all()
        return {
            "employees": [
                {
                    "id": str(e.id),
                    "code": e.employee_code,
                    "first_name": e.first_name,
                    "last_name": e.last_name,
                    "email": e.email,
                    "position": e.position,
                    "status": e.status
                }
                for e in employees
            ]
        }
    except Exception as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database error")
'''
        }
    }
    
    return fixes

def main():
    """Main function to analyze and report issues"""
    print("🔍 Analyzing service connections...")
    
    # Find mock endpoints
    mock_issues = find_mock_endpoints()
    
    print(f"\n📊 Found {len(mock_issues)} potential mock data issues:")
    for issue in mock_issues[:10]:  # Show first 10
        print(f"  📄 {issue['file']}:{issue['line']} - {issue['content'][:80]}...")
    
    # Generate fixes
    fixes = generate_service_fixes()
    
    print(f"\n🔧 Generated {len(fixes)} service fix templates")
    print("\n⚠️  MANUAL ACTIONS REQUIRED:")
    print("1. Run init_unified_db.py to create database tables")
    print("2. Replace mock endpoints in main.py with service calls")
    print("3. Add proper error handling to all endpoints")
    print("4. Remove localStorage fallbacks from frontend")
    print("5. Re-enable authentication middleware")
    
    print("\n📋 Priority Fixes:")
    print("- GL accounts endpoint (affects all financial reporting)")
    print("- Customer/Vendor endpoints (affects AR/AP modules)")
    print("- Employee endpoints (affects HRM/Payroll)")
    print("- Inventory endpoints (affects procurement)")

if __name__ == "__main__":
    main()