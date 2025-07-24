"""
User activity and management service.
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func

from app.models.user_activity import (
    LoginHistory, UserActivity, CompanyPasswordPolicy, 
    CrossCompanyAccess, UserSessionActivity, ActivityType
)


class UserActivityService:
    """Service for user activity tracking and management."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_login(
        self,
        user_id: UUID,
        company_id: UUID,
        success: bool = True,
        login_method: str = "email_password",
        failure_reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> LoginHistory:
        """Log user login attempt."""
        login_record = LoginHistory(
            user_id=user_id,
            company_id=company_id,
            login_method=login_method,
            success=success,
            failure_reason=failure_reason,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.db.add(login_record)
        self.db.commit()
        self.db.refresh(login_record)
        
        return login_record
    
    def log_activity(
        self,
        user_id: UUID,
        company_id: UUID,
        activity_type: str,
        action: str,
        description: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[UUID] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UserActivity:
        """Log user activity."""
        activity = UserActivity(
            user_id=user_id,
            company_id=company_id,
            activity_type=activity_type,
            action=action,
            description=description,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata
        )
        
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        
        return activity
    
    def get_login_history(
        self,
        user_id: Optional[UUID] = None,
        company_id: Optional[UUID] = None,
        limit: int = 100
    ) -> List[LoginHistory]:
        """Get login history with filters."""
        query = self.db.query(LoginHistory)
        
        if user_id:
            query = query.filter(LoginHistory.user_id == user_id)
        
        if company_id:
            query = query.filter(LoginHistory.company_id == company_id)
        
        return query.order_by(desc(LoginHistory.login_time)).limit(limit).all()
    
    def create_password_policy(
        self,
        company_id: UUID,
        policy_data: Dict[str, Any]
    ) -> CompanyPasswordPolicy:
        """Create password policy for a company."""
        policy = CompanyPasswordPolicy(
            company_id=company_id,
            min_length=policy_data.get('min_length', 8),
            max_length=policy_data.get('max_length', 128),
            require_uppercase=policy_data.get('require_uppercase', True),
            require_lowercase=policy_data.get('require_lowercase', True),
            require_numbers=policy_data.get('require_numbers', True),
            require_special_chars=policy_data.get('require_special_chars', True),
            password_history_count=policy_data.get('password_history_count', 5),
            password_expiry_days=policy_data.get('password_expiry_days', 90),
            max_failed_attempts=policy_data.get('max_failed_attempts', 5),
            lockout_duration_minutes=policy_data.get('lockout_duration_minutes', 30)
        )
        
        self.db.add(policy)
        self.db.commit()
        self.db.refresh(policy)
        
        return policy
    
    def grant_cross_company_access(
        self,
        user_id: UUID,
        source_company_id: UUID,
        target_company_id: UUID,
        access_type: str,
        approved_by: UUID,
        permissions: Optional[Dict[str, Any]] = None
    ) -> CrossCompanyAccess:
        """Grant cross-company access to a user."""
        access = CrossCompanyAccess(
            user_id=user_id,
            source_company_id=source_company_id,
            target_company_id=target_company_id,
            access_type=access_type,
            permissions=permissions,
            approved_by=approved_by
        )
        
        self.db.add(access)
        self.db.commit()
        self.db.refresh(access)
        
        return access