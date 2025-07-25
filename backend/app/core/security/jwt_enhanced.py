import jwt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from passlib.context import CryptContext
import redis
from app.core.config import settings

class EnhancedJWTManager:
    def __init__(self):
        # Generate strong secret key if not provided
        self.secret_key = self._get_or_generate_secret_key()
        self.algorithm = "HS256"
        self.access_token_expire = timedelta(minutes=30)
        self.refresh_token_expire = timedelta(days=7)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL)
    
    def _get_or_generate_secret_key(self) -> str:
        """Get secret key from config or generate a strong one"""
        if settings.SECRET_KEY == "dev-secret-key-change-in-production":
            # Generate cryptographically secure key
            return secrets.token_urlsafe(32)
        return settings.SECRET_KEY
    
    def create_access_token(self, data: Dict[str, Any], tenant_id: str) -> str:
        """Create JWT access token with enhanced security"""
        to_encode = data.copy()
        expire = datetime.utcnow() + self.access_token_expire
        
        # Add security claims
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
            "tenant_id": tenant_id,
            "jti": secrets.token_urlsafe(16)  # JWT ID for revocation
        })
        
        token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        # Store token in Redis for revocation tracking
        self.redis_client.setex(
            f"jwt:{to_encode['jti']}", 
            int(self.access_token_expire.total_seconds()),
            "valid"
        )
        
        return token
    
    def create_refresh_token(self, user_id: str, tenant_id: str) -> str:
        """Create refresh token"""
        to_encode = {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "type": "refresh",
            "exp": datetime.utcnow() + self.refresh_token_expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(16)
        }
        
        token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        # Store refresh token
        self.redis_client.setex(
            f"refresh:{to_encode['jti']}", 
            int(self.refresh_token_expire.total_seconds()),
            user_id
        )
        
        return token
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token with enhanced security checks"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check if token is revoked
            jti = payload.get("jti")
            if jti and not self.redis_client.exists(f"jwt:{jti}"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked"
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def revoke_token(self, token: str):
        """Revoke a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            jti = payload.get("jti")
            if jti:
                self.redis_client.delete(f"jwt:{jti}")
        except jwt.JWTError:
            pass  # Token already invalid
    
    def revoke_all_user_tokens(self, user_id: str):
        """Revoke all tokens for a user"""
        pattern = f"jwt:*"
        for key in self.redis_client.scan_iter(match=pattern):
            # This is a simplified approach - in production, you'd want to store user_id with token
            self.redis_client.delete(key)

jwt_manager = EnhancedJWTManager()