#!/usr/bin/env python3
"""Initialize database with sample data for production"""

from app.core.database import SessionLocal, init_db
from app.models.core_models import Customer, Vendor, ChartOfAccounts
import uuid

def init_sample_data():
    """Initialize database with minimal sample data"""
    db = SessionLocal()
    
    try:
        # Create sample chart of accounts
        accounts = [
            {"code": "1000", "name": "Cash", "type": "Asset"},
            {"code": "1200", "name": "Accounts Receivable", "type": "Asset"},
            {"code": "2000", "name": "Accounts Payable", "type": "Liability"},
            {"code": "3000", "name": "Owner's Equity", "type": "Equity"},
            {"code": "4000", "name": "Revenue", "type": "Revenue"},
            {"code": "5000", "name": "Expenses", "type": "Expense"}
        ]
        
        for acc_data in accounts:
            if not db.query(ChartOfAccounts).filter(ChartOfAccounts.account_code == acc_data["code"]).first():
                account = ChartOfAccounts(
                    id=uuid.uuid4(),
                    account_code=acc_data["code"],
                    account_name=acc_data["name"],
                    account_type=acc_data["type"],
                    is_active=True,
                    balance=0.0
                )
                db.add(account)
        
        # Create sample customers
        customers = [
            {"name": "ABC Corporation", "email": "contact@abc.com", "phone": "555-0123"},
            {"name": "XYZ Industries", "email": "info@xyz.com", "phone": "555-0456"}
        ]
        
        for cust_data in customers:
            if not db.query(Customer).filter(Customer.email == cust_data["email"]).first():
                customer = Customer(
                    id=uuid.uuid4(),
                    customer_code=f"CUST{len(db.query(Customer).all()) + 1:04d}",
                    customer_name=cust_data["name"],
                    email=cust_data["email"],
                    phone=cust_data["phone"],
                    credit_limit=50000.0,
                    current_balance=0.0,
                    payment_terms="net30",
                    status="active"
                )
                db.add(customer)
        
        # Create sample vendors
        vendors = [
            {"name": "ABC Supplies", "email": "billing@abcsupplies.com"},
            {"name": "XYZ Services", "email": "accounts@xyzservices.com"}
        ]
        
        for vend_data in vendors:
            if not db.query(Vendor).filter(Vendor.email == vend_data["email"]).first():
                vendor = Vendor(
                    id=uuid.uuid4(),
                    vendor_code=f"VEND{len(db.query(Vendor).all()) + 1:04d}",
                    vendor_name=vend_data["name"],
                    email=vend_data["email"],
                    current_balance=0.0,
                    payment_terms="net30",
                    status="active"
                )
                db.add(vendor)
        
        db.commit()
        print("✅ Sample data initialized successfully")
        
    except Exception as e:
        print(f"❌ Error initializing sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🔄 Initializing database...")
    init_db()
    init_sample_data()
    print("✅ Database initialization complete")