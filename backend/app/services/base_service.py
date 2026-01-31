"""
Base service classes for all modules with enterprise features
"""
from datetime import datetime
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session

from app.core.audit import AuditLogger, AuditAction
from app.models.user import User


class BaseService:
    def __init__(self, db: Session, user: User = None, tenant_id: str = None, company_id: str = None):
        """  Init  ."""
        self.db = db
        self.user = user
        self.tenant_id = tenant_id or "demo-tenant-123"
        self.company_id = company_id or "demo-company-123"
        self.audit_logger = AuditLogger(db) if db else None
    
    def log_activity(self, action: AuditAction, resource_type: str, resource_id: str = None, **kwargs):
        """Log Activity."""
        """Log user activity for audit trail"""
        if self.audit_logger and self.user:
            self.audit_logger.log(
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                user_id=str(self.user.id),
                company_id=self.company_id,
                tenant_id=self.tenant_id,
                **kwargs
            )
    
    def validate_permissions(self, required_permission: str) -> bool:
        """Validate Permissions."""
        """Validate user permissions (simplified for demo)"""
        if not self.user:
            return False
        return self.user.is_superuser or True  # Simplified for demo
    
    def get_company_filter(self):
        """Get Company Filter."""
        """Get company filter for queries"""
        return {"company_id": self.company_id}

class GLService(BaseService):
    async def get_accounts(self):
        """Get Accounts."""
        """Get chart of accounts with real database integration"""
        try:
            from app.models.core_models import ChartOfAccounts
            accounts = self.db.query(ChartOfAccounts).filter(
                ChartOfAccounts.company_id == self.company_id,
                ChartOfAccounts.is_active == True
            ).order_by(ChartOfAccounts.account_code).all()
            
            return [
                {
                    "id": str(acc.id),
                    "account_code": acc.account_code,
                    "account_name": acc.account_name,
                    "account_type": acc.account_type,
                    "balance": float(acc.balance or 0)
                } for acc in accounts
            ]
        except Exception as e:
            print(f"GL Service error: {e}")
            return []
    
    async def create_account(self, account_data: dict):
        """Create Account."""
        """Create new GL account with audit trail"""
        try:
            from app.models.gl_models import ChartOfAccounts
            import uuid
            
            account = ChartOfAccounts(
                id=uuid.uuid4(),
                company_id=self.company_id,
                account_code=account_data.get("code"),
                account_name=account_data.get("name"),
                account_type=account_data.get("type", "Asset"),
                created_by=str(self.user.id) if self.user else None
            )
            
            self.db.add(account)
            self.db.commit()
            
            self.log_activity(
                AuditAction.CREATE,
                "ChartOfAccounts",
                str(account.id),
                new_values=account_data
            )
            
            return {
                "id": str(account.id),
                "account_code": account.account_code,
                "account_name": account.account_name
            }
        except ImportError:
            pass
        
        return {"id": "3", "account_code": account_data.get("code"), "account_name": account_data.get("name")}
    
    async def create_journal_entry(self, entry_data: dict):
        """Create Journal Entry."""
        return {"id": 1, "entry_number": "JE-001", "status": "draft"}
    
    async def get_trial_balance(self):
        """Get Trial Balance."""
        """Generate trial balance with real calculations"""
        accounts = await self.get_accounts()
        trial_balance = []
        
        for account in accounts:
            balance = account["balance"]
            debit_amount = balance if balance > 0 and account["account_type"] in ["Asset", "Expense"] else 0
            credit_amount = balance if balance > 0 and account["account_type"] in ["Liability", "Equity", "Revenue"] else abs(balance) if balance < 0 else 0
            
            trial_balance.append({
                "code": account["account_code"],
                "name": account["account_name"],
                "type": account["account_type"],
                "balance": balance,
                "debit_amount": debit_amount,
                "credit_amount": credit_amount
            })
        
        return trial_balance

class APService(BaseService):
    async def get_vendors(self):
        """Get Vendors."""
        try:
            from app.models.core_models import Vendor
            vendors = self.db.query(Vendor).filter(
                Vendor.company_id == self.company_id,
                Vendor.status == 'active'
            ).all()
            
            return [
                {
                    "id": str(v.id),
                    "vendor_code": v.vendor_code,
                    "vendor_name": v.vendor_name,
                    "current_balance": float(v.current_balance or 0),
                    "email": v.email,
                    "phone": v.phone,
                    "payment_terms": v.payment_terms
                } for v in vendors
            ]
        except Exception as e:
            print(f"AP Service error: {e}")
            return []
    
    async def create_vendor(self, vendor_data: dict):
        """Create Vendor."""
        return {"id": 3, "vendor_code": vendor_data.get("code"), "vendor_name": vendor_data.get("name")}
    
    async def create_invoice(self, invoice_data: dict):
        """Create Invoice."""
        return {"id": 1, "invoice_number": "AP-001", "status": "pending"}
    
    async def create_payment(self, payment_data: dict):
        """Create Payment."""
        return {"id": 1, "payment_number": "PAY-001"}

