"""Secure environment variables and secrets management"""
import os
from cryptography.fernet import Fernet
from typing import Optional
import base64

class SecretsManager:
    """Secure secrets management"""
    
    def __init__(self):
        self._encryption_key = self._get_or_create_key()
        self._cipher = Fernet(self._encryption_key)
    
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key"""
        key_env = os.getenv('ENCRYPTION_KEY')
        if key_env:
            return base64.urlsafe_b64decode(key_env.encode())
        return Fernet.generate_key()
    
    def encrypt_secret(self, value: str) -> str:
        """Encrypt a secret value"""
        return self._cipher.encrypt(value.encode()).decode()
    
    def decrypt_secret(self, encrypted_value: str) -> str:
        """Decrypt a secret value"""
        return self._cipher.decrypt(encrypted_value.encode()).decode()
    
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a secret from environment variables"""
        value = os.getenv(key, default)
        if value and value.startswith('encrypted:'):
            return self.decrypt_secret(value[10:])
        return value

# Global secrets manager
secrets = SecretsManager()

# Secure environment variable getters
def get_database_url() -> str:
    """Get database URL securely"""
    return secrets.get_secret('DATABASE_URL', 'postgresql://localhost/paksa_financial')

def get_jwt_secret() -> str:
    """Get JWT secret securely"""
    return secrets.get_secret('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')

def get_encryption_key() -> str:
    """Get encryption key securely"""
    return secrets.get_secret('ENCRYPTION_KEY', Fernet.generate_key().decode())