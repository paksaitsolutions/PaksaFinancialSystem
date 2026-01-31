"""
Password policy service for enforcing password requirements.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import re

from passlib.context import CryptContext
from sqlalchemy import and_, desc
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.exceptions import ValidationException
from app.models.password_policy import PasswordPolicy, PasswordHistory, LoginAttempt
from app.models.user import User




pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordService:
    """Service for managing password policies and validation."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_active_policy(self) -> PasswordPolicy:
        policy = self.db.query(PasswordPolicy).filter(
            PasswordPolicy.is_active == True
        ).first()
        
        if not policy:
            policy = self._create_default_policy()
        
        return policy
    
    def validate_password(self, password: str, user_id: Optional[UUID] = None) -> Dict[str, Any]:
        policy = self.get_active_policy()
        errors = []
        
        if len(password) < policy.min_length:
            errors.append(f"Password must be at least {policy.min_length} characters long")
        
        if len(password) > policy.max_length:
            errors.append(f"Password must not exceed {policy.max_length} characters")
        
        if policy.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if policy.require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if policy.require_numbers and not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        
        if policy.require_special_chars and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        if user_id and self._is_password_in_history(password, user_id, policy.password_history_count):
            errors.append(f"Password cannot be one of the last {policy.password_history_count} passwords used")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'policy': {
                'min_length': policy.min_length,
                'max_length': policy.max_length,
                'require_uppercase': policy.require_uppercase,
                'require_lowercase': policy.require_lowercase,
                'require_numbers': policy.require_numbers,
                'require_special_chars': policy.require_special_chars
            }
        }
    
    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    def change_password(self, user_id: UUID, old_password: str, new_password: str) -> Dict[str, Any]:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValidationException("User not found")
        
        if not self.verify_password(old_password, user.hashed_password):
            raise ValidationException("Current password is incorrect")
        
        validation = self.validate_password(new_password, user_id)
        if not validation['valid']:
            raise ValidationException("; ".join(validation['errors']))
        
        new_hash = self.hash_password(new_password)
        
        self._add_to_password_history(user_id, user.hashed_password)
        
        user.hashed_password = new_hash
        user.password_changed_at = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return {'success': True, 'message': 'Password changed successfully'}
    
    def is_password_expired(self, user_id: UUID) -> bool:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.password_changed_at:
            return False
        
        policy = self.get_active_policy()
        expiry_date = user.password_changed_at + timedelta(days=policy.password_expiry_days)
        
        return datetime.utcnow() > expiry_date
    
    def record_login_attempt(self, user_id: UUID, success: bool, ip_address: str = None, user_agent: str = None):
        attempt = LoginAttempt(
            user_id=user_id,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            attempted_at=datetime.utcnow()
        )
        
        self.db.add(attempt)
        self.db.commit()
    
    def is_account_locked(self, user_id: UUID) -> Dict[str, Any]:
        policy = self.get_active_policy()
        lockout_window = datetime.utcnow() - timedelta(minutes=policy.lockout_duration_minutes)
        
        failed_attempts = self.db.query(LoginAttempt).filter(
            and_(
                LoginAttempt.user_id == user_id,
                LoginAttempt.success == False,
                LoginAttempt.attempted_at > lockout_window
            )
        ).count()
        
        is_locked = failed_attempts >= policy.max_failed_attempts
        
        if is_locked:
            last_failed = self.db.query(LoginAttempt).filter(
                and_(
                    LoginAttempt.user_id == user_id,
                    LoginAttempt.success == False
                )
            ).order_by(desc(LoginAttempt.attempted_at)).first()
            
            unlock_time = last_failed.attempted_at + timedelta(minutes=policy.lockout_duration_minutes)
        else:
            unlock_time = None
        
        return {
            'locked': is_locked,
            'failed_attempts': failed_attempts,
            'max_attempts': policy.max_failed_attempts,
            'unlock_time': unlock_time,
            'remaining_attempts': max(0, policy.max_failed_attempts - failed_attempts)
        }
    
    def unlock_account(self, user_id: UUID):
        policy = self.get_active_policy()
        lockout_window = datetime.utcnow() - timedelta(minutes=policy.lockout_duration_minutes)
        
        self.db.query(LoginAttempt).filter(
            and_(
                LoginAttempt.user_id == user_id,
                LoginAttempt.success == False,
                LoginAttempt.attempted_at > lockout_window
            )
        ).delete()
        
        self.db.commit()
    
    def _add_to_password_history(self, user_id: UUID, password_hash: str):
        history_entry = PasswordHistory(
            user_id=user_id,
            password_hash=password_hash
        )
        
        self.db.add(history_entry)
        
        policy = self.get_active_policy()
        old_entries = self.db.query(PasswordHistory).filter(
            PasswordHistory.user_id == user_id
        ).order_by(desc(PasswordHistory.created_at)).offset(policy.password_history_count).all()
        
        for entry in old_entries:
            self.db.delete(entry)
    
    def _is_password_in_history(self, password: str, user_id: UUID, history_count: int) -> bool:
        history_entries = self.db.query(PasswordHistory).filter(
            PasswordHistory.user_id == user_id
        ).order_by(desc(PasswordHistory.created_at)).limit(history_count).all()
        
        for entry in history_entries:
            if self.verify_password(password, entry.password_hash):
                return True
        
        return False
    
    def _create_default_policy(self) -> PasswordPolicy:
        policy = PasswordPolicy(
            name="Default Password Policy",
            description="Default security policy for password requirements",
            min_length=8,
            max_length=128,
            require_uppercase=True,
            require_lowercase=True,
            require_numbers=True,
            require_special_chars=True,
            password_history_count=5,
            password_expiry_days=90,
            max_failed_attempts=5,
            lockout_duration_minutes=30,
            is_active=True
        )
        
        self.db.add(policy)
        self.db.commit()
        self.db.refresh(policy)
        
        return policy