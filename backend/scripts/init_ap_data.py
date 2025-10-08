#!/usr/bin/env python3
"""
Initialize AP module with test data
"""
import asyncio
import sys
import os
from datetime import date, datetime, timedelta
from decimal import Decimal

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.models.accounts_payable.vendor import Vendor, VendorContact
from app.models.accounts_payable.invoice import APInvoice, APInvoiceLineItem, APPayment
from app.models.accounts_payable.credit_memo import CreditMemo
from app.models.enums import VendorStatus, InvoiceStatus, PaymentTerms

async def create_test_vendors(db: AsyncSession):
    """Create test vendors"""
    vendors_data = [
        {
            "code": "VEND001",
            "name": "ABC Supplies Co.",
            "legal_name": "ABC Supplies Company LLC",
            "tax_id": "12-3456789",
            "email": "billing@abcsupplies.com",
            "phone": "(555) 123-4567",
            "address_line1": "123 Business St",
            "city": "New York",
            "state": "NY",
            "postal_code": "10001",
            "country": "USA",
            "payment_terms": PaymentTerms.NET_30,
            "is_1099": True,
            "status": VendorStatus.ACTIVE
        },
        {
            "code": "VEND002", 
            "name": "XYZ Services Ltd.",
            "legal_name": "XYZ Professional Services Limited",
            "tax_id": "98-7654321",
            "email": "accounts@xyzservices.com",
            "phone": "(555) 987-6543",
            "address_line1": "456 Service Ave",
            "city": "Los Angeles",
            "state": "CA", 
            "postal_code": "90210",
            "country": "USA",
            "payment_terms": PaymentTerms.NET_15,
            "is_1099": False,
            "status": VendorStatus.ACTIVE
        },
        {
            "code": "VEND003",
            "name": "Tech Solutions Inc.",
            "legal_name": "Technology Solutions Incorporated",
            "tax_id": "55-9876543",
            "email": "billing@techsolutions.com",
            "phone": "(555) 555-0123",
            "address_line1": "789 Tech Blvd",
            "city": "Austin",
            "state": "TX",
            "postal_code": "73301",
            "country": "USA",
            "payment_terms": PaymentTerms.NET_45,
            "is_1099": True,
            "status": VendorStatus.ACTIVE
        }
    ]
    
    vendors = []
    for vendor_data in vendors_data:
        vendor = Vendor(**vendor_data)
        db.add(vendor)
        vendors.append(vendor)
    
    await db.flush()
    return vendors

async def create_test_invoices(db: AsyncSession, vendors):
    """Create test invoices"""
    invoices_data = [
        {
            "vendor": vendors[0],
            "invoice_number": "INV-2024-001",
            "invoice_date": date.today() - timedelta(days=30),
            "due_date": date.today() - timedelta(days=0),
            "description": "Office supplies and equipment",
            "subtotal": Decimal("2500.00"),
            "tax_amount": Decimal("200.00"),
            "total_amount": Decimal("2700.00"),
            "balance_due": Decimal("2700.00"),
            "status": InvoiceStatus.PENDING,
            "payment_terms": PaymentTerms.NET_30
        },
        {
            "vendor": vendors[1],
            "invoice_number": "SRV-2024-045",
            "invoice_date": date.today() - timedelta(days=15),
            "due_date": date.today() + timedelta(days=0),
            "description": "Professional consulting services",
            "subtotal": Decimal("5000.00"),
            "tax_amount": Decimal("400.00"),
            "total_amount": Decimal("5400.00"),
            "balance_due": Decimal("5400.00"),
            "status": InvoiceStatus.APPROVED,
            "payment_terms": PaymentTerms.NET_15
        },
        {
            "vendor": vendors[2],
            "invoice_number": "TECH-2024-012",
            "invoice_date": date.today() - timedelta(days=60),
            "due_date": date.today() - timedelta(days=15),
            "description": "Software licensing and support",
            "subtotal": Decimal("12000.00"),
            "tax_amount": Decimal("960.00"),
            "total_amount": Decimal("12960.00"),
            "balance_due": Decimal("0.00"),
            "paid_amount": Decimal("12960.00"),
            "status": InvoiceStatus.PAID,
            "payment_terms": PaymentTerms.NET_45
        },
        {
            "vendor": vendors[0],
            "invoice_number": "INV-2024-002",
            "invoice_date": date.today() - timedelta(days=5),
            "due_date": date.today() + timedelta(days=25),
            "description": "Monthly office supplies",
            "subtotal": Decimal("850.00"),
            "tax_amount": Decimal("68.00"),
            "total_amount": Decimal("918.00"),
            "balance_due": Decimal("918.00"),
            "status": InvoiceStatus.DRAFT,
            "payment_terms": PaymentTerms.NET_30
        }
    ]
    
    invoices = []
    for invoice_data in invoices_data:
        vendor = invoice_data.pop("vendor")
        invoice = APInvoice(vendor_id=vendor.id, **invoice_data)
        db.add(invoice)
        invoices.append(invoice)
    
    await db.flush()
    return invoices

async def create_test_payments(db: AsyncSession, vendors, invoices):
    """Create test payments"""
    payments_data = [
        {
            "vendor": vendors[2],
            "payment_number": "PAY-2024-001",
            "payment_date": date.today() - timedelta(days=10),
            "amount": Decimal("12960.00"),
            "payment_method": "ACH",
            "reference": "ACH-20240115-001",
            "memo": "Payment for software licensing",
            "status": "completed"
        },
        {
            "vendor": vendors[1],
            "payment_number": "PAY-2024-002",
            "payment_date": date.today(),
            "amount": Decimal("5400.00"),
            "payment_method": "Check",
            "reference": "CHK-1001",
            "memo": "Payment for consulting services",
            "status": "pending"
        }
    ]
    
    payments = []
    for payment_data in payments_data:
        vendor = payment_data.pop("vendor")
        payment = APPayment(vendor_id=vendor.id, **payment_data)
        db.add(payment)
        payments.append(payment)
    
    await db.flush()
    return payments

async def create_test_credit_memos(db: AsyncSession, vendors):
    """Create test credit memos"""
    credit_memos_data = [
        {
            "vendor": vendors[0],
            "credit_memo_number": "CM-2024-001",
            "credit_date": date.today() - timedelta(days=7),
            "amount": Decimal("150.00"),
            "applied_amount": Decimal("0.00"),
            "remaining_amount": Decimal("150.00"),
            "description": "Return of damaged office supplies",
            "status": "active"
        }
    ]
    
    credit_memos = []
    for memo_data in credit_memos_data:
        vendor = memo_data.pop("vendor")
        memo = CreditMemo(vendor_id=vendor.id, **memo_data)
        db.add(memo)
        credit_memos.append(memo)
    
    await db.flush()
    return credit_memos

async def main():
    """Initialize AP test data"""
    print("Initializing AP module with test data...")
    
    async with get_db_session() as db:
        try:
            # Create test data
            print("Creating test vendors...")
            vendors = await create_test_vendors(db)
            
            print("Creating test invoices...")
            invoices = await create_test_invoices(db, vendors)
            
            print("Creating test payments...")
            payments = await create_test_payments(db, vendors, invoices)
            
            print("Creating test credit memos...")
            credit_memos = await create_test_credit_memos(db, vendors)
            
            # Commit all changes
            await db.commit()
            
            print(f"✅ Successfully created:")
            print(f"   - {len(vendors)} vendors")
            print(f"   - {len(invoices)} invoices")
            print(f"   - {len(payments)} payments")
            print(f"   - {len(credit_memos)} credit memos")
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error initializing AP data: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(main())