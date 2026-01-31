"""
Unified Settings Service for all modules
"""
from sqlalchemy.orm import Session
from uuid import UUID

from app.models import Company, TaxRate, ChartOfAccounts
from app.services.base import BaseService


class UnifiedSettingsService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db, Company)
    
    def get_company_settings(self, company_id: UUID) -> dict:
        company = self.db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return {}
        
        # Get default tax rate
        default_tax = self.db.query(TaxRate).filter(
            TaxRate.company_id == company_id,
            TaxRate.is_active == True
        ).first()
        
        # Get default accounts
        default_accounts = self.db.query(ChartOfAccounts).filter(
            ChartOfAccounts.company_id == company_id,
            ChartOfAccounts.is_system_account == True
        ).all()
        
        return {
            "company": {
                "id": str(company.id),
                "name": company.company_name,
                "currency": company.base_currency,
                "fiscal_year_end": company.fiscal_year_end
            },
            "tax_settings": {
                "default_tax_rate": float(default_tax.rate_percentage) if default_tax else 0,
                "tax_code": default_tax.tax_code if default_tax else None
            },
            "account_settings": {
                account.account_type: {
                    "code": account.account_code,
                    "name": account.account_name,
                    "id": str(account.id)
                }
                for account in default_accounts
            }
        }
    
    def update_company_settings(self, company_id: UUID, settings: dict) -> Company:
        company = self.db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise ValueError("Company not found")
        
        if "company" in settings:
            company_data = settings["company"]
            company.company_name = company_data.get("name", company.company_name)
            company.base_currency = company_data.get("currency", company.base_currency)
            company.fiscal_year_end = company_data.get("fiscal_year_end", company.fiscal_year_end)
        
        return company