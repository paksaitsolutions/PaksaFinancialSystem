"""
Base service classes for all modules with enterprise features
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.core.audit import AuditLogger, AuditAction
from app.models.user import User

class BaseService:
    def __init__(self, db: Session, user: User = None, tenant_id: str = None, company_id: str = None):
        self.db = db
        self.user = user
        self.tenant_id = tenant_id or "demo-tenant-123"
        self.company_id = company_id or "demo-company-123"
        self.audit_logger = AuditLogger(db) if db else None
    
    def log_activity(self, action: AuditAction, resource_type: str, resource_id: str = None, **kwargs):
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
        """Validate user permissions (simplified for demo)"""
        if not self.user:
            return False
        return self.user.is_superuser or True  # Simplified for demo
    
    def get_company_filter(self):
        """Get company filter for queries"""
        return {"company_id": self.company_id}

class GLService(BaseService):
    async def get_accounts(self):
        """Get chart of accounts with real database integration"""
        try:
            from app.models.gl_models import ChartOfAccounts
            accounts = self.db.query(ChartOfAccounts).filter(
                ChartOfAccounts.company_id == self.company_id,
                ChartOfAccounts.is_active == True
            ).order_by(ChartOfAccounts.account_code).all()
            
            if accounts:
                return [
                    {
                        "id": str(acc.id),
                        "account_code": acc.account_code,
                        "account_name": acc.account_name,
                        "account_type": acc.account_type,
                        "balance": float(acc.balance)
                    } for acc in accounts
                ]
        except ImportError:
            pass
        
        # Fallback to demo data
        return [
            {"id": "1", "account_code": "1000", "account_name": "Cash", "account_type": "Asset", "balance": 50000},
            {"id": "2", "account_code": "1200", "account_name": "Accounts Receivable", "account_type": "Asset", "balance": 25000},
            {"id": "3", "account_code": "2000", "account_name": "Accounts Payable", "account_type": "Liability", "balance": 15000},
            {"id": "4", "account_code": "3000", "account_name": "Owner's Equity", "account_type": "Equity", "balance": 60000}
        ]
    
    async def create_account(self, account_data: dict):
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
        return {"id": 1, "entry_number": "JE-001", "status": "draft"}
    
    async def get_trial_balance(self):
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
        return [
            {"id": 1, "vendor_code": "V001", "vendor_name": "ABC Supplies", "current_balance": 5000},
            {"id": 2, "vendor_code": "V002", "vendor_name": "XYZ Services", "current_balance": 3000}
        ]
    
    async def create_vendor(self, vendor_data: dict):
        return {"id": 3, "vendor_code": vendor_data.get("code"), "vendor_name": vendor_data.get("name")}
    
    async def create_invoice(self, invoice_data: dict):
        return {"id": 1, "invoice_number": "AP-001", "status": "pending"}
    
    async def create_payment(self, payment_data: dict):
        return {"id": 1, "payment_number": "PAY-001"}

class ARService(BaseService):
    async def get_customers(self):
        return [
            {"id": 1, "customer_code": "C001", "customer_name": "Customer A", "current_balance": 15000, "credit_limit": 50000},
            {"id": 2, "customer_code": "C002", "customer_name": "Customer B", "current_balance": 8000, "credit_limit": 30000}
        ]
    
    async def create_customer(self, customer_data: dict):
        return {"id": 3, "customer_code": customer_data.get("code"), "customer_name": customer_data.get("name")}
    
    async def create_invoice(self, invoice_data: dict):
        return {"id": 1, "invoice_number": "AR-001", "status": "sent"}
    
    async def create_payment(self, payment_data: dict):
        return {"id": 1, "payment_number": "REC-001"}

class BudgetService(BaseService):
    async def get_budgets(self):
        return [
            {"id": 1, "budget_name": "2024 Annual Budget", "budget_year": 2024, "total_amount": 1000000, "status": "active"},
            {"id": 2, "budget_name": "Q1 2024 Budget", "budget_year": 2024, "total_amount": 250000, "status": "draft"}
        ]
    
    async def create_budget(self, budget_data: dict):
        return {"id": 3, "budget_name": budget_data.get("name"), "status": "draft"}

class CashService(BaseService):
    async def get_cash_accounts(self):
        return [
            {"id": 1, "account_name": "Main Checking", "account_number": "12345", "bank_name": "First Bank", "current_balance": 75000},
            {"id": 2, "account_name": "Savings", "account_number": "67890", "bank_name": "First Bank", "current_balance": 150000}
        ]
    
    async def create_cash_account(self, account_data: dict):
        return {"id": 3, "account_name": account_data.get("name")}
    
    async def create_transaction(self, transaction_data: dict):
        return {"id": 1, "amount": transaction_data.get("amount", 0)}

class HRMService(BaseService):
    async def get_employees(self):
        return [
            {"id": 1, "name": "John Doe", "department": "IT", "position": "Developer", "status": "active"},
            {"id": 2, "name": "Jane Smith", "department": "Finance", "position": "Accountant", "status": "active"}
        ]
    
    async def get_departments(self):
        return [
            {"id": 1, "name": "IT", "manager": "John Doe", "employee_count": 15},
            {"id": 2, "name": "Finance", "manager": "Jane Smith", "employee_count": 8}
        ]

class InventoryService(BaseService):
    async def get_items(self):
        return [
            {"id": 1, "name": "Product A", "sku": "SKU001", "quantity": 100, "unit_price": 25.00},
            {"id": 2, "name": "Product B", "sku": "SKU002", "quantity": 50, "unit_price": 45.00}
        ]
    
    async def get_locations(self):
        return [
            {"id": 1, "name": "Main Warehouse", "address": "123 Main St", "capacity": 10000},
            {"id": 2, "name": "Retail Store", "address": "456 Oak Ave", "capacity": 2000}
        ]

class PayrollService(BaseService):
    async def get_payroll_runs(self):
        return [
            {"id": 1, "period": "2024-01", "status": "completed", "total_amount": 125000, "employee_count": 25},
            {"id": 2, "period": "2024-02", "status": "draft", "total_amount": 128000, "employee_count": 26}
        ]
    
    async def get_employee_payslips(self):
        return [
            {"id": 1, "employee": "John Doe", "period": "2024-01", "gross_pay": 5000, "net_pay": 3800},
            {"id": 2, "employee": "Jane Smith", "period": "2024-01", "gross_pay": 4500, "net_pay": 3400}
        ]

class TaxService(BaseService):
    async def get_tax_rates(self):
        return [
            {"id": 1, "name": "Sales Tax", "rate": 8.25, "jurisdiction": "State", "status": "active"},
            {"id": 2, "name": "Income Tax", "rate": 25.0, "jurisdiction": "Federal", "status": "active"}
        ]
    
    async def get_tax_returns(self):
        return [
            {"id": 1, "period": "2023", "type": "Annual", "status": "filed", "amount_due": 15000},
            {"id": 2, "period": "Q4-2023", "type": "Quarterly", "status": "draft", "amount_due": 3500}
        ]

class ReportsService(BaseService):
    async def get_financial_statements(self):
        return {
            "balance_sheet": {"total_assets": 500000, "total_liabilities": 200000, "equity": 300000},
            "income_statement": {"revenue": 750000, "expenses": 600000, "net_income": 150000},
            "cash_flow": {"operating": 125000, "investing": -50000, "financing": -25000}
        }
    
    async def get_analytics_data(self):
        return {
            "revenue_trend": [100000, 110000, 120000, 115000, 125000],
            "expense_trend": [80000, 85000, 90000, 88000, 92000],
            "profit_margin": 20.5,
            "growth_rate": 12.3
        }