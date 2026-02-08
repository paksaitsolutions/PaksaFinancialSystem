"""
Test configuration and shared fixtures for all module tests.
"""
import os
from datetime import date
from uuid import UUID
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_database.db")
os.environ.setdefault("DEMO_MODE", "true")

from app.main import app
from app.core.database import get_db, engine
from app.models.base import Base

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override the get_db dependency for testing"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


def _seed_data(db):
    from app.models.core_models import (
        Company,
        Currency,
        ExchangeRate,
        ChartOfAccounts,
        Vendor,
        Customer,
        Employee,
        PayrollRun,
        BankAccount,
    )

    company_id = UUID("12345678-1234-5678-9012-123456789012")

    if not db.query(Company).first():
        company = Company(
            id=company_id,
            company_code="DEMO",
            company_name="Paksa Demo Company",
            legal_name="Paksa Demo Company LLC",
            base_currency="USD",
        )
        db.add(company)

    if not db.query(Currency).filter(Currency.currency_code == "USD").first():
        db.add(
            Currency(
                currency_code="USD",
                currency_name="US Dollar",
                symbol="$",
                decimal_places=2,
            )
        )

    if not db.query(ExchangeRate).first():
        db.add(
            ExchangeRate(
                from_currency="USD",
                to_currency="USD",
                rate=1.0,
                rate_date=date.today(),
            )
        )

    if not db.query(ChartOfAccounts).first():
        db.add(
            ChartOfAccounts(
                company_id=company_id,
                account_code="1000",
                account_name="Cash",
                account_type="Asset",
                balance=10000,
            )
        )

    if not db.query(BankAccount).first():
        db.add(
            BankAccount(
                company_id=company_id,
                account_name="Operating Cash",
                account_number="000123456",
                bank_name="Demo Bank",
                current_balance=25000,
            )
        )

    if not db.query(Vendor).first():
        db.add(
            Vendor(
                company_id=company_id,
                vendor_code="VEND-0001",
                vendor_name="Seed Vendor",
                email="vendor@seed.local",
            )
        )

    if not db.query(Customer).first():
        db.add(
            Customer(
                company_id=company_id,
                customer_code="CUST-0001",
                customer_name="Seed Customer",
                email="customer@seed.local",
            )
        )

    if not db.query(Employee).first():
        db.add(
            Employee(
                company_id=company_id,
                employee_code="EMP-0001",
                first_name="Seed",
                last_name="Employee",
                email="employee@seed.local",
                hire_date=date.today(),
                department="Finance",
                position="Accountant",
                salary=65000,
                status="active",
            )
        )

    if not db.query(PayrollRun).first():
        db.add(
            PayrollRun(
                company_id=company_id,
                run_number="PR-0001",
                pay_period="2024-12",
                pay_period_start=date(2024, 12, 1),
                pay_period_end=date(2024, 12, 31),
                pay_date=date(2025, 1, 5),
                status="draft",
                employee_count=1,
            )
        )

    db.commit()


@pytest.fixture(scope="session", autouse=True)
def seeded_db():
    """Seed the test database once per session."""
    from app.models.core_models import (
        APInvoice,
        APPayment,
        ARInvoice,
        ARPayment,
        AuditEvent,
        BankAccount,
        BankFeedConnection,
        CashConcentrationRule,
        ChartOfAccounts,
        Company,
        CompensationAction,
        Currency,
        Customer,
        Department,
        Employee,
        ExchangeRate,
        IdempotencyKey,
        InvestmentSweepConfig,
        JournalEntry,
        JournalEntryLine,
        PayrollEntry,
        PayrollRun,
        RefreshToken,
        SalesTaxNexus,
        TaxAutomationRule,
        TaxEFilingIntegration,
        TaxPaymentSchedule,
        Vendor,
        VendorPaymentInstruction,
        VendorPortalAccess,
        ZeroBalanceAccountConfig,
    )
    from app.models.user import User

    tables = [
        User.__table__,
        Company.__table__,
        Currency.__table__,
        ExchangeRate.__table__,
        ChartOfAccounts.__table__,
        JournalEntry.__table__,
        JournalEntryLine.__table__,
        Vendor.__table__,
        VendorPortalAccess.__table__,
        VendorPaymentInstruction.__table__,
        Customer.__table__,
        APInvoice.__table__,
        APPayment.__table__,
        ARInvoice.__table__,
        ARPayment.__table__,
        Department.__table__,
        Employee.__table__,
        PayrollRun.__table__,
        PayrollEntry.__table__,
        BankAccount.__table__,
        BankFeedConnection.__table__,
        CashConcentrationRule.__table__,
        ZeroBalanceAccountConfig.__table__,
        InvestmentSweepConfig.__table__,
        SalesTaxNexus.__table__,
        TaxAutomationRule.__table__,
        TaxEFilingIntegration.__table__,
        TaxPaymentSchedule.__table__,
        IdempotencyKey.__table__,
        RefreshToken.__table__,
        AuditEvent.__table__,
        CompensationAction.__table__,
    ]

    Base.metadata.create_all(bind=engine, tables=tables)
    db = TestingSessionLocal()
    try:
        _seed_data(db)
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=engine, tables=tables)


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def test_db():
    """Test database fixture"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def mock_user():
    """Mock user fixture"""
    user = Mock()
    user.id = 1
    user.email = "test@example.com"
    user.full_name = "Test User"
    user.is_active = True
    return user

# Common test data
TEST_COMPANY_ID = "550e8400-e29b-41d4-a716-446655440000"
TEST_USER_ID = 1

# Response validation helpers
def assert_success_response(response, expected_status=200):
    """Assert that response follows standardized success format"""
    assert response.status_code == expected_status
    data = response.json()
    assert data["status"] == "success"
    assert "message" in data
    return data

def assert_paginated_response(response, expected_status=200):
    """Assert that response follows standardized paginated format"""
    data = assert_success_response(response, expected_status)
    assert "data" in data
    assert "pagination" in data
    pagination = data["pagination"]
    assert "total" in pagination
    assert "page" in pagination
    assert "page_size" in pagination
    assert "pages" in pagination
    assert "has_next" in pagination
    assert "has_prev" in pagination
    return data

def assert_error_response(response, expected_status=400):
    """Assert that response follows standardized error format"""
    assert response.status_code == expected_status
    data = response.json()
    assert data["status"] == "error"
    assert "message" in data
    return data
