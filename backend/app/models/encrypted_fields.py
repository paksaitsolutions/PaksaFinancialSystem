"""
Encrypted field types for SQLAlchemy models.
"""
from sqlalchemy import TypeDecorator, String
from sqlalchemy.types import Text

from app.core.security.encryption import get_encryption_service


class EncryptedString(TypeDecorator):
    """Encrypted string field that automatically encrypts/decrypts data."""
    
    impl = String
    cache_ok = True
    
    def __init__(self, length=None, **kwargs):
        # Encrypted data is longer, so increase length
        if length:
            length = length * 2  # Rough estimate for encrypted size
        super().__init__(length, **kwargs)
    
    def process_bind_param(self, value, dialect):
        """Encrypt value before storing in database."""
        if value is not None:
            encryption_service = get_encryption_service()
            return encryption_service.encrypt(value)
        return value
    
    def process_result_value(self, value, dialect):
        """Decrypt value when retrieving from database."""
        if value is not None:
            encryption_service = get_encryption_service()
            try:
                return encryption_service.decrypt(value)
            except ValueError:
                # Return original value if decryption fails (for migration compatibility)
                return value
        return value


class EncryptedText(TypeDecorator):
    """Encrypted text field that automatically encrypts/decrypts data."""
    
    impl = Text
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        """Encrypt value before storing in database."""
        if value is not None:
            encryption_service = get_encryption_service()
            return encryption_service.encrypt(value)
        return value
    
    def process_result_value(self, value, dialect):
        """Decrypt value when retrieving from database."""
        if value is not None:
            encryption_service = get_encryption_service()
            try:
                return encryption_service.decrypt(value)
            except ValueError:
                # Return original value if decryption fails (for migration compatibility)
                return value
        return value