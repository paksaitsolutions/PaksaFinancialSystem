"""
Data encryption utilities for protecting sensitive information.
"""
import base64
import os
from typing import Optional, Union

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class EncryptionService:
    """Service for encrypting and decrypting sensitive data."""
    
    def __init__(self, key: Optional[bytes] = None):
        """Initialize encryption service with key."""
        if key:
            self.fernet = Fernet(key)
        else:
            self.fernet = Fernet(self._get_or_create_key())
    
    def encrypt(self, data: Union[str, bytes]) -> str:
        """Encrypt data and return base64 encoded string."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        encrypted_data = self.fernet.encrypt(data)
        return base64.b64encode(encrypted_data).decode('utf-8')
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt base64 encoded encrypted data."""
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = self.fernet.decrypt(encrypted_bytes)
            return decrypted_data.decode('utf-8')
        except Exception:
            raise ValueError("Invalid encrypted data or decryption failed")
    
    def encrypt_dict(self, data: dict, fields_to_encrypt: list) -> dict:
        """Encrypt specific fields in a dictionary."""
        encrypted_data = data.copy()
        
        for field in fields_to_encrypt:
            if field in encrypted_data and encrypted_data[field] is not None:
                encrypted_data[field] = self.encrypt(str(encrypted_data[field]))
        
        return encrypted_data
    
    def decrypt_dict(self, data: dict, fields_to_decrypt: list) -> dict:
        """Decrypt specific fields in a dictionary."""
        decrypted_data = data.copy()
        
        for field in fields_to_decrypt:
            if field in decrypted_data and decrypted_data[field] is not None:
                try:
                    decrypted_data[field] = self.decrypt(decrypted_data[field])
                except ValueError:
                    # Field might not be encrypted, leave as is
                    pass
        
        return decrypted_data
    
    @staticmethod
    def generate_key() -> bytes:
        """Generate a new encryption key."""
        return Fernet.generate_key()
    
    @staticmethod
    def derive_key_from_password(password: str, salt: bytes = None) -> bytes:
        """Derive encryption key from password."""
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def _get_or_create_key(self) -> bytes:
        """Get encryption key from environment or create new one."""
        key_env = os.getenv('ENCRYPTION_KEY')
        
        if key_env:
            return key_env.encode()
        
        # Generate new key (in production, this should be stored securely)
        key = self.generate_key()
        print(f"Generated new encryption key: {key.decode()}")
        print("Store this key securely in ENCRYPTION_KEY environment variable")
        
        return key


# Global encryption service instance
_encryption_service = None


def get_encryption_service() -> EncryptionService:
    """Get global encryption service instance."""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service


# Convenience functions
def encrypt_data(data: Union[str, bytes]) -> str:
    """Encrypt data using global encryption service."""
    return get_encryption_service().encrypt(data)


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt data using global encryption service."""
    return get_encryption_service().decrypt(encrypted_data)