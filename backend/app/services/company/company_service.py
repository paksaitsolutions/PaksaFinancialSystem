"""
Company management service.
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session
from uuid import UUID
import secrets

from app.models.company import Company, CompanyUser, CompanySettings, CompanyStatus, SubscriptionTier





class CompanyService:
    """Service for managing company profiles and multi-tenant operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def register_company(self, company_data: Dict[str, Any], admin_user_id: UUID) -> Company:
        company_code = self._generate_company_code(company_data['company_name'])
        
        company = Company(
            company_name=company_data['company_name'],
            company_code=company_code,
            email=company_data['email'],
            phone=company_data.get('phone'),
            website=company_data.get('website'),
            industry=company_data.get('industry'),
            business_type=company_data.get('business_type'),
            tax_id=company_data.get('tax_id'),
            registration_number=company_data.get('registration_number'),
            address_line1=company_data.get('address_line1'),
            address_line2=company_data.get('address_line2'),
            city=company_data.get('city'),
            state=company_data.get('state'),
            postal_code=company_data.get('postal_code'),
            country=company_data.get('country'),
            default_currency=company_data.get('default_currency', 'USD'),
            default_language=company_data.get('default_language', 'en-US'),
            timezone=company_data.get('timezone', 'UTC'),
            fiscal_year_start=company_data.get('fiscal_year_start', '01-01'),
            subscription_tier=company_data.get('subscription_tier', SubscriptionTier.BASIC),
            status=CompanyStatus.TRIAL,
            trial_ends_at=datetime.utcnow() + timedelta(days=30),
            database_schema=f"company_{company_code.lower()}",
            enabled_modules=self._get_default_modules(),
            numbering_formats=self._get_default_numbering_formats(),
            created_by=admin_user_id,
            updated_by=admin_user_id
        )
        
        self.db.add(company)
        self.db.flush()
        
        self.add_user_to_company(company.id, admin_user_id, role="admin", is_admin=True)
        self._create_default_settings(company.id)
        
        self.db.commit()
        self.db.refresh(company)
        
        return company
    
    def update_company(self, company_id: UUID, company_data: Dict[str, Any], updated_by: UUID) -> Company:
        company = self.get_company(company_id)
        if not company:
            raise ValueError(f"Company {company_id} not found")
        
        for field, value in company_data.items():
            if hasattr(company, field) and value is not None:
                setattr(company, field, value)
        
        company.updated_by = updated_by
        company.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(company)
        
        return company
    
    def add_user_to_company(
        self, 
        company_id: UUID, 
        user_id: UUID, 
        role: str = "user", 
        is_admin: bool = False,
        permissions: Optional[Dict] = None
    ) -> CompanyUser:
        """Add User To Company."""
        """Add a user to a company."""
        existing = self.db.query(CompanyUser).filter(
            and_(
                CompanyUser.company_id == company_id,
                CompanyUser.user_id == user_id
            )
        ).first()
        
        if existing:
            raise ValueError("User is already associated with this company")
        
        company_user = CompanyUser(
            company_id=company_id,
            user_id=user_id,
            role=role,
            is_admin=is_admin,
            permissions=permissions,
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(company_user)
        self.db.commit()
        self.db.refresh(company_user)
        
        return company_user
    
    def get_company(self, company_id: UUID) -> Optional[Company]:
        return self.db.query(Company).filter(Company.id == company_id).first()
    
    def get_company_by_code(self, company_code: str) -> Optional[Company]:
        return self.db.query(Company).filter(Company.company_code == company_code).first()
    
    def list_companies(self, status: Optional[str] = None, limit: int = 100) -> List[Company]:
        query = self.db.query(Company)
        
        if status:
            query = query.filter(Company.status == status)
        
        return query.order_by(desc(Company.created_at)).limit(limit).all()
    
    def get_company_users(self, company_id: UUID, active_only: bool = True) -> List[CompanyUser]:
        query = self.db.query(CompanyUser).filter(CompanyUser.company_id == company_id)
        
        if active_only:
            query = query.filter(CompanyUser.is_active == True)
        
        return query.all()
    
    def get_user_companies(self, user_id: UUID, active_only: bool = True) -> List[Company]:
        query = self.db.query(Company).join(CompanyUser).filter(
            CompanyUser.user_id == user_id
        )
        
        if active_only:
            query = query.filter(
                and_(
                    Company.status == CompanyStatus.ACTIVE,
                    CompanyUser.is_active == True
                )
            )
        
        return query.all()
    
    def _generate_company_code(self, company_name: str) -> str:
        base_code = ''.join(c.upper() for c in company_name if c.isalnum())[:6]
        suffix = secrets.token_hex(2).upper()
        company_code = f"{base_code}{suffix}"
        
        while self.get_company_by_code(company_code):
            suffix = secrets.token_hex(2).upper()
            company_code = f"{base_code}{suffix}"
        
        return company_code
    
    def _get_default_modules(self) -> Dict[str, bool]:
        return {
            "general_ledger": True,
            "accounts_payable": True,
            "accounts_receivable": True,
            "payroll": False,
            "inventory": False,
            "fixed_assets": False,
            "budgeting": False,
            "reporting": True,
            "analytics": False
        }
    
    def _get_default_numbering_formats(self) -> Dict[str, str]:
        return {
            "invoice": "INV-{YYYY}-{####}",
            "purchase_order": "PO-{YYYY}-{####}",
            "journal_entry": "JE-{YYYY}-{####}",
            "payment": "PAY-{YYYY}-{####}",
            "receipt": "REC-{YYYY}-{####}",
            "quote": "QUO-{YYYY}-{####}"
        }
    
    def _create_default_settings(self, company_id: UUID):
        settings = CompanySettings(
            company_id=company_id,
            chart_of_accounts_template="standard",
            approval_workflows={
                "purchase_orders": {"enabled": False, "amount_threshold": 1000},
                "invoices": {"enabled": False, "amount_threshold": 5000},
                "journal_entries": {"enabled": False}
            },
            notification_settings={
                "email_notifications": True,
                "invoice_reminders": True,
                "payment_confirmations": True
            },
            security_settings={
                "require_2fa": False,
                "session_timeout": 30,
                "password_expiry_days": 90
            }
        )
        
        self.db.add(settings)