"""
Encryption management service.
"""
import os
from typing import Dict, List, Optional, Any
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.security.encryption import EncryptionService, get_encryption_service
from app.models.encrypted_user import EncryptedUserProfile


class EncryptionManagementService:
    """Service for managing data encryption operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.encryption_service = get_encryption_service()
    
    def encrypt_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> EncryptedUserProfile:
        """Create or update encrypted user profile."""
        profile = self.db.query(EncryptedUserProfile).filter(
            EncryptedUserProfile.user_id == user_id
        ).first()
        
        if profile:
            for field, value in profile_data.items():
                if hasattr(profile, field) and value is not None:
                    setattr(profile, field, value)
        else:
            profile = EncryptedUserProfile(
                user_id=user_id,
                **profile_data
            )
            self.db.add(profile)
        
        self.db.commit()
        self.db.refresh(profile)
        
        return profile
    
    def get_user_profile(self, user_id: str) -> Optional[EncryptedUserProfile]:
        """Get decrypted user profile."""
        return self.db.query(EncryptedUserProfile).filter(
            EncryptedUserProfile.user_id == user_id
        ).first()
    
    def encrypt_existing_data(self, table_name: str, fields: List[str]) -> int:
        """Encrypt existing plain text data in specified table fields."""
        count = 0
        
        try:
            result = self.db.execute(text(f"SELECT id, {', '.join(fields)} FROM {table_name}"))
            records = result.fetchall()
            
            for record in records:
                record_id = record[0]
                updates = []
                
                for i, field in enumerate(fields):
                    value = record[i + 1]
                    if value and not self._is_encrypted(value):
                        encrypted_value = self.encryption_service.encrypt(value)
                        updates.append(f"{field} = :encrypted_{field}")
                
                if updates:
                    update_query = f"UPDATE {table_name} SET {', '.join(updates)} WHERE id = :record_id"
                    params = {f"encrypted_{field}": self.encryption_service.encrypt(record[i + 1]) 
                             for i, field in enumerate(fields) if record[i + 1]}
                    params['record_id'] = record_id
                    
                    self.db.execute(text(update_query), params)
                    count += 1
            
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            raise e
        
        return count
    
    def decrypt_field_for_search(self, encrypted_value: str) -> str:
        """Decrypt a field value for search operations."""
        try:
            return self.encryption_service.decrypt(encrypted_value)
        except ValueError:
            return encrypted_value
    
    def get_encryption_status(self) -> Dict[str, Any]:
        """Get encryption status and statistics."""
        key_configured = bool(os.getenv('ENCRYPTION_KEY'))
        encrypted_profiles = self.db.query(EncryptedUserProfile).count()
        
        return {
            'encryption_enabled': True,
            'key_configured': key_configured,
            'encrypted_user_profiles': encrypted_profiles,
            'encryption_algorithm': 'Fernet (AES 128)',
            'key_derivation': 'PBKDF2-HMAC-SHA256'
        }
    
    def _is_encrypted(self, value: str) -> bool:
        """Check if a value appears to be encrypted."""
        try:
            self.encryption_service.decrypt(value)
            return True
        except ValueError:
            return False