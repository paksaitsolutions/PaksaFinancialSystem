import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import Budget, BudgetLine, BudgetAllocation
from app.services.budget_integration import BudgetIntegrationService
from app.services.gl import GLService
from app.services.ap import APService
from app.services.ar import ARService
from app.services.procurement import ProcurementService
from app.services.payroll import PayrollService

@pytest.fixture
def budget_integration_service(db: Session,
                              budget_service,
                              gl_service,
                              ap_service,
                              ar_service,
                              procurement_service,
                              payroll_service):
    return BudgetIntegrationService(
        db=db,
        budget_service=budget_service,
        gl_service=gl_service,
        ap_service=ap_service,
        ar_service=ar_service,
        procurement_service=procurement_service,
        payroll_service=payroll_service
    )

@pytest.fixture
def sample_budget(db: Session, budget_service):
    budget = Budget(
        name="Test Budget",
        budget_type="operational",
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=365),
        status="approved"
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    
    line = BudgetLine(
        budget_id=budget.id,
        account_id=1,
        amount=10000.00,
        description="Test Line"
    )
    db.add(line)
    db.commit()
    
    return budget

@pytest.fixture
def sample_gl_entry(gl_service):
    return gl_service.create_entry({
        "account_id": 1,
        "amount": 1000.00,
        "description": "Test GL Entry"
    })

@pytest.fixture
def sample_ap_invoice(ap_service):
    return ap_service.create_invoice({
        "vendor_id": 1,
        "account_id": 1,
        "amount": 1000.00,
        "description": "Test AP Invoice"
    })

@pytest.fixture
def sample_ar_invoice(ar_service):
    return ar_service.create_invoice({
        "customer_id": 1,
        "account_id": 1,
        "amount": 1000.00,
        "description": "Test AR Invoice"
    })

@pytest.fixture
def sample_purchase_order(procurement_service):
    return procurement_service.create_purchase_order({
        "vendor_id": 1,
        "account_id": 1,
        "total_amount": 1000.00,
        "description": "Test PO"
    })

@pytest.fixture
def sample_payroll_entry(payroll_service):
    return payroll_service.create_payroll({
        "employee_id": 1,
        "account_id": 1,
        "net_pay": 1000.00,
        "description": "Test Payroll"
    })

def test_check_budget_availability(budget_integration_service, sample_budget):
    # Test with available budget
    assert budget_integration_service.check_budget_availability(
        account_id=1,
        amount=500.00,
        department_id=1,
        project_id=1
    )
    
    # Test with insufficient budget
    assert not budget_integration_service.check_budget_availability(
        account_id=1,
        amount=15000.00,
        department_id=1,
        project_id=1
    )

def test_allocate_budget(budget_integration_service, sample_budget):
    allocation = budget_integration_service.allocate_budget(
        budget_id=sample_budget.id,
        amount=500.00,
        account_id=1,
        department_id=1,
        project_id=1,
        description="Test Allocation"
    )
    assert allocation.amount == 500.00
    assert allocation.budget_id == sample_budget.id

def test_gl_entry_budget_allocation(budget_integration_service,
                                   sample_budget,
                                   sample_gl_entry):
    gl_entry = budget_integration_service.update_gl_entry_budget_allocation(
        gl_entry_id=sample_gl_entry.id,
        budget_id=sample_budget.id,
        amount=500.00,
        department_id=1,
        project_id=1
    )
    assert gl_entry.budget_allocation_id is not None

def test_ap_invoice_budget_allocation(budget_integration_service,
                                    sample_budget,
                                    sample_ap_invoice):
    invoice = budget_integration_service.update_ap_invoice_budget_allocation(
        invoice_id=sample_ap_invoice.id,
        budget_id=sample_budget.id,
        amount=500.00,
        department_id=1,
        project_id=1
    )
    assert invoice.budget_allocation_id is not None

def test_ar_invoice_budget_allocation(budget_integration_service,
                                    sample_budget,
                                    sample_ar_invoice):
    invoice = budget_integration_service.update_ar_invoice_budget_allocation(
        invoice_id=sample_ar_invoice.id,
        budget_id=sample_budget.id,
        amount=500.00,
        department_id=1,
        project_id=1
    )
    assert invoice.budget_allocation_id is not None

def test_purchase_order_budget_allocation(budget_integration_service,
                                         sample_budget,
                                         sample_purchase_order):
    po = budget_integration_service.update_purchase_order_budget_allocation(
        po_id=sample_purchase_order.id,
        budget_id=sample_budget.id,
        amount=500.00,
        department_id=1,
        project_id=1
    )
    assert po.budget_allocation_id is not None

def test_payroll_budget_allocation(budget_integration_service,
                                  sample_budget,
                                  sample_payroll_entry):
    payroll = budget_integration_service.update_payroll_entry_budget_allocation(
        payroll_id=sample_payroll_entry.id,
        budget_id=sample_budget.id,
        amount=500.00,
        department_id=1
    )
    assert payroll.budget_allocation_id is not None

def test_budget_spending_report(budget_integration_service,
                              sample_budget):
    report = budget_integration_service.get_budget_spending_report(
        account_id=1,
        department_id=1,
        project_id=1
    )
    assert report.total_budget >= 0
    assert report.total_spent >= 0
    assert report.remaining_budget >= 0
    assert 0 <= report.percentage_spent <= 100
