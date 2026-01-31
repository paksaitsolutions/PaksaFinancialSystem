from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from sqlalchemy.orm import Session
import logging

from app.models.company_settings import CompanySettings
from app.models.tenant_company import TenantCompany, CompanyAdmin, CompanyModule
from app.models.user import User
from app.schemas.tenant_company import TenantCompanyCreate, TenantCompanyUpdate



logger = logging.getLogger(__name__)

class TenantService:
    def __init__(self, db: Session):
        """  Init  ."""
        self.db = db
    
    def get_company_by_id(self, company_id: int) -> Optional[TenantCompany]:
        """Get Company By Id."""
        """Get company by ID"""
        return self.db.query(TenantCompany).filter(TenantCompany.id == company_id).first()
    
    def get_company_by_code(self, code: str) -> Optional[TenantCompany]:
        """Get Company By Code."""
        """Get company by code"""
        return self.db.query(TenantCompany).filter(TenantCompany.code == code).first()
    
    def get_company_by_subdomain(self, subdomain: str) -> Optional[TenantCompany]:
        """Get Company By Subdomain."""
        """Get company by subdomain"""
        return self.db.query(TenantCompany).filter(TenantCompany.subdomain == subdomain).first()
    
    def get_user_companies(self, user_id: int) -> List[TenantCompany]:
        """Get User Companies."""
        """Get all companies a user has access to"""
        return self.db.query(TenantCompany).join(CompanyAdmin).filter(
            CompanyAdmin.user_id == user_id,
            TenantCompany.is_active == True
        ).all()
    
    def check_user_company_access(self, user_id: int, company_id: int) -> bool:
        """Check User Company Access."""
        """Check if user has access to a company"""
        access = self.db.query(CompanyAdmin).filter(
            CompanyAdmin.user_id == user_id,
            CompanyAdmin.company_id == company_id
        ).first()
        return access is not None
    
    def get_company_admin_role(self, user_id: int, company_id: int) -> Optional[str]:
        """Get Company Admin Role."""
        """Get user's role in a company"""
        admin = self.db.query(CompanyAdmin).filter(
            CompanyAdmin.user_id == user_id,
            CompanyAdmin.company_id == company_id
        ).first()
        return admin.role if admin else None
    
    def is_company_owner(self, user_id: int, company_id: int) -> bool:
        """Is Company Owner."""
        """Check if user is the owner of a company"""
        admin = self.db.query(CompanyAdmin).filter(
            CompanyAdmin.user_id == user_id,
            CompanyAdmin.company_id == company_id,
            CompanyAdmin.role == 'owner'
        ).first()
        return admin is not None
    
    def get_company_modules(self, company_id: int) -> List[CompanyModule]:
        """Get Company Modules."""
        """Get all enabled modules for a company"""
        return self.db.query(CompanyModule).filter(
            CompanyModule.company_id == company_id,
            CompanyModule.is_enabled == True
        ).all()
    
    def is_module_enabled(self, company_id: int, module_name: str) -> bool:
        """Is Module Enabled."""
        """Check if a module is enabled for a company"""
        module = self.db.query(CompanyModule).filter(
            CompanyModule.company_id == company_id,
            CompanyModule.module_name == module_name,
            CompanyModule.is_enabled == True
        ).first()
        return module is not None
    
    def get_company_settings(self, company_id: int) -> Optional[CompanySettings]:
        """Get Company Settings."""
        """Get company settings"""
        return self.db.query(CompanySettings).filter(
            CompanySettings.company_id == company_id
        ).first()
    
    def update_company_branding(self, company_id: int, branding_data: Dict[str, Any]) -> bool:
        """Update Company Branding."""
        """Update company branding settings"""
        try:
            company = self.get_company_by_id(company_id)
            if not company:
                return False
            
            if 'primary_color' in branding_data:
                company.primary_color = branding_data['primary_color']
            if 'secondary_color' in branding_data:
                company.secondary_color = branding_data['secondary_color']
            if 'logo_url' in branding_data:
                company.logo_url = branding_data['logo_url']
            
            company.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating company branding: {str(e)}")
            self.db.rollback()
            return False
    
    def check_company_limits(self, company_id: int) -> Dict[str, Any]:
        """Check Company Limits."""
        """Check company usage against limits"""
        company = self.get_company_by_id(company_id)
        if not company:
            return {}
        
        # Check user limit
        current_users = self.db.query(User).filter(
            User.company_id == company_id,
            User.is_active == True
        ).count()
        
        
        return {
            'users': {
                'current': current_users,
                'limit': company.max_users,
                'percentage': (current_users / company.max_users * 100) if company.max_users > 0 else 0,
                'exceeded': current_users >= company.max_users
            },
            'storage': {
                'limit_gb': company.storage_limit_gb,
                'percentage': 0,
                'exceeded': False
            }
        }
    
    def can_add_user(self, company_id: int) -> bool:
        """Can Add User."""
        """Check if company can add more users"""
        limits = self.check_company_limits(company_id)
        return not limits.get('users', {}).get('exceeded', True)
    
    def get_company_subscription_status(self, company_id: int) -> Dict[str, Any]:
        """Get Company Subscription Status."""
        """Get company subscription status"""
        company = self.get_company_by_id(company_id)
        if not company:
            return {}
        
        now = datetime.utcnow()
        
        # Check trial status
        if company.status == 'Trial' and company.trial_ends_at:
            days_remaining = (company.trial_ends_at - now).days
            return {
                'type': 'trial',
                'status': 'active' if days_remaining > 0 else 'expired',
                'days_remaining': max(0, days_remaining),
                'expires_at': company.trial_ends_at
            }
        
        # Check subscription status
        if company.subscription_ends_at:
            days_remaining = (company.subscription_ends_at - now).days
            return {
                'type': 'subscription',
                'status': 'active' if days_remaining > 0 else 'expired',
                'days_remaining': max(0, days_remaining),
                'expires_at': company.subscription_ends_at,
                'plan': company.plan
            }
        
        return {
            'type': 'active',
            'status': 'active',
            'plan': company.plan
        }
    
    def extend_trial(self, company_id: int, days: int) -> bool:
        """Extend Trial."""
        """Extend company trial period"""
        try:
            company = self.get_company_by_id(company_id)
            if not company:
                return False
            
            if company.trial_ends_at:
                company.trial_ends_at += timedelta(days=days)
            else:
                company.trial_ends_at = datetime.utcnow() + timedelta(days=days)
            
            company.status = 'Trial'
            company.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Error extending trial for company {company_id}: {str(e)}")
            self.db.rollback()
            return False
    
    def suspend_company(self, company_id: int, reason: str = None) -> bool:
        """Suspend Company."""
        """Suspend a company"""
        try:
            company = self.get_company_by_id(company_id)
            if not company:
                return False
            
            company.status = 'Suspended'
            company.is_active = False
            company.updated_at = datetime.utcnow()
            
            # Deactivate all users
            self.db.query(User).filter(User.company_id == company_id).update(
                {User.is_active: False}
            )
            
            self.db.commit()
            logger.info(f"Company {company.name} suspended. Reason: {reason}")
            return True
        except Exception as e:
            logger.error(f"Error suspending company {company_id}: {str(e)}")
            self.db.rollback()
            return False
    
    def reactivate_company(self, company_id: int) -> bool:
        """Reactivate Company."""
        """Reactivate a suspended company"""
        try:
            company = self.get_company_by_id(company_id)
            if not company:
                return False
            
            company.status = 'Active'
            company.is_active = True
            company.updated_at = datetime.utcnow()
            
            # Reactivate all users
            self.db.query(User).filter(User.company_id == company_id).update(
                {User.is_active: True}
            )
            
            self.db.commit()
            logger.info(f"Company {company.name} reactivated")
            return True
        except Exception as e:
            logger.error(f"Error reactivating company {company_id}: {str(e)}")
            self.db.rollback()
            return False
    
    def get_company_analytics(self, company_id: int) -> Dict[str, Any]:
        """Get Company Analytics."""
        """Get company analytics data"""
        company = self.get_company_by_id(company_id)
        if not company:
            return {}
        
        # Get user statistics
        total_users = self.db.query(User).filter(User.company_id == company_id).count()
        active_users = self.db.query(User).filter(
            User.company_id == company_id,
            User.is_active == True
        ).count()
        
        # Get module usage
        enabled_modules = self.db.query(CompanyModule).filter(
            CompanyModule.company_id == company_id,
            CompanyModule.is_enabled == True
        ).count()
        
        
        return {
            'users': {
                'total': total_users,
                'active': active_users,
                'inactive': total_users - active_users
            },
            'modules': {
                'enabled': enabled_modules
            },
            'subscription': self.get_company_subscription_status(company_id),
            'limits': self.check_company_limits(company_id)
        }
    
    def validate_company_access(self, user: User, company_id: int) -> bool:
        """Validate Company Access."""
        """Validate if user can access company resources"""
        # Super admin can access any company
        if user.is_superuser:
            return True
        
        # Check if user belongs to the company or has admin access
        if user.company_id == company_id:
            return True
        
        return self.check_user_company_access(user.id, company_id)
    
    def get_company_context(self, company_id: int) -> Dict[str, Any]:
        """Get Company Context."""
        """Get complete company context for frontend"""
        company = self.get_company_by_id(company_id)
        if not company:
            return {}
        
        settings = self.get_company_settings(company_id)
        modules = self.get_company_modules(company_id)
        analytics = self.get_company_analytics(company_id)
        
        return {
            'company': {
                'id': company.id,
                'name': company.name,
                'code': company.code,
                'domain': company.domain,
                'logo_url': company.logo_url,
                'primary_color': company.primary_color,
                'secondary_color': company.secondary_color,
                'plan': company.plan,
                'status': company.status
            },
            'settings': settings.__dict__ if settings else {},
            'modules': [{'name': m.module_name, 'enabled': m.is_enabled} for m in modules],
            'analytics': analytics
        }