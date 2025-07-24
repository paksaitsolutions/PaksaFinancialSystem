from cryptography.fernet import Fernet
from app.core.db.tenant_middleware import get_current_tenant
from app.core.config import settings
import base64
import hashlib

class TenantDataEncryption:
    def __init__(self):
        self.master_key = settings.ENCRYPTION_KEY.encode()
    
    def _get_tenant_key(self, tenant_id: str = None) -> bytes:
        """Generate tenant-specific encryption key"""
        if not tenant_id:
            tenant_id = get_current_tenant()
        
        # Derive tenant key from master key and tenant ID
        key_material = f"{self.master_key.decode()}:{tenant_id}".encode()
        tenant_key = hashlib.sha256(key_material).digest()
        return base64.urlsafe_b64encode(tenant_key)
    
    def encrypt_data(self, data: str, tenant_id: str = None) -> str:
        """Encrypt data with tenant-specific key"""
        if not data:
            return data
        
        tenant_key = self._get_tenant_key(tenant_id)
        fernet = Fernet(tenant_key)
        
        encrypted_data = fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt_data(self, encrypted_data: str, tenant_id: str = None) -> str:
        """Decrypt data with tenant-specific key"""
        if not encrypted_data:
            return encrypted_data
        
        try:
            tenant_key = self._get_tenant_key(tenant_id)
            fernet = Fernet(tenant_key)
            
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception:
            return encrypted_data  # Return as-is if decryption fails
    
    def encrypt_field(self, model_instance, field_name: str):
        """Encrypt a specific field in a model instance"""
        value = getattr(model_instance, field_name)
        if value:
            encrypted_value = self.encrypt_data(str(value))
            setattr(model_instance, field_name, encrypted_value)
    
    def decrypt_field(self, model_instance, field_name: str):
        """Decrypt a specific field in a model instance"""
        encrypted_value = getattr(model_instance, field_name)
        if encrypted_value:
            decrypted_value = self.decrypt_data(encrypted_value)
            setattr(model_instance, field_name, decrypted_value)

# Global encryption instance
tenant_encryption = TenantDataEncryption()

# Decorator for automatic field encryption
def encrypt_fields(*field_names):
    """Decorator to automatically encrypt/decrypt model fields"""
    def decorator(cls):
        original_init = cls.__init__
        
        def new_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            # Encrypt sensitive fields on creation
            for field_name in field_names:
                if hasattr(self, field_name):
                    tenant_encryption.encrypt_field(self, field_name)
        
        cls.__init__ = new_init
        return cls
    return decorator