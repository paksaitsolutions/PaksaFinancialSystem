"""Enhanced JWT implementation with proper invalidation"""
import jwt
import redis
from datetime import datetime, timedelta
from typing import Optional

class JWTManager:
    def __init__(self, secret_key: str, redis_client: redis.Redis):
        self.secret_key = secret_key
        self.redis = redis_client
        self.algorithm = "HS256"
        self.access_token_expire = timedelta(minutes=30)
        self.refresh_token_expire = timedelta(days=7)
    
    def create_tokens(self, user_id: str, tenant_id: str) -> dict:
        """Create access and refresh tokens"""
        now = datetime.utcnow()
        
        # Access token
        access_payload = {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "type": "access",
            "iat": now,
            "exp": now + self.access_token_expire,
            "jti": f"access_{user_id}_{int(now.timestamp())}"
        }
        access_token = jwt.encode(access_payload, self.secret_key, algorithm=self.algorithm)
        
        # Refresh token
        refresh_payload = {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "type": "refresh",
            "iat": now,
            "exp": now + self.refresh_token_expire,
            "jti": f"refresh_{user_id}_{int(now.timestamp())}"
        }
        refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm=self.algorithm)
        
        # Store tokens in Redis for invalidation
        self.redis.setex(f"token:{access_payload['jti']}", int(self.access_token_expire.total_seconds()), "valid")
        self.redis.setex(f"token:{refresh_payload['jti']}", int(self.refresh_token_expire.total_seconds()), "valid")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": int(self.access_token_expire.total_seconds())
        }
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify and decode token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check if token is blacklisted
            if not self.redis.get(f"token:{payload['jti']}"):
                return None
            
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def invalidate_token(self, token: str) -> bool:
        """Invalidate a specific token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm], options={"verify_exp": False})
            self.redis.delete(f"token:{payload['jti']}")
            return True
        except:
            return False
    
    def invalidate_user_tokens(self, user_id: str):
        """Invalidate all tokens for a user"""
        pattern = f"token:*_{user_id}_*"
        for key in self.redis.scan_iter(match=pattern):
            self.redis.delete(key)