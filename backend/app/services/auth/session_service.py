"""
Session management service.
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from sqlalchemy import and_, or_, desc
from sqlalchemy.orm import Session
from uuid import UUID
import secrets

from app.core.exceptions import NotFoundException, ValidationException
from app.models.session import UserSession, SessionConfig, SessionStatus
from app.models.user import User





class SessionService:
    """Service for managing user sessions."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_session(
        self, 
        user_id: UUID, 
        ip_address: str = None, 
        user_agent: str = None,
        remember_me: bool = False
    ) -> UserSession:
        """Create Session."""
        """Create a new user session."""
        config = self.get_active_config()
        
        # Check concurrent session limit
        self._enforce_concurrent_session_limit(user_id, config.max_concurrent_sessions)
        
        # Generate session token
        session_token = self._generate_session_token()
        
        # Calculate expiration
        if remember_me:
            expires_at = datetime.utcnow() + timedelta(days=config.remember_me_duration_days)
        else:
            expires_at = datetime.utcnow() + timedelta(minutes=config.session_timeout_minutes)
        
        # Create session
        session = UserSession(
            session_token=session_token,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
            status=SessionStatus.ACTIVE
        )
        
    def create_session(
        self,
        user_id: UUID,
        company_id: UUID,
        ip_address: str = None,
        user_agent: str = None,
        remember_me: bool = False
    ) -> UserSession:
        """Create Session."""
        """Create a new user session scoped to a tenant/company."""
        config = self.get_active_config()
        self._enforce_concurrent_session_limit(user_id, config.max_concurrent_sessions)
        session_token = self._generate_session_token()
        if remember_me:
            expires_at = datetime.utcnow() + timedelta(days=config.remember_me_duration_days)
        else:
            expires_at = datetime.utcnow() + timedelta(minutes=config.session_timeout_minutes)
        session = UserSession(
            session_token=session_token,
            user_id=user_id,
            company_id=company_id,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
            status=SessionStatus.ACTIVE
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
            'valid': True,
            'session': session,
            'user_id': session.user_id,
            'expires_at': session.expires_at
        }
    
    def extend_session(self, session_token: str, duration_minutes: int = None) -> UserSession:
        session = self.get_session(session_token)
        if not session or not session.is_active():
            raise ValidationException("Invalid or inactive session")
        
        config = self.get_active_config()
        duration = duration_minutes or config.session_timeout_minutes
        
        session.extend_session(duration)
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    def terminate_session(self, session_token: str, reason: str = "User logout") -> bool:
        session = self.get_session(session_token)
        if not session:
            return False
        
        session.status = SessionStatus.TERMINATED
        session.terminated_at = datetime.utcnow()
        session.termination_reason = reason
        
        self.db.commit()
        return True
    
    def terminate_user_sessions(self, user_id: UUID, except_session: str = None, reason: str = "Admin action") -> int:
        query = self.db.query(UserSession).filter(
            and_(
                UserSession.user_id == user_id,
                UserSession.status == SessionStatus.ACTIVE
            )
        )
        
        if except_session:
            query = query.filter(UserSession.session_token != except_session)
        
        sessions = query.all()
        
        for session in sessions:
            session.status = SessionStatus.TERMINATED
            session.terminated_at = datetime.utcnow()
            session.termination_reason = reason
        
        self.db.commit()
        return len(sessions)
    
    def get_user_sessions(self, user_id: UUID, active_only: bool = True) -> List[UserSession]:
        query = self.db.query(UserSession).filter(UserSession.user_id == user_id)
        
        if active_only:
            query = query.filter(UserSession.status == SessionStatus.ACTIVE)
        
        return query.order_by(desc(UserSession.last_activity)).all()
    
    def cleanup_expired_sessions(self) -> int:
        expired_sessions = self.db.query(UserSession).filter(
            and_(
                UserSession.status == SessionStatus.ACTIVE,
                UserSession.expires_at < datetime.utcnow()
            )
        ).all()
        
        for session in expired_sessions:
            self._expire_session(session)
        
        self.db.commit()
        return len(expired_sessions)
    
    def get_active_config(self) -> SessionConfig:
        config = self.db.query(SessionConfig).filter(
            SessionConfig.is_active == True
        ).first()
        
        if not config:
            config = self._create_default_config()
        
        return config
    
    def is_fresh_login_required(self, session_token: str) -> bool:
        session = self.get_session(session_token)
        if not session or not session.is_active():
            return True
        
        config = self.get_active_config()
        fresh_login_threshold = datetime.utcnow() - timedelta(minutes=config.require_fresh_login_minutes)
        
        return session.created_at < fresh_login_threshold
    
    def _enforce_concurrent_session_limit(self, user_id: UUID, max_sessions: int):
        active_sessions = self.get_user_sessions(user_id, active_only=True)
        
        if len(active_sessions) >= max_sessions:
            # Terminate oldest sessions
            sessions_to_terminate = active_sessions[max_sessions-1:]
            
            for session in sessions_to_terminate:
                session.status = SessionStatus.TERMINATED
                session.terminated_at = datetime.utcnow()
                session.termination_reason = "Concurrent session limit exceeded"
            
            self.db.commit()
    
    def _expire_session(self, session: UserSession):
        session.status = SessionStatus.EXPIRED
        session.terminated_at = datetime.utcnow()
        session.termination_reason = "Session expired"
    
    def _generate_session_token(self) -> str:
        return secrets.token_urlsafe(32)
    
    def _create_default_config(self) -> SessionConfig:
        config = SessionConfig(
            name="Default Session Configuration",
            description="Default session management settings",
            session_timeout_minutes=30,
            max_concurrent_sessions=3,
            remember_me_duration_days=30,
            require_fresh_login_minutes=60,
            auto_logout_on_idle=True,
            is_active=True
        )
        
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        
        return config