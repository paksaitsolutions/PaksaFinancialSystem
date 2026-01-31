"""
Multi-tenant authentication service.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session
from uuid import UUID
import secrets

from app.core.security.encryption import encrypt_data, decrypt_data
from app.models.tenant_auth import (



    TenantAuthConfig, TenantSession, CompanyLoginAttempt, 
    PasswordResetToken, OAuthProvider, LoginMethod, SessionStatus
)


class TenantAuthService:
    """Service for multi-tenant authentication operations."""
    
    def __init__(self, db: Session):
        """  Init  ."""
        self.db = db
    
    def get_auth_config(self, company_id: UUID) -> Optional[TenantAuthConfig]:
        """Get Auth Config."""
        """Get authentication configuration for a company."""
        return self.db.query(TenantAuthConfig).filter(
            TenantAuthConfig.company_id == company_id
        ).first()
    
    def create_auth_config(self, company_id: UUID, config_data: Dict[str, Any]) -> TenantAuthConfig:
        """Create Auth Config."""
        """Create authentication configuration for a company."""
        config = TenantAuthConfig(
            company_id=company_id,
            custom_login_url=config_data.get('custom_login_url'),
            company_code_required=config_data.get('company_code_required', False),
            session_timeout_minutes=config_data.get('session_timeout_minutes', 30),
            remember_me_enabled=config_data.get('remember_me_enabled', True),
            remember_me_duration_days=config_data.get('remember_me_duration_days', 30),
            concurrent_sessions_limit=config_data.get('concurrent_sessions_limit', 5),
            password_reset_enabled=config_data.get('password_reset_enabled', True),
            password_reset_expiry_hours=config_data.get('password_reset_expiry_hours', 24),
            custom_reset_template=config_data.get('custom_reset_template'),
            oauth_providers=config_data.get('oauth_providers'),
            saml_config=config_data.get('saml_config'),
            login_logo_url=config_data.get('login_logo_url'),
            login_background_url=config_data.get('login_background_url'),
            brand_colors=config_data.get('brand_colors')
        )
        
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        
        return config
    
    def create_session(
        self,
        user_id: UUID,
        company_id: UUID,
        login_method: str = LoginMethod.EMAIL_PASSWORD,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        remember_me: bool = False
    ) -> TenantSession:
        """Create Session."""
        """Create a new tenant session."""
        # Get auth config for session timeout
        auth_config = self.get_auth_config(company_id)
        timeout_minutes = auth_config.session_timeout_minutes if auth_config else 30
        
        # Calculate expiry
        if remember_me and auth_config and auth_config.remember_me_enabled:
            expires_at = datetime.utcnow() + timedelta(days=auth_config.remember_me_duration_days)
        else:
            expires_at = datetime.utcnow() + timedelta(minutes=timeout_minutes)
        
        # Check concurrent sessions limit
        if auth_config:
            self._enforce_session_limit(user_id, company_id, auth_config.concurrent_sessions_limit)
        
        # Generate session token
        session_token = secrets.token_urlsafe(32)
        
        session = TenantSession(
            session_token=session_token,
            user_id=user_id,
            company_id=company_id,
            login_method=login_method,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
            remember_me=remember_me,
            status=SessionStatus.ACTIVE
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    def validate_session(self, session_token: str) -> Optional[TenantSession]:
        """Validate Session."""
        """Validate and refresh a session."""
        session = self.db.query(TenantSession).filter(
            and_(
                TenantSession.session_token == session_token,
                TenantSession.status == SessionStatus.ACTIVE,
                TenantSession.expires_at > datetime.utcnow()
            )
        ).first()
        
        if session:
            # Update last activity
            session.last_activity = datetime.utcnow()
            
            # Extend expiry if not remember_me session
            if not session.remember_me:
                auth_config = self.get_auth_config(session.company_id)
                timeout_minutes = auth_config.session_timeout_minutes if auth_config else 30
                session.expires_at = datetime.utcnow() + timedelta(minutes=timeout_minutes)
            
            self.db.commit()
        
        return session
    
    def terminate_session(self, session_token: str, reason: str = "user_logout") -> bool:
        """Terminate Session."""
        """Terminate a session."""
        session = self.db.query(TenantSession).filter(
            TenantSession.session_token == session_token
        ).first()
        
        if session:
            session.status = SessionStatus.TERMINATED
            session.terminated_reason = reason
            self.db.commit()
            return True
        
        return False
    
    def terminate_all_user_sessions(self, user_id: UUID, company_id: UUID, except_token: Optional[str] = None):
        """Terminate All User Sessions."""
        """Terminate all sessions for a user in a company."""
        query = self.db.query(TenantSession).filter(
            and_(
                TenantSession.user_id == user_id,
                TenantSession.company_id == company_id,
                TenantSession.status == SessionStatus.ACTIVE
            )
        )
        
        if except_token:
            query = query.filter(TenantSession.session_token != except_token)
        
        sessions = query.all()
        
        for session in sessions:
            session.status = SessionStatus.TERMINATED
            session.terminated_reason = "admin_termination"
        
        self.db.commit()
    
    def log_login_attempt(
        self,
        email: str,
        success: bool,
        company_id: Optional[UUID] = None,
        login_method: str = LoginMethod.EMAIL_PASSWORD,
        failure_reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> CompanyLoginAttempt:
        """Log Login Attempt."""
        """Log a login attempt."""
        attempt = CompanyLoginAttempt(
            company_id=company_id,
            email=email,
            success=success,
            login_method=login_method,
            failure_reason=failure_reason,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)
        
        return attempt
    
    def create_password_reset_token(
        self,
        user_id: UUID,
        company_id: UUID,
        email: str
    ) -> PasswordResetToken:
        """Create Password Reset Token."""
        """Create a password reset token."""
        # Invalidate existing tokens
        self.db.query(PasswordResetToken).filter(
            and_(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.company_id == company_id,
                PasswordResetToken.used == False
            )
        ).update({"used": True, "used_at": datetime.utcnow()})
        
        # Get auth config for expiry
        auth_config = self.get_auth_config(company_id)
        expiry_hours = auth_config.password_reset_expiry_hours if auth_config else 24
        
        token = secrets.token_urlsafe(32)
        
        reset_token = PasswordResetToken(
            token=token,
            user_id=user_id,
            company_id=company_id,
            email=email,
            expires_at=datetime.utcnow() + timedelta(hours=expiry_hours)
        )
        
        self.db.add(reset_token)
        self.db.commit()
        self.db.refresh(reset_token)
        
        return reset_token
    
    def validate_password_reset_token(self, token: str) -> Optional[PasswordResetToken]:
        """Validate Password Reset Token."""
        """Validate a password reset token."""
        return self.db.query(PasswordResetToken).filter(
            and_(
                PasswordResetToken.token == token,
                PasswordResetToken.used == False,
                PasswordResetToken.expires_at > datetime.utcnow()
            )
        ).first()
    
    def use_password_reset_token(self, token: str) -> bool:
        """Use Password Reset Token."""
        """Mark a password reset token as used."""
        reset_token = self.validate_password_reset_token(token)
        
        if reset_token:
            reset_token.used = True
            reset_token.used_at = datetime.utcnow()
            self.db.commit()
            return True
        
        return False
    
    def create_oauth_provider(
        self,
        company_id: UUID,
        provider_data: Dict[str, Any]
    ) -> OAuthProvider:
        """Create Oauth Provider."""
        """Create OAuth provider configuration."""
        provider = OAuthProvider(
            company_id=company_id,
            provider_name=provider_data['provider_name'],
            client_id=provider_data['client_id'],
            client_secret=encrypt_data(provider_data['client_secret']),
            redirect_uri=provider_data['redirect_uri'],
            scopes=provider_data.get('scopes'),
            is_active=provider_data.get('is_active', True),
            auto_create_users=provider_data.get('auto_create_users', False),
            default_role=provider_data.get('default_role')
        )
        
        self.db.add(provider)
        self.db.commit()
        self.db.refresh(provider)
        
        return provider
    
    def get_oauth_providers(self, company_id: UUID, active_only: bool = True) -> List[OAuthProvider]:
        """Get Oauth Providers."""
        """Get OAuth providers for a company."""
        query = self.db.query(OAuthProvider).filter(
            OAuthProvider.company_id == company_id
        )
        
        if active_only:
            query = query.filter(OAuthProvider.is_active == True)
        
        return query.all()
    
    def get_login_attempts(
        self,
        company_id: Optional[UUID] = None,
        email: Optional[str] = None,
        limit: int = 100
    ) -> List[CompanyLoginAttempt]:
        """Get Login Attempts."""
        """Get login attempts with optional filters."""
        query = self.db.query(CompanyLoginAttempt)
        
        if company_id:
            query = query.filter(CompanyLoginAttempt.company_id == company_id)
        
        if email:
            query = query.filter(CompanyLoginAttempt.email == email)
        
        return query.order_by(desc(CompanyLoginAttempt.created_at)).limit(limit).all()
    
    def cleanup_expired_sessions(self):
        """Cleanup Expired Sessions."""
        """Clean up expired sessions."""
        expired_sessions = self.db.query(TenantSession).filter(
            and_(
                TenantSession.status == SessionStatus.ACTIVE,
                TenantSession.expires_at < datetime.utcnow()
            )
        ).all()
        
        for session in expired_sessions:
            session.status = SessionStatus.EXPIRED
        
        self.db.commit()
        return len(expired_sessions)
    
    def _enforce_session_limit(self, user_id: UUID, company_id: UUID, limit: int):
        """ Enforce Session Limit."""
        """Enforce concurrent session limit."""
        active_sessions = self.db.query(TenantSession).filter(
            and_(
                TenantSession.user_id == user_id,
                TenantSession.company_id == company_id,
                TenantSession.status == SessionStatus.ACTIVE,
                TenantSession.expires_at > datetime.utcnow()
            )
        ).order_by(TenantSession.last_activity).all()
        
        if len(active_sessions) >= limit:
            # Terminate oldest sessions
            sessions_to_terminate = active_sessions[:len(active_sessions) - limit + 1]
            
            for session in sessions_to_terminate:
                session.status = SessionStatus.TERMINATED
                session.terminated_reason = "session_limit_exceeded"
            
            self.db.commit()