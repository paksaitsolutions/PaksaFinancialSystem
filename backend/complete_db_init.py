#!/usr/bin/env python3
"""Complete database initialization for all modules"""

from app.core.database import SessionLocal, init_db
from app.models.core_models import *
import uuid
from datetime import datetime, date
import hashlib

def get_password_hash(password: str) -> str:
    """Simple hash for initialization - replace with bcrypt in production"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_complete_data():
    """Initialize database with comprehensive sample data for all modules"""
    db = SessionLocal()
    
    try:
        # Users - only development accounts
        users = [
            {"username": "admin", "email": "admin@paksa.com", "name": "System Administrator", "password": "admin123", "superuser": True},
            {"username": "user", "email": "user@paksa.com", "name": "Regular User", "password": "user123", "superuser": False}
        ]
        
        for user_data in users:
            if not db.query(User).filter(User.email == user_data["email"]).first():
                user = User(
                    id=uuid.uuid4(),
                    username=user_data["username"],
                    email=user_data["email"],
                    full_name=user_data["name"],
                    hashed_password=get_password_hash(user_data["password"]),
                    is_active=True,
                    is_superuser=user_data["superuser"]
                )
                db.add(user)
        
        # Chart of Accounts
        accounts = [
            {"code": "1000", "name": "Cash", "type": "Asset", "balance": 50000},
            {"code": "1200", "name": "Accounts Receivable", "type": "Asset", "balance": 25000},
            {"code": "1300", "name": "Inventory", "type": "Asset", "balance": 15000},
            {"code": "1500", "name": "Equipment", "type": "Asset", "balance": 75000},
            {"code": "2000", "name": "Accounts Payable", "type": "Liability", "balance": 12000},
            {"code": "2100", "name": "Accrued Expenses", "type": "Liability", "balance": 5000},
            {"code": "3000", "name": "Owner's Equity", "type": "Equity", "balance": 100000},
            {"code": "4000", "name": "Sales Revenue", "type": "Revenue", "balance": 0},
            {"code": "5000", "name": "Cost of Goods Sold", "type": "Expense", "balance": 0},
            {"code": "6000", "name": "Operating Expenses", "type": "Expense", "balance": 0}
        ]
        
        for acc_data in accounts:
            if not db.query(ChartOfAccounts).filter(ChartOfAccounts.account_code == acc_data["code"]).first():
                account = ChartOfAccounts(
                    id=uuid.uuid4(),
                    account_code=acc_data["code"],
                    account_name=acc_data["name"],
                    account_type=acc_data["type"],
                    balance=acc_data["balance"],
                    is_active=True
                )
                db.add(account)
        
        # Customers
        customers = [
            {"name": "ABC Corporation", "email": "contact@abc.com", "phone": "555-0123", "credit_limit": 50000},
            {"name": "XYZ Industries", "email": "info@xyz.com", "phone": "555-0456", "credit_limit": 75000},
            {"name": "Tech Solutions Ltd", "email": "hello@tech.com", "phone": "555-0789", "credit_limit": 25000}
        ]
        
        for cust_data in customers:
            if not db.query(Customer).filter(Customer.email == cust_data["email"]).first():
                customer = Customer(
                    id=uuid.uuid4(),
                    customer_code=f"CUST{len(db.query(Customer).all()) + 1:04d}",
                    customer_name=cust_data["name"],
                    email=cust_data["email"],
                    phone=cust_data["phone"],
                    credit_limit=cust_data["credit_limit"],
                    current_balance=0.0,
                    payment_terms="net30",
                    status="active"
                )
                db.add(customer)
        
        # Vendors
        vendors = [
            {"name": "ABC Supplies", "email": "billing@abcsupplies.com", "phone": "555-1001"},
            {"name": "XYZ Services", "email": "accounts@xyzservices.com", "phone": "555-1002"},
            {"name": "Office Depot", "email": "ap@officedepot.com", "phone": "555-1003"}
        ]
        
        for vend_data in vendors:
            if not db.query(Vendor).filter(Vendor.email == vend_data["email"]).first():
                vendor = Vendor(
                    id=uuid.uuid4(),
                    vendor_code=f"VEND{len(db.query(Vendor).all()) + 1:04d}",
                    vendor_name=vend_data["name"],
                    email=vend_data["email"],
                    phone=vend_data["phone"],
                    current_balance=0.0,
                    payment_terms="net30",
                    status="active"
                )
                db.add(vendor)
        
        # Bank Accounts
        bank_accounts = [
            {"name": "Main Checking", "number": "12345678", "bank": "First National Bank", "balance": 75000},
            {"name": "Savings Account", "number": "87654321", "bank": "First National Bank", "balance": 150000}
        ]
        
        for bank_data in bank_accounts:
            if not db.query(BankAccount).filter(BankAccount.account_number == bank_data["number"]).first():
                account = BankAccount(
                    id=uuid.uuid4(),
                    account_name=bank_data["name"],
                    account_number=bank_data["number"],
                    bank_name=bank_data["bank"],
                    current_balance=bank_data["balance"],
                    is_active=True
                )
                db.add(account)
        
        # Employees
        employees = [
            {"first": "John", "last": "Doe", "email": "john.doe@company.com", "dept": "IT", "pos": "Developer"},
            {"first": "Jane", "last": "Smith", "email": "jane.smith@company.com", "dept": "Finance", "pos": "Accountant"},
            {"first": "Bob", "last": "Johnson", "email": "bob.johnson@company.com", "dept": "Sales", "pos": "Manager"}
        ]
        
        for emp_data in employees:
            if not db.query(Employee).filter(Employee.email == emp_data["email"]).first():
                employee = Employee(
                    id=uuid.uuid4(),
                    employee_code=f"EMP{len(db.query(Employee).all()) + 1:04d}",
                    first_name=emp_data["first"],
                    last_name=emp_data["last"],
                    email=emp_data["email"],
                    department=emp_data["dept"],
                    position=emp_data["pos"],
                    hire_date=date.today(),
                    salary=60000.0,
                    status="active"
                )
                db.add(employee)
        
        # Inventory Items
        items = [
            {"name": "Product A", "sku": "SKU001", "qty": 100, "cost": 25.00},
            {"name": "Product B", "sku": "SKU002", "qty": 50, "cost": 45.00},
            {"name": "Service Package", "sku": "SRV001", "qty": 0, "cost": 100.00}
        ]
        
        for item_data in items:
            if not db.query(InventoryItem).filter(InventoryItem.sku == item_data["sku"]).first():
                item = InventoryItem(
                    id=uuid.uuid4(),
                    item_name=item_data["name"],
                    sku=item_data["sku"],
                    quantity_on_hand=item_data["qty"],
                    unit_cost=item_data["cost"],
                    is_active=True
                )
                db.add(item)
        
        # Asset Categories
        categories = [
            {"name": "IT Equipment", "desc": "Computers, servers, networking", "life": 5},
            {"name": "Furniture", "desc": "Office furniture and fixtures", "life": 10},
            {"name": "Vehicles", "desc": "Company vehicles", "life": 8}
        ]
        
        for cat_data in categories:
            if not db.query(AssetCategory).filter(AssetCategory.name == cat_data["name"]).first():
                category = AssetCategory(
                    id=uuid.uuid4(),
                    company_id=uuid.uuid4(),
                    name=cat_data["name"],
                    description=cat_data["desc"],
                    default_useful_life=cat_data["life"]
                )
                db.add(category)
        
        # Fixed Assets
        assets = [
            {"number": "FA001", "name": "Office Computer", "cost": 1500, "depreciation": 450},
            {"number": "FA002", "name": "Office Desk", "cost": 800, "depreciation": 144},
            {"number": "FA003", "name": "Company Vehicle", "cost": 28000, "depreciation": 2083}
        ]
        
        for asset_data in assets:
            if not db.query(FixedAsset).filter(FixedAsset.asset_number == asset_data["number"]).first():
                asset = FixedAsset(
                    id=uuid.uuid4(),
                    company_id=uuid.uuid4(),
                    asset_number=asset_data["number"],
                    asset_name=asset_data["name"],
                    purchase_cost=asset_data["cost"],
                    accumulated_depreciation=asset_data["depreciation"],
                    current_value=asset_data["cost"] - asset_data["depreciation"],
                    purchase_date=date.today(),
                    useful_life_years=5,
                    status="active"
                )
                db.add(asset)
        
        # Tax Rates
        tax_rates = [
            {"name": "Sales Tax", "rate": 8.25, "jurisdiction": "State"},
            {"name": "Federal Income Tax", "rate": 21.0, "jurisdiction": "Federal"},
            {"name": "State Income Tax", "rate": 5.0, "jurisdiction": "State"}
        ]
        
        for tax_data in tax_rates:
            if not db.query(TaxRate).filter(TaxRate.tax_name == tax_data["name"]).first():
                tax_rate = TaxRate(
                    id=uuid.uuid4(),
                    tax_name=tax_data["name"],
                    rate=tax_data["rate"],
                    jurisdiction=tax_data["jurisdiction"],
                    is_active=True
                )
                db.add(tax_rate)
        
        # Budgets
        budgets = [
            {"name": "2024 Annual Budget", "year": 2024, "amount": 1000000, "status": "approved"},
            {"name": "Q1 2024 Marketing", "year": 2024, "amount": 50000, "status": "draft"}
        ]
        
        for budget_data in budgets:
            if not db.query(Budget).filter(Budget.budget_name == budget_data["name"]).first():
                budget = Budget(
                    id=uuid.uuid4(),
                    budget_name=budget_data["name"],
                    budget_year=budget_data["year"],
                    total_amount=budget_data["amount"],
                    status=budget_data["status"]
                )
                db.add(budget)
        
        db.commit()
        print("✅ Complete sample data initialized successfully")
        
        # Print summary
        print(f"📊 Data Summary:")
        print(f"   - Chart of Accounts: {db.query(ChartOfAccounts).count()} accounts")
        print(f"   - Customers: {db.query(Customer).count()} customers")
        print(f"   - Vendors: {db.query(Vendor).count()} vendors")
        print(f"   - Bank Accounts: {db.query(BankAccount).count()} accounts")
        print(f"   - Employees: {db.query(Employee).count()} employees")
        print(f"   - Inventory Items: {db.query(InventoryItem).count()} items")
        print(f"   - Users: {db.query(User).count()} users")
        print(f"   - Fixed Assets: {db.query(FixedAsset).count()} assets")
        print(f"   - Asset Categories: {db.query(AssetCategory).count()} categories")
        print(f"   - Tax Rates: {db.query(TaxRate).count()} rates")
        print(f"   - Budgets: {db.query(Budget).count()} budgets")
        
    except Exception as e:
        print(f"❌ Error initializing complete data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🔄 Initializing complete database...")
    init_db()
    init_complete_data()
    print("✅ Complete database initialization finished")