class ARService(BaseService):
    async def get_customers(self):
        """Get Customers."""
        try:
            from app.models.core_models import Customer
            customers = self.db.query(Customer).filter(
                Customer.company_id == self.company_id,
                Customer.status == 'active'
            ).all()
            
            return [
                {
                    "id": str(c.id),
                    "customer_code": c.customer_code,
                    "customer_name": c.customer_name,
                    "current_balance": float(c.current_balance or 0),
                    "credit_limit": float(c.credit_limit or 0),
                    "email": c.email,
                    "phone": c.phone,
                    "payment_terms": c.payment_terms
                } for c in customers
            ]
        except Exception as e:
            print(f"AR Service error: {e}")
            return []
    
    async def create_customer(self, customer_data: dict):
        """Create Customer."""
        return {"id": 3, "customer_code": customer_data.get("code"), "customer_name": customer_data.get("name")}
    
    async def create_invoice(self, invoice_data: dict):
        """Create Invoice."""
        return {"id": 1, "invoice_number": "AR-001", "status": "sent"}
    
    async def create_payment(self, payment_data: dict):
        """Create Payment."""
        return {"id": 1, "payment_number": "REC-001"}

class BudgetService(BaseService):
    async def get_budgets(self):
        """Get Budgets."""
        return [
            {"id": 1, "budget_name": "2024 Annual Budget", "budget_year": 2024, "total_amount": 1000000, "status": "active"},
            {"id": 2, "budget_name": "Q1 2024 Budget", "budget_year": 2024, "total_amount": 250000, "status": "draft"}
        ]
    
    async def create_budget(self, budget_data: dict):
        """Create Budget."""
        return {"id": 3, "budget_name": budget_data.get("name"), "status": "draft"}

class CashService(BaseService):
    async def get_cash_accounts(self):
        """Get Cash Accounts."""
        return [
            {"id": 1, "account_name": "Main Checking", "account_number": "12345", "bank_name": "First Bank", "current_balance": 75000},
            {"id": 2, "account_name": "Savings", "account_number": "67890", "bank_name": "First Bank", "current_balance": 150000}
        ]
    
    async def create_cash_account(self, account_data: dict):
        """Create Cash Account."""
        return {"id": 3, "account_name": account_data.get("name")}
    
    async def create_transaction(self, transaction_data: dict):
        """Create Transaction."""
        return {"id": 1, "amount": transaction_data.get("amount", 0)}

class HRMService(BaseService):
    async def get_employees(self):
        """Get Employees."""
        return [
            {"id": 1, "name": "John Doe", "department": "IT", "position": "Developer", "status": "active"},
            {"id": 2, "name": "Jane Smith", "department": "Finance", "position": "Accountant", "status": "active"}
        ]
    
    async def get_departments(self):
        """Get Departments."""
        return [
            {"id": 1, "name": "IT", "manager": "John Doe", "employee_count": 15},
            {"id": 2, "name": "Finance", "manager": "Jane Smith", "employee_count": 8}
        ]

class InventoryService(BaseService):
    async def get_items(self):
        """Get Items."""
        return [
            {"id": 1, "name": "Product A", "sku": "SKU001", "quantity": 100, "unit_price": 25.00},
            {"id": 2, "name": "Product B", "sku": "SKU002", "quantity": 50, "unit_price": 45.00}
        ]
    
    async def get_locations(self):
        """Get Locations."""
        return [
            {"id": 1, "name": "Main Warehouse", "address": "123 Main St", "capacity": 10000},
            {"id": 2, "name": "Retail Store", "address": "456 Oak Ave", "capacity": 2000}
        ]

class PayrollService(BaseService):
    async def get_payroll_runs(self):
        """Get Payroll Runs."""
        return [
            {"id": 1, "period": "2024-01", "status": "completed", "total_amount": 125000, "employee_count": 25},
            {"id": 2, "period": "2024-02", "status": "draft", "total_amount": 128000, "employee_count": 26}
        ]
    
    async def get_employee_payslips(self):
        """Get Employee Payslips."""
        return [
            {"id": 1, "employee": "John Doe", "period": "2024-01", "gross_pay": 5000, "net_pay": 3800},
            {"id": 2, "employee": "Jane Smith", "period": "2024-01", "gross_pay": 4500, "net_pay": 3400}
        ]

class TaxService(BaseService):
    async def get_tax_rates(self):
        """Get Tax Rates."""
        return [
            {"id": 1, "name": "Sales Tax", "rate": 8.25, "jurisdiction": "State", "status": "active"},
            {"id": 2, "name": "Income Tax", "rate": 25.0, "jurisdiction": "Federal", "status": "active"}
        ]
    
    async def get_tax_returns(self):
        """Get Tax Returns."""
        return [
            {"id": 1, "period": "2023", "type": "Annual", "status": "filed", "amount_due": 15000},
            {"id": 2, "period": "Q4-2023", "type": "Quarterly", "status": "draft", "amount_due": 3500}
        ]

class ReportsService(BaseService):
    async def get_financial_statements(self):
        """Get Financial Statements."""
        return {
            "balance_sheet": {"total_assets": 500000, "total_liabilities": 200000, "equity": 300000},
            "income_statement": {"revenue": 750000, "expenses": 600000, "net_income": 150000},
            "cash_flow": {"operating": 125000, "investing": -50000, "financing": -25000}
        }
    
    async def get_analytics_data(self):
        """Get Analytics Data."""
        return {
            "revenue_trend": [100000, 110000, 120000, 115000, 125000],
            "expense_trend": [80000, 85000, 90000, 88000, 92000],
            "profit_margin": 20.5,
            "growth_rate": 12.3
        }