#!/usr/bin/env python3
"""
Initialize AR module with test data
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
from app.models.accounts_receivable.customer import Customer, CustomerContact
from app.models.accounts_receivable.ar_invoice import ARInvoice, ARInvoiceLineItem, ARPayment
from app.models.enums import CustomerStatus, InvoiceStatus, PaymentTerms

async def create_test_customers(db: AsyncSession):
    """Create test customers"""
    customers_data = [
        {
            "code": "CUST001",
            "name": "Acme Corporation",
            "legal_name": "Acme Corporation Inc.",
            "tax_id": "12-3456789",
            "email": "billing@acmecorp.com",
            "phone": "(555) 123-4567",
            "address_line1": "123 Business Ave",
            "city": "New York",
            "state": "NY",
            "postal_code": "10001",
            "country": "USA",
            "payment_terms": PaymentTerms.NET_30,
            "credit_limit": Decimal("50000.00"),
            "status": CustomerStatus.ACTIVE
        },
        {
            "code": "CUST002", 
            "name": "Global Tech Solutions",
            "legal_name": "Global Technology Solutions LLC",
            "tax_id": "98-7654321",
            "email": "accounts@globaltech.com",
            "phone": "(555) 987-6543",
            "address_line1": "456 Tech Blvd",
            "city": "San Francisco",
            "state": "CA", 
            "postal_code": "94105",
            "country": "USA",
            "payment_terms": PaymentTerms.NET_15,
            "credit_limit": Decimal("75000.00"),
            "status": CustomerStatus.ACTIVE
        },
        {
            "code": "CUST003",
            "name": "Metro Manufacturing",
            "legal_name": "Metropolitan Manufacturing Co.",
            "tax_id": "55-9876543",
            "email": "billing@metromanuf.com",
            "phone": "(555) 555-0123",
            "address_line1": "789 Industrial Way",
            "city": "Chicago",
            "state": "IL",
            "postal_code": "60601",
            "country": "USA",
            "payment_terms": PaymentTerms.NET_45,
            "credit_limit": Decimal("100000.00"),
            "status": CustomerStatus.ACTIVE
        },
        {
            "code": "CUST004",
            "name": "Retail Plus Inc",
            "legal_name": "Retail Plus Incorporated",
            "tax_id": "33-1122334",
            "email": "ap@retailplus.com",
            "phone": "(555) 444-5566",
            "address_line1": "321 Commerce St",
            "city": "Dallas",
            "state": "TX",
            "postal_code": "75201",
            "country": "USA",
            "payment_terms": PaymentTerms.NET_30,
            "credit_limit": Decimal("25000.00"),
            "status": CustomerStatus.ACTIVE
        }
    ]
    
    customers = []
    for customer_data in customers_data:
        customer = Customer(**customer_data)
        db.add(customer)
        customers.append(customer)
    
    await db.flush()
    return customers

async def create_test_invoices(db: AsyncSession, customers):
    """Create test invoices"""
    invoices_data = [
        {
            "customer": customers[0],
            "invoice_number": "INV-2024-001",
            "invoice_date": date.today() - timedelta(days=45),
            "due_date": date.today() - timedelta(days=15),
            "description": "Professional services - Q1 2024",
            "subtotal": Decimal("15000.00"),
            "tax_amount": Decimal("1200.00"),
            "total_amount": Decimal("16200.00"),
            "balance_due": Decimal("16200.00"),
            "status": InvoiceStatus.SENT,
            "payment_terms": PaymentTerms.NET_30
        },
        {
            "customer": customers[1],
            "invoice_number": "INV-2024-002",
            "invoice_date": date.today() - timedelta(days=20),
            "due_date": date.today() - timedelta(days=5),
            "description": "Software licensing and support",
            "subtotal": Decimal("25000.00"),
            "tax_amount": Decimal("2000.00"),
            "total_amount": Decimal("27000.00"),
            "balance_due": Decimal("27000.00"),
            "status": InvoiceStatus.OVERDUE,
            "payment_terms": PaymentTerms.NET_15
        },
        {
            "customer": customers[2],
            "invoice_number": "INV-2024-003",
            "invoice_date": date.today() - timedelta(days=60),
            "due_date": date.today() - timedelta(days=15),
            "description": "Manufacturing equipment lease",
            "subtotal": Decimal("45000.00"),
            "tax_amount": Decimal("3600.00"),
            "total_amount": Decimal("48600.00"),
            "balance_due": Decimal("0.00"),
            "paid_amount": Decimal("48600.00"),
            "status": InvoiceStatus.PAID,
            "payment_terms": PaymentTerms.NET_45
        },
        {
            "customer": customers[0],
            "invoice_number": "INV-2024-004",
            "invoice_date": date.today() - timedelta(days=10),
            "due_date": date.today() + timedelta(days=20),
            "description": "Consulting services - February",
            "subtotal": Decimal("8500.00"),
            "tax_amount": Decimal("680.00"),
            "total_amount": Decimal("9180.00"),
            "balance_due": Decimal("9180.00"),
            "status": InvoiceStatus.SENT,
            "payment_terms": PaymentTerms.NET_30
        },
        {
            "customer": customers[3],
            "invoice_number": "INV-2024-005",
            "invoice_date": date.today() - timedelta(days=35),
            "due_date": date.today() - timedelta(days=5),
            "description": "Retail inventory management system",
            "subtotal": Decimal("12000.00"),
            "tax_amount": Decimal("960.00"),
            "total_amount": Decimal("12960.00"),
            "balance_due": Decimal("12960.00"),
            "status": InvoiceStatus.OVERDUE,
            "payment_terms": PaymentTerms.NET_30
        }
    ]
    
    invoices = []
    for invoice_data in invoices_data:
        customer = invoice_data.pop("customer")
        invoice = ARInvoice(customer_id=customer.id, **invoice_data)
        db.add(invoice)
        invoices.append(invoice)
    
    await db.flush()
    return invoices

async def create_test_payments(db: AsyncSession, customers, invoices):
    """Create test payments"""
    payments_data = [
        {
            "customer": customers[2],
            "payment_number": "PMT-2024-001",
            "payment_date": date.today() - timedelta(days=10),
            "amount": Decimal("48600.00"),
            "payment_method": "Wire Transfer",
            "reference": "WIRE-20240115-001",
            "memo": "Payment for manufacturing equipment lease",
            "status": "completed"
        },
        {
            "customer": customers[1],
            "payment_number": "PMT-2024-002",
            "payment_date": date.today() - timedelta(days=2),
            "amount": Decimal("13500.00"),
            "payment_method": "ACH",
            "reference": "ACH-20240123-002",
            "memo": "Partial payment for software licensing",
            "status": "completed"
        }
    ]
    
    payments = []
    for payment_data in payments_data:
        customer = payment_data.pop("customer")
        payment = ARPayment(customer_id=customer.id, **payment_data)
        db.add(payment)
        payments.append(payment)
    
    await db.flush()
    return payments

async def main():
    """Initialize AR test data"""
    print("Initializing AR module with test data...")
    
    async with get_db_session() as db:
        try:
            # Create test data
            print("Creating test customers...")
            customers = await create_test_customers(db)
            
            print("Creating test invoices...")
            invoices = await create_test_invoices(db, customers)
            
            print("Creating test payments...")
            payments = await create_test_payments(db, customers, invoices)
            
            # Commit all changes
            await db.commit()
            
            print(f"✅ Successfully created:")
            print(f"   - {len(customers)} customers")
            print(f"   - {len(invoices)} invoices")
            print(f"   - {len(payments)} payments")
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error initializing AR data: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(main())