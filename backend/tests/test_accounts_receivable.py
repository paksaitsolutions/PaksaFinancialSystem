"""
Tests for the Accounts Receivable module.
"""
import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4, UUID

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.modules.core_financials.accounts_receivable import models, schemas, services
from app.modules.core_financials.accounts_receivable.models import Customer
from app.modules.core_financials.accounting.models import GLAccount
from app.modules.cross_cutting.auth.models import User, Role, Permission
from core.database import Base, engine, TestingSessionLocal
from core.security import get_password_hash

# Test client
client = TestClient(app)

# Test data
TEST_CUSTOMER = {
    "name": "Test Customer",
    "email": "test@customer.com",
    "phone": "+1234567890",
    "billing_address": "123 Test St, Test City",
    "shipping_address": "123 Test St, Test City",
    "tax_id": "123456789",
    "payment_terms": 30,
}

TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User",
}

TEST_ROLE = {
    "name": "TestRole",
    "description": "Test Role",
    "permissions": ["read", "write", "admin"],
}

# Fixtures
@pytest.fixture(scope="module")
def db():
    """Create a test database session."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        # Clean up tables
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def test_role(db: Session):
    """Create a test role."""
    role = Role(**TEST_ROLE)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role

@pytest.fixture(scope="module")
def test_user(db: Session, test_role: Role):
    """Create a test user."""
    user_data = TEST_USER.copy()
    user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
    user = User(**user_data, role_id=test_role.id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(scope="module")
def test_customer(db: Session):
    """Create a test customer."""
    customer = Customer(**TEST_CUSTOMER)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer

@pytest.fixture(scope="module")
def test_gl_accounts(db: Session):
    """Create test GL accounts."""
    # Create AR account
    ar_account = GLAccount(
        account_number="1200",
        name="Accounts Receivable",
        account_type="asset",
        description="Accounts Receivable",
        is_active=True,
    )
    
    # Create revenue account
    revenue_account = GLAccount(
        account_number="4000",
        name="Sales Revenue",
        account_type="revenue",
        description="Sales Revenue",
        is_active=True,
    )
    
    db.add_all([ar_account, revenue_account])
    db.commit()
    db.refresh(ar_account)
    db.refresh(revenue_account)
    
    return {"ar": ar_account, "revenue": revenue_account}

@pytest.fixture(scope="module")
def auth_headers(test_user: User):
    """Get authentication headers."""
    # Login to get access token
    response = client.post(
        "/api/v1/auth/login",
        data={"username": TEST_USER["email"], "password": TEST_USER["password"]},
    )
    assert response.status_code == status.HTTP_200_OK
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# Test cases
class TestInvoiceAPI:
    """Test cases for Invoice API endpoints."""
    
    def test_create_invoice(self, db: Session, test_customer: Customer, test_gl_accounts: dict, auth_headers: dict):
        """Test creating a new invoice."""
        invoice_data = {
            "customer_id": str(test_customer.id),
            "issue_date": str(date.today()),
            "due_date": str(date.today() + timedelta(days=30)),
            "po_number": "PO123",
            "terms": "Net 30",
            "notes": "Test invoice",
            "invoice_items": [
                {
                    "description": "Test Item 1",
                    "quantity": 2,
                    "unit_price": "100.00",
                    "discount_percent": "10.00",
                    "tax_rate": "8.25",
                    "gl_account_id": str(test_gl_accounts["revenue"].id),
                },
                {
                    "description": "Test Item 2",
                    "quantity": 1,
                    "unit_price": "200.00",
                    "discount_percent": "0.00",
                    "tax_rate": "8.25",
                    "gl_account_id": str(test_gl_accounts["revenue"].id),
                },
            ],
        }
        
        response = client.post(
            "/api/v1/accounts-receivable/invoices/",
            json=invoice_data,
            headers=auth_headers,
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        # Verify response data
        assert "id" in data
        assert data["invoice_number"].startswith("INV-")
        assert data["customer_id"] == str(test_customer.id)
        assert data["status"] == "draft"
        assert data["subtotal"] == "400.00"  # (2*100) + (1*200)
        assert data["discount_amount"] == "20.00"  # 10% of 200 (first item only)
        assert data["tax_amount"] == "31.35"  # 8.25% of 380
        assert data["total_amount"] == "411.35"  # 400 - 20 + 31.35
        assert data["balance_due"] == data["total_amount"]  # No payments yet
        assert len(data["invoice_items"]) == 2
    
    def test_get_invoice(self, db: Session, auth_headers: dict):
        """Test retrieving an invoice by ID."""
        # First, create an invoice
        invoice = db.query(models.Invoice).first()
        assert invoice is not None
        
        response = client.get(
            f"/api/v1/accounts-receivable/invoices/{invoice.id}",
            headers=auth_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(invoice.id)
        assert data["invoice_number"] == invoice.invoice_number
    
    def test_list_invoices(self, auth_headers: dict):
        """Test listing invoices with filters."""
        response = client.get(
            "/api/v1/accounts-receivable/invoices/",
            headers=auth_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_send_invoice(self, db: Session, auth_headers: dict):
        """Test sending an invoice."""
        # Get a draft invoice
        invoice = db.query(models.Invoice).filter(
            models.Invoice.status == models.InvoiceStatus.DRAFT
        ).first()
        assert invoice is not None
        
        response = client.post(
            f"/api/v1/accounts-receivable/invoices/{invoice.id}/send",
            headers=auth_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "sent"
        assert data["date_sent"] is not None

class TestPaymentAPI:
    """Test cases for Payment API endpoints."""
    
    def test_record_payment(self, db: Session, test_customer: Customer, auth_headers: dict):
        """Test recording a payment."""
        # Get a sent or partially paid invoice
        invoice = db.query(models.Invoice).filter(
            models.Invoice.status.in_(["sent", "partially_paid"])
        ).first()
        assert invoice is not None
        
        payment_data = {
            "invoice_id": str(invoice.id),
            "customer_id": str(test_customer.id),
            "payment_date": str(date.today()),
            "amount": str(invoice.balance_due),
            "payment_method": "bank_transfer",
            "reference_number": "TEST123",
            "notes": "Test payment",
        }
        
        response = client.post(
            "/api/v1/accounts-receivable/payments/",
            json=payment_data,
            headers=auth_headers,
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        # Verify payment data
        assert "id" in data
        assert data["payment_number"].startswith("PAY-")
        assert data["amount"] == payment_data["amount"]
        assert data["status"] == "completed"
        
        # Verify invoice was updated
        invoice_response = client.get(
            f"/api/v1/accounts-receivable/invoices/{invoice.id}",
            headers=auth_headers,
        )
        invoice_data = invoice_response.json()
        assert invoice_data["status"] == "paid"
        assert invoice_data["balance_due"] == "0.00"
    
    def test_list_payments(self, auth_headers: dict):
        """Test listing payments."""
        response = client.get(
            "/api/v1/accounts-receivable/payments/",
            headers=auth_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

class TestCreditNoteAPI:
    """Test cases for Credit Note API endpoints."""
    
    def test_create_credit_note(self, db: Session, test_customer: Customer, test_gl_accounts: dict, auth_headers: dict):
        """Test creating a credit note."""
        # First, get an invoice to reference
        invoice = db.query(models.Invoice).first()
        assert invoice is not None
        
        credit_note_data = {
            "customer_id": str(test_customer.id),
            "reference_invoice_id": str(invoice.id),
            "issue_date": str(date.today()),
            "reason": "Test credit note",
            "credit_note_items": [
                {
                    "description": "Test Credit Item",
                    "quantity": 1,
                    "unit_price": "50.00",
                    "tax_rate": "8.25",
                    "gl_account_id": str(test_gl_accounts["revenue"].id),
                }
            ],
        }
        
        response = client.post(
            "/api/v1/accounts-receivable/credit-notes/",
            json=credit_note_data,
            headers=auth_headers,
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        # Verify response data
        assert "id" in data
        assert data["credit_note_number"].startswith("CN-")
        assert data["customer_id"] == str(test_customer.id)
        assert data["total_amount"] == "54.13"  # 50 + (50 * 8.25%)
        assert len(data["credit_note_items"]) == 1
    
    def test_apply_credit_note(self, db: Session, auth_headers: dict):
        """Test applying a credit note to an invoice."""
        # Get a credit note with remaining amount
        credit_note = db.query(models.CreditNote).filter(
            models.CreditNote.remaining_amount > 0
        ).first()
        
        if credit_note:
            # Get an invoice to apply the credit to
            invoice = db.query(models.Invoice).filter(
                models.Invoice.customer_id == credit_note.customer_id,
                models.Invoice.balance_due > 0,
            ).first()
            
            if invoice:
                apply_data = {
                    "invoice_id": str(invoice.id),
                    "amount": str(min(credit_note.remaining_amount, invoice.balance_due)),
                }
                
                response = client.post(
                    f"/api/v1/accounts-receivable/credit-notes/{credit_note.id}/apply",
                    json=apply_data,
                    headers=auth_headers,
                )
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                
                # Verify the credit note was applied
                assert data["remaining_amount"] < credit_note.remaining_amount
                
                # Verify the invoice was updated
                invoice_response = client.get(
                    f"/api/v1/accounts-receivable/invoices/{invoice.id}",
                    headers=auth_headers,
                )
                invoice_data = invoice_response.json()
                assert Decimal(invoice_data["balance_due"]) < invoice.balance_due

class TestReportsAPI:
    """Test cases for Reports API endpoints."""
    
    def test_accounts_aging_report(self, auth_headers: dict):
        """Test generating an accounts aging report."""
        response = client.get(
            "/api/v1/accounts-receivable/reports/accounts-aging",
            headers=auth_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify the report structure
        assert isinstance(data, list)
        if data:  # If there are results
            customer = data[0]
            assert "customer_id" in customer
            assert "customer_name" in customer
            assert "current" in customer
            assert "days_1_30" in customer
            assert "days_31_60" in customer
            assert "days_61_90" in customer
            assert "days_over_90" in customer
            assert "total" in customer
